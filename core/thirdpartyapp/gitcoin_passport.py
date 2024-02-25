from core.request_helper import RequestException, RequestHelper
from core.thirdpartyapp import config


class GitcoinPassportRequestError(RequestException):
    pass


class GitcoinPassport:
    requests = RequestHelper(
        api_key=config.GITCOIN_PASSPORT_API_KEY,
        base_url=config.GITCOIN_PASSPORT_BASE_URL,
    )
    scorer_id = config.GITCOIN_PASSPORT_SCORER_ID
    paths = {
        "submit-passport": "registry/submit-passport",
        "get-score": f"registry/score/{scorer_id}",
    }

    def submit_passport(self, address: str) -> None | str:
        """submit new address to gitcoin passport account
        :param address: address that want to add

        :return: user gitcoin passport score could be None
        """
        session = self.requests.get_session()
        path = self.paths.get("submit-passport")
        data = {
            "address": address,
            "scorer_id": self.scorer_id,
        }
        try:
            res = self.requests.post(session=session, path=path, data=data)
        except RequestException as e:
            raise GitcoinPassportRequestError(e)
        score = res.get("score")
        return score

    def get_score(self, address: str) -> tuple:
        """get address gitcoin passport total score and stamp scores
        :param address: address that already register in gitcoin passport account
        :return: tuple first elem is total_score second is dict {stamp_name: score}
        """
        session = self.requests.get_session()
        path = f'{self.paths.get("get-score")}/{address}'
        try:
            res = self.requests.get(session=session, path=path)
        except RequestException as e:
            raise GitcoinPassportRequestError(e)
        return res.get("score"), res.get("stamp_scores")
