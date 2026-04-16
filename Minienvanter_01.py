import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Envanter Yönetimi", layout="wide", page_icon="📦")

st.title("📦 Canlı Envanter & Sayım Mutabakatı")
st.markdown("Google Sheets (Bulut) ile senkronize çalışır.")

# 2. GOOGLE SHEETS BAĞLANTISI
def baglanti_kur():
    try:
        # Secrets'tan gelen veriyi oku
        secrets_dict = st.secrets["connections"]["gsheets"]
        
        # PEM anahtarı hatasını önlemek için \n karakterlerini düzelt
        if "private_key" in secrets_dict:
            # Bu işlem anahtardaki olası kopyalama hatalarını temizler
            cleaned_key = secrets_dict["private_key"].replace("\\n", "\n")
        
        conn = st.connection("gsheets", type=GSheetsConnection)
        # ttl=0 verinin her seferinde taze gelmesini sağlar
        return conn, conn.read(worksheet="Sayfa1", ttl=0)
    except Exception as e:
        st.error(f"⚠️ Bağlantı Kurulamadı! Detay: {e}")
        return None, pd.DataFrame()

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
        
        submit = st.form_submit_button("Veriyi Kaydet ve Buluta Gönder")

# 4. KAYIT İŞLEMİ
if submit and urun_adi and conn is not None:
    # Matematiksel Hesaplama
    olmasi_gereken = (baslangic + gelen + t_gelen) - (satan + t_giden)
    fark = yerinde_olan - olmasi_gereken
    
    # Yeni veri satırı
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
    
    # Mevcut veriye ekle
    if not df.empty:
        guncel_df = pd.concat([df, yeni_satir], ignore_index=True)
    else:
        guncel_df = yeni_satir
        
    # Google Sheets'e yükle
    try:
        conn.update(worksheet="Sayfa1", data=guncel_df)
        st.success(f"✅ {urun_adi} başarıyla kaydedildi!")
        st.rerun()
    except Exception as e:
        st.error(f"Yazma hatası oluştu: {e}")

# 5. VERİ GÖSTERİMİ (ANA EKRAN)
if not df.empty:
    st.subheader("📊 Güncel Envanter Listesi")
    
    # Fark sütunu için renklendirme
    def style_fark(val):
        color = 'red' if val < 0 else ('green' if val > 0 else 'black')
        return f'color: {color}; font-weight: bold'

    st.dataframe(
        df.style.applymap(style_fark, subset=['Fark']),
        use_container_width=True,
        hide_index=True
    )
    
    # Özet İstatistikler
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Ürün Çeşidi", len(df))
    c2.metric("Toplam Beklenen Stok", int(df["Olması Gereken"].sum()))
    c3.metric("Toplam Sayım Farkı", int(df["Fark"].sum()))
else:
    st.info("💡 Henüz kayıt yok. Sol taraftan ilk ürünü ekleyebilirsin.")
