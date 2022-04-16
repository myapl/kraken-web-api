
from dataclasses import dataclass

from kraken_web_api.enums import SubscriptionType


@dataclass(unsafe_hash=True)
class Subscription:
    name: SubscriptionType
    token: str = ''
    depth: int = 10
    interval: int = 0
