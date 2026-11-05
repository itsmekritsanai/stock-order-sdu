# Architecture & Threat Model: SDU Stock Order System (v3.0.6)

**Target:** Suan Dusit University e-Inventory & Requisition System  
**Audit Run:** `run-2`  
**Date:** 2026-11-05  

---

## 1. System Topology & Boundary Map

```mermaid
flowchart TD
    subgraph Public Internet / University Intranet
        REQ_CLIENT["Requester Client (Browser)"]
        ATTACKER["Unauthenticated Network Attacker"]
    end

    subgraph Internal Staff Boundary
        STAFF_CLIENT["Staff Client (Browser)"]
    end

    subgraph Host / Server Layer (Python 3.13)
        HTTP_ROUTER["SDUInventoryRequestHandler<br/>(backend/server.py:8080)"]
        STATIC_ENGINE["SimpleHTTPRequestHandler<br/>translate_path + is_safe_static_path"]
        AUTH_GATE["Staff HMAC Token Gate<br/>(verify_staff_token)"]
        API_HANDLERS["Business Logic Handlers<br/>(createRequisition, approve, complete, adjust)"]
    end

    subgraph Storage & Infrastructure (Docker Compose)
        PG_DB[("PostgreSQL 17 (Port 5433)<br/>sdu_inventory")]
        FS_ROOT["Local File System<br/>(PROJECT_ROOT: .env, backend/, assets/)"]
    end

    REQ_CLIENT -->|HTTP GET / POST /api| HTTP_ROUTER
    ATTACKER -->|HTTP GET /%2eenv, /api| HTTP_ROUTER
    STAFF_CLIENT -->|HTTP Bearer Auth| HTTP_ROUTER

    HTTP_ROUTER -->|Static File Request| STATIC_ENGINE
    STATIC_ENGINE -->|Read File| FS_ROOT

    HTTP_ROUTER -->|Admin Action| AUTH_GATE
    AUTH_GATE -->|Verified| API_HANDLERS
    HTTP_ROUTER -->|Public Action (createReq, login)| API_HANDLERS

    API_HANDLERS -->|SELECT ... FOR UPDATE / INSERT / UPDATE| PG_DB
```

---

## 2. Trust Boundaries & Entry Surfaces

| Boundary | Description | Key Actors | Controls Present |
|---|---|---|---|
| **Web Root Boundary (File System)** | HTTP requests for static assets (`/index.html`, `/staff.html`, `/assets/*`) | Any network client | `is_safe_static_path`, `translate_path` |
| **REST API Dispatch Boundary** | HTTP POST `/api` with JSON payload `{action, payload}` | Public Requesters, Warehouse Staff, Attackers | `STAFF_ACTIONS` set checking `Authorization: Bearer <token>` or `X-Staff-Token` |
| **State Machine Boundary** | Requisition status lifecycle: `PENDING` -> `APPROVED` -> `COMPLETED` / `REJECTED` | Staff (Approve/Complete), Database Locks | Row locking `SELECT ... FOR UPDATE`, explicit state checks |
| **Database Boundary** | Relational data persistence in PostgreSQL 17 (`sdu_inventory`) | Server worker threads | Parameterized queries with `%s` tuple binding |
| **DOM / Client-Side Rendering Boundary** | Dynamic HTML rendering in Browser (`innerHTML`, template strings) | End users viewing catalog & requisitions | `escapeHtml()` utility function |

---

## 3. Threat Actors & Asset Classification

1. **Unauthenticated External Attacker:** Can send arbitrary HTTP requests to port 8080. Aims to read sensitive secrets (`.env`, source code), bypass authentication, forge orders, or crash the server.
2. **Authenticated Requester:** University personnel. Aims to requisition supplies legitimately, but could attempt privilege escalation to staff functions or inject malicious quantities/content.
3. **Warehouse Staff (Privileged Operator):** Holds HMAC session token. Aims to manage inventory, approve orders, and manage users.
