# Findings Detail: Security Audit Run 1

This document provides technical analysis, source code traces, local reproduction steps, and exact source patches for all confirmed vulnerabilities identified in the Suan Dusit University Stock System (`stock-order-sdu`).

---

## Finding 1: Arbitrary Sensitive File Disclosure via SimpleHTTPRequestHandler Root Directory

- **Fingerprint:** `sdu-sec-001-sensitive-file-exposure`
- **Severity:** Critical (Likelihood: Critical, Impact: Critical)
- **CWE:** CWE-552 (Files or Directories Accessible to External Parties), CWE-200 (Exposure of Sensitive Information)
- **Affected File:** `backend/server.py:975, 984`

### 1. Description & Threat Model
The Python backend server uses Python's standard `SimpleHTTPRequestHandler` with its root directory set to `PROJECT_ROOT`. Python's `SimpleHTTPRequestHandler` serves any file found in the directory hierarchy unless explicitly blocked. Because the project root contains environment files (`.env`), Git version control metadata (`.git/`), database migrations (`schema_postgres.sql`), and Docker configurations (`docker-compose.yml`), any remote client can download these files via simple HTTP GET requests without authentication.

### 2. Source Code Trace
```
[Entrypoint] backend/server.py:975 (SDUInventoryRequestHandler.__init__)
     │  super().__init__(*args, directory=PROJECT_ROOT, **kwargs)
     ▼
[Propagation] backend/server.py:984 (SDUInventoryRequestHandler.do_GET)
     │  if not self.path.startswith('/api'):
     │      super().do_GET()
     ▼
[Sink] http/server.py:715 (SimpleHTTPRequestHandler.send_head)
        Opens and streams target file to client with HTTP 200
```

### 3. Local Reproduction
- **Attacker Perspective:** Unauthenticated external / intranet network user.
- **Request:**
  ```http
  GET /.env HTTP/1.1
  Host: localhost:8080
  ```
- **Observed Result:**
  The server responds with `HTTP 200 OK` and dumps the raw `.env` contents, exposing `DB_PASSWORD="postgrespassword"` and `STAFF_AUTH_SECRET="sdu_stock_staff_super_secret_key_2026"`.

### 4. Source Remediation
Add a path filter in `backend/server.py` to block access to hidden files, parent traversing sequences, and private directories:
```python
def translate_path(self, path):
    # Strip query parameters and anchors
    clean_path = path.split('?', 1)[0].split('#', 1)[0]
    parts = [p for p in clean_path.split('/') if p]
    
    # Block any hidden file or directory (.env, .git, etc.)
    if any(p.startswith('.') for p in parts):
        return None
        
    # Block sensitive code and data directories
    forbidden_dirs = {'backend', 'data', 'tests', 'scripts', '.venv', '__pycache__'}
    if any(p in forbidden_dirs for p in parts):
        return None
        
    return super().translate_path(path)
```

---

## Finding 2: Missing Server-Side Authentication & Authorization on Administrative API Endpoints

- **Fingerprint:** `sdu-sec-002-missing-api-authentication`
- **Severity:** High (Likelihood: High, Impact: High)
- **CWE:** CWE-306 (Missing Authentication for Critical Function), CWE-862 (Missing Authorization)
- **Affected File:** `backend/server.py:1044-1080`, `staff.html:1584`

### 1. Description & Threat Model
In `backend/server.py`, administrative actions (`approveRequisition`, `completeRequisition`, `rejectRequisition`, `restockItem`, `adjustStock`, `saveUser`, `deleteUser`, `addDepartment`, `saveItem`, `deleteItem`) are dispatched purely based on the `"action"` string supplied in the JSON POST payload. There is no server-side session, Bearer token, or API key verification. Staff authentication is enforced only on the client side in `staff.html` via `sessionStorage.getItem('staff_auth')`. Anyone can bypass the frontend UI and make direct HTTP calls to execute administrative actions.

### 2. Source Code Trace
```
[Entrypoint] backend/server.py:1020 (SDUInventoryRequestHandler.do_POST)
     │  Receives JSON body {"action": "adjustStock", ...}
     ▼
[Propagation] backend/server.py:1044 (SDUInventoryRequestHandler.do_POST)
     │  actions = {'adjustStock': self.handle_adjust_stock, ...}
     │  handler = actions.get(action)
     ▼
[Sink] backend/server.py:530 (SDUInventoryRequestHandler.handle_adjust_stock)
        Executes SQL UPDATE items SET quantity = %s without verifying credentials
```

### 3. Local Reproduction
- **Attacker Perspective:** Unauthenticated client on intranet.
- **Request:**
  ```http
  POST /api HTTP/1.1
  Host: localhost:8080
  Content-Type: application/json

  {
    "action": "adjustStock",
    "id": 1,
    "new_quantity": 9999,
    "reason": "unauthorized adjustment"
  }
  ```
- **Observed Result:**
  Returns `{"status": "success", "message": "ปรับยอดสต๊อกเรียบร้อยแล้ว"}` and updates stock count in the database.

### 4. Source Remediation
Introduce server-side token verification using HMAC with `STAFF_AUTH_SECRET`:
```python
STAFF_ACTIONS = {
    'approveRequisition', 'completeRequisition', 'rejectRequisition',
    'restockItem', 'adjustStock', 'saveUser', 'deleteUser',
    'addDepartment', 'saveItem', 'deleteItem'
}

if action in STAFF_ACTIONS:
    auth_header = self.headers.get('Authorization', '')
    if not self.is_authorized_staff(auth_header):
        self.send_json_response({'status': 'error', 'message': 'Unauthorized'}, status_code=401)
        return
```

---

## Finding 3: Stored Cross-Site Scripting (XSS) via Unsanitized Requisition and User Attributes

- **Fingerprint:** `sdu-sec-003-stored-xss-portals`
- **Severity:** High (Likelihood: Medium, Impact: High)
- **CWE:** CWE-79 (Improper Neutralization of Input During Web Page Generation)
- **Affected File:** `staff.html:1081-1083`, `index.html`

### 1. Description & Threat Model
User input fields from requisition forms (e.g. `requester`, `dept`, `purpose`, `notes`) are saved into the database as raw strings and later rendered in `staff.html` and `index.html` using JavaScript template literals concatenated directly into `element.innerHTML`. If a requester includes HTML or script tags, they execute automatically in the browser of any staff member reviewing requisitions.

### 2. Source Code Trace
```
[Entrypoint] index.html:1257 (submitRequisition)
     │  payload = { requester: input.value, purpose: textarea.value }
     ▼
[Propagation] backend/server.py:382 (handle_create_requisition)
     │  INSERT INTO requisitions (requester, purpose, ...) VALUES (%s, %s, ...)
     ▼
[Sink] staff.html:1081-1083 (renderRequisitions)
        card.innerHTML = `<div>ผู้ขอเบิก: ${req.requester}</div>
                          <div>วัตถุประสงค์: ${req.purpose}</div>`;
```

### 3. Local Reproduction
- **Attacker Perspective:** Requester submitting a supply order.
- **Payload:** `<img src=x onerror=alert(document.domain)>` placed in `purpose` field.
- **Observed Result:**
  When staff opens `staff.html`, the browser renders the image tag, triggers the `onerror` event, and executes JavaScript under the origin of the staff portal.

### 4. Source Remediation
Add an HTML escaping utility in `staff.html` and `index.html`:
```javascript
function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
```
Wrap all interpolated fields:
```javascript
`<div>${vIcons.user} <strong>ผู้ขอเบิก:</strong> ${escapeHtml(req.requester)}</div>`
`<div style="grid-column: 1 / -1;">${vIcons.fileText} <strong>วัตถุประสงค์:</strong> ${escapeHtml(req.purpose)}</div>`
```

---

## Finding 4: Plaintext Password Storage and Insecure Hardcoded Fallback Credentials

- **Fingerprint:** `sdu-sec-004-plaintext-password-storage`
- **Severity:** Medium (Likelihood: Medium, Impact: Medium)
- **CWE:** CWE-256 (Plaintext Storage of a Password), CWE-312 (Cleartext Storage of Sensitive Information)
- **Affected File:** `backend/server.py:734, 795`, `schema_postgres.sql:67`

### 1. Description & Threat Model
User passwords in the `users` table are stored in plaintext. In `backend/server.py:734`, if a user is created without a password, the system assigns a default hardcoded password `"sdu1234"`. In `backend/server.py:795`, login comparison uses direct plaintext string equality. Anyone with database read access or database backup archives gains immediate access to all user accounts.

### 2. Source Code Trace
```
[Entrypoint] backend/server.py:724 (handle_save_user)
     │  password = data.get("password") or "sdu1234"
     ▼
[Propagation] backend/server.py:734 (handle_save_user)
     │  INSERT INTO users (username, password, ...) VALUES (%s, %s, ...)
     ▼
[Sink] backend/server.py:795 (handle_login_user)
        if password != valid_pass:
            return 401
```

### 3. Source Remediation
Use Python standard library `hashlib.pbkdf2_hmac` with a unique cryptographic salt for each user:
```python
import hashlib, os, hmac

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 600000)
    return f"{salt.hex()}:{dk.hex()}"

def verify_password(stored: str, password: str) -> bool:
    if not stored or ':' not in stored:
        return stored == password  # legacy fallback during migration
    salt_hex, hash_hex = stored.split(':', 1)
    salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 600000)
    return hmac.compare_digest(dk.hex(), hash_hex)
```

---

## Finding 5: Permissive Wildcard Cross-Origin Resource Sharing (CORS) Policy

- **Fingerprint:** `sdu-sec-005-permissive-cors`
- **Severity:** Low (Likelihood: Low, Impact: Low)
- **CWE:** CWE-942 (Permissive Cross-Domain Policy with Untrusted Domains)
- **Affected File:** `backend/server.py:990`

### 1. Description & Threat Model
`SDUInventoryRequestHandler.send_cors_headers` unconditionally writes `Access-Control-Allow-Origin: *`. If an intranet user navigates to a malicious external site while their browser is on the university network, scripts on the external site can send cross-origin requests to `http://localhost:8080/api` and read response data.

### 2. Source Remediation
Restrict `Access-Control-Allow-Origin` to trusted hosts or omit it for same-origin requests in production:
```python
def send_cors_headers(self):
    origin = self.headers.get('Origin', '')
    allowed_origins = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:8080').split(',')
    if origin in allowed_origins:
        self.send_header('Access-Control-Allow-Origin', origin)
        self.send_header('Vary', 'Origin')
```

