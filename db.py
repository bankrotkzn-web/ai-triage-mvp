import sqlite3

def init_db():
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT,
            channel TEXT,
            text TEXT,
            category TEXT,
            draft_reply TEXT,
            confidence TEXT,
            escalate BOOLEAN,
            error TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_ticket(client_id, channel, text, category, draft_reply, confidence, escalate, error):
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tickets (client_id, channel, text, category, draft_reply, confidence, escalate, error)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (client_id, channel, text, category, draft_reply, confidence, escalate, error))
    conn.commit()
    conn.close()