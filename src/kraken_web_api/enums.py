from enum import Enum, auto


class DictResponse(Enum):
    """ Response type """
    connectionID = auto()
    channelID = auto()
    channelName = auto()


class ConnectionStatus(Enum):
    online = auto()
