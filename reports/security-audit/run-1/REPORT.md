# Security Audit Report: Suan Dusit University Stock System

**Target:** Digital Stock & Requisition System for Suan Dusit University (`stock-order-sdu`)  
**Audit Run:** `run-1`  
**Profile:** `standard`  
**Execution Policy:** Sandboxed Source-and-Local-Only  
**Status:** Complete  
**Date:** 2026-11-04  

---

## 1. Executive Summary & Security Posture

A comprehensive source-first security assessment was conducted on the Digital Stock & Requisition System for Suan Dusit University. The audit mapped all HTTP endpoints, database interactions, authentication mechanisms, file-serving routines, and client-side rendering pathways.

### Key Takeaways
- **Strong Foundation in Database Security:** All SQL operations in `backend/server.py` use parameterized queries with tuple binding (`%s`). No SQL Injection vulnerabilities were discovered.
- **Critical Exposure in File Serving:** The web server serves the repository root directory as its static web root without path restrictions. This inadvertently exposes `.env` (holding database credentials and HMAC secrets), internal `.git/` metadata, and database initialization files to unauthenticated network clients.
- **Missing API Authentication Enforcement:** Administrative mutation endpoints (such as approving orders, modifying stock quantities, and creating/deleting users) rely entirely on client-side frontend checks in `staff.html`. The backend dispatches these state-altering actions without verifying caller identity or authorization tokens.
- **Stored XSS in Staff Management UI:** Dynamic fields submitted during requisition (e.g., purpose, requester name) are rendered via raw string concatenation into `innerHTML` without HTML entity encoding.
- **Cleartext Passwords:** User credentials in PostgreSQL are stored and validated in plaintext with an insecure hardcoded fallback (`sdu1234`).

---

## 2. Confirmed Vulnerabilities Summary

| Severity | Fingerprint | Title | Affected Boundary | Observed Result |
|---|---|---|---|---|
| **CRITICAL** | `sdu-sec-001-sensitive-file-exposure` | Arbitrary Sensitive File Disclosure via SimpleHTTPRequestHandler | File System / Web Root | Unauthenticated HTTP GET to `/.env` returns database password and HMAC secrets. |
| **HIGH** | `sdu-sec-002-missing-api-authentication` | Missing Server-Side Authentication on Administrative API Endpoints | Authentication / REST API | Unauthenticated POST to `/api` successfully mutates stock quantities and user records. |
| **HIGH** | `sdu-sec-003-stored-xss-portals` | Stored Cross-Site Scripting (XSS) via Unsanitized Requisition Attributes | DOM / Client-Side UI | Browser executes injected JavaScript tags when staff reviews pending requisitions. |
| **MEDIUM** | `sdu-sec-004-plaintext-password-storage` | Plaintext Password Storage and Insecure Default Fallback | Database / Credentials | User passwords stored in cleartext; missing password defaults to hardcoded `sdu1234`. |
| **LOW** | `sdu-sec-005-permissive-cors` | Permissive Wildcard Cross-Origin Resource Sharing (CORS) Policy | HTTP Response Headers | `Access-Control-Allow-Origin: *` allows cross-origin reading from malicious intranet sites. |

---

## 3. Detailed Finding Summaries

### 3.1 [CRITICAL] Arbitrary Sensitive File Disclosure via SimpleHTTPRequestHandler
- **File & Line:** `backend/server.py:975, 984`
- **Principal:** Remote unauthenticated network client
- **Description:** `SDUInventoryRequestHandler` inherits from Python's standard `SimpleHTTPRequestHandler` with `directory=PROJECT_ROOT`. Unauthenticated GET requests to `/.env` or `/.git/config` return sensitive configuration files.
- **Demonstrated Impact:** Full disclosure of `DB_PASSWORD`, `DB_USER`, and `STAFF_AUTH_SECRET`.
- **Smallest Effective Fix:** Override `translate_path` in `SDUInventoryRequestHandler` to reject any path with dotfiles (`.env`, `.git`) or pointing to sensitive directories (`backend/`, `data/`, `tests/`, `scripts/`).

### 3.2 [HIGH] Missing Server-Side Authentication on Administrative API Endpoints
- **File & Line:** `backend/server.py:1044-1080`, `staff.html:1584`
- **Principal:** Unauthenticated network actor
- **Description:** Server-side `do_POST` dispatches directly to handlers like `handle_approve_requisition`, `handle_adjust_stock`, and `handle_save_user` without checking for an authorization token.
- **Demonstrated Impact:** Unauthorized callers can approve/reject requisitions, manipulate inventory levels, and create administrative accounts.
- **Smallest Effective Fix:** Enforce Bearer token verification in `do_POST` for all administrative actions, validating against `STAFF_AUTH_SECRET`.

### 3.3 [HIGH] Stored Cross-Site Scripting (XSS) in Staff & Requester Dashboards
- **File & Line:** `staff.html:1081-1083`, `index.html`
- **Principal:** Requester submitting supply requisition
- **Description:** User inputs (`requester`, `dept`, `purpose`, `reject_reason`) are concatenated directly into `innerHTML` using unescaped template literals.
- **Demonstrated Impact:** Execution of arbitrary JavaScript in the staff session context, enabling session hijacking and unauthorized API actions.
- **Smallest Effective Fix:** Add an `escapeHtml()` helper function and sanitize all user-controlled values before template interpolation.

### 3.4 [MEDIUM] Plaintext Password Storage and Insecure Default Fallback
- **File & Line:** `backend/server.py:734, 795`, `schema_postgres.sql:67`
- **Principal:** Actor with database read access
- **Description:** Passwords in the `users` table are stored in plaintext. In `backend/server.py:734`, if omitted, passwords default to `"sdu1234"`. In `backend/server.py:795`, authentication uses direct string comparison (`password != valid_pass`).
- **Demonstrated Impact:** Immediate credential compromise upon database backup inspection.
- **Smallest Effective Fix:** Implement PBKDF2-HMAC-SHA256 password hashing with unique random salts and `hmac.compare_digest` verification.

### 3.5 [LOW] Permissive Wildcard Cross-Origin Resource Sharing (CORS) Policy
- **File & Line:** `backend/server.py:990`
- **Principal:** Malicious external website visited by intranet user
- **Description:** The server unconditionally returns `Access-Control-Allow-Origin: *`.
- **Demonstrated Impact:** Cross-origin data reading from intranet instances.
- **Smallest Effective Fix:** Restrict `Access-Control-Allow-Origin` to configured trusted domains.

---

## 4. Positive Security Observations & Hardening Notes

1. **Immunity to SQL Injection:**
   - Every SQL query in `backend/server.py` uses parameterized queries (e.g. `cursor.execute("SELECT ... WHERE id = %s", (item_id,))`). No dynamic SQL string formatting was found.
2. **Transaction Integrity:**
   - Requisition approvals and stock adjustments use database transactions (`conn.commit()` / `conn.rollback()`) ensuring ACID consistency.
3. **Structured Secret Management Ready:**
   - The system already supports `.env` configuration loading via `load_env()` and uses environment variables for database credentials.

---

## 5. Coverage Ledger Summary

| Ledger Unit | Surface | Boundary | Subsystem | Attack Class | Status | Result |
|---|---|---|---|---|---|---|
| `http-web::file-system` | HTTP Web | File System | Static Files | Resource & File Handling | Candidate -> Confirmed | `sdu-sec-001` |
| `rest-api::auth-boundary` | REST API | Auth Boundary | Admin Mutations | Access Control | Candidate -> Confirmed | `sdu-sec-002` |
| `browser-ui::dom-boundary` | Browser UI | DOM Boundary | Requisition Rendering | Injection | Candidate -> Confirmed | `sdu-sec-003` |
| `database-storage::credential` | Database | Credential Boundary | User Passwords | Cryptography & Secrets | Candidate -> Confirmed | `sdu-sec-004` |
| `http-headers::cross-origin` | HTTP Headers | Cross-Origin | CORS Policy | Web Protocol & Auth | Candidate -> Confirmed | `sdu-sec-005` |
| `database-queries::sql` | Database | SQL Boundary | Inventory Queries | Injection | Covered | Clean (No SQLi) |

- **Total Audited Units:** 6
- **Confirmed Vulnerabilities:** 5
- **Clean Subsystems:** 1 (SQL Injection immunity verified)
- **Unresolved / Needs Validation:** 0

