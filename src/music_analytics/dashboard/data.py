import pandas as pd
import streamlit as st
from music_analytics.paths import clean_path


@st.cache_data
def load_data() -> dict:
    columns = {
        "plays": ["minutes", "valid_play", "artist", "track", "track_key"],
        "tracks": ["track", "artist", "valid_plays"],
        "artists": ["artist", "valid_plays"],
        "genres": ["genre", "valid_plays"],
        "days": ["date", "minutes", "plays", "valid_plays", "tracks", "top_artist", "top_genre"],
        "recommend_candidates": ["track_key", "track", "artist", "genre", "valid_plays", "recommend_score", "recommender_ready", "recommend_role"],
        "recommendations": ["seed_track_key", "candidate_track_key", "similarity", "rank"],
        "heatmap": ["weekday", "bucket", "minutes", "valid_plays", "tracks", "top_artists", "avg_minutes", "top_day_share"],
    }
    missing = [name for name in columns if not (clean_path / f"{name}.parquet").exists()]
    if missing:
        raise FileNotFoundError(f"Missing processed tables: {', '.join(missing)}. Run python scripts/make_data.py and python scripts/make_recommendations.py.")
    return {name: pd.read_parquet(clean_path / f"{name}.parquet", columns=cols) for name, cols in columns.items()}
