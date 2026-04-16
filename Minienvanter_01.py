import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Envanter Yönetimi", layout="wide", page_icon="📦")

# Uygulama Başlığı
st.title("📦 Canlı Envanter & Sayım Mutabakatı")
st.markdown("Google Sheets ile senkronize çalışır.")

# 2. GOOGLE SHEETS BAĞLANTISI
# Bu kısım Secrets'taki [connections.gsheets] bilgilerini kullanır
conn = st.connection("gsheets", type=GSheetsConnection)

def verileri_cek():
    try:
        # ttl=0 verinin her seferinde taze gelmesini sağlar (önbelleğe almaz)
        return conn.read(worksheet="Sayfa1", ttl=0)
    except Exception as e:
        st.error(f"Bağlantı Kurulamadı! Detay: {e}")
        return pd.DataFrame()

df = verileri_cek()

# 3. VERİ GİRİŞ PANELİ (SOL TARAF)
with st.sidebar:
    st.header("📊 Hareket Girişi")
    with st.form("envanter_formu", clear_on_submit=True):
        urun_adi = st.text_input("Ürün Adı")
        
        col1, col2 = st.columns(2)
        with col1:
            baslangic = st.number_input("Başlangıç", min_value=0, value=0)
            gelen = st.number_input("Gelen (+)", min_value=0, value=0)
            t_gelen = st.number_input("Transfer Gelen (+)", min_value=0, value=0)
        with col2:
            satan = st.number_input("Satan (-)", min_value=0, value=0)
            t_giden = st.number_input("Transfer Giden (-)", min_value=0, value=0)
            yerinde_olan = st.number_input("Yerinde (Fiziksel)", min_value=0, value=0)
        
        submit = st.form_submit_button("Veriyi Kaydet ve Gönder")

# 4. KAYIT İŞLEMİ
if submit and urun_adi:
    # Matematiksel Hesaplama
    olmasi_gereken = (baslangic + gelen + t_gelen) - (satan + t_giden)
    fark = yerinde_olan - olmasi_gereken
