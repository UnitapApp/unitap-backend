import json
import logging

import requests
import zstd


class GitcoinGraph:
    URL = "https://grants-stack-indexer-v2.gitcoin.co/graphql"

    def send_post_request(self, json_data):
        try:
            res = requests.post(
                self.URL, headers={"Content-Type": "application/json"}, json=json_data
            )
            print(res.content.startswith(b"\x28\xb5\x2f\xfd"))
            print()
            return json.loads(zstd.decompress(res.content))
        except Exception as e:
            print(e)
            logging.error("Could not connect to gitcoin graph API")
