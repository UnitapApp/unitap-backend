import binascii
import inspect
import logging

from bip_utils import Bip44, Bip44Coins
from django.db import models
from django.utils.translation import gettext_lazy as _
from encrypted_model_fields.fields import EncryptedCharField
from solders.keypair import Keypair
from solders.pubkey import Pubkey

from faucet.faucet_manager.lnpay_client import LNPayClient

from .constraints import (
    AllowListVerification,
    Attest,
    BeAttestedBy,
    BeFollowedByFarcasterUser,
    BeFollowedByLensUser,
    BrightIDAuraVerification,
    BrightIDMeetVerification,
    DidCollectLensPublication,
    DidLikedFarcasterCast,
    DidMirrorOnLensPublication,
    DidRecastFarcasterCast,
    HasENSVerification,
    HasFarcasterProfile,
    HasLensProfile,
    HasMinimumFarcasterFollower,
    HasMinimumLensFollower,
    HasMinimumLensPost,
    HasNFTVerification,
    HasTokenVerification,
    IsFollowingFarcasterUser,
    IsFollowingLensUser,
)
from .utils import SolanaWeb3Utils, Web3Utils


class NetworkTypes:
    EVM = "EVM"
    SOLANA = "Solana"
    LIGHTNING = "Lightning"
    NONEVM = "NONEVM"
    NONEVMXDC = "NONEVMXDC"

    networks = (
        (EVM, "EVM"),
        (SOLANA, "Solana"),
        (LIGHTNING, "Lightning"),
        (NONEVM, "NONEVM"),
        (NONEVMXDC, "NONEVMXDC"),
    )


class BigNumField(models.Field):
    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 200  # or some other number
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        return "numeric"

    def get_internal_type(self):
        return "BigNumField"

    def to_python(self, value):
        if isinstance(value, str):
            return int(value)

        return value

    def get_prep_value(self, value):
        return str(value)


class UserConstraint(models.Model):
    class Meta:
        abstract = True

    class Type(models.TextChoices):
        VERIFICATION = "VER", _("Verification")
        TIME = "TIME", _("Time")

    constraints = [
        BrightIDMeetVerification,
        BrightIDAuraVerification,
        HasNFTVerification,
        HasTokenVerification,
        AllowListVerification,
        HasENSVerification,
        HasLensProfile,
        IsFollowingLensUser,
        BeFollowedByLensUser,
        DidMirrorOnLensPublication,
        DidCollectLensPublication,
        HasMinimumLensPost,
        HasMinimumLensFollower,
        BeFollowedByFarcasterUser,
        HasMinimumFarcasterFollower,
        DidLikedFarcasterCast,
        DidRecastFarcasterCast,
        IsFollowingFarcasterUser,
        HasFarcasterProfile,
        BeAttestedBy,
        Attest,
    ]

    name = models.CharField(
        max_length=255,
        unique=True,
        choices=[
            (f'{inspect.getmodule(c).__name__.split(".")[0]}.{c.__name__}', c.__name__)
            for c in constraints
        ],
    )
    title = models.CharField(max_length=255)
    type = models.CharField(
        max_length=10, choices=Type.choices, default=Type.VERIFICATION
    )
    description = models.TextField(null=True, blank=True)
    negative_description = models.TextField(null=True, blank=True)
    explanation = models.TextField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    icon_url = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def create_name_field(cls, constraints):
        return models.CharField(
            max_length=255,
            unique=True,
            choices=[
                (
                    f'{inspect.getmodule(c).__name__.split(".")[0]}.{c.__name__}',
                    c.__name__,
                )
                for c in constraints
            ],
        )


class TokenPrice(models.Model):
    usd_price = models.CharField(max_length=255, null=False)
    datetime = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    price_url = models.URLField(max_length=255, null=True, blank=True)
    symbol = models.CharField(
        max_length=255, db_index=True, unique=True, null=False, blank=False
    )


class WalletAccount(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    private_key = EncryptedCharField(max_length=100)
    network_type = models.CharField(
        choices=NetworkTypes.networks, max_length=10, default=NetworkTypes.EVM
    )

    @property
    def address(self):
        try:
            node = Bip44.FromPrivateKey(
                binascii.unhexlify(self.private_key), Bip44Coins.ETHEREUM
            )
            return node.PublicKey().ToAddress()
        except:  # noqa: E722
            # dont change this, somehow it creates a bug if changed to Exception
            try:
                keypair = Keypair.from_base58_string(self.private_key)
                return str(keypair.pubkey())
            except:  # noqa: E722
                # dont change this, somehow it creates a bug if changed to Exception
                pass

    def __str__(self) -> str:
        return "%s - %s" % (self.name, self.address)

    @property
    def main_key(self):
        return self.private_key


class Chain(models.Model):
    chain_name = models.CharField(max_length=255)
    chain_id = models.CharField(max_length=255, unique=True)

    native_currency_name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=255)
    decimals = models.IntegerField(default=18)

    explorer_url = models.URLField(max_length=255, blank=True, null=True)
    explorer_api_url = models.URLField(max_length=255, blank=True, null=True)
    explorer_api_key = models.CharField(max_length=255, blank=True, null=True)
    rpc_url = models.URLField(max_length=255, blank=True, null=True)
    logo_url = models.URLField(max_length=255, blank=True, null=True)
    modal_url = models.URLField(max_length=255, blank=True, null=True)
    rpc_url_private = models.URLField(max_length=255)

    poa = models.BooleanField(default=False)

    wallet = models.ForeignKey(
        WalletAccount, related_name="chains", on_delete=models.PROTECT
    )

    max_gas_price = models.BigIntegerField(default=250000000000)
    gas_multiplier = models.FloatField(default=1)
    enough_fee_multiplier = models.BigIntegerField(default=200000)

    is_testnet = models.BooleanField(default=False)
    chain_type = models.CharField(
        max_length=10, choices=NetworkTypes.networks, default=NetworkTypes.EVM
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.chain_name} - {self.pk} - {self.symbol}:{self.chain_id}"

    @property
    def wallet_balance(self):
        return self.get_wallet_balance()

    def get_wallet_balance(self):
        if not self.is_active or not self.rpc_url_private:
            return 0

        try:
            if self.chain_type == NetworkTypes.EVM or int(self.chain_id) == 500:
                return Web3Utils(self.rpc_url, self.poa).get_balance(
                    self.wallet.address
                )
            elif self.chain_type == NetworkTypes.SOLANA:
                return (
                    SolanaWeb3Utils(self.rpc_url)
                    .w3.get_balance(Pubkey.from_string(self.wallet.address))
                    .value
                )
            elif self.chain_type == NetworkTypes.LIGHTNING:
                lnpay_client = LNPayClient(
                    self.rpc_url_private,
                    self.wallet.main_key,
                    self.fund_manager_address,
                )
                return lnpay_client.get_balance()
            raise Exception("Invalid chain type")
        except Exception as e:
            logging.exception(
                f"Error getting wallet balance for {self.chain_name} error is {e}"
            )
            return 0

    @property
    def has_enough_fees(self):
        if self.get_wallet_balance() > self.gas_price * self.enough_fee_multiplier:
            return True
        logging.warning(f"Chain {self.chain_name} has insufficient fees in wallet")
        return False

    @property
    def gas_price(self):
        if not self.is_active or not self.rpc_url_private:
            return self.max_gas_price + 1

        try:
            return Web3Utils(self.rpc_url, self.poa).get_gas_price()
        except:  # noqa: E722
            logging.exception(f"Error getting gas price for {self.chain_name}")
            return self.max_gas_price + 1


class AbstractGlobalSettings(models.Model):
    class Meta:
        abstract = True

    index = models.CharField(max_length=255, unique=True)
    value = models.TextField()

    @classmethod
    def set(cls, index: str, value: str):
        return cls.objects.update_or_create(index=index, defaults={"value": value})

    @classmethod
    def get(cls, index: str, default: str = None):
        try:
            return cls.objects.get(index=index).value
        except cls.DoesNotExist as e:
            if default is not None:
                obj, _ = cls.set(index, default)
                return obj.value
            raise e


class Sponsor(models.Model):
    name = models.CharField(max_length=255, unique=True)
    link = models.URLField(max_length=255)
    description = models.TextField(blank=True, null=True)
    # TODO: image
