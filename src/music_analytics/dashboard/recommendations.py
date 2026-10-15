from music_analytics.recommend import similar_to_selection
import re
import pandas as pd
import streamlit as st
from music_analytics.dashboard.theme import PALETTE
from music_analytics.dashboard.common import _esc


QUICK_MOODS = [
    "Rainy night", "Workout", "Relaxing", "Feel good", "Late night drive",
    "Romantic", "Study", "Party", "Heartbreak", "Nostalgic",
    "Angry", "Cozy", "Confident", "Dreamy",
]

_STOPWORDS = {
    "something", "songs", "song", "music", "about", "with", "that", "this", "like", "some",
    "want", "need", "feel", "feeling", "make", "play", "listen", "hear", "good", "just",
    "really", "little", "tracks", "track", "artist", "artists", "genre", "genres", "from",
    "your", "have", "what", "when", "then", "them", "they", "into", "than", "very", "kind",
    "type", "sort", "mood", "vibe", "vibes", "stuff", "things",
}

def _norm_text(s: str) -> str:
    """Lowercase, drop '&', and turn every other symbol into a single space."""
    s = (s or "").lower().replace("&", "")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def _genre_parts(genre: str) -> list:
    """'Hip-Hop/Rap' -> ['hiphop', 'rap']"""
    parts = (_norm_text(p).replace(" ", "") for p in str(genre).split("/"))
    return [p for p in parts if p]


def _match_genres(target: str, available) -> list:
    """Find the genres in the data that correspond to a lexicon genre name."""
    t_parts = _genre_parts(target)
    out = []
    for g in available:
        g_parts = _genre_parts(g)
        if any(tp == gp or (len(tp) >= 4 and tp in gp) or (len(gp) >= 4 and gp in tp)
               for tp in t_parts for gp in g_parts):
            out.append(g)
    return out


def load_mood_lexicon() -> dict:
    return {
        "rainy_moody": {
            "keywords": ["rain", "rainy", "moody", "sad", "dramatic", "melancholy", "heartbreak",
                         "cry", "crying", "lonely", "gloomy", "blue", "emotional", "somber",
                         "breakup", "heartbroken", "broken", "tears", "stormy", "drizzle", "autumn"],
            "genres": ["R&B/Soul", "Alternative", "Jazz"],
        },
        "energetic": {
            "keywords": ["workout", "energy", "hype", "party", "pump", "pumped", "gym", "run", "running",
                         "upbeat", "dance", "fast", "intense", "adrenaline", "hyped", "cardio",
                         "club", "festival", "banger", "cleaning"],
            "genres": ["K-Pop", "Pop", "Dance", "Hip-Hop/Rap", "Hard Rock"],
        },
        "calm": {
            "keywords": ["calm", "quiet", "soft", "relax", "relaxing", "chill", "sleep", "sleepy", "study",
                         "focus", "mellow", "peaceful", "gentle", "unwind", "lofi", "lo-fi",
                         "meditate", "meditation", "ambient", "slow", "bedtime", "reading"],
            "genres": ["Relaxation", "Jazz", "Soundtrack"],
        },
        "happy": {
            "keywords": ["happy", "fun", "feel good", "summer", "sunny", "bright", "cheerful",
                         "joy", "joyful", "positive", "good vibes", "smile", "sunshine", "playful", "cute", "bubbly"],
            "genres": ["Pop", "K-Pop", "Dance"],
        },
        "aggressive": {
            "keywords": ["angry", "aggressive", "rage", "hard", "heavy", "dark", "moshpit",
                         "mad", "furious", "loud", "punk", "metal", "scream"],
            "genres": ["Hard Rock", "Rock", "Hip-Hop/Rap"],
        },
        "romantic": {
            "keywords": ["romantic", "love", "crush", "valentine", "sweet", "intimate",
                         "date", "date night", "wedding", "slow dance", "butterflies"],
            "genres": ["R&B/Soul", "Pop"],
        },
        "nostalgic": {
            "keywords": ["nostalgic", "throwback", "old school", "retro", "classic", "memories",
                         "childhood", "oldies", "vintage", "remember", "80s", "90s", "2000s"],
            "genres": ["Soundtrack", "Rock"],
        },
        "late_night": {
            "keywords": ["late night", "midnight", "night drive", "drive", "driving", "road trip", "2am", "3am"],
            "genres": ["R&B/Soul", "Alternative", "Hip-Hop/Rap", "Dance"],
        },
        "cozy": {
            "keywords": ["cozy", "coffee", "warm", "acoustic", "rainy sunday", "blanket", "fireplace"],
            "genres": ["Jazz", "Soundtrack", "R&B/Soul", "Alternative", "Relaxation"],
        },
        "confident": {
            "keywords": ["confident", "boss", "swagger", "strut", "baddie", "empowered", "main character", "powerful"],
            "genres": ["Hip-Hop/Rap", "Pop", "K-Pop", "R&B/Soul"],
        },
        "dreamy": {
            "keywords": ["dreamy", "floaty", "ethereal", "spacey", "daydream", "airy"],
            "genres": ["Alternative", "Relaxation", "Soundtrack"],
        },
        "epic": {
            "keywords": ["epic", "cinematic", "movie", "film", "anime", "orchestral", "grand"],
            "genres": ["Soundtrack", "Hard Rock", "Rock"],
        },
    }


def score_genre_affinity(text: str, lexicon: dict, available_genres=None) -> tuple[dict, bool]:
    text = (text or "").lower()
    affinity: dict = {}
    matched_any = False
    for mood in lexicon.values():
        hits = sum(1 for kw in mood["keywords"]
                   if re.search(rf"\b{re.escape(kw)}(?:s|es|ed|ing|y)?\b", text))
        if hits:
            matched_any = True
            for g in mood["genres"]:
                targets = _match_genres(g, available_genres) if available_genres is not None else [g]
                for t in targets:
                    affinity[t] = affinity.get(t, 0) + hits
    return affinity, matched_any


def fuzzy_genre_fallback(text: str, tracks: pd.DataFrame) -> dict:
    """Match the text straight against genre names (whole words only)."""
    text_norm = _norm_text(text)
    affinity: dict = {}
    if not text_norm:
        return affinity
    padded = f" {text_norm} "
    words = set(text_norm.split())
    for genre in tracks["genre"].dropna().unique():
        for part in str(genre).split("/"):
            p = _norm_text(part)
            if not p:
                continue
            if f" {p} " in padded or p.replace(" ", "") in words:
                affinity[genre] = affinity.get(genre, 0) + 3
                break
    return affinity


def recommend_tracks(tracks: pd.DataFrame, request_text: str, selected_genres: list, limit: int = 7):
    pool = tracks.loc[tracks["recommender_ready"] & tracks["recommend_role"].ne("Leave Alone") & tracks["artist"].ne("Unknown Artist")].copy()
    lexicon = load_mood_lexicon()
    available = pool["genre"].dropna().unique()
    affinity, _ = score_genre_affinity(request_text, lexicon, available)
    for g, v in fuzzy_genre_fallback(request_text, pool).items():
        affinity[g] = affinity.get(g, 0) + v

    if selected_genres:
        narrowed = pool[pool["genre"].isin(selected_genres)]
        if not narrowed.empty:
            pool = narrowed.copy()

    text_lower = (request_text or "").lower().strip()
    text_norm = _norm_text(text_lower)
    padded = f" {text_norm} "
    tokens = {w for w in text_norm.split() if len(w) >= 4 and w not in _STOPWORDS}

    def text_boost(row) -> float:
        boost = 0.0
        if not text_norm:
            return boost
        artist = _norm_text(str(row.get("artist", "")))
        track = _norm_text(str(row.get("track", "")))
        if artist and f" {artist} " in padded:
            boost += 0.5
        if len(track) >= 3 and f" {track} " in padded:
            boost += 0.5
        if boost == 0 and tokens and tokens & set(f"{artist} {track}".split()):
            boost = 0.25
        return boost

    pool["genre_affinity"] = pool["genre"].map(lambda g: affinity.get(g, 0))
    max_affinity = max(affinity.values()) if affinity else 0
    pool["genre_affinity_norm"] = (pool["genre_affinity"] / max_affinity) if max_affinity else 0.0
    pool["text_boost"] = pool.apply(text_boost, axis=1)

    has_prompt_signal = bool(text_lower) and (max_affinity > 0 or pool["text_boost"].max() > 0)
    prompt_weight = 0.55 if has_prompt_signal else 0.0

    pool["final_score"] = (
        prompt_weight * (0.7 * pool["genre_affinity_norm"] + 0.3 * (pool["text_boost"] > 0).astype(float))
        + (1 - prompt_weight) * pool["recommend_score"]
        + pool["text_boost"]
    ).clip(lower=0)

    pool = pool.sort_values(["final_score", "valid_plays"], ascending=False).drop_duplicates(["track", "artist"])
    return pool.head(limit), has_prompt_signal


def _toggle_selection(item: str) -> None:
    sel = st.session_state.setdefault("my_selection", [])
    if item in sel:
        sel.remove(item)
    else:
        sel.append(item)


def _clear_selection() -> None:
    st.session_state["my_selection"] = []


def section_recommend(data: dict) -> None:
    tracks = data["recommend_candidates"]

    with st.container(key="player"):
        left, right = st.columns([0.45, 0.55])

        with left:
            st.subheader("What do you want to hear?")
            st.caption("You can search by artist, genre, or something else.")
            request_text = st.text_area("Your request", placeholder="a rainy night, a little dramatic",
                                         key="rec_request", height=90, label_visibility="collapsed")

            st.caption("Pick by Mood")
            quick = st.pills("Quick moods", QUICK_MOODS,
                              selection_mode="multi", key="quick_moods", label_visibility="collapsed")
            quick_text = " ".join(q.lower() for q in (quick or []))
            combined_text = f"{request_text or ''} {quick_text}".strip()

            genre_pool = set(tracks["genre"].dropna().unique())
            if "genre" in data["genres"].columns:
                genre_pool |= set(data["genres"]["genre"].dropna().unique())
            genre_options = sorted(g for g in genre_pool if g != "Unknown Genre")
            st.caption("Narrow the Genre")
            with st.container(height=230):
                chosen_genres = st.pills("Genres", genre_options, selection_mode="multi",
                                          key="rec_genres", label_visibility="collapsed")

            go = st.button("Get Recommendations ↗", type="primary", use_container_width=True)

        signature = (combined_text, tuple(sorted(chosen_genres or [])))
        if go or "rec_results" not in st.session_state or st.session_state.get("rec_signature") != signature:
            results, has_signal = recommend_tracks(tracks, combined_text, chosen_genres or [], limit=7)
            st.session_state["rec_results"] = results
            st.session_state["rec_request_display"] = combined_text
            st.session_state["rec_has_signal"] = has_signal
            st.session_state["rec_signature"] = signature

        results = st.session_state.get("rec_results", pd.DataFrame())
        request_display = st.session_state.get("rec_request_display", "")
        selection = st.session_state.setdefault("my_selection", [])

        with right:
            with st.container(key="player_screen"):
                st.subheader("Recommended Tracks")
                if request_display:
                    st.caption(f"Request: {request_display}")
                    if not st.session_state.get("rec_has_signal", False):
                        st.caption("No mood, genre, or artist match, so these are ranked by their revisit score.")

                for i, row in enumerate(results.itertuples(), start=1):
                    item = row.track_key
                    in_sel = item in selection
                    c1, c2, c3 = st.columns([0.12, 0.76, 0.12])
                    with c1:
                        color = PALETTE[(i - 1) % len(PALETTE)]
                        st.markdown(f'<div class="rank-chip" style="background:{color}">{i:02d}</div>', unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"**{_esc(row.track)}**<br><span class='muted'>{_esc(row.artist)} · {_esc(row.genre)}</span>",
                                    unsafe_allow_html=True)
                    with c3:
                        st.button("✓" if in_sel else "+", key=f"add_{i}_{row.track}_{row.artist}",
                                  help="Remove from selection" if in_sel else "Add to selection",
                                  on_click=_toggle_selection, args=(item,))

                if st.button("+ Add a track to your selection", key="manual_add_toggle"):
                    st.session_state["show_manual_add"] = not st.session_state.get("show_manual_add", False)

                if st.session_state.get("show_manual_add"):
                    manual_query = st.text_input("Search your library", key="manual_search")
                    if manual_query:
                        matches = tracks[
                            tracks["track"].str.contains(manual_query, case=False, na=False, regex=False)
                            | tracks["artist"].str.contains(manual_query, case=False, na=False, regex=False)
                        ].drop_duplicates(["track", "artist"]).head(5)
                        for row in matches.itertuples():
                            item = row.track_key
                            st.button(f"{'Remove' if item in selection else 'Add'} {row.track} — {row.artist}",
                                      key=f"manual_{row.track}_{row.artist}",
                                      on_click=_toggle_selection, args=(item,))

                if selection:
                    with st.expander(f"Your selection ({len(selection)})", expanded=True):
                        for i, item in enumerate(list(selection)):
                            c1, c2 = st.columns([0.86, 0.14])
                            with c1:
                                label = tracks.loc[tracks["track_key"].eq(item)].iloc[0]
                                st.write(f"• {label['track']} — {label['artist']}")
                            with c2:
                                st.button("✕", key=f"remove_{i}_{item}", help="Remove from selection",
                                          on_click=_toggle_selection, args=(item,))
                        st.button("Clear selection", key="clear_selection", on_click=_clear_selection)

                if selection:
                    neighbors = similar_to_selection(selection, data["recommendations"], tracks)
                    st.subheader("Similar to your selection")
                    for row in neighbors.itertuples(index=False):
                        st.markdown(f"**{_esc(row.track)}**<br><span class='muted'>{_esc(row.artist)} · {_esc(row.genre)}</span>", unsafe_allow_html=True)
                    if neighbors.empty:
                        st.caption("No eligible saved neighbors outside your selection.")
