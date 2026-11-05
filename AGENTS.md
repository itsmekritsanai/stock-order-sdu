# Project Guidelines & Rules (AGENTS.md)
# Suan Dusit University e-Inventory & Requisition System (Stock Order SDU)

This workspace is governed by the custom skill:
👉 **[stock-order-rules](.agents/skills/stock-order-rules/SKILL.md)**

---

## 📌 Critical System Rules for AI & Developers

1. **Strict Zero-Emoji Policy:**
   - Emojis (`⚠️`, `🟢`, `📦`, `🔍`, `🔔`, `✏️`, `🗑️`, `🏛️`, `💡`, `❌`) are **FORBIDDEN** in all UI elements, buttons, inputs, placeholders, and SweetAlert dialogs.
   - Always use 100% Vector SVG Icons (`svg_icons` / `vIcons`) or CSS badges.

2. **Single Source of Truth (SSOT):**
   - `index.html` (Requester) and `staff.html` (Staff) are generated via `scripts/generate_separated_portals.py`.
   - Never modify portals without reflecting changes in `scripts/generate_separated_portals.py`.

3. **Strict 100% Portal Separation (Zero-Trust):**
   - `index.html` (Public Requester) must **NEVER** contain staff actions (approvals, stock adjustments, user/dept management).
   - `staff.html` (Private Staff) is protected by HMAC token authentication.

4. **Inventory State Machine & Deduction Integrity:**
   - Formula: $\text{Available} = \text{On-Hand} - \text{Reserved}$
   - Formula: $\text{Total Pieces} = (\text{Boxes} \times \text{Pieces Per Box}) + \text{Pieces}$
   - `APPROVED` locks reserved quota (`reserved += approved`). Does NOT deduct physical `on_hand`.
   - `COMPLETED` deducts physical stock (`on_hand -= approved`, `reserved -= approved`) upon handover.

5. **No Native Dialogs:**
   - Never call `alert()`, `confirm()`, or `prompt()`.
   - Always use SweetAlert2 (`Swal.fire()`) with SDU Blue theme (`#1e40af`).

6. **Strict Versioning & Changelog Protocol:**
   - Every change must increment `SYSTEM_VERSION` (Semantic Versioning `MAJOR.MINOR.PATCH`).
   - Every change must be recorded in `CHANGELOG.md` under Keep a Changelog standards.
   - Version must match across `CHANGELOG.md`, `backend/server.py`, `scripts/generate_separated_portals.py`, `tests/test_stock_logic.py`, and UI footers.

7. **Zero-Build Vanilla Architecture:**
   - Pure HTML5, Vanilla CSS3, Modern ES6+. No npm, TailwindCSS, React, Vue, or Webpack.

8. **Automated Verification Script:**
   - Run verification before committing:
     ```powershell
     .venv\Scripts\python .agents/skills/stock-order-rules/scripts/verify_rules.py
     ```
   - Run test suite:
     ```powershell
     .venv\Scripts\pytest tests/test_stock_logic.py
     ```

