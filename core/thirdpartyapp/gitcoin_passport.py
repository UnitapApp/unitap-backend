import logging

from core.request_helper import RequestException, RequestHelper
from core.thirdpartyapp import config
from authentication.models import GitcoinPassportConnection


class GitcoinPassportRequestError(RequestException):
    pass


class GitcoinPassport:
    requests = RequestHelper(
        base_url=config.GITCOIN_PASSPORT_BASE_URL,
    )
    scorer_id = config.GITCOIN_PASSPORT_SCORER_ID
    paths = {
        "submit-passport": "registry/submit-passport",
        "get-score": f"registry/score/{scorer_id}",
    }

    @property
    def headers(self):
        return {
            "Content-Type": "application/json",
            "X-API-Key": config.GITCOIN_PASSPORT_API_KEY,
        }

    def submit_passport(self, address: str) -> None | str:
        """submit new address to gitcoin passport account
        :param address: address that want to add

        :return: user gitcoin passport score could be None
        """
        path = self.paths.get("submit-passport")
        data = {
            "address": address,
            "scorer_id": self.scorer_id,
        }
        try:
            res = self.requests.post(path=path, json=data, headers=self.headers)
        except RequestException as e:
            logging.error(f"error in gitcoin-passport occurred: {e}")
            return None

        score = res.get("score")
        return score

    def get_score(self, address: str) -> None | tuple:
        """get address gitcoin passport total score and stamp scores
        :param address: address that already register in gitcoin passport account
        :return: tuple first elem is total_score second is dict {stamp_name: score}
        """
        path = f'{self.paths.get("get-score")}/{address}'
        try:
            res = self.requests.get(path=path, headers=self.headers)
        except RequestException as e:
            logging.error(f"error in gitcoin-passport occurred: {e}")
            return None
        return res.get("score"), res.get("stamp_scores")
    
    def get_connection(self, user_profile) -> bool:
        return GitcoinPassportConnection.is_connected(user_profile=user_profile)
