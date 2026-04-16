import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Envanter Yönetimi", layout="wide", page_icon="📦")

st.title("📦 Canlı Envanter Takibi")

# 2. BAĞLANTI KURMA
# st.connection, Secrets içindeki [connections.gsheets] başlığını otomatik okur.
def baglanti_kur():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Veriyi çek
        df = conn.read(worksheet="Sayfa1", ttl=0)
        return conn, df
    except Exception as e:
        st.error(f"⚠️ Bağlantı Hatası: {e}")
        st.info("Lütfen Secrets ayarlarındaki formatı ve Google Sheet paylaşım iznini kontrol edin.")
        return None, pd.DataFrame()

conn, df = baglanti_kur()

# 3. VERİ GİRİŞ PANELİ (SOL TARAF)
with st.sidebar:
    st.header("📊 Hareket Girişi")
    with st.form("envanter_form", clear_on_submit=True):
        urun = st.text_input("Ürün Adı")
        col1, col2 = st.columns(2)
        with col1:
            baslangic = st.number_input("Başlangıç", min_value=0)
            gelen = st.number_input("Gelen (+)", min_value=0)
            t_gelen = st.number_input("Trf Gelen (+)", min_value=0)
        with col2:
            satan = st.number_input("Satan (-)", min_value=0)
            t_giden = st.number_input("Trf Giden (-)", min_value=0)
            sayim = st.number_input("Yerinde (Fiziksel)", min_value=0)
        
        submit = st.form_submit_button("Kaydet ve Gönder")

# 4. KAYIT İŞLEMİ
if submit and urun and conn is not None:
    beklenen = (baslangic + gelen + t_gelen) - (satan + t_giden)
    fark = sayim - beklenen
    
    yeni_satir = pd.DataFrame([{
        "Ürün Adı": urun,
        "Başlangıç": baslangic,
        "Gelen": gelen,
        "Satan": satan,
        "Trf Gelen": t_gelen,
        "Trf Giden": t_giden,
        "Yerinde Olan": sayim,
        "Olması Gereken": beklenen,
        "Fark": fark
    }])
    
    # Mevcut tabloyla birleştir
    guncel_df = pd.concat([df, yeni_satir], ignore_index=True) if not df.empty else yeni_satir
    
    try:
        conn.update(worksheet="Sayfa1", data=guncel_df)
        st.success(f"✅ {urun} kaydedildi!")
        st.rerun()
    except Exception as e:
        st.error(f"Güncelleme hatası: {e}")

# 5. TABLO GÖSTERİMİ
if not df.empty:
    st.subheader("📋 Güncel Liste")
    st.dataframe(df, use_container_width=True, hide_index=True)
