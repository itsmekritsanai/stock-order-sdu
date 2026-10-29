"""
Unified Web & MySQL REST API Server (backend/server.py)
Project: Suan Dusit University e-Inventory & Requisition System (Stock Order SDU)
Version: 2.2.0

Features:
- Serves Frontend Static Portals (index.html, staff.html, portal.html, assets/)
- Provides JSON REST API at /api connected to MySQL 8.0+ / MariaDB
- Implements ACID Transactions & Row-Level Locking (SELECT ... FOR UPDATE)
  to prevent inventory concurrency race conditions.
"""

import json
import os
import random
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

SYSTEM_VERSION = "2.2.0"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_SQL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")

THAI_MONTHS = [
    "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
    "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."
]


def load_env_config():
    """Load database and server settings from .env file and environment variables."""
    config = {
        "DB_HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "DB_PORT": int(os.environ.get("DB_PORT", "3306")),
        "DB_USER": os.environ.get("DB_USER", "root"),
        "DB_PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "DB_NAME": os.environ.get("DB_NAME", "sdu_inventory"),
        "PORT": int(os.environ.get("PORT", "8080")),
        "HOST": os.environ.get("HOST", "127.0.0.1"),
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


def get_db_connection(include_db=True):
    """Create a MySQL connection using PyMySQL or mysql-connector-python."""
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
    """Return a dictionary cursor compatible with both PyMySQL and mysql-connector."""
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
            cur.execute("SELECT * FROM departments WHERE is_active = 1 ORDER BY id ASC")
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
            # Verify stock availability with row-level read check
            for req_item in items:
                item_id = int(req_item.get("itemId"))
                total_pieces = int(req_item.get("totalPieces") or 0)
                cur.execute(
                    "SELECT id, name, on_hand_pieces, reserved_pieces, pieces_per_box FROM inventory_items WHERE id = %s FOR UPDATE",
                    (item_id,),
                )
                db_item = cur.fetchone()
                if not db_item:
                    conn.rollback()
                    return {"status": "error", "message": f"ไม่พบพัสดุรหัส {item_id} ในฐานข้อมูล"}

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

            cur.execute("SELECT * FROM requisition_items WHERE requisition_id = %s FOR UPDATE", (doc_no,))
            req_items = cur.fetchall()

            for ri in req_items:
                item_id = int(ri["item_id"])
                approved_qty = approved_overrides.get(item_id, int(ri["approved_pieces"] or ri["total_pieces"]))

                cur.execute("SELECT * FROM inventory_items WHERE id = %s FOR UPDATE", (item_id,))
                inv = cur.fetchone()
                if not inv:
                    continue

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

            cur.execute(
                "UPDATE requisitions SET status = 'COMPLETED', signature = %s WHERE id = %s",
                (signature, doc_no),
            )

        conn.commit()
        return {
            "status": "success",
            "docNo": doc_no,
            "statusNow": "COMPLETED",
            "message": "บันทึกลายเซ็นและตัดยอดคงคลังจริงใน MySQL เรียบร้อยแล้ว",
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

            if req["status"] == "APPROVED":
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

            cur.execute(
                "UPDATE requisitions SET status = 'REJECTED', reject_reason = %s WHERE id = %s",
                (reason, doc_no),
            )

        conn.commit()
        return {
            "status": "success",
            "docNo": doc_no,
            "statusNow": "REJECTED",
            "message": "ปฏิเสธคำขอและคืนยอดพัสดุใน MySQL เรียบร้อยแล้ว",
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
    if not name or not dept:
        return {"status": "error", "message": "กรุณาระบุชื่อ-นามสกุล และกลุ่มงาน/หน่วยงาน"}

    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute("SELECT id FROM departments WHERE full_label = %s OR name = %s LIMIT 1", (dept, dept))
            if not cur.fetchone():
                cat = "สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)"
                cur.execute(
                    "INSERT INTO departments (category, name, parent_name, full_label, is_active) VALUES (%s, %s, %s, %s, 1)",
                    (cat, dept, cat, dept),
                )
            if user_id:
                cur.execute("SELECT id FROM users WHERE id = %s", (int(user_id),))
                if cur.fetchone():
                    cur.execute(
                        "UPDATE users SET name = %s, position = %s, dept = %s, phone = %s, is_active = 1 WHERE id = %s",
                        (name, position, dept, phone, int(user_id)),
                    )
                else:
                    cur.execute(
                        "INSERT INTO users (id, name, position, dept, phone, is_active) VALUES (%s, %s, %s, %s, %s, 1)",
                        (int(user_id), name, position, dept, phone),
                    )
            else:
                cur.execute(
                    "INSERT INTO users (name, position, dept, phone, is_active) VALUES (%s, %s, %s, %s, 1)",
                    (name, position, dept, phone),
                )
                user_id = cur.lastrowid
        conn.commit()
        return {"status": "success", "message": "บันทึกข้อมูลบุคลากรสำเร็จ", "id": user_id}
    except Exception as e:
        conn.rollback()
        raise e
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
        return {"status": "error", "message": "กรุณาระบุชื่อหน่วยงาน"}
    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute("SELECT id FROM departments WHERE full_label = %s OR name = %s LIMIT 1", (name, name))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO departments (category, name, parent_name, full_label, is_active) VALUES (%s, %s, %s, %s, 1)",
                    (cat, name, cat, name),
                )
        conn.commit()
        return {"status": "success", "message": "เพิ่มกลุ่มงาน/หน่วยงานสำเร็จ", "name": name}
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

    if not name:
        return {"status": "error", "message": "กรุณาระบุชื่อรายการพัสดุ"}

    conn = get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            if item_id:
                cur.execute("SELECT id FROM inventory_items WHERE id = %s", (int(item_id),))
                if cur.fetchone():
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
# HTTP REQUEST HANDLER (Static Files + /api MySQL Endpoints)
# ==============================================================================

class SDUInventoryRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PROJECT_ROOT, **kwargs)

    def send_json(self, data, status_code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
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

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path.rstrip("/") != "/api":
            return self.send_json({"status": "error", "message": "Not Found"}, status_code=404)

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError as e:
            return self.send_json({"status": "error", "code": "INVALID_JSON", "message": str(e)}, status_code=400)

        action = body.get("action", "")
        payload = body.get("payload", body)

        try:
            if action == "createRequisition":
                return self.send_json(handle_create_requisition(payload))
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
    print(f"  SDU Stock Order & e-Inventory Server (v{SYSTEM_VERSION}) - MySQL Edition")
    print(f"  Web Portal : http://localhost:{port}/portal.html")
    print(f"  Requester  : http://localhost:{port}/index.html")
    print(f"  Staff      : http://localhost:{port}/staff.html")
    print(f"  MySQL API  : http://localhost:{port}/api")
    print(f"  MySQL DB   : {CONFIG['DB_USER']}@{CONFIG['DB_HOST']}:{CONFIG['DB_PORT']}/{CONFIG['DB_NAME']}")
    print("=" * 70)
    server.serve_forever()


if __name__ == "__main__":
    run_server()
