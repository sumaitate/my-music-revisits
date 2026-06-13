import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import plotly.graph_objects as go

from music_analytics.paths import clean_path, plot_path, report_path

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
    "profile.parquet",
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
profile = pd.read_parquet(clean_path / "profile.parquet")

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
        x=genres["plays"],
        y=genres["full_rate"],
        mode="markers+text",
        text=genres["genre"],
        marker={
            "size": 12 + 70 * genres["plays"] / max(genres["plays"].max(), 1),
            "color": "#71CFF2",
            "opacity": 0.65,
            "line": {"color": "#101010", "width": 1},
        },
    )
)
chart.update_layout(title="Genre Completion Field", paper_bgcolor="#EEF9FF", plot_bgcolor="#EEF9FF")
chart.write_html(plot_path / "genres.html")

profile_type = profile.loc[profile["metric"].eq("profile_type"), "value"].iloc[0]
ready = int(features["recommender_ready"].sum())

text = f"""# Sumi's Music Universe EDA

## Overview

The cleaned data contains {len(plays):,} plays across {len(tracks):,} tracks, {len(artists):,} artists, and {len(genres):,} genres. The observed listening time is {plays["minutes"].sum():,.1f} minutes.

## Listener Profile

The computed listener profile is **{profile_type}**.

## Recommender Readiness

The feature table has {ready:,} tracks ready for release-two recommendation experiments.
"""

(report_path / "eda.md").write_text(text, encoding="utf-8")

print("EDA saved.")
print("Open reports/eda.md and reports/figures.")