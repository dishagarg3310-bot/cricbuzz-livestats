import logging

import streamlit as st

logger = logging.getLogger(__name__)


def show_db_error(exc: Exception) -> None:
    """Log the real error, show a friendly message, and stop the page."""
    logger.error("Database error", exc_info=exc)
    st.error(
        "The database could not be reached. Check that MySQL is running and "
        "that the .env settings are correct. Details are in logs/app.log."
    )
    st.stop()