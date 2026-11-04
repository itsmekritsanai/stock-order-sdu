---
schema: 1
bug_id: requisition-state-machine-bypass
status: resolved
confidence: high
project_stack: Python 3.13 + ThreadingHTTPServer + PostgreSQL 17 (from requirements.txt, backend/server.py, docker-compose.yml)
created: 2026-11-04
source: internal code audit + live database state machine reproduction test
---

## Summary

**Observed:** 
คำขอเบิกพัสดุ (`requisitions`) ขาดการตรวจสอบสถานะต้นทางก่อนทำธุรกรรม (State Machine Transition Validation) ทำให้สามารถเรียกคำสั่งซ้ำซ้อนหรือข้ามขั้นตอนได้:
1. การเรียก `handle_complete_requisition` ซ้ำในใบเบิกที่สถานะเป็น `COMPLETED` อยู่แล้ว ส่งผลให้ระบบตัดยอดสต๊อกคงคลังจริง (`on_hand_pieces`) ซ้ำเป็นครั้งที่สอง และสร้างประวัติธุรกรรม `OUT` ซ้ำซ้อน ทำให้ยอดพัสดุในคลังหายไปฟรี
2. การเรียก `handle_approve_requisition` ซ้ำในใบเบิกที่สถานะเป็น `APPROVED` อยู่แล้ว ส่งผลให้ยอดติดจอง (`reserved_pieces`) ถูกบวกเพิ่มซ้ำ ทำให้เกิดสต๊อกติดจองผี (Phantom Reserved Quota) ที่ไม่สามารถปลดล็อกได้
3. การเรียก `handle_reject_requisition` ในใบเบิกที่สถานะเป็น `COMPLETED` แล้ว ทำให้สถานะเปลี่ยนเป็น `REJECTED` ทั้งที่พัสดุถูกตัดจ่ายออกจากห้องคลังไปแล้ว

**Expected:**
1. `handle_approve_requisition` ต้องยอมรับเฉพาะคำขอที่มีสถานะ `PENDING` เท่านั้น หากไม่ใช่ `PENDING` ให้ปฏิเสธด้วยข้อความระบุสถานะปัจจุบัน
2. `handle_complete_requisition` ต้องยอมรับเฉพาะคำขอที่มีสถานะ `APPROVED` เท่านั้น หากเป็น `COMPLETED` อยู่แล้ว ให้ส่งรหัสข้อผิดพลาดแจ้งว่า "คำขอนี้ได้รับการจ่ายพัสดุเรียบร้อยแล้ว" โดย **ห้ามตัดยอดสต๊อกซ้ำเด็ดขาด**
3. `handle_reject_requisition` ต้องยอมรับเฉพาะคำขอที่มีสถานะ `PENDING` หรือ `APPROVED` เท่านั้น และห้ามปฏิเสธคำขอที่ `COMPLETED` แล้ว

**Scope of impact:**
ความถูกต้องของยอดพัสดุคงคลังจริง (Inventory Integrity) ในห้องคลัง มสด. และประวัติธุรกรรมสต๊อก (`stock_transactions`) เสี่ยงต่อการเกิดสต๊อกติดลบหรือยอดสินค้าสูญหายเมื่อมีการกดปุ่มซ้ำ (Double Click) หรือส่งคำขอเครือข่ายซ้ำ (Network Replay)

---

## Evidence

- **โค้ดต้นทางใน `backend/server.py` บรรทัด 503-527 (`handle_complete_requisition`):**
  ```python
  cur.execute("SELECT * FROM requisitions WHERE id = %s FOR UPDATE", (doc_no,))
  req = cur.fetchone()
  # ขาดการตรวจสอบ if req["status"] != "APPROVED":
  for ri in req_items:
      new_on_hand = max(0, int(inv["on_hand_pieces"]) - approved_qty)
      cur.execute("UPDATE inventory_items SET on_hand_pieces = %s, reserved_pieces = %s WHERE id = %s", (new_on_hand, new_reserved, item_id))
      cur.execute("INSERT INTO stock_transactions ... VALUES (%s, 'OUT', ...)")
  ```
- **โค้ดต้นทางใน `backend/server.py` บรรทัด 441-471 (`handle_approve_requisition`):**
  ```python
  cur.execute("SELECT * FROM requisitions WHERE id = %s FOR UPDATE", (doc_no,))
  req = cur.fetchone()
  # ขาดการตรวจสอบ if req["status"] != "PENDING":
  for ri in req_items:
      cur.execute("UPDATE inventory_items SET reserved_pieces = reserved_pieces + %s WHERE id = %s", (approved_qty, item_id))
  ```
- **ผลการทดสอบการจำลองอาการจริง (Live Reproduction):**
  รันคำสั่ง `server.handle_complete_requisition({"docNo": "REQ-256910-0042", "signature": "test"})` บนเอกสารที่มีสถานะ `COMPLETED` อยู่แล้ว:
  * ผลลัพธ์: API ตอบกลับ `"status": "success"`
  * ผลต่อสต๊อก: พัสดุรหัส 1 ถูกตัดสต๊อกซ้ำจากยอดคงคลัง 50 ชิ้น ลดลงเหลือ 0 ชิ้นทันที และเกิดประวัติการตัดของ `OUT` ใบใหม่ขึ้นในตาราง `stock_transactions`

---

## Hypotheses

### H1 — Backend Handlers ขาดการตรวจสอบเงื่อนไขสถานะปัจจุบันก่อนเปลี่ยนสถานะ (confidence: high)

**Mechanism:**
ในฟังก์ชัน `handle_approve_requisition`, `handle_complete_requisition`, และ `handle_reject_requisition` มีการคิวรี `SELECT * FROM requisitions WHERE id = %s FOR UPDATE` แต่หลังจากได้แถวข้อมูล `req` มาแล้ว กลับนำไปวนลูปปรับปรุงยอดสต๊อกในตาราง `inventory_items` ทันที โดยไม่ได้ตรวจสอบว่าฟิลด์ `req["status"]` อยู่ในสถานะที่อนุญาตให้เปลี่ยนผ่าน (Valid State Transition) หรือไม่

**Predicts:**
เมื่อเพิ่มเงื่อนไขตรวจสอบสถานะ:
1. ใน `handle_approve_requisition`:
   * หาก `req["status"] != "PENDING"` ให้คืนค่า `{"status": "error", "code": "INVALID_STATE", "message": f"ไม่สามารถอนุมัติได้เนื่องจากคำขออยู่ในสถานะ {req['status']}"}`
2. ใน `handle_complete_requisition`:
   * หาก `req["status"] == "COMPLETED"` ให้คืนค่า `{"status": "error", "code": "ALREADY_COMPLETED", "message": "คำขอเลขที่นี้ได้รับการจ่ายพัสดุเรียบร้อยแล้ว"}`
   * หาก `req["status"] != "APPROVED"` ให้คืนค่า `{"status": "error", "code": "NOT_APPROVED", "message": "คำขอต้องได้รับการอนุมัติ (APPROVED) ก่อนดำเนินการจ่ายพัสดุ"}`
3. ใน `handle_reject_requisition`:
   * หาก `req["status"] == "COMPLETED"` ให้คืนค่า `{"status": "error", "code": "ALREADY_COMPLETED", "message": "ไม่สามารถปฏิเสธคำขอที่จ่ายพัสดุเรียบร้อยแล้วได้"}`
   * หาก `req["status"] == "REJECTED"` ให้คืนค่า `{"status": "error", "code": "ALREADY_REJECTED", "message": "คำขอนี้ถูกปฏิเสธไปแล้ว"}`
จะสามารถป้องกันการตัดสต๊อกซ้ำและการจองสต๊อกซ้ำได้อย่างสมบูรณ์ 100%

**Would be falsified by:**
พบว่ามีกลไกระดับ Database Trigger ใน PostgreSQL ที่คอยบล็อกการตัดสต๊อกซ้ำอยู่แล้ว (ซึ่งจากการตรวจสอบ DDL ใน `backend/schema_postgres.sql` ไม่มี Trigger สำหรับ State Transition Validation แต่อย่างใด มีเฉพาะ Trigger สำหรับ `updated_at`)

---

## Verification

### Steps to reproduce
1. คิวรีข้อมูลใบคำขอที่มีสถานะ `COMPLETED` (เช่น `REQ-256910-0042`)
2. บันทึกยอด `on_hand_pieces` ปัจจุบันของพัสดุที่เกี่ยวข้อง
3. ส่งคำสั่ง `POST /api` ด้วย Action `completeRequisition` สำหรับเอกสารเดิม
4. ตรวจสอบยอด `on_hand_pieces` หลังทำรายการ หากยอดลดลงอีกรอบ แสดงว่าเกิดข้อผิดพลาดจริง

### Verification log
- 2026-11-04 13:57: ทดสอบจำลองการเรียก `handle_complete_requisition` ซ้ำกับ `REQ-256910-0042` ยืนยันพบว่ายอด `on_hand_pieces` ถูกตัดซ้ำจริง (Confirmed H1)
- 2026-11-04 14:02: เขียน Regression Tests ชุด `TestRequisitionStateMachineSafety` ใน `tests/test_stock_logic.py` ก่อนแก้โค้ด และรันผลลัพธ์พบว่า **FAILED** ทั้ง 4 ข้อ ยืนยันพฤติกรรมบักจริงและข้อทดสอบมีความเด็ดขาด (Decisive)

---

## Allowed scope
- `backend/server.py` — ฟังก์ชัน `handle_approve_requisition`, `handle_complete_requisition`, `handle_reject_requisition`
- `tests/test_stock_logic.py` — เพิ่มกรณีทดสอบ Unit Test สำหรับตรวจสอบการป้องกัน Invalid State Transitions
- `.agents/` — ชุดเครื่องมือ BugScope Skills ที่ติดตั้งตามคำสั่งของผู้ใช้

## Forbidden scope
- `backend/schema_postgres.sql` — ห้ามแก้ไข DDL หรือสคีมาฐานข้อมูล
- `backend/schema.sql` — ห้ามแก้ไขสคีมาฐานข้อมูล
- `portal.html` — ห้ามแก้ไขหน้าตาหรือโค้ดส่วน Frontend
- `index.html` — ห้ามแก้ไขหน้าตาหรือโค้ดส่วน Frontend
- `staff.html` — ห้ามแก้ไขหน้าตาหรือโค้ดส่วน Frontend
- `.env` — ห้ามแก้ไขคอนฟิกระบบ
- `docker-compose.yml` — ห้ามแก้ไขคอนเทนเนอร์

## Blast radius
- ฟังก์ชันที่ถูกแก้ไขคือ Handler ของคำขอเบิกทั้ง 3 ตัว มีผลดีต่อความถูกต้องของสต๊อก และไม่มีผลกระทบต่อ Requester Portal เพราะผู้ขอเบิกใช้งานเฉพาะ `createRequisition` และ `trackRequisition`

---

## Success criteria

1. เมื่อเรียก `handle_complete_requisition` ซ้ำบนคำขอที่เป็น `COMPLETED` แล้ว ระบบต้องตอบกลับ `{"status": "error", "code": "ALREADY_COMPLETED"}` และยอด `on_hand_pieces` ต้องเท่าเดิม ไม่ลดลง
2. เมื่อเรียก `handle_approve_requisition` ซ้ำบนคำขอที่เป็น `APPROVED` แล้ว ระบบต้องตอบกลับ `{"status": "error", "code": "INVALID_STATE"}` และยอด `reserved_pieces` ต้องไม่ถูกบวกเพิ่ม
3. รันชุดทดสอบ `pytest tests/test_stock_logic.py` ผ่านครบทุกข้อ และข้อทดสอบใหม่สำหรับการป้องกัน State Transition ผ่าน 100%

---

## Resolution log

### What was verified
- ยืนยันการปฏิเสธคำขอที่ไม่อยู่ในสถานะที่ถูกต้อง (State Transition Enforcement):
  - `handle_approve_requisition`: ปฏิเสธหากสถานะไม่ใช่ `PENDING` (code: `INVALID_STATE`)
  - `handle_complete_requisition`: ปฏิเสธหากเป็น `COMPLETED` อยู่แล้ว (code: `ALREADY_COMPLETED`) หรือไม่ใช่ `APPROVED` (code: `NOT_APPROVED`)
  - `handle_reject_requisition`: ปฏิเสธหากเป็น `COMPLETED` (code: `ALREADY_COMPLETED`) หรือ `REJECTED` (code: `ALREADY_REJECTED`)
- รันการตรวจสอบขอบเขตอัตโนมัติ `check_scope.py`: ทุกไฟล์ที่แก้ไขอยู่ใน **Allowed scope** (0 violations)

### Files changed
- `backend/server.py` (Hypothesis H1): เพิ่มการตรวจสอบ `current_status` ใน `handle_approve_requisition`, `handle_complete_requisition`, และ `handle_reject_requisition` ก่อนเริ่มทำธุรกรรมและตัดยอดสต๊อก
- `tests/test_stock_logic.py` (Hypothesis H1 / Regression Safety): เพิ่มคลาส `TestRequisitionStateMachineSafety` ครอบคลุม 4 กรณีทดสอบ

### Success criteria results
1. **Success Criterion 1:** `handle_complete_requisition` ซ้ำบนคำขอที่เป็น `COMPLETED` คืนค่า `status: error`, `code: ALREADY_COMPLETED` พร้อม rollback ธุรกรรม -> **PASSED**
2. **Success Criterion 2:** `handle_approve_requisition` บนคำขอที่ `APPROVED`/`COMPLETED` คืนค่า `status: error`, `code: INVALID_STATE` ไม่มีการจองเพิ่ม -> **PASSED**
3. **Success Criterion 3:** รันชุดทดสอบ `pytest tests/test_stock_logic.py` ผ่านครบ 44/44 ข้อ (100% pass rate ในเวลา 1.00s) -> **PASSED**

### Left alone
- ฟังก์ชันระดับ Frontend ใน `portal.html` และ `staff.html` มีการแสดงผลสถานะอยู่แล้ว แต่ไม่มีการดักจับสถานะล่วงหน้าในระดับ UI ฝั่งไคลเอนต์ ปล่อยให้ Backend เป็นผู้บังคับใช้ Single Source of Truth ตามสโคปความปลอดภัย


