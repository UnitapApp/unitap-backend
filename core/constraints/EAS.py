import json.decoder
import logging
from abc import abstractmethod

from core.constraints.abstract import (
    ConstraintApp,
    ConstraintParam,
    ConstraintVerification,
)
from core.thirdpartyapp import EASUtils
from core.utils import Web3Utils


class AttestingABC(ConstraintVerification):
    app_name = ConstraintApp.ENS.value
    _param_keys = [
        ConstraintParam.CHAIN,
        ConstraintParam.ADDRESS,
        ConstraintParam.KEY,
        ConstraintParam.VALUE,
        ConstraintParam.EAS_SCHEMA_ID,
    ]

    @abstractmethod
    def check_attest(
        self,
        eas_utils: EASUtils,
        param_address: str,
        schema_id: str,
        user_address: str,
        key: str,
        value: str,
    ):
        raise NotImplementedError("You must implement this function")

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import Chain

        chain_pk = self.param_values.get(ConstraintParam.CHAIN.name)
        param_address = Web3Utils.to_checksum_address(
            self.param_values.get(ConstraintParam.ADDRESS.name)
        )
        schema_id = self.param_values.get(ConstraintParam.EAS_SCHEMA_ID.name)
        key = self.param_values.get(ConstraintParam.KEY.name)
        value = self.param_values.get(ConstraintParam.VALUE.name)
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass

        try:
            chain = Chain.objects.get(pk=chain_pk)
        except Chain.DoesNotExist:
            logging.error(f"chain with pk {chain_pk} not exists.")
            return False
        eas_utils = EASUtils(chain.chain_name)
        user_addresses = self.user_addresses
        for address in user_addresses:
            if self.check_attest(
                eas_utils,
                param_address,
                schema_id,
                Web3Utils.to_checksum_address(address),
                key,
                value,
            ):
                return True
        return False


class BeAttestedBy(AttestingABC):
    def check_attest(
        self,
        eas_utils: EASUtils,
        param_address: str,
        schema_id: str,
        user_address: str,
        key: str,
        value: str,
    ):
        return eas_utils.check_eas_event(
            attester=param_address,
            recipient=user_address,
            schema_id=schema_id,
            key=key,
            value=value,
        )


class Attest(AttestingABC):
    def check_attest(
        self,
        eas_utils: EASUtils,
        param_address: str,
        schema_id: str,
        user_address: str,
        key: str,
        value: str,
    ):
        return eas_utils.check_eas_event(
            attester=user_address,
            recipient=param_address,
            schema_id=schema_id,
            key=key,
            value=value,
        )
