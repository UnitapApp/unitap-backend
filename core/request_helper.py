import requests


class RequestException(requests.HTTPError):
    pass


class RequestHelper:
    _sessions = {}

    def __init__(self, base_url: None | str = None):
        self.base_url = base_url

    def _get_url(self, path: None | str) -> str:
        if not path:
            return self.base_url
        return f"{self.base_url}/{path}" if self.base_url else path

    def get(
        self,
        path: str,
        *,
        params: None | tuple | dict = None,
        headers: None | dict = None,
        timeout: None | int = 5,
        session: None | requests.Session = None,
    ) -> dict:
        try:
            url = self._get_url(path)
            if session is None:
                res = requests.get(
                    url=url, params=params, headers=headers, timeout=timeout
                )
            else:
                res = session.get(
                    url=url, params=params, headers=headers, timeout=timeout
                )
            res.raise_for_status()
            return res.json()
        except requests.RequestException as e:
            raise RequestException(e)

    def post(
        self,
        path: str,
        *,
        params: None | tuple = None,
        headers: None | dict = None,
        timeout: None | int = 5,
        data: None | dict = None,
        json: None | dict = None,
        session: None | requests.Session = None,
    ) -> dict:
        try:
            url = self._get_url(path)
            if session is None:
                res = requests.post(
                    url=url,
                    params=params,
                    headers=headers,
                    data=data,
                    json=json,
                    timeout=timeout,
                )
            else:
                res = session.post(
                    url=url,
                    params=params,
                    headers=headers,
                    data=data,
                    json=json,
                    timeout=timeout,
                )
            res.raise_for_status()
            return res.json()
        except requests.RequestException as e:
            raise RequestException(e)

    def get_session(self):
        session = requests.Session()
        return session
