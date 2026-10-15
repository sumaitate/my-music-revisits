import numpy as np
import pandas as pd
import pytest
from scipy import sparse
from music_analytics import build
from music_analytics.read import as_time, split_track
from music_analytics.scoring import smoothed_rate
from music_analytics.recommend import make_model, make_pairs


def library_row(title="Exact", artist="Artist", album="Album", key="a", apple_id="1"):
    return {"track": title, "artist": artist, "album": album, "genre": "Pop", "track_key": key,
            "track_id": key, "apple_id": apple_id, "track_name": title.lower(), "album_name": album.lower(),
            "artist_name": artist.lower(), "duration_milliseconds": 180000, "library_plays": 10,
            "library_skips": 0, "added_at": pd.Timestamp("2025-01-01", tz="UTC"), "release_at": pd.NaT}


def daily_row(title="Daily", artist="Daily Artist", key="d"):
    return {"track_name": title.lower(), "artist": artist, "album": "Daily Album", "genre": "Jazz",
            "track_key": key, "duration_milliseconds": 180000, "plays": 1, "minutes": 2}


def events(titles, timestamps=None, duration=180000, milliseconds=150000):
    times = timestamps or [f"2026-01-01T12:{i:02}:00Z" for i in range(len(titles))]
    return pd.DataFrame({"event_id": [str(i) for i in range(len(titles))], "event_type": "PLAY_END",
                         "song_name": titles, "album_name": ["Album" if t == "Exact" else "" for t in titles],
                         "event_end_timestamp": times, "event_start_timestamp": times, "event_received_timestamp": times,
                         "play_duration_milliseconds": milliseconds, "media_duration_in_milliseconds": duration,
                         "end_reason_type": "natural"})


def make(monkeypatch, raw, library=None, daily=None):
    monkeypatch.setattr(build, "read_csv", lambda name: raw.copy())
    return build.make_plays(pd.DataFrame([library_row()]) if library is None else library,
                            pd.DataFrame([daily_row()]) if daily is None else daily)


def test_blank_id_merge_does_not_multiply(monkeypatch):
    lib = pd.DataFrame([library_row(key="blank1", apple_id=""), library_row(key="blank2", apple_id=""),
                        library_row(key="one", apple_id="1"), library_row(key="duplicate", apple_id="1")])
    raw = pd.DataFrame({"track_identifier": [None, "1", "999"], "track_description": ["Raw - Missing", "Raw - Exact", "Raw - Other"],
                        "date_played": [20260101]*3, "hours": [1]*3, "play_count": [1]*3})
    monkeypatch.setattr(build, "read_csv", lambda name: raw.copy())
    result = build.make_daily(lib)
    assert len(result) == 3
    assert result.iloc[0]["artist"] == "Raw"
    assert result.iloc[1]["track_key"] == "one"
    assert result["date"].dt.tz is None


def test_merge_tiers_and_ambiguous_titles(monkeypatch):
    lib = pd.DataFrame([library_row(), library_row(title="Library", key="l"),
                        library_row(title="Ambiguous", key="x", artist="First"),
                        library_row(title="Ambiguous", key="y", artist="Second"),
                        library_row(title="Daily Conflict", key="z")])
    daily = pd.DataFrame([daily_row(), daily_row("Daily Conflict", "First", "dc1"), daily_row("Daily Conflict", "Second", "dc2")])
    raw = events(["Exact", "Daily", "Library", "Missing", "Ambiguous", "Daily Conflict"])
    result = make(monkeypatch, raw, lib, daily)
    assert len(result) == len(raw)
    assert result.match_tier.tolist() == ["exact title+album", "daily title", "library title", "unmatched", "unmatched", "unmatched"]
    assert result.artist.iloc[-2:].eq("Unknown Artist").all()
    assert result.ambiguous_title.sum() == 2


@pytest.mark.parametrize("times,hours,offsets", [
    (["2025-11-02T05:30:00Z", "2025-11-02T06:30:00Z"], [1, 1], [-4, -5]),
    (["2026-03-08T06:30:00Z", "2026-03-08T07:30:00Z"], [1, 3], [-5, -4]),
])
def test_dst(monkeypatch, times, hours, offsets):
    result = make(monkeypatch, events(["Exact"]*2, times))
    assert result.hour.tolist() == hours
    assert [x.utcoffset().total_seconds()/3600 for x in result.played_at_local] == offsets
    assert result.bucket.eq("00-04").all()
    assert result.weekday.eq("Sunday").all()


def test_missing_duration_is_not_itself_friction(monkeypatch):
    result = make(monkeypatch, events(["Exact"], duration=0))
    assert not result.duration_known.iloc[0]
    assert pd.isna(result.play_share.iloc[0])
    assert result.full_play.iloc[0]
    assert not result.friction.iloc[0]
    short = make(monkeypatch, events(["Exact"], duration=0, milliseconds=10000))
    assert short.friction.iloc[0]


def test_time_parser_mixed_values():
    target = pd.Timestamp("2026-01-01", tz="UTC")
    values = pd.Series([int(target.timestamp()*1000), "2026-01-01T00:00:00Z", None, "invalid"])
    parsed = as_time(values)
    assert parsed.iloc[:2].eq(target).all()
    assert parsed.iloc[2:].isna().all()


def test_split_preserves_multiple_separators():
    result = split_track(pd.Series(["Artist - Track - Live - 2025", "Single title"]))
    assert result.iloc[0].to_dict() == {"artist": "Artist", "track": "Track - Live - 2025"}
    assert pd.isna(result.iloc[1].artist)
    assert result.iloc[1].track == "Single title"


def test_shrinkage():
    assert smoothed_rate(0, 0, .3) == pytest.approx(.3)
    assert smoothed_rate(900000, 1000000, .3) == pytest.approx(.9, abs=1e-5)
    assert .3 < smoothed_rate(1, 1, .3) < 1


def test_neighbors_exclude_self_and_ineligible():
    tracks = pd.DataFrame({"track_key": list("abcde"), "artist": ["A", "B", "C", "D", "Unknown Artist"],
                           "recommender_ready": [True, False, True, True, True],
                           "recommend_role": ["Bring Back", "Bring Back", "Leave Alone", "Bring Back", "Bring Back"]})
    matrix = sparse.csr_matrix(np.ones((5, 3)))
    pairs = make_pairs(tracks, matrix, make_model(matrix, 2), 2)
    assert list(pairs.columns) == ["seed_track_key", "candidate_track_key", "similarity", "rank"]
    assert pairs.seed_track_key.ne(pairs.candidate_track_key).all()
    assert set(pairs.candidate_track_key) <= {"a", "d"}
    assert pairs.groupby("seed_track_key").size().le(2).all()


def test_cutoff_features_ignore_future_and_snapshot(monkeypatch):
    plays = make(monkeypatch, events(["Exact", "Exact"], ["2026-01-01T00:00:00Z", "2026-02-01T00:00:00Z"]))
    cutoff = pd.Timestamp("2026-01-15", tz="UTC")
    first = build.make_features(plays, cutoff, use_snapshot_features=False)
    changed = plays.copy()
    changed.loc[1, "minutes"] = 1000000
    second = build.make_features(changed, cutoff, use_snapshot_features=False)
    pd.testing.assert_frame_equal(first, second)
    assert first.plays.iloc[0] == 1
    assert not {"playlist_count", "playlist_log", "library_plays", "library_skips", "added_at"} & set(first.columns)
    assert first.recency_days.iloc[0] == 14


def test_heatmap_calendar_denominators(monkeypatch):
    plays = make(monkeypatch, events(["Exact", "Exact"], ["2026-01-05T12:00:00Z", "2026-01-12T12:00:00Z"]))
    heat = build.make_heatmap(plays)
    assert len(heat) == 42
    cell = heat.loc[heat.weekday.eq("Mon") & heat.bucket.eq("04-08")].iloc[0]
    assert cell.weekday_count == 2
    assert cell.avg_minutes == pytest.approx(2.5)
    assert cell.top_day_share == pytest.approx(.5)


def test_mixed_iso_precision():
    result = as_time(pd.Series(["2026-01-01T01:00:00.123Z", "2026-01-01T01:01:00Z"]))
    assert result.notna().all()


def test_html_escaping():
    from music_analytics.dashboard.common import _esc, metric
    assert "<script>" not in _esc("<script>alert('x')</script>")
    assert "<img" not in metric("<img>", "<img>", "<img>")


def test_evaluation_metric_definitions():
    from music_analytics.evaluate import metrics
    ranking = pd.DataFrame({"track_key": ["hit", "miss"], "artist": ["A", "B"]})
    score = metrics(ranking, {"hit", "unseen"}, 2)
    assert score["recall"] == .5
    assert score["hit_rate"] == 1
    assert score["ndcg"] == pytest.approx(1 / (1 + 1 / np.log2(3)))
