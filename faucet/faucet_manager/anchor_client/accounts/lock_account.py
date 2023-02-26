import typing
from dataclasses import dataclass
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import borsh_construct as borsh
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from anchorpy.borsh_extension import BorshPubkey
from ..program_id import PROGRAM_ID


class LockAccountJSON(typing.TypedDict):
    initialized: bool
    owner: str
    operator: str
    period: int
    round: int
    round_amount: int
    max_round_amount: int


@dataclass
class LockAccount:
    discriminator: typing.ClassVar = b"\xdf@G|\xffVv\xc0"
    layout: typing.ClassVar = borsh.CStruct(
        "initialized" / borsh.Bool,
        "owner" / BorshPubkey,
        "operator" / BorshPubkey,
        "period" / borsh.I64,
        "round" / borsh.I64,
        "round_amount" / borsh.U64,
        "max_round_amount" / borsh.U64,
    )
    initialized: bool
    owner: Pubkey
    operator: Pubkey
    period: int
    round: int
    round_amount: int
    max_round_amount: int

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["LockAccount"]:
        resp = await conn.get_account_info(address, commitment=commitment)
        info = resp.value
        if info is None:
            return None
        if info.owner != program_id:
            raise ValueError("Account does not belong to this program")
        bytes_data = info.data
        return cls.decode(bytes_data)

    @classmethod
    async def fetch_multiple(
        cls,
        conn: AsyncClient,
        addresses: list[Pubkey],
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.List[typing.Optional["LockAccount"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["LockAccount"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "LockAccount":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = LockAccount.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            initialized=dec.initialized,
            owner=dec.owner,
            operator=dec.operator,
            period=dec.period,
            round=dec.round,
            round_amount=dec.round_amount,
            max_round_amount=dec.max_round_amount,
        )

    def to_json(self) -> LockAccountJSON:
        return {
            "initialized": self.initialized,
            "owner": str(self.owner),
            "operator": str(self.operator),
            "period": self.period,
            "round": self.round,
            "round_amount": self.round_amount,
            "max_round_amount": self.max_round_amount,
        }

    @classmethod
    def from_json(cls, obj: LockAccountJSON) -> "LockAccount":
        return cls(
            initialized=obj["initialized"],
            owner=Pubkey.from_string(obj["owner"]),
            operator=Pubkey.from_string(obj["operator"]),
            period=obj["period"],
            round=obj["round"],
            round_amount=obj["round_amount"],
            max_round_amount=obj["max_round_amount"],
        )
