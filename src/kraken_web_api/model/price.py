from dataclasses import dataclass
from decimal import Decimal


@dataclass(unsafe_hash=True)
class Price:
    price: Decimal
    volume: Decimal
    timestamp: Decimal
