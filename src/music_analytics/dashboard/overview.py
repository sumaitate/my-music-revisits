import streamlit as st
from music_analytics.config import LISTENER_NAME, TZ_LABEL, BUCKET_LABELS
from music_analytics.dashboard.theme import PALETTE
from music_analytics.dashboard.common import _esc, metric


def hero() -> None:
    st.markdown(f"""
    <div class="hero">
      <div class="eyebrow">An experiment in listening</div>
      <h1>Hi, I'm {_esc(LISTENER_NAME)}.<br>This is my <span class="highlight">listening data.</span></h1>
      <div class="small-caps">October 2025 – March 2026</div>
      <p>
      In October 2025, I switched my music streaming app for 5 months to see which service I preferred. Majority of the tracks were imported from my previous library. When the experiment ended, I exported my data to analyze my music listening behavior and figure out which tracks I listened to most. 
      </p>
      
      <p>This is a capsule of my music listening data during that specific period, not a full picture of my listening behavior. A first listen or "discovery" here doesn't mean I discovered the song then.</p>
    </div>
    """, unsafe_allow_html=True)


def section_overview(data: dict) -> None:
    plays, tracks, days = data["plays"], data["tracks"], data["days"]
    artists, genres = data["artists"], data["genres"]

    n_days = len(days)
    total_minutes = plays["minutes"].sum()
    avg_minutes = total_minutes / n_days if n_days else 0
    n_artists = artists.loc[artists["artist"].ne("Unknown Artist"), "artist"].nunique()
    n_genres = genres["genre"].nunique()

    st.markdown('<div class="eyebrow">OVERVIEW</div>', unsafe_allow_html=True)
    st.subheader("At a Glance")

    items = [
        ("Total Listening Time", f"{total_minutes / 60:,.1f} Hours", f"{total_minutes:,.0f} Minutes"),
        ("Avg. per Listening Day", f"{avg_minutes:,.0f} Minutes", None),
        ("Listening Events", f"{len(plays):,}", None),
        ("Tracks in the History", f"{len(tracks):,}", None),
        ("Listening Days", f"{n_days:,}", None),
        ("Plays (30s+)", f"{int(plays['valid_play'].sum()):,}", None),
        ("Artists", f"{n_artists:,}", None),
        ("Unique Genres", f"{n_genres:,}", None),
    ]
    tiles = "".join(metric(label, value, sub) for label, value, sub in items)
    st.markdown(f'<div class="metric-grid">{tiles}</div>', unsafe_allow_html=True)

    st.markdown('<div class="small-caps">Top 5 Artists</div>', unsafe_allow_html=True)
    top_artists = (artists[artists["artist"].ne("Unknown Artist")]
                   .sort_values("valid_plays", ascending=False).head(5))
    max_plays = top_artists["valid_plays"].max() if len(top_artists) else 1
    rows_html = ""
    for i, row in enumerate(top_artists.itertuples(), start=1):
        width = (row.valid_plays / max_plays * 100) if max_plays else 0
        color = PALETTE[(i - 1) % len(PALETTE)]
        rows_html += (
            f'<div class="genre-row"><div class="genre-row-top"><span>{i:02d} {_esc(row.artist)}</span>'
            f'<span>{row.valid_plays:,}</span></div>'
            f'<div class="bar-bg"><div class="bar-fill" style="width:{width:.1f}%;background:{color};"></div></div></div>'
        )
    st.markdown(rows_html, unsafe_allow_html=True)

    kv_rows = []
    if n_days and "minutes" in days.columns:
        longest = days.loc[days["minutes"].idxmax()]
        kv_rows.append(("Longest Day", f"{longest['date']:%b %d, %Y} · {longest['minutes']:,.0f} Minutes"))
    heat = data["heatmap"]
    if heat is not None and not heat.empty and heat["minutes"].max() > 0:
        peak = heat.loc[heat["avg_minutes"].idxmax()]
        kv_rows.append(("Peak Listening Time",
                        f"{peak['weekday']}, {BUCKET_LABELS.get(peak['bucket'], peak['bucket'])} {TZ_LABEL}"))
    if len(tracks):
        top_track = tracks.sort_values("valid_plays", ascending=False).iloc[0]
        kv_rows.append(("Most-Played Track", f"{top_track['track']} — {top_track['artist']}"))
    if kv_rows:
        st.markdown('<div class="small-caps">Highlights</div>', unsafe_allow_html=True)
        st.markdown("".join(f'<div class="kv"><span>{_esc(k)}</span><strong>{_esc(v)}</strong></div>' for k, v in kv_rows),
                    unsafe_allow_html=True)
