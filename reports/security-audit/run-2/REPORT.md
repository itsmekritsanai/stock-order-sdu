# Security Audit Report: Suan Dusit University Stock System (v3.0.6)

**Target:** Digital Stock & Requisition System for Suan Dusit University (`stock-order-sdu`)  
**Audit Run:** `run-2`  
**Profile:** `standard`  
**Execution Policy:** Sandboxed Source-and-Local-Only  
**Status:** Complete  
**Date:** 2026-11-05  

---

## 1. Executive Summary & Security Posture

A comprehensive second-wave security audit was performed on the SDU Stock Order & e-Inventory System (`v3.0.6`). This audit evaluated the durability of past mitigations from Run 1, analyzed new functionality (department CRUD, threshold adjustments, searchable restock), and conducted deep vulnerability research into data integrity, parser behaviors, and boundary isolation.

### Key Audit Findings:
1. **Critical Bypass Discovered in Static File Protection (sdu-sec-006):** While `is_safe_static_path` was added to block sensitive files (`.env`, source code), the check did not decode percent-encoded (URL-encoded) paths. Sending `GET /%2eenv` completely bypassed the dotfile filter, allowing unauthenticated remote clients to download `.env` and `backend/server.py`.
2. **Negative Quantity Stock Injection (sdu-sec-007):** `handle_create_requisition` failed to validate that requested quantities are strictly positive. An attacker could submit negative quantities (e.g. `totalPieces: -1250`), which upon approval and handover artificially inflated warehouse stock.
3. **Stored XSS in Item Catalog Displays (sdu-sec-008):** In `index.html` and `staff.html`, item names, unit labels, and image paths were inserted directly into `innerHTML` without `escapeHtml()`, allowing attribute breakout and script execution.
4. **Denial of Service via Unbounded Body Size (sdu-sec-009):** `do_POST` read `self.rfile.read(content_length)` using untrusted client-supplied headers without enforcing a maximum payload bound.
5. **Re-validation of Past Fixes:**
   - Database SQL Injection immunity remains **100% verified** across all endpoints.
   - Requisition State Machine enforcement (CWE-841) successfully blocks double-completion and invalid transitions.
   - Password hashing with PBKDF2-HMAC-SHA256 and HMAC staff token verification are operational.

---

## 2. Confirmed Vulnerabilities Summary (Run 2)

| Severity | Fingerprint | Title | Affected Component | Observed Impact |
|---|---|---|---|---|
| **CRITICAL** | `sdu-sec-006` | URL-Encoding Filter Bypass in `is_safe_static_path` | Static Web Server | `GET /%2eenv` dumps database credentials and HMAC secrets. |
| **HIGH** | `sdu-sec-007` | Negative Quantity Requisition Injection | REST API / Inventory Logic | Negative items bypass stock checks and artificially inflate stock upon handover. |
| **HIGH** | `sdu-sec-008` | Stored XSS in Item Catalog & Inventory Tables | DOM / Client-Side UI | Malicious item attributes execute arbitrary JavaScript in user/staff sessions. |
| **MEDIUM** | `sdu-sec-009` | Uncontrolled Resource Consumption via Content-Length | HTTP Transport / POST | Exorbitant Content-Length headers trigger excessive server memory allocation. |
| **MEDIUM** | `sdu-sec-010` | Unauthenticated Requisition Creation | REST API / Requester Auth | Direct API callers can submit orders under any faculty or staff member's name. |
| **LOW** | `sdu-sec-011` | Insecure Default `STAFF_AUTH_SECRET` in Config | Configuration / Auth | Known static secret allows forging valid staff tokens if not overridden. |

---

## 3. High-Priority Remediation Roadmap

1. **Immediate Patch for URL-Encoded Path Traversal (`backend/server.py`):**
   - Unquote the path (`urllib.parse.unquote`) before checking directory and file allowlists/denylists, and canonicalize path with `os.path.realpath`.
2. **Strict Arithmetic Validation in Requisitions (`backend/server.py`):**
   - In `handle_create_requisition`: Require `qty_boxes >= 0`, `qty_pieces >= 0`, and recalculate `expected_total = (qty_boxes * ratio) + qty_pieces`. Enforce `total_pieces == expected_total` and `total_pieces > 0`.
3. **Complete HTML Escaping in Frontend Portals (`index.html`, `staff.html`):**
   - Ensure all item names, unit strings, and image URLs are wrapped in `escapeHtml()` prior to template string interpolation.
4. **Enforce Max Request Body Size (`backend/server.py`):**
   - Reject any POST request where `Content-Length > 10MB` with HTTP 413 Payload Too Large.
5. **Enforce Requester Authentication Token:**
   - Generate a signed requester token upon `loginRequester` and require it in `handle_create_requisition`.
