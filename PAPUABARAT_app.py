import streamlit as st
import pandas as pd
import numpy as np
import joblib
import datetime
import plotly.express as px

# ============================
# 1. CONFIGURASI APLIKASI
# ============================

st.set_page_config(
    page_title="Prediksi Cuaca Papua Barat",
    layout="wide",
    page_icon="⛅",
)

# Custom CSS untuk tampilan lebih menarik
st.markdown("""
<style>
body {
    background: linear-gradient(to bottom right, #0f2027, #2c5364);
}
.big-title {
    font-size: 42px;
    font-weight: bold;
    color: white;
    text-align: center;
    margin-bottom: 5px;
}
.sub-text {
    color: #e6f2ff;
    text-align: center;
    font-size: 18px;
}
.card {
    padding: 18px;
    border-radius: 15px;
    background: rgba(255,255,255,0.13);
    color: white;
    backdrop-filter: blur(5px);
}
.metric-value {
    font-size: 35px;
    font-weight: bold;
    color: #00ffcc;
}
</style>
""", unsafe_allow_html=True)


# ============================
# 2. LOAD MODEL & DATASET
# ============================

MODEL_PATH = "weather_model.pkl"
DATA_PATH = "papua_barat_weather.csv"   # nama file dataset kamu

try:
    model = joblib.load(MODEL_PATH)
    df = pd.read_csv(DATA_PATH)
    data_loaded = True
except:
    data_loaded = False
    st.error("❌ Model atau dataset belum ditemukan. Pastikan file *weather_model.pkl* dan dataset tersedia.")


# ============================
# 3. HEADER
# ============================

st.markdown("<p class='big-title'>🌦 Prediksi Cuaca Papua Barat</p>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>Sistem prediksi berbasis machine learning menggunakan data historis meteorologi Papua Barat</p>", unsafe_allow_html=True)

st.write("")


# ============================
# 4. PILIH WILAYAH
# ============================

if data_loaded:

    papua_regions = sorted(df["location"].unique())

    selected_region = st.selectbox("📍 Pilih Wilayah:", papua_regions)

    region_data = df[df["location"] == selected_region].tail(100)


    # ============================
    # 5. VISUALISASI DATA SEBELUM PREDIKSI
    # ============================

    st.subheader("📊 Tren Cuaca Wilayah: " + selected_region)

    colA, colB = st.columns(2)

    # grafik temperatur
    with colA:
        fig_temp = px.line(region_data, x="date", y="temperature", title="Tren Suhu (°C)")
        st.plotly_chart(fig_temp, use_container_width=True)

    # grafik curah hujan
    with colB:
        fig_rain = px.bar(region_data, x="date", y="rainfall", title="Curah Hujan (mm)")
        st.plotly_chart(fig_rain, use_container_width=True)


    st.markdown("---")


    # ============================
    # 6. INPUT PREDIKSI
    # ============================

    st.subheader("🧪 Input Parameter Prediksi")

    col1, col2, col3 = st.columns(3)

    temp = col1.number_input("🌡 Suhu saat ini (°C)", 10, 40, 28)
    humidity = col2.number_input("💧 Kelembapan (%)", 10, 100, 75)
    wind = col3.number_input("🌬 Kecepatan Angin (km/h)", 0, 120, 15)

    future_days = st.slider("⏳ Prediksi untuk berapa hari ke depan?", 1, 14, 7)


    # ============================
    # 7. PREDIKSI
    # ============================

    if st.button("🚀 Prediksi Cuaca"):

        future_dates = [datetime.date.today() + datetime.timedelta(days=i) for i in range(future_days)]

        pred_input = np.array([[temp, humidity, wind] for _ in range(future_days)])

        predictions = model.predict(pred_input)

        result_df = pd.DataFrame({
            "Tanggal": future_dates,
            "Prediksi Curah Hujan (mm)": predictions
        })

        st.success("🎉 Prediksi berhasil!")

        st.dataframe(result_df)


        # ============================
        # 8. HASIL DALAM BENTUK GRAFIK
        # ============================

        fig_result = px.line(result_df, x="Tanggal", y="Prediksi Curah Hujan (mm)",
                             markers=True, title="📈 Grafik Prediksi Curah Hujan")
        st.plotly_chart(fig_result, use_container_width=True)


        # ============================
        # 9. KARTU INFORMASI
        # ============================

        st.markdown("### 📌 Ringkasan Prediksi")
        colA, colB, colC = st.columns(3)

        with colA:
            st.markdown(f"<div class='card'>Rata-rata Curah Hujan:<br><span class='metric-value'>{round(result_df['Prediksi Curah Hujan (mm)'].mean(), 2)} mm</span></div>", unsafe_allow_html=True)

        with colB:
            st.markdown(f"<div class='card'>Hujan Tertinggi:<br><span class='metric-value'>{round(result_df['Prediksi Curah Hujan (mm)'].max(), 2)} mm</span></div>", unsafe_allow_html=True)

        with colC:
            st.markdown(f"<div class='card'>Hujan Terendah:<br><span class='metric-value'>{round(result_df['Prediksi Curah Hujan (mm)'].min(), 2)} mm</span></div>", unsafe_allow_html=True)


# ============================
# FOOTER
# ============================

st.markdown("""
<hr>
<p style='text-align:center; color:white;'>🚀 Dibuat untuk Analisis Cuaca Papua Barat — by Zahra</p>
""", unsafe_allow_html=True)
