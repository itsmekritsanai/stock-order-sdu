# Versioning & Testing Protocol (references/versioning-and-testing.md)

This reference outlines the Semantic Versioning protocol, Keep a Changelog documentation rules, and automated test execution.

---

## 1. Strict Versioning Protocol

* **Format:** Semantic Versioning 2.0.0 (`MAJOR.MINOR.PATCH`).
* **Trigger:** Whenever making bug fixes, features, or architectural enhancements:
  - **`PATCH` (e.g. 3.0.5 -> 3.0.6):** Bug fixes, UI adjustments, styling updates, refactoring.
  - **`MINOR` (e.g. 3.0.0 -> 3.1.0):** New backward-compatible feature (e.g. new export format, batch processing).
  - **`MAJOR` (e.g. 3.0.0 -> 4.0.0):** Breaking architectural changes (e.g. database migration, auth overhaul).

---

## 2. Synchronization Checklist

When bumping the version, all 7 locations must be updated simultaneously:

1. [`CHANGELOG.md`](file:///c:/Users/namtarn/Downloads/stock-order-sdu/CHANGELOG.md) - Under `## [X.Y.Z] - YYYY-MM-DD`
2. [`backend/server.py`](file:///c:/Users/namtarn/Downloads/stock-order-sdu/backend/server.py) - `SYSTEM_VERSION = "X.Y.Z"`
3. [`scripts/generate_separated_portals.py`](file:///c:/Users/namtarn/Downloads/stock-order-sdu/scripts/generate_separated_portals.py) - `SYSTEM_VERSION = "X.Y.Z"`
4. [`tests/test_stock_logic.py`](file:///c:/Users/namtarn/Downloads/stock-order-sdu/tests/test_stock_logic.py) - `assert SYSTEM_VERSION == "X.Y.Z"`
5. [`portal.html`](file:///c:/Users/namtarn/Downloads/stock-order-sdu/portal.html) - Footer `(Stock Order SDU vX.Y.Z)`
6. [`index.html`](file:///c:/Users/namtarn/Downloads/stock-order-sdu/index.html) - Footer `(vX.Y.Z)`
7. [`staff.html`](file:///c:/Users/namtarn/Downloads/stock-order-sdu/staff.html) - Footer `(Staff Portal vX.Y.Z)`

---

## 3. Keep a Changelog Format

Document every release under:
- `### Added` - For new features.
- `### Changed` - For changes in existing functionality.
- `### Deprecated` - For soon-to-be removed features.
- `### Removed` - For now removed features.
- `### Fixed` - For any bug fixes.
- `### Security` - In case of vulnerabilities / hardening.

---

## 4. Automated Testing

* **Framework:** `pytest` (with `pytest-cov`).
* **Command:**
  ```powershell
  .venv\Scripts\pytest tests/test_stock_logic.py
  ```
* **Coverage Target:** $\ge 90\%$.
* **Requirements:** All tests must pass with 0 failures before delivering code or pushing to git.
