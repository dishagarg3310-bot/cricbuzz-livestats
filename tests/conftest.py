import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from utils.db_connection import get_engine


@pytest.fixture(scope="session")
def db():
    """The shared engine. Database tests are skipped if MySQL is not reachable."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError:
        pytest.skip("MySQL is not reachable, skipping database tests")
    return engine