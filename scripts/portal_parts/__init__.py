"""
Modular Portal Generator Components (scripts/portal_parts/__init__.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

from .requester_catalog_and_cart_js import REQUESTER_CATALOG_AND_CART_JS
from .requester_head_and_layout import REQUESTER_HEAD_AND_LAYOUT
from .requester_history_and_auth_js import REQUESTER_HISTORY_AND_AUTH_JS
from .seed_data import (
    build_dept_js_items,
    initial_items,
    initial_requisitions,
    parse_docx_depts_and_users,
)
from .shared_ui import (
    DYNAMIC_MONTH_JS,
    SEARCHABLE_SELECT_CSS,
    SEARCHABLE_SELECT_JS,
    svg_icons,
)
from .staff_admin_crud_js import STAFF_ADMIN_CRUD_JS
from .staff_analytics_and_reports_js import STAFF_ANALYTICS_AND_REPORTS_JS
from .staff_auth_and_requisitions_js import STAFF_AUTH_AND_REQUISITIONS_JS
from .staff_head_and_layout import STAFF_HEAD_AND_LAYOUT
from .staff_stock_and_inventory_js import STAFF_STOCK_AND_INVENTORY_JS

REQUESTER_TEMPLATE = (
    REQUESTER_HEAD_AND_LAYOUT
    + REQUESTER_CATALOG_AND_CART_JS
    + REQUESTER_HISTORY_AND_AUTH_JS
)

STAFF_TEMPLATE = (
    STAFF_HEAD_AND_LAYOUT
    + STAFF_AUTH_AND_REQUISITIONS_JS
    + STAFF_STOCK_AND_INVENTORY_JS
    + STAFF_ANALYTICS_AND_REPORTS_JS
    + STAFF_ADMIN_CRUD_JS
)

__all__ = [
    "DYNAMIC_MONTH_JS",
    "REQUESTER_CATALOG_AND_CART_JS",
    "REQUESTER_HEAD_AND_LAYOUT",
    "REQUESTER_HISTORY_AND_AUTH_JS",
    "REQUESTER_TEMPLATE",
    "SEARCHABLE_SELECT_CSS",
    "SEARCHABLE_SELECT_JS",
    "STAFF_ADMIN_CRUD_JS",
    "STAFF_ANALYTICS_AND_REPORTS_JS",
    "STAFF_AUTH_AND_REQUISITIONS_JS",
    "STAFF_HEAD_AND_LAYOUT",
    "STAFF_STOCK_AND_INVENTORY_JS",
    "STAFF_TEMPLATE",
    "build_dept_js_items",
    "initial_items",
    "initial_requisitions",
    "parse_docx_depts_and_users",
    "svg_icons",
]
