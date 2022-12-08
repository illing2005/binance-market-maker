import json
from decimal import Decimal

import structlog
from rel import rel
from websocket import WebSocketApp

import settings

logger = structlog.get_logger()


class SymbolPriceObservable:
    """Observable for a symbol price

    It creates a websocket connection to a symbol ticker

    Observers can register to be notified of new price value.
    """

    def __init__(self, symbol: str):

        self.observers = []

        self.symbol = symbol
        url = f"{settings.WEBSOCKET_URI}/ws/{symbol.lower()}@ticker"
        self.ws = WebSocketApp(
            url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

    def register_observer(self, observer) -> None:
        self.observers.append(observer)

    def _on_message(self, ws: WebSocketApp, message: str) -> None:
        """Receive ticker updates from websocket and forward price to observers"""
        parsed_message = json.loads(message)
        latest_price = Decimal(parsed_message["c"])
        logger.info(f"Latest price for {self.symbol}: {latest_price}")

        # notify all observers
        for observer in self.observers:
            observer.notify_price(latest_price)

    def _on_error(self, ws: WebSocketApp, error: str) -> None:
        """Callback if websocket has an error

        Notifies all observers about the error
        """
        # notify all observers
        logger.info(error)
        for observer in self.observers:
            observer.notify_error(error)

    def _on_close(self, ws: WebSocketApp, *args) -> None:
        """Callback if websocket is closed

        We call the error notifier of each observer
        """
        logger.info(f"Closed connection to {ws.url.split('/')[-1]}")
        for observer in self.observers:
            observer.notify_error("Websocket closed")

    def _on_open(self, ws: WebSocketApp):
        """Callback if websocket is opened"""
        logger.info(f"Opened connection to {ws.url.split('/')[-1]}")

    def start_watching(self):
        """Start watching the price ticker"""
        self.ws.run_forever(
            dispatcher=rel, reconnect=5
        )  # 5 second reconnect delay if connection closed unexpectedly
