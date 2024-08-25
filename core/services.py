"""
Contains the Cloudflare Image service which handles the API exchanges
"""
from django.conf import settings

import requests


class ApiException(Exception):
    """
    Exception raised by Cloudflare Images API
    """

    pass


class CloudflareImagesService:
    """
    API client for Cloudflare Images
    """

    def __init__(self):
        """
        Loads the configuration
        """
        self.account_id = settings.CLOUDFLARE_IMAGES_ACCOUNT_ID
        self.api_token = settings.CLOUDFLARE_IMAGES_API_TOKEN
        self.account_hash = settings.CLOUDFLARE_IMAGES_ACCOUNT_HASH
        self.api_timeout = 60
        self.domain = None

    def upload(self, file):
        """
        Uploads a file and return its name, otherwise raise an exception
        """
        url = "https://api.cloudflare.com/client/v4/accounts/{}/images/v1".format(
            self.account_id
        )

        headers = {"Authorization": "Bearer {}".format(self.api_token)}

        files = {"file": file}

        response = requests.post(
            url, headers=headers, timeout=self.api_timeout, files=files
        )

        status_code = response.status_code
        if status_code != 200:
            raise ApiException(response.content)

        response_body = response.json()
        return response_body.get("result").get("id")

    def get_url(self, name, variant):
        """
        Returns the public URL for the given image ID
        """

        if self.domain:
            return "https://{}/cdn-cgi/imagedelivery/{}/{}/{}".format(
                self.domain, self.account_hash, name, variant
            )

        return "https://imagedelivery.net/{}/{}/{}".format(
            self.account_hash, name, variant
        )

    def open(self, name, variant=None):
        """
        Retrieves a file and return its content, otherwise raise an exception
        """

        url = self.get_url(name, variant or "public")

        response = requests.get(url, timeout=self.api_timeout)

        status_code = response.status_code
        if status_code != 200:
            raise ApiException(response.content)
        
        return response.content

    def delete(self, name):
        """
        Deletes a file if it exists, otherwise raise an exception
        """

        url = "https://api.cloudflare.com/client/v4/accounts/{}/images/v1/{}".format(
            self.account_id, name
        )

        headers = {"Authorization": "Bearer {}".format(self.api_token)}

        response = requests.delete(
            url, timeout=self.api_timeout, headers=headers
        )

        status_code = response.status_code
        if status_code != 200:
            raise ApiException(str(response.text))