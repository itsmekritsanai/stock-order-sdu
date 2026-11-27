# Versioning & Testing Protocol (references/versioning-and-testing.md)

This reference outlines the Semantic Versioning protocol, Keep a Changelog documentation rules, and automated test execution (v3.8.4).

---

## 1. Strict Versioning Protocol

* **Format:** Semantic Versioning 2.0.0 (`MAJOR.MINOR.PATCH`).
* **Trigger:** Whenever making bug fixes, features, or architectural enhancements:
  - **`PATCH` (e.g. 3.8.2 -> 3.8.3):** Bug fixes, UI adjustments, styling updates, documentation sync, refactoring.
  - **`MINOR` (e.g. 3.7.0 -> 3.8.0):** New backward-compatible feature (e.g. new analytics table, export format, quota rule type).
  - **`MAJOR` (e.g. 3.0.0 -> 4.0.0):** Breaking architectural changes (e.g. database engine overhaul, breaking API change).

---

## 2. Synchronization Checklist

When bumping the version, all 7 locations must be updated simultaneously:

1. [`CHANGELOG.md`](../../../../CHANGELOG.md) — Under `## [X.Y.Z] - YYYY-MM-DD`
2. [`backend/server.py`](../../../../backend/server.py) — `SYSTEM_VERSION = "X.Y.Z"`
3. [`scripts/generate_separated_portals.py`](../../../../scripts/generate_separated_portals.py) — `SYSTEM_VERSION = "X.Y.Z"`
4. [`tests/test_stock_logic.py`](../../../../tests/test_stock_logic.py) — `assert SYSTEM_VERSION == "X.Y.Z"`
5. [`portal.html`](../../../../portal.html) — Header badge & Footer (`ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต vX.Y.Z`)
6. [`index.html`](../../../../index.html) — Regenerated via SSOT (`vX.Y.Z`)
7. [`staff.html`](../../../../staff.html) — Regenerated via SSOT (`vX.Y.Z`)

---

## 3. Keep a Changelog Format

Document every release under:
- `### Added` — For new features.
- `### Changed` — For changes in existing functionality.
- `### Deprecated` — For soon-to-be removed features.
- `### Removed` — For removed features/files.
- `### Fixed` — For any bug fixes.
- `### Security` — For vulnerability fixes / hardening.

---

## 4. Automated Verification & Testing

* **Rules Verification Script:**
  ```powershell
  .venv\Scripts\python .agents/skills/stock-order-rules/scripts/verify_rules.py
  ```
* **Pytest Test Suite (91 tests across 9 test classes):**
  ```powershell
  .venv\Scripts\pytest tests/test_stock_logic.py -v
  ```
* **Coverage Target:** $\ge 90\%$.
* **CI/CD:** `.github/workflows/ci.yml` executes both `verify_rules.py` and `pytest` against a live `postgres:17-alpine` service container on every push/PR.
