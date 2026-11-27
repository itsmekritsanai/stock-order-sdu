# API Specification (docs/API_SPEC.md)
### ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต (v3.8.4)

---

## 1. ข้อมูลภาพรวม API (Overview & Conventions)

* **Protocol:** HTTP / HTTPS (RESTful JSON API + Binary Excel Download ให้บริการโดย [backend/server.py](../backend/server.py) เชื่อมต่อ PostgreSQL 17 หรือ MySQL)
* **Base Endpoint URL:** `http://localhost:8080/api`
* **Content-Type:** `application/json; charset=utf-8` (ยกเว้น `exportMonthlyAnalyticsExcel` ที่ส่ง `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`)
* **Request Body Limit:** สูงสุด `10 MB` (หากเกินตอบกลับ `413 PAYLOAD_TOO_LARGE`)
* **Security Headers:** ตอบกลับทุก Request พร้อม `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: same-origin`
* **Concurrency & ACID:** ใช้ `ThreadedConnectionPool` (PostgreSQL 17) ทำงานภายใต้ **ACID Transaction** และเรียงลำดับ `item_id` ก่อนล็อกแถวด้วย **`SELECT ... FOR UPDATE`** เพื่อป้องกัน Race Condition และ Deadlock

### ระบบยืนยันตัวตนและสิทธิ์การเข้าถึง (Authentication & RBAC)
* **Token Format:** HMAC-SHA256 Signed Token (อายุ 12 ชั่วโมง) แยก 2 ประเภท:
  * **`requester_token`** (ได้รับจาก `loginRequester` หรือ `loginStaff` สำหรับ Cross-Portal SSO)
  * **`staff_token`** (ได้รับจาก `loginStaff` หรือ `loginRequester` เมื่อผู้ใช้มีสิทธิ์ `STAFF`/`HEAD`/`ADMIN`)
* **การส่ง Token ใน Request Header:**
  * `Authorization: Bearer <token>` (รองรับ `X-Staff-Token` และ `X-Requester-Token` ด้วย)
  * `X-Staff-Role: STAFF | HEAD | ADMIN` (อนุญาตเฉพาะบัญชี `ADMIN` สำหรับสลับมุมมองสิทธิ์ชั่วคราว)
* **ตารางสิทธิ์ RBAC สำหรับ `STAFF_ACTIONS` (`check_staff_role_permission`):**
  * **`ADMIN`:** ทำได้ทุกคำสั่ง
  * **`STAFF`:** ทำได้ทุกคำสั่ง **ยกเว้น** `approveRequisition`, `deleteUser`, `deleteDepartment`
  * **`HEAD`:** ทำได้เฉพาะ `approveRequisition` และ `rejectRequisition` (ในกลุ่ม POST Staff Actions) + ดูรายงานวิเคราะห์ (`getMonthlyAnalytics`, `exportMonthlyAnalyticsExcel`, `getItemTransactions`)
  * หากไม่มี Token หรือ Token หมดอายุ -> `401 UNAUTHORIZED` / หากสิทธิ์ไม่ตรงบทบาท -> `403 FORBIDDEN_ROLE`
* **โหมดทดสอบ (`AUTH_BYPASS`):** ค่าเริ่มต้นบน Production คือ `AUTH_BYPASS="false"` (บังคับ Login เสมอ)

---

## 2. สรุปรายการ Endpoints (Summary Table)

| Method | Action | ระดับสิทธิ์การเข้าถึง | วัตถุประสงค์ |
| :---: | :--- | :--- | :--- |
| `GET` | `health` / `ping` | สาธารณะ | ตรวจสอบสถานะ API, เวอร์ชัน, การเชื่อมต่อฐานข้อมูล, และ `authBypass` |
| `GET` | `getItems` | สาธารณะ | ดึงรายการพัสดุคงคลัง (พร้อม `monthly_limit`, `last_unit_price`, `last_restocked_at`) |
| `GET` | `getDepartments` | สาธารณะ | ดึงรายชื่อกลุ่มงาน/หน่วยงานภายใน สวท. |
| `GET` | `trackRequisition` | สาธารณะ | ติดตามสถานะคำขอรายเอกสาร (ค้นหาแบบตรงเลขที่ `docNo` เท่านั้น) |
| `GET` | `getRequisitions` | ต้องล็อกอิน (Requester/Staff) | ดึงประวัติและคิวคำขอเบิก (รองรับตัวกรอง `status`, `month`, `search`) |
| `GET` | `getUsers` | ต้องล็อกอิน (Requester/Staff) | ดึงทำเนียบบุคลากรและบทบาท (ไม่ส่งฟิลด์ `password`) |
| `GET` | `getQuotas` | ต้องล็อกอิน (Requester/Staff) | ดึงรายการกฎโควตารายเดือนทั้งหมด (`USER` / `DEPT`) |
| `GET` | `getMonthlyAnalytics` | เจ้าหน้าที่ (`STAFF`/`HEAD`/`ADMIN`) | ดึงสถิติรายเดือน, Top/Least 5, รายบุคคล, ยอดซื้อเข้า, และรายการคำขอทั้งเดือน |
| `GET` | `exportMonthlyAnalyticsExcel` | เจ้าหน้าที่ (`STAFF`/`HEAD`/`ADMIN`) | ดาวน์โหลดรายงานสถิติประจำเดือนเป็นไฟล์ Excel แท้ `.xlsx` (6 ชีต) |
| `GET` | `getItemTransactions` | เจ้าหน้าที่ (`STAFF`/`HEAD`/`ADMIN`) | ดึงประวัติความเคลื่อนไหวสต๊อก (`IN`, `OUT`, `ADJUST`) พร้อมราคาซื้อเข้า |
| `POST` | `loginRequester` | สาธารณะ | เข้าสู่ระบบผู้ขอเบิก (คืน `token` และคืน `staff_token` ด้วยหากมีสิทธิ์สูงกว่า) |
| `POST` | `loginStaff` | สาธารณะ | เข้าสู่ระบบเจ้าหน้าที่/หัวหน้า/แอดมิน (คืนทั้ง `token` และ `requester_token` สำหรับ SSO) |
| `POST` | `createRequisition` | ต้องล็อกอิน (Requester/Staff) | ส่งคำขอเบิกพัสดุใหม่ (รวมยอดซ้ำ, ตรวจสต๊อก, ตรวจโควตารายบุคคล + กลุ่มงาน) |
| `POST` | `verifyRequisition` | `STAFF` / `ADMIN` | คัดกรองคำขอเบื้องต้น (`PENDING` -> `VERIFIED`) เพื่อส่งต่อหัวหน้า |
| `POST` | `approveRequisition` | `HEAD` / `ADMIN` | อนุมัติคำขอขั้นสุดท้าย (`VERIFIED` -> `APPROVED`) และล็อก `reserved_pieces` |
| `POST` | `completeRequisition` | `STAFF` / `ADMIN` | บันทึกลายเซ็น/ยืนยันส่งมอบ และตัดสต๊อกจริง (`APPROVED` -> `COMPLETED`) |
| `POST` | `rejectRequisition` | `STAFF` / `HEAD` / `ADMIN` | ปฏิเสธ/ยกเลิกคำขอ พร้อมคืนยอดจองหากเคย `APPROVED` |
| `POST` | `restockItem` | `STAFF` / `ADMIN` | บันทึกรับพัสดุเข้าคลัง พร้อมคำนวณราคาต่อหน่วยและยอดเงินซื้อเข้า |
| `POST` | `adjustStock` | `STAFF` / `ADMIN` | ปรับปรุงยอดสต๊อกจริงจากการตรวจนับ |
| `POST` | `saveItem` | `STAFF` / `ADMIN` | เพิ่มหรือแก้ไขรายการพัสดุ (หากเพิ่มใหม่และสต๊อก > 0 จะบันทึก `INITIAL_STOCK`) |
| `POST` | `deleteItem` | `STAFF` / `ADMIN` | ลบรายการพัสดุแบบ Soft Delete (`is_active = 0`) |
| `POST` | `saveUser` | `STAFF` / `ADMIN` | เพิ่มหรือแก้ไขข้อมูลบุคลากร (แฮชรหัสผ่านด้วย PBKDF2-HMAC-SHA256) |
| `POST` | `deleteUser` | `ADMIN` เท่านั้น | ลบบุคลากรแบบ Soft Delete (`is_active = 0`) |
| `POST` | `addDepartment` | `STAFF` / `ADMIN` | เพิ่มกลุ่มงาน/หน่วยงานใหม่เข้าสู่ตาราง `departments` |
| `POST` | `updateDepartment` | `STAFF` / `ADMIN` | แก้ไขชื่อกลุ่มงาน (อัปเดตสังกัดใน `users` และ `quota_rules` อัตโนมัติ) |
| `POST` | `deleteDepartment` | `ADMIN` เท่านั้น | ลบกลุ่มงานแบบ Soft Delete (ปฏิเสธหากยังมีบุคลากรสังกัดอยู่) |
| `POST` | `saveQuota` | `STAFF` / `ADMIN` | เพิ่มหรือแก้ไขกฎโควตารายเดือน (`USER` / `DEPT`, รายพัสดุหรือทุกพัสดุ) |
| `POST` | `deleteQuota` | `STAFF` / `ADMIN` | ลบกฎโควตารายเดือน |

---

## 3. รายละเอียด Endpoints แบบเจาะลึก (Endpoint Details)

### 3.1 `GET /api?action=health`
ตรวจสอบสถานะความพร้อมของ REST API และการเชื่อมต่อฐานข้อมูล

* **Response Success (200 OK):**
```json
{
  "status": "success",
  "healthy": true,
  "message": "ระบบจัดการวัสดุสำนักงานออนไลน์ (PostgreSQL 17) REST API is operational.",
  "version": "3.8.4",
  "database": "PostgreSQL 17",
  "db_name": "sdu_inventory",
  "authBypass": false
}
```

---

### 3.2 `GET /api?action=getItems`
ดึงรายการพัสดุที่เปิดใช้งานทั้งหมด พร้อมยอดสต๊อก 3 ระดับ โควตามาตรฐาน และราคาซื้อล่าสุด

* **Query Parameters:** `action=getItems`, `category` (ตัวเลือก เช่น `ซองเอกสาร` หรือ `ALL`)
* **Response Success (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 3,
      "name": "กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)",
      "category": "กระดาษและแบบฟอร์ม",
      "is_multi_unit": true,
      "unit_box_name": "กล่อง",
      "unit_piece_name": "ใบ",
      "pieces_per_box": 2000,
      "on_hand_pieces": 32000,
      "reserved_pieces": 0,
      "available_pieces": 32000,
      "min_alert": 5000,
      "monthly_limit": 0,
      "last_unit_price": 0.0,
      "last_restocked_at": "",
      "image_piece": "assets/images/กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ) ใบ.jpeg",
      "image_box": "assets/images/กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ) กล่อง.jpeg"
    }
  ],
  "total": 34
}
```

---

### 3.3 `GET /api?action=getRequisitions`
ดึงรายการคำขอเบิกพัสดุพร้อมรายการย่อย (ต้องส่ง `Authorization: Bearer <requester_token|staff_token>`)

* **Query Parameters:**
  * `status` (ตัวเลือก): `ALL`, `PENDING`, `VERIFIED`, `APPROVED`, `COMPLETED`, `REJECTED`
  * `month` (ตัวเลือก): `YYYY-MM` เช่น `2026-11` หรือ `ALL` (ใช้ SARGable Range Query บน `created_at`)
  * `search` (ตัวเลือก): ค้นหาจากเลขที่เอกสาร, ผู้ขอเบิก, กลุ่มงาน, หรือวัตถุประสงค์

---

### 3.4 `GET /api?action=trackRequisition&docNo={DOC_NO}`
ติดตามสถานะคำขอรายเอกสาร (จำกัดเฉพาะการค้นหาด้วยเลขที่เอกสาร `docNo` ที่ตรงตัว เพื่อป้องกันการเปิดเผยข้อมูลบุคคล)

* **Response Success (200 OK):**
```json
{
  "status": "success",
  "found": true,
  "data": {
    "id": "REQ-256911-0001",
    "date": "25 พ.ย. 2569 10:15 น.",
    "requester": "สมชัย จารุธนกิจพานิช",
    "dept": "กลุ่มงานเคาน์เตอร์บริการ",
    "phone": "5174",
    "purpose": "ใช้สำหรับการให้บริการนักศึกษา",
    "status": "APPROVED",
    "verified_by": "จุฑาธิป ปั้นทอง",
    "verified_date": "25 พ.ย. 2569 10:30 น.",
    "approved_by": "จิตราพร จันทรกูล",
    "approved_date": "25 พ.ย. 2569 11:00 น.",
    "items": [
      {
        "itemId": 7,
        "name": "กระดาษลายเส้น (ห่อละ 500 แผ่น)",
        "qtyBoxes": 1,
        "qtyPieces": 0,
        "totalPieces": 500,
        "unitBox": "ห่อ",
        "unitPiece": "แผ่น",
        "approvedPieces": 500
      }
    ]
  }
}
```

---

### 3.5 `GET /api?action=getQuotas`
ดึงกฎโควตารายเดือนทั้งหมด (ต้องล็อกอิน)

* **Response Success (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "targetType": "USER",
      "targetKey": "สมชัย จารุธนกิจพานิช",
      "itemId": 7,
      "itemName": "กระดาษลายเส้น (ห่อละ 500 แผ่น)",
      "unitPiece": "แผ่น",
      "monthlyLimit": 1000,
      "note": "โควตาประจำเดือน",
      "updatedBy": "ผู้ดูแลระบบคลังพัสดุ (Admin)",
      "updatedAt": "2026-11-25 10:00:00"
    }
  ],
  "total": 1
}
```

---

### 3.6 `GET /api?action=getItemTransactions&itemId={ID}`
ดึงประวัติความเคลื่อนไหวสต๊อกล่าสุด (สูงสุด 200 รายการ; หากไม่ส่ง `itemId` จะดึงทุกพัสดุ) — **Staff Token เท่านั้น**

* **Response Success (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 5,
      "itemId": 7,
      "itemName": "กระดาษลายเส้น (ห่อละ 500 แผ่น)",
      "unitPiece": "แผ่น",
      "transactionType": "IN",
      "changePieces": 500,
      "balanceAfter": 23500,
      "unitPrice": 0.45,
      "totalCost": 225.0,
      "referenceType": "STOCK_IN",
      "referenceId": "",
      "reason": "รับพัสดุเข้าคลัง (PO-2569-01)",
      "recordedBy": "จุฑาธิป ปั้นทอง",
      "createdAt": "2026-11-25 10:30:00",
      "formattedDate": "25 พ.ย. 2569 10:30 น."
    }
  ],
  "total": 1
}
```

---

### 3.7 `GET /api?action=getMonthlyAnalytics&month={YYYY-MM}`
ดึงข้อมูลรายงานวิเคราะห์และสถิติการเบิกจ่ายประจำเดือน (รองรับ `month=YYYY-MM` หรือ `month=ALL`) — **Staff Token เท่านั้น**

* **Response Success (200 OK):**
```json
{
  "status": "success",
  "data": {
    "month": "2026-11",
    "thaiMonth": "พฤศจิกายน 2569",
    "totalRequisitions": 15,
    "totalPending": 2,
    "totalVerified": 1,
    "totalApproved": 1,
    "totalCompleted": 10,
    "totalRejected": 1,
    "totalPiecesRequested": 4800,
    "totalPiecesApproved": 4500,
    "totalPurchaseCost": 12500.0,
    "totalRestockCount": 3,
    "totalRestockedPieces": 5000,
    "topItems": [
      {
        "itemId": 3,
        "name": "กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)",
        "category": "กระดาษและแบบฟอร์ม",
        "unitPiece": "ใบ",
        "totalRequested": 2000,
        "totalApproved": 2000,
        "reqCount": 4
      }
    ],
    "leastItems": [],
    "allItemUsage": [],
    "personUsage": [],
    "purchaseSummary": [],
    "purchaseTransactions": [],
    "monthRequisitions": [
      {
        "id": "REQ-256911-0001",
        "date": "25 พ.ย. 2569 10:15 น.",
        "requester": "สมชัย จารุธนกิจพานิช",
        "dept": "กลุ่มงานเคาน์เตอร์บริการ",
        "status": "COMPLETED",
        "items": [],
        "totalPieces": 500,
        "approvedPieces": 500
      }
    ]
  }
}
```

---

### 3.8 `GET /api?action=exportMonthlyAnalyticsExcel&month={YYYY-MM}`
ส่งออกไฟล์ Excel แท้ (`.xlsx`) ที่สร้างด้วยโมดูล Zero-Dependency [backend/excel_export.py](../backend/excel_export.py) ประกอบด้วย **6 ชีต**:
1. `ภาพรวมประจำเดือน`
2. `สรุปรายบุคคล`
3. `สรุปทุกพัสดุ`
4. `รายละเอียดคำขอเบิก`
5. `สรุปยอดซื้อเข้า`
6. `ประวัติซื้อเข้า`

* **Headers:** `Authorization: Bearer <staff_token>`
* **Response:** Binary `.xlsx` (`Content-Disposition: attachment; filename="SDU_Monthly_Analytics_<month>.xlsx"`)

---

### 3.9 `POST /api` — เข้าสู่ระบบผู้ขอเบิก (`loginRequester`)
ตรวจสอบ Username (ไม่คำนึงตัวพิมพ์เล็ก-ใหญ่) และรหัสผ่านเฉพาะบุคคล (PBKDF2) จากตาราง `users`

* **Request Body:**
```json
{
  "action": "loginRequester",
  "payload": {
    "username": "somchai_jar",
    "password": "<password>"
  }
}
```
* **Response Success (200 OK):**
```json
{
  "status": "success",
  "message": "เข้าสู่ระบบสำเร็จ",
  "token": "<requester_hmac_token>",
  "user": {
    "id": 1,
    "name": "สมชัย จารุธนกิจพานิช",
    "username": "somchai_jar",
    "role": "REQUESTER",
    "position": "กลุ่มงานเคาน์เตอร์บริการ",
    "dept": "กลุ่มงานเคาน์เตอร์บริการ",
    "phone": "5174"
  }
}
```
*(หากบัญชีมีสิทธิ์ `STAFF`, `HEAD`, หรือ `ADMIN` ระบบจะแนบ `"staff_token"` และ `"staff_role"` เพื่อรองรับ Cross-Portal SSO ด้วย)*

---

### 3.10 `POST /api` — เข้าสู่ระบบเจ้าหน้าที่/หัวหน้า/ผู้ดูแล (`loginStaff`)
ตรวจสอบบัญชีจากค่า Config หรือตาราง `users` ที่มีสิทธิ์ `STAFF`/`HEAD`/`ADMIN` และออกโทเค็นคู่ขนานสำหรับทั้ง 2 พอร์ทัล

* **Request Body:**
```json
{
  "action": "loginStaff",
  "payload": {
    "username": "jittraporn_cha",
    "password": "<password>"
  }
}
```
* **Response Success (200 OK):**
```json
{
  "status": "success",
  "message": "เข้าสู่ระบบสำเร็จ (หัวหน้าหน่วยงาน (ผู้อนุมัติขั้นสุดท้าย))",
  "token": "<staff_hmac_token>",
  "requester_token": "<requester_hmac_token>",
  "requester_user": {
    "id": 2,
    "name": "จิตราพร จันทรกูล",
    "username": "jittraporn_cha",
    "role": "HEAD",
    "position": "รองผู้อำนวยการ",
    "dept": "สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน",
    "phone": "5235"
  },
  "username": "jittraporn_cha",
  "name": "จิตราพร จันทรกูล",
  "role": "HEAD",
  "active_role": "HEAD",
  "role_label": "หัวหน้าหน่วยงาน (ผู้อนุมัติขั้นสุดท้าย)"
}
```

---

### 3.11 `POST /api` — ส่งคำขอเบิกพัสดุ (`createRequisition`)
สร้างใบคำขอเบิกใหม่ในสถานะ `PENDING` โดยฝั่งเซิร์ฟเวอร์จะรวมยอดพัสดุหากมี `itemId` ซ้ำ, ตรวจสอบสต๊อกพร้อมเบิก (`Available`), และตรวจสอบโควตารายเดือนทั้งระดับบุคคล (`QUOTA_EXCEEDED`) และระดับกลุ่มงาน (`DEPT_QUOTA_EXCEEDED`)

* **Headers:** `Authorization: Bearer <requester_token|staff_token>`
* **Request Body:**
```json
{
  "action": "createRequisition",
  "payload": {
    "requester": "สมชัย จารุธนกิจพานิช",
    "dept": "กลุ่มงานเคาน์เตอร์บริการ",
    "phone": "5174",
    "purpose": "ใช้สำหรับให้บริการนักศึกษา",
    "items": [
      {
        "itemId": 7,
        "name": "กระดาษลายเส้น (ห่อละ 500 แผ่น)",
        "qtyBoxes": 1,
        "qtyPieces": 0,
        "totalPieces": 500,
        "unitBox": "ห่อ",
        "unitPiece": "แผ่น"
      }
    ]
  }
}
```
* **Response Error Codes:** `INSUFFICIENT_STOCK`, `QUOTA_EXCEEDED`, `DEPT_QUOTA_EXCEEDED`, `UNAUTHORIZED`

---

### 3.12 `POST /api` — คัดกรองและส่งต่อหัวหน้า (`verifyRequisition`)
เจ้าหน้าที่พัสดุ (`STAFF`/`ADMIN`) ตรวจสอบรายการ ปรับจำนวนเสนอเบิก (ถ้ามี) และเปลี่ยนสถานะ `PENDING` -> `VERIFIED`

* **Headers:** `Authorization: Bearer <staff_token>`
* **Request Body:**
```json
{
  "action": "verifyRequisition",
  "payload": {
    "docNo": "REQ-256911-0001",
    "verifiedBy": "จุฑาธิป ปั้นทอง",
    "items": [
      { "itemId": 7, "approvedPieces": 500 }
    ]
  }
}
```

---

### 3.13 `POST /api` — อนุมัติคำขอขั้นสุดท้าย (`approveRequisition`)
หัวหน้าหน่วยงาน (`HEAD`/`ADMIN`) อนุมัติคำขอ (`VERIFIED` -> `APPROVED`) และล็อกยอดติดจอง `reserved_pieces += approved_pieces` ภายใต้ `SELECT ... FOR UPDATE`

* **Headers:** `Authorization: Bearer <staff_token>`
* **Request Body:**
```json
{
  "action": "approveRequisition",
  "payload": {
    "docNo": "REQ-256911-0001",
    "approvedBy": "จิตราพร จันทรกูล",
    "items": [
      { "itemId": 7, "approvedPieces": 500 }
    ]
  }
}
```

---

### 3.14 `POST /api` — บันทึกจ่ายพัสดุและตัดสต๊อกจริง (`completeRequisition`)
เจ้าหน้าที่ (`STAFF`/`ADMIN`) ส่งมอบพัสดุ เปลี่ยนสถานะ `APPROVED` -> `COMPLETED`, ตัด `on_hand_pieces` และ `reserved_pieces`, และบันทึก `OUT` ลง `stock_transactions`

* **Headers:** `Authorization: Bearer <staff_token>`
* **Request Body:**
```json
{
  "action": "completeRequisition",
  "payload": {
    "docNo": "REQ-256911-0001",
    "signature": "data:image/png;base64,iVBORw0KGgo..."
  }
}
```

---

### 3.15 `POST /api` — ปฏิเสธ/ยกเลิกคำขอ (`rejectRequisition`)
เปลี่ยนสถานะเป็น `REJECTED` พร้อมบันทึก `reject_reason` และคืนยอดจอง `reserved_pieces` หากคำขอเคยอยู่ในสถานะ `APPROVED`

* **Headers:** `Authorization: Bearer <staff_token>` (`STAFF`/`HEAD`/`ADMIN`)
* **Request Body:**
```json
{
  "action": "rejectRequisition",
  "payload": {
    "docNo": "REQ-256911-0001",
    "reason": "พัสดุสำรองสำหรับช่วงสอบ กรุณาติดต่อห้องคลัง"
  }
}
```

---

### 3.16 `POST /api` — รับพัสดุเข้าคลัง (`restockItem`)
เพิ่มยอด `on_hand_pieces`, อัปเดต `last_restocked_at` และ `last_unit_price` (หากระบุราคา), และบันทึก `IN` พร้อมต้นทุนลง `stock_transactions`

* **Headers:** `Authorization: Bearer <staff_token>` (`STAFF`/`ADMIN`)
* **Request Body:**
```json
{
  "action": "restockItem",
  "payload": {
    "itemId": 7,
    "quantityPieces": 1000,
    "unitPrice": 0.45,
    "totalCost": 450.0,
    "note": "รับพัสดุเข้าคลังตามใบสั่งซื้อ PO-2569-12",
    "recordedBy": "จุฑาธิป ปั้นทอง"
  }
}
```
*(หากส่งเพียง `totalCost` ระบบจะคำนวณ `unit_price = round(totalCost / quantityPieces, 2)` ให้อัตโนมัติ หรือส่งเพียง `unitPrice` ระบบจะคำนวณ `total_cost` ให้อัตโนมัติ)*

---

### 3.17 `POST /api` — ปรับยอดสต๊อกจริง (`adjustStock`)
ปรับ `on_hand_pieces` ตามยอดตรวจนับจริงและบันทึกผลต่าง (`ADJUST`) ลง `stock_transactions`

* **Headers:** `Authorization: Bearer <staff_token>` (`STAFF`/`ADMIN`)
* **Request Body:**
```json
{
  "action": "adjustStock",
  "payload": {
    "itemId": 7,
    "newQty": 22950,
    "reason": "ตรวจนับสต๊อกประจำเดือน พบชำรุด 50 แผ่น",
    "recordedBy": "จุฑาธิป ปั้นทอง"
  }
}
```

---

### 3.18 `POST /api` — จัดการรายการพัสดุ (`saveItem` / `deleteItem`)
* **`saveItem`** (`STAFF`/`ADMIN`): ส่ง `id: null` เพื่อเพิ่มพัสดุใหม่ (ใช้ `SERIAL RETURNING id` และบันทึก `INITIAL_STOCK` อัตโนมัติเมื่อ `on_hand_pieces > 0`) หรือส่ง `id` เดิมเพื่อแก้ไขข้อมูล โควตามาตรฐาน เกณฑ์เตือน และรูปภาพ
* **`deleteItem`** (`STAFF`/`ADMIN`): ส่ง `{ "action": "deleteItem", "id": 35 }` เพื่อ Soft Delete (`is_active = 0`)

---

### 3.19 `POST /api` — จัดการบุคลากร (`saveUser` / `deleteUser`)
* **`saveUser`** (`STAFF`/`ADMIN`): เพิ่มหรือแก้ไขข้อมูลบุคลากร (`name`, `username`, `password`, `role`, `position`, `dept`, `phone`) โดยเข้ารหัสรหัสผ่านด้วย PBKDF2-HMAC-SHA256 ก่อนบันทึก
* **`deleteUser`** (`ADMIN` เท่านั้น): ส่ง `{ "action": "deleteUser", "id": 16 }` เพื่อ Soft Delete (`is_active = 0`)

---

### 3.20 `POST /api` — จัดการกลุ่มงาน/หน่วยงาน (`addDepartment` / `updateDepartment` / `deleteDepartment`)
* **`addDepartment`** (`STAFF`/`ADMIN`): เพิ่มกลุ่มงานใหม่เข้าสู่ `departments`
* **`updateDepartment`** (`STAFF`/`ADMIN`): แก้ไขชื่อกลุ่มงาน (`id`, `name`) พร้อมอัปเดตชื่อสังกัดของบุคลากรใน `users` และกฎโควตาใน `quota_rules` ที่ผูกอยู่โดยอัตโนมัติ
* **`deleteDepartment`** (`ADMIN` เท่านั้น): Soft Delete กลุ่มงาน (ปฏิเสธหากยังมีบุคลากรสังกัดอยู่)

---

### 3.21 `POST /api` — จัดการกฎโควตารายเดือน (`saveQuota` / `deleteQuota`)
* **`saveQuota`** (`STAFF`/`ADMIN`):
```json
{
  "action": "saveQuota",
  "payload": {
    "targetType": "DEPT",
    "targetKey": "กลุ่มงานเคาน์เตอร์บริการ",
    "itemId": 7,
    "monthlyLimit": 2000,
    "note": "โควตาประจำเดือนสำหรับกลุ่มงานเคาน์เตอร์บริการ",
    "updatedBy": "ผู้ดูแลระบบคลังพัสดุ (Admin)"
  }
}
```
* **`deleteQuota`** (`STAFF`/`ADMIN`): ส่ง `id` หรือ `(targetType, targetKey, itemId)` เพื่อลบกฎโควตาออกจาก `quota_rules`
