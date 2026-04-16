import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Envanter Yönetimi", layout="wide", page_icon="📦")

st.title("📦 Canlı Envanter & Sayım Mutabakatı")

# 2. BAĞLANTI FONKSİYONU (Secrets Kısıtlamasını Aşan Versiyon)
def baglanti_kur():
    try:
        # Secrets kontrolü
        if "connections" not in st.secrets or "gsheets" not in st.secrets.connections:
            st.error("❌ Secrets ayarları eksik! [connections.gsheets] başlığını kontrol et.")
            return None, pd.DataFrame()

        # Secrets verilerini bir sözlüğe kopyala (Hata almamak için üzerine yazmıyoruz)
        creds = dict(st.secrets["connections"]["gsheets"])
        
        # Anahtardaki PEM formatı hatalarını temizle
        if "private_key" in creds:
            creds["private_key"] = creds["private_key"].replace("\\n", "\n")
        
        # Bağlantıyı manuel konfigürasyonla kur
        conn = st.connection("gsheets", type=GSheetsConnection, **creds)
        
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
            baslangic = st.number_input("Başlangıç", min_value=0, value=0)
            gelen = st.number_input("Gelen (+)", min_value=0, value=0)
            t_gelen = st.number_input("Transfer Gelen (+)", min_value=0, value=0)
        with col2:
            satan = st.number_input("Satan (-)", min_value=0, value=0)
            t_giden = st.number_input("Transfer Giden (-)", min_value=0, value=0)
            yerinde_olan = st.number_input("Yerinde (Fiziksel)", min_value=0, value=0)
        
        submit = st.form_submit_button("Veriyi Kaydet ve Gönder")

# 4. KAYIT İŞLEMİ
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
        st.success(f"✅ {urun_adi} kaydedildi!")
        st.rerun()
    except Exception as e:
        st.error(f"Yazma hatası oluştu: {e}")

# 5. VERİ GÖSTERİMİ
if not df.empty:
    st.subheader("📊 Güncel Envanter Listesi")
    
    def style_fark(val):
        color = 'red' if val < 0 else ('green' if val > 0 else 'black')
        return f'color: {color}; font-weight: bold'

    st.dataframe(
        df.style.applymap(style_fark, subset=['Fark']),
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Ürün", len(df))
    if "Olması Gereken" in df.columns:
        c2.metric("Beklenen Stok", int(df["Olması Gereken"].sum()))
    if "Fark" in df.columns:
        c3.metric("Toplam Fark", int(df["Fark"].sum()))
else:
    st.info("💡 Henüz kayıt yok. Sol taraftan ekleme yapabilirsin.")
