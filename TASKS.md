# แผนงานและรายการขั้นตอนการพัฒนา (TASKS.md / ROADMAP)
### ระบบขอเบิกพัสดุและคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต (Stock Order SDU)

---

## 🎯 สรุปภาพรวมความคืบหน้า (Progress Summary)
- [x] **Phase 1: สถาปัตยกรรมหลักและการแยกระบบพอร์ทัล 100% (Completed)**
- [x] **Phase 2: ยกระดับ UI/UX, Vector Icons, SweetAlert2 และระบบรายการคำขอ (Completed)**
- [x] **Phase 3: ความสมบูรณ์ของระบบ, ไอคอน Favicon, ลิขสิทธิ์ และ PWA Mobile Support (Completed)**
- [x] **Phase 4: การออกแบบฐานข้อมูลเชิงสัมพันธ์ MySQL & สคริปต์สร้างตารางอัตโนมัติ (Completed)**
- [x] **Phase 5: พัฒนา Python MySQL REST API Server & เชื่อมต่อ Frontend พร้อม Offline Fallback (Completed)**
- [ ] **Phase 6: การทดสอบอัตโนมัติ (pytest Coverage >= 90%), CI/CD Workflow & Production Deployment**

---

## ✅ Phase 1: สถาปัตยกรรมหลักและการแยกระบบ (Completed)
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

## ✅ Phase 2: ยกระดับ UI/UX, SweetAlert2 และระบบรายการคำขอ (Completed)
- [x] **Task 2.1:** ปรับเปลี่ยนไอคอนทั้งหมดเป็น 100% Vector SVG Icons (Stroke-based) ปราศจากการใช้ Emoji ใน UI
- [x] **Task 2.2:** ปรับระบบ Searchable User & Department Combobox ให้เลือกชื่อหัวหน้าหน่วยงาน/บุคลากรเพื่อเติมกลุ่มงาน สวท. ทั้ง 5 หน่วยงานให้อัตโนมัติ
- [x] **Task 2.3:** นำเข้าไลบรารี **SweetAlert2** และดาวน์โหลดเป็น Local Asset (`assets/js/sweetalert2.all.min.js`) รองรับ Offline 100%
- [x] **Task 2.4:** ปรับแต่งธีม SweetAlert2 ให้เป็นโทนสีน้ำเงิน มสด. (`#1e40af`) และฟอนต์ `Prompt`
- [x] **Task 2.5:** กำจัดคำสั่ง `alert()`, `confirm()`, และ `prompt()` ออกจากโค้ดทั้งหมด (0 occurrences)
- [x] **Task 2.6:** เพิ่มปุ่ม **"รายการคำขอของฉัน"** บน Header พร้อมตัวเลขนับจำนวนคำขอ (Count Badge)
- [x] **Task 2.7:** พัฒนาหน้าต่างป๊อปอัปดูรายการคำขอ (`#myRequisitionsModal`) พร้อมระบบค้นหา, แท็บคัดกรองสถานะ 5 สถานะ, การ์ดแสดงรายการพัสดุ และปุ่มคัดลอกเลขที่เอกสาร
- [x] **Task 2.8:** ระบบ Real-time Cross-tab Sync ด้วย Storage Event Listener อัปเดตข้อมูลข้ามแท็บทันที

---

## ✅ Phase 3: ความสมบูรณ์ของระบบ, Favicon, ลิขสิทธิ์ และ PWA Support (Completed)
- [x] **Task 3.1:** นำเข้าตราสัญลักษณ์ทางการ มสด. (`logo_sdu.png`) ย้ายจัดเก็บใน `assets/logo_sdu.png` และสร้างไอคอน **`favicon.ico`**, **`assets/favicon.svg`**, **`assets/icon-192.png`**, **`assets/icon-512.png`** เพื่อลบข้อผิดพลาด `404 Not Found: /favicon.ico` บนเซิร์ฟเวอร์
- [x] **Task 3.2:** สร้างไฟล์ **`LICENSE`** (MIT License) อย่างเป็นทางการให้สอดคล้องกับ Badge ใน README
- [x] **Task 3.3:** พัฒนาหน้า **`404.html`** แบบ Custom ธีม SDU Blue พร้อมปุ่มพากลับสู่หน้าหลัก (`index.html`) และพอร์ทัลกลาง (`portal.html`)
- [x] **Task 3.4:** สร้างไฟล์ **`manifest.json`** และการตั้งค่า Web App Manifest เพื่อรองรับฟีเจอร์ **Add to Home Screen (PWA)** สำหรับอาจารย์และบุคลากรที่ใช้งานผ่านสมาร์ตโฟน/แท็บเล็ต
- [x] **Task 3.5:** นำตราสัญลักษณ์ทางการ มสด. ไปประดับบน Header ของ `index.html`, `staff.html` และหัวเอกสารใบขอเบิกพัสดุ (PDF Printable Form) อย่างสง่างาม

---

## ✅ Phase 4: การออกแบบฐานข้อมูลเชิงสัมพันธ์ MySQL & สคริปต์สร้างตารางอัตโนมัติ (Completed)
- [x] **Task 4.1:** ออกแบบและสร้างไฟล์ **`backend/schema.sql`** สำหรับฐานข้อมูล MySQL 8.0+ / MariaDB (`sdu_inventory`) ด้วยเอนจิน `InnoDB` และชุดอักขระ `utf8mb4_unicode_ci` ครอบคลุม 6 ตารางหลัก:
  - `departments`: ข้อมูลกลุ่มงาน/หน่วยงานภายใน สวท. 5 หน่วยงาน
  - `users`: ข้อมูลรายชื่อบุคลากรผู้มีสิทธิ์ขอเบิก (เริ่มต้นด้วยหัวหน้าหน่วยงาน 4 ท่านจาก `รายนามบุคลากร สวท.docx`)
  - `inventory_items`: ข้อมูลรายการพัสดุ 34 รายการ พร้อมคอลัมน์คำนวณ `available_pieces` (`GENERATED ALWAYS AS (on_hand_pieces - reserved_pieces) VIRTUAL`)
  - `requisitions`: ข้อมูลหัวเอกสารใบขอเบิก สถานะ และลายเซ็นดิจิทัล Base64 (`LONGTEXT`)
  - `requisition_items`: รายการพัสดุย่อยในแต่ละใบขอเบิก พร้อม Snapshot อัตราส่วนแปลงหน่วย (`pieces_per_box_snapshot`) และ FK `ON DELETE CASCADE`
  - `stock_transactions`: ประวัติความเคลื่อนไหวสต๊อก (`IN`, `OUT`, `ADJUST`, `INITIAL_MIGRATION`) สำหรับตรวจสอบย้อนหลัง (Audit Log)
- [x] **Task 4.2:** สร้างสคริปต์ **`backend/init_db.py`** สำหรับสร้างฐานข้อมูล ตาราง และนำเข้าข้อมูลตั้งต้นอัตโนมัติในคำสั่งเดียว
- [x] **Task 4.3:** สร้างไฟล์ `requirements.txt` (`PyMySQL`, `pytest`, `pytest-cov`) และอัปเดตตัวแปรสภาพแวดล้อมใน `.env` และ `.env.example` สำหรับการเชื่อมต่อ MySQL

---

## ✅ Phase 5: พัฒนา Python MySQL REST API Server & ระบบจัดการบุคลากร/พัสดุสำหรับ Staff (Completed)
- [x] **Task 5.1:** พัฒนาเซิร์ฟเวอร์ **`backend/server.py`** ให้บริการทั้ง Static Web Portals และ MySQL REST API (`/api`) ที่พอร์ต `8080`
- [x] **Task 5.2:** ติดตั้งระบบ **ACID Transactions** และ **Row-Level Locking (`SELECT ... FOR UPDATE`)** ใน `backend/server.py` เพื่อป้องกันปัญหา Race Condition เมื่อมีผู้เบิกหรือตัดสต๊อกพร้อมกัน
- [x] **Task 5.3:** เชื่อมต่อ `index.html` และ `staff.html` เข้ากับ MySQL REST API (`MYSQL_API_URL = "/api"`, `syncFromMySQLAPI()`, `postToMySQLAPI()`)
- [x] **Task 5.4:** รองรับการทำรายการครบวงจรผ่าน MySQL API: สร้างคำขอเบิก (`createRequisition`), อนุมัติเต็มจำนวน/บางส่วน (`approveRequisition`), ปฏิเสธ/ยกเลิกคืนยอดจอง (`rejectRequisition`), ลงนามรับของตัดสต๊อกจริง (`completeRequisition`), รับพัสดุเข้าคลัง (`restockItem`), ปรับยอดตรวจนับ (`adjustStock`), จัดการบุคลากร/หน่วยงาน (`saveUser`, `deleteUser`, `addDepartment`), และเพิ่ม/แก้ไข/ลบรายการพัสดุ (`saveItem`, `deleteItem`)
- [x] **Task 5.5:** สร้างระบบ **Hybrid Offline Fallback**: ทำงานบน `localStorage` ได้ทันทีหากเปิดใช้งานแบบออฟไลน์หรือยังไม่ได้รันเซิร์ฟเวอร์ MySQL

---

## ⏳ Phase 6: การทดสอบอัตโนมัติ (pytest Coverage >= 90%), CI/CD Workflow & Production Deployment
- [ ] **Task 6.1:** สร้างชุดทดสอบอัตโนมัติ **`tests/test_stock_logic.py`** ด้วย **`pytest`** ครอบคลุม:
  - การคำนวณแปลง 2 หน่วยนับ $(\text{Boxes} \times \text{Ratio}) + \text{Pieces}$
  - สูตรคำนวณสต๊อกคงเหลือจริง $\text{Available} = \text{On-Hand} - \text{Reserved}$
  - การตรวจสอบสถานะคำขอ (State Transitions: `PENDING` ➔ `APPROVED` ➔ `COMPLETED` / `REJECTED`)
  - การตรวจสอบความครบถ้วนและความถูกต้องของโครงสร้าง JSON หน่วยงาน 90 แห่ง และสคีมา MySQL (`backend/schema.sql`)
  - ตรวจสอบเกณฑ์ **Test Code Coverage >= 90%**
- [ ] **Task 6.2:** สร้าง **GitHub Actions CI Workflow (`.github/workflows/ci.yml`)** เพื่อรันการตรวจสอบ Python Test (`pytest`) และ JavaScript Syntax อัตโนมัติทุกครั้งที่มีการ Push โค้ด
- [ ] **Task 6.3:** ตรวจสอบ Relative Path ของรูปภาพและ Asset ทั้งหมดให้ถูกต้องสมบูรณ์ (`./assets/...`)
- [ ] **Task 6.4:** ทดสอบการทำงานร่วมกันระหว่างหลายอุปกรณ์ผ่านเครือข่ายองค์กรเชื่อมต่อไปยังฐานข้อมูล MySQL กลาง
