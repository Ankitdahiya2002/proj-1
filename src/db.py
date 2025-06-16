import os
import sys
import sqlite3
from datetime import datetime, timedelta
import pandas as pd

DB_FILE = "omnisicient.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user',
        blocked INTEGER DEFAULT 0,
        reset_token TEXT,
        reset_token_expiry DATETIME,
        name TEXT,
        profession TEXT,
        verified INTEGER DEFAULT 0,
        verification_token TEXT
    )
    """)

    # Safe ALTER for verification_token_expiry
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN verification_token_expiry TEXT")
    except sqlite3.OperationalError:
        pass  # Column likely exists

    # Email logs table
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

    # Chats table
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

    # Uploaded files table
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

# User functions
def create_user(email, password_hash, name=None, profession=None, role='user', verification_token=None):
    conn = get_connection()
    cursor = conn.cursor()
    expiry = (datetime.now() + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("""
            INSERT INTO users (email, password, name, profession, role, verification_token, verification_token_expiry)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (email, password_hash, name, profession, role, verification_token, expiry))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def verify_user_token(token):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email, verification_token_expiry FROM users WHERE verification_token = ?", (token,))
    user = cursor.fetchone()

    if user:
        expiry = user["verification_token_expiry"]
        if expiry and datetime.now() <= datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S"):
            cursor.execute("""
                UPDATE users 
                SET verified = 1, verification_token = NULL, verification_token_expiry = NULL 
                WHERE verification_token = ?
            """, (token,))
            conn.commit()
            conn.close()
            return True
    conn.close()
    return False

def update_reset_token(email, token, expiry):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE email = ?",
        (token, expiry.strftime('%Y-%m-%d %H:%M:%S'), email)
    )
    conn.commit()
    conn.close()

def reset_password(email, new_password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET password = ?, reset_token = NULL, reset_token_expiry = NULL 
        WHERE email = ?
    """, (new_password_hash, email))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return [dict(user) for user in users]

def is_user_verified(email):
    user = get_user(email)
    return user and user.get("verified") == 1

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

# Chat functions
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

# File functions
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

# Safe database initialization with corruption handling
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
