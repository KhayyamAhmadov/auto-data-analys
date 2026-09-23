import time
import streamlit as st
from web.core.data_utils import greeting
from web.core.ui import icon, spacer

FEATURES = [
    ("folder_open", "blue", "Məlumatlarınızı idarə edin", "CSV, Excel və JSON fayllarını bir yerdən yükləyin."),
    ("cleaning_services", "green", "Data keyfiyyətini yoxlayın", "Boş dəyərləri, dublikatları və sütun tiplərini müəyyən edin."),
    ("insights", "violet", "Məlumatlarınızı analiz edin", "Statistik göstəriciləri və əsas məlumat nümunələrini kəşf edin."),
    ("description", "orange", "Nəticələrinizi əldə edin", "Analiz nəticələrini strukturlaşdırılmış hesabat kimi yükləyin.")]

spacer("large")

left, right = st.columns([1.2, 1], gap="large", vertical_alignment="center")


with left:
    st.title(":blue[maybeData?]", anchor=False)
    st.markdown("##### Datanı yüklə, yoxla, anla")
    st.caption(
        "Datanızı yükləyin, analiz prosesini sadələşdirin və "
        "əsas nəticələri bir platformada kəşf edin.")
    spacer("medium")

    for icon_name, color, title, text in FEATURES:
        icon_col, text_col = st.columns([1, 11], gap="small", vertical_alignment="center")
        with icon_col:
            st.markdown(f"### {icon(icon_name, color)}")
        with text_col:
            st.markdown(f"**{title}**")
            st.caption(text)


with right:
    with st.container(border=True):
        spacer()
        _, img_center, _ = st.columns([1, 2, 1])
        with img_center:
            st.image("art/KvlDt.jpg", width=200)

        st.subheader(greeting(), anchor=False)
        st.caption("Hesabınıza daxil olun.")

        with st.form("login_form", border=False):
            name = st.text_input("Nickname", placeholder="Adınız")
            password = st.text_input("Password", type="password", placeholder="Şifrənizi daxil edin")
            spacer()
            submitted = st.form_submit_button("Daxil ol", type="primary", width="stretch")

        if submitted:
            clean_name = name.strip()

            if not clean_name or not password:
                st.error("Bütün sahələri doldurun.")

            elif password == "123":
                st.session_state["name"] = clean_name
                st.session_state["logged_in"] = True

                st.success("Giriş uğurlu oldu.")
                with st.spinner("Ana səhifəyə yönləndirilir..."):
                    time.sleep(1)
                st.rerun()

            else:
                st.error("Şifrə yanlışdır.")
