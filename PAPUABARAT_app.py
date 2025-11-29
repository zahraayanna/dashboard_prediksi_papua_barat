import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------
# APP TITLE
# --------------------------
st.title("📊 Dashboard Prediksi Papua Barat")

# --------------------------
# LOAD DATA
# --------------------------
@st.cache_data
def load_data():
    try:
        if "prediksi.xlsx" in os.listdir():
            df = pd.read_excel("prediksi.xlsx")
        else:
            df = pd.read_csv("prediksi.csv")
        df.set_index(df.columns[0], inplace=True)
        return df
    except Exception as e:
        st.error(f"❌ Gagal memuat data: {e}")
        return None


df = load_data()

if df is not None:
    # --------------------------
    # SIDEBAR
    # --------------------------
    st.sidebar.header("⚙ Pengaturan")

    prediksi_list = df.columns.tolist()

    selected_option = st.sidebar.selectbox(
        "Pilih Data Prediksi:",
        options=prediksi_list
    )

    chart_type = st.sidebar.radio(
        "Pilih Jenis Grafik:",
        ["Line", "Area", "Bar"]
    )

    # --------------------------
    # MAIN CONTENT
    # --------------------------
    st.subheader(f"📌 Data Prediksi: **{selected_option}**")

    filtered_df = df[[selected_option]]

    st.write(filtered_df)

    # --------------------------
    # PLOT AREA
    # --------------------------
    st.subheader("📈 Visualisasi Grafik")

    if chart_type == "Line":
        fig = px.line(filtered_df, x=filtered_df.index, y=selected_option, markers=True)

    elif chart_type == "Area":
        fig = px.area(filtered_df, x=filtered_df.index, y=selected_option)

    else:  # Bar chart
        fig = px.bar(filtered_df, x=filtered_df.index, y=selected_option)

    fig.update_layout(
        template="plotly_white",
        title=f"Grafik Prediksi: {selected_option}",
        title_font=dict(size=22),
        xaxis_title="Tahun",
        yaxis_title="Nilai Prediksi",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # --------------------------
    # DOWNLOAD DATA
    # --------------------------
    csv = filtered_df.to_csv().encode('utf-8')
    st.download_button(
        "⬇️ Download data CSV",
        data=csv,
        file_name=f"prediksi_{selected_option}.csv",
        mime="text/csv"
    )

else:
    st.warning("⚠ Data tidak ditemukan. Pastikan file `prediksi.csv` ada di folder project.")
value(), file_name="DSS_Iklim_PapuaBarat.xlsx")



