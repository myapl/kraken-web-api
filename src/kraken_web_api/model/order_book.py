from dataclasses import dataclass, field
from typing import List, Optional

from kraken_web_api.model.price import Price


@dataclass(unsafe_hash=True)
class OrderBook:
    channelID: Optional[int] = None
    count: Optional[str] = None
    symbol: Optional[str] = None
    asks: List[Price] = field(default_factory=list)
    bids: List[Price] = field(default_factory=list)
