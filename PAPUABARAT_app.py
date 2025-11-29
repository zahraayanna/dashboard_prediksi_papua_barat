import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pickle
from sklearn.preprocessing import StandardScaler
import numpy as np

# -----------------------------
# CONFIGURASI UI
# -----------------------------
st.set_page_config(
    page_title="Prediksi Cuaca Papua Barat",
    page_icon="🌦",
    layout="wide"
)

st.markdown("""
<style>
body {
    background-color: #F5F7FA;
}
.big-title {
    font-size: 36px;
    font-weight: bold;
    color: #1F4E79;
}
.sub {
    font-size: 17px;
    color: #2C3E50;
}
.card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">🌦 Prediksi Cuaca Papua Barat</p>', unsafe_allow_html=True)
st.markdown('<p class="sub">Dashboard prediksi berbasis data historis dan machine learning.</p>', unsafe_allow_html=True)
st.write("")

# -----------------------------
# LOAD DATASET
# -----------------------------
df = pd.read_excel("PAPUABARAT2.xlsx")

df['Tanggal'] = pd.to_datetime(df['Tanggal'])

# -----------------------------
# LOAD MODEL
# -----------------------------
model = pickle.load(open("model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

# -----------------------------
# PILIH VARIABEL
# -----------------------------
OPTIONS = {
    "Suhu Minimum (°C)": "Tn",
    "Suhu Maksimum (°C)": "Tx",
    "Suhu Rata-Rata (°C)": "Tavg",
    "Kelembaban Udara (%)": "kelembaban",
    "Curah Hujan (mm)": "curah_hujan",
    "Durasi Penyinaran Matahari (jam)": "matahari",
    "Kecepatan Angin Maksimum (m/s)": "kecepatan_angin"
}

st.markdown("### 🔍 Pilih Parameter")
selected = st.selectbox("Parameter cuaca yang ingin ditampilkan:", OPTIONS.keys())

selected_column = OPTIONS[selected]

# -----------------------------
# PREDIKSI
# -----------------------------
last_values = df.iloc[-1, 1:].values.reshape(1, -1)
scaled_values = scaler.transform(last_values)

future_prediction = model.predict(scaled_values)[0]

# -----------------------------
# PLOT
# -----------------------------
st.markdown("### 📈 Perbandingan Data Historis & Prediksi")

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(df['Tanggal'], df[selected_column], label='Data Historis', linewidth=2)
ax.scatter(df['Tanggal'].iloc[-1], df[selected_column].iloc[-1], color='blue')

# titik prediksi (sebagai garis titik putus-putus)
future_date = df['Tanggal'].max() + pd.Timedelta(days=1)
ax.plot([df['Tanggal'].max(), future_date], 
        [df[selected_column].iloc[-1], future_prediction[list(OPTIONS.values()).index(selected_column)]],
        linestyle="--", label="Prediksi", linewidth=2)

ax.set_title(f"Tren {selected}")
ax.set_xlabel("Tanggal")
ax.set_ylabel(selected)
ax.legend()

st.pyplot(fig)

# -----------------------------
# HASIL PREDIKSI
# -----------------------------
st.markdown("### 🔮 Hasil Prediksi Besok")
st.markdown(f"""
<div class="card">
📌 <b>{selected}</b> diperkirakan bernilai 
<span style="font-size:22px;color:#d35400;font-weight:bold;">
{round(future_prediction[list(OPTIONS.values()).index(selected_column)], 2)}
</span>
</div>
""", unsafe_allow_html=True)
