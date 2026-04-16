import streamlit as st
import gspread
import pandas as pd

# 1. Sayfa Ayarları
st.set_page_config(page_title="Envanter Takip", layout="wide")
st.title("📦 Basit Envanter Sistemi")

# 2. Google Sheets Bağlantısı
def baglanti_kur():
    try:
        # Secrets'tan direkt al (EN DOĞRU YÖNTEM)
        gc = gspread.service_account_from_dict(st.secrets)

        # Spreadsheet'i URL ile aç
        sh = gc.open_by_url(st.secrets["spreadsheet"])

        # İlk sayfayı al
        worksheet = sh.get_worksheet(0)

        return worksheet

    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return None

worksheet = baglanti_kur()

# 3. Veri İşlemleri
if worksheet:
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    st.success("✅ Veritabanına Bağlanıldı!")

    # Sidebar - Yeni ürün ekleme
    with st.sidebar:
        st.header("Yeni Ürün Ekle")

        with st.form("ekleme_formu", clear_on_submit=True):
            urun_adi = st.text_input("Ürün İsmi")
            adet = st.number_input("Stok Adedi", min_value=0, step=1)
            notlar = st.text_area("Notlar")

            submit = st.form_submit_button("Sisteme Kaydet")

            if submit:
                if not urun_adi:
                    st.warning("Ürün ismi boş olamaz!")
                else:
                    worksheet.append_row([urun_adi, adet, notlar])
                    st.success("Kayıt Başarılı!")
                    st.rerun()

    # Tablo gösterimi
    if not df.empty:
        st.subheader("📋 Güncel Stok Listesi")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Henüz veri yok. Sol menüden ilk ürünü ekle.")
