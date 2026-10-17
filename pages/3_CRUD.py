import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from services import crud_service as crud

st.set_page_config(page_title="Manage Players", page_icon="🛠️", layout="wide")

st.title("🛠️ Manage Players")
st.caption("Add, edit and delete players. Players added here are marked as 'sample' data.")

ROLE_OPTIONS = [""] + list(crud.ROLES)


def role_label(role: str) -> str:
    return role or "(not set)"


def flash(kind: str, message: str) -> None:
    """Remember a message, clear caches, and rerun so every tab shows fresh data."""
    st.session_state["flash"] = (kind, message)
    st.cache_data.clear()
    st.rerun()


if "flash" in st.session_state:
    kind, message = st.session_state.pop("flash")
    (st.success if kind == "success" else st.error)(message)

tab_view, tab_add, tab_edit, tab_delete = st.tabs(["View", "Add", "Edit", "Delete"])

# ---------- View ----------
with tab_view:
    c1, c2, c3 = st.columns([2, 1, 1])
    search = c1.text_input("Search by name")
    role_filter = c2.selectbox(
        "Role", ROLE_OPTIONS, format_func=lambda r: r or "All roles", key="view_role"
    )
    limit = c3.slider("Max rows", 10, 200, 50)
    try:
        rows = crud.list_players(search=search, role=role_filter or None, limit=limit)
    except SQLAlchemyError:
        st.error("Could not read the database.")
        st.stop()
    st.write(f"{len(rows)} player(s) shown")
    st.dataframe(rows, width="stretch", hide_index=True)

# ---------- Add ----------
with tab_add:
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Full name *")
        country = st.text_input("Country")
        role = st.selectbox("Playing role", ROLE_OPTIONS, format_func=role_label)
        batting = st.text_input("Batting style (e.g. Right Handed Bat)")
        bowling = st.text_input("Bowling style (e.g. Right-arm medium)")
        submitted = st.form_submit_button("Add player")
    if submitted:
        try:
            new_id = crud.create_player(name, country, role or None, batting, bowling)
            flash("success", f"Player added (id {new_id}).")
        except crud.ValidationError as exc:
            st.error(str(exc))
        except SQLAlchemyError:
            st.error("Database error. Nothing was saved.")

# ---------- Edit ----------
with tab_edit:
    everyone = crud.list_players(limit=500)
    if not everyone:
        st.info("No players in the database.")
    else:
        labels = {p["player_id"]: f"{p['full_name']} (id {p['player_id']})" for p in everyone}
        pid = st.selectbox("Player to edit", list(labels), format_func=labels.get, key="edit_pick")
        current = crud.get_player(pid)
        with st.form(f"edit_form_{pid}"):
            e_name = st.text_input("Full name *", value=current["full_name"])
            e_country = st.text_input("Country", value=current["country"] or "")
            e_role = st.selectbox(
                "Playing role",
                ROLE_OPTIONS,
                index=ROLE_OPTIONS.index(current["playing_role"] or ""),
                format_func=role_label,
            )
            e_bat = st.text_input("Batting style", value=current["batting_style"] or "")
            e_bowl = st.text_input("Bowling style", value=current["bowling_style"] or "")
            saved = st.form_submit_button("Save changes")
        if saved:
            try:
                crud.update_player(pid, e_name, e_country, e_role or None, e_bat, e_bowl)
                flash("success", "Player updated.")
            except (crud.ValidationError, crud.NotFoundError) as exc:
                st.error(str(exc))
            except SQLAlchemyError:
                st.error("Database error. Nothing was changed.")

# ---------- Delete ----------
with tab_delete:
    everyone = crud.list_players(limit=500)
    if not everyone:
        st.info("No players in the database.")
    else:
        labels = {p["player_id"]: f"{p['full_name']} (id {p['player_id']})" for p in everyone}
        pid = st.selectbox("Player to delete", list(labels), format_func=labels.get, key="del_pick")
        st.json(crud.get_player(pid))
        st.warning(
            "Players who already have scorecards, partnerships or career stats "
            "cannot be deleted. Only players you added yourself usually can."
        )
        confirm = st.checkbox("Yes, I want to delete this player", key=f"confirm_{pid}")
        if st.button("Delete player", disabled=not confirm):
            try:
                crud.delete_player(pid)
                flash("success", "Player deleted.")
            except (crud.ValidationError, crud.NotFoundError) as exc:
                st.error(str(exc))
            except SQLAlchemyError:
                st.error("Database error. Nothing was deleted.")