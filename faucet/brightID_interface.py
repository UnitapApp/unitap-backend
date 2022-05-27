import requests
import json
import time
import requests
import base64
import ed25519

from brightIDfaucet.private import BRIGHT_PRIVATE_KEY


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
        
        # sponsor the user
        self.sponsor(context_id, network)
        
        return True
    
    def sponsor(self, context_id, network="node"):
        URL = f'http://{network}.brightid.org/brightid/v6/operations'
        op = {
            'name': 'Sponsor',
            'app': self.app_name,
            'appUserId': context_id,
            'timestamp': int(time.time()*1000),
            'v': 6
        }
        signing_key = ed25519.SigningKey(base64.b64decode(BRIGHT_PRIVATE_KEY))
        message = json.dumps(op, sort_keys=True, separators=(',', ':')).encode('ascii')
        sig = signing_key.sign(message)
        op['sig'] = base64.b64encode(sig).decode('ascii')
        r = requests.post(URL, json.dumps(op))
        if r.status_code != 200 or "error" in r.json():
            return False
        return True