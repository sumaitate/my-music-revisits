import html
import streamlit as st
from music_analytics.dashboard.theme import COLORS


def _esc(value) -> str:
    """HTML-escape text (and `$`, which markdown can mistake for math)."""
    return html.escape(str(value)).replace("$", "&#36;")


def metric(label: str, value: str, sub: str | None = None) -> str:
    """Returns one tile's HTML; tiles are rendered together inside .metric-grid."""
    sub_html = f'<span class="metric-sub">{_esc(sub)}</span>' if sub else ""
    return f'<div class="metric"><span class="muted">{_esc(label)}</span><strong>{_esc(value)}</strong>{sub_html}</div>'


def info_card(title: str, lines: list) -> None:
    """Soft pink detail card: bold black title with info lines underneath."""
    body = "".join(f'<div class="info-line">{_esc(line)}</div>' for line in lines if line)
    st.markdown(
        f'<div class="info-wrap"><div class="info-card">'
        f'<div class="info-title">{_esc(title)}</div>{body}'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def pink_divider() -> None:
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


def style_axes(fig, x_title: str, y_title: str) -> None:
    """Bold, high-contrast axes with clear titles."""
    ink = COLORS["ink"]
    axis = dict(
        showline=True, linecolor=ink, linewidth=2,
        gridcolor="#BCD0E8", zeroline=False,
        ticks="outside", tickcolor=ink,
        tickfont=dict(size=13, color=ink),
        automargin=True,
    )
    fig.update_xaxes(title_text=f"<b>{x_title}</b>", title_font=dict(size=14, color=ink), **axis)
    fig.update_yaxes(title_text=f"<b>{y_title}</b>", title_font=dict(size=14, color=ink), **axis)
    fig.update_xaxes(tickfont=dict(weight="bold"))
    fig.update_yaxes(tickfont=dict(weight="bold"))
    fig.update_layout(font=dict(color=ink), margin=dict(l=10, r=10, t=10, b=10))
