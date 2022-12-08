import environ

# Take environment variables from .env file
env = environ.Env()
environ.Env.read_env(".env")


BINANCE_API_KEY = env("BINANCE_API_KEY")
BINANCE_SECRET_KEY = env("BINANCE_SECRET_KEY")
