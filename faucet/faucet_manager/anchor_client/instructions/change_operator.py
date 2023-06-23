from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class ChangeOperatorArgs(typing.TypedDict):
    new_operator: Pubkey


layout = borsh.CStruct("new_operator" / BorshPubkey)


class ChangeOperatorAccounts(typing.TypedDict):
    lock_account: Pubkey
    owner: Pubkey


def change_operator(
    args: ChangeOperatorArgs,
    accounts: ChangeOperatorAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["lock_account"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xbc\xfb\xa9=\xb6JZ\xf6"
    encoded_args = layout.build(
        {
            "new_operator": args["new_operator"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
