import requests
from core.thirdpartyapp import config

def fetch_nft_pass_wallets():
    results = []
    while True:
        try:
            response = requests.post(
                config.NFT_PASS_SUBGRAPH_URL,
                json={"query": "{nfts(first: 1000, skip: " + str(len(results)) + ") {id owner tokenId}}"},
            )
            json = response.json()
            for item in json["data"]["nfts"]:
                results.append(item)
            if len(json["data"]["nfts"]) != 1000:
                break
            if len(json["data"]["nfts"]) == 0:
                break
        except Exception as e:
            print(e)
            break
    holders = {}
    for item in results:
        if item["owner"] not in holders:
            holders[item["owner"]] = []
        holders[item["owner"]].append(item)
    return holders

