import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Envanter Yönetimi", layout="wide", page_icon="📦")

st.title("📦 Canlı Envanter & Sayım Mutabakatı")

# 2. BAĞLANTI FONKSİYONU
# Kütüphane versiyon hatalarını önlemek için en standart yapıyı kullanıyoruz.
def baglanti_kur():
    try:
        # st.connection, Secrets içindeki [connections.gsheets] alanını otomatik okur.
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Google Sheet'teki "Sayfa1" sekmesini oku
        df = conn.read(worksheet="Sayfa1", ttl=0)
        return conn, df
    except Exception as e:
        st.error(f"⚠️ Bağlantı Kurulamadı! Detay: {e}")
        st.info("İpucu: 'Unable to load PEM file' hatası alıyorsanız Secrets kutusundaki private_key formatını düzeltmelisiniz.")
        return None, pd.DataFrame()

# Bağlantıyı başlat ve veriyi çek
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
    # Stok Matematiği
    olmasi_gereken = (baslangic + gelen + t_gelen) - (satan + t_giden)
    fark = yerinde_olan - olmasi_gereken
    
    # Yeni veri satırı oluştur
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
    
    # Mevcut veriye yeni satırı ekle
    if not df.empty:
        guncel_df = pd.concat([df, yeni_satir], ignore_index=True)
    else:
        guncel_df = yeni_satir
        
    # Google Sheets'e geri gönder
    try:
        conn.update(worksheet="Sayfa1", data=guncel_df)
        st.success(f"✅ {urun_adi} başarıyla kaydedildi!")
        st.rerun() # Sayfayı yenileyerek listeyi güncelle
    except Exception as e:
        st.error(f"Google Sheets güncelleme hatası: {e}")

# 5. VERİ GÖSTERİMİ (ANA EKRAN)
if not df.empty:
    st.subheader("📊 Güncel Envanter Listesi")
    
    # Fark sütunu için renklendirme (Eksi ise kırmızı, artı ise yeşil)
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
    if "Olması Gereken" in df.columns:
        c2.metric("Toplam Beklenen Stok", int(df["Olması Gereken"].sum()))
    if "Fark" in df.columns:
        c3.metric("Toplam Sayım Farkı", int(df["Fark"].sum()))
else:
    st.info("💡 Henüz kayıt yok. Sol taraftaki menüyü kullanarak ilk ürününü ekleyebilirsin.")
