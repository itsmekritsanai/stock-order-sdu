# Architecture & Single Source of Truth (references/architecture-and-ssot.md)

This reference outlines the system architecture, dual-portal segregation, backend design, and Single Source of Truth (SSOT) protocols.

---

## 1. Single Source of Truth (SSOT)

* **Generator Script:** [`scripts/generate_separated_portals.py`](file:///c:/Users/namtarn/Downloads/stock-order-sdu/scripts/generate_separated_portals.py)
* **Rule:** `index.html` and `staff.html` are generated artifacts.
* **Workflow:**
  1. Parse `data/รายนามบุคลากร สวท.docx` for the official 5 departments and initial department heads.
  2. Embed initial items, default users, default requisitions, and `SYSTEM_VERSION`.
  3. Output clean, self-contained `index.html` and `staff.html`.
* **When making structural HTML/CSS/JS edits:**
  - Update `scripts/generate_separated_portals.py` first (or synchronously).
  - Execute `.venv\Scripts\python scripts/generate_separated_portals.py`.
  - Verify that running the generator produces identical code with zero unintended diffs.

---

## 2. Zero-Build Frontend Architecture

* **Framework Policy:** No React, No Vue, No Angular, No Next.js, No TailwindCSS.
* **Stack:**
  - Semantic HTML5
  - Vanilla CSS3 with Design Tokens (`--primary: #1e40af`, `--accent: #059669`, `--warning: #d97706`, `--danger: #dc2626`)
  - Modern ES6+ JavaScript
* **Runtime Overhead:** 0ms build step. Browser refresh immediately loads latest changes.

---

## 3. Strict 100% Portal Separation (Zero-Trust)

* **Requester Portal (`index.html`):**
  - Public-facing entry point for university personnel.
  - Requires simple username/password requester authentication.
  - Features: Search catalog, multi-unit selector, cart drawer, requisition submission, personal history ("My Requisitions"), official PDF printout.
  - **Forbidden:** Approval buttons, stock adjustment, physical handover, item/user/department management.
* **Staff Portal (`staff.html`):**
  - Warehouse administration portal.
  - Protected by PBKDF2 password hashing and HMAC-SHA256 session tokens.
  - Features: Metrics dashboard, approval queue, physical stock deduction, searchable restock & stock adjustment, min alert threshold configuration, user CRUD, department CRUD.

---

## 4. Backend & Database Architecture

* **Database Engine:** PostgreSQL 17 (`postgres:17-alpine`) on port `5433` via Docker Compose (with MySQL fallback compatibility).
* **Database Name:** `sdu_inventory`
* **Tables:** `departments`, `users`, `inventory_items`, `requisitions`, `requisition_items`, `stock_transactions`.
* **Web & API Server:** `backend/server.py` using Python `ThreadingHTTPServer` and `psycopg2-binary`.
* **Concurrency Protection:** ACID Transactions and row-level locking via `SELECT ... FOR UPDATE` during approvals and stock handovers.

