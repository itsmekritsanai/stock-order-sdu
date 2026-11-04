import os, sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import backend.server as server

conn = server.get_db_connection()
try:
    with server.dict_cursor(conn) as cur:
        cur.execute("SELECT id, username, password FROM users WHERE password IS NOT NULL")
        rows = cur.fetchall()
        migrated = 0
        for row in rows:
            stored = str(row.get("password") or "").strip()
            if stored and not stored.startswith("pbkdf2_sha256$"):
                new_hash = server.hash_password(stored)
                cur.execute("UPDATE users SET password = %s WHERE id = %s", (new_hash, row["id"]))
                migrated += 1
    conn.commit()
    print(f"Successfully migrated {migrated} user passwords to PBKDF2-HMAC-SHA256!")
finally:
    conn.close()
