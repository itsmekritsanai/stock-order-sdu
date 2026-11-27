"""
Database Connection Pooling & Auto-Migration (backend/database.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

import threading
try:
    from config import CONFIG, IS_POSTGRES, get_server_attr
except ImportError:
    from backend.config import CONFIG, IS_POSTGRES, get_server_attr

_SCHEMA_CHECKED = False
_PG_POOL = None
_PG_POOL_KEY = None
_PG_POOL_LOCK = threading.Lock()


class _PooledPgConnection:
    """Wrapper around a psycopg2 pooled connection so conn.close() safely returns it to the pool."""

    def __init__(self, pool, raw_conn):
        self._pool = pool
        self._conn = raw_conn
        self._returned = False

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def cursor(self, *args, **kwargs):
        return self._conn.cursor(*args, **kwargs)

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        if self._returned:
            return
        self._returned = True
        try:
            if not self._conn.closed:
                try:
                    self._conn.rollback()
                except Exception:
                    pass
                self._pool.putconn(self._conn)
            else:
                self._pool.putconn(self._conn, close=True)
        except Exception:
            try:
                self._conn.close()
            except Exception:
                pass


def _get_pg_pool():
    """Return or lazily initialize a ThreadedConnectionPool for PostgreSQL."""
    global _PG_POOL, _PG_POOL_KEY
    from psycopg2.extras import RealDictCursor
    from psycopg2.pool import ThreadedConnectionPool

    pool_key = (
        CONFIG["DB_HOST"],
        CONFIG["DB_PORT"],
        CONFIG["DB_USER"],
        CONFIG["DB_PASSWORD"],
        CONFIG["DB_NAME"],
    )
    with _PG_POOL_LOCK:
        if _PG_POOL is None or _PG_POOL_KEY != pool_key:
            if _PG_POOL is not None:
                try:
                    _PG_POOL.closeall()
                except Exception:
                    pass
            _PG_POOL = ThreadedConnectionPool(
                minconn=1,
                maxconn=20,
                host=CONFIG["DB_HOST"],
                port=CONFIG["DB_PORT"],
                user=CONFIG["DB_USER"],
                password=CONFIG["DB_PASSWORD"],
                dbname=CONFIG["DB_NAME"],
                cursor_factory=RealDictCursor,
            )
            _PG_POOL_KEY = pool_key
        return _PG_POOL


def ensure_database_schema(conn=None):
    """Idempotently ensure required columns and default data exist in PostgreSQL or MySQL."""
    global _SCHEMA_CHECKED
    if _SCHEMA_CHECKED:
        return
    try:
        from auth import hash_password
    except ImportError:
        from backend.auth import hash_password

    close_after = False
    if conn is None:
        try:
            conn = call_get_db_connection(include_db=True)
            close_after = True
        except Exception as e:
            print(f"[WARN] Database connection failed during schema check: {e}")
            return

    try:
        with conn.cursor() as cur:
            if IS_POSTGRES:
                cur.execute("SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'role' LIMIT 1;")
                had_role_col = bool(cur.fetchone())
                _ = had_role_col
                cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(100) UNIQUE;")
                cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS password VARCHAR(255) DEFAULT '';")
                cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) NOT NULL DEFAULT 'REQUESTER';")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);")
                cur.execute("ALTER TABLE inventory_items ADD COLUMN IF NOT EXISTS monthly_limit INT NOT NULL DEFAULT 0;")
                cur.execute("ALTER TABLE inventory_items ADD COLUMN IF NOT EXISTS last_unit_price DECIMAL(12, 2) NOT NULL DEFAULT 0.00;")
                cur.execute("ALTER TABLE inventory_items ADD COLUMN IF NOT EXISTS last_restocked_at TIMESTAMP DEFAULT NULL;")
                cur.execute("ALTER TABLE requisitions ADD COLUMN IF NOT EXISTS verified_by VARCHAR(150) DEFAULT NULL;")
                cur.execute("ALTER TABLE requisitions ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP DEFAULT NULL;")
                cur.execute("ALTER TABLE requisitions ADD COLUMN IF NOT EXISTS verified_date VARCHAR(100) DEFAULT NULL;")
                cur.execute("ALTER TABLE requisitions ADD COLUMN IF NOT EXISTS approved_by VARCHAR(150) DEFAULT NULL;")
                cur.execute("ALTER TABLE requisitions ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP DEFAULT NULL;")
                cur.execute("ALTER TABLE requisitions ADD COLUMN IF NOT EXISTS approved_date VARCHAR(100) DEFAULT NULL;")
                cur.execute("ALTER TABLE requisitions ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP DEFAULT NULL;")
                cur.execute("ALTER TABLE requisitions ADD COLUMN IF NOT EXISTS completed_date VARCHAR(100) DEFAULT NULL;")
                cur.execute("ALTER TABLE requisitions ADD COLUMN IF NOT EXISTS rejected_at TIMESTAMP DEFAULT NULL;")
                cur.execute("ALTER TABLE requisitions ADD COLUMN IF NOT EXISTS rejected_date VARCHAR(100) DEFAULT NULL;")
                cur.execute("ALTER TABLE stock_transactions ADD COLUMN IF NOT EXISTS recorded_by VARCHAR(150) DEFAULT NULL;")
                cur.execute("ALTER TABLE stock_transactions ADD COLUMN IF NOT EXISTS unit_price DECIMAL(12, 2) NOT NULL DEFAULT 0.00;")
                cur.execute("ALTER TABLE stock_transactions ADD COLUMN IF NOT EXISTS total_cost DECIMAL(12, 2) NOT NULL DEFAULT 0.00;")
                cur.execute("ALTER TABLE requisitions DROP CONSTRAINT IF EXISTS requisitions_status_check;")
                cur.execute("ALTER TABLE requisitions ADD CONSTRAINT requisitions_status_check CHECK (status IN ('PENDING', 'VERIFIED', 'APPROVED', 'COMPLETED', 'REJECTED'));")
                cur.execute("SELECT 1 FROM departments WHERE full_label = 'กลุ่มงานเคาน์เตอร์บริการ' LIMIT 1;")
                if not cur.fetchone():
                    cur.execute("""
                        INSERT INTO departments (category, name, parent_name, full_label)
                        VALUES ('สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)', 'กลุ่มงานเคาน์เตอร์บริการ', 'สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)', 'กลุ่มงานเคาน์เตอร์บริการ');
                    """)
                cur.execute("SELECT id, password FROM users WHERE password IS NOT NULL AND password <> '' AND password NOT LIKE 'pbkdf2_sha256$%';")
                plain_rows = cur.fetchall()
                if isinstance(plain_rows, list):
                    for prow in plain_rows:
                        uid = prow["id"] if isinstance(prow, dict) else prow[0]
                        raw_pw = prow["password"] if isinstance(prow, dict) else prow[1]
                        if raw_pw and not str(raw_pw).startswith("pbkdf2_sha256$"):
                            cur.execute("UPDATE users SET password = %s WHERE id = %s;", (hash_password(str(raw_pw)), uid))
                cur.execute("""
                    INSERT INTO requisitions (id, date, requester, dept, phone, purpose, status, signature, reject_reason, completed_at, completed_date, rejected_at, rejected_date, created_at, updated_at)
                    VALUES ('REQ-256910-0001', '1 ต.ค. 2569 09:30 น.', 'อาจารย์ผู้แทน โรงเรียนการเรือน', 'โรงเรียนการเรือน', '', 'ใช้สำหรับการจัดการเรียนการสอนและการสอบปฏิบัติการ ประจำภาคการศึกษา 1/2569', 'COMPLETED', 'ผู้รับพัสดุ: อ.ผู้แทน โรงเรียนการเรือน', '', '2026-10-01 03:00:00', '1 ต.ค. 2569 10:00 น.', NULL, '', '2026-10-01 02:30:00', '2026-10-01 03:00:00')
                    ON CONFLICT (id) DO NOTHING;
                """)
                cur.execute("SELECT 1 FROM requisition_items WHERE requisition_id = 'REQ-256910-0001' LIMIT 1;")
                if not cur.fetchone():
                    cur.execute("""
                        INSERT INTO requisition_items (requisition_id, item_id, name, qty_boxes, qty_pieces, total_pieces, unit_box, unit_piece, approved_pieces, pieces_per_box_snapshot)
                        VALUES 
                          ('REQ-256910-0001', 3, 'กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)', 0, 500, 500, 'กล่อง', 'ใบ', 500, 2000),
                          ('REQ-256910-0001', 7, 'กระดาษลายเส้น (ห่อละ 500 แผ่น)', 1, 0, 500, 'ห่อ', 'แผ่น', 500, 500);
                    """)
                else:
                    cur.execute("""
                        DELETE FROM requisition_items
                        WHERE requisition_id = 'REQ-256910-0001'
                          AND id NOT IN (
                            SELECT MIN(id) FROM requisition_items WHERE requisition_id = 'REQ-256910-0001' GROUP BY item_id
                          );
                    """)
                cur.execute("SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE(MAX(id), 1)) FROM users;")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS quota_rules (
                      id SERIAL PRIMARY KEY,
                      target_type VARCHAR(20) NOT NULL CHECK (target_type IN ('USER', 'DEPT')),
                      target_key VARCHAR(255) NOT NULL,
                      item_id INT NOT NULL DEFAULT 0,
                      monthly_limit INT NOT NULL DEFAULT 0,
                      note VARCHAR(255) DEFAULT '',
                      updated_by VARCHAR(150) DEFAULT '',
                      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      UNIQUE (target_type, target_key, item_id)
                    );
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_quota_target ON quota_rules (target_type, target_key);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_req_dept ON requisitions (dept);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_tx_created_at ON stock_transactions (created_at);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_tx_type_created_at ON stock_transactions (transaction_type, created_at);")
                cur.execute("""
                    CREATE OR REPLACE FUNCTION update_updated_at_column()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.updated_at = CURRENT_TIMESTAMP;
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                """)
                cur.execute("DROP TRIGGER IF EXISTS trg_quota_rules_updated_at ON quota_rules;")
                cur.execute("CREATE TRIGGER trg_quota_rules_updated_at BEFORE UPDATE ON quota_rules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
            else:
                cur.execute("""
                    SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users' AND COLUMN_NAME = 'username';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE `users` ADD COLUMN `username` VARCHAR(100) UNIQUE AFTER `name`;")
                    cur.execute("ALTER TABLE `users` ADD COLUMN `password` VARCHAR(255) DEFAULT '' AFTER `username`;")
                cur.execute("""
                    SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users' AND COLUMN_NAME = 'role';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE `users` ADD COLUMN `role` VARCHAR(50) NOT NULL DEFAULT 'REQUESTER' AFTER `password`;")
                cur.execute("SELECT id, password FROM users WHERE password IS NOT NULL AND password <> '' AND password NOT LIKE 'pbkdf2_sha256$%';")
                plain_rows_my = cur.fetchall()
                if isinstance(plain_rows_my, list):
                    for prow in plain_rows_my:
                        uid = prow["id"] if isinstance(prow, dict) else prow[0]
                        raw_pw = prow["password"] if isinstance(prow, dict) else prow[1]
                        if raw_pw and not str(raw_pw).startswith("pbkdf2_sha256$"):
                            cur.execute("UPDATE users SET password = %s WHERE id = %s;", (hash_password(str(raw_pw)), uid))
                cur.execute("""
                    SELECT COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'requisitions' AND COLUMN_NAME = 'status';
                """)
                status_col = cur.fetchone()
                if status_col and "VERIFIED" not in str(status_col.get("COLUMN_TYPE", "")):
                    cur.execute("ALTER TABLE `requisitions` MODIFY COLUMN `status` ENUM('PENDING', 'VERIFIED', 'APPROVED', 'COMPLETED', 'REJECTED') NOT NULL DEFAULT 'PENDING';")
                cur.execute("""
                    SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'requisitions' AND COLUMN_NAME = 'completed_at';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE `requisitions` ADD COLUMN `completed_at` DATETIME DEFAULT NULL AFTER `reject_reason`;")
                    cur.execute("ALTER TABLE `requisitions` ADD COLUMN `completed_date` VARCHAR(100) DEFAULT NULL AFTER `completed_at`;")
                    cur.execute("ALTER TABLE `requisitions` ADD COLUMN `rejected_at` DATETIME DEFAULT NULL AFTER `completed_date`;")
                    cur.execute("ALTER TABLE `requisitions` ADD COLUMN `rejected_date` VARCHAR(100) DEFAULT NULL AFTER `rejected_at`;")
                    cur.execute("ALTER TABLE `requisitions` ADD COLUMN `verified_by` VARCHAR(150) DEFAULT NULL;")
                    cur.execute("ALTER TABLE `requisitions` ADD COLUMN `verified_at` DATETIME DEFAULT NULL;")
                    cur.execute("ALTER TABLE `requisitions` ADD COLUMN `verified_date` VARCHAR(100) DEFAULT NULL;")
                    cur.execute("ALTER TABLE `requisitions` ADD COLUMN `approved_by` VARCHAR(150) DEFAULT NULL;")
                    cur.execute("ALTER TABLE `requisitions` ADD COLUMN `approved_at` DATETIME DEFAULT NULL;")
                    cur.execute("ALTER TABLE `requisitions` ADD COLUMN `approved_date` VARCHAR(100) DEFAULT NULL;")
                cur.execute("""
                    SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'inventory_items' AND COLUMN_NAME = 'monthly_limit';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE `inventory_items` ADD COLUMN `monthly_limit` INT NOT NULL DEFAULT 0;")
                    cur.execute("ALTER TABLE `inventory_items` ADD COLUMN `last_restocked_at` DATETIME DEFAULT NULL;")
                cur.execute("""
                    SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'stock_transactions' AND COLUMN_NAME = 'recorded_by';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE `stock_transactions` ADD COLUMN `recorded_by` VARCHAR(150) DEFAULT NULL;")
                cur.execute("""
                    SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'inventory_items' AND COLUMN_NAME = 'last_unit_price';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE `inventory_items` ADD COLUMN `last_unit_price` DECIMAL(12, 2) NOT NULL DEFAULT 0.00;")
                cur.execute("""
                    SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'stock_transactions' AND COLUMN_NAME = 'unit_price';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE `stock_transactions` ADD COLUMN `unit_price` DECIMAL(12, 2) NOT NULL DEFAULT 0.00;")
                    cur.execute("ALTER TABLE `stock_transactions` ADD COLUMN `total_cost` DECIMAL(12, 2) NOT NULL DEFAULT 0.00;")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS `quota_rules` (
                      `id` INT AUTO_INCREMENT PRIMARY KEY,
                      `target_type` ENUM('USER', 'DEPT') NOT NULL,
                      `target_key` VARCHAR(255) NOT NULL,
                      `item_id` INT NOT NULL DEFAULT 0,
                      `monthly_limit` INT NOT NULL DEFAULT 0,
                      `note` VARCHAR(255) DEFAULT '',
                      `updated_by` VARCHAR(150) DEFAULT '',
                      `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                      UNIQUE KEY `uq_quota_target_item` (`target_type`, `target_key`, `item_id`),
                      INDEX `idx_quota_target` (`target_type`, `target_key`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """)
        conn.commit()
        _SCHEMA_CHECKED = True
    except Exception as err:
        try:
            conn.rollback()
        except Exception:
            pass
        print(f"[WARN] Schema auto-migration skipped or non-fatal error: {err}")
    finally:
        if close_after:
            conn.close()


def get_db_connection(include_db=True):
    """Create or borrow a database connection (PostgreSQL 17 with ThreadedConnectionPool or MySQL)."""
    db_type = CONFIG.get("DB_TYPE", "postgres").lower()
    if db_type in ("postgres", "postgresql"):
        import psycopg2
        from psycopg2.extras import RealDictCursor

        if include_db:
            pool = _get_pg_pool()
            raw_conn = pool.getconn()
            if raw_conn.closed:
                pool.putconn(raw_conn, close=True)
                raw_conn = pool.getconn()
            raw_conn.autocommit = False
            conn = _PooledPgConnection(pool, raw_conn)
            if not _SCHEMA_CHECKED:
                ensure_database_schema(conn)
            return conn

        conn = psycopg2.connect(
            host=CONFIG["DB_HOST"],
            port=CONFIG["DB_PORT"],
            user=CONFIG["DB_USER"],
            password=CONFIG["DB_PASSWORD"],
            dbname="postgres",
            cursor_factory=RealDictCursor,
        )
        conn.autocommit = False
        return conn

    db_name = CONFIG["DB_NAME"] if include_db else None
    try:
        import pymysql
        import pymysql.cursors

        conn = pymysql.connect(
            host=CONFIG["DB_HOST"],
            port=CONFIG["DB_PORT"],
            user=CONFIG["DB_USER"],
            password=CONFIG["DB_PASSWORD"],
            database=db_name,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
        if not _SCHEMA_CHECKED and include_db:
            ensure_database_schema(conn)
        return conn
    except ImportError:
        import mysql.connector  # type: ignore[import-not-found]

        conn = mysql.connector.connect(
            host=CONFIG["DB_HOST"],
            port=CONFIG["DB_PORT"],
            user=CONFIG["DB_USER"],
            password=CONFIG["DB_PASSWORD"],
            database=db_name,
            charset="utf8mb4",
            autocommit=False,
        )
        if not _SCHEMA_CHECKED and include_db:
            ensure_database_schema(conn)
        return conn


def call_get_db_connection(*args, **kwargs):
    """Invoke server.get_db_connection (respecting unittest.mock.patch on server.get_db_connection)."""
    fn = get_server_attr("get_db_connection", get_db_connection)
    return fn(*args, **kwargs)


def dict_cursor(conn):
    """Return a dictionary cursor compatible with psycopg2, PyMySQL, and mysql-connector."""
    try:
        return conn.cursor(dictionary=True)
    except TypeError:
        return conn.cursor()
