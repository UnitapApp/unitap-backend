import logging

from core.request_helper import RequestException, RequestHelper
from core.thirdpartyapp import config


class ZoraUtil:
    request = RequestHelper(base_url=config.ZORA_BASE_URL)
    paths = {"get-address-token-transfer": "api/v2/addresses/{address}/token-transfers"}

    def __init__(self) -> None:
        self.session = self.request.get_session()

    @property
    def headers(self):
        return {"accept: application/json"}

    def get_tx(self, nft_address: str, address: str):
        params = {
            "type": "ERC-20,ERC-721,ERC-1155",
            "filter": "to",
            "token": nft_address,
        }
        try:
            res = self.request.get(
                path=self.paths.get("get-address-token-transfer").format(
                    address=address
                ),
                session=self.session,
                headers=self.headers,
                params=params,
            )
            return res.json()
        except RequestException as e:
            logging.error(f"Could not get token info from zora: {str(e)}")
            return None
