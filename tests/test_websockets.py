import json
import logging
from unittest.mock import MagicMock, patch
import pytest
from websockets.client import WebSocketClientProtocol

from kraken_web_api.enums import ConnectionStatus
from kraken_web_api.model.connection import SocketConnection
from kraken_web_api.model.order_book import OrderBook
from kraken_web_api.websocket import WebSocket


class AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration


class TestWebsocket:
    def setup_method(self):
        self.ws_client = WebSocket(name="TestWebSocketClient", socket_log_level=logging.NOTSET)

    @pytest.mark.asyncio
    @patch("kraken_web_api.websocket.WebSocket._send_public")
    @patch("kraken_web_api.websocket.WebSocket._get_public_connection")
    async def test_orders_book_subscribe(self, mock_get_public_connection, mock_send_public):
        mock_get_public_connection.return_value = SocketConnection(
            connectionID="123",
            event="event",
            status=ConnectionStatus.online,
            version="1.0.0",
            websocket=WebSocketClientProtocol()
        )
        mock_send_public.return_value = None
        subscription_obj = {
            "event": "subscribe",
            "subscription": {
                "name": "book",
                "depth": 10,
            },
            "pair": ["ETH/BTC"]
        }
        await self.ws_client.subscribe_orders_book(subscription_obj['pair'][0],
                                                   subscription_obj['subscription']['depth'])
        assert mock_get_public_connection.called
        assert mock_send_public.assert_called_once
        assert mock_send_public.call_args.args[0] == json.dumps(subscription_obj)

    @pytest.mark.asyncio
    @patch("kraken_web_api.websocket.Handler")
    async def test_recieve_order_book_change(self, handler_mock):
        expected_book = OrderBook(channelID=1234)
        handler_mock.handle_message.return_value = expected_book
        resp = ['']
        self.ws_client._on_orderbook_changed = MagicMock()
        await self.ws_client._recieve(AsyncIterator(resp))
        books = [b for b in self.ws_client.order_books if b.channelID == expected_book.channelID]
        assert handler_mock.handle_message.called
        assert len(books) > 0
        assert self.ws_client._on_orderbook_changed.called
