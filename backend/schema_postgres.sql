-- =============================================================================
-- ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
-- PostgreSQL 17 Database Schema & Initial Seed Data
-- =============================================================================

-- Drop existing tables in reverse dependency order
DROP TABLE IF EXISTS quota_rules CASCADE;
DROP TABLE IF EXISTS stock_transactions CASCADE;
DROP TABLE IF EXISTS requisition_items CASCADE;
DROP TABLE IF EXISTS requisitions CASCADE;
DROP TABLE IF EXISTS inventory_items CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

-- -----------------------------------------------------------------------------
-- 1. ตาราง departments (กลุ่มงาน/หน่วยงานภายใน สวท.)
-- -----------------------------------------------------------------------------
CREATE TABLE departments (
  id SERIAL PRIMARY KEY,
  category VARCHAR(150) NOT NULL,
  name VARCHAR(255) NOT NULL,
  parent_name VARCHAR(255) NOT NULL,
  full_label VARCHAR(255) NOT NULL,
  is_active SMALLINT NOT NULL DEFAULT 1
);

CREATE INDEX idx_dept_category ON departments (category);
CREATE INDEX idx_dept_full_label ON departments (full_label);

-- -----------------------------------------------------------------------------
-- 2. ตาราง users (รายชื่อบุคลากร สวท.)
-- -----------------------------------------------------------------------------
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  username VARCHAR(100) UNIQUE,
  password VARCHAR(255) DEFAULT '',
  role VARCHAR(50) NOT NULL DEFAULT 'REQUESTER',
  position VARCHAR(255) DEFAULT '',
  dept VARCHAR(255) NOT NULL,
  phone VARCHAR(50) DEFAULT '',
  is_active SMALLINT NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_name ON users (name);
CREATE INDEX idx_users_username ON users (username);
CREATE INDEX idx_users_dept ON users (dept);

-- -----------------------------------------------------------------------------
-- 3. ตาราง inventory_items (คลังพัสดุกลาง 34 รายการ พร้อมระบบแปลง 2 หน่วยนับ)
-- -----------------------------------------------------------------------------
CREATE TABLE inventory_items (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  category VARCHAR(100) NOT NULL,
  is_multi_unit SMALLINT NOT NULL DEFAULT 1,
  unit_box_name VARCHAR(50) DEFAULT NULL,
  unit_piece_name VARCHAR(50) NOT NULL DEFAULT 'ชิ้น',
  pieces_per_box INT NOT NULL DEFAULT 1 CHECK (pieces_per_box >= 1),
  on_hand_pieces INT NOT NULL DEFAULT 0 CHECK (on_hand_pieces >= 0),
  reserved_pieces INT NOT NULL DEFAULT 0 CHECK (reserved_pieces >= 0),
  min_alert INT NOT NULL DEFAULT 500 CHECK (min_alert >= 0),
  monthly_limit INT NOT NULL DEFAULT 0 CHECK (monthly_limit >= 0),
  last_unit_price DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
  last_restocked_at TIMESTAMP DEFAULT NULL,
  image_piece TEXT DEFAULT NULL,
  image_box TEXT DEFAULT NULL,
  is_active SMALLINT NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_items_name ON inventory_items (name);
CREATE INDEX idx_items_category ON inventory_items (category);

-- -----------------------------------------------------------------------------
-- 4. ตาราง requisitions (เอกสารใบคำขอเบิกพัสดุ)
-- -----------------------------------------------------------------------------
CREATE TABLE requisitions (
  id VARCHAR(50) PRIMARY KEY,
  date VARCHAR(100) NOT NULL,
  requester VARCHAR(150) NOT NULL,
  dept VARCHAR(255) NOT NULL,
  phone VARCHAR(50) DEFAULT '',
  purpose TEXT NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'VERIFIED', 'APPROVED', 'COMPLETED', 'REJECTED')),
  signature TEXT DEFAULT NULL,
  reject_reason TEXT DEFAULT NULL,
  verified_by VARCHAR(150) DEFAULT NULL,
  verified_at TIMESTAMP DEFAULT NULL,
  verified_date VARCHAR(100) DEFAULT NULL,
  approved_by VARCHAR(150) DEFAULT NULL,
  approved_at TIMESTAMP DEFAULT NULL,
  approved_date VARCHAR(100) DEFAULT NULL,
  completed_at TIMESTAMP DEFAULT NULL,
  completed_date VARCHAR(100) DEFAULT NULL,
  rejected_at TIMESTAMP DEFAULT NULL,
  rejected_date VARCHAR(100) DEFAULT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_req_status ON requisitions (status);
CREATE INDEX idx_req_requester ON requisitions (requester);
CREATE INDEX idx_req_dept ON requisitions (dept);
CREATE INDEX idx_req_created_at ON requisitions (created_at);

-- -----------------------------------------------------------------------------
-- 5. ตาราง requisition_items (รายการพัสดุย่อยในแต่ละใบคำขอ)
-- -----------------------------------------------------------------------------
CREATE TABLE requisition_items (
  id SERIAL PRIMARY KEY,
  requisition_id VARCHAR(50) NOT NULL REFERENCES requisitions(id) ON DELETE CASCADE,
  item_id INT NOT NULL REFERENCES inventory_items(id) ON DELETE RESTRICT,
  name VARCHAR(255) NOT NULL,
  qty_boxes INT NOT NULL DEFAULT 0 CHECK (qty_boxes >= 0),
  qty_pieces INT NOT NULL DEFAULT 0 CHECK (qty_pieces >= 0),
  total_pieces INT NOT NULL DEFAULT 0 CHECK (total_pieces > 0),
  unit_box VARCHAR(50) DEFAULT NULL,
  unit_piece VARCHAR(50) NOT NULL DEFAULT 'ชิ้น',
  approved_pieces INT NOT NULL DEFAULT 0 CHECK (approved_pieces >= 0),
  pieces_per_box_snapshot INT NOT NULL DEFAULT 1 CHECK (pieces_per_box_snapshot >= 1)
);

CREATE INDEX idx_req_items_req_id ON requisition_items (requisition_id);
CREATE INDEX idx_req_items_item_id ON requisition_items (item_id);

-- -----------------------------------------------------------------------------
-- 6. ตาราง stock_transactions (บันทึกประวัติความเคลื่อนไหวสต๊อก Audit Trail)
-- -----------------------------------------------------------------------------
CREATE TABLE stock_transactions (
  id SERIAL PRIMARY KEY,
  item_id INT NOT NULL REFERENCES inventory_items(id) ON DELETE RESTRICT,
  transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('IN', 'OUT', 'ADJUST')),
  change_pieces INT NOT NULL,
  balance_after INT NOT NULL DEFAULT 0 CHECK (balance_after >= 0),
  unit_price DECIMAL(12, 2) NOT NULL DEFAULT 0.00 CHECK (unit_price >= 0),
  total_cost DECIMAL(12, 2) NOT NULL DEFAULT 0.00 CHECK (total_cost >= 0),
  reference_type VARCHAR(50) NOT NULL,
  reference_id VARCHAR(50) DEFAULT NULL,
  reason VARCHAR(255) DEFAULT NULL,
  recorded_by VARCHAR(150) DEFAULT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tx_item_id ON stock_transactions (item_id);
CREATE INDEX idx_tx_created_at ON stock_transactions (created_at);
CREATE INDEX idx_tx_type_created_at ON stock_transactions (transaction_type, created_at);

-- -----------------------------------------------------------------------------
-- 7. ตาราง quota_rules (กำหนดโควตารายเดือนแยกตามบุคลากรและกลุ่มงาน/หน่วยงาน)
-- -----------------------------------------------------------------------------
CREATE TABLE quota_rules (
  id SERIAL PRIMARY KEY,
  target_type VARCHAR(20) NOT NULL CHECK (target_type IN ('USER', 'DEPT')),
  target_key VARCHAR(255) NOT NULL,
  item_id INT NOT NULL DEFAULT 0,
  monthly_limit INT NOT NULL DEFAULT 0,
  note VARCHAR(255) DEFAULT '',
  updated_by VARCHAR(150) DEFAULT '',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (target_type, target_key, item_id)
);

CREATE INDEX idx_quota_target ON quota_rules (target_type, target_key);

-- -----------------------------------------------------------------------------
-- ฟังก์ชันและ Trigger สำหรับอัปเดต updated_at อัตโนมัติ
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_inventory_items_updated_at ON inventory_items;
CREATE TRIGGER trg_inventory_items_updated_at BEFORE UPDATE ON inventory_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_requisitions_updated_at ON requisitions;
CREATE TRIGGER trg_requisitions_updated_at BEFORE UPDATE ON requisitions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_quota_rules_updated_at ON quota_rules;
CREATE TRIGGER trg_quota_rules_updated_at BEFORE UPDATE ON quota_rules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- ข้อมูลตั้งต้น (SEED DATA)
-- =============================================================================

-- 1. ข้อมูลกลุ่มงาน/หน่วยงาน สวท. (6 กลุ่มงาน/หน่วยงาน)
INSERT INTO departments (category, name, parent_name, full_label) VALUES
  ('สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)', 'สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน', 'สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)', 'สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน'),
  ('สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)', 'กลุ่มงานส่งเสริมวิชาการ', 'สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)', 'กลุ่มงานส่งเสริมวิชาการ'),
  ('สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)', 'กลุ่มงานบริการวิชาการ', 'สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)', 'กลุ่มงานบริการวิชาการ'),
  ('สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)', 'กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ', 'สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)', 'กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ'),
  ('สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)', 'หน่วยงานศึกษาทั่วไปและการเรียนรู้ตลอดชีวิต', 'สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)', 'หน่วยงานศึกษาทั่วไปและการเรียนรู้ตลอดชีวิต'),
  ('สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)', 'กลุ่มงานเคาน์เตอร์บริการ', 'สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)', 'กลุ่มงานเคาน์เตอร์บริการ');

-- 2. ข้อมูลรายชื่อผู้ใช้งาน สวท. จาก Book1.xlsx (15 บัญชี พร้อม Username, Password, Role, กลุ่มงาน และเบอร์ภายใน)
INSERT INTO users (id, name, username, password, role, position, dept, phone, is_active) VALUES
  (1, 'สมชัย จารุธนกิจพานิช', 'somchai_jar', 'S123456', 'REQUESTER', 'กลุ่มงานเคาน์เตอร์บริการ', 'กลุ่มงานเคาน์เตอร์บริการ', '5174', 1),
  (2, 'จิตราพร จันทรกูล', 'jittraporn_cha', 'J08111972', 'HEAD', 'รองผู้อำนวยการ', 'สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน', '5235', 1),
  (3, 'ทรรศนีย์ สุทธิภาพย์', 'tatsanee_soo', 'T02082518', 'REQUESTER', 'กลุ่มงานบริการวิชาการ', 'กลุ่มงานบริการวิชาการ', '5171', 1),
  (4, 'สุธางค์ หงษ์กลาง', 'sutang_hon', 'K272523', 'REQUESTER', 'กลุ่มงานบริการวิชาการ', 'กลุ่มงานบริการวิชาการ', '5173', 1),
  (5, 'ธนธรณ์ ยิ้มแย้ม', 'thanathorn_yim', 'T15012520', 'REQUESTER', 'งานเคาน์เตอร์บริการ', 'กลุ่มงานเคาน์เตอร์บริการ', '5173', 1),
  (6, 'สรัลพรรษ ชมศรี', 'saranphat_cho', 'A20062541', 'REQUESTER', 'กลุ่มงานบริการวิชาการ', 'กลุ่มงานบริการวิชาการ', '5173', 1),
  (7, 'สาริกา เสือบำรุง', 'sarika_sua', 'Sarika@1978', 'REQUESTER', 'กลุ่มงานบริการวิชาการ', 'กลุ่มงานบริการวิชาการ', '5173', 1),
  (8, 'ณัฐชา แก้ววิมล', 'natcha_kae', 'N200620', 'REQUESTER', 'กลุ่มงานส่งเสริมวิชาการ', 'กลุ่มงานส่งเสริมวิชาการ', '5173', 1),
  (9, 'ธนพรรธน์ เอี่ยมสะอาด', 'thanaphat_aie', 'T199726', 'REQUESTER', 'กลุ่มงานส่งเสริมวิชาการ', 'กลุ่มงานส่งเสริมวิชาการ', '5173', 1),
  (10, 'รัตติการณ์ คำแก้ววันดี', 'ratthikarn_kha', 'N123456', 'REQUESTER', 'หน่วยงานศึกษาทั่วไปและการเรียนรู้ตลอดชีวิต', 'หน่วยงานศึกษาทั่วไปและการเรียนรู้ตลอดชีวิต', '5171', 1),
  (11, 'นายอภิชาติ กรมนา', 'apichart_kro', 'I4apichart', 'REQUESTER', 'กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ', 'กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ', '5234', 1),
  (12, 'อธิพงศ์ อินโท', 'atipong_int', 'J080521', 'REQUESTER', 'กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ', 'กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ', '5234', 1),
  (13, 'นายบุญธรรม สังขะเสน', 'boonthum_sun', 'B422120', 'REQUESTER', 'กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ', 'กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ', '5235', 1),
  (14, 'จุริรัตน์ สิงอ่อน', 'Jabie_Sin', 'J094929', 'REQUESTER', 'กลุ่มงานบริการวิชาการ', 'กลุ่มงานบริการวิชาการ', '5173', 1),
  (15, 'จุฑาธิป ปั้นทอง', 'chuthathip_pan', 'bowmin/18092545', 'STAFF', 'กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ', 'กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ', '5175', 1);

-- 3. ข้อมูลพัสดุคงคลังตั้งต้น 34 รายการ
INSERT INTO inventory_items (id, name, category, is_multi_unit, unit_box_name, unit_piece_name, pieces_per_box, on_hand_pieces, reserved_pieces, min_alert, image_piece, image_box) VALUES
  (1, 'ซองเอกสารสีขาว 7´10 (500 ซองต่อกล่อง)', 'ซองเอกสาร', 1, 'กล่อง', 'ซอง', 500, 0, 0, 250, 'assets/images/ซองเอกสารสีขาว 7´10 (500 ซองต่อกล่อง) ซอง.jpeg', 'assets/images/ซองเอกสารสีขาว 7´10 (500 ซองต่อกล่อง) กล่อง.jpeg'),
  (2, 'ซองเอกสารน้ำตาล (มสด) 9´12.3', 'ซองเอกสาร', 1, 'กล่อง', 'ซอง', 500, 0, 0, 500, 'assets/images/ซองเอกสารน้ำตาล (มสด) 9´12.3 ซอง.jpeg', 'assets/images/ซองเอกสารน้ำตาล (มสด) 9´12.3 กล่อง.jpeg'),
  (3, 'กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)', 'กระดาษและแบบฟอร์ม', 1, 'กล่อง', 'ใบ', 2000, 32000, 0, 5000, 'assets/images/กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ) ใบ.jpeg', 'assets/images/กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ) กล่อง.jpeg'),
  (4, 'ซองขยายข้างมีครุฑ 279´432 (กล่องละ 250 ซอง)', 'ซองเอกสาร', 1, 'กล่อง', 'ซอง', 250, 1250, 0, 500, 'assets/images/ซองขยายข้างมีครุฑ 279´432 (กล่องละ 250 ซอง) ซอง.jpeg', 'assets/images/ซองขยายข้างมีครุฑ 279´432 (กล่องละ 250 ซอง) กล่อง.jpeg'),
  (5, 'กระดาษสติ๊กเกอร์แนวนอน ตัดหน้าซองจดหมาย', 'กระดาษและแบบฟอร์ม', 1, 'ซอง', 'แผ่น', 500, 4500, 0, 500, 'assets/images/กระดาษสติ๊กเกอร์แนวนอน ตัดหน้าซองจดหมาย แผ่น.jpeg', 'assets/images/กระดาษสติ๊กเกอร์แนวนอน ตัดหน้าซองจดหมาย กล่อง.jpeg'),
  (6, 'กระดาษสติ๊กเกอร์แนวตั้ง ติดหน้าซองข้อสอบ', 'กระดาษและแบบฟอร์ม', 1, 'ซอง', 'แผ่น', 500, 500, 0, 250, 'assets/images/กระดาษสติ๊กเกอร์แนวตั้ง ติดหน้าซองข้อสอบ แผ่น.png', 'assets/images/กระดาษสติ๊กเกอร์แนวตั้ง ติดหน้าซองข้อสอบ กล่อง.jpeg'),
  (7, 'กระดาษลายเส้น (ห่อละ 500 แผ่น)', 'กระดาษและแบบฟอร์ม', 1, 'ห่อ', 'แผ่น', 500, 23000, 0, 1000, 'assets/images/กระดาษลายเส้น (ห่อละ 500 แผ่น) แผ่น.jpeg', 'assets/images/กระดาษลายเส้น (ห่อละ 500 แผ่น) กล่อง.jpeg'),
  (8, 'กระดาษสติ๊กเกอร์ เต็มแผ่น', 'กระดาษและแบบฟอร์ม', 1, 'ห่อ', 'แผ่น', 500, 0, 0, 100, 'assets/images/กระดาษสติ๊กเกอร์ เต็มแผ่น แผ่น.png', 'assets/images/กระดาษสติ๊กเกอร์ เต็มแผ่น กล่อง.jpeg'),
  (9, 'แบบฟอร์มแก้ I', 'กระดาษและแบบฟอร์ม', 1, 'กล่อง', 'ชิ้น', 500, 2500, 0, 500, 'assets/images/แบบฟอร์มแก้ I ชิ้น.jpeg', 'assets/images/แบบฟอร์มแก้ I กล่อง.jpeg'),
  (10, 'ซองข้อสอบน้ำตาลไม่ขยายข้างพิมพ์ข้อความ (มสด)', 'ซองเอกสาร', 1, 'กล่อง', 'ซอง', 250, 3700, 0, 1000, 'assets/images/ซองข้อสอบน้ำตาลไม่ขยายข้างพิมพ์ข้อความ (มสด) ซอง.jpeg', 'assets/images/ซองข้อสอบน้ำตาลไม่ขยายข้างพิมพ์ข้อความ (มสด) กล่อง.jpeg'),
  (11, 'ซองเอกสารไม่ขยายข้าง สีน้ำตาล 10´15 นิ้ว (มสด) (กล่องละ 250 ซอง)', 'ซองเอกสาร', 1, 'กล่อง', 'ซอง', 250, 1500, 0, 500, 'assets/images/ซองเอกสารไม่ขยายข้าง สีน้ำตาล 10´15 นิ้ว (มสด) (กล่องละ 250 ซอง) ซอง.jpeg', 'assets/images/ซองเอกสารไม่ขยายข้าง สีน้ำตาล 10´15 นิ้ว (มสด) (กล่องละ 250 ซอง) กล่อง.jpeg'),
  (12, 'แบบฟอร์มทรานสคริป(ไทย)ป.ตรี ซองละ 500 ใบ', 'กระดาษและแบบฟอร์ม', 1, 'ซอง', 'ใบ', 500, 1500, 0, 300, 'assets/images/แบบฟอร์มทรานสคริป(ไทย)ป.ตรี ซองละ 500 ใบ ใบ.png', 'assets/images/แบบฟอร์มทรานสคริป(ไทย)ป.ตรี ซองละ 500 ใบ กล่อง.jpeg'),
  (13, 'แบบฟอร์มทรานสคริป(อังกฤษ)ป.ตรี ซองละ 500 ใบ', 'กระดาษและแบบฟอร์ม', 1, 'ซอง', 'ใบ', 500, 3500, 0, 500, 'assets/images/แบบฟอร์มทรานสคริป(อังกฤษ)ป.ตรี ซองละ 500 ใบ ใบ.jpeg', 'assets/images/แบบฟอร์มทรานสคริป(อังกฤษ)ป.ตรี ซองละ 500 ใบ กล่อง.jpeg'),
  (14, 'ทรานสคริป ป.โท(ไทย) ซองละ 500 ใบ', 'กระดาษและแบบฟอร์ม', 1, 'ซอง', 'ใบ', 500, 1000, 0, 200, 'assets/images/ทรานสคริป ป.โท(ไทย) ซองละ 500 ใบ ใบ.png', 'assets/images/ทรานสคริป ป.โท(ไทย) ซองละ 500 ใบ กล่อง.png'),
  (15, 'ทรานสคริป ป.โท(อังกฤษ) ซองละ 500 ใบ', 'กระดาษและแบบฟอร์ม', 1, 'ซอง', 'ใบ', 500, 1500, 0, 300, 'assets/images/ทรานสคริป ป.โท(อังกฤษ) ซองละ 500 ใบ ใบ.png', 'assets/images/ทรานสคริป ป.โท(อังกฤษ) ซองละ 500 ใบ กล่อง.jpeg'),
  (16, 'ใบรับรอง(ไทย)ซองละ 500 ใบ', 'กระดาษและแบบฟอร์ม', 1, 'ซอง', 'ใบ', 500, 2000, 0, 400, 'assets/images/ใบรับรอง(ไทย)ซองละ 500 ใบ ใบ.jpeg', 'assets/images/ใบรับรอง(ไทย)ซองละ 500 ใบ กล่อง.jpeg'),
  (17, 'ใบรับรอง(อังกฤษ)ซองละ 500 ใบ', 'กระดาษและแบบฟอร์ม', 1, 'ซอง', 'ใบ', 500, 3000, 0, 500, 'assets/images/ใบรับรอง(อังกฤษ)ซองละ 500 ใบ ใบ.png', 'assets/images/ใบรับรอง(อังกฤษ)ซองละ 500 ใบ กล่อง.png'),
  (18, 'คลิปดำNO.108', 'เครื่องเขียนและแฟ้ม', 1, 'ลัง', 'กล่อง', 12, 72, 0, 24, 'assets/images/คลิปดำNO.108 กล่อง.jpeg', 'assets/images/คลิปดำNO.108 ลัง.jpeg'),
  (19, 'คลิปดำNO.110', 'เครื่องเขียนและแฟ้ม', 1, 'ลัง', 'กล่อง', 12, 60, 0, 24, 'assets/images/คลิปดำNO.110 กล่อง.jpeg', 'assets/images/คลิปดำNO.110 ลัง.jpeg'),
  (20, 'ไส้MAX 10 MM', 'เครื่องเขียนและแฟ้ม', 1, 'ลัง', 'กล่อง', 20, 20, 0, 5, 'assets/images/ไส้MAX 10 MM กล่อง.jpeg', 'assets/images/ไส้MAX 10 MM ลัง.jpeg'),
  (21, 'ไส้MAX 12', 'เครื่องเขียนและแฟ้ม', 1, 'ลัง', 'กล่อง', 20, 20, 0, 5, 'assets/images/ไส้MAX 12 กล่อง.jpeg', 'assets/images/ไส้MAX 12 ลัง.jpeg'),
  (22, 'ซองกันกระแทก 270´327', 'ซองเอกสาร', 1, 'กล่อง', 'ซอง', 80, 2400, 0, 500, 'assets/images/ซองกันกระแทก 270´327 ซอง.jpeg', 'assets/images/ซองกันกระแทก 270´327 ซอง.jpeg'),
  (23, 'แฟ้มเสนอ', 'เครื่องเขียนและแฟ้ม', 0, 'เล่ม', 'เล่ม', 1, 5, 0, 5, 'assets/images/แฟ้มเสนอ เล่ม.jpeg', 'assets/images/แฟ้มเสนอ เล่ม.jpeg'),
  (24, 'แม็กเล็ก', 'เครื่องเขียนและแฟ้ม', 0, 'กล่อง', 'อัน', 1, 7, 0, 2, 'assets/images/แม็กเล็ก อัน.jpeg', 'assets/images/แม็กเล็ก กล่อง.jpeg'),
  (25, 'แม็กใหญ่', 'เครื่องเขียนและแฟ้ม', 0, 'กล่อง', 'อัน', 1, 5, 0, 2, 'assets/images/แม็กใหญ่ อัน.jpeg', 'assets/images/แม็กใหญ่ กล่อง.png'),
  (26, 'สก็อตเทปใส', 'เครื่องเขียนและแฟ้ม', 1, 'แพ็ค', 'ม้วน', 6, 4, 0, 6, 'assets/images/สก็อตเทปใส ม้วน.jpeg', 'assets/images/สก็อตเทปใส กล่อง.jpeg'),
  (27, 'สก็อตเทปขุ่น', 'เครื่องเขียนและแฟ้ม', 1, 'แพ็ค', 'ม้วน', 6, 25, 0, 6, 'assets/images/สก็อตเทปขุ่น ม้วน.jpeg', 'assets/images/สก็อตเทปขุ่น กล่อง.png'),
  (28, 'สก็อตเทปย่น', 'เครื่องเขียนและแฟ้ม', 1, 'แพ็ค', 'ม้วน', 6, 0, 0, 6, 'assets/images/สก็อตเทปย่น ม้วน.jpeg', 'assets/images/สก็อตเทปย่น กล่อง.jpeg'),
  (29, 'กาวแท่ง', 'เครื่องเขียนและแฟ้ม', 0, 'กล่อง', 'แท่ง', 1, 8, 0, 5, 'assets/images/กาวแท่ง แท่ง.jpeg', 'assets/images/กาวแท่ง กล่อง.png'),
  (30, 'กาวขวด', 'เครื่องเขียนและแฟ้ม', 0, 'กล่อง', 'ขวด', 1, 4, 0, 2, 'assets/images/กาวขวด ขวด.jpeg', 'assets/images/กาวขวด กล่อง.png'),
  (31, 'กรรไกร', 'เครื่องเขียนและแฟ้ม', 0, 'กล่อง', 'อัน', 1, 20, 0, 5, 'assets/images/กรรไกร อัน.jpeg', 'assets/images/กรรไกร กล่อง.png'),
  (32, 'คัตเตอร์', 'เครื่องเขียนและแฟ้ม', 0, 'กล่อง', 'อัน', 1, 12, 0, 3, 'assets/images/คัตเตอร์ อัน.jpeg', 'assets/images/คัตเตอร์ กล่อง.png'),
  (33, 'เครื่องเจาะกระดาษ', 'เครื่องเขียนและแฟ้ม', 0, 'กล่อง', 'เครื่อง', 1, 2, 0, 1, 'assets/images/เครื่องเจาะกระดาษ เครื่อง.jpeg', 'assets/images/เครื่องเจาะกระดาษ กล่อง.png'),
  (34, 'ไม้บรรทัด', 'เครื่องเขียนและแฟ้ม', 0, 'กล่อง', 'อัน', 1, 7, 0, 2, 'assets/images/ไม้บรรทัด อัน.jpeg', 'assets/images/ไม้บรรทัด กล่อง.png');

-- 4. ข้อมูลใบคำขอเบิกพัสดุประวัติจริง (เดือน ต.ค. 2569)
INSERT INTO requisitions (id, date, requester, dept, phone, purpose, status, signature, reject_reason, completed_at, completed_date, rejected_at, rejected_date, created_at, updated_at) VALUES
  ('REQ-256910-0001', '1 ต.ค. 2569 09:30 น.', 'อาจารย์ผู้แทน โรงเรียนการเรือน', 'โรงเรียนการเรือน', '', 'ใช้สำหรับการจัดการเรียนการสอนและการสอบปฏิบัติการ ประจำภาคการศึกษา 1/2569', 'COMPLETED', 'ผู้รับพัสดุ: อ.ผู้แทน โรงเรียนการเรือน', '', '2026-10-01 03:00:00', '1 ต.ค. 2569 10:00 น.', NULL, '', '2026-10-01 02:30:00', '2026-10-01 03:00:00'),
  ('REQ-256910-0002', '2 ต.ค. 2569 10:15 น.', 'อาจารย์ผู้แทน คณะพยาบาลศาสตร์', 'คณะพยาบาลศาสตร์', '', 'ใช้สำหรับการสอบประเมินความรู้ทางการพยาบาล ภาคเรียน 1/2569', 'COMPLETED', 'ผู้รับพัสดุ: อ.ผู้แทน คณะพยาบาลศาสตร์', '', '2026-10-02 04:00:00', '2 ต.ค. 2569 11:00 น.', NULL, '', '2026-10-02 03:15:00', '2026-10-02 04:00:00'),
  ('REQ-256910-0003', '5 ต.ค. 2569 13:45 น.', 'อาจารย์ผู้แทน คณะวิทยาศาสตร์และเทคโนโลยี', 'คณะวิทยาศาสตร์และเทคโนโลยี', '', 'ใช้สำหรับการจัดสอบวัดผลภาคบรรยายและปฏิบัติการ ประจำภาคการศึกษา 1/2569', 'COMPLETED', 'ผู้รับพัสดุ: อ.ผู้แทน คณะวิทยาศาสตร์และเทคโนโลยี', '', '2026-10-05 07:30:00', '5 ต.ค. 2569 14:30 น.', NULL, '', '2026-10-05 06:45:00', '2026-10-05 07:30:00');

INSERT INTO requisition_items (requisition_id, item_id, name, qty_boxes, qty_pieces, total_pieces, unit_box, unit_piece, approved_pieces, pieces_per_box_snapshot) VALUES
  ('REQ-256910-0001', 3, 'กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)', 0, 500, 500, 'กล่อง', 'ใบ', 500, 2000),
  ('REQ-256910-0001', 7, 'กระดาษลายเส้น (ห่อละ 500 แผ่น)', 1, 0, 500, 'ห่อ', 'แผ่น', 500, 500),
  ('REQ-256910-0002', 3, 'กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)', 0, 1000, 1000, 'กล่อง', 'ใบ', 1000, 2000),
  ('REQ-256910-0003', 3, 'กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)', 0, 1000, 1000, 'กล่อง', 'ใบ', 1000, 2000);

-- 5. บันทึกความเคลื่อนไหวสต๊อกย้อนหลัง (Audit Trail)
INSERT INTO stock_transactions (item_id, transaction_type, change_pieces, balance_after, reference_type, reference_id, reason, recorded_by, created_at) VALUES
  (3, 'OUT', -500, 34000, 'REQUISITION', 'REQ-256910-0001', 'เบิกจ่ายสำเร็จ (โรงเรียนการเรือน)', 'เจ้าหน้าที่พัสดุ สวท.', '2026-10-01 03:00:00'),
  (3, 'OUT', -1000, 33000, 'REQUISITION', 'REQ-256910-0002', 'เบิกจ่ายสำเร็จ (คณะพยาบาลศาสตร์)', 'เจ้าหน้าที่พัสดุ สวท.', '2026-10-02 04:00:00'),
  (3, 'OUT', -1000, 32000, 'REQUISITION', 'REQ-256910-0003', 'เบิกจ่ายสำเร็จ (คณะวิทยาศาสตร์และเทคโนโลยี)', 'เจ้าหน้าที่พัสดุ สวท.', '2026-10-05 07:30:00'),
  (7, 'OUT', -500, 23000, 'REQUISITION', 'REQ-256910-0001', 'เบิกจ่ายสำเร็จ (โรงเรียนการเรือน)', 'เจ้าหน้าที่พัสดุ สวท.', '2026-10-01 03:00:00');

-- ซิงค์ค่าลำดับ Sequence ให้ต่อเนื่องจากข้อมูลที่กำหนด ID เอง
SELECT setval(pg_get_serial_sequence('departments', 'id'), COALESCE(MAX(id), 1)) FROM departments;
SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE(MAX(id), 1)) FROM users;
SELECT setval(pg_get_serial_sequence('inventory_items', 'id'), COALESCE(MAX(id), 1)) FROM inventory_items;
SELECT setval(pg_get_serial_sequence('requisition_items', 'id'), COALESCE(MAX(id), 1)) FROM requisition_items;
SELECT setval(pg_get_serial_sequence('stock_transactions', 'id'), COALESCE(MAX(id), 1)) FROM stock_transactions;

