"""This is just an example test using pytest

In a production environment I would add unittest for every function/method and integration tests to check that
the components interact correctly
"""
from decimal import Decimal

import pytest

from market_makers import BinanceMarketMaker


@pytest.mark.parametrize(
    "current_price,expected",
    [(Decimal("15000"), False), (Decimal("8000"), True), (Decimal("21000"), True)],
)
def test_order_got_filled(current_price, expected):
    mm = BinanceMarketMaker("BTCUSDT")
    mm.current_bid_order = {"id": 1, "price": Decimal("10000")}
    mm.current_ask_order = {"id": 2, "price": Decimal("20000")}

    assert mm.order_got_filled(current_price) == expected
