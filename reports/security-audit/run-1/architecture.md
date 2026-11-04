# Architecture & Threat Model: Suan Dusit University Stock System

## 1. System Overview
The **Digital Stock & Requisition System for Suan Dusit University (SDU)** is a single-node web application designed to facilitate inventory tracking, supply requisitioning, approval workflows, and staff management for university staff and personnel.

### Technology Stack
- **Backend:** Python 3.13 (`http.server.HTTPServer` with `SimpleHTTPRequestHandler`) in `backend/server.py`
- **Database:** PostgreSQL 17 (`sdu_inventory`), accessed via `psycopg2-binary` (with MySQL fallback support via `PyMySQL`)
- **Frontend:** Vanilla HTML5, CSS3, JavaScript ES6 (`index.html`, `staff.html`, `portal.html`)
- **Container Infrastructure:** Docker Compose (`sdu_stock_postgres`, `sdu_stock_pgadmin`)
- **Port:** HTTP 8080 (app), PostgreSQL 5433 (external mapped), pgAdmin 5051

---

## 2. Trust Boundaries & Privilege Tiers

```
[ Unauthenticated Requester / External Network ]
                      │
                      │ HTTP GET / POST (port 8080)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ Web Application Server (backend/server.py)                  │
│                                                             │
│   ├── Static File Handler (SimpleHTTPRequestHandler)         │
│   │     * Root directory: PROJECT_ROOT                      │
│   │                                                         │
│   └── API Dispatcher (do_POST /api)                         │
│         * Public: loginUser, createRequisition, getInventory│
│         * Staff/Admin: approve, reject, adjustStock,        │
│                        saveUser, deleteUser, etc.           │
└─────────────────────────────┬───────────────────────────────┘
                              │ Parameterized SQL queries
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PostgreSQL 17 Database (sdu_inventory)                      │
│   Tables: items, categories, requisitions, requisition_items│
│           stock_transactions, departments, users, settings  │
└─────────────────────────────────────────────────────────────┘
```

### Privilege Tiers:
1. **Unauthenticated Public / Intranet Client:**
   - Allowed: View portal landing page (`portal.html`), submit requisition (`index.html`), view basic inventory items.
   - Intended boundary: Should NOT be able to access server secrets, database configurations, or invoke administrative actions.
2. **Authenticated Requester (User):**
   - Can authenticate with username/password to track submitted requisitions.
3. **Staff Administrator:**
   - Intended to manage inventory, approve/reject requisitions, perform stock adjustments, manage users and departments (`staff.html`).
   - Boundary enforcement: *Currently client-side only via `sessionStorage`*.

---

## 3. Surface & Attack Boundary Breakdown

| Surface | Protocol / Format | Handlers | Security Controls | Identified Weakness |
|---|---|---|---|---|
| **Static Web Server** | HTTP GET | `do_GET` -> `super().do_GET()` | None (serves `PROJECT_ROOT`) | Exposes `.env`, `.git`, source files |
| **Public API** | HTTP POST (JSON) | `loginUser`, `createRequisition`, `getInventory` | Parameterized SQL | Stored XSS in requisition fields |
| **Administrative API** | HTTP POST (JSON) | `adjustStock`, `approveRequisition`, `saveUser` | Client-side `sessionStorage` only | Missing server-side auth token check |
| **Database Storage** | PostgreSQL | `psycopg2` | Parameterized `%s` queries | Passwords stored in plaintext |
| **HTTP Headers** | CORS | `send_cors_headers` | Wildcard `*` | Allows cross-origin API invocation |

