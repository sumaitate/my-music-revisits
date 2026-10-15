import plotly.express as px
import streamlit as st
from music_analytics.config import TZ_LABEL, WEEKDAYS, BUCKETS, BUCKET_LABELS
from music_analytics.dashboard.theme import COLORS
from music_analytics.dashboard.common import info_card, style_axes


def section_heatmap(data: dict) -> None:
    st.markdown('<div class="eyebrow">LISTENING TIMES</div>', unsafe_allow_html=True)
    st.subheader("When I Listen")
    st.caption("Click a circle to inspect listening by weekday and time. Larger circles mean more minutes per calendar weekday.")

    heat = data["heatmap"]
    fig = px.scatter(
        heat, x="bucket", y="weekday", size="avg_minutes", color="avg_minutes",
        category_orders={"bucket": BUCKETS, "weekday": list(reversed(WEEKDAYS))},
        color_continuous_scale=[[0, COLORS["mint"]], [1, COLORS["pink"]]],
        size_max=22,
        hover_data=["minutes", "valid_plays", "tracks", "top_artists", "top_day_share"],
    )
    fig.update_traces(marker=dict(line=dict(color=COLORS["ink"], width=1)))
    fig.update_layout(height=280, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                       coloraxis_showscale=False)
    style_axes(fig, f"Time of Day ({TZ_LABEL})", "Weekday")
    # Time buckets like "00-04" are text, not dates: force category axes so plotly doesn't read them as years
    fig.update_xaxes(type="category", categoryorder="array", categoryarray=BUCKETS)
    fig.update_yaxes(type="category")
    if set(heat["bucket"]).issubset(set(BUCKETS)):
        fig.update_xaxes(tickmode="array", tickvals=BUCKETS, ticktext=[BUCKET_LABELS[b] for b in BUCKETS])
    event = st.plotly_chart(fig, on_select="rerun", selection_mode="points", key="heatmap")

    if event and event.selection and event.selection.points:
        point = event.selection.points[0]
        row = heat.iloc[int(point["point_index"])]
        bits = [f"{row['avg_minutes']:.1f} minutes per weekday", f"{row['minutes']:.1f} minutes total", f"{row['top_day_share']:.1%} from the largest date", f"{int(row['valid_plays'])} plays (30s+)"]
        bits.append(f"{int(row['tracks'])} tracks")
        lines = [" · ".join(bits)]
        if row["top_artists"]:
            lines.append(f"Most-played artists: {row['top_artists']}")
        info_card(f"{row['weekday']}, {BUCKET_LABELS.get(row['bucket'], row['bucket'])} {TZ_LABEL}", lines)
