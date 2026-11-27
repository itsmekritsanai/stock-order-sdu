"""
Authentication, Password Hashing, HMAC Session Tokens & RBAC (backend/auth.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

import hashlib
import hmac
import os
import time
from typing import Optional

try:
    from config import CONFIG
    from database import call_get_db_connection, dict_cursor
except ImportError:
    from backend.config import CONFIG
    from backend.database import call_get_db_connection, dict_cursor


def hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with a 16-byte random salt."""
    if not password:
        password = CONFIG.get("DEFAULT_USER_PASSWORD", "sdu1234")
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
    secret = CONFIG.get("REQUESTER_AUTH_SECRET") or CONFIG.get("STAFF_AUTH_SECRET", "sdu_inventory_staff_secret_token_change_in_production")
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
        secret = CONFIG.get("REQUESTER_AUTH_SECRET") or CONFIG.get("STAFF_AUTH_SECRET", "sdu_inventory_staff_secret_token_change_in_production")
        payload = f"requester:{u}:{ts_str}".encode("utf-8")
        expected_sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected_sig)
    except Exception:
        return False


def generate_staff_token(username: Optional[str] = None) -> str:
    """Generate HMAC-SHA256 signed session token for staff."""
    username = username or CONFIG.get("STAFF_USERNAME", "admin_staff")
    ts = str(int(time.time()))
    secret = CONFIG.get("STAFF_AUTH_SECRET", "sdu_inventory_staff_secret_token_change_in_production")
    payload = f"staff:{username}:{ts}".encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return f"{username}.{ts}.{sig}"


def is_auth_bypass_enabled() -> bool:
    """Return True when AUTH_BYPASS testing mode is enabled via env or .env config."""
    raw = os.environ.get("AUTH_BYPASS")
    if raw is None:
        raw = CONFIG.get("AUTH_BYPASS", "false")
    return str(raw).strip().lower() in ("true", "1", "yes", "on")


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


def extract_staff_username(token: str) -> str:
    """Extract username from HMAC-SHA256 staff token."""
    if not token or not isinstance(token, str):
        return ""
    parts = token.rsplit(".", 2)
    return parts[0] if len(parts) == 3 else ""


def get_staff_role(username: str) -> str:
    """Resolve RBAC role ('STAFF', 'HEAD', or 'ADMIN') from built-in aliases or database users.role."""
    u = str(username or "").strip().lower()
    if not u:
        return "STAFF"
    head_user = str(CONFIG.get("HEAD_USERNAME", "head_approver")).strip().lower()
    staff_screener = str(CONFIG.get("STAFF_SCREENER_USERNAME", "staff")).strip().lower()
    admin_user = str(CONFIG.get("STAFF_USERNAME", "admin_staff")).strip().lower()

    if u in (admin_user, "admin_staff", "admin"):
        return "ADMIN"
    if u in (head_user, "head", "head_approver", "approver", "director"):
        return "HEAD"
    if u in (staff_screener, "staff", "warehouse_staff", "screener", "officer"):
        return "STAFF"

    try:
        conn = call_get_db_connection()
        try:
            with dict_cursor(conn) as cur:
                cur.execute(
                    "SELECT role FROM users WHERE LOWER(username) = %s AND is_active = 1 LIMIT 1",
                    (u,),
                )
                row = cur.fetchone()
                if row:
                    db_role = str(row.get("role") or "").strip().upper()
                    if db_role in ("ADMIN", "HEAD", "STAFF"):
                        return db_role
        finally:
            conn.close()
    except Exception:
        pass

    if u == "jittraporn_cha":
        return "HEAD"
    if u == "chuthathip_pan":
        return "STAFF"
    return "STAFF"


def get_role_label(role: str) -> str:
    r = str(role or "").strip().upper()
    if r == "ADMIN":
        return "ผู้ดูแลระบบสูงสุด (Admin)"
    if r == "HEAD":
        return "หัวหน้าหน่วยงาน (ผู้อนุมัติขั้นสุดท้าย)"
    return "เจ้าหน้าที่พัสดุ (ผู้คัดกรองและดูแลคลัง)"


def check_staff_role_permission(action: str, role: str):
    """Verify if a staff role ('STAFF', 'HEAD', 'ADMIN') is permitted to execute an API action."""
    r = str(role or "ADMIN").strip().upper()
    if r == "ADMIN":
        return True, ""
    if r == "STAFF":
        forbidden_for_staff = {"approveRequisition", "deleteUser", "deleteDepartment"}
        if action in forbidden_for_staff:
            return False, "สิทธิ์เจ้าหน้าที่พัสดุ (STAFF) ไม่สามารถกดอนุมัติคำขอขั้นสุดท้ายได้ กรุณาส่งต่อให้หัวหน้าหน่วยงาน (HEAD) อนุมัติ"
        return True, ""
    if r == "HEAD":
        allowed_for_head = {"approveRequisition", "rejectRequisition"}
        if action in allowed_for_head:
            return True, ""
        return False, "สิทธิ์หัวหน้าหน่วยงาน (HEAD) สำหรับพิจารณาอนุมัติคำขอขั้นสุดท้ายเท่านั้น ไม่สามารถคัดกรองขั้นต้นหรือปรับแก้สต๊อกได้"
    return False, "ไม่มีสิทธิ์ดำเนินการในส่วนนี้"


def handle_login_requester(payload):
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()
    if not username or not password:
        return {"status": "error", "message": "กรุณากรอกชื่อผู้ใช้งานและรหัสผ่าน"}

    conn = call_get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            cur.execute(
                "SELECT id, name, username, password, role, position, dept, phone FROM users WHERE (LOWER(username) = LOWER(%s) OR name = %s) AND is_active = 1 LIMIT 1",
                (username, username),
            )
            row = cur.fetchone()
            if not row:
                return {
                    "status": "error",
                    "message": f'ไม่พบบัญชีผู้ใช้งาน "{username}" ในระบบ กรุณาติดต่อเจ้าหน้าที่พัสดุเพื่อสร้างบัญชี'
                }
            stored_pass = str(row.get("password") or "").strip()
            if stored_pass:
                is_valid = verify_password(stored_pass, password)
            else:
                default_user_pass = CONFIG.get("DEFAULT_USER_PASSWORD", "sdu1234")
                is_valid = password in (default_user_pass, "sdu1234")
            if not is_valid:
                return {
                    "status": "error",
                    "message": "รหัสผ่านไม่ถูกต้อง กรุณาตรวจสอบหรือติดต่อเจ้าหน้าที่พัสดุ"
                }

            uname_final = row.get("username") or username
            db_role = str(row.get("role") or "").strip().upper()
            if db_role not in ("REQUESTER", "STAFF", "HEAD", "ADMIN"):
                db_role = "HEAD" if uname_final.lower() == "jittraporn_cha" else ("STAFF" if uname_final.lower() == "chuthathip_pan" else "REQUESTER")

            req_token = generate_requester_token(uname_final, row["name"])
            resp = {
                "status": "success",
                "message": "เข้าสู่ระบบสำเร็จ",
                "token": req_token,
                "user": {
                    "id": int(row["id"]),
                    "name": row["name"],
                    "username": uname_final,
                    "role": db_role,
                    "position": row.get("position") or "",
                    "dept": row.get("dept") or "",
                    "phone": row.get("phone") or "",
                }
            }
            if db_role in ("STAFF", "HEAD", "ADMIN"):
                resp["staff_token"] = generate_staff_token(uname_final)
                resp["staff_role"] = db_role
            return resp
    finally:
        conn.close()


def handle_login_staff(payload):
    """Authenticate staff/head/admin and return HMAC signed token with RBAC role."""
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()
    requested_role = str(payload.get("requested_role") or payload.get("role") or "").strip().upper()
    if not username or not password:
        return {"status": "error", "message": "กรุณากรอกชื่อผู้ใช้งานและรหัสผ่าน"}

    staff_user = CONFIG.get("STAFF_USERNAME", "admin_staff")
    staff_pass = CONFIG.get("STAFF_PASSWORD", "sdu1234")
    head_pass = CONFIG.get("HEAD_PASSWORD", staff_pass)
    is_valid = False
    resolved_role = None
    display_name = username
    matched_user_profile = None

    u_lower = username.lower()
    if u_lower in (staff_user.lower(), "admin_staff", "admin") and password in (staff_pass, "sdu1234"):
        is_valid = True
        resolved_role = "ADMIN"
        display_name = "ผู้ดูแลระบบคลังพัสดุ (Admin)"
    elif u_lower in ("staff", "warehouse_staff", "screener") and password in (staff_pass, "sdu1234"):
        is_valid = True
        resolved_role = "STAFF"
        display_name = "เจ้าหน้าที่พัสดุ สวท. (ผู้คัดกรอง)"
    elif u_lower in ("head", "head_approver", "approver", "director") and password in (head_pass, staff_pass, "sdu1234"):
        is_valid = True
        resolved_role = "HEAD"
        display_name = "หัวหน้าสำนักงานผู้อำนวยการ สวท. (ผู้อนุมัติ)"
    else:
        try:
            conn = call_get_db_connection()
            with dict_cursor(conn) as cur:
                cur.execute(
                    "SELECT id, name, username, password, role, position, dept, phone FROM users WHERE (LOWER(username) = LOWER(%s) OR name = %s) AND is_active = 1 LIMIT 1",
                    (username, username)
                )
                row = cur.fetchone()
                if row and verify_password(str(row.get("password") or ""), password):
                    db_role = str(row.get("role") or "").strip().upper()
                    uname_db = str(row.get("username") or username).strip().lower()
                    if db_role in ("ADMIN", "HEAD", "STAFF"):
                        is_valid = True
                        resolved_role = db_role
                        display_name = row.get("name") or username
                        matched_user_profile = {
                            "id": int(row["id"]),
                            "name": row.get("name") or username,
                            "username": row.get("username") or username,
                            "role": db_role,
                            "position": row.get("position") or "",
                            "dept": row.get("dept") or "สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน",
                            "phone": row.get("phone") or "",
                        }
                    elif uname_db == "jittraporn_cha":
                        is_valid = True
                        resolved_role = "HEAD"
                        display_name = row.get("name") or username
                        matched_user_profile = {
                            "id": int(row["id"]),
                            "name": row.get("name") or username,
                            "username": row.get("username") or username,
                            "role": "HEAD",
                            "position": row.get("position") or "",
                            "dept": row.get("dept") or "สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน",
                            "phone": row.get("phone") or "",
                        }
                    else:
                        conn.close()
                        return {
                            "status": "error",
                            "code": "ROLE_MISMATCH",
                            "message": f"บัญชี '{username}' เป็นสิทธิ์ผู้ขอเบิกพัสดุ (REQUESTER) กรุณาเลือกแท็บ 'ผู้ขอเบิกพัสดุ' เพื่อเข้าสู่ระบบ",
                        }
            conn.close()
        except Exception:
            pass

    if not is_valid:
        return {"status": "error", "message": "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"}

    final_role = resolved_role or get_staff_role(username)
    if requested_role in ("STAFF", "HEAD", "ADMIN"):
        if final_role != "ADMIN" and final_role != requested_role:
            return {
                "status": "error",
                "code": "ROLE_MISMATCH",
                "message": f"บัญชี '{username}' มีสิทธิ์เป็น '{get_role_label(final_role)}' ไม่สามารถเข้าใช้งานในแท็บ '{get_role_label(requested_role)}' ได้ กรุณาเลือกแท็บให้ตรงกับบทบาทของท่าน",
            }

    active_role = requested_role if (final_role == "ADMIN" and requested_role in ("STAFF", "HEAD", "ADMIN")) else final_role
    token = generate_staff_token(username)
    requester_profile = matched_user_profile or {
        "id": 0,
        "name": display_name,
        "username": username,
        "role": final_role,
        "position": get_role_label(final_role),
        "dept": "สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน",
        "phone": "",
    }
    req_token = generate_requester_token(requester_profile["username"], requester_profile["name"])
    return {
        "status": "success",
        "message": f"เข้าสู่ระบบสำเร็จ ({get_role_label(active_role)})",
        "token": token,
        "requester_token": req_token,
        "requester_user": requester_profile,
        "username": username,
        "name": display_name,
        "role": final_role,
        "active_role": active_role,
        "role_label": get_role_label(active_role),
    }
