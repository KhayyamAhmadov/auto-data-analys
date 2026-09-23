from __future__ import annotations
import hashlib
import streamlit as st
from web.core.data_utils import NamedBytesIO
from data_load.load_file import load_file

DEFAULTS = {
    "logged_in": False,
    "name": "User",
    # dataset
    "dataset_name": None,
    "dataset_bytes": None,
    "dataset_hash": None,
    "df": None,
    "uploader_key": 0,
    # analiz və hesabat
    "analysis_done": False,
    "analysis_result": None,
    "reports_count": 0}


def init_state() -> None:
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)


def has_dataset() -> bool:
    return st.session_state.get("df") is not None


def set_dataset(uploaded) -> bool:
    data = uploaded.getvalue()
    digest = hashlib.sha1(data).hexdigest()

    if st.session_state["dataset_hash"] == digest:
        return True

    try:
        df = load_file(NamedBytesIO(data, uploaded.name))
    except Exception as exc:
        st.error(f"✕ Fayl oxunmadı: {exc}")
        return False

    st.session_state.update(
        dataset_name=uploaded.name,
        dataset_bytes=data,
        dataset_hash=digest,
        df=df,
        analysis_done=False,
        analysis_result=None,)
    return True


def clear_dataset() -> None:
    st.session_state.update(
        dataset_name=None,
        dataset_bytes=None,
        dataset_hash=None,
        df=None,
        analysis_done=False,
        analysis_result=None,
        uploader_key=st.session_state["uploader_key"] + 1)


def get_file() -> NamedBytesIO:
    return NamedBytesIO(
        st.session_state["dataset_bytes"],
        st.session_state["dataset_name"])


def logout() -> None:
    clear_dataset()
    st.session_state["reports_count"] = 0
    st.session_state["logged_in"] = False
    st.rerun()
