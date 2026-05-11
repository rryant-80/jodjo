import streamlit as st
from st_gsheets_connection import GSheetsConnection

# --- BARIS YANG HARUS DITAMBAHKAN ---
# Ini memberikan instruksi kepada Streamlit untuk membuat objek koneksi bernama 'conn'
conn = st.connection("gsheets", type=GSheetsConnection)
# ------------------------------------

# Sekarang 'conn' sudah ada, baris di bawah ini tidak akan error lagi
df_order = conn.read(
    spreadsheet="https://docs.google.com/spreadsheets/d/15ud5cMl-Pk_uh2tSG_MfwIyAlPMvZNxg1UehegsbHA4/edit",
    worksheet="order"
)

st.write(df_order)
