import base64
import json
import time
from abc import ABC

import ed25519
import requests


class BaseThirdPartyDriver(ABC):
    pass


class BrightIDConnectionDriver(BaseThirdPartyDriver):
    def __init__(self):
        self.app = "unitap"

    def create_verification_link(self, contextId):
        return f"https://app.brightid.org/link-verification/http:%2F\
        %2Fnode.brightid.org/{self.app}/{str(contextId).lower()}"

    def create_qr_content(self, contextId):
        return f"brightid://link-verification/http:%2f%2fnode.bright\
        id.org/{self.app}/{str(contextId).lower()}"

    def get_meets_verification_status(self, context_id):
        return self._get_verification_status(context_id, "BrightID")

    def get_aura_verification_status(self, context_id):
        return self._get_verification_status(context_id, "Aura")

    def _get_verification_status(self, context_id, verification_type):
        endpoint = f"https://aura-node.brightid.org/brightid/v5/verifications/{self.app}/{context_id}?verification={verification_type}"  # noqa E501

        bright_response = requests.get(endpoint)
        bright_response = bright_response.json()

        try:
            if bright_response["data"] is not None:
                return True, bright_response["data"]["contextIds"]
            else:
                return False, bright_response["errorNum"]
        except KeyError:
            return False, bright_response["errorNum"]

    def check_sponsorship(self, context_id):
        endpoint = (
            f"https://app.brightid.org/node/v5/sponsorships/{str(context_id).lower()}"
        )
        bright_response = requests.get(endpoint)
        bright_response = bright_response.json()

        try:
            if bright_response["data"] is not None:
                if bright_response["data"]["appHasAuthorized"] is True:
                    return True
                else:
                    return False
            else:
                return False
        except KeyError:
            return False, bright_response["errorNum"]

    def sponsor(self, context_id):
        from brightIDfaucet.settings import BRIGHT_PRIVATE_KEY

        endpoint = "https://app.brightid.org/node/v5/operations"
        op = {
            "name": "Sponsor",
            "app": self.app,
            "contextId": str(context_id).lower(),
            "timestamp": int(time.time() * 1000),
            "v": 5,
        }
        signing_key = ed25519.SigningKey(base64.b64decode(BRIGHT_PRIVATE_KEY))
        message = json.dumps(op, sort_keys=True, separators=(",", ":")).encode("ascii")
        sig = signing_key.sign(message)
        op["sig"] = base64.b64encode(sig).decode("ascii")
        r = requests.post(endpoint, json.dumps(op))
        print("res: ", r.json())
        if r.status_code != 200 or "error" in r.json():
            return False
        return True
