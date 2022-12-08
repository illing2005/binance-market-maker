import structlog
from rel import rel

from observables import SymbolPriceObservable

logger = structlog.get_logger()


def main(symbol: str):
    obs = SymbolPriceObservable(symbol)
    obs.start_watching()

    # create a second observable
    obs = SymbolPriceObservable("ETHUSDT")
    obs.start_watching()

    # start dispatching the websockets
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()


if __name__ == "__main__":
    symbol = "BTCUSDT"
    main(symbol)
