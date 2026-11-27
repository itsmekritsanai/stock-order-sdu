"""
Inventory Item & Stock Transaction Handlers (backend/inventory_handlers.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

from datetime import datetime

try:
    from config import IS_POSTGRES, format_thai_datetime
    from database import call_get_db_connection, dict_cursor
except ImportError:
    from backend.config import IS_POSTGRES, format_thai_datetime
    from backend.database import call_get_db_connection, dict_cursor


def handle_get_items(params):
    category = params.get("category", ["ALL"])[0]
    conn = call_get_db_connection()
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
                "monthly_limit": int(r.get("monthly_limit") or 0),
                "last_unit_price": round(float(r.get("last_unit_price") or 0), 2),
                "last_restocked_at": str(r["last_restocked_at"]) if r.get("last_restocked_at") else "",
                "image_piece": r["image_piece"] or "",
                "image_box": r["image_box"] or "",
            })
        return {"status": "success", "data": items, "total": len(items)}
    finally:
        conn.close()


def handle_get_item_transactions(params):
    raw_id = params.get("itemId", [""])[0] if isinstance(params.get("itemId"), list) else str(params.get("itemId") or "")
    raw_id = raw_id.strip()
    item_id = int(raw_id) if raw_id.isdigit() else 0

    conn = call_get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            if item_id > 0:
                cur.execute(
                    """
                    SELECT st.*, i.name AS item_name, i.unit_piece_name
                    FROM stock_transactions st
                    LEFT JOIN inventory_items i ON st.item_id = i.id
                    WHERE st.item_id = %s
                    ORDER BY st.created_at DESC, st.id DESC
                    LIMIT 200
                    """,
                    (item_id,),
                )
            else:
                cur.execute(
                    """
                    SELECT st.*, i.name AS item_name, i.unit_piece_name
                    FROM stock_transactions st
                    LEFT JOIN inventory_items i ON st.item_id = i.id
                    ORDER BY st.created_at DESC, st.id DESC
                    LIMIT 200
                    """
                )
            rows = cur.fetchall()

        tx_list = []
        for r in rows:
            dt_val = r.get("created_at")
            if isinstance(dt_val, datetime):
                fmt_date = format_thai_datetime(dt_val)
                iso_str = dt_val.strftime("%Y-%m-%d %H:%M:%S")
            else:
                iso_str = str(dt_val or "")
                fmt_date = iso_str
            tx_list.append({
                "id": int(r["id"]),
                "itemId": int(r["item_id"]),
                "itemName": r.get("item_name") or f"พัสดุ #{r['item_id']}",
                "unitPiece": r.get("unit_piece_name") or "ชิ้น",
                "transactionType": r["transaction_type"],
                "changePieces": int(r["change_pieces"] or 0),
                "balanceAfter": int(r["balance_after"] or 0),
                "unitPrice": round(float(r.get("unit_price") or 0), 2),
                "totalCost": round(float(r.get("total_cost") or 0), 2),
                "referenceType": r.get("reference_type") or "",
                "referenceId": r.get("reference_id") or "",
                "reason": r.get("reason") or "",
                "recordedBy": r.get("recorded_by") or "เจ้าหน้าที่พัสดุ สวท.",
                "createdAt": iso_str,
                "formattedDate": fmt_date,
            })
        return {"status": "success", "data": tx_list, "total": len(tx_list)}
    finally:
        conn.close()


def handle_restock_item(payload):
    item_id = int(payload.get("itemId") or 0)
    qty = int(payload.get("quantityPieces") or payload.get("quantity") or payload.get("qty") or 0)
    note = str(payload.get("note") or "รับพัสดุเข้าคลัง").strip()
    recorded_by = str(payload.get("recordedBy") or payload.get("recorded_by") or "เจ้าหน้าที่พัสดุ สวท.").strip()

    try:
        raw_unit_price = payload.get("unitPrice", payload.get("unit_price", 0))
        raw_total_cost = payload.get("totalCost", payload.get("total_cost", 0))
        unit_price = float(raw_unit_price if raw_unit_price not in (None, "") else 0)
        total_cost = float(raw_total_cost if raw_total_cost not in (None, "") else 0)
    except (TypeError, ValueError):
        return {"status": "error", "message": "กรุณาระบุราคาหรือยอดเงินซื้อเข้าเป็นตัวเลขที่ถูกต้อง"}

    if unit_price < 0 or total_cost < 0:
        return {"status": "error", "message": "ราคาต่อหน่วยและยอดเงินรวมต้องไม่ติดลบ"}

    if total_cost > 0 and unit_price <= 0 and qty > 0:
        unit_price = round(total_cost / qty, 2)
    elif unit_price > 0 and total_cost <= 0 and qty > 0:
        total_cost = round(unit_price * qty, 2)
    else:
        unit_price = round(unit_price, 2)
        total_cost = round(total_cost, 2)

    if not item_id or qty <= 0:
        return {"status": "error", "message": "กรุณาระบุรหัสพัสดุ (itemId) และจำนวนที่รับเข้ามากกว่า 0"}

    conn = call_get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute("SELECT * FROM inventory_items WHERE id = %s FOR UPDATE", (item_id,))
            inv = cur.fetchone()
            if not inv:
                conn.rollback()
                return {"status": "error", "message": f"ไม่พบพัสดุ ID {item_id}"}

            new_on_hand = int(inv["on_hand_pieces"] or 0) + qty
            now = datetime.now()
            if unit_price > 0:
                cur.execute(
                    "UPDATE inventory_items SET on_hand_pieces = %s, last_restocked_at = %s, last_unit_price = %s WHERE id = %s",
                    (new_on_hand, now, unit_price, item_id),
                )
            else:
                cur.execute(
                    "UPDATE inventory_items SET on_hand_pieces = %s, last_restocked_at = %s WHERE id = %s",
                    (new_on_hand, now, item_id),
                )
            cur.execute(
                """
                INSERT INTO stock_transactions (item_id, transaction_type, change_pieces, balance_after, unit_price, total_cost, reference_type, reference_id, reason, recorded_by, created_at)
                VALUES (%s, 'IN', %s, %s, %s, %s, 'STOCK_IN', NULL, %s, %s, %s)
                """,
                (item_id, qty, new_on_hand, unit_price, total_cost, note, recorded_by, now),
            )

        conn.commit()
        return {
            "status": "success",
            "message": "รับพัสดุเข้าคลังสำเร็จ",
            "itemId": item_id,
            "on_hand_pieces": new_on_hand,
            "unit_price": unit_price,
            "total_cost": total_cost,
            "last_restocked_at": str(now),
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
    recorded_by = str(payload.get("recordedBy") or payload.get("recorded_by") or "เจ้าหน้าที่พัสดุ สวท.").strip()

    if not item_id or new_qty is None or int(new_qty) < 0:
        return {"status": "error", "message": "กรุณาระบุรหัสพัสดุ (itemId) และยอดคงคลังจริงตั้งแต่ 0 ขึ้นไป"}

    new_qty = int(new_qty)
    conn = call_get_db_connection()
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
                INSERT INTO stock_transactions (item_id, transaction_type, change_pieces, balance_after, reference_type, reference_id, reason, recorded_by)
                VALUES (%s, 'ADJUST', %s, %s, 'ADJUSTMENT', NULL, %s, %s)
                """,
                (item_id, diff, new_qty, reason, recorded_by),
            )

        conn.commit()
        return {
            "status": "success",
            "message": "ปรับยอดสต๊อกจริงในฐานข้อมูลสำเร็จ",
            "itemId": item_id,
            "on_hand_pieces": new_qty,
            "reason": reason,
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
    monthly_limit = max(0, int(payload.get("monthly_limit") or payload.get("monthlyLimit") or 0))
    image_piece = str(payload.get("image_piece") or "assets/images/แฟ้มเสนอ เล่ม.jpeg").strip()
    image_box = str(payload.get("image_box") or image_piece).strip()
    recorded_by = str(payload.get("recordedBy") or payload.get("recorded_by") or "เจ้าหน้าที่พัสดุ สวท.").strip()

    if not item_id and not name:
        return {"status": "error", "message": "กรุณาระบุชื่อรายการพัสดุ"}

    conn = call_get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            is_new_insert = False
            if item_id:
                cur.execute("SELECT * FROM inventory_items WHERE id = %s", (int(item_id),))
                existing = cur.fetchone()
                if existing:
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
                    if "monthly_limit" not in payload and "monthlyLimit" not in payload:
                        monthly_limit = existing.get("monthly_limit") or 0
                    if "image_piece" not in payload:
                        image_piece = existing["image_piece"]
                    if "image_box" not in payload:
                        image_box = existing["image_box"]

                    cur.execute(
                        """
                        UPDATE inventory_items
                        SET name = %s, category = %s, is_multi_unit = %s,
                            unit_box_name = %s, unit_piece_name = %s, pieces_per_box = %s,
                            on_hand_pieces = %s, min_alert = %s, monthly_limit = %s,
                            image_piece = %s, image_box = %s, is_active = 1
                        WHERE id = %s
                        """,
                        (
                            name, category, is_multi_unit, unit_box_name, unit_piece_name,
                            pieces_per_box, on_hand_pieces, min_alert, monthly_limit,
                            image_piece, image_box, int(item_id),
                        ),
                    )
                else:
                    is_new_insert = True
                    cur.execute(
                        """
                        INSERT INTO inventory_items
                          (id, name, category, is_multi_unit, unit_box_name, unit_piece_name,
                           pieces_per_box, on_hand_pieces, reserved_pieces, min_alert, monthly_limit,
                           image_piece, image_box, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, %s, %s, %s, %s, 1)
                        """,
                        (
                            int(item_id), name, category, is_multi_unit, unit_box_name, unit_piece_name,
                            pieces_per_box, on_hand_pieces, min_alert, monthly_limit, image_piece, image_box,
                        ),
                    )
                    if IS_POSTGRES:
                        cur.execute("SELECT setval(pg_get_serial_sequence('inventory_items', 'id'), COALESCE(MAX(id), 1)) FROM inventory_items;")
            else:
                is_new_insert = True
                if IS_POSTGRES:
                    cur.execute(
                        """
                        INSERT INTO inventory_items
                          (name, category, is_multi_unit, unit_box_name, unit_piece_name,
                           pieces_per_box, on_hand_pieces, reserved_pieces, min_alert, monthly_limit,
                           image_piece, image_box, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, 0, %s, %s, %s, %s, 1)
                        RETURNING id
                        """,
                        (
                            name, category, is_multi_unit, unit_box_name, unit_piece_name,
                            pieces_per_box, on_hand_pieces, min_alert, monthly_limit, image_piece, image_box,
                        ),
                    )
                    row = cur.fetchone()
                    item_id = row["id"] if row else None
                else:
                    cur.execute(
                        """
                        INSERT INTO inventory_items
                          (name, category, is_multi_unit, unit_box_name, unit_piece_name,
                           pieces_per_box, on_hand_pieces, reserved_pieces, min_alert, monthly_limit,
                           image_piece, image_box, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, 0, %s, %s, %s, %s, 1)
                        """,
                        (
                            name, category, is_multi_unit, unit_box_name, unit_piece_name,
                            pieces_per_box, on_hand_pieces, min_alert, monthly_limit, image_piece, image_box,
                        ),
                    )
                    item_id = cur.lastrowid

            if is_new_insert and item_id and on_hand_pieces > 0:
                cur.execute(
                    """
                    INSERT INTO stock_transactions
                      (item_id, transaction_type, change_pieces, balance_after, unit_price, total_cost, reference_type, reference_id, reason, recorded_by)
                    VALUES (%s, 'IN', %s, %s, 0.00, 0.00, 'INITIAL_STOCK', NULL, %s, %s)
                    """,
                    (int(item_id), on_hand_pieces, on_hand_pieces, "ยอดคงคลังตั้งต้นเมื่อเพิ่มรายการพัสดุใหม่", recorded_by),
                )
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
    conn = call_get_db_connection()
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
