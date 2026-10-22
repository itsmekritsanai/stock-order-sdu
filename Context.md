# Project Context

## ภาพรวมโครงการ (Project Overview)
**ระบบเบิกพัสดุและคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต**  
*(Suan Dusit University e-Inventory & Requisition System)*  
เว็บแอปพลิเคชันบริหารจัดการคลังพัสดุกลางและขอเบิกพัสดุออนไลน์ แยกสิทธิ์การทำงานระหว่าง **ผู้ขอเบิก (อาจารย์/บุคลากร)** และ **เจ้าหน้าที่คลังพัสดุ** ออกจากกันเด็ดขาด 100% พร้อมระบบลงนามรับของดิจิทัล (E-Signature) และพิมพ์ใบเบิกพัสดุทางการ (Official PDF)

---

## 1. ภาษา / Framework (Tech Stack)
* **Frontend Web Core:**
  * **HTML5:** Semantic HTML, โครงสร้างหน้าเว็บรองรับ Mobile & Desktop
  * **CSS3:** Vanilla CSS (CSS Variables, Flexbox, CSS Grid) ไม่ใช้ TailwindCSS
  * **JavaScript:** Modern Vanilla JavaScript (ES6+) แบบ Zero-Runtime Dependency
* **Generator & Automation Tools:**
  * **Python 3.x:** ใช้สำหรับคอมไพล์และสร้างโค้ดหน้าเว็บ (`generate_separated_portals.py`)
* **Libraries & UI Components:**
  * **SweetAlert2 (v11):** ป๊อปอัปแจ้งเตือนและกล่องยืนยัน สไตล์ SDU Theme (`assets/js/sweetalert2.all.min.js`) พร้อม CDN Fallback
  * **Google Fonts:** `Prompt` (สำหรับ UI ทั่วไป) และ `Sarabun` (สำหรับแบบฟอร์มเอกสารทางการ)
  * **Vector Icons:** 100% SVG Vector Icons (Stroke-based) ปราศจากการใช้ Emoji ใน UI
  * **Canvas API:** ระบบแท่นลงนามดิจิทัล (E-Signature Pad)
* **Data Storage & Sync Architecture:**
  * **ปัจจุบัน (Local Mode):** Browser `localStorage` (`inventory_items`, `inventory_requisitions`) พร้อม Real-time Cross-Tab Sync ด้วย `storage` event
  * **เป้าหมายถัดไป (Cloud Deployment):** Google Sheets API (Google Apps Script Web App REST API) สำหรับรองรับการใช้งานผ่าน GitHub Pages ข้ามอุปกรณ์

---

## 2. โครงสร้างไฟล์หลัก (File Structure)
```text
stock-order-sdu/
├── index.html                           # หน้าเว็บสำหรับผู้ขอเบิก (Requester Portal)
├── staff.html                           # หน้าเว็บสำหรับเจ้าหน้าที่พัสดุ (Staff & Admin Portal)
├── generate_separated_portals.py        # สคริปต์คอมไพล์สร้าง index.html และ staff.html
├── departments_structured.json          # ฐานข้อมูล 90+ คณะ/สำนัก/กอง มหาวิทยาลัยสวนดุสิต
├── assets/
│   ├── js/sweetalert2.all.min.js       # ไลบรารี SweetAlert2 ออฟไลน์
│   └── images/                          # ภาพถ่ายพัสดุจริง (58 รายการ)
├── Context.md                           # ข้อกำหนดบริบทและการพัฒนาโปรเจกต์
├── TODO.md                              # รายการสิ่งที่ต้องทำและ Roadmap การเชื่อมต่อ Google Sheets
├── README.md                            # คู่มือและเอกสารแนะนำโครงการ
└── system_requirements_specification.md # เอกสารวิเคราะห์ความต้องการเชิงระบบ (SRS)
```

---

## 3. รูปแบบการเขียนโค้ด (Coding Style)
* **Frontend (HTML / CSS / JavaScript):**
  * **Vanilla First:** หลีกเลี่ยง Framework ขนาดใหญ่ เน้นโค้ดที่เปิดบนเบราว์เซอร์ได้ทันทีโดยไม่ต้อง Build
  * **Design System Tokens:** อ้างอิงตัวแปร CSS เสมอ เช่น `var(--primary)`, `var(--primary-hover)`, `var(--accent)`, `var(--radius)`
  * **Indentation:** 2 spaces สำหรับ HTML, CSS, JavaScript
  * **SVG Icons:** ใช้ SVG Stroke เวกเตอร์จาก `svg_icons` เท่านั้น ห้ามใส่ Emoji ลงในเนื้องาน UI หรือปุ่ม
  * **Dialogs / Alerts:** ใช้ `Swal.fire()` (SweetAlert2) เท่านั้น **ห้ามใช้ `alert()`, `confirm()`, หรือ `prompt()` แบบดั้งเดิมของเบราว์เซอร์**
  * **Offline Capability:** ต้องมีไฟล์ Asset ภายในเครื่อง (`assets/`) ควบคู่กับ CDN Fallback เสมอ
* **Python Scripts:**
  * ยึดตามมาตรฐาน **PEP 8**
  * Indentation: 4 spaces
  * จัดการไฟล์ด้วย Context Manager (`with open(...) as f:`) และระบุ `encoding='utf-8'` เสมอ

---

## 4. การทดสอบและการควบคุมคุณภาพ (Testing & QA)
* **Python Testing:**
  * ใช้ **`pytest`**
  * กำหนดเกณฑ์ **Test Coverage >= 90%**
* **Frontend Validation:**
  * ตรวจสอบ JavaScript Syntax ความถูกต้องด้วย Node.js Parser (`new Function(code)`) ต้องได้ผลลัพธ์ผ่าน 100% ไม่มี Syntax Error
  * ตรวจสอบ HTTP Status Code 200 บน Web Server เสมอ
  * ทดสอบ Responsive Layout ให้ใช้งานได้สมบูรณ์ทั้งบนมือถือ แท็บเล็ต และคอมพิวเตอร์

---

## 5. กฎสำคัญและข้อห้าม (Crucial Rules & Constraints)
1. **ห้ามแก้ไขไฟล์ Config หลักโดยไม่ขออนุญาต:** ห้ามเปลี่ยนแปลงไฟล์ตั้งค่าระบบ หรือโครงสร้างหลักของ Repository โดยไม่ได้รับความเห็นชอบ
2. **รักษาความปลอดภัยและการแยกส่วนระบบ (100% Strict Portal Separation):**
   * ห้ามรวมหน้า `index.html` และ `staff.html` เข้าด้วยกันเด็ดขาด
   * หน้า `index.html` ต้องไม่มีฟังก์ชันอนุมัติ, การตัดสต๊อกจริง, หรือการเข้าถึงแดชบอร์ดเจ้าหน้าที่
3. **ป้องกันข้อมูลสูญหาย (Accidental Data Loss Prevention):**
   * ห้ามรันคำสั่งที่ลบหรือเขียนทับข้อมูลสำคัญโดยไม่ได้สำรองข้อมูล
4. **ความถูกต้องของการตัดสต๊อก:**
   * สต๊อกพร้อมเบิกต้องคำนวณตามสูตร: `Available = On-Hand - Reserved`
   * การอนุมัติคำขอจะต้องเพิ่มยอด `Reserved` (ยังไม่ตัด On-Hand)
   * การตัดสต๊อกจริง (`On-Hand`) จะเกิดขึ้นเมื่อผู้รับลงนามรับของในแท่นเซ็นดิจิทัล (`staff.html`) สำเร็จแล้วเท่านั้น
