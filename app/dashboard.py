"""
My Music Revisits — Streamlit app

Requires: streamlit >= 1.40 (for st.pills, and st.container(key=...) used for styling).
Upgrade with:
    pip install -U streamlit

DATA ASSUMPTIONS (adjust the column lookups below if yours differ):
- plays.parquet   : minutes  [+ optionally artist, track, genre per event,
                     + optionally a timestamp column for the "Listening Times"
                     heatmap — tries played_at / timestamp / ts / datetime /
                     played_datetime / played_at_utc]
- tracks.parquet  : track, artist, genre, plays, full_rate, friction_rate
                     [+ optionally recommend_score]
- genres.parquet  : genre, plays
- artists.parquet : artist, plays
- days.parquet    : date, minutes, plays, tracks, top_artist, top_genre
- hours.parquet   : optional. Used for the heatmap only if plays has no timestamp
                     column (the heatmap is built from plays timestamps first so it
                     can be shown in EST). Tries to detect weekday / time-bucket /
                     minutes columns automatically. If neither works, that one
                     section just shows a note — tell me the real column names and
                     I'll wire it up.
"""

import html
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="My Music Revisits", page_icon="💿", layout="wide")

LISTENER_NAME = "Sumaitat"  # <- change to your name

# Listening-times heatmap timezone. "Etc/GMT+5" is a fixed UTC-5 offset (true EST all year).
# Use "America/New_York" instead if you want daylight saving time applied.
TIMEZONE = "Etc/GMT+5"
TZ_LABEL = "EST"

COLORS = {
    "page": "#EDF8FF",      # Ice Blue
    "page_soft": "rgba(237, 248, 255, 0.88)",  # main content backing at 70% opacity (keeps text readable, dots peek through)
    "ink": "#17252D",
    "black": "#101010",     # labels and card titles
    "muted": "#244F82",     # navy blue (replaces the grey text)
    "select": "#8B1230",    # dark red: selected tab / selected pills
    "pink": "#F5A8CD",      # Candy Pink
    "cyan": "#A8E8CE",      # Mint
    "mint": "#A8E8CE",      # Mint
    "purple": "#C5ADFF",    # Lavender
    "yellow": "#FFE28C",    # Butter
    "coral": "#F5A8CD",     # Candy Pink
    "blue": "#A9D6F5",      # polka dots (soft blue)
    "sky": "#D3EBFB",       # tab backgrounds (soft blue)
    "sky_soft": "rgba(211, 235, 251, 0.78)",   # tab background, slightly see-through so the dots show
    "sky_shade": "rgba(150, 196, 232, 0.50)",  # soft shadow gradient at the tab edges
    "wash": "rgba(252, 200, 226, 0.30)",       # lighter pink, low opacity (every pink panel, card and tab)
}

PALETTE = [
    COLORS["purple"],
    COLORS["pink"],
    COLORS["yellow"],
    COLORS["mint"],
    COLORS["cyan"],
]

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
BUCKETS = ["00-04", "04-08", "08-12", "12-16", "16-20", "20-24"]
BUCKET_LABELS = dict(zip(BUCKETS, ["12–4 AM", "4–8 AM", "8 AM–12 PM", "12–4 PM", "4–8 PM", "8 PM–12 AM"]))

QUICK_MOODS = [
    "Rainy night", "Workout", "Relaxing", "Feel good", "Late night drive",
    "Romantic", "Study", "Party", "Heartbreak", "Nostalgic",
    "Angry", "Cozy", "Confident", "Dreamy",
]


# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------
@st.cache_data
def load_data() -> dict:
    root = Path(__file__).resolve().parents[1] / "data" / "processed"
    data = {}
    for name in ["plays", "tracks", "artists", "genres", "days"]:
        data[name] = pd.read_parquet(root / f"{name}.parquet")
    for optional in ["hours", "features"]:
        path = root / f"{optional}.parquet"
        data[optional] = pd.read_parquet(path) if path.exists() else pd.DataFrame()
    return data


# ----------------------------------------------------------------------------
# Style
# ----------------------------------------------------------------------------
def style() -> None:
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Pixelify+Sans:wght@500;700&display=swap');

    /* Polka dots: blue and pink, offset from each other */
    .stApp {{
        background-color: {COLORS['page']}; color: {COLORS['ink']};
        background-image:
            radial-gradient(circle, {COLORS['blue']} 6px, transparent 6.5px),
            radial-gradient(circle, {COLORS['pink']} 6px, transparent 6.5px);
        background-size: 38px 38px, 38px 38px;
        background-position: 0 0, 19px 19px;
    }}
    header[data-testid="stHeader"] {{ background: transparent; }}
    .block-container {{
        max-width: 1180px; padding-top: 2rem;
        background-color: {COLORS['page_soft']};
    }}

    .section-divider {{ border: none; border-top: 3px solid {COLORS['pink']}; margin: 1.4rem 0; }}
    h1, h2, h3 {{ font-family: 'Pixelify Sans', monospace !important; color: {COLORS['ink']} !important; }}
    h1 {{ font-size: clamp(1.7rem, 6vw, 2.6rem) !important; line-height: 1.15 !important; }}
    .stMarkdown, .stTextInput, .stTextArea, .stMultiSelect, .stButton {{ font-family: 'Nunito', sans-serif; }}

    /* Captions: navy and bold so they're easy to read */
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{
        color: {COLORS['muted']} !important; opacity: 1 !important;
        font-size: .88rem !important; font-weight: 600 !important;
    }}
    textarea::placeholder, input::placeholder {{ color: #5B84B1 !important; opacity: 1 !important; }}

    /* Hero */
    .hero {{
        background: linear-gradient(135deg, #F8FCFF 0%, #DCEEFC 100%);
        border: 1px solid {COLORS['ink']}; border-radius: 16px;
        padding: 1.2rem 1.5rem; margin-bottom: 1rem;
        box-shadow: 0 0 22px rgba(150, 205, 245, .35);
    }}
    .eyebrow {{ font-size: .75rem; font-weight: 900; letter-spacing: 1.5px; color: {COLORS['black']}; text-transform: uppercase; margin-bottom: .3rem; }}
    .small-caps {{ font-size: .75rem; font-weight: 800; letter-spacing: 1.2px; color: {COLORS['black']}; text-transform: uppercase; margin: .4rem 0; }}
    .highlight {{ border-bottom: 7px solid {COLORS['pink']}; }}

    /* Tabs: blue tab buttons, light low-opacity pink when selected, dark red selected text */
    div[data-baseweb="tab-list"] {{ gap: .5rem; background: transparent; }}
    button[data-baseweb="tab"] {{
        background: {COLORS['sky_soft']}; border: 1px solid {COLORS['ink']};
        border-radius: 12px 12px 0 0; padding: .5rem 1rem; height: auto;
    }}
    button[data-baseweb="tab"] p {{ font-weight: 800; color: {COLORS['ink']}; }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background: {COLORS['wash']}; border: 1px solid {COLORS['select']};
        box-shadow: inset 0 -3px 0 {COLORS['select']};
    }}
    button[data-baseweb="tab"][aria-selected="true"],
    button[data-baseweb="tab"][aria-selected="true"] * {{ color: {COLORS['select']} !important; }}
    div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] {{ display: none; }}
    div[data-baseweb="tab-panel"] {{
        background: linear-gradient(180deg,
            {COLORS['sky_shade']} 0%,
            {COLORS['sky_soft']} 14%,
            {COLORS['sky_soft']} 88%,
            {COLORS['sky_shade']} 100%);
        border: 1px solid {COLORS['ink']};
        border-radius: 0 16px 16px 16px; padding: 1rem 1rem .9rem !important;
    }}

    /* Panels (light, low-opacity pink cards inside the blue tab) */
    [class*="st-key-panel_"] {{
        background: {COLORS['wash']}; border: 1px solid {COLORS['ink']}; border-radius: 14px;
        padding: 1rem 1.1rem 1.2rem; box-sizing: border-box;
    }}
    [class*="st-key-panel_"] .small-caps {{ margin: .8rem 0 .4rem; }}

    /* Overview metric tiles: one grid so every tile lines up and stays the same size per row */
    .metric-grid {{
        display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: .5rem; margin-bottom: .2rem;
    }}
    .metric {{
        box-sizing: border-box; min-width: 0;
        background: {COLORS['page']}; border: 1px solid {COLORS['ink']}; border-radius: 10px;
        padding: .5rem .7rem;
    }}
    .metric .muted {{ display: block; font-size: .72rem; font-weight: 800; line-height: 1.2; }}
    .metric strong {{ display: block; font-size: 1.15rem; line-height: 1.25; }}
    .metric-sub {{ display: block; font-size: .7rem; font-weight: 700; line-height: 1.2; color: {COLORS['muted']}; }}
    .kv {{ display: flex; justify-content: space-between; gap: .8rem; padding: .45rem 0; border-bottom: 1px dashed {COLORS['blue']}; }}
    .kv span {{ font-weight: 700; font-size: .85rem; color: {COLORS['muted']}; }}
    .kv strong {{ text-align: right; font-size: .9rem; }}

    .genre-row {{ margin-bottom: .6rem; }}
    .genre-row-top {{ display: flex; justify-content: space-between; gap: .5rem; font-size: .88rem; font-weight: 700; margin-bottom: .25rem; }}
    .bar-bg {{ background: {COLORS['page']}; border: 1px solid {COLORS['ink']}; border-radius: 999px; height: 10px; overflow: hidden; }}
    .bar-fill {{ height: 100%; border-radius: 999px; }}

    .bubble {{ border-radius: 999px; background: {COLORS['cyan']}; border: 1px solid {COLORS['ink']}; margin-left: auto; }}

    /* Detail card: used for the selected artist and for every plot click */
    .info-wrap {{ padding: .6rem 0 .9rem; }}
    .info-card {{
        box-sizing: border-box; width: 100%;
        background: {COLORS['wash']}; border: 1px solid {COLORS['ink']}; border-radius: 10px;
        padding: .5rem .75rem;
    }}
    .info-title {{ font-size: 1.05rem; font-weight: 900; color: {COLORS['black']}; line-height: 1.2; overflow-wrap: anywhere; }}
    .info-line {{ font-size: .8rem; font-weight: 700; color: {COLORS['ink']}; line-height: 1.35; margin-top: .12rem; overflow-wrap: anywhere; }}
    .info-title + .info-line {{ margin-top: .25rem; }}

    .rank-chip {{
        width: 34px; height: 34px; border-radius: 8px; color: {COLORS['ink']}; font-weight: 900;
        border: 1px solid {COLORS['ink']};
        display: flex; align-items: center; justify-content: center; font-size: .85rem;
    }}
    .muted {{ color: {COLORS['muted']}; font-size: .85rem; font-weight: 700; }}

    /* Recommendation player */
    .st-key-player {{
        background: transparent;
        border: 1px solid {COLORS['ink']}; border-radius: 22px;
        padding: 1.1rem 1.2rem 1.3rem; box-sizing: border-box;
    }}
    .st-key-player_screen {{
        background: {COLORS['wash']}; border: 1px solid {COLORS['ink']}; border-radius: 14px;
        padding: .9rem 1rem; box-sizing: border-box;
    }}

    /* Buttons */
    div[data-testid="stButton"] > button {{
        background: {COLORS['wash']}; color: {COLORS['ink']}; border: 1px solid {COLORS['ink']}; font-weight: 800;
    }}
    div[data-testid="stButton"] > button:hover {{
        background: {COLORS['pink']}; border-color: {COLORS['ink']}; color: {COLORS['ink']};
    }}
    div[data-testid="stButton"] > button[kind="primary"],
    div[data-testid="stButton"] > button[data-testid="stBaseButton-primary"] {{
        background: {COLORS['pink']}; color: {COLORS['ink']}; border: 1px solid {COLORS['ink']}; font-weight: 800;
    }}

    /* Pills wrap onto new lines so every option is visible */
    div[data-testid="stButtonGroup"] {{
        flex-wrap: wrap !important; overflow: visible !important;
        height: auto !important; max-height: none !important;
    }}
    div[data-testid="stButtonGroup"] > div {{ flex-wrap: wrap !important; overflow: visible !important; }}
    button[data-testid="stBaseButton-pills"], button[data-testid="stBaseButton-pillsActive"] {{ white-space: nowrap; }}

    /* Pills, progress, inputs, expander, alerts: pink accent + thin outline */
    button[data-testid="stBaseButton-pills"] {{
        background: {COLORS['wash']}; border: 1px solid {COLORS['ink']}; color: {COLORS['ink']}; font-weight: 700;
    }}
    button[data-testid="stBaseButton-pills"]:hover {{
        background: {COLORS['pink']}; border-color: {COLORS['ink']}; color: {COLORS['ink']};
    }}
    button[data-testid="stBaseButton-pillsActive"] {{
        background: {COLORS['pink']}; border: 2px solid {COLORS['select']}; font-weight: 900;
    }}
    button[data-testid="stBaseButton-pillsActive"],
    button[data-testid="stBaseButton-pillsActive"] * {{ color: {COLORS['select']} !important; }}
    [data-testid="stProgress"] [role="progressbar"] > div > div {{ background-color: {COLORS['pink']} !important; }}
    div[data-baseweb="textarea"], div[data-baseweb="input"] {{
        border: 1px solid {COLORS['ink']} !important; border-radius: 10px; background: {COLORS['wash']} !important;
    }}
    div[data-baseweb="base-input"] {{ border: none !important; background: transparent !important; }}
    div[data-baseweb="base-input"] textarea, div[data-baseweb="base-input"] input {{ background: transparent !important; }}
    div[data-baseweb="textarea"]:focus-within, div[data-baseweb="input"]:focus-within {{
        border-color: {COLORS['select']} !important; box-shadow: 0 0 0 1px {COLORS['select']};
    }}
    div[data-testid="stExpander"] details {{
        border: 1px solid {COLORS['ink']}; border-radius: 10px; background: {COLORS['wash']};
    }}
    div[data-testid="stAlert"] {{
        background-color: {COLORS['wash']}; border: 1px solid {COLORS['ink']}; border-radius: 10px;
    }}
    div[data-testid="stAlert"] > div {{ background-color: transparent !important; color: {COLORS['ink']}; }}

    /* ---------- Tablets and small laptops ---------- */
    @media (max-width: 900px) {{
        .block-container {{ padding: 1rem .9rem 2rem !important; }}
        .hero {{ padding: 1rem 1.1rem; }}
        .hero p {{ font-size: .92rem; margin-bottom: .5rem; }}
        div[data-baseweb="tab-panel"] {{ padding: .8rem .7rem .7rem !important; }}
        button[data-baseweb="tab"] {{ padding: .4rem .7rem; }}
        button[data-baseweb="tab"] p {{ font-size: .8rem; }}
        [class*="st-key-panel_"] {{ padding: .8rem .8rem 1rem; }}
        .st-key-player {{ padding: .8rem .8rem 1rem; }}
        .st-key-player_screen {{ padding: .8rem; }}
        .metric {{ padding: .4rem .6rem; }}
        .metric .muted {{ font-size: .66rem; }}
        .metric strong {{ font-size: 1rem; }}
        .metric-sub {{ font-size: .64rem; }}
        .kv span, .kv strong {{ font-size: .8rem; }}
        .genre-row-top {{ font-size: .82rem; }}
        .info-title {{ font-size: .98rem; }}
        .info-line {{ font-size: .76rem; }}
    }}

    /* ---------- Phones ---------- */
    @media (max-width: 640px) {{
        .block-container {{ padding: .6rem .6rem 1.5rem !important; }}
        .section-divider {{ margin: .9rem 0; }}
        .small-caps {{ font-size: .68rem; }}
        button[data-baseweb="tab"] {{ padding: .35rem .55rem; }}
        button[data-baseweb="tab"] p {{ font-size: .72rem; }}
        [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{ font-size: .8rem !important; }}

        /* Keep the small rows (artist list, track list, repeat list, selection list) on one line
           instead of stacking every cell; the two big page columns still stack. */
        [data-testid="stColumn"] [data-testid="stHorizontalBlock"] {{
            flex-wrap: nowrap !important; gap: .4rem !important; align-items: center;
        }}
        [data-testid="stColumn"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
            min-width: 0 !important; width: auto !important; flex: 1 1 0 !important;
        }}
        [data-testid="stColumn"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1):nth-last-child(4) {{ flex-grow: 8 !important; }}
        [data-testid="stColumn"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2):nth-last-child(3) {{ flex-grow: 58 !important; }}
        [data-testid="stColumn"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3):nth-last-child(2) {{ flex-grow: 20 !important; }}
        [data-testid="stColumn"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(4):nth-last-child(1) {{ flex-grow: 14 !important; }}
        [data-testid="stColumn"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1):nth-last-child(3) {{ flex-grow: 12 !important; }}
        [data-testid="stColumn"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2):nth-last-child(2) {{ flex-grow: 76 !important; }}
        [data-testid="stColumn"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3):nth-last-child(1) {{ flex-grow: 12 !important; }}
        [data-testid="stColumn"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1):nth-last-child(2) {{ flex-grow: 80 !important; }}
        [data-testid="stColumn"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2):nth-last-child(1) {{ flex-grow: 20 !important; }}
        [data-testid="stColumn"] [data-testid="stColumn"] button {{ padding: .2rem .45rem; min-height: 0; }}
    }}
    </style>
    """, unsafe_allow_html=True)


def _esc(value) -> str:
    """HTML-escape text (and `$`, which markdown can mistake for math)."""
    return html.escape(str(value)).replace("$", "&#36;")


def metric(label: str, value: str, sub: str | None = None) -> str:
    """Returns one tile's HTML; tiles are rendered together inside .metric-grid."""
    sub_html = f'<span class="metric-sub">{sub}</span>' if sub else ""
    return f'<div class="metric"><span class="muted">{label}</span><strong>{value}</strong>{sub_html}</div>'


def info_card(title: str, lines: list) -> None:
    """Soft pink detail card: bold black title with info lines underneath."""
    body = "".join(f'<div class="info-line">{_esc(line)}</div>' for line in lines if line)
    st.markdown(
        f'<div class="info-wrap"><div class="info-card">'
        f'<div class="info-title">{_esc(title)}</div>{body}'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def pink_divider() -> None:
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


def style_axes(fig, x_title: str, y_title: str) -> None:
    """Bold, high-contrast axes with clear titles."""
    ink = COLORS["ink"]
    axis = dict(
        showline=True, linecolor=ink, linewidth=2,
        gridcolor="#BCD0E8", zeroline=False,
        ticks="outside", tickcolor=ink,
        tickfont=dict(size=13, color=ink),
        automargin=True,
    )
    fig.update_xaxes(title_text=f"<b>{x_title}</b>", title_font=dict(size=14, color=ink), **axis)
    fig.update_yaxes(title_text=f"<b>{y_title}</b>", title_font=dict(size=14, color=ink), **axis)
    try:  # bold tick labels (needs a recent plotly); falls back gracefully
        fig.update_xaxes(tickfont=dict(weight="bold"))
        fig.update_yaxes(tickfont=dict(weight="bold"))
    except ValueError:
        pass
    fig.update_layout(font=dict(color=ink), margin=dict(l=10, r=10, t=10, b=10))


# ----------------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------------
def hero(data: dict) -> None:
    st.markdown(f"""
    <div class="hero">
      <div class="eyebrow">An experiment in listening</div>
      <h1>Hi, I'm {LISTENER_NAME}.<br>This is my <span class="highlight">listening data.</span></h1>
      <div class="small-caps">October 2025 – March 2026</div>
      <p>
      In October 2025, I switched my music streaming app for 5 months to see which service I preferred. Majority of the tracks were imported from my previous library. When the experiment ended, I exported my data to analyze my music listening behavior and figure out which tracks I listened to most. 
      </p>
      
      <p>This is a capsule of my music listening data during that specific period, not a full picture of my listening behavior. A first listen or "discovery" here doesn't mean I discovered the song then.</p>
    </div>
    """, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Overview (left column): metrics, top 5 artists, highlights
# ----------------------------------------------------------------------------
def section_overview(data: dict) -> None:
    plays, tracks, days = data["plays"], data["tracks"], data["days"]
    artists, genres = data["artists"], data["genres"]

    n_days = len(days)
    total_minutes = plays["minutes"].sum() if "minutes" in plays.columns else 0
    avg_minutes = total_minutes / n_days if n_days else 0
    avg_events = len(plays) / n_days if n_days else 0
    n_artists = artists.loc[artists["artist"].ne("Unknown Artist"), "artist"].nunique()
    n_genres = genres["genre"].nunique() if "genre" in genres.columns else len(genres)

    st.markdown('<div class="eyebrow">OVERVIEW</div>', unsafe_allow_html=True)
    st.subheader("At a Glance")

    items = [
        ("Total Listening Time", f"{total_minutes / 60:,.1f} Hours", f"{total_minutes:,.0f} Minutes"),
        ("Avg. per Listening Day", f"{avg_minutes:,.0f} Minutes", None),
        ("Listening Events", f"{len(plays):,}", None),
        ("Tracks in the History", f"{len(tracks):,}", None),
        ("Listening Days", f"{n_days:,}", None),
        ("Avg. Events per Day", f"{avg_events:,.0f}", None),
        ("Artists", f"{n_artists:,}", None),
        ("Unique Genres", f"{n_genres:,}", None),
    ]
    tiles = "".join(metric(label, value, sub) for label, value, sub in items)
    st.markdown(f'<div class="metric-grid">{tiles}</div>', unsafe_allow_html=True)

    # Top 5 artists
    st.markdown('<div class="small-caps">Top 5 Artists</div>', unsafe_allow_html=True)
    top_artists = (artists[artists["artist"].ne("Unknown Artist")]
                   .sort_values("plays", ascending=False).head(5))
    max_plays = top_artists["plays"].max() if len(top_artists) else 1
    rows_html = ""
    for i, row in enumerate(top_artists.itertuples(), start=1):
        width = (row.plays / max_plays * 100) if max_plays else 0
        color = PALETTE[(i - 1) % len(PALETTE)]
        rows_html += (
            f'<div class="genre-row"><div class="genre-row-top"><span>{i:02d} {row.artist}</span>'
            f'<span>{row.plays:,}</span></div>'
            f'<div class="bar-bg"><div class="bar-fill" style="width:{width:.1f}%;background:{color};"></div></div></div>'
        )
    st.markdown(rows_html, unsafe_allow_html=True)

    # Highlights
    kv_rows = []
    if n_days and "minutes" in days.columns:
        longest = days.loc[days["minutes"].idxmax()]
        kv_rows.append(("Longest Day", f"{longest['date']:%b %d, %Y} · {longest['minutes']:,.0f} Minutes"))
    heat = build_heatmap_table(data)
    if heat is not None and not heat.empty and heat["minutes"].max() > 0:
        peak = heat.loc[heat["minutes"].idxmax()]
        kv_rows.append(("Peak Listening Time",
                        f"{peak['weekday']}, {BUCKET_LABELS.get(peak['bucket'], peak['bucket'])} {TZ_LABEL}"))
    if len(tracks):
        top_track = tracks.sort_values("plays", ascending=False).iloc[0]
        kv_rows.append(("Most-Played Track", f"{top_track['track']} — {top_track['artist']}"))
    if kv_rows:
        st.markdown('<div class="small-caps">Highlights</div>', unsafe_allow_html=True)
        st.markdown("".join(f'<div class="kv"><span>{k}</span><strong>{v}</strong></div>' for k, v in kv_rows),
                    unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Genres (left column)
# ----------------------------------------------------------------------------
def section_genres(data: dict) -> None:
    genres, plays = data["genres"], data["plays"]

    st.markdown('<div class="eyebrow">GENRES</div>', unsafe_allow_html=True)
    st.subheader("Leading Genres")
    st.caption("Ranked by share of all listening events.")

    total_events = len(plays)
    g_sorted = genres.sort_values("plays", ascending=False).reset_index(drop=True)
    if total_events:
        # drop genres whose share would display as 0.0%
        g_sorted = g_sorted[g_sorted["plays"].map(lambda p: f"{p / total_events:.1%}" != "0.0%")].reset_index(drop=True)

    show_all = st.session_state.get("show_all_genres", False)
    shown = g_sorted if show_all else g_sorted.head(6)

    rows_html = ""
    for i, row in enumerate(shown.itertuples(), start=1):
        share = row.plays / total_events if total_events else 0
        color = PALETTE[(i - 1) % len(PALETTE)]
        rows_html += (
            f'<div class="genre-row"><div class="genre-row-top"><span>{i:02d} {row.genre}</span><span>{share:.1%}</span></div>'
            f'<div class="bar-bg"><div class="bar-fill" style="width:{share*100:.1f}%;background:{color};"></div></div></div>'
        )
    box = st.container(height=420) if show_all else st.container()
    with box:
        st.markdown(rows_html, unsafe_allow_html=True)

    if not show_all and len(g_sorted) > 6:
        rest = g_sorted.iloc[6:]
        rest_events = int(rest["plays"].sum())
        rest_share = rest_events / total_events if total_events else 0
        named = rest.head(4)
        bits = ", ".join(f"{r.genre} ({r.plays/total_events:.1%})" for r in named.itertuples())
        st.caption(f"The other {len(rest)} named genres account for {rest_events:,} listening events "
                   f"({rest_share:.1%}), led by {bits}.")

    if len(g_sorted) > 6 or show_all:
        if st.button("Show fewer" if show_all else "All genres", key="toggle_genres"):
            st.session_state["show_all_genres"] = not show_all
            st.rerun()


# ----------------------------------------------------------------------------
# Artists (right column)
# ----------------------------------------------------------------------------
def section_artists(data: dict) -> None:
    artists, plays, tracks = data["artists"], data["plays"], data["tracks"]

    st.markdown('<div class="eyebrow">ARTISTS</div>', unsafe_allow_html=True)
    st.subheader("Most-Played Artists")

    a_sorted = (artists[artists["artist"].ne("Unknown Artist")]
                .sort_values("plays", ascending=False).head(10).reset_index(drop=True))
    max_plays = a_sorted["plays"].max() if len(a_sorted) else 1

    for i, row in enumerate(a_sorted.itertuples(), start=1):
        size = 8 + 14 * (row.plays / max_plays if max_plays else 0)
        c1, c2, c3, c4 = st.columns([0.08, 0.58, 0.2, 0.14])
        with c1:
            st.write(f"**{i:02d}**")
        with c2:
            if st.button(row.artist, key=f"artist_{i}", use_container_width=True):
                st.session_state["selected_artist"] = row.artist
        with c3:
            st.write(f"{row.plays:,}")
        with c4:
            st.markdown(f'<div class="bubble" style="width:{size}px;height:{size}px;"></div>', unsafe_allow_html=True)

    selected_artist = st.session_state.get("selected_artist")
    if selected_artist:
        detail = _artist_detail(selected_artist, plays, tracks)
        if detail:
            info_card(detail["name"], [detail["stats"], f"Most played: {detail['top']}"])


def _artist_detail(artist: str, plays: pd.DataFrame, tracks: pd.DataFrame) -> dict | None:
    if {"artist", "track"}.issubset(plays.columns):
        sub = plays[plays["artist"].eq(artist)]
        if sub.empty:
            return None
        events = len(sub)
        n_tracks = sub["track"].nunique()
        minutes = sub["minutes"].sum() if "minutes" in sub.columns else None
        most_played = sub["track"].value_counts().idxmax()
        minutes_bit = f" · {minutes:,.0f} minutes" if minutes is not None else ""
        return {"name": artist,
                "stats": f"{events:,} events · {n_tracks} tracks{minutes_bit}",
                "top": most_played}

    sub_t = tracks[tracks["artist"].eq(artist)]
    if sub_t.empty:
        return None
    events = int(sub_t["plays"].sum())
    n_tracks = len(sub_t)
    most_played = sub_t.sort_values("plays", ascending=False).iloc[0]["track"]
    return {"name": artist, "stats": f"{events:,} events · {n_tracks} tracks", "top": most_played}


# ----------------------------------------------------------------------------
# Breakdown: repeat listening
# ----------------------------------------------------------------------------
def section_repeat(data: dict) -> None:
    tracks, plays = data["tracks"], data["plays"]
    st.markdown('<div class="eyebrow">REPEAT LISTENING</div>', unsafe_allow_html=True)
    st.subheader("How Much Did I Replay?")

    label_to_n = {"Top 5 Tracks": 5, "Top 10 Tracks": 10, "Top 25 Tracks": 25}
    choice = st.pills("Compare", list(label_to_n.keys()), selection_mode="single",
                       default="Top 5 Tracks", key="repeat_choice", label_visibility="collapsed")
    n = label_to_n.get(choice, 5)

    top = tracks.sort_values("plays", ascending=False).head(n)
    total = len(plays)
    share = top["plays"].sum() / total if total else 0

    st.progress(float(share))
    st.caption(f"My top {n} tracks account for {share:.1%} of listening events ({int(top['plays'].sum()):,} of {total:,}).")

    list_box = st.container(height=260) if n > 5 else st.container()
    with list_box:
        for i, row in enumerate(top.itertuples(), start=1):
            c1, c2 = st.columns([0.78, 0.22])
            with c1:
                st.markdown(f"**{i}. {row.track}** — {row.artist}")
            with c2:
                st.markdown(f"<div style='text-align:right'>{row.plays:,} plays</div>", unsafe_allow_html=True)

    st.caption("Counts include all recorded listening events, including short plays.")


# ----------------------------------------------------------------------------
# Breakdown: daily listening
# ----------------------------------------------------------------------------
def section_daily(data: dict) -> None:
    days = data["days"]
    st.markdown('<div class="eyebrow">DAILY LISTENING</div>', unsafe_allow_html=True)
    st.subheader("Minutes Listened per Day")
    st.caption("Click any dot to see how many tracks I played that day and which artists I played most.")

    plot_days = days.copy()
    plot_days["date"] = pd.to_datetime(plot_days["date"])
    fig = px.scatter(
        plot_days, x="date", y="minutes", size="minutes", color="minutes",
        hover_data=["plays", "tracks", "top_artist", "top_genre"],
        color_continuous_scale=[[0, COLORS["cyan"]], [.7, COLORS["yellow"]], [1, COLORS["coral"]]],
        size_max=14,
    )
    fig.update_layout(height=260, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
    style_axes(fig, "Date", "Minutes Listened")
    fig.update_xaxes(type="date", tickformat="%b %d", hoverformat="%b %d, %Y")
    fig.update_yaxes(rangemode="tozero")
    event = st.plotly_chart(fig, on_select="rerun", selection_mode="points", key="daily_pulse")

    if event and event.selection and event.selection.points:
        point = event.selection.points[0]
        day = plot_days.iloc[int(point["point_index"])]
        info_card(
            f"{day['date']:%b %d, %Y}",
            [f"{day['minutes']:.1f} minutes · {day['tracks']} tracks · {day['plays']} events",
             f"Top artist: {day['top_artist']}",
             f"Top genre: {day['top_genre']}"],
        )


# ----------------------------------------------------------------------------
# Breakdown: listening times heatmap
# ----------------------------------------------------------------------------
def build_heatmap_table(data: dict) -> pd.DataFrame | None:
    plays = data.get("plays")
    ts_col = None
    if plays is not None and not plays.empty:
        ts_col = next((c for c in ["played_at", "timestamp", "ts", "datetime", "played_datetime", "date_time", "played_at_utc"]
                       if c in plays.columns), None)

    # Preferred: rebuild from the play timestamps so they can be converted to EST
    if ts_col:
        df = plays.copy()
        df["_ts"] = pd.to_datetime(df[ts_col], utc=True, errors="coerce")
        df = df.dropna(subset=["_ts"])
        df["_ts"] = df["_ts"].dt.tz_convert(TIMEZONE)
        df["weekday"] = df["_ts"].dt.dayofweek.map(lambda d: WEEKDAYS[d])
        df["bucket"] = (df["_ts"].dt.hour // 4).map(lambda i: BUCKETS[i])

        agg_kwargs = {"minutes": ("minutes", "sum"), "plays": ("minutes", "count")}
        if "track" in df.columns:
            agg_kwargs["tracks"] = ("track", "nunique")
        agg = df.groupby(["weekday", "bucket"]).agg(**agg_kwargs).reset_index()

        if "artist" in df.columns:
            top_artists = (df.groupby(["weekday", "bucket"])["artist"]
                            .apply(lambda s: ", ".join(s.value_counts().head(3).index))
                            .reset_index(name="top_artists"))
            agg = agg.merge(top_artists, on=["weekday", "bucket"], how="left")

        full_index = pd.MultiIndex.from_product([WEEKDAYS, BUCKETS], names=["weekday", "bucket"])
        agg = agg.set_index(["weekday", "bucket"]).reindex(full_index, fill_value=0).reset_index()
        return agg

    # Fallback: a precomputed hours table (used as-is, no timezone conversion possible)
    hours = data.get("hours")
    if hours is not None and not hours.empty:
        cols = {c.lower(): c for c in hours.columns}
        weekday_col = next((cols[c] for c in ["weekday", "day_of_week", "dow", "day"] if c in cols), None)
        bucket_col = next((cols[c] for c in ["bucket", "hour_bucket", "time_bucket", "period", "block"] if c in cols), None)
        minutes_col = next((cols[c] for c in ["minutes", "total_minutes"] if c in cols), None)
        if weekday_col and bucket_col and minutes_col:
            df = hours.rename(columns={weekday_col: "weekday", bucket_col: "bucket", minutes_col: "minutes"}).copy()
            for candidates, target in [
                (["plays", "events", "count"], "plays"),
                (["tracks", "n_tracks"], "tracks"),
                (["top_artist", "top_artists", "most_played_artists"], "top_artists"),
            ]:
                match = next((cols[c] for c in candidates if c in cols), None)
                if match:
                    df[target] = hours[match]
            return df

    return None


def section_heatmap(data: dict) -> None:
    st.markdown('<div class="eyebrow">LISTENING TIMES</div>', unsafe_allow_html=True)
    st.subheader("When I Listen")
    st.caption("Click a circle to inspect listening by weekday and time. Larger circles mean more minutes.")

    heat = build_heatmap_table(data)
    if heat is None:
        st.info("This section needs either an hours.parquet table with weekday/bucket/minutes columns, "
                 "or a timestamp column on plays.parquet. Tell me the real column names and I'll wire it up.")
        return

    fig = px.scatter(
        heat, x="bucket", y="weekday", size="minutes", color="minutes",
        category_orders={"bucket": BUCKETS, "weekday": list(reversed(WEEKDAYS))},
        color_continuous_scale=[[0, COLORS["cyan"]], [1, COLORS["coral"]]],
        size_max=22,
        hover_data=[c for c in ["plays", "tracks", "top_artists"] if c in heat.columns],
    )
    fig.update_traces(marker=dict(line=dict(color=COLORS["ink"], width=1)))
    fig.update_layout(height=280, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                       coloraxis_showscale=False)
    style_axes(fig, f"Time of Day ({TZ_LABEL})", "Weekday")
    # Time buckets like "00-04" are text, not dates: force category axes so plotly doesn't read them as years
    fig.update_xaxes(type="category", categoryorder="array", categoryarray=BUCKETS)
    fig.update_yaxes(type="category")
    if set(heat["bucket"]).issubset(set(BUCKETS)):
        fig.update_xaxes(tickmode="array", tickvals=BUCKETS, ticktext=[BUCKET_LABELS[b] for b in BUCKETS])
    event = st.plotly_chart(fig, on_select="rerun", selection_mode="points", key="heatmap")

    if event and event.selection and event.selection.points:
        point = event.selection.points[0]
        row = heat.iloc[int(point["point_index"])]
        bits = [f"{row['minutes']:.1f} minutes"]
        if "plays" in row:
            bits.append(f"{int(row['plays'])} events")
        if "tracks" in row:
            bits.append(f"{int(row['tracks'])} tracks")
        lines = [" · ".join(bits)]
        if "top_artists" in row and row["top_artists"]:
            lines.append(f"Most-played artists: {row['top_artists']}")
        info_card(f"{row['weekday']}, {BUCKET_LABELS.get(row['bucket'], row['bucket'])} {TZ_LABEL}", lines)


# ----------------------------------------------------------------------------
# Recommendation engine
# ----------------------------------------------------------------------------
_STOPWORDS = {
    "something", "songs", "song", "music", "about", "with", "that", "this", "like", "some",
    "want", "need", "feel", "feeling", "make", "play", "listen", "hear", "good", "just",
    "really", "little", "tracks", "track", "artist", "artists", "genre", "genres", "from",
    "your", "have", "what", "when", "then", "them", "they", "into", "than", "very", "kind",
    "type", "sort", "mood", "vibe", "vibes", "stuff", "things",
}


def _norm_text(s: str) -> str:
    """Lowercase, drop '&', and turn every other symbol into a single space."""
    s = (s or "").lower().replace("&", "")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def _genre_parts(genre: str) -> list:
    """'Hip-Hop/Rap' -> ['hiphop', 'rap']"""
    parts = (_norm_text(p).replace(" ", "") for p in str(genre).split("/"))
    return [p for p in parts if p]


def _match_genres(target: str, available) -> list:
    """Find the genres in the data that correspond to a lexicon genre name."""
    t_parts = _genre_parts(target)
    out = []
    for g in available:
        g_parts = _genre_parts(g)
        if any(tp == gp or (len(tp) >= 4 and tp in gp) or (len(gp) >= 4 and gp in tp)
               for tp in t_parts for gp in g_parts):
            out.append(g)
    return out


def load_mood_lexicon() -> dict:
    return {
        "rainy_moody": {
            "keywords": ["rain", "rainy", "moody", "sad", "dramatic", "melancholy", "heartbreak",
                         "cry", "crying", "lonely", "gloomy", "blue", "emotional", "somber",
                         "breakup", "heartbroken", "broken", "tears", "stormy", "drizzle", "autumn"],
            "genres": ["R&B/Soul", "Alternative", "Jazz"],
        },
        "energetic": {
            "keywords": ["workout", "energy", "hype", "party", "pump", "pumped", "gym", "run", "running",
                         "upbeat", "dance", "fast", "intense", "adrenaline", "hyped", "cardio",
                         "club", "festival", "banger", "cleaning"],
            "genres": ["K-Pop", "Pop", "Dance", "Hip-Hop/Rap", "Hard Rock"],
        },
        "calm": {
            "keywords": ["calm", "quiet", "soft", "relax", "relaxing", "chill", "sleep", "sleepy", "study",
                         "focus", "mellow", "peaceful", "gentle", "unwind", "lofi", "lo-fi",
                         "meditate", "meditation", "ambient", "slow", "bedtime", "reading"],
            "genres": ["Relaxation", "Jazz", "Soundtrack"],
        },
        "happy": {
            "keywords": ["happy", "fun", "feel good", "summer", "sunny", "bright", "cheerful",
                         "joy", "joyful", "positive", "good vibes", "smile", "sunshine", "playful", "cute", "bubbly"],
            "genres": ["Pop", "K-Pop", "Dance"],
        },
        "aggressive": {
            "keywords": ["angry", "aggressive", "rage", "hard", "heavy", "dark", "moshpit",
                         "mad", "furious", "loud", "punk", "metal", "scream"],
            "genres": ["Hard Rock", "Rock", "Hip-Hop/Rap"],
        },
        "romantic": {
            "keywords": ["romantic", "love", "crush", "valentine", "sweet", "intimate",
                         "date", "date night", "wedding", "slow dance", "butterflies"],
            "genres": ["R&B/Soul", "Pop"],
        },
        "nostalgic": {
            "keywords": ["nostalgic", "throwback", "old school", "retro", "classic", "memories",
                         "childhood", "oldies", "vintage", "remember", "80s", "90s", "2000s"],
            "genres": ["Soundtrack", "Rock"],
        },
        "late_night": {
            "keywords": ["late night", "midnight", "night drive", "drive", "driving", "road trip", "2am", "3am"],
            "genres": ["R&B/Soul", "Alternative", "Hip-Hop/Rap", "Dance"],
        },
        "cozy": {
            "keywords": ["cozy", "coffee", "warm", "acoustic", "rainy sunday", "blanket", "fireplace"],
            "genres": ["Jazz", "Soundtrack", "R&B/Soul", "Alternative", "Relaxation"],
        },
        "confident": {
            "keywords": ["confident", "boss", "swagger", "strut", "baddie", "empowered", "main character", "powerful"],
            "genres": ["Hip-Hop/Rap", "Pop", "K-Pop", "R&B/Soul"],
        },
        "dreamy": {
            "keywords": ["dreamy", "floaty", "ethereal", "spacey", "daydream", "airy"],
            "genres": ["Alternative", "Relaxation", "Soundtrack"],
        },
        "epic": {
            "keywords": ["epic", "cinematic", "movie", "film", "anime", "orchestral", "grand"],
            "genres": ["Soundtrack", "Hard Rock", "Rock"],
        },
    }


def score_genre_affinity(text: str, lexicon: dict, available_genres=None) -> tuple[dict, bool]:
    text = (text or "").lower()
    affinity: dict = {}
    matched_any = False
    for mood in lexicon.values():
        hits = sum(1 for kw in mood["keywords"]
                   if re.search(rf"\b{re.escape(kw)}(?:s|es|ed|ing|y)?\b", text))
        if hits:
            matched_any = True
            for g in mood["genres"]:
                targets = _match_genres(g, available_genres) if available_genres is not None else [g]
                for t in targets:
                    affinity[t] = affinity.get(t, 0) + hits
    return affinity, matched_any


def fuzzy_genre_fallback(text: str, tracks: pd.DataFrame) -> dict:
    """Match the text straight against genre names (whole words only)."""
    text_norm = _norm_text(text)
    affinity: dict = {}
    if not text_norm:
        return affinity
    padded = f" {text_norm} "
    words = set(text_norm.split())
    for genre in tracks["genre"].dropna().unique():
        for part in str(genre).split("/"):
            p = _norm_text(part)
            if not p:
                continue
            if f" {p} " in padded or p.replace(" ", "") in words:
                affinity[genre] = affinity.get(genre, 0) + 3
                break
    return affinity


def recommend_tracks(tracks: pd.DataFrame, request_text: str, selected_genres: list, limit: int = 7):
    pool = tracks.copy()
    lexicon = load_mood_lexicon()
    available = pool["genre"].dropna().unique()
    affinity, matched_any = score_genre_affinity(request_text, lexicon, available)
    for g, v in fuzzy_genre_fallback(request_text, pool).items():
        affinity[g] = affinity.get(g, 0) + v

    if selected_genres:
        narrowed = pool[pool["genre"].isin(selected_genres)]
        if not narrowed.empty:
            pool = narrowed.copy()

    if "recommend_score" not in pool.columns:
        full_rate = pd.to_numeric(pool.get("full_rate", 0), errors="coerce").fillna(0)
        friction = pd.to_numeric(pool.get("friction_rate", 0), errors="coerce").fillna(0)
        plays_rank = pd.to_numeric(pool["plays"], errors="coerce").fillna(0).rank(pct=True)
        pool = pool.assign(recommend_score=(0.6 * (0.6 * full_rate + 0.4 * (1 - friction)) + 0.4 * plays_rank).clip(0, 1))
    else:
        pool = pool.copy()

    text_lower = (request_text or "").lower().strip()
    text_norm = _norm_text(text_lower)
    padded = f" {text_norm} "
    tokens = {w for w in text_norm.split() if len(w) >= 4 and w not in _STOPWORDS}

    def text_boost(row) -> float:
        boost = 0.0
        if not text_norm:
            return boost
        artist = _norm_text(str(row.get("artist", "")))
        track = _norm_text(str(row.get("track", "")))
        if artist and f" {artist} " in padded:
            boost += 0.5
        if len(track) >= 3 and f" {track} " in padded:
            boost += 0.5
        if boost == 0 and tokens and tokens & set(f"{artist} {track}".split()):
            boost = 0.25
        return boost

    pool["genre_affinity"] = pool["genre"].map(lambda g: affinity.get(g, 0))
    max_affinity = max(affinity.values()) if affinity else 0
    pool["genre_affinity_norm"] = (pool["genre_affinity"] / max_affinity) if max_affinity else 0.0
    pool["text_boost"] = pool.apply(text_boost, axis=1)

    has_prompt_signal = bool(text_lower) and (max_affinity > 0 or pool["text_boost"].max() > 0)
    prompt_weight = 0.55 if has_prompt_signal else 0.0

    pool["final_score"] = (
        prompt_weight * (0.7 * pool["genre_affinity_norm"] + 0.3 * (pool["text_boost"] > 0).astype(float))
        + (1 - prompt_weight) * pool["recommend_score"]
        + pool["text_boost"]
    ).clip(lower=0)

    pool = pool.sort_values(["final_score", "plays"], ascending=False).drop_duplicates(["track", "artist"])
    return pool.head(limit), has_prompt_signal


# ----------------------------------------------------------------------------
# Selection helpers (used as button callbacks so state updates before the rerun)
# ----------------------------------------------------------------------------
def _toggle_selection(item: str) -> None:
    sel = st.session_state.setdefault("my_selection", [])
    if item in sel:
        sel.remove(item)
    else:
        sel.append(item)


def _clear_selection() -> None:
    st.session_state["my_selection"] = []


# ----------------------------------------------------------------------------
# Recommendation tab UI
# ----------------------------------------------------------------------------
def section_recommend(data: dict) -> None:
    tracks = data["tracks"]

    with st.container(key="player"):
        left, right = st.columns([0.45, 0.55])

        with left:
            st.subheader("What do you want to hear?")
            st.caption("You can search by artist, genre, or something else.")
            request_text = st.text_area("Your request", placeholder="a rainy night, a little dramatic",
                                         key="rec_request", height=90, label_visibility="collapsed")

            st.caption("Pick by Mood")
            quick = st.pills("Quick moods", QUICK_MOODS,
                              selection_mode="multi", key="quick_moods", label_visibility="collapsed")
            quick_text = " ".join(q.lower() for q in (quick or []))
            combined_text = f"{request_text or ''} {quick_text}".strip()

            genre_pool = set(tracks["genre"].dropna().unique())
            if "genre" in data["genres"].columns:
                genre_pool |= set(data["genres"]["genre"].dropna().unique())
            genre_options = sorted(g for g in genre_pool if g != "Unknown Genre")
            st.caption("Narrow the Genre")
            with st.container(height=230):
                chosen_genres = st.pills("Genres", genre_options, selection_mode="multi",
                                          key="rec_genres", label_visibility="collapsed")

            go = st.button("Get Recommendations ↗", type="primary", use_container_width=True)

        # Recompute on button click, on first load, or whenever the inputs change
        signature = (combined_text, tuple(sorted(chosen_genres or [])))
        if go or "rec_results" not in st.session_state or st.session_state.get("rec_signature") != signature:
            results, has_signal = recommend_tracks(tracks, combined_text, chosen_genres or [], limit=7)
            st.session_state["rec_results"] = results
            st.session_state["rec_request_display"] = combined_text
            st.session_state["rec_has_signal"] = has_signal
            st.session_state["rec_signature"] = signature

        results = st.session_state.get("rec_results", pd.DataFrame())
        request_display = st.session_state.get("rec_request_display", "")
        selection = st.session_state.setdefault("my_selection", [])

        with right:
            with st.container(key="player_screen"):
                st.subheader("Recommended Tracks")
                if request_display:
                    st.caption(f"Request: {request_display}")
                    if not st.session_state.get("rec_has_signal", False):
                        st.caption("No mood, genre, or artist match, so these are my most-listened favorites.")

                for i, row in enumerate(results.itertuples(), start=1):
                    item = f"{row.track} — {row.artist}"
                    in_sel = item in selection
                    c1, c2, c3 = st.columns([0.12, 0.76, 0.12])
                    with c1:
                        color = PALETTE[(i - 1) % len(PALETTE)]
                        st.markdown(f'<div class="rank-chip" style="background:{color}">{i:02d}</div>', unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"**{row.track}**<br><span class='muted'>{row.artist} · {row.genre}</span>",
                                    unsafe_allow_html=True)
                    with c3:
                        st.button("✓" if in_sel else "+", key=f"add_{i}_{row.track}_{row.artist}",
                                  help="Remove from selection" if in_sel else "Add to selection",
                                  on_click=_toggle_selection, args=(item,))

                if st.button("+ Add a track to your selection", key="manual_add_toggle"):
                    st.session_state["show_manual_add"] = not st.session_state.get("show_manual_add", False)

                if st.session_state.get("show_manual_add"):
                    manual_query = st.text_input("Search your library", key="manual_search")
                    if manual_query:
                        matches = tracks[
                            tracks["track"].str.contains(manual_query, case=False, na=False)
                            | tracks["artist"].str.contains(manual_query, case=False, na=False)
                        ].drop_duplicates(["track", "artist"]).head(5)
                        for row in matches.itertuples():
                            item = f"{row.track} — {row.artist}"
                            st.button(f"{'Remove' if item in selection else 'Add'} {item}",
                                      key=f"manual_{row.track}_{row.artist}",
                                      on_click=_toggle_selection, args=(item,))

                if selection:
                    with st.expander(f"Your selection ({len(selection)})", expanded=True):
                        for i, item in enumerate(list(selection)):
                            c1, c2 = st.columns([0.86, 0.14])
                            with c1:
                                st.write("• " + item)
                            with c2:
                                st.button("✕", key=f"remove_{i}_{item}", help="Remove from selection",
                                          on_click=_toggle_selection, args=(item,))
                        st.button("Clear selection", key="clear_selection", on_click=_clear_selection)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main() -> None:
    style()
    data = load_data()
    hero(data)
    pink_divider()

    tab1, tab2 = st.tabs(["01. MY MUSIC BREAKDOWN", "02. GET A RECOMMENDATION"])

    with tab1:
        left, right = st.columns([0.36, 0.64], gap="medium")

        with left:
            with st.container(key="panel_overview"):
                section_overview(data)
            with st.container(key="panel_genres"):
                section_genres(data)

        with right:
            with st.container(key="panel_artists"):
                section_artists(data)
            with st.container(key="panel_repeat"):
                section_repeat(data)
            with st.container(key="panel_daily"):
                section_daily(data)
            with st.container(key="panel_heatmap"):
                section_heatmap(data)

    with tab2:
        section_recommend(data)


if __name__ == "__main__":
    main()