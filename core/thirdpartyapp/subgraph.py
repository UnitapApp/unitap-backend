import logging
from core.request_helper import RequestException, RequestHelper
from core.thirdpartyapp import config


def fetch_nft_pass_wallets():
    count = 0
    requests = RequestHelper()
    session = requests.get_session()
    holders = {}
    while True:
        try:
            data = session.post(
                config.NFT_PASS_SUBGRAPH_URL,
                json={
                    "query": "{nfts(first: 1000, skip: "
                    + str(count)
                    + ") {id owner tokenId}}"
                },
            ).json()
        except RequestException as e:
            logging.error(f"Error fetching nft pass wallets from subgraph : {e}")
            holders = {}
            break
        else:
            if len(data["data"]["nfts"]) == 0:
                break
            for item in data["data"]["nfts"]:
                count += 1
                if item["owner"] not in holders:
                    holders[item["owner"]] = []
                holders[item["owner"]].append(item['tokenId'])
            if len(data["data"]["nfts"]) != 1000:
                break
    session.close()
    return holders
