import requests
import json
import time
import requests
import base64
import ed25519
from eth_account.messages import encode_defunct
from web3 import Web3
from eth_account import Account


def verify_signature_eth_scheme(address, signature):
    try:
        digest = encode_defunct(text=address)
        signer = Account.recover_message(digest, signature=signature)
        if signer == address:
            return True
        else:
            return False
    except Exception as e:
        print("error in verify_signature_eth_scheme: ", e)
        return False


class BrightIDSoulboundAPIInterface:
    def __init__(self, app) -> None:
        self.app = app

    def get_verification_status(self, context_id, verification):
        if verification == "BrightID" or verification == "Meet":
            verification_type = "BrightID"
        elif verification == "Aura":
            verification_type = "Aura"
        else:
            raise ValueError("Invalid verification type")

        # get list of context ids from brightId
        endpoint = f"https://aura-node.brightid.org/brightid/v5/verifications/{self.app}/{context_id}?verification={verification_type}"
        # print("endpoint: ", endpoint)
        bright_response = requests.get(endpoint)
        # decode response
        bright_response = bright_response.json()
        # print("bright_response: ", bright_response)

        try:
            if bright_response["data"] is not None:
                return True, bright_response["data"]["contextIds"]
            else:
                return False, None
        except KeyError:
            return False, None

    def check_sponsorship(self, context_id):
        endpoint = (
            f"https://app.brightid.org/node/v5/sponsorships/{context_id}"
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
            return False

    def sponsor(self, context_id):
        from brightIDfaucet.settings import BRIGHT_PRIVATE_KEY

        URL = "https://app.brightid.org/node/v5/operations"
        op = {
            "name": "Sponsor",
            "app": self.app,
            # "appUserId": context_id,
            "contextId": str(context_id).lower(),
            "timestamp": int(time.time() * 1000),
            "v": 5,
        }
        signing_key = ed25519.SigningKey(base64.b64decode(BRIGHT_PRIVATE_KEY))
        message = json.dumps(op, sort_keys=True, separators=(",", ":")).encode("ascii")
        sig = signing_key.sign(message)
        op["sig"] = base64.b64encode(sig).decode("ascii")
        r = requests.post(URL, json.dumps(op))
        print("res: ", r.json())
        if r.status_code != 200 or "error" in r.json():
            return False
        return True


BRIGHTID_SOULDBOUND_INTERFACE = BrightIDSoulboundAPIInterface("unitapTest")
