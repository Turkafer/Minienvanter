import streamlit as st
import gspread
import pandas as pd

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Envanter Takip", layout="wide", page_icon="📦")
st.title("📦 Canlı Envanter Takip Sistemi")

# 2. BAĞLANTI VE ANAHTAR TAMİR MOTORU
def baglanti_kur():
    try:
        # Secrets'tan anahtarı al ve temizle
        raw_key = st.secrets["private_key"]
        
        # PEM Hatasını (InvalidByte) önlemek için temizlik
        # Ters bölü n işaretlerini gerçek alt satıra çevirir ve gereksiz boşlukları siler
        clean_key = raw_key.replace("\\n", "\n")
        
        creds = {
            "type": st.secrets["type"],
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": clean_key,
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"],
            "auth_uri": st.secrets["auth_uri"],
            "token_uri": st.secrets["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["client_x509_cert_url"]
        }
        
        # Yetkilendirme ve Tabloyu Açma
        gc = gspread.service_account_from_dict(creds)
        sh = gc.open_by_url(st.secrets["spreadsheet"])
        return sh.get_worksheet(0)
    except Exception as e:
        st.error(f"⚠️ Bağlantı Hatası: {e}")
        return None

worksheet = baglanti_kur()

# 3. VERİ İŞLEME VE ARAYÜZ
if worksheet:
    # Verileri çek
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    
    # SOL PANEL: VERİ GİRİŞİ
    with st.sidebar:
        st.header("📋 Yeni Ürün Girişi")
        with st.form("envanter_form", clear_on_submit=True):
            urun = st.text_input("Ürün Adı")
            col1, col2 = st.columns(2)
            with col1:
                baslangic = st.number_input("Başlangıç", min_value=0, value=0)
                gelen = st.number_input("Gelen (+)", min_value=0, value=0)
                t_gelen = st.number_input("Transfer Gelen (+)", min_value=0, value=0)
            with col2:
                satan = st.number_input("Satan (-)", min_value=0, value=0)
                t_giden = st.number_input("Transfer Giden (-)", min_value=0, value=0)
                fiziksel = st.number_input("Sayım (Fiziksel)", min_value=0, value=0)
            
            submit = st.form_submit_button("Sisteme Kaydet")

    # KAYIT HESAPLAMASI
    if submit and urun:
        # Envanter Matematiği
        beklenen = (baslangic + gelen + t_gelen) - (satan + t_giden)
        fark = fiziksel - beklenen
        
        # Google Sheet'e eklenecek satır
        yeni_satir = [urun, baslangic, gelen, satan, t_gelen, t_giden, fiziksel, beklenen, fark]
        
        try:
            worksheet.append_row(yeni_satir)
            st.success(f"✅ {urun} başarıyla eklendi!")
            st.rerun()
        except Exception as e:
            st.error(f"Yazma Hatası: {e}")

    # TABLO GÖSTERİMİ
    if not df.empty:
        st.subheader("📊 Güncel Envanter Listesi")
        
        # Fark sütununu renklendirme
        def color_fark(val):
            color = 'red' if val < 0 else ('green' if val > 0 else 'black')
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            df.style.applymap(color_fark, subset=['Fark'] if 'Fark' in df.columns else []),
            use_container_width=True
        )
    else:
        st.info("💡 Henüz kayıt yok. Sol taraftan ekleme yapabilirsiniz.")
