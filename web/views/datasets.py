import pandas as pd
import streamlit as st
from web.core.ui import empty_state, page_header, spacer, stats_row
from web.core.data_utils import quality_summary, format_bytes
from web.core.state import clear_dataset, has_dataset, set_dataset

page_header("Datasets", "Datasetinizi yükləyin və məlumatlarınıza baxın.")


with st.container(border=True):
    st.markdown(":blue[:material/upload_file:] **Dataset yüklə**")
    st.caption("CSV, Excel (xlsx, xls) və JSON faylları dəstəklənir.")

    uploaded = st.file_uploader("Dataset seçin", type=["csv", "xlsx", "xls", "json"], label_visibility="collapsed", key=f"uploader_{st.session_state['uploader_key']}")
    if uploaded is not None:
        set_dataset(uploaded)


if not has_dataset():
    spacer()
    empty_state("folder_open", "Hələ dataset yüklənməyib", "Yuxarıdakı sahəyə CSV, Excel və ya JSON faylı atın.", "violet")
    st.stop()


df = st.session_state["df"]
summary = quality_summary(df)
df_name = st.session_state["dataset_name"]



spacer()
with st.container(border=True):
    info_col, action_col1, action_col2 = st.columns([4, 1.5, 1.2], vertical_alignment="center")
    with info_col:
        st.markdown(f":blue[:material/description:] **{df_name}**")
        st.caption(f"{summary['rows']:,} sətir, {summary['columns']} sütun")
    with action_col1:
        if st.button("Analizə keç", icon=":material/insights:", type="primary", width="stretch"):
            st.switch_page("web/views/analysis.py")
    with action_col2:
        if st.button("Sil", icon=":material/delete:", width="stretch"):
            clear_dataset()
            st.rerun()


spacer()
stats_row([
    ("table_rows", "blue", "Sətir sayı", f"{summary['rows']:,}", "Dataset üzrə"),
    ("view_column", "violet", "Sütun sayı", summary["columns"], "Dataset üzrə"),
    ("memory", "green", "Tutduğu yaddaş", format_bytes(summary["memory_bytes"]), "B, KB, MB, GB"),])


spacer("medium")
tab_preview = st.tabs([":blue[:material/table_view:] Preview"])[0]

with tab_preview:
    max_rows = min(100, max(summary["rows"], 1))
    default_rows = min(20, max_rows)
    if max_rows > 5:
        rows_to_show = st.slider("Göstəriləcək sətir sayı", 5, max_rows, default_rows)
    else:
        rows_to_show = max_rows
    st.dataframe(df.head(rows_to_show), width="stretch")
    st.caption(f"Ümumi sətir sayı: {summary['rows']:,}")