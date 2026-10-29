"""
1-Click MySQL Database Initializer (backend/init_db.py)
Creates the `sdu_inventory` database and imports `backend/schema.sql`
with all 5 tables, 90+ SDU departments, 34 stock items, and sample requisitions.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from server import CONFIG, SCHEMA_SQL_PATH, get_db_connection


def init_mysql_schema():
    print("=" * 65)
    print("  ติดตั้งฐานข้อมูล MySQL: ระบบคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต")
    print(f"  Target: {CONFIG['DB_USER']}@{CONFIG['DB_HOST']}:{CONFIG['DB_PORT']}/{CONFIG['DB_NAME']}")
    print("=" * 65)

    if not os.path.exists(SCHEMA_SQL_PATH):
        print(f"[!] ไม่พบไฟล์ SQL Schema ที่: {SCHEMA_SQL_PATH}")
        sys.exit(1)

    with open(SCHEMA_SQL_PATH, "r", encoding="utf-8") as f:
        sql_script = f.read()

    conn = get_db_connection(include_db=False)
    try:
        cur = conn.cursor()
        statements = [s.strip() for s in sql_script.split(";") if s.strip()]
        for stmt in statements:
            cur.execute(stmt)
        conn.commit()
        print("[+] สร้างฐานข้อมูล ตารางทั้ง 5 ตาราง และนำเข้าข้อมูลตั้งต้นสำเร็จ 100%!")
    finally:
        conn.close()


if __name__ == "__main__":
    init_mysql_schema()

