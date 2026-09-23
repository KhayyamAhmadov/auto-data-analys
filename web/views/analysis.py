from pathlib import Path
import streamlit as st
from web.core.ui import empty_state, page_header, section, spacer
from web.core.data_utils import quality_summary, show_pdf
from web.core.state import get_file, has_dataset
from web.core.email import send_analysis_email

page_header("Analysis", "Datasetinizi analiz edin və nəticələrə baxın.")


def start_analysis() -> bool:
    try:
        from main import run_analysis
        from analys.report import ReportGenerator

        with st.spinner("Data analiz edilir..."):
            result = run_analysis(get_file())
            generator = ReportGenerator()
            pdf_path = generator.create_report(
                result["profile"],
                result["cleaning"],
                result["eda"],
                result["charts"],
                result["findings"])

    except Exception as exc:
        st.error(f"Analiz zamanı xəta baş verdi:\n\n{exc}")
        return False

    st.session_state["analysis_result"] = result
    st.session_state["pdf_path"] = pdf_path
    st.session_state["analysis_done"] = True
    return True


if not has_dataset():
    empty_state("folder_open", "Dataset yoxdur", "Əvvəlcə Datasets bölməsindən dataset yükləyin.", "violet")
    spacer()
    if st.button("Datasets bölməsinə keç", icon=":material/folder_open:", type="primary"):
        st.switch_page("web/views/datasets.py")
    st.stop()


df = st.session_state["df"]
summary = quality_summary(df)


with st.container(border=True):
    info_col, button_col = st.columns([3, 1], vertical_alignment="center")

    with info_col:
        st.markdown(f":blue[:material/description:] **{st.session_state['dataset_name']}**")
        st.caption(f"{summary['rows']:,} sətir, {summary['columns']} sütun")

    with button_col:
        start_clicked = st.button("Start Analysis", icon=":material/play_arrow:", type="primary", width="stretch")

if start_clicked and start_analysis():
    st.session_state["analysis_flash"] = True
    st.rerun()

if st.session_state.pop("analysis_flash", False):
    spacer()
    st.success("Data analizi uğurla tamamlandı.", icon=":material/check_circle:")


if not st.session_state["analysis_done"]:
    spacer()
    st.info("Nəticələri görmək üçün analizi başladın.", icon=":material/info:")
    st.stop()



section("Analysis Results", color="green")

pdf_path = st.session_state.get("pdf_path")

if pdf_path:
    with st.container(border=True):
        title_col, download_col = st.columns([3, 1], vertical_alignment="center")

        with title_col:
            st.markdown(":orange[:material/picture_as_pdf:] **PDF Report**")
            st.caption("Hesabatı burada oxuyun və ya kompüterinizə yükləyin.")

        with download_col:
            pdf_file = Path(pdf_path)
            if pdf_file.exists():
                st.download_button("PDF yüklə", icon=":material/download:", data=pdf_file.read_bytes(), file_name=pdf_file.name,  mime="application/pdf", type="primary", width="stretch")

        show_pdf(pdf_path)         



    section("Send Report", color="blue")
    with st.container(border=True):

        st.markdown(":material/mail: **PDF hesabatını email ilə göndər**")
        st.caption("Analiz nəticələri və PDF report göstərdiyiniz " "email ünvanına göndəriləcək.")
        receiver_email = st.text_input("Email address", placeholder="example@gmail.com")
        send_email = st.button("Send Report", icon=":material/send:", type="primary", width="stretch")
        if send_email:
            if not receiver_email:
                st.warning("Zəhmət olmasa email ünvanını daxil edin.")
            else:
                result = st.session_state["analysis_result"]
                try:
                    with st.spinner("Email göndərilir..."):

                        send_analysis_email(receiver_email=receiver_email, pdf_path=pdf_path, dataset_name=st.session_state["dataset_name"])

                    st.success("PDF hesabatı email ilə göndərildi.",icon=":material/check_circle:")

                except Exception as exc:
                    st.error(f"Email göndərilərkən xəta baş verdi:\n\n{exc}")