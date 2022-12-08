# Binance Market Maker

## How to run
TODO

### Dependencies
This project uses [pip-tools](https://github.com/jazzband/pip-tools) for dependency management.
New dependencies need to be added to `requirements/src/requirements.in`.

Then we need to compile the requirements:
```shell
pip-compile --generate-hashes requirements/src/requirements.in  -o requirements/compiled/requirements.txt
```

### Task description

You are asked to provide liquidity to the Exchange, placing open orders
and adjusting the price when the market is moving. To keep it simple:
- On symbol `BTCUSDT` or `BTCBUSD`
- Get the latest price from the production site (https://binance.com)
- Place a bid open order and an ask open order on testnet
(https://testnet.binance.vision), if the price on the production site
moves to a position where your bid or ask order can be ﬁlled, cancel
them and place them again. For example:
    - On the production site, the latest `BTCUSDT` price is $20,000.
First, you place two orders on the testnet:
       - A bid order with price $19,900
       - An ask order with price $20,100
    - Then soon later on the production site, the latest price
changed to $20,150. Because your ask order on testnet can be
filled by that price, you will need to cancel both the bid and ask
orders and place them again.

**Notes:**

- Should not use any pre-build library related to Binance or other
crypto exchanges.
- Language is not limited, but please give details of how to run.
- UI is not required, running from the terminal is enough.
- Submit the code into a GitHub repository, commit history will also
be reviewed.
High quality code is expected, production-ready standards.
