import base64
import html
import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from music_analytics.paths import clean_path, root_path


st.set_page_config(
    page_title="Sumi's Music Universe",
    layout="wide",
)


color = {
    "page": "#EEF9FF",
    "page2": "#F6FCFF",
    "panel": "rgba(235, 247, 255, 0.68)",
    "text": "#101010",
    "body": "#222222",
    "soft": "#4A4A4A",
    "line": "#101010",
    "border": "#A8C7D8",
    "grid": "rgba(104, 143, 160, 0.16)",
    "sky": "#71CFF2",
    "cyan": "#54C7EC",
    "mint": "#8BE8C7",
    "yellow": "#F5D76E",
    "coral": "#F9786B",
    "pink": "#F7A7C8",
    "purple": "#B9A2F7",
    "teal": "#4DC6B6",
    "orange": "#F6A04D",
    "gray": "#C8D4DA",
    "slate": "#7E9099",
    "red": "#E95A4F",
}


genre_color = {
    "K-Pop": "#71CFF2",
    "Pop": "#F7A7C8",
    "Alternative": "#F9786B",
    "R&B/Soul": "#8BE8C7",
    "Hip-Hop/Rap": "#4DC6B6",
    "Relaxation": "#F5D76E",
    "Electronic": "#F6A04D",
    "Soundtrack": "#B9A2F7",
    "Jazz": "#C8D4DA",
    "Rock": "#7E9099",
    "Hard Rock": "#6F7F88",
    "Unknown Genre": "#D2DEE4",
}


role_color = {
    "Playlist": "#8BE8C7",
    "Discovery": "#71CFF2",
    "Playback": "#F9786B",
    "Browsing": "#B9A2F7",
    "Unknown": "#C8D4DA",
}


class_color = {
    "Core Favorite": "#54C7EC",
    "Rediscovery Candidate": "#8BE8C7",
    "Overexposed or Unstable": "#F6A04D",
    "General Candidate": "#B9A2F7",
    "Lost Discovery": "#F7A7C8",
    "Exclude From Recommendations": "#C8D4DA",
}


role_name = {
    "Core Favorite": "Keep Close",
    "Rediscovery Candidate": "Rediscover",
    "Overexposed or Unstable": "Risky",
    "General Candidate": "Bring Back",
    "Lost Discovery": "Faded",
    "Exclude From Recommendations": "Leave Alone",
}


name_map = {
    "start": "Started",
    "end": "Ended",
    "date": "Date",
    "played_at": "Played",
    "minutes": "Minutes",
    "plays": "Plays",
    "tracks": "Tracks",
    "artists": "Artists",
    "albums": "Albums",
    "genres": "Genres",
    "top_artist": "Top Artist",
    "top_genre": "Top Genre",
    "top_source": "Top Source",
    "source_label": "Source",
    "source_role": "Source Type",
    "session_type": "Session",
    "full_rate": "Completion",
    "friction_rate": "Skip Rate",
    "affinity_score": "Affinity",
    "ready_reason": "Reason",
    "candidate_class": "Role",
    "recommender_ready": "Ready?",
    "active_days": "Active Days",
    "playlist_count": "Playlists",
    "display": "Track",
    "artist": "Artist",
    "album": "Album",
    "genre": "Genre",
    "track": "Track",
    "route_value": "Route Strength",
    "discoveries": "Discoveries",
    "discovery_share": "Discovery",
    "repeat_share": "Repeats",
    "play_share": "Completion",
    "first_plays": "First Plays",
    "repeat_plays": "Repeat Plays",
    "full_plays": "Completed Plays",
    "friction_plays": "Skipped Plays",
}


def font_css() -> str:
    paths = [
        root_path / "assets" / "fonts" / "Poxel.ttf",
        root_path / "assets" / "fonts" / "Poxel Font.ttf",
        root_path / "assets" / "fonts" / "Poxel.otf",
        root_path / "assets" / "fonts" / "Poxel Font.otf",
    ]

    for path in paths:
        if path.exists():
            data = base64.b64encode(path.read_bytes()).decode("utf-8")
            kind = "opentype" if path.suffix.lower() == ".otf" else "truetype"
            return f"""
            @font-face {{
                font-family: "Poxel Local";
                src: url(data:font/{kind};base64,{data}) format("{kind}");
                font-weight: 400;
                font-style: normal;
                font-display: swap;
            }}
            """

    return ""


def page_style() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Pixelify+Sans:wght@400;600;700&display=swap');

        {font_css()}

        :root {{
            --game: "Poxel Local", "Pixelify Sans", monospace;
            --body: "Nunito", "Quicksand", "DM Sans", "Arial Rounded MT Bold", sans-serif;
            --page: #EEF9FF;
            --text: #101010;
            --bodyText: #222222;
            --soft: #4A4A4A;
            --border: #A8C7D8;
            --cyan: #54C7EC;
            --mint: #8BE8C7;
            --coral: #F9786B;
            --yellow: #F5D76E;
            --purple: #B9A2F7;
            --gray: #C8D4DA;
        }}

        html, body, [data-testid="stAppViewContainer"] {{
            background:
                linear-gradient(rgba(168,199,216,0.04) 1px, transparent 1px),
                linear-gradient(90deg, rgba(168,199,216,0.04) 1px, transparent 1px),
                radial-gradient(circle at 10% 5%, rgba(113,207,242,0.14), transparent 30%),
                radial-gradient(circle at 88% 12%, rgba(247,167,200,0.10), transparent 28%),
                radial-gradient(circle at 52% 96%, rgba(139,232,199,0.10), transparent 32%),
                #EEF9FF !important;
            background-size: 32px 32px, 32px 32px, auto, auto, auto, auto !important;
            color: var(--text) !important;
            font-family: var(--body) !important;
        }}

        [data-testid="stHeader"] {{
            background: rgba(238, 249, 255, 0.86) !important;
        }}

        .block-container {{
            max-width: 1360px;
            padding-top: 1.15rem;
            padding-bottom: 3.7rem;
        }}

        h1, h2, h3, h4 {{
            color: var(--text) !important;
        }}

        h2 {{
            font-family: var(--game) !important;
            font-size: 1.85rem !important;
            letter-spacing: 0.01em !important;
            margin-top: 0.7rem !important;
            margin-bottom: 0.2rem !important;
        }}

        h3, h4 {{
            font-family: var(--body) !important;
            font-weight: 800 !important;
            letter-spacing: -0.01em !important;
        }}

        p, div, span, label {{
            font-family: var(--body);
            color: var(--bodyText);
        }}

        [data-testid="stSidebar"] {{
            background: rgba(226, 245, 253, 0.88) !important;
            border-right: 1px solid rgba(168,199,216,0.72);
        }}

        [data-testid="stSidebar"] * {{
            color: var(--text) !important;
        }}

        .top-shell {{
            margin-bottom: 0.85rem;
        }}

        .pixel-logo {{
            display: inline-block;
            font-family: var(--game);
            font-size: 0.98rem;
            line-height: 1;
            letter-spacing: 0.035em;
            color: #101010;
            background: rgba(255,255,255,0.22);
            border: 1px solid rgba(16,16,16,0.22);
            border-radius: 13px;
            padding: 0.38rem 0.58rem;
            box-shadow: 2px 2px 0 rgba(84,199,236,0.18);
        }}

        .hero {{
            padding: 2.05rem 0 1.15rem 0;
        }}

        .hero-title {{
            font-family: var(--game);
            font-size: clamp(2.05rem, 4.9vw, 4.35rem);
            line-height: 0.98;
            color: #101010;
            letter-spacing: 0.01em;
            margin: 0;
            max-width: 960px;
            text-shadow: 2px 2px 0 rgba(255,255,255,0.80), 4px 4px 0 rgba(84,199,236,0.18);
        }}

        .hero-subtitle {{
            font-family: var(--body);
            font-size: 1.14rem;
            color: #4A4A4A;
            margin: 0.8rem 0 0 0.1rem;
            font-weight: 700;
        }}

        .purpose {{
            max-width: 880px;
            color: #4A4A4A;
            font-size: 1.02rem;
            line-height: 1.45;
            margin-top: 0.15rem;
            margin-bottom: 0.9rem;
        }}

        .summary {{
            max-width: 900px;
            border-left: 4px solid #54C7EC;
            padding: 0.72rem 0 0.72rem 0.9rem;
            margin: 0.75rem 0 1.1rem 0;
        }}

        .summary-title {{
            font-weight: 800;
            font-size: 0.92rem;
            color: #101010;
            margin-bottom: 0.25rem;
        }}

        .summary-body {{
            color: #4A4A4A;
            margin: 0;
            font-size: 0.98rem;
            line-height: 1.45;
        }}

        .identity-card {{
            border: 1px solid rgba(168,199,216,0.78);
            border-radius: 22px;
            padding: 1.1rem 1.2rem;
            background: rgba(235,247,255,0.58);
            margin-bottom: 1rem;
        }}

        .identity-title {{
            font-weight: 800;
            color: #101010;
            font-size: 1.12rem;
            margin-bottom: 0.3rem;
        }}

        .identity-text {{
            font-size: 1.02rem;
            color: #222222;
            line-height: 1.48;
            max-width: 950px;
            margin: 0;
        }}

        .section-text {{
            max-width: 900px;
            color: #4A4A4A;
            font-size: 0.98rem;
            line-height: 1.45;
            margin: 0.1rem 0 0.75rem 0;
        }}

        .peak-card {{
            border: 1px solid rgba(168,199,216,0.78);
            border-radius: 20px;
            padding: 0.95rem 1rem;
            background: rgba(235,247,255,0.55);
            margin: 0.65rem 0 1rem 0;
        }}

        .peak-card p {{
            margin: 0.45rem 0 0 0;
            color: #222222;
            line-height: 1.45;
        }}

        .chip {{
            display: inline-block;
            font-size: 0.78rem;
            font-weight: 800;
            padding: 0.18rem 0.52rem;
            margin: 0.1rem 0.12rem 0.1rem 0;
            border-radius: 999px;
            border: 1px solid rgba(16,16,16,0.18);
            background: rgba(255,255,255,0.26);
            color: #101010;
        }}

        .caption {{
            max-width: 900px;
            font-size: 0.94rem;
            color: #4A4A4A;
            margin: -0.25rem 0 1rem 0;
            line-height: 1.42;
        }}

        .map-row {{
            display: flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0.26rem 0;
            color: #222222;
            font-size: 0.92rem;
        }}

        .key-dot {{
            width: 0.68rem;
            height: 0.68rem;
            border-radius: 999px;
            border: 1px solid #101010;
            display: inline-block;
            flex: 0 0 auto;
        }}

        .ledger {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 0.83rem;
            background: rgba(235,247,255,0.60);
            border: 1px solid rgba(168,199,216,0.76);
            border-radius: 18px;
            overflow: hidden;
        }}

        .ledger th {{
            position: sticky;
            top: 0;
            font-size: 0.78rem;
            font-weight: 800;
            text-align: left;
            padding: 0.66rem;
            border-bottom: 1px solid rgba(168,199,216,0.82);
            color: #101010;
            background: rgba(221,242,251,0.94);
            z-index: 2;
        }}

        .ledger td {{
            padding: 0.60rem 0.66rem;
            border-bottom: 1px solid rgba(168,199,216,0.38);
            color: #222222;
            vertical-align: top;
            max-width: 300px;
            overflow-wrap: anywhere;
            line-height: 1.35;
        }}

        .ledger tr:hover {{
            background: rgba(113,207,242,0.12);
        }}

        .pill {{
            display: inline-block;
            border-radius: 999px;
            padding: 0.16rem 0.46rem;
            font-size: 0.72rem;
            font-weight: 800;
            border: 1px solid rgba(16,16,16,0.18);
            background: rgba(255,255,255,0.30);
            color: #101010;
            white-space: nowrap;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.28rem;
            background: transparent;
            border-bottom: 1px solid rgba(168,199,216,0.72);
            padding-bottom: 0.35rem;
            margin-bottom: 1.25rem;
        }}

        .stTabs [data-baseweb="tab"] {{
            height: 2.2rem;
            border-radius: 999px;
            color: #101010 !important;
            background: rgba(255,255,255,0.12);
            border: 1px solid transparent;
            font-family: var(--body) !important;
            font-weight: 800;
            font-size: 0.92rem;
            padding-left: 0.9rem;
            padding-right: 0.9rem;
        }}

        .stTabs [data-baseweb="tab"]:hover {{
            background: rgba(255,255,255,0.24);
            border-color: rgba(168,199,216,0.70);
        }}

        .stTabs [aria-selected="true"] {{
            background: rgba(84,199,236,0.12);
            border: 1px solid rgba(84,199,236,0.95);
            box-shadow: inset 0 -3px 0 #54C7EC;
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid rgba(168,199,216,0.76);
            border-radius: 18px;
            overflow: hidden;
            background: rgba(235,247,255,0.58);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero() -> None:
    st.markdown(
        """
        <div class="top-shell">
            <span class="pixel-logo">Sumi's Music Universe</span>
            <div class="hero">
                <div class="hero-title">Hi, I’m Sumi, and this is my music universe.</div>
                <div class="hero-subtitle">Explore it with me.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def map_key() -> None:
    with st.expander("Map Key", expanded=False):
        st.markdown(
            """
            <div class="map-row"><span class="key-dot" style="background:#71CFF2;"></span><span>Circle size: more listening.</span></div>
            <div class="map-row"><span class="key-dot" style="background:#FFFFFF;"></span><span>Ring thickness: stronger signal.</span></div>
            <div class="map-row"><span class="key-dot" style="background:#F5D76E;"></span><span>Glow: important moment.</span></div>
            <div class="map-row"><span class="key-dot" style="background:#54C7EC;"></span><span>Cyan: listening or repeat history.</span></div>
            <div class="map-row"><span class="key-dot" style="background:#8BE8C7;"></span><span>Mint: discovery or source routes.</span></div>
            <div class="map-row"><span class="key-dot" style="background:#F9786B;"></span><span>Coral: skips or friction.</span></div>
            <div class="map-row"><span class="key-dot" style="background:#F5D76E;"></span><span>Yellow: peak activity.</span></div>
            <div class="map-row"><span class="key-dot" style="background:#B9A2F7;"></span><span>Purple: recommendations.</span></div>
            <div class="map-row"><span class="key-dot" style="background:#C8D4DA;"></span><span>Gray: unknown or low signal.</span></div>
            """,
            unsafe_allow_html=True,
        )


def page_head(title: str, text: str) -> None:
    st.subheader(title)
    st.markdown(f"<div class='purpose'>{html.escape(text)}</div>", unsafe_allow_html=True)


def summary(text: str) -> None:
    st.markdown(
        f"""
        <div class="summary">
            <div class="summary-title">Summary</div>
            <p class="summary-body">{html.escape(text)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def paragraph(text: str) -> None:
    st.markdown(f"<div class='section-text'>{html.escape(text)}</div>", unsafe_allow_html=True)


def caption(text: str) -> None:
    st.markdown(f"<div class='caption'>{html.escape(text)}</div>", unsafe_allow_html=True)


def need_table(name: str) -> Path:
    path = clean_path / f"{name}.parquet"

    if not path.exists():
        raise FileNotFoundError("Processed data is missing. Stop Streamlit and run python3 scripts/make_data.py first.")

    return path


@st.cache_data(show_spinner=False)
def load_table(name: str) -> pd.DataFrame:
    return pd.read_parquet(need_table(name))


@st.cache_data(show_spinner=False)
def load_data() -> dict[str, pd.DataFrame]:
    return {
        "plays": load_table("plays"),
        "tracks": load_table("tracks"),
        "artists": load_table("artists"),
        "albums": load_table("albums"),
        "genres": load_table("genres"),
        "days": load_table("days"),
        "hours": load_table("hours"),
        "sources": load_table("sources"),
        "sessions": load_table("sessions"),
        "features": load_table("features"),
        "life": load_table("life"),
        "profile": load_table("profile"),
    }


def base_chart(chart: go.Figure, height: int = 420) -> go.Figure:
    chart.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(238,249,255,0.15)",
        font={"color": color["text"], "family": "Nunito, Quicksand, sans-serif"},
        title={"font": {"size": 19, "color": color["text"], "family": "Poxel Local, Pixelify Sans, Nunito, sans-serif"}, "x": 0.02},
        margin={"l": 52, "r": 24, "t": 58, "b": 46},
        hoverlabel={
            "bgcolor": "#F6FCFF",
            "bordercolor": "#A8C7D8",
            "font": {"color": "#101010", "family": "Nunito"},
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {"size": 11, "color": color["text"], "family": "Nunito"},
            "bgcolor": "rgba(255,255,255,0.0)",
        },
    )

    chart.update_xaxes(
        showgrid=True,
        gridcolor=color["grid"],
        zeroline=False,
        linecolor="rgba(16,16,16,0.26)",
        tickfont={"color": color["text"], "family": "Nunito"},
        title_font={"color": color["text"], "family": "Nunito"},
    )

    chart.update_yaxes(
        showgrid=True,
        gridcolor=color["grid"],
        zeroline=False,
        linecolor="rgba(16,16,16,0.26)",
        tickfont={"color": color["text"], "family": "Nunito"},
        title_font={"color": color["text"], "family": "Nunito"},
    )

    return chart


chart_count = 0


def show_chart(chart: go.Figure, key: str | None = None):
    global chart_count

    chart_count += 1

    if key is None:
        key = f"plotly_chart_{chart_count}"

    return st.plotly_chart(
        chart,
        width="stretch",
        key=key,
        config={"displayModeBar": False, "responsive": True},
    )

def short_text(value, size: int = 40) -> str:
    text = str(value)

    if len(text) <= size:
        return text

    return text[: size - 1] + "…"


def rate_text(value) -> str:
    if pd.isna(value):
        return "0.0%"

    return f"{float(value):.1%}"


def count_text(value) -> str:
    if pd.isna(value):
        return "0"

    return f"{float(value):,.0f}"


def date_time(value, short: bool = True) -> str:
    if pd.isna(value):
        return ""

    time = pd.to_datetime(value)

    if short:
        return time.strftime("%b %-d · %-I:%M %p")

    return time.strftime("%b %-d, %Y · %-I:%M %p")


def day_text(value) -> str:
    if pd.isna(value):
        return ""

    return pd.to_datetime(value).strftime("%b %-d, %Y")


def score_value(profile: pd.DataFrame, metric: str) -> float:
    row = profile[profile["metric"].eq(metric)]

    if row.empty:
        return 0.0

    return float(row["score"].iloc[0])


def label_value(profile: pd.DataFrame, metric: str) -> str:
    row = profile[profile["metric"].eq(metric)]

    if row.empty:
        return ""

    return str(row["value"].iloc[0])


def top_value(value: pd.Series) -> str:
    value = value.dropna().astype(str)

    if value.empty:
        return "Unknown"

    return value.value_counts().index[0]


def display_table(data: pd.DataFrame, rows: int = 50, pill: str | None = None) -> str:
    shown = data.head(rows).copy()

    for column in shown.columns:
        if column in {"start", "end", "played_at"}:
            shown[column] = shown[column].map(lambda value: date_time(value, short=True) if pd.notna(value) else "")

        elif column == "date":
            shown[column] = shown[column].map(lambda value: day_text(value) if pd.notna(value) else "")

        elif column == "affinity_score":
            shown[column] = shown[column].map(lambda value: f"{float(value):.3f}" if pd.notna(value) else "")

        elif "rate" in column or "share" in column:
            shown[column] = shown[column].map(lambda value: rate_text(value) if pd.notna(value) else "")

        elif column == "minutes":
            shown[column] = shown[column].map(lambda value: f"{float(value):,.1f}" if pd.notna(value) else "")

        elif column in {"plays", "tracks", "artists", "albums", "genres", "active_days", "playlist_count", "discoveries", "route_value"}:
            shown[column] = shown[column].map(lambda value: count_text(value) if pd.notna(value) else "")

        elif column == "recommender_ready":
            shown[column] = shown[column].map(lambda value: "Ready" if bool(value) else "Not ready")

        elif column == "candidate_class":
            shown[column] = shown[column].map(lambda value: role_name.get(str(value), str(value)))

    shown = shown.rename(columns={column: name_map.get(column, column.replace("_", " ").title()) for column in shown.columns})

    html_text = "<table class='ledger'><thead><tr>"

    for column in shown.columns:
        html_text += f"<th>{html.escape(str(column))}</th>"

    html_text += "</tr></thead><tbody>"

    for _, row in shown.iterrows():
        html_text += "<tr>"

        for column in shown.columns:
            value = html.escape(str(row[column]))

            if pill is not None and column == pill:
                html_text += f"<td><span class='pill'>{value}</span></td>"
            else:
                html_text += f"<td>{value}</td>"

        html_text += "</tr>"

    html_text += "</tbody></table>"

    return html_text


def ring_chart(label: str, value: str, score: float, shade: str, note: str, hover: str) -> go.Figure:
    score = max(0.0, min(float(score), 1.0))
    angle = np.linspace(90, 90 - 360 * score, 130)
    base = np.linspace(0, 360, 260)

    chart = go.Figure()

    chart.add_trace(
        go.Scatterpolar(
            r=[1] * len(base),
            theta=base,
            mode="lines",
            line={"color": "rgba(16,16,16,0.10)", "width": 12},
            hoverinfo="skip",
            showlegend=False,
        )
    )

    chart.add_trace(
        go.Scatterpolar(
            r=[1] * len(angle),
            theta=angle,
            mode="lines",
            line={"color": shade, "width": 13},
            hovertemplate=f"{hover}<br>{value}<extra></extra>",
            showlegend=False,
        )
    )

    chart.add_trace(
        go.Scatterpolar(
            r=[1],
            theta=[90 - 360 * score],
            mode="markers",
            marker={"size": 12, "color": shade, "line": {"color": color["line"], "width": 1}},
            hovertemplate=f"{hover}<extra></extra>",
            showlegend=False,
        )
    )

    chart.add_annotation(
        x=0.5,
        y=0.57,
        text=f"<b>{value}</b>",
        showarrow=False,
        font={"size": 23, "color": color["text"], "family": "Nunito"},
    )

    chart.add_annotation(
        x=0.5,
        y=0.38,
        text=label,
        showarrow=False,
        font={"size": 11, "color": color["text"], "family": "Nunito"},
    )

    chart.add_annotation(
        x=0.5,
        y=0.24,
        text=note,
        showarrow=False,
        font={"size": 9, "color": color["soft"], "family": "Nunito"},
    )

    chart.update_layout(
        height=200,
        margin={"l": 6, "r": 6, "t": 6, "b": 6},
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel={"bgcolor": "#F6FCFF", "bordercolor": "#A8C7D8", "font": {"color": "#101010"}},
        polar={
            "bgcolor": "rgba(0,0,0,0)",
            "radialaxis": {"visible": False, "range": [0, 1.22]},
            "angularaxis": {"visible": False},
        },
    )

    return chart


def make_tracks(data: pd.DataFrame) -> pd.DataFrame:
    tracks = (
        data.groupby("track_key", dropna=False)
        .agg(
            display=("display", "first"),
            track=("track", "first"),
            artist=("artist", "first"),
            album=("album", "first"),
            genre=("genre", "first"),
            plays=("track_key", "size"),
            minutes=("minutes", "sum"),
            full_plays=("full_play", "sum"),
            friction_plays=("friction", "sum"),
            average_share=("play_share", "mean"),
            active_days=("date", "nunique"),
        )
        .reset_index()
    )

    tracks["full_rate"] = tracks["full_plays"] / tracks["plays"]
    tracks["friction_rate"] = tracks["friction_plays"] / tracks["plays"]

    return tracks.sort_values(["plays", "minutes"], ascending=[False, False]).reset_index(drop=True)


def make_artists(data: pd.DataFrame) -> pd.DataFrame:
    artists = (
        data.groupby("artist", dropna=False)
        .agg(
            plays=("track_key", "size"),
            tracks=("track_key", "nunique"),
            albums=("album", "nunique"),
            genres=("genre", "nunique"),
            minutes=("minutes", "sum"),
            full_plays=("full_play", "sum"),
            friction_plays=("friction", "sum"),
        )
        .reset_index()
    )

    artists["full_rate"] = artists["full_plays"] / artists["plays"]
    artists["friction_rate"] = artists["friction_plays"] / artists["plays"]

    return artists.sort_values(["plays", "minutes"], ascending=[False, False]).reset_index(drop=True)


def make_days(data: pd.DataFrame) -> pd.DataFrame:
    days = (
        data.groupby("date", dropna=True)
        .agg(
            plays=("track_key", "size"),
            tracks=("track_key", "nunique"),
            artists=("artist", "nunique"),
            minutes=("minutes", "sum"),
            full_plays=("full_play", "sum"),
            friction_plays=("friction", "sum"),
            top_artist=("artist", top_value),
            top_source=("source_label", top_value),
            top_genre=("genre", top_value),
        )
        .reset_index()
    )

    days["date"] = pd.to_datetime(days["date"])
    days["full_rate"] = days["full_plays"] / days["plays"]
    days["friction_rate"] = days["friction_plays"] / days["plays"]

    return days.sort_values("date").reset_index(drop=True)


def wave_chart(days: pd.DataFrame, title: str) -> go.Figure:
    data = days.copy()

    if data.empty:
        return base_chart(go.Figure(), 390)

    q1 = data["minutes"].quantile(0.50)
    q2 = data["minutes"].quantile(0.78)
    q3 = data["minutes"].quantile(0.93)

    data["tone"] = np.select(
        [data["minutes"].ge(q3), data["minutes"].ge(q2), data["minutes"].ge(q1)],
        [color["coral"], color["yellow"], color["cyan"]],
        default=color["sky"],
    )

    data["dot"] = 10 + 38 * (data["minutes"] / max(data["minutes"].max(), 1)).fillna(0)

    chart = go.Figure()

    chart.add_trace(
        go.Scatter(
            x=data["date"],
            y=data["minutes"],
            mode="markers",
            marker={
                "size": data["dot"],
                "color": data["tone"],
                "opacity": 0.74,
                "line": {"color": "rgba(16,16,16,0.34)", "width": 1},
            },
            customdata=data[["plays", "tracks", "artists", "top_artist", "top_genre", "top_source"]],
            hovertemplate="Listening Pulse<br>%{x|%b %-d, %Y}<br>Minutes: %{y:.1f}<br>Plays: %{customdata[0]:,}<br>Top Artist: %{customdata[3]}<br>Top Genre: %{customdata[4]}<br>Top Source: %{customdata[5]}<extra></extra>",
            showlegend=False,
        )
    )

    chart.add_trace(
        go.Scatter(
            x=data["date"],
            y=data["minutes"].rolling(7, min_periods=1).mean(),
            mode="lines",
            line={"color": "rgba(16,16,16,0.28)", "width": 1.2, "dash": "dot"},
            hoverinfo="skip",
            showlegend=False,
        )
    )

    for _, row in data.sort_values("minutes", ascending=False).head(3).iterrows():
        chart.add_annotation(
            x=row["date"],
            y=row["minutes"],
            text=f"{row['minutes']:.0f}",
            showarrow=True,
            arrowcolor="rgba(16,16,16,0.34)",
            font={"size": 11, "color": color["text"], "family": "Nunito"},
        )

    chart.update_layout(title=title)
    chart.update_xaxes(title_text="Date", tickformat="%b %Y")
    chart.update_yaxes(title_text="Minutes")

    return base_chart(chart, 415)


def split_ring(repeat: float, discovery: float) -> go.Figure:
    repeat = max(0.0, min(float(repeat), 1.0))
    discovery = max(0.0, min(float(discovery), 1.0))
    base = np.linspace(0, 360, 260)

    chart = go.Figure()

    for radius in [0.82, 1.08]:
        chart.add_trace(
            go.Scatterpolar(
                r=[radius] * len(base),
                theta=base,
                mode="lines",
                line={"color": "rgba(16,16,16,0.10)", "width": 13},
                showlegend=False,
                hoverinfo="skip",
            )
        )

    for value, radius, shade, name in [
        (repeat, 0.82, color["cyan"], "Repeat History"),
        (discovery, 1.08, color["sky"], "Discovery Edge"),
    ]:
        angle = np.linspace(90, 90 - 360 * value, 140)
        chart.add_trace(
            go.Scatterpolar(
                r=[radius] * len(angle),
                theta=angle,
                mode="lines",
                line={"color": shade, "width": 16},
                name=name,
                hovertemplate=f"{name}: {value:.1%}<extra></extra>",
            )
        )

    chart.add_annotation(
        x=0.5,
        y=0.56,
        text=f"<b>Repeat History</b><br>{repeat:.1%}",
        showarrow=False,
        font={"size": 17, "color": color["text"], "family": "Nunito"},
    )

    chart.add_annotation(
        x=0.5,
        y=0.34,
        text=f"Discovery Edge {discovery:.1%}",
        showarrow=False,
        font={"size": 11, "color": color["soft"], "family": "Nunito"},
    )

    chart.update_layout(
        title="Repeat History vs. Discovery",
        height=415,
        margin={"l": 18, "r": 18, "t": 58, "b": 18},
        paper_bgcolor="rgba(0,0,0,0)",
        polar={
            "bgcolor": "rgba(0,0,0,0)",
            "radialaxis": {"visible": False, "range": [0, 1.3]},
            "angularaxis": {"visible": False},
        },
        font={"color": color["text"], "family": "Nunito"},
        legend={"orientation": "h", "x": 0.18, "y": -0.04},
    )

    return chart


def rhythm_grid(data: pd.DataFrame, metric: str) -> go.Figure:
    hours = (
        data.groupby(["weekday_num", "weekday", "hour"], dropna=True)
        .agg(
            plays=("track_key", "size"),
            minutes=("minutes", "sum"),
            full_plays=("full_play", "sum"),
            friction_plays=("friction", "sum"),
        )
        .reset_index()
    )

    if hours.empty:
        return base_chart(go.Figure(), 420)

    hours["full_rate"] = hours["full_plays"] / hours["plays"]
    hours["friction_rate"] = hours["friction_plays"] / hours["plays"]

    scale = hours[metric].fillna(0)
    size = 10 + 40 * (scale / max(scale.max(), 1))
    shade = np.select(
        [scale.ge(scale.quantile(0.90)), scale.ge(scale.quantile(0.65))],
        [color["coral"], color["yellow"]],
        default=color["sky"],
    )

    chart = go.Figure()

    chart.add_trace(
        go.Scatter(
            x=hours["hour"],
            y=hours["weekday"],
            mode="markers",
            marker={
                "size": size,
                "color": shade,
                "opacity": 0.74,
                "line": {"color": "rgba(16,16,16,0.30)", "width": 1},
            },
            customdata=hours[["plays", "minutes", "full_rate", "friction_rate"]],
            hovertemplate="Daily Rhythm<br>%{y} at %{x}:00<br>Plays: %{customdata[0]}<br>Minutes: %{customdata[1]:.1f}<br>Completion: %{customdata[2]:.1%}<br>Skip Rate: %{customdata[3]:.1%}<extra></extra>",
            showlegend=False,
        )
    )

    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    chart.update_layout(title="Daily Rhythm")
    chart.update_xaxes(title_text="Hour", dtick=2)
    chart.update_yaxes(title_text="Weekday", categoryorder="array", categoryarray=list(reversed(order)))

    return base_chart(chart, 430)


def planet_chart(data: pd.DataFrame) -> go.Figure:
    genres = data.copy().sort_values("plays", ascending=False).head(12).reset_index(drop=True)

    if genres.empty:
        return base_chart(go.Figure(), 480)

    total = max(genres["plays"].sum(), 1)
    genres["share"] = genres["plays"] / total

    x_values = []
    y_values = []

    for place in range(len(genres)):
        if place == 0:
            x_values.append(0)
            y_values.append(0)
        else:
            angle = 2 * math.pi * (place - 1) / max(1, len(genres) - 1)
            radius = 1.55 + 0.18 * place
            x_values.append(radius * math.cos(angle))
            y_values.append(radius * math.sin(angle))

    genres["x"] = x_values
    genres["y"] = y_values
    genres["size"] = 46 + 138 * genres["share"]
    genres["shade"] = genres["genre"].map(lambda value: genre_color.get(str(value), color["gray"]))
    genres["label"] = np.where(genres.index < 6, genres["genre"], "")

    chart = go.Figure()

    for radius in [1.55, 2.05, 2.55, 3.05]:
        circle_x = [radius * math.cos(step) for step in np.linspace(0, 2 * math.pi, 160)]
        circle_y = [radius * math.sin(step) for step in np.linspace(0, 2 * math.pi, 160)]
        chart.add_trace(
            go.Scatter(
                x=circle_x,
                y=circle_y,
                mode="lines",
                line={"color": "rgba(16,16,16,0.08)", "width": 1},
                hoverinfo="skip",
                showlegend=False,
            )
        )

    chart.add_trace(
        go.Scatter(
            x=genres["x"],
            y=genres["y"],
            mode="markers+text",
            marker={
                "size": genres["size"],
                "color": genres["shade"],
                "opacity": 0.70,
                "line": {"color": "rgba(16,16,16,0.46)", "width": 1.2},
            },
            text=genres["label"],
            textposition="middle center",
            textfont={"size": 10, "color": color["text"], "family": "Nunito"},
            customdata=genres[["genre", "plays", "tracks", "artists", "minutes", "share", "full_rate", "friction_rate"]],
            hovertemplate="<b>%{customdata[0]}</b><br>Plays: %{customdata[1]:,}<br>Share: %{customdata[5]:.1%}<br>Minutes: %{customdata[4]:.1f}<br>Completion: %{customdata[6]:.1%}<br>Skip Rate: %{customdata[7]:.1%}<extra></extra>",
            showlegend=False,
        )
    )

    chart.update_layout(
        title="Genre Planets",
        xaxis={"visible": False},
        yaxis={"visible": False, "scaleanchor": "x", "scaleratio": 1},
    )

    return base_chart(chart, 500)


def artist_chart(data: pd.DataFrame) -> go.Figure:
    artists = data.head(18).copy().reset_index(drop=True)

    if artists.empty:
        return base_chart(go.Figure(), 420)

    artists["rank"] = np.arange(1, len(artists) + 1)
    artists["x"] = artists["rank"]
    artists["y"] = np.sin(artists["rank"] / 1.8) * 0.50
    artists["size"] = 20 + 64 * artists["plays"] / max(artists["plays"].max(), 1)
    artists["label"] = np.where(artists.index < 10, artists["artist"].map(lambda value: short_text(value, 16)), "")

    chart = go.Figure()

    chart.add_trace(
        go.Scatter(
            x=artists["x"],
            y=artists["y"],
            mode="lines",
            line={"color": "rgba(16,16,16,0.20)", "width": 1.1, "dash": "dot"},
            hoverinfo="skip",
            showlegend=False,
        )
    )

    chart.add_trace(
        go.Scatter(
            x=artists["x"],
            y=artists["y"],
            mode="markers+text",
            marker={
                "size": artists["size"],
                "color": color["sky"],
                "opacity": 0.72,
                "line": {"color": "rgba(16,16,16,0.46)", "width": 1},
            },
            text=artists["label"],
            textposition="top center",
            textfont={"size": 10, "color": color["text"], "family": "Nunito"},
            customdata=artists[["artist", "plays", "tracks", "albums", "genres", "minutes", "friction_rate"]],
            hovertemplate="<b>%{customdata[0]}</b><br>Rank: %{x}<br>Plays: %{customdata[1]:,}<br>Tracks: %{customdata[2]:,}<br>Minutes: %{customdata[5]:.1f}<br>Skip Rate: %{customdata[6]:.1%}<extra></extra>",
            showlegend=False,
        )
    )

    chart.update_layout(title="Artist Pull")
    chart.update_xaxes(title_text="Rank", showgrid=False)
    chart.update_yaxes(visible=False)

    return base_chart(chart, 420)


def route_chart(data: pd.DataFrame, value_col: str, title: str) -> go.Figure:
    route = data.copy().loc[:, ~data.columns.duplicated()].copy()

    if value_col not in route.columns:
        raise ValueError(f"Missing route value column: {value_col}")

    route = route.sort_values(value_col, ascending=True).reset_index(drop=True)

    if route.empty:
        return base_chart(go.Figure(), 420)

    chart = go.Figure()
    max_value = max(route[value_col].max(), 1)

    for place, row in route.iterrows():
        source_type = str(row.get("source_role", "Unknown"))
        shade = role_color.get(source_type, color["gray"])
        width = 7 + 28 * row[value_col] / max_value

        chart.add_trace(
            go.Scatter(
                x=[0, row[value_col]],
                y=[place, place],
                mode="lines+markers",
                line={"color": shade, "width": width},
                marker={
                    "size": [7, 16],
                    "color": shade,
                    "line": {"color": color["line"], "width": 1},
                },
                text=[row["source_label"], row["source_label"]],
                customdata=[[row.get("plays", 0), row.get("minutes", 0), row.get("source_role", ""), row.get(value_col, 0)]] * 2,
                hovertemplate="<b>%{text}</b><br>Route Strength: %{customdata[3]:,}<br>Plays: %{customdata[0]:,}<br>Minutes: %{customdata[1]:.1f}<br>Source Type: %{customdata[2]}<extra></extra>",
                showlegend=False,
            )
        )

    chart.update_layout(title=title)
    chart.update_xaxes(title_text=name_map.get(value_col, value_col.replace("_", " ").title()))
    chart.update_yaxes(
        title_text="Source",
        tickmode="array",
        tickvals=list(range(len(route))),
        ticktext=route["source_label"].map(lambda value: short_text(value, 24)),
        showgrid=False,
    )

    return base_chart(chart, 445)


def discovery_chart(data: pd.DataFrame) -> go.Figure:
    daily = data.copy()

    if daily.empty:
        return base_chart(go.Figure(), 400)

    daily["size"] = 14 + 48 * daily["discoveries"] / max(daily["discoveries"].max(), 1)
    palette = [color["cyan"], color["mint"], color["purple"], color["coral"]]
    daily["shade"] = [palette[index % len(palette)] for index in range(len(daily))]

    chart = go.Figure()

    chart.add_trace(
        go.Scatter(
            x=daily["date"],
            y=daily["discoveries"],
            mode="markers",
            marker={
                "size": daily["size"],
                "color": daily["shade"],
                "opacity": 0.72,
                "line": {"color": "rgba(16,16,16,0.40)", "width": 1},
            },
            customdata=daily[["top_source", "top_genre"]],
            hovertemplate="Discovery Trail<br>%{x|%b %-d, %Y}<br>New Tracks: %{y}<br>Top Source: %{customdata[0]}<br>Top Genre: %{customdata[1]}<extra></extra>",
            showlegend=False,
        )
    )

    for _, row in daily.sort_values("discoveries", ascending=False).head(4).iterrows():
        chart.add_annotation(
            x=row["date"],
            y=row["discoveries"],
            text=f"{int(row['discoveries'])}",
            showarrow=True,
            arrowcolor="rgba(16,16,16,0.34)",
            font={"size": 11, "color": color["text"], "family": "Nunito"},
        )

    chart.update_layout(title="Discovery Trail")
    chart.update_xaxes(title_text="Date", tickformat="%b %Y")
    chart.update_yaxes(title_text="New Tracks")

    return base_chart(chart, 405)


def source_constellation(data: pd.DataFrame) -> go.Figure:
    source = data.copy()

    if source.empty:
        return base_chart(go.Figure(), 430)

    source["size"] = 22 + 76 * source["plays"] / max(source["plays"].max(), 1)
    source["shade"] = source["source_role"].map(lambda value: role_color.get(str(value), color["gray"]))
    source["label"] = np.where(
        source["source_label"].isin(["Library Playlist", "Album Page", "Search to Album", "Search", "Radio or Station"]),
        source["source_label"],
        "",
    )

    chart = go.Figure()

    chart.add_trace(
        go.Scatter(
            x=source["discovery_share"],
            y=source["friction_rate"],
            mode="markers+text",
            marker={
                "size": source["size"],
                "color": source["shade"],
                "opacity": 0.70,
                "line": {"color": "rgba(16,16,16,0.44)", "width": 1.3},
            },
            text=source["label"],
            textposition="top center",
            textfont={"size": 10, "color": color["text"], "family": "Nunito"},
            customdata=source[["source_label", "source_role", "plays", "minutes", "full_rate", "repeat_share"]],
            hovertemplate="<b>%{customdata[0]}</b><br>Source Type: %{customdata[1]}<br>Plays: %{customdata[2]:,}<br>Minutes: %{customdata[3]:.1f}<br>Completion: %{customdata[4]:.1%}<br>Repeats: %{customdata[5]:.1%}<extra></extra>",
            showlegend=False,
        )
    )

    chart.update_layout(title="Discovery vs. Skipping")
    chart.update_xaxes(title_text="Discovery")
    chart.update_yaxes(title_text="Skip Rate")

    return base_chart(chart, 430)


def warning_board(tracks: pd.DataFrame, limit: int) -> go.Figure:
    data = tracks.copy().head(limit).sort_values("friction_rate").reset_index(drop=True)

    if data.empty:
        return base_chart(go.Figure(), 440)

    chart = go.Figure()

    for place, row in data.iterrows():
        shade = color["red"] if row["friction_rate"] >= 0.90 else color["coral"]

        chart.add_trace(
            go.Scatter(
                x=[0, row["friction_rate"]],
                y=[place, place],
                mode="lines+markers",
                line={"color": "rgba(16,16,16,0.18)", "width": 3},
                marker={
                    "size": [5, 18],
                    "color": ["rgba(16,16,16,0.18)", shade],
                    "line": {"color": color["line"], "width": 1},
                },
                text=[row["display"], row["display"]],
                customdata=[[row["track"], row["artist"], row["album"], row["plays"], row["minutes"], row["average_share"], row["full_rate"]]] * 2,
                hovertemplate="<b>%{text}</b><br>Artist: %{customdata[1]}<br>Plays: %{customdata[3]}<br>Minutes: %{customdata[4]:.1f}<br>Completion: %{customdata[5]:.1%}<br>Full Listens: %{customdata[6]:.1%}<extra></extra>",
                showlegend=False,
            )
        )

    chart.update_layout(title="Skip Signals")
    chart.update_xaxes(title_text="Skip Rate", range=[0, 1.05])
    chart.update_yaxes(
        title_text="Track",
        tickmode="array",
        tickvals=list(range(len(data))),
        ticktext=data["display"].map(lambda value: short_text(value, 36)),
        showgrid=False,
    )

    return base_chart(chart, 500)


def source_skip_chart(data: pd.DataFrame) -> go.Figure:
    source = data.copy().sort_values("friction_rate", ascending=False).head(12).reset_index(drop=True)

    if source.empty:
        return base_chart(go.Figure(), 430)

    source["x"] = [place % 4 for place in range(len(source))]
    source["y"] = [-(place // 4) for place in range(len(source))]
    source["size"] = 50 + 82 * source["plays"] / max(source["plays"].max(), 1)
    source["shade"] = np.where(source["friction_rate"].ge(0.75), color["coral"], color["sky"])

    chart = go.Figure()

    chart.add_trace(
        go.Scatter(
            x=source["x"],
            y=source["y"],
            mode="markers+text",
            marker={
                "size": source["size"],
                "color": source["shade"],
                "opacity": 0.68,
                "line": {"color": color["red"], "width": 1 + 7 * source["friction_rate"].fillna(0)},
            },
            text=source["source_label"].map(lambda value: short_text(value, 17)),
            textposition="middle center",
            textfont={"size": 10, "color": color["text"], "family": "Nunito"},
            customdata=source[["plays", "friction_rate", "full_rate"]],
            hovertemplate="<b>%{text}</b><br>Plays: %{customdata[0]:,}<br>Skip Rate: %{customdata[1]:.1%}<br>Completion: %{customdata[2]:.1%}<extra></extra>",
            showlegend=False,
        )
    )

    chart.update_layout(title="Source Breakdown", xaxis={"visible": False}, yaxis={"visible": False})

    return base_chart(chart, 430)


def terrain_chart(data: pd.DataFrame) -> go.Figure:
    values = data["play_share"].dropna().clip(0, 1.5)

    if values.empty:
        return base_chart(go.Figure(), 380)

    counts, bins = np.histogram(values, bins=34, range=(0, 1.5))
    mids = (bins[:-1] + bins[1:]) / 2

    chart = go.Figure()

    chart.add_trace(
        go.Scatter(
            x=mids,
            y=counts,
            mode="markers",
            marker={
                "size": 10 + 38 * counts / max(counts.max(), 1),
                "color": np.where(mids < 0.25, color["coral"], np.where(mids > 0.8, color["mint"], color["sky"])),
                "opacity": 0.68,
                "line": {"color": "rgba(16,16,16,0.36)", "width": 1},
            },
            hovertemplate="Completion Terrain<br>Completion: %{x:.2f}<br>Count: %{y}<extra></extra>",
            showlegend=False,
        )
    )

    chart.add_trace(
        go.Scatter(
            x=mids,
            y=counts,
            mode="lines",
            line={"color": "rgba(16,16,16,0.20)", "width": 1, "dash": "dot"},
            hoverinfo="skip",
            showlegend=False,
        )
    )

    chart.update_layout(title="Completion Terrain")
    chart.update_xaxes(title_text="Completion")
    chart.update_yaxes(title_text="Count")

    return base_chart(chart, 385)


def arena_chart(features: pd.DataFrame) -> go.Figure:
    data = features.copy()

    if data.empty:
        return base_chart(go.Figure(), 480)

    data["size"] = 13 + 58 * data["minutes"] / max(data["minutes"].max(), 1)
    xcut = data["plays"].quantile(0.75)
    ycut = data["affinity_score"].quantile(0.75)

    chart = go.Figure()

    for name, group in data.groupby("candidate_class"):
        clean_name = role_name.get(str(name), str(name))

        chart.add_trace(
            go.Scatter(
                x=group["plays"],
                y=group["affinity_score"],
                mode="markers",
                marker={
                    "size": group["size"],
                    "color": class_color.get(str(name), color["gray"]),
                    "opacity": 0.66,
                    "line": {
                        "color": "rgba(16,16,16,0.46)",
                        "width": np.where(group["friction_rate"].ge(0.75), 3, 1),
                    },
                },
                name=clean_name,
                customdata=group[["display", "artist", "album", "genre", "active_days", "friction_rate", "playlist_count", "ready_reason", "candidate_class"]],
                hovertemplate="<b>%{customdata[0]}</b><br>Artist: %{customdata[1]}<br>Genre: %{customdata[3]}<br>Plays: %{x}<br>Affinity: %{y:.3f}<br>Skip Rate: %{customdata[5]:.1%}<br>Role: %{customdata[8]}<br>%{customdata[7]}<extra></extra>",
            )
        )

    chart.add_vline(x=xcut, line_dash="dash", line_color="rgba(16,16,16,0.36)")
    chart.add_hline(y=ycut, line_dash="dash", line_color="rgba(16,16,16,0.36)")
    chart.add_annotation(x=xcut * 1.08, y=min(1, ycut * 1.08), text="Keep Close", showarrow=False)
    chart.add_annotation(x=max(1, xcut * 0.35), y=min(1, ycut * 1.08), text="Rediscover", showarrow=False)
    chart.add_annotation(x=xcut * 1.08, y=max(0, ycut * 0.55), text="Risky", showarrow=False)
    chart.add_annotation(x=max(1, xcut * 0.35), y=max(0, ycut * 0.55), text="Leave Alone", showarrow=False)

    chart.update_layout(title="Recommendation Map")
    chart.update_xaxes(title_text="Exposure")
    chart.update_yaxes(title_text="Affinity")

    return base_chart(chart, 510)


def node_strip(tracks: pd.DataFrame) -> go.Figure:
    data = tracks.head(18).copy().reset_index(drop=True)

    if data.empty:
        return base_chart(go.Figure(), 390)

    data["rank"] = np.arange(1, len(data) + 1)
    data["x"] = data["rank"]
    data["y"] = np.sin(data["rank"] / 2.0) * 0.28
    data["size"] = 18 + 58 * data["plays"] / max(data["plays"].max(), 1)
    data["label"] = np.where(data.index < 9, data["display"].map(lambda value: short_text(value, 18)), "")

    chart = go.Figure()

    chart.add_trace(
        go.Scatter(
            x=data["x"],
            y=data["y"],
            mode="lines",
            line={"color": "rgba(16,16,16,0.20)", "width": 1.1, "dash": "dot"},
            showlegend=False,
            hoverinfo="skip",
        )
    )

    chart.add_trace(
        go.Scatter(
            x=data["x"],
            y=data["y"],
            mode="markers+text",
            marker={
                "size": data["size"],
                "color": color["mint"],
                "opacity": 0.68,
                "line": {"color": "rgba(16,16,16,0.46)", "width": 1},
            },
            text=data["label"],
            textposition="top center",
            textfont={"size": 10, "color": color["text"], "family": "Nunito"},
            customdata=data[["display", "artist", "album", "genre", "plays", "minutes", "full_rate", "friction_rate"]],
            hovertemplate="<b>%{customdata[0]}</b><br>Artist: %{customdata[1]}<br>Plays: %{customdata[4]}<br>Minutes: %{customdata[5]:.1f}<br>Completion: %{customdata[6]:.1%}<br>Skip Rate: %{customdata[7]:.1%}<extra></extra>",
            showlegend=False,
        )
    )

    chart.update_layout(title="Top Tracks")
    chart.update_xaxes(title_text="Rank", showgrid=False)
    chart.update_yaxes(visible=False)

    return base_chart(chart, 395)


def filter_data(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    plays = tables["plays"].copy()
    features = tables["features"].copy()

    st.sidebar.header("Filters")

    first_date = plays["played_at"].min().date()
    last_date = plays["played_at"].max().date()

    dates = st.sidebar.date_input(
        "Date range",
        value=(first_date, last_date),
        min_value=first_date,
        max_value=last_date,
    )

    if isinstance(dates, tuple) and len(dates) == 2:
        plays = plays[
            (plays["played_at"].dt.date >= dates[0])
            & (plays["played_at"].dt.date <= dates[1])
        ]

    artists = sorted(plays["artist"].dropna().unique().tolist())
    chosen_artists = st.sidebar.multiselect("Artist", artists)

    if chosen_artists:
        plays = plays[plays["artist"].isin(chosen_artists)]

    genres = sorted(plays["genre"].dropna().unique().tolist())
    chosen_genres = st.sidebar.multiselect("Genre", genres)

    if chosen_genres:
        plays = plays[plays["genre"].isin(chosen_genres)]

    sources = sorted(plays["source_label"].dropna().unique().tolist())
    chosen_sources = st.sidebar.multiselect("Source", sources)

    if chosen_sources:
        plays = plays[plays["source_label"].isin(chosen_sources)]

    minimum = st.sidebar.slider("Minimum track plays", 1, 25, 1, 1)
    valid = features[features["plays"].ge(minimum)]["track_key"]
    plays = plays[plays["track_key"].isin(valid)]

    status = st.sidebar.selectbox(
        "Track status",
        [
            "All tracks",
            "High affinity",
            "Core favorites",
            "Rediscovery candidates",
            "Lost discoveries",
            "Recommender ready",
            "High friction",
        ],
    )

    if status == "High affinity":
        valid = features[features["favorite_like"]]["track_key"]
        plays = plays[plays["track_key"].isin(valid)]

    elif status == "Core favorites":
        valid = features[features["candidate_class"].eq("Core Favorite")]["track_key"]
        plays = plays[plays["track_key"].isin(valid)]

    elif status == "Rediscovery candidates":
        valid = features[features["candidate_class"].eq("Rediscovery Candidate")]["track_key"]
        plays = plays[plays["track_key"].isin(valid)]

    elif status == "Lost discoveries":
        valid = features[features["candidate_class"].eq("Lost Discovery")]["track_key"]
        plays = plays[plays["track_key"].isin(valid)]

    elif status == "Recommender ready":
        valid = features[features["recommender_ready"]]["track_key"]
        plays = plays[plays["track_key"].isin(valid)]

    elif status == "High friction":
        valid = features[features["friction_rate"].ge(features["friction_rate"].quantile(0.75))]["track_key"]
        plays = plays[plays["track_key"].isin(valid)]

    behavior = st.sidebar.selectbox(
        "Play behavior",
        [
            "All plays",
            "Full plays only",
            "Friction-heavy plays",
            "Discovery plays",
            "Repeat plays",
        ],
    )

    if behavior == "Full plays only":
        plays = plays[plays["full_play"]]

    elif behavior == "Friction-heavy plays":
        plays = plays[plays["friction"]]

    elif behavior == "Discovery plays":
        plays = plays[plays["first_play"]]

    elif behavior == "Repeat plays":
        plays = plays[plays["repeat_seen"]]

    return plays


def show_about(data: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> None:
    profile = tables["profile"]
    features = tables["features"]

    page_head(
        "About Me",
        "I tend to move on quickly when a song does not click, but I also have a strong repeat history. My listening is shaped heavily by playlists, especially Library Playlist, and a lot of my activity happens at night. This page gives the quick overview: how much I repeat, how often I skip, how many discoveries stay, and how much of my listening is driven by playlists.",
    )

    summary(
        "The quick read is that my listening is playlist-led, repeat-heavy, and selective. I skip quickly when something does not fit the moment, but the artists, playlists, and moods that do fit tend to pull me back repeatedly."
    )

    repeat = score_value(profile, "repeat_intensity")
    retained = score_value(profile, "discovery_retention")
    skipped = score_value(profile, "friction_score")
    playlist = score_value(profile, "playlist_dependence")
    artist = score_value(profile, "artist_concentration")
    full = score_value(profile, "deep_listening")
    night = score_value(profile, "night_share")
    ready = int(features["recommender_ready"].sum())

    first = st.columns(4)
    metrics = [
        ("Repeat History", rate_text(repeat), repeat, color["cyan"], "Repeat plays.", "Share of listening that comes from repeat plays."),
        ("Skip Rate", rate_text(skipped), skipped, color["coral"], "Friction.", "Share of plays that ended with friction or low completion."),
        ("Discovery Retention", rate_text(retained), retained, color["mint"], "Returned later.", "Share of first-time tracks that returned later."),
        ("Tracks to Revisit", f"{ready:,}", min(ready / max(len(features), 1), 1), color["yellow"], "Recommend again.", "Tracks with enough signal to recommend again."),
    ]

    for column, metric in zip(first, metrics):
        with column:
            show_chart(ring_chart(*metric))

    second = st.columns(4)
    metrics = [
        ("Playlist Pull", rate_text(playlist), playlist, color["mint"], "Source habit.", "How much listening depends on playlists."),
        ("Artist Pull", rate_text(artist), artist, color["purple"], "Concentration.", "How concentrated listening is around top artists."),
        ("Full Listens", rate_text(full), full, color["sky"], "Completion.", "Share of plays completed meaningfully."),
        ("Night Listening", rate_text(night), night, color["pink"], "Late activity.", "Share of listening that happens at night."),
    ]

    for column, metric in zip(second, metrics):
        with column:
            show_chart(ring_chart(*metric))

    days = make_days(data)
    left, right = st.columns([1.35, 1])

    with left:
        show_chart(wave_chart(days, "Listening Pulse"))
        caption("This chart shows my listening activity over time. Each dot represents a day. Larger dots mean more minutes listened. Coral dots highlight the biggest listening days, yellow dots show high activity, and cyan dots show normal activity.")

    with right:
        split = pd.Series(
            {
                "new": float(data["first_play"].sum()),
                "repeat": float(data["repeat_seen"].sum()),
            }
        )
        total = split.sum()
        repeat_share = split["repeat"] / total if total else 0
        discovery_share = split["new"] / total if total else 0
        show_chart(split_ring(repeat_share, discovery_share))
        caption("This shows whether my listening universe is built more from repeat history or first-time discoveries.")


def show_listening(data: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> None:
    page_head(
        "Listening",
        "This page shows when I listen, how intense those listening moments are, and whether my routine is built from short sessions, long loops, or stronger listening stretches.",
    )

    days = make_days(data)
    peak = days.sort_values("minutes", ascending=False).head(1)

    if not peak.empty:
        row = peak.iloc[0]
        summary(
            f"Peak day: {day_text(row['date'])}. I listened for {row['minutes']:.1f} minutes, led by {row['top_artist']}, {row['top_genre']}, and {row['top_source']}."
        )

    show_chart(wave_chart(days, "Listening Pulse"))
    caption("This chart shows my listening activity over time. Each dot represents a day. Larger dots mean more minutes listened. Coral dots highlight the biggest listening days, yellow dots show high activity, and cyan dots show normal activity.")

    metric = st.selectbox("Rhythm value", ["plays", "minutes", "full_rate", "friction_rate"])

    show_chart(rhythm_grid(data, metric))
    caption("This chart shows when listening happens by weekday and hour. Larger circles mean more plays in that time slot. Use it to see whether my listening is clustered around mornings, evenings, weekends, or late-night sessions.")

    with st.expander("Open Listening Archive", expanded=False):
        sessions = tables["sessions"].copy()
        columns = [
            "start",
            "minutes",
            "plays",
            "tracks",
            "artists",
            "top_artist",
            "top_source",
            "session_type",
            "full_rate",
            "friction_rate",
        ]
        st.markdown(display_table(sessions[columns], rows=75, pill="Session"), unsafe_allow_html=True)


def show_taste(data: pd.DataFrame) -> None:
    page_head(
        "Taste",
        "This page explores the genres and artists that shape my listening. The goal is to show what takes up the most space, what pulls me back, and where I tend to finish or drop off.",
    )

    artists = make_artists(data)

    genres = (
        data.groupby("genre", dropna=False)
        .agg(
            plays=("track_key", "size"),
            tracks=("track_key", "nunique"),
            artists=("artist", "nunique"),
            minutes=("minutes", "sum"),
            full_plays=("full_play", "sum"),
            friction_plays=("friction", "sum"),
        )
        .reset_index()
    )

    genres["full_rate"] = genres["full_plays"] / genres["plays"]
    genres["friction_rate"] = genres["friction_plays"] / genres["plays"]
    genres = genres.sort_values("plays", ascending=False)

    top_genre = genres.iloc[0]["genre"] if not genres.empty else "Unknown"
    summary(
        f"{top_genre} takes up the most space in my listening, but the smaller genre planets show the other moods and sounds around it. The artist chart shows who pulls me back most often."
    )

    show_chart(planet_chart(genres))
    caption("This is an exploration of the genres I listen to the most. Bigger planets mean more plays or listening share. The largest planet is the genre that takes up the most space in my music universe. Smaller planets show the other genres orbiting around it.")

    show_chart(artist_chart(artists))
    caption("This chart shows which artists pull me back the most. Larger circles represent more plays. The strongest artists are labeled first, while smaller artists can stay visible through hover details.")

    with st.expander("Open Completion Field", expanded=False):
        chart = go.Figure()
        data_plot = genres.copy()
        data_plot["size"] = 16 + 74 * data_plot["plays"] / max(data_plot["plays"].max(), 1)
        data_plot["shade"] = data_plot["genre"].map(lambda value: genre_color.get(str(value), color["gray"]))

        chart.add_trace(
            go.Scatter(
                x=data_plot["plays"],
                y=data_plot["full_rate"],
                mode="markers+text",
                marker={
                    "size": data_plot["size"],
                    "color": data_plot["shade"],
                    "opacity": 0.64,
                    "line": {"color": color["line"], "width": 1 + 7 * data_plot["friction_rate"].fillna(0)},
                },
                text=np.where(data_plot.index < 8, data_plot["genre"].map(lambda value: short_text(value, 16)), ""),
                textposition="top center",
                customdata=data_plot[["genre", "tracks", "artists", "minutes", "friction_rate"]],
                hovertemplate="<b>%{customdata[0]}</b><br>Plays: %{x:,}<br>Completion: %{y:.1%}<br>Skip Rate: %{customdata[4]:.1%}<extra></extra>",
                showlegend=False,
            )
        )

        chart.update_layout(title="Completion Field")
        chart.update_xaxes(title_text="Plays")
        chart.update_yaxes(title_text="Completion", range=[0, 1.05])
        show_chart(base_chart(chart, 430))
        caption("This chart compares how often each genre is played with how often it is completed. Genres farther right have more plays. Genres higher up have stronger completion. Thicker rings or warmer colors show more friction.")


def show_discovery(data: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> None:
    page_head(
        "Discovery",
        "This page shows what I discover, what returns, and what fades out. It separates one-time finds from tracks that actually become part of my listening.",
    )

    features = tables["features"]
    first_seen = data[data["first_play"]].copy()
    retained = features[features["retained"]].copy()
    faded = features[features["candidate_class"].eq("Lost Discovery")].copy()

    summary(
        "I discover new tracks throughout the listening history, but not every first signal becomes part of the repeat history. The counters separate new tracks, returned tracks, and faded tracks."
    )

    columns = st.columns(3)
    metrics = [
        ("New Tracks", f"{len(first_seen):,}", min(len(first_seen) / max(len(features), 1), 1), color["cyan"], "First heard.", "Tracks I heard for the first time."),
        ("Returned Tracks", f"{len(retained):,}", min(len(retained) / max(len(features), 1), 1), color["mint"], "Came back.", "New tracks that came back later."),
        ("Faded Tracks", f"{len(faded):,}", min(len(faded) / max(len(features), 1), 1), color["pink"], "Did not return.", "Tracks that had a first signal but did not return."),
    ]

    for column, metric in zip(columns, metrics):
        with column:
            show_chart(ring_chart(*metric))

    daily = (
        first_seen.groupby("date", dropna=True)
        .agg(
            discoveries=("track_key", "nunique"),
            top_source=("source_label", top_value),
            top_genre=("genre", top_value),
        )
        .reset_index()
    )
    daily["date"] = pd.to_datetime(daily["date"])

    show_chart(discovery_chart(daily))
    caption("This chart shows when new tracks entered my listening history. Each dot is a day with new discoveries. Larger dots mean more first-time tracks on that day.")

    source = (
        first_seen.groupby(["source_label", "source_role"], dropna=False)
        .agg(
            discoveries=("track_key", "nunique"),
            plays=("track_key", "size"),
            minutes=("minutes", "sum"),
            full_rate=("full_play", "mean"),
            friction_rate=("friction", "mean"),
        )
        .reset_index()
    )

    river = source[
        ["source_label", "source_role", "discoveries", "plays", "minutes", "full_rate", "friction_rate"]
    ].copy()
    river["route_value"] = river["discoveries"]
    river = river.loc[:, ~river.columns.duplicated()].copy()

    show_chart(route_chart(river, "route_value", "Discovery Sources"))
    caption("This chart shows where new music enters from. Longer routes mean more discoveries came from that source.")

    with st.expander("Open Discovery Archive", expanded=False):
        columns = [
            "display",
            "artist",
            "album",
            "genre",
            "plays",
            "full_rate",
            "friction_rate",
            "affinity_score",
            "ready_reason",
        ]
        st.markdown(display_table(faded[columns], rows=75), unsafe_allow_html=True)


def show_skips(data: pd.DataFrame) -> None:
    page_head(
        "Skips",
        "This page shows where listening breaks down. A skip signal means I started a track but did not meaningfully complete, repeat, or keep it.",
    )

    summary(
        "The main signal here is friction. A high skip rate does not always mean a song is bad; it means the play often ended early, had low completion, or did not turn into a retained listen."
    )

    columns = st.columns(3)
    metrics = [
        ("Skip Rate", rate_text(data["friction"].mean()), data["friction"].mean(), color["coral"], "Friction.", "Share of plays that ended with friction or low completion."),
        ("Good Plays", rate_text(data["good_play"].mean()), data["good_play"].mean(), color["sky"], "Stayed.", "Share of plays that lasted beyond 30 seconds."),
        ("Full Listens", rate_text(data["full_play"].mean()), data["full_play"].mean(), color["mint"], "Completed.", "Share of plays completed meaningfully."),
    ]

    for column, metric in zip(columns, metrics):
        with column:
            show_chart(ring_chart(*metric))

    threshold = st.slider("Minimum Plays Gate", 2, 20, 4, 1)
    tracks = make_tracks(data)
    tracks = tracks[tracks["plays"].ge(threshold)].sort_values("friction_rate", ascending=False)

    more = st.checkbox("Show More Skip Signals", value=False)
    limit = 15 if more else 10

    show_chart(warning_board(tracks, limit))
    caption("This chart shows the tracks with the strongest skip signals. Coral dots mark tracks that were started but not meaningfully completed or retained. The default view stays limited so the chart remains readable.")

    source = (
        data.groupby("source_label")
        .agg(
            plays=("track_key", "size"),
            friction_rate=("friction", "mean"),
            full_rate=("full_play", "mean"),
            minutes=("minutes", "sum"),
        )
        .reset_index()
        .sort_values("friction_rate", ascending=False)
    )

    show_chart(source_skip_chart(source))
    caption("This chart shows which sources create the most friction. Larger circles mean more activity from that source. Warmer colors mean higher skip behavior.")

    show_chart(terrain_chart(data))
    caption("This chart shows where plays end. It helps separate early drop-offs from full listens.")

    with st.expander("Open Skip Archive", expanded=False):
        columns = ["display", "artist", "album", "genre", "plays", "minutes", "full_rate", "friction_rate"]
        st.markdown(display_table(tracks[columns], rows=75), unsafe_allow_html=True)


def show_sources(data: pd.DataFrame) -> None:
    page_head(
        "Sources",
        "This page shows where my listening starts. It explains whether my music comes mostly from playlists, search, radio, album pages, or other routes.",
    )

    source = (
        data.groupby(["source_label", "source_role"], dropna=False)
        .agg(
            plays=("track_key", "size"),
            tracks=("track_key", "nunique"),
            artists=("artist", "nunique"),
            minutes=("minutes", "sum"),
            first_plays=("first_play", "sum"),
            repeat_plays=("repeat_seen", "sum"),
            full_rate=("full_play", "mean"),
            friction_rate=("friction", "mean"),
        )
        .reset_index()
    )

    source["play_share"] = source["plays"] / source["plays"].sum()
    source["discovery_share"] = source["first_plays"] / source["plays"]
    source["repeat_share"] = source["repeat_plays"] / source["plays"]
    source = source.loc[:, ~source.columns.duplicated()].copy()

    top_source = source.sort_values("plays", ascending=False).iloc[0]["source_label"] if not source.empty else "Unknown"
    summary(
        f"Most of my listening starts from {top_source}. If that route dominates the map, it means the source strongly shapes what I hear, repeat, discover, and skip."
    )

    route = source.copy()
    route["route_value"] = route["plays"]

    show_chart(route_chart(route, "route_value", "Source Routes"))
    caption("This chart shows the main entry points into my listening. Longer routes mean more plays from that source. If Library Playlist is the longest route, it means playlists shape a large part of my listening.")

    show_chart(source_constellation(source))
    caption("This chart compares each source by discovery and skip behavior. Farther right means more discovery. Higher means more skipping. Larger circles mean more plays.")

    with st.expander("Open Source Archive", expanded=False):
        st.markdown(display_table(source, rows=75, pill="Source Type"), unsafe_allow_html=True)


def show_recommendations(tables: dict[str, pd.DataFrame]) -> None:
    page_head(
        "Recommendations",
        "This page looks at which tracks should come back, which ones are strong favorites, and which ones may be too risky to recommend again.",
    )

    features = tables["features"].copy()
    summary(
        "The recommendation map compares exposure and affinity. Tracks with higher affinity and enough exposure are stronger candidates to bring back, while tracks with high skip behavior should be treated carefully."
    )

    chosen = st.multiselect(
        "Recommendation role",
        sorted(features["candidate_class"].dropna().unique().tolist()),
    )

    if chosen:
        features = features[features["candidate_class"].isin(chosen)]

    show_chart(arena_chart(features))
    caption("This chart compares exposure and affinity. Tracks with higher affinity and enough exposure are stronger candidates to bring back. Tracks with high skip behavior should be treated carefully.")

    with st.expander("Open Track Inventory", expanded=False):
        columns = [
            "display",
            "artist",
            "album",
            "genre",
            "plays",
            "minutes",
            "active_days",
            "friction_rate",
            "affinity_score",
            "candidate_class",
            "ready_reason",
            "recommender_ready",
        ]
        st.markdown(display_table(features[columns], rows=100, pill="Role"), unsafe_allow_html=True)


def show_scanner(data: pd.DataFrame) -> None:
    page_head(
        "Scanner",
        "Use this page to inspect one artist, track, genre, or source in detail. The scanner explains where that object appears, how often it shows up, and whether it carries repeat, discovery, or skip signals.",
    )

    scan_type = st.selectbox("Scan type", ["Artist", "Track", "Genre", "Source"])

    if scan_type == "Artist":
        options = sorted(data["artist"].dropna().unique().tolist())
        choice = st.selectbox("Choose artist", options)
        detail = data[data["artist"].eq(choice)]

    elif scan_type == "Track":
        options = sorted(data["display"].dropna().unique().tolist())
        choice = st.selectbox("Choose track", options)
        detail = data[data["display"].eq(choice)]

    elif scan_type == "Genre":
        options = sorted(data["genre"].dropna().unique().tolist())
        choice = st.selectbox("Choose genre", options)
        detail = data[data["genre"].eq(choice)]

    else:
        options = sorted(data["source_label"].dropna().unique().tolist())
        choice = st.selectbox("Choose source", options)
        detail = data[data["source_label"].eq(choice)]

    if detail.empty:
        st.warning("No plays match this scan.")
        return

    friction = detail["friction"].mean()
    full = detail["full_play"].mean()
    active_days = detail["date"].nunique()

    if friction >= 0.60:
        note = f"{choice} appears in the current filter with a strong skip signal. That means the listens may be context-dependent, incomplete, or not fully retained."
    elif full >= 0.60:
        note = f"{choice} appears with a strong completion signal. That means it tends to hold attention when it shows up."
    elif active_days >= 5:
        note = f"{choice} appears across multiple active days, so it is part of a recurring listening pattern."
    else:
        note = f"{choice} is a smaller signal in the current filter, but it can still show where a specific part of the listening history lives."

    st.markdown(
        f"""
        <div class="identity-card">
            <div class="identity-title">{html.escape(choice)}</div>
            <p class="identity-text">{html.escape(note)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(4)
    metrics = [
        ("Plays", f"{len(detail):,}", min(len(detail) / max(len(data), 1), 1), color["cyan"], "Count.", "How often this appears."),
        ("Minutes", f"{detail['minutes'].sum():,.1f}", min(detail["minutes"].sum() / max(data["minutes"].sum(), 1), 1), color["yellow"], "Time.", "How much listening time this holds."),
        ("Active Days", f"{active_days:,}", min(active_days / max(data["date"].nunique(), 1), 1), color["mint"], "Days.", "How many days this appears."),
        ("Skip Rate", rate_text(friction), friction, color["coral"], "Friction.", "How often this breaks down."),
    ]

    for column, metric in zip(columns, metrics):
        with column:
            show_chart(ring_chart(*metric))

    paragraph(
        "This chart shows when the selected object appeared. If there is only one visible play, it shows one clear event instead of an empty timeline."
    )

    days = make_days(detail)

    if len(days) <= 1:
        chart = go.Figure()
        label = detail["played_at"].map(lambda value: date_time(value, short=False))

        chart.add_trace(
            go.Scatter(
                x=detail["played_at"],
                y=[1] * len(detail),
                mode="markers+text",
                marker={
                    "size": 34,
                    "color": color["cyan"],
                    "opacity": 0.74,
                    "line": {"color": color["line"], "width": 1.2},
                },
                text=label,
                textposition="top center",
                textfont={"size": 11, "color": color["text"], "family": "Nunito"},
                hovertemplate="Event Marker<br>%{text}<extra></extra>",
                showlegend=False,
            )
        )

        chart.update_layout(title="Event Marker")
        chart.update_xaxes(title_text="Time", tickformat="%b %-d · %-I %p")
        chart.update_yaxes(visible=False)
        show_chart(base_chart(chart, 340))
    else:
        show_chart(wave_chart(days, "Event Marker"))

    paragraph("This chart shows the top tracks inside the current scan. Larger nodes mean more plays.")

    tracks = make_tracks(detail)
    show_chart(node_strip(tracks))

    with st.expander("Open Scan Details", expanded=False):
        source = (
            detail.groupby("source_label")
            .agg(
                plays=("track_key", "size"),
                minutes=("minutes", "sum"),
                full_rate=("full_play", "mean"),
                friction_rate=("friction", "mean"),
            )
            .reset_index()
            .sort_values("plays", ascending=False)
        )
        st.markdown(display_table(source, rows=60), unsafe_allow_html=True)


def main() -> None:
    page_style()
    hero()

    try:
        tables = load_data()
    except FileNotFoundError as error:
        st.error(str(error))
        st.stop()

    data = filter_data(tables)

    if data.empty:
        st.warning("No plays match the current filters.")
        st.stop()

    map_key()

    about, listening, taste, discovery, skips, sources, recommendations, scanner = st.tabs(
        [
            "About Me",
            "Listening",
            "Taste",
            "Discovery",
            "Skips",
            "Sources",
            "Recommendations",
            "Scanner",
        ]
    )

    with about:
        show_about(data, tables)

    with listening:
        show_listening(data, tables)

    with taste:
        show_taste(data)

    with discovery:
        show_discovery(data, tables)

    with skips:
        show_skips(data)

    with sources:
        show_sources(data)

    with recommendations:
        show_recommendations(tables)

    with scanner:
        show_scanner(data)


if __name__ == "__main__":
    main()