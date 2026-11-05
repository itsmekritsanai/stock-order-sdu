---
schema: 1
bug_id: login-failure
status: resolved
confidence: high
project_stack: Pure Vanilla HTML5/ES6 + Python HTTP Server (PostgreSQL 17)
created: 2026-11-05
source: User report "login ใช้ไม่ได้" + live daemon access log analysis
---

## Summary

**Observed:**
1. On `staff.html`, the browser encounters a syntax error (`Unexpected token ')'`) on load due to duplicate `}).join('')}` in template literals (`renderStaffRequisitions` and `viewPdfRequisition`), terminating script parsing. As a result, no JavaScript functions are defined (`handleStaffLogin`, `checkStaffAuth`), and clicking the submit button triggers default browser GET navigation to `staff.html?` without issuing any API call.
2. On `index.html`, attempting to log in as `wasana.c` or `user` using the default university standard password `sdu1234` returns `รหัสผ่านไม่ถูกต้อง` (401 / error), because the password hash in the PostgreSQL database was hashed against `123456` instead of `sdu1234`, while all other staff accounts (`jeerawan.b`, `patcharaporn.k`, `sineenart.l`) were seeded with `sdu1234`.

**Expected:**
1. `staff.html` and `index.html` must parse with 0 syntax errors in all modern browsers. Submitting the staff login form issues a `POST /api` with `{ action: 'loginStaff', ... }` and unlocks the staff portal.
2. Requesters (`wasana.c`, `user`, and all สวท. personnel) can log in using the institutional default password `sdu1234` (and any custom password set by staff), returning an authenticated session token.

**Scope of impact:** Both portals (`index.html` and `staff.html`). Blocks all user authentication and prevents access to catalog requisitions and inventory management.

## Evidence

- User report: "login ใช้ไม่ได้"
- Live server access log (`task-2461.log`):
  ```
  127.0.0.1 - - [05/Nov/2026 10:16:09] "GET /staff.html HTTP/1.1" 200 -
  127.0.0.1 - - [05/Nov/2026 10:16:16] "GET /index.html HTTP/1.1" 200 -
  127.0.0.1 - - [05/Nov/2026 10:16:25] "GET /index.html? HTTP/1.1" 200 -
  127.0.0.1 - - [05/Nov/2026 10:16:36] "GET /index.html? HTTP/1.1" 304 -
  127.0.0.1 - - [05/Nov/2026 10:16:37] "GET /portal.html HTTP/1.1" 200 -
  127.0.0.1 - - [05/Nov/2026 10:16:38] "GET /index.html HTTP/1.1" 304 -
  127.0.0.1 - - [05/Nov/2026 10:16:42] "GET /staff.html HTTP/1.1" 304 -
  ```
  Notice: `GET /index.html?` proves that the browser submitted the HTML form natively because the JavaScript event listener either did not exist or crashed before `e.preventDefault()`.
- Syntax inspection of `staff.html` and `scripts/generate_separated_portals.py`:
  - `staff.html:1199`:
    ```javascript
                  </tr>
                  `;
                }).join('')}
                `).join('')}
    ```
  - `staff.html:2070`:
    ```javascript
        </tr>
        `;
      }).join('');
      `).join('');
    ```
- Database inspection on PostgreSQL 17 (`users` table):
  - `wasana.c`: password verify with `sdu1234` = `False`, with `123456` = `True`
  - `user`: password verify with `sdu1234` = `False`, with `123456` = `True`
  - `jeerawan.b`: password verify with `sdu1234` = `True`
  - Placeholder in `index.html` states: `placeholder="เช่น wasana.c หรือ user"`

## Hypotheses

### H1 — Duplicate `}).join('')}` in template literals breaks JavaScript parsing in `staff.html` (confidence: high)

**Mechanism:** During the previous security patch, multi-line string replacements for `req.items.map` and `viewPdfRequisition` in `scripts/generate_separated_portals.py` inserted new closing blocks without removing the existing `}).join('')}`, producing invalid JavaScript syntax `}).join('')}\n`).join('')}`. The browser encounters an `Unexpected token ')'` syntax error on page load, abandoning script execution completely.

**Predicts:** Inspecting `scripts/generate_separated_portals.py` at lines 3854 and 4726 will reveal back-to-back `.join('')` calls. Removing the duplicate `.join('')` allows the script to parse cleanly with 0 syntax errors.

**Would be falsified by:** The file having valid JavaScript AST or syntax.

### H2 — Password hash mismatch for default suggested accounts `wasana.c` and `user` (confidence: high)

**Mechanism:** The database entries for `wasana.c` and `user` were updated in previous test runs to the password `123456`, whereas `backend/schema_postgres.sql` and the frontend UI guide users to use the default `sdu1234`. When a user attempts to log in with `sdu1234`, `handle_login_requester` returns `รหัสผ่านไม่ถูกต้อง`. Furthermore, in `backend/server.py`, `handle_login_requester` should accept `sdu1234` as an initial fallback for unmigrated demo/default accounts, matching the behavior of `handle_login_staff`.

**Predicts:** Testing `POST /api` `loginRequester` with `wasana.c` and `sdu1234` currently fails with status `error`. Resetting the hash or supporting `sdu1234` fallback immediately returns `status: success` with token.

**Would be falsified by:** `wasana.c` accepting `sdu1234` currently.

### H3 — Dead unreachable code in `formatStockDisplay` (confidence: high)

**Mechanism:** In both requester and staff templates in `scripts/generate_separated_portals.py`, the previous patch prepended the escaped body but left the unescaped return statements before the closing brace `}`. While not a syntax error, it leaves dead code and confuses AST parsers.

**Predicts:** Lines 1705-1710 and 4748-4753 contain duplicate `if (!isMulti ...)` statements after `return `${pieces} ${safePiece}`;`.

**Would be falsified by:** `formatStockDisplay` having only one `return` block.

## Suspect files

- `scripts/generate_separated_portals.py:3854` — Duplicate `.join('')` in staff modal template [H1]
- `scripts/generate_separated_portals.py:4726` — Duplicate `.join('')` in staff PDF export template [H1]
- `scripts/generate_separated_portals.py:1705` — Unreachable duplicate block in requester `formatStockDisplay` [H3]
- `scripts/generate_separated_portals.py:4748` — Unreachable duplicate block in staff `formatStockDisplay` [H3]
- `backend/server.py:890` — Password validation in `handle_login_requester` [H2]
- `staff.html:1199` — Compiled duplicate `.join('')` [H1]
- `staff.html:2070` — Compiled duplicate `.join('')` [H1]

## Verification steps

1. [H1] Check `scripts/generate_separated_portals.py` at line 3854 and 4726.
   - Confirms H1 if: consecutive `}).join('')}\n`).join('')}` is present.
   - Refutes H1 if: only one `.join('')` exists.
2. [H2] Check `handle_login_requester` live API call with `{"username": "wasana.c", "password": "sdu1234"}`.
   - Confirms H2 if: response is `{"status": "error", "message": "รหัสผ่านไม่ถูกต้อง..."}`.
   - Refutes H2 if: response is `{"status": "success"}`.
3. [H3] Check `scripts/generate_separated_portals.py` lines 1696-1711 and 4739-4754 for double function bodies.
   - Confirms H3 if: duplicate `if (!isMulti || ratio <= 1)` appears twice within the same function.

## Allowed scope

- `scripts/generate_separated_portals.py`
- `backend/server.py`
- `staff.html`
- `index.html`
- `portal.html`
- `CHANGELOG.md`
- `tests/test_stock_logic.py`

**Blast radius:** Login authentication logic in backend server and SSOT separated portal generator, plus footer version synchronization. Does not affect database schema or state machine deduction rules.

## Forbidden scope

- `backend/schema_postgres.sql` — Schema and table structures are already correct; no DDL alterations needed.
- `data/` and `.venv/` — No changes to raw data or environment.

## Success criteria

- [x] `staff.html` and `index.html` compile cleanly via `scripts/generate_separated_portals.py` with 0 duplicate tokens or syntax errors.
- [x] Staff login on `staff.html` with `admin_staff` and password `••••••••` or `sdu1234` successfully logs in, receives token, and renders dashboard.
- [x] Requester login on `index.html` with `wasana.c` and password `sdu1234` successfully logs in, receives token, and renders item catalog.
- [x] Requester login on `index.html` with `user` and password `sdu1234` successfully logs in.
- [x] Automated pytest test suite passes 100% (`pytest tests/test_stock_logic.py` - 56 passed).
- [x] Official verification script passes 100% (`verify_rules.py` - 100% compliant).
- [x] `SYSTEM_VERSION` bumped to `3.0.8` across all institutional files and changelog updated.

## Verification log

- 2026-11-05 10:26 Baseline pytest test suite: 54 passed in 3.19s.
- 2026-11-05 10:26 Step 1 [H1]: Inspected `scripts/generate_separated_portals.py` lines 3853-3856 and 4725-4728. Confirmed duplicate `.join('')` calls producing invalid JavaScript syntax `}).join('')}\n`).join('')}` in staff modal and PDF export templates. Verdict: `CONFIRMED`.
- 2026-11-05 10:26 Step 2 [H2]: Executed `handle_login_requester` with `wasana.c` and password `sdu1234`. Output: `{"status": "error", "message": "รหัสผ่านไม่ถูกต้อง กรุณาตรวจสอบหรือติดต่อเจ้าหน้าที่พัสดุ"}`. Confirmed default password rejected. Verdict: `CONFIRMED`.
- 2026-11-05 10:26 Step 3 [H3]: Inspected `formatStockDisplay` in both portals. Found duplicate unreachable unescaped function bodies after `return `${pieces} ${safePiece}`;`. Verdict: `CONFIRMED`.

## Resolution log

- 2026-11-05 10:27 Fix H1 & H3: Removed duplicate `join` tokens and cleaned dead duplicate `formatStockDisplay` body in `scripts/generate_separated_portals.py`. Re-compiled `index.html` and `staff.html`. Verified 0 duplicate tokens.
- 2026-11-05 10:27 Fix H2: Added institutional `sdu1234` default fallback in `backend/server.py` (`handle_login_requester`), and reset PBKDF2 hashes for demo accounts `wasana.c` and `user` to `sdu1234`.
- 2026-11-05 10:28 Version Synchronization: Bumped `SYSTEM_VERSION` to `3.0.8` across `CHANGELOG.md`, `backend/server.py`, `scripts/generate_separated_portals.py`, `portal.html`, `index.html`, `staff.html`, and `tests/test_stock_logic.py`.
- 2026-11-05 10:29 Scope verification: Checked with `check_scope.py`. All 7 changed files strictly within declared allowed scope.
- 2026-11-05 10:29 Rule verification: Ran `verify_rules.py` - 100% compliant (0 emojis, 0 native dialogs, versions synced, generator clean, 56 passed).
- 2026-11-05 10:30 Server restart: Daemon restarted on port 8080. Live tests confirmed Staff login (`admin_staff`), Requester login (`wasana.c`, `user`), and API health check all return HTTP 200 OK.

