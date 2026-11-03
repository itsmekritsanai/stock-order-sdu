"""
1-Click Database Initializer (backend/init_db.py)
Creates the `sdu_inventory` database and imports schema (PostgreSQL 17 or MySQL)
with all 6 tables, departments, 34 stock items, and sample requisitions.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from server import CONFIG, SCHEMA_SQL_PATH, IS_POSTGRES, get_db_connection


def init_database_schema():
    db_engine = "PostgreSQL 17" if IS_POSTGRES else "MySQL"
    print("=" * 65)
    print(f"  ติดตั้งฐานข้อมูล {db_engine}: ระบบคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต")
    print(f"  Target: {CONFIG['DB_USER']}@{CONFIG['DB_HOST']}:{CONFIG['DB_PORT']}/{CONFIG['DB_NAME']}")
    print("=" * 65)

    if not os.path.exists(SCHEMA_SQL_PATH):
        print(f"[!] ไม่พบไฟล์ SQL Schema ที่: {SCHEMA_SQL_PATH}")
        sys.exit(1)

    with open(SCHEMA_SQL_PATH, "r", encoding="utf-8") as f:
        sql_script = f.read()

    if IS_POSTGRES:
        # Check / create database if not exists
        conn_default = get_db_connection(include_db=False)
        conn_default.autocommit = True
        try:
            with conn_default.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (CONFIG["DB_NAME"],))
                if not cur.fetchone():
                    print(f"[*] กำลังสร้างฐานข้อมูล '{CONFIG['DB_NAME']}'...")
                    cur.execute(f'CREATE DATABASE "{CONFIG["DB_NAME"]}"')
                    print(f"[+] สร้างฐานข้อมูล '{CONFIG['DB_NAME']}' สำเร็จ")
                else:
                    print(f"[*] พบฐานข้อมูล '{CONFIG['DB_NAME']}' อยู่แล้ว")
        finally:
            conn_default.close()

        # Connect to sdu_inventory and run schema script
        conn = get_db_connection(include_db=True)
        try:
            with conn.cursor() as cur:
                print(f"[*] กำลังรันสคริปต์ {os.path.basename(SCHEMA_SQL_PATH)}...")
                cur.execute(sql_script)
            conn.commit()
            print("[+] ติดตั้งตารางทั้ง 6 ตาราง และนำเข้าข้อมูลตั้งต้นสำเร็จ 100%!")
        except Exception as e:
            conn.rollback()
            print(f"[!] เกิดข้อผิดพลาดในการรันสคริปต์: {e}")
            raise e
        finally:
            conn.close()
    else:
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
    init_database_schema()
