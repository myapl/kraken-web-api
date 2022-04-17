
from dataclasses import dataclass
from typing import List, Optional

from kraken_web_api.enums import SubscriptionType


@dataclass(unsafe_hash=True)
class Subscription:
    name: SubscriptionType
    token: Optional[str] = None
    depth: Optional[int] = None
    interval: Optional[int] = None


@dataclass(unsafe_hash=True)
class SubscriptionRequest:
    event: str
    subscription: Subscription
    reqid: Optional[int] = None
    pair: Optional[List[str]] = None
