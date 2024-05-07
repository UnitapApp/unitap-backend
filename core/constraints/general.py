import csv
from abc import ABC, abstractmethod

import rest_framework.exceptions
from django.db.models.functions import Lower

from core.constraints.abstract import ConstraintParam, ConstraintVerification
from core.utils import InvalidAddressException, NFTClient, TokenClient


class HasNFTVerification(ConstraintVerification):
    _param_keys = [
        ConstraintParam.CHAIN,
        ConstraintParam.ADDRESS,
        ConstraintParam.MINIMUM,
    ]

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs):
        from core.models import Chain

        chain_pk = self.param_values[ConstraintParam.CHAIN.name]
        collection_address = self.param_values[ConstraintParam.ADDRESS.name]
        minimum = self.param_values[ConstraintParam.MINIMUM.name]

        chain = Chain.objects.get(pk=chain_pk)
        nft_client = NFTClient(chain=chain, contract=collection_address)

        user_wallets = self.user_profile.wallets.filter(wallet_type=chain.chain_type)

        token_count = 0
        try:
            for wallet in user_wallets:
                token_count += nft_client.get_number_of_tokens(
                    nft_client.to_checksum_address(wallet.address)
                )
        except InvalidAddressException as e:
            raise rest_framework.exceptions.ValidationError(e)

        return token_count >= int(minimum)


class ABCTokenVerification(ConstraintVerification, ABC):
    _param_keys = [
        ConstraintParam.CHAIN,
        ConstraintParam.ADDRESS,
        ConstraintParam.MINIMUM,
    ]

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    @abstractmethod
    def get_amount(
        self, user_address: str, token_address: str, token_client: TokenClient
    ) -> int:
        raise NotImplementedError("you must implement this function")

    def is_observed(self, *args, **kwargs):
        from core.models import Chain

        chain_pk = self.param_values[ConstraintParam.CHAIN.name]
        token_address = self.param_values[ConstraintParam.ADDRESS.name]
        minimum = self.param_values[ConstraintParam.MINIMUM.name]

        if token_address[:4] == "0x00":
            token_address = None

        chain = Chain.objects.get(pk=chain_pk)

        user_wallets = self.user_profile.wallets.filter(wallet_type=chain.chain_type)

        token_client = TokenClient(chain=chain, contract=token_address)

        token_count = 0

        try:
            for wallet in user_wallets:
                token_count += self.get_amount(
                    wallet.address, token_address, token_client
                )
        except InvalidAddressException as e:
            raise rest_framework.exceptions.ValidationError(e)

        return token_count >= int(minimum)


class HasTokenVerification(ABCTokenVerification):
    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def get_amount(
        self, user_address: str, token_address: str, token_client: TokenClient
    ) -> int:
        if token_address is None:
            return token_client.get_native_token_balance(user_address)
        return token_client.get_non_native_token_balance(user_address)


class HasTokenTransferVerification(ABCTokenVerification):
    _param_keys = [
        ConstraintParam.CHAIN,
        ConstraintParam.ADDRESS,
        ConstraintParam.MINIMUM,
    ]

    def get_amount(
        self, user_address: str, token_address: str, token_client: TokenClient
    ) -> int:
        if token_address is None:
            return 0
        return token_client.get_non_native_token_transfer_amount(user_address)


class AllowListVerification(ConstraintVerification):
    _param_keys = [ConstraintParam.CSV_FILE]

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs):
        file_path = self.param_values[ConstraintParam.CSV_FILE.name]
        self.allow_list = []
        with open(file_path, newline="") as f:
            reader = csv.reader(f)
            data = list(reader)
            self.allow_list = [a[0].lower() for a in data]
            user_wallets = self.user_profile.wallets.values_list(
                Lower("address"), flat=True
            )
            for wallet in user_wallets:
                if wallet in self.allow_list:
                    return True
            return False
