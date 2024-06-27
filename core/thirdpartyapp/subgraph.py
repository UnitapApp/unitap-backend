import logging
from collections import defaultdict

from core.request_helper import RequestException, RequestHelper
from core.thirdpartyapp import config
from core.utils import Web3Utils


class Subgraph:
    requests = RequestHelper(config.SUBGRAPH_BASE_URL)
    path = {"unitap_pass": "query/73675/unitap-pass-eth/version/latest"}

    def __init__(self):
        self.session = self.requests.get_session()

    def __del__(self):
        self.session.close()

    @staticmethod
    def get_current_block_number():
        from core.models import Chain

        eth_chain = Chain.objects.get(chain_id=1)
        w3 = Web3Utils(eth_chain.rpc_url_private)
        current_block_number = w3.get_current_block()
        return current_block_number

    def send_post_request(self, path, query, vars, **kwargs):
        try:
            return self.requests.post(
                path=path,
                json={"query": query, "variables": vars},
                session=self.session,
                **kwargs,
            )
        except RequestException:
            logging.error("Could not connect to subgraph API")

    def get_unitap_pass_holders(self, first=1000) -> dict[str : set[str]]:
        """get unitap pass holders
        :return: {'owner_id':{'unitap_pass_id'}}
        """

        count = 0
        holders = defaultdict(set)
        current_block_number = self.get_current_block_number()
        query = """
        query GetNFTHolders($first: Int, $skip: Int, $block_number: Int) {
            nfts (first: $first, skip: $skip, block: {number: $number}) {
                tokenId,
                owner
            }
        }
        """
        vars = {"first": first, "block_number": current_block_number - 1}

        while True:
            res = self.send_post_request(
                self.path.get("unitap_pass"), query=query, vars=vars
            )
            match res:
                case None:
                    return {}
                case {"data": {"nfts": nfts}} if len(nfts) == 0:
                    return holders
                case {"data": {"nfts": nfts}}:
                    for item in nfts:
                        count += 1
                        holders[item["owner"]].add(item["tokenId"])
