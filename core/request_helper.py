from contextlib import contextmanager

import requests


class RequestException(requests.HTTPError):
    pass


class RequestHelper:
    def __init__(self, api_key: None | str = None, base_url: None | str = None):
        self.api_key = api_key
        self.base_url = base_url

    def _get_url(self, path: None | str) -> str:
        return f"{self.base_url}/{path}" if not self.base_url else path

    def _get_headers(self, headers: None | dict) -> dict:
        headers = headers or dict()
        headers["Content-Type"] = "application/json"
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        return headers

    def get(
        self,
        session: requests.Session,
        path: str,
        *,
        params: None | tuple = None,
        headers: None | dict = None,
        timeout: None | int = 5,
    ) -> dict:
        try:
            url = self._get_url(path)
            _headers = self._get_headers(headers)
            res = session.get(url=url, params=params, headers=_headers, timeout=timeout)
            res.raise_for_status()
            return res.json()
        except requests.RequestException as e:
            raise RequestException(e)

    def post(
        self,
        session: requests.Session,
        path: str,
        *,
        params: None | tuple = None,
        headers: None | dict = None,
        timeout: None | int = 5,
        data: None | dict = None,
    ) -> dict:
        try:
            url = self._get_url(path)
            _headers = self._get_headers(headers)
            res = session.post(
                url=url, params=params, headers=_headers, data=data, timeout=timeout
            )
            res.raise_for_status()
            return res.json()
        except requests.RequestException as e:
            raise RequestException(e)

    @contextmanager
    def get_session(self):
        session = requests.Session()
        try:
            yield session
        finally:
            session.close()
