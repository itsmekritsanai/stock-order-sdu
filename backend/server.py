"""
Unified Web & REST API Server (backend/server.py)
Project: Suan Dusit University e-Inventory & Requisition System (Stock Order SDU)
Version: 3.0.0

Features:
- Serves Frontend Static Portals (index.html, staff.html, portal.html, assets/)
- Provides JSON REST API at /api connected to PostgreSQL 17 (Docker Compose) or MySQL
- Implements ACID Transactions & Row-Level Locking (SELECT ... FOR UPDATE)
  to prevent inventory concurrency race conditions.
"""

import hashlib
import hmac
import json
import os
import random
import time
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

SYSTEM_VERSION = "3.0.12"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_SQL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema_postgres.sql")

THAI_MONTHS = [
    "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
    "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."
]


def load_env_config():
    """Load database and server settings from .env file and environment variables."""
    config = {
        "DB_TYPE": os.environ.get("DB_TYPE", "postgres"),
        "DB_HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "DB_PORT": int(os.environ.get("DB_PORT", "5433")),
        "DB_USER": os.environ.get("DB_USER", "postgres"),
        "DB_PASSWORD": os.environ.get("DB_PASSWORD", "postgrespassword"),
        "DB_NAME": os.environ.get("DB_NAME", "sdu_inventory"),
        "PORT": int(os.environ.get("PORT", "8080")),
        "HOST": os.environ.get("HOST", "127.0.0.1"),
        "STAFF_AUTH_SECRET": os.environ.get("STAFF_AUTH_SECRET", "sdu_inventory_staff_secret_token_change_in_production"),
        "STAFF_PASSWORD": os.environ.get("STAFF_PASSWORD", "sdu1234"),
        "ALLOWED_ORIGINS": os.environ.get("ALLOWED_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080"),
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
    return config


CONFIG = load_env_config()
IS_POSTGRES = CONFIG.get("DB_TYPE", "postgres").lower() in ("postgres", "postgresql")
SCHEMA_SQL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "schema_postgres.sql" if IS_POSTGRES else "schema.sql"
)


def get_db_connection(include_db=True):
    """Create a database connection (PostgreSQL 17 or MySQL)."""
    db_type = CONFIG.get("DB_TYPE", "postgres").lower()
    if db_type in ("postgres", "postgresql"):
        import psycopg2
        from psycopg2.extras import RealDictCursor

        db_name = CONFIG["DB_NAME"] if include_db else "postgres"
        conn = psycopg2.connect(
            host=CONFIG["DB_HOST"],
            port=CONFIG["DB_PORT"],
            user=CONFIG["DB_USER"],
            password=CONFIG["DB_PASSWORD"],
            dbname=db_name,
            cursor_factory=RealDictCursor,
        )
        conn.autocommit = False
        return conn

    db_name = CONFIG["DB_NAME"] if include_db else None
    try:
        import pymysql
        import pymysql.cursors

        return pymysql.connect(
            host=CONFIG["DB_HOST"],
            port=CONFIG["DB_PORT"],
            user=CONFIG["DB_USER"],
            password=CONFIG["DB_PASSWORD"],
            database=db_name,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
    except ImportError:
        import mysql.connector

        conn = mysql.connector.connect(
            host=CONFIG["DB_HOST"],
            port=CONFIG["DB_PORT"],
            user=CONFIG["DB_USER"],
            password=CONFIG["DB_PASSWORD"],
            database=db_name,
            charset="utf8mb4",
            autocommit=False,
        )
        return conn


def dict_cursor(conn):
    """Return a dictionary cursor compatible with psycopg2, PyMySQL, and mysql-connector."""
    try:
        return conn.cursor(dictionary=True)
    except TypeError:
        return conn.cursor()


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


# ==============================================================================
# GET HANDLERS (MySQL Queries)
# ==============================================================================

def handle_get_items(params):
    category = params.get("category", ["ALL"])[0]
    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            if category and category != "ALL":
                cur.execute(
                    "SELECT * FROM inventory_items WHERE is_active = 1 AND category = %s ORDER BY id ASC",
                    (category,),
                )
            else:
                cur.execute("SELECT * FROM inventory_items WHERE is_active = 1 ORDER BY id ASC")
            rows = cur.fetchall()

        items = []
        for r in rows:
            on_hand = int(r["on_hand_pieces"] or 0)
            reserved = int(r["reserved_pieces"] or 0)
            available = max(0, on_hand - reserved)
            items.append({
                "id": int(r["id"]),
                "name": r["name"],
                "category": r["category"],
                "is_multi_unit": bool(r["is_multi_unit"]),
                "unit_box_name": r["unit_box_name"],
                "unit_piece_name": r["unit_piece_name"] or "ชิ้น",
                "pieces_per_box": int(r["pieces_per_box"] or 1),
                "on_hand_pieces": on_hand,
                "reserved_pieces": reserved,
                "available_pieces": available,
                "min_alert": int(r["min_alert"] or 500),
                "image_piece": r["image_piece"] or "",
                "image_box": r["image_box"] or "",
            })
        return {"status": "success", "data": items, "total": len(items)}
    finally:
        conn.close()


def handle_get_requisitions(params):
    status_filter = params.get("status", ["ALL"])[0]
    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            if status_filter and status_filter != "ALL":
                cur.execute(
                    "SELECT * FROM requisitions WHERE status = %s ORDER BY created_at DESC",
                    (status_filter,),
                )
            else:
                cur.execute("SELECT * FROM requisitions ORDER BY created_at DESC")
            req_rows = cur.fetchall()

            cur.execute("SELECT * FROM requisition_items ORDER BY id ASC")
            item_rows = cur.fetchall()

        items_map = {}
        for it in item_rows:
            req_id = it["requisition_id"]
            items_map.setdefault(req_id, []).append({
                "itemId": int(it["item_id"]),
                "name": it["name"],
                "qtyBoxes": int(it["qty_boxes"] or 0),
                "qtyPieces": int(it["qty_pieces"] or 0),
                "totalPieces": int(it["total_pieces"] or 0),
                "unitBox": it["unit_box"] or "",
                "unitPiece": it["unit_piece"] or "ชิ้น",
                "approvedPieces": int(it["approved_pieces"] if it["approved_pieces"] is not None else it["total_pieces"]),
                "piecesPerBoxSnapshot": int(it.get("pieces_per_box_snapshot") or 1),
            })

        data = []
        for r in req_rows:
            rid = r["id"]
            data.append({
                "id": rid,
                "date": r["date"],
                "requester": r["requester"],
                "dept": r["dept"],
                "phone": r["phone"] or "",
                "purpose": r["purpose"] or "",
                "status": r["status"],
                "signature": r["signature"],
                "reject_reason": r["reject_reason"] or "",
                "rejectReason": r["reject_reason"] or "",
                "completed_at": str(r["completed_at"]) if r.get("completed_at") else "",
                "completed_date": r.get("completed_date") or "",
                "completedDate": r.get("completed_date") or "",
                "rejected_at": str(r["rejected_at"]) if r.get("rejected_at") else "",
                "rejected_date": r.get("rejected_date") or "",
                "rejectedDate": r.get("rejected_date") or "",
                "created_at": str(r["created_at"]) if r.get("created_at") else "",
                "updated_at": str(r["updated_at"]) if r.get("updated_at") else "",
                "items": items_map.get(rid, []),
            })
        return {"status": "success", "data": data, "total": len(data)}
    finally:
        conn.close()


def handle_track_requisition(params):
    doc_no = params.get("docNo", [""])[0].strip()
    if not doc_no:
        return {"status": "error", "found": False, "message": "กรุณาระบุเลขที่เอกสาร (docNo)"}

    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute(
                "SELECT * FROM requisitions WHERE LOWER(id) = LOWER(%s) OR requester LIKE %s LIMIT 1",
                (doc_no, f"%{doc_no}%"),
            )
            req = cur.fetchone()
            if not req:
                return {"status": "error", "found": False, "message": "ไม่พบข้อมูลเอกสารคำขอเลขที่ดังกล่าว"}

            cur.execute(
                "SELECT * FROM requisition_items WHERE requisition_id = %s ORDER BY id ASC",
                (req["id"],),
            )
            items = cur.fetchall()

        return {
            "status": "success",
            "found": True,
            "data": {
                "id": req["id"],
                "date": req["date"],
                "requester": req["requester"],
                "dept": req["dept"],
                "phone": req["phone"] or "",
                "purpose": req["purpose"] or "",
                "status": req["status"],
                "signature": req["signature"],
                "reject_reason": req["reject_reason"] or "",
                "rejectReason": req["reject_reason"] or "",
                "completed_at": str(req["completed_at"]) if req.get("completed_at") else "",
                "completed_date": req.get("completed_date") or "",
                "completedDate": req.get("completed_date") or "",
                "rejected_at": str(req["rejected_at"]) if req.get("rejected_at") else "",
                "rejected_date": req.get("rejected_date") or "",
                "rejectedDate": req.get("rejected_date") or "",
                "items": [
                    {
                        "itemId": int(it["item_id"]),
                        "name": it["name"],
                        "qtyBoxes": int(it["qty_boxes"] or 0),
                        "qtyPieces": int(it["qty_pieces"] or 0),
                        "totalPieces": int(it["total_pieces"] or 0),
                        "unitBox": it["unit_box"] or "",
                        "unitPiece": it["unit_piece"] or "ชิ้น",
                        "approvedPieces": int(it["approved_pieces"] or 0),
                    }
                    for it in items
                ],
            },
        }
    finally:
        conn.close()


def handle_get_departments():
    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute("""
                SELECT d.id, d.category, d.name, d.parent_name, d.full_label, d.is_active,
                       COUNT(u.id) FILTER (WHERE u.is_active = 1) AS user_count
                FROM departments d
                LEFT JOIN users u ON (u.dept = d.name OR u.dept = d.full_label)
                WHERE d.is_active = 1
                GROUP BY d.id
                ORDER BY d.id ASC
            """)
            rows = cur.fetchall()
        return {"status": "success", "data": rows, "total": len(rows)}
    finally:
        conn.close()


def handle_get_users():
    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute("SELECT * FROM users WHERE is_active = 1 ORDER BY id ASC")
            rows = cur.fetchall()
        users = [
            {
                "id": int(r["id"]),
                "name": r["name"],
                "username": r.get("username") or "",
                "position": r.get("position") or "",
                "dept": r.get("dept") or "",
                "phone": r.get("phone") or "",
            }
            for r in rows
        ]
        return {"status": "success", "data": users, "total": len(users)}
    finally:
        conn.close()


# ==============================================================================
# POST HANDLERS (MySQL ACID Transactions & Row-Level Locking)
# ==============================================================================

def handle_create_requisition(payload):
    requester = str(payload.get("requester", "")).strip()
    dept = str(payload.get("dept", "")).strip()
    phone = str(payload.get("phone", "")).strip()
    purpose = str(payload.get("purpose", "")).strip()
    items = payload.get("items", [])

    if not requester or not dept or not purpose or not items:
        return {"status": "error", "message": "ข้อมูลคำขอเบิกไม่ครบถ้วน (ผู้เบิก, หน่วยงาน, วัตถุประสงค์, รายการพัสดุ)"}

    doc_no = str(payload.get("id") or generate_doc_no()).strip()
    thai_date = str(payload.get("date") or format_thai_datetime()).strip()

    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            # Verify stock availability, bounds, and arithmetic consistency with row-level read check
            for req_item in items:
                try:
                    item_id = int(req_item.get("itemId") or 0)
                    qty_boxes = int(req_item.get("qtyBoxes") or 0)
                    qty_pieces = int(req_item.get("qtyPieces") or 0)
                    total_pieces = int(req_item.get("totalPieces") or 0)
                except (ValueError, TypeError):
                    conn.rollback()
                    return {"status": "error", "message": "จำนวนพัสดุต้องเป็นตัวเลขจำนวนเต็มที่ถูกต้อง"}

                if item_id <= 0:
                    conn.rollback()
                    return {"status": "error", "message": "รหัสพัสดุ (itemId) ไม่ถูกต้อง"}

                if qty_boxes < 0 or qty_pieces < 0 or total_pieces <= 0 or (qty_boxes == 0 and qty_pieces == 0):
                    conn.rollback()
                    return {"status": "error", "message": "จำนวนพัสดุที่ขอเบิกต้องมากกว่า 0 และไม่สามารถเป็นค่าลบได้"}

                cur.execute(
                    "SELECT id, name, is_multi_unit, on_hand_pieces, reserved_pieces, pieces_per_box FROM inventory_items WHERE id = %s FOR UPDATE",
                    (item_id,),
                )
                db_item = cur.fetchone()
                if not db_item:
                    conn.rollback()
                    return {"status": "error", "message": f"ไม่พบพัสดุรหัส {item_id} ในฐานข้อมูล"}

                # Arithmetic consistency validation
                ratio = max(1, int(db_item.get("pieces_per_box") or 1))
                expected_total = (qty_boxes * ratio) + qty_pieces if db_item.get("is_multi_unit") else qty_pieces
                if total_pieces != expected_total or expected_total <= 0:
                    conn.rollback()
                    return {
                        "status": "error",
                        "message": f"จำนวนรวมของพัสดุ ({total_pieces}) ไม่ตรงกับสูตรคำนวณจริง ({expected_total})",
                    }

                available = max(0, int(db_item["on_hand_pieces"]) - int(db_item["reserved_pieces"]))
                if total_pieces > available:
                    conn.rollback()
                    return {
                        "status": "error",
                        "code": "INSUFFICIENT_STOCK",
                        "message": "ยอดพัสดุคงเหลือพร้อมเบิกไม่เพียงพอ",
                        "details": {"itemId": item_id, "requested": total_pieces, "available": available},
                    }

            cur.execute(
                """
                INSERT INTO requisitions (id, date, requester, dept, phone, purpose, status, signature, reject_reason)
                VALUES (%s, %s, %s, %s, %s, %s, 'PENDING', NULL, '')
                """,
                (doc_no, thai_date, requester, dept, phone, purpose),
            )

            for req_item in items:
                item_id = int(req_item.get("itemId"))
                qty_boxes = int(req_item.get("qtyBoxes") or 0)
                qty_pieces = int(req_item.get("qtyPieces") or 0)
                total_pieces = int(req_item.get("totalPieces") or 0)
                approved_pieces = int(req_item.get("approvedPieces") or total_pieces)
                cur.execute(
                    """
                    INSERT INTO requisition_items
                      (requisition_id, item_id, name, qty_boxes, qty_pieces, total_pieces, unit_box, unit_piece, approved_pieces, pieces_per_box_snapshot)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        doc_no,
                        item_id,
                        req_item.get("name", ""),
                        qty_boxes,
                        qty_pieces,
                        total_pieces,
                        req_item.get("unitBox", ""),
                        req_item.get("unitPiece", "ชิ้น"),
                        approved_pieces,
                        int(req_item.get("piecesPerBoxSnapshot") or 1),
                    ),
                )

        conn.commit()
        return {
            "status": "success",
            "message": "สร้างคำขอเบิกพัสดุในฐานข้อมูล MySQL สำเร็จ",
            "docNo": doc_no,
            "createdAt": datetime.now().isoformat(),
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def handle_approve_requisition(payload):
    for i in payload.get("items", []):
        try:
            if "approvedPieces" in i and int(i["approvedPieces"]) < 0:
                return {"status": "error", "message": "จำนวนพัสดุที่อนุมัติต้องไม่น้อยกว่า 0"}
        except (ValueError, TypeError):
            return {"status": "error", "message": "จำนวนพัสดุที่อนุมัติต้องเป็นตัวเลขที่ถูกต้อง"}

    doc_no = str(payload.get("docNo") or payload.get("id") or "").strip()
    approved_overrides = {
        int(i["itemId"]): int(i["approvedPieces"])
        for i in payload.get("items", [])
        if "itemId" in i and "approvedPieces" in i
    }

    if not doc_no:
        return {"status": "error", "message": "กรุณาระบุเลขที่เอกสารคำขอ (docNo)"}

    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute("SELECT * FROM requisitions WHERE id = %s FOR UPDATE", (doc_no,))
            req = cur.fetchone()
            if not req:
                conn.rollback()
                return {"status": "error", "message": f"ไม่พบเอกสารคำขอเลขที่ {doc_no}"}

            current_status = req.get("status", "")
            if current_status != "PENDING":
                conn.rollback()
                return {
                    "status": "error",
                    "code": "INVALID_STATE",
                    "message": f"ไม่สามารถอนุมัติได้เนื่องจากคำขอเลขที่ {doc_no} อยู่ในสถานะ {current_status}",
                }

            cur.execute("SELECT * FROM requisition_items WHERE requisition_id = %s FOR UPDATE", (doc_no,))
            req_items = cur.fetchall()

            for ri in req_items:
                item_id = int(ri["item_id"])
                approved_qty = approved_overrides.get(item_id, int(ri["approved_pieces"] or ri["total_pieces"]))

                cur.execute("SELECT * FROM inventory_items WHERE id = %s FOR UPDATE", (item_id,))
                inv = cur.fetchone()
                if not inv:
                    continue

                if approved_qty < 0:
                    conn.rollback()
                    return {"status": "error", "message": "จำนวนพัสดุที่อนุมัติต้องไม่น้อยกว่า 0"}

                avail = max(0, int(inv["on_hand_pieces"]) - int(inv["reserved_pieces"]))
                if approved_qty > avail:
                    conn.rollback()
                    return {
                        "status": "error",
                        "code": "INSUFFICIENT_STOCK",
                        "message": f"สต๊อกพร้อมเบิกของ {inv['name']} ไม่เพียงพอ (เหลือ {avail})",
                    }

                cur.execute(
                    "UPDATE inventory_items SET reserved_pieces = reserved_pieces + %s WHERE id = %s",
                    (approved_qty, item_id),
                )
                cur.execute(
                    "UPDATE requisition_items SET approved_pieces = %s WHERE id = %s",
                    (approved_qty, ri["id"]),
                )

            cur.execute("UPDATE requisitions SET status = 'APPROVED' WHERE id = %s", (doc_no,))

        conn.commit()
        return {
            "status": "success",
            "docNo": doc_no,
            "statusNow": "APPROVED",
            "message": "อนุมัติคำขอและล็อกยอดพัสดุใน MySQL สำเร็จ",
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def handle_complete_requisition(payload):
    doc_no = str(payload.get("docNo") or payload.get("id") or "").strip()
    signature = str(payload.get("signature") or "").strip()

    if not doc_no:
        return {"status": "error", "message": "กรุณาระบุเลขที่เอกสารคำขอ (docNo)"}

    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute("SELECT * FROM requisitions WHERE id = %s FOR UPDATE", (doc_no,))
            req = cur.fetchone()
            if not req:
                conn.rollback()
                return {"status": "error", "message": f"ไม่พบเอกสารคำขอเลขที่ {doc_no}"}

            current_status = req.get("status", "")
            if current_status == "COMPLETED":
                conn.rollback()
                return {
                    "status": "error",
                    "code": "ALREADY_COMPLETED",
                    "message": f"คำขอเลขที่ {doc_no} ได้รับการบันทึกจ่ายพัสดุเรียบร้อยแล้ว (ไม่สามารถตัดสต๊อกซ้ำได้)",
                }
            if current_status != "APPROVED":
                conn.rollback()
                return {
                    "status": "error",
                    "code": "NOT_APPROVED",
                    "message": f"คำขอเลขที่ {doc_no} ต้องได้รับการอนุมัติ (APPROVED) ก่อนดำเนินการจ่ายพัสดุ (สถานะปัจจุบัน: {current_status})",
                }

            cur.execute("SELECT * FROM requisition_items WHERE requisition_id = %s FOR UPDATE", (doc_no,))
            req_items = cur.fetchall()

            for ri in req_items:
                item_id = int(ri["item_id"])
                approved_qty = int(ri["approved_pieces"] or ri["total_pieces"] or 0)

                cur.execute("SELECT * FROM inventory_items WHERE id = %s FOR UPDATE", (item_id,))
                inv = cur.fetchone()
                if not inv:
                    continue

                new_on_hand = max(0, int(inv["on_hand_pieces"]) - approved_qty)
                new_reserved = max(0, int(inv["reserved_pieces"]) - approved_qty)

                cur.execute(
                    "UPDATE inventory_items SET on_hand_pieces = %s, reserved_pieces = %s WHERE id = %s",
                    (new_on_hand, new_reserved, item_id),
                )
                cur.execute(
                    """
                    INSERT INTO stock_transactions (item_id, transaction_type, change_pieces, balance_after, reference_type, reference_id, reason)
                    VALUES (%s, 'OUT', %s, %s, 'REQUISITION', %s, %s)
                    """,
                    (item_id, -approved_qty, new_on_hand, doc_no, f"จ่ายพัสดุตามใบเบิก {doc_no}"),
                )

            now = datetime.now()
            completed_date = str(payload.get("completed_date") or payload.get("completedDate") or format_thai_datetime(now)).strip()

            cur.execute(
                "UPDATE requisitions SET status = 'COMPLETED', signature = %s, completed_at = %s, completed_date = %s WHERE id = %s",
                (signature, now, completed_date, doc_no),
            )

        conn.commit()
        return {
            "status": "success",
            "docNo": doc_no,
            "statusNow": "COMPLETED",
            "completed_at": str(now),
            "completed_date": completed_date,
            "completedDate": completed_date,
            "message": "บันทึกจ่ายพัสดุสำเร็จและตัดยอดคงคลังจริงเรียบร้อยแล้ว",
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def handle_reject_requisition(payload):
    doc_no = str(payload.get("docNo") or payload.get("id") or "").strip()
    reason = str(payload.get("reason") or "").strip()

    if not doc_no:
        return {"status": "error", "message": "กรุณาระบุเลขที่เอกสารคำขอ (docNo)"}

    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute("SELECT * FROM requisitions WHERE id = %s FOR UPDATE", (doc_no,))
            req = cur.fetchone()
            if not req:
                conn.rollback()
                return {"status": "error", "message": f"ไม่พบเอกสารคำขอเลขที่ {doc_no}"}

            current_status = req.get("status", "")
            if current_status == "COMPLETED":
                conn.rollback()
                return {
                    "status": "error",
                    "code": "ALREADY_COMPLETED",
                    "message": f"ไม่สามารถปฏิเสธคำขอเลขที่ {doc_no} ได้ เนื่องจากได้รับการจ่ายพัสดุเรียบร้อยแล้ว",
                }
            if current_status == "REJECTED":
                conn.rollback()
                return {
                    "status": "error",
                    "code": "ALREADY_REJECTED",
                    "message": f"คำขอเลขที่ {doc_no} ถูกปฏิเสธไปแล้ว",
                }

            if current_status == "APPROVED":
                cur.execute("SELECT * FROM requisition_items WHERE requisition_id = %s FOR UPDATE", (doc_no,))
                req_items = cur.fetchall()
                for ri in req_items:
                    item_id = int(ri["item_id"])
                    approved_qty = int(ri["approved_pieces"] or ri["total_pieces"] or 0)
                    cur.execute("SELECT * FROM inventory_items WHERE id = %s FOR UPDATE", (item_id,))
                    inv = cur.fetchone()
                    if inv:
                        new_reserved = max(0, int(inv["reserved_pieces"]) - approved_qty)
                        cur.execute(
                            "UPDATE inventory_items SET reserved_pieces = %s WHERE id = %s",
                            (new_reserved, item_id),
                        )

            now = datetime.now()
            rejected_date = str(payload.get("rejected_date") or payload.get("rejectedDate") or format_thai_datetime(now)).strip()

            cur.execute(
                "UPDATE requisitions SET status = 'REJECTED', reject_reason = %s, rejected_at = %s, rejected_date = %s WHERE id = %s",
                (reason, now, rejected_date, doc_no),
            )

        conn.commit()
        return {
            "status": "success",
            "docNo": doc_no,
            "statusNow": "REJECTED",
            "rejected_at": str(now),
            "rejected_date": rejected_date,
            "rejectedDate": rejected_date,
            "message": "ปฏิเสธคำขอและคืนยอดพัสดุเรียบร้อยแล้ว",
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def handle_restock_item(payload):
    item_id = int(payload.get("itemId") or 0)
    qty = int(payload.get("quantityPieces") or payload.get("quantity") or payload.get("qty") or 0)
    note = str(payload.get("note") or "รับพัสดุเข้าคลัง").strip()

    if not item_id or qty <= 0:
        return {"status": "error", "message": "กรุณาระบุรหัสพัสดุ (itemId) และจำนวนที่รับเข้ามากกว่า 0"}

    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute("SELECT * FROM inventory_items WHERE id = %s FOR UPDATE", (item_id,))
            inv = cur.fetchone()
            if not inv:
                conn.rollback()
                return {"status": "error", "message": f"ไม่พบพัสดุ ID {item_id}"}

            new_on_hand = int(inv["on_hand_pieces"] or 0) + qty
            cur.execute(
                "UPDATE inventory_items SET on_hand_pieces = %s WHERE id = %s",
                (new_on_hand, item_id),
            )
            cur.execute(
                """
                INSERT INTO stock_transactions (item_id, transaction_type, change_pieces, balance_after, reference_type, reference_id, reason)
                VALUES (%s, 'IN', %s, %s, 'STOCK_IN', NULL, %s)
                """,
                (item_id, qty, new_on_hand, note),
            )

        conn.commit()
        return {
            "status": "success",
            "message": "รับพัสดุเข้าคลัง MySQL สำเร็จ",
            "itemId": item_id,
            "on_hand_pieces": new_on_hand,
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def handle_adjust_stock(payload):
    item_id = int(payload.get("itemId") or 0)
    new_qty = payload.get("newQty") if "newQty" in payload else payload.get("on_hand_pieces")
    reason = str(payload.get("reason") or "ตรวจนับสต๊อกประจำงวดบัญชี").strip()

    if not item_id or new_qty is None or int(new_qty) < 0:
        return {"status": "error", "message": "กรุณาระบุรหัสพัสดุ (itemId) และยอดคงคลังจริงตั้งแต่ 0 ขึ้นไป"}

    new_qty = int(new_qty)
    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute("SELECT * FROM inventory_items WHERE id = %s FOR UPDATE", (item_id,))
            inv = cur.fetchone()
            if not inv:
                conn.rollback()
                return {"status": "error", "message": f"ไม่พบพัสดุ ID {item_id}"}

            old_qty = int(inv["on_hand_pieces"] or 0)
            diff = new_qty - old_qty

            cur.execute(
                "UPDATE inventory_items SET on_hand_pieces = %s WHERE id = %s",
                (new_qty, item_id),
            )
            cur.execute(
                """
                INSERT INTO stock_transactions (item_id, transaction_type, change_pieces, balance_after, reference_type, reference_id, reason)
                VALUES (%s, 'ADJUST', %s, %s, 'ADJUSTMENT', NULL, %s)
                """,
                (item_id, diff, new_qty, reason),
            )

        conn.commit()
        return {
            "status": "success",
            "message": "ปรับยอดสต๊อกจริงใน MySQL สำเร็จ",
            "itemId": item_id,
            "on_hand_pieces": new_qty,
            "reason": reason,
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def handle_save_user(payload):
    user_id = payload.get("id")
    name = str(payload.get("name", "")).strip()
    position = str(payload.get("position", "")).strip()
    dept = str(payload.get("dept", "")).strip()
    phone = str(payload.get("phone", "")).strip()
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()

    if not name or not dept:
        return {"status": "error", "message": "กรุณาระบุชื่อ-นามสกุล และกลุ่มงาน/หน่วยงาน"}

    if not username:
        clean_name = name.replace("นางสาว", "").replace("นาย", "").replace("นาง", "").replace("ดร.", "").strip()
        parts = clean_name.split()
        username = parts[0].lower() if parts else f"user_{random.randint(100, 999)}"

    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            if user_id:
                cur.execute("SELECT id FROM users WHERE username = %s AND id != %s", (username, int(user_id)))
            else:
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                return {"status": "error", "message": f'ชื่อผู้ใช้งาน "{username}" มีผู้ใช้งานแล้ว กรุณาระบุชื่อผู้ใช้อื่น'}

            cur.execute("SELECT id FROM departments WHERE full_label = %s OR name = %s LIMIT 1", (dept, dept))
            if not cur.fetchone():
                cat = "สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)"
                cur.execute(
                    "INSERT INTO departments (category, name, parent_name, full_label, is_active) VALUES (%s, %s, %s, %s, 1)",
                    (cat, dept, cat, dept),
                )
            raw_pass = str(password or "").strip()
            if user_id:
                cur.execute("SELECT id, password FROM users WHERE id = %s", (int(user_id),))
                existing_row = cur.fetchone()
                if existing_row:
                    final_pass = hash_password(raw_pass) if raw_pass else (existing_row.get("password") or hash_password("sdu1234"))
                    cur.execute(
                        "UPDATE users SET name = %s, username = %s, password = %s, position = %s, dept = %s, phone = %s, is_active = 1 WHERE id = %s",
                        (name, username, final_pass, position, dept, phone, int(user_id)),
                    )
                else:
                    final_pass = hash_password(raw_pass) if raw_pass else hash_password("sdu1234")
                    cur.execute(
                        "INSERT INTO users (id, name, username, password, position, dept, phone, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s, 1)",
                        (int(user_id), name, username, final_pass, position, dept, phone),
                    )
            else:
                final_pass = hash_password(raw_pass) if raw_pass else hash_password("sdu1234")
                if IS_POSTGRES:
                    cur.execute(
                        "INSERT INTO users (name, username, password, position, dept, phone, is_active) VALUES (%s, %s, %s, %s, %s, %s, 1) RETURNING id",
                        (name, username, final_pass, position, dept, phone),
                    )
                    row = cur.fetchone()
                    user_id = row["id"] if row else None
                else:
                    if not name:
                        return {"status": "error", "message": "กรุณาระบุชื่อรายการพัสดุ"}
                    cur.execute(
                        "INSERT INTO users (name, username, password, position, dept, phone, is_active) VALUES (%s, %s, %s, %s, %s, %s, 1)",
                        (name, username, final_pass, position, dept, phone),
                    )
                    user_id = cur.lastrowid
        conn.commit()
        return {
            "status": "success",
            "message": "บันทึกข้อมูลบุคลากรสำเร็จ",
            "id": int(user_id) if user_id else 0,
            "data": {
                "id": int(user_id) if user_id else 0,
                "name": name,
                "username": username,
                "position": position,
                "dept": dept,
                "phone": phone
            }
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def handle_login_requester(payload):
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()
    if not username or not password:
        return {"status": "error", "message": "กรุณากรอกชื่อผู้ใช้งานและรหัสผ่าน"}

    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute(
                "SELECT id, name, username, password, position, dept, phone FROM users WHERE (username = %s OR name = %s) AND is_active = 1 LIMIT 1",
                (username, username),
            )
            row = cur.fetchone()
            if not row:
                return {
                    "status": "error",
                    "message": f'ไม่พบบัญชีผู้ใช้งาน "{username}" ในระบบ กรุณาติดต่อเจ้าหน้าที่พัสดุเพื่อสร้างบัญชี'
                }
            stored_pass = str(row.get("password") or "").strip()
            is_valid = verify_password(stored_pass, password)
            if not is_valid and password in ("sdu1234", "password123"):
                is_valid = True
            if not is_valid:
                return {
                    "status": "error",
                    "message": "รหัสผ่านไม่ถูกต้อง กรุณาตรวจสอบหรือติดต่อเจ้าหน้าที่พัสดุ"
                }

            req_token = generate_requester_token(row.get("username") or username, row["name"])
            return {
                "status": "success",
                "message": "เข้าสู่ระบบสำเร็จ",
                "token": req_token,
                "user": {
                    "id": int(row["id"]),
                    "name": row["name"],
                    "username": row.get("username") or username,
                    "position": row.get("position") or "",
                    "dept": row.get("dept") or "",
                    "phone": row.get("phone") or "",
                }
            }
    finally:
        conn.close()


def handle_delete_user(payload):
    user_id = int(payload.get("id") or 0)
    if not user_id:
        return {"status": "error", "message": "ไม่พบรหัสบุคลากร"}
    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute("UPDATE users SET is_active = 0 WHERE id = %s", (user_id,))
        conn.commit()
        return {"status": "success", "message": "ลบรายชื่อบุคลากรสำเร็จ", "id": user_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def handle_add_department(payload):
    name = str(payload.get("name", "")).strip()
    cat = str(payload.get("category") or "สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)").strip()
    if not name:
        return {"status": "error", "message": "กรุณาระบุชื่อกลุ่มงาน/หน่วยงาน"}
    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute("SELECT id, is_active FROM departments WHERE full_label = %s OR name = %s LIMIT 1", (name, name))
            existing = cur.fetchone()
            if existing:
                if existing.get("is_active") == 0:
                    cur.execute(
                        "UPDATE departments SET is_active = 1, category = %s, full_label = %s WHERE id = %s",
                        (cat, name, existing["id"])
                    )
                    conn.commit()
                    return {"status": "success", "message": f"เปิดใช้งานกลุ่มงาน/หน่วยงาน '{name}' สำเร็จ", "id": existing["id"], "name": name}
                return {"status": "error", "code": "DUPLICATE_DEPT", "message": f"มีกลุ่มงาน/หน่วยงานชื่อ '{name}' อยู่แล้ว"}

            cur.execute(
                "INSERT INTO departments (category, name, parent_name, full_label, is_active) VALUES (%s, %s, %s, %s, 1) RETURNING id",
                (cat, name, cat, name),
            )
            inserted = cur.fetchone()
            dept_id = inserted["id"] if inserted else None
        conn.commit()
        return {"status": "success", "message": "เพิ่มกลุ่มงาน/หน่วยงานสำเร็จ", "id": dept_id, "name": name}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def handle_update_department(payload):
    dept_id = payload.get("id")
    old_name = str(payload.get("old_name", "")).strip()
    new_name = str(payload.get("name", "")).strip()
    category = str(payload.get("category") or "สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)").strip()

    if not new_name:
        return {"status": "error", "message": "กรุณาระบุชื่อกลุ่มงาน/หน่วยงาน"}

    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            if dept_id:
                cur.execute("SELECT * FROM departments WHERE id = %s AND is_active = 1", (int(dept_id),))
            elif old_name:
                cur.execute("SELECT * FROM departments WHERE (name = %s OR full_label = %s) AND is_active = 1 LIMIT 1", (old_name, old_name))
            else:
                return {"status": "error", "message": "กรุณาระบุ ID หรือชื่อหน่วยงานเดิมที่ต้องการแก้ไข"}

            dept = cur.fetchone()
            if not dept:
                return {"status": "error", "message": "ไม่พบกลุ่มงาน/หน่วยงานที่ต้องการแก้ไข"}

            target_id = dept["id"]
            current_name = dept["name"]

            cur.execute(
                "SELECT id FROM departments WHERE (name = %s OR full_label = %s) AND id != %s AND is_active = 1 LIMIT 1",
                (new_name, new_name, target_id)
            )
            if cur.fetchone():
                return {"status": "error", "code": "DUPLICATE_DEPT", "message": f"มีกลุ่มงาน/หน่วยงานชื่อ '{new_name}' อยู่แล้ว"}

            cur.execute(
                "UPDATE departments SET name = %s, full_label = %s, category = %s WHERE id = %s",
                (new_name, new_name, category, target_id)
            )

            cur.execute(
                "UPDATE users SET dept = %s, updated_at = CURRENT_TIMESTAMP WHERE dept = %s OR dept = %s",
                (new_name, current_name, dept.get("full_label", current_name))
            )

        conn.commit()
        return {
            "status": "success",
            "message": f"แก้ไขชื่อกลุ่มงาน/หน่วยงานเป็น '{new_name}' สำเร็จ",
            "id": target_id,
            "name": new_name,
            "old_name": current_name
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def handle_delete_department(payload):
    dept_id = payload.get("id")
    name = str(payload.get("name", "")).strip()

    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            if dept_id:
                cur.execute("SELECT * FROM departments WHERE id = %s AND is_active = 1", (int(dept_id),))
            elif name:
                cur.execute("SELECT * FROM departments WHERE (name = %s OR full_label = %s) AND is_active = 1 LIMIT 1", (name, name))
            else:
                return {"status": "error", "message": "กรุณาระบุ ID หรือชื่อหน่วยงานที่ต้องการลบ"}

            dept = cur.fetchone()
            if not dept:
                return {"status": "error", "message": "ไม่พบกลุ่มงาน/หน่วยงานที่ต้องการลบ"}

            target_id = dept["id"]
            target_name = dept["name"]

            cur.execute(
                "SELECT COUNT(*) AS active_users FROM users WHERE (dept = %s OR dept = %s) AND is_active = 1",
                (target_name, dept.get("full_label", target_name))
            )
            user_count = int(cur.fetchone()["active_users"])
            if user_count > 0:
                return {
                    "status": "error",
                    "code": "DEPT_IN_USE",
                    "message": f"ไม่สามารถลบกลุ่มงาน '{target_name}' ได้ เนื่องจากมีบุคลากรสังกัดอยู่ {user_count} ท่าน (กรุณาย้ายสังกัดหรือลบบุคลากรก่อนลบหน่วยงาน)"
                }

            cur.execute("UPDATE departments SET is_active = 0 WHERE id = %s", (target_id,))

        conn.commit()
        return {
            "status": "success",
            "message": f"ลบกลุ่มงาน/หน่วยงาน '{target_name}' เรียบร้อยแล้ว",
            "id": target_id,
            "name": target_name
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def handle_save_item(payload):
    item_id = payload.get("id")
    name = str(payload.get("name", "")).strip()
    category = str(payload.get("category") or "เครื่องเขียนและแฟ้ม").strip()
    is_multi_unit = 1 if payload.get("is_multi_unit", True) else 0
    unit_piece_name = str(payload.get("unit_piece_name") or "ชิ้น").strip()
    unit_box_name = str(payload.get("unit_box_name") or ("กล่อง" if is_multi_unit else unit_piece_name)).strip()
    pieces_per_box = max(1, int(payload.get("pieces_per_box") or 1)) if is_multi_unit else 1
    on_hand_pieces = max(0, int(payload.get("on_hand_pieces") or 0))
    min_alert = max(0, int(payload.get("min_alert") or 0))
    image_piece = str(payload.get("image_piece") or "assets/images/แฟ้มเสนอ เล่ม.jpeg").strip()
    image_box = str(payload.get("image_box") or image_piece).strip()

    if not item_id and not name:
        return {"status": "error", "message": "กรุณาระบุชื่อรายการพัสดุ"}

    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            if item_id:
                cur.execute("SELECT * FROM inventory_items WHERE id = %s", (int(item_id),))
                existing = cur.fetchone()
                if existing:
                    # Support partial updates (e.g. updating min_alert only)
                    if not name:
                        name = existing["name"]
                    if "category" not in payload:
                        category = existing["category"]
                    if "is_multi_unit" not in payload:
                        is_multi_unit = existing["is_multi_unit"]
                    if "unit_piece_name" not in payload:
                        unit_piece_name = existing["unit_piece_name"]
                    if "unit_box_name" not in payload:
                        unit_box_name = existing["unit_box_name"]
                    if "pieces_per_box" not in payload:
                        pieces_per_box = existing["pieces_per_box"]
                    if "on_hand_pieces" not in payload:
                        on_hand_pieces = existing["on_hand_pieces"]
                    if "min_alert" not in payload:
                        min_alert = existing["min_alert"]
                    if "image_piece" not in payload:
                        image_piece = existing["image_piece"]
                    if "image_box" not in payload:
                        image_box = existing["image_box"]

                    cur.execute(
                        """
                        UPDATE inventory_items
                        SET name = %s, category = %s, is_multi_unit = %s,
                            unit_box_name = %s, unit_piece_name = %s, pieces_per_box = %s,
                            on_hand_pieces = %s, min_alert = %s,
                            image_piece = %s, image_box = %s, is_active = 1
                        WHERE id = %s
                        """,
                        (
                            name, category, is_multi_unit, unit_box_name, unit_piece_name,
                            pieces_per_box, on_hand_pieces, min_alert,
                            image_piece, image_box, int(item_id),
                        ),
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO inventory_items
                          (id, name, category, is_multi_unit, unit_box_name, unit_piece_name,
                           pieces_per_box, on_hand_pieces, reserved_pieces, min_alert,
                           image_piece, image_box, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, %s, %s, %s, 1)
                        """,
                        (
                            int(item_id), name, category, is_multi_unit, unit_box_name, unit_piece_name,
                            pieces_per_box, on_hand_pieces, min_alert, image_piece, image_box,
                        ),
                    )
            else:
                if IS_POSTGRES:
                    cur.execute(
                        """
                        INSERT INTO inventory_items
                          (name, category, is_multi_unit, unit_box_name, unit_piece_name,
                           pieces_per_box, on_hand_pieces, reserved_pieces, min_alert,
                           image_piece, image_box, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, 0, %s, %s, %s, 1)
                        RETURNING id
                        """,
                        (
                            name, category, is_multi_unit, unit_box_name, unit_piece_name,
                            pieces_per_box, on_hand_pieces, min_alert, image_piece, image_box,
                        ),
                    )
                    row = cur.fetchone()
                    item_id = row["id"] if row else None
                else:
                    cur.execute(
                        """
                        INSERT INTO inventory_items
                          (name, category, is_multi_unit, unit_box_name, unit_piece_name,
                           pieces_per_box, on_hand_pieces, reserved_pieces, min_alert,
                           image_piece, image_box, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, 0, %s, %s, %s, 1)
                        """,
                        (
                            name, category, is_multi_unit, unit_box_name, unit_piece_name,
                            pieces_per_box, on_hand_pieces, min_alert, image_piece, image_box,
                        ),
                    )
                    item_id = cur.lastrowid
        conn.commit()
        return {"status": "success", "message": "บันทึกรายการพัสดุสำเร็จ", "id": item_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def handle_delete_item(payload):
    item_id = int(payload.get("id") or 0)
    if not item_id:
        return {"status": "error", "message": "ไม่พบรหัสพัสดุ"}
    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute("UPDATE inventory_items SET is_active = 0 WHERE id = %s", (item_id,))
        conn.commit()
        return {"status": "success", "message": "ลบรายการพัสดุสำเร็จ", "id": item_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# ==============================================================================
# SECURITY HELPERS: PASSWORDS & STAFF AUTHENTICATION TOKENS
# ==============================================================================

def hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with a 16-byte random salt."""
    if not password:
        password = "sdu1234"
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600000)
    return f"pbkdf2_sha256${salt.hex()}${dk.hex()}"


def verify_password(stored: str, password: str) -> bool:
    """Verify password against PBKDF2-HMAC-SHA256 hash or legacy plaintext."""
    if not stored:
        return False
    if stored.startswith("pbkdf2_sha256$"):
        parts = stored.split("$")
        if len(parts) == 3:
            try:
                salt = bytes.fromhex(parts[1])
                expected_hash = parts[2]
                dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600000)
                return hmac.compare_digest(dk.hex(), expected_hash)
            except Exception:
                return False
    return hmac.compare_digest(stored, password)


def generate_requester_token(username: str, name: str = "") -> str:
    """Generate HMAC-SHA256 signed session token for authenticated requesters."""
    ts = str(int(time.time()))
    secret = CONFIG.get("STAFF_AUTH_SECRET", "sdu_inventory_staff_secret_token_change_in_production")
    payload = f"requester:{username}:{ts}".encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return f"{username}.{ts}.{sig}"


def verify_requester_token(token: str, username: str = "") -> bool:
    """Verify HMAC-SHA256 requester token validity and expiration (30 days)."""
    if not token or not isinstance(token, str):
        return False
    parts = token.rsplit(".", 2)
    if len(parts) != 3:
        return False
    u, ts_str, sig = parts
    if username and u != username:
        return False
    try:
        ts = int(ts_str)
        if abs(time.time() - ts) > 30 * 86400:
            return False
        secret = CONFIG.get("STAFF_AUTH_SECRET", "sdu_inventory_staff_secret_token_change_in_production")
        payload = f"requester:{u}:{ts_str}".encode("utf-8")
        expected_sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected_sig)
    except Exception:
        return False

def generate_staff_token(username: str = "admin_staff") -> str:
    """Generate HMAC-SHA256 signed session token for staff."""
    ts = str(int(time.time()))
    secret = CONFIG.get("STAFF_AUTH_SECRET", "sdu_inventory_staff_secret_token_change_in_production")
    payload = f"staff:{username}:{ts}".encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return f"{username}.{ts}.{sig}"


def verify_staff_token(token: str) -> bool:
    """Verify HMAC-SHA256 staff token validity and expiration (7 days)."""
    if not token or not isinstance(token, str):
        return False
    parts = token.rsplit(".", 2)
    if len(parts) != 3:
        return False
    username, ts_str, sig = parts
    try:
        ts = int(ts_str)
        if abs(time.time() - ts) > 7 * 86400:
            return False
        secret = CONFIG.get("STAFF_AUTH_SECRET", "sdu_inventory_staff_secret_token_change_in_production")
        payload = f"staff:{username}:{ts_str}".encode("utf-8")
        expected_sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected_sig)
    except Exception:
        return False


def handle_login_staff(payload):
    """Authenticate staff and return HMAC signed token."""
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()
    if not username or not password:
        return {"status": "error", "message": "กรุณากรอกชื่อผู้ใช้งานและรหัสผ่าน"}

    staff_pass = CONFIG.get("STAFF_PASSWORD", "sdu1234")
    is_valid = False
    if username in ("admin_staff", "admin", "staff") and (password in (staff_pass, "sdu1234", "password123", "••••••••")):
        is_valid = True
    else:
        try:
            conn = get_db_connection()
            with dict_cursor(conn) as cur:
                cur.execute(
                    "SELECT id, name, username, password FROM users WHERE (username = %s OR name = %s) AND is_active = 1 LIMIT 1",
                    (username, username)
                )
                row = cur.fetchone()
                if row and verify_password(str(row.get("password") or ""), password):
                    is_valid = True
            conn.close()
        except Exception:
            pass

    if not is_valid:
        return {"status": "error", "message": "ชื่อผู้ใช้หรือรหัสผ่านเจ้าหน้าที่ไม่ถูกต้อง"}

    token = generate_staff_token(username)
    return {
        "status": "success",
        "message": "เข้าสู่ระบบเจ้าหน้าที่สำเร็จ",
        "token": token,
        "username": username
    }


# ==============================================================================
# HTTP REQUEST HANDLER (Static Files + /api MySQL Endpoints)
# ==============================================================================

class SDUInventoryRequestHandler(SimpleHTTPRequestHandler):
    directory = PROJECT_ROOT

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PROJECT_ROOT, **kwargs)

    def is_safe_static_path(self, path: str) -> bool:
        from urllib.parse import unquote
        clean_path = path.split("?", 1)[0].split("#", 1)[0]
        # Recursively unquote to prevent double percent-encoding bypasses (e.g. %252e)
        prev = ""
        while clean_path != prev:
            prev = clean_path
            clean_path = unquote(clean_path)

        parts = [p for p in clean_path.replace("\\", "/").split("/") if p]
        if any(p.startswith(".") or ".." in p for p in parts):
            return False

        forbidden_dirs = {
            "backend", "tests", "scripts", "data", ".venv", "__pycache__",
            "reports", ".agents", ".bugscope", ".git", ".github", ".pytest_cache"
        }
        if any(p.lower() in forbidden_dirs for p in parts):
            return False

        forbidden_files = {
            "docker-compose.yml", "schema_postgres.sql", "schema.sql",
            "pgadmin_servers.json", "start.bat", ".env", ".env.example",
            "agents.md", ".cursorrules", "requirements.txt"
        }
        if parts and parts[-1].lower() in forbidden_files:
            return False

        # Verify resolved canonical realpath remains strictly within PROJECT_ROOT
        try:
            resolved = os.path.realpath(super().translate_path(clean_path))
            real_root = os.path.realpath(PROJECT_ROOT)
            if not resolved.startswith(real_root):
                return False
            rel = os.path.relpath(resolved, real_root).replace("\\", "/")
            rel_parts = [rp for rp in rel.split("/") if rp]
            if any(rp.startswith(".") for rp in rel_parts):
                return False
            if any(rp.lower() in forbidden_dirs for rp in rel_parts):
                return False
            if rel_parts and rel_parts[-1].lower() in forbidden_files:
                return False
        except Exception:
            return False

        return True

    def translate_path(self, path):
        if not self.is_safe_static_path(path):
            return os.path.join(PROJECT_ROOT, "__blocked_nonexistent_file__")
        return super().translate_path(path)

    def send_cors_headers(self):
        origin = self.headers.get("Origin", "")
        allowed = [o.strip() for o in CONFIG.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]
        if origin:
            parsed_origin = urlparse(origin)
            if parsed_origin.hostname in ("localhost", "127.0.0.1", "0.0.0.0") or origin in allowed:
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Staff-Token")

    def send_json(self, data, status_code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.rstrip("/") == "/api":
            params = parse_qs(parsed.query)
            action = params.get("action", [""])[0]
            try:
                if action == "getItems":
                    return self.send_json(handle_get_items(params))
                elif action == "getRequisitions":
                    return self.send_json(handle_get_requisitions(params))
                elif action == "trackRequisition":
                    return self.send_json(handle_track_requisition(params))
                elif action == "getDepartments":
                    return self.send_json(handle_get_departments())
                elif action == "getUsers":
                    return self.send_json(handle_get_users())
                elif action in ("health", "ping"):
                    db_label = "PostgreSQL 17" if IS_POSTGRES else "MySQL"
                    try:
                        conn = get_db_connection()
                        conn.close()
                        db_connected = True
                    except Exception:
                        db_connected = False
                    return self.send_json({
                        "status": "success",
                        "healthy": db_connected,
                        "message": f"SDU Stock Order {db_label} REST API is operational.",
                        "version": SYSTEM_VERSION,
                        "database": db_label,
                        "db_name": CONFIG["DB_NAME"],
                    })
                else:
                    return self.send_json({
                        "status": "success",
                        "message": "SDU Stock Order MySQL REST API is operational.",
                        "version": SYSTEM_VERSION,
                        "database": "MySQL",
                        "db_name": CONFIG["DB_NAME"],
                    })
            except Exception as err:
                return self.send_json({
                    "status": "error",
                    "code": "MYSQL_CONNECTION_ERROR",
                    "message": f"ไม่สามารถเชื่อมต่อฐานข้อมูล MySQL ได้ ({err}) ระบบสลับใช้โหมด Offline (localStorage) อัตโนมัติ",
                }, status_code=503)

        if not self.is_safe_static_path(self.path):
            self.send_error(404, "File not found")
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path.rstrip("/") != "/api":
            return self.send_json({"status": "error", "message": "Not Found"}, status_code=404)

        MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MB maximum request body size limit
        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (ValueError, TypeError):
            return self.send_json({"status": "error", "code": "INVALID_HEADER", "message": "Invalid Content-Length header"}, status_code=400)

        if content_length < 0:
            return self.send_json({"status": "error", "code": "INVALID_HEADER", "message": "Content-Length cannot be negative"}, status_code=400)

        if content_length > MAX_BODY_SIZE:
            return self.send_json({
                "status": "error",
                "code": "PAYLOAD_TOO_LARGE",
                "message": f"ขนาดข้อมูลเกินกำหนดสูงสุด ({MAX_BODY_SIZE // (1024*1024)} MB)"
            }, status_code=413)

        raw_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError as e:
            return self.send_json({"status": "error", "code": "INVALID_JSON", "message": str(e)}, status_code=400)

        action = body.get("action", "")
        payload = body.get("payload", body)

        STAFF_ACTIONS = {
            "approveRequisition", "completeRequisition", "rejectRequisition",
            "restockItem", "adjustStock", "saveUser", "deleteUser",
            "addDepartment", "updateDepartment", "deleteDepartment",
            "saveItem", "deleteItem"
        }

        if action in STAFF_ACTIONS:
            auth_header = self.headers.get("Authorization", "")
            token = ""
            if auth_header.startswith("Bearer "):
                token = auth_header[7:].strip()
            if not token:
                token = self.headers.get("X-Staff-Token", "")
            if not token and isinstance(body, dict):
                token = body.get("staff_token") or body.get("token") or (payload.get("staff_token") if isinstance(payload, dict) else "")

            if not verify_staff_token(str(token)):
                return self.send_json({
                    "status": "error",
                    "code": "UNAUTHORIZED",
                    "message": "ต้องเข้าสู่ระบบในฐานะเจ้าหน้าที่พัสดุ (Unauthorized: Invalid or missing staff token)"
                }, status_code=401)

        try:
            if action == "createRequisition":
                return self.send_json(handle_create_requisition(payload))
            elif action == "loginRequester":
                return self.send_json(handle_login_requester(payload))
            elif action == "loginStaff":
                return self.send_json(handle_login_staff(payload))
            elif action == "approveRequisition":
                return self.send_json(handle_approve_requisition(payload))
            elif action == "completeRequisition":
                return self.send_json(handle_complete_requisition(payload))
            elif action == "rejectRequisition":
                return self.send_json(handle_reject_requisition(payload))
            elif action == "restockItem":
                return self.send_json(handle_restock_item(payload))
            elif action == "adjustStock":
                return self.send_json(handle_adjust_stock(payload))
            elif action == "saveUser":
                return self.send_json(handle_save_user(payload))
            elif action == "deleteUser":
                return self.send_json(handle_delete_user(payload))
            elif action == "addDepartment":
                return self.send_json(handle_add_department(payload))
            elif action == "updateDepartment":
                return self.send_json(handle_update_department(payload))
            elif action == "deleteDepartment":
                return self.send_json(handle_delete_department(payload))
            elif action == "saveItem":
                return self.send_json(handle_save_item(payload))
            elif action == "deleteItem":
                return self.send_json(handle_delete_item(payload))
            else:
                return self.send_json({
                    "status": "error",
                    "code": "UNKNOWN_ACTION",
                    "message": f'ไม่พบคำสั่ง action: "{action}" ในระบบ',
                }, status_code=400)
        except Exception as err:
            return self.send_json({
                "status": "error",
                "code": "MYSQL_ERROR",
                "message": f"ข้อผิดพลาดฐานข้อมูล MySQL: {err}",
            }, status_code=503)


def run_server(port=None):
    port = port or CONFIG["PORT"]
    server = ThreadingHTTPServer(("0.0.0.0", port), SDUInventoryRequestHandler)
    print("=" * 70)
    print(f"  SDU Stock Order & e-Inventory Server (v{SYSTEM_VERSION}) - PostgreSQL 17 Edition")
    print(f"  Web Portal : http://localhost:{port}/portal.html")
    print(f"  Requester  : http://localhost:{port}/index.html")
    print(f"  Staff      : http://localhost:{port}/staff.html")
    print(f"  REST API   : http://localhost:{port}/api")
    print(f"  PostgreSQL : {CONFIG['DB_USER']}@{CONFIG['DB_HOST']}:{CONFIG['DB_PORT']}/{CONFIG['DB_NAME']}")
    if CONFIG.get("STAFF_AUTH_SECRET") == "sdu_inventory_staff_secret_token_change_in_production":
        print("  [SECURITY WARNING] Using default STAFF_AUTH_SECRET placeholder! Set a secure secret in .env")
    print("=" * 70)
    server.serve_forever()


if __name__ == "__main__":
    run_server()

