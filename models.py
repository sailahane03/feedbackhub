from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db

def authenticate_user(username, password):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash, role FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()

    if row and (row[1] == "" or check_password_hash(row[1], password)):
        return {"id": row[0], "role": row[2]}
    return None


def create_user(username, password):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'user')",
        (username, generate_password_hash(password))
    )
    conn.commit()
    conn.close()


def submit_feedback(user_id, subject, rating, comments):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO feedback (user_id, subject, rating, comments) VALUES (?, ?, ?, ?)",
        (user_id, subject, rating, comments)
    )
    conn.commit()
    conn.close()

