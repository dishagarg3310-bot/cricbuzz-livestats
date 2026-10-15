from services import crud_service as crud

pid = crud.create_player(
    "Test Player", country="India", role="Batsman", batting_style="Right Handed Bat"
)
print("created:", pid)
print("read:", crud.get_player(pid))

crud.update_player(pid, "Test Player", "India", "All-rounder", "Right Handed Bat", "Right-arm medium")
print("updated role:", crud.get_player(pid)["playing_role"])
print("search 'test':", len(crud.list_players(search="test")), "row(s)")

for label, call in [
    ("empty name", lambda: crud.create_player("", role="Batsman")),
    ("bad role", lambda: crud.create_player("Someone Else", role="Pilot")),
    ("duplicate", lambda: crud.create_player("Test Player")),
    ("delete Kohli", lambda: crud.delete_player(1413)),
]:
    try:
        call()
        print(label, "-> NOT BLOCKED (problem!)")
    except crud.ValidationError as exc:
        print(label, "-> blocked:", exc)

crud.delete_player(pid)
try:
    crud.get_player(pid)
except crud.NotFoundError as exc:
    print("after delete:", exc)
