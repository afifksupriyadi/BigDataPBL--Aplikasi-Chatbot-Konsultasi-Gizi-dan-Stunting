import streamlit as st
import requests

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="Chatbot Konsultasi Gizi dan Stunting", layout="centered")

# URL FastAPI (sesuaikan dengan alamat backend Anda)
BASE_URL = "http://127.0.0.1:8000"

st.title("Chatbot Konsultasi Gizi dan Stunting")

# Form login
username = st.text_input("Username", placeholder="Masukkan username Anda")
password = st.text_input("Password", type="password", placeholder="Masukkan password Anda")
login_button = st.button("Login")

if login_button:
    if not username or not password:
        st.error("Username dan password tidak boleh kosong!")
    else:
        # Kirim permintaan ke endpoint /login
        response = requests.post(
            f"{BASE_URL}/login",
            json={"username": username, "password": password}
        )

        if response.status_code == 200:
            data = response.json()
            st.session_state["token"] = data["access_token"]  # Simpan token
            st.success(f"Login berhasil! Token Anda: {st.session_state['token']}")

            # Pindah ke halaman chat
            st.write("Mengalihkan ke halaman chat...")
            st.experimental_set_query_params(page="Chat")  # Navigasi
        else:
            st.error("Login gagal! Periksa username dan password Anda.")
