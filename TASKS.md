# แผนงานและรายการขั้นตอนการพัฒนา (TASKS.md / ROADMAP)
### ระบบขอเบิกพัสดุและคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต (Stock Order SDU)

---

## สรุปภาพรวมความคืบหน้า (Progress Summary)
- [x] **Phase 1: สถาปัตยกรรมหลักและการแยกระบบพอร์ทัล 100% (Completed)**
- [x] **Phase 2: ยกระดับ UI/UX, Vector Icons, SweetAlert2 และระบบรายการคำขอ (Completed)**
- [x] **Phase 3: ความสมบูรณ์ของระบบ, ไอคอน Favicon, ลิขสิทธิ์ และ PWA Mobile Support (Completed)**
- [x] **Phase 4: การออกแบบฐานข้อมูล PostgreSQL 17 / Docker Compose (Completed)**
- [x] **Phase 5: พัฒนา Python PostgreSQL REST API Server & เชื่อมต่อ Frontend พร้อม Offline Fallback (Completed)**
- [x] **Phase 6: การทดสอบอัตโนมัติ (pytest Unit & Integration Tests) & CI/CD Workflow (Completed)**
- [x] **Phase 7: ระบบอนุมัติ 2 ขั้นตอน, โควตาการเบิกรายเดือน และการวิเคราะห์ข้อมูลระยะยาว (Completed)**
- [x] **Phase 8: การควบคุมสิทธิ์ RBAC, แบบฟอร์มใบเบิก 4 ฝ่าย, การส่งออกสถิติ และ Audit Trail (Completed)**

---

## Phase 1: สถาปัตยกรรมหลักและการแยกระบบ (Completed)
- [x] **Task 1.1:** สกัดข้อมูลพัสดุจริง 34 รายการ (66 รูปภาพหน่วยย่อยและหน่วยกล่อง ตั้งชื่อไฟล์ตรงตามชื่อพัสดุภาษาไทย) จากไฟล์ Excel `data/ยอดสต๊อก ตค.xlsx`
- [x] **Task 1.2:** โครงสร้างข้อมูลกลุ่มงาน 5 หน่วยงานภายใน สวท. และรายชื่อหัวหน้าหน่วยงาน 4 ท่าน จากไฟล์ `data/รายนามบุคลากร สวท.docx`
- [x] **Task 1.3:** แยกโค้ดเป็น 2 พอร์ทัลอิสระ `index.html` (ผู้ขอเบิก) และ `staff.html` (เจ้าหน้าที่)
- [x] **Task 1.4:** ระบบล็อกอินรักษาความปลอดภัยเบื้องต้นสำหรับเจ้าหน้าที่พัสดุ (Staff Auth Session)
- [x] **Task 1.5:** ระบบคำนวณ 2 หน่วยนับอัตโนมัติ (กล่อง และ ชิ้น/ซอง/แผ่น)
- [x] **Task 1.6:** สูตรคำนวณยอดสต๊อกพร้อมเบิกจริง `Available = On-Hand - Reserved`
- [x] **Task 1.7:** ระบบตะกร้าขอเบิกพัสดุ (Slide-Over Cart Drawer) พร้อมระบุวัตถุประสงค์
- [x] **Task 1.8:** ระบบคิวอนุมัติคำขอเบิกพัสดุ (Approval Workflow) ใน `staff.html`
- [x] **Task 1.9:** แท่นลงนามลายเซ็นดิจิทัล (HTML5 Canvas E-Signature Pad) รองรับ Touchscreen
- [x] **Task 1.10:** ระบบพิมพ์ใบเบิกพัสดุทางการ (Official PDF Printable Form) พร้อมตราสัญลักษณ์ มสด. และประทับลายเซ็นจริง

---

## Phase 2: ยกระดับ UI/UX, SweetAlert2 และระบบรายการคำขอ (Completed)
- [x] **Task 2.1:** ปรับเปลี่ยนไอคอนทั้งหมดเป็น 100% Vector SVG Icons (Stroke-based) ปราศจากการใช้ Emoji ใน UI
- [x] **Task 2.2:** ปรับระบบ Searchable User & Department Combobox ให้เลือกชื่อหัวหน้าหน่วยงาน/บุคลากรเพื่อเติมกลุ่มงาน สวท. ทั้ง 5 หน่วยงานให้อัตโนมัติ
- [x] **Task 2.3:** นำเข้าไลบรารี **SweetAlert2** และดาวน์โหลดเป็น Local Asset (`assets/js/sweetalert2.all.min.js`) รองรับ Offline 100%
- [x] **Task 2.4:** ปรับแต่งธีม SweetAlert2 ให้เป็นโทนสีน้ำเงิน มสด. (`#1e40af`) และฟอนต์ `Prompt`
- [x] **Task 2.5:** กำจัดคำสั่ง `alert()`, `confirm()`, และ `prompt()` ออกจากโค้ดทั้งหมด (0 occurrences)
- [x] **Task 2.6:** เพิ่มปุ่ม **"รายการคำขอของฉัน"** บน Header พร้อมตัวเลขนับจำนวนคำขอ (Count Badge)
- [x] **Task 2.7:** พัฒนาหน้าต่างป๊อปอัปดูรายการคำขอ (`#myRequisitionsModal`) พร้อมระบบค้นหา, แท็บคัดกรองสถานะ 5 สถานะ, การ์ดแสดงรายการพัสดุ และปุ่มคัดลอกเลขที่เอกสาร
- [x] **Task 2.8:** ระบบ Real-time Cross-tab Sync ด้วย Storage Event Listener อัปเดตข้อมูลข้ามแท็บทันที

---

## Phase 3: ความสมบูรณ์ของระบบ, Favicon, ลิขสิทธิ์ และ PWA Support (Completed)
- [x] **Task 3.1:** นำเข้าตราสัญลักษณ์ทางการ มสด. (`logo_sdu.png`) ย้ายจัดเก็บใน `assets/logo_sdu.png` และสร้างไอคอน **`favicon.ico`**, **`assets/favicon.svg`**, **`assets/icon-192.png`**, **`assets/icon-512.png`** เพื่อลบข้อผิดพลาด `404 Not Found: /favicon.ico` บนเซิร์ฟเวอร์
- [x] **Task 3.2:** สร้างไฟล์ **`LICENSE`** (MIT License) อย่างเป็นทางการให้สอดคล้องกับ Badge ใน README
- [x] **Task 3.3:** พัฒนาหน้า **`404.html`** แบบ Custom ธีม SDU Blue พร้อมปุ่มพากลับสู่หน้าหลัก (`index.html`) และพอร์ทัลกลาง (`portal.html`)
- [x] **Task 3.4:** สร้างไฟล์ **`manifest.json`** และการตั้งค่า Web App Manifest เพื่อรองรับฟีเจอร์ **Add to Home Screen (PWA)** สำหรับอาจารย์และบุคลากรที่ใช้งานผ่านสมาร์ตโฟน/แท็บเล็ต
- [x] **Task 3.5:** นำตราสัญลักษณ์ทางการ มสด. ไปประดับบน Header ของ `index.html`, `staff.html` และหัวเอกสารใบขอเบิกพัสดุ (PDF Printable Form) อย่างสง่างาม

---

## Phase 4: สถาปัตยกรรมฐานข้อมูล PostgreSQL 17 และ Docker Compose (Completed)
- [x] **Task 4.1:** ออกแบบและสร้างไฟล์ **`backend/schema_postgres.sql`** สำหรับฐานข้อมูล **PostgreSQL 17** (`sdu_inventory`) ครอบคลุม 6 ตารางหลัก:
  - `departments`: ข้อมูลกลุ่มงาน/หน่วยงานภายใน สวท. 5 หน่วยงาน
  - `users`: ข้อมูลรายชื่อบุคลากรผู้มีสิทธิ์ขอเบิก (หัวหน้าหน่วยงาน 4 ท่านจาก `รายนามบุคลากร สวท.docx`)
  - `inventory_items`: ข้อมูลรายการพัสดุ 34 รายการ พร้อมระบบแปลง 2 หน่วยนับ
  - `requisitions`: ข้อมูลหัวเอกสารใบขอเบิก สถานะ และลายเซ็นดิจิทัล Base64
  - `requisition_items`: รายการพัสดุย่อยในแต่ละใบขอเบิก พร้อม Snapshot อัตราส่วนแปลงหน่วย (`pieces_per_box_snapshot`) และ FK `ON DELETE CASCADE`
  - `stock_transactions`: ประวัติความเคลื่อนไหวสต๊อก (`IN`, `OUT`, `ADJUST`) สำหรับตรวจสอบย้อนหลัง (Audit Log)
  - สร้าง Trigger PL/pgSQL อัปเดต `updated_at` อัตโนมัติ และสคริปต์ซิงค์ Sequence (`setval`)
- [x] **Task 4.2:** สร้างไฟล์ **`docker-compose.yml`** รัน PostgreSQL 17 (`postgres:17-alpine`) บนพอร์ต `5433` พร้อมตั้งค่า Auto-init สคริปต์ SQL และคอนเทนเนอร์ Web/API (`sdu_stock_app`)
- [x] **Task 4.3:** อัปเดตสคริปต์ **`backend/init_db.py`** ตรวจสอบและสร้างฐานข้อมูลพร้อมนำเข้า Schema ทั้งบน PostgreSQL 17 และ MySQL
- [x] **Task 4.4:** อัปเดต `requirements.txt` ติดตั้ง `psycopg2-binary>=2.9.9` และกำหนดค่าสภาพแวดล้อมใน `.env` และ `.env.example`

---

## Phase 5: พัฒนา Python PostgreSQL REST API Server & ระบบจัดการบุคลากร/พัสดุ (Completed)
- [x] **Task 5.1:** พัฒนาเซิร์ฟเวอร์ **`backend/server.py`** ให้บริการทั้ง Static Web Portals และ REST API (`/api`) ที่พอร์ต `8080` รองรับไดรเวอร์ `psycopg2`
- [x] **Task 5.2:** ติดตั้งระบบ **ACID Transactions** และ **Row-Level Locking (`SELECT ... FOR UPDATE`)** เพื่อป้องกันปัญหา Concurrency / Race Condition 100%
- [x] **Task 5.3:** รองรับการทำรายการด้วยคำสั่ง `INSERT ... RETURNING id` บน PostgreSQL สำหรับการบันทึก User และ Inventory Item ใหม่
- [x] **Task 5.4:** รองรับการทำรายการครบวงจร: สร้างคำขอเบิก (`createRequisition`), อนุมัติเต็มจำนวน/บางส่วน (`approveRequisition`), ปฏิเสธ/ยกเลิกคืนยอดจอง (`rejectRequisition`), ลงนามรับของตัดสต๊อกจริง (`completeRequisition`), รับพัสดุเข้าคลัง (`restockItem`), ปรับยอดตรวจนับ (`adjustStock`), จัดการบุคลากร/หน่วยงาน (`saveUser`, `deleteUser`, `addDepartment`), และเพิ่ม/แก้ไข/ลบรายการพัสดุ (`saveItem`, `deleteItem`)
- [x] **Task 5.5:** สร้างระบบ **Hybrid Offline Fallback**: ทำงานบน `localStorage` ได้ทันทีหากเปิดใช้งานแบบออฟไลน์

---

## Phase 6: การทดสอบอัตโนมัติ & CI/CD Workflow (Completed)
- [x] **Task 6.1:** สร้างชุดทดสอบอัตโนมัติ **`tests/test_stock_logic.py`** ด้วย **`pytest`** ครอบคลุม:
  - การคำนวณแปลง 2 หน่วยนับ $(\text{Boxes} \times \text{Ratio}) + \text{Pieces}$
  - สูตรคำนวณสต๊อกคงเหลือจริง $\text{Available} = \text{On-Hand} - \text{Reserved}$
  - การตรวจสอบสถานะคำขอ (State Transitions: `PENDING` ➔ `APPROVED` ➔ `COMPLETED` / `REJECTED`)
  - การตรวจสอบความครบถ้วนและความถูกต้องของโครงสร้าง SQL สคีมา PostgreSQL (`backend/schema_postgres.sql`)
  - ตรวจสอบฟังก์ชันตัวช่วยระบบ (Buddhist Era, Document Number Generator, Configuration)
- [x] **Task 6.2:** สร้าง **GitHub Actions CI Workflow (`.github/workflows/ci.yml`)** เพื่อรันการตรวจสอบ Python Test (`pytest`) อัตโนมัติทุกครั้งที่มีการ Push โค้ด
- [x] **Task 6.3:** ปรับปรุงเอกสารคู่มือทั้งหมดสู่เวอร์ชัน `3.0.0`

---

## Phase 7: ระบบอนุมัติ 2 ขั้นตอน, โควตาการเบิกรายเดือน และการวิเคราะห์ข้อมูลระยะยาว (Completed)
- [x] **Task 7.1:** อัปเดตสคีมาฐานข้อมูล PostgreSQL 17 (`backend/schema_postgres.sql` และ `backend/server.py` auto-migration):
  - เพิ่มคอลัมน์ `monthly_limit INT DEFAULT 0` ในตาราง `inventory_items`
  - เพิ่มคอลัมน์ `last_restocked_at TIMESTAMP DEFAULT NULL` ในตาราง `inventory_items`
  - ขยายสถานะคำขอใน `requisitions.status` รองรับ `VERIFIED` (`PENDING`, `VERIFIED`, `APPROVED`, `COMPLETED`, `REJECTED`)
  - เพิ่มคอลัมน์ `verified_by VARCHAR(150)`, `verified_at TIMESTAMP`, `approved_by VARCHAR(150)`, `approved_at TIMESTAMP` ในตาราง `requisitions`
  - เพิ่มคอลัมน์ `recorded_by VARCHAR(150)` ในตาราง `stock_transactions`
- [x] **Task 7.2:** พัฒนาระบบจำกัดจำนวนการเบิกต่อเดือน (Monthly Quota Limit Enforcement):
  - ตรวจสอบผลรวมยอดเบิกสะสมในงวดเดือนปัจจุบันก่อนสร้างคำขอใน `handle_create_requisition`
  - ปฏิเสธคำขอหากผลรวมเกิน `monthly_limit`
  - แสดงป้ายแจ้งเตือนโควตารายเดือนและยอดโควตาคงเหลือในแคตตาล็อกหน้าผู้เบิก (`index.html`)
  - หน้าต่างปรับตั้งค่าโควตาประจำเดือนในหน้าคลังพัสดุเจ้าหน้าที่ (`staff.html`)
- [x] **Task 7.3:** ปรับปรุงวงจรคำขอเบิก 2 ขั้นตอน (Staff Screening -> Head Final Approval):
  - เจ้าหน้าที่พัสดุกดปุ่ม "ผ่านการคัดกรอง (ส่งต่อหัวหน้า)" เปลี่ยนสถานะเป็น `VERIFIED`
  - เพิ่มแท็บ "รอหัวหน้าอนุมัติ (`VERIFIED`)" ในหน้า `staff.html`
  - หัวหน้าหน่วยงานกดยืนยันอนุมัติขั้นสุดท้าย เปลี่ยนสถานะเป็น `APPROVED` (ล็อกยอด `reserved_pieces`)
  - อัปเดต REST API: `verifyRequisition`, `approveRequisition`, `rejectRequisition`
- [x] **Task 7.4:** ระบบประทับเวลาการรับเข้าพัสดุ (Incoming Stock Timestamp):
  - บันทึก Timestamp ละเอียดระดับวินาทีใน `stock_transactions` เมื่อรับเข้าพัสดุ (`restockItem`)
  - แสดงคอลัมน์ "วันเวลารับเข้าล่าสุด" ในตารางคลังพัสดุ และแสดงตารางประวัติการรับเข้าย้อนหลัง
- [x] **Task 7.5:** ระบบจัดเก็บข้อมูลระยะยาวและตัวกรองเรียกดูย้อนหลังรายเดือน (Monthly Historical Filter):
  - เพิ่ม Dropdown กรองเดือน/ปี พ.ศ. ในหน้าคำขอเบิก (`renderStaffRequisitions`, `myRequisitionsModal`)
  - เพิ่มตัวกรองงวดเดือนในตารางประวัติความเคลื่อนไหวสต๊อก
- [x] **Task 7.6:** แดชบอร์ดสรุปยอดสถิติและการวิเคราะห์การเบิกรายเดือน (Monthly Analytics Dashboard):
  - สร้าง Endpoint `getMonthlyAnalytics` สรุปภาพรวมประจำเดือน
  - แสดงอันดับพัสดุที่ถูกเบิกมากที่สุด (Top Requisitioned Items)
  - แสดงอันดับพัสดุที่ถูกเบิกน้อยที่สุด / ไม่มีการเบิก (Least Requisitioned / Slow-Moving Items)
- [x] **Task 7.7:** อัปเดตแบบฟอร์มใบเบิกพัสดุทางการ (Official PDF) รองรับการแสดงผลลายมือชื่อและการอนุมัติ
- [x] **Task 7.8:** อัปเดตชุดทดสอบอัตโนมัติ `tests/test_stock_logic.py` ครอบคลุม State Machine 2 ชั้น และ Quota Validation

---

## Phase 8: การควบคุมสิทธิ์ RBAC, แบบฟอร์มใบเบิก 4 ฝ่าย, การส่งออกสถิติ และ Audit Trail ย้อนหลัง (Completed)
- [x] **Task 8.1:** ระบบจัดการสิทธิ์การใช้งานตามบทบาท (Role-Based Access Control - RBAC):
  - แยกสิทธิ์และบัญชีผู้ใช้งานระหว่าง เจ้าหน้าที่พัสดุ (`STAFF`), หัวหน้าหน่วยงานผู้อนุมัติ (`HEAD`), และผู้ดูแลระบบ (`ADMIN`)
  - สิทธิ์ `STAFF`: จัดการสต๊อก, รับของเข้าคลัง, ตรวจสอบคำขอ, และกดยืนยันผ่านการคัดกรอง (`Verify`)
  - สิทธิ์ `HEAD`: เข้าสู่ระบบเพื่อพิจารณาอนุมัติขั้นสุดท้าย (`Approve`) หรือส่งกลับแก้ไขคำขอสถานะ `VERIFIED`
  - บังคับใช้สิทธิ์ทั้งในระดับ Backend API และการควบคุมการแสดงผลปุ่มบน Frontend
- [x] **Task 8.2:** ยกระดับแบบฟอร์มใบเบิกพัสดุทางการ (Official PDF Printable Form) เป็น 4 ฝ่าย:
  - ปรับปรุงบล็อกท้ายเอกสาร A4 PDF แสดงช่องลงนาม 4 ฝ่ายครบถ้วน:
    1. ผู้ขอเบิกพัสดุ (Requester - ชื่อตัวบรรจงและวันที่ขอเบิก)
    2. เจ้าหน้าที่พัสดุผู้คัดกรอง (Staff Verifier - ดึงชื่อและวันเวลาคัดกรองจริง)
    3. หัวหน้าหน่วยงานผู้อนุมัติ (Head Approver - ดึงชื่อและวันเวลาอนุมัติจริง)
    4. ผู้รับมอบพัสดุ (Receiver - ประทับรูปลายเซ็นดิจิทัลจริงและวันที่รับมอบ)
- [x] **Task 8.3:** ระบบส่งออกรายงานสรุปยอดและสถิติรายเดือน (Monthly Analytics Export):
  - เพิ่มปุ่มส่งออกรายงานสถิติประจำเดือนเป็นไฟล์ CSV / Excel
  - พัฒนาแบบฟอร์มพิมพ์รายงานสรุปประจำเดือนสำหรับผู้บริหาร (Executive Monthly Summary PDF)
- [x] **Task 8.4:** หน้าต่างตรวจสอบประวัติความเคลื่อนไหวสต๊อกย้อนหลังรายพัสดุ (Item Transaction Audit Trail Modal):
  - เพิ่มปุ่ม "ดูประวัติความเคลื่อนไหว" ในแต่ละแถวของตารางคลังพัสดุ
  - แสดงตารางประวัติย้อนหลังทุกรายการจาก `stock_transactions` (รับเข้า, จ่ายออกตามใบเบิก, ปรับยอดตรวจนับ พร้อมวันเวลาและผู้บันทึก)
- [x] **Task 8.5:** แสดงผลโควตาคงเหลือของผู้ขอเบิกแบบ Dynamic (Personal Monthly Quota Tracking):
  - คำนวณยอดที่ผู้ขอเบิกท่านนั้นๆ เคยขอเบิกไปแล้วในเดือนปัจจุบันเทียบกับ `monthly_limit`
  - แสดงผล "โควตาคงเหลือของท่านในเดือนนี้" บนการ์ดพัสดุในหน้าแคตตาล็อกผู้ขอเบิก
- [x] **Task 8.6:** ระบบแจ้งเตือนพัสดุถึงจุดสั่งซื้อใหม่ (Low Stock Reorder Point Alert):
  - เพิ่มการ์ดสรุปรายการพัสดุที่คงเหลือต่ำกว่าเกณฑ์แจ้งเตือนขั้นต่ำ (`min_alert`) บนแท็บคลังพัสดุ
  - แสดงป้ายแจ้งเตือนสถานะสต๊อกใกล้หมดเพื่อการวางแผนจัดซื้อล่วงหน้า
