import base64
import datetime
import json
import time

import ed25519
import pytz
import requests
from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from eth_account import Account
from eth_account.messages import encode_defunct, encode_typed_data


def verify_signature_eth_scheme(address, message, signature):
    try:
        digest = encode_defunct(text=message)
        signer = Account.recover_message(digest, signature=signature)
        if signer == address:
            return True
        else:
            return False
    except Exception as e:
        print("error in verify_signature_eth_scheme: ", e)
        return False


def verify_login_signature(address, message, signature):
    if (
        message["message"]["message"] != "Unitap Sign In"
        or message["message"]["URI"] != "https://unitap.app"
    ):
        return False

    timestamp = datetime.datetime.fromisoformat(
        message["message"]["IssuedAt"].replace("Z", "+00:00")
    )
    current_time = datetime.datetime.now(pytz.utc)
    if current_time - timestamp > datetime.timedelta(minutes=5):
        return False

    hashed_message = encode_typed_data(full_message=message)

    try:
        signer = Account.recover_message(hashed_message, signature=signature)
        if signer == address:
            return True
        else:
            return False
    except Exception as e:
        print("error in verify_login_signature: ", e)
        return False


class BrightIDSoulboundAPIInterface:
    def __init__(self, app) -> None:
        self.app = app

    def create_verification_link(self, contextId):
        return f"https://app.brightid.org/link-verification/http:%2F\
        %2Fnode.brightid.org/{self.app}/{str(contextId).lower()}"

    def create_qr_content(self, contextId):
        return f"brightid://link-verification/http:%2f%2fnode.bright\
        id.org/{self.app}/{str(contextId).lower()}"  # TODO

    def get_verification_status(self, context_id, verification):
        if verification == "BrightID" or verification == "Meet":
            verification_type = "BrightID"
        elif verification == "Aura":
            verification_type = "Aura"
        else:
            raise ValueError({"verification_status": "Invalid verification type"})

        # get list of context ids from brightId
        endpoint = f"https://aura-node.brightid.org/brightid/v5/veri\
        fications/{self.app}/{context_id}?verification={verification_type}"
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
    UserProfile = apps.get_model("authentication", "UserProfile")

    # Check if the string matches the required format
    validator = RegexValidator(
        regex=r"^(?=.*[a-zA-Z])([\w.@+-]{4,150})$",
        message="Username must be more than 3 characters, contain at \
            least one letter, and only contain letters, digits and @/./+/-/_.",
    )

    try:
        validator(username)
    except ValidationError:
        return (
            False,
            "Username must be more than 3 characters, contain at least one \
                letter, and only contain letters, digits and @/./+/-/_.",
            "validation_error",
        )

    # Check if the string is not already in use
    if UserProfile.objects.filter(username=username).exists():
        return False, f"The username {username} is already in use.", "already_in_use"

    return True, f"{username} is available.", "success"
