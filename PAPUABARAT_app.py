import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import datetime

# ======== UI CONFIG ========
st.set_page_config(page_title="DSS Iklim Papua Barat", layout="wide")

st.markdown("""
<style>
    .main-title {
        font-size: 32px; 
        font-weight: bold;
        color: #0066CC;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🌦️ DSS Prediksi Iklim - Papua Barat</p>', unsafe_allow_html=True)
st.write("Aplikasi ini membantu analisis tren iklim berdasarkan data cuaca harian dari Papua Barat.")

# ======== LOAD DATA ========
EXCEL_FILE = "PAPUABARAT2.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(EXCEL_FILE)
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    return df

try:
    data = load_data()
except:
    st.error("❌ File `PAPUABARAT2.xlsx` tidak ditemukan. Upload atau tambahkan ke project.")
    st.stop()

# ======== RULE-BASED DSS ========
def prediksi_cuaca(ch, sun):
    if ch > 50: return "Hujan Lebat"
    elif ch > 20: return "Hujan"
    elif ch > 5: return "Berawan"
    elif sun > 6: return "Cerah"
    return "Berawan"

def risiko_kekeringan(ch, sun):
    if ch < 1 and sun > 6: return "Tinggi"
    elif ch < 5: return "Sedang"
    return "Rendah"

def status_angin(angin):
    if angin > 30: return "Badai"
    elif angin > 15: return "Kencang"
    return "Normal"

data["Prediksi Cuaca"] = data.apply(lambda r: prediksi_cuaca(r["curah_hujan"], r["matahari"]), axis=1)
data["Risiko Kekeringan"] = data.apply(lambda r: risiko_kekeringan(r["curah_hujan"], r["matahari"]), axis=1)
data["Status Angin"] = data["kecepatan_angin"].apply(status_angin)

# ======== FILTER TANGGAL ========
st.sidebar.header("📅 Pilih Tanggal Analisis")
tanggal = st.sidebar.date_input("Tanggal", value=data["Tanggal"].min())

row = data[data["Tanggal"] == pd.to_datetime(tanggal)]

if row.empty:
    st.warning("⚠️ Tidak ada data untuk tanggal tersebut.")
else:
    info = row.iloc[0]

    st.subheader(f"📊 Kondisi Iklim ({tanggal.strftime('%d %B %Y')})")
    st.write(f"""
    - Suhu rata-rata: **{info['Tavg']}°C**
    - Kelembaban: **{info['kelembaban']}%**
    - Curah hujan: **{info['curah_hujan']} mm**
    - Matahari: **{info['matahari']} jam**
    - Kecepatan angin: **{info['kecepatan_angin']} km/jam**
    """)

    st.success(f"🌤️ Prediksi Cuaca: **{info['Prediksi Cuaca']}**")
    st.warning(f"🔥 Risiko Kekeringan: **{info['Risiko Kekeringan']}**")
    st.info(f"💨 Status Angin: **{info['Status Angin']}**")

# ======== GRAFIK ========
st.markdown("---")
st.subheader("📈 Visualisasi Tren Iklim")

pilihan = st.selectbox(
    "Pilih indikator untuk ditampilkan:",
    ["curah_hujan", "Tavg", "kelembaban", "matahari", "kecepatan_angin", "Prediksi Cuaca"]
)

if pilihan in ["Prediksi Cuaca"]:
    fig = px.histogram(data, x="Tanggal", color="Prediksi Cuaca", title="Distribusi Prediksi Cuaca")
else:
    fig = px.line(data, x="Tanggal", y=pilihan, title=f"Tren {pilihan.capitalize()} Harian")

st.plotly_chart(fig, use_container_width=True)

# ======== EXPORT DATA ========
with st.expander("⬇️ Unduh Hasil Analisis"):
    buffer = io.BytesIO()
    data.to_excel(buffer, index=False)
    st.download_button("Download Excel", buffer.getvalue(), file_name="DSS_Iklim_PapuaBarat.xlsx")
