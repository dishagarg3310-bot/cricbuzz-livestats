import html

import streamlit as st

GREEN = "#22c55e"
GOLD = "#fbbf24"
CARD = "#111c2e"
BORDER = "#1f2d46"
MUTED = "#8b9bb4"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background:
        radial-gradient(1100px 560px at 8% -10%, rgba(34,197,94,.14), transparent 60%),
        radial-gradient(900px 500px at 100% 0%, rgba(251,191,36,.08), transparent 55%),
        #0b1220;
}
.block-container { padding-top: 2.2rem; max-width: 1280px; }
[data-testid="stHeader"] { background: transparent; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1b2d 0%, #0b1220 100%);
    border-right: 1px solid #1f2d46;
}

/* ---------- hero ---------- */
.hero {
    display: flex; align-items: center; gap: 22px;
    padding: 28px 32px; margin-bottom: 26px; border-radius: 22px;
    border: 1px solid rgba(34,197,94,.35);
    background:
        radial-gradient(500px 220px at 90% 0%, rgba(251,191,36,.16), transparent 70%),
        linear-gradient(135deg, rgba(34,197,94,.20) 0%, rgba(17,28,46,.95) 60%);
    box-shadow: 0 12px 40px rgba(0,0,0,.35);
}
.hero-icon {
    font-size: 3rem; width: 78px; height: 78px; flex: none;
    display: flex; align-items: center; justify-content: center;
    border-radius: 20px; background: rgba(34,197,94,.15);
    border: 1px solid rgba(34,197,94,.4);
}
.hero h1 {
    margin: 0; padding: 0; font-family: 'Poppins', sans-serif; font-weight: 800;
    font-size: 2.3rem; line-height: 1.15;
    background: linear-gradient(90deg, #ffffff 0%, #86efac 55%, #fbbf24 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero p { margin: 6px 0 0 0; color: #a9b8cf; font-size: 1.02rem; }

/* ---------- section titles ---------- */
.section-title {
    font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 1.25rem;
    margin: 26px 0 4px 0; padding-left: 12px; border-left: 4px solid #22c55e;
}
.section-caption { color: #8b9bb4; font-size: .9rem; margin: 0 0 12px 16px; }

/* ---------- KPI cards ---------- */
.kpi {
    background: #111c2e; border: 1px solid #1f2d46; border-radius: 18px;
    padding: 18px 20px; transition: all .2s ease; position: relative; overflow: hidden;
}
.kpi:hover {
    transform: translateY(-4px); border-color: #22c55e;
    box-shadow: 0 10px 28px rgba(34,197,94,.18);
}
.kpi .icon { position: absolute; right: 14px; top: 10px; font-size: 1.7rem; opacity: .85; }
.kpi .label {
    color: #8b9bb4; font-size: .74rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: .09em;
}
.kpi .value {
    font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 2.1rem;
    margin-top: 4px; color: #f8fafc;
}

/* ---------- match cards ---------- */
.mcard {
    display: flex; justify-content: space-between; align-items: center; gap: 16px;
    background: #111c2e; border: 1px solid #1f2d46; border-left: 4px solid #22c55e;
    border-radius: 14px; padding: 14px 18px; margin-bottom: 10px; transition: all .2s ease;
}
.mcard:hover { border-color: #22c55e; transform: translateX(3px); }
.mcard .teams { font-weight: 600; font-size: 1.02rem; color: #8b9bb4; }
.mcard .teams .win { color: #22c55e; font-weight: 700; }
.mcard .vs { color: #5b6b85; margin: 0 8px; font-weight: 400; font-size: .85rem; }
.mcard .meta { color: #8b9bb4; font-size: .82rem; margin-top: 4px; }
.mcard .pill {
    background: rgba(251,191,36,.12); color: #fbbf24;
    border: 1px solid rgba(251,191,36,.35); padding: 5px 12px; border-radius: 999px;
    font-size: .8rem; font-weight: 600; white-space: nowrap;
}

/* ---------- native widgets ---------- */
[data-testid="stMetric"] {
    background: #111c2e; border: 1px solid #1f2d46; border-radius: 16px; padding: 14px 18px;
}
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    background: #111c2e; border-radius: 10px; padding: 8px 18px; border: 1px solid #1f2d46;
}
.stTabs [aria-selected="true"] {
    background: rgba(34,197,94,.16); color: #22c55e; border-color: rgba(34,197,94,.5);
}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
    border-radius: 12px; border: 1px solid rgba(34,197,94,.5); font-weight: 600;
    background: linear-gradient(135deg, rgba(34,197,94,.25), rgba(34,197,94,.08));
    transition: all .2s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {
    border-color: #22c55e; box-shadow: 0 6px 18px rgba(34,197,94,.25); transform: translateY(-1px);
}
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; border: 1px solid #1f2d46; }
[data-testid="stExpander"] { border-radius: 14px; border: 1px solid #1f2d46; background: #0f1a2b; }
[data-testid="stPageLink"] a, a[data-testid="stPageLink-NavLink"] {
    border-radius: 12px; border: 1px solid #1f2d46; background: #111c2e;
}
.brand { padding: 10px 6px; color: #8b9bb4; font-size: .8rem; }
.brand b { color: #22c55e; font-family: 'Poppins', sans-serif; font-size: .95rem; }
</style>
"""


def apply_theme() -> None:
    """Call right after st.set_page_config on every page."""
    st.markdown(CSS, unsafe_allow_html=True)
    st.sidebar.markdown(
        '<div class="brand"><b>🏏 Cricbuzz LiveStats</b><br>Cricbuzz API · MySQL · Streamlit</div>',
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, icon: str = "🏏") -> None:
    st.markdown(
        f'<div class="hero"><div class="hero-icon">{icon}</div>'
        f"<div><h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p></div></div>",
        unsafe_allow_html=True,
    )


def section(title: str, caption: str = "") -> None:
    st.markdown(f'<div class="section-title">{html.escape(title)}</div>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="section-caption">{html.escape(caption)}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value, icon: str = "") -> str:
    return (
        f'<div class="kpi"><div class="icon">{icon}</div>'
        f'<div class="label">{html.escape(str(label))}</div>'
        f'<div class="value">{html.escape(str(value))}</div></div>'
    )


def _has(value) -> bool:
    return value is not None and value == value


def match_card(m: dict) -> str:
    team1, team2 = str(m.get("team1") or ""), str(m.get("team2") or "")
    winner = m.get("winner") if _has(m.get("winner")) else None

    def team_html(name: str) -> str:
        css = ' class="win"' if winner and name == winner else ""
        return f"<span{css}>{html.escape(name)}</span>"

    if winner and _has(m.get("margin")):
        result = f"{winner} won by {int(m['margin'])} {m.get('margin_type') or ''}".strip()
    elif winner:
        result = f"{winner} won"
    else:
        result = "No result"

    when = m.get("match_date")
    when = when.strftime("%d %b %Y") if hasattr(when, "strftime") else str(when or "")
    venue = html.escape(str(m.get("venue_name") or ""))
    desc = html.escape(str(m.get("match_desc") or ""))

    return (
        '<div class="mcard"><div>'
        f'<div class="teams">{team_html(team1)}<span class="vs">vs</span>{team_html(team2)}</div>'
        f'<div class="meta">{desc} · {venue} · {when}</div></div>'
        f'<div class="pill">{html.escape(result)}</div></div>'
    )


def style_fig(fig, height: int | None = None):
    """Make a Plotly figure match the app theme."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, sans-serif", "color": "#e6edf3"},
        colorway=[GREEN, GOLD, "#38bdf8", "#f472b6", "#a78bfa", "#fb923c"],
        margin={"l": 10, "r": 10, "t": 50, "b": 10},
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,.07)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,.07)")
    if height:
        fig.update_layout(height=height)
    return fig