# GitHub Copilot Instructions (copilot-instructions.md)
# Project: Suan Dusit University e-Inventory & Requisition System (Stock Order SDU)

## Project Summary & Core Mission
A standalone institutional web application for Suan Dusit University (SDU) providing a seamless, paperless supply requisition workflow with two strictly separated portals:
1. `index.html` (Public Requester Portal for 90+ faculties and departments)
2. `staff.html` (Private Staff & Inventory Portal with E-Signature and official PDF generation)

---

## Key Constraints for Copilot & AI Code Generation

### 1. Architectural Guardrails
- **Zero-Build Frontend:** Use Pure HTML5, Vanilla CSS3 (Custom Variables), and Modern ES6+ JavaScript. Do not suggest or install npm packages, TailwindCSS, or frontend frameworks.
- **Strict Boundary:** Never introduce staff actions (approvals, item deletion, on-hand adjustments) into `index.html`.
- **Single Source of Truth:** Code for `index.html` and `staff.html` is generated through `generate_separated_portals.py`. Always reflect major structural changes in the Python generator.

### 2. Business Logic & Inventory Equations
- **Available Stock Calculation:**
  $$\text{Available} = \text{On-Hand} - \text{Reserved}$$
- **Multi-Unit Calculation:**
  $$\text{Total Pieces} = (\text{Boxes} \times \text{Pieces Per Box}) + \text{Pieces}$$
- **State Transition:**
  - `PENDING`: Request created by requester.
  - `APPROVED`: Staff approved; locks quota (`reserved_pieces += approved_pieces`).
  - `COMPLETED`: Requester signed digital pad; deducts stock (`on_hand_pieces -= approved_pieces`, `reserved_pieces -= approved_pieces`).
  - `REJECTED`: Staff rejected; releases reserved quota.

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
- Record every change immediately in `docs/CHANGELOG.md` following the Keep a Changelog standard (Added, Changed, Deprecated, Removed, Fixed, Security).
- Maintain version number synchronization across `docs/CHANGELOG.md`, `generate_separated_portals.py` (`SYSTEM_VERSION`), UI footers, and backend (`CONFIG.VERSION`).

