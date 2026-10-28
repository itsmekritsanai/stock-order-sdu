# ระบบเบิกพัสดุและคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต
### (Suan Dusit University e-Inventory & Requisition System)

[![Version: 1.3.0](https://img.shields.io/badge/version-1.3.0-blue.svg)](docs/CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)](https://html.spec.whatwg.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=flat&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![CSS3](https://img.shields.io/badge/CSS3-Vanilla-1572B6?style=flat&logo=css3&logoColor=white)](https://www.w3.org/Style/CSS/)
[![SweetAlert2](https://img.shields.io/badge/SweetAlert2-v11-b02a37?style=flat)](https://sweetalert2.github.io/)
[![University](https://img.shields.io/badge/University-Suan%20Dusit%20University-1e40af)](https://www.dusit.ac.th/)


เว็บแอปพลิเคชันระบบบริหารจัดการคลังพัสดุกลางและขอเบิกพัสดุออนไลน์ มหาวิทยาลัยสวนดุสิต ที่ได้รับการออกแบบใหม่ให้ทันสมัย รองรับการแยกส่วนการใช้งานระหว่าง **"ผู้ขอเบิก (อาจารย์/บุคลากร)"** และ **"เจ้าหน้าที่คลังพัสดุ"** ออกจากกันโดยเด็ดขาด 100% เพื่อความปลอดภัย พร้อมระบบลงนามรับของดิจิทัล (E-Signature) พิมพ์ใบเบิกทางการ (Official PDF) และระบบป๊อปอัปแจ้งเตือน SweetAlert2 สวยงามระดับมืออาชีพ

---

> [!IMPORTANT]
> ### 🚨 เอกสารบังคับที่ต้องอ่านก่อนเริ่มเขียนโค้ด "ทุกครั้ง" (Strict Mandatory Reading - Read Before Every Session)
> **ข้อกำหนดเด็ดขาด:** นักพัฒนาและ AI Assistant **"ต้องอ่านและทำความเข้าใจเอกสารเหล่านี้ก่อนเริ่มลงมือเขียนหรือแก้ไขโค้ดทุกครั้งโดยไม่มีข้อยกเว้น"** เพื่อป้องกันความผิดพลาดและรักษามาตรฐานความปลอดภัย สถาปัตยกรรม และ Design System ของระบบ:
>
> 1. 🌐 **[docs/PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md) (สำคัญที่สุด - ต้องอ่านอันดับแรก):**
>    * **Single Source of Truth (SSOT):** โค้ดของ `index.html` และ `staff.html` สร้างและควบคุมผ่าน [generate_separated_portals.py](generate_separated_portals.py)
>    * **Zero-Build Runtime:** โค้ดทั้งหมดต้องเป็น Pure Semantic HTML5, Vanilla CSS3 และ Modern JavaScript (ES6+) รันแบบ Static ได้ทันทีโดยไม่ต้องผ่าน Build Tool / Node.js
>    * **Design System & CSS Tokens:** อ้างอิงตัวแปร CSS ของระบบเท่านั้น (`var(--primary)`, `var(--accent)`, `var(--neutral-*)`)
>    * **Strict No-Emoji Policy:** ห้ามใช้อีโมจิรูปภาพใน UI ทุกหน้า ให้ใช้ SVG Vector Icons (viewBox 24x24) จากชุดที่กำหนดไว้เท่านั้น
>    * **Zero-Trust Portal Isolation:** แยกสิทธิ์เด็ดขาด ห้ามใส่ลิงก์เชื่อมต่อไปยัง `staff.html` จากหน้าผู้ขอเบิก
> 2. 📄 **[docs/system_requirements_specification.md](docs/system_requirements_specification.md) (ข้อกำหนดเชิงระบบ SRS v1.1):**
>    * เข้าใจ Business Logic กระบวนการขอเบิก (Requisition Workflow), การตัดสต๊อก 3 ระดับ (*On-Hand, Reserved, Available*) และการแปลงหน่วยนับ (Multi-Unit Ratio)
> 3. 🗄️ **[docs/SCHEMA.md](docs/SCHEMA.md) & 🔌 [docs/API_SPEC.md](docs/API_SPEC.md):**
>    * รายละเอียดโครงสร้างข้อมูลใน `localStorage` (`inventory_items`, `inventory_requisitions`) และข้อกำหนด API สำหรับเชื่อมต่อ Google Apps Script Web App
> 4. 🤖 **[.github/copilot-instructions.md](.github/copilot-instructions.md) / [.cursorrules](.cursorrules):**
>    * กฎเหล็กและข้อกำหนดสไตล์การเขียนโค้ดสำหรับ AI Coding Assistant
> 5. 📋 **[docs/TASKS.md](docs/TASKS.md):**
>    * ตรวจสอบ Roadmap สถานะงานปัจจุบันและงานในเฟสถัดไปเพื่อป้องกันการทำงานซ้ำซ้อน

---

## สถาปัตยกรรมการแยกระบบ (Architecture & Security Separation)

ระบบแบ่งการเข้าถึงเป็น 2 พอร์ทัลอิสระ เพื่อความปลอดภัยสูงสุด:

```mermaid
graph TD
    subgraph "Public Requester Portal (index.html)"
        REQ["ผู้ขอเบิก (อาจารย์ / บุคลากร)"] --> FORM["ค้นหาคณะ/หน่วยงาน (90+ รายการ)<br/>ระบุชื่อและเบอร์โทรศัพท์"]
        FORM --> CAT["ค้นหาพัสดุ (No SKU Search)<br/>คำนวณหน่วยนับ กล่อง/ชิ้น"]
        CAT --> CART["ตะกร้าพัสดุ & ระบุวัตถุประสงค์"]
        CART --> SUBMIT["ส่งคำขอเบิก (SweetAlert2 Popup)"]
        SUBMIT --> MYREQS["รายการคำขอของฉัน (ดูสถานะ & คัดลอกรหัส)"]
        SUBMIT --> TRACK["ติดตามสถานะคำขอ (Tracking Timeline)"]
    end

    subgraph "Shared Data Synchronization (localStorage & Real-time Sync)"
        DB[("inventory_items<br/>inventory_requisitions<br/>(Cross-Tab Storage Sync)")]
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
    DB -->|"แจ้งเตือนคิวอนุมัติ Real-time"| DASH
    ESIG -->|"อัปเดตสถานะและยอดคงเหลือ"| DB
    DB -->|"อัปเดตยอดพร้อมเบิกและ Badge"| CAT
    DB -->|"แสดงประวัติคำขอและไทม์ไลน์"| MYREQS
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
* **ปุ่ม "รายการคำขอของฉัน" (My Requisitions):**
  * ปุ่มบนเมนูด้านบนพร้อม **ตัวเลขนับจำนวนคำขอ (Count Badge)** แสดงยอดคำขอแบบเรียลไทม์
  * หน้าต่างป๊อปอัปดูรายการคำขอทั้งหมด พร้อมช่องค้นหาเอกสาร/ผู้เบิก/พัสดุ
  * แท็บคัดกรองสถานะ: ทั้งหมด, รออนุมัติ (Pending), อนุมัติแล้ว (Approved), รับมอบสำเร็จ (Completed), ไม่อนุมัติ (Rejected)
  * ปุ่มคัดลอกเลขที่เอกสารในคลิกเดียว พร้อมปุ่มทางลัดเปิดดูไทม์ไลน์สถานะทันที
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

### 3. มาตรฐานการออกแบบและประสบการณ์ผู้ใช้ (Design & UX)
* **SweetAlert2 Modern Dialogs:** ป๊อปอัปแจ้งเตือนและหน้าต่างยืนยันทั้งหมดใช้ SweetAlert2 ตกแต่งในธีมสีน้ำเงิน มสด. (`#1e40af`) และเขียวมรกต (`#059669`)
* **Offline Asset Support:** ดาวน์โหลดไฟล์ `sweetalert2.all.min.js` เก็บไว้ใน `assets/js/` เพื่อให้ระบบทำงานได้เสถียร 100% แม้ไม่มีอินเทอร์เน็ตภายนอก พร้อมระบบ CDN Fallback อัตโนมัติ
* **100% Vector SVG Icons:** ปราศจาก Emoji โดยเปลี่ยนมาใช้ไอคอนเวกเตอร์เส้น Stroke คุณภาพสูงทั้งหมด
* **Typography:** ใช้ฟอนต์ Google Fonts `Prompt` สำหรับหน้าจอการใช้งานทั่วไป และ `Sarabun` สำหรับแบบฟอร์มเอกสารทางการ
* **Real-time Cross-Tab Synchronization:** ระบบตรวจจับการเปลี่ยนแปลงข้อมูลข้ามแท็บเบราว์เซอร์อัตโนมัติ ไม่ต้องกด Refresh หน้าเว็บ

---

## โครงสร้างไฟล์ในโครงการ (Project Structure)

```text
stock-order-sdu/
│
├── .cursorrules                         # กฎเกณฑ์สำหรับ AI Assisted Coding (Cursor)
├── PROJECT_CONTEXT.md                   # บริบทภาพรวม สถาปัตยกรรม ข้อกำหนด และกฎระเบียบ
├── TASKS.md                             # รายการขั้นตอนงานและแผนการพัฒนา (Roadmap)
├── README.md                            # คู่มือและเอกสารแนะนำโครงการ
├── LICENSE                              # สัญญาอนุญาต MIT License
├── .env.example                         # เทมเพลตตัวแปรระบบสำหรับการเชื่อมต่อ API
├── .gitignore                           # การกำหนดไฟล์ที่ไม่ต้องนำขึ้น Git
│
├── portal.html                          # ศูนย์กลางเชื่อมต่อพอร์ทัลกลาง (Gateway Hub)
├── index.html                           # หน้าเว็บสำหรับผู้ขอเบิก (Public Requester Portal)
├── staff.html                           # หน้าเว็บสำหรับเจ้าหน้าที่พัสดุ (Private Staff Portal)
├── 404.html                             # หน้าแสดงข้อผิดพลาดเมื่อไม่พบหน้าเว็บ (Custom 404)
├── manifest.json                        # การตั้งค่า Progressive Web App (PWA) ติดตั้งบนมือถือ
├── favicon.ico                          # ไอคอน Favicon แบบหลายขนาด
│
├── start.bat                            # สคริปต์ 1-Click เปิดระบบอัตโนมัติบน Windows
├── launch.py                            # สคริปต์ 1-Click รัน Local Server ด้วย Python
│
├── .github/                             # การกำหนดค่า GitHub และ AI Assistant
│   └── copilot-instructions.md          # ข้อกำหนดสำหรับ GitHub Copilot
│
├── docs/                                # โฟลเดอร์รวมเอกสารข้อมูลและคู่มือระบบ (.md)
│   ├── PROJECT_CONTEXT.md               # บริบทภาพรวม สถาปัตยกรรม ข้อกำหนด และกฎระเบียบ
│   ├── system_requirements_specification.md # เอกสารวิเคราะห์ความต้องการเชิงระบบ (SRS v1.1)
│   ├── TASKS.md                         # รายการขั้นตอนงานและแผนพัฒนา (Roadmap)
│   ├── CHANGELOG.md                     # บันทึกประวัติการเปลี่ยนแปลงตามเวอร์ชัน
│   ├── SCHEMA.md                        # รายละเอียดฐานข้อมูล Entity-Relationship & Data Types
│   └── API_SPEC.md                      # โครงสร้าง API Endpoints (Request/Response Specs)
│
├── assets/                              # ทรัพยากรของโครงการ
│   ├── logo_sdu.png                     # ตราสัญลักษณ์ทางการ มหาวิทยาลัยสวนดุสิต
│   ├── favicon.svg / favicon-*.png      # ไอคอน Favicon ขนาดต่างๆ
│   ├── icon-192.png / icon-512.png      # ไอคอนสำหรับติดตั้งเป็น PWA App
│   ├── css/                             # สไตล์ชีต CSS ของระบบ
│   │   └── styles.css                   # สไตล์ชีตหลักตกแต่งระบบ Stock Order SDU
│   ├── js/                              # ไลบรารี JavaScript ออฟไลน์
│   │   └── sweetalert2.all.min.js       # SweetAlert2 Local Asset สำหรับการทำงานออฟไลน์
│   └── images/                          # รูปภาพพัสดุจริงสกัดจากไฟล์สต๊อก (58 รายการ)
│       ├── image1.jpeg ~ image58.jpeg
│
├── departments_structured.json          # ฐานข้อมูลรายชื่อคณะ/สำนัก/สถาบัน/โรงเรียน 90+ หน่วยงาน
├── คณะและหน่วยงาน.txt                     # ข้อมูลดิบรายชื่อหน่วยงาน มหาวิทยาลัยสวนดุสิต
├── ยอดสต๊อก ตค.xlsx                       # ข้อมูลสต๊อกพัสดุดิบตั้งต้นจาก Excel
└── generate_separated_portals.py        # สคริปต์ Python สำหรับสร้างและคอมไพล์โค้ด HTML ทั้งสองพอร์ทัล
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

* **ปัจจุบัน (Local Mode):** ทั้งสองระบบเชื่อมต่อข้อมูลกันผ่าน Browser **`localStorage`** พร้อมระบบซิงค์ข้ามแท็บเรียลไทม์ (`storage` event):
  * **`inventory_items`**: ข้อมูลรายการพัสดุ ยอดคงเหลือจริง (On-Hand), ยอดติดจอง (Reserved), เกณฑ์แจ้งเตือนสต๊อกต่ำ และภาพถ่าย
  * **`inventory_requisitions`**: ประวัติคำขอเบิก สถานะเอกสาร รายการที่อนุมัติ และภาพลายเซ็นดิจิทัล Base64
* **แผนพัฒนาขั้นถัดไป (Cloud Database):** เชื่อมต่อฐานข้อมูลเข้ากับ **Google Sheets (ผ่าน Google Apps Script Web App)** เพื่อรองรับการเปิดใช้งานจริงข้ามอุปกรณ์ผ่าน **GitHub Pages** (ดูรายละเอียดใน [docs/TASKS.md](docs/TASKS.md) และ [docs/API_SPEC.md](docs/API_SPEC.md))

---

## แผนการพัฒนาและเอกสารสำคัญ (Roadmap & Documentation)

* 🤖 **[AI Development Rules (.cursorrules)](.cursorrules)** / **[.github/copilot-instructions.md](.github/copilot-instructions.md)**
* 🌐 **[ภาพรวมบริบทโครงการ (docs/PROJECT_CONTEXT.md)](docs/PROJECT_CONTEXT.md)**
* 📝 **[บันทึกประวัติการเปลี่ยนแปลง (docs/CHANGELOG.md)](docs/CHANGELOG.md)**
* 📋 **[รายการขั้นตอนงานและแผนพัฒนา (docs/TASKS.md)](docs/TASKS.md)**
* 🗄️ **[รายละเอียดโครงสร้างฐานข้อมูล (docs/SCHEMA.md)](docs/SCHEMA.md)**
* 🔌 **[โครงสร้าง API Endpoints (docs/API_SPEC.md)](docs/API_SPEC.md)**
* ⚙️ **[เทมเพลตตัวแปรระบบ (.env.example)](.env.example)**
* 📄 **[System Requirements Specification (docs/SRS v1.1)](docs/system_requirements_specification.md)**

---

## ผู้จัดทำ (Author)

* **มหาวิทยาลัยสวนดุสิต (Suan Dusit University)**
* GitHub Repository: [itsmekritsanai/stock-order-sdu](https://github.com/itsmekritsanai/stock-order-sdu)
