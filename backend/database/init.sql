-- ==============================================================================
-- Suan Dusit University - Stock Order SDU (PostgreSQL Initialization Script)
-- ระบบขอเบิกพัสดุและคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต
-- ==============================================================================

-- 1. Create Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Departments Table
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    parent_name VARCHAR(255),
    full_label VARCHAR(300) GENERATED ALWAYS AS (
        CASE 
            WHEN parent_name IS NOT NULL AND parent_name <> '' 
            THEN parent_name || ' - ' || name 
            ELSE name 
        END
    ) STORED
);

-- 3. Inventory Items Table
CREATE TABLE IF NOT EXISTS inventory_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    is_multi_unit BOOLEAN DEFAULT FALSE,
    unit_box_name VARCHAR(50),
    unit_piece_name VARCHAR(50) NOT NULL DEFAULT 'ชิ้น',
    pieces_per_box INT NOT NULL DEFAULT 1 CHECK (pieces_per_box >= 1),
    on_hand_pieces INT NOT NULL DEFAULT 0 CHECK (on_hand_pieces >= 0),
    reserved_pieces INT NOT NULL DEFAULT 0 CHECK (reserved_pieces >= 0),
    min_alert INT NOT NULL DEFAULT 0 CHECK (min_alert >= 0),
    expected_restock_date DATE,
    image_piece VARCHAR(255),
    image_box VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. Requisitions Table
CREATE TABLE IF NOT EXISTS requisitions (
    id VARCHAR(50) PRIMARY KEY,
    dept VARCHAR(255) NOT NULL,
    requester VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    purpose TEXT,
    date_display VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'COMPLETED', 'REJECTED')),
    signature TEXT,
    reject_reason TEXT,
    disbursed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. Requisition Items Table
CREATE TABLE IF NOT EXISTS requisition_items (
    id SERIAL PRIMARY KEY,
    requisition_id VARCHAR(50) NOT NULL REFERENCES requisitions(id) ON DELETE CASCADE,
    item_id INT REFERENCES inventory_items(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    qty_boxes INT NOT NULL DEFAULT 0 CHECK (qty_boxes >= 0),
    qty_pieces INT NOT NULL DEFAULT 0 CHECK (qty_pieces >= 0),
    total_pieces INT NOT NULL CHECK (total_pieces > 0),
    unit_box VARCHAR(50),
    unit_piece VARCHAR(50) NOT NULL DEFAULT 'ชิ้น',
    approved_pieces INT NOT NULL DEFAULT 0 CHECK (approved_pieces >= 0)
);

-- 6. Indexes for High-Performance Queries
CREATE INDEX IF NOT EXISTS idx_inventory_items_category ON inventory_items(category);
CREATE INDEX IF NOT EXISTS idx_requisitions_status ON requisitions(status);
CREATE INDEX IF NOT EXISTS idx_requisitions_requester ON requisitions(requester);
CREATE INDEX IF NOT EXISTS idx_requisition_items_req_id ON requisition_items(requisition_id);

-- 7. Seed Initial Data
INSERT INTO inventory_items (name, category, is_multi_unit, unit_box_name, unit_piece_name, pieces_per_box, on_hand_pieces, reserved_pieces, min_alert, image_piece, image_box)
VALUES
('ซองขยายข้างมีครุฑ 279´432 (กล่องละ 250 ซอง)', 'ซองเอกสาร', TRUE, 'กล่อง', 'ซอง', 250, 1750, 500, 500, 'assets/images/image1.jpeg', 'assets/images/image10.jpeg'),
('กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)', 'กระดาษและแบบฟอร์ม', TRUE, 'กล่อง', 'ใบ', 2000, 34500, 2000, 5000, 'assets/images/image2.jpeg', 'assets/images/image11.jpeg'),
('ซองเอกสารสีขาว 7´10 (500 ซองต่อกล่อง)', 'ซองเอกสาร', TRUE, 'กล่อง', 'ซอง', 500, 1000, 0, 250, 'assets/images/image3.jpeg', 'assets/images/image12.jpeg'),
('กระดาษลายเส้น (ห่อละ 500 แผ่น)', 'กระดาษและแบบฟอร์ม', TRUE, 'ห่อ', 'แผ่น', 500, 23500, 0, 1000, 'assets/images/image4.jpeg', 'assets/images/image13.jpeg'),
('แฟ้มเสนอ', 'เครื่องเขียนและแฟ้ม', FALSE, 'เล่ม', 'เล่ม', 1, 15, 3, 5, 'assets/images/image5.jpeg', 'assets/images/image5.jpeg'),
('ซองเอกสารน้ำตาล (มสด) 9´12.3', 'ซองเอกสาร', TRUE, 'กล่อง', 'ซอง', 500, 1500, 0, 500, 'assets/images/image14.jpeg', 'assets/images/image15.jpeg')
ON CONFLICT DO NOTHING;

