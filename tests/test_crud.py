import pytest
from sqlalchemy import text

from services import crud_service as crud

PREFIX = "pytest_"


@pytest.fixture(autouse=True)
def clean_up(db):
    """Remove any player created by a test, even if the test fails."""
    yield
    with db.begin() as conn:
        conn.execute(
            text("DELETE FROM players WHERE full_name LIKE :p"),
            {"p": "pytest\\_%"},
        )


def test_create_read_update_delete_round_trip():
    pid = crud.create_player(
        f"{PREFIX}round_trip", role="Batsman", batting_style="Right Handed Bat"
    )
    player = crud.get_player(pid)
    assert player["full_name"] == f"{PREFIX}round_trip"
    assert player["playing_role"] == "Batsman"
    assert player["data_source"] == "sample"

    crud.update_player(pid, f"{PREFIX}round_trip", role="All-rounder")
    assert crud.get_player(pid)["playing_role"] == "All-rounder"

    crud.delete_player(pid)
    with pytest.raises(crud.NotFoundError):
        crud.get_player(pid)


def test_manual_ids_stay_out_of_the_api_range():
    pid = crud.create_player(f"{PREFIX}id_range")
    assert pid >= crud.MANUAL_ID_START


def test_search_finds_the_new_player():
    crud.create_player(f"{PREFIX}searchable")
    names = [p["full_name"] for p in crud.list_players(search="pytest_searchable")]
    assert f"{PREFIX}searchable" in names


@pytest.mark.parametrize("name", ["", "   ", None])
def test_empty_name_is_rejected(name):
    with pytest.raises(crud.ValidationError, match="Name is required"):
        crud.create_player(name)


def test_unknown_role_is_rejected():
    with pytest.raises(crud.ValidationError, match="Role must be one of"):
        crud.create_player(f"{PREFIX}bad_role", role="Pilot")


def test_too_long_name_is_rejected():
    with pytest.raises(crud.ValidationError):
        crud.create_player("x" * 121)


def test_duplicate_name_is_rejected_ignoring_case():
    crud.create_player(f"{PREFIX}dup")
    with pytest.raises(crud.ValidationError, match="already exists"):
        crud.create_player(f"{PREFIX.upper()}DUP")


def test_player_with_scorecards_cannot_be_deleted(db):
    with db.connect() as conn:
        pid = conn.execute(
            text("SELECT player_id FROM batting_scorecards LIMIT 1")
        ).scalar()
    if pid is None:
        pytest.skip("No scorecards loaded")
    with pytest.raises(crud.ValidationError, match="Cannot delete"):
        crud.delete_player(pid)
    assert crud.get_player(pid)["player_id"] == pid


def test_missing_player_raises_not_found():
    with pytest.raises(crud.NotFoundError):
        crud.get_player(-1)
    with pytest.raises(crud.NotFoundError):
        crud.update_player(-1, "Someone")
    with pytest.raises(crud.NotFoundError):
        crud.delete_player(-1)