"""Candidate scoring and precomputed content/behavior neighbors."""
import json
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder, StandardScaler, normalize

from music_analytics.config import BLOCK_WEIGHTS, SHRINKAGE_K
from music_analytics.paths import clean_path, model_path

DEFAULT_SCORE_WEIGHTS = {"affinity": .40, "completion": .20, "activity": .15, "playlist": .15, "exposure": .10}
PAIR_COLUMNS = ["seed_track_key", "candidate_track_key", "similarity", "rank"]


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
    plays = int(row["valid_plays"])
    skip = float(row["smoothed_friction_rate"])
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


def prepare(data: pd.DataFrame, use_snapshot_features: bool = True, score_weights: dict | None = None) -> pd.DataFrame:
    tracks = data.copy()
    tracks["recommend_role"] = tracks["candidate_class"].map(role_name)
    tracks["recommend_text"] = tracks[["track", "artist", "album", "genre"]].fillna("").agg(" ".join, axis=1)
    tracks["exposure_score"] = tracks["plays_log"] / max(tracks["plays_log"].max(), 1)
    tracks["activity_score"] = tracks["days_log"] / max(tracks["days_log"].max(), 1)
    signals = {"affinity": tracks["affinity_score"], "completion": tracks["smoothed_full_rate"],
               "activity": tracks["activity_score"], "exposure": tracks["exposure_score"]}
    if use_snapshot_features:
        signals["playlist"] = tracks["playlist_log"] / max(tracks["playlist_log"].max(), 1)
    weights = DEFAULT_SCORE_WEIGHTS if score_weights is None else score_weights
    total = sum(weights.get(name, 0) for name in signals)
    if total <= 0:
        raise ValueError("Scoring weights must include a positive available signal")
    tracks["quality_score"] = sum(weights.get(name, 0) * signal.clip(0, 1) for name, signal in signals.items()) / total
    tracks["risk_score"] = tracks["smoothed_friction_rate"].clip(0, 1)
    tracks["recommend_score"] = (.70 * tracks["quality_score"] - .25 * tracks["risk_score"]).clip(0, 1)
    tracks["recommend_reason"] = tracks.apply(role_reason, axis=1)
    return tracks


def make_matrix(tracks: pd.DataFrame, use_snapshot_features: bool = True, blocks=None):
    text_model = TfidfVectorizer(min_df=1, max_features=12000, ngram_range=(1, 2),
                               stop_words="english", strip_accents="unicode", lowercase=True)
    text = tracks["recommend_text"]
    try:
        text_matrix = text_model.fit_transform(text)
    except ValueError as exc:
        if "empty vocabulary" not in str(exc):
            raise
        text_matrix = sparse.csr_matrix((len(tracks), 1))
    category_cols = ["artist", "album", "genre"]
    category_model = OneHotEncoder(handle_unknown="ignore", sparse_output=True)
    category_matrix = category_model.fit_transform(tracks[category_cols].fillna(""))
    number_cols = ["plays_log", "minutes_log", "days_log", "smoothed_full_rate", "smoothed_friction_rate"]
    if use_snapshot_features:
        number_cols.insert(3, "playlist_log")
    scale_model = StandardScaler(with_mean=False)
    numeric = scale_model.fit_transform(tracks[number_cols].replace([np.inf, -np.inf], 0).fillna(0))
    matrices = {"text": normalize(text_matrix), "categorical": normalize(category_matrix),
                "behavior": normalize(sparse.csr_matrix(numeric))}
    selected = list(BLOCK_WEIGHTS) if blocks is None else list(blocks)
    matrix = sparse.hstack([matrices[name] * BLOCK_WEIGHTS[name] for name in selected], format="csr")
    return matrix, {"category_cols": category_cols, "number_cols": number_cols, "blocks": matrices}


def make_model(matrix, top: int) -> NearestNeighbors:
    return NearestNeighbors(n_neighbors=min(3 * top + 1, matrix.shape[0]), metric="cosine",
                            algorithm="brute").fit(matrix)


def make_candidates(tracks: pd.DataFrame) -> pd.DataFrame:
    columns = ["track_key", "display", "track", "artist", "album", "genre", "plays", "valid_plays",
               "minutes", "active_days", "full_rate", "friction_rate", "smoothed_full_rate",
               "smoothed_friction_rate", "affinity_score", "candidate_class", "recommend_role",
               "recommend_score", "quality_score", "risk_score", "recommender_ready", "ready_reason", "recommend_reason"]
    return tracks[columns].sort_values(["recommend_score", "affinity_score", "valid_plays", "track_key"],
                                       ascending=[False, False, False, True]).reset_index(drop=True)


def make_pairs(tracks: pd.DataFrame, matrix, model: NearestNeighbors, top: int) -> pd.DataFrame:
    if tracks.empty or top <= 0:
        return pd.DataFrame(columns=PAIR_COLUMNS)
    distances, positions = model.kneighbors(matrix, n_neighbors=min(3 * top + 1, len(tracks)))
    keys = tracks["track_key"].to_numpy()
    eligible = (tracks["recommender_ready"] & tracks["recommend_role"].ne("Leave Alone")
                & tracks["artist"].ne("Unknown Artist")).to_numpy()
    seed_positions = np.arange(len(tracks))[:, None]
    valid = (positions != seed_positions) & eligible[positions] & (keys[positions] != keys[:, None])
    ranks = valid.cumsum(axis=1)
    seed, slot = np.where(valid & (ranks <= top))
    return pd.DataFrame({"seed_track_key": keys[seed], "candidate_track_key": keys[positions[seed, slot]],
                         "similarity": np.maximum(0, 1 - distances[seed, slot]), "rank": ranks[seed, slot]},
                        columns=PAIR_COLUMNS)


def build(top: int = 15, score_weights: dict | None = None) -> dict:
    source = clean_path / "features.parquet"
    if not source.exists():
        raise FileNotFoundError("Missing features.parquet. Run python scripts/make_data.py first.")
    tracks = prepare(pd.read_parquet(source), score_weights=score_weights)
    matrix, parts = make_matrix(tracks)
    pairs = make_pairs(tracks, matrix, make_model(matrix, top), top)
    candidates = make_candidates(tracks)
    profile = make_profile(tracks, pairs)
    for name, table in {"recommend_candidates": candidates, "recommendations": pairs, "recommend_profile": profile}.items():
        table.to_parquet(clean_path / f"{name}.parquet", index=False)
    settings = {"top": top, "tracks": len(tracks), "matrix_rows": matrix.shape[0], "matrix_cols": matrix.shape[1],
                "candidate_rows": len(candidates), "pair_rows": len(pairs), "shrinkage_k": SHRINKAGE_K,
                "block_weights": BLOCK_WEIGHTS, "category_cols": parts["category_cols"],
                "number_cols": parts["number_cols"], "score_weights": score_weights or DEFAULT_SCORE_WEIGHTS,
                "rate_denominator": "plays (all listening events)", "use_snapshot_features": True}
    (model_path / "recommend_settings.json").write_text(json.dumps(settings, indent=2), encoding="utf-8")
    return settings


def load_outputs() -> dict[str, pd.DataFrame]:
    return {"candidates": pd.read_parquet(clean_path / "recommend_candidates.parquet"),
            "recommendations": pd.read_parquet(clean_path / "recommendations.parquet")}


def find_track(name: str, limit: int = 10) -> pd.DataFrame:
    candidates = pd.read_parquet(clean_path / "recommend_candidates.parquet")
    query = str(name).strip().lower()
    if not query:
        return candidates.head(limit)
    match = pd.Series(False, index=candidates.index)
    for col in ["display", "artist", "album", "genre"]:
        match |= candidates[col].str.lower().str.contains(query, regex=False, na=False)
    return candidates.loc[match].head(limit)


def join_pair_details(pairs: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    identity = ["track_key", "display", "track", "artist", "album", "genre"]
    seed = candidates[identity].rename(columns={c: "seed_" + c for c in identity})
    candidate = candidates.rename(columns={c: "candidate_" + c for c in identity})
    return pairs.merge(seed, on="seed_track_key", how="left", validate="m:1").merge(
        candidate, on="candidate_track_key", how="left", validate="m:1")


def recommend_for(track_key: str, limit: int = 10) -> pd.DataFrame:
    outputs = load_outputs()
    pairs = outputs["recommendations"]
    return join_pair_details(pairs.loc[pairs["seed_track_key"].eq(str(track_key))].sort_values("rank").head(limit),
                             outputs["candidates"])


def similar_to_selection(keys, pairs: pd.DataFrame, candidates: pd.DataFrame, limit: int = 7) -> pd.DataFrame:
    selected = set(keys)
    matches = pairs.loc[pairs["seed_track_key"].isin(selected) & ~pairs["candidate_track_key"].isin(selected)]
    matches = matches.sort_values(["similarity", "candidate_track_key"], ascending=[False, True]).drop_duplicates("candidate_track_key")
    result = matches.merge(candidates, left_on="candidate_track_key", right_on="track_key", validate="m:1")
    result = result.loc[result["recommender_ready"] & result["recommend_role"].ne("Leave Alone") & result["artist"].ne("Unknown Artist")]
    return result.head(limit)
