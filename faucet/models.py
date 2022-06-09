from datetime import timedelta
from django.db import models
from django.db import transaction
import uuid
from .managerAbi import manager_abi
from django.utils import timezone
from encrypted_model_fields.fields import EncryptedCharField
from eth_account.signers.local import LocalAccount
from eth_typing import Address
from web3 import Web3
from web3.exceptions import TimeExhausted
from web3.gas_strategies.rpc import rpc_gas_price_strategy
import binascii
from web3.middleware import geth_poa_middleware
from bip_utils import Bip44Coins, Bip44
from brightIDfaucet.settings import BRIGHT_ID_INTERFACE


class WalletAccount(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    private_key = EncryptedCharField(max_length=100)

    @property
    def address(self):
        node = Bip44.FromPrivateKey(binascii.unhexlify(self.private_key), Bip44Coins.ETHEREUM)
        return node.PublicKey().ToAddress()

    def __str__(self) -> str:
        return "%s - %s" % (self.name, self.address)

    @property
    def main_key(self):
        return self.private_key


class BrightUserManager(models.Manager):

    def get_or_create(self, address):
        try:
            return super().get_queryset().get(address=address)
        except BrightUser.DoesNotExist:
            # don't create user if sponsorship fails
            # so user can retry connecting their wallet
            with transaction.atomic():
                _user = BrightUser(address=address)
                _user.save()
                if not _user.sponsor():
                    raise Exception("Could not sponsor")
                return _user


class BrightUser(models.Model):
    PENDING = "0"
    VERIFIED = "1"

    states = ((PENDING, "Pending"),
              (VERIFIED, "Verified"))

    address = models.CharField(max_length=45, unique=True)
    context_id = models.UUIDField(default=uuid.uuid4, unique=True)

    _verification_status = models.CharField(max_length=1, choices=states, default=PENDING)
    _sponsored = models.BooleanField(default=False)

    objects = BrightUserManager()

    def __str__(self):
        return "%d - %s" % (self.pk, self.address)

    @property
    def verification_url(self, bright_interface=BRIGHT_ID_INTERFACE):
        return bright_interface.get_verification_link(str(self.context_id))

    @property
    def verification_status(self):
        if self._verification_status == self.VERIFIED:
            return self.VERIFIED
        return self.get_verification_status()

    def sponsor(self):
        if not self._sponsored:
            if BRIGHT_ID_INTERFACE.sponsor(str(self.context_id)):
                self._sponsored = True
                self.save()
        return self._sponsored

    def get_verification_status(self) -> states:
        is_verified = BRIGHT_ID_INTERFACE.get_verification_status(str(self.context_id))
        if is_verified:
            self._verification_status = self.VERIFIED
            self.save()
        return self._verification_status

    def get_verification_url(self) -> str:
        return BRIGHT_ID_INTERFACE.get_verification_link(str(self.context_id))


class ClaimReceipt(models.Model):
    MAX_PENDING_DURATION = 15  # minutes
    PENDING = '0'
    VERIFIED = '1'
    REJECTED = '2'

    states = ((PENDING, "Pending"),
              (VERIFIED, "Verified"),
              (REJECTED, "Rejected")
              )

    chain = models.ForeignKey("Chain", related_name="claims", on_delete=models.PROTECT)
    bright_user = models.ForeignKey(BrightUser, related_name="claims", on_delete=models.PROTECT)

    _status = models.CharField(max_length=1, choices=states, default=PENDING)

    amount = models.BigIntegerField()
    datetime = models.DateTimeField()
    tx_hash = models.CharField(max_length=100, blank=True, null=True)

    @staticmethod
    def update_status(chain, bright_user):
        # verified and rejected receipts don't get updated,
        # so only update pending receipts
        for pending_recept in ClaimReceipt.objects.filter(chain=chain,
                                                          bright_user=bright_user,
                                                          _status=ClaimReceipt.PENDING):

            ClaimReceipt.update_claim_receipt_from_tx_receipt(chain, pending_recept)

            if pending_recept._status == ClaimReceipt.PENDING and pending_recept.is_expired():
                pending_recept._status = ClaimReceipt.REJECTED
                pending_recept.save()

    @staticmethod
    def update_claim_receipt_from_tx_receipt(chain, pending_recept):
        chain.wait_for_tx_receipt(pending_recept, pending_recept.tx_hash)

    def is_expired(self):
        return timezone.now() - self.datetime > timedelta(minutes=self.MAX_PENDING_DURATION)

    def status(self) -> states:
        if self._status in [self.VERIFIED, self.REJECTED]:
            return self._status
        self.update_status(self.chain, self.bright_user)
        return self._status


class Chain(models.Model):
    chain_name = models.CharField(max_length=255)
    chain_id = models.CharField(max_length=255, unique=True)

    native_currency_name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=255)
    decimals = models.IntegerField(default=18)

    explorer_url = models.URLField(max_length=255, blank=True, null=True)
    rpc_url = models.URLField(max_length=255, blank=True, null=True)
    logo_url = models.URLField(max_length=255, blank=True, null=True)
    rpc_url_private = models.URLField(max_length=255, blank=True, null=True)

    max_claim_amount = models.BigIntegerField()

    poa = models.BooleanField(default=False)

    fund_manager_address = models.CharField(max_length=255, blank=True, null=True)
    wallet = models.ForeignKey(WalletAccount, related_name="chains", blank=True, null=True,
                               on_delete=models.PROTECT)

    def w3(self) -> Web3:
        assert self.rpc_url_private is not None
        _w3 = Web3(Web3.HTTPProvider(self.rpc_url_private))
        if self.poa:
            _w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        if _w3.isConnected():
            _w3.eth.set_gas_price_strategy(rpc_gas_price_strategy)
            return _w3
        raise Exception(f"Could not connect to rpc {self.rpc_url_private}")

    @property
    def account(self) -> LocalAccount:
        return self.w3().eth.account.privateKeyToAccount(self.wallet.main_key)

    @property
    def fund_manager(self):
        return self.w3().eth.contract(address=self.fund_manager_address, abi=manager_abi)

    @property
    def balance(self) -> int:
        try:
            return self.w3().eth.get_balance(self.account.address)
        except:
            return "N/A"

    def transfer(self, bright_user: BrightUser, amount: int) -> ClaimReceipt:
        tx = self.sign_transfer_tx(amount, bright_user)
        claim_receipt = self.create_claim_receipt(amount, bright_user, tx)
        self.broadcast_transaction(tx)
        return claim_receipt

    def broadcast_transaction(self, tx):
        self.w3().eth.send_raw_transaction(tx.rawTransaction)

    def broadcast_and_wait_for_receipt(self, claim_receipt, tx):
        self.broadcast_transaction(tx)
        self.wait_for_tx_receipt(claim_receipt, tx['hash'].hex())

    def wait_for_tx_receipt(self, claim_receipt, tx):
        try:
            receipt = self.w3().eth.wait_for_transaction_receipt(tx)
            if receipt['status'] == 1:
                claim_receipt._status = ClaimReceipt.VERIFIED
                claim_receipt.save()

        except TimeExhausted:
            pass

    def create_claim_receipt(self, amount, bright_user, tx):
        claim_receipt = ClaimReceipt.objects.create(chain=self, bright_user=bright_user,
                                                    datetime=timezone.now(),
                                                    amount=amount,
                                                    tx_hash=tx['hash'].hex(),
                                                    _status=ClaimReceipt.PENDING)
        return claim_receipt

    def sign_transfer_tx(self, amount, bright_user):
        tx_data = self.get_transaction_data(amount, bright_user)
        tx = self.w3().eth.account.sign_transaction(tx_data, self.account.key)
        return tx

    @property
    def gas_price(self):
        return self.w3().eth.generate_gas_price()

    def get_transaction_data(self, amount: int, bright_user: BrightUser):

        nonce = self.w3().eth.get_transaction_count(self.account.address, "pending")
        tx_func = self.fund_manager.functions.withdrawEth(amount, bright_user.address)
        gas_estimation = tx_func.estimateGas({'from': self.account.address})
        tx_data = tx_func.buildTransaction({
            'nonce': nonce,
            'from': self.account.address,
            'gas': gas_estimation,
            'gasPrice': self.gas_price
        })
        return tx_data

    def __str__(self):
        return f"{self.pk} - {self.symbol}:{self.chain_id}"
