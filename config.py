import os

from dotenv import load_dotenv

from utils.logger import setup_logging

load_dotenv()
setup_logging()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_SSL_CA = os.getenv("DB_SSL_CA")

# Live refresh spends API calls, so it is OFF unless explicitly turned on.
ALLOW_LIVE_REFRESH = os.getenv("ALLOW_LIVE_REFRESH", "false").strip().lower() == "true"