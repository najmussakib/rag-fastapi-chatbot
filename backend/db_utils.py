import sqllite3
from datetime import datetime

DB_NAME = "rag_app.db"

def get_db_connection():
    conn = sqllite3.connect(DB_NAME)
    conn.row_factory = sqllite3.Row
    return conn

# Creating DB Tables
def create_appication_logs():
    """Stores chat history and model responses."""
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS application_logs
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_query TEXT,
                gpt_response TEXT,
                model TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.close()

def create_document_store():
    """Keeps track of uploaded documents."""
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS document_store
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 filename TEXT,
                 upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.close()

# Managing Chat Logs: inserting new chat logs and retrieving chat history for a given session.
def insert_application_logs(session_id, user_query, gpt_response, model):
    conn = get_db_connection()
    conn.execute('INSERT INTO application_logs(session_id, user_query, gpt_response, model) VALUE(?, ?, ?, ?)',
                 (session_id, user_query, gpt_response, model))
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_query, gpt_response FROM application_logs WHERE session_id = ? ORDER BY create_at',
                   (session_id,))
    messages = []
    for row in cursor.fetchall():
        messages.extend([
            {"role": "human", "content": row['user_query']},
            {"role": "ai", "content": row['gpt_response']}
        ])
    conn.close()
    return messages

# Managing Document Records : CRUD Operations
def insert_document_record(filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO document_store (filename) VALUES (?)',
                   (filename,))
    file_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return file_id

def get_all_documents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, filename, uplaod_timestamp FROM document_store ORDER BY upload_timestamp DESC')
    documents = cursor.fetchall()
    conn.close()
    return [dict(doc) for doc in documents]

def delete_document_record(file_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM document_store WHERE id = ?',
                 (file_id,))
    conn.commit()
    conn.close()
    return True

# Initialize the database tables
create_appication_logs()
create_document_store()
