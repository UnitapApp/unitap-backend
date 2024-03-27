import json
import logging

from core.request_helper import RequestException, RequestHelper
from core.thirdpartyapp.config import EAS_BASE_URL


class EASUtils:
    types_ = {
        "BigNumber": lambda number: int(number, 16),
        "string": str,
        "bool": lambda x: x,
    }

    def __init__(self, chain_name: str) -> None:
        self.requests = RequestHelper(EAS_BASE_URL.get(chain_name.lower()))

    @property
    def headers(self) -> dict:
        return {"content-type": "application/json"}

    def _check_decoded_data(self, data: dict, key: str, value: list | dict) -> bool:
        data_value = data.get("value")
        if data.get("name") == key and isinstance(data_value, dict):
            return self._check_decoded_data(data_value, key, value)
        if data.get("name") == key and isinstance(data_value, list):
            for val in data_value:
                if isinstance(val, dict):
                    res = self._check_decoded_data(val, key, value)
                else:
                    res = self.types_.get(data.get("type"), str)(val) == value
                if res:
                    return True
            return False
        if data.get("hex"):
            return self.types_.get(data.get("type"))(data.get("hex")) == value
        if isinstance(data_value, dict):
            return False
        return self.types_.get(data.get("type"), str)(data_value) == value

    def get_eas_event(
        self, attester: str, recipient: str, schema_id: str
    ) -> None | list[dict]:
        """ """
        query = """
            query Attestations($where: AttestationWhereInput, $take: Int) {
              attestations(where: $where, take: $take) {
                attester
                isOffchain
                decodedDataJson
              }
            }
        """
        variables = {
            "where": {
                "attester": {"equals": attester},
                "recipient": {"equals": recipient},
                "schemaId": {"equals": schema_id},
            }
        }
        body = {"query": query, "variables": variables}
        try:
            res = self.requests.post(path="", json=body, headers=self.headers)
        except RequestException as e:
            logging.error(f"can not send request properly. {e}")
            return None
        attestations = res.get("data").get("attestations")
        return attestations

    def check_eas_event(
        self, attester: str, recipient: str, schema_id: str, key: str, value
    ) -> bool:
        attestations = self.get_eas_event(attester, recipient, schema_id)
        if not attestations:
            return False
        for attestation in attestations:
            decoded_data = json.loads(attestation.get("decodedDataJson"))
            for data in decoded_data:
                if self._check_decoded_data(data, key, value):
                    return True
        return False
