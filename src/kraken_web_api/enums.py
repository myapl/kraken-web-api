from enum import Enum, auto


class DictResponse(Enum):
    """ Response type """
    connectionID = auto()
    channelID = auto()
    channelName = auto()


class SubscriptionType(Enum):
    book = auto()
    ohlc = auto()
    openOrders = auto()
    ownTrades = auto()
    spread = auto()
    ticker = auto()
    trade = auto()


class ConnectionStatus(Enum):
    online = auto()


class ChannelStatus(Enum):
    subscribed = auto()
    unsubscribed = auto()
