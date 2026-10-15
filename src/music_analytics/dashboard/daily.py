import pandas as pd
import plotly.express as px
import streamlit as st
from music_analytics.dashboard.theme import COLORS
from music_analytics.dashboard.common import info_card, style_axes


def section_daily(data: dict) -> None:
    days = data["days"]
    st.markdown('<div class="eyebrow">DAILY LISTENING</div>', unsafe_allow_html=True)
    st.subheader("Minutes Listened per Day")
    st.caption("Click any dot to see how many tracks I played that day and which artists I played most.")

    plot_days = days.copy()
    plot_days["date"] = pd.to_datetime(plot_days["date"])
    fig = px.scatter(
        plot_days, x="date", y="minutes", size="minutes", color="minutes",
        hover_data=["plays", "valid_plays", "tracks", "top_artist", "top_genre"],
        color_continuous_scale=[[0, COLORS["mint"]], [.7, COLORS["yellow"]], [1, COLORS["pink"]]],
        size_max=14,
    )
    fig.update_layout(height=260, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
    style_axes(fig, "Date", "Minutes Listened")
    fig.update_xaxes(type="date", tickformat="%b %d", hoverformat="%b %d, %Y")
    fig.update_yaxes(rangemode="tozero")
    event = st.plotly_chart(fig, on_select="rerun", selection_mode="points", key="daily_pulse")

    if event and event.selection and event.selection.points:
        point = event.selection.points[0]
        day = plot_days.iloc[int(point["point_index"])]
        info_card(
            f"{day['date']:%b %d, %Y}",
            [f"{day['minutes']:.1f} minutes · {day['tracks']} tracks · {day['plays']} events",
             f"Top artist: {day['top_artist']}",
             f"Top genre: {day['top_genre']}"],
        )
