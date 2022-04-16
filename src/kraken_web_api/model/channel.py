from dataclasses import dataclass
from typing import Dict

from kraken_web_api.enums import ChannelStatus
from kraken_web_api.helpers.helpers import from_dict_to_dataclass
from kraken_web_api.model.subscription import Subscription


@dataclass(unsafe_hash=True)
class Channel:
    """ Keep track of subscription channel """
    channelName: str
    event: str
    status: ChannelStatus
    subscription: Subscription
    pair: str = ""
    channelID: int = 0

    @staticmethod
    def from_dict(dict: Dict):
        return Channel(
            channelName=dict['channelName'],
            event=dict['event'],
            status=ChannelStatus[dict['status']],
            subscription=from_dict_to_dataclass(Subscription, dict['subscription']),
            pair=dict['pair'],
            channelID=int(dict['channelID']),
        )
