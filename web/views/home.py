import streamlit as st
from web.core.ui import cta_band, feature_card, section, spacer, stats_row, steps_row
from web.core.state import has_dataset

name = st.session_state["name"]


with st.container(border=True):
    spacer()
    text_col, _ = st.columns([3, 2])

    with text_col:
        st.title(f"Salam, {name}", anchor=False)
        st.subheader(":blue[Datanızı bir neçə kliklə analiz edin.]", anchor=False)
        st.markdown(
            ":gray[CSV, Excel və ya JSON faylınızı yükləyin, keyfiyyətini yoxlayın, "
            "statistikaya baxın və nəticəni hesabat kimi yükləyin.]")
        st.markdown(
            ":blue-badge[:material/table_chart: CSV] "
            ":green-badge[:material/grid_on: Excel] "
            ":orange-badge[:material/data_object: JSON]")
        spacer()

        upload_col, analysis_col, _ = st.columns([1.2, 1.2, 1], gap="small")
        with upload_col:
            if st.button("Dataset yüklə", icon=":material/upload_file:", type="primary",
                         width="stretch", key="hero_upload"):
                st.switch_page("web/views/datasets.py")
        with analysis_col:
            if st.button("Analizə keç", icon=":material/insights:", width="stretch",
                         disabled=not has_dataset(), key="hero_analysis"):
                st.switch_page("web/views/analysis.py")
    spacer()


section("Cari vəziyyət", "Bu sessiyada nə hazırdır.", color="blue")
stats_row([
    ("database", "blue", "Datasets", 1 if has_dataset() else 0, "Yüklənmiş dataset"),
    ("insights", "violet", "Analyses", 1 if st.session_state["analysis_done"] else 0, "Tamamlanmış analiz"),
    ("picture_as_pdf", "orange", "Reports", st.session_state["reports_count"], "Yüklənmiş hesabat"),
    ("bolt", "green", "Status", "Ready", "Sistem statusu")])


section("Necə işləyir", "Üç addımda datadan nəticəyə.", color="green")
steps_row([
    ("Yüklə", "CSV, Excel və ya JSON faylını Datasets bölməsində seçin."),
    ("Analiz et", "Struktur, keyfiyyət və statistikanı Analysis bölməsində görün."),
    ("Hesabat al", "Nəticələri Analysis bölməsindən PDF hesabat kimi yükləyin."),])



section("Platforma imkanları", color="violet")
f1, f2, f3, f4 = st.columns(4)
with f1:
    feature_card("analytics", "Data Analysis", "Dataset haqqında ümumi məlumat, sütunlar və məlumat strukturu.", "blue")
with f2:
    feature_card("cleaning_services", "Data Cleaning", "Boş dəyərlər, dublikatlar və data type yoxlaması.", "green")
with f3:
    feature_card("show_chart", "Statistics", "Mean, median, standart sapma, korrelyasiya və digər göstəricilər.", "violet")
with f4:
    feature_card("picture_as_pdf", "Reports", "Analiz nəticələrini PDF formatında yükləyin.", "orange")


spacer("medium")
cta_band("Başlamağa hazırsınız?", "İlk datasetinizi yükləyin — analiz bir kliklə başlayır.", "Başla", "web/views/datasets.py", key="cta_band_start", button_icon=":material/arrow_forward:")
