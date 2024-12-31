from datetime import datetime
import sqlite3
import uuid

# Nama database
DB_NAME = "chatbot_gizi_stunting.db"

# Fungsi koneksi database
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Membuat tabel jika belum ada
def create_tables():
    conn = get_db_connection()

    # Tabel Users
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')

    # Tabel Sessions
    conn.execute('''CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        user_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )''')

    # Tabel Chat History
    conn.execute('''CREATE TABLE IF NOT EXISTS chat_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        user_query TEXT NOT NULL,
                        ai_response TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                    )''')
    conn.close()

# Fungsi untuk registrasi pengguna baru
def register_user(username: str, hashed_password: str):
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username sudah ada
    finally:
        conn.close()

# Fungsi untuk login pengguna
def authenticate_user(username: str, hashed_password: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    return user["id"] if user else None

# Fungsi untuk membuat session baru
def create_new_session(user_id: int):
    conn = get_db_connection()
    session_id = str(uuid.uuid4())
    conn.execute('INSERT INTO sessions (session_id, user_id) VALUES (?, ?)', (session_id, user_id))
    conn.commit()
    conn.close()
    return session_id

# Fungsi untuk mengambil chat history berdasarkan session ID
def get_chat_history(session_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_query, ai_response FROM chat_history WHERE session_id = ? ORDER BY created_at', (session_id,))
    messages = []
    for row in cursor.fetchall():
        messages.extend([
            {"role": "human", "content": row['user_query']},
            {"role": "ai", "content": row['ai_response']}
        ])
    conn.close()
    return messages

# Fungsi untuk menyimpan chat history
def insert_chat_history(session_id: str, user_query: str, ai_response: str):
    conn = get_db_connection()
    conn.execute('INSERT INTO chat_history (session_id, user_query, ai_response) VALUES (?, ?, ?)',
                 (session_id, user_query, ai_response))
    conn.commit()
    conn.close()

# Fungsi untuk mengambil semua sesi berdasarkan user ID
def get_user_sessions(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT session_id, created_at FROM sessions WHERE user_id = ?', (user_id,))
    sessions = [{"session_id": row["session_id"], "created_at": row["created_at"]} for row in cursor.fetchall()]
    conn.close()
    return sessions

# Inisialisasi tabel
create_tables()
