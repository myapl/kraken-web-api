import dataclasses
from decimal import Decimal
from enum import Enum
import inspect
from typing import Dict


def from_dict_to_dataclass(cls, data):
    dict = {}
    for key, val in inspect.signature(cls).parameters.items():
        if val.annotation == Decimal:
            dict[key] = Decimal(data.get(key, val.default))
        else:
            dict[key] = data.get(key, val.default)
    return cls(**dict)


def from_dataclass_to_dict(instance) -> Dict[str, str]:
    result_dict: dict = dict()
    for key, val in inspect.signature(type(instance)).parameters.items():
        value = getattr(instance, key)
        if value is not None:
            if isinstance(value, Enum):
                result_dict[key] = value.name
                continue
            if dataclasses.is_dataclass(value):
                result_dict[key] = from_dataclass_to_dict(value)
                continue
            result_dict[key] = value
    return result_dict
