import streamlit as st
import gspread
import pandas as pd

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Kesin Çözüm Envanter", layout="wide")
st.title("📦 Profesyonel Envanter Takibi")

# 2. ANAHTAR TAMİR VE BAĞLANTI MOTORU
def baglanti_kur():
    try:
        # Secrets'tan anahtarı al
        raw_key = st.secrets["private_key"]
        
        # --- OTOMATİK TAMİR BAŞLANGICI ---
        # Hata veren alt çizgileri (_) ve yanlış boşlukları temizle
        p_key = raw_key.replace("_", "").replace(" ", "")
        
        # Başlık ve bitiş kısımlarını standart hale getir
        if "BEGINPRIVATEKEY" in p_key:
            p_key = p_key.replace("-----BEGINPRIVATEKEY-----", "-----BEGIN PRIVATE KEY-----\n")
        if "ENDPRIVATEKEY" in p_key:
            p_key = p_key.replace("-----ENDPRIVATEKEY-----", "\n-----END PRIVATE KEY-----\n")
        
        # Kaçış karakterlerini gerçek alt satıra çevir
        p_key = p_key.replace("\\n", "\n")
        # --- OTOMATİK TAMİR BİTİŞİ ---

        creds = {
            "type": st.secrets["type"],
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": p_key,
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"],
            "auth_uri": st.secrets["auth_uri"],
            "token_uri": st.secrets["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["client_x509_cert_url"]
        }
        
        gc = gspread.service_account_from_dict(creds)
        sh = gc.open_by_url(st.secrets["spreadsheet"])
        return sh.get_worksheet(0)
    except Exception as e:
        st.error(f"⚠️ Kritik Bağlantı Hatası: {e}")
        return None

worksheet = baglanti_kur()

# 3. VERİ İŞLEME VE ARAYÜZ
if worksheet:
    # Google Sheets'ten verileri çek
    try:
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
    except:
        df = pd.DataFrame()

    # SOL PANEL: VERİ GİRİŞİ
    with st.sidebar:
        st.header("📊 Yeni Hareket Girişi")
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
                sayim = st.number_input("Sayım (Fiziksel)", min_value=0)
            
            submit = st.form_submit_button("Sisteme Kaydet")

    # KAYIT HESAPLAMASI
    if submit and urun:
        beklenen = (baslangic + gelen + t_gelen) - (satan + t_giden)
        fark = sayim - beklenen
        yeni_satir = [urun, baslangic, gelen, satan, t_gelen, t_giden, sayim, beklenen, fark]
        
        try:
            worksheet.append_row(yeni_satir)
            st.success(f"✅ {urun} kaydedildi!")
            st.rerun()
        except Exception as e:
            st.error(f"Yazma Hatası: {e}")

    # TABLO GÖSTERİMİ
    if not df.empty:
        st.subheader("📋 Mevcut Envanter Tablosu")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("💡 Henüz kayıt bulunamadı. Sol menüden ilk ürünü ekleyin.")
