import os
import logging
import uuid
from fastapi import FastAPI, HTTPException, Depends
from model import QueryInput, QueryResponse, UserRegistration
from db_utils import (
    register_user, authenticate_user, create_new_session, 
    get_chat_history, insert_chat_history, get_user_sessions
)
from hashlib import sha256
from langchain_utils import get_rag_chain_full
from dotenv import load_dotenv

# Memuat variabel dari .env
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

# Konfigurasi logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

app = FastAPI()

users = {}  # Simulasi penyimpanan token untuk user (bisa diganti dengan Redis atau database)

def verify_token(token: str):
    logging.info(f"Verifying token: {token}")
    logging.info(f"Current users: {users}")
    if token not in users:
        logging.warning(f"Invalid token: {token}")
        raise HTTPException(status_code=401, detail="Invalid token")
    return users[token]  # Kembalikan user_id yang sesuai

@app.post("/register")
def register(user: UserRegistration):
    hashed_password = sha256(user.password.encode()).hexdigest()
    success = register_user(user.username, hashed_password)
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists")
    logging.info(f"New user registered: {user.username}")
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserRegistration):
    hashed_password = sha256(user.password.encode()).hexdigest()
    user_id = authenticate_user(user.username, hashed_password)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    token = user.username  # Menggunakan username sebagai token
    users[token] = user_id  # Simpan token dengan user_id
    logging.info(f"User logged in: {user.username}, Token: {token}")
    return {"access_token": token, "token_type": "bearer"}

@app.post("/chat", response_model=QueryResponse)
def chat(query_input: QueryInput, token: str = Depends(verify_token)):
    # Validasi user_id dari token
    user_id = token
    
    # Buat session baru jika belum ada
    if not query_input.session_id:
        query_input.session_id = create_new_session(user_id)
        logging.info(f"New session created: User ID {user_id}, Session ID {query_input.session_id}")


    # Ambil chat history berdasarkan session_id
    chat_history = get_chat_history(query_input.session_id)

    # Jalankan RAG Chain
    rag_chain = get_rag_chain_full()
    result = rag_chain.invoke({"input": query_input.question, "chat_history": chat_history})
    answer = result["answer"]

    # Simpan ke database
    insert_chat_history(query_input.session_id, query_input.question, answer)

    # Tambahkan logging
    logging.info(f"Chat request: User ID {user_id}, Session ID {query_input.session_id}, "
                 f"Question: {query_input.question}, Answer: {answer}")
    
    # Kembalikan jawaban dan riwayat percakapan
    return QueryResponse(
        answer=answer,
        user_id=user_id,
        session_id=query_input.session_id,
    )

@app.get("/get-sessions")
def get_sessions(user_id: int = Depends(verify_token)):
    sessions = get_user_sessions(user_id)
    logging.info(f"Sessions retrieved: User ID {user_id}, Total sessions {len(sessions)}")
    return {"sessions": sessions}

@app.post("/logout")
def logout(token: str):
    logging.info(f"Received logout request for token: {token}")
    
    # Validasi token
    if token not in users:
        logging.warning(f"Logout failed: Invalid token {token}")
        raise HTTPException(status_code=401, detail="Invalid token")

    # Hapus token dari dictionary users
    del users[token]
    logging.info(f"User {token} successfully logged out")
    
    return {"message": f"User {token} logged out successfully"}

