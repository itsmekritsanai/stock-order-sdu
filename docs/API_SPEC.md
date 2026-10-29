# API Specification (docs/API_SPEC.md)
### ระบบขอเบิกพัสดุและคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต (Stock Order SDU)

---

## 1. ข้อมูลภาพรวม API (Overview & Conventions)

* **Protocol:** HTTP / HTTPS (RESTful JSON API ให้บริการโดย Python MySQL Server [`backend/server.py`](file:///c:/Users/Sho/Downloads/project%20stock/backend/server.py))
* **Base Endpoint URL:**
  ```text
  http://localhost:8080/api
  ```
* **Content-Type:** `application/json; charset=utf-8`
* **การจัดการ Concurrency & Database Transaction:** ใช้ฐานข้อมูล **MySQL (`InnoDB`)** ทำงานภายใต้ **ACID Transaction (`BEGIN` / `COMMIT` / `ROLLBACK`)** ร่วมกับ **Row-Level Locking (`SELECT ... FOR UPDATE`)** เพื่อป้องกันปัญหา Race Condition เมื่อมีการขอเบิกหรือตัดสต๊อกพร้อมกัน

---

## 2. สรุปรายการ Endpoints (Summary Table)

| Method | Endpoint Parameter | Action Name | สิทธิ์การเข้าถึง | วัตถุประสงค์ |
| :---: | :--- | :--- | :---: | :--- |
| `GET` | `?action=getItems` | `getItems` | สาธารณะ | ดึงรายการพัสดุและยอดคงคลังทั้งหมด |
| `GET` | `?action=getRequisitions` | `getRequisitions` | เจ้าหน้าที่/ทั่วไป | ดึงประวัติและคิวคำขอทั้งหมด |
| `GET` | `?action=trackRequisition&docNo=...`| `trackRequisition` | สาธารณะ | ติดตามสถานะคำขอรายเอกสาร |
| `GET` | `?action=getDepartments` | `getDepartments` | สาธารณะ | ดึงรายชื่อกลุ่มงาน/หน่วยงานภายใน สวท. |
| `GET` | `?action=getUsers` | `getUsers` | สาธารณะ | ดึงรายชื่อบุคลากรผู้มีสิทธิ์ขอเบิก (เริ่มต้นด้วยหัวหน้าหน่วยงาน 4 ท่าน) |
| `POST`| Payload `action: "createRequisition"`| `createRequisition` | สาธารณะ | ส่งคำขอเบิกพัสดุใหม่ |
| `POST`| Payload `action: "approveRequisition"`| `approveRequisition` | เจ้าหน้าที่ | อนุมัติคำขอและล็อกยอดติดจอง |
| `POST`| Payload `action: "completeRequisition"`| `completeRequisition`| เจ้าหน้าที่ | บันทึกลายเซ็นและตัดยอดสต๊อกจริง |
| `POST`| Payload `action: "rejectRequisition"` | `rejectRequisition` | เจ้าหน้าที่ | ไม่อนุมัติคำขอและคืนสิทธิ์ |
| `POST`| Payload `action: "restockItem"` | `restockItem` | เจ้าหน้าที่ | รับพัสดุเข้าคลัง |
| `POST`| Payload `action: "adjustStock"` | `adjustStock` | เจ้าหน้าที่ | ปรับปรุงยอดสต๊อกจริงจากการตรวจนับ |
| `POST`| Payload `action: "saveItem"` | `saveItem` | เจ้าหน้าที่ | เพิ่มหรือแก้ไขรายการพัสดุในคลัง (พร้อมรูปภาพ) |
| `POST`| Payload `action: "deleteItem"` | `deleteItem` | เจ้าหน้าที่ | ลบรายการพัสดุออกจากคลัง |
| `POST`| Payload `action: "saveUser"` | `saveUser` | เจ้าหน้าที่ | เพิ่มหรือแก้ไขรายชื่อบุคลากร (User) |
| `POST`| Payload `action: "deleteUser"` | `deleteUser` | เจ้าหน้าที่ | ลบรายชื่อบุคลากรออกจากระบบ |
| `POST`| Payload `action: "addDepartment"` | `addDepartment` | เจ้าหน้าที่ | เพิ่มกลุ่มงาน/หน่วยงานใหม่เข้าสู่ตาราง `departments` |

---

## 3. รายละเอียด Endpoints แบบเจาะลึก (Endpoint Details)

### 3.1 `GET /api?action=getItems`
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
      "image_piece": "assets/images/image1.jpeg",
      "image_box": "assets/images/image10.jpeg"
    }
  ],
  "total": 1
}
```

---

### 3.2 `GET /api?action=trackRequisition&docNo={DOC_NO}`
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
    "status": "APPROVED",
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

### 3.3 `POST /api` — ส่งคำขอเบิกพัสดุ (`createRequisition`)
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

---

### 3.4 `POST /api` — อนุมัติคำขอ (`approveRequisition`)
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

### 3.5 `POST /api` — บันทึกรับของสำเร็จและตัดสต๊อกจริง (`completeRequisition`)
ผู้ขอเบิกเดินทางมารับของและเซ็นชื่อผ่านแท่นดิจิทัล ระบบจะตัดยอด `on_hand_pieces` และคืน `reserved_pieces`

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
  "message": "บันทึกลายเซ็นและตัดยอดคงคลังจริงเรียบร้อยแล้ว"
}
```

---

### 3.6 `POST /api` — ไม่อนุมัติคำขอ (`rejectRequisition`)
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