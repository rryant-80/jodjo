import streamlit as st
# Coba gunakan cara import ini jika cara pertama gagal terus
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Jodjo Dashboard Order", layout="wide")

st.title("🚀 Jodjo Dashboard Order")

# 1. KONEKSI & AMBIL DATA
conn = st.connection("gsheets", type=GSheetsConnection)
url_sheet = "https://docs.google.com/spreadsheets/d/15ud5cMl-Pk_uh2tSG_MfwIyAlPMvZNxg1UehegsbHA4/edit"

try:
    # Ambil data dari sheet 'order'
    df = conn.read(spreadsheet=url_sheet, worksheet="order")
    
    # Konversi kolom tanggal ke format datetime agar bisa diolah (Sesuaikan nama kolom)
    # Pastikan di Google Sheets kolom tanggal namanya 'tanggal'
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    df['tahun'] = df['tanggal'].dt.year
    df['bulan_nama'] = df['tanggal'].dt.strftime('%B')
    df['bulan_angka'] = df['tanggal'].dt.month

    # 2. FILTER TAHUN
    list_tahun = sorted(df['tahun'].unique().tolist(), reverse=True)
    selected_year = st.sidebar.selectbox("📅 Pilih Tahun", list_tahun)

    # Filter data berdasarkan tahun
    df_yearly = df[df['tahun'] == selected_year]

    # 3. GRAFIK CHART AREA PER BULAN
    st.subheader(f"📈 Tren Order Tahun {selected_year}")
    
    # Kelompokkan data per bulan
    monthly_data = df_yearly.groupby(['bulan_angka', 'bulan_nama']).size().reset_index(name='Jumlah Order')
    monthly_data = monthly_data.sort_values('bulan_angka')

    # Tampilkan Chart Area
    st.area_chart(monthly_data.set_index('bulan_nama')['Jumlah Order'], color="#2ecc71")

    # 4. FILTER BULAN (Untuk Card Informasi)
    # Gunakan selectbox untuk memilih bulan yang ingin dilihat detailnya
    list_bulan = monthly_data['bulan_nama'].tolist()
    selected_month = st.selectbox("🔍 Pilih Bulan untuk Detail Informasi", list_bulan)

    # Data difilter berdasarkan Tahun & Bulan pilihan
    df_final = df_yearly[df_yearly['bulan_nama'] == selected_month]

    st.markdown("---")
    st.subheader(f"📊 Informasi Detail - {selected_month} {selected_year}")

    # 5. CARD INFORMASI (Metrics)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Jumlah orderan berdasarkan Top Username
        top_user = df_final['username'].value_counts().idxmax() if not df_final.empty else "-"
        count_user = df_final['username'].value_counts().max() if not df_final.empty else 0
        st.metric("Top Pengguna", top_user, f"{count_user} Order")

    with col2:
        # Jumlah trip berdasarkan Top Driver
        top_driver = df_final['driver'].value_counts().idxmax() if not df_final.empty else "-"
        count_driver = df_final['driver'].value_counts().max() if not df_final.empty else 0
        st.metric("Top Driver", top_driver, f"{count_driver} Trip")

    with col3:
        # Total Tarif (Omzet)
        # Pastikan kolom tarif bernama 'tarif' atau 'harga' di Google Sheet
        total_tarif = df_final['tarif'].sum() if not df_final.empty else 0
        st.metric("Total Omzet", f"Rp {total_tarif:,.0f}")

    st.markdown("---")
    
    # Tampilkan Tabel Data Terfilter
    st.subheader("📋 Daftar Transaksi")
    st.dataframe(df_final[['kode', 'username', 'driver', 'tarif', 'tanggal']], use_container_width=True)

except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")
    st.info("Pastikan nama kolom di Google Sheets sesuai (tanggal, username, driver, tarif)")
