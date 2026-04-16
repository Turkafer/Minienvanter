import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Bulut Envanter", layout="wide")

st.title("☁️ Bulut Tabanlı Stok Mutabakatı")

# Google Sheets Bağlantısı
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
except Exception as e:
    st.error("Bağlantı Kurulamadı! Lütfen Secrets (URL) ayarlarını kontrol et.")
    df = pd.DataFrame()

# GİRİŞ FORMU (Yan Panel)
with st.sidebar:
    st.header("Yeni Hareket Gir")
    with st.form("input_form"):
        urun = st.text_input("Ürün Adı")
        baslangic = st.number_input("Eldeki Devir (Başlangıç)", value=0)
        gelen = st.number_input("Gelen Ürün", value=0)
        satan = st.number_input("Satılan Ürün", value=0)
        t_gelen = st.number_input("Transfer Gelen (+)", value=0)
        t_giden = st.number_input("Transfer Giden (-)", value=0)
        yerinde_olan = st.number_input("Yerinde Olan (Sayım)", value=0)
        ekle = st.form_submit_button("Kaydet ve Buluta Gönder")

if ekle and urun:
    # Matematiksel Hesaplama
    olmasi_gereken = (baslangic + gelen + t_gelen) - (satan + t_giden)
    fark = yerinde_olan - olmasi_gereken
    
    yeni_satir = pd.DataFrame([{
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
    
    # Veriyi birleştir ve güncelle
    if not df.empty:
        df = pd.concat([df, yeni_satir], ignore_index=True)
    else:
        df = yeni_satir
        
    conn.update(data=df)
    st.success(f"{urun} başarıyla kaydedildi!")
    st.rerun()

# TABLOYU GÖSTER
if not df.empty:
    st.subheader("📊 Güncel Stok Durumu")
    
    # Fark sütununu renklendirme
    def color_fark(val):
        color = 'red' if val < 0 else ('green' if val > 0 else 'black')
        return f'color: {color}'

    st.dataframe(df.style.applymap(color_fark, subset=['Fark']), use_container_width=True)
else:
    st.info("Henüz kayıtlı veri yok. Sol taraftan ürün ekleyerek başlayabilirsin.")
