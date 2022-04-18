
from abc import ABC, abstractmethod
from typing import Dict

from kraken_web_api.enums import SubscriptionType
from kraken_web_api.model.subscription import Subscription, SubscriptionRequest
from kraken_web_api.helpers.helpers import from_dataclass_to_dict


class RequestCreator(ABC):
    @abstractmethod
    def create(self, type: SubscriptionType, **kwargs) -> Dict:
        """ Create subscription object """
        raise NotImplementedError()


class SubscribtionRequestCreator(RequestCreator):

    def create(self, type: SubscriptionType, **kwargs) -> Dict:
        """ Create subscription object """

        if type == SubscriptionType.book:
            return self._create_book_subscription_request(**kwargs)

        if type == SubscriptionType.ohlc:
            raise NotImplementedError()

        if type == SubscriptionType.openOrders:
            raise NotImplementedError()

        if type == SubscriptionType.ownTrades:
            raise NotImplementedError()

        if type == SubscriptionType.spread:
            raise NotImplementedError()

        if type == SubscriptionType.ticker:
            return self._create_ticker_subscription_request(**kwargs)

        if type == SubscriptionType.trade:
            raise NotImplementedError()

        raise ValueError("Wrong SubscriptionType has been passed.")

    def _create_book_subscription_request(self, **kwargs) -> Dict:
        """ Creates book subscription request """
        if 'pair' not in kwargs:
            raise TypeError("Arguments must contain a 'pair' parameter")
        if 'subscribe' not in kwargs:
            raise TypeError("Arguments must contain a 'subscribe' parameter")
        if kwargs['subscribe'] and 'depth' not in kwargs:
            raise TypeError("Arguments must contain a 'depth' parameter")

        request = SubscriptionRequest(
            event="subscribe" if kwargs['subscribe'] else "unsubscribe",
            subscription=Subscription(
                name=SubscriptionType.book,
                depth=kwargs['depth'] if kwargs['subscribe'] else None,
            ),
            pair=[kwargs['pair']]
        )
        return from_dataclass_to_dict(request)

    def _create_ticker_subscription_request(self, **kwargs) -> Dict:
        """ Creates ticker subscription request """
        if 'pair' not in kwargs:
            raise TypeError("Arguments must contain a 'pair' parameter")
        if 'subscribe' not in kwargs:
            raise TypeError("Arguments must contain a 'subscribe' parameter")
        request = SubscriptionRequest(
            event="subscribe" if kwargs['subscribe'] else "unsubscribe",
            subscription=Subscription(
                name=SubscriptionType.ticker,
            ),
            pair=[kwargs['pair']]
        )
        return from_dataclass_to_dict(request)
