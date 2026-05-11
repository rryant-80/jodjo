import streamlit as st
# Coba gunakan cara import ini jika cara pertama gagal terus
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Jodjo Dashboard", layout="wide")

# 1. Judul Dashboard
st.title("🚀 Jodjo Dashboard Sulteng")

# 2. Inisialisasi Koneksi
conn = st.connection("gsheets", type=GSheetsConnection)

# Tentukan URL Google Sheets Bapak
url_sheet = "https://docs.google.com/spreadsheets/d/15ud5cMl-Pk_uh2tSG_MfwIyAlPMvZNxg1UehegsbHA4/edit"

# 3. Tarik Data
df_order = conn.read(spreadsheet=url_sheet, worksheet="order")

# 4. Tampilkan Ringkasan (Metric)
total_order = len(df_order)
total_omzet = df_order['total'].sum() # Pastikan nama kolom 'total' sesuai di Sheet

col1, col2 = st.columns(2)
col1.metric("Total Transaksi", f"{total_order} Order")
col2.metric("Total Omzet", f"Rp {total_omzet:,.0f}")

# 5. Tambahkan Grafik Area
st.subheader("📈 Tren Order Jodjo")
# Mengasumsikan ada kolom 'tanggal transaksi'
if 'tanggal transaksi' in df_order.columns:
    df_order['tanggal transaksi'] = pd.to_datetime(df_order['tanggal transaksi'])
    chart_data = df_order.groupby('tanggal transaksi').size()
    st.area_chart(chart_data)

# 6. Tampilkan Tabel Utama
st.subheader("📋 Detail Data")
st.dataframe(df_order, use_container_width=True)
