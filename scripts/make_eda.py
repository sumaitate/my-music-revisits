from music_analytics.config import LISTENER_NAME
from music_analytics.paths import make_paths
import pandas as pd
import plotly.graph_objects as go

from music_analytics.paths import clean_path, plot_path, report_path

make_paths()

needed = [
    "plays.parquet",
    "tracks.parquet",
    "artists.parquet",
    "genres.parquet",
    "days.parquet",
    "hours.parquet",
    "sources.parquet",
    "sessions.parquet",
    "features.parquet",
]

missing = [name for name in needed if not (clean_path / name).exists()]

if missing:
    raise FileNotFoundError("Processed data is missing. Run python3 scripts/make_data.py first.")

plays = pd.read_parquet(clean_path / "plays.parquet")
tracks = pd.read_parquet(clean_path / "tracks.parquet")
artists = pd.read_parquet(clean_path / "artists.parquet")
genres = pd.read_parquet(clean_path / "genres.parquet")
days = pd.read_parquet(clean_path / "days.parquet")
features = pd.read_parquet(clean_path / "features.parquet")

chart = go.Figure()
chart.add_trace(
    go.Scatter(
        x=days["date"],
        y=days["minutes"],
        mode="markers+lines",
        marker={"size": 9, "color": "#71CFF2", "line": {"color": "#101010", "width": 1}},
        line={"color": "rgba(16,16,16,0.35)", "dash": "dot"},
    )
)
chart.update_layout(title="Listening Pulse", paper_bgcolor="#EEF9FF", plot_bgcolor="#EEF9FF")
chart.write_html(plot_path / "daily_minutes.html")

chart = go.Figure()
chart.add_trace(
    go.Scatter(
        x=genres["valid_plays"],
        y=genres["full_rate"],
        mode="markers+text",
        text=genres["genre"],
        marker={
            "size": 12 + 70 * genres["valid_plays"] / max(genres["valid_plays"].max(), 1),
            "color": "#71CFF2",
            "opacity": 0.65,
            "line": {"color": "#101010", "width": 1},
        },
    )
)
chart.update_layout(title="Genre Completion Field", paper_bgcolor="#EEF9FF", plot_bgcolor="#EEF9FF")
chart.write_html(plot_path / "genres.html")

ready = int(features["recommender_ready"].sum())

text = f"""# {LISTENER_NAME}'s Music Revisits EDA

## Overview

The cleaned data contains {len(plays):,} listening events ({int(plays["valid_play"].sum()):,} plays of at least 30 seconds) across {len(tracks):,} tracks, {len(artists):,} artists, and {len(genres):,} genres. The observed listening time is {plays["minutes"].sum():,.1f} minutes.

## Recommender Readiness

The feature table has {ready:,} tracks ready for recommendation scoring.
"""

(report_path / "eda.md").write_text(text, encoding="utf-8")

print("EDA saved.")
print("Open reports/eda.md and reports/figures.")