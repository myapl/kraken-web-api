
import asyncio
import json
import logging
from typing import Callable, Dict, List, Set, Optional, Union
from websockets import client

from kraken_web_api.constants import SOCKET_PUBLIC
from kraken_web_api.enums import ChannelStatus, ConnectionStatus, SubscriptionType
from kraken_web_api.exceptions import SocketConnectionError
from kraken_web_api.handlers import Handler
from kraken_web_api.model.channel import Channel
from kraken_web_api.model.connection import SocketConnection
from kraken_web_api.model.order_book import OrderBook
from kraken_web_api.model.price import Price
from kraken_web_api.model.ticker import Ticker
from kraken_web_api.subscribe_creator import SubscribtionRequestCreator, RequestCreator


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
        self.order_books: List[OrderBook] = list()
        self.tickers: List[Ticker] = list()
        self.disconnecting = False
        self.request_creator: RequestCreator = SubscribtionRequestCreator()  # type: ignore
        self._on_orderbook_changed: Optional[Callable] = None
        self._on_ticker_changed: Optional[Callable] = None

        self.logger.debug("Kraken websocket client has been instantiated")

    async def __aenter__(self):
        await self._connect_socket(SOCKET_PUBLIC)
        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        await self.unsubscribe_all()
        await self._disconnect_all()

    async def subscribe_orders_book(self, pair: str, depth: int, on_update: Callable = None) -> None:
        """ Subscribe to orders book
        Parameters:
            pair (str) : Trading pair ("ETH/BTC", etc.)
            depth (int) : Book depth (10, 100, 500, etc.)
            on_update (function) : Function to invoke on book updates
        """
        if self._get_public_connection() is None:
            await self._connect_socket(SOCKET_PUBLIC)
        request = self.request_creator.create(type=SubscriptionType.book,
                                              pair=pair, depth=depth, subscribe=True)
        await self._send_public(json.dumps(request))
        self._on_orderbook_changed = on_update

    async def subscribe_ticker_info(self, pair: str, on_update: Callable = None) -> None:
        """ Ticker information on currency pair. """
        if self._get_public_connection() is None:
            await self._connect_socket(SOCKET_PUBLIC)
        request = self.request_creator.create(type=SubscriptionType.ticker,
                                              pair=pair, subscribe=True)
        await self._send_public(json.dumps(request))
        self._on_ticker_changed = on_update

    async def unsubscribe_all(self) -> None:
        """ Unsubscribe all channels """
        for channel in self.channels:
            if channel.status == ChannelStatus.subscribed:
                await self._unsubscribe_public(channel)

    async def _unsubscribe_public(self, channel: Channel) -> None:
        """ Unsubscribe channel using public connection """
        request = None
        connection = self._get_public_connection()
        if connection is not None:
            if channel.subscription.name == SubscriptionType.book.name:
                request = self._create_unsubscribe_book_request(channel)
            if channel.subscription.name == SubscriptionType.ticker.name:
                pass
            if request is not None:
                await connection.websocket.send(json.dumps(request))

    def _create_unsubscribe_book_request(self, channel: Channel) -> Optional[Dict]:
        books = [b for b in self.order_books if b.channelID == channel.channelID]
        if len(books) > 0:
            return self.request_creator.create(type=SubscriptionType.book,
                                               pair=books[0].symbol, subscribe=False)
        return None

    def _create_unsubscribe_ticker_request(self, channel: Channel) -> Optional[Dict]:
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
        connection = self._handle_connection_message(websocket.messages.pop(), websocket)
        self.connections.add(connection)
        asyncio.create_task(self._recieve(connection.websocket))
        self.logger.debug("Websocket connection has been created: %s", socket)

    async def _recieve(self, websocket) -> None:
        """ Recieve message """
        await asyncio.sleep(0)
        async for message in websocket:
            self.logger.debug("Message recieved: %s", message)
            object = Handler.handle_message(message)
            self._handle_object(object)

    async def _send_public(self, message) -> None:
        """ Send a message to websocket """
        connection = self._get_public_connection()
        if connection is not None:
            await connection.websocket.send(message)

    def _handle_connection_message(self, message: Union[str, bytes],
                                   websocket: client.WebSocketClientProtocol
                                   ) -> SocketConnection:
        """ Handle recieved connection message """
        if isinstance(message, bytes):
            message = message.decode()
        connection = Handler.handle_message(message)
        if not isinstance(connection, SocketConnection):
            raise SocketConnectionError("Unable to handle recieved connection message: %s", message)
        connection.websocket = websocket
        return connection

    def _handle_object(self, obj: object) -> None:
        """ Handle object depending of it's type """
        if isinstance(obj, Channel):
            self._handle_channel(obj)
        if isinstance(obj, OrderBook):
            self._handle_order_book(obj)
        if isinstance(obj, Ticker):
            self._handle_ticker(obj)

    def _handle_ticker(self, ticker: Ticker) -> None:
        tickers = [t for t in self.tickers if t.channelName == ticker.channelName and t.pair == ticker.pair]
        if len(tickers) > 0:
            self.tickers.remove(tickers[0])
        self.tickers.append(ticker)
        if self._on_ticker_changed is not None:
            self._on_ticker_changed()

    def _handle_order_book(self, book: OrderBook) -> None:
        """ Handle recieved book data """
        if book.channelID is not None:
            # new book initialized
            books = [b for b in self.order_books if b.channelID == book.channelID]
            if len(books) > 0:
                books[0] = book
            else:
                self.order_books.append(book)
        else:
            # book data update
            books = [b for b in self.order_books if b.symbol == book.symbol and b.count == book.count]
            if len(books) > 0:
                self._update_book_data(book, books[0])
        if self._on_orderbook_changed is not None:
            self._on_orderbook_changed()
        self.logger.debug("Order book has been updated: %s", book)

    def _update_book_data(self, data: OrderBook, book: OrderBook) -> None:
        if len(data.asks) > 0:
            self._update_book_prices(data.asks, book.asks)
        if len(data.bids) > 0:
            self._update_book_prices(data.bids, book.bids)

    def _update_book_prices(self, data: List[Price], prices: List[Price]):
        for new_price in data:
            price = [p for p in prices if p.price == new_price.price]
            if len(price) == 0:
                prices.append(new_price)
                continue
            if new_price.volume == 0.0:
                prices.remove(price[0])
                continue
            price[0].volume = new_price.volume
            price[0].timestamp = new_price.timestamp

    def _handle_channel(self, channel: Channel) -> None:
        """ Handle channel object recieved """
        if channel.status == ChannelStatus.subscribed:
            self.channels.add(channel)
            self.logger.debug("New channel subscribed: %s", channel)
        else:
            channels = [c for c in self.channels if c.channelID == channel.channelID]
            if len(channels) > 0:
                self.channels.remove(channels[0])
                self.logger.debug("Channel has been unsubscribed: %s", channel)

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
