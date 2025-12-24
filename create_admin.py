from db import get_db

def create_admin():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, password_hash, role, is_initialized) VALUES ('admin', '', 'admin', 0)"
    )
    conn.commit()
    conn.close()
    print("[✓] Admin user created")

if __name__ == "__main__":
    create_admin()
