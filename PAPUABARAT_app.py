import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------- CONFIG -------------------
st.set_page_config(
    page_title="DSS Iklim Papua Barat",
    layout="wide",
    page_icon="🌦️"
)

# ------------------- STYLE -------------------
st.markdown("""
<style>
    .big-title { font-size:32px; font-weight:700; color:#004AAD;}
    .metric-box {
        background-color: #E7F0FF;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-left: 6px solid #004AAD;
    }
</style>
""", unsafe_allow_html=True)

# ------------------- TITLE -------------------
st.markdown("<div class='big-title'>🌦️ Decision Support System Iklim Papua Barat</div>", unsafe_allow_html=True)
st.write("Sistem ini membantu analisis tren cuaca berdasarkan dataset historis Papua Barat.")

# ------------------- LOAD DATA -------------------
@st.cache_data
def load_data():
    df = pd.read_excel("PAPUABARAT2.xlsx")  # << FILE WAJIB ADA DI ROOT
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    df.set_index("Tanggal", inplace=True)
    return df

try:
    data = load_data()
except:
    st.error("❌ File `prediksi.xlsx` tidak ditemukan. Pastikan file ada di folder aplikasi.")
    st.stop()

# ------------------- SIDE FILTER -------------------
st.sidebar.header("📅 Filter Data")

date_selected = st.sidebar.date_input(
    "Pilih Tanggal",
    min_value=data.index.min(),
    max_value=data.index.max(),
    value=data.index.min()
)

parameter = st.sidebar.selectbox(
    "📊 Pilih Grafik",
    ["Suhu Harian", "Curah Hujan", "Kelembaban", "Kecepatan Angin", "Penyinaran Matahari"]
)

# ------------------- DAILY INFORMATION -------------------
st.subheader(f"📍 Informasi Cuaca: {date_selected.strftime('%d %B %Y')}")

if str(date_selected) in data.index.astype(str):
    row = data.loc[str(date_selected)].iloc[0] if isinstance(data.loc[str(date_selected)], pd.DataFrame) else data.loc[str(date_selected)]

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("🌡 Suhu Rata-rata", f"{row['Tavg']}°C")
    col2.metric("💧 Kelembaban", f"{row['kelembaban']}%")
    col3.metric("☔ Curah Hujan", f"{row['curah_hujan']} mm")
    col4.metric("🌞 Matahari", f"{row['matahari']} jam")
    col5.metric("🍃 Kecepatan Angin", f"{row['kecepatan_angin']} km/jam")

else:
    st.warning("Data untuk tanggal ini tidak tersedia.")

st.markdown("---")

# ------------------- GRAPH SECTION -------------------
st.subheader("📈 Visualisasi Tren Iklim")

if parameter == "Suhu Harian":
    fig = px.line(data, y=["Tn", "Tx", "Tavg"], title="Perubahan Suhu Harian")
elif parameter == "Curah Hujan":
    fig = px.line(data, y="curah_hujan", title="Curah Hujan Harian (mm)")
elif parameter == "Kelembaban":
    fig = px.line(data, y="kelembaban", title="Kelembaban Harian (%)")
elif parameter == "Kecepatan Angin":
    fig = px.line(data, y="kecepatan_angin", title="Kecepatan Angin (km/jam)")
else:
    fig = px.line(data, y="matahari", title="Durasi Penyinaran Matahari (jam)")

fig.update_traces(line=dict(width=3))
fig.update_layout(height=450, template="plotly_white")

st.plotly_chart(fig, use_container_width=True)

# ------------------- TABLE -------------------
with st.expander("📁 Lihat Data Lengkap"):
    st.dataframe(data)

# ------------------- DOWNLOAD -------------------
buffer = pd.ExcelWriter("hasil_export.xlsx", engine="xlsxwriter")
data.to_excel(buffer, sheet_name="Hasil", index=True)
buffer.save()

st.download_button(
    label="⬇️ Unduh Data Hasil",
    data=open("hasil_export.xlsx", "rb"),
    file_name="DSS_PapuaBarat.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

