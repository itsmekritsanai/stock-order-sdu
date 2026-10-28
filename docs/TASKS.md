# แผนงานและรายการขั้นตอนการพัฒนา (TASKS.md / ROADMAP)
### ระบบขอเบิกพัสดุและคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต (Stock Order SDU)

---

## 🎯 สรุปภาพรวมความคืบหน้า (Progress Summary)
- [x] **Phase 1: สถาปัตยกรรมหลักและการแยกระบบพอร์ทัล 100% (Completed)**
- [x] **Phase 2: ยกระดับ UI/UX, Vector Icons, SweetAlert2 และระบบรายการคำขอ (Completed)**
- [x] **Phase 3: ความสมบูรณ์ของระบบ, ไอคอน Favicon, ลิขสิทธิ์ และ PWA Mobile Support (Completed)**
- [x] **Phase 4: การจัดเตรียมฐานข้อมูล Google Sheets & โค้ดต้นแบบ Google Apps Script (Completed)**
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

## ✅ Phase 4: การจัดเตรียมฐานข้อมูล PostgreSQL, pgAdmin และ Docker Environment (Completed)
- [x] **Task 4.1:** สร้างไฟล์ **`docker-compose.yml`** กำหนด Service PostgreSQL 16 (Port 5432) และ pgAdmin 4 (Port 5050) สำหรับรันระบบฐานข้อมูลแบบ Containerized 1 คำสั่ง (Completed)
- [x] **Task 4.2:** สร้างสคริปต์ DDL **`backend/database/init.sql`** กำหนดตารางสัมพันธ์ `departments`, `inventory_items`, `requisitions`, `requisition_items` พร้อม CHECK Constraints และ Indexes (Completed)
- [x] **Task 4.3:** นำเข้าข้อมูลเริ่มต้น (Seed Data) รายการพัสดุ 58 รายการ และโครงสร้างหน่วยงาน มสด. อัตโนมัติ (Completed)
- [x] **Task 4.4:** รองรับตัวเลือกสำรอง Google Sheets + Google Apps Script (`backend/Code.gs`) สำหรับกรณีไม่ต้องการโฮสต์ฐานข้อมูลเอง (Completed)

---

## ⏳ Phase 5: พัฒนา REST API Controller เชื่อมต่อ PostgreSQL & ระบบ Offline Fallback
- [ ] **Task 5.1:** พัฒนา Backend API Controller (Node.js Express / Python FastAPI) เชื่อมต่อ PostgreSQL ด้วย Connection Pool
- [ ] **Task 5.2:** ติดตั้งระบบ **Row-Level Transaction Locking (`SELECT ... FOR UPDATE`)** เพื่อป้องกันสต๊อกติดลบเมื่อเบิกพร้อมกัน
- [ ] **Task 5.3:** ปรับปรุง `index.html` ให้โหลดรายการพัสดุสด และส่งคำขอเบิกผ่าน API เข้า PostgreSQL
- [ ] **Task 5.4:** ปรับปรุง `staff.html` ให้ดึงคำขอรออนุมัติ และบันทึกคำสั่งอนุมัติ/ตัดยอดสต๊อกเข้า PostgreSQL พร้อมลายเซ็นดิจิทัล
- [ ] **Task 5.5:** สร้างระบบ **Offline & Network Fallback**: หากเชื่อมต่อฐานข้อมูลไม่ได้ ให้สลับไปใช้ข้อมูลใน `localStorage` พร้อมแสดง SweetAlert2 แจ้งเตือนผู้ใช้
- [ ] **Task 5.6: ระบบบล็อกการเบิกเมื่อพัสดุหมด (Out-of-Stock Guard):**
  - ตรวจสอบยอดสต๊อกคงเหลือพร้อมเบิก ($\text{Available} = \text{On-Hand} - \text{Reserved}$) แบบเรียลไทม์
  - หาก $\text{Available} \le 0$ ให้ปิดการใช้งานปุ่มเบิกพัสดุ (`disabled`) บน `index.html` และเปลี่ยนข้อความปุ่มเป็น "สินค้าหมด"
  - ล็อกช่องกรอกจำนวน ไม่สามารถหยิบใส่ตะกร้า (Cart Drawer) ได้ และเพิ่ม Validation ตรวจสอบทั้งฝั่ง Frontend และ Backend ปฏิเสธการสร้างคำขอเมื่อสต๊อกไม่พอ
- [ ] **Task 5.7: ระบบแจ้งกำหนดการพัสดุเข้าเมื่อของหมด (Estimated Restock Date):**
  - เพิ่มฟิลด์ `expected_restock_date` ในฐานข้อมูล เพื่อบันทึกวันที่คาดว่าพัสดุล็อตใหม่จะเข้าคลัง
  - เพิ่มฟอร์มในหน้าเจ้าหน้าที่ (`staff.html`) ให้สามารถระบุ/แก้ไขวันที่พัสดุจะมาได้ทั้งแบบรายชิ้นและแบบกลุ่ม
  - แสดงป้ายแจ้งเตือนเด่นชัดบนการ์ดพัสดุในหน้าผู้ขอเบิก (`index.html`) เมื่อของหมด เช่น *"สินค้าหมด (คาดว่าของจะเข้า: 15 พ.ย. 2569)"*
- [ ] **Task 5.8: บันทึกและแสดงผลวันที่กดยืนยันจ่ายของ (Disbursement Confirmation Date):**
  - เพิ่มฟิลด์ `disbursed_at` (Timestamp) ในตาราง `requisitions`
  - ประทับเวลาและบันทึกวัน-เวลาที่จ่ายของจริงอัตโนมัติเมื่อเจ้าหน้าที่กด "ยืนยันการจ่ายของ/รับมอบสำเร็จ" (`COMPLETED`) ใน `staff.html`
  - แสดงผล "วันที่ยืนยันจ่ายของ" ในหน้าต่างประวัติคำขอของผู้เบิก (`#myRequisitionsModal`), หน้ารายละเอียดประวัติของเจ้าหน้าที่ และพิมพ์ลงบนแบบฟอร์มใบเบิกพัสดุทางการ (Official PDF Form)

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
