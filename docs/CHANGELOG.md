# บันทึกการเปลี่ยนแปลง (Changelog)

รูปแบบไฟล์นี้ยึดตามมาตรฐาน [Keep a Changelog](https://keepachangelog.com/th/1.1.0/) และใช้ระบบระบุเลขเวอร์ชันตาม [Semantic Versioning (SemVer 2.0.0)](https://semver.org/lang/th/).

---

## 📌 นโยบายการกำหนดเลขเวอร์ชัน (Versioning Policy)

เลขเวอร์ชันของโครงการมีรูปแบบ **`MAJOR.MINOR.PATCH`** (เช่น `1.3.0`):

1. **`MAJOR` (หลัก):** เมื่อมีการปรับโครงสร้างระบบขนาดใหญ่ที่อาจมี Breaking Changes หรือกระทบความเข้ากันได้ย้อนหลัง (เช่น การเปลี่ยนระบบฐานข้อมูลหลักทั้งหมด หรือปรับปรุงสถาปัตยกรรมความปลอดภัยระดับรากฐาน)
2. **`MINOR` (รอง):** เมื่อมีการเพิ่มคุณสมบัติ/ฟังก์ชันใหม่ (New Features) ตาม Roadmap หรือ Phase งาน โดยยังคงรักษาความเข้ากันได้ย้อนหลัง 100%
3. **`PATCH` (ย่อย):** เมื่อมีการแก้ไขข้อผิดพลาด (Bug Fixes), ปรับแต่งหน้าตา (UI/UX tweaks), ปรับปรุงความปลอดภัยย่อย หรืออัปเดตเอกสาร

> **กฎเหล็กสำหรับทีมพัฒนาและผู้ช่วย AI:**  
> ทุกครั้งที่มีการแก้ไข ปรับปรุง หรือเพิ่มเติมโค้ดในโครงการ **จะต้องปรับเลขเวอร์ชันและบันทึกรายละเอียดลงในไฟล์ `CHANGELOG.md` นี้เสมอ**

---

## [Unreleased]

### Planned (Phase 5 - 6)
- **Phase 5:** เชื่อมต่อ Frontend (`index.html`, `staff.html`) เข้ากับ Google Sheets API ผ่าน Google Apps Script Web App พร้อมระบบ Offline Fallback
- **Phase 6:** ชุดทดสอบอัตโนมัติ `pytest` ครอบคลุมคำนวณสต๊อกและแปลงหน่วย (Coverage >= 90%), CI/CD Workflow (`.github/workflows/ci.yml`) และ GitHub Pages Deployment

---

## [1.3.0] - 2026-10-24

### Added
- **Backend Google Apps Script (`backend/Code.gs`):** โค้ดต้นแบบ REST API สมบูรณ์แบบ รองรับ HTTP GET และ POST เพื่อเชื่อมต่อฐานข้อมูล Google Sheets
- **Concurrency Locking:** ติดตั้ง `LockService.getScriptLock()` พร้อม Timeout 30 วินาที ป้องกันปัญหา Race Condition เมื่อมีการขอเบิกหรือตัดสต๊อกพร้อมกัน
- **Database Schema Support:** จัดเตรียมโครงสร้าง 4 แผ่นงานหลัก (`Items`, `Requisitions`, `Requisition_Items`, `Departments`) ใน `SDU_Inventory_Database`
- **Environment Configuration:** สร้างไฟล์ `.env` และ `.env.example` สำหรับระบุค่า `VITE_GOOGLE_SCRIPT_API_URL`
- **Documentation:** เพิ่มคู่มือการ Deploy Google Apps Script ใน 1 นาที (`backend/README.md`)

### Changed
- **Form Defaults:** เคลียร์ค่าเริ่มต้นของฟอร์มผู้ขอเบิกใน `index.html` ให้เป็นค่าว่างพร้อมคำแนะนำ Placeholder ที่ชัดเจน
- **API Spec & Schema:** ปรับปรุงเอกสาร `docs/API_SPEC.md` และ `docs/SCHEMA.md` ให้ตรงกับพฤติกรรมจริงของ Google Apps Script

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
  - `index.html`: Requester Portal (สำหรับอาจารย์/บุคลากร 90+ หน่วยงาน เข้าใช้งานได้ทันทีไม่ต้องล็อกอิน)
  - `staff.html`: Staff & Warehouse Portal (สำหรับเจ้าหน้าที่พัสดุ ล็อกอินรักษาความปลอดภัย)
- **58 Stock Items:** สกัดและนำเข้าข้อมูลพัสดุจริง 58 รายการจากไฟล์ Excel `ยอดสต๊อก ตค.xlsx`
- **Department Hierarchy:** โครงสร้างข้อมูล 90+ คณะ/โรงเรียน/สถาบัน/กอง/ศูนย์ จัดเก็บใน `departments_structured.json`
- **Searchable Department Combobox:** คอมโบบ็อกซ์ค้นหาหน่วยงานแบบเรียลไทม์
- **Multi-Unit Inventory Conversion:** คำนวณแปลงหน่วยนับอัตโนมัติ (กล่อง/ห่อ และ ชิ้น/แผ่น/ซอง)
- **3-Tier Inventory Equation:** สูตรคำนวณยอดสต๊อกพร้อมเบิกจริง `Available = On-Hand - Reserved`
- **Cart Drawer:** ตะกร้าขอเบิกพัสดุแบบสไลด์ข้าง พร้อมระบุวัตถุประสงค์
- **Approval Workflow:** ระบบคิวคำขอและพิจารณาอนุมัติสำหรับเจ้าหน้าที่พัสดุ
- **Touchscreen E-Signature Pad:** แท่นลงนามลายเซ็นดิจิทัลผ่าน Canvas API รองรับหน้าจอสัมผัส สไตลัส และเมาส์
- **Official PDF Printable Form:** แบบฟอร์มใบขอเบิกพัสดุตามระเบียบมหาวิทยาลัยสวนดุสิต พร้อมตราสัญลักษณ์และประทับลายเซ็นจริง
- **Single Source of Truth (SSOT):** สคริปต์คอมไพเลอร์ `generate_separated_portals.py` รวบรวมโค้ดและสร้าง `index.html` และ `staff.html`
