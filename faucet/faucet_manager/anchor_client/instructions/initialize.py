from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class InitializeArgs(typing.TypedDict):
    owner: Pubkey
    operator: Pubkey


layout = borsh.CStruct("owner" / BorshPubkey, "operator" / BorshPubkey)


class InitializeAccounts(typing.TypedDict):
    lock_account: Pubkey
    owner: Pubkey


def initialize(
    args: InitializeArgs,
    accounts: InitializeAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["lock_account"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xaf\xafm\x1f\r\x98\x9b\xed"
    encoded_args = layout.build(
        {
            "owner": args["owner"],
            "operator": args["operator"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
