"""
Configuration & Core Utilities (backend/config.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

import os
import random
import sys
from datetime import datetime

SYSTEM_VERSION = "3.9.0"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

THAI_MONTHS = [
    "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
    "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."
]

STATUS_THAI_LABELS = {
    "PENDING": "รอคัดกรอง",
    "VERIFIED": "รอหัวหน้าอนุมัติ",
    "APPROVED": "อนุมัติแล้ว รอรับของ",
    "COMPLETED": "จ่ายสำเร็จแล้ว",
    "REJECTED": "ไม่อนุมัติ / ยกเลิก",
}


def load_env_config():
    """Load database, server settings, passwords, and secrets from .env file and environment variables."""
    config = {
        "DB_TYPE": os.environ.get("DB_TYPE", "postgres"),
        "DB_HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "DB_PORT": int(os.environ.get("DB_PORT", "5433")),
        "DB_USER": os.environ.get("DB_USER", "postgres"),
        "DB_PASSWORD": os.environ.get("DB_PASSWORD", "postgrespassword"),
        "DB_NAME": os.environ.get("DB_NAME", "sdu_inventory"),
        "PORT": int(os.environ.get("PORT", "8080")),
        "HOST": os.environ.get("HOST", "127.0.0.1"),
        "BASE_URL": os.environ.get("BASE_URL", "http://localhost:8080"),
        "API_BASE_URL": os.environ.get("API_BASE_URL", "/api"),
        "ALLOWED_ORIGINS": os.environ.get("ALLOWED_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080"),
        "STAFF_USERNAME": os.environ.get("STAFF_USERNAME", "admin_staff"),
        "STAFF_PASSWORD": os.environ.get("STAFF_PASSWORD", "sdu1234"),
        "STAFF_AUTH_SECRET": os.environ.get("STAFF_AUTH_SECRET", "sdu_inventory_staff_secret_token_change_in_production"),
        "ADMIN_PASSWORD_HASH": os.environ.get("ADMIN_PASSWORD_HASH", "sha256_or_bcrypt_hash_placeholder"),
        "DEFAULT_USER_PASSWORD": os.environ.get("DEFAULT_USER_PASSWORD", "sdu1234"),
        "REQUESTER_AUTH_SECRET": os.environ.get("REQUESTER_AUTH_SECRET", "sdu_inventory_requester_secret_token_change_in_production"),
        "AUTH_BYPASS": os.environ.get("AUTH_BYPASS", "false"),
    }
    env_file = os.path.join(PROJECT_ROOT, ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k in ("DB_PORT", "PORT"):
                    try:
                        config[k] = int(v)
                    except ValueError:
                        pass
                else:
                    config[k] = v

    # Real process/container environment variables override .env file defaults
    for k in list(config.keys()):
        if k in os.environ and os.environ[k] != "":
            val = os.environ[k]
            if k in ("DB_PORT", "PORT"):
                try:
                    config[k] = int(val)
                except ValueError:
                    pass
            else:
                config[k] = val
    return config


CONFIG = load_env_config()
IS_POSTGRES = CONFIG.get("DB_TYPE", "postgres").lower() in ("postgres", "postgresql")
SCHEMA_SQL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "schema_postgres.sql" if IS_POSTGRES else "schema.sql"
)


def format_thai_datetime(dt=None):
    """Format datetime as Thai Buddhist Era string (e.g. '29 ต.ค. 2569 14:30 น.')."""
    if dt is None:
        dt = datetime.now()
    thai_year = dt.year + 543
    month_str = THAI_MONTHS[dt.month - 1]
    return f"{dt.day} {month_str} {thai_year} {dt.strftime('%H:%M')} น."


def generate_doc_no():
    """Generate official requisition document number REQ-YYYYMM-XXXX in Buddhist Era."""
    now = datetime.now()
    thai_year = now.year + 543
    month = f"{now.month:02d}"
    rand_digits = random.randint(1000, 9999)
    return f"REQ-{thai_year}{month}-{rand_digits}"


def parse_month_date_range(month_filter: str):
    """Parse YYYY-MM (CE or BE) into SARGable (start_dt, end_dt, doc_prefix) bounds for index-friendly queries."""
    try:
        parts = str(month_filter).strip().split("-")
        y = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 else 1
        if not (1 <= m <= 12):
            return None, None, None
        y_be = y + 543 if y < 2400 else y
        y_ce = y if y < 2400 else y - 543
        start_dt = datetime(y_ce, m, 1, 0, 0, 0)
        end_dt = datetime(y_ce + 1, 1, 1, 0, 0, 0) if m == 12 else datetime(y_ce, m + 1, 1, 0, 0, 0)
        doc_pfx = f"REQ-{y_be}{m:02d}-"
        return start_dt, end_dt, doc_pfx
    except Exception:
        return None, None, None


def get_server_attr(attr_name: str, default_val):
    """Resolve attribute from loaded 'server' module so unittest.mock.patch('server.<attr>') works across submodules."""
    for mod_name in ("server", "backend.server"):
        srv = sys.modules.get(mod_name)
        if srv is not None and hasattr(srv, attr_name):
            return getattr(srv, attr_name)
    return default_val
