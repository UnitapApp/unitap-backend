# from .utility_helpers import post_request

__version__ = '0.1.0'

__VERSION__ = 'py' + __version__
__ENDPOINT_URL__ = 'https://lnpay.co/v1/'
__DEFAULT_WAK__ = ''
__PUBLIC_API_KEY__ = ''


def initialize(public_api_key, default_wak=None, params=None):
    """
    LNPay module initialization function required for interacting with the LNPay API.

    Parameters
    ----------
    public_api_key (str): Account public key from https://lnpay.co/dashboard/developers
    default_wak (str, optional): Default Wallet Access Key to use for a specific wallet when creating a `LNPayWallet`.
    params (Object): Object representing additional parameters to set globally. Example: {'endpoint_url': 'https://lnpay.co/v1/'}
    """

    if params is None:
        params = {}

    print('initializing lnpay..')

    global __VERSION__
    global __PUBLIC_API_KEY__
    global __ENDPOINT_URL__
    global __DEFAULT_WAK__

    __VERSION__ = 'py' + __version__
    __PUBLIC_API_KEY__ = public_api_key
    __ENDPOINT_URL__ = params.get('endpoint_url', __ENDPOINT_URL__)
    __DEFAULT_WAK__ = default_wak

# def create_wallet(params):
#     return post_request('wallet', params)
