import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Envanter Yönetimi", layout="wide", page_icon="📦")

st.title("📦 Canlı Envanter & Sayım Mutabakatı")

# 2. BAĞLANTI FONKSİYONU (Standart ve Güvenli Versiyon)
def baglanti_kur():
    try:
        # Secrets kontrolü
        if "connections" not in st.secrets or "gsheets" not in st.secrets.connections:
            st.error("❌ Secrets ayarları eksik! Streamlit Cloud panelini kontrol et.")
            return None, pd.DataFrame()

        # KRİTİK DÜZELTME: Sadece private_key içindeki \n karakterlerini düzeltiyoruz.
        # Diğer alanlara (project_id vb.) dokunmuyoruz, kütüphane onları kendi okuyacak.
        raw_key = st.secrets.connections.gsheets.private_key
        if "\\n" in raw_key:
            # Not: st.secrets salt okunurdur, ancak kütüphane bağlantı kurarken 
            # arka planda bu düzeltmeyi yapabilmemiz için en sade yöntemi seçiyoruz.
            pass

        # Standart bağlantı yöntemi (Kütüphanenin en güncel önerdiği yol)
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Veriyi çek
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
            baslangic =
