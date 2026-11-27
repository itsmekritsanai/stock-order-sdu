"""
Users, Departments & Quota Rule CRUD Handlers (backend/org_quota_handlers.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

import random

try:
    from auth import hash_password
    from config import CONFIG, IS_POSTGRES
    from database import call_get_db_connection, dict_cursor
except ImportError:
    from backend.auth import hash_password
    from backend.config import CONFIG, IS_POSTGRES
    from backend.database import call_get_db_connection, dict_cursor


def handle_get_departments():
    conn = call_get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute("""
                SELECT d.id, d.category, d.name, d.parent_name, d.full_label, d.is_active,
                       COALESCE(SUM(CASE WHEN u.is_active = 1 THEN 1 ELSE 0 END), 0) AS user_count
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
    conn = call_get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute("SELECT * FROM users WHERE is_active = 1 ORDER BY id ASC")
            rows = cur.fetchall()
        users = [
            {
                "id": int(r["id"]),
                "name": r["name"],
                "username": r.get("username") or "",
                "role": r.get("role") or "REQUESTER",
                "position": r.get("position") or "",
                "dept": r.get("dept") or "",
                "phone": r.get("phone") or "",
            }
            for r in rows
        ]
        return {"status": "success", "data": users, "total": len(users)}
    finally:
        conn.close()


def handle_get_quotas():
    conn = call_get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute("""
                SELECT q.id, q.target_type, q.target_key, q.item_id, q.monthly_limit,
                       q.note, q.updated_by, q.updated_at,
                       i.name AS item_name, i.unit_piece_name
                FROM quota_rules q
                LEFT JOIN inventory_items i ON q.item_id = i.id AND q.item_id > 0
                ORDER BY q.target_type ASC, q.target_key ASC, q.item_id ASC
            """)
            rows = cur.fetchall()
        data = [
            {
                "id": int(r["id"]),
                "targetType": r["target_type"],
                "target_type": r["target_type"],
                "targetKey": r["target_key"],
                "target_key": r["target_key"],
                "itemId": int(r["item_id"] or 0),
                "item_id": int(r["item_id"] or 0),
                "itemName": r.get("item_name") or ("ทุกพัสดุในคลัง (ค่าเริ่มต้น)" if int(r["item_id"] or 0) == 0 else f"พัสดุ #{r['item_id']}"),
                "unitPiece": r.get("unit_piece_name") or "ชิ้น",
                "monthlyLimit": int(r["monthly_limit"] or 0),
                "monthly_limit": int(r["monthly_limit"] or 0),
                "note": r.get("note") or "",
                "updatedBy": r.get("updated_by") or "",
                "updatedAt": str(r["updated_at"]) if r.get("updated_at") else "",
            }
            for r in rows
        ]
        return {"status": "success", "data": data, "total": len(data)}
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
    role = str(payload.get("role", "REQUESTER")).strip().upper()
    if role not in ("REQUESTER", "STAFF", "HEAD", "ADMIN"):
        role = "REQUESTER"

    if not name or not dept:
        return {"status": "error", "message": "กรุณาระบุชื่อ-นามสกุล และกลุ่มงาน/หน่วยงาน"}

    if not username:
        clean_name = name.replace("นางสาว", "").replace("นาย", "").replace("นาง", "").replace("ดร.", "").strip()
        parts = clean_name.split()
        username = parts[0].lower() if parts else f"user_{random.randint(100, 999)}"

    conn = call_get_db_connection()
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
            default_user_pass = CONFIG.get("DEFAULT_USER_PASSWORD", "sdu1234")
            if user_id:
                cur.execute("SELECT id, name, password, role FROM users WHERE id = %s", (int(user_id),))
                existing_row = cur.fetchone()
                if existing_row:
                    old_user_name = existing_row.get("name") or ""
                    final_pass = hash_password(raw_pass) if raw_pass else (existing_row.get("password") or hash_password(default_user_pass))
                    final_role = role if "role" in payload else (existing_row.get("role") or "REQUESTER")
                    cur.execute(
                        "UPDATE users SET name = %s, username = %s, password = %s, role = %s, position = %s, dept = %s, phone = %s, is_active = 1 WHERE id = %s",
                        (name, username, final_pass, final_role, position, dept, phone, int(user_id)),
                    )
                    if old_user_name and old_user_name != name:
                        cur.execute(
                            "UPDATE quota_rules SET target_key = %s WHERE target_type = 'USER' AND target_key = %s",
                            (name, old_user_name),
                        )
                else:
                    final_pass = hash_password(raw_pass) if raw_pass else hash_password(default_user_pass)
                    cur.execute(
                        "INSERT INTO users (id, name, username, password, role, position, dept, phone, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)",
                        (int(user_id), name, username, final_pass, role, position, dept, phone),
                    )
                    if IS_POSTGRES:
                        cur.execute("SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE(MAX(id), 1)) FROM users;")
            else:
                final_pass = hash_password(raw_pass) if raw_pass else hash_password(default_user_pass)
                if IS_POSTGRES:
                    cur.execute(
                        "INSERT INTO users (name, username, password, role, position, dept, phone, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s, 1) RETURNING id",
                        (name, username, final_pass, role, position, dept, phone),
                    )
                    row = cur.fetchone()
                    user_id = row["id"] if row else None
                else:
                    if not name:
                        return {"status": "error", "message": "กรุณาระบุชื่อรายการพัสดุ"}
                    cur.execute(
                        "INSERT INTO users (name, username, password, role, position, dept, phone, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s, 1)",
                        (name, username, final_pass, role, position, dept, phone),
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
                "role": role,
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


def handle_delete_user(payload):
    user_id = int(payload.get("id") or 0)
    if not user_id:
        return {"status": "error", "message": "ไม่พบรหัสบุคลากร"}
    conn = call_get_db_connection()
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
    conn = call_get_db_connection()
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

            if IS_POSTGRES:
                cur.execute(
                    "INSERT INTO departments (category, name, parent_name, full_label, is_active) VALUES (%s, %s, %s, %s, 1) RETURNING id",
                    (cat, name, cat, name),
                )
                inserted = cur.fetchone()
                dept_id = inserted["id"] if inserted else None
            else:
                cur.execute(
                    "INSERT INTO departments (category, name, parent_name, full_label, is_active) VALUES (%s, %s, %s, %s, 1)",
                    (cat, name, cat, name),
                )
                dept_id = cur.lastrowid
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
    if not dept_id and not old_name:
        return {"status": "error", "message": "กรุณาระบุ ID หรือชื่อเดิมของกลุ่มงาน"}

    conn = call_get_db_connection()
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
            cur.execute(
                "UPDATE quota_rules SET target_key = %s WHERE target_type = 'DEPT' AND (target_key = %s OR target_key = %s)",
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

    if not dept_id and not name:
        return {"status": "error", "message": "กรุณาระบุ ID หรือชื่อหน่วยงานที่ต้องการลบ"}

    conn = call_get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            if dept_id:
                cur.execute("SELECT * FROM departments WHERE id = %s AND is_active = 1", (int(dept_id),))
            else:
                cur.execute("SELECT * FROM departments WHERE (name = %s OR full_label = %s) AND is_active = 1 LIMIT 1", (name, name))

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


def handle_save_quota(payload):
    quota_id = payload.get("id")
    target_type = str(payload.get("targetType") or payload.get("target_type") or "").strip().upper()
    target_key = str(payload.get("targetKey") or payload.get("target_key") or "").strip()
    try:
        item_id = max(0, int(payload.get("itemId") if "itemId" in payload else (payload.get("item_id") or 0)))
        monthly_limit = max(0, int(payload.get("monthlyLimit") if "monthlyLimit" in payload else (payload.get("monthly_limit") or 0)))
    except (ValueError, TypeError):
        return {"status": "error", "message": "ค่าจำนวนโควตาหรือรหัสพัสดุต้องเป็นตัวเลขจำนวนเต็ม"}
    note = str(payload.get("note") or "").strip()
    updated_by = str(payload.get("updatedBy") or payload.get("updated_by") or "เจ้าหน้าที่พัสดุ สวท.").strip()

    if target_type not in ("USER", "DEPT"):
        return {"status": "error", "message": "ประเภทเป้าหมายโควตาต้องเป็น USER (บุคลากร) หรือ DEPT (กลุ่มงาน)"}
    if not target_key:
        return {"status": "error", "message": "กรุณาระบุชื่อบุคลากรหรือชื่อกลุ่มงาน/หน่วยงาน"}

    conn = call_get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute(
                "SELECT id FROM quota_rules WHERE target_type = %s AND target_key = %s AND item_id = %s LIMIT 1",
                (target_type, target_key, item_id),
            )
            conflict_row = cur.fetchone()
            target_id = None
            if quota_id:
                cur.execute("SELECT id FROM quota_rules WHERE id = %s LIMIT 1", (int(quota_id),))
                existing_by_id = cur.fetchone()
                if existing_by_id:
                    target_id = existing_by_id["id"]
            if target_id and conflict_row and int(conflict_row["id"]) != int(target_id):
                cur.execute("DELETE FROM quota_rules WHERE id = %s", (int(target_id),))
                target_id = int(conflict_row["id"])
            elif not target_id and conflict_row:
                target_id = int(conflict_row["id"])

            if target_id:
                cur.execute(
                    """
                    UPDATE quota_rules
                    SET target_type = %s, target_key = %s, item_id = %s, monthly_limit = %s,
                        note = %s, updated_by = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (target_type, target_key, item_id, monthly_limit, note, updated_by, target_id),
                )
            else:
                if IS_POSTGRES:
                    cur.execute(
                        """
                        INSERT INTO quota_rules (target_type, target_key, item_id, monthly_limit, note, updated_by)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (target_type, target_key, item_id, monthly_limit, note, updated_by),
                    )
                    ins = cur.fetchone()
                    target_id = int(ins["id"]) if ins else 0
                else:
                    cur.execute(
                        """
                        INSERT INTO quota_rules (target_type, target_key, item_id, monthly_limit, note, updated_by)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (target_type, target_key, item_id, monthly_limit, note, updated_by),
                    )
                    target_id = int(cur.lastrowid or 0)
        conn.commit()
        return {
            "status": "success",
            "message": f"บันทึกกฎโควตาสำหรับ '{target_key}' สำเร็จ",
            "id": target_id,
            "data": {
                "id": target_id,
                "targetType": target_type,
                "targetKey": target_key,
                "itemId": item_id,
                "monthlyLimit": monthly_limit,
                "note": note,
                "updatedBy": updated_by,
            },
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def handle_delete_quota(payload):
    quota_id = payload.get("id")
    target_type = str(payload.get("targetType") or payload.get("target_type") or "").strip().upper()
    target_key = str(payload.get("targetKey") or payload.get("target_key") or "").strip()
    item_id = payload.get("itemId") if "itemId" in payload else payload.get("item_id")

    if not quota_id and not (target_type and target_key):
        return {"status": "error", "message": "กรุณาระบุ ID หรือข้อมูลกฎโควตาที่ต้องการลบ"}

    conn = call_get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            if quota_id:
                cur.execute("DELETE FROM quota_rules WHERE id = %s", (int(quota_id),))
            elif item_id is not None:
                cur.execute(
                    "DELETE FROM quota_rules WHERE target_type = %s AND target_key = %s AND item_id = %s",
                    (target_type, target_key, int(item_id)),
                )
            else:
                cur.execute(
                    "DELETE FROM quota_rules WHERE target_type = %s AND target_key = %s",
                    (target_type, target_key),
                )
        conn.commit()
        return {"status": "success", "message": "ลบกฎโควตาเรียบร้อยแล้ว", "id": quota_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
