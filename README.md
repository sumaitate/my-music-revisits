<<<<<<< HEAD
# **My Music Revisits:** Finding Tracks Worth Returning To
Under construction

```text
my-music-revisits/
├── app/
│   └── dashboard.py
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── reports/
│   ├── eda.md
│   └── figures/
├── scripts/
│   ├── audit_data.py
│   ├── make_data.py
│   └── make_eda.py
├── src/
│   └── music_analytics/
│       ├── build.py
│       ├── paths.py
│       └── read.py
├── requirements.txt
└── README.md
```
=======
# My Music Revisits

Personal Apple Music listening-history analysis, a Streamlit dashboard, and a content-based track recommender. The observed export covers October 2025 through March 2026. Replay is a behavioral signal, not proof of satisfaction.

## Install and run

Use Python 3.11 or newer. From the repository root on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python scripts/audit_data.py
python scripts/make_data.py
python scripts/make_eda.py
python scripts/make_recommendations.py
python scripts/check_rankings.py
python scripts/evaluate_recommender.py
python -m pytest -q
python -m streamlit run app/dashboard.py
```

The retained command-line neighbor lookup is `python scripts/show_recommendations.py "track or artist"`.

The editable installation exposes `music_analytics` from `src/`; scripts do not modify Python's import path. The requirements file records minimum versions. Directory creation is explicit in script entry points, never a side effect of importing paths.

## Input and output

Place the Apple export CSV files under `data/raw/csv` and JSON archives under `data/raw/json_zips`. The pipeline finds input files recursively by name. Required build inputs are `music_play_activity.csv`, `play_history_daily_tracks.csv`, `library_tracks.json.zip`, and `library_playlists.json.zip`.

`build.py` defines the processed schemas. `plays.parquet` contains positive-duration PLAY_END listening events; `valid_play` means at least 30 seconds. Aggregate `plays` columns retain raw event counts for compatibility and rate denominators. `valid_plays` drives artist, track, and genre rankings and display shares. Minutes include short events. Unknown duration produces an unknown completion share, not an automatic skip.

Activity timestamps retain UTC and add `played_at_local` in America/New_York. Calendar fields use local time, labeled ET. The daily export has no timezone metadata: its dates and synthesized date-plus-hour timestamps remain timezone-naive and are used only for notebook inspection, not the activity timeline.

`heatmap.parquet` stores all 42 weekday/four-hour cells. Circle size is mean minutes per calendar weekday in the observation range, including silent dates. Detail cards show total minutes and the largest date's contribution.

`recommend.py` is the single scoring source. The dashboard filters saved candidates by readiness, role, and known artist, then applies the existing mood/genre/text boosts. Compact neighbor pairs are joined to candidate metadata at read time. The unused sample, serialized model, and matrix artifacts were removed. The notebook consumes both profile tables, so individual metrics remain; the arbitrary listener-profile label was removed.

## Evaluation

The approved midnight-ET cutoffs are December 20 and 27, 2025 for tuning and January 31 and February 7, 2026 for held-out reporting, each with a 28-day target window. Features and thresholds use only pre-cutoff plays. Library play/skip counts, added dates, and playlist counts are excluded in evaluation. The report distinguishes production scoring weights from the separately tuned blend and reports a historical-profile neighbor ablation.

See [evaluation](reports/evaluation.md), [headline comparison](reports/before_after.md), [ranking comparison](reports/ranking_comparison.md), and [plain-language changelog](reports/CHANGELOG.md). Per-window metrics and summaries are available as CSV files. With one user, two held-out windows, overlapping target windows, and export-time metadata, results are descriptive rather than evidence of general recommendation quality.

## Structure

- `src/music_analytics/build.py`, `read.py`, `paths.py`: data processing and paths.
- `src/music_analytics/config.py`, `scoring.py`: shared settings and rate shrinkage.
- `src/music_analytics/recommend.py`, `evaluate.py`: scoring, neighbors, and rolling evaluation.
- `src/music_analytics/dashboard/`: data loading, static CSS/theme, and one module per section.
- `app/dashboard.py`: Streamlit entry point and tab layout.
- `scripts/`: pipeline entry points.
- `tests/`: small regression fixtures and dashboard interaction checks.
- `notebooks/`: retained historical audit and exploratory analysis; the EDA notebook's reads are updated for compact neighbor pairs.

The raw audit notebook describes an older intermediate-data layout. It is retained as historical exploration rather than a required pipeline stage. Its results should not be confused with the current processed pipeline.

AI-assisted refactoring and verification are documented in the changelog.
>>>>>>> e7230f5 (revised project with new display)
