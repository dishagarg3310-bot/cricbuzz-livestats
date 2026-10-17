from sqlalchemy import text

from services.analytics_service import _statements, get_sql_text


def run_query_file(engine, number, variables=None):
    """Run sql/qNN.sql and return one list of rows per SELECT."""
    results = []
    with engine.connect() as conn:
        for var, value in (variables or {}).items():
            conn.execute(text(f"SET @{var} = :v"), {"v": value})
        for statement in _statements(get_sql_text(number)):
            results.append(conn.execute(text(statement)).mappings().all())
    return results