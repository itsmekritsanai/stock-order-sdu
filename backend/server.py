"""
Unified Web & REST API Server Entry Point (backend/server.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
Version: 3.9.0

Modular Backend Architecture:
- backend/config.py               : Environment configuration, constants, Thai date & docNo utilities
- backend/database.py             : ThreadedConnectionPool (PostgreSQL 17 / MySQL) & schema auto-migration (had_role_col)
- backend/auth.py                 : PBKDF2-HMAC-SHA256 password hashing, HMAC session tokens, RBAC & SSO login
- backend/inventory_handlers.py   : Inventory items & stock transaction handlers (restock, adjust, CRUD)
- backend/requisition_handlers.py : Two-tier requisition lifecycle & ACID row-level locking handlers
- backend/org_quota_handlers.py   : Users, departments & quota rules CRUD handlers
- backend/analytics_handlers.py   : Monthly analytics & native 6-sheet Excel (exportMonthlyAnalyticsExcel)
- backend/excel_export.py         : Zero-dependency native .xlsx workbook builder
"""

import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

try:
    from config import (
        CONFIG,
        IS_POSTGRES,
        PROJECT_ROOT,
        SCHEMA_SQL_PATH,
        STATUS_THAI_LABELS,
        THAI_MONTHS,
        format_thai_datetime,
        generate_doc_no,
        load_env_config,
        parse_month_date_range,
    )
    from database import (
        _PooledPgConnection,
        _get_pg_pool,
        dict_cursor,
        ensure_database_schema,
        get_db_connection,
    )
    from auth import (
        check_staff_role_permission,
        extract_staff_username,
        generate_requester_token,
        generate_staff_token,
        get_role_label,
        get_staff_role,
        handle_login_requester,
        handle_login_staff,
        hash_password,
        is_auth_bypass_enabled,
        verify_password,
        verify_requester_token,
        verify_staff_token,
    )
    from inventory_handlers import (
        handle_adjust_stock,
        handle_delete_item,
        handle_get_item_transactions,
        handle_get_items,
        handle_restock_item,
        handle_save_item,
    )
    from requisition_handlers import (
        handle_approve_requisition,
        handle_complete_requisition,
        handle_create_requisition,
        handle_get_requisitions,
        handle_reject_requisition,
        handle_track_requisition,
        handle_verify_requisition,
        resolve_effective_monthly_limits,
    )
    from org_quota_handlers import (
        handle_add_department,
        handle_delete_department,
        handle_delete_quota,
        handle_delete_user,
        handle_get_departments,
        handle_get_quotas,
        handle_get_users,
        handle_save_quota,
        handle_save_user,
        handle_update_department,
    )
    from analytics_handlers import (
        handle_export_monthly_analytics_excel,
        handle_get_monthly_analytics,
    )
    from excel_export import build_monthly_analytics_xlsx  # type: ignore[import-not-found]
except ImportError:
    from backend.config import (
        CONFIG,
        IS_POSTGRES,
        PROJECT_ROOT,
        SCHEMA_SQL_PATH,
        STATUS_THAI_LABELS,
        THAI_MONTHS,
        format_thai_datetime,
        generate_doc_no,
        load_env_config,
        parse_month_date_range,
    )
    from backend.database import (
        _PooledPgConnection,
        _get_pg_pool,
        dict_cursor,
        ensure_database_schema,
        get_db_connection,
    )
    from backend.auth import (
        check_staff_role_permission,
        extract_staff_username,
        generate_requester_token,
        generate_staff_token,
        get_role_label,
        get_staff_role,
        handle_login_requester,
        handle_login_staff,
        hash_password,
        is_auth_bypass_enabled,
        verify_password,
        verify_requester_token,
        verify_staff_token,
    )
    from backend.inventory_handlers import (
        handle_adjust_stock,
        handle_delete_item,
        handle_get_item_transactions,
        handle_get_items,
        handle_restock_item,
        handle_save_item,
    )
    from backend.requisition_handlers import (
        handle_approve_requisition,
        handle_complete_requisition,
        handle_create_requisition,
        handle_get_requisitions,
        handle_reject_requisition,
        handle_track_requisition,
        handle_verify_requisition,
        resolve_effective_monthly_limits,
    )
    from backend.org_quota_handlers import (
        handle_add_department,
        handle_delete_department,
        handle_delete_quota,
        handle_delete_user,
        handle_get_departments,
        handle_get_quotas,
        handle_get_users,
        handle_save_quota,
        handle_save_user,
        handle_update_department,
    )
    from backend.analytics_handlers import (
        handle_export_monthly_analytics_excel,
        handle_get_monthly_analytics,
    )
    from backend.excel_export import build_monthly_analytics_xlsx

SYSTEM_VERSION = "3.9.0"


# ==============================================================================
# HTTP REQUEST HANDLER (Static Files + /api Endpoints)
# ==============================================================================

class SDUInventoryRequestHandler(SimpleHTTPRequestHandler):
    directory = PROJECT_ROOT

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PROJECT_ROOT, **kwargs)

    def is_safe_static_path(self, path: str) -> bool:
        clean_path = path.split("?", 1)[0].split("#", 1)[0]
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
            "start.bat", ".env", ".env.example",
            "agents.md", ".cursorrules", "requirements.txt"
        }
        if parts and parts[-1].lower() in forbidden_files:
            return False

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

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        super().end_headers()

    def send_cors_headers(self):
        origin = self.headers.get("Origin", "")
        allowed = [o.strip() for o in CONFIG.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]
        if origin:
            parsed_origin = urlparse(origin)
            if parsed_origin.hostname in ("localhost", "127.0.0.1", "0.0.0.0") or origin in allowed:
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Staff-Token, X-Staff-Role, X-Requester-Token")

    def _extract_auth_token(self, body=None, payload=None):
        auth_header = self.headers.get("Authorization", "")
        token = ""
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
        if not token:
            token = self.headers.get("X-Staff-Token", "").strip()
        if not token:
            token = self.headers.get("X-Requester-Token", "").strip()
        if not token and isinstance(body, dict):
            token = str(
                body.get("staff_token")
                or body.get("requester_token")
                or body.get("token")
                or (payload.get("staff_token") if isinstance(payload, dict) else "")
                or (payload.get("requester_token") if isinstance(payload, dict) else "")
                or ""
            ).strip()
        return token

    def send_json(self, data, status_code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def send_bytes(self, body, content_type, filename):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
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

            STAFF_ONLY_GET_ACTIONS = {
                "getMonthlyAnalytics",
                "exportMonthlyAnalyticsExcel",
                "getItemTransactions",
            }
            AUTH_REQUIRED_GET_ACTIONS = {
                "getRequisitions",
                "getUsers",
                "getQuotas",
            }

            if action in STAFF_ONLY_GET_ACTIONS:
                token = self._extract_auth_token()
                if not verify_staff_token(token) and not is_auth_bypass_enabled():
                    return self.send_json({
                        "status": "error",
                        "code": "UNAUTHORIZED",
                        "message": "ต้องเข้าสู่ระบบในฐานะเจ้าหน้าที่พัสดุเพื่อเข้าถึงข้อมูลนี้",
                    }, status_code=401)
            elif action in AUTH_REQUIRED_GET_ACTIONS:
                token = self._extract_auth_token()
                if not (verify_staff_token(token) or verify_requester_token(token)) and not is_auth_bypass_enabled():
                    return self.send_json({
                        "status": "error",
                        "code": "UNAUTHORIZED",
                        "message": "กรุณาเข้าสู่ระบบก่อนเข้าถึงข้อมูลนี้",
                    }, status_code=401)

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
                elif action == "getQuotas":
                    return self.send_json(handle_get_quotas())
                elif action == "getMonthlyAnalytics":
                    return self.send_json(handle_get_monthly_analytics(params))
                elif action == "exportMonthlyAnalyticsExcel":
                    xlsx_bytes, filename = handle_export_monthly_analytics_excel(params)
                    return self.send_bytes(
                        xlsx_bytes,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        filename,
                    )
                elif action == "getItemTransactions":
                    return self.send_json(handle_get_item_transactions(params))
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
                        "message": f"ระบบจัดการวัสดุสำนักงานออนไลน์ ({db_label}) REST API is operational.",
                        "version": SYSTEM_VERSION,
                        "database": db_label,
                        "db_name": CONFIG["DB_NAME"],
                        "authBypass": is_auth_bypass_enabled(),
                    })
                else:
                    db_label = "PostgreSQL 17" if IS_POSTGRES else "MySQL"
                    return self.send_json({
                        "status": "success",
                        "message": f"ระบบจัดการวัสดุสำนักงานออนไลน์ ({db_label}) REST API is operational.",
                        "version": SYSTEM_VERSION,
                        "database": db_label,
                        "db_name": CONFIG["DB_NAME"],
                        "authBypass": is_auth_bypass_enabled(),
                    })
            except Exception as err:
                print(f"[ERROR] GET /api action={action}: {err}", flush=True)
                return self.send_json({
                    "status": "error",
                    "code": "DB_CONNECTION_ERROR",
                    "message": "ไม่สามารถเชื่อมต่อฐานข้อมูลได้ในขณะนี้ ระบบสลับใช้โหมด Offline (localStorage) อัตโนมัติ",
                }, status_code=503)

        if not self.is_safe_static_path(self.path):
            self.send_error(404, "File not found")
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path.rstrip("/") != "/api":
            return self.send_json({"status": "error", "message": "Not Found"}, status_code=404)

        MAX_BODY_SIZE = 10 * 1024 * 1024
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
            "verifyRequisition", "approveRequisition", "completeRequisition", "rejectRequisition",
            "restockItem", "adjustStock", "saveUser", "deleteUser",
            "addDepartment", "updateDepartment", "deleteDepartment",
            "saveItem", "deleteItem", "saveQuota", "deleteQuota"
        }

        if action == "createRequisition":
            token = self._extract_auth_token(body, payload)
            if not (verify_requester_token(token) or verify_staff_token(token)) and not is_auth_bypass_enabled():
                return self.send_json({
                    "status": "error",
                    "code": "UNAUTHORIZED",
                    "message": "กรุณาเข้าสู่ระบบก่อนส่งคำขอเบิกพัสดุ",
                }, status_code=401)

        if action in STAFF_ACTIONS:
            token = self._extract_auth_token(body, payload)

            if not verify_staff_token(str(token)):
                if is_auth_bypass_enabled():
                    override_role = self.headers.get("X-Staff-Role", "").strip().upper()
                    effective_role = override_role if override_role in ("STAFF", "HEAD", "ADMIN") else "ADMIN"
                else:
                    return self.send_json({
                        "status": "error",
                        "code": "UNAUTHORIZED",
                        "message": "ต้องเข้าสู่ระบบในฐานะเจ้าหน้าที่พัสดุ (Unauthorized: Invalid or missing staff token)"
                    }, status_code=401)
            else:
                token_user = extract_staff_username(str(token))
                token_role = get_staff_role(token_user)
                override_role = self.headers.get("X-Staff-Role", "").strip().upper()
                effective_role = override_role if (token_role == "ADMIN" and override_role in ("STAFF", "HEAD", "ADMIN")) else token_role

            allowed, reason_msg = check_staff_role_permission(action, effective_role)
            if not allowed:
                return self.send_json({
                    "status": "error",
                    "code": "FORBIDDEN_ROLE",
                    "message": reason_msg
                }, status_code=403)
            if isinstance(payload, dict) and "caller_role" not in payload:
                payload["caller_role"] = effective_role

        try:
            if action == "createRequisition":
                return self.send_json(handle_create_requisition(payload))
            elif action == "loginRequester":
                return self.send_json(handle_login_requester(payload))
            elif action == "loginStaff":
                return self.send_json(handle_login_staff(payload))
            elif action == "verifyRequisition":
                return self.send_json(handle_verify_requisition(payload))
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
            elif action == "saveQuota":
                return self.send_json(handle_save_quota(payload))
            elif action == "deleteQuota":
                return self.send_json(handle_delete_quota(payload))
            else:
                return self.send_json({
                    "status": "error",
                    "code": "UNKNOWN_ACTION",
                    "message": f'ไม่พบคำสั่ง action: "{action}" ในระบบ',
                }, status_code=400)
        except Exception as err:
            db_label = "PostgreSQL 17" if IS_POSTGRES else "MySQL"
            print(f"[ERROR] POST /api action={action}: {err}", flush=True)
            return self.send_json({
                "status": "error",
                "code": "DB_ERROR",
                "message": f"เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล {db_label} กรุณาลองใหม่อีกครั้ง",
            }, status_code=503)


def run_server(port=None):
    port = port or CONFIG["PORT"]
    host = CONFIG.get("HOST", "127.0.0.1")
    ensure_database_schema()
    server = ThreadingHTTPServer((host, port), SDUInventoryRequestHandler)
    print("=" * 70)
    print(f"  ระบบจัดการวัสดุสำนักงานออนไลน์ Server (v{SYSTEM_VERSION}) - PostgreSQL 17 Edition")
    print(f"  Bind Addr  : http://{host}:{port}")
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
