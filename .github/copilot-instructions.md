# GitHub Copilot Instructions (copilot-instructions.md)
# Project: Suan Dusit University e-Inventory & Requisition System (Stock Order SDU — v3.8.3)

## Project Summary & Core Mission
A standalone institutional web application for Suan Dusit University (SDU) backed by a PostgreSQL 17 relational database (`sdu_inventory`, 7 tables) managed via Docker Compose (with MySQL backward compatibility), served by a Python REST API (`backend/server.py` + zero-dependency Excel exporter `backend/excel_export.py`), providing a paperless two-tier supply requisition workflow with two strictly separated portals:
1. `index.html` (Requester Portal for 6 สวท. units and 15 seeded accounts from `Book1.xlsx`, with Auto-Role Login, Cross-Portal SSO, real-time personal/department quota display, and official 4-signature PDF)
2. `staff.html` (Private Staff/Head/Admin Portal protected by RBAC + HMAC tokens, supporting 2-tier approval, restock pricing, stock adjustment, quota rules, monthly analytics, and 6-sheet native `.xlsx` export)

---

## Key Constraints for Copilot & AI Code Generation

### 1. Architectural Guardrails
- **Zero-Build Frontend:** Use Pure HTML5, Vanilla CSS3 (Custom Variables), and Modern ES6+ JavaScript. Do not suggest or install npm packages, TailwindCSS, or frontend frameworks.
- **Relational Backend & Docker Infrastructure:** Database schema is defined in `backend/schema_postgres.sql` (PostgreSQL 17, 7 tables including `quota_rules`) and executed via `docker-compose.yml` (`postgres:17-alpine` bound to `127.0.0.1:5433`, `app` on port `8080`). Served via `backend/server.py` (`psycopg2-binary` with `ThreadedConnectionPool`, ACID transactions, and `SELECT ... FOR UPDATE` row locking).
- **Strict Boundary:** Never introduce staff actions (verification, approvals, item deletion, on-hand adjustments, quota/user/dept CRUD) into `index.html`.
- **Single Source of Truth:** Code for `index.html` and `staff.html` is generated through `scripts/generate_separated_portals.py`. Always reflect major structural changes in the Python generator and re-run it.

### 2. Business Logic & Inventory Equations
- **Available Stock Calculation:**
  $$\text{Available} = \text{On-Hand} - \text{Reserved}$$
- **Multi-Unit Calculation:**
  $$\text{Total Pieces} = (\text{Boxes} \times \text{Pieces Per Box}) + \text{Pieces}$$
- **Two-Tier State Transition:**
  - `PENDING`: Request created by requester (validated against available stock + `USER`/`DEPT` monthly quotas).
  - `VERIFIED`: Staff (`STAFF`/`ADMIN`) screened and forwarded to Head.
  - `APPROVED`: Department Head (`HEAD`/`ADMIN`) final approval; locks quota (`reserved_pieces += approved_pieces`). Does NOT deduct `on_hand_pieces`.
  - `COMPLETED`: Staff (`STAFF`/`ADMIN`) handed over items; deducts stock (`on_hand_pieces -= approved_pieces`, `reserved_pieces -= approved_pieces`) and logs an `OUT` record in `stock_transactions`.
  - `REJECTED`: Staff/Head/Admin rejected or cancelled; releases `reserved_pieces` if previously `APPROVED`.

### 3. UI/UX Rules
- **No Emoji in UI:** Use SVG icons (`svg_icons` dictionary in Python, `<svg class="svg-icon">` / `vIcons` in HTML/JS).
- **SweetAlert2 for All Dialogs:** Never generate `alert()`, `confirm()`, or `prompt()`. Use `Swal.fire()` with SDU blue theme (`#1e40af`).
- **Searchable Dropdown Standard:** Every `<select>` control (static and SweetAlert2 modals) must be searchable via `enhanceSearchableSelect`.
- **Typography:** Google Fonts `Prompt` for interfaces and `Sarabun` for official A4 PDF documents.

### 4. Code Style & Testing
- Indentation: 2 spaces for HTML/CSS/JS, 4 spaces for Python (PEP 8).
- Verification: `.agents/skills/stock-order-rules/scripts/verify_rules.py` and `pytest tests/test_stock_logic.py` (91 tests, coverage target >= 90%).
- All JavaScript must parse cleanly without syntax errors.

### 5. Strict Versioning & Changelog Protocol
- Whenever making code changes, bug fixes, or enhancements, increment `SYSTEM_VERSION` following Semantic Versioning (`MAJOR.MINOR.PATCH`).
- Record every change immediately in `CHANGELOG.md` following Keep a Changelog.
- Synchronize `SYSTEM_VERSION` across `CHANGELOG.md`, `backend/server.py`, `scripts/generate_separated_portals.py`, `tests/test_stock_logic.py`, and UI footers (`portal.html`, `index.html`, `staff.html`).
