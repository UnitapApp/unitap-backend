from core.utils import Web3Utils

from .constants import ERC20_TOKENTAP_ABI


class TokentapContractClient:
    def __init__(self, token_distribution) -> None:
        self.token_distribution = token_distribution
        self.web3_utils = Web3Utils(
            self.token_distribution.chain.rpc_url_private,
            self.token_distribution.chain.poa,
        )
        abi = ERC20_TOKENTAP_ABI
        self.web3_utils.set_contract(self.token_distribution.contract, abi)
        self.web3_utils.set_account(self.token_distribution.chain.wallet.private_key)

    def get_distribution(self):
        func = self.web3_utils.contract.functions.distributions(
            self.token_distribution.distribution_id
        )
        output = self.web3_utils.contract_call(func)
        return self.__analyze_distirbution(output)

    def __analyze_distirbution(self, output):
        distributions_abi = [
            item
            for item in self.web3_utils.contract.abi
            if item.get("name") == "distributions"
        ]
        assert len(distributions_abi) == 1, "The distributions' abi not found"
        distributions_abi = distributions_abi[0]
        result = {}
        for index, item in enumerate(distributions_abi["outputs"]):
            result[item["name"]] = output[index]
        return result

    def get_token_distributed_log(self, receipt):
        return self.web3_utils.contract.events.TokenDistributed().process_receipt(
            receipt, errors=self.web3_utils.LOG_DISCARD
        )[0]
