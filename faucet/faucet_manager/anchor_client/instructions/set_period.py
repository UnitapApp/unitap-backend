from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class SetPeriodArgs(typing.TypedDict):
    period: int


layout = borsh.CStruct("period" / borsh.I64)


class SetPeriodAccounts(typing.TypedDict):
    lock_account: Pubkey
    owner: Pubkey


def set_period(
    args: SetPeriodArgs,
    accounts: SetPeriodAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["lock_account"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"z/\x1e\xb1]\xb9\r\xbc"
    encoded_args = layout.build(
        {
            "period": args["period"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
