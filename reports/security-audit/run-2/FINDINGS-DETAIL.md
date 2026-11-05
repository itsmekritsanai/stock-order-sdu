# Detailed Vulnerability Findings (Run 2: v3.0.6)

This document provides in-depth technical analysis, evidence, reproduction steps, and remediation guidance for all vulnerabilities identified during Audit Run 2.

---

### Finding 1: [CRITICAL] URL-Encoding Filter Bypass in `is_safe_static_path` (CWE-22 / CWE-552)

- **ID:** `sdu-sec-006-url-decode-path-traversal`
- **CVSS 3.1 Score:** **9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)**
- **Affected File:** `backend/server.py:1273-1289`
- **Vulnerability Type:** Path Traversal / Sensitive Information Disclosure

#### Technical Analysis
In `backend/server.py`, `is_safe_static_path` was introduced to prevent clients from downloading internal files (such as `.env` and source code). However, it inspected the raw URL string before unquoting:
```python
clean_path = path.split("?", 1)[0].split("#", 1)[0]
parts = [p for p in clean_path.replace("\\", "/").split("/") if p]
if any(p.startswith(".") for p in parts):
    return False
```
When a client requests `/%2eenv`:
- `clean_path` is `/%2eenv`
- `parts` is `['%2eenv']`
- `'%2eenv'.startswith('.')` evaluates to `False`!
- The check passes, and execution proceeds to `super().translate_path('/%2eenv')`.
- Python's standard `SimpleHTTPRequestHandler.translate_path` decodes `%2e` into `.`, resolving to `C:\...\stock-order-sdu\.env` and returning the file with HTTP 200 OK!
The same bypass allows reading `/%62ackend/server.py` (`%62` = `b`), `/%2egit/config`, and all internal project files.

#### Proof of Concept
```powershell
curl.exe -i http://127.0.0.1:8080/%2eenv
curl.exe -i http://127.0.0.1:8080/%62ackend/server.py
```
**Observed Result:** Full content of `.env` (including database passwords and staff auth secret) and `server.py` returned over the wire.

#### Remediation
In `backend/server.py`:
```python
from urllib.parse import unquote

def is_safe_static_path(self, path: str) -> bool:
    unquoted = unquote(path.split("?", 1)[0].split("#", 1)[0])
    # Normalize path and check canonical target
    parts = [p for p in unquoted.replace("\\", "/").split("/") if p]
    if any(p.startswith(".") or ".." in p for p in parts):
        return False
    forbidden_dirs = {"backend", "tests", "scripts", "data", ".venv", "__pycache__", "reports"}
    if any(p in forbidden_dirs for p in parts):
        return False
    forbidden_files = {"docker-compose.yml", "schema_postgres.sql", "schema.sql", "pgadmin_servers.json", "start.bat", ".env"}
    if parts and parts[-1].lower() in forbidden_files:
        return False
    return True
```

---

### Finding 2: [HIGH] Negative Quantity Supply Injection in `handle_create_requisition` (CWE-1284 / CWE-20)

- **ID:** `sdu-sec-007-negative-quantity-stock-injection`
- **CVSS 3.1 Score:** **8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)**
- **Affected File:** `backend/server.py:348-420`, `467-493`
- **Vulnerability Type:** Improper Input Validation / Business Logic Flaw

#### Technical Analysis
In `backend/server.py:378`:
```python
available = max(0, int(db_item["on_hand_pieces"]) - int(db_item["reserved_pieces"]))
if total_pieces > available:
    return {"status": "error", "code": "INSUFFICIENT_STOCK"}
```
If an attacker submits `totalPieces: -1250`:
- `-1250 > available` is `False`.
- The negative requisition is inserted successfully into `requisitions` and `requisition_items`.
- When staff approves the requisition in `handle_approve_requisition`:
  `cur.execute("UPDATE inventory_items SET reserved_pieces = reserved_pieces + %s", (-1250, item_id))` reduces `reserved_pieces` below zero.
- When handed over (`handle_complete_requisition`):
  `new_on_hand = max(0, int(inv["on_hand_pieces"]) - (-1250))`
  Physical stock in the warehouse is artificially increased by 1,250 pieces!

#### Proof of Concept
Sending an HTTP POST to `/api` with:
```json
{
  "action": "createRequisition",
  "payload": {
    "requester": "Attacker",
    "dept": "สำนักงานผู้อำนวยการ สวท.",
    "purpose": "Inventory Tampering",
    "items": [{"itemId": 1, "qtyBoxes": -5, "qtyPieces": 0, "totalPieces": -1250}]
  }
}
```
Result: Returns `{"status": "success", "docNo": "REQ-..."}`.

#### Remediation
In `handle_create_requisition`:
```python
for req_item in items:
    qty_boxes = int(req_item.get("qtyBoxes") or 0)
    qty_pieces = int(req_item.get("qtyPieces") or 0)
    total_pieces = int(req_item.get("totalPieces") or 0)

    if qty_boxes < 0 or qty_pieces < 0 or total_pieces <= 0:
        return {"status": "error", "message": "จำนวนพัสดุที่ขอเบิกต้องมากกว่า 0"}

    # Recalculate and enforce ratio consistency
    expected_total = (qty_boxes * int(db_item["pieces_per_box"])) + qty_pieces if db_item["is_multi_unit"] else qty_pieces
    if total_pieces != expected_total or total_pieces <= 0:
        return {"status": "error", "message": "จำนวนรวมของพัสดุไม่ตรงกับอัตราส่วนหน่วยนับ"}
```

---

### Finding 3: [HIGH] Stored Cross-Site Scripting (XSS) in Catalog & Inventory Item Displays (CWE-79)

- **ID:** `sdu-sec-008-stored-xss-catalog-items`
- **CVSS 3.1 Score:** **7.6 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:L/A:N)**
- **Affected Files:** `index.html:1574-1590`, `staff.html:2098-2101`
- **Vulnerability Type:** Cross-Site Scripting (XSS)

#### Technical Analysis
In `index.html`:
```javascript
<img src="${imgSrc}" class="item-img" alt="${item.name}" onerror="this.onerror=null; this.src='assets/logo_sdu.png'">
<h3 class="item-title">${item.name}</h3>
```
And in `staff.html`:
```javascript
<td><strong>${item.name}</strong></td>
```
None of these properties (`name`, `unit_box_name`, `unit_piece_name`, `image_piece`, `image_box`) are passed through `escapeHtml()`. If an item is created or updated with payload:
`image_box: '" onerror="alert(document.domain)" x="'`
The resulting HTML breaks out of the `src` attribute and executes JavaScript whenever any user or staff member views the catalog.

#### Remediation
Use `escapeHtml()` on all item fields in both `index.html` and `staff.html`:
```javascript
const safeImg = escapeHtml(imgSrc);
const safeName = escapeHtml(item.name);
const safeBox = escapeHtml(item.unit_box_name);
const safePiece = escapeHtml(item.unit_piece_name);
```

---

### Finding 4: [MEDIUM] Unbounded Content-Length Resource Exhaustion (DoS) (CWE-400 / CWE-770)

- **ID:** `sdu-sec-009-unbounded-content-length-dos`
- **CVSS 3.1 Score:** **6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)**
- **Affected File:** `backend/server.py:1374-1375`

#### Technical Analysis
In `do_POST`:
```python
content_length = int(self.headers.get("Content-Length", 0))
raw_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
```
No maximum size limit is checked before reading `self.rfile`. Sending an exorbitant `Content-Length` header triggers a memory allocation of that size, causing high CPU/RAM load or an unhandled out-of-memory exception.

#### Remediation
Enforce a reasonable upper bound (e.g. 10 MB):
```python
MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MB
if content_length > MAX_BODY_SIZE:
    self.send_error(413, "Payload Too Large: Maximum allowed size is 10MB")
    return
```

---

### Finding 5: [MEDIUM] Missing Requester Authentication on `createRequisition` (CWE-287 / CWE-306)

- **ID:** `sdu-sec-010-unauthenticated-requisition-creation`
- **CVSS 3.1 Score:** **5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)**
- **Affected File:** `backend/server.py:348-356`, `1409-1410`

#### Technical Analysis
While `index.html` requires users to log in before displaying the cart and requisition form, the backend REST endpoint `/api?action=createRequisition` accepts arbitrary requester names and departments without validating any caller session token or verifying credentials.

#### Remediation
Validate requester credentials or issue a signed requester session token on `loginRequester` and verify it in `handle_create_requisition`.

---

### Finding 6: [LOW] Hard-Coded Default STAFF_AUTH_SECRET (CWE-798)

- **ID:** `sdu-sec-011-default-staff-secret`
- **CVSS 3.1 Score:** **4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)**
- **Affected Files:** `.env:34`, `backend/server.py:44`

#### Technical Analysis
The static placeholder `"sdu_inventory_staff_secret_token_change_in_production"` is present in `.env` and hard-coded as fallback in `backend/server.py`. If deployed without generating a unique production secret, an attacker knowing the default string can forge valid HMAC tokens.

#### Remediation
Log a prominent warning if the default secret is used, or generate an ephemeral random secret at server boot when `STAFF_AUTH_SECRET` is unset or equals the default placeholder.
