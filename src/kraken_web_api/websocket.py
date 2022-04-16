
import asyncio
import json
import logging
from typing import Callable, Set, Optional
from websockets import client

from kraken_web_api.constants import SOCKET_PUBLIC
from kraken_web_api.enums import ConnectionStatus
from kraken_web_api.exceptions import SocketConnectionError
from kraken_web_api.handlers import Handler
from kraken_web_api.model.channel import Channel
from kraken_web_api.model.connection import SocketConnection


class WebSocket:
    def __init__(self, name: str = "KrakenWS",
                 socket_log_level: int = logging.INFO) -> None:
        """ Initialise new kraken websocket client
        Parameters:
            name (str) : Name of the client (for logger)
            socket_log_level (int) : log level for socket inner client (not for kraken WS client)
        """
        self._configure_loggers(name, socket_log_level)
        self.connections: Set[SocketConnection] = set()
        self.channels: Set[Channel] = set()
        self.disconnecting = False
        self.logger.debug("Kraken client has been instantiated")

    async def __aenter__(self):
        await self._connect_socket(SOCKET_PUBLIC)
        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        await self._disconnect_all()

    async def subscribe_orders_book(self, on_update: Callable = None) -> bool:
        """ Subscribe to orders book
        Parameters:
            pair (str) : Trading pair ("NANO/ETH", etc.)
            depth (int) : Book depth (10, 100, 500, etc.)
            on_update (function) : Function to invoke on book updates
        Return:
            result (bool) : Success
        """
        if self._get_public_connection() is None:
            await self._connect_socket(SOCKET_PUBLIC)
        subscription_obj = {
            "event": "subscribe",
            "subscription": {
                "depth": 10,
                "name": "book"
            },
            "pair": ["NANO/ETH"]
        }
        await self._send_public(json.dumps(subscription_obj))
        return True

    async def unsubscribe_all(self):
        """ Unsubscribe all channels """
        pass

    async def _connect_socket(self, socket: str) -> None:
        """ Create new websocket connection
        Parameters:
            socket (str) : websocket uri
        """
        self.logger.debug("Connecting to kraken public websocket: %s", socket)
        websocket = await client.connect(socket)
        if len(websocket.messages) == 0:
            raise SocketConnectionError("Could not connect to kraken websocket: %s", socket)
        message = websocket.messages.pop()
        if isinstance(message, bytes):
            message = message.decode()
        connection = Handler.handle_message(message)
        if not isinstance(connection, SocketConnection):
            raise SocketConnectionError("Unable to handle recieved connection message: %s", socket)
        connection.websocket = websocket
        self.connections.add(connection)
        asyncio.create_task(self._recieve(connection.websocket))
        self.logger.debug("Websocket connection has been created: %s", socket)

    async def _recieve(self, websocket):
        """ Recieve message """
        await asyncio.sleep(0)
        async for message in websocket:
            self.logger.debug("Message recieved: %s", message)
            object = Handler.handle_message(message)
            self._handle_object(object)

    async def _send_public(self, message):
        """ Send a message to websocket """
        connection = self._get_public_connection()
        if connection is not None:
            await connection.websocket.send(message)

    def _handle_object(self, obj: object):
        if isinstance(obj, Channel):
            self.channels.add(obj)
            self.logger.debug("New channel subscribed: %s", obj)

    async def _disconnect_all(self) -> None:
        """ Disconnect all active websocket connections """
        if not self.disconnecting:
            self.disconnecting = True
            for connection in self.connections:
                if connection.status == ConnectionStatus.online:
                    await connection.websocket.close()
                    await asyncio.sleep(2)  # TODO: remove in production
                    self.logger.debug("Socket connection closed: %s", connection.websocket)
            self.connections.clear()
        else:
            while self.disconnecting:
                await asyncio.sleep(0)
        self.disconnecting = False

    def _get_public_connection(self) -> Optional[SocketConnection]:
        """ Get public connection with online status """
        for connection in self.connections:
            if connection.status == ConnectionStatus.online\
               and not connection.is_private:
                return connection
        return None

    def _configure_loggers(self, name: str, socket_log_level: int) -> None:
        """ Configure it's own and websockets.client loggers """
        self.logger = logging.getLogger(name)
        ws_logger = logging.getLogger("websockets.client")
        ws_logger.setLevel(socket_log_level)
