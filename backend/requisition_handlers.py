"""
Requisition Lifecycle & Two-Tier Approval Handlers (backend/requisition_handlers.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

import re
from datetime import datetime

try:
    from config import IS_POSTGRES, format_thai_datetime, generate_doc_no, parse_month_date_range
    from database import call_get_db_connection, dict_cursor
except ImportError:
    from backend.config import IS_POSTGRES, format_thai_datetime, generate_doc_no, parse_month_date_range
    from backend.database import call_get_db_connection, dict_cursor


def resolve_effective_monthly_limits(cur, item_id: int, item_default_limit: int, requester: str, dept: str):
    """Resolve effective monthly quota limits (personal_limit, dept_limit, user_src, dept_src).
    Precedence for personal quota: USER+item_id > USER+all_items(0) > inventory_items.monthly_limit.
    Precedence for department quota: DEPT+item_id > DEPT+all_items(0).
    Returns None when no limit applies at that tier.
    """
    user_item_rule = None
    user_all_rule = None
    dept_item_rule = None
    dept_all_rule = None

    try:
        cur.execute(
            """
            SELECT target_type, target_key, item_id, monthly_limit
            FROM quota_rules
            WHERE (target_type = 'USER' AND target_key = %s AND item_id IN (%s, 0))
               OR (target_type = 'DEPT' AND target_key = %s AND item_id IN (%s, 0))
            """,
            (requester, int(item_id), dept, int(item_id)),
        )
        rows = cur.fetchall()
        if isinstance(rows, list):
            for r in rows:
                t_type = str(r.get("target_type") or "").upper()
                r_item_id = int(r.get("item_id") or 0)
                if t_type == "USER":
                    if r_item_id == int(item_id):
                        user_item_rule = r
                    elif r_item_id == 0:
                        user_all_rule = r
                elif t_type == "DEPT":
                    if r_item_id == int(item_id):
                        dept_item_rule = r
                    elif r_item_id == 0:
                        dept_all_rule = r
    except Exception:
        pass

    if user_item_rule is not None:
        lim = int(user_item_rule.get("monthly_limit") or 0)
        eff_user_limit = lim if lim > 0 else None
        user_src = "USER_ITEM"
    elif user_all_rule is not None:
        lim = int(user_all_rule.get("monthly_limit") or 0)
        eff_user_limit = lim if lim > 0 else None
        user_src = "USER_ALL"
    elif int(item_default_limit or 0) > 0:
        eff_user_limit = int(item_default_limit)
        user_src = "ITEM_DEFAULT"
    else:
        eff_user_limit = None
        user_src = "NONE"

    if dept_item_rule is not None:
        d_lim = int(dept_item_rule.get("monthly_limit") or 0)
        eff_dept_limit = d_lim if d_lim > 0 else None
        dept_src = "DEPT_ITEM"
    elif dept_all_rule is not None:
        d_lim = int(dept_all_rule.get("monthly_limit") or 0)
        eff_dept_limit = d_lim if d_lim > 0 else None
        dept_src = "DEPT_ALL"
    else:
        eff_dept_limit = None
        dept_src = "NONE"

    return eff_user_limit, eff_dept_limit, user_src, dept_src


def handle_get_requisitions(params):
    status_filter = params.get("status", ["ALL"])[0]
    month_filter = params.get("month", ["ALL"])[0].strip()
    conn = call_get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            query = "SELECT * FROM requisitions WHERE 1=1"
            q_params = []
            if status_filter and status_filter != "ALL":
                query += " AND status = %s"
                q_params.append(status_filter)
            if month_filter and month_filter != "ALL":
                start_dt, end_dt, doc_pfx = parse_month_date_range(month_filter)
                if start_dt and end_dt:
                    query += " AND ((created_at IS NOT NULL AND created_at >= %s AND created_at < %s) OR id LIKE %s)"
                    q_params.extend([start_dt, end_dt, f"{doc_pfx}%"])
                else:
                    query += " AND id LIKE %s"
                    q_params.append(f"REQ-%{month_filter}%")

            query += " ORDER BY created_at DESC"
            cur.execute(query, tuple(q_params))
            req_rows = cur.fetchall()

            req_ids = [r["id"] for r in req_rows if r.get("id")]
            item_rows = []
            if req_ids:
                if IS_POSTGRES:
                    cur.execute(
                        "SELECT * FROM requisition_items WHERE requisition_id = ANY(%s) ORDER BY id ASC",
                        (req_ids,),
                    )
                else:
                    placeholders = ", ".join(["%s"] * len(req_ids))
                    cur.execute(
                        f"SELECT * FROM requisition_items WHERE requisition_id IN ({placeholders}) ORDER BY id ASC",
                        tuple(req_ids),
                    )
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
                "verified_by": r.get("verified_by") or "",
                "verified_at": str(r["verified_at"]) if r.get("verified_at") else "",
                "verified_date": r.get("verified_date") or "",
                "approved_by": r.get("approved_by") or "",
                "approved_at": str(r["approved_at"]) if r.get("approved_at") else "",
                "approved_date": r.get("approved_date") or "",
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

    conn = call_get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute(
                "SELECT * FROM requisitions WHERE LOWER(id) = LOWER(%s) LIMIT 1",
                (doc_no,),
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


def handle_create_requisition(payload):
    requester = str(payload.get("requester", "")).strip()
    dept = str(payload.get("dept", "")).strip()
    phone = str(payload.get("phone", "")).strip()
    purpose = str(payload.get("purpose", "")).strip()
    items = payload.get("items", [])

    if not requester or not dept or not purpose or not items or not isinstance(items, list):
        return {"status": "error", "message": "ข้อมูลคำขอเบิกไม่ครบถ้วน (ผู้เบิก, หน่วยงาน, วัตถุประสงค์, รายการพัสดุ)"}

    raw_doc_no = str(payload.get("id") or "").strip()
    if raw_doc_no and re.fullmatch(r"REQ-\d{6}-\d{4}", raw_doc_no):
        doc_no = raw_doc_no
    else:
        doc_no = generate_doc_no()
    thai_date = str(payload.get("date") or format_thai_datetime()).strip()

    parsed_items = []
    agg_totals_by_item = {}
    for req_item in items:
        try:
            item_id = int(req_item.get("itemId") or 0)
            qty_boxes = int(req_item.get("qtyBoxes") or 0)
            qty_pieces = int(req_item.get("qtyPieces") or 0)
            total_pieces = int(req_item.get("totalPieces") or 0)
        except (ValueError, TypeError):
            return {"status": "error", "message": "จำนวนพัสดุต้องเป็นตัวเลขจำนวนเต็มที่ถูกต้อง"}

        if item_id <= 0:
            return {"status": "error", "message": "รหัสพัสดุ (itemId) ไม่ถูกต้อง"}

        if qty_boxes < 0 or qty_pieces < 0 or total_pieces <= 0 or (qty_boxes == 0 and qty_pieces == 0):
            return {"status": "error", "message": "จำนวนพัสดุที่ขอเบิกต้องมากกว่า 0 และไม่สามารถเป็นค่าลบได้"}

        parsed_items.append({
            "itemId": item_id,
            "qtyBoxes": qty_boxes,
            "qtyPieces": qty_pieces,
            "totalPieces": total_pieces,
            "name": req_item.get("name", ""),
            "unitBox": req_item.get("unitBox", ""),
            "unitPiece": req_item.get("unitPiece", "ชิ้น"),
            "piecesPerBoxSnapshot": int(req_item.get("piecesPerBoxSnapshot") or 1),
        })
        agg_totals_by_item[item_id] = agg_totals_by_item.get(item_id, 0) + total_pieces

    conn = call_get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            db_items_map = {}
            for item_id in sorted(agg_totals_by_item.keys()):
                cur.execute(
                    "SELECT id, name, is_multi_unit, on_hand_pieces, reserved_pieces, pieces_per_box, monthly_limit, unit_piece_name FROM inventory_items WHERE id = %s FOR UPDATE",
                    (item_id,),
                )
                db_item = cur.fetchone()
                if not db_item:
                    conn.rollback()
                    return {"status": "error", "message": f"ไม่พบพัสดุรหัส {item_id} ในฐานข้อมูล"}
                db_items_map[item_id] = db_item

            for p_item in parsed_items:
                db_item = db_items_map[p_item["itemId"]]
                ratio = max(1, int(db_item.get("pieces_per_box") or 1))
                expected_total = (p_item["qtyBoxes"] * ratio) + p_item["qtyPieces"] if db_item.get("is_multi_unit") else p_item["qtyPieces"]
                if p_item["totalPieces"] != expected_total or expected_total <= 0:
                    conn.rollback()
                    return {
                        "status": "error",
                        "message": f"จำนวนรวมของพัสดุ ({p_item['totalPieces']}) ไม่ตรงกับสูตรคำนวณจริง ({expected_total})",
                    }

            cur_now = datetime.now()
            cur_iso_month = cur_now.strftime("%Y-%m")
            month_start, month_end, doc_pfx = parse_month_date_range(cur_iso_month)
            cur_be_doc = f"{doc_pfx}%" if doc_pfx else f"REQ-{(cur_now.year + 543)}{cur_now.month:02d}-%"

            for item_id in sorted(agg_totals_by_item.keys()):
                db_item = db_items_map[item_id]
                agg_requested = agg_totals_by_item[item_id]
                available = max(0, int(db_item["on_hand_pieces"]) - int(db_item["reserved_pieces"]))
                if agg_requested > available:
                    conn.rollback()
                    return {
                        "status": "error",
                        "code": "INSUFFICIENT_STOCK",
                        "message": "ยอดพัสดุคงเหลือพร้อมเบิกไม่เพียงพอ",
                        "details": {"itemId": item_id, "requested": agg_requested, "available": available},
                    }

                eff_user_limit, eff_dept_limit, _, _ = resolve_effective_monthly_limits(
                    cur, item_id, int(db_item.get("monthly_limit") or 0), requester, dept
                )
                unit_p = db_item.get("unit_piece_name") or "ชิ้น"

                if eff_user_limit is not None and eff_user_limit > 0:
                    cur.execute(
                        """
                        SELECT COALESCE(SUM(ri.total_pieces), 0) AS month_total
                        FROM requisitions r
                        JOIN requisition_items ri ON r.id = ri.requisition_id
                        WHERE ri.item_id = %s
                          AND r.requester = %s
                          AND r.status != 'REJECTED'
                          AND (
                            (r.created_at IS NOT NULL AND r.created_at >= %s AND r.created_at < %s)
                            OR (r.created_at IS NULL AND r.id LIKE %s)
                          )
                        """,
                        (item_id, requester, month_start, month_end, cur_be_doc),
                    )
                    month_row = cur.fetchone()
                    current_month_total = int(month_row["month_total"] or 0) if month_row else 0
                    if current_month_total + agg_requested > eff_user_limit:
                        conn.rollback()
                        rem = max(0, eff_user_limit - current_month_total)
                        return {
                            "status": "error",
                            "code": "QUOTA_EXCEEDED",
                            "message": f"บุคลากร '{requester}' ขอเบิก '{db_item['name']}' เกินโควตาสูงสุดประจำเดือนต่อท่าน (จำกัด {eff_user_limit} {unit_p}/ท่าน/เดือน, ในเดือนนี้ท่านเบิกไปแล้ว {current_month_total} {unit_p}, คงเหลือโควตา {rem} {unit_p})",
                            "details": {
                                "itemId": item_id,
                                "requester": requester,
                                "monthlyLimit": eff_user_limit,
                                "currentMonthTotal": current_month_total,
                                "remainingQuota": rem,
                                "requested": agg_requested,
                            },
                        }

                if eff_dept_limit is not None and eff_dept_limit > 0:
                    cur.execute(
                        """
                        SELECT COALESCE(SUM(ri.total_pieces), 0) AS month_total
                        FROM requisitions r
                        JOIN requisition_items ri ON r.id = ri.requisition_id
                        WHERE ri.item_id = %s
                          AND r.dept = %s
                          AND r.status != 'REJECTED'
                          AND (
                            (r.created_at IS NOT NULL AND r.created_at >= %s AND r.created_at < %s)
                            OR (r.created_at IS NULL AND r.id LIKE %s)
                          )
                        """,
                        (item_id, dept, month_start, month_end, cur_be_doc),
                    )
                    dept_row = cur.fetchone()
                    dept_month_total = int(dept_row["month_total"] or 0) if dept_row else 0
                    if dept_month_total + agg_requested > eff_dept_limit:
                        conn.rollback()
                        dept_rem = max(0, eff_dept_limit - dept_month_total)
                        return {
                            "status": "error",
                            "code": "DEPT_QUOTA_EXCEEDED",
                            "message": f"กลุ่มงาน '{dept}' ขอเบิก '{db_item['name']}' เกินโควตาสูงสุดประจำเดือนของกลุ่มงาน (จำกัด {eff_dept_limit} {unit_p}/กลุ่มงาน/เดือน, ในเดือนนี้กลุ่มงานเบิกไปแล้ว {dept_month_total} {unit_p}, คงเหลือโควตา {dept_rem} {unit_p})",
                            "details": {
                                "itemId": item_id,
                                "dept": dept,
                                "monthlyLimit": eff_dept_limit,
                                "currentMonthTotal": dept_month_total,
                                "remainingQuota": dept_rem,
                                "requested": agg_requested,
                            },
                        }

            inserted_req = False
            for _attempt in range(5):
                try:
                    cur.execute("SAVEPOINT sp_req_insert")
                    cur.execute(
                        """
                        INSERT INTO requisitions (id, date, requester, dept, phone, purpose, status, signature, reject_reason)
                        VALUES (%s, %s, %s, %s, %s, %s, 'PENDING', NULL, '')
                        """,
                        (doc_no, thai_date, requester, dept, phone, purpose),
                    )
                    cur.execute("RELEASE SAVEPOINT sp_req_insert")
                    inserted_req = True
                    break
                except Exception as ins_err:
                    err_txt = str(ins_err).lower()
                    if "unique" in err_txt or "duplicate" in err_txt:
                        try:
                            cur.execute("ROLLBACK TO SAVEPOINT sp_req_insert")
                        except Exception:
                            pass
                        doc_no = generate_doc_no()
                        continue
                    raise
            if not inserted_req:
                conn.rollback()
                return {"status": "error", "message": "ไม่สามารถสร้างเลขที่เอกสารคำขอที่ไม่ซ้ำได้ กรุณาลองใหม่อีกครั้ง"}

            for p_item in parsed_items:
                db_item = db_items_map[p_item["itemId"]]
                approved_pieces = p_item["totalPieces"]
                ratio_snap = max(1, int(db_item.get("pieces_per_box") or p_item["piecesPerBoxSnapshot"] or 1))
                cur.execute(
                    """
                    INSERT INTO requisition_items
                      (requisition_id, item_id, name, qty_boxes, qty_pieces, total_pieces, unit_box, unit_piece, approved_pieces, pieces_per_box_snapshot)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        doc_no,
                        p_item["itemId"],
                        p_item["name"] or db_item.get("name", ""),
                        p_item["qtyBoxes"],
                        p_item["qtyPieces"],
                        p_item["totalPieces"],
                        p_item["unitBox"],
                        p_item["unitPiece"],
                        approved_pieces,
                        ratio_snap,
                    ),
                )

        conn.commit()
        return {
            "status": "success",
            "message": "สร้างคำขอเบิกพัสดุในฐานข้อมูลสำเร็จ",
            "docNo": doc_no,
            "createdAt": datetime.now().isoformat(),
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def handle_verify_requisition(payload):
    doc_no = str(payload.get("docNo") or payload.get("id") or "").strip()
    verified_by = str(payload.get("verifiedBy") or payload.get("verified_by") or "เจ้าหน้าที่พัสดุ สวท.").strip()
    caller_role = str(payload.get("caller_role") or payload.get("role") or "").strip().upper()
    if caller_role == "HEAD":
        return {
            "status": "error",
            "code": "FORBIDDEN_ROLE",
            "message": "สิทธิ์หัวหน้าหน่วยงาน (HEAD) ไม่สามารถทำการคัดกรองขั้นต้นได้ (เฉพาะเจ้าหน้าที่พัสดุ STAFF หรือ ADMIN)",
        }

    approved_overrides = {
        int(i["itemId"]): int(i["approvedPieces"])
        for i in payload.get("items", [])
        if "itemId" in i and "approvedPieces" in i
    }

    if not doc_no:
        return {"status": "error", "message": "กรุณาระบุเลขที่เอกสารคำขอ (docNo)"}

    conn = call_get_db_connection()
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
                    "message": f"ไม่สามารถคัดกรองได้เนื่องจากคำขอเลขที่ {doc_no} อยู่ในสถานะ {current_status} (ต้องอยู่ในสถานะ PENDING)",
                }

            cur.execute("SELECT * FROM requisition_items WHERE requisition_id = %s ORDER BY item_id ASC, id ASC FOR UPDATE", (doc_no,))
            req_items = cur.fetchall()

            for ri in req_items:
                item_id = int(ri["item_id"])
                approved_qty = approved_overrides.get(item_id, int(ri["approved_pieces"] if ri["approved_pieces"] is not None else ri["total_pieces"]))
                if approved_qty < 0:
                    conn.rollback()
                    return {"status": "error", "message": "จำนวนพัสดุที่เสนออนุมัติต้องไม่น้อยกว่า 0"}

                cur.execute(
                    "UPDATE requisition_items SET approved_pieces = %s WHERE id = %s",
                    (approved_qty, ri["id"]),
                )

            now = datetime.now()
            verified_date = str(payload.get("verified_date") or payload.get("verifiedDate") or format_thai_datetime(now)).strip()

            cur.execute(
                """
                UPDATE requisitions 
                SET status = 'VERIFIED', verified_by = %s, verified_at = %s, verified_date = %s
                WHERE id = %s
                """,
                (verified_by, now, verified_date, doc_no),
            )

        conn.commit()
        return {
            "status": "success",
            "docNo": doc_no,
            "statusNow": "VERIFIED",
            "verified_by": verified_by,
            "verified_at": str(now),
            "verified_date": verified_date,
            "message": "ผ่านการคัดกรองเบื้องต้นและส่งต่อให้หัวหน้าอนุมัติเรียบร้อยแล้ว",
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def handle_approve_requisition(payload):
    caller_role = str(payload.get("caller_role") or payload.get("role") or "").strip().upper()
    if caller_role == "STAFF":
        return {
            "status": "error",
            "code": "FORBIDDEN_ROLE",
            "message": "สิทธิ์เจ้าหน้าที่พัสดุ (STAFF) ไม่สามารถกดอนุมัติคำขอขั้นสุดท้ายได้ กรุณาส่งต่อให้หัวหน้าหน่วยงาน (HEAD) เป็นผู้อนุมัติ",
        }

    for i in payload.get("items", []):
        try:
            if "approvedPieces" in i and int(i["approvedPieces"]) < 0:
                return {"status": "error", "message": "จำนวนพัสดุที่อนุมัติต้องไม่น้อยกว่า 0"}
        except (ValueError, TypeError):
            return {"status": "error", "message": "จำนวนพัสดุที่อนุมัติต้องเป็นตัวเลขที่ถูกต้อง"}

    doc_no = str(payload.get("docNo") or payload.get("id") or "").strip()
    approved_by = str(payload.get("approvedBy") or payload.get("approved_by") or "หัวหน้าฝ่าย/ผู้อำนวยการ สวท.").strip()
    approved_overrides = {
        int(i["itemId"]): int(i["approvedPieces"])
        for i in payload.get("items", [])
        if "itemId" in i and "approvedPieces" in i
    }

    if not doc_no:
        return {"status": "error", "message": "กรุณาระบุเลขที่เอกสารคำขอ (docNo)"}

    conn = call_get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute("SELECT * FROM requisitions WHERE id = %s FOR UPDATE", (doc_no,))
            req = cur.fetchone()
            if not req:
                conn.rollback()
                return {"status": "error", "message": f"ไม่พบเอกสารคำขอเลขที่ {doc_no}"}

            current_status = req.get("status", "")
            if current_status not in ("VERIFIED", "PENDING"):
                conn.rollback()
                return {
                    "status": "error",
                    "code": "INVALID_STATE",
                    "message": f"ไม่สามารถอนุมัติได้เนื่องจากคำขอเลขที่ {doc_no} อยู่ในสถานะ {current_status}",
                }

            cur.execute("SELECT * FROM requisition_items WHERE requisition_id = %s ORDER BY item_id ASC, id ASC FOR UPDATE", (doc_no,))
            req_items = cur.fetchall()

            for ri in req_items:
                item_id = int(ri["item_id"])
                approved_qty = approved_overrides.get(item_id, int(ri["approved_pieces"] if ri["approved_pieces"] is not None else ri["total_pieces"]))

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

            now = datetime.now()
            approved_date = str(payload.get("approved_date") or payload.get("approvedDate") or format_thai_datetime(now)).strip()

            cur.execute(
                """
                UPDATE requisitions 
                SET status = 'APPROVED', approved_by = %s, approved_at = %s, approved_date = %s
                WHERE id = %s
                """,
                (approved_by, now, approved_date, doc_no),
            )

        conn.commit()
        return {
            "status": "success",
            "docNo": doc_no,
            "statusNow": "APPROVED",
            "approved_by": approved_by,
            "approved_at": str(now),
            "approved_date": approved_date,
            "message": "อนุมัติคำขอขั้นสุดท้ายและล็อกยอดพัสดุสำเร็จ",
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def handle_complete_requisition(payload):
    doc_no = str(payload.get("docNo") or payload.get("id") or "").strip()
    signature = str(payload.get("signature") or "").strip()
    recorded_by = str(payload.get("recordedBy") or payload.get("recorded_by") or "เจ้าหน้าที่พัสดุ สวท.").strip()

    if not doc_no:
        return {"status": "error", "message": "กรุณาระบุเลขที่เอกสารคำขอ (docNo)"}

    conn = call_get_db_connection()
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

            cur.execute("SELECT * FROM requisition_items WHERE requisition_id = %s ORDER BY item_id ASC, id ASC FOR UPDATE", (doc_no,))
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
                    INSERT INTO stock_transactions (item_id, transaction_type, change_pieces, balance_after, reference_type, reference_id, reason, recorded_by)
                    VALUES (%s, 'OUT', %s, %s, 'REQUISITION', %s, %s, %s)
                    """,
                    (item_id, -approved_qty, new_on_hand, doc_no, f"จ่ายพัสดุตามใบเบิก {doc_no}", recorded_by),
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

    conn = call_get_db_connection()
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
                cur.execute("SELECT * FROM requisition_items WHERE requisition_id = %s ORDER BY item_id ASC, id ASC FOR UPDATE", (doc_no,))
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
