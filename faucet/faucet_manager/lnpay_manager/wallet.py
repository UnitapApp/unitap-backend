from .lnpay_main import __DEFAULT_WAK__
from .utility_helpers import get_request, post_request


class LNPayWallet:
    """
    Class for LNPay Wallet API Functions

    Learn more at docs.lnpay.co
    """

    def __init__(self, access_key_str):
        """
        Parameters
        ----------
        access_key_str (str): Access key for a specific wallet. Optional if `default_wak` is initialized in `LNPay`.
        """

        if access_key_str:
            self.access_key = access_key_str
        elif __DEFAULT_WAK__ is not None:
            self.access_key = __DEFAULT_WAK__
        else:
            raise AttributeError(
                "No wallet access key specified! Set a default, or initialize LNPayWallet with one"
            )

    def get_info(self):
        """
        Get the wallet object which includes current balance.

        https://docs.lnpay.co/wallet/get-balance

        Returns
        -------
        JSON Object representing the response of the LNPay API

        Example:
        ```
        {
          "id": "w_pXHvKoKeKfrv",
          "created_at": 1577600922,
          "updated_at": 1577600922,
          "user_label": "Wallet for ATM",
          "balance": 1000,
          "statusType": {
                "id": 200,
                "type": "wallet",
                "name": "active",
                "display_name": "Active"
            },
        }
        ```
        """
        return get_request("wallet/{}".format(self.access_key))

    def get_transactions(self):
        """
        Get a list of wallet transactions that have been SETTLED.
        This includes only transactions that have an impact on wallet balance.
        These DO NOT include unsettled/unpaid invoices.

        https://docs.lnpay.co/wallet/get-transactions

        Returns
        -------
        List of wallet transactions.
        Example:
        ```
        [
            {
                "id": "wtx_OXWNFNYYY0NsGLwLx7AtcPM",
                "created_at": 1580475159,
                "wallet_id": "w_ALMWRQrSoSf4Qh",
                "num_satoshis": 158,
                "user_label": "asdf",
                "lnTx": {
                    "id": "lntx_hlLn7xArPmew8KKSjqJqy6Vo",
                    "created_at": 1580129586,
                    "updated_at": 1580129586,
                    "dest_pubkey": "033868c219bdb51a33560d854d500fe7d3898a1ad9e05dd89d0007e11313588500",
                    "payment_request": "",
                    "r_hash_decoded": "7e13af679b551d8b0b804c3f0c74b43352c2d4c332ead6d693a8ea0aa6b6beec",
                    "memo": "",
                    "description_hash": "",
                    "num_satoshis": 2,
                    "expiry": 0,
                    "expires_at": null,
                    "payment_preimage": "323550597244415037724d6a436765567a72735875667438626e66754d385547",
                    "settled": 1,
                    "settled_at": 1580129586
                },
                "wtxType": {
                    "id": 30,
                    "layer": "ln",
                    "name": "ln_transfer_in",
                    "display_name": "Transfer In"
                }
            }
        ]
        ```
        """
        return get_request("wallet/{}/transactions".format(self.access_key))

    def create_invoice(self, params):
        """
        Generates an invoice for this wallet.

        https://docs.lnpay.co/wallet/generate-invoice

        Parameters
        ----------
        params (Object): Object representing an invoice request. Example: `{'num_satoshis': 2,'memo': 'Tester'}`

        Returns
        -------
        LnTx Object (https://docs.lnpay.co/lntx/)
        Example:
        ```
        {
          "id": "lntx_IaWG3yS6FB3ZQJDRjXkkkkk",
          "created_at": 1577600922,
          "updated_at": 1577600922,
          "dest_pubkey": "033868c219bdb51a33560d854d500fe7d3898a1ad9e05dd89d0007e11313588500",
          "payment_request": "lnbc10n1pw7l9l3pp5pr2sr8pdt2yjm04am0wktr7cphkt8c3gtlvq8qlgaqw9jsh3d6qsdpj2pshjampd3kzunrfde4jq3npw43k2ap6ypgx7mmjgesh2cm9wscqzpgxqrrss4z9zac6gtpskjkhtdsxjd0m4are599k4ya9al0ktqqf7y70xqt5xs3as53va424nsh2dxumdln3ymm2048550hrj5sw8nw2ajzc9p9l3s97",
          "r_hash_decoded": "f646ff04116d16b7a70e953034b1c7c475c771847eb43e66892039ff5589863b",
          "description_hash": null,
          "memo": "This is a memo",
          "num_satoshis": 11,
          "expiry": 86400,
          "expires_at": 1578992143,
          "payment_preimage": "71566c546f304e70507a486b7561356177426a7535716345713670482f45582b4e4262337a654mmmmm6d673d",
          "settled": 1,
          "settled_at": 1575992143
        }
        ```
        """
        return post_request("wallet/{}/invoice".format(self.access_key), params)

    def pay_invoice(self, params):
        """
        Pay a LN invoice from the specified wallet.

        https://docs.lnpay.co/wallet/pay-invoice

        Parameters
        ----------
        params (Object): Object representing an invoice payment request. Example: `{'payment_request': 'ln....'}`

        Returns
        -------
        Returns invoice payment information if successful or a specific error directly from the Lightning Node.

        Successful example:
        ```
        {
            "id":"wtx_JOhQFFI826owtE51AfFC975c",
            "created_at":1577657602,
            "wallet_id":"w_hkjS9r6mTYeABc",
            "wtxType": {
                "id": 20,
                "layer": "ln",
                "name": "ln_withdrawal",
                "display_name": "LN Withdrawal"
            },
            "num_satoshis":-5,
            "user_label":"Test invoice for docs",
            "lnTx":{
                "id":"lntx_82yveCX2Wn0EkkdyzvyBv",
                "created_at":1577657602,
                "updated_at":1577657602,
                "dest_pubkey":"02c16cca44562b590dd279c942200bdccfd4f990c3a69fad620c10ef2f8228eaff",
                "payment_request":"lnbc50n1p0qjf84pp5f70yqjjvu0z0esf7hksnca44d8j440mk5743qv70ku6jy9ewj8eqdpz23jhxapqd9h8vmmfvdjjqen0wgsxgmmrwvxqyz5vqcqzyssp583w0tugt4scyek2dat72p389lau0j8u9t5qnep29y0c32hyfn8rqrzjqt0pr36g7ke9elfvaqq3wmfey6laun0z8v0lg0nf9fdhdncxsp0y5zxkp5qqnsgqqqqqqquyqqqqqksqrc9qy9qsqzmvy83s8np7yrlqs98ge90tj3wwhfawjtq3cewv4vavmq0p5c4anhkm2aeyzjcvycttfgzwtak7nrrk6e3m3td8g4t8ha06uzzare4cqqne839",
                "r_hash_decoded":"4f9e404a4ce3c4fcc13ebda13c76b569e55abf76a7ab1033cfb73522172e91f2",
                "memo":"Test invoice for docs",
                "num_satoshis":5,
                "expiry":86400,
                "expires_at":1577744002,
                "payment_preimage":"6631394e526f35325135563854574f316651513330527a6e4e47315630795147662f7066466e4276664a773d",
                "settled":1,
                "settled_at":1577657602
            }
        }
        ```

        Failure example:
        ```
        {
            "name":"Bad Request",
            "message":"invoice is already paid",
            "code":0,
            "status":400
        }
        ```
        """
        return post_request("wallet/{}/withdraw".format(self.access_key), params)

    def internal_transfer(self, params):
        """
        Transfer satoshis from source wallet to destination wallet.

        https://docs.lnpay.co/wallet/transfers-between-wallets

        Parameters
        ----------
        params (Object): Object representing a transfer request. Example: `{'dest_wallet_id': 'w_XXX','num_satoshis': 1,'memo': 'Memo'}`

        Returns
        -------
        Transfer execution information.

        Successful example:
        ```
        {
            "wtx_transfer_in":{
                "id":"wtx_aM9r4YEUrwohStWaxW7lDpRs",
                "created_at":1579269413,
                "wallet_id":"w_n743yizWqe43Oz",
                "num_satoshis":1,
                "user_label":"Test transfer",
                "lnTx":null,
                "wtxType":{
                    "id":30,
                    "layer":"ln",
                    "name":"ln_transfer_in",
                    "display_name":"Transfer In"
                }
            }
        },
            "wtx_transfer_out":{
                "id":"wtx_S9okrFLSS9LR97fWkdDfJ6U",
                "created_at":1579269412,
                "wallet_id":"w_hkjS9r6mTYeABc",
                "num_satoshis":-1,
                "user_label":"Test transfer",
                "lnTx":null,
                "wtxType":{
                    "id":40,
                    "layer":"ln",
                    "name":"ln_transfer_out",
                    "display_name":"Transfer Out"
                }
            }
        }
        ```

        Failure example:
        ```
        {
            "name":"Bad Request",
            "message":"insufficient funds",
            "code":0,
            "status":400
        }
        ```
        """
        return post_request("wallet/{}/transfer".format(self.access_key), params)

    def get_lnurl(self, params):
        """
        Generate an LNURL-withdraw link.

        Note: These LNURLs are ONE-TIME use. This is to prevent repeated access to the wallet.

        https://docs.lnpay.co/wallet/lnurl-withdraw

        Parameters
        ----------
        params (Object): Object representing a lnurl withdraw request. Example: `{'num_satoshis': 1,'memo': 'SatsBack'}`

        Returns
        -------
        Generated lnurl object.

        Example:
        ```
        {
            "lnurl":"LNURL1DP68GURN8GHJ7MRWWPSHJTNRDUHHVVF0W4EK2U30WASKCMR9WSHHWC2LFACXUM35DDR5736ZF4HXVS6VGEV8GU6YDE49GC30D3H82UNV94C8YMMRV4EHX0M0W36R66MGD95KS4JGFADRS4ZRFEXK2SN2FFUXUSMHFA98XDZ8D3T9SDECWVHR43"
        }
        ```

        """
        return get_request(
            "wallet/{}/lnurl/withdraw?num_satoshis={}".format(
                self.access_key, params["num_satoshis"]
            )
        )
