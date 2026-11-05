# UI/UX & No-Emoji Guidelines (references/ui-ux-guidelines.md)

This reference outlines the institutional visual style, icon usage, dialog patterns, and strict anti-emoji standards for Suan Dusit University (SDU).

---

## 1. Strict No-Emoji Policy

* **Rule:** No Unicode emoji characters may appear in HTML markup, JavaScript string literals, placeholders, SweetAlert dialogs, table cells, or status badges.
* **Why:** The SDU e-Inventory system is an official university administrative platform. Emojis render inconsistently across operating systems and undermine the institutional identity.
* **Prohibited vs Allowed Replacements:**

| Prohibited Emoji | Prohibited Example | Permitted Replacement |
| :--- | :--- | :--- |
| `⚠️` | `⚠️ ต่ำกว่าเกณฑ์` | `${vIcons.alertTriangle} ต่ำกว่าเกณฑ์` or `<span class="badge badge-warning">ต่ำกว่าเกณฑ์</span>` |
| `🟢` | `🟢 ปกติ` | `${vIcons.checkCircle} ปกติ` or `<span class="badge badge-success">ปกติ</span>` |
| `📦` | `📦 ยอดคงคลัง:` | `ยอดคงคลัง:` or `${vIcons.box} ยอดคงคลัง:` |
| `🔍` | `placeholder="🔍 ค้นหา..."` | `placeholder="ค้นหา..."` |
| `🔔` | `🔔 เตือนที่:` | `${vIcons.bell} เตือนที่:` |
| `✏️` | `✏️ แก้ไข` | `${vIcons.pen} แก้ไข` |
| `🗑️` | `🗑️ ลบ` | `${vIcons.trash} ลบ` |
| `🏛️` | `🏛️ จัดการกลุ่มงาน` | `${vIcons.building} จัดการกลุ่มงาน` |
| `💡` | `💡 คำแนะนำ` | `คำแนะนำ` or `<div class="tip-box">...</div>` |
| `❌` | `❌ หมดสต๊อก` | `<span class="badge badge-danger">หมดสต๊อกชั่วคราว:</span>` |

---

## 2. Vector SVG Icons Registry

Icons are standard SVG elements with `viewBox="0 0 24 24"`, stroke-width 2, fill none, stroke currentColor.

Available in JavaScript through `vIcons`:

```javascript
const vIcons = {
  box: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>`,
  cart: `<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg>`,
  layers: `<svg class="svg-icon" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>`,
  tag: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94.94-2.48 0-3.42L12 2Z"/><circle cx="7" cy="7" r=".5" fill="currentColor"/></svg>`,
  pen: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="m18 2 4 4-12 12H6v-4L18 2z"/><path d="m15 5 4 4"/><path d="M2 22h20"/></svg>`,
  trash: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>`,
  checkCircle: `<svg class="svg-icon" viewBox="0 0 24 24" style="width:14px;height:14px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`,
  alertTriangle: `<svg class="svg-icon" viewBox="0 0 24 24" style="width:14px;height:14px;"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>`,
  bell: `<svg class="svg-icon" viewBox="0 0 24 24" style="width:14px;height:14px;"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>`,
  printer: `<svg class="svg-icon" viewBox="0 0 24 24"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect width="12" height="8" x="6" y="14"/></svg>`,
  building: `<svg class="svg-icon" viewBox="0 0 24 24"><line x1="3" x2="21" y1="22" y2="22"/><line x1="6" x2="6" y1="18" y2="11"/><line x1="10" x2="10" y1="18" y2="11"/><line x1="14" x2="14" y1="18" y2="11"/><line x1="18" x2="18" y1="18" y2="11"/><polygon points="12 2 20 7 4 7"/></svg>`,
  user: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`
};
```

---

## 3. SweetAlert2 Standard Dialog Rules

* **Confirm Button Color:** `#1e40af` (SDU Blue)
* **Success Accent Color:** `#059669` (SDU Green)
* **Danger/Delete Color:** `#dc2626`
* **Cancel Button Color:** `#64748b` (Slate Neutral)
* **Font Family:** `Prompt, sans-serif`
* **Toast Notification Standard:**
  ```javascript
  Swal.fire({
    icon: 'success',
    title: 'บันทึกข้อมูลเรียบร้อยแล้ว',
    timer: 1500,
    showConfirmButton: false
  });
  ```

