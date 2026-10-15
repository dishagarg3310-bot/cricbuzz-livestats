import re
from datetime import datetime, timezone
from typing import Optional


def epoch_ms_to_datetime(value) -> Optional[datetime]:
    """'1707955200000' -> datetime (UTC, naive). Empty/invalid -> None."""
    try:
        ms = int(value)
    except (TypeError, ValueError):
        return None
    if ms <= 0:
        return None
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    return dt.replace(tzinfo=None)


def to_int(value) -> Optional[int]:
    """'50000' -> 50000. '-', '', None -> None (NULL, never 0)."""
    try:
        return int(str(value).strip().replace(",", ""))
    except (TypeError, ValueError):
        return None


def to_float(value) -> Optional[float]:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def overs_to_balls(overs) -> Optional[int]:
    """41.4 -> 41*6 + 4 = 250. Never multiply overs by 6 directly."""
    if overs is None or overs == "":
        return None
    whole, _, part = str(overs).partition(".")
    try:
        return int(whole) * 6 + int(part or 0)
    except ValueError:
        return None


def parse_toss(text: str) -> tuple:
    """'India opt to bowl' -> ('India', 'bowl'). Unknown format -> (None, None)."""
    match = re.match(r"^(.+?)\s+(?:opt|opts|elected|chose)\s+to\s+(bat|bowl)", text or "", re.I)
    if not match:
        return None, None
    return match.group(1).strip(), match.group(2).lower()


def parse_result(status: str) -> tuple:
    """'India won by 8 wkts' -> ('India', 8, 'wickets'). Tie/no result -> (None, None, None)."""
    match = re.match(r"^(.+?)\s+won by\s+(\d+)\s+(run|runs|wkt|wkts|wicket|wickets)", status or "", re.I)
    if not match:
        return None, None, None
    kind = "runs" if match.group(3).lower().startswith("run") else "wickets"
    return match.group(1).strip(), int(match.group(2)), kind


def parse_dismissal_type(outdec: str) -> str:
    """Classify a dismissal text like 'c Hope b Joseph' for the catches/stumpings queries."""
    text = (outdec or "").strip().lower()
    if not text:
        return "did_not_bat"
    if text in ("not out", "batting"):
        return "not_out"
    if text.startswith("c & b") or text.startswith("c and b"):
        return "caught_and_bowled"
    if text.startswith("st "):
        return "stumped"
    if text.startswith("run out"):
        return "run_out"
    if text.startswith("lbw"):
        return "lbw"
    if text.startswith("hit wicket"):
        return "hit_wicket"
    if text.startswith("c "):
        return "caught"
    if text.startswith("b "):
        return "bowled"
    return "other"


def parse_height_cm(text: str) -> Optional[int]:
    """'5 ft 9 in (175 cm) ' -> 175."""
    match = re.search(r"\((\d+)\s*cm\)", text or "")
ROLE_MAP = {
    "batsman": "Batsman",
    "bowler": "Bowler",
    "wk-batsman": "Wicket-keeper",
    "wicketkeeper": "Wicket-keeper",
    "batting allrounder": "All-rounder",
    "bowling allrounder": "All-rounder",
    "allrounder": "All-rounder",
}


def map_role(role) -> Optional[str]:
    """API role text -> one of the 4 roles the database allows. Unknown -> None (NULL)."""
    return ROLE_MAP.get(str(role or "").strip().lower())