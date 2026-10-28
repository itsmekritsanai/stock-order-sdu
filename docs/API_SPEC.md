# API Specification (docs/API_SPEC.md)
### ระบบขอเบิกพัสดุและคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต (Stock Order SDU)

---

## 1. ข้อมูลภาพรวม API (Overview & Conventions)

* **Protocol:** HTTP / HTTPS (RESTful JSON API)
* **Backend Architecture:**
  * **Primary (Phase 5):** Backend REST API Service (Node.js Express / Python FastAPI) เชื่อมต่อกับ **PostgreSQL 16 Database** บน Docker
  * **Alternative / Fallback:** Google Apps Script Web App สำหรับ Deployment แบบ Serverless
* **Base Endpoint URL:**
  * Local Dev (Docker / Node API): `http://localhost:3000/api` หรือ `http://localhost:8080/api`
  * Google Apps Script: `https://script.google.com/macros/s/{DEPLOYMENT_ID}/exec`
* **Content-Type:** `application/json`
* **การจัดการ Concurrency:**
  * **PostgreSQL:** จัดการผ่าน Database Transaction ร่วมกับ Row-Level Locking (`SELECT ... FOR UPDATE`)
  * **Google Apps Script:** ใช้ `LockService.getScriptLock()` รอคิวการเขียนสต๊อกสูงสุด 30 วินาที ป้องกัน Race Condition

---

## 2. สรุปรายการ Endpoints (Summary Table)

| Method | Endpoint Parameter | Action Name | สิทธิ์การเข้าถึง | วัตถุประสงค์ |
| :---: | :--- | :--- | :---: | :--- |
| `GET` | `?action=getItems` | `getItems` | สาธารณะ | ดึงรายการพัสดุและยอดคงคลังทั้งหมด |
| `GET` | `?action=getRequisitions` | `getRequisitions` | เจ้าหน้าที่/ทั่วไป | ดึงประวัติและคิวคำขอทั้งหมด |
| `GET` | `?action=trackRequisition&docNo=...`| `trackRequisition` | สาธารณะ | ติดตามสถานะคำขอรายเอกสาร |
| `GET` | `?action=getDepartments` | `getDepartments` | สาธารณะ | ดึงรายชื่อ 90+ หน่วยงาน |
| `POST`| Payload `action: "createRequisition"`| `createRequisition` | สาธารณะ | ส่งคำขอเบิกพัสดุใหม่ |
| `POST`| Payload `action: "approveRequisition"`| `approveRequisition` | เจ้าหน้าที่ | อนุมัติคำขอและล็อกยอดติดจอง |
| `POST`| Payload `action: "completeRequisition"`| `completeRequisition`| เจ้าหน้าที่ | บันทึกลายเซ็นและตัดยอดสต๊อกจริง |
| `POST`| Payload `action: "rejectRequisition"` | `rejectRequisition` | เจ้าหน้าที่ | ไม่อนุมัติคำขอและคืนสิทธิ์ |
| `POST`| Payload `action: "restockItem"` | `restockItem` | เจ้าหน้าที่ | รับพัสดุเข้าคลัง |

---

## 3. รายละเอียด Endpoints แบบเจาะลึก (Endpoint Details)

### 3.1 `GET /exec?action=getItems`
ดึงรายการพัสดุคงคลังทั้งหมด พร้อมยอดคงเหลือจริง (`on_hand_pieces`), ยอดติดจอง (`reserved_pieces`) และยอดพร้อมเบิก (`available_pieces`)

* **Query Parameters:**
  * `action=getItems` (จำเป็น)
  * `category` (ตัวเลือก): กรองหมวดหมู่ เช่น `ซองเอกสาร`

* **Response Success (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "ซองขยายข้างมีครุฑ 279´432 (กล่องละ 250 ซอง)",
      "category": "ซองเอกสาร",
      "is_multi_unit": true,
      "unit_box_name": "กล่อง",
      "unit_piece_name": "ซอง",
      "pieces_per_box": 250,
      "on_hand_pieces": 1750,
      "reserved_pieces": 500,
      "available_pieces": 1250,
      "min_alert": 500,
      "expected_restock_date": "2026-11-15",
      "image_piece": "assets/images/image1.jpeg",
      "image_box": "assets/images/image10.jpeg"
    }
  ],
  "total": 1
}
```

---

### 3.2 `GET /exec?action=trackRequisition&docNo={DOC_NO}`
ค้นหาสถานะของคำขอตามเลขที่เอกสาร

* **Query Parameters:**
  * `action=trackRequisition` (จำเป็น)
  * `docNo` (จำเป็น): เช่น `REQ-256910-0042`

* **Response Success (200 OK):**
```json
{
  "status": "success",
  "found": true,
  "data": {
    "id": "REQ-256910-0042",
    "date": "21 ต.ค. 2569 10:15 น.",
    "requester": "อ.สมชาย ใจดี",
    "dept": "โรงเรียนการเรือน - เทคโนโลยีการประกอบอาหารและการบริการ",
    "phone": "081-998-7766",
    "purpose": "ใช้สำหรับการจัดการเรียนการสอนและสอบปฏิบัติการ ภาคเรียน 1/2569",
    "status": "COMPLETED",
    "disbursed_at": "2026-10-22T14:30:00Z",
    "items": [
      {
        "itemId": 1,
        "name": "ซองขยายข้างมีครุฑ 279´432",
        "qtyBoxes": 2,
        "qtyPieces": 0,
        "totalPieces": 500,
        "unitBox": "กล่อง",
        "unitPiece": "ซอง",
        "approvedPieces": 500
      }
    ]
  }
}
```

* **Response Not Found (200 OK with found: false):**
```json
{
  "status": "error",
  "found": false,
  "message": "ไม่พบข้อมูลเอกสารคำขอเลขที่ดังกล่าว"
}
```

---

### 3.3 `POST /exec` — ส่งคำขอเบิกพัสดุ (`createRequisition`)
สร้างใบคำขอเบิกใหม่เข้าสู่ระบบในสถานะ `PENDING`

* **Request Headers:**
  * `Content-Type: application/json`

* **Request Body:**
```json
{
  "action": "createRequisition",
  "payload": {
    "requester": "อ.สมชาย ใจดี",
    "dept": "โรงเรียนการเรือน - เทคโนโลยีการประกอบอาหารและการบริการ",
    "phone": "081-998-7766",
    "purpose": "ใช้สอบปลายภาค ภาคการศึกษา 1/2569",
    "items": [
      {
        "itemId": 1,
        "name": "ซองขยายข้างมีครุฑ 279´432",
        "qtyBoxes": 1,
        "qtyPieces": 50,
        "totalPieces": 300,
        "unitBox": "กล่อง",
        "unitPiece": "ซอง"
      }
    ]
  }
}
```

* **Response Success (200 OK):**
```json
{
  "status": "success",
  "message": "สร้างคำขอเบิกพัสดุสำเร็จ",
  "docNo": "REQ-256910-4491",
  "createdAt": "2026-10-22T16:30:00Z"
}
```

* **Response Error (ยอดพัสดุไม่พอ):**
```json
{
  "status": "error",
  "code": "INSUFFICIENT_STOCK",
  "message": "ยอดพัสดุคงเหลือพร้อมเบิกไม่เพียงพอ",
  "details": {
    "itemId": 1,
    "requested": 300,
    "available": 200
  }
}
```

* **Response Error (พัสดุหมดสต๊อก / Out of Stock Guard):**
```json
{
  "status": "error",
  "code": "OUT_OF_STOCK",
  "message": "ไม่สามารถสร้างคำขอได้ เนื่องจากพัสดุบางรายการหมดสต๊อก (Available <= 0)",
  "details": {
    "itemId": 1,
    "name": "ซองขยายข้างมีครุฑ 279´432",
    "available": 0,
    "expected_restock_date": "2026-11-15"
  }
}
```

---

### 3.4 `POST /exec` — อนุมัติคำขอ (`approveRequisition`)
เจ้าหน้าที่กดอนุมัติคำขอ ระบบจะเปลี่ยนสถานะเป็น `APPROVED` และเพิ่มยอดล็อกใน `reserved_pieces`

* **Request Body:**
```json
{
  "action": "approveRequisition",
  "payload": {
    "docNo": "REQ-256910-4491",
    "items": [
      {
        "itemId": 1,
        "approvedPieces": 300
      }
    ]
  }
}
```

* **Response Success (200 OK):**
```json
{
  "status": "success",
  "docNo": "REQ-256910-4491",
  "statusNow": "APPROVED",
  "message": "อนุมัติคำขอและล็อกยอดพัสดุสำเร็จ"
}
```

---

### 3.5 `POST /exec` — บันทึกรับของสำเร็จและตัดสต๊อกจริง (`completeRequisition`)
ผู้ขอเบิกเดินทางมารับของและเซ็นชื่อผ่านแท่นดิจิทัล ระบบจะบันทึกวัน-เวลาที่จ่ายของจริง (`disbursed_at = CURRENT_TIMESTAMP`), ลดสต๊อกจริง `on_hand_pieces` และคืนยอดจอง `reserved_pieces`

* **Request Body:**
```json
{
  "action": "completeRequisition",
  "payload": {
    "docNo": "REQ-256910-4491",
    "signature": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
  }
}
```

* **Response Success (200 OK):**
```json
{
  "status": "success",
  "docNo": "REQ-256910-4491",
  "statusNow": "COMPLETED",
  "disbursedAt": "2026-10-22T14:30:00Z",
  "message": "บันทึกลายเซ็น ประทับเวลายืนยันจ่ายของ และตัดยอดคงคลังจริงเรียบร้อยแล้ว"
}
```

---

### 3.6 `POST /exec` — ไม่อนุมัติคำขอ (`rejectRequisition`)
เจ้าหน้าที่ปฏิเสธคำขอ คืนยอดที่เคยล็อกไว้ (ถ้ามี) และบันทึกเหตุผล

* **Request Body:**
```json
{
  "action": "rejectRequisition",
  "payload": {
    "docNo": "REQ-256910-4491",
    "reason": "พัสดุมีรายการสำรองสำหรับโครงการพระราชทาน กรุณาติดต่อห้องพัสดุ"
  }
}
```

* **Response Success (200 OK):**
```json
{
  "status": "success",
  "docNo": "REQ-256910-4491",
  "statusNow": "REJECTED",
  "message": "ปฏิเสธคำขอและคืนยอดพัสดุเรียบร้อยแล้ว"
}
```

---

### 3.7 `POST /exec` — รับพัสดุเข้าคลัง (`restockItem`)
เจ้าหน้าที่นำพัสดุเข้าคลังเพื่อเพิ่มสต๊อก `on_hand_pieces`

* **Request Body:**
```json
{
  "action": "restockItem",
  "payload": {
    "itemId": 1,
    "addBoxes": 10,
    "addPieces": 0
  }
}
```

* **Response Success (200 OK):**
```json
{
  "status": "success",
  "itemId": 1,
  "newOnHandPieces": 4250,
  "message": "รับพัสดุเข้าคลังสำเร็จ"
}
```

---

### 3.8 `POST /exec` — กำหนดวันที่พัสดุเข้าเมื่อของหมด (`updateRestockDate`)
เจ้าหน้าที่ระบุหรืออัปเดตวันที่คาดว่าพัสดุจะมาส่งเข้าคลังเมื่อของหมด

* **Request Body:**
```json
{
  "action": "updateRestockDate",
  "payload": {
    "itemId": 1,
    "expectedRestockDate": "2026-11-15"
  }
}
```

* **Response Success (200 OK):**
```json
{
  "status": "success",
  "itemId": 1,
  "expectedRestockDate": "2026-11-15",
  "message": "บันทึกวันที่คาดว่าพัสดุจะเข้าสำเร็จ"
}
```
