import typing
from anchorpy.error import ProgramError


class MaxCapExceed(ProgramError):
    def __init__(self) -> None:
        super().__init__(6000, "PERIODIC_MAX_CAP_EXCEEDED")

    code = 6000
    name = "MaxCapExceed"
    msg = "PERIODIC_MAX_CAP_EXCEEDED"


class InvalidValue(ProgramError):
    def __init__(self) -> None:
        super().__init__(6001, "INVALID_VALUE")

    code = 6001
    name = "InvalidValue"
    msg = "INVALID_VALUE"


CustomError = typing.Union[MaxCapExceed, InvalidValue]
CUSTOM_ERROR_MAP: dict[int, CustomError] = {
    6000: MaxCapExceed(),
    6001: InvalidValue(),

}


def from_code(code: int) -> typing.Optional[CustomError]:
    maybe_err = CUSTOM_ERROR_MAP.get(code)
    if maybe_err is None:
        return None
    return maybe_err
