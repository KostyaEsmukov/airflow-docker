import datetime
import re


def type_timedelta(ctx, param, value):
    if not isinstance(value, str):
        raise TypeError("timedelta should have type=str")

    match = re.match(r"^(-)?(\d+)([dhms])$", value)
    if match is None:
        raise ValueError(fr"timedelta should match `\d+[dhms]`, got `{value}`")

    has_neg_sign, value, unit = match.groups()
    value = int(value)
    value *= {
        # fmt: off
        "s": 1,
        "m": 60,
        "h": 60 * 60,
        "d": 60 * 60 * 24,
        # fmt: on
    }[unit]
    value *= -1 if has_neg_sign else 1
    return datetime.timedelta(seconds=value)
