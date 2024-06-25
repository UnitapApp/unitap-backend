import logging
from core.request_helper import RequestException, RequestHelper
from core.thirdpartyapp import config


def fetch_nft_pass_wallets():
    results = []
    while True:

        requests = RequestHelper()
        session = requests.get_session()
        data = None
        try:
            data = session.post(
                config.NFT_PASS_SUBGRAPH_URL,
                json={
                    "query": "{nfts(first: 1000, skip: "
                    + str(len(results))
                    + ") {id owner tokenId}}"
                },
            ).json()
        except:
            logging.error("Error fetching nft pass wallets")
            break

        if len(data["data"]["nfts"]) == 0:
            break
        for item in data["data"]["nfts"]:
            results.append(item)
        if len(data["data"]["nfts"]) != 1000:
            break

    holders = {}
    for item in results:
        if item["owner"] not in holders:
            holders[item["owner"]] = []
        holders[item["owner"]].append(item)
    session.close()
    return holders
