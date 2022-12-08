import structlog
from rel import rel

from market_makers import BinanceMarketMaker
from observables import SymbolPriceObservable

logger = structlog.get_logger()


def main() -> None:
    """Main function to start the market maker

    It creates a market maker and observable for BTCUSDT
    """
    mm_btc = BinanceMarketMaker("BTCUSDT")
    obs_btc = SymbolPriceObservable("BTCUSDT")
    obs_btc.register_observer(mm_btc)
    obs_btc.start_watching()

    # Script allows to run multiple market makers in parallel.
    # Uncomment the following lines to run a second market maker
    # mm_eth = BinanceMarketMaker("ETHUSDT")
    # obs_eth = SymbolPriceObservable("ETHUSDT")
    # obs_eth.register_observer(mm_eth)
    # obs_eth.start_watching()

    # start dispatching the websockets
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()


if __name__ == "__main__":
    main()
