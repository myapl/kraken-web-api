import logging

from kraken_web_api.websocket import WebSocket


class TestWebsocket:
    def setup_method(self):
        self.ws_client = WebSocket(
            name="TestWebSocketClient",
            socket_log_level=logging.NOTSET)

    def test_orders_book_subscribe(self):
        assert True
