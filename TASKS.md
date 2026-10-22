# แผนงานและรายการขั้นตอนการพัฒนา (TASKS.md / ROADMAP)
### ระบบขอเบิกพัสดุและคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต (Stock Order SDU)

---

## 🎯 สรุปภาพรวมความคืบหน้า (Progress Summary)
- [x] **Phase 1: สถาปัตยกรรมหลักและการแยกระบบพอร์ทัล 100% (Completed)**
- [x] **Phase 2: ยกระดับ UI/UX, Vector Icons, SweetAlert2 และระบบรายการคำขอ (Completed)**
- [ ] **Phase 3: การออกแบบโครงสร้างฐานข้อมูล Google Sheets (Current Focus)**
- [ ] **Phase 4: พัฒนา Google Apps Script REST API & Concurrency Control**
- [ ] **Phase 5: เชื่อมต่อ Frontend เข้ากับ Google Sheets API & Offline Fallback**
- [ ] **Phase 6: Deploy ขึ้น GitHub Pages & การทดสอบข้ามอุปกรณ์ (Multi-device Testing)**

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
- [x] **Task 2.6:** เพิ่มปุ่ม **"📋 รายการคำขอของฉัน"** บน Header พร้อมตัวเลขนับจำนวนคำขอ (Count Badge)
- [x] **Task 2.7:** พัฒนาหน้าต่างป๊อปอัปดูรายการคำขอ (`#myRequisitionsModal`) พร้อมระบบค้นหา, แท็บคัดกรองสถานะ 5 สถานะ, การ์ดแสดงรายการพัสดุ และปุ่มคัดลอกเลขที่เอกสาร
- [x] **Task 2.8:** ระบบ Real-time Cross-tab Sync ด้วย Storage Event Listener อัปเดตข้อมูลข้ามแท็บทันที

---

## ⏳ Phase 3: การเตรียมโครงสร้างฐานข้อมูล Google Sheets (Next Step)
- [ ] **Task 3.1:** สร้างไฟล์ Google Sheets ฐานข้อมูลหลัก (ชื่อ `SDU_Inventory_Database`)
- [ ] **Task 3.2:** สร้างแผ่นงาน `Items` (คลังพัสดุ 58 รายการ) พร้อมคอลัมน์ `id`, `name`, `category`, `unit_box_name`, `unit_piece_name`, `pieces_per_box`, `on_hand_pieces`, `reserved_pieces`, `min_alert`, `image_piece`, `image_box`
- [ ] **Task 3.3:** สร้างแผ่นงาน `Requisitions` (ประวัติและคิวคำขอ) พร้อมคอลัมน์ `id`, `timestamp`, `requester`, `department`, `phone`, `purpose`, `status`, `signature_url_or_base64`, `updated_at`
- [ ] **Task 3.4:** สร้างแผ่นงาน `Requisition_Items` (รายการพัสดุในคำขอ) พร้อมคอลัมน์ `requisition_id`, `item_id`, `item_name`, `qty_boxes`, `qty_pieces`, `total_pieces`, `unit_box`, `unit_piece`, `approved_pieces`
- [ ] **Task 3.5:** สร้างแผ่นงาน `Departments` (รายชื่อ 90+ หน่วยงาน)

---

## ⏳ Phase 4: พัฒนา Google Apps Script REST API (Next Step)
- [ ] **Task 4.1:** สร้างสคริปต์ Google Apps Script ใน Google Sheets
- [ ] **Task 4.2:** เขียนฟังก์ชัน `doGet(e)`:
  - `action=getItems`: ส่งออก JSON รายการพัสดุและสต๊อกคงเหลือทั้งหมด
  - `action=getRequisitions`: ส่งออก JSON รายการคำขอเบิกทั้งหมด (รองรับ filter ตามสถานะ)
  - `action=trackRequisition&docNo=...`: ค้นหาประวัติและสถานะคำขอตามเลขที่เอกสาร
  - `action=getDepartments`: ส่งออก JSON รายชื่อหน่วยงาน 90+ รายการ
- [ ] **Task 4.3:** เขียนฟังก์ชัน `doPost(e)`:
  - `action=createRequisition`: บันทึกคำขอใหม่ลงชีต `Requisitions` และ `Requisition_Items`
  - `action=approveRequisition`: เปลี่ยนสถานะเป็น `APPROVED` และเพิ่มยอด `reserved_pieces`
  - `action=completeRequisition`: เปลี่ยนสถานะเป็น `COMPLETED`, บันทึกลายเซ็น Base64, และลดสต๊อกจริง `on_hand_pieces`
  - `action=rejectRequisition`: เปลี่ยนสถานะเป็น `REJECTED` และคืนยอดจอง
  - `action=restockItem`: ปรับเพิ่มยอดคงเหลือจริงในคลัง
- [ ] **Task 4.4:** ติดตั้ง `LockService.getScriptLock()` เพื่อป้องกัน Concurrency เมื่อมีคนกดเบิกพร้อมกันในเสี้ยววินาที
- [ ] **Task 4.5:** Deploy เป็น **Web App** (ตั้งค่า Execute as: *Me*, Who has access: *Anyone*) พร้อมรับ Web App URL

---

## ⏳ Phase 5: เชื่อมต่อ Frontend เข้ากับ Google Sheets API
- [ ] **Task 5.1:** เพิ่มตัวแปร `GOOGLE_SCRIPT_API_URL` ใน `index.html` และ `staff.html`
- [ ] **Task 5.2:** ปรับปรุง `index.html` ให้โหลดรายการพัสดุสดจาก Google Sheets ตอนเปิดหน้าเว็บ
- [ ] **Task 5.3:** ปรับปรุง `submitRequisition()` ใน `index.html` ให้ส่งข้อมูลผ่าน `fetch(..., {method: 'POST'})` เข้า Google Apps Script
- [ ] **Task 5.4:** ปรับปรุง `staff.html` ให้ดึงคำขอรออนุมัติ และส่งคำสั่งตัดยอดสต๊อกเข้า Google Sheets ทันที
- [ ] **Task 5.5:** สร้างระบบ **Offline Fallback**: หากเชื่อมต่อ Google Sheets ไม่ได้หรือออฟไลน์ ให้ fallback ใช้ข้อมูลใน `localStorage` พร้อมแสดง SweetAlert2 เตือนผู้ใช้

---

## ⏳ Phase 6: Deploy ขึ้น GitHub Pages & ทดสอบข้ามอุปกรณ์
- [ ] **Task 6.1:** ตรวจสอบ Relative Path ของรูปภาพและ Asset ทั้งหมดให้ถูกต้อง (`./assets/...`)
- [ ] **Task 6.2:** เปิดใช้งาน **GitHub Pages** ใน Repository Settings (เลือก Source: `main` branch)
- [ ] **Task 6.3:** ทดสอบการขอเบิกจากอุปกรณ์อื่น (มือถือ หรือคอมพิวเตอร์เครื่องอื่น)
- [ ] **Task 6.4:** ตรวจสอบความถูกต้องว่าข้อมูลคำขอเข้าสู่ Google Sheets จริง และหน้าจอของเจ้าหน้าที่พัสดุมองเห็นทันที
- [ ] **Task 6.5:** อัปเดตลิงก์ GitHub Pages ตัวจริงลงใน `README.md`
