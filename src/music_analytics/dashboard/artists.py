import pandas as pd
import streamlit as st
from music_analytics.dashboard.common import info_card


def section_artists(data: dict) -> None:
    artists, plays = data["artists"], data["plays"]

    st.markdown('<div class="eyebrow">ARTISTS</div>', unsafe_allow_html=True)
    st.subheader("Most-Played Artists")

    a_sorted = (artists[artists["artist"].ne("Unknown Artist")]
                .sort_values("valid_plays", ascending=False).head(10).reset_index(drop=True))
    max_plays = a_sorted["valid_plays"].max() if len(a_sorted) else 1

    for i, row in enumerate(a_sorted.itertuples(), start=1):
        size = 8 + 14 * (row.valid_plays / max_plays if max_plays else 0)
        c1, c2, c3, c4 = st.columns([0.08, 0.58, 0.2, 0.14])
        with c1:
            st.write(f"**{i:02d}**")
        with c2:
            if st.button(row.artist, key=f"artist_{i}", use_container_width=True):
                st.session_state["selected_artist"] = row.artist
        with c3:
            st.write(f"{row.valid_plays:,}")
        with c4:
            st.markdown(f'<div class="bubble" style="width:{size}px;height:{size}px;"></div>', unsafe_allow_html=True)

    selected_artist = st.session_state.get("selected_artist")
    if selected_artist:
        detail = _artist_detail(selected_artist, plays)
        if detail:
            info_card(detail["name"], [detail["stats"], f"Most played: {detail['top']}"])


@st.cache_data
def _artist_detail(artist: str, plays: pd.DataFrame) -> dict | None:
    sub = plays.loc[plays["artist"].eq(artist)]
    if sub.empty:
        return None
    valid = sub.loc[sub["valid_play"]]
    top = valid["track"].value_counts()
    return {"name": artist,
            "stats": f"{len(valid):,} plays (30s+) · {len(sub):,} events · {sub['track_key'].nunique()} tracks · {sub['minutes'].sum():,.0f} minutes",
            "top": top.index[0] if not top.empty else "No plays of at least 30 seconds"}
