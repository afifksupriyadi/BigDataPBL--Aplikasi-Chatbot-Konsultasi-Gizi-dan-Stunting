import streamlit as st
import requests

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="Chatbot Konsultasi Gizi dan Stunting", layout="centered")

# Periksa apakah pengguna sudah login
if "token" not in st.session_state:
    st.warning("Anda harus login terlebih dahulu!")
    st.experimental_set_query_params(page="Login")
    st.stop()

st.title("Chatbot Konsultasi Gizi dan Stunting")

# Form pertanyaan
with st.form(key="chat_form"):
    question = st.text_area("Masukkan pertanyaan Anda:")
    session_id = st.text_input("Session ID (opsional):", value="", help="Kosongkan jika ingin membuat sesi baru.")
    submit_button = st.form_submit_button("Kirim")

# Kirim pertanyaan ke backend
if submit_button:
    if not question.strip():
        st.error("Pertanyaan tidak boleh kosong!")
    else:
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            params={"token": st.session_state["token"]},
            json={"question": question, "session_id": session_id}
        )
        if response.status_code == 200:
            data = response.json()
            st.success(f"Jawaban: {data['answer']}")
            st.info(f"Session ID: {data['session_id']}")
        else:
            st.error("Gagal mendapatkan jawaban.")
