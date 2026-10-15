"""Rolling replay evaluation using only pre-cutoff behavior."""
from itertools import product
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import normalize
from music_analytics.build import make_features
from music_analytics.config import TIMEZONE
from music_analytics.paths import report_path
from music_analytics.recommend import prepare, make_matrix, DEFAULT_SCORE_WEIGHTS

CUTOFFS = [("2025-12-20", "tuning"), ("2025-12-27", "tuning"),
           ("2026-01-31", "held_out"), ("2026-02-07", "held_out")]
WINDOW_DAYS = 28
RANDOM_SEED = 42
KS = (10, 25, 50)


def metrics(ranking: pd.DataFrame, targets: set, k: int) -> dict:
    top = ranking.head(k)
    hits = top["track_key"].isin(targets).to_numpy(dtype=float)
    discounts = 1 / np.log2(np.arange(len(hits)) + 2)
    ideal = (1 / np.log2(np.arange(min(k, len(targets))) + 2)).sum()
    return {"recall": float(hits.sum() / len(targets)) if targets else np.nan,
            "hit_rate": float(hits.any()) if targets else np.nan,
            "ndcg": float((hits * discounts).sum() / ideal) if ideal else np.nan,
            "distinct_artists": int(top["artist"].nunique()), "returned": len(top)}


def rank_by(data: pd.DataFrame, score: str, eligible_only: bool = False) -> pd.DataFrame:
    if eligible_only:
        data = data.loc[data["recommender_ready"] & data["recommend_role"].ne("Leave Alone") & data["artist"].ne("Unknown Artist")]
    return data.sort_values([score, "track_key"], ascending=[False, True])


def window(plays: pd.DataFrame, cutoff):
    cutoff = pd.Timestamp(cutoff, tz=TIMEZONE)
    end = cutoff + pd.DateOffset(days=WINDOW_DAYS)
    if end > plays["played_at"].max():
        raise ValueError(f"Incomplete test window ending {end}")
    features = make_features(plays, cutoff, use_snapshot_features=False)
    features = features.loc[features["valid_plays"].ge(1)].reset_index(drop=True)
    future = plays.loc[plays["played_at"].ge(cutoff) & plays["played_at"].lt(end) & plays["valid_play"]]
    future_keys = set(future["track_key"])
    eligible_targets = future_keys & set(features["track_key"])
    targets = future_keys
    if features.empty or not targets:
        raise ValueError(f"No eligible replay target at {cutoff}")
    return features, targets, {"cutoff": cutoff.isoformat(), "window_end": end.isoformat(), "eligible_tracks": len(features),
                               "target_tracks": len(targets), "eligible_target_tracks": len(eligible_targets), "unseen_future_tracks": len(future_keys - eligible_targets)}


def neighbor_scores(prepared: pd.DataFrame) -> dict:
    """Historical-centroid proxy; remove each candidate's own similarity contribution."""
    combined, parts = make_matrix(prepared, use_snapshot_features=False)
    exposure = prepared["valid_plays"].to_numpy(dtype=float)
    scores = {}
    for name, block in {**parts["blocks"], "combined": combined}.items():
        unit = normalize(block)
        centroid = unit.T @ exposure
        numerator = np.asarray(unit @ centroid).ravel() - exposure * np.asarray(unit.multiply(unit).sum(axis=1)).ravel()
        denominator = exposure.sum() - exposure
        scores[name] = np.divide(numerator, denominator, out=np.zeros(len(exposure)), where=denominator > 0)
    return scores


def evaluate(plays: pd.DataFrame) -> dict:
    windows = [(split, *window(plays, cutoff)) for cutoff, split in CUTOFFS]
    # The complete grid and objective are fixed before inspecting held-out windows.
    grid = [{"affinity": a / 4, "completion": b / 4, "exposure": c / 4}
            for a, b, c in product(range(5), repeat=3) if a + b + c == 4]
    tuning = []
    for weights in grid:
        values = []
        for split, features, targets, meta in windows:
            if split != "tuning":
                continue
            prepared = prepare(features, use_snapshot_features=False, score_weights=weights)
            values.append(metrics(rank_by(prepared, "recommend_score", True), targets, 25)["ndcg"])
        tuning.append({**weights, "mean_ndcg25": float(np.mean(values))})
    best = max(range(len(grid)), key=lambda i: tuning[i]["mean_ndcg25"])
    chosen = grid[best]
    rows = []
    window_rows = []
    for split, features, targets, meta in windows:
        prepared = prepare(features, use_snapshot_features=False, score_weights=chosen)
        rng = np.random.default_rng(RANDOM_SEED)
        prepared["random_score"] = rng.random(len(prepared))
        production = prepare(features, use_snapshot_features=False)
        rankings = {"random": rank_by(prepared, "random_score"),
                    "most_valid_plays": rank_by(prepared, "valid_plays"),
                    "most_recent": rank_by(prepared, "last_play"),
                    "affinity": rank_by(prepared, "affinity_score"),
                    "smoothed_completion": rank_by(prepared, "smoothed_full_rate"),
                    "recommend_score": rank_by(production, "recommend_score", True),
                    "tuned_recommend_score": rank_by(prepared, "recommend_score", True)}
        for name, values in neighbor_scores(prepared).items():
            prepared["neighbor_score"] = values
            rankings["neighbors_" + name] = rank_by(prepared, "neighbor_score")
        for method, ranking in rankings.items():
            for k in KS:
                rows.append({"split": split, "cutoff": meta["cutoff"], "method": method, "k": k,
                             **metrics(ranking, targets, k)})
        window_rows.append({"split": split, **meta})
    results = pd.DataFrame(rows)
    results.to_csv(report_path / "evaluation.csv", index=False)
    summary = results.groupby(["split", "method", "k"])[["recall", "hit_rate", "ndcg", "distinct_artists", "returned"]].agg(["mean", "std"])
    summary.columns = ["_".join(c) for c in summary.columns]
    summary = summary.reset_index()
    summary.to_csv(report_path / "evaluation_summary.csv", index=False)
    pd.DataFrame(tuning).to_csv(report_path / "evaluation_tuning.csv", index=False)
    pd.DataFrame(window_rows).to_csv(report_path / "evaluation_windows.csv", index=False)
    settings = {"cutoffs": CUTOFFS, "window_days": WINDOW_DAYS, "seed": RANDOM_SEED,
                "score_weights": chosen, "tuning_objective": "mean NDCG@25 on tuning cutoffs",
                "use_snapshot_features": False, "default_score_weights": DEFAULT_SCORE_WEIGHTS}
    (report_path / "evaluation_settings.json").write_text(json.dumps(settings, indent=2), encoding="utf-8")
    held = summary.loc[summary["split"].eq("held_out")]
    lines = ["# Replay evaluation", "", "## Protocol", "",
             "Cutoffs are midnight America/New_York. Training is strictly before each cutoff; targets fall in [cutoff, cutoff + 28 calendar days). Only tracks with a prior valid play are eligible. Targets are all tracks with a valid play in the test window, as specified. Unseen future tracks cannot be returned from the eligible set, but remain in recall and NDCG denominators; eligible targets and unseen targets are reported separately. This imposes an explicit achievable-recall ceiling.", "",
             "Library snapshot play/skip counts, added_at, and playlist_count/playlist_log are excluded from evaluation features. Numeric neighbor blocks therefore have five columns in evaluation, six in production. Metadata still comes from the export: historical metadata revisions cannot be reconstructed.", "",
             "The first two windows tune the affinity/completion/exposure blend on the approved 0.25 grid; the last two are held out. The selected weights are " + json.dumps(chosen) + ". Risk and the outer 0.70 quality / 0.25 friction coefficients are unchanged. Both final-score methods apply readiness and Leave Alone/Unknown Artist exclusions; simple baselines rank the full eligible set. Short recommendation lists are penalized, not padded.", "",
             "The production default weights remain separately recorded in recommend_settings.json. recommend_score tests those production weights in evaluation mode; tuned_recommend_score separately tests the blend selected on earlier windows. The tuning result does not silently replace production weights or claim an export-snapshot model was backtested.", "",
             "Recall@k = hits / all test-window valid-play targets; HitRate@k = whether any hit appears; NDCG@k uses binary relevance and logarithmic rank discounts. Artist counts include Unknown Artist as a single label where baselines return it. Standard deviations are sample standard deviations across windows. Random uses seed 42, one draw per window; its variability is across windows, not many random seeds.", "", "## Windows", "", "```", pd.DataFrame(window_rows).to_string(index=False), "```", "", "## Held-out results", "",
             "| Method | k | Recall mean Ã‚Â± SD | HitRate mean Ã‚Â± SD | NDCG mean Ã‚Â± SD | Artists mean Ã‚Â± SD |", "|---|---:|---:|---:|---:|---:|"]
    for row in held.itertuples(index=False):
        lines.append(f"| {row.method} | {row.k} | {row.recall_mean:.3f} Ã‚Â± {row.recall_std:.3f} | {row.hit_rate_mean:.3f} Ã‚Â± {row.hit_rate_std:.3f} | {row.ndcg_mean:.3f} Ã‚Â± {row.ndcg_std:.3f} | {row.distinct_artists_mean:.1f} Ã‚Â± {row.distinct_artists_std:.1f} |")
    comparison = held.loc[held["k"].eq(25)].set_index("method")
    lines += ["", "## Interpretation", "",
              f"At k=25, the production-score NDCG is {comparison.loc['recommend_score', 'ndcg_mean']:.3f}, "
              f"the tuned blend is {comparison.loc['tuned_recommend_score', 'ndcg_mean']:.3f}, "
              f"most-valid-plays is {comparison.loc['most_valid_plays', 'ndcg_mean']:.3f}, and "
              f"affinity is {comparison.loc['affinity', 'ndcg_mean']:.3f}. Compare these descriptive values with their across-window variability; tuning is not evidence of an improvement."]
    lines += ["", "## Neighbor ablation", "",
              "Text-only, categorical-only, behavior-only, and combined blocks are evaluated against the same replay targets. Each candidate is scored by cosine similarity to the full pre-cutoff history weighted by valid-play counts, excluding its own contribution. This is a historical-profile proxy, not a test of the dashboard's user-selected seeds. No future plays select seeds or weight the profile.", "", "## Limitations", "",
              "One listener, a short export window, only two held-out windows, and overlapping 28-day windows make these estimates unstable and correlated. They are descriptive, not statistical evidence of general superiority. HitRate can saturate for a single user. Replay is not satisfaction; absence of replay is not dislike. Snapshot metadata and identity resolution remain limitations even though snapshot behavioral features are excluded. Training-window metrics are available in the CSV for audit, not presented as held-out evidence.", ""]
    (report_path / "evaluation.md").write_text("\n".join(lines), encoding="utf-8")
    return settings
