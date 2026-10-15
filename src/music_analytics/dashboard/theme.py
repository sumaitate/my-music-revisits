"""Dashboard colors and static stylesheet."""
from pathlib import Path
import streamlit as st

COLORS = {'page': '#EDF8FF', 'page_soft': 'rgba(237, 248, 255, 0.88)', 'ink': '#17252D', 'black': '#101010', 'muted': '#244F82', 'select': '#8B1230', 'pink': '#F5A8CD', 'mint': '#A8E8CE', 'purple': '#C5ADFF', 'yellow': '#FFE28C', 'blue': '#A9D6F5', 'sky_soft': 'rgba(211, 235, 251, 0.78)', 'sky_shade': 'rgba(150, 196, 232, 0.50)', 'wash': 'rgba(252, 200, 226, 0.30)'}
PALETTE = [COLORS["purple"], COLORS["pink"], COLORS["yellow"], COLORS["mint"]]
CSS = Path(__file__).with_name("style.css").read_text(encoding="utf-8")


def style() -> None:
    st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)
