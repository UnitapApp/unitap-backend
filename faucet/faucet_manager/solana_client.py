import logging
from typing import Sequence, Tuple
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.system_program import transfer, TransferParams
from solana.transaction import Transaction
from solana.rpc.api import Client
from solana.exceptions import SolanaExceptionBase
from solana.rpc.core import RPCException, RPCNoResultException


class SolanaClient:
    def __init__(self, rpc_client: Client, signer: Keypair) -> None:
        self.rpc_client = rpc_client
        self.signer = signer

    def call_program(self, instruction):
        txn = Transaction().add(instruction)

        try:
            return self.rpc_client.send_transaction(txn, self.signer).value
        except SolanaExceptionBase as exc:
            logging.error(exc.error_msg)
        except RPCException as exc:
            logging.error(exc)
        except RPCNoResultException as exc:
            logging.error(exc)
        return False

    def transfer_lamports(self, sender: Pubkey, receiver: Pubkey, amount: int):
        instruction = transfer(
            TransferParams(from_pubkey=sender, to_pubkey=receiver, lamports=amount)
        )
        txn = Transaction().add(instruction)

        try:
            return self.rpc_client.send_transaction(txn, self.signer).value
        except SolanaExceptionBase as exc:
            logging.error(exc.error_msg)
        except RPCException as exc:
            logging.error(exc)
        except RPCNoResultException as exc:
            logging.error(exc)
        return False

    def transfer_many_lamports(
        self, sender: Pubkey, receivers: Sequence[Tuple[Pubkey, int]]
    ):
        txn = Transaction()
        for rec in receivers:
            instruction = transfer(
                TransferParams(from_pubkey=sender, to_pubkey=rec[0], lamports=rec[1])
            )
            txn.add(instruction)

        try:
            return self.rpc_client.send_transaction(txn, self.signer).value
        except SolanaExceptionBase as exc:
            logging.error(exc.error_msg)
        except RPCException as exc:
            logging.error(exc)
        except RPCNoResultException as exc:
            logging.error(exc)
        return False
