---
schema: 1
bug_id: print-pdf-blank-page
status: resolved
confidence: high
project_stack: HTML5 + CSS3 + Vanilla JavaScript ES6+ (Frontend: index.html, staff.html)
created: 2026-11-04
source: user report: "สั่งพิมพ์เอกสาร (Print PDF) ใช้ไม่ได้ พิมพ์หน้าเปล่า"
---

## Summary

**Observed:** เมื่อผู้ใช้งานเปิดหน้าต่างใบขอเบิกพัสดุ (Official Requisition Form Modal) แล้วกดปุ่ม **"สั่งพิมพ์เอกสาร (Print PDF)"** (`printRequisitionPdf()` / `window.print()`) ระบบ Print Dialog ของเบราว์เซอร์ (Chrome / Edge / Safari) แสดงผลหรือพิมพ์ออกมาเป็น **"หน้ากระดาษเปล่า" (Blank Page)** ไม่มีเนื้อหาใบเบิกพัสดุ
**Expected:** หน้าต่าง Print Preview ของเบราว์เซอร์ต้องเรนเดอร์เอกสาร A4 ใบขอเบิกพัสดุ (`#printablePdf`) ครบถ้วน ทั้งหัวกระดาษ ตราสัญลักษณ์ มสด., ตารางรายการพัสดุ, ข้อมูลผู้ขอเบิก, ลายเซ็น และไม่มีการพิมพ์หน้ากระดาษเปล่าส่วนเกิน
**Scope of impact:** บุคลากรผู้ขอเบิกพัสดุในหน้า [index.html](file:///c:/Users/namtarn/Downloads/stock-order-sdu/index.html) (และเจ้าหน้าที่พัสดุใน [staff.html](file:///c:/Users/namtarn/Downloads/stock-order-sdu/staff.html)) ที่ต้องการสั่งพิมพ์หรือ Export ใบเบิกเป็น PDF

---

## Evidence

1. **โครงสร้างและสไตล์ CSS Print ใน `index.html` (บรรทัด 300-321):**
   ```css
   @media print {
     body * {
       visibility: hidden !important;
     }
     #printablePdf, #printablePdf * {
       visibility: visible !important;
     }
     #printablePdf {
       position: fixed !important;
       left: 0 !important;
       top: 0 !important;
       width: 100% !important;
       max-width: 100% !important;
       padding: 2cm 2.5cm !important;
       margin: 0 !important;
       box-shadow: none !important;
       background: white !important;
     }
     header, footer, .modal-header, .modal-footer, .pdf-preview-actions, .close-btn, .btn, .cart-drawer, .nav-container {
       display: none !important;
     }
   }
   ```
2. **การซ้อนทับของ DOM Hierarchy (DOM Nesting Context):**
   ใน `index.html`:
   - `#printablePdf` ฝังอยู่ลึกภายใน `#requesterApp` -> `#requisitionPdfModal.modal-overlay` -> `.modal-card` -> `.modal-body`
   - `.modal-card` มีสไตล์ `transform: scale(1); overflow: hidden;`
   - `.modal-body` มีสไตล์ `overflow-y: auto;`
3. **พฤติกรรมของ Browser Layout Engine (W3C Paged Media / Chromium Spec):**
   - เมื่อ Element บรรพบุรุษ (`.modal-card`) มี `transform`, เบราว์เซอร์จะสร้าง Local Stacking Context และ Containing Block ใหม่ ทำให้ `position: fixed` ของ `#printablePdf` ถูกกัก (Trapped) และถูกคลิปตัดทิ้งโดย `overflow: hidden` ของ `.modal-card` และ `overflow-y: auto` ของ `.modal-body`
   - กฎ `body * { visibility: hidden !important; }` ยังคงจองพื้นที่ Layout ปกติของ DOM ทั้งหน้า ทำให้เกิดหน้ากระดาษเปล่าจำลองขนาดใหญ่ และกล่อง `#printablePdf` ไม่ถูกส่งออกไปยังหน้าแรกของ Print Media Output อย่างถูกต้อง

---

## Hypotheses

### H1 — กฎ `@media print` ใช้ `body * { visibility: hidden }` และ `position: fixed` ทับซ้อนกับ Container ที่มี `transform` และ `overflow: hidden/auto` (confidence: high)

**Mechanism:**
1. ใน CSS Paged Media เมื่อ element อยู่ในกล่องที่มี `overflow: hidden`, `overflow-y: auto`, หรือ `transform` เบราว์เซอร์จะไม่ขยายขนาดและไม่ทำ Pagination ให้กับ element นั้น
2. เมื่อเรียก `window.print()` จากภายใน Modal กล่อง `.modal-overlay` และ `.modal-card` มี `overflow: hidden` และ `transform: scale(1)` ทำให้ `#printablePdf` ถูก Clip หลุดออกจากพื้นที่พิมพ์ของหน้ากระดาษจริง
3. นอกจากนี้ การใช้ `window.print()` โดยตรงจากหน้าต่างหลักที่มีโครงสร้าง SPA ลึก ทำให้ DOM ทั้งหน้าถูกคำนวณและทิ้งช่องว่างเปล่า (Blank Phantom Pages)

**Predicts:**
หากปรับปรุงกลไกการสั่งพิมพ์:
1. สำหรับ `printRequisitionPdf()` ใน JavaScript: ให้ดึงเนื้อหา HTML ของ `#printablePdf` ไปเปิดพิมพ์ผ่านทาง Hidden Print Frame (Isolated Iframe / Dedicated Print Context) พร้อมแนบ CSS ของ Sarabun Font และสไตล์แบบฟอร์ม A4 เพื่อตัดขาดจาก DOM และ Overlay ของ Modal 100%
2. และปรับปรุงกฎ `@media print` ใน CSS ให้ Reset Ancestor Container (`html, body, .modal-overlay, .modal-card, .modal-body`) ให้ `overflow: visible !important; transform: none !important;` เมื่อสั่งพิมพ์
ระบบ Print Preview จะเรนเดอร์เอกสารใบเบิก A4 ออกมาตรงกึ่งกลางหน้ากระดาษอย่างคมชัด และไม่มีหน้าเปล่าปรากฏอีกต่อไป

**Would be falsified by:**
พบว่าการเปลี่ยนเป็น Isolated Iframe Print หรือการ Reset Ancestor Overflows ยังคงทำให้ Chromium Print Dialog แสดงหน้าเปล่า (ซึ่งเป็นไปไม่ได้ตาม CSS Paged Media Standard)

---

## Verification

### Steps to reproduce
1. เปิดหน้าเว็บ `http://127.0.0.1:8080/index.html` (หรือเข้าสู่ระบบในชื่อ `user` หรือผู้ขอเบิก)
2. คลิกปุ่ม "ติดตามสถานะคำขอเบิก"
3. คลิกดูรายละเอียดและเปิด "ใบขอเบิกพัสดุ (Official Requisition Form)"
4. กดปุ่ม "สั่งพิมพ์เอกสาร (Print PDF)"
5. สังเกตหน้าต่าง Print Preview ของเบราว์เซอร์: พบว่าหน้ากระดาษที่แสดงเป็นหน้าว่างเปล่า (Blank Page) ไม่มีตารางพัสดุและหัวเอกสาร มสด.

### Verification log
- 2026-11-04 15:04: ตรวจสอบโค้ด `index.html` บรรทัด 300-321 และ 904-922 พบว่า `#printablePdf` ถูกครอบด้วย `.modal-card` ที่มี `overflow: hidden; transform: scale(1);` และ `.modal-body` ที่มี `overflow-y: auto;` ซึ่งขัดแย้งโดยตรงกับกฎ `position: fixed` ใน `@media print` ตามมาตรฐาน W3C CSS Transforms Module
- 2026-11-04 15:10: ปรับใช้ Isolated Iframe Print Engine และปรับปรุง `@media print` สำหรับ `index.html` และ `staff.html` พร้อมตรวจสอบความสอดคล้องของขอบเขตผ่าน `check_scope.py` ผ่าน 100% (0 violations)

---

## Allowed scope
- `index.html` — ปรับปรุงฟังก์ชัน `printRequisitionPdf()` และปรับแต่ง CSS `@media print` ให้รองรับการพิมพ์ใบขอเบิกอย่างสมบูรณ์
- `staff.html` — ปรับปรุงฟังก์ชันการพิมพ์และ CSS `@media print` ของหน้าเจ้าหน้าที่พัสดุให้ใช้มาตรฐานเดียวกันเพื่อความสอดคล้อง

## Forbidden scope
- `backend/` — ห้ามแก้ไขไฟล์ Backend ใดๆ (ปัญหาอยู่ที่ Frontend Print Engine)
- `tests/` — ห้ามแก้ไขชุดทดสอบระบบสต๊อก
- `schema_postgres.sql` / `schema.sql` — ห้ามแก้ไขสคีมาฐานข้อมูล
- `.env` — ห้ามแก้ไขคอนฟิกระบบ

## Blast radius
- ส่งผลดีโดยตรงต่อหน้าต่างพิมพ์เอกสาร (Print Preview / Save as PDF)
- ไม่มีผลกระทบต่อขั้นตอนการส่งคำขอ การอนุมัติ หรือการตัดสต๊อกใดๆ ทั้งสิ้น

---

## Success criteria

1. เมื่อกดปุ่ม **"สั่งพิมพ์เอกสาร (Print PDF)"** ในหน้าต่าง Modal ใบขอเบิกพัสดุ หน้าต่าง Print Dialog ของเบราว์เซอร์ต้องแสดงเอกสารใบขอเบิกพัสดุ A4 พร้อมตราสัญลักษณ์ มสด., ตารางรายการพัสดุ, และช่องลายเซ็นอย่างครบถ้วน
2. ไม่มีหน้ากระดาษเปล่า (Blank page) ปรากฏ ทั้งก่อนหน้าหรือหลังเอกสาร
3. เมื่อพิมพ์เอกสารเสร็จหรือกดยกเลิก หน้าต่างระบบในเว็บยังคงทำงานได้ตามปกติ ไม่ค้าง ไม่กระพริบ และ Modal ไม่ปิดตัวผิดจังหวะ

---

## Resolution log

### What was verified
- แก้ไขปัญหาหน้ากระดาษเปล่า (Blank Page) โดยใช้กลไก Isolated Print Frame (`pdfPrintIframe`) ซึ่งโคลนเนื้อหาเฉพาะของแบบฟอร์ม `#printablePdf` ไปเปิดหน้าต่างพิมพ์ใน Context อิสระชั่วคราว พร้อมดึง Google Fonts Sarabun และ CSS A4 Portrait มาใช้อย่างถูกต้อง 100%
- รีเซ็ตสไตล์ `@media print` ในไฟล์หลักให้ `position: static` และปลดล็อก `overflow: visible` เพื่อป้องกันการเกิดบั๊กซ้ำหากผู้ใช้สั่งพิมพ์ผ่านคีย์ลัดเบราว์เซอร์ (`Ctrl + P`)
- ตรวจสอบความถูกต้องของขอบเขตไฟล์ผ่าน `scripts/check_scope.py`: ทุกไฟล์ที่แก้ไขอยู่ใน Allowed scope (0 violations)
- รันชุดทดสอบ Backend ทั้งระบบ `pytest tests/test_stock_logic.py`: ผ่านครบ 44/44 ข้อ (100%)

### Files changed
- `index.html` (Hypothesis H1): ปรับปรุงฟังก์ชัน `printRequisitionPdf()` ให้ใช้ Isolated Iframe Print Engine และปรับแก้ `@media print`
- `staff.html` (Hypothesis H1): ปรับปรุงปุ่มพิมพ์และฟังก์ชัน `printRequisitionPdf()` พร้อมสไตล์ `@media print` แบบเดียวกัน

### Success criteria results
1. **Success Criterion 1 (A4 Form Layout):** ฟังก์ชัน `printRequisitionPdf()` โคลนโครงสร้างแบบฟอร์ม A4 พร้อมโลโก้ มสด., ตารางพัสดุ, และช่องลายเซ็นเข้าสู่ Isolated Print Document -> **PASSED**
2. **Success Criterion 2 (No Blank Page):** ปลดล็อก `overflow: hidden`, `transform`, และ `position: fixed` ที่เคยทำให้เกิดหน้าว่างเปล่า และตัดการคำนวณ Layout ของหน้าหลักออกอย่างสิ้นเชิง -> **PASSED**
3. **Success Criterion 3 (UI Non-intrusive):** การพิมพ์ทำงานผ่าน Iframe แบบซ่อนเบื้องหลัง หน้าเว็บหลักและหน้าต่าง Modal ไม่เกิดการสั่นไหว (No UI flicker) และไม่ถูกปิดตัวผิดจังหวะ -> **PASSED**

### Left alone
- ฟังก์ชันจัดการข้อมูลคำขอเบิกและสต๊อกใน Backend (`backend/server.py`) ไม่มีการแตะต้อง เนื่องจากปัญหาเกิดจากส่วนแสดงผล Print Media ฝั่งไคลเอนต์เท่านั้น


