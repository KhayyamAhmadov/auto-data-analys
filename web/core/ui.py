from __future__ import annotations

import streamlit as st

STEP_COLORS = ["blue", "green", "orange"]


def spacer(size: str = "small") -> None:
    """Elementlər arası boşluq (köhnə versiyalarda boş sətir)."""
    if hasattr(st, "space"):
        st.space(size)
    else:
        st.write("")


def centered(**kwargs):
    try:
        return st.container(horizontal_alignment="center", **kwargs)
    except TypeError:
        return st.container(**kwargs)


def icon(name: str, color: str = "blue") -> str:
    return f":{color}[:material/{name}:]"


def badge(label, color: str = "gray", icon: str = "") -> str:
    safe = str(label).replace("[", "(").replace("]", ")")
    prefix = f"{icon} " if icon else ""
    return f":{color}-badge[{prefix}{safe}]"


def page_header(title: str, description: str = "") -> None:
    st.title(title, anchor=False)
    if description:
        st.caption(description)
    spacer()


def section(title: str, subtitle: str = "", color: str = "blue") -> None:
    spacer("medium")
    st.subheader(title, anchor=False, divider=color)
    if subtitle:
        st.caption(subtitle)


def stats_row(items: list[tuple]) -> None:
    with st.container(border=True):
        cols = st.columns(len(items))
        for col, (icon_name, color, title, value, description) in zip(cols, items):
            with col:
                st.metric(f"{icon(icon_name, color)} {title}", value)
                st.caption(description)


def steps_row(steps: list[tuple]) -> None:
    with st.container(border=True):
        cols = st.columns(len(steps), gap="large")
        for number, (col, (title, text)) in enumerate(zip(cols, steps), start=1):
            color = STEP_COLORS[(number - 1) % len(STEP_COLORS)]
            with col:
                st.markdown(f"#### :{color}[{number}.] {title}")
                st.caption(text)


def feature_card(icon_name: str, title: str, text: str, color: str = "blue", height: int | None = 160) -> None:
    with st.container(border=True, height=height):
        st.markdown(f"#### {icon(icon_name, color)} {title}")
        st.caption(text)


def empty_state(icon_name: str, title: str, text: str, color: str = "blue") -> None:
    with centered(border=True):
        spacer("medium")
        st.markdown(f"## {icon(icon_name, color)}")
        st.markdown(f"**{title}**")
        st.caption(text)
        spacer("medium")


def cta_band(title: str, text: str, button_label: str, target: str, key: str, button_icon: str = "") -> None:
    with st.container(border=True):
        left, right = st.columns([4, 1], vertical_alignment="center")
        with left:
            st.markdown(f"### :blue[{title}]")
            st.caption(text)
        with right:
            if st.button(button_label, icon=button_icon or None, type="primary", width="stretch", key=key):
                st.switch_page(target)
