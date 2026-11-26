# Architecture & Single Source of Truth (references/architecture-and-ssot.md)

This reference outlines the system architecture, dual-portal segregation, backend design, and Single Source of Truth (SSOT) protocols (v3.8.3).

---

## 1. Single Source of Truth (SSOT)

* **Generator Script:** [`scripts/generate_separated_portals.py`](../../../../scripts/generate_separated_portals.py)
* **Rule:** `index.html` and `staff.html` are generated artifacts.
* **Workflow:**
  1. Embed 6 สวท. departments, 15 seeded accounts (from `Book1.xlsx`, with passwords stripped from public HTML), 34 initial inventory items (66 images), `SYSTEM_VERSION`, universal searchable dropdown helpers, and dynamic calendar month helpers.
  2. Output clean, self-contained `index.html` and `staff.html`.
* **When making structural HTML/CSS/JS edits:**
  - Update `scripts/generate_separated_portals.py` first (or synchronously).
  - Execute `.venv\Scripts\python scripts/generate_separated_portals.py` (or `python scripts/generate_separated_portals.py`).
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

## 3. Strict 100% Portal Separation & Cross-Portal SSO

* **Gateway Hub (`portal.html`):**
  - Central launchpad with 4-role shortcuts, 4-step workflow overview, and real-time `/api?action=health` status indicator.
* **Requester Portal (`index.html`):**
  - Entry point for university personnel using Auto-Role Login (case-insensitive username + PBKDF2-verified password).
  - Features: Live search catalog, 2-unit selector, real-time personal & department quota indicators, cart drawer, requisition submission, "My Requisitions" with dynamic calendar month filter, official 4-signature PDF printout, and 1-click switch back to `staff.html` (only shown to `STAFF`/`HEAD`/`ADMIN` accounts).
  - **Forbidden:** Screening/approval buttons, stock adjustment, restock, physical handover, item/user/department/quota management.
* **Staff & Approver Portal (`staff.html`):**
  - Warehouse & approval portal protected by RBAC (`STAFF`, `HEAD`, `ADMIN`) and HMAC-SHA256 session tokens, with 1-click Cross-Portal SSO switch to `index.html`.
  - Features: Two-tier approval queue (`PENDING` -> `VERIFIED` -> `APPROVED` -> `COMPLETED`), restock with 3-mode cost pricing, stock adjustment, audit trail modal, min alert configuration, item/user/department/quota CRUD, monthly analytics (including per-person usage, purchase costs, and all monthly requisitions), native 6-sheet Excel (`.xlsx`) export, and Executive Summary PDF.

---

## 4. Backend & Database Architecture

* **Containerized 1-Command Deploy:** `Dockerfile` (`python:3.11-slim`, non-root `appuser`) + `docker-compose.yml` running `sdu_stock_postgres` (`postgres:17-alpine`, bound to `127.0.0.1:5433`, persisted in `./postgres-data`) and `sdu_stock_app` (port `8080`).
* **Database Name:** `sdu_inventory` (PostgreSQL 17 with MySQL fallback compatibility).
* **Tables (7):** `departments`, `users`, `inventory_items`, `requisitions`, `requisition_items`, `stock_transactions`, `quota_rules`.
* **Web, API & Export Server:** `backend/server.py` (`ThreadingHTTPServer`, `ThreadedConnectionPool`, RBAC, Security Headers) + `backend/excel_export.py` (zero-dependency native `.xlsx` generator).
* **Concurrency Protection:** ACID Transactions and ordered row-level locking via `SELECT ... FOR UPDATE` during requisition creation, approvals, and stock handovers.
