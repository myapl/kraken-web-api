
from dataclasses import dataclass
from decimal import Decimal
from typing import Tuple


@dataclass(unsafe_hash=True)
class TickerData:
    ask: Tuple[Decimal, int, Decimal]
    bid: Tuple[Decimal, int, Decimal]
    close: Tuple[Decimal, Decimal]
    volume: Tuple[Decimal, Decimal]
    average_price: Tuple[Decimal, Decimal]
    trades: Tuple[int, int]
    low_price: Tuple[Decimal, Decimal]
    high_price: Tuple[Decimal, Decimal]
    open_price: Tuple[Decimal, Decimal]


@dataclass(unsafe_hash=True)
class Ticker:
    channelID: int
    data: TickerData
    channelName: str
    pair: str
