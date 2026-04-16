import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Sayfa Yapılandırması
st.set_page_config(page_title="Envanter Sistemi", layout="wide")
st.title("📦 Kesin Çözüm: Envanter Takibi")

# BAĞLANTI KURMA
# st.connection sadece 'gsheets' ismine bakar ve Secrets'ı otomatik tarar.
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Sayfa1", ttl=0)
    
    st.success("✅ Bağlantı Kuruldu!")
    
    # Veri Giriş Formu
    with st.sidebar:
        st.header("Veri Girişi")
        with st.form("kayit_formu", clear_on_submit=True):
            urun = st.text_input("Ürün Adı")
            adet = st.number_input("Adet", min_value=0)
            submit = st.form_submit_button("Kaydet")
            
            if submit and urun:
                yeni_veri = pd.DataFrame([{"Ürün Adı": urun, "Adet": adet}])
                guncel_df = pd.concat([df, yeni_veri], ignore_index=True)
                conn.update(worksheet="Sayfa1", data=guncel_df)
                st.rerun()

    # Veriyi Göster
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"❌ Hala Hata Var: {e}")
    st.info("Lütfen aşağıdaki Secrets adımlarını BİREBİR uygulayın.")
