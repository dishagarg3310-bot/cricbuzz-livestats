from functools import lru_cache
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine

import config

ROOT = Path(__file__).resolve().parent.parent


def _connect_args() -> dict:
    """Use SSL when DB_SSL_CA points at a certificate file (Aiven needs this)."""
    if not config.DB_SSL_CA:
        return {}
    ca_path = Path(config.DB_SSL_CA)
    if not ca_path.is_absolute():
        ca_path = ROOT / ca_path
    if not ca_path.exists():
        raise FileNotFoundError(f"CA certificate not found: {ca_path}")
    return {"ssl": {"ca": str(ca_path)}}


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
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=280,
        connect_args=_connect_args(),
    )