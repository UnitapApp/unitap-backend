from .utility_helpers import get_request


class LNPayLnTx:
    """
    A class used for LnTx API Functions

    Learn more at https://docs.lnpay.co
    """

    def __init__(self, tx_id):
        """
        Parameters
        ----------
        tx_id (str) : The LNPay transaction id (ex. lntx_tVompfuizfryXznKhc38J8)
        """

        self.tx_id = tx_id

    def get_info(self):
        """
        Gets the invoice information for the `tx_id` set in the `__init__` of this class.

        Returns
        -------
        LnTx (Lightning Invoice) Object
        https://docs.lnpay.co/lntx/

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
        return get_request('lntx/{}'.format(self.tx_id))
