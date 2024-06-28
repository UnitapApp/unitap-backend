import logging

from core.request_helper import RequestException, RequestHelper
from core.thirdpartyapp.config import LENS_BASE_URL
from core.utils import Web3Utils


class LensUtil:
    requests = RequestHelper(base_url=LENS_BASE_URL)

    def __init__(self) -> None:
        self.session = self.requests.get_session()

    def __del__(self):
        self.session.close()

    @property
    def headers(self):
        return {
            "user-agent": "spectaql",
        }

    def _pagination(self, cursor: str, json: dict, variables: dict) -> dict:
        variables["request"]["cursor"] = cursor
        json["variables"] = variables
        return json

    def _post_request(self, json: dict) -> dict:
        return self.requests.post(
            path="", json=json, headers=self.headers, session=self.session
        )

    def _get_profile_info(self, address: str):
        query = """
        query DefaultProfile($request: DefaultProfileRequest!) {
          defaultProfile(request: $request) {
            stats {
              followers
              posts
            }
            id
          }
        }
        """
        variables = {"request": {"for": address}}
        json = {
            "query": query,
            "variables": variables,
        }
        try:
            res = self._post_request(json=json)
            profile_info = res.get("data").get("defaultProfile")
            return profile_info
        except RequestException as e:
            logging.error(f"connection lost, {e}")
            return None

        except (KeyError, TypeError, AttributeError):
            return None

    def _get_profile_id(self, address: str):
        address = Web3Utils.to_checksum_address(address)
        try:
            profile_info = self._get_profile_info(address)
            return profile_info.get("id")
        except (KeyError, TypeError, AttributeError):
            return None

    def get_profile_id(self, address: str) -> None | str:
        """get EVM address profile_id in lens
        :param address: EVM address
        :return: None if profile_id not exists else str
        """
        return self._get_profile_id(address)

    def _get_follow_status(self, profile_id: str, follower_id: str) -> bool:
        query = """
                query FollowStatusBulk($request: FollowStatusBulkRequest!) {
                  followStatusBulk(request: $request) {
                    status {
                      value
                      isFinalisedOnchain
                    }
                  }
                }
            """
        try:
            variables = {
                "request": {
                    "followInfos": [{"follower": follower_id, "profileId": profile_id}]
                }
            }
            json = {"query": query, "variables": variables}
            res = self._post_request(json)
            return bool(
                res.get("data").get("followStatusBulk")[0].get("status").get("value")
                and res.get("data")
                .get("followStatusBulk")[0]
                .get("status")
                .get("isFinalisedOnchain")
            )

        except RequestException as e:
            logging.error(f"connection lost, {e.args}")
            return False
        except (KeyError, TypeError, AttributeError) as e:
            logging.error(f"{e}")
            return False

    def is_following(self, profile_id: str, address: str) -> bool:
        """check if address followed profile_id or not
        :param profile_id: profile_id that must followed
        :param address: address that must following profile_id
        :return: True or False
        """
        address = Web3Utils.to_checksum_address(address)
        address_profile_id = self._get_profile_id(address=address)
        return bool(
            address_profile_id
            and self._get_follow_status(
                profile_id=profile_id, follower_id=address_profile_id
            )
        )

    def be_followed_by(self, profile_id: str, address: str):
        """check if address be followed by profile_id
        :param profile_id: profile_id that must followed EVM addr
        :param address: address that must be followed by profile_id
        :return: True or False
        """
        address = Web3Utils.to_checksum_address(address)
        address_profile_id = self._get_profile_id(address=address)
        return bool(
            address_profile_id
            and self._get_follow_status(
                profile_id=address_profile_id, follower_id=profile_id
            )
        )

    def did_mirror_on_publication(self, publication_id: str, address) -> bool:
        """check if address mirrored post
        :param publication_id: post_id mirrored
        :param address: address that mirrored post
        :return: True or False
        """
        query = """
                query Publications($request: PublicationsRequest!) {
                  publications(request: $request) {
                    items {
                      ... on Mirror {
                        by {
                          id
                          ownedBy {
                            address
                          }
                        }
                      }
                    }
                  }
                }
            """
        json = {"query": query}
        profile_id = self._get_profile_id(address)
        variables = {
            "request": {"where": {"mirrorOn": publication_id, "from": profile_id}}
        }
        json["variables"] = variables
        try:
            res = self._post_request(json=json)
        except RequestException as e:
            logging.error(f"connection lost, {e}")
            return False

        return bool(res.get("data").get("publications").get("items"))

    def did_collect_publication(self, publication_id: str, address: str) -> bool:
        """check if address collected publication
        :param publication_id: post_id mirrored
        :param address: address that mirrored post
        :return: True or False
        """
        query = """
        query Publications($request: PublicationsRequest!) {
          publications(request: $request) {
            items {
              ... on Post {
                id
              }
              ... on Comment {
                id
              }
              ... on Mirror {
                id
              }
              ... on Quote {
                id
              }
            }
          }
        }
        """
        json = {"query": query}
        profile_id = self._get_profile_id(address)
        variables = {
            "request": {
                "where": {
                    "withOpenActions": [{"category": "COLLECT"}],
                    "actedBy": profile_id,
                    "publicationIds": publication_id,
                }
            }
        }
        json["variables"] = variables
        try:
            res = self._post_request(json=json)
        except RequestException as e:
            logging.error(f"connection lost, {e}")
            return False

        return bool(res.get("data").get("publications").get("items"))

    def get_follower_number(self, address: str) -> None | int:
        """return follower number
        :param address:
        :return: int
        """
        try:
            profile_info = self._get_profile_info(address)
            return profile_info.get("stats").get("followers")
        except RequestException as e:
            logging.error(f"connection lost, {e}")
            return None

        except (KeyError, TypeError, AttributeError):
            return None

    def get_post_number(self, address: str) -> None | int:
        """return post number
        :param address:
        :return: int
        """
        try:
            profile_info = self._get_profile_info(address)
            return profile_info.get("stats").get("posts")
        except RequestException as e:
            logging.error(f"connection lost, {e}")
            return None

        except (KeyError, TypeError, AttributeError):
            return None
