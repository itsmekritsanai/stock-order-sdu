# แผนการดำเนินงานและรายการสิ่งที่ต้องทำ (Project To-Do List)
## ระบบขอเบิกพัสดุออนไลน์ มหาวิทยาลัยสวนดุสิต (Stock Order SDU)

---

### ✅ สิ่งที่ทำเสร็จสมบูรณ์แล้ว (Completed)

#### 1. สถาปัตยกรรมและการแยกส่วนระบบ (Architecture Separation)
- [x] แยกพอร์ทัลผู้ขอเบิก (`index.html`) และพอร์ทัลเจ้าหน้าที่พัสดุ (`staff.html`) ออกจากกัน 100% เพื่อความปลอดภัย
- [x] ตัดลิงก์และสิทธิ์การอนุมัติ/จัดการสต๊อกออกจากหน้าผู้ขอเบิกทั้งหมด
- [x] ระบบตรวจสอบสิทธิ์เจ้าหน้าที่ (Staff Authentication Gate)

#### 2. ฝั่งผู้ขอเบิก (Requester Portal — `index.html`)
- [x] ช่องค้นหาหน่วยงาน/คณะแบบ Searchable Combobox ครอบคลุม 90+ หน่วยงาน มสด.
- [x] ระบบค้นหาพัสดุด้วยชื่อและคัดกรองหมวดหมู่ (Fuzzy search, ไม่ต้องจำรหัส SKU)
- [x] ระบบคำนวณ 2 หน่วยนับอัตโนมัติ (กล่อง และ ชิ้น/ซอง/ใบ/แผ่น)
- [x] แสดงยอดสต๊อกพร้อมเบิกจริงตามสูตร `Available = On-Hand - Reserved`
- [x] ตะกร้าขอเบิกพัสดุ (Slide-over Cart Drawer) พร้อมระบุวัตถุประสงค์
- [x] **ปุ่ม "📋 รายการคำขอของฉัน"** บน Header พร้อม Badge ตัวเลขนับจำนวนคำขอแบบเรียลไทม์
- [x] หน้าต่างดูรายการคำขอทั้งหมด (`#myRequisitionsModal`) พร้อมฟังก์ชันค้นหา, คัดกรองตามสถานะ, และปุ่มคัดลอกเลขที่เอกสาร
- [x] ระบบติดตามสถานะคำขอ (Self-Service Tracking) พร้อมไทม์ไลน์ 4 ขั้นตอน

#### 3. ฝั่งเจ้าหน้าที่พัสดุ (Staff Portal — `staff.html`)
- [x] แดชบอร์ดสรุปยอดสถิติพัสดุและคิวคำขอ (Pending, Approved, Completed, Low Stock)
- [x] คิวอนุมัติคำขอเบิกพัสดุ (ระบบกันจองยอดสต๊อก Reserved เมื่ออนุมัติ)
- [x] แท่นลงนามดิจิทัล (Digital E-Signature Pad) บนหน้าจอสัมผัส/เมาส์เมื่อมารับของ
- [x] ระบบตัดสต๊อกจริงอัตโนมัติ (Deduct On-Hand) เมื่อลงนามรับของเสร็จสิ้น
- [x] พิมพ์แบบฟอร์มใบเบิกพัสดุทางการ (Official PDF) ตราสัญลักษณ์มหาวิทยาลัย พร้อมประทับลายเซ็นจริง

#### 4. ดีไซน์ ประสบการณ์ผู้ใช้ และความเสถียร (UI/UX & Resilience)
- [x] ปรับปรุงดีไซน์เป็น 100% Vector SVG Icons ปราศจาก Emoji
- [x] ธีมฟอนต์ Google Fonts `Prompt` (โมเดิร์น) และ `Sarabun` (เอกสารทางการ)
- [x] เปลี่ยน Alert และ Dialog ทั้งหมดเป็น **SweetAlert2** ธีมสีน้ำเงิน มสด. (`#1e40af`)
- [x] ติดตั้ง SweetAlert2 ออฟไลน์ใน `assets/js/sweetalert2.all.min.js` (ทำงานได้แม้เน็ตหลุด)
- [x] ระบบ Real-time Cross-tab Sync ด้วย Storage Event Listeners ข้อมูลอัปเดตทันทีข้ามแท็บ

---

### 📋 สิ่งที่ต้องทำต่อไป: เชื่อมต่อ Google Sheets เป็น Database สำหรับ GitHub Pages (Next Steps)

> **เป้าหมาย:** ให้อาจารย์และเจ้าหน้าที่สามารถเปิดใช้งานผ่าน **GitHub Pages** จากคอมพิวเตอร์หรือมือถือคนละเครื่องได้ โดยข้อมูลพัสดุและคำขอเบิกทั้งหมดจะถูกจัดเก็บบน **Google Sheets** แบบเรียลไทม์

#### 📌 Phase 1: การเตรียมโครงสร้าง Google Sheets
- [ ] สร้างไฟล์ Google Sheets ใหม่ (เช่น `SDU_Inventory_Database`)
- [ ] **แผ่นงานที่ 1: `Items` (คลังพัสดุ)**
  - คอลัมน์: `id`, `name`, `category`, `unit_box_name`, `unit_piece_name`, `pieces_per_box`, `on_hand_pieces`, `reserved_pieces`, `min_alert`, `image_piece`, `image_box`
  - นำเข้าข้อมูลพัสดุตั้งต้น 58 รายการจาก `ยอดสต๊อก ตค.xlsx`
- [ ] **แผ่นงานที่ 2: `Requisitions` (ประวัติและคิวคำขอเบิก)**
  - คอลัมน์: `id`, `timestamp`, `requester`, `department`, `phone`, `purpose`, `status`, `signature_url_or_base64`, `updated_at`
- [ ] **แผ่นงานที่ 3: `Requisition_Items` (รายการพัสดุในแต่ละคำขอ)**
  - คอลัมน์: `requisition_id`, `item_id`, `item_name`, `qty_boxes`, `qty_pieces`, `total_pieces`, `unit_box`, `unit_piece`, `approved_pieces`
- [ ] **แผ่นงานที่ 4: `Departments` (หน่วยงานและคณะ)**
  - นำเข้ารายชื่อ 90+ คณะ/สำนัก/กอง จาก `departments_structured.json`

#### 📌 Phase 2: พัฒนา Google Apps Script (GAS) Web App
- [ ] เปิดเมนู Extensions -> Apps Script ใน Google Sheets
- [ ] เขียนฟังก์ชัน `doGet(e)`:
  - `action=getItems`: ดึงรายการสต๊อกพัสดุคงคลังทั้งหมด
  - `action=getRequisitions`: ดึงรายการคำขอเบิกทั้งหมด (สำหรับหน้า Staff และหน้าดูรายการคำขอ)
  - `action=trackRequisition&docNo=...`: ค้นหาสถานะคำขอตามเลขที่เอกสาร
  - `action=getDepartments`: ดึงรายชื่อหน่วยงาน
- [ ] เขียนฟังก์ชัน `doPost(e)`:
  - `action=createRequisition`: บันทึกคำขอเบิกใหม่ลงชีต `Requisitions` และ `Requisition_Items`
  - `action=approveRequisition`: เปลี่ยนสถานะเป็น APPROVED และอัปเดตยอดกันจอง (Reserved) ในชีต `Items`
  - `action=completeRequisition`: เปลี่ยนสถานะเป็น COMPLETED, บันทึกลายเซ็น, และตัดยอดสต๊อกจริง (On-Hand)
  - `action=rejectRequisition`: ปฏิเสธคำขอและคืนยอดจอง
  - `action=restockItem`: ปรับเพิ่มยอดพัสดุเข้าคลัง
- [ ] ใส่ระบบ `LockService.getScriptLock()` ป้องกัน Concurrency เมื่อมีคนกดเบิกพร้อมกันในเสี้ยววินาที
- [ ] ทำการ Deploy เป็น **Web App**:
  - Execute as: *Me (เจ้าของสคริปต์)*
  - Who has access: *Anyone (ทุกคน)* เพื่อให้เว็บที่โฮสต์บน GitHub Pages สามารถเรียก API ได้

#### 📌 Phase 3: เชื่อมต่อหน้าเว็บ Frontend เข้ากับ Google Apps Script API
- [ ] สร้างไฟล์เชื่อมต่อ API หรือเพิ่ม Service Module ใน JavaScript
  - ตั้งค่าตัวแปร `const GOOGLE_SCRIPT_API_URL = "https://script.google.com/macros/s/....../exec";`
- [ ] ปรับปรุง [index.html](file:///c:/Users/Sho/Downloads/project%20stock/index.html):
  - ดึงข้อมูลพัสดุสดจาก Google Sheets เมื่อเปิดหน้าเว็บ
  - เมื่อกดยืนยันเบิกพัสดุ ส่งข้อมูล JSON แบบ `POST` ไปที่ Google Apps Script
  - เมื่อเปิดหน้าต่าง "📋 รายการคำขอของฉัน" ดึงข้อมูลล่าสุดจาก Google Sheets
- [ ] ปรับปรุง [staff.html](file:///c:/Users/Sho/Downloads/project%20stock/staff.html):
  - โหลดรายการคำขอรออนุมัติและรายการพัสดุจาก Google Sheets
  - เมื่อกดอนุมัติ หรือลงนามรับของ ให้ส่งข้อมูลไปบันทึกตัดยอดใน Google Sheets ทันที
- [ ] จัดทำระบบ **Offline & Fallback Mechanism**:
  - หากอินเทอร์เน็ตหลุดหรือเรียก Google Apps Script ไม่ได้ ให้ fallback อ่านข้อมูลจาก `localStorage` พร้อมแจ้งเตือนผู้ใช้

#### 📌 Phase 4: Deploy ขึ้น GitHub Pages & ทดสอบข้ามอุปกรณ์
- [ ] ตรวจสอบ Path ทรัพยากรทั้งหมดให้เป็น Relative Path (`./assets/...`)
- [ ] ทดสอบสร้างคำขอจากมือถือ หรือเบราว์เซอร์คนละเครื่อง
- [ ] ตรวจสอบว่าข้อมูลใน Google Sheets อัปเดตทันที
- [ ] ตรวจสอบว่าหน้าจอเจ้าหน้าที่พัสดุที่เปิดอีกเครื่องหนึ่งมองเห็นข้อมูลคำขอใหม่
- [ ] อัปเดตเอกสาร `README.md` เพิ่มขั้นตอนการติดตั้ง Google Sheets และลิงก์ GitHub Pages ตัวจริง
