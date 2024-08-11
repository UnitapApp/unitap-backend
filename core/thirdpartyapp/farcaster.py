import logging

from core.request_helper import RequestException, RequestHelper
from core.thirdpartyapp import config
from core.utils import Web3Utils


class FarcasterUtil:
    requests = RequestHelper(config.FARCASTER_BASE_URL)
    paths = {
        "cast": "cast",
        "get_bulk_profile_by_address": "user/bulk-by-address",
        "get_bulk_profile_by_fid": "user/bulk",
        "get_bulk_channel": "channel/bulk",
    }

    def __init__(self):
        self.session = self.requests.get_session()

    def __del__(self):
        self.session.close()

    @property
    def headers(self):
        return {"api_key": config.FARCASTER_API_KEY, "accept": "application/json"}

    def _get_profile(self, address: str) -> dict:
        address = Web3Utils.to_checksum_address(address)
        params = {"addresses": address}
        path = self.paths.get("get_bulk_profile_by_address")
        res = self.requests.get(
            path=path, headers=self.headers, params=params, session=self.session
        )
        return res[address.lower()][0]

    def _get_bulk_profile(self, addresses: list[str]) -> dict:
        path = self.paths.get("get_bulk_profile_by_address")
        addresses = map(Web3Utils.to_checksum_address, addresses)
        params = {"addresses": ",".join(addresses)}
        res = self.requests.get(
            path=path, session=self.session, params=params, headers=self.headers
        )
        return res

    def get_address_fid(self, address: str) -> None | str:
        """return fid for given EVM address.
        :param address: address that we want to get fid
        :return: return fid
        """
        try:
            res = self._get_profile(address)
            return res["fid"]
        except (RequestException, KeyError):
            logging.error("user profile for this address not found")
            return None

    def get_follower_number(self, address: str) -> None | int:
        """return follower number for given EVM address.
        :param address: address that we want to get fid
        :return: follower number
        """
        try:
            res = self._get_profile(address)
            return res["follower_count"]
        except (RequestException, KeyError):
            logging.error("user profile for this address not found")
            return None

    def _get_reacts_on_casts(self, cast_hash: str) -> dict:
        path = self.paths.get("cast")
        params = {"identifier": cast_hash, "type": "hash"}

        res = self.requests.get(
            path=path,
            headers=self.headers,
            session=self.session,
            params=params,
        )
        return res["reactions"]

    def _get_fids_from_addresses(self, addreses: list[str]) -> list[str]:
        profiles = self._get_bulk_profile(addreses)
        return set([profiles[address][0]["fid"] for address in profiles])

    def did_liked_cast(self, cast_hash: str, addresses: list[str]) -> bool:
        """
        :param cast_hash: cast must be liked
        :param addresses: list of EVM address
        :return: True or False
        """
        try:
            fids = self._get_fids_from_addresses(addresses)
            likes = self._get_reacts_on_casts(cast_hash)["likes"]
            for like in likes:
                if like["fid"] in fids:
                    return True
        except (RequestException, KeyError, AttributeError) as e:
            logging.error(f"user not found, error: {e}")
        return False

    def did_recast_cast(self, cast_hash: str, addresses: list[str]) -> bool:
        """
        :param cast_hash: cast must be recast
        :param addresses: list of EVM address
        :return: True or False
        """
        try:
            fids = self._get_fids_from_addresses(addresses)
            recasts = self._get_reacts_on_casts(cast_hash)["recasts"]
            for recast in recasts:
                if recast["fid"] in fids:
                    return True
        except (RequestException, KeyError, AttributeError) as e:
            logging.error(f"user not found, error: {e}")
        return False

    def _get_followers_status(self, user_fid: str, follower_fids: str | list) -> bool:
        if isinstance(follower_fids, list):
            follower_fids = ",".join(follower_fids)
        path = self.paths.get("get_bulk_profile_by_fid")
        params = {"viewer_fid": user_fid, "fids": follower_fids}
        res = self.requests.get(
            path=path, params=params, session=self.session, headers=self.headers
        )[0]["viewer_context"]["followed_by"]
        return {
            data["fid"]: data["viewer_context"]["following"] for data in res["users"]
        }

    def is_following(self, fid: str, address: str) -> bool:
        """check if address followed fid or not.
        :param fid: fid that must followed
        :param address: address that must following profile_id
        :return: True or False
        """
        try:
            follower_fid = self._get_profile(address)["fid"]
            return self._get_followers_status(follower_fid, fid)
        except (
            RequestException,
            IndexError,
            KeyError,
            AttributeError,
            ValueError,
        ) as e:
            logging.error(f"could not check following status, error: {e}")
        return False

    def be_followed_by(self, fid: str, address: str):
        """check if address be followed by fid.
        :param fid: fid that must followed EVM addr
        :param address: address that must be followed by profile_id
        :return: True or False
        """
        try:
            following_fid = self._get_profile(address)["fid"]
            return self._get_follow_status(fid, following_fid)
        except (
            RequestException,
            IndexError,
            KeyError,
            AttributeError,
            ValueError,
        ) as e:
            logging.error(f"could not check following status, error: {e}")
        return False

    def is_following_channel(self, channel_id: str, addresses: list[str]) -> bool:
        """check if one address is following channel.
        :param channel_id: channel id that must be followed by user
        :param addresses: list of EVM address
        :return: True or False
        """
        path = self.paths.get("get_bulk_channel")
        try:
            fids = self._get_fids_from_addresses(addresses)
            params = {
                "ids": channel_id,
                "type": "id",
            }
            for fid in fids:
                params["viewer_fid"] = fid
                res = self.requests.get(
                    path, session=self.session, params=params, headers=self.headers
                )
                if res.get("channels")[0].get("viewer_context").get("following"):
                    return True
        except (RequestException, KeyError, AttributeError) as e:
            logging.error(f"Channel not found, error: {e}")
        return False

    def is_following_batch(self, fids: list[str], address: str) -> None | dict:
        try:
            follower_fid = self._get_profile(address)["fid"]
            return self._get_follow_status(follower_fid, fids)
        except (
            RequestException,
            IndexError,
            KeyError,
            AttributeError,
            ValueError,
        ) as e:
            logging.error(f"could not check following status, error: {e}")
        return None
