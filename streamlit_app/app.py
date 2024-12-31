import streamlit as st

# Konfigurasi halaman utama
st.set_page_config(page_title="Chatbot Konsultasi Gizi dan Stunting", layout="centered")

# Periksa apakah pengguna sudah login
if "token" not in st.session_state:
    st.warning("Anda belum login. Silakan login pada menu di samping.")
    st.stop()

# Halaman utama
st.title("Selamat Datang di Chatbot Gizi & Stunting!")
st.write("Silakan gunakan menu di samping untuk navigasi.")
