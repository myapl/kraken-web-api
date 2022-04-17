
from decimal import Decimal
from unittest.mock import patch
import pytest

from kraken_web_api.exceptions import InvalidJsonException
from kraken_web_api.handlers import Handler
from kraken_web_api.model.order_book import OrderBook
from kraken_web_api.model.price import Price


# DATA_LIST = '[2128,{"as":[["0.000702680","5.09240716","1650138439.570743"],["0.000702690","8.30209792","1650138431.584508"],'\
#             '["0.000702800","75.34738000","1650136717.634559"],["0.000704000","576.85005775","1650138427.602444"],'\
#             '["0.000704010","11.66061559","1650138372.871539"],["0.000704600","20.60000000","1650138428.371404"],'\
#             '["0.000704950","30.40000000","1650138402.439233"],["0.000705560","70.00000000","1650136802.115268"],'\
#             '["0.000706170","13.46546135","1650136806.111192"],["0.000706720","416.00000000","1650132966.347460"]],'\
#             '"bs":[["0.000700620","521.46800762","1650138439.347806"],["0.000699890","26.60000000","1650138439.544563"],'\
#             '["0.000699590","28.40000000","1650138435.955864"],["0.000699250","70.00000000","1650138426.457273"],'\
#             '["0.000699190","25.90000000","1650137804.420159"],["0.000699130","6.98700000","1650137826.323426"],'\
#             '["0.000698600","1074.71266459","1650138430.877872"],["0.000697620","73.48488570","1650138430.153760"],'\
#             '["0.000695750","476.31709490","1650138426.515436"],["0.000695740","424.00000000","1650138426.453783"]]},'\
#             '"book-10","NANO/ETH"]'

BOOK_INIT_LIST = [2128, {"as": [["0.000702680", "5.09240716", "1650138439.570743"], ["0.000702690", "8.30209792", "1650138431.584508"]],
                         "bs": [["0.000700620", "521.46800762", "1650138439.347806"], ["0.000699890", "26.60000000", "1650138439.544563"]]},
                  "book-10", "NANO/ETH"]

BOOK_BID_UPDATE = [2128, {"b": [["0.000707640", "265.70008036", "1650173638.242924"]], "c": "4140403579"}, "book-10", "NANO/ETH"]
BOOK_ASK_UPDATE = [2128, {"a": [["0.000709420", "173.18000000", "1650173637.897915"]], "c": "3299039756"}, "book-10", "NANO/ETH"]

DATA_LIST_MESSAGE = '[2128,{"as":[["0.000702680","5.09240716","1650138439.570743"],["0.000702690","8.30209792","1650138431.584508"]],\
                    "bs":[["0.000700620","521.46800762","1650138439.347806"],["0.000699890","26.60000000","1650138439.544563"]]},\
                    "book-10","NANO/ETH"]'

DATA_DICT_MESSAGE = '{"channelID":2128,"channelName":"book-10","event":"subscriptionStatus","pair":"NANO/ETH","status":"subscribed",\
                    "subscription":{"depth":10,"name":"book"}}'

EXPECTED_ORDER_BOOK = OrderBook(
                                    2128,
                                    "book-10",
                                    "NANO/ETH",
                                    [
                                        Price(Decimal('0.000702680'), Decimal('5.09240716'), Decimal('1650138439.570743')),
                                        Price(Decimal('0.000702690'), Decimal('8.30209792'), Decimal('1650138431.584508'))
                                    ],
                                    [
                                        Price(Decimal('0.000700620'), Decimal('521.46800762'), Decimal('1650138439.347806')),
                                        Price(Decimal('0.000699890'), Decimal('26.60000000'), Decimal('1650138439.544563'))
                                    ],
                                )

# EXPECTED_ORDER_BOOK = OrderBook(
#                                     "book-10",
#                                     "NANO/ETH",
#                                     [
#                                         Price(0.000702680, 5.09240716, 1650138439.570743),
#                                         Price(0.000702690, 8.30209792, 1650138431.584508)
#                                     ],
#                                     [
#                                         Price(0.000700620, 521.46800762, 1650138439.347806),
#                                         Price(0.000699890, 26.60000000, 1650138439.544563)
#                                     ],
#                                 )


def on_update():
    pass


class TestHandlers:

    def setup_method(self):
        self.expected_order_book = EXPECTED_ORDER_BOOK

    def test_handle_message_raises_invalid_json(self):
        with pytest.raises(InvalidJsonException):
            Handler.handle_message('{"name":"invalid json"')

    @patch("kraken_web_api.handlers.Handler")
    def test_handle_list_message_invoke_handle_list(self, mock):
        mock._handle_list_object.return_value = None
        Handler.handle_message(DATA_LIST_MESSAGE)
        assert mock._handle_list_object.called

    @patch("kraken_web_api.handlers.Handler")
    def test_handle_dict_message_invoke_handle_dict(self, mock):
        mock._handle_dict_object.return_value = None
        Handler.handle_message(DATA_DICT_MESSAGE)
        assert mock._handle_dict_object.called

    def test_handle_book_data(self):
        order_book = OrderBook()
        order_book = Handler.handle_book_data(BOOK_INIT_LIST, order_book)
        assert order_book == self.expected_order_book

    def test_handle_book_bid_update(self):
        order_book = Handler.handle_book_data(BOOK_BID_UPDATE, self.expected_order_book)
        self.expected_order_book.bids.append(
            Price(Decimal('0.000707640'), Decimal('265.70008036'), Decimal('1650173638.242924')))
        assert order_book == self.expected_order_book
