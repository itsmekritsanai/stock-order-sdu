"""
Single Source of Truth (SSOT) Portal Generator (scripts/generate_separated_portals.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
Version: 3.9.0

Modular Portal Generator Architecture:
- scripts/portal_parts/seed_data.py                     : DOCX department/user parser, 34 initial items, initial requisitions
- scripts/portal_parts/shared_ui.py                     : Vector SVG icon registry (svg_icons), Searchable Select & Dynamic Month JS/CSS
- scripts/portal_parts/requester_head_and_layout.py     : Requester Portal (index.html) HTML head, CSS & body layout
- scripts/portal_parts/requester_catalog_and_cart_js.py : Requester Portal DB sync, catalog, quota & cart drawer JS
- scripts/portal_parts/requester_history_and_auth_js.py : Requester Portal My Requisitions, 4-party A4 PDF & Auto-Role Login/SSO JS
- scripts/portal_parts/staff_head_and_layout.py         : Staff Portal (staff.html) HTML head, CSS, login card & dashboard layout
- scripts/portal_parts/staff_auth_and_requisitions_js.py: Staff Portal DB/API sync, RBAC, SSO & two-tier requisition approval JS
- scripts/portal_parts/staff_stock_and_inventory_js.py  : Staff Portal 3-mode restock pricing, stock adjust, PDF & inventory history JS
- scripts/portal_parts/staff_analytics_and_reports_js.py: Staff Portal monthly analytics, purchase costs, per-person & Excel/PDF export JS
- scripts/portal_parts/staff_admin_crud_js.py           : Staff Portal item, user, department & quota rules CRUD modals JS
"""

import json
import os
import re
import sys

SYSTEM_VERSION = "3.9.0"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from portal_parts import (  # noqa: E402
    DYNAMIC_MONTH_JS,
    REQUESTER_TEMPLATE,
    SEARCHABLE_SELECT_CSS,
    SEARCHABLE_SELECT_JS,
    STAFF_TEMPLATE,
    build_dept_js_items,
    initial_items,
    initial_requisitions,
    parse_docx_depts_and_users,
    svg_icons,
)

DEPT_DOCX_PATH = os.path.join(PROJECT_ROOT, "data", "รายนามบุคลากร สวท.docx")


def load_generator_env():
    """Load generator environment variables from .env and process environment."""
    cfg = {
        "MYSQL_API_URL": "/api",
        "DEFAULT_USER_PASSWORD": "password123",
        "STAFF_PASSWORD": "sdu1234",
        "STAFF_USERNAME": "admin_staff",
        "AUTH_BYPASS": False,
    }
    env_path = os.path.join(PROJECT_ROOT, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as ef:
            for line in ef:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k == "API_BASE_URL":
                    cfg["MYSQL_API_URL"] = v
                elif k == "DEFAULT_USER_PASSWORD":
                    cfg["DEFAULT_USER_PASSWORD"] = v
                elif k == "STAFF_PASSWORD":
                    cfg["STAFF_PASSWORD"] = v
                elif k == "STAFF_USERNAME":
                    cfg["STAFF_USERNAME"] = v
                elif k == "AUTH_BYPASS":
                    cfg["AUTH_BYPASS"] = v.lower() in ("true", "1", "yes", "on")

    if os.environ.get("API_BASE_URL"):
        cfg["MYSQL_API_URL"] = os.environ["API_BASE_URL"]
    if os.environ.get("DEFAULT_USER_PASSWORD"):
        cfg["DEFAULT_USER_PASSWORD"] = os.environ["DEFAULT_USER_PASSWORD"]
    if os.environ.get("STAFF_PASSWORD"):
        cfg["STAFF_PASSWORD"] = os.environ["STAFF_PASSWORD"]
    if os.environ.get("STAFF_USERNAME"):
        cfg["STAFF_USERNAME"] = os.environ["STAFF_USERNAME"]
    if "AUTH_BYPASS" in os.environ and os.environ["AUTH_BYPASS"] != "":
        cfg["AUTH_BYPASS"] = os.environ["AUTH_BYPASS"].strip().lower() in ("true", "1", "yes", "on")
    return cfg


_ENV_CFG = load_generator_env()
MYSQL_API_URL = _ENV_CFG["MYSQL_API_URL"]
DEFAULT_USER_PASSWORD = _ENV_CFG["DEFAULT_USER_PASSWORD"]
STAFF_PASSWORD = _ENV_CFG["STAFF_PASSWORD"]
STAFF_USERNAME = _ENV_CFG["STAFF_USERNAME"]
AUTH_BYPASS = _ENV_CFG["AUTH_BYPASS"]

depts_data, initial_users = parse_docx_depts_and_users(DEPT_DOCX_PATH)
dept_js_items = build_dept_js_items(depts_data)
dept_json_str = json.dumps(dept_js_items, ensure_ascii=False, indent=2)
users_json_str = json.dumps(initial_users, ensure_ascii=False, indent=2)

requester_template = REQUESTER_TEMPLATE
staff_template = STAFF_TEMPLATE


def render_portal_template(template_str: str) -> str:
    """Replace SSOT tokens in a portal HTML template."""
    return (
        template_str
        .replace("__SYSTEM_VERSION__", SYSTEM_VERSION)
        .replace("__AUTH_BYPASS__", "true" if AUTH_BYPASS else "false")
        .replace("__SEARCHABLE_SELECT_CSS__", SEARCHABLE_SELECT_CSS)
        .replace("__DYNAMIC_MONTH_JS__", DYNAMIC_MONTH_JS)
        .replace("__SEARCHABLE_SELECT_JS__", SEARCHABLE_SELECT_JS)
        .replace("__DEFAULT_ITEMS__", json.dumps(initial_items, ensure_ascii=False))
        .replace("__DEFAULT_REQS__", json.dumps(initial_requisitions, ensure_ascii=False))
        .replace("__DEFAULT_DEPTS__", dept_json_str)
        .replace("__DEFAULT_USERS__", users_json_str)
    )


def sync_portal_hub_version(version: str = SYSTEM_VERSION) -> bool:
    """Synchronize SYSTEM_VERSION in portal.html footer and version badge."""
    portal_path = os.path.join(PROJECT_ROOT, "portal.html")
    if not os.path.exists(portal_path):
        return False
    with open(portal_path, "r", encoding="utf-8") as f:
        portal_content = f.read()
    updated_portal = re.sub(
        r"(ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต\s*)v[0-9]+\.[0-9]+\.[0-9]+",
        rf"\g<1>v{version}",
        portal_content,
    )
    updated_portal = re.sub(
        r'(<span class="version-pill">)v[0-9]+\.[0-9]+\.[0-9]+(</span>)',
        rf"\g<1>v{version}\g<2>",
        updated_portal,
    )
    if updated_portal != portal_content:
        with open(portal_path, "w", encoding="utf-8") as f:
            f.write(updated_portal)
        print(f"Updated portal.html footer version to v{version}")
        return True
    return False


def generate_all_portals():
    """Compile and write index.html, staff.html, and sync portal.html version."""
    requester_html = render_portal_template(requester_template)
    with open(os.path.join(PROJECT_ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(requester_html)
    print("Created index.html (Requester Only Portal)")

    staff_html = render_portal_template(staff_template)
    with open(os.path.join(PROJECT_ROOT, "staff.html"), "w", encoding="utf-8") as f:
        f.write(staff_html)
    print("Created staff.html (Inventory Staff & Admin Portal)")

    sync_portal_hub_version(SYSTEM_VERSION)
    return requester_html, staff_html


if __name__ == "__main__":
    generate_all_portals()
