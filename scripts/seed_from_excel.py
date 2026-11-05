"""
Seed & Reset SDU Inventory Database from Excel (Option A)
Suan Dusit University e-Inventory & Requisition System (Stock Order SDU)
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

import server

items_34 = [
    {
        "id": 1,
        "name": "ซองเอกสารสีขาว 7´10 (500 ซองต่อกล่อง)",
        "category": "ซองเอกสาร",
        "is_multi_unit": True,
        "unit_box_name": "กล่อง",
        "unit_piece_name": "ซอง",
        "pieces_per_box": 500,
        "on_hand_pieces": 0,
        "reserved_pieces": 0,
        "min_alert": 250,
        "image_piece": "assets/images/ซองเอกสารสีขาว 7´10 (500 ซองต่อกล่อง) ซอง.jpeg",
        "image_box": "assets/images/ซองเอกสารสีขาว 7´10 (500 ซองต่อกล่อง) กล่อง.jpeg"
    },
    {
        "id": 2,
        "name": "ซองเอกสารน้ำตาล (มสด) 9´12.3",
        "category": "ซองเอกสาร",
        "is_multi_unit": True,
        "unit_box_name": "กล่อง",
        "unit_piece_name": "ซอง",
        "pieces_per_box": 500,
        "on_hand_pieces": 0,
        "reserved_pieces": 0,
        "min_alert": 500,
        "image_piece": "assets/images/ซองเอกสารน้ำตาล (มสด) 9´12.3 ซอง.jpeg",
        "image_box": "assets/images/ซองเอกสารน้ำตาล (มสด) 9´12.3 กล่อง.jpeg"
    },
    {
        "id": 3,
        "name": "กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)",
        "category": "กระดาษและแบบฟอร์ม",
        "is_multi_unit": True,
        "unit_box_name": "กล่อง",
        "unit_piece_name": "ใบ",
        "pieces_per_box": 2000,
        "on_hand_pieces": 32000,
        "reserved_pieces": 0,
        "min_alert": 5000,
        "image_piece": "assets/images/กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ) ใบ.jpeg",
        "image_box": "assets/images/กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ) กล่อง.jpeg"
    },
    {
        "id": 4,
        "name": "ซองขยายข้างมีครุฑ 279´432 (กล่องละ 250 ซอง)",
        "category": "ซองเอกสาร",
        "is_multi_unit": True,
        "unit_box_name": "กล่อง",
        "unit_piece_name": "ซอง",
        "pieces_per_box": 250,
        "on_hand_pieces": 1250,
        "reserved_pieces": 0,
        "min_alert": 500,
        "image_piece": "assets/images/ซองขยายข้างมีครุฑ 279´432 (กล่องละ 250 ซอง) ซอง.jpeg",
        "image_box": "assets/images/ซองขยายข้างมีครุฑ 279´432 (กล่องละ 250 ซอง) กล่อง.jpeg"
    },
    {
        "id": 5,
        "name": "กระดาษสติ๊กเกอร์แนวนอน ตัดหน้าซองจดหมาย",
        "category": "กระดาษและแบบฟอร์ม",
        "is_multi_unit": True,
        "unit_box_name": "ซอง",
        "unit_piece_name": "แผ่น",
        "pieces_per_box": 500,
        "on_hand_pieces": 4500,
        "reserved_pieces": 0,
        "min_alert": 500,
        "image_piece": "assets/images/กระดาษสติ๊กเกอร์แนวนอน ตัดหน้าซองจดหมาย แผ่น.jpeg",
        "image_box": "assets/images/กระดาษสติ๊กเกอร์แนวนอน ตัดหน้าซองจดหมาย กล่อง.jpeg"
    },
    {
        "id": 6,
        "name": "กระดาษสติ๊กเกอร์แนวตั้ง ติดหน้าซองข้อสอบ",
        "category": "กระดาษและแบบฟอร์ม",
        "is_multi_unit": True,
        "unit_box_name": "ซอง",
        "unit_piece_name": "แผ่น",
        "pieces_per_box": 500,
        "on_hand_pieces": 500,
        "reserved_pieces": 0,
        "min_alert": 250,
        "image_piece": "assets/images/กระดาษสติ๊กเกอร์แนวตั้ง ติดหน้าซองข้อสอบ แผ่น.png",
        "image_box": "assets/images/กระดาษสติ๊กเกอร์แนวตั้ง ติดหน้าซองข้อสอบ กล่อง.jpeg"
    },
    {
        "id": 7,
        "name": "กระดาษลายเส้น (ห่อละ 500 แผ่น)",
        "category": "กระดาษและแบบฟอร์ม",
        "is_multi_unit": True,
        "unit_box_name": "ห่อ",
        "unit_piece_name": "แผ่น",
        "pieces_per_box": 500,
        "on_hand_pieces": 23000,
        "reserved_pieces": 0,
        "min_alert": 1000,
        "image_piece": "assets/images/กระดาษลายเส้น (ห่อละ 500 แผ่น) แผ่น.jpeg",
        "image_box": "assets/images/กระดาษลายเส้น (ห่อละ 500 แผ่น) กล่อง.jpeg"
    },
    {
        "id": 8,
        "name": "กระดาษสติ๊กเกอร์ เต็มแผ่น",
        "category": "กระดาษและแบบฟอร์ม",
        "is_multi_unit": True,
        "unit_box_name": "ห่อ",
        "unit_piece_name": "แผ่น",
        "pieces_per_box": 500,
        "on_hand_pieces": 0,
        "reserved_pieces": 0,
        "min_alert": 100,
        "image_piece": "assets/images/กระดาษสติ๊กเกอร์ เต็มแผ่น แผ่น.png",
        "image_box": "assets/images/กระดาษสติ๊กเกอร์ เต็มแผ่น กล่อง.jpeg"
    },
    {
        "id": 9,
        "name": "แบบฟอร์มแก้ I",
        "category": "กระดาษและแบบฟอร์ม",
        "is_multi_unit": True,
        "unit_box_name": "กล่อง",
        "unit_piece_name": "ชิ้น",
        "pieces_per_box": 500,
        "on_hand_pieces": 2500,
        "reserved_pieces": 0,
        "min_alert": 500,
        "image_piece": "assets/images/แบบฟอร์มแก้ I ชิ้น.jpeg",
        "image_box": "assets/images/แบบฟอร์มแก้ I กล่อง.jpeg"
    },
    {
        "id": 10,
        "name": "ซองข้อสอบน้ำตาลไม่ขยายข้างพิมพ์ข้อความ (มสด)",
        "category": "ซองเอกสาร",
        "is_multi_unit": True,
        "unit_box_name": "กล่อง",
        "unit_piece_name": "ซอง",
        "pieces_per_box": 250,
        "on_hand_pieces": 3700,
        "reserved_pieces": 0,
        "min_alert": 1000,
        "image_piece": "assets/images/ซองข้อสอบน้ำตาลไม่ขยายข้างพิมพ์ข้อความ (มสด) ซอง.jpeg",
        "image_box": "assets/images/ซองข้อสอบน้ำตาลไม่ขยายข้างพิมพ์ข้อความ (มสด) กล่อง.jpeg"
    },
    {
        "id": 11,
        "name": "ซองเอกสารไม่ขยายข้าง สีน้ำตาล 10´15 นิ้ว (มสด) (กล่องละ 250 ซอง)",
        "category": "ซองเอกสาร",
        "is_multi_unit": True,
        "unit_box_name": "กล่อง",
        "unit_piece_name": "ซอง",
        "pieces_per_box": 250,
        "on_hand_pieces": 1500,
        "reserved_pieces": 0,
        "min_alert": 500,
        "image_piece": "assets/images/ซองเอกสารไม่ขยายข้าง สีน้ำตาล 10´15 นิ้ว (มสด) (กล่องละ 250 ซอง) ซอง.jpeg",
        "image_box": "assets/images/ซองเอกสารไม่ขยายข้าง สีน้ำตาล 10´15 นิ้ว (มสด) (กล่องละ 250 ซอง) กล่อง.jpeg"
    },
    {
        "id": 12,
        "name": "แบบฟอร์มทรานสคริป(ไทย)ป.ตรี ซองละ 500 ใบ",
        "category": "กระดาษและแบบฟอร์ม",
        "is_multi_unit": True,
        "unit_box_name": "ซอง",
        "unit_piece_name": "ใบ",
        "pieces_per_box": 500,
        "on_hand_pieces": 1500,
        "reserved_pieces": 0,
        "min_alert": 300,
        "image_piece": "assets/images/แบบฟอร์มทรานสคริป(ไทย)ป.ตรี ซองละ 500 ใบ ใบ.png",
        "image_box": "assets/images/แบบฟอร์มทรานสคริป(ไทย)ป.ตรี ซองละ 500 ใบ กล่อง.jpeg"
    },
    {
        "id": 13,
        "name": "แบบฟอร์มทรานสคริป(อังกฤษ)ป.ตรี ซองละ 500 ใบ",
        "category": "กระดาษและแบบฟอร์ม",
        "is_multi_unit": True,
        "unit_box_name": "ซอง",
        "unit_piece_name": "ใบ",
        "pieces_per_box": 500,
        "on_hand_pieces": 3500,
        "reserved_pieces": 0,
        "min_alert": 500,
        "image_piece": "assets/images/แบบฟอร์มทรานสคริป(อังกฤษ)ป.ตรี ซองละ 500 ใบ ใบ.jpeg",
        "image_box": "assets/images/แบบฟอร์มทรานสคริป(อังกฤษ)ป.ตรี ซองละ 500 ใบ กล่อง.jpeg"
    },
    {
        "id": 14,
        "name": "ทรานสคริป ป.โท(ไทย) ซองละ 500 ใบ",
        "category": "กระดาษและแบบฟอร์ม",
        "is_multi_unit": True,
        "unit_box_name": "ซอง",
        "unit_piece_name": "ใบ",
        "pieces_per_box": 500,
        "on_hand_pieces": 1000,
        "reserved_pieces": 0,
        "min_alert": 200,
        "image_piece": "assets/images/ทรานสคริป ป.โท(ไทย) ซองละ 500 ใบ ใบ.png",
        "image_box": "assets/images/ทรานสคริป ป.โท(ไทย) ซองละ 500 ใบ กล่อง.png"
    },
    {
        "id": 15,
        "name": "ทรานสคริป ป.โท(อังกฤษ) ซองละ 500 ใบ",
        "category": "กระดาษและแบบฟอร์ม",
        "is_multi_unit": True,
        "unit_box_name": "ซอง",
        "unit_piece_name": "ใบ",
        "pieces_per_box": 500,
        "on_hand_pieces": 1500,
        "reserved_pieces": 0,
        "min_alert": 300,
        "image_piece": "assets/images/ทรานสคริป ป.โท(อังกฤษ) ซองละ 500 ใบ ใบ.png",
        "image_box": "assets/images/ทรานสคริป ป.โท(อังกฤษ) ซองละ 500 ใบ กล่อง.jpeg"
    },
    {
        "id": 16,
        "name": "ใบรับรอง(ไทย)ซองละ 500 ใบ",
        "category": "กระดาษและแบบฟอร์ม",
        "is_multi_unit": True,
        "unit_box_name": "ซอง",
        "unit_piece_name": "ใบ",
        "pieces_per_box": 500,
        "on_hand_pieces": 2000,
        "reserved_pieces": 0,
        "min_alert": 400,
        "image_piece": "assets/images/ใบรับรอง(ไทย)ซองละ 500 ใบ ใบ.jpeg",
        "image_box": "assets/images/ใบรับรอง(ไทย)ซองละ 500 ใบ กล่อง.jpeg"
    },
    {
        "id": 17,
        "name": "ใบรับรอง(อังกฤษ)ซองละ 500 ใบ",
        "category": "กระดาษและแบบฟอร์ม",
        "is_multi_unit": True,
        "unit_box_name": "ซอง",
        "unit_piece_name": "ใบ",
        "pieces_per_box": 500,
        "on_hand_pieces": 3000,
        "reserved_pieces": 0,
        "min_alert": 500,
        "image_piece": "assets/images/ใบรับรอง(อังกฤษ)ซองละ 500 ใบ ใบ.png",
        "image_box": "assets/images/ใบรับรอง(อังกฤษ)ซองละ 500 ใบ กล่อง.png"
    },
    {
        "id": 18,
        "name": "คลิปดำNO.108",
        "category": "เครื่องเขียนและแฟ้ม",
        "is_multi_unit": True,
        "unit_box_name": "ลัง",
        "unit_piece_name": "กล่อง",
        "pieces_per_box": 12,
        "on_hand_pieces": 72,
        "reserved_pieces": 0,
        "min_alert": 24,
        "image_piece": "assets/images/คลิปดำNO.108 กล่อง.jpeg",
        "image_box": "assets/images/คลิปดำNO.108 ลัง.jpeg"
    },
    {
        "id": 19,
        "name": "คลิปดำNO.110",
        "category": "เครื่องเขียนและแฟ้ม",
        "is_multi_unit": True,
        "unit_box_name": "ลัง",
        "unit_piece_name": "กล่อง",
        "pieces_per_box": 12,
        "on_hand_pieces": 60,
        "reserved_pieces": 0,
        "min_alert": 24,
        "image_piece": "assets/images/คลิปดำNO.110 กล่อง.jpeg",
        "image_box": "assets/images/คลิปดำNO.110 ลัง.jpeg"
    },
    {
        "id": 20,
        "name": "ไส้MAX 10 MM",
        "category": "เครื่องเขียนและแฟ้ม",
        "is_multi_unit": True,
        "unit_box_name": "ลัง",
        "unit_piece_name": "กล่อง",
        "pieces_per_box": 20,
        "on_hand_pieces": 20,
        "reserved_pieces": 0,
        "min_alert": 5,
        "image_piece": "assets/images/ไส้MAX 10 MM กล่อง.jpeg",
        "image_box": "assets/images/ไส้MAX 10 MM ลัง.jpeg"
    },
    {
        "id": 21,
        "name": "ไส้MAX 12",
        "category": "เครื่องเขียนและแฟ้ม",
        "is_multi_unit": True,
        "unit_box_name": "ลัง",
        "unit_piece_name": "กล่อง",
        "pieces_per_box": 20,
        "on_hand_pieces": 20,
        "reserved_pieces": 0,
        "min_alert": 5,
        "image_piece": "assets/images/ไส้MAX 12 กล่อง.jpeg",
        "image_box": "assets/images/ไส้MAX 12 ลัง.jpeg"
    },
    {
        "id": 22,
        "name": "ซองกันกระแทก 270´327",
        "category": "ซองเอกสาร",
        "is_multi_unit": True,
        "unit_box_name": "กล่อง",
        "unit_piece_name": "ซอง",
        "pieces_per_box": 80,
        "on_hand_pieces": 2400,
        "reserved_pieces": 0,
        "min_alert": 500,
        "image_piece": "assets/images/ซองกันกระแทก 270´327 ซอง.jpeg",
        "image_box": "assets/images/ซองกันกระแทก 270´327 ซอง.jpeg"
    },
    {
        "id": 23,
        "name": "แฟ้มเสนอ",
        "category": "เครื่องเขียนและแฟ้ม",
        "is_multi_unit": False,
        "unit_box_name": "เล่ม",
        "unit_piece_name": "เล่ม",
        "pieces_per_box": 1,
        "on_hand_pieces": 5,
        "reserved_pieces": 0,
        "min_alert": 5,
        "image_piece": "assets/images/แฟ้มเสนอ เล่ม.jpeg",
        "image_box": "assets/images/แฟ้มเสนอ เล่ม.jpeg"
    },
    {
        "id": 24,
        "name": "แม็กเล็ก",
        "category": "เครื่องเขียนและแฟ้ม",
        "is_multi_unit": False,
        "unit_box_name": "กล่อง",
        "unit_piece_name": "อัน",
        "pieces_per_box": 1,
        "on_hand_pieces": 7,
        "reserved_pieces": 0,
        "min_alert": 2,
        "image_piece": "assets/images/แม็กเล็ก อัน.jpeg",
        "image_box": "assets/images/แม็กเล็ก กล่อง.jpeg"
    },
    {
        "id": 25,
        "name": "แม็กใหญ่",
        "category": "เครื่องเขียนและแฟ้ม",
        "is_multi_unit": False,
        "unit_box_name": "กล่อง",
        "unit_piece_name": "อัน",
        "pieces_per_box": 1,
        "on_hand_pieces": 5,
        "reserved_pieces": 0,
        "min_alert": 2,
        "image_piece": "assets/images/แม็กใหญ่ อัน.jpeg",
        "image_box": "assets/images/แม็กใหญ่ กล่อง.png"
    },
    {
        "id": 26,
        "name": "สก็อตเทปใส",
        "category": "เครื่องเขียนและแฟ้ม",
        "is_multi_unit": True,
        "unit_box_name": "แพ็ค",
        "unit_piece_name": "ม้วน",
        "pieces_per_box": 6,
        "on_hand_pieces": 4,
        "reserved_pieces": 0,
        "min_alert": 6,
        "image_piece": "assets/images/สก็อตเทปใส ม้วน.jpeg",
        "image_box": "assets/images/สก็อตเทปใส กล่อง.jpeg"
    },
    {
        "id": 27,
        "name": "สก็อตเทปขุ่น",
        "category": "เครื่องเขียนและแฟ้ม",
        "is_multi_unit": True,
        "unit_box_name": "แพ็ค",
        "unit_piece_name": "ม้วน",
        "pieces_per_box": 6,
        "on_hand_pieces": 25,
        "reserved_pieces": 0,
        "min_alert": 6,
        "image_piece": "assets/images/สก็อตเทปขุ่น ม้วน.jpeg",
        "image_box": "assets/images/สก็อตเทปขุ่น กล่อง.png"
    },
    {
        "id": 28,
        "name": "สก็อตเทปย่น",
        "category": "เครื่องเขียนและแฟ้ม",
        "is_multi_unit": True,
        "unit_box_name": "แพ็ค",
        "unit_piece_name": "ม้วน",
        "pieces_per_box": 6,
        "on_hand_pieces": 0,
        "reserved_pieces": 0,
        "min_alert": 6,
        "image_piece": "assets/images/สก็อตเทปย่น ม้วน.jpeg",
        "image_box": "assets/images/สก็อตเทปย่น กล่อง.jpeg"
    },
    {
        "id": 29,
        "name": "กาวแท่ง",
        "category": "เครื่องเขียนและแฟ้ม",
        "is_multi_unit": False,
        "unit_box_name": "กล่อง",
        "unit_piece_name": "แท่ง",
        "pieces_per_box": 1,
        "on_hand_pieces": 8,
        "reserved_pieces": 0,
        "min_alert": 5,
        "image_piece": "assets/images/กาวแท่ง แท่ง.jpeg",
        "image_box": "assets/images/กาวแท่ง กล่อง.png"
    },
    {
        "id": 30,
        "name": "กาวขวด",
        "category": "เครื่องเขียนและแฟ้ม",
        "is_multi_unit": False,
        "unit_box_name": "กล่อง",
        "unit_piece_name": "ขวด",
        "pieces_per_box": 1,
        "on_hand_pieces": 4,
        "reserved_pieces": 0,
        "min_alert": 2,
        "image_piece": "assets/images/กาวขวด ขวด.jpeg",
        "image_box": "assets/images/กาวขวด กล่อง.png"
    },
    {
        "id": 31,
        "name": "กรรไกร",
        "category": "เครื่องเขียนและแฟ้ม",
        "is_multi_unit": False,
        "unit_box_name": "กล่อง",
        "unit_piece_name": "อัน",
        "pieces_per_box": 1,
        "on_hand_pieces": 20,
        "reserved_pieces": 0,
        "min_alert": 5,
        "image_piece": "assets/images/กรรไกร อัน.jpeg",
        "image_box": "assets/images/กรรไกร กล่อง.png"
    },
    {
        "id": 32,
        "name": "คัตเตอร์",
        "category": "เครื่องเขียนและแฟ้ม",
        "is_multi_unit": False,
        "unit_box_name": "กล่อง",
        "unit_piece_name": "อัน",
        "pieces_per_box": 1,
        "on_hand_pieces": 12,
        "reserved_pieces": 0,
        "min_alert": 3,
        "image_piece": "assets/images/คัตเตอร์ อัน.jpeg",
        "image_box": "assets/images/คัตเตอร์ กล่อง.png"
    },
    {
        "id": 33,
        "name": "เครื่องเจาะกระดาษ",
        "category": "เครื่องเขียนและแฟ้ม",
        "is_multi_unit": False,
        "unit_box_name": "กล่อง",
        "unit_piece_name": "เครื่อง",
        "pieces_per_box": 1,
        "on_hand_pieces": 2,
        "reserved_pieces": 0,
        "min_alert": 1,
        "image_piece": "assets/images/เครื่องเจาะกระดาษ เครื่อง.jpeg",
        "image_box": "assets/images/เครื่องเจาะกระดาษ กล่อง.png"
    },
    {
        "id": 34,
        "name": "ไม้บรรทัด",
        "category": "เครื่องเขียนและแฟ้ม",
        "is_multi_unit": False,
        "unit_box_name": "กล่อง",
        "unit_piece_name": "อัน",
        "pieces_per_box": 1,
        "on_hand_pieces": 7,
        "reserved_pieces": 0,
        "min_alert": 2,
        "image_piece": "assets/images/ไม้บรรทัด อัน.jpeg",
        "image_box": "assets/images/ไม้บรรทัด กล่อง.png"
    }
]


def seed_database():
    print("Connecting to PostgreSQL...")
    conn = server.get_db_connection()
    try:
        with conn.cursor() as cur:
            print("Clearing old test data...")
            cur.execute("DELETE FROM stock_transactions;")
            cur.execute("DELETE FROM requisition_items;")
            cur.execute("DELETE FROM requisitions;")
            cur.execute("DELETE FROM inventory_items;")

            print("Inserting 34 inventory items aligned with Excel...")
            for it in items_34:
                cur.execute("""
                    INSERT INTO inventory_items (
                        id, name, category, is_multi_unit, unit_box_name, unit_piece_name,
                        pieces_per_box, on_hand_pieces, reserved_pieces, min_alert,
                        image_piece, image_box, is_active
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                """, (
                    it["id"],
                    it["name"],
                    it["category"],
                    1 if it["is_multi_unit"] else 0,
                    it["unit_box_name"],
                    it["unit_piece_name"],
                    it["pieces_per_box"],
                    it["on_hand_pieces"],
                    it["reserved_pieces"],
                    it["min_alert"],
                    it["image_piece"],
                    it["image_box"]
                ))

            print("Inserting 3 real October requisitions (COMPLETED)...")
            # 1. REQ-256910-0001 (โรงเรียนการเรือน 1 ต.ค. 2569)
            cur.execute("""
                INSERT INTO requisitions (
                    id, date, requester, dept, phone, purpose, status, signature,
                    reject_reason, completed_at, completed_date, rejected_at, rejected_date,
                    created_at, updated_at
                ) VALUES (
                    'REQ-256910-0001', '1 ต.ค. 2569 09:30 น.', 'อาจารย์ผู้แทน โรงเรียนการเรือน',
                    'โรงเรียนการเรือน', '', 'ใช้สำหรับการจัดการเรียนการสอนและการสอบปฏิบัติการ ประจำภาคการศึกษา 1/2569',
                    'COMPLETED', 'ผู้รับพัสดุ: อ.ผู้แทน โรงเรียนการเรือน', '',
                    '2026-10-01 03:00:00', '1 ต.ค. 2569 10:00 น.', NULL, '',
                    '2026-10-01 02:30:00', '2026-10-01 03:00:00'
                )
            """)
            cur.execute("""
                INSERT INTO requisition_items (
                    requisition_id, item_id, name, qty_boxes, qty_pieces, total_pieces,
                    unit_box, unit_piece, approved_pieces, pieces_per_box_snapshot
                ) VALUES
                ('REQ-256910-0001', 3, 'กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)', 0, 500, 500, 'กล่อง', 'ใบ', 500, 2000),
                ('REQ-256910-0001', 7, 'กระดาษลายเส้น (ห่อละ 500 แผ่น)', 1, 0, 500, 'ห่อ', 'แผ่น', 500, 500)
            """)

            # 2. REQ-256910-0002 (คณะพยาบาลศาสตร์ 2 ต.ค. 2569)
            cur.execute("""
                INSERT INTO requisitions (
                    id, date, requester, dept, phone, purpose, status, signature,
                    reject_reason, completed_at, completed_date, rejected_at, rejected_date,
                    created_at, updated_at
                ) VALUES (
                    'REQ-256910-0002', '2 ต.ค. 2569 10:15 น.', 'อาจารย์ผู้แทน คณะพยาบาลศาสตร์',
                    'คณะพยาบาลศาสตร์', '', 'ใช้สำหรับการสอบประเมินความรู้ทางการพยาบาล ภาคเรียน 1/2569',
                    'COMPLETED', 'ผู้รับพัสดุ: อ.ผู้แทน คณะพยาบาลศาสตร์', '',
                    '2026-10-02 04:00:00', '2 ต.ค. 2569 11:00 น.', NULL, '',
                    '2026-10-02 03:15:00', '2026-10-02 04:00:00'
                )
            """)
            cur.execute("""
                INSERT INTO requisition_items (
                    requisition_id, item_id, name, qty_boxes, qty_pieces, total_pieces,
                    unit_box, unit_piece, approved_pieces, pieces_per_box_snapshot
                ) VALUES
                ('REQ-256910-0002', 3, 'กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)', 0, 1000, 1000, 'กล่อง', 'ใบ', 1000, 2000)
            """)

            # 3. REQ-256910-0003 (คณะวิทยาศาสตร์และเทคโนโลยี 5 ต.ค. 2569)
            cur.execute("""
                INSERT INTO requisitions (
                    id, date, requester, dept, phone, purpose, status, signature,
                    reject_reason, completed_at, completed_date, rejected_at, rejected_date,
                    created_at, updated_at
                ) VALUES (
                    'REQ-256910-0003', '5 ต.ค. 2569 13:45 น.', 'อาจารย์ผู้แทน คณะวิทยาศาสตร์และเทคโนโลยี',
                    'คณะวิทยาศาสตร์และเทคโนโลยี', '', 'ใช้สำหรับการจัดสอบวัดผลภาคบรรยายและปฏิบัติการ ประจำภาคการศึกษา 1/2569',
                    'COMPLETED', 'ผู้รับพัสดุ: อ.ผู้แทน คณะวิทยาศาสตร์และเทคโนโลยี', '',
                    '2026-10-05 07:30:00', '5 ต.ค. 2569 14:30 น.', NULL, '',
                    '2026-10-05 06:45:00', '2026-10-05 07:30:00'
                )
            """)
            cur.execute("""
                INSERT INTO requisition_items (
                    requisition_id, item_id, name, qty_boxes, qty_pieces, total_pieces,
                    unit_box, unit_piece, approved_pieces, pieces_per_box_snapshot
                ) VALUES
                ('REQ-256910-0003', 3, 'กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)', 0, 1000, 1000, 'กล่อง', 'ใบ', 1000, 2000)
            """)

            print("Inserting stock audit trail transactions (OUT)...")
            # Item 3: กระดาษคำตอบ
            cur.execute("""
                INSERT INTO stock_transactions (
                    item_id, transaction_type, change_pieces, balance_after,
                    reference_type, reference_id, reason, created_at
                ) VALUES
                (3, 'OUT', 500, 34000, 'REQUISITION', 'REQ-256910-0001', 'เบิกจ่ายสำเร็จ (โรงเรียนการเรือน)', '2026-10-01 03:00:00'),
                (3, 'OUT', 1000, 33000, 'REQUISITION', 'REQ-256910-0002', 'เบิกจ่ายสำเร็จ (คณะพยาบาลศาสตร์)', '2026-10-02 04:00:00'),
                (3, 'OUT', 1000, 32000, 'REQUISITION', 'REQ-256910-0003', 'เบิกจ่ายสำเร็จ (คณะวิทยาศาสตร์และเทคโนโลยี)', '2026-10-05 07:30:00'),
                (7, 'OUT', 500, 23000, 'REQUISITION', 'REQ-256910-0001', 'เบิกจ่ายสำเร็จ (โรงเรียนการเรือน)', '2026-10-01 03:00:00')
            """)

            print("Resetting PostgreSQL sequences...")
            cur.execute("SELECT setval(pg_get_serial_sequence('inventory_items', 'id'), 34);")
            cur.execute("SELECT setval(pg_get_serial_sequence('requisition_items', 'id'), COALESCE(MAX(id), 1)) FROM requisition_items;")
            cur.execute("SELECT setval(pg_get_serial_sequence('stock_transactions', 'id'), COALESCE(MAX(id), 1)) FROM stock_transactions;")

        conn.commit()
        print("Database successfully reset and aligned to Excel (Option A)!")
    finally:
        conn.close()


if __name__ == '__main__':
    seed_database()
