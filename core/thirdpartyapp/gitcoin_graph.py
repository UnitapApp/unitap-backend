import json
import logging

import requests
import zstandard as zstd


class GitcoinGraph:
    URL = "https://grants-stack-indexer-v2.gitcoin.co/graphql"

    def send_post_request(self, json_data):
        try:
            res = requests.post(
                self.URL, headers={"Content-Type": "application/json"}, json=json_data
            )
            return json.loads(zstd.decompress(res.content, 1073741824).decode())
        except Exception as e:
            print(e)
            logging.error("Could not connect to gitcoin graph API")
