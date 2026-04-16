import streamlit as st
import gspread
import pandas as pd

st.set_page_config(page_title="Envanter Sistemi", layout="wide")
st.title("📦 Envanter Takip Paneli")

# BAĞLANTI FONKSİYONU
def baglan():
    try:
        # Secrets'tan bilgileri al
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
        
        # Google Sheets'e yetki ile bağlan
        gc = gspread.service_account_from_dict(creds)
        # Dosya URL'sini kullanarak aç
        sh = gc.open_by_url(st.secrets["spreadsheet"])
        # Sayfa1 isimli sekmeyi seç
        worksheet = sh.worksheet("Sayfa1")
        return worksheet
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return None

worksheet = baglan()

if worksheet:
    # Verileri Çek
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    
    st.success("✅ Google Sheets Bağlantısı Aktif!")
    
    # Form Alanı
    with st.sidebar:
        st.header("Yeni Kayıt")
        with st.form("kayit_formu"):
            urun = st.text_input("Ürün Adı")
            adet = st.number_input("Adet", min_value=0)
            submit = st.form_submit_button("Kaydet")
            
            if submit and urun:
                # Sayfanın en altına yeni satır ekle
                worksheet.append_row([urun, adet])
                st.success("Kaydedildi!")
                st.rerun()

    # Tabloyu Göster
    st.dataframe(df, use_container_width=True)
