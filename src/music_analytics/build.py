import json

import numpy as np
import pandas as pd

from music_analytics.paths import clean_path, work_path
from music_analytics.read import as_day, as_time, audit_data, read_csv, read_zip, safe_rate, split_track, text_key


def get_col(data: pd.DataFrame, name: str, fill=None) -> pd.Series:
    if name in data.columns:
        return data[name]

    if isinstance(fill, pd.Series):
        return fill.reindex(data.index)

    return pd.Series(fill, index=data.index)


def id_text(value: pd.Series) -> pd.Series:
    number = pd.to_numeric(value, errors="coerce")
    return number.astype("Int64").astype(str).replace("<NA>", "")


def key_text(value: pd.Series) -> pd.Series:
    return value.map(text_key)


def scale_score(value: pd.Series) -> pd.Series:
    value = pd.to_numeric(value, errors="coerce").fillna(0)

    if value.max() == value.min():
        return pd.Series(0.0, index=value.index)

    return (value - value.min()) / (value.max() - value.min())


def clean_source(value) -> str:
    text = str(value).strip().lower()
    text = text.replace("_", " ")
    text = text.replace("/", " ")
    return " ".join(text.split())


def source_label(source, feature, container) -> str:
    text = clean_source(f"{source} {feature} {container}")

    if text in {"", "nan", "none"}:
        return "Unknown Source"

    if "search" in text and "album" in text:
        return "Search to Album"

    if "search" in text:
        return "Search"

    if "library" in text and "playlist" in text:
        return "Library Playlist"

    if "playlist" in text:
        return "Playlist"

    if "album detail" in text or "album page" in text or "album" in text:
        return "Album Page"

    if "now playing" in text:
        return "Now Playing"

    if "radio" in text or "station" in text:
        return "Radio or Station"

    if "recommend" in text or "for you" in text:
        return "Recommendation Surface"

    if "artist" in text:
        return "Artist Page"

    if "missing active tab" in text:
        return "Unknown Source"

    return "Other Source"


def source_role(label: str) -> str:
    if label in {"Search", "Search to Album", "Recommendation Surface", "Radio or Station"}:
        return "Discovery"

    if label in {"Playlist", "Library Playlist"}:
        return "Playlist"

    if label in {"Album Page", "Artist Page"}:
        return "Browsing"

    if label == "Now Playing":
        return "Playback"

    return "Unknown"


def time_label(hour) -> str:
    if pd.isna(hour):
        return "Unknown Time"

    hour = int(hour)

    if 5 <= hour < 12:
        return "Morning"

    if 12 <= hour < 17:
        return "Afternoon"

    if 17 <= hour < 22:
        return "Evening"

    return "Night"


def top_value(value: pd.Series) -> str:
    value = value.dropna().astype(str)

    if value.empty:
        return "Unknown"

    return value.value_counts().index[0]


def load_library() -> pd.DataFrame:
    data = read_zip("library_tracks.json.zip")

    library = pd.DataFrame(index=data.index)
    library["track_id"] = id_text(get_col(data, "track_identifier", ""))
    library["apple_id"] = id_text(get_col(data, "apple_music_track_identifier", ""))
    library["track"] = get_col(data, "title", "").astype("string").str.strip()
    library["artist"] = get_col(data, "artist", "").astype("string").str.strip()
    library["album"] = get_col(data, "album", "").astype("string").str.strip()
    library["genre"] = get_col(data, "genre", "").astype("string").str.strip()
    library["duration_milliseconds"] = pd.to_numeric(get_col(data, "track_duration", 0), errors="coerce").fillna(0)
    library["library_plays"] = pd.to_numeric(get_col(data, "track_play_count", 0), errors="coerce").fillna(0)
    library["library_skips"] = pd.to_numeric(get_col(data, "skip_count", 0), errors="coerce").fillna(0)
    library["added_at"] = as_time(get_col(data, "date_added_to_library", pd.Series(index=data.index)))
    library["release_at"] = as_time(get_col(data, "release_date", pd.Series(index=data.index)))

    library = library[
        library["track"].notna()
        & library["artist"].notna()
        & library["track"].astype(str).str.strip().ne("")
        & library["artist"].astype(str).str.strip().ne("")
    ].copy()

    library["track_name"] = key_text(library["track"])
    library["artist_name"] = key_text(library["artist"])
    library["album_name"] = key_text(library["album"])

    library["track_key"] = np.where(
        library["apple_id"].ne(""),
        "apple:" + library["apple_id"],
        library["artist_name"] + "|" + library["track_name"] + "|" + library["album_name"],
    )

    return library.drop_duplicates("track_key").reset_index(drop=True)


def load_playlists() -> tuple[pd.DataFrame, pd.DataFrame]:
    data = read_zip("library_playlists.json.zip")

    playlists = pd.DataFrame(index=data.index)
    playlists["playlist_id"] = id_text(get_col(data, "container_identifier", ""))
    playlists["playlist"] = get_col(data, "title", "").astype("string").str.strip()
    playlists["playlist_type"] = get_col(data, "container_type", "").astype("string").str.strip()
    playlists["added_at"] = as_time(get_col(data, "added_date", pd.Series(index=data.index)))
    playlists["items"] = get_col(data, "playlist_item_identifiers", pd.Series(index=data.index))

    links = playlists[["playlist_id", "playlist", "playlist_type", "items"]].explode("items")
    links = links.dropna(subset=["items"]).copy()
    links["track_id"] = id_text(links["items"])
    links = links.drop(columns=["items"])
    links = links.drop_duplicates(["playlist_id", "track_id"]).reset_index(drop=True)

    playlists["track_count"] = playlists["items"].map(lambda value: len(value) if isinstance(value, list) else 0)
    playlists = playlists.drop(columns=["items"])

    return playlists.reset_index(drop=True), links


def make_daily(library: pd.DataFrame) -> pd.DataFrame:
    data = read_csv("play_history_daily_tracks.csv")
    split = split_track(get_col(data, "track_description", ""))

    daily = pd.DataFrame(index=data.index)
    daily["apple_id"] = id_text(get_col(data, "track_identifier", ""))
    daily["track"] = split["track"].astype("string").str.strip()
    daily["artist"] = split["artist"].astype("string").str.strip()
    daily["date"] = as_day(get_col(data, "date_played", pd.Series(index=data.index)))
    daily["hour"] = pd.to_numeric(get_col(data, "hours", 0), errors="coerce").fillna(0).astype(int)
    daily["played_at"] = daily["date"] + pd.to_timedelta(daily["hour"], unit="h")
    daily["play_milliseconds"] = pd.to_numeric(get_col(data, "play_duration_milliseconds", 0), errors="coerce").fillna(0)
    daily["plays"] = pd.to_numeric(get_col(data, "play_count", 0), errors="coerce").fillna(0)
    daily["skips"] = pd.to_numeric(get_col(data, "skip_count", 0), errors="coerce").fillna(0)
    daily["source_type"] = get_col(data, "source_type", "").astype("string")
    daily["end_reason"] = get_col(data, "end_reason_type", "").astype("string")
    daily["ignore_recs"] = get_col(data, "ignore_for_recommendations", False).astype(bool)

    lookup = library[
        [
            "apple_id",
            "track_id",
            "track_key",
            "track",
            "artist",
            "album",
            "genre",
            "duration_milliseconds",
        ]
    ].rename(
        columns={
            "track": "track_library",
            "artist": "artist_library",
            "album": "album_library",
            "genre": "genre_library",
            "duration_milliseconds": "duration_library",
        }
    )

    daily = daily.merge(lookup, on="apple_id", how="left")

    daily["track"] = daily["track_library"].combine_first(daily["track"])
    daily["artist"] = daily["artist_library"].combine_first(daily["artist"]).fillna("Unknown Artist")
    daily["album"] = daily["album_library"].fillna("Unknown Album")
    daily["genre"] = daily["genre_library"].fillna("Unknown Genre")
    daily["duration_milliseconds"] = daily["duration_library"].fillna(0)

    daily["track_name"] = key_text(daily["track"])
    daily["artist_name"] = key_text(daily["artist"])
    daily["album_name"] = key_text(daily["album"])

    daily["track_key"] = daily["track_key"].where(
        daily["track_key"].notna(),
        daily["artist_name"] + "|" + daily["track_name"] + "|" + daily["album_name"],
    )

    daily["minutes"] = daily["play_milliseconds"] / 60000
    daily["skip_rate"] = safe_rate(daily["skips"], daily["plays"])

    daily = daily.drop(
        columns=["track_library", "artist_library", "album_library", "genre_library", "duration_library"],
        errors="ignore",
    )

    return daily.reset_index(drop=True)


def make_plays(library: pd.DataFrame, daily: pd.DataFrame) -> pd.DataFrame:
    data = read_csv("music_play_activity.csv")

    if "event_type" in data.columns:
        data = data[data["event_type"].astype(str).str.upper().eq("PLAY_END")].copy()

    data["play_milliseconds"] = pd.to_numeric(get_col(data, "play_duration_milliseconds", 0), errors="coerce")
    data = data[data["play_milliseconds"].notna() & data["play_milliseconds"].gt(0)].copy()

    if data.empty:
        raise ValueError("music_play_activity.csv produced zero usable play rows.")

    base_time = get_col(data, "event_timestamp", pd.Series(index=data.index))

    plays = pd.DataFrame(index=data.index)
    plays["event_id"] = get_col(data, "event_id", "").astype("string")
    plays["track"] = get_col(data, "song_name", "").astype("string").str.strip()
    plays["album"] = get_col(data, "album_name", "").astype("string").str.strip()
    plays["played_at"] = as_time(get_col(data, "event_end_timestamp", base_time))
    plays["start_at"] = as_time(get_col(data, "event_start_timestamp", base_time))
    plays["received_at"] = as_time(get_col(data, "event_received_timestamp", base_time))
    plays["play_milliseconds"] = data["play_milliseconds"].fillna(0)
    plays["duration_milliseconds"] = pd.to_numeric(get_col(data, "media_duration_in_milliseconds", 0), errors="coerce").fillna(0)
    plays["end_reason"] = get_col(data, "end_reason_type", "").astype("string")
    plays["source_type"] = get_col(data, "source_type", "").astype("string")
    plays["feature"] = get_col(data, "feature_name", "").astype("string")
    plays["container"] = get_col(data, "container_name", "").astype("string")
    plays["container_type"] = get_col(data, "container_type", "").astype("string")
    plays["device"] = get_col(data, "device_type", "").astype("string")
    plays["media_type"] = get_col(data, "media_type", "").astype("string")
    plays["auto_play"] = get_col(data, "auto_play", "").astype("string")
    plays["shuffle_play"] = get_col(data, "shuffle_play", "").astype("string")
    plays["repeat_play"] = get_col(data, "repeat_play", "").astype("string")
    plays["use_history"] = get_col(data, "use_listening_history", "").astype("string")
    plays["offline"] = get_col(data, "offline", "").astype("string")

    plays = plays[
        plays["track"].notna()
        & plays["track"].astype(str).str.strip().ne("")
        & plays["played_at"].notna()
    ].copy()

    plays["track_name"] = key_text(plays["track"])
    plays["album_name"] = key_text(plays["album"])

    exact = library.sort_values("library_plays", ascending=False).drop_duplicates(["track_name", "album_name"])
    exact = exact[
        [
            "track_name",
            "album_name",
            "track_id",
            "apple_id",
            "track_key",
            "artist",
            "album",
            "genre",
            "duration_milliseconds",
        ]
    ].rename(
        columns={
            "track_id": "track_id_exact",
            "apple_id": "apple_id_exact",
            "track_key": "track_key_exact",
            "artist": "artist_exact",
            "album": "album_exact",
            "genre": "genre_exact",
            "duration_milliseconds": "duration_exact",
        }
    )

    title = library.sort_values("library_plays", ascending=False).drop_duplicates("track_name")
    title = title[
        [
            "track_name",
            "track_id",
            "apple_id",
            "track_key",
            "artist",
            "album",
            "genre",
            "duration_milliseconds",
        ]
    ].rename(
        columns={
            "track_id": "track_id_title",
            "apple_id": "apple_id_title",
            "track_key": "track_key_title",
            "artist": "artist_title",
            "album": "album_title",
            "genre": "genre_title",
            "duration_milliseconds": "duration_title",
        }
    )

    daily_title = daily.sort_values(["plays", "minutes"], ascending=[False, False]).drop_duplicates("track_name")
    daily_title = daily_title[
        [
            "track_name",
            "track_key",
            "artist",
            "album",
            "genre",
            "duration_milliseconds",
        ]
    ].rename(
        columns={
            "track_key": "track_key_daily",
            "artist": "artist_daily",
            "album": "album_daily",
            "genre": "genre_daily",
            "duration_milliseconds": "duration_daily",
        }
    )

    plays = plays.merge(exact, on=["track_name", "album_name"], how="left")
    plays = plays.merge(daily_title, on="track_name", how="left")
    plays = plays.merge(title, on="track_name", how="left")

    plays["artist"] = plays["artist_exact"].combine_first(plays["artist_daily"]).combine_first(plays["artist_title"]).fillna("Unknown Artist")
    plays["album"] = plays["album"].where(plays["album"].notna() & plays["album"].astype(str).str.strip().ne(""))
    plays["album"] = plays["album"].combine_first(plays["album_exact"]).combine_first(plays["album_daily"]).combine_first(plays["album_title"]).fillna("Unknown Album")
    plays["genre"] = plays["genre_exact"].combine_first(plays["genre_daily"]).combine_first(plays["genre_title"]).fillna("Unknown Genre")
    plays["track_id"] = plays["track_id_exact"].combine_first(plays["track_id_title"])
    plays["apple_id"] = plays["apple_id_exact"].combine_first(plays["apple_id_title"])
    plays["track_key"] = plays["track_key_exact"].combine_first(plays["track_key_daily"]).combine_first(plays["track_key_title"])

    plays["artist_name"] = key_text(plays["artist"])
    plays["album_name"] = key_text(plays["album"])
    plays["track_key"] = plays["track_key"].where(
        plays["track_key"].notna(),
        plays["artist_name"] + "|" + plays["track_name"] + "|" + plays["album_name"],
    )

    plays["display"] = plays["track"].astype(str) + " — " + plays["artist"].astype(str)
    plays["source_label"] = [
        source_label(source, feature, container)
        for source, feature, container in zip(plays["source_type"], plays["feature"], plays["container_type"])
    ]
    plays["source_role"] = plays["source_label"].map(source_role)

    plays["minutes"] = plays["play_milliseconds"] / 60000
    plays["play_share"] = safe_rate(plays["play_milliseconds"], plays["duration_milliseconds"]).clip(0, 1.5)
    plays["good_play"] = plays["play_milliseconds"] >= 30000
    plays["full_play"] = np.where(
        plays["duration_milliseconds"].gt(0),
        plays["play_share"].ge(0.80),
        plays["play_milliseconds"].ge(120000),
    )

    reason = plays["end_reason"].fillna("").astype(str).str.lower()
    plays["friction"] = (
        reason.str.contains("skip", regex=False)
        | reason.str.contains("scrub", regex=False)
        | reason.str.contains("manually", regex=False)
        | plays["play_milliseconds"].lt(30000)
        | plays["play_share"].lt(0.25)
    )

    plays["date"] = plays["played_at"].dt.date
    plays["month"] = plays["played_at"].dt.strftime("%Y-%m")
    plays["weekday"] = plays["played_at"].dt.day_name()
    plays["weekday_num"] = plays["played_at"].dt.weekday
    plays["hour"] = plays["played_at"].dt.hour
    plays["time_block"] = plays["hour"].map(time_label)

    keep = [
        "event_id",
        "played_at",
        "start_at",
        "received_at",
        "date",
        "month",
        "weekday",
        "weekday_num",
        "hour",
        "time_block",
        "track_key",
        "track_id",
        "apple_id",
        "track",
        "artist",
        "album",
        "genre",
        "display",
        "play_milliseconds",
        "duration_milliseconds",
        "minutes",
        "play_share",
        "good_play",
        "full_play",
        "friction",
        "end_reason",
        "source_type",
        "source_label",
        "source_role",
        "feature",
        "container",
        "container_type",
        "device",
        "media_type",
        "auto_play",
        "shuffle_play",
        "repeat_play",
        "use_history",
        "offline",
    ]

    plays = plays[keep].drop_duplicates(["event_id", "played_at", "track_key", "play_milliseconds"])
    plays = plays.sort_values("played_at").reset_index(drop=True)
    plays["play_num"] = plays.groupby("track_key").cumcount() + 1
    plays["first_play"] = plays["play_num"].eq(1)
    plays["repeat_seen"] = plays["play_num"].gt(1)

    return plays


def make_tracks(plays: pd.DataFrame, library: pd.DataFrame, links: pd.DataFrame) -> pd.DataFrame:
    tracks = (
        plays.groupby("track_key", dropna=False)
        .agg(
            track=("track", "first"),
            artist=("artist", "first"),
            album=("album", "first"),
            genre=("genre", "first"),
            display=("display", "first"),
            plays=("track_key", "size"),
            minutes=("minutes", "sum"),
            good_plays=("good_play", "sum"),
            full_plays=("full_play", "sum"),
            friction_plays=("friction", "sum"),
            average_share=("play_share", "mean"),
            first_play=("played_at", "min"),
            last_play=("played_at", "max"),
            active_days=("date", "nunique"),
            source_count=("source_label", "nunique"),
            source_top=("source_label", top_value),
            role_top=("source_role", top_value),
        )
        .reset_index()
    )

    small = library[
        [
            "track_key",
            "track_id",
            "apple_id",
            "duration_milliseconds",
            "library_plays",
            "library_skips",
            "added_at",
            "release_at",
        ]
    ].drop_duplicates("track_key")

    tracks = tracks.merge(small, on="track_key", how="left")

    counts = links.groupby("track_id").agg(playlist_count=("playlist_id", "nunique")).reset_index()
    tracks = tracks.merge(counts, on="track_id", how="left")
    tracks["playlist_count"] = tracks["playlist_count"].fillna(0)

    tracks["good_rate"] = safe_rate(tracks["good_plays"], tracks["plays"])
    tracks["full_rate"] = safe_rate(tracks["full_plays"], tracks["plays"])
    tracks["friction_rate"] = safe_rate(tracks["friction_plays"], tracks["plays"])
    tracks["library_ready"] = tracks["track_id"].notna() | tracks["apple_id"].notna()
    tracks["retained"] = tracks["plays"].ge(2)
    tracks["recommender_ready"] = tracks["plays"].ge(2) & tracks["artist"].ne("Unknown Artist")

    return tracks.sort_values(["plays", "minutes"], ascending=[False, False]).reset_index(drop=True)


def make_artists(plays: pd.DataFrame) -> pd.DataFrame:
    artists = (
        plays.groupby("artist", dropna=False)
        .agg(
            plays=("track_key", "size"),
            tracks=("track_key", "nunique"),
            albums=("album", "nunique"),
            genres=("genre", "nunique"),
            minutes=("minutes", "sum"),
            good_plays=("good_play", "sum"),
            full_plays=("full_play", "sum"),
            friction_plays=("friction", "sum"),
            first_play=("played_at", "min"),
            last_play=("played_at", "max"),
            active_days=("date", "nunique"),
            source_top=("source_label", top_value),
        )
        .reset_index()
    )

    artists["good_rate"] = safe_rate(artists["good_plays"], artists["plays"])
    artists["full_rate"] = safe_rate(artists["full_plays"], artists["plays"])
    artists["friction_rate"] = safe_rate(artists["friction_plays"], artists["plays"])

    return artists.sort_values(["plays", "minutes"], ascending=[False, False]).reset_index(drop=True)


def make_albums(plays: pd.DataFrame) -> pd.DataFrame:
    albums = (
        plays.groupby(["album", "artist"], dropna=False)
        .agg(
            plays=("track_key", "size"),
            tracks=("track_key", "nunique"),
            minutes=("minutes", "sum"),
            full_plays=("full_play", "sum"),
            friction_plays=("friction", "sum"),
            first_play=("played_at", "min"),
            last_play=("played_at", "max"),
        )
        .reset_index()
    )

    albums["full_rate"] = safe_rate(albums["full_plays"], albums["plays"])
    albums["friction_rate"] = safe_rate(albums["friction_plays"], albums["plays"])

    return albums.sort_values(["plays", "minutes"], ascending=[False, False]).reset_index(drop=True)


def make_genres(plays: pd.DataFrame) -> pd.DataFrame:
    genres = (
        plays.groupby("genre", dropna=False)
        .agg(
            plays=("track_key", "size"),
            tracks=("track_key", "nunique"),
            artists=("artist", "nunique"),
            minutes=("minutes", "sum"),
            full_plays=("full_play", "sum"),
            friction_plays=("friction", "sum"),
            source_top=("source_label", top_value),
            time_top=("time_block", top_value),
        )
        .reset_index()
    )

    genres["full_rate"] = safe_rate(genres["full_plays"], genres["plays"])
    genres["friction_rate"] = safe_rate(genres["friction_plays"], genres["plays"])
    genres["share"] = safe_rate(genres["plays"], pd.Series(genres["plays"].sum(), index=genres.index))

    return genres.sort_values(["plays", "minutes"], ascending=[False, False]).reset_index(drop=True)


def make_days(plays: pd.DataFrame) -> pd.DataFrame:
    days = (
        plays.groupby("date", dropna=True)
        .agg(
            plays=("track_key", "size"),
            tracks=("track_key", "nunique"),
            artists=("artist", "nunique"),
            minutes=("minutes", "sum"),
            full_plays=("full_play", "sum"),
            friction_plays=("friction", "sum"),
            top_artist=("artist", top_value),
            top_genre=("genre", top_value),
            top_source=("source_label", top_value),
        )
        .reset_index()
    )

    days["date"] = pd.to_datetime(days["date"])
    days["full_rate"] = safe_rate(days["full_plays"], days["plays"])
    days["friction_rate"] = safe_rate(days["friction_plays"], days["plays"])

    return days.sort_values("date").reset_index(drop=True)


def make_hours(plays: pd.DataFrame) -> pd.DataFrame:
    hours = (
        plays.groupby(["weekday_num", "weekday", "hour"], dropna=True)
        .agg(
            plays=("track_key", "size"),
            minutes=("minutes", "sum"),
            full_plays=("full_play", "sum"),
            friction_plays=("friction", "sum"),
        )
        .reset_index()
    )

    hours["full_rate"] = safe_rate(hours["full_plays"], hours["plays"])
    hours["friction_rate"] = safe_rate(hours["friction_plays"], hours["plays"])

    return hours.sort_values(["weekday_num", "hour"]).reset_index(drop=True)


def make_sources(plays: pd.DataFrame) -> pd.DataFrame:
    sources = (
        plays.groupby(["source_label", "source_role"], dropna=False)
        .agg(
            plays=("track_key", "size"),
            tracks=("track_key", "nunique"),
            artists=("artist", "nunique"),
            genres=("genre", "nunique"),
            minutes=("minutes", "sum"),
            first_plays=("first_play", "sum"),
            repeat_plays=("repeat_seen", "sum"),
            full_plays=("full_play", "sum"),
            friction_plays=("friction", "sum"),
        )
        .reset_index()
    )

    sources["play_share"] = safe_rate(sources["plays"], pd.Series(sources["plays"].sum(), index=sources.index))
    sources["discovery_share"] = safe_rate(sources["first_plays"], sources["plays"])
    sources["repeat_share"] = safe_rate(sources["repeat_plays"], sources["plays"])
    sources["full_rate"] = safe_rate(sources["full_plays"], sources["plays"])
    sources["friction_rate"] = safe_rate(sources["friction_plays"], sources["plays"])

    return sources.sort_values(["plays", "minutes"], ascending=[False, False]).reset_index(drop=True)


def make_sessions(plays: pd.DataFrame) -> pd.DataFrame:
    data = plays.sort_values("played_at").copy()
    gap = data["played_at"].diff().dt.total_seconds().div(60)
    data["session"] = (gap.isna() | gap.gt(30)).cumsum()

    sessions = (
        data.groupby("session")
        .agg(
            start=("played_at", "min"),
            end=("played_at", "max"),
            plays=("track_key", "size"),
            tracks=("track_key", "nunique"),
            artists=("artist", "nunique"),
            genres=("genre", "nunique"),
            minutes=("minutes", "sum"),
            full_plays=("full_play", "sum"),
            friction_plays=("friction", "sum"),
            top_artist=("artist", top_value),
            top_genre=("genre", top_value),
            top_source=("source_label", top_value),
            start_hour=("hour", "first"),
        )
        .reset_index()
    )

    sessions["length"] = (sessions["end"] - sessions["start"]).dt.total_seconds().div(60)
    sessions["full_rate"] = safe_rate(sessions["full_plays"], sessions["plays"])
    sessions["friction_rate"] = safe_rate(sessions["friction_plays"], sessions["plays"])
    sessions["time_block"] = sessions["start_hour"].map(time_label)

    sessions["session_type"] = np.select(
        [
            sessions["plays"].ge(25),
            sessions["tracks"].le(3) & sessions["plays"].ge(6),
            sessions["friction_rate"].ge(0.45),
            sessions["full_rate"].ge(0.70),
        ],
        [
            "Long Routine",
            "Repeat Loop",
            "High Friction",
            "Deep Listening",
        ],
        default="Casual Session",
    )

    return sessions.sort_values("start").reset_index(drop=True)


def make_features(tracks: pd.DataFrame, plays: pd.DataFrame) -> pd.DataFrame:
    data = tracks.copy()

    latest = plays["played_at"].max()
    data["recency_days"] = (latest - data["last_play"]).dt.total_seconds().div(86400).fillna(0)

    data["plays_log"] = np.log1p(data["plays"])
    data["minutes_log"] = np.log1p(data["minutes"])
    data["days_log"] = np.log1p(data["active_days"])
    data["playlist_log"] = np.log1p(data["playlist_count"])
    data["fresh_score"] = 1 / (1 + data["recency_days"])
    data["keep_score"] = 1 - data["friction_rate"].fillna(0).clip(0, 1)

    data["affinity_score"] = (
        0.32 * scale_score(data["plays_log"])
        + 0.20 * scale_score(data["minutes_log"])
        + 0.16 * scale_score(data["days_log"])
        + 0.10 * scale_score(data["playlist_log"])
        + 0.10 * scale_score(data["fresh_score"])
        + 0.12 * scale_score(data["keep_score"])
    )

    play_high = data["plays"].quantile(0.75)
    play_mid = data["plays"].quantile(0.50)
    score_high = data["affinity_score"].quantile(0.75)
    score_mid = data["affinity_score"].quantile(0.50)
    friction_high = data["friction_rate"].quantile(0.75)

    data["favorite_like"] = data["affinity_score"].ge(score_high)

    data["candidate_class"] = np.select(
        [
            data["plays"].ge(play_high) & data["affinity_score"].ge(score_high) & data["friction_rate"].lt(friction_high),
            data["plays"].lt(play_mid) & data["affinity_score"].ge(score_high),
            data["plays"].ge(play_high) & data["friction_rate"].ge(friction_high),
            data["plays"].eq(1) & data["full_rate"].ge(0.80),
            data["affinity_score"].lt(score_mid) & data["friction_rate"].ge(friction_high),
        ],
        [
            "Core Favorite",
            "Rediscovery Candidate",
            "Overexposed or Unstable",
            "Lost Discovery",
            "Exclude From Recommendations",
        ],
        default="General Candidate",
    )

    data["ready_reason"] = np.select(
        [
            data["candidate_class"].eq("Core Favorite"),
            data["candidate_class"].eq("Rediscovery Candidate"),
            data["candidate_class"].eq("Lost Discovery"),
            data["candidate_class"].eq("Overexposed or Unstable"),
            data["candidate_class"].eq("Exclude From Recommendations"),
        ],
        [
            "High affinity, repeated listening, and low friction.",
            "Strong affinity signal but not enough recent exposure.",
            "Strong first-play completion without later return.",
            "High play count but elevated friction.",
            "Low affinity and high friction.",
        ],
        default="Usable track with moderate behavioral evidence.",
    )

    data["text"] = (
        data["track"].fillna("").astype(str)
        + " "
        + data["artist"].fillna("").astype(str)
        + " "
        + data["album"].fillna("").astype(str)
        + " "
        + data["genre"].fillna("").astype(str)
    ).str.lower()

    return data.sort_values("affinity_score", ascending=False).reset_index(drop=True)


def make_life(features: pd.DataFrame) -> pd.DataFrame:
    life = features[
        [
            "track_key",
            "display",
            "track",
            "artist",
            "album",
            "genre",
            "plays",
            "minutes",
            "active_days",
            "first_play",
            "last_play",
            "full_rate",
            "friction_rate",
            "affinity_score",
            "candidate_class",
            "ready_reason",
            "recommender_ready",
        ]
    ].copy()

    life["stage"] = np.select(
        [
            life["candidate_class"].eq("Core Favorite"),
            life["candidate_class"].eq("Rediscovery Candidate"),
            life["candidate_class"].eq("Lost Discovery"),
            life["candidate_class"].eq("Overexposed or Unstable"),
            life["candidate_class"].eq("Exclude From Recommendations"),
        ],
        [
            "Kept",
            "Ready to Revisit",
            "Lost After First Play",
            "Unstable Repeat",
            "Dropped",
        ],
        default="Observed",
    )

    return life.reset_index(drop=True)


def make_profile(plays: pd.DataFrame, tracks: pd.DataFrame, artists: pd.DataFrame, sources: pd.DataFrame) -> pd.DataFrame:
    total = max(len(plays), 1)
    unique_tracks = plays["track_key"].nunique()

    repeat_score = 1 - (unique_tracks / total)
    top_artist_share = artists.head(10)["plays"].sum() / total
    playlist_share = plays["source_role"].eq("Playlist").mean()
    night_share = plays["time_block"].eq("Night").mean()
    friction_score = plays["friction"].mean()
    deep_score = plays["full_play"].mean()
    discovery_share = plays["first_play"].mean()
    retention_score = tracks["retained"].mean()

    genre_counts = plays["genre"].value_counts(normalize=True)
    top_genre_share = genre_counts.iloc[0] if not genre_counts.empty else 0
    genre_score = 1 - top_genre_share

    scores = {
        "Friction-Sensitive Listener": friction_score,
        "Repeat-Driven Listener": repeat_score,
        "Exploratory Listener": discovery_share,
        "Playlist-Led Listener": playlist_share,
        "Night-Heavy Listener": night_share,
        "Artist-Loyal Listener": top_artist_share,
        "Deep-Listening Listener": deep_score,
    }

    profile_type = max(scores, key=scores.get)
    top_source = sources.iloc[0]["source_label"] if not sources.empty else "Unknown Source"
    top_time = plays["time_block"].value_counts().index[0] if not plays.empty else "Unknown Time"

    rows = [
        {"metric": "profile_type", "value": profile_type, "score": scores[profile_type]},
        {"metric": "repeat_intensity", "value": "Repeat Intensity", "score": repeat_score},
        {"metric": "discovery_share", "value": "Discovery Share", "score": discovery_share},
        {"metric": "discovery_retention", "value": "Discovery Retention", "score": retention_score},
        {"metric": "playlist_dependence", "value": "Playlist Dependence", "score": playlist_share},
        {"metric": "night_share", "value": "Night Listening", "score": night_share},
        {"metric": "artist_concentration", "value": "Artist Concentration", "score": top_artist_share},
        {"metric": "genre_fluidity", "value": "Genre Fluidity", "score": genre_score},
        {"metric": "friction_score", "value": "Friction Score", "score": friction_score},
        {"metric": "deep_listening", "value": "Deep Listening", "score": deep_score},
        {"metric": "top_source", "value": top_source, "score": 0},
        {"metric": "top_time", "value": top_time, "score": 0},
    ]

    return pd.DataFrame(rows)


def save_check(tables: dict[str, pd.DataFrame]) -> None:
    profile_type = tables["profile"].loc[tables["profile"]["metric"].eq("profile_type"), "value"].iloc[0]

    check = {
        "plays": int(len(tables["plays"])),
        "tracks": int(len(tables["tracks"])),
        "artists": int(len(tables["artists"])),
        "albums": int(len(tables["albums"])),
        "genres": int(len(tables["genres"])),
        "sessions": int(len(tables["sessions"])),
        "minutes": float(tables["plays"]["minutes"].sum()),
        "first_play": tables["plays"]["played_at"].min().isoformat(),
        "last_play": tables["plays"]["played_at"].max().isoformat(),
        "ready_tracks": int(tables["features"]["recommender_ready"].sum()),
        "profile_type": str(profile_type),
    }

    with (work_path / "data_check.json").open("w", encoding="utf-8") as file:
        json.dump(check, file, indent=2)


def save_data() -> dict[str, pd.DataFrame]:
    audit_data()

    library = load_library()
    playlists, links = load_playlists()
    daily = make_daily(library)
    plays = make_plays(library, daily)

    if plays.empty:
        raise ValueError("No play rows were created. Processed files were not written.")

    tracks = make_tracks(plays, library, links)
    artists = make_artists(plays)
    albums = make_albums(plays)
    genres = make_genres(plays)
    days = make_days(plays)
    hours = make_hours(plays)
    sources = make_sources(plays)
    sessions = make_sessions(plays)
    features = make_features(tracks, plays)
    life = make_life(features)
    profile = make_profile(plays, tracks, artists, sources)

    tables = {
        "library": library,
        "playlists": playlists,
        "playlist_tracks": links,
        "daily_tracks": daily,
        "plays": plays,
        "tracks": tracks,
        "artists": artists,
        "albums": albums,
        "genres": genres,
        "days": days,
        "hours": hours,
        "sources": sources,
        "sessions": sessions,
        "features": features,
        "life": life,
        "profile": profile,
    }

    for name, table in tables.items():
        table.to_parquet(clean_path / f"{name}.parquet", index=False, engine="pyarrow")

    save_check(tables)

    return tables