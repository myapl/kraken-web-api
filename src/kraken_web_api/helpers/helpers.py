from decimal import Decimal
import inspect


def from_dict_to_dataclass(cls, data):
    dict = {}
    for key, val in inspect.signature(cls).parameters.items():
        if val.annotation == Decimal:
            dict[key] = Decimal(data.get(key, val.default))
        else:
            dict[key] = data.get(key, val.default)
    return cls(**dict)
