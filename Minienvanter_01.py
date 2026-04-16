import streamlit as st
import gspread
import pandas as pd

# 1. Sayfa Ayarları
st.set_page_config(page_title="Envanter Takip", layout="wide")
st.title("📦 Basit Envanter Sistemi")

# 2. Google Sheets Bağlantısı
def baglanti_kur():
    try:
        # Secrets'tan tüm bilgileri çekiyoruz
        creds = {
            "type": st.secrets["type"],
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": st.secrets["private_key"].replace("\\n", "\n"),
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"],
            "auth_uri": st.secrets["auth_uri"],
            "token_uri": st.secrets["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["client_x509_cert_url"]
        }
        
        # Yetkilendirme
        gc = gspread.service_account_from_dict(creds)
        # Spreadsheet'i URL ile aç
        sh = gc.open_by_url(st.secrets["spreadsheet"])
        # İlk sayfayı (sekme) al
        return sh.get_worksheet(0)
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return None

worksheet = baglanti_kur()

# 3. Veri İşlemleri
if worksheet:
    # Mevcut verileri çek ve göster
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    
    st.success("✅ Veritabanına Bağlanıldı!")
    
    # Yeni Veri Ekleme Formu
    with st.sidebar:
        st.header("Yeni Ürün Ekle")
        with st.form("ekleme_formu", clear_on_submit=True):
            urun_adi = st.text_input("Ürün İsmi")
            adet = st.number_input("Stok Adedi", min_value=0, step=1)
            notlar = st.text_area("Notlar")
            submit = st.form_submit_button("Sisteme Kaydet")
            
            if submit and urun_adi:
                # Tabloya yeni satır ekle
                worksheet.append_row([urun_adi, adet, notlar])
                st.success("Kayıt Başarılı!")
                st.rerun()

    # Tabloyu ekranda göster
    if not df.empty:
        st.subheader("📋 Güncel Stok Listesi")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Henüz veri yok. Sol menüden ilk ürünü ekle.")
