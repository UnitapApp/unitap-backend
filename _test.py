from web3 import Web3

# from eth_multicall import Multicall, Call
from simple_multicall import Multicall
def prize_pool_trigger():
    def get_nft_holders_multicall(token_ids, web3, nft_contract):
         
            multicall = Multicall(w3=web3,custom_address='0xeefba1e63905ef1d7acba5a8513c70307c1ce441',custom_abi='[{"constant":true,"inputs":[],"name":"getCurrentBlockTimestamp","outputs":[{"name":"timestamp","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"components":[{"name":"target","type":"address"},{"name":"callData","type":"bytes"}],"name":"calls","type":"tuple[]"}],"name":"aggregate","outputs":[{"name":"blockNumber","type":"uint256"},{"name":"returnData","type":"bytes[]"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getLastBlockHash","outputs":[{"name":"blockHash","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"addr","type":"address"}],"name":"getEthBalance","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getCurrentBlockDifficulty","outputs":[{"name":"difficulty","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getCurrentBlockGasLimit","outputs":[{"name":"gaslimit","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getCurrentBlockCoinbase","outputs":[{"name":"coinbase","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"blockNumber","type":"uint256"}],"name":"getBlockHash","outputs":[{"name":"blockHash","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"}]')
            calls = [
                multicall.create_call(nft_contract, "ownerOf", [token_id])
                for token_id in token_ids
            ]
            
            results = multicall.call(calls)
           
            return results
        
    RPC_URL = "https://rpc.public.curie.radiumblock.co/http/ethereum"
    web3 = Web3(Web3.HTTPProvider(RPC_URL))

    if web3.is_connected():
        print("Connected to RPC")
    else:
        print("Failed to connect to RPC")

    contract_address = "0x23826Fd930916718a98A21FF170088FBb4C30803"
    contract_abi = [
        {
            "inputs": [
                {"internalType": "uint256", "name": "tokenId", "type": "uint256"}
            ],
            "name": "ownerOf",
            "outputs": [{"internalType": "address", "name": "", "type": "address"}],
            "stateMutability": "view",
            "type": "function",
        },
    ]
    nft_contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    holders = {}
    batch_size = 100
    token_id = 0

    while True:
        # Generate token_ids batch
        token_ids = list(range(token_id, token_id + batch_size))

        try:
            res = get_nft_holders_multicall(token_ids, web3, nft_contract)
            results = res[1]
            print(f"Fetched {len(results)} results", "block number = ", res[0])
            for i, result in enumerate(results):
                token_id = token_ids[i]
                holder = result[12:32].hex()
                if holder in holders:
                    holders[holder][0] += 1
                    holders[holder][1].append(token_id)
                else:
                    holders[holder] = [1, [token_id]]
            token_id += batch_size

        except Exception as e:
            # print(f'Error while fetching token IDs {token_ids}: {e}')
            batch_size = batch_size // 2
            if batch_size == 1:
                break    
    
    
    
    
    for holder in holders:
        print(f'{holder} has {holders[holder][0]} NFTs. {holders[holder][1]}')
    print('Total holders:', len(holders))
    return True




prize_pool_trigger()