import streamlit as st


def section_repeat(data: dict) -> None:
    tracks, plays = data["tracks"], data["plays"]
    st.markdown('<div class="eyebrow">REPEAT LISTENING</div>', unsafe_allow_html=True)
    st.subheader("How Much Did I Replay?")

    label_to_n = {"Top 5 Tracks": 5, "Top 10 Tracks": 10, "Top 25 Tracks": 25}
    choice = st.pills("Compare", list(label_to_n.keys()), selection_mode="single",
                       default="Top 5 Tracks", key="repeat_choice", label_visibility="collapsed")
    n = label_to_n.get(choice, 5)

    top = tracks.sort_values("valid_plays", ascending=False).head(n)
    total = int(plays["valid_play"].sum())
    share = top["valid_plays"].sum() / total if total else 0

    st.progress(float(share))
    st.caption(f"My top {n} tracks account for {share:.1%} of plays (30s+) ({int(top['valid_plays'].sum()):,} of {total:,}).")

    list_box = st.container(height=260) if n > 5 else st.container()
    with list_box:
        for i, row in enumerate(top.itertuples(), start=1):
            c1, c2 = st.columns([0.78, 0.22])
            with c1:
                st.markdown(f"**{i}. {row.track}** — {row.artist}")
            with c2:
                st.markdown(f"<div style='text-align:right'>{row.valid_plays:,} plays</div>", unsafe_allow_html=True)

    st.caption("Counts include plays of at least 30 seconds; short listening events are excluded.")
