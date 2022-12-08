import hashlib
import hmac
from datetime import datetime
from decimal import Decimal
from enum import Enum
from urllib.parse import urlencode

import requests

import settings


class BinanceSpotClient:
    """Basic API Client for spot trading"""

    class Side(Enum):
        SELL = "SELL"
        BUY = "BUY"

    def __init__(self):
        self.base_url = settings.BINANCE_API_URL
        self.api_key = settings.BINANCE_API_KEY
        self.secret_key = settings.BINANCE_SECRET_KEY

        self.session = requests.session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def _get_signature(self, payload: dict) -> str:
        """Create HMAC SHA256 for payload

        Args:
            payload (dict): Dict with request parameters
        Returns:
            Signature string
        """
        query_string = urlencode(payload)

        return hmac.new(
            bytes(self.secret_key.encode("utf-8")),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _send_request(self, method: str, endpoint: str, payload: dict) -> dict:
        """Send request to REST API

        Args:
            method (str): Type of request (get, post, delete)
            endpoint (str): Endpoint to request
            payload (dict): Dict with request parameters
        Returns:
            Dict with API response
        """
        url = f"{self.base_url}{endpoint}"

        # add timestamp and sign request
        payload["timestamp"] = int(datetime.now().timestamp() * 1000)
        payload["signature"] = self._get_signature(payload)

        request_method = getattr(self.session, method)
        if method == "get":
            response = request_method(url, params=payload)
        else:
            response = request_method(url, data=payload)

        return response.json()

    def place_limit_order(
        self,
        symbol: str,
        side: Side,
        quantity: Decimal,
        price: Decimal,
    ):
        """Place a limit order for symbol

        Args:
            symbol (str): Market identifier (i.e. BTCUSDT or BTCBUSD)
            side (ENUM): SELL or BUY
            quantity (Decimal): Order amount
            price (Decimal): Order price
        Returns:
            dict with created order
        """

        url = "/api/v3/order"
        payload = {
            "symbol": symbol,
            "type": "LIMIT",
            "side": side.value,
            "quantity": quantity,
            "price": price,
            "timeInForce": "GTC",
        }

        return self._send_request("post", url, payload)

    def cancel_all_orders(self, symbol: str) -> dict:
        """Cancel all open orders for symbol

        Args:
            symbol (str): Market identifier (i.e. BTCUSDT or BTCBUSD)
        Returns:
            list of cancelled orders
        """
        endpoint = "/api/v3/openOrders"
        payload = {
            "symbol": symbol,
        }
        return self._send_request("delete", endpoint, payload)

    def get_open_orders(self, symbol: str) -> dict:
        """Get all open orders for symbol

        Args:
            symbol (str): Market identifier (i.e. BTCUSDT or BTCBUSD)
        Returns:
            list of open orders
        """
        endpoint = "/api/v3/openOrders"

        payload = {
            "symbol": symbol,
        }
        return self._send_request("get", endpoint, payload)

    def cancel_and_replace(
        self,
        symbol: str,
        side: Side,
        quantity: Decimal,
        price: Decimal,
        cancel_order_id: int,
    ) -> dict:
        """Cancel order and create a new one

        Args:
            symbol (str): Market identifier (i.e. BTCUSDT or BTCBUSD)
            side (ENUM): SELL or BUY
            quantity (Decimal): Order amount
            price (Decimal): Order price
            cancel_order_id (int): Order to cancel

        Returns:
            dict with created order and cancel result
        """
        endpoint = "/api/v3/order/cancelReplace"

        payload = {
            "symbol": symbol,
            "type": "LIMIT",
            "side": side.value,
            "quantity": quantity,
            "timeInForce": "GTC",
            "price": price,
            "cancelOrderId": cancel_order_id,
            "cancelReplaceMode": "STOP_ON_FAILURE",
        }

        return self._send_request("post", endpoint, payload)


if __name__ == "__main__":
    c = BinanceSpotClient()
    symbol = "BTCUSDT"
    order = c.place_limit_order(
        symbol=symbol,
        side=BinanceSpotClient.Side.SELL,
        quantity=Decimal("0.1"),
        price=Decimal(20000),
    )
    print(order)
    print(c.get_open_orders(symbol))

    print(
        c.cancel_and_replace(
            symbol=symbol,
            side=BinanceSpotClient.Side.SELL,
            quantity=Decimal("0.1"),
            price=Decimal(50000),
            cancel_order_id=order["orderId"],
        )
    )
    print(c.get_open_orders(symbol))
    print(c.cancel_all_orders(symbol))
    print(c.get_open_orders(symbol))
