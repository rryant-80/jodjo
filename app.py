import streamlit as st
# Coba gunakan cara import ini jika cara pertama gagal terus
from streamlit_gsheets import GSheetsConnection 

conn = st.connection("gsheets", type=GSheetsConnection)

df_order = conn.read(
    spreadsheet="https://docs.google.com/spreadsheets/d/15ud5cMl-Pk_uh2tSG_MfwIyAlPMvZNxg1UehegsbHA4/edit",
    worksheet="order"
)

st.write(df_order)
