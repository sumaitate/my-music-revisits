import streamlit as st
from music_analytics.dashboard.theme import style
from music_analytics.dashboard.data import load_data
from music_analytics.dashboard.common import pink_divider
from music_analytics.dashboard.overview import hero, section_overview
from music_analytics.dashboard.genres import section_genres
from music_analytics.dashboard.artists import section_artists
from music_analytics.dashboard.repeat import section_repeat
from music_analytics.dashboard.daily import section_daily
from music_analytics.dashboard.heatmap import section_heatmap
from music_analytics.dashboard.recommendations import section_recommend

st.set_page_config(page_title="My Music Revisits", page_icon="💿", layout="wide")

def main() -> None:
    style()
    data = load_data()
    hero()
    pink_divider()

    tab1, tab2 = st.tabs(["01. MY MUSIC BREAKDOWN", "02. GET A RECOMMENDATION"])

    with tab1:
        left, right = st.columns([0.36, 0.64], gap="medium")

        with left:
            with st.container(key="panel_overview"):
                section_overview(data)
            with st.container(key="panel_genres"):
                section_genres(data)

        with right:
            with st.container(key="panel_artists"):
                section_artists(data)
            with st.container(key="panel_repeat"):
                section_repeat(data)
            with st.container(key="panel_daily"):
                section_daily(data)
            with st.container(key="panel_heatmap"):
                section_heatmap(data)

    with tab2:
        section_recommend(data)


if __name__ == "__main__":
    main()