# บันทึกการเปลี่ยนแปลง (Changelog)

รูปแบบไฟล์นี้ยึดตามมาตรฐาน [Keep a Changelog](https://keepachangelog.com/th/1.1.0/) และใช้ระบบระบุเลขเวอร์ชันตาม [Semantic Versioning (SemVer 2.0.0)](https://semver.org/lang/th/).

---

## 📌 นโยบายการกำหนดเลขเวอร์ชัน (Versioning Policy)

เลขเวอร์ชันของโครงการมีรูปแบบ **`MAJOR.MINOR.PATCH`** (เช่น `2.0.0`):

1. **`MAJOR` (หลัก):** เมื่อมีการปรับโครงสร้างระบบขนาดใหญ่ที่อาจมี Breaking Changes หรือกระทบความเข้ากันได้ย้อนหลัง (เช่น การเปลี่ยนระบบฐานข้อมูลหลักทั้งหมด หรือปรับปรุงสถาปัตยกรรมความปลอดภัยระดับรากฐาน)
2. **`MINOR` (รอง):** เมื่อมีการเพิ่มคุณสมบัติ/ฟังก์ชันใหม่ (New Features) ตาม Roadmap หรือ Phase งาน โดยยังคงรักษาความเข้ากันได้ย้อนหลัง 100%
3. **`PATCH` (ย่อย):** เมื่อมีการแก้ไขข้อผิดพลาด (Bug Fixes), ปรับแต่งหน้าตา (UI/UX tweaks), ปรับปรุงความปลอดภัยย่อย หรืออัปเดตเอกสาร

> **กฎเหล็กสำหรับทีมพัฒนาและผู้ช่วย AI:**  
> ทุกครั้งที่มีการแก้ไข ปรับปรุง หรือเพิ่มเติมโค้ดในโครงการ **จะต้องปรับเลขเวอร์ชันและบันทึกรายละเอียดลงในไฟล์ `CHANGELOG.md` นี้เสมอ**

---

## [Unreleased]

### Planned (Phase 6)
- **Phase 6:** ชุดทดสอบอัตโนมัติ `pytest` ครอบคลุมคำนวณสต๊อกและแปลงหน่วย (Coverage >= 90%), CI/CD Workflow (`.github/workflows/ci.yml`) และการทดสอบใช้งานจริงระดับองค์กร

---

## [2.2.0] - 2026-10-30

### Added
- **Staff Inventory Item Management (`staff.html` & `backend/server.py`):** เพิ่มฟังก์ชันให้เจ้าหน้าที่สามารถ **เพิ่มรายการพัสดุใหม่เข้าคลัง (`+ เพิ่มรายการพัสดุใหม่`)**, **แก้ไขรายละเอียดพัสดุ** และ **ลบรายการพัสดุ** ได้จากแท็บ **"สรุปยอดสต๊อกคลัง"** ในหน้า `staff.html` โดยรองรับการกำหนดหมวดหมู่, ระบบ 2 หน่วยนับ (หน่วยใหญ่/หน่วยย่อยและอัตราส่วนแปลงหน่วย), ยอดคงคลังเริ่มต้น, เกณฑ์แจ้งเตือนขั้นต่ำ และการอัปโหลดรูปภาพพัสดุจากเครื่องหรือระบุพาธไฟล์รูปภาพ พร้อมซิงค์กับฐานข้อมูล MySQL (`saveItem`, `deleteItem`) และหน้าแคตตาล็อกผู้เบิก (`index.html`) แบบเรียลไทม์

### Changed
- **Initial Users Filtered to Department Heads Only (4 ท่าน):** ปรับรายชื่อผู้ขอเบิกตั้งต้นจากไฟล์ `data/รายนามบุคลากร สวท.docx` ให้แสดงเฉพาะระดับ **หัวหน้าหน่วยงาน/กลุ่มงาน 4 ท่าน** (`นางสาววาสนา จันทร์จ่าย`, `นางสาวจีรวรรณ บุญพิทักษ์`, `นางสาวพัชราภรณ์ ขำแป้ง`, `นางสาวสินีนาฎ ลักษณะโยธิน`) ส่วนบุคลากรท่านอื่นสามารถให้เจ้าหน้าที่ (Staff) เพิ่มในภายหลังได้ผ่านแท็บ **"จัดการบุคลากร / หน่วยงาน"**

---

## [2.1.0] - 2026-10-30

### Added
- **Personnel Directory from `data/รายนามบุคลากร สวท.docx` (29 Users):** ดึงรายชื่อบุคลากรทั้ง **29 ท่าน** พร้อมตำแหน่งและกลุ่มงานต้นสังกัดจากไฟล์ `data/รายนามบุคลากร สวท.docx` มาเป็นข้อมูลผู้ขอเบิกตั้งต้นในระบบ (`index.html`, `staff.html`, และตาราง `users` ใน `backend/schema.sql`)
- **Searchable User Combobox & Auto-Fill (`index.html`):** อัปเกรดช่อง **ชื่อ-นามสกุล ผู้ขอเบิก** ในหน้าผู้เบิกให้เป็น Searchable Combobox ที่ค้นหาและเลือกชื่อบุคลากร สวท. ได้ทันที (เมื่อเลือกชื่อบุคลากรแล้ว ระบบจะเติม **กลุ่มงาน/หน่วยงานที่สังกัด** และ **เบอร์โทรศัพท์** ให้อัตโนมัติ หรือหากเลือกกลุ่มงานก่อน ระบบจะจัดกลุ่มรายชื่อบุคลากรในสังกัดนั้นขึ้นแสดงลำดับแรก)
- **Staff User & Department Management (`staff.html` & `backend/server.py`):** เพิ่มแท็บ **"จัดการบุคลากร / หน่วยงาน"** ในหน้าเจ้าหน้าที่พัสดุ (`staff.html`) ให้เจ้าหน้าที่สามารถ **เพิ่มรายชื่อบุคลากรใหม่ (Add User)**, **แก้ไขข้อมูลบุคลากร (Edit User)**, **ลบรายชื่อบุคลากร (Delete User)** และ **เพิ่มกลุ่มงาน/หน่วยงานใหม่ (Add Department)** ในภายหลังได้ตลอดเวลา พร้อมซิงค์ข้อมูลแบบเรียลไทม์ทั้งบน MySQL REST API (`getUsers`, `saveUser`, `deleteUser`, `addDepartment`) และ `localStorage`

---

## [2.0.2] - 2026-10-30

### Changed
- **Department Source Updated to `data/รายนามบุคลากร สวท.docx` (5 กลุ่มงาน/หน่วยงานหลัก สวท.):** เปลี่ยนแหล่งข้อมูลหน่วยงานสำหรับช่องเลือกหน่วยงานผู้ขอเบิกใน `scripts/generate_separated_portals.py`, `index.html`, `staff.html` และ `backend/schema.sql` ให้ดึงจากไฟล์ `data/รายนามบุคลากร สวท.docx` แทน โดยประกอบด้วย **5 หน่วยงาน/กลุ่มงานหลักภายใต้สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)**:
  1. `สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน`
  2. `กลุ่มงานส่งเสริมวิชาการ`
  3. `กลุ่มงานบริการวิชาการ`
  4. `กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ`
  5. `หน่วยงานศึกษาทั่วไปและการเรียนรู้ตลอดชีวิต`

---

## [2.0.1] - 2026-10-29

### Changed
- **Direct Department Source (`data/คณะและหน่วยงาน.txt` — 28 Main Departments):** เปลี่ยนระบบดึงรายชื่อคณะและหน่วยงานมาอ่านเฉพาะหน่วยงานหลัก `<p>` โดยตรงจากไฟล์ `data/คณะและหน่วยงาน.txt` (ตัดข้อย่อยสาขาวิชา `<li>` และรายการ `(ภาพรวม)` ออก) เหลือเฉพาะ **28 หน่วยงานหลัก** (หมวดคณะ/โรงเรียน 10 แห่ง และหมวดสถาบัน/สำนัก/ศูนย์ 18 แห่ง) ทั้งใน `index.html`, `staff.html` และ `backend/schema.sql`

### Fixed
- **Item Image Mapping & Thai Filenames (`assets/images/`):** ตรวจสอบตำแหน่งรูปภาพจริงจาก XML Drawing (`xl/drawings/drawing1.xml`) ในไฟล์ `data/ยอดสต๊อก ตค.xlsx` แก้ไขรูปภาพที่สลับกัน (เช่น แบบฟอร์มทรานสคริปไทย/อังกฤษ ป.ตรี/ป.โท และใบรับรองไทย/อังกฤษ) และตั้งชื่อไฟล์รูปภาพทั้ง **66 ไฟล์** (สำหรับ 34 รายการพัสดุ ทั้งหน่วยย่อยและหน่วยใหญ่) ใน `assets/images/` ให้ตรงกับชื่อพัสดุและหน่วยนับจริง 100% พร้อมระบบอัปเดตพาธรูปภาพใน `localStorage` อัตโนมัติ

---

## [2.0.0] - 2026-10-29

### Added
- **MySQL Relational Database Schema (`backend/schema.sql`):** สร้างสคีมาฐานข้อมูล MySQL 8.0+ / MariaDB (`sdu_inventory`) ด้วยเอนจิน `InnoDB` และชุดอักขระ `utf8mb4_unicode_ci` ประกอบด้วย 5 ตารางหลัก (`departments`, `inventory_items`, `requisitions`, `requisition_items`, `stock_transactions`) พร้อม Virtual Generated Column คำนวณ `available_pieces` อัตโนมัติ และข้อมูลตั้งต้นครบทั้ง 90 หน่วยงาน และ 34 รายการพัสดุจริง
- **Python MySQL REST API Server (`backend/server.py`):** พัฒนาเซิร์ฟเวอร์รวม (Unified Static + REST API Server บนพอร์ต `8080`) เชื่อมต่อฐานข้อมูล MySQL ผ่าน `PyMySQL` พร้อมควบคุมความถูกต้องของข้อมูลด้วย **ACID Transactions** และการล็อกแถวระดับฐานข้อมูล (`SELECT ... FOR UPDATE`)
- **1-Click Database Initializer (`backend/init_db.py`):** สคริปต์สร้างฐานข้อมูล ตาราง และนำเข้าข้อมูลตั้งต้นอัตโนมัติจากไฟล์ `backend/schema.sql`
- **Python Dependencies (`requirements.txt`):** เพิ่มไฟล์จัดการไลบรารี Python (`PyMySQL>=1.1.0`, `pytest>=8.0.0`, `pytest-cov>=5.0.0`)

### Changed
- **Database Migration to MySQL (Breaking Architecture Upgrade):** เปลี่ยนระบบฐานข้อมูลและ API หลังบ้านทั้งหมดจาก Google Sheets & Google Apps Script มาเป็น **MySQL (`sdu_inventory`) + Python REST API (`/api`)**
- **Frontend MySQL Sync (`index.html`, `staff.html`):** อัปเดตตัวสร้างพอร์ทัล `scripts/generate_separated_portals.py` ให้ซิงค์ข้อมูลผ่าน `MYSQL_API_URL` (`syncFromMySQLAPI`, `postToMySQLAPI`) พร้อมระบบ Hybrid Offline Fallback บน `localStorage`
- **Environment & Launcher Updates (`.env.example`, `scripts/launch.py`):** อัปเดตตัวแปรสภาพแวดล้อมสำหรับการเชื่อมต่อ MySQL (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`) และปรับ `scripts/launch.py` ให้รัน `backend/server.py` โดยอัตโนมัติ
- **Documentation Overhaul:** ปรับปรุงเอกสารทั้งหมด (`README.md`, `PROJECT_CONTEXT.md`, `TASKS.md`, `backend/README.md`, `docs/API_SPEC.md`, `docs/SCHEMA.md`) ให้สอดคล้องกับสถาปัตยกรรม MySQL `v2.0.0`

### Removed
- **Legacy Google Apps Script (`backend/Code.gs`):** ลบไฟล์โค้ด Google Apps Script เดิมออกทั้งหมดหลังย้ายเข้าสู่ระบบฐานข้อมูล MySQL เต็มรูปแบบ

---

## [1.4.0] - 2026-10-29

### Added
- **Full 34-Item Stock Catalog (58 Images):** อัปเดตรายการพัสดุในหน้าเว็บ (`index.html` และ `staff.html`) ให้ครบทั้ง 34 รายการพัสดุจริง (58 รูปภาพหน่วยย่อยและหน่วยกล่อง) สอดคล้องกับ `data/ยอดสต๊อก ตค.xlsx` พร้อมระบบ Auto-Merge อัปเกรดข้อมูลใน `localStorage` อัตโนมัติ
- **Cloud API Sync & Offline Fallback (Phase 5):** เชื่อมต่อ API ในทั้งสองพอร์ทัล รองรับการทำงานแบบ Hybrid Offline-First
- **Visual Tracking Timeline (`index.html`):** แสดงไทม์ไลน์สถานะคำขอ 3 ขั้นตอน (`Pending` ➔ `Approved` / `Rejected` ➔ `Completed`) พร้อมรองรับการค้นหาด้วยเลขที่เอกสารหรือชื่อผู้ขอเบิก และแสดงเหตุผลกรณีไม่อนุมัติ
- **Partial Approval & Order Cancellation (`staff.html`):** เพิ่มช่องปรับแก้ไขจำนวนอนุมัติจ่ายจริงรายรายการก่อนกดอนุมัติ และปุ่มยกเลิกคำขอที่อนุมัติแล้วเพื่อคืนยอด `reserved_pieces` กลับสู่สต๊อกพร้อมเบิก
- **4th Requisition Status Tab (`staff.html`):** เพิ่มแท็บ **"ไม่อนุมัติ / ยกเลิก (Rejected)"** ในหน้าบริหารคำขอของเจ้าหน้าที่ พร้อมตัวนับจำนวนรายการ
- **Multi-Unit Stock-In & Stock Adjustment (`staff.html`):** อัปเกรดโมดอลรับเข้าพัสดุให้ระบุได้ทั้งหน่วยใหญ่ (กล่อง/ห่อ) และหน่วยย่อย (ชิ้น/ซอง/แผ่น) และเพิ่มปุ่ม **"ปรับยอดสต๊อก (Adjustment)"** พร้อมระบุเหตุผลการตรวจนับตามเอกสาร SRS

### Fixed
- **Dynamic Dashboard Metrics (`staff.html`):** แก้ไขตัวเลข "รายการพัสดุทั้งหมดในระบบ" (`#metricTotalItems`) จากค่าคงที่ให้คำนวณตามจำนวนรายการจริงในฐานข้อมูล
- **E-Signature Blank Canvas Validation (`staff.html`):** ป้องกันการกดยืนยันจ่ายของโดยที่ยังไม่ได้เซ็นลายมือชื่อบน Canvas
- **Dynamic PDF Requisition Date (`staff.html`):** แก้ไขวันที่ขอเบิกในแบบฟอร์ม PDF ของหน้าเจ้าหน้าที่ให้ดึงจากข้อมูลคำขอจริง (`req.date`)
- **Zero-Trust 404 Page (`404.html`):** เปลี่ยนลิงก์ปุ่มรองจาก `staff.html` เป็น `portal.html` เพื่อรักษาการแยกส่วนพอร์ทัลตามกฎความปลอดภัย

---

## [1.3.1] - 2026-10-29

### Changed
- **Project Folder Structure Reorganization:** จัดระเบียบโครงสร้างโฟลเดอร์ใหม่ให้เป็นหมวดหมู่ตามมาตรฐานวิศวกรรมซอฟต์แวร์ โดยคงไฟล์หน้าเว็บหลัก (`index.html`, `staff.html`, `portal.html`, `404.html`, `manifest.json`) ไว้ที่ Root Directory เพื่อรองรับ GitHub Pages 100%:
  - **`data/`:** ย้ายไฟล์ข้อมูลหลักและข้อมูลดิบตั้งต้น (`departments_structured.json`, `คณะและหน่วยงาน.txt`, `ยอดสต๊อก ตค.xlsx`) มารวมไว้ในโฟลเดอร์ข้อมูลกลาง
  - **`scripts/`:** ย้ายสคริปต์คอมไพเลอร์และตัวรันเซิร์ฟเวอร์ (`generate_separated_portals.py`, `launch.py`, `run.bat`) เข้าสู่โฟลเดอร์สคริปต์ พร้อมปรับการอ้างอิง `PROJECT_ROOT` แบบอัตโนมัติ
  - **`docs/`:** ย้ายเอกสาร `system_requirements_specification.md` เข้าสู่โฟลเดอร์ `docs/` และแยกเอกสารรายงานการฝึกงานไว้ใน `docs/internship/` (พร้อมอัปเดต `.gitignore`)
- **Documentation & Version Sync:** อัปเดตแผนผังโครงสร้างไฟล์และลิงก์อ้างอิงใน `README.md`, `PROJECT_CONTEXT.md`, `TASKS.md`, `.cursorrules`, และ `.github/copilot-instructions.md` ให้ตรงกับโครงสร้างใหม่ พร้อมปรับเลขเวอร์ชันเป็น `1.3.1` Across-the-board

---

## [1.3.0] - 2026-10-24

### Added
- **Initial Cloud API Prototype:** สร้างต้นแบบ REST API รองรับ HTTP GET และ POST สำหรับซิงค์ข้อมูลคำขอเบิกและสต๊อกพัสดุ
- **Concurrency Locking:** ป้องกันปัญหา Race Condition เมื่อมีการขอเบิกหรือตัดสต๊อกพร้อมกัน
- **Database Schema Support:** จัดเตรียมโครงสร้างตารางหลัก (`Items`, `Requisitions`, `Requisition_Items`, `Departments`)
- **Environment Configuration:** สร้างไฟล์ `.env` และ `.env.example` สำหรับตั้งค่าการเชื่อมต่อ API

### Changed
- **Form Defaults:** เคลียร์ค่าเริ่มต้นของฟอร์มผู้ขอเบิกใน `index.html` ให้เป็นค่าว่างพร้อมคำแนะนำ Placeholder ที่ชัดเจน
- **API Spec & Schema:** ปรับปรุงเอกสาร `docs/API_SPEC.md` และ `docs/SCHEMA.md`

---

## [1.2.0] - 2026-10-23

### Added
- **SDU Branding & Visual Identity:** ติดตั้งตราสัญลักษณ์มหาวิทยาลัยสวนดุสิตทางการ (`assets/logo_sdu.png`)
- **Favicon Suite:** สร้างชุดไอคอน Favicon ครบวงจร (`favicon.ico`, `assets/favicon.svg`, `assets/icon-192.png`, `assets/icon-512.png`) ขจัดปัญหา `404 Not Found: /favicon.ico`
- **Progressive Web App (PWA):** สร้างไฟล์ `manifest.json` รองรับฟีเจอร์ Add to Home Screen บนสมาร์ตโฟนและแท็บเล็ต
- **Custom Error Page:** เพิ่มหน้า `404.html` ธีม SDU Blue พร้อมปุ่มนำทางกลับหน้าหลัก
- **Unified Portal Gateway (`portal.html`):** ประตูทางเข้าหลักรวมพอร์ทัล พร้อมปุ่มเปิด 2 แท็บพร้อมกันสำหรับทดสอบ
- **1-Click Launchers:** สคริปต์เปิดเซิร์ฟเวอร์ทดสอบในคลิกเดียว (`start.bat`, `launch.py`, `run.bat`)
- **Requester PDF Requisition:** เปิดใช้งานฟังก์ชันเปิดและพิมพ์ใบขอเบิกพัสดุ (PDF Printable Form) บนหน้าผู้ขอเบิก (`index.html`)
- **License:** สร้างไฟล์สัญญาอนุญาต `LICENSE` (MIT License)

### Security & Hardening
- **Total Portal Isolation:** ลบลิงก์เชื่อมโยงไปยังพอร์ทัลเจ้าหน้าที่ (`staff.html`) และ Portal Gateway ออกจาก Footer ของ `index.html` เพื่อความปลอดภัยแบบ Zero-Trust

### Changed
- **Project Structure:** ย้ายข้อกำหนดสำหรับ Copilot ไปยัง `.github/copilot-instructions.md` และปรับปรุง `.gitignore` ละเว้นไฟล์ฝึกงาน

---

## [1.1.0] - 2026-10-22

### Added
- **SweetAlert2 Integration:** ติดตั้งไลบรารี SweetAlert2 v11 เป็น Local Asset (`assets/js/sweetalert2.all.min.js`) รองรับ Offline 100% พร้อม CDN Fallback
- **SDU Custom SweetAlert Theme:** ปรับแต่งธีม SweetAlert2 เป็นโทนสีน้ำเงิน มสด. (`#1e40af`) มุมโค้ง 14px และฟอนต์ Prompt
- **My Requisitions Modal:** หน้าต่างตรวจสอบประวัติคำขอเบิกส่วนตัวบน `index.html` พร้อม Badge แสดงจำนวนคำขอ, ตัวกรอง 5 สถานะ และระบบค้นหา
- **One-Click Doc Copy:** ปุ่มคัดลอกเลขที่เอกสารคำขอเบิกพัสดุ (เช่น `REQ-256910-XXXX`) ลง Clipboard
- **Cross-Tab Real-time Sync:** ระบบอัปเดตข้อมูลอัตโนมัติข้ามแท็บผ่าน HTML5 `storage` event listener
- **Vector SVG Icons:** นำระบบไอคอน 100% Vector SVG (Stroke-based, 24x24) มาใช้งานแทน Emoji

### Fixed
- **Purge Native Dialogs:** กำจัดคำสั่ง `alert()`, `confirm()`, และ `prompt()` ออกจากโค้ดระบบทั้งหมด (เหลือ 0 จุด)
- **Purge Emojis:** ลบอักขระ Emoji ออกจากปุ่ม ป้ายสถานะ และกล่องข้อความทั้งหมดตามนโยบายระบบทางการ

---

## [1.0.0] - 2026-10-21

### Added
- **Initial Core Architecture:** สถาปัตยกรรมระบบเบิกพัสดุและคลังดิจิทัล มหาวิทยาลัยสวนดุสิต แยกหน้าพอร์ทัล 100%
  - `index.html`: Requester Portal (สำหรับอาจารย์/บุคลากร 90 หน่วยงาน เข้าใช้งานได้ทันทีไม่ต้องล็อกอิน)
  - `staff.html`: Staff & Warehouse Portal (สำหรับเจ้าหน้าที่พัสดุ ล็อกอินรักษาความปลอดภัย)
- **Stock Catalog & Images:** สกัดและนำเข้าข้อมูลพัสดุจริง 34 รายการ (58 รูปภาพ) จากไฟล์ Excel `ยอดสต๊อก ตค.xlsx`
- **Department Hierarchy:** โครงสร้างข้อมูล 90 คณะ/โรงเรียน/สถาบัน/กอง/ศูนย์ จัดเก็บใน `departments_structured.json`
- **Searchable Department Combobox:** คอมโบบ็อกซ์ค้นหาหน่วยงานแบบเรียลไทม์
- **Multi-Unit Inventory Conversion:** คำนวณแปลงหน่วยนับอัตโนมัติ (กล่อง/ห่อ และ ชิ้น/แผ่น/ซอง)
- **3-Tier Inventory Equation:** สูตรคำนวณยอดสต๊อกพร้อมเบิกจริง `Available = On-Hand - Reserved`
- **Cart Drawer:** ตะกร้าขอเบิกพัสดุแบบสไลด์ข้าง พร้อมระบุวัตถุประสงค์
- **Approval Workflow:** ระบบคิวคำขอและพิจารณาอนุมัติสำหรับเจ้าหน้าที่พัสดุ
- **Touchscreen E-Signature Pad:** แท่นลงนามลายเซ็นดิจิทัลผ่าน Canvas API รองรับหน้าจอสัมผัส สไตลัส และเมาส์
- **Official PDF Printable Form:** แบบฟอร์มใบขอเบิกพัสดุตามระเบียบมหาวิทยาลัยสวนดุสิต พร้อมตราสัญลักษณ์และประทับลายเซ็นจริง
- **Single Source of Truth (SSOT):** สคริปต์คอมไพเลอร์ `generate_separated_portals.py` รวบรวมโค้ดและสร้าง `index.html` และ `staff.html`
