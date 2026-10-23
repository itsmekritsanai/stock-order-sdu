# แผนงานและรายการขั้นตอนการพัฒนา (TASKS.md / ROADMAP)
### ระบบขอเบิกพัสดุและคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต (Stock Order SDU)

---

## 🎯 สรุปภาพรวมความคืบหน้า (Progress Summary)
- [x] **Phase 1: สถาปัตยกรรมหลักและการแยกระบบพอร์ทัล 100% (Completed)**
- [x] **Phase 2: ยกระดับ UI/UX, Vector Icons, SweetAlert2 และระบบรายการคำขอ (Completed)**
- [x] **Phase 3: ความสมบูรณ์ของระบบ, ไอคอน Favicon, ลิขสิทธิ์ และ PWA Mobile Support (Completed)**
- [ ] **Phase 4: การจัดเตรียมฐานข้อมูล Google Sheets & โค้ดต้นแบบ Google Apps Script**
- [ ] **Phase 5: เชื่อมต่อ Frontend เข้ากับ Google Sheets API & ระบบ Offline Fallback**
- [ ] **Phase 6: การทดสอบอัตโนมัติ (pytest Coverage >= 90%), CI/CD Workflow & GitHub Pages Deployment**

---

## ✅ Phase 1: สถาปัตยกรรมหลักและการแยกระบบ (Completed)
- [x] **Task 1.1:** สกัดข้อมูลพัสดุจริง 58 รายการจากไฟล์ Excel `ยอดสต๊อก ตค.xlsx` และรูปภาพประกอบ
- [x] **Task 1.2:** โครงสร้างข้อมูลหน่วยงาน 90+ คณะ/โรงเรียน/กอง จาก `คณะและหน่วยงาน.txt` เป็น `departments_structured.json`
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
- [x] **Task 2.2:** ปรับระบบ Searchable Department Combobox ให้ค้นหาแบบเรียลไทม์ได้ครอบคลุมทั้ง 90+ หน่วยงาน
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
- [x] **Task 3.3:** พัฒนาหน้า **`404.html`** แบบ Custom ธีม SDU Blue พร้อมปุ่มพากลับสู่หน้าหลัก (`index.html`) รองรับกรณีพิมพ์ URL ผิดบน GitHub Pages
- [x] **Task 3.4:** สร้างไฟล์ **`manifest.json`** และการตั้งค่า Web App Manifest เพื่อรองรับฟีเจอร์ **Add to Home Screen (PWA)** สำหรับอาจารย์และบุคลากรที่ใช้งานผ่านสมาร์ตโฟน/แท็บเล็ต
- [x] **Task 3.5:** นำตราสัญลักษณ์ทางการ มสด. ไปประดับบน Header ของ `index.html`, `staff.html` และหัวเอกสารใบขอเบิกพัสดุ (PDF Printable Form) อย่างสง่างาม

---

## ⏳ Phase 4: การจัดเตรียมฐานข้อมูล Google Sheets & โค้ดต้นแบบ Google Apps Script (Backend Template)
- [ ] **Task 4.1:** สร้างไฟล์โค้ดต้นแบบ **`backend/Code.gs`** รวบรวมฟังก์ชัน Google Apps Script ทั้งหมดตามที่ระบุใน [docs/API_SPEC.md](docs/API_SPEC.md) เพื่อให้สามารถคัดลอกไปวางใน Google Sheets Script Editor แล้วกด Deploy ใช้งานได้ทันทีใน 1 นาที
- [ ] **Task 4.2:** ติดตั้งระบบ **`LockService.getScriptLock()`** ใน `Code.gs` เพื่อป้องกัน Concurrency Race Condition เมื่อมีคนกดเบิกพร้อมกันในเสี้ยววินาที
- [ ] **Task 4.3:** จัดเตรียมโครงสร้าง Google Sheets ฐานข้อมูลหลัก (ชื่อ `SDU_Inventory_Database`):
  - แผ่นงาน `Items`: คลังพัสดุ 58 รายการ พร้อมข้อมูลแปลงหน่วยนับ
  - แผ่นงาน `Requisitions`: ประวัติและคิวคำขอเบิกพัสดุ
  - แผ่นงาน `Requisition_Items`: รายการพัสดุในแต่ละคำขอ
  - แผ่นงาน `Departments`: ฐานข้อมูล 90+ หน่วยงาน
- [ ] **Task 4.4:** Deploy Google Apps Script เป็น **Web App** (Execute as: *Me*, Access: *Anyone*) พร้อมบันทึก Web App URL ลงใน `.env`

---

## ⏳ Phase 5: เชื่อมต่อ Frontend เข้ากับ Google Sheets API & ระบบ Offline Fallback
- [ ] **Task 5.1:** เพิ่มตัวแปร `GOOGLE_SCRIPT_API_URL` ใน `index.html` และ `staff.html` (อ่านจาก config หรือ runtime constant)
- [ ] **Task 5.2:** ปรับปรุง `index.html` ให้โหลดรายการพัสดุสดจาก Google Sheets API ตอนเปิดหน้าเว็บ
- [ ] **Task 5.3:** ปรับปรุงฟังก์ชัน `submitRequisition()` ใน `index.html` ให้ส่งข้อมูลคำขอผ่าน `fetch(..., {method: 'POST'})` เข้า Google Apps Script
- [ ] **Task 5.4:** ปรับปรุง `staff.html` ให้ดึงคำขอรออนุมัติ และส่งคำสั่งตัดยอดสต๊อกเข้า Google Sheets ทันที
- [ ] **Task 5.5:** สร้างระบบ **Offline & Network Fallback**: หากเชื่อมต่อ Google Sheets ไม่ได้หรือออฟไลน์ ให้สลับไปใช้ข้อมูลใน `localStorage` พร้อมแสดง SweetAlert2 แจ้งเตือนผู้ใช้

---

## ⏳ Phase 6: การทดสอบอัตโนมัติ (pytest Coverage >= 90%), CI/CD Workflow & GitHub Pages Deployment
- [ ] **Task 6.1:** สร้างชุดทดสอบอัตโนมัติ **`tests/test_stock_logic.py`** ด้วย **`pytest`** ครอบคลุม:
  - การคำนวณแปลง 2 หน่วยนับ $(\text{Boxes} \times \text{Ratio}) + \text{Pieces}$
  - สูตรคำนวณสต๊อกคงเหลือจริง $\text{Available} = \text{On-Hand} - \text{Reserved}$
  - การตรวจสอบสถานะคำขอ (State Transitions: `PENDING` ➔ `APPROVED` ➔ `COMPLETED` / `REJECTED`)
  - การตรวจสอบความครบถ้วนและความถูกต้องของโครงสร้าง JSON หน่วยงาน 90+ แห่ง
  - ตรวจสอบเกณฑ์ **Test Code Coverage >= 90%**
- [ ] **Task 6.2:** สร้าง **GitHub Actions CI Workflow (`.github/workflows/ci.yml`)** เพื่อรันการตรวจสอบ Python Test (`pytest`) และ JavaScript Syntax อัตโนมัติทุกครั้งที่มีการ Push โค้ด
- [ ] **Task 6.3:** ตรวจสอบ Relative Path ของรูปภาพและ Asset ทั้งหมดให้ถูกต้องสมบูรณ์ (`./assets/...`)
- [ ] **Task 6.4:** เปิดใช้งาน **GitHub Pages** ใน Repository Settings (เลือก Source: `main` branch)
- [ ] **Task 6.5:** ทดสอบการขอเบิกจากอุปกรณ์อื่น (มือถือ หรือคอมพิวเตอร์เครื่องอื่น) ว่าข้อมูลไหลลง Google Sheets และหน้าจอเจ้าหน้าที่มองเห็นทันที
- [ ] **Task 6.6:** อัปเดตลิงก์ GitHub Pages ตัวจริงลงใน `README.md`
