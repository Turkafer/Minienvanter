import streamlit as st
import gspread
import pandas as pd

# ------------------------
# SAYFA AYARLARI
# ------------------------
st.set_page_config(page_title="Envanter Takip", layout="wide")
st.title("📦 Canlı Envanter Sistemi")

# ------------------------
# GOOGLE SHEETS BAĞLANTI
# ------------------------
@st.cache_resource
def baglanti_kur():
    try:
        creds = dict(st.secrets)

        # 🔥 Cloud fix: \n düzeltmesi
        if "private_key" in creds:
            creds["private_key"] = creds["private_key"].replace("\\n", "\n")

        gc = gspread.service_account_from_dict(creds)
        sh = gc.open_by_url(st.secrets["spreadsheet"])
        return sh.get_worksheet(0)

    except Exception as e:
        st.error(f"Bağlantı hatası: {e}")
        return None

worksheet = baglanti_kur()

# ------------------------
# VERİ ÇEKME
# ------------------------
@st.cache_data(ttl=5)
def veri_getir():
    if worksheet is None:
        return pd.DataFrame()

    data = worksheet.get_all_records()
    return pd.DataFrame(data)

df = veri_getir()

# ------------------------
# KOLONLAR
# ------------------------
KOLONLAR = [
    "Ürün",
    "Envanterde Olan",
    "Gelen",
    "Satılan",
    "Transfer Gelen",
    "Transfer Giden",
    "Olması Gereken",
    "Yerinde Olan",
    "Fark"
]

if df.empty:
    df = pd.DataFrame(columns=KOLONLAR)

# ------------------------
# SIDEBAR - EKLEME
# ------------------------
with st.sidebar:
    st.header("➕ Yeni Ürün")

    with st.form("form", clear_on_submit=True):
        urun = st.text_input("Ürün Adı")

        envanter = st.number_input("Envanterde Olan", min_value=0)
        gelen = st.number_input("Gelen", min_value=0)
        satilan = st.number_input("Satılan", min_value=0)
        t_gelen = st.number_input("Transfer Gelen", min_value=0)
        t_giden = st.number_input("Transfer Giden", min_value=0)
        yerinde = st.number_input("Yerinde Olan", min_value=0)

        submit = st.form_submit_button("Kaydet")

        if submit:
            if not urun:
                st.warning("Ürün adı boş olamaz")

            elif not df.empty and "Ürün" in df.columns and urun in df["Ürün"].values:
                st.warning("Bu ürün zaten var!")

            else:
                olmasi_gereken = envanter + gelen + t_gelen - satilan - t_giden
                fark = yerinde - olmasi_gereken

                worksheet.append_row([
                    urun,
                    envanter,
                    gelen,
                    satilan,
                    t_gelen,
                    t_giden,
                    olmasi_gereken,
                    yerinde,
                    fark
                ])

                st.success("Kayıt eklendi!")
                st.cache_data.clear()
                st.rerun()

# ------------------------
# TABLO
# ------------------------
st.subheader("📊 Envanter Durumu")

if not df.empty and worksheet is not None:

    df["Olması Gereken"] = (
        df["Envanterde Olan"]
        + df["Gelen"]
        + df["Transfer Gelen"]
        - df["Satılan"]
        - df["Transfer Giden"]
    )

    df["Fark"] = df["Yerinde Olan"] - df["Olması Gereken"]

    st.dataframe(df, use_container_width=True)

else:
    st.info("Henüz veri yok veya bağlantı kurulamadı.")
