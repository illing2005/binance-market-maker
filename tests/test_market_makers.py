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


def test_create_maker_orders(mocker):
    def mock_place_limit_order(*args, **kwargs):
        mock_place_limit_order.order_id += 1
        return {
            "orderId": mock_place_limit_order.order_id,
            "price": str(kwargs["price"]),
        }

    mock_place_limit_order.order_id = 0
    mocked_client = mocker.patch(
        "market_makers.BinanceSpotClient.place_limit_order",
        side_effect=mock_place_limit_order,
    )

    mm = BinanceMarketMaker("BTCUSDT")
    mm.create_maker_orders(Decimal("2000"))

    assert mocked_client.call_count == 2
    assert mm.current_ask_order == {"id": 1, "price": Decimal("2050")}
    assert mm.current_bid_order == {"id": 2, "price": Decimal("1950")}


def test_notify_price(mocker):
    mm = BinanceMarketMaker("BTCUSDT")
    mocked_cancel_orders = mocker.patch(
        "market_makers.BinanceSpotClient.cancel_all_orders",
        return_value=[],
    )
    mocked_create_maker_orders = mocker.patch(
        "market_makers.BinanceMarketMaker.create_maker_orders",
        return_value=[],
    )

    # test with no orders set
    mm.notify_price(Decimal("10000"))
    assert mocked_cancel_orders.call_count == 0
    assert mocked_create_maker_orders.call_count == 1

    # test orders and price in between
    mm.current_bid_order = {"id": 1, "price": Decimal("9900")}
    mm.current_ask_order = {"id": 2, "price": Decimal("10100")}
    mm.notify_price(Decimal("10050"))
    assert mocked_cancel_orders.call_count == 0
    assert mocked_create_maker_orders.call_count == 1

    # test orders and price below bid order
    mm.current_bid_order = {"id": 1, "price": Decimal("9900")}
    mm.current_ask_order = {"id": 2, "price": Decimal("10100")}
    mm.notify_price(Decimal("9850"))
    assert mocked_cancel_orders.call_count == 1
    assert mocked_create_maker_orders.call_count == 2
