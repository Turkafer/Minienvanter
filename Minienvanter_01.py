import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Envanter Yönetimi", layout="wide", page_icon="📦")

st.title("📦 Canlı Envanter & Sayım Mutabakatı")

# 2. BAĞLANTI FONKSİYONU (Hata Temizleyici İçerir)
def baglanti_kur():
    try:
        # Secrets yapısını kontrol et
        if "connections" not in st.secrets or "gsheets" not in st.secrets.connections:
            st.error("❌ Secrets ayarları eksik! [connections.gsheets] başlığını kontrol et.")
            return None, pd.DataFrame()

        # Anahtarı çek ve PEM formatı hatalarını (InvalidByte) temizle
        raw_key = st.secrets["connections"]["gsheets"]["private_key"]
        
        # Olası hatalı karakterleri temizleme işlemi
        cleaned_key = raw_key.replace("\\n", "\n")
        if not cleaned_key.startswith("-----BEGIN PRIVATE KEY-----"):
            cleaned_key = "-----BEGIN PRIVATE KEY-----\n" + cleaned_key
        if not cleaned_key.endswith("-----END PRIVATE KEY-----"):
            cleaned_key = cleaned_key + "\n-----END PRIVATE KEY-----"
            
        # Temizlenen anahtarı geçici olarak sisteme tanıt
        # Bu işlem 'Unable to load PEM file' hatasını engeller
        st.secrets.connections.gsheets.private_key = cleaned_key

        conn = st.connection("gsheets", type=GSheetsConnection)
        # Veriyi çek (Sayfa1 ismini kontrol et)
        df = conn.read(worksheet="Sayfa1", ttl=0)
        return conn, df
    except Exception as e:
        st.error(f"⚠️ Bağlantı Hatası: {e}")
        return None, pd.DataFrame()

# Bağlantıyı başlat
conn, df = baglanti_kur()

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
            satan = st.number_input("S
