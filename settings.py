import environ

# Take environment variables from .env file
env = environ.Env()
environ.Env.read_env(".env")


BINANCE_API_URL = env("BINANCE_API_URL", default="https://testnet.binance.vision")
BINANCE_API_KEY = env("BINANCE_API_KEY")
BINANCE_SECRET_KEY = env("BINANCE_SECRET_KEY")

WEBSOCKET_URI = "wss://stream.binance.com:443"
