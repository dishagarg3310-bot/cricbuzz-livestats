import logging

from sqlalchemy import text
from sqlalchemy.engine import Engine

from api.cricbuzz_client import CricbuzzClient
from services.parsers import epoch_ms_to_datetime
from utils.db_connection import get_engine

logger = logging.getLogger(__name__)

FORMATS = [(1, "Test"), (2, "ODI"), (3, "T20"), (4, "IPL")]


def seed_formats(engine: Engine) -> None:
    """Insert the fixed list of formats (safe to run many times)."""
    with engine.begin() as conn:
        conn.execute(
            text("INSERT IGNORE INTO formats (format_id, format_name) VALUES (:id, :name)"),
            [{"id": i, "name": n} for i, n in FORMATS],
        )


def load_series(engine: Engine, data: dict) -> int:
    """Save every series from /series/v1/international. Returns rows processed."""
    rows = []
    for group in data.get("seriesMapProto", []):
        for s in group.get("series", []):
            start = epoch_ms_to_datetime(s.get("startDt"))
            end = epoch_ms_to_datetime(s.get("endDt"))
            rows.append(
                {
                    "id": s["id"],
                    "name": s["name"],
                    "start": start.date() if start else None,
                    "end": end.date() if end else None,
                }
            )

    sql = text(
        """
        INSERT INTO series (series_id, series_name, start_date, end_date, data_source)
        VALUES (:id, :name, :start, :end, 'api')
        ON DUPLICATE KEY UPDATE
            series_name = VALUES(series_name),
            start_date = VALUES(start_date),
            end_date = VALUES(end_date)
        """
    )
    with engine.begin() as conn:
        conn.execute(sql, rows)
    return len(rows)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = get_engine()
    seed_formats(engine)
    count = load_series(engine, CricbuzzClient().series_list())
    print("series processed:", count)