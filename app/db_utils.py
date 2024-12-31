import mysql.connector
from mysql.connector import Error
import uuid

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'chatbot_gizi_stunting'
}

# Fungsi koneksi MySQL
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None

# Membuat tabel jika belum ada
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabel Users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabel Sessions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(255) UNIQUE NOT NULL,
            user_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabel Chat History
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            user_query TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

# Fungsi untuk registrasi pengguna baru
def register_user(username: str, hashed_password: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        return True
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

# Fungsi untuk login pengguna
def authenticate_user(username: str, hashed_password: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = %s AND password = %s", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

# Fungsi untuk membuat session baru
def create_new_session(user_id: int):
    conn = get_db_connection()
    session_id = str(uuid.uuid4())
    cursor = conn.cursor()
    cursor.execute('INSERT INTO sessions (session_id, user_id) VALUES (%s, %s)', (session_id, user_id))
    conn.commit()
    conn.close()
    return session_id

def get_chat_history(session_id: str):
    """
    Fungsi untuk mengambil riwayat percakapan berdasarkan session ID dari database MySQL.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # dictionary=True untuk menggunakan nama kolom
    query = """
        SELECT user_query, ai_response
        FROM chat_history
        WHERE session_id = %s
        ORDER BY created_at
    """
    cursor.execute(query, (session_id,))
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
    cursor = conn.cursor()
    cursor.execute('INSERT INTO chat_history (session_id, user_query, ai_response) VALUES (%s, %s, %s)',(session_id, user_query, ai_response))
    conn.commit()
    conn.close()

# Fungsi untuk mengambil semua sesi berdasarkan user ID
def get_user_sessions(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT session_id, created_at FROM sessions WHERE user_id = %s', (user_id,))
    sessions = [{"session_id": row[0], "created_at": row[1]} for row in cursor.fetchall()]
    conn.close()
    return sessions

# Inisialisasi tabel
create_tables()
