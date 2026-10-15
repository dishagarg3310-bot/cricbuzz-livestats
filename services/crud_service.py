from typing import Optional

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from services.detail_loader import _country_id
from utils.db_connection import get_engine

ROLES = ("Batsman", "Bowler", "All-rounder", "Wicket-keeper")
MANUAL_ID_START = 2_000_000_000


class ValidationError(ValueError):
    """The input is invalid or the action is not allowed."""


class NotFoundError(LookupError):
    """The requested row does not exist."""


def _clean(full_name, role, batting_style, bowling_style):
    full_name = (full_name or "").strip()
    if not full_name:
        raise ValidationError("Name is required.")
    if len(full_name) > 120:
        raise ValidationError("Name must be at most 120 characters.")
    if role and role not in ROLES:
        raise ValidationError(f"Role must be one of: {', '.join(ROLES)}.")
    batting_style = (batting_style or "").strip() or None
    bowling_style = (bowling_style or "").strip() or None
    if batting_style and len(batting_style) > 30:
        raise ValidationError("Batting style must be at most 30 characters.")
    if bowling_style and len(bowling_style) > 40:
        raise ValidationError("Bowling style must be at most 40 characters.")
    return full_name, role or None, batting_style, bowling_style


def create_player(
    full_name: str,
    country: Optional[str] = None,
    role: Optional[str] = None,
    batting_style: Optional[str] = None,
    bowling_style: Optional[str] = None,
) -> int:
    full_name, role, batting_style, bowling_style = _clean(
        full_name, role, batting_style, bowling_style
    )
    with get_engine().begin() as conn:
        exists = conn.execute(
            text("SELECT player_id FROM players WHERE LOWER(full_name) = LOWER(:n)"),
            {"n": full_name},
        ).first()
        if exists:
            raise ValidationError(f"A player named '{full_name}' already exists.")

        new_id = conn.execute(
            text(
                "SELECT COALESCE(MAX(player_id), :s - 1) + 1 "
                "FROM players WHERE player_id >= :s"
            ),
            {"s": MANUAL_ID_START},
        ).scalar()
        conn.execute(
            text(
                """INSERT INTO players
                   (player_id, full_name, country_id, playing_role,
                    batting_style, bowling_style, data_source)
                   VALUES (:id, :name, :c, :r, :bat, :bowl, 'sample')"""
            ),
            {
                "id": new_id,
                "name": full_name,
                "c": _country_id(conn, (country or "").strip() or None),
                "r": role,
                "bat": batting_style,
                "bowl": bowling_style,
            },
        )
    return new_id


def get_player(player_id: int) -> dict:
    with get_engine().connect() as conn:
        row = conn.execute(
            text(
                """SELECT p.player_id, p.full_name, co.country_name AS country,
                          p.playing_role, p.batting_style, p.bowling_style,
                          p.data_source
                   FROM players p
                   LEFT JOIN countries co ON co.country_id = p.country_id
                   WHERE p.player_id = :p"""
            ),
            {"p": player_id},
        ).mappings().first()
    if row is None:
        raise NotFoundError(f"Player {player_id} not found.")
    return dict(row)


def list_players(
    search: Optional[str] = None, role: Optional[str] = None, limit: int = 100
) -> list:
    sql = """SELECT p.player_id, p.full_name, co.country_name AS country,
                    p.playing_role, p.batting_style, p.bowling_style
             FROM players p
             LEFT JOIN countries co ON co.country_id = p.country_id
             WHERE 1 = 1"""
    params = {"limit": int(limit)}
    if search and search.strip():
        sql += " AND p.full_name LIKE :search"
        params["search"] = f"%{search.strip()}%"
    if role:
        sql += " AND p.playing_role = :role"
        params["role"] = role
    sql += " ORDER BY p.full_name LIMIT :limit"
    with get_engine().connect() as conn:
        return [dict(r) for r in conn.execute(text(sql), params).mappings()]


def update_player(
    player_id: int,
    full_name: str,
    country: Optional[str] = None,
    role: Optional[str] = None,
    batting_style: Optional[str] = None,
    bowling_style: Optional[str] = None,
) -> None:
    full_name, role, batting_style, bowling_style = _clean(
        full_name, role, batting_style, bowling_style
    )
    with get_engine().begin() as conn:
        found = conn.execute(
            text("SELECT 1 FROM players WHERE player_id = :p"), {"p": player_id}
        ).first()
        if not found:
            raise NotFoundError(f"Player {player_id} not found.")
        conn.execute(
            text(
                """UPDATE players
                   SET full_name = :name, country_id = :c, playing_role = :r,
                       batting_style = :bat, bowling_style = :bowl
                   WHERE player_id = :p"""
            ),
            {
                "p": player_id,
                "name": full_name,
                "c": _country_id(conn, (country or "").strip() or None),
                "r": role,
                "bat": batting_style,
                "bowl": bowling_style,
            },
        )


def delete_player(player_id: int) -> None:
    with get_engine().begin() as conn:
        found = conn.execute(
            text("SELECT 1 FROM players WHERE player_id = :p"), {"p": player_id}
        ).first()
        if not found:
            raise NotFoundError(f"Player {player_id} not found.")
        try:
            conn.execute(
                text("DELETE FROM players WHERE player_id = :p"), {"p": player_id}
            )
        except IntegrityError as exc:
            raise ValidationError(
                "Cannot delete: this player has scorecards, partnerships or "
                "career stats linked to them."
            ) from exc