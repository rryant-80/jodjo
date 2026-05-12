import streamlit as st
from st_gsheets_connection import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="JODJO Dashboard Order",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"   # Lebih baik untuk mobile
)

# ================== CUSTOM CSS - MODERN ELEGANT ==================
st.markdown("""
<style>
    .main {background-color: #0F172A;}
    .stApp {background-color: #0F172A;}
    
    h1, h2, h3 {
        color: #67E8F9;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1E2937, #334155);
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border: 1px solid #334155;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .stPlotlyChart {
        background-color: #1E2937;
        border-radius: 16px;
        padding: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .sidebar .css-1d391kg {
        background-color: #1E2937;
    }
    
    .stSelectbox label, .stMultiSelect label {
        color: #CBD5E1;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.title("🚀 JODJO Dashboard Order")
st.markdown("**Monitoring Real-time • Order Analytics**")

# ================== KONEKSI DATA ==================
conn = st.connection("gsheets", type=GSheetsConnection)
url_sheet = "https://docs.google.com/spreadsheets/d/15ud5cMl-Pk_uh2tSG_MfwIyAlPMvZNxg1UehegsbHA4/edit"

try:
    df = conn.read(spreadsheet=url_sheet, worksheet="order")
    
    # Pembersihan Data
    df = df.dropna(subset=['tanggal transaksi', 'kode order'])
    df['tanggal transaksi'] = pd.to_datetime(df['tanggal transaksi'])
    df['tahun'] = df['tanggal transaksi'].dt.year
    df['bulan_nama'] = df['tanggal transaksi'].dt.strftime('%B')
    df['bulan_angka'] = df['tanggal transaksi'].dt.month

    # ================== FILTER RAMPING ==================
    col1, col2 = st.columns([1, 3])
    with col1:
        list_tahun = sorted(df['tahun'].unique().tolist(), reverse=True)
        selected_year = st.selectbox("📅 Pilih Tahun", list_tahun, index=0)
    
    with col2:
        # Optional: Filter bulan (bisa di-expand nanti)
        st.markdown("")

    # Filter data
    df_yearly = df[df['tahun'] == selected_year]

    # ================== KPI CARDS ==================
    st.markdown(f"### 📊 Ringkasan Tahun {selected_year}")
    
    c1, c2, c3, c4 = st.columns(4)
    
    total_order = len(df_yearly)
    total_omzet = df_yearly['tarif'].sum() if 'tarif' in df_yearly.columns else 0
    avg_order = df_yearly['tarif'].mean() if not df_yearly.empty else 0
    
    with c1:
        st.metric("Total Order", f"{total_order:,}", "📈")
    with c2:
        st.metric("Total Omzet", f"Rp {total_omzet:,.0f}", "💰")
    with c3:
        st.metric("Rata-rata Omzet", f"Rp {avg_order:,.0f}", "📊")
    with c4:
        st.metric("Jumlah Hari Aktif", len(df_yearly['tanggal transaksi'].dt.date.unique()), "📅")

    # ================== AREA CHART - MODERN ==================
    st.markdown(f"### 📈 Tren Order JODJO - Tahun {selected_year}")
    
    monthly_data = df_yearly.groupby(['bulan_angka', 'bulan_nama']).size().reset_index(name='Jumlah Order')
    monthly_data = monthly_data.sort_values('bulan_angka')
    
    fig = px.area(
        monthly_data, 
        x='bulan_nama', 
        y='Jumlah Order',
        title="",
        color_discrete_sequence=['#14B8A6'],
        height=460
    )
    
    fig.update_traces(
        line=dict(width=4),
        fillcolor='rgba(20, 184, 166, 0.35)',
        hovertemplate="<b>%{x}</b><br>Order: %{y:,}<extra></extra>"
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#E2E8F0", size=13),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor="#334155", tickfont=dict(size=13)),
        yaxis=dict(gridcolor="#334155", tickfont=dict(size=13)),
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ================== DETAIL PER BULAN ==================
    list_bulan = monthly_data['bulan_nama'].tolist()
    selected_month = st.selectbox("🔍 Pilih Bulan untuk Detail", list_bulan)

    df_final = df_yearly[df_yearly['bulan_nama'] == selected_month]

    # ================== METRICS DETAIL ==================
    st.subheader(f"📋 Ringkasan {selected_month} {selected_year}")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        top_user = df_final['username'].value_counts().idxmax() if not df_final.empty else "-"
        st.metric("Pelanggan Teraktif", top_user, 
                 f"{df_final['username'].value_counts().max() if not df_final.empty else 0} Order")
    
    with c2:
        top_driver = df_final['nama driver'].value_counts().idxmax() if not df_final.empty else "-"
        st.metric("Driver Terlaris", top_driver, 
                 f"{df_final['nama driver'].value_counts().max() if not df_final.empty else 0} Trip")
    
    with c3:
        omzet_bulan = df_final['tarif'].sum() if not df_final.empty else 0
        st.metric("Omzet Bulan Ini", f"Rp {omzet_bulan:,.0f}")

    # ================== TABEL DETAIL ==================
    st.subheader(f"Daftar Transaksi - {selected_month}")
    st.dataframe(
        df_final[['kode order', 'username', 'nama driver', 'tarif', 'asal', 'tujuan', 'tanggal transaksi']],
        use_container_width=True,
        hide_index=True,
        height=400
    )

except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")
    st.info("Pastikan nama kolom di Google Sheet sudah sesuai dan sheet bernama 'order'.")
