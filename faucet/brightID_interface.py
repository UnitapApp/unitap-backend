import requests


class BrightIDInterface:

    def __init__(self, app_name):
        self.app_name = app_name

    def get_verification_link(self, context_id, network="app"):
        return f"https://{network}.brightid.org/link-verification/{self.app_name}/{context_id}"

    def get_verification_status(self, context_id, network="node"):
        response = requests.get(
            f'http://{network}.brightid.org/brightid/'
            f'v6/verifications/{self.app_name}/{context_id}'
        ).json()
        if 'error' in response:
            return False
        return True
