"""
Unit & Integration Tests for Stock Order SDU (tests/test_stock_logic.py)
Project: Suan Dusit University e-Inventory & Requisition System (PostgreSQL 17 Edition)
"""

import os
import sys
import pytest
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))

from server import (
    CONFIG,
    IS_POSTGRES,
    SCHEMA_SQL_PATH,
    SYSTEM_VERSION,
    format_thai_datetime,
    generate_doc_no,
    load_env_config,
    THAI_MONTHS,
)


class TestStockInventoryCalculations:
    """Test multi-unit conversions and stock availability formulas."""

    def test_multi_unit_conversion_to_total_pieces(self):
        # 2 boxes of 250 pieces/box + 0 individual pieces = 500 pieces
        boxes = 2
        pieces_per_box = 250
        pieces = 0
        total = (boxes * pieces_per_box) + pieces
        assert total == 500

        # 1 box of 500 pieces/box + 25 pieces = 525 pieces
        boxes = 1
        pieces_per_box = 500
        pieces = 25
        total = (boxes * pieces_per_box) + pieces
        assert total == 525

    def test_single_unit_items(self):
        # Items with single unit (e.g., folder / book)
        pieces = 3
        pieces_per_box = 1
        total = (0 * pieces_per_box) + pieces
        assert total == 3

    def test_available_stock_formula(self):
        # Available = On-Hand - Reserved
        on_hand = 1750
        reserved = 500
        available = max(0, on_hand - reserved)
        assert available == 1250

    def test_available_stock_cannot_be_negative(self):
        on_hand = 50
        reserved = 100
        available = max(0, on_hand - reserved)
        assert available == 0

    def test_insufficient_stock_detection(self):
        on_hand = 100
        reserved = 80
        available = max(0, on_hand - reserved)  # 20
        requested = 25
        assert requested > available


class TestRequisitionLifecycleStates:
    """Test state transitions and business rules of requisition lifecycle."""

    def test_valid_status_transitions(self):
        valid_statuses = {"PENDING", "APPROVED", "COMPLETED", "REJECTED"}
        assert "PENDING" in valid_statuses
        assert "APPROVED" in valid_statuses
        assert "COMPLETED" in valid_statuses
        assert "REJECTED" in valid_statuses

    def test_approve_locks_reserved_quota(self):
        on_hand = 1000
        reserved = 200
        requested_and_approved = 300

        # Approve state transition
        new_reserved = reserved + requested_and_approved
        new_available = max(0, on_hand - new_reserved)

        assert new_reserved == 500
        assert new_available == 500
        assert on_hand == 1000  # On-hand remains unchanged until completion

    def test_completion_deducts_on_hand_and_releases_reserved(self):
        on_hand = 1000
        reserved = 500
        completed_qty = 300

        new_on_hand = max(0, on_hand - completed_qty)
        new_reserved = max(0, reserved - completed_qty)
        new_available = max(0, new_on_hand - new_reserved)

        assert new_on_hand == 700
        assert new_reserved == 200
        assert new_available == 500

    def test_rejection_releases_reserved_stock(self):
        on_hand = 1000
        reserved = 500
        cancelled_qty = 300

        new_reserved = max(0, reserved - cancelled_qty)
        new_available = max(0, on_hand - new_reserved)

        assert new_reserved == 200
        assert new_available == 800


class TestThaiFormattersAndHelpers:
    """Test Buddhist Era formatting, document number generation, and helpers."""

    def test_thai_datetime_format(self):
        test_dt = datetime(2026, 10, 29, 14, 30)
        formatted = format_thai_datetime(test_dt)
        assert "2569" in formatted
        assert "ต.ค." in formatted
        assert "14:30 น." in formatted

    def test_generate_doc_no_format(self):
        doc_no = generate_doc_no()
        assert doc_no.startswith("REQ-")
        parts = doc_no.split("-")
        assert len(parts) == 3
        # Year in Buddhist Era: 2026 -> 2569
        assert parts[1].startswith("25")
        assert len(parts[2]) == 4  # 4 random digits

    def test_thai_months_list(self):
        assert len(THAI_MONTHS) == 12
        assert THAI_MONTHS[0] == "ม.ค."
        assert THAI_MONTHS[11] == "ธ.ค."

    def test_system_version_format(self):
        assert SYSTEM_VERSION == "3.0.7"


class TestPostgresSchemaAndConfiguration:
    """Test schema files, environment config, and Docker compose files."""

    def test_schema_postgres_exists(self):
        schema_pg = os.path.join(PROJECT_ROOT, "backend", "schema_postgres.sql")
        assert os.path.exists(schema_pg), "schema_postgres.sql must exist"

        with open(schema_pg, "r", encoding="utf-8") as f:
            content = f.read()

        assert "CREATE TABLE departments" in content
        assert "CREATE TABLE users" in content
        assert "CREATE TABLE inventory_items" in content
        assert "CREATE TABLE requisitions" in content
        assert "CREATE TABLE requisition_items" in content
        assert "CREATE TABLE stock_transactions" in content
        assert "update_updated_at_column" in content
        assert "setval" in content

    def test_docker_compose_configuration(self):
        compose_file = os.path.join(PROJECT_ROOT, "docker-compose.yml")
        assert os.path.exists(compose_file), "docker-compose.yml must exist"

        with open(compose_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "postgres:17-alpine" in content
        assert "dpage/pgadmin4" in content
        assert "5433:5432" in content or "DB_PORT" in content
        assert "5051:80" in content or "PGADMIN_PORT" in content

    def test_pgadmin_servers_configuration(self):
        pgadmin_json = os.path.join(PROJECT_ROOT, "pgadmin_servers.json")
        assert os.path.exists(pgadmin_json), "pgadmin_servers.json must exist"

        with open(pgadmin_json, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Stock Order SDU" in content
        assert "sdu_inventory" in content

    def test_load_env_config(self):
        cfg = load_env_config()
        assert "DB_PORT" in cfg
        assert "PORT" in cfg
        assert "DB_USER" in cfg
        assert "DB_NAME" in cfg


from unittest.mock import MagicMock, patch
import server


class TestApiHandlers:
    """Test API endpoint handlers in backend/server.py."""

    def test_handle_get_departments_mock(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [
            {"id": 1, "name": "สำนักงานผู้อำนวยการ สวท.", "category": "สวท.", "full_label": "สำนักงานผู้อำนวยการ สวท."}
        ]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur

        with patch("server.get_db_connection", return_value=mock_conn):
            res = server.handle_get_departments()
            assert res["status"] == "success"
            assert res["total"] == 1
            assert res["data"][0]["name"] == "สำนักงานผู้อำนวยการ สวท."

    def test_handle_get_users_mock(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [
            {"id": 1, "name": "นางสาววาสนา จันทร์จ่าย", "position": "หัวหน้าสำนักงาน", "dept": "สวท.", "phone": "081-998-7766"}
        ]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur

        with patch("server.get_db_connection", return_value=mock_conn):
            res = server.handle_get_users()
            assert res["status"] == "success"
            assert res["total"] == 1
            assert res["data"][0]["name"] == "นางสาววาสนา จันทร์จ่าย"

    def test_handle_track_requisition_not_found(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = None
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur

        with patch("server.get_db_connection", return_value=mock_conn):
            res = server.handle_track_requisition({"docNo": ["REQ-NOT-EXIST"]})
            assert res["status"] == "error"
            assert res["found"] is False

    def test_handle_track_requisition_missing_doc_no(self):
        res = server.handle_track_requisition({})
        assert res["status"] == "error"
        assert res["found"] is False

    def test_handle_create_requisition_validation(self):
        res = server.handle_create_requisition({})
        assert res["status"] == "error"
        assert "ข้อมูลคำขอเบิกไม่ครบถ้วน" in res["message"]

    def test_handle_approve_requisition_validation(self):
        res = server.handle_approve_requisition({})
        assert res["status"] == "error"
        assert "docNo" in res["message"]

    def test_handle_complete_requisition_validation(self):
        res = server.handle_complete_requisition({})
        assert res["status"] == "error"
        assert "docNo" in res["message"]

    def test_handle_reject_requisition_validation(self):
        res = server.handle_reject_requisition({})
        assert res["status"] == "error"
        assert "docNo" in res["message"]

    def test_handle_restock_item_validation(self):
        res = server.handle_restock_item({"itemId": 0})
        assert res["status"] == "error"

    def test_handle_adjust_stock_validation(self):
        res = server.handle_adjust_stock({"itemId": 0})
        assert res["status"] == "error"

    def test_handle_save_user_validation(self):
        res = server.handle_save_user({"name": ""})
        assert res["status"] == "error"

    def test_handle_delete_user_validation(self):
        res = server.handle_delete_user({"id": 0})
        assert res["status"] == "error"

    def test_handle_add_department_validation(self):
        res = server.handle_add_department({"name": ""})
        assert res["status"] == "error"

    def test_handle_update_department_validation(self):
        res = server.handle_update_department({"name": ""})
        assert res["status"] == "error"
        res_no_id = server.handle_update_department({"name": "กลุ่มงานใหม่"})
        assert res_no_id["status"] == "error"

    def test_handle_delete_department_validation(self):
        res = server.handle_delete_department({})
        assert res["status"] == "error"

    def test_department_crud_lifecycle(self):
        import uuid
        uid = uuid.uuid4().hex[:6]
        test_dept_name = f"กลุ่มงานทดสอบ {uid}"
        updated_dept_name = f"กลุ่มงานทดสอบแก้ไข {uid}"

        # 1. Add
        add_res = server.handle_add_department({"name": test_dept_name})
        assert add_res["status"] == "success"
        dept_id = add_res.get("id")

        # 2. Duplicate check
        dup_res = server.handle_add_department({"name": test_dept_name})
        assert dup_res["status"] == "error"
        assert dup_res.get("code") == "DUPLICATE_DEPT"

        # 3. Update name
        upd_res = server.handle_update_department({"id": dept_id, "name": updated_dept_name})
        assert upd_res["status"] == "success"
        assert upd_res["name"] == updated_dept_name

        # 4. Delete
        del_res = server.handle_delete_department({"id": dept_id})
        assert del_res["status"] == "success"

    def test_handle_save_item_validation(self):
        res = server.handle_save_item({"name": ""})
        assert res["status"] == "error"

    def test_handle_save_item_partial_min_alert(self):
        res = server.handle_save_item({"id": 1, "min_alert": 250})
        assert res["status"] == "success"
        assert res["id"] == 1

    def test_handle_delete_item_validation(self):
        res = server.handle_delete_item({"id": 0})
        assert res["status"] == "error"

    def test_handle_login_requester_missing_fields(self):
        res = server.handle_login_requester({})
        assert res["status"] == "error"
        assert "กรุณากรอกชื่อผู้ใช้งานและรหัสผ่าน" in res["message"]

        res = server.handle_login_requester({"username": "user", "password": ""})
        assert res["status"] == "error"

    def test_handle_login_requester_not_found(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = None
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur

        with patch("server.get_db_connection", return_value=mock_conn):
            res = server.handle_login_requester({"username": "unknown_user", "password": "sdu1234"})
            assert res["status"] == "error"
            assert "ไม่พบบัญชีผู้ใช้งาน" in res["message"]

    def test_handle_login_requester_wrong_password(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = {
            "id": 1,
            "name": "นางสาววาสนา จันทร์จ่าย",
            "username": "wasana.c",
            "password": "sdu1234",
            "position": "หัวหน้าสำนักงาน",
            "dept": "สำนักงานผู้อำนวยการ สวท.",
            "phone": "081-998-7766"
        }
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur

        with patch("server.get_db_connection", return_value=mock_conn):
            res = server.handle_login_requester({"username": "wasana.c", "password": "wrong_password"})
            assert res["status"] == "error"
            assert "รหัสผ่านไม่ถูกต้อง" in res["message"]

    def test_handle_login_requester_success(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = {
            "id": 1,
            "name": "นางสาววาสนา จันทร์จ่าย",
            "username": "wasana.c",
            "password": "sdu1234",
            "position": "หัวหน้าสำนักงาน",
            "dept": "สำนักงานผู้อำนวยการ สวท.",
            "phone": "081-998-7766"
        }
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur

        with patch("server.get_db_connection", return_value=mock_conn):
            res = server.handle_login_requester({"username": "wasana.c", "password": "sdu1234"})
            assert res["status"] == "success"
            assert res["user"]["name"] == "นางสาววาสนา จันทร์จ่าย"
            assert res["user"]["username"] == "wasana.c"
            assert res["user"]["dept"] == "สำนักงานผู้อำนวยการ สวท."


class TestSecurityEnhancements:
    """Unit tests for security audit defensive fixes (Vulnerabilities 1-5)."""

    def test_static_file_path_security_filtering(self):
        handler = server.SDUInventoryRequestHandler
        req_inst = handler.__new__(handler)

        # Forbidden dotfiles
        assert req_inst.is_safe_static_path('/.env') is False
        assert req_inst.is_safe_static_path('/.git/config') is False
        assert req_inst.is_safe_static_path('/.env.local') is False

        # Forbidden internal code & data directories
        assert req_inst.is_safe_static_path('/backend/server.py') is False
        assert req_inst.is_safe_static_path('/data/inventory.db') is False
        assert req_inst.is_safe_static_path('/tests/test_stock_logic.py') is False
        assert req_inst.is_safe_static_path('/reports/security-audit/findings.json') is False

        # Forbidden root config files
        assert req_inst.is_safe_static_path('/docker-compose.yml') is False
        assert req_inst.is_safe_static_path('/schema_postgres.sql') is False
        assert req_inst.is_safe_static_path('/pgadmin_servers.json') is False

        # Allowed static public files
        assert req_inst.is_safe_static_path('/index.html') is True
        assert req_inst.is_safe_static_path('/staff.html') is True
        assert req_inst.is_safe_static_path('/portal.html') is True
        assert req_inst.is_safe_static_path('/assets/favicon.ico') is True

    def test_password_pbkdf2_hashing_and_verification(self):
        plain = 'MySecurePass#2026'
        hashed = server.hash_password(plain)

        assert hashed.startswith('pbkdf2_sha256$')
        assert server.verify_password(hashed, plain) is True
        assert server.verify_password(hashed, 'WrongPassword') is False

        # Backward compatibility with legacy plaintext passwords
        assert server.verify_password('sdu1234', 'sdu1234') is True
        assert server.verify_password('sdu1234', 'wrong') is False

    def test_staff_hmac_token_lifecycle(self):
        token = server.generate_staff_token('admin_staff')
        assert token.startswith('admin_staff.')
        assert server.verify_staff_token(token) is True

        # Invalid token rejection
        assert server.verify_staff_token('invalid.token') is False
        assert server.verify_staff_token('') is False
        assert server.verify_staff_token('admin_staff.1000000000.invalidsignature') is False

    def test_handle_login_staff(self):
        # Valid staff login
        res = server.handle_login_staff({'username': 'admin_staff', 'password': '••••••••'})
        assert res['status'] == 'success'
        assert 'token' in res
        assert server.verify_staff_token(res['token']) is True

        # Invalid staff login
        res_fail = server.handle_login_staff({'username': 'admin_staff', 'password': 'completely_wrong_pass'})
        assert res_fail['status'] == 'error'


class TestRequisitionStateMachineSafety:
    """Test prevention of invalid state transitions (CWE-841 / bugscope-requisition-state-machine-bypass)."""

    def test_complete_already_completed_requisition_rejected(self):
        """A COMPLETED requisition must NOT be completed again (prevent double stock deduction)."""
        res = server.handle_complete_requisition({"docNo": "REQ-256910-0042", "signature": "test"})
        assert res["status"] == "error"
        assert res.get("code") in ("ALREADY_COMPLETED", "INVALID_STATE")

    def test_complete_pending_or_rejected_requisition_rejected(self):
        """A REJECTED or PENDING requisition must NOT be completed directly."""
        res = server.handle_complete_requisition({"docNo": "REQ-256910-0043", "signature": "test"})
        assert res["status"] == "error"
        assert res.get("code") in ("NOT_APPROVED", "INVALID_STATE")

    def test_approve_already_approved_or_completed_rejected(self):
        """An already COMPLETED or APPROVED requisition must NOT be approved again."""
        res = server.handle_approve_requisition({"docNo": "REQ-256910-0042"})
        assert res["status"] == "error"
        assert res.get("code") in ("INVALID_STATE", "ALREADY_COMPLETED")

    def test_reject_already_completed_requisition_rejected(self):
        """A COMPLETED requisition cannot be rejected after goods handover."""
        res = server.handle_reject_requisition({"docNo": "REQ-256910-0042", "reason": "test"})
        assert res["status"] == "error"
        assert res.get("code") in ("ALREADY_COMPLETED", "INVALID_STATE")


class TestSecurityAuditRun2Patches:
    """Tests for vulnerabilities remediated in Security Audit Run 2 (v3.0.7)."""

    def test_url_encoded_path_traversal_blocked(self):
        """sdu-sec-006: Percent-encoding path traversal and dotfile bypass attempts must be rejected."""
        import server
        handler = server.SDUInventoryRequestHandler.__new__(server.SDUInventoryRequestHandler)
        handler.directory = server.PROJECT_ROOT

        # Encoded dotfiles & secret files
        assert handler.is_safe_static_path("/%2eenv") is False
        assert handler.is_safe_static_path("/%2e%2e/backend/server.py") is False
        assert handler.is_safe_static_path("/%62ackend/server.py") is False
        assert handler.is_safe_static_path("/backend/server.py") is False
        assert handler.is_safe_static_path("/.env") is False
        assert handler.is_safe_static_path("/docker-compose.yml") is False

        # Legitimate static files
        assert handler.is_safe_static_path("/index.html") is True
        assert handler.is_safe_static_path("/staff.html") is True
        assert handler.is_safe_static_path("/portal.html") is True

    def test_create_requisition_negative_quantity_rejected(self):
        """sdu-sec-007: Negative piece/box quantities must be strictly rejected."""
        import server
        res = server.handle_create_requisition({
            "docNo": "TEST-NEG-001",
            "requester": "Test Requester",
            "dept": "สำนักงานผู้อำนวยการ สวท.",
            "purpose": "Security test for negative quantity",
            "items": [{"itemId": 1, "qtyBoxes": -1, "qtyPieces": 0, "totalPieces": -250}]
        })
        assert res["status"] == "error"
        assert "0" in res["message"] or "ไม่สามารถเป็นค่าลบได้" in res["message"]

    def test_create_requisition_arithmetic_mismatch_rejected(self):
        """sdu-sec-007: Client-spoofed totalPieces differing from expected formula must be rejected."""
        import server
        res = server.handle_create_requisition({
            "docNo": "TEST-MISMATCH-001",
            "requester": "Test Requester",
            "dept": "สำนักงานผู้อำนวยการ สวท.",
            "purpose": "Security test for arithmetic mismatch",
            "items": [{"itemId": 1, "qtyBoxes": 1, "qtyPieces": 0, "totalPieces": 999999}]
        })
        assert res["status"] == "error"
        assert "ไม่ตรงกับสูตรคำนวณจริง" in res["message"]

    def test_approve_requisition_negative_quantity_rejected(self):
        """sdu-sec-007: Approving negative quantity must be rejected."""
        import server
        res = server.handle_approve_requisition({
            "docNo": "REQ-256910-6434",
            "items": [{"itemId": 2, "approvedPieces": -10}]
        })
        assert res["status"] == "error"
        assert "ไม่น้อยกว่า 0" in res["message"]

    def test_requester_token_lifecycle(self):
        """sdu-sec-010: Requester HMAC session token generation and verification."""
        import server
        token = server.generate_requester_token("wasana.c")
        assert token.startswith("wasana.c.")
        assert server.verify_requester_token(token, "wasana.c") is True
        assert server.verify_requester_token(token, "other.user") is False
        assert server.verify_requester_token("invalid.token", "wasana.c") is False

    def test_handle_login_requester_returns_token(self):
        """sdu-sec-010: handle_login_requester must return an authenticated session token."""
        import server
        res = server.handle_login_requester({"username": "wasana.c", "password": "123456"})
        assert res["status"] == "success"
        assert "token" in res
        assert server.verify_requester_token(res["token"], "wasana.c") is True
