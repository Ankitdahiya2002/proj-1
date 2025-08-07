import os
import sys
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import hashlib

DB_FILE = "omnisicient.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # ✅ Users table (fixed missing field)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        name TEXT,
        profession TEXT,
        verified INTEGER DEFAULT 0,
        verification_token TEXT,
        verification_token_expiry TEXT,
        reset_token TEXT,
        reset_token_expiry TEXT,
        blocked INTEGER DEFAULT 0
    );
    """)

    # ✅ Email logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS email_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipient TEXT,
        subject TEXT,
        status TEXT,
        error TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ✅ Chats table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        user_input TEXT,
        ai_response TEXT,
        thread_id TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_email) REFERENCES users(email)
    )
    """)

    # ✅ Uploaded files table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS uploaded_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        file_name TEXT,
        file_type TEXT,
        extracted_text TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_email) REFERENCES users(email)
    )
    """)

    conn.commit()
    conn.close()

# === User Functions ===

def create_user(email, password_hash, name, profession, verification_token):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        return False

    expiry = (datetime.now() + timedelta(hours=1)).replace(microsecond=0)

    expiry_str = expiry.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO users (email, password, name, profession, verified, verification_token, verification_token_expiry)
        VALUES (?, ?, ?, ?, 0, ?, ?)
    """, (email, password_hash, name, profession, verification_token, expiry_str))

    conn.commit()
    conn.close()
    return True

def verify_user_token(token):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT email, verified, verification_token_expiry
        FROM users
        WHERE verification_token = ?
    """, (token,))
    row = cursor.fetchone()

    if row:
        expiry_str = row["verification_token_expiry"]
        if expiry_str:
            expiry = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
            if datetime.now() > expiry:
                conn.close()
                return False

        if row["verified"]:
            conn.close()
            return True

        cursor.execute("""
            UPDATE users
            SET verified = 1, verification_token = NULL, verification_token_expiry = NULL
            WHERE email = ?
        """, (row["email"],))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False

def get_user(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def is_user_verified(email):
    user = get_user(email)
    return user and user.get("verified") == 1

def update_reset_token(email, token, expiry):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET reset_token = ?, reset_token_expiry = ?
        WHERE email = ?
    """, (token, expiry.strftime("%Y-%m-%d %H:%M:%S"), email))
    conn.commit()
    conn.close()
    

def reset_user_password_by_token(token, new_hashed_password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT email, reset_token_expiry FROM users
        WHERE reset_token = ?
    """, (token,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return False

    email, expiry = user

    # ✅ FIXED: Match format (no microseconds)
    if datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S") < datetime.now():
        conn.close()
        return False  # token expired

    # Update password
    cursor.execute("""
        UPDATE users
        SET password = ?, reset_token = NULL, reset_token_expiry = NULL
        WHERE email = ?
    """, (new_hashed_password, email))

    conn.commit()
    conn.close()
    return True


def reset_password(email, new_hashed_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET password = ?, reset_token = NULL, reset_token_expiry = NULL
        WHERE email = ?
    """, (new_hashed_password, email))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return [dict(user) for user in users]


def verify_user_credentials(email, password):
    import hashlib
    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # 🐞 Debug lines:
    print(f"[DEBUG] Checking login for: {email}")
    print(f"[DEBUG] Hashed password: {hashed_password}")

    cursor.execute("""
        SELECT * FROM users WHERE email = ? AND password = ?
    """, (email, hashed_password))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        print(f"[DEBUG] ✅ User verified: {user[0]}")
    else:
        print(f"[DEBUG] ❌ Login failed")

    return user is not None



def block_user(email, block=True):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET blocked = ? WHERE email = ?", (1 if block else 0, email))
    conn.commit()
    conn.close()

def count_registered_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

# === Chat Functions ===

def save_chat(user_email, user_input, ai_response, thread_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chats (user_email, user_input, ai_response, thread_id)
        VALUES (?, ?, ?, ?)
    """, (user_email, user_input, ai_response, thread_id))
    conn.commit()
    conn.close()

def get_user_chats(user_email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats WHERE user_email = ? ORDER BY timestamp DESC", (user_email,))
    chats = cursor.fetchall()
    conn.close()
    return chats

def export_chats_to_csv():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM chats", conn)
    conn.close()
    return df.to_csv(index=False).encode('utf-8')

# === File Functions ===

def save_uploaded_file(user_email, file_name, file_type, extracted_text):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO uploaded_files (user_email, file_name, file_type, extracted_text)
        VALUES (?, ?, ?, ?)
    """, (user_email, file_name, file_type, extracted_text))
    conn.commit()
    conn.close()

def get_uploaded_files(user_email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, file_name, file_type, timestamp 
        FROM uploaded_files 
        WHERE user_email = ?
        ORDER BY timestamp DESC
    """, (user_email,))
    files = cursor.fetchall()
    conn.close()
    return [dict(file) for file in files]

def get_file_content(file_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT extracted_text FROM uploaded_files WHERE id = ?", (file_id,))
    result = cursor.fetchone()
    conn.close()
    return result["extracted_text"] if result else None

# === Email Logs ===

def log_email_status(recipient, subject, status, error=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO email_logs (recipient, subject, status, error)
        VALUES (?, ?, ?, ?)
    """, (recipient, subject, status, error))
    conn.commit()
    conn.close()

def get_email_logs(limit=20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT recipient, subject, status, error, timestamp
        FROM email_logs
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# === Safe Init ===

def safe_initialize():
    try:
        create_tables()
    except sqlite3.DatabaseError as e:
        print(f"[ERROR] Database is corrupted: {e}")
        try:
            backup_path = DB_FILE + ".corrupt.bak"
            os.rename(DB_FILE, backup_path)
            print(f"[!] Backed up corrupted DB to: {backup_path}")
        except Exception as backup_err:
            print(f"[!] Backup failed: {backup_err}")
        try:
            os.remove(DB_FILE)
            print("[✓] Corrupted DB deleted. Recreating...")
            create_tables()
            print("[✓] Database recreated successfully.")
        except Exception as final_err:
            print(f"[X] Failed to recreate database: {final_err}")
            sys.exit(1)

if __name__ == "__main__":
    safe_initialize()
