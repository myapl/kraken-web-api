
from dataclasses import dataclass
from typing import Dict
from websockets.client import WebSocketClientProtocol

from kraken_web_api.enums import ConnectionStatus


@dataclass(unsafe_hash=True)
class SocketConnection:
    connectionID: str
    event: str
    status: ConnectionStatus
    version: str
    websocket: WebSocketClientProtocol
    is_private: bool = False

    @staticmethod
    def from_dict(dict: Dict):
        return SocketConnection(
            connectionID=dict['connectionID'],
            event=dict['event'],
            status=ConnectionStatus[dict['status']],
            version=dict['version'],
            websocket=WebSocketClientProtocol()
        )
