import streamlit as st
import pandas as pd
import io
import plotly.express as px

st.set_page_config(page_title="DSS Iklim Papua Barat", layout="wide")

st.title("🌦️ Decision Support System Iklim - PAPUA BARAT")
st.markdown("Mendukung literasi iklim dan berpikir komputasi calon guru fisika melalui analisis data cuaca harian.")

# ---------------- RULE-BASED FUNCTIONS ----------------
def prediksi_cuaca(ch, matahari):
    if ch > 50:
        return "Hujan Lebat"
    elif ch > 20:
        return "Hujan"
    elif ch > 5:
        return "Berawan"
    elif matahari > 5:
        return "Cerah"
    else:
        return "Berawan"

def risiko_kekeringan(ch, matahari):
    if ch < 1 and matahari > 6:
        return "Risiko Tinggi"
    elif ch < 5:
        return "Risiko Sedang"
    else:
        return "Risiko Rendah"

def status_angin(angin):
    if angin > 30:
        return "Badai"
    elif angin > 15:
        return "Kencang"
    else:
        return "Normal"

# --------------------------------------------------------

st.sidebar.header("⬆️ Upload Data")
uploaded_file = st.sidebar.file_uploader("Unggah file Excel (.xlsx)", type=["xlsx"])

@st.cache_data
def process_data(file):
    df = pd.read_excel(file, sheet_name="Data Harian - Table")
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], format="%d-%m-%Y")

    # Tambahkan kolom baru hasil DSS
    df["Prediksi Cuaca"] = df.apply(lambda row: prediksi_cuaca(row["curah_hujan"], row["matahari"]), axis=1)
    df["Risiko Kekeringan"] = df.apply(lambda row: risiko_kekeringan(row["curah_hujan"], row["matahari"]), axis=1)
    df["Status Angin"] = df["kecepatan_angin"].apply(status_angin)

    return df

# Jika tidak upload file → pakai default
data = process_data(uploaded_file) if uploaded_file else process_data("PAPUABARAT2.xlsx")

# ---------------- SIDE FILTER ----------------
st.sidebar.header("⚙️ Pengaturan Tampilan")

indikator = st.sidebar.selectbox(
    "🔍 Pilih Analisis yang Ditampilkan",
    ["Prediksi Cuaca", "Risiko Kekeringan", "Status Angin", "Curah Hujan", "Suhu", "Kecepatan Angin"]
)

tanggal = st.sidebar.date_input("📅 Pilih Tanggal", value=data["Tanggal"].min(),
                                min_value=data["Tanggal"].min(), max_value=data["Tanggal"].max())

selected_row = data[data["Tanggal"] == pd.to_datetime(tanggal)]

# ---------------- Hasil Harian ----------------
if not selected_row.empty:
    st.subheader(f"📊 Data Iklim - {tanggal.strftime('%d %B %Y')}")
    info = selected_row.iloc[0]

    st.write(f"- Suhu rata-rata: **{info['Tavg']}°C**")
    st.write(f"- Kelembaban: **{info['kelembaban']}%**")
    st.write(f"- Curah hujan: **{info['curah_hujan']} mm**")
    st.write(f"- Matahari: **{info['matahari']} jam**")
    st.write(f"- Kecepatan angin: **{info['kecepatan_angin']} km/jam**")

    st.markdown("### 🤖 Hasil Analisis DSS")
    st.success(f"🌥 Prediksi Cuaca: **{info['Prediksi Cuaca']}**")
    st.info(f"💧 Risiko Kekeringan: **{info['Risiko Kekeringan']}**")
    st.warning(f"🌪 Status Angin: **{info['Status Angin']}**")
else:
    st.error("🚫 Tidak ada data untuk tanggal tersebut.")

# ---------------- Grafik ----------------
st.markdown("---")
st.subheader("📈 Grafik Tren Data")

if indikator == "Curah Hujan":
    fig = px.line(data, x="Tanggal", y="curah_hujan", title="Tren Curah Hujan")
elif indikator == "Suhu":
    fig = px.line(data, x="Tanggal", y=["Tn", "Tx", "Tavg"], title="Tren Suhu Harian")
elif indikator == "Kecepatan Angin":
    fig = px.line(data, x="Tanggal", y="kecepatan_angin", title="Tren Kecepatan Angin")
else:
    fig = px.histogram(data, x="Tanggal", color=indikator, title=f"Distribusi {indikator}")

st.plotly_chart(fig, use_container_width=True)

# ---------------- Data Table + Download ----------------
with st.expander("📁 Lihat & Unduh Data"):
    st.dataframe(data)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        data.to_excel(writer, index=False, sheet_name="Hasil DSS")

    st.download_button(
        label="⬇️ Unduh Hasil Analisis Excel",
        data=buffer.getvalue(),
        file_name="DSS_PapuaBarat.xlsx",
        mime="application/vnd.ms-excel"
    )
