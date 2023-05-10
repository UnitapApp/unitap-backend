from authentication.models import UserProfile
import requests
import json
import time
import requests
import base64
import ed25519
from eth_account.messages import encode_defunct
from web3 import Web3
from eth_account import Account
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


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

    def create_verification_link(self, contextId):
        return f"https://app.brightid.org/link-verification/http:%2F%2Fnode.brightid.org/{self.app}/{str(contextId).lower()}"

    def create_qr_content(self, contextId):
        return f"brightid://link-verification/http:%2f%2fnode.brightid.org/{self.app}/{str(contextId).lower()}"  # TODO

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


BRIGHTID_SOULDBOUND_INTERFACE = BrightIDSoulboundAPIInterface("unitap")


def is_username_valid_and_available(username):
    # Check if the string matches the required format
    validator = RegexValidator(
        regex=r"^[\w.@+-]{1,150}$",
        message="Username can only contain letters, digits and @/./+/-/_.",
    )

    try:
        validator(username)
    except ValidationError:
        return (
            False,
            "Username can only contain letters, digits and @/./+/-/_.",
            "validation_error",
        )

    # Check if the string is not already in use
    if UserProfile.objects.filter(username=username).exists():
        return False, f"The username {username} is already in use.", "already_in_use"

    return True, f"{username} is available.", "success"
