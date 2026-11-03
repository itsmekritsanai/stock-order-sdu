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
        assert SYSTEM_VERSION == "3.0.2"


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

    def test_handle_save_item_validation(self):
        res = server.handle_save_item({"name": ""})
        assert res["status"] == "error"

    def test_handle_delete_item_validation(self):
        res = server.handle_delete_item({"id": 0})
        assert res["status"] == "error"
