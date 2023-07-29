from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class ChangeOwnerArgs(typing.TypedDict):
    new_owner: Pubkey


layout = borsh.CStruct("new_owner" / BorshPubkey)


class ChangeOwnerAccounts(typing.TypedDict):
    lock_account: Pubkey
    owner: Pubkey


def change_owner(
    args: ChangeOwnerArgs,
    accounts: ChangeOwnerAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["lock_account"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"m((Z\xe0x\xc1\xb8"
    encoded_args = layout.build(
        {
            "new_owner": args["new_owner"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
