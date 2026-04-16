import streamlit as st
import gspread
import pandas as pd

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Envanter Takip", layout="wide", page_icon="📦")
st.title("📦 Canlı Envanter Takibi")

# 2. VERİTABANI BAĞLANTISI (Doğrudan gspread ile)
def baglanti_kur():
    try:
        # Secrets'tan bilgileri sözlük olarak alıyoruz
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
        
        # Google Sheets Yetkilendirme
        gc = gspread.service_account_from_dict(creds)
        # Tabloyu URL ile açıyoruz
        sh = gc.open_by_url(st.secrets["spreadsheet"])
        # İlk sayfayı seçiyoruz
        return sh.get_worksheet(0)
    except Exception as e:
        st.error(f"⚠️ Bağlantı Hatası: {e}")
        return None

worksheet = baglanti_kur()

# 3. VERİ İŞLEME VE GÖSTERİM
if worksheet:
    # Google Sheets'ten tüm verileri çek
    records = worksheet.get_all_records()
    df = pd.DataFrame(records)
    
    # FORM: Sol tarafta veri girişi
    with st.sidebar:
        st.header("📋 Yeni Kayıt")
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
                fiziksel = st.number_input("Yerinde (Fiziksel)", min_value=0)
            
            submit = st.form_submit_button("Sisteme İşle")

    # KAYIT MEKANİZMASI
    if submit and urun:
        # Hesaplama: (Başlangıç + Gelen + Trf Gelen) - (Satan + Trf Giden)
        beklenen = (baslangic + gelen + t_gelen) - (satan + t_giden)
        fark = fiziksel - beklenen
        
        # Google Sheet'e eklenecek satır (Sıralama önemli)
        yeni_satir = [urun, baslangic, gelen, satan, t_gelen, t_giden, fiziksel, beklenen, fark]
        
        try:
            worksheet.append_row(yeni_satir)
            st.success(f"✅ {urun} başarıyla kaydedildi!")
            st.rerun()
        except Exception as e:
            st.error(f"Yazma hatası: {e}")

    # TABLO GÖSTERİMİ
    if not df.empty:
        st.subheader("📊 Güncel Envanter Durumu")
        # Fark sütununu renklendirmek için görsel dokunuş
        def style_fark(val):
            color = 'red' if val < 0 else ('green' if val > 0 else 'black')
            return f'color: {color}; font-weight: bold'
        
        st.dataframe(df.style.applymap(style_fark, subset=['Fark'] if 'Fark' in df.columns else []), use_container_width=True)
    else:
        st.info("Henüz veri yok. Sol taraftan ürün ekleyerek başlayın.")
