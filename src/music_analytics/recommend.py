import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from music_analytics.paths import clean_path, model_path


def need_col(data: pd.DataFrame, name: str, value):
    if name not in data.columns:
        data[name] = value

    return data

def safe_num(data: pd.DataFrame, name: str) -> pd.Series:
    if name not in data.columns:
        return pd.Series(0.0, index=data.index)

    return pd.to_numeric(data[name], errors="coerce").fillna(0.0)


def safe_text(data: pd.DataFrame, name: str) -> pd.Series:
    if name not in data.columns:
        return pd.Series("", index=data.index)

    return data[name].fillna("").astype(str)

def fill_text(data: pd.DataFrame, name: str, fallback) -> pd.Series:
    text = safe_text(data, name).map(clean_text)

    if isinstance(fallback, pd.Series):
        backup = fallback.fillna("").astype(str).map(clean_text)
        text = text.mask(text.eq(""), backup)
    else:
        text = text.mask(text.eq(""), str(fallback))

    return text

def clean_text(value) -> str:
    text = "" if pd.isna(value) else str(value)
    text = text.replace("\n", " ").replace("\r", " ")
    text = " ".join(text.split())

    return text


def role_name(value: str) -> str:
    mapping = {
        "Core Favorite": "Keep Close",
        "Rediscovery Candidate": "Rediscover",
        "Overexposed or Unstable": "Risky",
        "General Candidate": "Bring Back",
        "Lost Discovery": "Rediscover",
        "Exclude From Recommendations": "Leave Alone",
    }

    return mapping.get(str(value), "Bring Back")


def role_reason(row: pd.Series) -> str:
    role = row["recommend_role"]
    plays = int(row["plays"])
    skip = float(row["friction_rate"])
    affinity = float(row["affinity_score"])
    artist = row["artist"]
    genre = row["genre"]

    if role == "Keep Close":
        return f"This is a strong anchor because it has repeat history, enough exposure, and a strong affinity signal for {artist} or {genre}."

    if role == "Rediscover":
        return "This is worth resurfacing because it has a useful signal but is not dominating the current listening pattern."

    if role == "Risky":
        return f"This needs caution because it has {plays:,} plays but a high skip rate of {skip:.1%}."

    if role == "Leave Alone":
        return "This should be avoided for now because the signal is weak, incomplete, or too noisy for a confident recommendation."

    if affinity >= 0.65:
        return "This is a good bring-back candidate because its affinity score is high enough to suggest it belongs in the listening universe."

    return "This is a general bring-back candidate because it has enough metadata and behavior signal to compare against other tracks."


def make_text(data: pd.DataFrame) -> pd.Series:
    text = (
        safe_text(data, "display")
        + " "
        + safe_text(data, "track")
        + " "
        + safe_text(data, "artist")
        + " "
        + safe_text(data, "album")
        + " "
        + safe_text(data, "genre")
        + " "
        + safe_text(data, "candidate_class")
        + " "
        + safe_text(data, "ready_reason")
    )

    if "text" in data.columns:
        text = text + " " + safe_text(data, "text")

    return text.map(clean_text)


def prepare(data: pd.DataFrame) -> pd.DataFrame:
    tracks = data.copy()

    need_col(tracks, "track_key", tracks.index.astype(str))
    need_col(tracks, "display", safe_text(tracks, "track"))
    need_col(tracks, "track", safe_text(tracks, "display"))
    need_col(tracks, "artist", "Unknown Artist")
    need_col(tracks, "album", "Unknown Album")
    need_col(tracks, "genre", "Unknown Genre")
    need_col(tracks, "candidate_class", "General Candidate")
    need_col(tracks, "ready_reason", "")
    need_col(tracks, "recommender_ready", True)

    numeric = [
        "plays",
        "minutes",
        "active_days",
        "full_rate",
        "friction_rate",
        "average_share",
        "playlist_count",
        "affinity_score",
        "recency_days",
        "fresh_score",
        "keep_score",
        "plays_log",
        "minutes_log",
        "days_log",
        "playlist_log",
    ]

    for name in numeric:
        tracks[name] = safe_num(tracks, name)

    tracks["track_key"] = fill_text(tracks, "track_key", tracks.index.astype(str))
    tracks["display"] = fill_text(tracks, "display", "Unknown Track")
    tracks["track"] = fill_text(tracks, "track", tracks["display"])
    tracks["artist"] = fill_text(tracks, "artist", "Unknown Artist")
    tracks["album"] = fill_text(tracks, "album", "Unknown Album")
    tracks["genre"] = fill_text(tracks, "genre", "Unknown Genre")
    tracks["candidate_class"] = fill_text(tracks, "candidate_class", "General Candidate")
    tracks["ready_reason"] = fill_text(tracks, "ready_reason", "")

    tracks["recommender_ready"] = tracks["recommender_ready"].fillna(False).astype(bool)
    tracks["recommend_role"] = tracks["candidate_class"].map(role_name)
    tracks["recommend_text"] = make_text(tracks)

    exposure = np.log1p(tracks["plays"])
    time = np.log1p(tracks["minutes"])
    activity = np.log1p(tracks["active_days"])
    playlists = np.log1p(tracks["playlist_count"])

    tracks["exposure_score"] = exposure / max(exposure.max(), 1)
    tracks["time_score"] = time / max(time.max(), 1)
    tracks["activity_score"] = activity / max(activity.max(), 1)
    tracks["playlist_score"] = playlists / max(playlists.max(), 1)

    tracks["quality_score"] = (
        0.40 * tracks["affinity_score"].clip(0, 1)
        + 0.20 * tracks["full_rate"].clip(0, 1)
        + 0.15 * tracks["activity_score"].clip(0, 1)
        + 0.15 * tracks["playlist_score"].clip(0, 1)
        + 0.10 * tracks["exposure_score"].clip(0, 1)
    )

    tracks["risk_score"] = tracks["friction_rate"].clip(0, 1)

    tracks["recommend_score"] = (
        0.70 * tracks["quality_score"]
        + 0.20 * tracks["recommender_ready"].astype(float)
        - 0.25 * tracks["risk_score"]
    ).clip(0, 1)

    tracks["recommend_reason"] = tracks.apply(role_reason, axis=1)

    return tracks


def encoder() -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=True)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=True)


def make_matrix(tracks: pd.DataFrame):
    text_model = TfidfVectorizer(
        min_df=1,
        max_features=12000,
        ngram_range=(1, 2),
        stop_words="english",
        strip_accents="unicode",
        lowercase=True,
    )

    category_model = encoder()

    scale_model = StandardScaler(with_mean=False)

    text_matrix = text_model.fit_transform(tracks["recommend_text"])

    category_cols = [
        "artist",
        "album",
        "genre",
        "candidate_class",
        "recommend_role",
    ]

    category_matrix = category_model.fit_transform(tracks[category_cols])

    number_cols = [
        "plays_log",
        "minutes_log",
        "days_log",
        "playlist_log",
        "plays",
        "minutes",
        "active_days",
        "full_rate",
        "friction_rate",
        "average_share",
        "playlist_count",
        "affinity_score",
        "fresh_score",
        "keep_score",
        "exposure_score",
        "time_score",
        "activity_score",
        "playlist_score",
        "quality_score",
        "risk_score",
        "recommend_score",
    ]

    number_data = tracks[number_cols].replace([np.inf, -np.inf], 0).fillna(0)
    number_matrix = scale_model.fit_transform(number_data)

    matrix = sparse.hstack(
        [
            text_matrix * 1.00,
            category_matrix * 0.85,
            number_matrix * 1.25,
        ],
        format="csr",
    )

    parts = {
        "text_model": text_model,
        "category_model": category_model,
        "scale_model": scale_model,
        "category_cols": category_cols,
        "number_cols": number_cols,
    }

    return matrix, parts


def make_model(matrix, top: int) -> NearestNeighbors:
    count = min(top + 1, matrix.shape[0])

    model = NearestNeighbors(
        n_neighbors=count,
        metric="cosine",
        algorithm="brute",
    )

    model.fit(matrix)

    return model


def make_candidates(tracks: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "track_key",
        "display",
        "track",
        "artist",
        "album",
        "genre",
        "plays",
        "minutes",
        "active_days",
        "full_rate",
        "friction_rate",
        "average_share",
        "playlist_count",
        "affinity_score",
        "candidate_class",
        "recommend_role",
        "recommend_score",
        "quality_score",
        "risk_score",
        "recommender_ready",
        "ready_reason",
        "recommend_reason",
    ]

    return tracks[columns].sort_values(
        ["recommend_score", "affinity_score", "plays"],
        ascending=[False, False, False],
    )


def make_pairs(tracks: pd.DataFrame, matrix, model: NearestNeighbors, top: int) -> pd.DataFrame:
    near_dist, near_index = model.kneighbors(matrix, n_neighbors=min(top + 1, len(tracks)))

    rows = []

    for seed_pos in range(len(tracks)):
        seed = tracks.iloc[seed_pos]

        for place in range(near_index.shape[1]):
            candidate_pos = int(near_index[seed_pos, place])
            distance = float(near_dist[seed_pos, place])

            if candidate_pos == seed_pos:
                continue

            candidate = tracks.iloc[candidate_pos]

            if candidate["recommend_role"] == "Leave Alone":
                continue

            if not bool(candidate["recommender_ready"]):
                continue

            similarity = max(0.0, 1.0 - distance)

            rows.append(
                {
                    "seed_track_key": seed["track_key"],
                    "seed_display": seed["display"],
                    "seed_track": seed["track"],
                    "seed_artist": seed["artist"],
                    "seed_album": seed["album"],
                    "seed_genre": seed["genre"],
                    "candidate_track_key": candidate["track_key"],
                    "candidate_display": candidate["display"],
                    "candidate_track": candidate["track"],
                    "candidate_artist": candidate["artist"],
                    "candidate_album": candidate["album"],
                    "candidate_genre": candidate["genre"],
                    "similarity": similarity,
                    "recommend_role": candidate["recommend_role"],
                    "recommend_score": candidate["recommend_score"],
                    "affinity_score": candidate["affinity_score"],
                    "plays": candidate["plays"],
                    "minutes": candidate["minutes"],
                    "active_days": candidate["active_days"],
                    "full_rate": candidate["full_rate"],
                    "friction_rate": candidate["friction_rate"],
                    "candidate_class": candidate["candidate_class"],
                    "recommend_reason": candidate["recommend_reason"],
                }
            )

            if len([row for row in rows if row["seed_track_key"] == seed["track_key"]]) >= top:
                break

    return pd.DataFrame(rows)

def make_profile(tracks: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    total = len(tracks)
    ready = int(tracks["recommender_ready"].sum())
    keep_close = int(tracks["recommend_role"].eq("Keep Close").sum())
    rediscover = int(tracks["recommend_role"].eq("Rediscover").sum())
    risky = int(tracks["recommend_role"].eq("Risky").sum())
    leave = int(tracks["recommend_role"].eq("Leave Alone").sum())
    bring = int(tracks["recommend_role"].eq("Bring Back").sum())

    values = [
        {
            "metric": "tracks",
            "value": total,
            "description": "Tracks available to the recommendation layer.",
        },
        {
            "metric": "ready_tracks",
            "value": ready,
            "description": "Tracks with enough signal to recommend again.",
        },
        {
            "metric": "keep_close",
            "value": keep_close,
            "description": "High-confidence favorites or anchor tracks.",
        },
        {
            "metric": "rediscover",
            "value": rediscover,
            "description": "Tracks worth resurfacing because they have useful signal but are not dominant.",
        },
        {
            "metric": "bring_back",
            "value": bring,
            "description": "General recommendation candidates.",
        },
        {
            "metric": "risky",
            "value": risky,
            "description": "Tracks with meaningful exposure but high skip behavior.",
        },
        {
            "metric": "leave_alone",
            "value": leave,
            "description": "Tracks that should not be prioritized right now.",
        },
        {
            "metric": "recommendation_pairs",
            "value": len(pairs),
            "description": "Saved similar-track recommendation pairs.",
        },
    ]

    return pd.DataFrame(values)


def sample_scores(matrix, tracks: pd.DataFrame, count: int = 12) -> pd.DataFrame:
    limit = min(count, len(tracks))

    if limit == 0:
        return pd.DataFrame()

    scores = cosine_similarity(matrix[:limit], matrix[:limit])

    rows = []

    for row in range(limit):
        for col in range(limit):
            if row == col:
                continue

            rows.append(
                {
                    "track": tracks.iloc[row]["display"],
                    "compare_track": tracks.iloc[col]["display"],
                    "similarity": float(scores[row, col]),
                }
            )

    return pd.DataFrame(rows).sort_values("similarity", ascending=False)

def save_artifacts(tracks: pd.DataFrame, matrix, parts: dict, model: NearestNeighbors, settings: dict) -> None:
    model_path.mkdir(parents=True, exist_ok=True)

    sparse.save_npz(model_path / "recommend_matrix.npz", matrix)

    joblib.dump(
        {
            "model": model,
            "parts": parts,
            "track_keys": tracks["track_key"].tolist(),
            "display": tracks["display"].tolist(),
            "artist": tracks["artist"].tolist(),
            "settings": settings,
        },
        model_path / "recommend_model.joblib",
    )

    with open(model_path / "recommend_settings.json", "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=2)


def build(top: int = 15) -> dict:
    source = clean_path / "features.parquet"

    if not source.exists():
        raise FileNotFoundError("Missing data/processed/features.parquet. Run python3 scripts/make_data.py first.")

    raw = pd.read_parquet(source)
    tracks = prepare(raw)

    matrix, parts = make_matrix(tracks)
    model = make_model(matrix, top)

    candidates = make_candidates(tracks)
    pairs = make_pairs(tracks, matrix, model, top)
    profile = make_profile(tracks, pairs)
    sample = sample_scores(matrix, tracks)

    candidates.to_parquet(clean_path / "recommend_candidates.parquet", index=False, engine="pyarrow")
    pairs.to_parquet(clean_path / "recommendations.parquet", index=False, engine="pyarrow")
    profile.to_parquet(clean_path / "recommend_profile.parquet", index=False, engine="pyarrow")
    sample.to_parquet(clean_path / "recommend_sample.parquet", index=False, engine="pyarrow")

    settings = {
        "top": top,
        "tracks": int(len(tracks)),
        "matrix_rows": int(matrix.shape[0]),
        "matrix_cols": int(matrix.shape[1]),
        "candidate_rows": int(len(candidates)),
        "pair_rows": int(len(pairs)),
    }

    save_artifacts(tracks, matrix, parts, model, settings)

    return settings


def load_outputs() -> dict[str, pd.DataFrame]:
    files = {
        "candidates": clean_path / "recommend_candidates.parquet",
        "recommendations": clean_path / "recommendations.parquet",
        "profile": clean_path / "recommend_profile.parquet",
        "sample": clean_path / "recommend_sample.parquet",
    }

    missing = [str(path) for path in files.values() if not path.exists()]

    if missing:
        raise FileNotFoundError("Recommendation outputs are missing. Run python3 scripts/make_recommendations.py first.")

    return {name: pd.read_parquet(path) for name, path in files.items()}


def find_track(name: str, limit: int = 10) -> pd.DataFrame:
    outputs = load_outputs()
    candidates = outputs["candidates"].copy()

    name = clean_text(name).lower()

    if not name:
        return candidates.head(limit)

    match = candidates[
        candidates["display"].str.lower().str.contains(name, regex=False, na=False)
        | candidates["artist"].str.lower().str.contains(name, regex=False, na=False)
        | candidates["album"].str.lower().str.contains(name, regex=False, na=False)
        | candidates["genre"].str.lower().str.contains(name, regex=False, na=False)
    ]

    return match.head(limit)


def recommend_for(track_key: str, limit: int = 10) -> pd.DataFrame:
    outputs = load_outputs()
    pairs = outputs["recommendations"].copy()

    result = pairs[pairs["seed_track_key"].eq(str(track_key))]
    result = result.sort_values(["similarity", "recommend_score"], ascending=[False, False])

    return result.head(limit)