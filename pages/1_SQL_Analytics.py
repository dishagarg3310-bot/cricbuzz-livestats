import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from services import analytics_service as an

st.set_page_config(page_title="SQL Analytics", page_icon="📊", layout="wide")

st.title("📊 SQL Analytics")
st.caption("Pick a question, adjust the thresholds, and see the result from MySQL.")

level = st.sidebar.selectbox("Level", ["All"] + an.LEVELS)
options = [q for q in an.QUESTIONS if level == "All" or q["level"] == level]

question = st.selectbox(
    "Question",
    options,
    format_func=lambda q: f"Q{q['no']} · {q['title']}",
)
st.markdown(f"**Level:** {question['level']}")

values = {}
if question["params"]:
    st.markdown("**Thresholds** (the default is the value from the project brief)")
    for p in question["params"]:
        values[p["var"]] = st.number_input(
            p["label"],
            min_value=1,
            value=p["default"],
            step=1,
            key=f"q{question['no']}_{p['var']}",
        )

try:
    with st.spinner("Running query..."):
        results = an.run_question(question["no"], tuple(values.items()))
except (SQLAlchemyError, FileNotFoundError) as exc:
    st.error(f"Query failed: {exc}")
    st.stop()

labels = question["labels"]
for i, df in enumerate(results, start=1):
    if len(results) > 1:
        title = labels[i - 1] if labels else f"Result {i}"
        st.subheader(title)
    if df.empty:
        st.info("No rows returned. If this question has a threshold, try a lower value.")
    else:
        st.dataframe(df, width="stretch", hide_index=True)
        st.download_button(
            "Download CSV",
            df.to_csv(index=False),
            file_name=f"q{question['no']:02d}_{i}.csv",
            key=f"dl_{question['no']}_{i}",
        )

with st.expander("Show SQL"):
    st.code(an.get_sql_text(question["no"]), language="sql")