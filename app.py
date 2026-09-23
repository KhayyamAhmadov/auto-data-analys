import streamlit as st
from web.core.state import init_state, logout
from web.core.ui import badge


st.set_page_config(
    page_title="maybeData?",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_state()
st.logo("art/KvlDt.jpg", size="large")


def build_navigation(pages, position):
    try:
        return st.navigation(pages, position=position)
    except TypeError:
        # Köhnə Streamlit versiyalarında position parametri yoxdur
        return st.navigation(pages)


if not st.session_state["logged_in"]:
    login_page = st.Page("web/views/login.py", title="Login", icon=":material/lock:", default=True)
    build_navigation([login_page], "hidden").run()
    st.stop()


def render_topbar() -> None:
    brand, status, user, logout_col = st.columns([1.5, 4.5, 1.6, 1.2], vertical_alignment="center")

    with brand:
        st.markdown(":blue[**maybeData?**]")

    with status:
        dataset_name = st.session_state.get("dataset_name")
        dataset_badge = (
            badge(f"Dataset: {dataset_name}", "green", ":material/database:")
            if dataset_name
            else badge("Dataset yoxdur", "gray", ":material/database:")
        )
        analysis_badge = (
            badge("Analiz hazırdır", "green", ":material/check_circle:")
            if st.session_state.get("analysis_done")
            else badge("Analiz yoxdur", "gray", ":material/schedule:")
        )
        st.markdown(f"{dataset_badge} {analysis_badge}")

    with user:
        st.markdown(badge(st.session_state["name"], "blue", ":material/person:"))

    with logout_col:
        if st.button("Çıxış", icon=":material/logout:", type="tertiary", width="stretch"):
            logout()


def render_nav(pages) -> None:
    """Səhifə keçidlərini ortada göstərir (yalnız Streamlit komponentləri ilə)."""
    try:
        row = st.container(horizontal=True, horizontal_alignment="center", gap="large")
    except TypeError:
        # Köhnə versiyalar: sütunlarla ortalama
        cols = st.columns([2, 1, 1, 1, 2])
        for col, page in zip(cols[1:4], pages):
            with col:
                st.page_link(page)
        return

    with row:
        for page in pages:
            st.page_link(page)


pages = [
    st.Page("web/views/home.py", title="Home", icon=":material/home:", default=True),
    st.Page("web/views/datasets.py", title="Datasets", icon=":material/folder_open:"),
    st.Page("web/views/analysis.py", title="Analysis", icon=":material/insights:"),
]

# Standart naviqasiya gizlədilir, keçidləri render_nav() ortada göstərir
current_page = build_navigation(pages, "hidden")

render_topbar()
render_nav(pages)
st.divider()
current_page.run()

st.divider()
st.caption("maybeData?")
