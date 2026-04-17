import streamlit as st
import pandas as pd

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Hızlı Envanter", layout="wide", page_icon="📦")
st.title("📦 Envanter Takip Paneli")
st.info("💡 Not: Bu sürümde veriler hafızada tutulur. Sayfa yenilenirse veriler sıfırlanır.")

# 2. HAFIZA (SESSION STATE) KURULUMU
if 'envanter_tablosu' not in st.session_state:
    st.session_state.envanter_tablosu = pd.DataFrame(columns=[
        "Ürün Adı", "Başlangıç", "Gelen", "Satan", 
        "Trf Gelen", "Trf Giden", "Fiziksel Sayım", 
        "Beklenen Stok", "Fark"
    ])

# 3. YAN PANEL: VERİ GİRİŞİ
with st.sidebar:
    st.header("📋 Yeni Hareket Girişi")
    with st.form("envanter_formu", clear_on_submit=True):
        urun = st.text_input("Ürün Adı")
        
        col1, col2 = st.columns(2)
        with col1:
            baslangic = st.number_input("Başlangıç", min_value=0, value=0)
            gelen = st.number_input("Gelen (+)", min_value=0, value=0)
            t_gelen = st.number_input("Trf Gelen (+)", min_value=0, value=0)
        with col2:
            satan = st.number_input("Satan (-)", min_value=0, value=0)
            t_giden = st.number_input("Trf Giden (-)", min_value=0, value=0)
            fiziksel = st.number_input("Sayım (Fiziksel)", min_value=0, value=0)
        
        submit = st.form_submit_button("Listeye Ekle")

# 4. HESAPLAMA VE KAYIT MANTIĞI
if submit and urun:
    # Envanter Matematiği
    beklenen = (baslangic + gelen + t_gelen) - (satan + t_giden)
    fark = fiziksel - beklenen
    
    # Yeni satırı hazırla
    yeni_satir = {
        "Ürün Adı": urun,
        "Başlangıç": baslangic,
        "Gelen": gelen,
        "Satan": satan,
        "Trf Gelen": t_gelen,
        "Trf Giden": t_giden,
        "Fiziksel Sayım": fiziksel,
        "Beklenen Stok": beklenen,
        "Fark": fark
    }
    
    # Hafızadaki tabloya ekle
    st.session_state.envanter_tablosu = pd.concat([
        st.session_state.envanter_tablosu, 
        pd.DataFrame([yeni_satir])
    ], ignore_index=True)
    
    st.toast(f"✅ {urun} listeye eklendi!")

# 5. TABLO GÖSTERİMİ VE ÖZET
df = st.session_state.envanter_tablosu

if not df.empty:
    # İstatistik Paneli
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Ürün", len(df))
    c2.metric("Toplam Fark", int(df["Fark"].sum()))
    c3.metric("Kritik Ürün Sayısı", len(df[df["Fark"] < 0]))

    st.subheader("📊 Güncel Liste")
    
    # Renklendirme Fonksiyonu
    def renk_fark(val):
        if val < 0:
            return 'background-color: #ffcccc; color: #990000; font-weight: bold' # Kırmızı tonları
        elif val > 0:
            return 'background-color: #ccffcc; color: #006600; font-weight: bold' # Yeşil tonları
        else:
            return ''

    # .map() kullanımıyla versiyon hatası giderildi
    st.dataframe(
        df.style.map(renk_fark, subset=['Fark']),
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    # Alt tarafta veri yönetimi
    col_dl, col_clr = st.columns([4, 1])
    with col_dl:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Listeyi Bilgisayarına İndir (CSV)",
            data=csv,
            file_name='envanter_listesi.csv',
            mime='text/csv',
        )
    with col_clr:
        if st.button("🗑️ Listeyi Sıfırla"):
            st.session_state.envanter_tablosu = pd.DataFrame(columns=df.columns)
            st.rerun()
else:
    st.write("---")
    st.info("Henüz veri girişi yapılmadı. Sol taraftaki formu kullanarak ürün ekleyebilirsiniz.")
