import streamlit as st
# Coba gunakan cara import ini jika cara pertama gagal terus
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="JODJO - Order Dashboard", layout="wide")

st.title("🚀 JODJO Dashboard Order")

# 1. KONEKSI DATA
conn = st.connection("gsheets", type=GSheetsConnection)
url_sheet = "https://docs.google.com/spreadsheets/d/15ud5cMl-Pk_uh2tSG_MfwIyAlPMvZNxg1UehegsbHA4/edit"

try:
    # Membaca sheet 'order'
    df = conn.read(spreadsheet=url_sheet, worksheet="order")
    
    # 2. PENGOLAHAN TANGGAL (yyyy-mm-dd hh:mm:ss)
    # Membersihkan data jika ada baris kosong
    df = df.dropna(subset=['tanggal transaksi'])
    
    # Konversi ke datetime
    df['tanggal transaksi'] = pd.to_datetime(df['tanggal transaksi'])
    df['tahun'] = df['tanggal transaksi'].dt.year
    df['bulan_nama'] = df['tanggal transaksi'].dt.strftime('%B')
    df['bulan_angka'] = df['tanggal transaksi'].dt.month
    df['tanggal_saja'] = df['tanggal transaksi'].dt.date

    # 3. SIDEBAR FILTER TAHUN
    list_tahun = sorted(df['tahun'].unique().tolist(), reverse=True)
    selected_year = st.sidebar.selectbox("📅 Pilih Tahun", list_tahun)

    # Filter data tahunan
    df_yearly = df[df['tahun'] == selected_year]

    # 4. GRAFIK AREA BULANAN
    st.subheader(f"📈 Tren Order JODJO - Tahun {selected_year}")
    
    # Menghitung jumlah order per bulan
    monthly_data = df_yearly.groupby(['bulan_angka', 'bulan_nama']).size().reset_index(name='Jumlah Order')
    monthly_data = monthly_data.sort_values('bulan_angka')
    
    # Tampilkan Grafik
    st.area_chart(monthly_data.set_index('bulan_nama')['Jumlah Order'], color="#2ecc71")

    st.markdown("---")

    # 5. FILTER BULAN UNTUK DETAIL CARD
    # Agar interaktif, pilih bulan untuk melihat siapa top user & driver di bulan itu
    list_bulan = monthly_data['bulan_nama'].tolist()
    col_filter, col_empty = st.columns([1, 2])
    with col_filter:
        selected_month = st.selectbox("🔍 Detail Per Bulan:", list_bulan)

    # Data Akhir berdasarkan filter Tahun & Bulan
    df_final = df_yearly[df_yearly['bulan_nama'] == selected_month]

    # 6. CARD INFORMASI (METRICS)
    st.subheader(f"📊 Ringkasan Aktivitas - {selected_month} {selected_year}")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        if not df_final.empty:
            top_user = df_final['username'].value_counts().idxmax()
            order_count = df_final['username'].value_counts().max()
            st.metric("Pelanggan Teraktif", top_user, f"{order_count} Order")
        else:
            st.metric("Pelanggan Teraktif", "-", "0 Order")

    with c2:
        if not df_final.empty:
            top_driver = df_final['driver'].value_counts().idxmax()
            trip_count = df_final['driver'].value_counts().max()
            st.metric("Driver Terlaris", top_driver, f"{trip_count} Trip")
        else:
            st.metric("Driver Terlaris", "-", "0 Trip")

    with c3:
        # Menghitung total tarif
        total_omzet = df_final['tarif'].sum() if not df_final.empty else 0
        st.metric("Total Omzet", f"Rp {total_omzet:,.0f}")

    st.markdown("---")

    # 7. TABEL DATA DETAIL
    st.subheader(f"📋 Daftar Transaksi {selected_month}")
    # Menampilkan kolom yang relevan saja
    st.dataframe(
        df_final[['kode order', 'username', 'driver', 'tarif', 'asal', 'tujuan', 'tanggal transaksi']], 
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.error(f"Terjadi kesalahan saat memproses data: {e}")
    st.info("Pastikan nama kolom di Google Sheets Anda sesuai dengan kode (cek spasi atau huruf kapital).")
