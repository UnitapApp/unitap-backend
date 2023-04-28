import requests
import json
import time
import requests
import base64
import ed25519

# http://node.brightid.org/brightid/v6/verifications/unitap/53735351-050d-4284-a362-620b1992be9a


class BrightIDInterface:
    def __init__(self, app_name):
        self.app_name = app_name

    def get_verification_link(self, context_id, network="app"):
        return f"https://{network}.brightid.org/link-verification/http:%2F%2Fnode.brightid.org/{self.app_name}/{context_id}"

    def _is_unique(self, context_id):
        """
        return a tuple, the first element is a boolean indicating if the user is unique
        the second element is the list of context ids that the user has been verified by
        """

        url = f"https://app.brightid.org/node/v5/verifications/{self.app_name}/{context_id}"
        response = requests.get(url).json()

        if "error" in response.keys():
            return False
        data = response.get("data")
        if not data:
            return False
        return data.get("unique", False), data.get("contextIds", [])

    def get_verification_status(self, context_id, network="node"):
        unique, contextIds = self._is_unique(context_id)

        if unique:
            # if the given context id is unique, then it is verified
            return True
        elif not contextIds:
            # if the given context id is not unique,
            # but it has no more context ids to check,
            #  then it is not verified
            return False
        elif self._is_unique(contextIds[0])[0]:
            # the first element in the contextIds list must be unique to be verified
            return True
        else:
            return False

    def sponsor(self, context_id, network="app"):
        from brightIDfaucet.settings import BRIGHT_PRIVATE_KEY

        URL = "https://app.brightid.org/node/v5/operations"

        op = {
            "v": 5,
            "name": "Sponsor",
            "app": self.app_name,
            # "appUserId": context_id,
            "contextId": context_id,
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
