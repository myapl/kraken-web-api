
from decimal import Decimal
import json
from typing import Dict, List
from kraken_web_api.enums import DictResponse

from kraken_web_api.exceptions import BookDataHandlingException, InvalidJsonException
from kraken_web_api.model.channel import Channel
from kraken_web_api.model.order_book import OrderBook
from kraken_web_api.model.price import Price
from kraken_web_api.model.connection import SocketConnection


class Handler:
    """ Handle responses from kraken """

    @staticmethod
    def handle_message(message: str) -> object:
        """ Create object from json data """
        try:
            obj = json.loads(message)
            if isinstance(obj, List):
                return Handler._handle_list_object(obj)
            if isinstance(obj, Dict):
                return Handler._handle_dict_object(obj)
        except Exception as e:
            raise InvalidJsonException("Incorrect JSON data from Kraken: %s", e)
        return None

    @staticmethod
    def _handle_dict_object(data_dict: Dict) -> object:
        """ Handle respons in Dict format """
        if DictResponse.connectionID.name in data_dict:
            return SocketConnection.from_dict(data_dict)
        if DictResponse.channelID.name in data_dict:
            return Channel.from_dict(data_dict)
        return None

    @staticmethod
    def _handle_list_object(data_list: List) -> object:
        # subscription_id = data_list[0]
        book = OrderBook()
        return Handler.handle_book_data(data_list, book)

    @staticmethod
    def handle_book_data(data_list: List, book: OrderBook) -> OrderBook:
        # recieved a book init message
        if "as" in data_list[1] or "bs" in data_list[1]:
            return Handler._init_new_book(data_list)
        # recieved a book update message
        if "a" in data_list[1] or "b" in data_list[1]:
            return Handler._update_book(data_list, book)
        raise BookDataHandlingException("Can't handle book data: %s", data_list)

    @staticmethod
    def _init_new_book(data: List) -> OrderBook:
        book = OrderBook(data[0], data[-2], data[-1], [], [])
        asks = data[1]["as"]
        for ask in asks:
            price = Price(Decimal(ask[0]), Decimal(ask[1]), Decimal(ask[2]))
            book.asks.append(price)
        bids = data[1]["bs"]
        for bid in bids:
            price = Price(Decimal(bid[0]), Decimal(bid[1]), Decimal(bid[2]))
            book.bids.append(price)
        return book

    @staticmethod
    def _update_book(data: List, order_book: OrderBook) -> OrderBook:
        if "a" in data[1]:
            order_book.asks = Handler._update_order_book_price(data[1]["a"], order_book.asks)
        if "b" in data[1]:
            order_book.bids = Handler._update_order_book_price(data[1]["b"], order_book.bids)
        order_book.symbol = data[-1]
        order_book.count = data[-2]
        return order_book

    @staticmethod
    def _update_order_book_price(data: List, prices: List[Price]):
        for record in data:
            price_object = Price(Decimal(record[0]), Decimal(record[1]), Decimal(record[2]))
            # price = [p for p in prices if p.price == price_object.price]
            # if len(price) == 0:
            #     prices.append(price_object)
            #     continue
            # if price_object.volume == 0.0:
            #     prices.remove(price[0])
            #     continue
            # price[0].volume = price_object.volume
            # price[0].timestamp = price_object.timestamp
            prices.append(price_object)
        return prices
