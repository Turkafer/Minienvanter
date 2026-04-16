import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Envanter Yönetimi", layout="wide", page_icon="📦")

st.title("📦 Canlı Envanter & Sayım Mutabakatı")

# 2. BAĞLANTI FONKSİYONU
def baglanti_kur():
    try:
        # ÖNEMLİ: İçine project_id, private_key vb. yazmıyoruz. 
        # Sadece bağlantı ismini ("gsheets") veriyoruz.
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Google Sheet'teki sekme isminin "Sayfa1" olduğundan emin ol.
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
            satan = st.number_input("Satan (-)", min_value=0, value=0)
            t_giden = st.number_input("Transfer Giden (-)", min_value=0, value=0)
            yerinde_olan = st.number_input("Yerinde (Fiziksel)", min_value=0, value=0)
        
        submit = st.form_submit_button("Veriyi Kaydet ve Gönder")

# 4. KAYIT İŞLEMİ VE HESAPLAMA
if submit and urun_adi and conn is not None:
    olmasi_gereken = (baslangic + gelen + t_gelen) - (satan + t_giden)
    fark = yerinde_olan - olmasi_gereken
    
    yeni_satir = pd.DataFrame([{
        "Ürün Adı": urun_adi,
        "Başlangıç": baslangic,
        "Gelen": gelen,
        "Satan": satan,
        "Trf Gelen": t_gelen,
        "Trf Giden": t_giden,
        "Yerinde Olan": yerinde_olan,
        "Olması Gereken": olmasi_gereken,
        "Fark": fark
    }])
    
    if not df.empty:
        guncel_df = pd.concat([df, yeni_satir], ignore_index=True)
    else:
        guncel_df = yeni_satir
        
    try:
        conn.update(worksheet="Sayfa1", data=guncel_df)
        st.success(f"✅ {urun_adi} başarıyla kaydedildi!")
        st.rerun()
    except Exception as e:
        st.error(f"Google Sheets güncelleme hatası: {e}")

# 5. VERİ GÖSTERİMİ
if not df.empty:
    st.subheader("📊 Güncel Envanter Listesi")
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("💡 Henüz kayıt yok. Sol taraftan ürün ekleyebilirsiniz.")
