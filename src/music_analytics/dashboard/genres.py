import streamlit as st
from music_analytics.dashboard.theme import PALETTE
from music_analytics.dashboard.common import _esc


def section_genres(data: dict) -> None:
    genres, plays = data["genres"], data["plays"]

    st.markdown('<div class="eyebrow">GENRES</div>', unsafe_allow_html=True)
    st.subheader("Leading Genres")
    st.caption("Ranked by share of plays of at least 30 seconds.")

    total_events = int(plays["valid_play"].sum())
    g_sorted = genres.sort_values("valid_plays", ascending=False).reset_index(drop=True)
    if total_events:
        # drop genres whose share would display as 0.0%
        g_sorted = g_sorted[g_sorted["valid_plays"].map(lambda p: f"{p / total_events:.1%}" != "0.0%")].reset_index(drop=True)

    show_all = st.session_state.get("show_all_genres", False)
    shown = g_sorted if show_all else g_sorted.head(6)

    rows_html = ""
    for i, row in enumerate(shown.itertuples(), start=1):
        share = row.valid_plays / total_events if total_events else 0
        color = PALETTE[(i - 1) % len(PALETTE)]
        rows_html += (
            f'<div class="genre-row"><div class="genre-row-top"><span>{i:02d} {_esc(row.genre)}</span><span>{share:.1%}</span></div>'
            f'<div class="bar-bg"><div class="bar-fill" style="width:{share*100:.1f}%;background:{color};"></div></div></div>'
        )
    box = st.container(height=420) if show_all else st.container()
    with box:
        st.markdown(rows_html, unsafe_allow_html=True)

    if not show_all and len(g_sorted) > 6:
        rest = g_sorted.iloc[6:]
        rest_events = int(rest["valid_plays"].sum())
        rest_share = rest_events / total_events if total_events else 0
        named = rest.head(4)
        bits = ", ".join(f"{r.genre} ({r.valid_plays/total_events:.1%})" for r in named.itertuples())
        st.caption(f"The other {len(rest)} named genres account for {rest_events:,} plays (30s+) "
                   f"({rest_share:.1%}), led by {bits}.")

    if len(g_sorted) > 6 or show_all:
        if st.button("Show fewer" if show_all else "All genres", key="toggle_genres"):
            st.session_state["show_all_genres"] = not show_all
            st.rerun()
