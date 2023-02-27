# from eth_account.messages import encode_defunct


def verify_signature_eth_scheme(address, signed_message):
    # decrypt signed message using Ethereum signature scheme.
    # message = encode_defunct(text=address)

    return True


import requests


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
        print("endpoint: ", endpoint)
        bright_response = requests.get(endpoint)
        # decode response
        bright_response = bright_response.json()
        print("bright_response: ", bright_response)

        try:
            if bright_response["data"] is not None:
                return True, bright_response["data"]["contextIds"]
            else:
                return False, None
        except KeyError:
            return False, None


BRIGHTID_SOULDBOUND_INTERFACE = BrightIDSoulboundAPIInterface("unitapTest")
