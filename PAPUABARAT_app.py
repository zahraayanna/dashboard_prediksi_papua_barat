import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# =======================
# CONFIGURASI APP
# =======================
st.set_page_config(page_title="🌦️ Prediksi Iklim Papua Barat", layout="wide")

st.title("🌦️ Decision Support System Iklim - Papua Barat")
st.write("Aplikasi analisis iklim dan prediksi sederhana berbasis tren data historis.")

# Debug: tampilkan daftar file agar user tahu apakah file terbaca
st.sidebar.write("📁 Folder berisi file:")
st.sidebar.write(os.listdir())

DATA_FILE = "PAPUABARAT2.xlsx"


# =======================
# LOAD DATA
# =======================
try:
    df = pd.read_excel(DATA_FILE, sheet_name="Data Harian - Table")

    # pastikan tidak ada duplicate column
    df = df.loc[:, ~df.columns.duplicated()]

    # format tanggal
    df['Tanggal'] = pd.to_datetime(df['Tanggal'], dayfirst=True)
    df['Tahun'] = df['Tanggal'].dt.year
    df['Bulan'] = df['Tanggal'].dt.month

    # variabel yang tersedia
    possible_vars = ["Tn", "Tx", "Tavg", "kelembaban", "curah_hujan", "matahari", "kecepatan_angin"]
    available_vars = [v for v in possible_vars if v in df.columns]

    label_dict = {
        "Tn": "Suhu Minimum (°C)",
        "Tx": "Suhu Maksimum (°C)",
        "Tavg": "Suhu Rata-rata (°C)",
        "kelembaban": "Kelembaban Udara (%)",
        "curah_hujan": "Curah Hujan (mm)",
        "matahari": "Durasi Penyinaran Matahari (jam)",
        "kecepatan_angin": "Kecepatan Angin (km/jam)"
    }

    # =======================
    # AGREGASI BULANAN
    # =======================
    agg = {v: 'mean' for v in available_vars}
    if "curah_hujan" in available_vars:
        agg["curah_hujan"] = "sum"

    monthly_df = df.groupby(["Tahun", "Bulan"]).agg(agg).reset_index()
    monthly_df["Tanggal"] = pd.to_datetime(
        monthly_df["Tahun"].astype(str) + "-" + monthly_df["Bulan"].astype(str) + "-01"
    )

    st.subheader("📊 Data Bulanan Papua Barat")
    st.dataframe(monthly_df)

    # =======================
    # GRAPH SECTION
    # =======================
    st.subheader("📈 Grafik Tren Iklim")

    selected_var = st.selectbox("Pilih Variabel untuk Ditampilkan", available_vars,
                                format_func=lambda x: label_dict[x])

    fig = px.line(
        monthly_df,
        x="Tanggal",
        y=selected_var,
        title=f"Tren {label_dict[selected_var]}",
        markers=True
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # =======================
    # PREDIKSI SEDERHANA
    # =======================
    st.subheader("🔮 Prediksi Tren Sederhana (Moving Average)")

    window_size = st.slider("Panjang Periode Moving Average", 2, 12, 6)

    monthly_df["Prediksi"] = monthly_df[selected_var].rolling(window=window_size).mean()

    fig2 = px.line(
        monthly_df,
        x="Tanggal",
        y=["Prediksi", selected_var],
        labels={"value": "Nilai", "variable": "Tipe Data"},
        title=f"Prediksi Moving Average untuk {label_dict[selected_var]}"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # =======================
    # DOWNLOAD
    # =======================
    st.subheader("📥 Unduh Hasil Analisis")

    export_df = monthly_df[["Tanggal", selected_var, "Prediksi"]]
    csv_file = export_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download CSV",
        data=csv_file,
        file_name=f"Hasil_Prediksi_{selected_var}.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"❌ File '{DATA_FILE}' tidak ditemukan atau format sheet salah.\n\nError: {e}")
    st.info("Pastikan file **PAPUABARAT2.xlsx** ada di folder yang sama dengan `app.py`.")
