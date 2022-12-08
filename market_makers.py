from decimal import Decimal

import structlog

import settings
from client import BinanceSpotClient, APIException

logger = structlog.get_logger()


class BinanceMarketMaker:

    client = None

    def __init__(
        self,
        symbol: str,
        spread: Decimal = settings.DEFAULT_SPREAD,
        quantity: Decimal = settings.DEFAULT_QUANTITY,
    ):
        self.symbol = symbol
        self.spread = spread
        self.quantity = quantity
        self.current_ask_order = None
        self.current_bid_order = None

        if self.client is None:
            self.client = BinanceSpotClient()

    def __str__(self) -> str:
        return f"Market Maker for {self.symbol}"

    def notify_price(self, latest_price: Decimal):
        """Gets called when new price is observed

        It handles creation and cancellation of orders

        Args:
            latest_price (Decimal): Price from ticker
        """
        try:
            # if no orders are in place create new ones
            if self.current_ask_order is None and self.current_bid_order is None:
                self.create_maker_orders(latest_price)
            # If ask or bid order was filled, cancel orders and create new ones
            # An alternative approach would be to use the "cancel_and_replace" endpoint which would save us one API call
            elif self.order_got_filled(latest_price):
                self.client.cancel_all_orders(self.symbol)
                self.create_maker_orders(latest_price)
        except APIException as e:
            # In case we get an API error make sure to cancel all open orders
            self.client.cancel_all_orders(self.symbol)
            raise e

    def order_got_filled(self, latest_price: Decimal) -> bool:
        """Check if ask or bid order got filled

        This is basically a mock which checks if production price is
        below/above the ask/bid orders of the market maker.
        If that's the case we assume the order got filled
        """
        if self.current_ask_order["price"] < latest_price:
            logger.info(
                f"{self}: ask order got filled",
                ask_price=self.current_ask_order["price"],
                latest_price=latest_price,
            )
            return True
        if self.current_bid_order["price"] > latest_price:
            logger.info(
                f"{self}: bid order got filled",
                bid_price=self.current_bid_order["price"],
                latest_price=latest_price,
            )
            return True
        return False

    def create_maker_orders(self, latest_price: Decimal) -> None:
        """Creates ask and bid orders

        Ask and bid price are determined using the latest_price and the
        "spread" which can be configured in __init__ or settings.py

        Args:
            latest_price (Decimal): price from ticker
        """
        ask_price = latest_price + self.spread
        bid_price = latest_price - self.spread

        ask_order = self.client.place_limit_order(
            symbol=self.symbol,
            side=BinanceSpotClient.Side.SELL,
            quantity=self.quantity,
            price=ask_price,
        )
        self.current_ask_order = {
            "id": ask_order["orderId"],
            "price": Decimal(ask_order["price"]),
        }
        bid_order = self.client.place_limit_order(
            symbol=self.symbol,
            side=BinanceSpotClient.Side.BUY,
            quantity=self.quantity,
            price=bid_price,
        )
        self.current_bid_order = {
            "id": bid_order["orderId"],
            "price": Decimal(bid_order["price"]),
        }

        logger.info(
            f"{self}: new orders created",
            ask_price=ask_order["price"],
            bid_price=bid_order["price"],
        )

    def notify_error(self, error: str) -> None:
        """Callback when there is an error with price observable

        In that case we want to delete all open orders
        """
        self.client.cancel_all_orders(self.symbol)
