import time

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

import config
from api.cricbuzz_client import CricbuzzAPIError
from services import live_service as live
from utils.style import apply_theme, hero
from utils.ui import show_db_error

st.set_page_config(page_title="Live Matches", page_icon="📡", layout="wide")
apply_theme()

COOLDOWN_SECONDS = 60

hero(
    "Live Matches",
    "Live data comes from the Cricbuzz API. Each refresh uses 1 of the monthly API calls.",
    icon="📡",
)

top_left, top_right = st.columns([3, 1])

if config.ALLOW_LIVE_REFRESH:
    if top_left.button("🔄 Refresh live data (uses 1 API call)"):
        wait = COOLDOWN_SECONDS - (time.time() - st.session_state.get("last_refresh", 0))
        if wait > 0:
            st.warning(f"Please wait {int(wait)} more seconds before refreshing again.")
        else:
            try:
                with st.spinner("Calling the Cricbuzz API..."):
                    live.refresh_live()
                st.session_state["last_refresh"] = time.time()
                st.success("Live data refreshed.")
            except CricbuzzAPIError as exc:
                st.error(f"API call failed: {exc}")
else:
    top_left.info(
        "Live refresh is turned off on this public demo to protect the API quota. "
        "You are seeing the last saved data."
    )

left = live.calls_left()
top_right.metric("API calls left", left if left is not None else "-")

data, label = live.load_saved()
st.caption(label)
matches = live.parse_matches(data)

tab_live, tab_upcoming = st.tabs(["Live and recent (API)", "Upcoming (database)"])

with tab_live:
    if not matches:
        st.info("No matches in the saved response.")
    else:
        states = sorted({m["state"] for m in matches})
        chosen = st.selectbox("State", ["All"] + states)
        shown = [m for m in matches if chosen == "All" or m["state"] == chosen]
        st.write(f"{len(shown)} match(es)")
        for m in shown:
            with st.container(border=True):
                c1, c2 = st.columns([3, 2])
                c1.markdown(f"**{m['team1']}** vs **{m['team2']}**")
                c1.caption(f"{m['series']} · {m['desc']} · {m['format']}")
                c2.markdown(f"**{m['state']}**")
                c2.caption(m["start"])
                st.write(
                    f"{m['team1_short']}: {m['score1'] or '-'}   |   "
                    f"{m['team2_short']}: {m['score2'] or '-'}"
                )
                if m["status"]:
                    st.write(m["status"])
                st.caption(f"{m['venue'] or ''}, {m['city'] or ''}")

with tab_upcoming:
    try:
        upcoming = live.upcoming_from_db()
    except SQLAlchemyError as exc:
        show_db_error(exc)
    if upcoming.empty:
        st.info("No upcoming matches in the database.")
    else:
        st.dataframe(upcoming, width="stretch", hide_index=True)