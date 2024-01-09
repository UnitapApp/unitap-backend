import json

import requests


def get_request(location):
    from .lnpay_main import __ENDPOINT_URL__, __PUBLIC_API_KEY__, __VERSION__

    """
    Network utility method for making a GET call to a LNPay endpoint

    Parameters
    ----------
    location (str): URL path requested

    Returns
    -------
    Network response as a JSON Object.
    """
    endpoint = __ENDPOINT_URL__ + location
    headers = {
        "X-Api-Key": __PUBLIC_API_KEY__,
        "X-LNPay-sdk": __VERSION__,
    }

    r = requests.get(url=endpoint, headers=headers)
    return r.json()


def post_request(location, params):
    from .lnpay_main import __ENDPOINT_URL__, __PUBLIC_API_KEY__, __VERSION__

    """
    Network utility method for making a POST call to a LNPay endpoint

    Parameters
    ----------
    location (str): URL path requested
    params (object): the `data` to be POSTed in the network request

    Returns
    -------
    Network response as a JSON Object.
    """

    endpoint = __ENDPOINT_URL__ + location
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": __PUBLIC_API_KEY__,
        "X-LNPay-sdk": __VERSION__,
    }

    data = json.dumps(params)

    r = requests.post(url=endpoint, data=data, headers=headers)
    return r.json()
