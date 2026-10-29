# GitHub Copilot Instructions (copilot-instructions.md)
# Project: Suan Dusit University e-Inventory & Requisition System (Stock Order SDU)

## Project Summary & Core Mission
A standalone institutional web application for Suan Dusit University (SDU) backed by a MySQL relational database (`sdu_inventory`) and Python REST API (`backend/server.py`), providing a seamless, paperless supply requisition workflow with two strictly separated portals:
1. `index.html` (Public Requester Portal for 5 สวท. units and 4 initial department heads from `รายนามบุคลากร สวท.docx`)
2. `staff.html` (Private Staff & Inventory Portal with E-Signature, official PDF generation, Inventory Item CRUD, and User/Department Management)

---

## Key Constraints for Copilot & AI Code Generation

### 1. Architectural Guardrails
- **Zero-Build Frontend:** Use Pure HTML5, Vanilla CSS3 (Custom Variables), and Modern ES6+ JavaScript. Do not suggest or install npm packages, TailwindCSS, or frontend frameworks.
- **MySQL Relational Backend:** Database schema is defined in `backend/schema.sql` (`InnoDB`, `utf8mb4_unicode_ci`) and served via `backend/server.py` (`PyMySQL` with ACID transactions and `SELECT ... FOR UPDATE` row locking).
- **Strict Boundary:** Never introduce staff actions (approvals, item deletion, on-hand adjustments) into `index.html`.
- **Single Source of Truth:** Code for `index.html` and `staff.html` is generated through `scripts/generate_separated_portals.py`. Always reflect major structural changes in the Python generator.

### 2. Business Logic & Inventory Equations
- **Available Stock Calculation:**
  $$\text{Available} = \text{On-Hand} - \text{Reserved}$$
- **Multi-Unit Calculation:**
  $$\text{Total Pieces} = (\text{Boxes} \times \text{Pieces Per Box}) + \text{Pieces}$$
- **State Transition:**
  - `PENDING`: Request created by requester.
  - `APPROVED`: Staff approved; locks quota (`reserved_pieces += approved_pieces`).
  - `COMPLETED`: Requester signed digital pad; deducts stock (`on_hand_pieces -= approved_pieces`, `reserved_pieces -= approved_pieces`) and logs an `OUT` record in `stock_transactions`.
  - `REJECTED`: Staff rejected or cancelled; releases reserved quota.

### 3. UI/UX Rules
- **No Emoji in UI:** Use SVG icons (`svg_icons` dictionary in Python, `<svg class="svg-icon">` in HTML).
- **SweetAlert2 for All Dialogs:** Never generate `alert()`, `confirm()`, or `prompt()`. Use `Swal.fire()` with SDU blue theme (`#1e40af`).
- **Typography:** Google Fonts `Prompt` for interfaces and `Sarabun` for official documents.

### 4. Code Style & Testing
- Indentation: 2 spaces for HTML/CSS/JS, 4 spaces for Python (PEP 8).
- Python Testing: `pytest` with code coverage target >= 90%.
- All JavaScript must parse cleanly without syntax errors in Node.js.

### 5. Strict Versioning & Changelog Protocol
- Whenever making code changes, bug fixes, or enhancements, increment the system version following Semantic Versioning (`MAJOR.MINOR.PATCH`).
- Record every change immediately in `CHANGELOG.md` following the Keep a Changelog standard (Added, Changed, Deprecated, Removed, Fixed, Security).
- Maintain version number synchronization across `CHANGELOG.md`, `scripts/generate_separated_portals.py` (`SYSTEM_VERSION`), UI footers, and backend (`backend/server.py` `SYSTEM_VERSION`).
