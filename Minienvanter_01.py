import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Bulut Envanter", layout="wide")

st.title("☁️ Bulut Tabanlı Stok Mutabakatı")

# Google Sheets Bağlantısı
# Not: .streamlit/secrets.toml dosyasına linki eklemelisin
conn = st.connection("gsheets", type=GSheetsConnection)

# Mevcut veriyi oku
df = conn.read(worksheet="Sayfa1")

# GİRİŞ FORMU
with st.sidebar:
    st.header("Yeni Hareket Gir")
    with st.form("input_form"):
        urun = st.text_input("Ürün Adı")
        baslangic = st.number_input("Başlangıç", value=0)
        gelen = st.number_input("Gelen", value=0)
        satan = st.number_input("Satılan", value=0)
        t_gelen = st.number_input("Trf Gelen", value=0)
        t_giden = st.number_input("Trf Giden", value=0)
        yerinde_olan = st.number_input("Yerinde Olan", value=0)
        ekle = st.form_submit_button("Kaydet")

if ekle and urun:
    # Hesaplamalar
    olmasi_gereken = (baslangic + gelen + t_gelen) - (satan + t_giden)
    fark = yerinde_olan - olmasi_gereken
    
    # Yeni satırı hazırla
    yeni_veri = pd.DataFrame([{
        "Ürün Adı": urun,
        "Başlangıç": baslangic,
        "Gelen": gelen,
        "Satan": satan,
        "Trf Gelen": t_gelen,
        "Trf Giden": t_giden,
        "Yerinde Olan": yerinde_olan,
        "Olması Gereken": olmasi_gereken,
        "Fark": fark
    }])
    
    # Mevcut veriye ekle ve Google Sheets'e yaz
    df = pd.concat([df, yeni_veri], ignore_index=True)
    conn.update(worksheet="Sayfa1", data=df)
    st.success("Veri başarıyla buluta kaydedildi!")
    st.rerun()

# TABLOYU GÖSTER
if not df.empty:
    st.subheader("📊 Güncel Stok Durumu (Canlı Veri)")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Henüz kayıtlı veri yok.")