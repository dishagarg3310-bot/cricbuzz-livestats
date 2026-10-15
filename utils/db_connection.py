from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine

import config


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Return the one shared database engine for the whole app."""
    url = URL.create(
        drivername="mysql+pymysql",
        username=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT,
        database=config.DB_NAME,
        query={"charset": "utf8mb4"},
    )
    return create_engine(url, pool_pre_ping=True)