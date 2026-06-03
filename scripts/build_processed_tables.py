from pathlib import Path
import re

import numpy as np
import pandas as pd


PROJECT_ROOT = Path.cwd()

RAW_CSV_DIR = PROJECT_ROOT / "data" / "raw" / "csv"
INTERIM_CSV_DIR = PROJECT_ROOT / "data" / "interim" / "csv"
PROCESSED_PARQUET_DIR = PROJECT_ROOT / "data" / "processed" / "parquet"
METADATA_DIR = PROJECT_ROOT / "data" / "metadata"

BUILD_REPORT_PATH = METADATA_DIR / "processed_table_report.csv"


def clean_column_name(column_name: str) -> str:
    cleaned = column_name.strip().lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned.strip("_")


def clean_column_names(dataframe: pd.DataFrame) -> pd.DataFrame:
    cleaned = dataframe.copy()
    cleaned.columns = [clean_column_name(column) for column in cleaned.columns]
    return cleaned


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def parse_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", utc=True)


def parse_yyyymmdd(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series.astype(str), format="%Y%m%d", errors="coerce")


def split_track_description(series: pd.Series) -> pd.DataFrame:
    split_values = series.fillna("").astype(str).str.split(" - ", n=1, expand=True)

    artist = split_values[0].replace("", np.nan)

    if split_values.shape[1] > 1:
        title = split_values[1].replace("", np.nan)
    else:
        title = series

    return pd.DataFrame(
        {
            "artist_from_description": artist,
            "title_from_description": title,
        }
    )


def build_listening_events() -> pd.DataFrame:
    path = RAW_CSV_DIR / "play_history_daily_tracks.csv"
    dataframe = clean_column_names(read_csv(path))

    dataframe["date_played"] = parse_yyyymmdd(dataframe["date_played"])
    dataframe["listening_minutes"] = dataframe["play_duration_milliseconds"] / 60000
    dataframe["listening_hours"] = dataframe["listening_minutes"] / 60
    dataframe["skip_rate"] = np.where(
        dataframe["play_count"] > 0,
        dataframe["skip_count"] / dataframe["play_count"],
        0,
    )

    track_parts = split_track_description(dataframe["track_description"])
    dataframe = pd.concat([dataframe, track_parts], axis=1)

    dataframe["week"] = dataframe["date_played"].dt.to_period("W").astype(str)
    dataframe["month"] = dataframe["date_played"].dt.to_period("M").astype(str)
    dataframe["day_name"] = dataframe["date_played"].dt.day_name()

    return dataframe


def build_library_tracks() -> pd.DataFrame:
    path = INTERIM_CSV_DIR / "library_tracks.csv"
    dataframe = clean_column_names(read_csv(path))

    date_columns = [
        "date_added_to_library",
        "date_added_to_icloud_music_library",
        "last_modified_date",
        "release_date",
        "favorite_date_track",
        "date_of_last_skip",
        "last_played_date",
    ]

    for column in date_columns:
        if column in dataframe.columns:
            dataframe[column] = parse_datetime(dataframe[column])

    if "track_duration" in dataframe.columns:
        dataframe["track_duration_minutes"] = dataframe["track_duration"] / 60000

    if "track_play_count" in dataframe.columns and "skip_count" in dataframe.columns:
        dataframe["library_skip_rate"] = np.where(
            dataframe["track_play_count"] > 0,
            dataframe["skip_count"] / dataframe["track_play_count"],
            0,
        )

    return dataframe


def build_favorites() -> pd.DataFrame:
    path = RAW_CSV_DIR / "favorites.csv"
    dataframe = clean_column_names(read_csv(path))

    if "last_modified" in dataframe.columns:
        dataframe["last_modified"] = parse_datetime(dataframe["last_modified"])

    dataframe["preference_score"] = dataframe["preference"].map(
        {
            "LIKE": 1,
            "NEUTRAL": 0,
            "DISLIKE": -1,
        }
    )

    return dataframe


def build_play_activity_events() -> pd.DataFrame:
    path = RAW_CSV_DIR / "music_play_activity.csv"
    dataframe = clean_column_names(read_csv(path))

    selected_columns = [
        "event_id",
        "event_type",
        "event_start_timestamp",
        "event_end_timestamp",
        "event_timestamp",
        "song_name",
        "album_name",
        "item_type",
        "media_type",
        "device_type",
        "device_os_name",
        "device_os_version",
        "feature_name",
        "container_type",
        "container_origin_type",
        "end_reason_type",
        "play_duration_milliseconds",
        "media_duration_in_milliseconds",
        "start_position_in_milliseconds",
        "end_position_in_milliseconds",
        "shuffle_play",
        "repeat_play",
        "offline",
        "provided_codec",
        "provided_playback_format",
        "provided_audio_sample_rate",
        "user_s_audio_quality",
        "user_s_playback_format",
        "use_listening_history",
    ]

    existing_columns = [column for column in selected_columns if column in dataframe.columns]
    dataframe = dataframe[existing_columns].copy()

    for column in ["event_start_timestamp", "event_end_timestamp", "event_timestamp"]:
        if column in dataframe.columns:
            dataframe[column] = parse_datetime(dataframe[column])

    if "play_duration_milliseconds" in dataframe.columns:
        dataframe["listening_minutes"] = dataframe["play_duration_milliseconds"] / 60000

    if "media_duration_in_milliseconds" in dataframe.columns:
        dataframe["media_duration_minutes"] = dataframe["media_duration_in_milliseconds"] / 60000

    if "listening_minutes" in dataframe.columns and "media_duration_minutes" in dataframe.columns:
        dataframe["completion_ratio"] = np.where(
            dataframe["media_duration_minutes"] > 0,
            dataframe["listening_minutes"] / dataframe["media_duration_minutes"],
            np.nan,
        )

        dataframe["completion_ratio"] = dataframe["completion_ratio"].clip(lower=0, upper=1.5)

    return dataframe


def write_table(name: str, dataframe: pd.DataFrame) -> dict:
    path = PROCESSED_PARQUET_DIR / f"{name}.parquet"
    dataframe.to_parquet(path, index=False)

    return {
        "table_name": name,
        "path": str(path.relative_to(PROJECT_ROOT)),
        "row_count": len(dataframe),
        "column_count": len(dataframe.columns),
    }


def main() -> None:
    PROCESSED_PARQUET_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    tables = {
        "listening_events": build_listening_events(),
        "library_tracks_clean": build_library_tracks(),
        "favorites_clean": build_favorites(),
        "play_activity_events": build_play_activity_events(),
    }

    report = pd.DataFrame(
        [write_table(name, dataframe) for name, dataframe in tables.items()]
    )

    report.to_csv(BUILD_REPORT_PATH, index=False)

    print(report.to_string(index=False))
    print()
    print(f"Saved processed table report to: {BUILD_REPORT_PATH}")


if __name__ == "__main__":
    main()
