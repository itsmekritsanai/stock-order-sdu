# ระบบเบิกพัสดุและคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต
### (Suan Dusit University e-Inventory & Requisition System)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)](https://html.spec.whatwg.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=flat&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![CSS3](https://img.shields.io/badge/CSS3-Vanilla-1572B6?style=flat&logo=css3&logoColor=white)](https://www.w3.org/Style/CSS/)
[![University](https://img.shields.io/badge/University-Suan%20Dusit%20University-1e40af)](https://www.dusit.ac.th/)

เว็บแอปพลิเคชันระบบบริหารจัดการคลังพัสดุกลางและขอเบิกพัสดุออนไลน์ มหาวิทยาลัยสวนดุสิต ที่ได้รับการออกแบบใหม่ให้ทันสมัย รองรับการแยกส่วนการใช้งานระหว่าง **"ผู้ขอเบิก (อาจารย์/บุคลากร)"** และ **"เจ้าหน้าที่คลังพัสดุ"** ออกจากกันโดยเด็ดขาด 100% เพื่อความปลอดภัย พร้อมระบบลงนามรับของดิจิทัล (E-Signature) และพิมพ์ใบเบิกทางการ (Official PDF)

---

## สถาปัตยกรรมการแยกระบบ (Architecture & Security Separation)

ระบบแบ่งการเข้าถึงเป็น 2 พอร์ทัลอิสระ เพื่อความปลอดภัยสูงสุด:

```mermaid
graph TD
    subgraph "Public Requester Portal (index.html)"
        REQ["ผู้ขอเบิก (อาจารย์ / บุคลากร)"] --> FORM["ค้นหาคณะ/หน่วยงาน (90+ รายการ)<br/>ระบุชื่อและเบอร์โทรศัพท์"]
        FORM --> CAT["ค้นหาพัสดุ (No SKU Search)<br/>คำนวณหน่วยนับ กล่อง/ชิ้น"]
        CAT --> CART["ตะกร้าพัสดุ & ระบุวัตถุประสงค์"]
        CART --> SUBMIT["ส่งคำขอเบิก (รับรหัส REQ-XXXX)"]
        SUBMIT --> TRACK["ติดตามสถานะคำขอ (Tracking)"]
    end

    subgraph "Shared Data Synchronization (localStorage)"
        DB[("inventory_items<br/>inventory_requisitions")]
    end

    subgraph "Private Staff Portal (staff.html)"
        STAFF["เจ้าหน้าที่พัสดุ"] --> LOGIN["ระบบยืนยันตัวตน (Staff Login)"]
        LOGIN --> DASH["คิวคำขอ & บริหารสต๊อก"]
        DASH --> APPROVE["อนุมัติคำขอ (กันยอดสต๊อก Reserved)"]
        APPROVE --> ESIG["แท่นลงนามดิจิทัล (E-Signature) เมื่อมารับของ"]
        ESIG --> DEDUCT["ตัดยอดสต๊อกจริง (Deduct On-Hand)"]
        DEDUCT --> PDF["พิมพ์ใบเบิกพัสดุทางการ (PDF) พร้อมลายเซ็นจริง"]
        DASH --> STOCK["ตรวจนับ & รับพัสดุเข้าคลัง"]
    end

    SUBMIT -->|"บันทึกคำขอใหม่"| DB
    DB -->|"แสดงผลในคิวอนุมัติ"| DASH
    ESIG -->|"อัปเดตสถานะและยอดคงเหลือ"| DB
    DB -->|"อัปเดตยอดพร้อมเบิกและสถานะ"| CAT
    DB -->|"ตรวจสอบสถานะคำขอ"| TRACK
```

---

## คุณสมบัติเด่นของระบบ (Key Features)

### 1. หน้าสำหรับผู้ขอเบิก — `index.html` (Requester Portal)
* **ไม่ต้องเข้าสู่ระบบ (Zero-Friction Access):** ผู้เบิกสามารถเปิดลิงก์และใช้งานได้ทันที
* **Searchable Department Combobox:** ช่องเลือกหน่วยงาน/คณะ/โรงเรียนที่สังกัด สามารถพิมพ์ค้นหาแบบเรียลไทม์ได้ครอบคลุมทั้ง 90+ หน่วยงานของมหาวิทยาลัยสวนดุสิต
* **ค้นหาพัสดุด้วยชื่อ (No SKU Dependency):** ค้นหาด้วยชื่อพัสดุภาษาไทยแบบ Fuzzy Matching สะดวกรวดเร็ว
* **ระบบคำนวณหลายหน่วยนับ (Multi-Unit Conversion):** สามารถเลือกเบิกเป็น "กล่อง" หรือ "ชิ้น/ซอง/แผ่น" ได้ โดยระบบจะคำนวณยอดรวมและตัดสต๊อกให้อัตโนมัติ
* **แสดงสต๊อกคงเหลือจริง (Available Stock):** แสดงยอดสต๊อกที่เบิกได้จริงตามสูตร `Available = On-Hand - Reserved` ป้องกันการเบิกชนกัน
* **ตะกร้าขอเบิกและสร้างเอกสาร:** เพิ่มรายการใส่ตะกร้า ระบุวัตถุประสงค์ และสร้างเลขที่คำขอ `REQ-256910-XXXX`
* **ระบบติดตามสถานะคำขอ (Self-Service Tracking):** ผู้เบิกสามารถนำเลขที่เอกสารมาตรวจสอบสถานะคำขอได้ด้วยตัวเองตลอด 24 ชั่วโมง
* **ความปลอดภัยสูง:** ตัดแท็บและสิทธิ์การเข้าถึงของเจ้าหน้าที่พัสดุออกทั้งหมด ผู้เบิกไม่สามารถเข้ามาอนุมัติหรือปรับแก้สต๊อกได้

### 2. หน้าสำหรับเจ้าหน้าที่พัสดุ — `staff.html` (Staff & Admin Portal)
* **ระบบล็อกอินรักษาความปลอดภัย (Staff Authentication):** ป้องกันไม่ให้ผู้เบิกหรือบุคคลภายนอกเข้าถึงข้อมูลคลัง
* **แดชบอร์ดสรุปยอดสต๊อก (Dashboard Metrics):** สรุปยอดคำขอรออนุมัติ, อนุมัติแล้วรอจ่าย, จำนวนรายการคงคลัง และพัสดุใกล้หมด
* **ระบบคิวอนุมัติคำขอ (Approval Workflow):** 
  * ตรวจสอบรายละเอียดและวัตถุประสงค์
  * อนุมัติคำขอเพื่อกันยอดสต๊อก (Reserved) ป้องกันการเบิกซ้ำซ้อน
* **แท่นลงนามดิจิทัล (E-Signature Pad):**
  * เมื่อผู้ขอเบิกเดินทางมารับพัสดุที่ห้องคลัง เจ้าหน้าที่กดปุ่ม "ลงนามรับของ"
  * รองรับการเซ็นชื่อผ่านหน้าจอสัมผัส (Touchscreen), ปากกาสไตลัส, หรือเมาส์
* **ตัดสต๊อกอัตโนมัติ (Automated Inventory Deduction):** เมื่อผู้รับลงนามรับของเรียบร้อย ระบบจะตัดสต๊อกจริง (On-Hand) และคืนยอดกันจอง (Reserved) ให้ทันที
* **พิมพ์ใบเบิกพัสดุทางการ (Official PDF Printable Form):**
  * แบบฟอร์มราชการมาตรฐานตามระเบียบพัสดุ
  * ตราสัญลักษณ์มหาวิทยาลัยสวนดุสิต (Vector Seal)
  * ประทับรูปลายเซ็นดิจิทัลของผู้รับมอบลงในเอกสารโดยอัตโนมัติ
* **ระบบบริหารสต๊อกคลัง (Inventory Management):**
  * ตรวจสอบยอดสต๊อก 3 สถานะ: คงเหลือจริง (On-Hand) | ติดจอง (Reserved) | พร้อมเบิก (Available)
  * ฟังก์ชันรับพัสดุเข้าคลัง (+) และการแจ้งเตือนพัสดุต่ำกว่าเกณฑ์

### 3. มาตรฐานการออกแบบ (Design & Aesthetics)
* **100% Vector SVG Icons:** ปราศจาก Emoji โดยเปลี่ยนมาใช้ไอคอนเวกเตอร์เส้น Stroke คุณภาพสูงทั้งหมด
* **Typography:** ใช้ฟอนต์ Google Fonts `Prompt` สำหรับหน้าจอการใช้งานทั่วไป และ `Sarabun` สำหรับแบบฟอร์มเอกสารทางการ
* **Modern Color Palette:** โทนสีน้ำเงินกรมท่า มสด. (`#1e40af`) ผสมผสานสีเขียวมรกต (`#059669`) และสีเทาสะอาดตา

---

## โครงสร้างไฟล์ในโครงการ (Project Structure)

```text
stock-order-sdu/
│
├── index.html                           # หน้าเว็บสำหรับผู้ขอเบิก (Public Requester Portal)
├── staff.html                           # หน้าเว็บสำหรับเจ้าหน้าที่พัสดุ (Private Staff Portal)
│
├── assets/                              # ทรัพยากรของโครงการ
│   └── images/                          # รูปภาพพัสดุจริงสกัดจากไฟล์สต๊อก (58 รายการ)
│       ├── image1.jpeg ~ image58.jpeg
│
├── departments_structured.json          # ฐานข้อมูลรายชื่อคณะ/สำนัก/สถาบัน/โรงเรียน 90+ หน่วยงาน
├── คณะและหน่วยงาน.txt                     # ข้อมูลดิบรายชื่อหน่วยงาน มหาวิทยาลัยสวนดุสิต
├── ยอดสต๊อก ตค.xlsx                       # ข้อมูลสต๊อกพัสดุดิบตั้งต้นจาก Excel
├── system_requirements_specification.md # เอกสารวิเคราะห์ความต้องการเชิงระบบ (SRS v1.1)
│
├── generate_separated_portals.py        # สคริปต์ Python สำหรับสร้างและคอมไพล์โค้ด HTML ทั้งสองพอร์ทัล
├── .gitignore                           # การกำหนดไฟล์ที่ไม่ต้องนำขึ้น Git
└── README.md                            # เอกสารแนะนำและคู่มือการใช้งานโครงการ
```

---

## วิธีการติดตั้งและรันโครงการ (Getting Started)

ระบบถูกสร้างขึ้นโดยใช้มาตรฐาน **Pure HTML5 / Vanilla CSS / Modern JavaScript (ES6+)** จึงสามารถรันได้ทันทีโดยไม่ต้องติดตั้ง Library ภายนอกหรือ Node.js

### ขั้นตอนการรันด้วย Python Local Web Server:

1. เปิด Terminal หรือ PowerShell ในโฟลเดอร์ของโครงการ:
   ```bash
   cd "project stock"
   ```

2. สั่งรัน Local HTTP Server ผ่าน Python:
   ```bash
   python -m http.server 8080
   ```

3. เปิด Web Browser เพื่อใช้งาน:
   * **หน้าสำหรับผู้ขอเบิก:** [http://localhost:8080/index.html](http://localhost:8080/index.html)
   * **หน้าสำหรับเจ้าหน้าที่พัสดุ:** [http://localhost:8080/staff.html](http://localhost:8080/staff.html)

---

## ฐานข้อมูลและการจัดเก็บข้อมูล (Data Persistence)

ทั้งสองระบบเชื่อมต่อข้อมูลกันผ่าน Browser **`localStorage`**:
* **`inventory_items`**: ข้อมูลรายการพัสดุ ยอดคงเหลือจริง (On-Hand), ยอดติดจอง (Reserved), เกณฑ์แจ้งเตือนสต๊อกต่ำ และภาพถ่าย
* **`inventory_requisitions`**: ประวัติคำขอเบิก สถานะเอกสาร รายการที่อนุมัติ และภาพลายเซ็นดิจิทัล Base64

---

## เอกสารอ้างอิงและข้อกำหนดเชิงระบบ (SRS)

ดูรายละเอียดข้อกำหนดเชิงระบบ กฎระเบียบทางธุรกิจ และ Data Dictionary เพิ่มเติมได้ที่:
* [System Requirements Specification (SRS v1.1)](system_requirements_specification.md)

---

## ผู้จัดทำ (Author)

* **มหาวิทยาลัยสวนดุสิต (Suan Dusit University)**
* GitHub Repository: [itsmekritsanai/stock-order-sdu](https://github.com/itsmekritsanai/stock-order-sdu)
