import json
import os

SYSTEM_VERSION = "2.2.0"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPT_DOCX_PATH = os.path.join(PROJECT_ROOT, 'data', 'รายนามบุคลากร สวท.docx')

# Read API_BASE_URL (MySQL REST API endpoint) from .env if available
MYSQL_API_URL = "/api"
env_path = os.path.join(PROJECT_ROOT, '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as ef:
        for line in ef:
            line = line.strip()
            if line.startswith('API_BASE_URL='):
                MYSQL_API_URL = line.split('=', 1)[1].strip().strip('"').strip("'")

def parse_docx_depts_and_users(docx_path):
    import zipfile
    import xml.etree.ElementTree as ET
    units = []
    users = []
    with zipfile.ZipFile(docx_path, 'r') as z:
        root = ET.fromstring(z.read('word/document.xml'))
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    for tr in root.findall('.//w:tr', ns):
        tcs = tr.findall('.//w:tc', ns)
        if len(tcs) < 4:
            continue
        seq_txt = ''.join(tcs[0].itertext()).strip().rstrip('.')
        if not seq_txt.isdigit():
            continue
        fname = ''.join(tcs[1].itertext()).strip()
        lname = ''.join(tcs[2].itertext()).strip()
        full_name = f"{fname} {lname}".strip()
        paras = [''.join(p.itertext()).strip() for p in tcs[3].findall('.//w:p', ns) if ''.join(p.itertext()).strip()]
        pos = paras[0] if paras else ''
        sub = paras[1] if len(paras) > 1 else ''
        if sub == 'และงานทะเบียน':
            pos = pos + sub
            sub = ''

        if 'ผู้อำนวยการ' in pos and not pos.startswith('หัวหน้า'):
            unit = 'สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน'
        elif 'หัวหน้าสำนักงาน' in pos or 'หัวหน้าสำนักงาน' in sub:
            unit = 'สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน'
        elif pos.startswith('หัวหน้า'):
            unit = pos.replace('หัวหน้า', '', 1).strip()
        elif sub.startswith(('กลุ่มงาน', 'หน่วยงาน', 'สำนักงาน')):
            unit = sub
        else:
            unit = 'สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน'

        if unit and unit not in units:
            units.append(unit)

        # User ตั้งต้นเอาเฉพาะ "หัวหน้าหน่วยงาน/กลุ่มงาน" (ส่วนคนอื่นให้ Staff เพิ่มทีหลังได้)
        if pos.startswith('หัวหน้า'):
            users.append({
                "id": len(users) + 1,
                "name": full_name,
                "position": pos,
                "dept": unit,
                "phone": ""
            })

    preferred_order = [
        'สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน',
        'กลุ่มงานส่งเสริมวิชาการ',
        'กลุ่มงานบริการวิชาการ',
        'กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ',
        'หน่วยงานศึกษาทั่วไปและการเรียนรู้ตลอดชีวิต'
    ]
    ordered_units = [u for u in preferred_order if u in units] + [u for u in units if u not in preferred_order]
    return {"สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)": ordered_units}, users

depts_data, initial_users = parse_docx_depts_and_users(DEPT_DOCX_PATH)

# Build department data array for JS (5 units from รายนามบุคลากร สวท.docx)
dept_js_items = []
for cat_name, unit_list in depts_data.items():
    cat_items = []
    for unit_name in unit_list:
        cat_items.append({
            "label": unit_name,
            "value": unit_name,
            "sub": False
        })
    dept_js_items.append({
        "category": cat_name,
        "items": cat_items
    })

dept_json_str = json.dumps(dept_js_items, ensure_ascii=False, indent=2)
users_json_str = json.dumps(initial_users, ensure_ascii=False, indent=2)

# Common SVG vector icons
svg_icons = {
    "box": '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>',
    "cart": '<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg>',
    "clipboard": '<svg class="svg-icon" viewBox="0 0 24 24"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg>',
    "chart": '<svg class="svg-icon" viewBox="0 0 24 24"><line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/><line x1="2" x2="22" y1="20" y2="20"/></svg>',
    "file_text": '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>',
    "building": '<svg class="svg-icon" viewBox="0 0 24 24"><line x1="3" x2="21" y1="22" y2="22"/><line x1="6" x2="6" y1="18" y2="11"/><line x1="10" x2="10" y1="18" y2="11"/><line x1="14" x2="14" y1="18" y2="11"/><line x1="18" x2="18" y1="18" y2="11"/><polygon points="12 2 20 7 4 7"/></svg>',
    "user": '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "phone": '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>',
    "search": '<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
    "layers": '<svg class="svg-icon" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
    "tag": '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94.94-2.48 0-3.42L12 2Z"/><circle cx="7" cy="7" r=".5" fill="currentColor"/></svg>',
    "pen_tool": '<svg class="svg-icon" viewBox="0 0 24 24"><path d="m18 2 4 4-12 12H6v-4L18 2z"/><path d="m15 5 4 4"/><path d="M2 22h20"/></svg>',
    "printer": '<svg class="svg-icon" viewBox="0 0 24 24"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect width="12" height="8" x="6" y="14"/></svg>',
    "check": '<svg class="svg-icon" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>',
    "check_circle": '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    "x": '<svg class="svg-icon" viewBox="0 0 24 24"><line x1="18" x2="6" y1="6" y2="18"/><line x1="6" x2="18" y1="6" y2="18"/></svg>',
    "chevron_down": '<svg class="svg-icon svg-icon-sm" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></svg>',
    "trash": '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>',
    "upload": '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>',
    "plus": '<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="16"/><line x1="8" x2="16" y1="12" y2="12"/></svg>',
    "alert_triangle": '<svg class="svg-icon" viewBox="0 0 24 24"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>',
    "clock": '<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "calendar": '<svg class="svg-icon" viewBox="0 0 24 24"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>',
    "eye": '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>',
    "arrow_left": '<svg class="svg-icon" viewBox="0 0 24 24"><line x1="19" x2="5" y1="12" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>',
    "edit": '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>',
    "lock": '<svg class="svg-icon" viewBox="0 0 24 24"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
    "log_out": '<svg class="svg-icon svg-icon-sm" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>',
    "info": '<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="16" y2="12"/><line x1="12" x2="12.01" y1="8" y2="8"/></svg>',
    "list": '<svg class="svg-icon" viewBox="0 0 24 24"><line x1="8" x2="21" y1="6" y2="6"/><line x1="8" x2="21" y1="12" y2="12"/><line x1="8" x2="21" y1="18" y2="18"/><line x1="3" x2="3.01" y1="6" y2="6"/><line x1="3" x2="3.01" y1="12" y2="12"/><line x1="3" x2="3.01" y1="18" y2="18"/></svg>'
}

# Shared Database Initial Data (34 Stock Items with 58 Real Images from ยอดสต๊อก ตค.xlsx)
initial_items = [
  {"id": 1, "name": "ซองขยายข้างมีครุฑ 279´432 (กล่องละ 250 ซอง)", "category": "ซองเอกสาร", "is_multi_unit": True, "unit_box_name": "กล่อง", "unit_piece_name": "ซอง", "pieces_per_box": 250, "on_hand_pieces": 1750, "reserved_pieces": 500, "min_alert": 500, "image_piece": "assets/images/ซองขยายข้างมีครุฑ 279´432 (กล่องละ 250 ซอง) ซอง.jpeg", "image_box": "assets/images/ซองขยายข้างมีครุฑ 279´432 (กล่องละ 250 ซอง) กล่อง.jpeg"},
  {"id": 2, "name": "กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "กล่อง", "unit_piece_name": "ใบ", "pieces_per_box": 2000, "on_hand_pieces": 34500, "reserved_pieces": 2000, "min_alert": 5000, "image_piece": "assets/images/กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ) ใบ.jpeg", "image_box": "assets/images/กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ) กล่อง.jpeg"},
  {"id": 3, "name": "ซองเอกสารสีขาว 7´10 (500 ซองต่อกล่อง)", "category": "ซองเอกสาร", "is_multi_unit": True, "unit_box_name": "กล่อง", "unit_piece_name": "ซอง", "pieces_per_box": 500, "on_hand_pieces": 1000, "reserved_pieces": 0, "min_alert": 250, "image_piece": "assets/images/ซองเอกสารสีขาว 7´10 (500 ซองต่อกล่อง) ซอง.jpeg", "image_box": "assets/images/ซองเอกสารสีขาว 7´10 (500 ซองต่อกล่อง) กล่อง.jpeg"},
  {"id": 4, "name": "กระดาษลายเส้น (ห่อละ 500 แผ่น)", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ห่อ", "unit_piece_name": "แผ่น", "pieces_per_box": 500, "on_hand_pieces": 23500, "reserved_pieces": 0, "min_alert": 1000, "image_piece": "assets/images/กระดาษลายเส้น (ห่อละ 500 แผ่น) แผ่น.jpeg", "image_box": "assets/images/กระดาษลายเส้น (ห่อละ 500 แผ่น) กล่อง.jpeg"},
  {"id": 5, "name": "แฟ้มเสนอ", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "เล่ม", "unit_piece_name": "เล่ม", "pieces_per_box": 1, "on_hand_pieces": 15, "reserved_pieces": 3, "min_alert": 5, "image_piece": "assets/images/แฟ้มเสนอ เล่ม.jpeg", "image_box": "assets/images/แฟ้มเสนอ เล่ม.jpeg"},
  {"id": 6, "name": "ซองเอกสารน้ำตาล (มสด) 9´12.3", "category": "ซองเอกสาร", "is_multi_unit": True, "unit_box_name": "กล่อง", "unit_piece_name": "ซอง", "pieces_per_box": 500, "on_hand_pieces": 1500, "reserved_pieces": 0, "min_alert": 500, "image_piece": "assets/images/ซองเอกสารน้ำตาล (มสด) 9´12.3 ซอง.jpeg", "image_box": "assets/images/ซองเอกสารน้ำตาล (มสด) 9´12.3 กล่อง.jpeg"},
  {"id": 7, "name": "กระดาษสติ๊กเกอร์แนวนอน ตัดหน้าซองจดหมาย", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ซอง", "unit_piece_name": "แผ่น", "pieces_per_box": 500, "on_hand_pieces": 4500, "reserved_pieces": 0, "min_alert": 500, "image_piece": "assets/images/กระดาษสติ๊กเกอร์แนวนอน ตัดหน้าซองจดหมาย แผ่น.jpeg", "image_box": "assets/images/กระดาษสติ๊กเกอร์แนวนอน ตัดหน้าซองจดหมาย กล่อง.jpeg"},
  {"id": 8, "name": "กระดาษสติ๊กเกอร์แนวตั้ง ติดหน้าซองข้อสอบ", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ซอง", "unit_piece_name": "แผ่น", "pieces_per_box": 500, "on_hand_pieces": 1000, "reserved_pieces": 0, "min_alert": 250, "image_piece": "assets/images/กระดาษสติ๊กเกอร์แนวตั้ง ติดหน้าซองข้อสอบ แผ่น.png", "image_box": "assets/images/กระดาษสติ๊กเกอร์แนวตั้ง ติดหน้าซองข้อสอบ กล่อง.jpeg"},
  {"id": 9, "name": "กระดาษสติ๊กเกอร์ เต็มแผ่น", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ห่อ", "unit_piece_name": "แผ่น", "pieces_per_box": 500, "on_hand_pieces": 500, "reserved_pieces": 0, "min_alert": 100, "image_piece": "assets/images/กระดาษสติ๊กเกอร์ เต็มแผ่น แผ่น.png", "image_box": "assets/images/กระดาษสติ๊กเกอร์ เต็มแผ่น กล่อง.jpeg"},
  {"id": 10, "name": "แบบฟอร์มแก้ I", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "กล่อง", "unit_piece_name": "ชิ้น", "pieces_per_box": 500, "on_hand_pieces": 2500, "reserved_pieces": 0, "min_alert": 500, "image_piece": "assets/images/แบบฟอร์มแก้ I ชิ้น.jpeg", "image_box": "assets/images/แบบฟอร์มแก้ I กล่อง.jpeg"},
  {"id": 11, "name": "ซองข้อสอบน้ำตาลไม่ขยายข้างพิมพ์ข้อความ (มสด)", "category": "ซองเอกสาร", "is_multi_unit": True, "unit_box_name": "กล่อง", "unit_piece_name": "ซอง", "pieces_per_box": 250, "on_hand_pieces": 4000, "reserved_pieces": 0, "min_alert": 1000, "image_piece": "assets/images/ซองข้อสอบน้ำตาลไม่ขยายข้างพิมพ์ข้อความ (มสด) ซอง.jpeg", "image_box": "assets/images/ซองข้อสอบน้ำตาลไม่ขยายข้างพิมพ์ข้อความ (มสด) กล่อง.jpeg"},
  {"id": 12, "name": "ซองเอกสารไม่ขยายข้าง สีน้ำตาล 10´15 นิ้ว (มสด) (กล่องละ 250 ซอง)", "category": "ซองเอกสาร", "is_multi_unit": True, "unit_box_name": "กล่อง", "unit_piece_name": "ซอง", "pieces_per_box": 250, "on_hand_pieces": 1500, "reserved_pieces": 0, "min_alert": 500, "image_piece": "assets/images/ซองเอกสารไม่ขยายข้าง สีน้ำตาล 10´15 นิ้ว (มสด) (กล่องละ 250 ซอง) ซอง.jpeg", "image_box": "assets/images/ซองเอกสารไม่ขยายข้าง สีน้ำตาล 10´15 นิ้ว (มสด) (กล่องละ 250 ซอง) กล่อง.jpeg"},
  {"id": 13, "name": "แบบฟอร์มทรานสคริป(ไทย)ป.ตรี ซองละ 500 ใบ", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ซอง", "unit_piece_name": "ใบ", "pieces_per_box": 500, "on_hand_pieces": 1500, "reserved_pieces": 0, "min_alert": 300, "image_piece": "assets/images/แบบฟอร์มทรานสคริป(ไทย)ป.ตรี ซองละ 500 ใบ ใบ.png", "image_box": "assets/images/แบบฟอร์มทรานสคริป(ไทย)ป.ตรี ซองละ 500 ใบ กล่อง.jpeg"},
  {"id": 14, "name": "แบบฟอร์มทรานสคริป(อังกฤษ)ป.ตรี ซองละ 500 ใบ", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ซอง", "unit_piece_name": "ใบ", "pieces_per_box": 500, "on_hand_pieces": 3500, "reserved_pieces": 0, "min_alert": 500, "image_piece": "assets/images/แบบฟอร์มทรานสคริป(อังกฤษ)ป.ตรี ซองละ 500 ใบ ใบ.jpeg", "image_box": "assets/images/แบบฟอร์มทรานสคริป(อังกฤษ)ป.ตรี ซองละ 500 ใบ กล่อง.jpeg"},
  {"id": 15, "name": "ทรานสคริป ป.โท(ไทย) ซองละ 500 ใบ", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ซอง", "unit_piece_name": "ใบ", "pieces_per_box": 500, "on_hand_pieces": 1000, "reserved_pieces": 0, "min_alert": 200, "image_piece": "assets/images/ทรานสคริป ป.โท(ไทย) ซองละ 500 ใบ ใบ.png", "image_box": "assets/images/ทรานสคริป ป.โท(ไทย) ซองละ 500 ใบ กล่อง.png"},
  {"id": 16, "name": "ทรานสคริป ป.โท(อังกฤษ) ซองละ 500 ใบ", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ซอง", "unit_piece_name": "ใบ", "pieces_per_box": 500, "on_hand_pieces": 1500, "reserved_pieces": 0, "min_alert": 300, "image_piece": "assets/images/ทรานสคริป ป.โท(อังกฤษ) ซองละ 500 ใบ ใบ.png", "image_box": "assets/images/ทรานสคริป ป.โท(อังกฤษ) ซองละ 500 ใบ กล่อง.jpeg"},
  {"id": 17, "name": "ใบรับรอง(ไทย)ซองละ 500 ใบ", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ซอง", "unit_piece_name": "ใบ", "pieces_per_box": 500, "on_hand_pieces": 2000, "reserved_pieces": 0, "min_alert": 400, "image_piece": "assets/images/ใบรับรอง(ไทย)ซองละ 500 ใบ ใบ.jpeg", "image_box": "assets/images/ใบรับรอง(ไทย)ซองละ 500 ใบ กล่อง.jpeg"},
  {"id": 18, "name": "ใบรับรอง(อังกฤษ)ซองละ 500 ใบ", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ซอง", "unit_piece_name": "ใบ", "pieces_per_box": 500, "on_hand_pieces": 3500, "reserved_pieces": 0, "min_alert": 500, "image_piece": "assets/images/ใบรับรอง(อังกฤษ)ซองละ 500 ใบ ใบ.png", "image_box": "assets/images/ใบรับรอง(อังกฤษ)ซองละ 500 ใบ กล่อง.png"},
  {"id": 19, "name": "คลิปดำNO.108", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": True, "unit_box_name": "ลัง", "unit_piece_name": "กล่อง", "pieces_per_box": 12, "on_hand_pieces": 72, "reserved_pieces": 0, "min_alert": 24, "image_piece": "assets/images/คลิปดำNO.108 กล่อง.jpeg", "image_box": "assets/images/คลิปดำNO.108 ลัง.jpeg"},
  {"id": 20, "name": "คลิปดำNO.110", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": True, "unit_box_name": "ลัง", "unit_piece_name": "กล่อง", "pieces_per_box": 12, "on_hand_pieces": 60, "reserved_pieces": 0, "min_alert": 24, "image_piece": "assets/images/คลิปดำNO.110 กล่อง.jpeg", "image_box": "assets/images/คลิปดำNO.110 ลัง.jpeg"},
  {"id": 21, "name": "ไส้MAX 10 MM", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": True, "unit_box_name": "ลัง", "unit_piece_name": "กล่อง", "pieces_per_box": 20, "on_hand_pieces": 20, "reserved_pieces": 0, "min_alert": 5, "image_piece": "assets/images/ไส้MAX 10 MM กล่อง.jpeg", "image_box": "assets/images/ไส้MAX 10 MM ลัง.jpeg"},
  {"id": 22, "name": "ไส้MAX 12", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": True, "unit_box_name": "ลัง", "unit_piece_name": "กล่อง", "pieces_per_box": 20, "on_hand_pieces": 20, "reserved_pieces": 0, "min_alert": 5, "image_piece": "assets/images/ไส้MAX 12 กล่อง.jpeg", "image_box": "assets/images/ไส้MAX 12 ลัง.jpeg"},
  {"id": 23, "name": "ซองกันกระแทก 270´327", "category": "ซองเอกสาร", "is_multi_unit": True, "unit_box_name": "กล่อง", "unit_piece_name": "ซอง", "pieces_per_box": 80, "on_hand_pieces": 2400, "reserved_pieces": 0, "min_alert": 500, "image_piece": "assets/images/ซองกันกระแทก 270´327 ซอง.jpeg", "image_box": "assets/images/ซองกันกระแทก 270´327 ซอง.jpeg"},
  {"id": 24, "name": "แม็กเล็ก", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "กล่อง", "unit_piece_name": "อัน", "pieces_per_box": 1, "on_hand_pieces": 7, "reserved_pieces": 0, "min_alert": 2, "image_piece": "assets/images/แม็กเล็ก อัน.jpeg", "image_box": "assets/images/แม็กเล็ก กล่อง.jpeg"},
  {"id": 25, "name": "แม็กใหญ่", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "กล่อง", "unit_piece_name": "อัน", "pieces_per_box": 1, "on_hand_pieces": 5, "reserved_pieces": 0, "min_alert": 2, "image_piece": "assets/images/แม็กใหญ่ อัน.jpeg", "image_box": "assets/images/แม็กใหญ่ กล่อง.png"},
  {"id": 26, "name": "สก็อตเทปใส", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": True, "unit_box_name": "แพ็ค", "unit_piece_name": "ม้วน", "pieces_per_box": 6, "on_hand_pieces": 24, "reserved_pieces": 0, "min_alert": 6, "image_piece": "assets/images/สก็อตเทปใส ม้วน.jpeg", "image_box": "assets/images/สก็อตเทปใส กล่อง.jpeg"},
  {"id": 27, "name": "สก็อตเทปขุ่น", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": True, "unit_box_name": "แพ็ค", "unit_piece_name": "ม้วน", "pieces_per_box": 6, "on_hand_pieces": 27, "reserved_pieces": 0, "min_alert": 6, "image_piece": "assets/images/สก็อตเทปขุ่น ม้วน.jpeg", "image_box": "assets/images/สก็อตเทปขุ่น กล่อง.png"},
  {"id": 28, "name": "สก็อตเทปย่น", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": True, "unit_box_name": "แพ็ค", "unit_piece_name": "ม้วน", "pieces_per_box": 6, "on_hand_pieces": 10, "reserved_pieces": 0, "min_alert": 6, "image_piece": "assets/images/สก็อตเทปย่น ม้วน.jpeg", "image_box": "assets/images/สก็อตเทปย่น กล่อง.jpeg"},
  {"id": 29, "name": "กาวแท่ง", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "กล่อง", "unit_piece_name": "แท่ง", "pieces_per_box": 1, "on_hand_pieces": 22, "reserved_pieces": 0, "min_alert": 5, "image_piece": "assets/images/กาวแท่ง แท่ง.jpeg", "image_box": "assets/images/กาวแท่ง กล่อง.png"},
  {"id": 30, "name": "กาวขวด", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "กล่อง", "unit_piece_name": "ขวด", "pieces_per_box": 1, "on_hand_pieces": 6, "reserved_pieces": 0, "min_alert": 2, "image_piece": "assets/images/กาวขวด ขวด.jpeg", "image_box": "assets/images/กาวขวด กล่อง.png"},
  {"id": 31, "name": "กรรไกร", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "กล่อง", "unit_piece_name": "อัน", "pieces_per_box": 1, "on_hand_pieces": 20, "reserved_pieces": 0, "min_alert": 5, "image_piece": "assets/images/กรรไกร อัน.jpeg", "image_box": "assets/images/กรรไกร กล่อง.png"},
  {"id": 32, "name": "คัตเตอร์", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "กล่อง", "unit_piece_name": "อัน", "pieces_per_box": 1, "on_hand_pieces": 12, "reserved_pieces": 0, "min_alert": 3, "image_piece": "assets/images/คัตเตอร์ อัน.jpeg", "image_box": "assets/images/คัตเตอร์ กล่อง.png"},
  {"id": 33, "name": "เครื่องเจาะกระดาษ", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "กล่อง", "unit_piece_name": "เครื่อง", "pieces_per_box": 1, "on_hand_pieces": 2, "reserved_pieces": 0, "min_alert": 1, "image_piece": "assets/images/เครื่องเจาะกระดาษ เครื่อง.jpeg", "image_box": "assets/images/เครื่องเจาะกระดาษ กล่อง.png"},
  {"id": 34, "name": "ไม้บรรทัด", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "กล่อง", "unit_piece_name": "อัน", "pieces_per_box": 1, "on_hand_pieces": 7, "reserved_pieces": 0, "min_alert": 2, "image_piece": "assets/images/ไม้บรรทัด อัน.jpeg", "image_box": "assets/images/ไม้บรรทัด กล่อง.png"}
]

initial_requisitions = [
  {
    "id": "REQ-256910-0042",
    "dept": "สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน",
    "requester": "นางสาววาสนา จันทร์จ่าย",
    "phone": "081-998-7766",
    "purpose": "ใช้สำหรับการจัดการเรียนการสอนและสอบปฏิบัติการ ภาคเรียน 1/2569",
    "date": "21 ต.ค. 2569 10:15 น.",
    "status": "APPROVED",
    "signature": None,
    "reject_reason": "",
    "created_at": "2026-10-21T03:15:00.000Z",
    "updated_at": "2026-10-21T03:30:00.000Z",
    "items": [
      { "itemId": 1, "name": "ซองขยายข้างมีครุฑ 279´432", "qtyBoxes": 2, "qtyPieces": 0, "totalPieces": 500, "unitBox": "กล่อง", "unitPiece": "ซอง", "approvedPieces": 500, "piecesPerBoxSnapshot": 250 },
      { "itemId": 2, "name": "กระดาษคำตอบ", "qtyBoxes": 1, "qtyPieces": 0, "totalPieces": 2000, "unitBox": "กล่อง", "unitPiece": "ใบ", "approvedPieces": 2000, "piecesPerBoxSnapshot": 2000 },
      { "itemId": 5, "name": "แฟ้มเสนอ", "qtyBoxes": 0, "qtyPieces": 3, "totalPieces": 3, "unitBox": "เล่ม", "unitPiece": "เล่ม", "approvedPieces": 3, "piecesPerBoxSnapshot": 1 }
    ]
  },
  {
    "id": "REQ-256910-0043",
    "dept": "กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ",
    "requester": "นางสาวสินีนาฎ ลักษณะโยธิน",
    "phone": "089-112-3344",
    "purpose": "เตรียมเอกสารรับรองและบริการการศึกษา ภาคเรียน 1/2569",
    "date": "21 ต.ค. 2569 10:45 น.",
    "status": "PENDING",
    "signature": None,
    "reject_reason": "",
    "created_at": "2026-10-21T03:45:00.000Z",
    "updated_at": "2026-10-21T03:45:00.000Z",
    "items": [
      { "itemId": 3, "name": "ซองเอกสารสีขาว 7´10", "qtyBoxes": 1, "qtyPieces": 0, "totalPieces": 500, "unitBox": "กล่อง", "unitPiece": "ซอง", "approvedPieces": 500, "piecesPerBoxSnapshot": 500 },
      { "itemId": 4, "name": "กระดาษลายเส้น", "qtyBoxes": 2, "qtyPieces": 0, "totalPieces": 1000, "unitBox": "ห่อ", "unitPiece": "แผ่น", "approvedPieces": 1000, "piecesPerBoxSnapshot": 500 }
    ]
  }
]

# Official Vector Emblem for PDF (SVG)
pdf_seal_svg = '''
<svg class="pdf-vector-seal" viewBox="0 0 100 100" width="70" height="70" fill="none" stroke="#991b1b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="50" cy="50" r="45" stroke-dasharray="3 3"/>
  <circle cx="50" cy="50" r="40"/>
  <path d="M50 18 L70 32 L70 56 L50 78 L30 56 L30 32 Z" fill="#fef2f2"/>
  <line x1="38" x2="62" y1="46" y2="46"/>
  <line x1="42" x2="58" y1="52" y2="52"/>
  <line x1="46" x2="54" y1="58" y2="58"/>
  <polygon points="50,26 54,36 64,36 56,42 59,52 50,46 41,52 44,42 36,36 46,36" fill="#991b1b" stroke="none"/>
</svg>
'''

# Common CSS tokens
common_css = '''
    :root {
      --primary: #1e40af;
      --primary-hover: #1d4ed8;
      --primary-light: #eff6ff;
      --primary-border: #bfdbfe;
      --accent: #059669;
      --accent-hover: #047857;
      --warning: #d97706;
      --warning-light: #fef3c7;
      --danger: #dc2626;
      --danger-light: #fee2e2;
      --neutral-50: #f8fafc;
      --neutral-100: #f1f5f9;
      --neutral-200: #e2e8f0;
      --neutral-300: #cbd5e1;
      --neutral-400: #94a3b8;
      --neutral-600: #475569;
      --neutral-700: #334155;
      --neutral-800: #1e293b;
      --neutral-900: #0f172a;
      --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
      --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
      --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
      --radius: 10px;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Prompt', 'Sarabun', sans-serif;
      background-color: var(--neutral-50);
      color: var(--neutral-800);
      line-height: 1.5;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    .svg-icon {
      display: inline-block;
      width: 1.15rem;
      height: 1.15rem;
      stroke-width: 2;
      stroke: currentColor;
      fill: none;
      stroke-linecap: round;
      stroke-linejoin: round;
      vertical-align: -0.15em;
      flex-shrink: 0;
    }
    .svg-icon-lg { width: 1.6rem; height: 1.6rem; }
    .svg-icon-sm { width: 0.95rem; height: 0.95rem; }

    header {
      background: white;
      border-bottom: 1px solid var(--neutral-200);
      position: sticky;
      top: 0;
      z-index: 40;
      box-shadow: var(--shadow-sm);
    }

    .nav-container {
      max-width: 1380px;
      margin: 0 auto;
      padding: 0.75rem 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }

    .brand { display: flex; align-items: center; gap: 0.85rem; }
    .brand-logo-img {
      height: 48px;
      width: auto;
      object-fit: contain;
      filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.08));
      transition: transform 0.2s ease;
    }
    .brand-logo-img:hover { transform: scale(1.04); }
    .brand-icon {
      width: 42px;
      height: 42px;
      background: linear-gradient(135deg, var(--primary), #3b82f6);
      color: white;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25);
    }
    .brand-text h1 { font-size: 1.15rem; font-weight: 700; color: var(--neutral-900); line-height: 1.2; }
    .brand-text p { font-size: 0.8rem; color: var(--neutral-400); }

    main {
      max-width: 1380px;
      margin: 1.5rem auto;
      padding: 0 1.5rem;
      flex: 1;
      width: 100%;
    }

    .btn {
      padding: 0.5rem 1rem;
      border-radius: 8px;
      font-family: inherit;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      border: 1px solid transparent;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.2s;
    }
    .btn-outline { background: white; border-color: var(--neutral-300); color: var(--neutral-700); }
    .btn-outline:hover { background: var(--neutral-50); border-color: var(--neutral-400); }
    .btn-primary { background: var(--primary); color: white; }
    .btn-primary:hover { background: var(--primary-hover); }
    .btn-success { background: var(--accent); color: white; }
    .btn-success:hover { background: var(--accent-hover); }
    .btn-danger { background: var(--danger); color: white; }

    /* Modal Styles */
    .modal-overlay {
      position: fixed; inset: 0;
      background: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(3px);
      z-index: 100;
      display: flex; align-items: center; justify-content: center;
      padding: 1.5rem;
      opacity: 0; pointer-events: none;
      transition: opacity 0.25s;
    }
    .modal-overlay.open { opacity: 1; pointer-events: auto; }
    .modal-card {
      background: white; border-radius: 12px;
      width: 100%; max-width: 540px;
      box-shadow: var(--shadow-lg);
      overflow: hidden; display: flex; flex-direction: column;
      transform: scale(0.95); transition: transform 0.25s;
    }
    .modal-overlay.open .modal-card { transform: scale(1); }
    .modal-header {
      padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--neutral-200);
      display: flex; justify-content: space-between; align-items: center;
    }
    .modal-header h3 { font-size: 1.15rem; font-weight: 700; color: var(--neutral-900); display: flex; align-items: center; gap: 0.5rem; }
    .modal-body { padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; }
    .modal-footer {
      padding: 1rem 1.5rem; background: var(--neutral-50);
      border-top: 1px solid var(--neutral-200);
      display: flex; justify-content: flex-end; gap: 0.75rem;
    }
    .close-btn { background: none; border: none; color: var(--neutral-400); cursor: pointer; padding: 4px; display: flex; align-items: center; border-radius: 6px; }
    .close-btn:hover { color: var(--neutral-800); background: var(--neutral-100); }

    /* Combobox Styles */
    .custom-combobox-wrapper { position: relative; }
    .combobox-control { position: relative; display: flex; align-items: center; }
    .combobox-input { width: 100%; padding-right: 2.4rem; cursor: text; }
    .combobox-toggle-btn {
      position: absolute; right: 0.5rem; background: none; border: none;
      color: var(--neutral-400); cursor: pointer; padding: 4px; display: flex; align-items: center;
      transition: transform 0.2s;
    }
    .combobox-control.open .combobox-toggle-btn { transform: rotate(180deg); }
    .combobox-dropdown {
      position: absolute; top: calc(100% + 4px); left: 0; right: 0;
      background: white; border: 1px solid var(--neutral-300); border-radius: 8px;
      max-height: 310px; overflow-y: auto; box-shadow: var(--shadow-lg);
      z-index: 60; display: none;
    }
    .combobox-dropdown.open { display: block; animation: fadeIn 0.15s ease-out; }
    .combobox-group-title {
      padding: 8px 12px 4px 12px; font-size: 0.75rem; font-weight: 700;
      color: var(--primary); background: var(--neutral-50);
      border-top: 1px solid var(--neutral-200); border-bottom: 1px solid var(--neutral-200);
      position: sticky; top: 0; z-index: 2;
    }
    .combobox-group-title:first-child { border-top: none; }
    .combobox-item {
      padding: 8px 14px; font-size: 0.875rem; color: var(--neutral-800);
      cursor: pointer; transition: background 0.15s;
      display: flex; align-items: center; justify-content: space-between;
    }
    .combobox-item:hover { background: var(--primary-light); color: var(--primary); }
    .combobox-item.selected { background: #eff6ff; font-weight: 600; color: var(--primary); }
    .combobox-item-sub { padding-left: 28px; color: var(--neutral-600); font-size: 0.825rem; border-left: 2px solid var(--neutral-200); margin-left: 14px; }
    .combobox-item-sub:hover { border-left-color: var(--primary); }
    .combobox-no-results { padding: 1.25rem 1rem; text-align: center; color: var(--neutral-400); font-size: 0.85rem; }

    .form-group { display: flex; flex-direction: column; gap: 0.4rem; }
    .form-group label { font-size: 0.85rem; font-weight: 600; color: var(--neutral-700); display: flex; align-items: center; gap: 0.4rem; }
    .form-control {
      padding: 0.6rem 0.85rem; border: 1px solid var(--neutral-300); border-radius: 8px;
      font-family: inherit; font-size: 0.9rem; outline: none; transition: border-color 0.2s, box-shadow 0.2s; background: white;
    }
    .form-control:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15); }

    /* SweetAlert2 SDU Theme Customization */
    .swal2-popup {
      font-family: 'Prompt', 'Sarabun', sans-serif !important;
      border-radius: 14px !important;
      padding: 1.75rem 1.5rem !important;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
    }
    .swal2-title {
      font-family: 'Prompt', sans-serif !important;
      font-size: 1.35rem !important;
      font-weight: 700 !important;
      color: #0f172a !important;
    }
    .swal2-html-container {
      font-family: 'Prompt', 'Sarabun', sans-serif !important;
      font-size: 0.95rem !important;
      color: #475569 !important;
      line-height: 1.6 !important;
    }
    .swal2-confirm {
      font-family: 'Prompt', sans-serif !important;
      border-radius: 8px !important;
      font-weight: 600 !important;
      font-size: 0.95rem !important;
      padding: 0.6rem 1.5rem !important;
    }
    .swal2-cancel {
      font-family: 'Prompt', sans-serif !important;
      border-radius: 8px !important;
      font-weight: 500 !important;
      font-size: 0.95rem !important;
      padding: 0.6rem 1.25rem !important;
    }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

    /* Official PDF Requisition Slip Styles */
    .pdf-preview-container { background: #525659; padding: 2rem; border-radius: 12px; display: flex; flex-direction: column; align-items: center; gap: 1.5rem; }
    .pdf-page { background: white; width: 100%; max-width: 800px; padding: 2.8rem 3.2rem; box-shadow: 0 10px 25px rgba(0,0,0,0.3); font-family: 'Sarabun', sans-serif; color: #000; line-height: 1.6; }
    .pdf-header { text-align: center; margin-bottom: 1.75rem; position: relative; display: flex; flex-direction: column; align-items: center; }
    .pdf-header h2 { font-size: 1.35rem; font-weight: 700; margin-bottom: 0.25rem; }
    .pdf-header p { font-size: 0.9rem; color: #444; }
    .pdf-meta-table { width: 100%; margin-bottom: 1.25rem; font-size: 0.95rem; }
    .pdf-meta-table td { padding: 4px 0; }
    .pdf-items-table { width: 100%; border-collapse: collapse; margin: 1.25rem 0; font-size: 0.95rem; }
    .pdf-items-table th, .pdf-items-table td { border: 1px solid #333; padding: 8px 10px; }
    .pdf-items-table th { background: #f3f4f6; font-weight: 600; text-align: center; }
    .pdf-signatures { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 2.5rem; text-align: center; font-size: 0.875rem; }
    .sig-box { display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 140px; }
    .sig-img-preview { max-height: 60px; max-width: 130px; margin-bottom: 4px; }
    .sig-line { width: 80%; border-bottom: 1px dotted #333; margin-bottom: 6px; }

    /* Clean Print Isolation - Only the A4 document prints */
    @media print {
      body * {
        visibility: hidden !important;
      }
      #printablePdf, #printablePdf * {
        visibility: visible !important;
      }
      #printablePdf {
        position: fixed !important;
        left: 0 !important;
        top: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        padding: 2cm 2.5cm !important;
        margin: 0 !important;
        box-shadow: none !important;
        background: white !important;
      }
      header, footer, .modal-header, .modal-footer, .pdf-preview-actions, .close-btn, .btn, .cart-drawer, .nav-container {
        display: none !important;
      }
    }
'''

# --------------------------------------------------------------------
# 1. WRITE INDEX.HTML (REQUESTER ONLY PORTAL)
# --------------------------------------------------------------------
requester_html = f'''<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ระบบขอเบิกพัสดุออนไลน์ | มหาวิทยาลัยสวนดุสิต</title>
  
  <!-- PWA & Mobile Icons -->
  <meta name="theme-color" content="#1e40af">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="คลังพัสดุ มสด.">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
  <link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="assets/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="assets/apple-touch-icon.png">
  <link rel="manifest" href="manifest.json">

  <!-- Google Fonts: Prompt for modern UI, Sarabun for official doc/text -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&family=Sarabun:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  
  <!-- SweetAlert2 (Offline local asset with CDN fallback) -->
  <script src="assets/js/sweetalert2.all.min.js"></script>
  <script>
    if (typeof Swal === 'undefined') {{
      document.write('<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"><\\/script>');
    }}
  </script>
  
  <style>
{common_css}

    /* Requester Specific Styles */
    .requester-bar {{
      background: white; border: 1px solid var(--neutral-200); border-radius: var(--radius);
      padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm);
      display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 1.25rem; align-items: flex-end;
    }}
    @media (max-width: 900px) {{ .requester-bar {{ grid-template-columns: 1fr; }} }}

    .search-filter-bar {{ display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }}
    .search-box-wrapper {{ flex: 1; min-width: 300px; position: relative; }}
    .search-input {{
      width: 100%; padding: 0.75rem 1rem 0.75rem 2.75rem; border: 1px solid var(--neutral-300);
      border-radius: 10px; font-family: inherit; font-size: 0.95rem; background: white;
      box-shadow: var(--shadow-sm); outline: none; transition: all 0.2s;
    }}
    .search-input:focus {{ border-color: var(--primary); box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12); }}
    .search-icon {{ position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: var(--neutral-400); pointer-events: none; display: flex; }}

    .category-pills {{ display: flex; gap: 0.5rem; overflow-x: auto; align-items: center; padding-bottom: 4px; }}
    .pill-btn {{
      padding: 0.5rem 1rem; background: white; border: 1px solid var(--neutral-200); border-radius: 999px;
      font-family: inherit; font-size: 0.825rem; font-weight: 500; color: var(--neutral-600);
      cursor: pointer; white-space: nowrap; transition: all 0.2s;
    }}
    .pill-btn:hover {{ border-color: var(--neutral-300); background: var(--neutral-100); }}
    .pill-btn.active {{ background: var(--primary); color: white; border-color: var(--primary); box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25); }}

    .catalog-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 1.25rem; }}
    .item-card {{
      background: white; border: 1px solid var(--neutral-200); border-radius: var(--radius);
      overflow: hidden; box-shadow: var(--shadow-sm); display: flex; flex-direction: column;
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    .item-card:hover {{ transform: translateY(-3px); box-shadow: var(--shadow-md); border-color: var(--primary-border); }}
    .item-image-wrapper {{ height: 175px; background: var(--neutral-100); position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center; }}
    .item-img {{ width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s ease; }}
    .item-card:hover .item-img {{ transform: scale(1.03); }}
    .image-toggle-pills {{
      position: absolute; bottom: 8px; left: 8px; display: flex; gap: 4px;
      background: rgba(15, 23, 42, 0.75); padding: 3px; border-radius: 6px; backdrop-filter: blur(4px);
    }}
    .img-pill-btn {{ background: transparent; border: none; color: white; font-family: inherit; font-size: 0.675rem; padding: 2px 6px; border-radius: 4px; cursor: pointer; opacity: 0.8; }}
    .img-pill-btn.active {{ background: var(--primary); opacity: 1; font-weight: 600; }}

    .card-body {{ padding: 1.15rem; display: flex; flex-direction: column; flex: 1; }}
    .item-title {{ font-size: 0.95rem; font-weight: 600; color: var(--neutral-900); line-height: 1.4; margin-bottom: 0.5rem; min-height: 2.8rem; }}
    .ratio-badge {{ display: inline-flex; align-items: center; gap: 5px; font-size: 0.75rem; color: var(--neutral-600); background: var(--neutral-100); padding: 4px 8px; border-radius: 6px; margin-bottom: 0.75rem; width: fit-content; }}
    .stock-info {{ background: var(--primary-light); border: 1px solid var(--primary-border); border-radius: 8px; padding: 0.5rem 0.75rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; }}
    .stock-label {{ font-size: 0.75rem; color: var(--primary); font-weight: 500; }}
    .stock-value {{ font-size: 0.875rem; font-weight: 700; color: var(--primary); }}
    .card-actions {{ margin-top: auto; display: flex; flex-direction: column; gap: 0.6rem; }}
    .qty-inputs {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }}
    .qty-col label {{ font-size: 0.7rem; color: var(--neutral-600); display: block; margin-bottom: 2px; }}
    .qty-input {{ width: 100%; padding: 0.45rem; border: 1px solid var(--neutral-300); border-radius: 6px; font-family: inherit; font-size: 0.85rem; text-align: center; }}
    .btn-add-cart {{
      width: 100%; background: var(--primary); color: white; border: none; border-radius: 8px;
      padding: 0.6rem; font-family: inherit; font-size: 0.875rem; font-weight: 600; cursor: pointer;
      display: flex; align-items: center; justify-content: center; gap: 0.5rem; transition: background 0.2s, transform 0.1s;
    }}
    .btn-add-cart:hover {{ background: var(--primary-hover); }}
    .btn-add-cart:active {{ transform: scale(0.98); }}

    /* Cart Button Trigger */
    .cart-trigger {{
      position: relative;
      background: var(--primary);
      color: white;
      border: none;
      border-radius: 8px;
      padding: 0.55rem 1.15rem;
      font-family: inherit;
      font-weight: 600;
      font-size: 0.875rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.6rem;
      box-shadow: 0 2px 6px rgba(30, 64, 175, 0.25);
      transition: all 0.2s ease;
    }}
    .cart-trigger:hover {{
      background: var(--primary-hover);
      box-shadow: 0 4px 10px rgba(30, 64, 175, 0.35);
      transform: translateY(-1px);
    }}
    .cart-trigger:active {{
      transform: translateY(0);
    }}
    .cart-badge {{
      background: #ef4444;
      color: white;
      font-size: 0.75rem;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 999px;
      line-height: 1;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 20px;
      height: 20px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    }}

    /* Cart Drawer */
    .cart-drawer-overlay {{ position: fixed; inset: 0; background: rgba(15, 23, 42, 0.5); backdrop-filter: blur(2px); z-index: 50; opacity: 0; pointer-events: none; transition: opacity 0.3s; }}
    .cart-drawer-overlay.open {{ opacity: 1; pointer-events: auto; }}
    .cart-drawer {{
      position: fixed; top: 0; right: 0; bottom: 0; width: 440px; max-width: 90vw; background: white;
      box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15); z-index: 51; transform: translateX(100%); transition: transform 0.3s ease-out;
      display: flex; flex-direction: column;
    }}
    .cart-drawer-overlay.open .cart-drawer {{ transform: translateX(0); }}
    .cart-header {{ padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--neutral-200); display: flex; justify-content: space-between; align-items: center; }}
    .cart-header h3 {{ font-size: 1.1rem; font-weight: 700; color: var(--neutral-900); display: flex; align-items: center; gap: 0.5rem; }}
    .cart-items-list {{ flex: 1; overflow-y: auto; padding: 1rem 1.5rem; display: flex; flex-direction: column; gap: 0.75rem; }}
    .cart-item-card {{ background: var(--neutral-50); border: 1px solid var(--neutral-200); border-radius: 8px; padding: 0.85rem; display: flex; justify-content: space-between; align-items: center; gap: 0.75rem; }}
    .cart-item-details h4 {{ font-size: 0.875rem; font-weight: 600; color: var(--neutral-900); margin-bottom: 0.25rem; }}
    .cart-item-qty {{ font-size: 0.8rem; color: var(--neutral-600); }}
    .cart-item-remove {{ background: none; border: none; color: var(--danger); cursor: pointer; padding: 4px; opacity: 0.7; display: flex; align-items: center; }}
    .cart-item-remove:hover {{ opacity: 1; }}
    .cart-footer {{ padding: 1.25rem 1.5rem; border-top: 1px solid var(--neutral-200); background: white; display: flex; flex-direction: column; gap: 1rem; }}
    .btn-submit-requisition {{
      width: 100%; background: var(--accent); color: white; border: none; border-radius: 8px;
      padding: 0.85rem; font-family: inherit; font-size: 1rem; font-weight: 600; cursor: pointer;
      display: flex; align-items: center; justify-content: center; gap: 0.5rem; box-shadow: 0 4px 10px rgba(5, 150, 105, 0.25);
    }}
    .btn-submit-requisition:hover {{ background: var(--accent-hover); }}

    /* Requester Status Tracking Modal */
    .tracking-timeline {{
      display: flex; flex-direction: column; gap: 1rem; position: relative; padding-left: 2rem; margin: 1rem 0;
    }}
    .tracking-timeline::before {{
      content: ''; position: absolute; left: 11px; top: 8px; bottom: 8px; width: 2px; background: var(--neutral-200);
    }}
    .timeline-step {{ position: relative; display: flex; flex-direction: column; gap: 0.2rem; }}
    .timeline-dot {{
      position: absolute; left: -2rem; top: 3px; width: 24px; height: 24px; border-radius: 999px;
      background: white; border: 2px solid var(--neutral-300); display: flex; align-items: center; justify-content: center; font-size: 0.7rem;
    }}
    .timeline-step.active .timeline-dot {{ background: var(--accent); border-color: var(--accent); color: white; }}
    .timeline-title {{ font-size: 0.9rem; font-weight: 600; color: var(--neutral-800); }}
    .timeline-desc {{ font-size: 0.8rem; color: var(--neutral-600); }}

    /* My Requisitions Modal & Card Styles */
    .req-modal-card {{
      max-width: 840px !important;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
    }}
    .req-filter-tabs {{
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
      margin-bottom: 1rem;
    }}
    .req-tab-btn {{
      padding: 0.45rem 0.95rem;
      border-radius: 999px;
      border: 1px solid var(--neutral-300);
      background: white;
      font-family: inherit;
      font-size: 0.825rem;
      font-weight: 500;
      color: var(--neutral-700);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      transition: all 0.2s;
    }}
    .req-tab-btn:hover {{
      background: var(--neutral-100);
      border-color: var(--neutral-400);
    }}
    .req-tab-btn.active {{
      background: var(--primary);
      color: white;
      border-color: var(--primary);
      box-shadow: 0 2px 6px rgba(30, 64, 175, 0.25);
    }}
    .req-card-item {{
      background: white;
      border: 1px solid var(--neutral-200);
      border-radius: 12px;
      padding: 1.25rem;
      margin-bottom: 1rem;
      box-shadow: var(--shadow-sm);
      transition: all 0.2s;
      border-left: 4px solid var(--primary);
    }}
    .req-card-item:hover {{
      border-color: var(--primary-border);
      box-shadow: var(--shadow-md);
      transform: translateY(-1px);
    }}
    .req-card-item.status-border-pending {{ border-left-color: #d97706; }}
    .req-card-item.status-border-approved {{ border-left-color: #2563eb; }}
    .req-card-item.status-border-completed {{ border-left-color: #059669; }}
    .req-card-item.status-border-rejected {{ border-left-color: #dc2626; }}

    .req-status-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.775rem;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 999px;
    }}
    .pill-pending {{ background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }}
    .pill-approved {{ background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }}
    .pill-completed {{ background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }}
    .pill-rejected {{ background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }}

    .req-item-mini-table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 0.75rem;
      font-size: 0.85rem;
      background: var(--neutral-50);
      border-radius: 8px;
      overflow: hidden;
    }}
    .req-item-mini-table th {{
      background: #f1f5f9;
      color: var(--neutral-700);
      font-weight: 600;
      text-align: left;
      padding: 6px 12px;
      font-size: 0.8rem;
    }}
    .req-item-mini-table td {{
      padding: 7px 12px;
      border-top: 1px solid var(--neutral-200);
      color: var(--neutral-800);
    }}

    footer {{
      margin-top: auto; padding: 1.5rem; background: white; border-top: 1px solid var(--neutral-200);
      text-align: center; font-size: 0.85rem; color: var(--neutral-600);
      display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 1rem;
    }}
  </style>
</head>
<body>

  <!-- Top Navigation Header (Requester Portal Only) -->
  <header>
    <div class="nav-container">
      <div class="brand">
        <img src="assets/logo_sdu.png" alt="มหาวิทยาลัยสวนดุสิต" class="brand-logo-img">
        <div class="brand-text">
          <h1>ระบบขอเบิกพัสดุออนไลน์</h1>
          <p>มหาวิทยาลัยสวนดุสิต (สำหรับอาจารย์และเจ้าหน้าที่หน่วยงาน)</p>
        </div>
      </div>

      <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
        <button class="btn btn-outline" id="btnMyRequisitions" onclick="openMyRequisitionsModal()" style="display: inline-flex; align-items: center; gap: 0.5rem; font-weight: 600;">
          {svg_icons['clipboard']} รายการคำขอของฉัน
          <span class="count-tag" id="myReqsBadge" style="background: var(--primary-light); color: var(--primary); font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 999px; border: 1px solid var(--primary-border); margin-left: 2px;">0</span>
        </button>

        <button class="btn btn-outline" onclick="openTrackingModal()">
          {svg_icons['search']} ติดตามสถานะคำขอ
        </button>

        <button class="cart-trigger" onclick="toggleCartDrawer()">
          {svg_icons['cart']} ตะกร้าของฉัน
          <span class="cart-badge" id="cartCount">0</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Main Content Area -->
  <main>
    <!-- Requester Info Form with SEARCHABLE Combobox -->
    <div class="requester-bar">
      <div class="form-group custom-combobox-wrapper" id="deptComboboxWrapper">
        <label for="deptSearchInput">
          {svg_icons['building']} กลุ่มงาน / หน่วยงานที่สังกัด (สวท.) *
        </label>
        <div class="combobox-control" id="deptComboboxControl">
          <input type="text" id="deptSearchInput" class="form-control combobox-input" 
                 placeholder="พิมพ์ค้นหาหรือเลือกกลุ่มงาน... (เช่น ส่งเสริมวิชาการ, บริการวิชาการ, ทะเบียนนักศึกษา)" 
                 autocomplete="off" 
                 value=""
                 onfocus="openDeptDropdown()" 
                 oninput="handleDeptSearch(this.value)">
          <input type="hidden" id="deptSelect" value="">
          <button type="button" class="combobox-toggle-btn" onclick="toggleDeptDropdown(event)" title="เปิด/ปิด รายการ">
            {svg_icons['chevron_down']}
          </button>
        </div>
        <div class="combobox-dropdown" id="deptDropdownList">
          <!-- Populated and filtered by JS -->
        </div>
      </div>
      <div class="form-group custom-combobox-wrapper" id="userComboboxWrapper">
        <label for="requesterName">
          {svg_icons['user']} ชื่อ-นามสกุล ผู้ขอเบิก (บุคลากร สวท.) *
        </label>
        <div class="combobox-control" id="userComboboxControl">
          <input type="text" id="requesterName" class="form-control combobox-input" 
                 placeholder="คลิกเลือกหรือพิมพ์ค้นหาชื่อบุคลากร... (เช่น ณัฐชา, จุฑาธิป, วาสนา)" 
                 autocomplete="off" 
                 value=""
                 onfocus="openUserDropdown()" 
                 oninput="handleUserSearch(this.value)">
          <button type="button" class="combobox-toggle-btn" onclick="toggleUserDropdown(event)" title="เปิด/ปิด รายชื่อบุคลากร">
            {svg_icons['chevron_down']}
          </button>
        </div>
        <div class="combobox-dropdown" id="userDropdownList">
          <!-- Populated and filtered by JS -->
        </div>
      </div>
      <div class="form-group">
        <label for="requesterPhone">
          {svg_icons['phone']} เบอร์โทรศัพท์ติดต่อ
        </label>
        <input type="tel" id="requesterPhone" class="form-control" placeholder="เช่น 081-234-5678" value="">
      </div>
    </div>

    <!-- Search & Filters -->
    <div class="search-filter-bar">
      <div class="search-box-wrapper">
        <span class="search-icon">{svg_icons['search']}</span>
        <input type="text" id="itemSearchInput" class="search-input" 
               placeholder="พิมพ์ค้นหาชื่อพัสดุ (เช่น 279, ซองขยาย, ครุฑ, แฟ้ม, กระดาษคำตอบ)..." 
               oninput="handleSearch()">
      </div>
      <div class="category-pills">
        <button class="pill-btn active" onclick="filterCategory('ALL', this)">ทั้งหมด</button>
        <button class="pill-btn" onclick="filterCategory('ซองเอกสาร', this)">ซองเอกสาร</button>
        <button class="pill-btn" onclick="filterCategory('กระดาษและแบบฟอร์ม', this)">กระดาษ/แบบฟอร์ม</button>
        <button class="pill-btn" onclick="filterCategory('เครื่องเขียนและแฟ้ม', this)">เครื่องเขียน/แฟ้ม</button>
      </div>
    </div>

    <!-- Item Catalog Cards Grid -->
    <div class="catalog-grid" id="catalogGrid">
      <!-- Rendered dynamically by JS -->
    </div>
  </main>

  <!-- Slide-Over Cart Drawer -->
  <div class="cart-drawer-overlay" id="cartOverlay" onclick="toggleCartDrawer()">
    <div class="cart-drawer" onclick="event.stopPropagation()">
      <div class="cart-header">
        <h3>{svg_icons['cart']} ตะกร้าขอเบิกพัสดุ</h3>
        <button class="close-btn" onclick="toggleCartDrawer()">{svg_icons['x']}</button>
      </div>

      <div class="cart-items-list" id="cartItemsList">
        <!-- Rendered by JS -->
      </div>

      <div class="cart-footer">
        <div class="form-group">
          <label for="cartPurpose">
            {svg_icons['edit']} วัตถุประสงค์ในการเบิกใช้งาน *
          </label>
          <textarea id="cartPurpose" class="form-control" rows="2" placeholder="เช่น ใช้สำหรับการสอบปลายภาค, งานประชุมวิชาการ..."></textarea>
        </div>
        <button class="btn-submit-requisition" onclick="submitRequisition()">
          {svg_icons['check_circle']} ยืนยันส่งคำขอเบิกพัสดุ
        </button>
      </div>
    </div>
  </div>

  <!-- Requisition Success Modal -->
  <div class="modal-overlay" id="successModal">
    <div class="modal-card">
      <div class="modal-header">
        <h3 style="color: var(--accent);">{svg_icons['check_circle']} ส่งคำขอเบิกสำเร็จ</h3>
        <button class="close-btn" onclick="closeSuccessModal()">{svg_icons['x']}</button>
      </div>
      <div class="modal-body" style="text-align: center; padding: 2rem 1.5rem;">
        <div style="font-size: 1.1rem; color: var(--neutral-600); margin-bottom: 0.5rem;">เลขที่เอกสารคำขอเบิกของคุณ:</div>
        <div style="font-size: 1.75rem; font-weight: 700; color: var(--primary); letter-spacing: 1px; background: var(--primary-light); padding: 0.75rem 1rem; border-radius: 8px; border: 1px dashed var(--primary-border); margin-bottom: 1rem;" id="successDocNo">
          REQ-256910-0000
        </div>
        <p style="font-size: 0.9rem; color: var(--neutral-600); line-height: 1.6;">
          คำขอของท่านถูกส่งไปยัง <strong>เจ้าหน้าที่แผนกพัสดุ</strong> เรียบร้อยแล้ว<br>
          เมื่อเจ้าหน้าที่อนุมัติและจัดของเสร็จสิ้น ท่านสามารถเดินทางมารับพัสดุพร้อมเซ็นชื่อรับมอบผ่านหน้าจอได้ที่ห้องคลังพัสดุ
        </p>
      </div>
      <div class="modal-footer" style="justify-content: center; gap: 1rem;">
        <button class="btn btn-primary" onclick="closeSuccessModal()">ตกลง / เบิกรายการอื่นต่อ</button>
      </div>
    </div>
  </div>

  <!-- My Requisitions Modal -->
  <div class="modal-overlay" id="myRequisitionsModal">
    <div class="modal-card req-modal-card">
      <div class="modal-header">
        <h3 style="display: flex; align-items: center; gap: 0.5rem;">
          {svg_icons['clipboard']} รายการคำขอเบิกพัสดุของฉัน
          <span id="myReqsModalCount" style="font-size: 0.85rem; font-weight: normal; color: var(--neutral-600);">(0 รายการ)</span>
        </h3>
        <button class="close-btn" onclick="closeMyRequisitionsModal()">{svg_icons['x']}</button>
      </div>

      <div class="modal-body" style="padding: 1.25rem; overflow-y: auto; max-height: calc(88vh - 130px);">
        <!-- Search and Filter Bar -->
        <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 0.85rem;">
          <div style="flex: 1; min-width: 260px; position: relative;">
            <span style="position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); color: var(--neutral-400); display: flex;">
              {svg_icons['search']}
            </span>
            <input type="text" id="myReqsSearchInput" class="form-control" style="padding-left: 2.3rem;"
                   placeholder="ค้นหาเลขที่คำขอ, ชื่อผู้ขอ, หน่วยงาน, หรือชื่อพัสดุ..." 
                   oninput="handleMyReqsSearch()">
          </div>
        </div>

        <div class="req-filter-tabs">
          <button class="req-tab-btn active" onclick="filterMyReqsTab('ALL', this)">ทั้งหมด</button>
          <button class="req-tab-btn" onclick="filterMyReqsTab('PENDING', this)">รออนุมัติ</button>
          <button class="req-tab-btn" onclick="filterMyReqsTab('APPROVED', this)">อนุมัติแล้ว</button>
          <button class="req-tab-btn" onclick="filterMyReqsTab('COMPLETED', this)">รับมอบสำเร็จ</button>
          <button class="req-tab-btn" onclick="filterMyReqsTab('REJECTED', this)">ไม่อนุมัติ</button>
        </div>

        <!-- Requisitions Cards List -->
        <div id="myRequisitionsList">
          <!-- Rendered by JS -->
        </div>
      </div>

      <div class="modal-footer" style="justify-content: space-between; align-items: center;">
        <span style="font-size: 0.8rem; color: var(--neutral-400); display: flex; align-items: center; gap: 4px;">
          {svg_icons['info']} ข้อมูลอัปเดตแบบเรียลไทม์ ซิงค์กับระบบคลังพัสดุ
        </span>
        <button class="btn btn-outline" onclick="closeMyRequisitionsModal()">ปิดหน้าต่าง</button>
      </div>
    </div>
  </div>

  <!-- Tracking Modal -->
  <div class="modal-overlay" id="trackingModal">
    <div class="modal-card">
      <div class="modal-header">
        <h3>{svg_icons['search']} ติดตามสถานะคำขอเบิก</h3>
        <button class="close-btn" onclick="closeTrackingModal()">{svg_icons['x']}</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>ระบุเลขที่เอกสาร หรือ ชื่อผู้ขอเบิก (เช่น REQ-256910-0042 หรือ สมชาย)</label>
          <div style="display: flex; gap: 0.5rem;">
            <input type="text" id="trackingInput" class="form-control" placeholder="พิมพ์เลขที่เอกสาร REQ-... หรือชื่อผู้ขอเบิก">
            <button class="btn btn-primary" onclick="searchTracking()">ค้นหา</button>
          </div>
        </div>

        <div id="trackingResultArea">
          <p style="font-size: 0.85rem; color: var(--neutral-400); text-align: center; padding: 1.5rem 0;">
            กรุณาระบุเลขที่เอกสารเพื่อดูสถานะการอนุมัติ
          </p>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-outline" onclick="closeTrackingModal()">ปิด</button>
      </div>
    </div>
  </div>

  <!-- OFFICIAL REQUISITION PDF MODAL (REQUESTER PORTAL) -->
  <div class="modal-overlay" id="requisitionPdfModal" style="display: none; align-items: center; justify-content: center; z-index: 100;">
    <div class="modal-card" style="max-width: 880px; width: 95%; max-height: 94vh; padding: 0; display: flex; flex-direction: column; overflow: hidden; background: white;">
      <div class="modal-header" style="padding: 1rem 1.5rem; background: var(--neutral-50); border-bottom: 1px solid var(--neutral-200); display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          {svg_icons['file_text']}
          <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--neutral-900);">ใบขอเบิกพัสดุ (Official Requisition Form)</h3>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <button class="btn btn-primary" onclick="printRequisitionPdf()" style="padding: 0.45rem 1rem; font-size: 0.85rem;">
            {svg_icons['printer']} สั่งพิมพ์เอกสาร (Print PDF)
          </button>
          <button class="close-btn" onclick="closeRequisitionPdfModal()">
            {svg_icons['x']}
          </button>
        </div>
      </div>
      
      <div class="modal-body" style="padding: 1.5rem; overflow-y: auto; background: #525659; display: flex; justify-content: center;">
        <div class="pdf-page" id="printablePdf">
          <div class="pdf-header">
            <img src="assets/logo_sdu.png" alt="ตราสัญลักษณ์ มหาวิทยาลัยสวนดุสิต" style="height: 75px; width: auto; object-fit: contain; margin-bottom: 0.5rem;">
            <h2>ใบขอเบิกพัสดุ</h2>
            <p>ฝ่ายพัสดุและคลังสินค้ากลาง มหาวิทยาลัยสวนดุสิต</p>
          </div>

          <table class="pdf-meta-table">
            <tr>
              <td style="width: 55%;"><strong>เลขที่เอกสาร:</strong> <span id="pdfDocNo">-</span></td>
              <td><strong>วันที่ขอเบิก:</strong> <span id="pdfDate">-</span></td>
            </tr>
            <tr>
              <td><strong>หน่วยงาน/คณะ:</strong> <span id="pdfDept">-</span></td>
              <td><strong>ชื่อผู้ขอเบิก:</strong> <span id="pdfRequester">-</span></td>
            </tr>
            <tr>
              <td colspan="2"><strong>วัตถุประสงค์ในการขอเบิก:</strong> <span id="pdfPurpose">-</span></td>
            </tr>
          </table>

          <table class="pdf-items-table">
            <thead>
              <tr>
                <th style="width: 45px;">ลำดับ</th>
                <th>รายการพัสดุ</th>
                <th style="width: 140px;">จำนวนที่ขอเบิก</th>
                <th style="width: 140px;">จำนวนจ่ายจริง</th>
                <th style="width: 100px;">หมายเหตุ</th>
              </tr>
            </thead>
            <tbody id="pdfItemsTbody">
              <!-- Rendered by JS -->
            </tbody>
          </table>

          <div class="pdf-signatures">
            <div class="sig-box">
              <div class="sig-line"></div>
              <div>ลงชื่อ.......................................................</div>
              <div style="margin-top: 4px;">(<span id="pdfSigRequester">-</span>)</div>
              <div style="font-size: 0.8rem; color: #555;">ผู้ขอเบิก</div>
            </div>

            <div class="sig-box">
              <div class="sig-line"></div>
              <div>ลงชื่อ.......................................................</div>
              <div style="margin-top: 4px;">(.......................................................)</div>
              <div style="font-size: 0.8rem; color: #555;">หัวหน้าหน่วยงาน / ผู้เห็นชอบ</div>
            </div>

            <div class="sig-box">
              <div class="sig-line"></div>
              <div id="pdfSigOfficerBox">
                <div>ลงชื่อ.......................................................</div>
              </div>
              <div style="margin-top: 4px;">(<span id="pdfSigRecipient">-</span>)</div>
              <div style="font-size: 0.8rem; color: #555;">ผู้รับพัสดุ / เจ้าหน้าที่จ่ายของ</div>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer" style="padding: 0.75rem 1.5rem; background: var(--neutral-50); border-top: 1px solid var(--neutral-200); display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 0.8rem; color: var(--neutral-400);">
          เอกสารแบบฟอร์มมาตรฐาน มสด. | พิมพ์ขนาด A4
        </span>
        <button class="btn btn-outline" onclick="closeRequisitionPdfModal()">ปิดหน้าต่าง</button>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <footer>
    <div>
      © 2569 ระบบขอเบิกพัสดุและคลังดิจิทัล มหาวิทยาลัยสวนดุสิต (v{SYSTEM_VERSION}) | ใช้งานเฉพาะภายในสถาบัน
    </div>
  </footer>

  <!-- Scripts -->
  <script>
    const APP_VERSION = '{SYSTEM_VERSION}';
    const MYSQL_API_URL = '{MYSQL_API_URL}';
    const defaultDepts = {dept_json_str};
    const defaultUsers = {users_json_str};

    const vIcons = {{
      box: `{svg_icons['box']}`,
      cart: `{svg_icons['cart']}`,
      clipboard: `{svg_icons['clipboard']}`,
      search: `{svg_icons['search']}`,
      layers: `{svg_icons['layers']}`,
      tag: `{svg_icons['tag']}`,
      trash: `{svg_icons['trash']}`,
      check: `{svg_icons['check']}`,
      clock: `{svg_icons['clock']}`,
      info: `{svg_icons['info']}`,
      user: `{svg_icons['user']}`,
      building: `{svg_icons['building']}`,
      file_text: `{svg_icons['file_text']}`,
      printer: `{svg_icons['printer']}`,
      x: `{svg_icons['x']}`
    }};

    // SHARED LOCAL STORAGE DB INITIALIZATION
    const DB_ITEMS_KEY = 'inventory_items';
    const DB_REQS_KEY = 'inventory_requisitions';
    const DB_USERS_KEY = 'inventory_users';
    const DB_DEPTS_KEY = 'inventory_departments';

    const defaultItems = {json.dumps(initial_items, ensure_ascii=False)};
    const defaultReqs = {json.dumps(initial_requisitions, ensure_ascii=False)};

    function getDeptsDB() {{
      const data = localStorage.getItem(DB_DEPTS_KEY);
      if (!data) {{
        localStorage.setItem(DB_DEPTS_KEY, JSON.stringify(defaultDepts));
        return JSON.parse(JSON.stringify(defaultDepts));
      }}
      try {{
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed) && parsed.length > 0 && parsed[0].category && parsed[0].category.includes('สวท')) {{
          return parsed;
        }}
        localStorage.setItem(DB_DEPTS_KEY, JSON.stringify(defaultDepts));
        return JSON.parse(JSON.stringify(defaultDepts));
      }} catch (e) {{
        localStorage.setItem(DB_DEPTS_KEY, JSON.stringify(defaultDepts));
        return JSON.parse(JSON.stringify(defaultDepts));
      }}
    }}

    function saveDeptsDB(depts) {{
      localStorage.setItem(DB_DEPTS_KEY, JSON.stringify(depts));
    }}

    function getUsersDB() {{
      const data = localStorage.getItem(DB_USERS_KEY);
      if (!data) {{
        localStorage.setItem(DB_USERS_KEY, JSON.stringify(defaultUsers));
        return JSON.parse(JSON.stringify(defaultUsers));
      }}
      try {{
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed) && parsed.length > 0) {{
          // Auto-migrate if localStorage still had the old 29-user list (contains ผอ.อังค์ริสา)
          if (parsed.some(u => u.name && u.name.includes('อังค์ริสา'))) {{
            const customAdded = parsed.filter(u => Number(u.id) > 29);
            const migrated = [
              ...JSON.parse(JSON.stringify(defaultUsers)),
              ...customAdded.map((u, idx) => ({{ ...u, id: defaultUsers.length + idx + 1 }}))
            ];
            localStorage.setItem(DB_USERS_KEY, JSON.stringify(migrated));
            return migrated;
          }}
          return parsed;
        }}
        localStorage.setItem(DB_USERS_KEY, JSON.stringify(defaultUsers));
        return JSON.parse(JSON.stringify(defaultUsers));
      }} catch (e) {{
        localStorage.setItem(DB_USERS_KEY, JSON.stringify(defaultUsers));
        return JSON.parse(JSON.stringify(defaultUsers));
      }}
    }}

    function saveUsersDB(users) {{
      localStorage.setItem(DB_USERS_KEY, JSON.stringify(users));
    }}

    function getItemsDB() {{
      const data = localStorage.getItem(DB_ITEMS_KEY);
      if (!data) {{
        localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(defaultItems));
        return JSON.parse(JSON.stringify(defaultItems));
      }}
      try {{
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed) && parsed.length > 0) {{
          const defMap = new Map(defaultItems.map(i => [i.id, i]));
          let needsSave = false;
          const upgraded = parsed.map(ex => {{
            const defItem = defMap.get(ex.id);
            if (defItem && ex.image_piece && ex.image_piece.startsWith('assets/images/image')) {{
              needsSave = true;
              return {{ ...defItem, on_hand_pieces: ex.on_hand_pieces, reserved_pieces: ex.reserved_pieces }};
            }}
            return ex;
          }});
          if (needsSave) localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(upgraded));
          return upgraded;
        }}
        return parsed;
      }} catch (e) {{
        localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(defaultItems));
        return JSON.parse(JSON.stringify(defaultItems));
      }}
    }}

    async function syncFromMySQLAPI() {{
      if (!MYSQL_API_URL || !navigator.onLine) return;
      try {{
        const [itemsRes, reqsRes, usersRes, deptsRes] = await Promise.all([
          fetch(`${{MYSQL_API_URL}}?action=getItems`).then(r => r.json()).catch(() => null),
          fetch(`${{MYSQL_API_URL}}?action=getRequisitions`).then(r => r.json()).catch(() => null),
          fetch(`${{MYSQL_API_URL}}?action=getUsers`).then(r => r.json()).catch(() => null),
          fetch(`${{MYSQL_API_URL}}?action=getDepartments`).then(r => r.json()).catch(() => null)
        ]);
        if (itemsRes && itemsRes.status === 'success' && Array.isArray(itemsRes.data) && itemsRes.data.length > 0) {{
          saveItemsDB(itemsRes.data);
          renderCatalog();
        }}
        if (reqsRes && reqsRes.status === 'success' && Array.isArray(reqsRes.data) && reqsRes.data.length > 0) {{
          saveReqsDB(reqsRes.data);
          updateMyReqsBadge();
        }}
        if (usersRes && usersRes.status === 'success' && Array.isArray(usersRes.data) && usersRes.data.length > 0) {{
          saveUsersDB(usersRes.data);
        }}
        if (deptsRes && deptsRes.status === 'success' && Array.isArray(deptsRes.data) && deptsRes.data.length > 0) {{
          const grouped = {{}};
          deptsRes.data.forEach(d => {{
            const cat = d.category || 'สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)';
            const lbl = d.full_label || d.name;
            if (!grouped[cat]) grouped[cat] = [];
            if (lbl && !grouped[cat].some(x => x.value === lbl)) {{
              grouped[cat].push({{ label: lbl, value: lbl, sub: false }});
            }}
          }});
          const formattedDepts = Object.keys(grouped).map(k => ({{ category: k, items: grouped[k] }}));
          if (formattedDepts.length > 0) saveDeptsDB(formattedDepts);
        }}
      }} catch (err) {{
        console.warn('Offline fallback active (localStorage):', err);
      }}
    }}

    async function postToMySQLAPI(action, payload) {{
      if (!MYSQL_API_URL || !navigator.onLine) return null;
      try {{
        const res = await fetch(MYSQL_API_URL, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
          body: JSON.stringify({{ action, payload }})
        }});
        return await res.json();
      }} catch (err) {{
        console.warn('MySQL API unreachable, saved to localStorage fallback:', err);
        return null;
      }}
    }}

    function saveItemsDB(items) {{
      localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(items));
    }}

    function getReqsDB() {{
      const data = localStorage.getItem(DB_REQS_KEY);
      if (!data) {{
        localStorage.setItem(DB_REQS_KEY, JSON.stringify(defaultReqs));
        return defaultReqs;
      }}
      try {{
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed)) {{
          const defMap = new Map(defaultReqs.map(r => [r.id, r]));
          let needsSave = false;
          const updated = parsed.map(r => {{
            const defReq = defMap.get(r.id);
            if (defReq && (r.dept === 'โรงเรียนการเรือน' || r.dept === 'คณะพยาบาลศาสตร์')) {{
              needsSave = true;
              return {{ ...r, dept: defReq.dept, requester: defReq.requester, purpose: defReq.purpose }};
            }}
            return r;
          }});
          if (needsSave) localStorage.setItem(DB_REQS_KEY, JSON.stringify(updated));
          return updated;
        }}
        return parsed;
      }} catch (e) {{
        return defaultReqs;
      }}
    }}

    function saveReqsDB(reqs) {{
      localStorage.setItem(DB_REQS_KEY, JSON.stringify(reqs));
    }}

    let cart = [];
    let currentCategory = 'ALL';

    // Department Combobox Logic
    function renderDeptDropdown(filterText = "") {{
      const dropdown = document.getElementById('deptDropdownList');
      const cleanFilter = filterText.trim().toLowerCase();
      let totalMatches = 0;
      let html = "";
      const currentVal = document.getElementById('deptSelect').value;
      const deptsData = getDeptsDB();

      deptsData.forEach(cat => {{
        const matchedItems = cat.items.filter(item => 
          item.label.toLowerCase().includes(cleanFilter) || item.value.toLowerCase().includes(cleanFilter)
        );

        if (matchedItems.length > 0) {{
          totalMatches += matchedItems.length;
          html += `<div class="combobox-group-title">${{cat.category}}</div>`;
          matchedItems.forEach(item => {{
            const isSelected = item.value === currentVal;
            const subClass = item.sub ? 'combobox-item-sub' : '';
            const safeVal = item.value.replace(/'/g, "\\'");
            const safeLbl = item.label.replace(/'/g, "\\'");
            html += `
              <div class="combobox-item ${{subClass}} ${{isSelected ? 'selected' : ''}}" 
                   onclick="selectDepartment('${{safeVal}}', '${{safeLbl}}')">
                <span>${{item.label}}</span>
                ${{isSelected ? `<span style="color: var(--primary); font-size: 0.8rem;">${{vIcons.check}}</span>` : ''}}
              </div>
            `;
          }});
        }}
      }});

      if (totalMatches === 0) {{
        html = `<div class="combobox-no-results">ไม่พบหน่วยงานที่ตรงกับ "${{filterText}}"</div>`;
      }}
      dropdown.innerHTML = html;
    }}

    function openDeptDropdown() {{
      closeUserDropdown();
      document.getElementById('deptDropdownList').classList.add('open');
      document.getElementById('deptComboboxControl').classList.add('open');
      renderDeptDropdown("");
    }}

    function closeDeptDropdown() {{
      document.getElementById('deptDropdownList').classList.remove('open');
      document.getElementById('deptComboboxControl').classList.remove('open');
    }}

    function toggleDeptDropdown(e) {{
      e.stopPropagation();
      const dropdown = document.getElementById('deptDropdownList');
      if (dropdown.classList.contains('open')) closeDeptDropdown();
      else {{
        document.getElementById('deptSearchInput').focus();
        openDeptDropdown();
      }}
    }}

    function handleDeptSearch(text) {{
      document.getElementById('deptSelect').value = text.trim();
      openDeptDropdown();
      renderDeptDropdown(text);
    }}

    function selectDepartment(value, label) {{
      document.getElementById('deptSelect').value = value;
      document.getElementById('deptSearchInput').value = label;
      closeDeptDropdown();
    }}

    // User (Personnel) Combobox Logic
    function renderUserDropdown(filterText = "") {{
      const dropdown = document.getElementById('userDropdownList');
      const users = getUsersDB();
      const currentName = document.getElementById('requesterName').value.trim();
      const selectedDept = document.getElementById('deptSelect').value.trim();
      // If filterText equals a known user's exact name, show all users so they can switch easily
      const isExactSelectedName = users.some(u => u.name === filterText.trim());
      const cleanFilter = isExactSelectedName ? "" : filterText.trim().toLowerCase();

      const matched = users.filter(u =>
        !cleanFilter ||
        (u.name && u.name.toLowerCase().includes(cleanFilter)) ||
        (u.position && u.position.toLowerCase().includes(cleanFilter)) ||
        (u.dept && u.dept.toLowerCase().includes(cleanFilter))
      );

      if (matched.length === 0) {{
        dropdown.innerHTML = `<div class="combobox-no-results">ไม่พบรายชื่อในระบบ (สามารถพิมพ์ชื่อ "${{filterText}}" เพื่อขอเบิกได้ทันที)</div>`;
        return;
      }}

      let html = "";
      // Group by department, putting selectedDept first if chosen
      const groups = {{}};
      matched.forEach(u => {{
        const d = u.dept || 'ไม่ระบุกลุ่มงาน';
        if (!groups[d]) groups[d] = [];
        groups[d].push(u);
      }});

      const deptKeys = Object.keys(groups);
      if (selectedDept && groups[selectedDept]) {{
        deptKeys.sort((a, b) => (a === selectedDept ? -1 : b === selectedDept ? 1 : 0));
      }}

      deptKeys.forEach(deptName => {{
        const isCurrentDept = deptName === selectedDept;
        html += `<div class="combobox-group-title">${{deptName}}${{isCurrentDept ? ' (กลุ่มงานที่เลือก)' : ''}}</div>`;
        groups[deptName].forEach(u => {{
          const isSelected = u.name === currentName;
          html += `
            <div class="combobox-item ${{isSelected ? 'selected' : ''}}"
                 onclick="selectRequesterUser(${{u.id}})"
                 style="display: flex; justify-content: space-between; align-items: center; gap: 0.5rem;">
              <div style="display: flex; flex-direction: column;">
                <span style="font-weight: 500; color: var(--neutral-900);">${{u.name}}</span>
                <span style="font-size: 0.75rem; color: var(--neutral-500);">${{u.position || '-'}}</span>
              </div>
              ${{isSelected ? `<span style="color: var(--primary); font-size: 0.8rem;">${{vIcons.check}}</span>` : ''}}
            </div>
          `;
        }});
      }});

      dropdown.innerHTML = html;
    }}

    function openUserDropdown() {{
      closeDeptDropdown();
      document.getElementById('userDropdownList').classList.add('open');
      document.getElementById('userComboboxControl').classList.add('open');
      renderUserDropdown(document.getElementById('requesterName').value);
    }}

    function closeUserDropdown() {{
      const dd = document.getElementById('userDropdownList');
      const ctrl = document.getElementById('userComboboxControl');
      if (dd) dd.classList.remove('open');
      if (ctrl) ctrl.classList.remove('open');
    }}

    function toggleUserDropdown(e) {{
      e.stopPropagation();
      const dropdown = document.getElementById('userDropdownList');
      if (dropdown.classList.contains('open')) closeUserDropdown();
      else {{
        document.getElementById('requesterName').focus();
        openUserDropdown();
      }}
    }}

    function handleUserSearch(text) {{
      openUserDropdown();
      renderUserDropdown(text);
    }}

    function selectRequesterUser(userId) {{
      const users = getUsersDB();
      const user = users.find(u => Number(u.id) === Number(userId));
      if (user) {{
        document.getElementById('requesterName').value = user.name;
        if (user.dept) {{
          document.getElementById('deptSelect').value = user.dept;
          document.getElementById('deptSearchInput').value = user.dept;
        }}
        if (user.phone) {{
          document.getElementById('requesterPhone').value = user.phone;
        }}
      }}
      closeUserDropdown();
    }}

    document.addEventListener('click', (e) => {{
      const deptWrapper = document.getElementById('deptComboboxWrapper');
      if (deptWrapper && !deptWrapper.contains(e.target)) closeDeptDropdown();
      const userWrapper = document.getElementById('userComboboxWrapper');
      if (userWrapper && !userWrapper.contains(e.target)) closeUserDropdown();
    }});

    // Catalog Rendering
    function formatStockDisplay(totalPieces, ratio, boxName, pieceName, isMulti) {{
      if (!isMulti || ratio <= 1) return `${{totalPieces.toLocaleString()}} ${{pieceName}}`;
      const boxes = Math.floor(totalPieces / ratio);
      const pieces = totalPieces % ratio;
      if (boxes > 0 && pieces > 0) return `${{boxes}} ${{boxName}} ${{pieces}} ${{pieceName}}`;
      if (boxes > 0) return `${{boxes}} ${{boxName}}`;
      return `${{pieces}} ${{pieceName}}`;
    }}

    function renderCatalog() {{
      const items = getItemsDB();
      const grid = document.getElementById('catalogGrid');
      const searchTerm = document.getElementById('itemSearchInput').value.trim().toLowerCase();

      const filtered = items.filter(item => {{
        const matchesCategory = currentCategory === 'ALL' || item.category === currentCategory;
        const matchesSearch = item.name.toLowerCase().includes(searchTerm);
        return matchesCategory && matchesSearch;
      }});

      if (filtered.length === 0) {{
        grid.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--neutral-400);">
            <p style="font-size: 1.1rem; font-weight: 500;">ไม่พบรายการพัสดุที่ตรงกับ "${{searchTerm}}"</p>
          </div>
        `;
        return;
      }}

      grid.innerHTML = filtered.map(item => {{
        const availablePieces = Math.max(0, item.on_hand_pieces - item.reserved_pieces);
        const stockStr = formatStockDisplay(availablePieces, item.pieces_per_box, item.unit_box_name, item.unit_piece_name, item.is_multi_unit);
        const imgSrc = item.current_img_mode === 'box' ? item.image_box : item.image_piece;

        return `
          <div class="item-card">
            <div class="item-image-wrapper">
              <img src="${{imgSrc}}" class="item-img" alt="${{item.name}}" onerror="this.onerror=null; this.src='assets/logo_sdu.png'">
              ${{item.is_multi_unit ? `
                <div class="image-toggle-pills">
                  <button class="img-pill-btn ${{item.current_img_mode !== 'box' ? 'active' : ''}}" 
                          onclick="toggleItemImg(${{item.id}}, 'piece')">รูปชิ้น</button>
                  <button class="img-pill-btn ${{item.current_img_mode === 'box' ? 'active' : ''}}" 
                          onclick="toggleItemImg(${{item.id}}, 'box')">รูป${{item.unit_box_name}}</button>
                </div>
              ` : ''}}
            </div>
            <div class="card-body">
              <h3 class="item-title">${{item.name}}</h3>
              ${{item.is_multi_unit ? `
                <span class="ratio-badge">${{vIcons.layers}} 1 ${{item.unit_box_name}} = ${{item.pieces_per_box.toLocaleString()}} ${{item.unit_piece_name}}</span>
              ` : `
                <span class="ratio-badge">${{vIcons.tag}} หน่วยเดี่ยว: ${{item.unit_piece_name}}</span>
              `}}
              <div class="stock-info">
                <span class="stock-label">พร้อมให้เบิก (Available):</span>
                <span class="stock-value">${{stockStr}}</span>
              </div>
              <div class="card-actions">
                <div class="qty-inputs">
                  ${{item.is_multi_unit ? `
                    <div class="qty-col">
                      <label>จำนวน (${{item.unit_box_name}})</label>
                      <input type="number" id="qty-box-${{item.id}}" class="qty-input" min="0" placeholder="0">
                    </div>
                  ` : ''}}
                  <div class="qty-col" style="${{!item.is_multi_unit ? 'grid-column: span 2;' : ''}}">
                    <label>จำนวน (${{item.unit_piece_name}})</label>
                    <input type="number" id="qty-piece-${{item.id}}" class="qty-input" min="0" placeholder="0">
                  </div>
                </div>
                <button class="btn-add-cart" onclick="addToCart(${{item.id}})">
                  ${{vIcons.cart}} เพิ่มเข้าตะกร้า
                </button>
              </div>
            </div>
          </div>
        `;
      }}).join('');
    }}

    function toggleItemImg(itemId, mode) {{
      const items = getItemsDB();
      const itm = items.find(i => i.id === itemId);
      if (itm) {{
        itm.current_img_mode = mode;
        saveItemsDB(items);
        renderCatalog();
      }}
    }}

    function handleSearch() {{ renderCatalog(); }}
    function filterCategory(cat, btn) {{
      currentCategory = cat;
      document.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderCatalog();
    }}

    // Cart Logic
    function addToCart(itemId) {{
      const items = getItemsDB();
      const item = items.find(i => i.id === itemId);
      if (!item) return;

      const boxInput = document.getElementById(`qty-box-${{item.id}}`);
      const pieceInput = document.getElementById(`qty-piece-${{item.id}}`);
      const qtyBoxes = boxInput ? parseInt(boxInput.value || 0) : 0;
      const qtyPieces = pieceInput ? parseInt(pieceInput.value || 0) : 0;

      if (qtyBoxes <= 0 && qtyPieces <= 0) {{
        Swal.fire({{
          icon: 'warning',
          title: 'กรุณาระบุจำนวน',
          text: 'กรุณาระบุจำนวนที่ต้องการเบิกอย่างน้อย 1 ชิ้นหรือกล่องครับ',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        }});
        return;
      }}

      const totalPieces = (qtyBoxes * item.pieces_per_box) + qtyPieces;
      const availablePieces = item.on_hand_pieces - item.reserved_pieces;

      if (totalPieces > availablePieces) {{
        Swal.fire({{
          icon: 'error',
          title: 'ยอดพัสดุไม่เพียงพอ',
          html: `คุณขอเบิกจำนวน <b>${{totalPieces.toLocaleString()}} ${{item.unit_piece_name}}</b><br>แต่มีพร้อมเบิกเพียง <b>${{availablePieces.toLocaleString()}} ${{item.unit_piece_name}}</b>`,
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'เข้าใจแล้ว'
        }});
        return;
      }}

      const existing = cart.find(c => c.itemId === itemId);
      if (existing) {{
        existing.qtyBoxes += qtyBoxes;
        existing.qtyPieces += qtyPieces;
        existing.totalPieces += totalPieces;
      }} else {{
        cart.push({{
          itemId: item.id,
          name: item.name,
          unitBox: item.unit_box_name,
          unitPiece: item.unit_piece_name,
          qtyBoxes: qtyBoxes,
          qtyPieces: qtyPieces,
          totalPieces: totalPieces,
          is_multi: item.is_multi_unit
        }});
      }}

      if (boxInput) boxInput.value = '';
      if (pieceInput) pieceInput.value = '';
      updateCartBadge();
      renderCartDrawer();
      toggleCartDrawer(true);

      Swal.mixin({{
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 1800,
        timerProgressBar: true
      }}).fire({{
        icon: 'success',
        title: `เพิ่ม "${{item.name}}" ใส่ตะกร้าแล้ว`
      }});
    }}

    function updateCartBadge() {{
      document.getElementById('cartCount').innerText = cart.length;
    }}

    function toggleCartDrawer(forceOpen) {{
      const overlay = document.getElementById('cartOverlay');
      if (forceOpen === true) overlay.classList.add('open');
      else if (forceOpen === false) overlay.classList.remove('open');
      else overlay.classList.toggle('open');
    }}

    function renderCartDrawer() {{
      const list = document.getElementById('cartItemsList');
      if (cart.length === 0) {{
        list.innerHTML = `<div style="text-align: center; padding: 3rem 1rem; color: var(--neutral-400);"><p>ยังไม่มีรายการพัสดุในตะกร้า</p></div>`;
        return;
      }}

      list.innerHTML = cart.map((c, idx) => {{
        let qtyText = c.qtyBoxes > 0 && c.qtyPieces > 0 ? 
          `${{c.qtyBoxes}} ${{c.unitBox}} + ${{c.qtyPieces}} ${{c.unitPiece}} (รวม ${{c.totalPieces.toLocaleString()}} ${{c.unitPiece}})` :
          (c.qtyBoxes > 0 ? `${{c.qtyBoxes}} ${{c.unitBox}} (รวม ${{c.totalPieces.toLocaleString()}} ${{c.unitPiece}})` : `${{c.qtyPieces}} ${{c.unitPiece}}`);

        return `
          <div class="cart-item-card">
            <div class="cart-item-details">
              <h4>${{c.name}}</h4>
              <div class="cart-item-qty">จำนวนที่ขอเบิก: <strong>${{qtyText}}</strong></div>
            </div>
            <button class="cart-item-remove" onclick="removeCartItem(${{idx}})" title="ลบออก">${{vIcons.trash}}</button>
          </div>
        `;
      }}).join('');
    }}

    function removeCartItem(idx) {{
      const removed = cart[idx];
      cart.splice(idx, 1);
      updateCartBadge();
      renderCartDrawer();
      if (removed) {{
        Swal.mixin({{
          toast: true,
          position: 'top-end',
          showConfirmButton: false,
          timer: 1800,
          timerProgressBar: true
        }}).fire({{
          icon: 'info',
          title: `ลบ "${{removed.name}}" ออกจากตะกร้าแล้ว`
        }});
      }}
    }}

    function submitRequisition() {{
      const dept = document.getElementById('deptSelect').value;
      const requester = document.getElementById('requesterName').value.trim();
      const phone = document.getElementById('requesterPhone').value.trim();
      const purpose = document.getElementById('cartPurpose').value.trim();

      if (!dept) {{
        Swal.fire({{
          icon: 'warning',
          title: 'ข้อมูลไม่ครบถ้วน',
          text: 'กรุณาเลือกหน่วยงาน / คณะ / โรงเรียนที่สังกัดครับ',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        }});
        return;
      }}
      if (!requester) {{
        Swal.fire({{
          icon: 'warning',
          title: 'ข้อมูลไม่ครบถ้วน',
          text: 'กรุณากรอกชื่อ-นามสกุล ผู้ขอเบิกครับ',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        }});
        return;
      }}
      if (cart.length === 0) {{
        Swal.fire({{
          icon: 'warning',
          title: 'ไม่มีรายการในตะกร้า',
          text: 'กรุณาเลือกรายการพัสดุและระบุจำนวนก่อนส่งคำขอครับ',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        }});
        return;
      }}
      if (!purpose) {{
        Swal.fire({{
          icon: 'warning',
          title: 'ระบุวัตถุประสงค์',
          text: 'กรุณาระบุวัตถุประสงค์ในการเบิกใช้งานพัสดุครับ',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        }});
        return;
      }}

      Swal.fire({{
        title: 'ยืนยันส่งคำขอเบิกพัสดุ?',
        html: `
          <div style="text-align: left; font-size: 0.95rem; margin-top: 0.5rem; color: #475569; line-height: 1.6;">
            <p><strong>หน่วยงาน:</strong> ${{dept}}</p>
            <p><strong>ผู้ขอเบิก:</strong> ${{requester}} ${{phone ? `(${{phone}})` : ''}}</p>
            <p><strong>จำนวนพัสดุ:</strong> ${{cart.length}} รายการ</p>
            <p><strong>วัตถุประสงค์:</strong> ${{purpose}}</p>
          </div>
        `,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#059669',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ยืนยันส่งคำขอ',
        cancelButtonText: 'ยกเลิก'
      }}).then((result) => {{
        if (result.isConfirmed) {{
          const randomNo = Math.floor(1000 + Math.random() * 9000);
          const newDocNo = `REQ-256910-${{randomNo}}`;

          const nowIso = new Date().toISOString();
          const newReq = {{
            id: newDocNo,
            dept: dept,
            requester: requester,
            phone: phone,
            purpose: purpose,
            date: "21 ต.ค. 2569 " + new Date().toLocaleTimeString('th-TH', {{hour: '2-digit', minute:'2-digit'}}) + " น.",
            status: "PENDING",
            signature: null,
            reject_reason: "",
            created_at: nowIso,
            updated_at: nowIso,
            items: cart.map(c => ({{
              itemId: c.itemId,
              name: c.name,
              qtyBoxes: c.qtyBoxes,
              qtyPieces: c.qtyPieces,
              totalPieces: c.totalPieces,
              unitBox: c.unitBox,
              unitPiece: c.unitPiece,
              approvedPieces: c.totalPieces
            }}))
          }};

          // Save to shared localStorage DB & sync to MySQL API
          const reqs = getReqsDB();
          reqs.unshift(newReq);
          saveReqsDB(reqs);
          postToMySQLAPI('createRequisition', newReq);

          cart = [];
          document.getElementById('cartPurpose').value = '';
          updateCartBadge();
          updateMyReqsBadge();
          toggleCartDrawer(false);
          renderCatalog();

          Swal.fire({{
            icon: 'success',
            title: 'ส่งคำขอเบิกพัสดุสำเร็จ!',
            html: `
              <div style="margin: 0.75rem 0;">
                <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 0.5rem;">เลขที่เอกสารคำขอเบิกของคุณ:</p>
                <div style="font-size: 1.6rem; font-weight: 700; color: #1e40af; background: #eff6ff; padding: 0.75rem 1rem; border-radius: 8px; border: 1px dashed #bfdbfe; letter-spacing: 1px;">
                  ${{newDocNo}}
                </div>
                <p style="font-size: 0.85rem; color: #475569; margin-top: 0.85rem; line-height: 1.6;">
                  คำขอของท่านเข้าสู่สถานะ <b>"รออนุมัติ (Pending)"</b> และถูกส่งต่อไปยังเจ้าหน้าที่แผนกพัสดุเรียบร้อยแล้ว<br>
                  เมื่อเจ้าหน้าที่อนุมัติ ท่านสามารถเดินทางไปรับพัสดุได้ที่ห้องคลังพัสดุ
                </p>
              </div>
            `,
            showCancelButton: true,
            confirmButtonColor: '#1e40af',
            cancelButtonColor: '#64748b',
            confirmButtonText: 'ดูในรายการคำขอของฉัน',
            cancelButtonText: 'ตกลง / เบิกรายการอื่นต่อ'
          }}).then((res) => {{
            if (res.isConfirmed) {{
              openMyRequisitionsModal();
            }}
          }});
        }}
      }});
    }}

    function closeSuccessModal() {{
      document.getElementById('successModal').classList.remove('open');
      renderCatalog();
    }}

    // My Requisitions Modal Logic
    let myReqsFilterStatus = 'ALL';

    function openMyRequisitionsModal() {{
      const modal = document.getElementById('myRequisitionsModal');
      modal.classList.add('open');
      renderMyRequisitionsModal();
    }}

    function closeMyRequisitionsModal() {{
      const modal = document.getElementById('myRequisitionsModal');
      modal.classList.remove('open');
    }}

    function filterMyReqsTab(status, btn) {{
      myReqsFilterStatus = status;
      document.querySelectorAll('.req-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderMyRequisitionsModal();
    }}

    function handleMyReqsSearch() {{
      renderMyRequisitionsModal();
    }}

    function updateMyReqsBadge() {{
      const reqs = getReqsDB();
      const badge = document.getElementById('myReqsBadge');
      if (badge) {{
        badge.innerText = reqs.length;
      }}
    }}

    function copyDocNumber(docNo) {{
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(docNo);
      }} else {{
        const temp = document.createElement('input');
        temp.value = docNo;
        document.body.appendChild(temp);
        temp.select();
        document.execCommand('copy');
        document.body.removeChild(temp);
      }}
      Swal.mixin({{
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 1800,
        timerProgressBar: true
      }}).fire({{
        icon: 'success',
        title: `คัดลอกเลขที่เอกสาร ${{docNo}} แล้ว`
      }});
    }}

    function viewTrackingForDoc(docNo) {{
      closeMyRequisitionsModal();
      openTrackingModal();
      const trackInput = document.getElementById('trackingInput');
      if (trackInput) {{
        trackInput.value = docNo;
        searchTracking();
      }}
    }}

    function renderMyRequisitionsModal() {{
      const listEl = document.getElementById('myRequisitionsList');
      const countEl = document.getElementById('myReqsModalCount');
      const searchVal = (document.getElementById('myReqsSearchInput')?.value || '').trim().toLowerCase();
      
      const reqs = getReqsDB();

      let filtered = reqs.filter(r => {{
        if (myReqsFilterStatus !== 'ALL' && r.status !== myReqsFilterStatus) return false;
        if (searchVal) {{
          const matchId = (r.id || '').toLowerCase().includes(searchVal);
          const matchName = (r.requester || '').toLowerCase().includes(searchVal);
          const matchDept = (r.dept || '').toLowerCase().includes(searchVal);
          const matchPurpose = (r.purpose || '').toLowerCase().includes(searchVal);
          const matchItem = (r.items || []).some(it => (it.name || '').toLowerCase().includes(searchVal));
          return matchId || matchName || matchDept || matchPurpose || matchItem;
        }}
        return true;
      }});

      if (countEl) {{
        countEl.innerText = `(พบ ${{filtered.length}} จาก ${{reqs.length}} รายการ)`;
      }}

      if (filtered.length === 0) {{
        listEl.innerHTML = `
          <div style="text-align: center; padding: 3rem 1rem; color: var(--neutral-400);">
            <div style="margin-bottom: 0.75rem; color: var(--neutral-300);">
              ${{vIcons.clipboard}}
            </div>
            <h4 style="font-size: 1.05rem; font-weight: 600; color: var(--neutral-600); margin-bottom: 0.25rem;">
              ไม่พบรายการคำขอเบิกพัสดุ
            </h4>
            <p style="font-size: 0.85rem; color: var(--neutral-400); max-width: 360px; margin: 0 auto 1.25rem auto;">
              ${{searchVal || myReqsFilterStatus !== 'ALL' ? 'ลองเปลี่ยนคำค้นหาหรือตัวกรองสถานะ' : 'คุณยังไม่มีประวัติการส่งคำขอเบิกพัสดุในระบบ'}}
            </p>
            ${{!searchVal && myReqsFilterStatus === 'ALL' ? `
              <button class="btn btn-primary" onclick="closeMyRequisitionsModal()">
                ${{vIcons.cart}} ไปที่แคตตาล็อกเลือกเบิกพัสดุ
              </button>
            ` : ''}}
          </div>
        `;
        return;
      }}

      listEl.innerHTML = filtered.map(req => {{
        let statusBadge = '';
        let borderClass = 'status-border-pending';

        if (req.status === 'PENDING') {{
          statusBadge = `<span class="req-status-pill pill-pending">${{vIcons.clock}} รออนุมัติ (Pending)</span>`;
          borderClass = 'status-border-pending';
        }} else if (req.status === 'APPROVED') {{
          statusBadge = `<span class="req-status-pill pill-approved">${{vIcons.check}} อนุมัติแล้ว (รอรับพัสดุ)</span>`;
          borderClass = 'status-border-approved';
        }} else if (req.status === 'COMPLETED') {{
          statusBadge = `<span class="req-status-pill pill-completed">${{vIcons.check}} รับมอบสำเร็จแล้ว</span>`;
          borderClass = 'status-border-completed';
        }} else if (req.status === 'REJECTED') {{
          statusBadge = `<span class="req-status-pill pill-rejected">${{vIcons.x}} ไม่อนุมัติ</span>`;
          borderClass = 'status-border-rejected';
        }}

        const itemsRows = (req.items || []).map(it => {{
          let reqQty = it.qtyBoxes > 0 && it.qtyPieces > 0 ?
            it.qtyBoxes + ' ' + it.unitBox + ' + ' + it.qtyPieces + ' ' + it.unitPiece :
            (it.qtyBoxes > 0 ? it.qtyBoxes + ' ' + it.unitBox : it.qtyPieces + ' ' + it.unitPiece);
          let appQty = it.approvedPieces !== undefined ? it.approvedPieces.toLocaleString() + ' ' + it.unitPiece : '-';
          let appColor = (req.status === 'APPROVED' || req.status === 'COMPLETED') ? 'var(--accent)' : 'var(--neutral-600)';
          return `
            <tr>
              <td>${{it.name}}</td>
              <td style="text-align: right; font-weight: 500;">${{reqQty}}</td>
              <td style="text-align: right; font-weight: 600; color: ${{appColor}};">${{appQty}}</td>
            </tr>
          `;
        }}).join('');

        let phoneText = req.phone ? ' (' + req.phone + ')' : '';

        return `
          <div class="req-card-item ${{borderClass}}">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.75rem;">
              <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                <span style="font-weight: 700; font-size: 1.05rem; color: var(--neutral-900); font-family: monospace; letter-spacing: 0.5px;">
                  ${{req.id}}
                </span>
                <button class="btn btn-outline" style="padding: 2px 7px; font-size: 0.75rem;" onclick="copyDocNumber('${{req.id}}')" title="คัดลอกเลขที่เอกสาร">
                  ${{vIcons.clipboard}} คัดลอก
                </button>
                ${{statusBadge}}
              </div>
              <div style="font-size: 0.8rem; color: var(--neutral-400); display: flex; align-items: center; gap: 4px;">
                ${{vIcons.clock}} ${{req.date}}
              </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.6rem; font-size: 0.85rem; color: var(--neutral-700); margin-bottom: 0.75rem; background: var(--neutral-50); padding: 0.75rem; border-radius: 8px;">
              <div>
                <span style="color: var(--neutral-400); font-size: 0.8rem;">ผู้ขอเบิก:</span><br>
                <strong>${{req.requester}}</strong>${{phoneText}}
              </div>
              <div>
                <span style="color: var(--neutral-400); font-size: 0.8rem;">หน่วยงาน:</span><br>
                <span>${{req.dept}}</span>
              </div>
              <div style="grid-column: 1 / -1;">
                <span style="color: var(--neutral-400); font-size: 0.8rem;">วัตถุประสงค์:</span><br>
                <span>${{req.purpose || '-'}}</span>
              </div>
              ${{req.status === 'REJECTED' && (req.reject_reason || req.rejectReason) ? `
              <div style="grid-column: 1 / -1; background: var(--danger-light); color: #991b1b; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid #fecaca;">
                <strong>เหตุผลที่ไม่อนุมัติ:</strong> ${{req.reject_reason || req.rejectReason}}
              </div>
              ` : ''}}
            </div>

            <table class="req-item-mini-table">
              <thead>
                <tr>
                  <th>รายการพัสดุ</th>
                  <th style="width: 140px; text-align: right;">จำนวนที่ขอ</th>
                  <th style="width: 140px; text-align: right;">อนุมัติจัดจ่าย</th>
                </tr>
              </thead>
              <tbody>
                ${{itemsRows}}
              </tbody>
            </table>

            <div style="margin-top: 0.85rem; display: flex; justify-content: flex-end; gap: 0.5rem; flex-wrap: wrap;">
              <button class="btn btn-outline" style="font-size: 0.8rem; padding: 0.4rem 0.85rem;" onclick="viewTrackingForDoc('${{req.id}}')">
                ${{vIcons.search}} ติดตามไทม์ไลน์สถานะ
              </button>
              <button class="btn btn-primary" style="font-size: 0.8rem; padding: 0.4rem 0.85rem;" onclick="openRequisitionPdf('${{req.id}}')">
                ${{vIcons.file_text}} พิมพ์ใบเบิกพัสดุ (PDF)
              </button>
            </div>
          </div>
        `;
      }}).join('');
    }}

    // Tracking Modal
    function openTrackingModal() {{
      document.getElementById('trackingModal').classList.add('open');
    }}
    function closeTrackingModal() {{
      document.getElementById('trackingModal').classList.remove('open');
    }}
    function searchTracking() {{
      const query = document.getElementById('trackingInput').value.trim();
      const area = document.getElementById('trackingResultArea');
      if (!query) return;
      const reqs = getReqsDB();
      const qLower = query.toLowerCase();
      const req = reqs.find(r =>
        (r.id || '').toLowerCase() === qLower ||
        (r.id || '').toLowerCase().includes(qLower) ||
        (r.requester || '').toLowerCase().includes(qLower)
      );

      if (!req) {{
        Swal.fire({{
          icon: 'error',
          title: 'ไม่พบข้อมูลคำขอเบิก',
          text: `ไม่พบข้อมูลคำขอเบิกที่ตรงกับ "${{query}}" ในระบบ กรุณาตรวจสอบเลขที่เอกสารหรือชื่อผู้ขอเบิกอีกครั้งครับ`,
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        }});
        area.innerHTML = `<p style="color: var(--danger); text-align: center; padding: 1rem;">ไม่พบข้อมูลคำขอเบิกที่ตรงกับ "${{query}}"</p>`;
        return;
      }}

      let statusBadge = '<span class="req-status-pill pill-pending">' + vIcons.clock + ' รอเจ้าหน้าที่พัสดุอนุมัติ</span>';
      if (req.status === 'APPROVED') statusBadge = '<span class="req-status-pill pill-approved">' + vIcons.check + ' อนุมัติแล้ว (เชิญรับพัสดุ)</span>';
      if (req.status === 'COMPLETED') statusBadge = '<span class="req-status-pill pill-completed">' + vIcons.check + ' รับมอบพัสดุสำเร็จแล้ว</span>';
      if (req.status === 'REJECTED') statusBadge = '<span class="req-status-pill pill-rejected">' + vIcons.x + ' ไม่อนุมัติ</span>';

      const step1Active = true;
      const step2Active = req.status === 'APPROVED' || req.status === 'COMPLETED';
      const step3Active = req.status === 'COMPLETED';
      const isRejected = req.status === 'REJECTED';
      const reasonText = req.reject_reason || req.rejectReason || 'ไม่ระบุเหตุผล';

      const timelineHtml = isRejected ? `
        <div class="tracking-timeline">
          <div class="timeline-step active">
            <div class="timeline-dot">${{vIcons.check}}</div>
            <div class="timeline-title">1. ส่งคำขอเบิกพัสดุ (Pending)</div>
            <div class="timeline-desc">บันทึกคำขอเบิกเข้าระบบเมื่อ ${{req.date}}</div>
          </div>
          <div class="timeline-step active">
            <div class="timeline-dot" style="background: var(--danger); border-color: var(--danger);">${{vIcons.x}}</div>
            <div class="timeline-title" style="color: var(--danger);">2. ไม่อนุมัติคำขอ / ยกเลิกรายการ (Rejected)</div>
            <div class="timeline-desc" style="color: #991b1b;">เหตุผล: ${{reasonText}}</div>
          </div>
        </div>
      ` : `
        <div class="tracking-timeline">
          <div class="timeline-step ${{step1Active ? 'active' : ''}}">
            <div class="timeline-dot">${{step1Active ? vIcons.check : '1'}}</div>
            <div class="timeline-title">1. ส่งคำขอเบิกพัสดุ (Pending)</div>
            <div class="timeline-desc">บันทึกคำขอเบิกเข้าระบบเมื่อ ${{req.date}}</div>
          </div>
          <div class="timeline-step ${{step2Active ? 'active' : ''}}">
            <div class="timeline-dot">${{step2Active ? vIcons.check : '2'}}</div>
            <div class="timeline-title">2. อนุมัติและกันยอดสต๊อก (Approved)</div>
            <div class="timeline-desc">${{step2Active ? 'เจ้าหน้าที่อนุมัติและกันสต๊อกเรียบร้อยแล้ว พร้อมให้มารับพัสดุ' : 'รอเจ้าหน้าที่คลังพัสดุตรวจสอบและอนุมัติ'}}</div>
          </div>
          <div class="timeline-step ${{step3Active ? 'active' : ''}}">
            <div class="timeline-dot">${{step3Active ? vIcons.check : '3'}}</div>
            <div class="timeline-title">3. ลงนามดิจิทัลและรับมอบพัสดุ (Completed)</div>
            <div class="timeline-desc">${{step3Active ? 'ผู้เบิกลงนาม E-Signature รับของและตัดยอดสต๊อกจริงเรียบร้อยแล้ว' : 'รอผู้ขอเบิกเดินทางมารับของและเซ็นชื่อบนหน้าจอที่ห้องพัสดุ'}}</div>
          </div>
        </div>
      `;

      area.innerHTML = `
        <div style="background: var(--neutral-50); border: 1px solid var(--neutral-200); border-radius: 8px; padding: 1.15rem; margin-top: 1rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.75rem;">
            <strong style="font-size: 1.05rem; color: var(--primary); font-family: monospace;">${{req.id}}</strong>
            ${{statusBadge}}
          </div>
          <div style="font-size: 0.85rem; color: var(--neutral-600); margin-bottom: 0.75rem; display: flex; flex-direction: column; gap: 4px;">
            <div style="display: flex; align-items: center; gap: 6px;">${{vIcons.user}} <strong>ผู้เบิก:</strong> ${{req.requester}} (${{req.dept}})</div>
            <div style="display: flex; align-items: center; gap: 6px;">${{vIcons.clock}} <strong>วันที่ขอ:</strong> ${{req.date}}</div>
          </div>
          ${{timelineHtml}}
          <div style="font-size: 0.85rem; border-top: 1px dashed var(--neutral-200); padding-top: 0.65rem;">
            <strong>รายการพัสดุ:</strong>
            <ul style="padding-left: 1.25rem; margin-top: 4px;">
              ${{req.items.map(i => `<li>${{i.name}}: ขอ ${{i.totalPieces.toLocaleString()}} ${{i.unitPiece}} (อนุมัติ ${{(i.approvedPieces ?? i.totalPieces).toLocaleString()}} ${{i.unitPiece}})</li>`).join('')}}
            </ul>
          </div>
          <div style="margin-top: 0.85rem; display: flex; justify-content: flex-end;">
            <button class="btn btn-outline" style="font-size: 0.8rem; padding: 0.35rem 0.75rem;" onclick="openRequisitionPdf('${{req.id}}')">
              ${{vIcons.file_text}} พิมพ์ใบขอเบิกพัสดุ (PDF)
            </button>
          </div>
        </div>
      `;
    }}

    // Requisition Official PDF Viewer (Requester Portal)
    function openRequisitionPdf(docNo) {{
      const reqs = getReqsDB();
      const req = reqs.find(r => r.id === docNo);
      if (!req) {{
        Swal.fire({{
          icon: 'error',
          title: 'ไม่พบเอกสาร',
          text: `ไม่พบข้อมูลเอกสารเลขที่ ${{docNo}}`,
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        }});
        return;
      }}

      document.getElementById('pdfDocNo').innerText = req.id;
      document.getElementById('pdfDate').innerText = req.date || '21 ตุลาคม 2569';
      document.getElementById('pdfDept').innerText = req.dept;
      document.getElementById('pdfRequester').innerText = req.requester + (req.phone ? ` (โทร ${{req.phone}})` : '');
      document.getElementById('pdfPurpose').innerText = req.purpose || '-';
      document.getElementById('pdfSigRequester').innerText = req.requester;
      document.getElementById('pdfSigRecipient').innerText = req.requester;

      const tbody = document.getElementById('pdfItemsTbody');
      tbody.innerHTML = (req.items || []).map((it, idx) => {{
        let reqQty = it.qtyBoxes > 0 && it.qtyPieces > 0 ?
          `${{it.qtyBoxes}} ${{it.unitBox}} + ${{it.qtyPieces}} ${{it.unitPiece}} (รวม ${{it.totalPieces.toLocaleString()}} ${{it.unitPiece}})` :
          (it.qtyBoxes > 0 ? `${{it.qtyBoxes}} ${{it.unitBox}} (${{it.totalPieces.toLocaleString()}} ${{it.unitPiece}})` : `${{it.qtyPieces}} ${{it.unitPiece}}`);
        
        let approvedQty = it.approvedPieces !== undefined ? `${{it.approvedPieces.toLocaleString()}} ${{it.unitPiece}}` : (req.status === 'COMPLETED' ? reqQty : '-');

        let noteText = 'รออนุมัติ';
        if (req.status === 'APPROVED') noteText = 'อนุมัติแล้ว';
        else if (req.status === 'COMPLETED') noteText = 'จ่ายพัสดุครบถ้วน';
        else if (req.status === 'REJECTED') noteText = 'ไม่อนุมัติ';

        return `
          <tr>
            <td style="text-align: center;">${{idx + 1}}</td>
            <td><strong>${{it.name}}</strong></td>
            <td style="text-align: right;">${{reqQty}}</td>
            <td style="text-align: right; font-weight: 600; color: ${{req.status === 'COMPLETED' ? '#059669' : '#000'}};">${{approvedQty}}</td>
            <td style="text-align: center; font-size: 0.85rem; color: #555;">${{noteText}}</td>
          </tr>
        `;
      }}).join('');

      const sigBox = document.getElementById('pdfSigOfficerBox');
      if (req.signature) {{
        sigBox.innerHTML = `<img src="${{req.signature}}" class="sig-img-preview" alt="ลายเซ็นดิจิทัลผู้รับพัสดุ">`;
      }} else {{
        sigBox.innerHTML = `<div>ลงชื่อ.......................................................</div>`;
      }}

      const modal = document.getElementById('requisitionPdfModal');
      modal.style.display = 'flex';
      modal.classList.add('open');
    }}

    function closeRequisitionPdfModal() {{
      const modal = document.getElementById('requisitionPdfModal');
      modal.style.display = 'none';
      modal.classList.remove('open');
    }}

    function printRequisitionPdf() {{
      window.print();
    }}

    // Initial Load
    document.addEventListener('DOMContentLoaded', () => {{
      getDeptsDB();
      getUsersDB();
      getItemsDB();
      getReqsDB();
      renderCatalog();
      updateMyReqsBadge();
      syncFromMySQLAPI();
    }});

    // Real-time synchronization across tabs/windows
    window.addEventListener('storage', (e) => {{
      if (e.key === DB_REQS_KEY || e.key === DB_ITEMS_KEY) {{
        updateMyReqsBadge();
        renderCatalog();
        const myReqModal = document.getElementById('myRequisitionsModal');
        if (myReqModal && myReqModal.classList.contains('open')) {{
          renderMyRequisitionsModal();
        }}
      }}
      if (e.key === DB_USERS_KEY) {{
        const userDd = document.getElementById('userDropdownList');
        if (userDd && userDd.classList.contains('open')) {{
          renderUserDropdown(document.getElementById('requesterName').value);
        }}
      }}
      if (e.key === DB_DEPTS_KEY) {{
        const deptDd = document.getElementById('deptDropdownList');
        if (deptDd && deptDd.classList.contains('open')) {{
          renderDeptDropdown(document.getElementById('deptSearchInput').value);
        }}
      }}
    }});
  </script>
</body>
</html>
'''

with open(os.path.join(PROJECT_ROOT, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(requester_html)

print("Created index.html (Requester Only Portal)")


# --------------------------------------------------------------------
# 2. WRITE STAFF.HTML (INVENTORY STAFF & ADMIN PORTAL)
# --------------------------------------------------------------------
staff_html = f'''<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ระบบบริหารคลังพัสดุ (Staff Portal) | มหาวิทยาลัยสวนดุสิต</title>
  
  <!-- PWA & Mobile Icons -->
  <meta name="theme-color" content="#1e40af">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="คลังพัสดุ มสด.">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
  <link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="assets/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="assets/apple-touch-icon.png">
  <link rel="manifest" href="manifest.json">

  <!-- Google Fonts: Prompt for modern UI, Sarabun for official doc/text -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&family=Sarabun:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  
  <!-- SweetAlert2 (Offline local asset with CDN fallback) -->
  <script src="assets/js/sweetalert2.all.min.js"></script>
  <script>
    if (typeof Swal === 'undefined') {{
      document.write('<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"><\\/script>');
    }}
  </script>
  
  <style>
{common_css}

    /* Staff Specific Styles */
    .dashboard-header {{
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem;
    }}
    .dashboard-header h2 {{ font-size: 1.35rem; font-weight: 700; color: var(--neutral-900); }}

    .status-tabs {{ display: flex; gap: 0.5rem; background: var(--neutral-100); padding: 4px; border-radius: 8px; }}
    .status-tab {{
      padding: 0.45rem 1rem; border: none; background: transparent; font-family: inherit;
      font-size: 0.85rem; font-weight: 500; color: var(--neutral-600); border-radius: 6px;
      cursor: pointer; display: flex; align-items: center; gap: 0.4rem;
    }}
    .status-tab.active {{ background: white; color: var(--primary); font-weight: 600; box-shadow: var(--shadow-sm); }}
    .count-tag {{ font-size: 0.7rem; padding: 1px 6px; border-radius: 999px; background: var(--neutral-200); color: var(--neutral-700); }}
    .status-tab.active .count-tag {{ background: var(--primary-light); color: var(--primary); }}

    .requisition-card {{
      background: white; border: 1px solid var(--neutral-200); border-radius: var(--radius);
      padding: 1.25rem 1.5rem; margin-bottom: 1rem; box-shadow: var(--shadow-sm);
      display: flex; flex-direction: column; gap: 1rem; transition: border-color 0.2s;
    }}
    .requisition-card:hover {{ border-color: var(--neutral-300); }}
    .req-top-row {{ display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem; }}
    .req-doc-id {{ font-size: 1.05rem; font-weight: 700; color: var(--primary); display: flex; align-items: center; gap: 0.5rem; }}
    .req-badge {{ display: inline-block; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }}
    .badge-pending {{ background: var(--warning-light); color: var(--warning); }}
    .badge-approved {{ background: #e0e7ff; color: #4338ca; }}
    .badge-completed {{ background: #dcfce7; color: #15803d; }}
    .badge-rejected {{ background: var(--danger-light); color: var(--danger); }}

    .req-details-grid {{
      display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 0.75rem; font-size: 0.85rem; color: var(--neutral-600);
    }}
    .req-details-grid div {{ display: flex; align-items: center; gap: 0.4rem; }}
    .req-table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; margin: 0.5rem 0; }}
    .req-table th {{ background: var(--neutral-100); text-align: left; padding: 0.5rem 0.75rem; font-weight: 600; color: var(--neutral-700); border-bottom: 1px solid var(--neutral-200); }}
    .req-table td {{ padding: 0.5rem 0.75rem; border-bottom: 1px solid var(--neutral-100); }}
    .req-actions {{ display: flex; justify-content: flex-end; gap: 0.75rem; flex-wrap: wrap; padding-top: 0.5rem; border-top: 1px solid var(--neutral-100); }}

    /* Navigation tabs */
    .view-switcher {{ display: flex; background: var(--neutral-100); padding: 4px; border-radius: 10px; gap: 4px; }}
    .view-btn {{
      padding: 0.5rem 1rem; border: none; background: transparent; font-family: inherit;
      font-size: 0.875rem; font-weight: 500; color: var(--neutral-600); border-radius: 8px;
      cursor: pointer; display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s ease;
    }}
    .view-btn:hover {{ color: var(--neutral-900); }}
    .view-btn.active {{ background: white; color: var(--primary); font-weight: 600; box-shadow: var(--shadow-sm); }}

    .view-content {{ display: none; }}
    .view-content.active {{ display: block; animation: fadeIn 0.25s ease-out; }}

    /* Canvas Signature Pad */
    .signature-pad-container {{ border: 2px dashed var(--neutral-300); border-radius: 8px; background: #fafafa; position: relative; touch-action: none; }}
    canvas#signaturePad {{ width: 100%; height: 200px; display: block; cursor: crosshair; }}
    .signature-placeholder {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 0.9rem; color: var(--neutral-400); pointer-events: none; }}



    /* Metrics */
    .metrics-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem; margin-bottom: 1.5rem; }}
    .metric-card {{ background: white; border: 1px solid var(--neutral-200); border-radius: var(--radius); padding: 1.25rem; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; gap: 0.4rem; }}
    .metric-header {{ display: flex; align-items: center; gap: 0.5rem; color: var(--neutral-600); font-size: 0.825rem; font-weight: 500; }}
    .metric-val {{ font-size: 1.6rem; font-weight: 700; color: var(--neutral-900); }}

    /* Login Screen Gate */
    .login-container {{
      max-width: 420px; margin: 4rem auto; background: white; border-radius: 12px;
      padding: 2rem; border: 1px solid var(--neutral-200); box-shadow: var(--shadow-lg);
    }}
  </style>
</head>
<body>

  <!-- LOGIN SCREEN (If not authenticated) -->
  <div id="loginScreen" class="login-container" style="display: none;">
    <div style="text-align: center; margin-bottom: 1.5rem;">
      <img src="assets/logo_sdu.png" alt="มหาวิทยาลัยสวนดุสิต" style="height: 72px; width: auto; object-fit: contain; margin-bottom: 0.75rem; filter: drop-shadow(0 2px 6px rgba(0,0,0,0.1));">
      <h2 style="font-size: 1.25rem; font-weight: 700; color: var(--neutral-900);">เข้าสู่ระบบเจ้าหน้าที่พัสดุ</h2>
      <p style="font-size: 0.85rem; color: var(--neutral-600); margin-top: 4px;">ฝ่ายพัสดุและคลังสินค้ากลาง มหาวิทยาลัยสวนดุสิต</p>
    </div>

    <form onsubmit="handleStaffLogin(event)" style="display: flex; flex-direction: column; gap: 1rem;">
      <div class="form-group">
        <label>{svg_icons['user']} ชื่อผู้ใช้งาน (Username)</label>
        <input type="text" id="loginUsername" class="form-control" value="admin_staff" required>
      </div>
      <div class="form-group">
        <label>{svg_icons['lock']} รหัสผ่าน (Password)</label>
        <input type="password" id="loginPassword" class="form-control" value="••••••••" required>
      </div>
      <button type="submit" class="btn btn-primary" style="justify-content: center; padding: 0.75rem; margin-top: 0.5rem;">
        เข้าสู่ระบบจัดการคลังพัสดุ
      </button>
    </form>

    <div style="margin-top: 1.5rem; text-align: center; border-top: 1px solid var(--neutral-200); padding-top: 1rem; display: flex; justify-content: center; gap: 0.75rem; align-items: center;">
      <a href="portal.html" style="font-size: 0.85rem; color: var(--primary); text-decoration: none; font-weight: 500;">
        ศูนย์กลางพอร์ทัล
      </a>
      <span style="color: var(--neutral-300);">|</span>
      <a href="index.html" style="font-size: 0.85rem; color: var(--neutral-600); text-decoration: none;">
        หน้าขอเบิกพัสดุ (สำหรับผู้เบิก) →
      </a>
    </div>
  </div>

  <!-- AUTHENTICATED STAFF PORTAL APP -->
  <div id="staffPortalApp">
    <!-- Top Navigation Header -->
    <header>
      <div class="nav-container">
        <div class="brand">
          <img src="assets/logo_sdu.png" alt="มหาวิทยาลัยสวนดุสิต" class="brand-logo-img">
          <div class="brand-text">
            <h1>ระบบบริหารคลังพัสดุ (Staff Portal)</h1>
            <p>ฝ่ายพัสดุและคลังสินค้ากลาง มหาวิทยาลัยสวนดุสิต</p>
          </div>
        </div>

        <!-- View Switcher Tabs -->
        <nav class="view-switcher">
          <button class="view-btn active" onclick="switchStaffView('requisitions')">
            {svg_icons['clipboard']} รายการคำขอเบิก <span class="count-tag" id="navPendingBadge">0</span>
          </button>
          <button class="view-btn" onclick="switchStaffView('inventory')">
            {svg_icons['chart']} สรุปยอดสต๊อกคลัง
          </button>
          <button class="view-btn" onclick="switchStaffView('users')">
            {svg_icons['user']} จัดการบุคลากร / หน่วยงาน <span class="count-tag" id="navUsersBadge">4</span>
          </button>
        </nav>

        <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
          <a href="portal.html" class="btn btn-outline" style="font-size: 0.8rem; padding: 0.4rem 0.75rem;">
            {svg_icons['layers']} ศูนย์กลางพอร์ทัล
          </a>
          <a href="index.html" target="_blank" class="btn btn-outline" style="font-size: 0.8rem; padding: 0.4rem 0.75rem;">
            เปิดหน้าผู้เบิก ↗
          </a>
          <button class="btn btn-outline" style="color: var(--danger); font-size: 0.8rem; padding: 0.4rem 0.75rem;" onclick="logoutStaff()">
            {svg_icons['log_out']} ออกจากระบบ
          </button>
        </div>
      </div>
    </header>

    <main>
      <!-- TAB 1: REQUISITION MANAGEMENT -->
      <section id="view-requisitions" class="view-content active">
        <div class="dashboard-header">
          <div>
            <h2>จัดการและอนุมัติคำขอเบิกพัสดุ</h2>
            <p style="color: var(--neutral-600); font-size: 0.85rem;">ตรวจสอบคำขอที่ส่งมาจากอาจารย์/หน่วยงาน, อนุมัติกันยอดสต๊อก, และจ่ายของพร้อมเซ็นชื่อ</p>
          </div>
          <div class="status-tabs">
            <button class="status-tab active" onclick="filterStaffRequisitionStatus('PENDING', this)">
              รออนุมัติ <span class="count-tag" id="pendingCount">0</span>
            </button>
            <button class="status-tab" onclick="filterStaffRequisitionStatus('APPROVED', this)">
              รอจ่ายของ <span class="count-tag" id="approvedCount">0</span>
            </button>
            <button class="status-tab" onclick="filterStaffRequisitionStatus('COMPLETED', this)">
              จ่ายสำเร็จแล้ว <span class="count-tag" id="completedCount">0</span>
            </button>
            <button class="status-tab" onclick="filterStaffRequisitionStatus('REJECTED', this)">
              ไม่อนุมัติ / ยกเลิก <span class="count-tag" id="rejectedCount">0</span>
            </button>
          </div>
        </div>

        <div id="requisitionsContainer">
          <!-- Rendered dynamically by JS -->
        </div>
      </section>

      <!-- TAB 2: INVENTORY & STOCK MANAGEMENT -->
      <section id="view-inventory" class="view-content">
        <div class="metrics-row">
          <div class="metric-card">
            <div class="metric-header">{svg_icons['box']} รายการพัสดุทั้งหมดในระบบ</div>
            <span class="metric-val" id="metricTotalItems">34 <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">รายการ</small></span>
          </div>
          <div class="metric-card">
            <div class="metric-header" style="color: var(--danger);">{svg_icons['alert_triangle']} พัสดุต่ำกว่าเกณฑ์ขั้นต่ำ (Reorder Alert)</div>
            <span class="metric-val" style="color: var(--danger);" id="metricLowStock">12 <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">รายการ</small></span>
          </div>
          <div class="metric-card">
            <div class="metric-header" style="color: var(--primary);">{svg_icons['clock']} ยอดจองรอจ่าย (Reserved Stock)</div>
            <span class="metric-val" style="color: var(--primary);" id="metricReserved">0 <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">ชิ้น</small></span>
          </div>
          <div class="metric-card">
            <div class="metric-header" style="color: var(--accent);">{svg_icons['calendar']} รอบบัญชีปัจจุบัน</div>
            <span class="metric-val" style="color: var(--accent);">ต.ค. 2569</span>
          </div>
        </div>

        <div style="background: white; border-radius: var(--radius); border: 1px solid var(--neutral-200); padding: 1.5rem; box-shadow: var(--shadow-sm);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
            <h3 style="font-size: 1.1rem; font-weight: 700;">ตารางรายการสต๊อกคงเหลือจริง (On-Hand vs Available)</h3>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
              <button class="btn btn-outline" onclick="simulateExcelImport()">
                {svg_icons['upload']} นำเข้าจาก Excel
              </button>
              <button class="btn btn-outline" onclick="openStockAdjustModal()">
                {svg_icons['edit']} ปรับยอดสต๊อก (Adjustment)
              </button>
              <button class="btn btn-outline" onclick="openStockInModal()">
                {svg_icons['plus']} บันทึกรับเข้าพัสดุ (เติมสต๊อก)
              </button>
              <button class="btn btn-primary" onclick="openItemModal()">
                {svg_icons['plus']} เพิ่มรายการพัสดุใหม่
              </button>
            </div>
          </div>

          <div style="overflow-x: auto;">
            <table class="req-table" style="font-size: 0.9rem;">
              <thead>
                <tr>
                  <th style="width: 60px;">ลำดับ</th>
                  <th>ชื่อรายการพัสดุ</th>
                  <th>หน่วยบรรจุ</th>
                  <th>คงคลังจริง (On-Hand)</th>
                  <th>ยอดจอง (Reserved)</th>
                  <th>พร้อมเบิก (Available)</th>
                  <th>สถานะสต๊อก</th>
                  <th style="width: 150px; text-align: right;">จัดการ</th>
                </tr>
              </thead>
              <tbody id="inventoryTableBody">
                <!-- Rendered by JS -->
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- TAB 3: USER & DEPARTMENT MANAGEMENT (สวท.) -->
      <section id="view-users" class="view-content">
        <div class="metrics-row">
          <div class="metric-card">
            <div class="metric-header">{svg_icons['user']} บุคลากรผู้มีสิทธิ์เบิกทั้งหมด</div>
            <span class="metric-val" id="metricTotalUsers">4 <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">ท่าน</small></span>
          </div>
          <div class="metric-card">
            <div class="metric-header" style="color: var(--primary);">{svg_icons['building']} กลุ่มงาน / หน่วยงานภายใน สวท.</div>
            <span class="metric-val" style="color: var(--primary);" id="metricTotalDepts">5 <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">หน่วยงาน</small></span>
          </div>
        </div>

        <div style="background: white; border-radius: var(--radius); border: 1px solid var(--neutral-200); padding: 1.5rem; box-shadow: var(--shadow-sm);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem;">
            <div>
              <h3 style="font-size: 1.1rem; font-weight: 700;">ทำเนียบรายชื่อบุคลากรและกลุ่มงาน สวท.</h3>
              <p style="font-size: 0.825rem; color: var(--neutral-600);">ข้อมูลตั้งต้นจากไฟล์ รายนามบุคลากร สวท.docx — เจ้าหน้าที่สามารถเพิ่ม แก้ไข หรือลบรายชื่อบุคลากรและกลุ่มงานได้ตลอดเวลา</p>
            </div>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
              <button class="btn btn-outline" onclick="openAddDeptModal()">
                {svg_icons['building']} + เพิ่มกลุ่มงาน/หน่วยงาน
              </button>
              <button class="btn btn-primary" onclick="openUserModal()">
                {svg_icons['plus']} เพิ่มรายชื่อบุคลากร (User)
              </button>
            </div>
          </div>

          <div style="display: flex; gap: 0.75rem; margin-bottom: 1rem; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 240px;">
              <input type="text" id="staffUserSearchInput" class="form-control"
                     placeholder="พิมพ์ค้นหาชื่อ-นามสกุล, ตำแหน่ง หรือกลุ่มงาน..."
                     oninput="renderStaffUsersTable()">
            </div>
            <div style="min-width: 240px;">
              <select id="staffUserDeptFilter" class="form-control" onchange="renderStaffUsersTable()">
                <option value="ALL">ทุกกลุ่มงาน / หน่วยงานทั้งหมด</option>
              </select>
            </div>
          </div>

          <div style="overflow-x: auto;">
            <table class="req-table" style="font-size: 0.9rem;">
              <thead>
                <tr>
                  <th style="width: 60px; text-align: center;">ลำดับ</th>
                  <th>ชื่อ-นามสกุล</th>
                  <th>ตำแหน่ง</th>
                  <th>กลุ่มงาน / หน่วยงานที่สังกัด</th>
                  <th style="width: 140px;">เบอร์โทรศัพท์</th>
                  <th style="width: 160px; text-align: right;">จัดการ</th>
                </tr>
              </thead>
              <tbody id="staffUsersTableBody">
                <!-- Rendered by JS -->
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- TAB 3: OFFICIAL PDF PRINTABLE PREVIEW -->
      <section id="view-pdf" class="view-content">
        <div class="pdf-preview-container">
          <div class="pdf-preview-actions" style="display: flex; gap: 1rem;">
            <button class="btn btn-success" onclick="window.print()">
              {svg_icons['printer']} สั่งพิมพ์เอกสารราชการ (Print PDF)
            </button>
            <button class="btn btn-outline" style="background: white;" onclick="switchStaffView('requisitions')">
              {svg_icons['arrow_left']} กลับหน้ารายการเบิก
            </button>
          </div>

          <div class="pdf-page" id="printablePdf">
            <div class="pdf-header">
              <img src="assets/logo_sdu.png" alt="ตราสัญลักษณ์ มหาวิทยาลัยสวนดุสิต" style="height: 75px; width: auto; object-fit: contain; margin-bottom: 0.5rem;">
              <h2>ใบขอเบิกพัสดุ</h2>
              <p>ฝ่ายพัสดุและคลังสินค้ากลาง มหาวิทยาลัยสวนดุสิต</p>
            </div>

            <table class="pdf-meta-table">
              <tr>
                <td style="width: 55%;"><strong>เลขที่เอกสาร:</strong> <span id="pdfDocNo">REQ-256910-0042</span></td>
                <td><strong>วันที่ขอเบิก:</strong> <span id="pdfDate">21 ต.ค. 2569</span></td>
              </tr>
              <tr>
                <td><strong>หน่วยงาน/กลุ่มงาน:</strong> <span id="pdfDept">สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน</span></td>
                <td><strong>ชื่อผู้ขอเบิก:</strong> <span id="pdfRequester">นางสาววาสนา จันทร์จ่าย</span></td>
              </tr>
              <tr>
                <td colspan="2"><strong>วัตถุประสงค์ในการขอเบิก:</strong> <span id="pdfPurpose">ใช้สำหรับจัดส่งเอกสารราชการและหนังสือสำคัญ ประจำภาคการศึกษา 1/2569</span></td>
              </tr>
            </table>

            <table class="pdf-items-table">
              <thead>
                <tr>
                  <th style="width: 45px;">ลำดับ</th>
                  <th>รายการพัสดุ</th>
                  <th style="width: 140px;">จำนวนที่ขอเบิก</th>
                  <th style="width: 140px;">จำนวนจ่ายจริง</th>
                  <th style="width: 100px;">หมายเหตุ</th>
                </tr>
              </thead>
              <tbody id="pdfItemsTbody">
                <!-- Rendered by JS -->
              </tbody>
            </table>

            <div style="font-size: 0.85rem; margin-top: 1rem;">
              * ข้าพเจ้าได้รับมอบพัสดุตามรายการและจำนวนที่ระบุข้างต้นไว้ในสภาพเรียบร้อยครบถ้วนแล้ว
            </div>

            <!-- Signatures Section -->
            <div class="pdf-signatures">
              <div class="sig-box">
                <div class="sig-line"></div>
                <div>( <span id="pdfSignRequester">นางสาววาสนา จันทร์จ่าย</span> )</div>
                <div style="font-size: 0.75rem; color: #666;">ผู้ขอเบิกพัสดุ</div>
                <div style="font-size: 0.75rem; color: #666;">21 ต.ค. 2569</div>
              </div>

              <div class="sig-box">
                <div style="font-size: 0.8rem; color: #0284c7; font-weight: bold; margin-bottom: 8px;">[ ประทับตราอนุมัติ ]</div>
                <div class="sig-line"></div>
                <div>( นางสมศรี พัสดุดี )</div>
                <div style="font-size: 0.75rem; color: #666;">เจ้าหน้าที่พัสดุผู้จ่ายของ</div>
                <div style="font-size: 0.75rem; color: #666;">21 ต.ค. 2569 11:15 น.</div>
              </div>

              <div class="sig-box">
                <div id="pdfReceiverSigArea">
                  <!-- Signature will be placed here -->
                </div>
                <div class="sig-line"></div>
                <div>( <span id="pdfReceiverName">นางสาววาสนา จันทร์จ่าย</span> )</div>
                <div style="font-size: 0.75rem; color: #666;">ผู้รับพัสดุ</div>
                <div style="font-size: 0.75rem; color: #666;" id="pdfReceiveTime">21 ต.ค. 2569</div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>

  <!-- MODAL: E-SIGNATURE PAD -->
  <div class="modal-overlay" id="signatureModal">
    <div class="modal-card">
      <div class="modal-header">
        <h3>{svg_icons['pen_tool']} ลงนามรับมอบพัสดุ (E-Signature)</h3>
        <button class="close-btn" onclick="closeSignatureModal()">{svg_icons['x']}</button>
      </div>
      <div class="modal-body">
        <p style="font-size: 0.875rem; color: var(--neutral-600);">
          ผู้รับของ: <strong id="sigModalRequesterName" style="color: var(--neutral-900);">นางสาววาสนา จันทร์จ่าย</strong> 
          (<span id="sigModalDocNo">REQ-256910-0042</span>)
        </p>

        <div class="signature-pad-container">
          <canvas id="signaturePad"></canvas>
          <div class="signature-placeholder" id="sigPlaceholder">ใช้นิ้วหรือเมาส์เซ็นลายมือชื่อที่นี่</div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 0.75rem; color: var(--neutral-400);">ระบบจะนำลายเซ็นไปประทับในเอกสารใบเบิก PDF ทันที</span>
          <button class="btn btn-outline" style="font-size: 0.75rem; padding: 4px 8px;" onclick="clearSignature()">
            ล้างลายเซ็น
          </button>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-outline" onclick="closeSignatureModal()">ยกเลิก</button>
        <button class="btn btn-success" onclick="confirmSignatureAndComplete()">
          {svg_icons['check']} ยืนยันจ่ายของและบันทึกลายเซ็น
        </button>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <footer style="text-align: center; padding: 2rem 1rem; color: var(--neutral-400); font-size: 0.85rem; border-top: 1px solid var(--neutral-200); margin-top: 3rem; background: white;">
    <div>
      © 2569 ระบบบริหารคลังพัสดุ มหาวิทยาลัยสวนดุสิต (Staff Portal v{SYSTEM_VERSION}) | ใช้งานเฉพาะภายในสถาบัน
    </div>
  </footer>

  <!-- Scripts -->
  <script>
    const APP_VERSION = '{SYSTEM_VERSION}';
    const MYSQL_API_URL = '{MYSQL_API_URL}';
    const vIcons = {{
      box: `{svg_icons['box']}`,
      cart: `{svg_icons['cart']}`,
      layers: `{svg_icons['layers']}`,
      tag: `{svg_icons['tag']}`,
      trash: `{svg_icons['trash']}`,
      pen: `{svg_icons['pen_tool']}`,
      check: `{svg_icons['check']}`,
      x: `{svg_icons['x']}`,
      eye: `{svg_icons['eye']}`,
      printer: `{svg_icons['printer']}`,
      building: `{svg_icons['building']}`,
      user: `{svg_icons['user']}`,
      calendar: `{svg_icons['calendar']}`,
      fileText: `{svg_icons['file_text']}`
    }};

    const DB_ITEMS_KEY = 'inventory_items';
    const DB_REQS_KEY = 'inventory_requisitions';
    const DB_USERS_KEY = 'inventory_users';
    const DB_DEPTS_KEY = 'inventory_departments';

    const defaultItems = {json.dumps(initial_items, ensure_ascii=False)};
    const defaultReqs = {json.dumps(initial_requisitions, ensure_ascii=False)};
    const defaultDepts = {dept_json_str};
    const defaultUsers = {users_json_str};

    function getDeptsDB() {{
      const data = localStorage.getItem(DB_DEPTS_KEY);
      if (!data) {{
        localStorage.setItem(DB_DEPTS_KEY, JSON.stringify(defaultDepts));
        return JSON.parse(JSON.stringify(defaultDepts));
      }}
      try {{
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed) && parsed.length > 0 && parsed[0].category && parsed[0].category.includes('สวท')) {{
          return parsed;
        }}
        localStorage.setItem(DB_DEPTS_KEY, JSON.stringify(defaultDepts));
        return JSON.parse(JSON.stringify(defaultDepts));
      }} catch (e) {{
        localStorage.setItem(DB_DEPTS_KEY, JSON.stringify(defaultDepts));
        return JSON.parse(JSON.stringify(defaultDepts));
      }}
    }}
    function saveDeptsDB(depts) {{ localStorage.setItem(DB_DEPTS_KEY, JSON.stringify(depts)); }}

    function getUsersDB() {{
      const data = localStorage.getItem(DB_USERS_KEY);
      if (!data) {{
        localStorage.setItem(DB_USERS_KEY, JSON.stringify(defaultUsers));
        return JSON.parse(JSON.stringify(defaultUsers));
      }}
      try {{
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed) && parsed.length > 0) {{
          // Auto-migrate if localStorage still had the old 29-user list (contains ผอ.อังค์ริสา)
          if (parsed.some(u => u.name && u.name.includes('อังค์ริสา'))) {{
            const customAdded = parsed.filter(u => Number(u.id) > 29);
            const migrated = [
              ...JSON.parse(JSON.stringify(defaultUsers)),
              ...customAdded.map((u, idx) => ({{ ...u, id: defaultUsers.length + idx + 1 }}))
            ];
            localStorage.setItem(DB_USERS_KEY, JSON.stringify(migrated));
            return migrated;
          }}
          return parsed;
        }}
        localStorage.setItem(DB_USERS_KEY, JSON.stringify(defaultUsers));
        return JSON.parse(JSON.stringify(defaultUsers));
      }} catch (e) {{
        localStorage.setItem(DB_USERS_KEY, JSON.stringify(defaultUsers));
        return JSON.parse(JSON.stringify(defaultUsers));
      }}
    }}
    function saveUsersDB(users) {{ localStorage.setItem(DB_USERS_KEY, JSON.stringify(users)); }}

    function getItemsDB() {{
      const data = localStorage.getItem(DB_ITEMS_KEY);
      if (!data) {{
        localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(defaultItems));
        return JSON.parse(JSON.stringify(defaultItems));
      }}
      try {{
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed) && parsed.length > 0) {{
          const defMap = new Map(defaultItems.map(i => [i.id, i]));
          let needsSave = false;
          const upgraded = parsed.map(ex => {{
            const defItem = defMap.get(ex.id);
            if (defItem && ex.image_piece && ex.image_piece.startsWith('assets/images/image')) {{
              needsSave = true;
              return {{ ...defItem, on_hand_pieces: ex.on_hand_pieces, reserved_pieces: ex.reserved_pieces }};
            }}
            return ex;
          }});
          if (needsSave) localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(upgraded));
          return upgraded;
        }}
        return parsed;
      }} catch (e) {{
        localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(defaultItems));
        return JSON.parse(JSON.stringify(defaultItems));
      }}
    }}
    function saveItemsDB(items) {{ localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(items)); }}

    function getReqsDB() {{
      const data = localStorage.getItem(DB_REQS_KEY);
      if (!data) {{
        localStorage.setItem(DB_REQS_KEY, JSON.stringify(defaultReqs));
        return defaultReqs;
      }}
      try {{
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed)) {{
          const defMap = new Map(defaultReqs.map(r => [r.id, r]));
          let needsSave = false;
          const updated = parsed.map(r => {{
            const defReq = defMap.get(r.id);
            if (defReq && (r.dept === 'โรงเรียนการเรือน' || r.dept === 'คณะพยาบาลศาสตร์')) {{
              needsSave = true;
              return {{ ...r, dept: defReq.dept, requester: defReq.requester, purpose: defReq.purpose }};
            }}
            return r;
          }});
          if (needsSave) localStorage.setItem(DB_REQS_KEY, JSON.stringify(updated));
          return updated;
        }}
        return parsed;
      }} catch (e) {{
        return defaultReqs;
      }}
    }}
    function saveReqsDB(reqs) {{ localStorage.setItem(DB_REQS_KEY, JSON.stringify(reqs)); }}

    async function syncFromMySQLAPI() {{
      if (!MYSQL_API_URL || !navigator.onLine) return;
      try {{
        const [itemsRes, reqsRes, usersRes, deptsRes] = await Promise.all([
          fetch(`${{MYSQL_API_URL}}?action=getItems`).then(r => r.json()).catch(() => null),
          fetch(`${{MYSQL_API_URL}}?action=getRequisitions`).then(r => r.json()).catch(() => null),
          fetch(`${{MYSQL_API_URL}}?action=getUsers`).then(r => r.json()).catch(() => null),
          fetch(`${{MYSQL_API_URL}}?action=getDepartments`).then(r => r.json()).catch(() => null)
        ]);
        if (itemsRes && itemsRes.status === 'success' && Array.isArray(itemsRes.data) && itemsRes.data.length > 0) {{
          saveItemsDB(itemsRes.data);
        }}
        if (reqsRes && reqsRes.status === 'success' && Array.isArray(reqsRes.data) && reqsRes.data.length > 0) {{
          saveReqsDB(reqsRes.data);
        }}
        if (usersRes && usersRes.status === 'success' && Array.isArray(usersRes.data) && usersRes.data.length > 0) {{
          saveUsersDB(usersRes.data);
        }}
        if (deptsRes && deptsRes.status === 'success' && Array.isArray(deptsRes.data) && deptsRes.data.length > 0) {{
          const grouped = {{}};
          deptsRes.data.forEach(d => {{
            const cat = d.category || 'สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)';
            const lbl = d.full_label || d.name;
            if (!grouped[cat]) grouped[cat] = [];
            if (lbl && !grouped[cat].some(x => x.value === lbl)) {{
              grouped[cat].push({{ label: lbl, value: lbl, sub: false }});
            }}
          }});
          const formattedDepts = Object.keys(grouped).map(k => ({{ category: k, items: grouped[k] }}));
          if (formattedDepts.length > 0) saveDeptsDB(formattedDepts);
        }}
        loadStaffDashboard();
      }} catch (err) {{
        console.warn('Offline fallback active (localStorage):', err);
      }}
    }}

    async function postToMySQLAPI(action, payload) {{
      if (!MYSQL_API_URL || !navigator.onLine) return null;
      try {{
        const res = await fetch(MYSQL_API_URL, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
          body: JSON.stringify({{ action, payload }})
        }});
        return await res.json();
      }} catch (err) {{
        console.warn('MySQL API unreachable, saved to localStorage fallback:', err);
        return null;
      }}
    }}

    // Auth Simulation
    function checkStaffAuth() {{
      const isAuth = sessionStorage.getItem('staff_auth') === 'true';
      if (!isAuth) {{
        document.getElementById('loginScreen').style.display = 'block';
        document.getElementById('staffPortalApp').style.display = 'none';
      }} else {{
        document.getElementById('loginScreen').style.display = 'none';
        document.getElementById('staffPortalApp').style.display = 'block';
        loadStaffDashboard();
      }}
    }}

    function handleStaffLogin(e) {{
      e.preventDefault();
      sessionStorage.setItem('staff_auth', 'true');
      checkStaffAuth();
    }}

    function logoutStaff() {{
      Swal.fire({{
        title: 'ยืนยันออกจากระบบ?',
        text: 'คุณต้องการออกจากระบบเจ้าหน้าที่พัสดุใช่หรือไม่',
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ออกจากระบบ',
        cancelButtonText: 'ยกเลิก'
      }}).then((result) => {{
        if (result.isConfirmed) {{
          sessionStorage.removeItem('staff_auth');
          checkStaffAuth();
        }}
      }});
    }}

    // Navigation
    function switchStaffView(viewName) {{
      document.querySelectorAll('.view-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.view-btn').forEach(el => el.classList.remove('active'));
      
      const target = document.getElementById(`view-${{viewName}}`);
      if (target) target.classList.add('active');

      const btns = document.querySelectorAll('.view-btn');
      if (viewName === 'requisitions' && btns[0]) btns[0].classList.add('active');
      if (viewName === 'inventory' && btns[1]) btns[1].classList.add('active');
      if (viewName === 'users' && btns[2]) btns[2].classList.add('active');
    }}

    // Requisition Management Logic
    let currentStaffStatus = 'PENDING';
    let currentActiveReqForSig = null;

    function filterStaffRequisitionStatus(status, btn) {{
      currentStaffStatus = status;
      document.querySelectorAll('.status-tab').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderStaffRequisitions(status);
    }}

    function renderStaffRequisitions(status) {{
      const reqs = getReqsDB();
      const container = document.getElementById('requisitionsContainer');
      const filtered = reqs.filter(r => r.status === status);

      // Counters
      const pendingCount = reqs.filter(r => r.status === 'PENDING').length;
      document.getElementById('pendingCount').innerText = pendingCount;
      document.getElementById('navPendingBadge').innerText = pendingCount;
      document.getElementById('approvedCount').innerText = reqs.filter(r => r.status === 'APPROVED').length;
      document.getElementById('completedCount').innerText = reqs.filter(r => r.status === 'COMPLETED').length;
      const rejectedEl = document.getElementById('rejectedCount');
      if (rejectedEl) rejectedEl.innerText = reqs.filter(r => r.status === 'REJECTED').length;

      if (filtered.length === 0) {{
        container.innerHTML = `
          <div style="background: white; border-radius: var(--radius); padding: 3rem; text-align: center; color: var(--neutral-400); border: 1px dashed var(--neutral-300);">
            <div style="margin-bottom: 0.5rem;">${{vIcons.fileText}}</div>
            <p>ไม่มีรายการคำขอในสถานะนี้</p>
          </div>
        `;
        return;
      }}

      container.innerHTML = filtered.map(req => {{
        let badgeClass = 'badge-pending';
        let badgeText = 'รออนุมัติ (Pending)';
        if (req.status === 'APPROVED') {{ badgeClass = 'badge-approved'; badgeText = 'อนุมัติแล้ว รอผู้เบิกมารับของ'; }}
        if (req.status === 'COMPLETED') {{ badgeClass = 'badge-completed'; badgeText = 'จ่ายของสำเร็จแล้ว (Completed)'; }}
        if (req.status === 'REJECTED') {{ badgeClass = 'badge-rejected'; badgeText = 'ไม่อนุมัติ / ยกเลิก (Rejected)'; }}
        const reasonStr = req.reject_reason || req.rejectReason || '';

        return `
          <div class="requisition-card">
            <div class="req-top-row">
              <div class="req-doc-id">
                ${{vIcons.fileText}} ${{req.id}}
                <span class="req-badge ${{badgeClass}}">${{badgeText}}</span>
              </div>
              <span style="font-size: 0.8rem; color: var(--neutral-400); display: flex; align-items: center; gap: 4px;">
                ${{vIcons.calendar}} วันที่ขอ: ${{req.date}}
              </span>
            </div>

            <div class="req-details-grid">
              <div>${{vIcons.building}} <strong>หน่วยงาน:</strong> ${{req.dept}}</div>
              <div>${{vIcons.user}} <strong>ผู้ขอเบิก:</strong> ${{req.requester}} (${{req.phone || '-'}})</div>
              <div style="grid-column: 1 / -1;">${{vIcons.fileText}} <strong>วัตถุประสงค์:</strong> ${{req.purpose}}</div>
              ${{req.status === 'REJECTED' && reasonStr ? `
                <div style="grid-column: 1 / -1; background: var(--danger-light); color: #991b1b; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid #fecaca;">
                  <strong>เหตุผลที่ไม่อนุมัติ / ยกเลิก:</strong> ${{reasonStr}}
                </div>
              ` : ''}}
            </div>

            <table class="req-table">
              <thead>
                <tr>
                  <th>รายการพัสดุ</th>
                  <th style="width: 150px;">จำนวนที่ขอ</th>
                  <th style="width: 170px;">จำนวนอนุมัติจ่ายจริง</th>
                  <th style="width: 110px;">สถานะ</th>
                </tr>
              </thead>
              <tbody>
                ${{req.items.map(item => `
                  <tr>
                    <td><strong>${{item.name}}</strong></td>
                    <td>${{item.qtyBoxes > 0 ? `${{item.qtyBoxes}} ${{item.unitBox}} ` : ''}}${{item.qtyPieces > 0 ? `${{item.qtyPieces}} ${{item.unitPiece}}` : ''}} (${{item.totalPieces.toLocaleString()}} ${{item.unitPiece}})</td>
                    <td style="font-weight: 600; color: var(--accent);">
                      ${{req.status === 'PENDING' ? `
                        <div style="display: flex; align-items: center; gap: 6px;">
                          <input type="number" id="approve-qty-${{req.id}}-${{item.itemId}}"
                                 value="${{item.approvedPieces ?? item.totalPieces}}"
                                 min="0" max="${{item.totalPieces}}"
                                 style="width: 85px; padding: 4px 6px; border: 1px solid var(--neutral-300); border-radius: 6px; font-family: inherit; font-weight: 600; text-align: right;">
                          <span>${{item.unitPiece}}</span>
                        </div>
                      ` : `${{(item.approvedPieces ?? item.totalPieces).toLocaleString()}} ${{item.unitPiece}}`}}
                    </td>
                    <td>
                      ${{req.status === 'REJECTED'
                        ? `<span style="color: var(--danger);">ยกเลิก</span>`
                        : `<span style="color: var(--accent);">พร้อมจ่าย</span>`}}
                    </td>
                  </tr>
                `).join('')}}
              </tbody>
            </table>

            <div class="req-actions">
              ${{req.status === 'PENDING' ? `
                <button class="btn btn-outline" style="color: var(--danger);" onclick="rejectRequisition('${{req.id}}')">
                  ${{vIcons.x}} ปฏิเสธคำขอ
                </button>
                <button class="btn btn-primary" onclick="approveRequisition('${{req.id}}')">
                  ${{vIcons.check}} อนุมัติคำขอ (กันสต๊อก)
                </button>
              ` : ''}}

              ${{req.status === 'APPROVED' ? `
                <button class="btn btn-outline" style="color: var(--danger);" onclick="rejectRequisition('${{req.id}}')">
                  ${{vIcons.x}} ยกเลิก / คืนสต๊อกจอง
                </button>
                <button class="btn btn-outline" onclick="previewDocInPdf('${{req.id}}')">
                  ${{vIcons.eye}} ดูตัวอย่างใบเบิก PDF
                </button>
                <button class="btn btn-success" onclick="openSignatureModal('${{req.id}}')">
                  ${{vIcons.pen}} จ่ายของและเซ็นชื่อรับ (E-Signature)
                </button>
              ` : ''}}

              ${{req.status === 'COMPLETED' ? `
                <button class="btn btn-outline" onclick="previewDocInPdf('${{req.id}}')">
                  ${{vIcons.printer}} พิมพ์ใบเบิก PDF (มีลายเซ็นแล้ว)
                </button>
              ` : ''}}

              ${{req.status === 'REJECTED' ? `
                <button class="btn btn-outline" onclick="previewDocInPdf('${{req.id}}')">
                  ${{vIcons.eye}} ดูใบคำขอ PDF
                </button>
              ` : ''}}
            </div>
          </div>
        `;
      }}).join('');
    }}

    function approveRequisition(docNo) {{
      const reqs = getReqsDB();
      const items = getItemsDB();
      const req = reqs.find(r => r.id === docNo);
      if (!req) return;

      // Read partial or full approved quantities from inputs
      const updatedItems = req.items.map(i => {{
        const inputEl = document.getElementById(`approve-qty-${{docNo}}-${{i.itemId}}`);
        const val = inputEl ? parseInt(inputEl.value, 10) : (i.approvedPieces ?? i.totalPieces);
        const cleanVal = isNaN(val) || val < 0 ? 0 : val;
        return {{ ...i, approvedPieces: cleanVal }};
      }});

      // Validate stock availability before locking Reserved
      for (const i of updatedItems) {{
        const itm = items.find(si => si.id === i.itemId);
        if (itm) {{
          const avail = Math.max(0, itm.on_hand_pieces - itm.reserved_pieces);
          if (i.approvedPieces > avail) {{
            Swal.fire({{
              icon: 'error',
              title: 'สต๊อกพร้อมเบิกไม่เพียงพอ',
              html: `รายการ <b>${{itm.name}}</b> มีพร้อมเบิกเพียง <b>${{avail.toLocaleString()}} ${{itm.unit_piece_name}}</b> (ต้องการอนุมัติ ${{i.approvedPieces.toLocaleString()}} ${{itm.unit_piece_name}})`,
              confirmButtonColor: '#1e40af',
              confirmButtonText: 'ตกลง'
            }});
            return;
          }}
        }}
      }}

      Swal.fire({{
        title: 'ยืนยันการอนุมัติคำขอเบิก?',
        html: `
          <div style="text-align: left; font-size: 0.95rem; margin-top: 0.5rem; color: #475569; line-height: 1.6;">
            <p><strong>เลขที่เอกสาร:</strong> <span style="color: #1e40af; font-weight: 700;">${{docNo}}</span></p>
            <p><strong>ผู้ขอเบิก:</strong> ${{req.requester}} (${{req.dept}})</p>
            <p><strong>จำนวนพัสดุ:</strong> ${{req.items.length}} รายการ</p>
            <div style="margin-top: 0.5rem; padding: 0.5rem 0.75rem; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; color: #166534; font-size: 0.85rem;">
              • ระบบจะทำการกันยอดสต๊อก (Reserved Stock) ตามจำนวนที่อนุมัติทันที
            </div>
          </div>
        `,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#1e40af',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ยืนยันอนุมัติ',
        cancelButtonText: 'ยกเลิก'
      }}).then((result) => {{
        if (result.isConfirmed) {{
          req.status = 'APPROVED';
          req.updated_at = new Date().toISOString();
          req.items = updatedItems;
          req.items.forEach(i => {{
            const itm = items.find(si => si.id === i.itemId);
            if (itm) itm.reserved_pieces += i.approvedPieces;
          }});
          saveReqsDB(reqs);
          saveItemsDB(items);
          postToMySQLAPI('approveRequisition', {{
            docNo: docNo,
            items: req.items.map(i => ({{ itemId: i.itemId, approvedPieces: i.approvedPieces }}))
          }});
          renderStaffRequisitions(currentStaffStatus);
          renderInventoryTable();

          Swal.fire({{
            icon: 'success',
            title: 'อนุมัติคำขอสำเร็จ!',
            text: `คำขอเลขที่ ${{docNo}} ได้รับการอนุมัติและกันสต๊อกเรียบร้อยแล้ว`,
            confirmButtonColor: '#1e40af',
            confirmButtonText: 'ตกลง'
          }});
        }}
      }});
    }}

    function rejectRequisition(docNo) {{
      const reqs = getReqsDB();
      const targetReq = reqs.find(r => r.id === docNo);
      if (!targetReq) return;
      const wasApproved = targetReq.status === 'APPROVED';

      Swal.fire({{
        title: wasApproved ? 'ยกเลิกคำขอและคืนสต๊อกจอง' : 'ปฏิเสธคำขอเบิกพัสดุ',
        text: `ระบุเหตุผลในการ${{wasApproved ? 'ยกเลิกและคืนยอดจอง' : 'ไม่อนุมัติ'}}คำขอเลขที่ ${{docNo}}:`,
        input: 'textarea',
        inputPlaceholder: 'เช่น พัสดุในคลังไม่เพียงพอ, ผู้เบิกขอยกเลิก, เกินกำหนดเวลารับของ...',
        inputValue: wasApproved ? 'ผู้ขอเบิกขอยกเลิกรายการ / เกินกำหนดเวลารับพัสดุ (คืนยอดจองเข้าคลัง)' : 'พัสดุในคลังไม่เพียงพอสำหรับรอบการเบิกนี้',
        showCancelButton: true,
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#64748b',
        confirmButtonText: wasApproved ? 'ยืนยันยกเลิกและคืนสต๊อก' : 'ยืนยันปฏิเสธคำขอ',
        cancelButtonText: 'ยกเลิก',
        inputValidator: (val) => {{
          if (!val || !val.trim()) {{
            return 'กรุณาระบุเหตุผลครับ!';
          }}
        }}
      }}).then((result) => {{
        if (result.isConfirmed && result.value) {{
          const items = getItemsDB();
          const req = reqs.find(r => r.id === docNo);
          if (req) {{
            // If previously APPROVED, release reserved_pieces back to stock
            if (req.status === 'APPROVED') {{
              req.items.forEach(i => {{
                const itm = items.find(si => si.id === i.itemId);
                if (itm) {{
                  itm.reserved_pieces = Math.max(0, itm.reserved_pieces - (i.approvedPieces ?? i.totalPieces));
                }}
              }});
              saveItemsDB(items);
            }}
            req.status = 'REJECTED';
            req.reject_reason = result.value.trim();
            req.rejectReason = result.value.trim();
            req.updated_at = new Date().toISOString();
            saveReqsDB(reqs);
            postToMySQLAPI('rejectRequisition', {{ docNo: docNo, reason: req.reject_reason }});
            renderStaffRequisitions(currentStaffStatus);
            renderInventoryTable();

            Swal.fire({{
              icon: 'warning',
              title: wasApproved ? 'ยกเลิกและคืนยอดสต๊อกเรียบร้อยแล้ว' : 'ปฏิเสธคำขอเรียบร้อยแล้ว',
              text: `คำขอ ${{docNo}} ถูกเปลี่ยนสถานะเป็นไม่อนุมัติ/ยกเลิกเรียบร้อยแล้ว`,
              confirmButtonColor: '#1e40af',
              confirmButtonText: 'ตกลง'
            }});
          }}
        }}
      }});
    }}

    // E-Signature
    let canvas, ctx, isDrawing = false, hasDrawnSignature = false;
    function initSignaturePad() {{
      canvas = document.getElementById('signaturePad');
      ctx = canvas.getContext('2d');
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * 2;
      canvas.height = rect.height * 2;
      ctx.scale(2, 2);
      ctx.strokeStyle = '#0f172a';
      ctx.lineWidth = 2.5;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      function getPos(e) {{
        const r = canvas.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        return {{ x: clientX - r.left, y: clientY - r.top }};
      }}
      function startDraw(e) {{
        e.preventDefault(); isDrawing = true; hasDrawnSignature = true;
        const pos = getPos(e); ctx.beginPath(); ctx.moveTo(pos.x, pos.y);
        document.getElementById('sigPlaceholder').style.display = 'none';
      }}
      function draw(e) {{
        if (!isDrawing) return; e.preventDefault();
        const pos = getPos(e); ctx.lineTo(pos.x, pos.y); ctx.stroke();
      }}
      function stopDraw(e) {{ if (isDrawing) {{ isDrawing = false; ctx.closePath(); }} }}

      canvas.onmousedown = startDraw;
      canvas.onmousemove = draw;
      canvas.onmouseup = stopDraw;
      canvas.onmouseleave = stopDraw;
      canvas.ontouchstart = startDraw;
      canvas.ontouchmove = draw;
      canvas.ontouchend = stopDraw;
    }}

    function openSignatureModal(docNo) {{
      const reqs = getReqsDB();
      currentActiveReqForSig = reqs.find(r => r.id === docNo);
      if (!currentActiveReqForSig) return;

      document.getElementById('sigModalRequesterName').innerText = currentActiveReqForSig.requester;
      document.getElementById('sigModalDocNo').innerText = currentActiveReqForSig.id;
      document.getElementById('signatureModal').classList.add('open');

      setTimeout(() => {{
        initSignaturePad();
        clearSignature();
      }}, 100);
    }}

    function closeSignatureModal() {{
      document.getElementById('signatureModal').classList.remove('open');
    }}

    function clearSignature() {{
      hasDrawnSignature = false;
      if (ctx && canvas) {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        document.getElementById('sigPlaceholder').style.display = 'block';
      }}
    }}

    function confirmSignatureAndComplete() {{
      if (!currentActiveReqForSig) return;
      if (!hasDrawnSignature) {{
        Swal.fire({{
          icon: 'warning',
          title: 'กรุณาลงลายมือชื่อ',
          text: 'กรุณาให้ผู้รับพัสดุเซ็นชื่อบนกรอบกระดานดิจิทัลก่อนกดยืนยันการจ่ายของครับ',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        }});
        return;
      }}
      const sigDataUrl = canvas.toDataURL('image/png');
      const reqs = getReqsDB();
      const items = getItemsDB();

      const req = reqs.find(r => r.id === currentActiveReqForSig.id);
      if (req) {{
        req.signature = sigDataUrl;
        req.status = 'COMPLETED';
        req.updated_at = new Date().toISOString();

        // Deduct permanently from On-Hand and release Reserved
        req.items.forEach(i => {{
          const itm = items.find(si => si.id === i.itemId);
          if (itm) {{
            const deductQty = i.approvedPieces ?? i.totalPieces;
            itm.on_hand_pieces = Math.max(0, itm.on_hand_pieces - deductQty);
            itm.reserved_pieces = Math.max(0, itm.reserved_pieces - deductQty);
          }}
        }});

        saveReqsDB(reqs);
        saveItemsDB(items);
        postToMySQLAPI('completeRequisition', {{
          docNo: req.id,
          signature: sigDataUrl
        }});
      }}

      closeSignatureModal();
      renderStaffRequisitions('APPROVED');
      renderInventoryTable();

      Swal.fire({{
        icon: 'success',
        title: 'บันทึกการจ่ายของและเซ็นรับสำเร็จ!',
        html: `
          <div style="margin: 0.5rem 0; color: #475569; font-size: 0.95rem;">
            ระบบได้ตัดยอดสต๊อกคงคลังและประทับตราลายเซ็นดิจิทัลลงในเอกสารเรียบร้อยแล้ว
          </div>
        `,
        confirmButtonColor: '#059669',
        confirmButtonText: 'ดูใบเบิก PDF (พร้อมลายเซ็น)'
      }}).then(() => {{
        previewDocInPdf(currentActiveReqForSig.id);
      }});
    }}

    function simulateExcelImport() {{
      const items = getItemsDB();
      Swal.fire({{
        title: 'นำเข้าข้อมูลสต๊อกจาก Excel',
        html: `
          <div style="text-align: left; margin: 0.5rem 0; color: #475569; font-size: 0.95rem;">
            <p style="margin-bottom: 0.5rem;">ตรวจสอบฐานข้อมูลจากไฟล์ <b>"data/ยอดสต๊อก ตค.xlsx"</b>:</p>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem; font-size: 0.85rem; color: #334155; line-height: 1.6;">
              • รายการพัสดุที่นำเข้าสำเร็จ: <b>${{items.length}} รายการ (58 รูปภาพพัสดุจริง)</b><br>
              • สถานะการซิงค์: <b>ข้อมูลสต๊อกและอัตราส่วนแปลงหน่วยพร้อมใช้งาน 100%</b><br>
              • หมวดหมู่: <b>ซองเอกสาร, กระดาษและแบบฟอร์ม, เครื่องเขียนและแฟ้ม</b>
            </div>
          </div>
        `,
        icon: 'success',
        confirmButtonColor: '#1e40af',
        confirmButtonText: 'ตกลง'
      }});
    }}

    function openStockInModal() {{
      const items = getItemsDB();
      const options = items.map(i => {{
        const ratioTxt = i.is_multi_unit ? ` [1 ${{i.unit_box_name}} = ${{i.pieces_per_box}} ${{i.unit_piece_name}}]` : '';
        return `<option value="${{i.id}}">${{i.name}}${{ratioTxt}} (คงเหลือ: ${{i.on_hand_pieces.toLocaleString()}} ${{i.unit_piece_name}})</option>`;
      }}).join('');

      Swal.fire({{
        title: 'บันทึกรับเข้าพัสดุใหม่ (Stock-In)',
        html: `
          <div style="text-align: left; display: flex; flex-direction: column; gap: 0.75rem; margin-top: 0.5rem;">
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #475569;">เลือกรายการพัสดุ:</label>
              <select id="swalStockItem" class="swal2-select" style="width: 100%; margin: 4px 0 0 0; font-family: inherit; font-size: 0.9rem; padding: 0.5rem; border-radius: 8px; border: 1px solid #cbd5e1;">
                ${{options}}
              </select>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
              <div>
                <label style="font-size: 0.85rem; font-weight: 600; color: #475569;">จำนวนหน่วยใหญ่ (กล่อง/ห่อ):</label>
                <input type="number" id="swalStockBoxes" min="0" placeholder="0" class="swal2-input" style="width: 100%; margin: 4px 0 0 0; height: 42px; font-size: 1rem; border-radius: 8px;">
              </div>
              <div>
                <label style="font-size: 0.85rem; font-weight: 600; color: #475569;">จำนวนหน่วยย่อย (ชิ้น/ซอง/ใบ):</label>
                <input type="number" id="swalStockQty" min="0" placeholder="0" class="swal2-input" style="width: 100%; margin: 4px 0 0 0; height: 42px; font-size: 1rem; border-radius: 8px;">
              </div>
            </div>
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #475569;">หมายเหตุ / เลขที่ใบส่งของ (ถ้ามี):</label>
              <input type="text" id="swalStockNote" placeholder="เช่น PO-2569-001 หรือ รับเข้าประจำเดือน..." class="swal2-input" style="width: 100%; margin: 4px 0 0 0; height: 42px; font-size: 0.9rem; border-radius: 8px;">
            </div>
          </div>
        `,
        showCancelButton: true,
        confirmButtonColor: '#1e40af',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ยืนยันรับเข้าคลัง',
        cancelButtonText: 'ยกเลิก',
        preConfirm: () => {{
          const itemId = parseInt(document.getElementById('swalStockItem').value, 10);
          const boxes = parseInt(document.getElementById('swalStockBoxes').value, 10) || 0;
          const pieces = parseInt(document.getElementById('swalStockQty').value, 10) || 0;
          if (boxes <= 0 && pieces <= 0) {{
            Swal.showValidationMessage('กรุณาระบุจำนวนที่รับเข้าอย่างน้อย 1 กล่องหรือ 1 ชิ้นครับ');
            return false;
          }}
          return {{ itemId, boxes, pieces }};
        }}
      }}).then((res) => {{
        if (res.isConfirmed && res.value) {{
          const {{ itemId, boxes, pieces }} = res.value;
          const items = getItemsDB();
          const itm = items.find(i => i.id === itemId);
          if (itm) {{
            const ratio = itm.is_multi_unit ? (itm.pieces_per_box || 1) : 1;
            const totalAdded = (boxes * ratio) + pieces;
            itm.on_hand_pieces += totalAdded;
            saveItemsDB(items);
            postToMySQLAPI('restockItem', {{ itemId: itm.id, quantityPieces: totalAdded }});
            renderInventoryTable();

            Swal.fire({{
              icon: 'success',
              title: 'รับเข้าพัสดุสำเร็จ!',
              text: `เพิ่ม "${{itm.name}}" รวม ${{totalAdded.toLocaleString()}} ${{itm.unit_piece_name}} เข้าสต๊อกเรียบร้อยแล้ว`,
              confirmButtonColor: '#1e40af',
              confirmButtonText: 'ตกลง'
            }});
          }}
        }}
      }});
    }}

    function openStockAdjustModal() {{
      const items = getItemsDB();
      const options = items.map(i => `<option value="${{i.id}}">${{i.name}} (คงคลังปัจจุบัน: ${{i.on_hand_pieces.toLocaleString()}} ${{i.unit_piece_name}})</option>`).join('');

      Swal.fire({{
        title: 'ปรับยอดสต๊อกจริง (Stock Adjustment)',
        html: `
          <div style="text-align: left; display: flex; flex-direction: column; gap: 0.75rem; margin-top: 0.5rem;">
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #475569;">เลือกรายการพัสดุ:</label>
              <select id="swalAdjItem" class="swal2-select" style="width: 100%; margin: 4px 0 0 0; font-family: inherit; font-size: 0.9rem; padding: 0.5rem; border-radius: 8px; border: 1px solid #cbd5e1;">
                ${{options}}
              </select>
            </div>
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #475569;">ยอดคงคลังจริงที่ตรวจนับได้ (หน่วยย่อย):</label>
              <input type="number" id="swalAdjNewQty" min="0" placeholder="ระบุยอดคงคลังจริงจากการตรวจนับ" class="swal2-input" style="width: 100%; margin: 4px 0 0 0; height: 42px; font-size: 1rem; border-radius: 8px;">
            </div>
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #475569;">เหตุผลในการปรับยอดสต๊อก *:</label>
              <select id="swalAdjReason" class="swal2-select" style="width: 100%; margin: 4px 0 0 0; font-family: inherit; font-size: 0.9rem; padding: 0.5rem; border-radius: 8px; border: 1px solid #cbd5e1;">
                <option value="ตรวจนับสต๊อกประจำงวดบัญชี">ตรวจนับสต๊อกประจำงวดบัญชี</option>
                <option value="พัสดุชำรุด / เสื่อมสภาพ">พัสดุชำรุด / เสื่อมสภาพ</option>
                <option value="พัสดุสูญหาย / คลาดเคลื่อน">พัสดุสูญหาย / คลาดเคลื่อน</option>
                <option value="ปรับปรุงยอดยกมาต้นงวด">ปรับปรุงยอดยกมาต้นงวด</option>
              </select>
            </div>
          </div>
        `,
        showCancelButton: true,
        confirmButtonColor: '#1e40af',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'บันทึกการปรับยอด',
        cancelButtonText: 'ยกเลิก',
        preConfirm: () => {{
          const itemId = parseInt(document.getElementById('swalAdjItem').value, 10);
          const rawVal = document.getElementById('swalAdjNewQty').value;
          const newQty = parseInt(rawVal, 10);
          const reason = document.getElementById('swalAdjReason').value;
          if (rawVal === '' || isNaN(newQty) || newQty < 0) {{
            Swal.showValidationMessage('กรุณาระบุยอดคงคลังจริงที่ถูกต้อง (ตั้งแต่ 0 ขึ้นไป) ครับ');
            return false;
          }}
          return {{ itemId, newQty, reason }};
        }}
      }}).then((res) => {{
        if (res.isConfirmed && res.value) {{
          const {{ itemId, newQty, reason }} = res.value;
          const items = getItemsDB();
          const itm = items.find(i => i.id === itemId);
          if (itm) {{
            const oldQty = itm.on_hand_pieces;
            itm.on_hand_pieces = newQty;
            saveItemsDB(items);
            postToMySQLAPI('adjustStock', {{ itemId: itm.id, newQty: newQty, reason: reason }});
            renderInventoryTable();

            Swal.fire({{
              icon: 'success',
              title: 'ปรับปรุงยอดสต๊อกสำเร็จ!',
              html: `รายการ <b>${{itm.name}}</b><br>ปรับยอดจาก ${{oldQty.toLocaleString()}} เป็น <b>${{newQty.toLocaleString()}} ${{itm.unit_piece_name}}</b><br><small style="color:#64748b;">เหตุผล: ${{reason}}</small>`,
              confirmButtonColor: '#1e40af',
              confirmButtonText: 'ตกลง'
            }});
          }}
        }}
      }});
    }}

    // PDF Preview
    function previewDocInPdf(docNo) {{
      const reqs = getReqsDB();
      const req = reqs.find(r => r.id === docNo);
      if (!req) return;

      document.getElementById('pdfDocNo').innerText = req.id;
      const pdfDateEl = document.getElementById('pdfDate');
      if (pdfDateEl) pdfDateEl.innerText = req.date || '21 ต.ค. 2569';
      document.getElementById('pdfDept').innerText = req.dept;
      document.getElementById('pdfRequester').innerText = req.requester + (req.phone ? ` (โทร ${{req.phone}})` : '');
      document.getElementById('pdfPurpose').innerText = req.purpose;
      document.getElementById('pdfSignRequester').innerText = req.requester;
      document.getElementById('pdfReceiverName').innerText = req.requester;

      const tbody = document.getElementById('pdfItemsTbody');
      tbody.innerHTML = req.items.map((item, idx) => `
        <tr>
          <td style="text-align: center;">${{idx + 1}}</td>
          <td>${{item.name}}</td>
          <td style="text-align: center;">${{item.qtyBoxes > 0 ? `${{item.qtyBoxes}} ${{item.unitBox}} ` : ''}}${{item.qtyPieces > 0 ? `${{item.qtyPieces}} ${{item.unitPiece}}` : ''}}</td>
          <td style="text-align: center; font-weight: bold; color: #166534;">${{(item.approvedPieces ?? item.totalPieces).toLocaleString()}} ${{item.unitPiece}}</td>
          <td style="text-align: center;">${{req.status === 'REJECTED' ? 'ไม่อนุมัติ' : 'ครบถ้วน'}}</td>
        </tr>
      `).join('');

      const sigArea = document.getElementById('pdfReceiverSigArea');
      if (req.signature) {{
        sigArea.innerHTML = `<img src="${{req.signature}}" class="sig-img-preview" alt="ลายเซ็นดิจิทัล">`;
        document.getElementById('pdfReceiveTime').innerText = `เซ็นรับเมื่อ: ${{req.date || '21 ต.ค. 2569'}} (E-Signature)`;
      }} else {{
        sigArea.innerHTML = `<div style="height: 50px; display: flex; align-items: center; justify-content: center; color: #999; font-style: italic;">[ ยังไม่ได้เซ็นรับของ ]</div>`;
        document.getElementById('pdfReceiveTime').innerText = `วันที่รับของจริง: .......................................`;
      }}
      switchStaffView('pdf');
    }}

    // Inventory Table
    function formatStockDisplay(totalPieces, ratio, boxName, pieceName, isMulti) {{
      if (!isMulti || ratio <= 1) return `${{totalPieces.toLocaleString()}} ${{pieceName}}`;
      const boxes = Math.floor(totalPieces / ratio);
      const pieces = totalPieces % ratio;
      if (boxes > 0 && pieces > 0) return `${{boxes}} ${{boxName}} ${{pieces}} ${{pieceName}}`;
      if (boxes > 0) return `${{boxes}} ${{boxName}}`;
      return `${{pieces}} ${{pieceName}}`;
    }}

    function renderInventoryTable() {{
      const items = getItemsDB();
      const tbody = document.getElementById('inventoryTableBody');

      let totalReserved = 0;
      let lowStockCount = 0;

      tbody.innerHTML = items.map((item, idx) => {{
        const available = Math.max(0, item.on_hand_pieces - item.reserved_pieces);
        const isLow = available <= item.min_alert;
        totalReserved += item.reserved_pieces;
        if (isLow) lowStockCount++;

        return `
          <tr>
            <td style="text-align: center;">${{idx + 1}}</td>
            <td><strong>${{item.name}}</strong></td>
            <td>${{item.is_multi_unit ? `1 ${{item.unit_box_name}} = ${{item.pieces_per_box}} ${{item.unit_piece_name}}` : `หน่วยเดี่ยว (${{item.unit_piece_name}})`}}</td>
            <td>${{item.on_hand_pieces.toLocaleString()}} ${{item.unit_piece_name}}</td>
            <td style="color: var(--primary); font-weight: 500;">${{item.reserved_pieces.toLocaleString()}} ${{item.unit_piece_name}}</td>
            <td style="font-weight: 700; color: ${{isLow ? 'var(--danger)' : 'var(--accent)'}};">
              ${{formatStockDisplay(available, item.pieces_per_box, item.unit_box_name, item.unit_piece_name, item.is_multi_unit)}}
            </td>
            <td>
              ${{isLow ? `
                <span style="background: var(--danger-light); color: var(--danger); font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 999px;">
                  ต่ำกว่าเกณฑ์ (${{item.min_alert}})
                </span>
              ` : `
                <span style="background: #dcfce7; color: #166534; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 999px;">
                  ปกติ
                </span>
              `}}
            </td>
            <td style="text-align: right; white-space: nowrap;">
              <button class="btn btn-outline" style="padding: 4px 10px; font-size: 0.775rem; margin-right: 4px;" onclick="openItemModal(${{item.id}})">
                แก้ไข
              </button>
              <button class="btn btn-outline" style="padding: 4px 10px; font-size: 0.775rem; color: var(--danger);" onclick="deleteInventoryItem(${{item.id}})">
                ลบ
              </button>
            </td>
          </tr>
        `;
      }}).join('');

      const totalItemsEl = document.getElementById('metricTotalItems');
      if (totalItemsEl) {{
        totalItemsEl.innerHTML = `${{items.length.toLocaleString()}} <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">รายการ</small>`;
      }}
      document.getElementById('metricReserved').innerHTML = `${{totalReserved.toLocaleString()}} <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">ชิ้น</small>`;
      document.getElementById('metricLowStock').innerHTML = `${{lowStockCount}} <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">รายการ</small>`;
    }}

    function readFileAsDataURL(fileInput) {{
      return new Promise((resolve) => {{
        if (!fileInput || !fileInput.files || !fileInput.files[0]) {{
          resolve(null);
          return;
        }}
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = () => resolve(null);
        reader.readAsDataURL(fileInput.files[0]);
      }});
    }}

    function openItemModal(itemId = null) {{
      const items = getItemsDB();
      const existing = itemId !== null ? items.find(i => Number(i.id) === Number(itemId)) : null;
      const categories = ['ซองเอกสาร', 'กระดาษและแบบฟอร์ม', 'เครื่องเขียนและแฟ้ม'];
      const catOptions = categories.map(c =>
        `<option value="${{c}}" ${{existing && existing.category === c ? 'selected' : ''}}>${{c}}</option>`
      ).join('');
      const isMulti = existing ? Boolean(existing.is_multi_unit) : true;

      Swal.fire({{
        title: existing ? 'แก้ไขรายการพัสดุ' : 'เพิ่มรายการพัสดุใหม่เข้าคลัง',
        width: 600,
        html: `
          <div style="text-align: left; display: flex; flex-direction: column; gap: 0.75rem; margin-top: 0.5rem; font-size: 0.9rem;">
            <div>
              <label style="font-size: 0.825rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">ชื่อรายการพัสดุ *</label>
              <input id="swal-item-name" class="swal2-input" style="margin: 0; width: 100%; height: 40px; font-size: 0.925rem;" placeholder="เช่น กระดาษ A4 80 แกรม (ห่อละ 500 แผ่น)" value="${{existing ? existing.name : ''}}">
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
              <div>
                <label style="font-size: 0.825rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">หมวดหมู่พัสดุ *</label>
                <select id="swal-item-cat" class="swal2-input" style="margin: 0; width: 100%; height: 40px; font-size: 0.9rem;">
                  ${{catOptions}}
                </select>
              </div>
              <div>
                <label style="font-size: 0.825rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">รูปแบบหน่วยนับ</label>
                <select id="swal-item-multi" class="swal2-input" style="margin: 0; width: 100%; height: 40px; font-size: 0.9rem;"
                        onchange="document.getElementById('swal-multi-box-wrap').style.display = this.value === '1' ? 'grid' : 'none';">
                  <option value="1" ${{isMulti ? 'selected' : ''}}>2 หน่วยนับ (เช่น กล่อง/ซอง)</option>
                  <option value="0" ${{!isMulti ? 'selected' : ''}}>หน่วยนับเดี่ยว (เช่น อัน, เล่ม)</option>
                </select>
              </div>
            </div>
            <div id="swal-multi-box-wrap" style="display: ${{isMulti ? 'grid' : 'none'}}; grid-template-columns: 1fr 1fr; gap: 0.75rem; background: #f8fafc; padding: 0.65rem; border-radius: 8px; border: 1px solid #e2e8f0;">
              <div>
                <label style="font-size: 0.8rem; font-weight: 600; color: #1e40af; display: block; margin-bottom: 4px;">ชื่อหน่วยใหญ่ (เช่น กล่อง/ห่อ)</label>
                <input id="swal-item-unit-box" class="swal2-input" style="margin: 0; width: 100%; height: 38px; font-size: 0.9rem;" placeholder="เช่น กล่อง, ห่อ, แพ็ค" value="${{existing ? (existing.unit_box_name || 'กล่อง') : 'กล่อง'}}">
              </div>
              <div>
                <label style="font-size: 0.8rem; font-weight: 600; color: #1e40af; display: block; margin-bottom: 4px;">จำนวนหน่วยย่อยต่อ 1 หน่วยใหญ่</label>
                <input type="number" id="swal-item-ratio" min="1" class="swal2-input" style="margin: 0; width: 100%; height: 38px; font-size: 0.9rem;" placeholder="เช่น 500" value="${{existing ? (existing.pieces_per_box || 1) : 500}}">
              </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.65rem;">
              <div>
                <label style="font-size: 0.8rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">ชื่อหน่วยย่อย *</label>
                <input id="swal-item-unit-piece" class="swal2-input" style="margin: 0; width: 100%; height: 38px; font-size: 0.9rem;" placeholder="เช่น ชิ้น, ซอง, ใบ" value="${{existing ? (existing.unit_piece_name || 'ชิ้น') : 'ชิ้น'}}">
              </div>
              <div>
                <label style="font-size: 0.8rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">ยอดคงคลัง (หน่วยย่อย)</label>
                <input type="number" id="swal-item-onhand" min="0" class="swal2-input" style="margin: 0; width: 100%; height: 38px; font-size: 0.9rem;" value="${{existing ? existing.on_hand_pieces : 100}}">
              </div>
              <div>
                <label style="font-size: 0.8rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">เกณฑ์เตือนขั้นต่ำ</label>
                <input type="number" id="swal-item-min" min="0" class="swal2-input" style="margin: 0; width: 100%; height: 38px; font-size: 0.9rem;" value="${{existing ? existing.min_alert : 20}}">
              </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
              <div>
                <label style="font-size: 0.8rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">รูปภาพหน่วยย่อย (อัปโหลดหรือระบุไฟล์)</label>
                <input type="file" id="swal-item-file-piece" accept="image/*" style="font-size: 0.75rem; width: 100%; margin-bottom: 4px;">
                <input id="swal-item-img-piece" class="swal2-input" style="margin: 0; width: 100%; height: 34px; font-size: 0.8rem;" placeholder="assets/images/..." value="${{existing ? (existing.image_piece || '') : ''}}">
              </div>
              <div>
                <label style="font-size: 0.8rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">รูปภาพหน่วยใหญ่/กล่อง</label>
                <input type="file" id="swal-item-file-box" accept="image/*" style="font-size: 0.75rem; width: 100%; margin-bottom: 4px;">
                <input id="swal-item-img-box" class="swal2-input" style="margin: 0; width: 100%; height: 34px; font-size: 0.8rem;" placeholder="assets/images/..." value="${{existing ? (existing.image_box || '') : ''}}">
              </div>
            </div>
          </div>
        `,
        showCancelButton: true,
        confirmButtonColor: '#1e40af',
        cancelButtonColor: '#64748b',
        confirmButtonText: existing ? 'บันทึกการแก้ไข' : 'เพิ่มรายการพัสดุ',
        cancelButtonText: 'ยกเลิก',
        preConfirm: async () => {{
          const name = document.getElementById('swal-item-name').value.trim();
          const category = document.getElementById('swal-item-cat').value;
          const is_multi_unit = document.getElementById('swal-item-multi').value === '1';
          const unit_piece_name = document.getElementById('swal-item-unit-piece').value.trim() || 'ชิ้น';
          const unit_box_name = is_multi_unit
            ? (document.getElementById('swal-item-unit-box').value.trim() || 'กล่อง')
            : unit_piece_name;
          const pieces_per_box = is_multi_unit
            ? Math.max(1, parseInt(document.getElementById('swal-item-ratio').value, 10) || 1)
            : 1;
          const on_hand_pieces = Math.max(0, parseInt(document.getElementById('swal-item-onhand').value, 10) || 0);
          const min_alert = Math.max(0, parseInt(document.getElementById('swal-item-min').value, 10) || 0);

          if (!name) {{
            Swal.showValidationMessage('กรุณาระบุชื่อรายการพัสดุ');
            return false;
          }}

          const uploadedPiece = await readFileAsDataURL(document.getElementById('swal-item-file-piece'));
          const uploadedBox = await readFileAsDataURL(document.getElementById('swal-item-file-box'));
          const defaultFallbackImg = 'assets/images/แฟ้มเสนอ เล่ม.jpeg';
          const image_piece = uploadedPiece || document.getElementById('swal-item-img-piece').value.trim() || defaultFallbackImg;
          const image_box = uploadedBox || document.getElementById('swal-item-img-box').value.trim() || image_piece;

          return {{
            name,
            category,
            is_multi_unit,
            unit_box_name,
            unit_piece_name,
            pieces_per_box,
            on_hand_pieces,
            min_alert,
            image_piece,
            image_box
          }};
        }}
      }}).then((result) => {{
        if (!result.isConfirmed || !result.value) return;
        const val = result.value;
        const currentItems = getItemsDB();
        let savedItem = null;

        if (existing) {{
          const idx = currentItems.findIndex(i => Number(i.id) === Number(existing.id));
          if (idx !== -1) {{
            currentItems[idx] = {{ ...currentItems[idx], ...val }};
            savedItem = currentItems[idx];
          }}
        }} else {{
          const maxId = currentItems.reduce((m, i) => Math.max(m, Number(i.id) || 0), 0);
          savedItem = {{
            id: maxId + 1,
            ...val,
            reserved_pieces: 0
          }};
          currentItems.push(savedItem);
        }}

        saveItemsDB(currentItems);
        if (savedItem) postToMySQLAPI('saveItem', savedItem);
        renderInventoryTable();

        Swal.fire({{
          icon: 'success',
          title: existing ? 'แก้ไขรายการพัสดุสำเร็จ' : 'เพิ่มรายการพัสดุใหม่สำเร็จ',
          text: `"${{val.name}}" พร้อมให้เบิกใช้งานในหน้าแคตตาล็อกทันที`,
          timer: 2000,
          showConfirmButton: false
        }});
      }});
    }}

    function deleteInventoryItem(itemId) {{
      const items = getItemsDB();
      const target = items.find(i => Number(i.id) === Number(itemId));
      if (!target) return;

      Swal.fire({{
        title: 'ยืนยันการลบรายการพัสดุ?',
        text: `ต้องการลบ "${{target.name}}" ออกจากคลังพัสดุใช่หรือไม่`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ลบรายการพัสดุ',
        cancelButtonText: 'ยกเลิก'
      }}).then((result) => {{
        if (!result.isConfirmed) return;
        const updated = items.filter(i => Number(i.id) !== Number(itemId));
        saveItemsDB(updated);
        postToMySQLAPI('deleteItem', {{ id: itemId }});
        renderInventoryTable();
        Swal.fire({{
          icon: 'success',
          title: 'ลบรายการพัสดุเรียบร้อยแล้ว',
          timer: 1500,
          showConfirmButton: false
        }});
      }});
    }}

    // User & Department Management (Staff Portal)
    function getAllDeptNames() {{
      const deptsData = getDeptsDB();
      const names = [];
      deptsData.forEach(cat => {{
        (cat.items || []).forEach(it => {{
          if (it.value && !names.includes(it.value)) names.push(it.value);
        }});
      }});
      return names;
    }}

    function ensureDeptExists(deptName) {{
      const clean = (deptName || '').trim();
      if (!clean) return;
      const deptsData = getDeptsDB();
      if (deptsData.length === 0) {{
        deptsData.push({{ category: 'สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)', items: [] }});
      }}
      const exists = deptsData.some(c => (c.items || []).some(it => it.value === clean));
      if (!exists) {{
        deptsData[0].items.push({{ label: clean, value: clean, sub: false }});
        saveDeptsDB(deptsData);
        postToMySQLAPI('addDepartment', {{ category: deptsData[0].category, name: clean }});
      }}
    }}

    function renderStaffUsersTable() {{
      const users = getUsersDB();
      const deptNames = getAllDeptNames();

      const navUsersBadge = document.getElementById('navUsersBadge');
      if (navUsersBadge) navUsersBadge.innerText = users.length;

      const totalUsersEl = document.getElementById('metricTotalUsers');
      if (totalUsersEl) {{
        totalUsersEl.innerHTML = `${{users.length.toLocaleString()}} <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">ท่าน</small>`;
      }}
      const totalDeptsEl = document.getElementById('metricTotalDepts');
      if (totalDeptsEl) {{
        totalDeptsEl.innerHTML = `${{deptNames.length.toLocaleString()}} <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">หน่วยงาน</small>`;
      }}

      const filterSelect = document.getElementById('staffUserDeptFilter');
      if (filterSelect) {{
        const prevVal = filterSelect.value || 'ALL';
        filterSelect.innerHTML = `<option value="ALL">ทุกกลุ่มงาน / หน่วยงานทั้งหมด (${{deptNames.length}})</option>` +
          deptNames.map(d => `<option value="${{d}}">${{d}}</option>`).join('');
        if (deptNames.includes(prevVal)) filterSelect.value = prevVal;
      }}

      const searchEl = document.getElementById('staffUserSearchInput');
      const q = (searchEl ? searchEl.value : '').trim().toLowerCase();
      const deptFilter = filterSelect ? filterSelect.value : 'ALL';

      const filtered = users.filter(u => {{
        const matchDept = deptFilter === 'ALL' || u.dept === deptFilter;
        const matchSearch = !q ||
          (u.name && u.name.toLowerCase().includes(q)) ||
          (u.position && u.position.toLowerCase().includes(q)) ||
          (u.dept && u.dept.toLowerCase().includes(q)) ||
          (u.phone && u.phone.toLowerCase().includes(q));
        return matchDept && matchSearch;
      }});

      const tbody = document.getElementById('staffUsersTableBody');
      if (!tbody) return;

      if (filtered.length === 0) {{
        tbody.innerHTML = `
          <tr>
            <td colspan="6" style="text-align: center; padding: 2.5rem; color: var(--neutral-400);">
              ไม่พบรายชื่อบุคลากรที่ตรงกับเงื่อนไขการค้นหา
            </td>
          </tr>
        `;
        return;
      }}

      tbody.innerHTML = filtered.map((u, idx) => `
        <tr>
          <td style="text-align: center; color: var(--neutral-600);">${{idx + 1}}</td>
          <td><strong>${{u.name}}</strong></td>
          <td style="color: var(--neutral-700);">${{u.position || '-'}}</td>
          <td>
            <span style="background: var(--primary-light); color: var(--primary); font-size: 0.775rem; font-weight: 600; padding: 3px 10px; border-radius: 999px; border: 1px solid var(--primary-border); display: inline-block;">
              ${{u.dept || '-'}}
            </span>
          </td>
          <td style="color: var(--neutral-600);">${{u.phone || '-'}}</td>
          <td style="text-align: right; white-space: nowrap;">
            <button class="btn btn-outline" style="padding: 4px 10px; font-size: 0.775rem; margin-right: 4px;" onclick="openUserModal(${{u.id}})">
              แก้ไข
            </button>
            <button class="btn btn-outline" style="padding: 4px 10px; font-size: 0.775rem; color: var(--danger);" onclick="deleteStaffUser(${{u.id}})">
              ลบ
            </button>
          </td>
        </tr>
      `).join('');
    }}

    function openUserModal(userId = null) {{
      const users = getUsersDB();
      const existing = userId !== null ? users.find(u => Number(u.id) === Number(userId)) : null;
      const deptNames = getAllDeptNames();

      const deptOptionsHtml = deptNames.map(d =>
        `<option value="${{d}}" ${{existing && existing.dept === d ? 'selected' : ''}}>${{d}}</option>`
      ).join('') + `<option value="__NEW__">+ เพิ่มกลุ่มงาน / หน่วยงานใหม่...</option>`;

      Swal.fire({{
        title: existing ? 'แก้ไขข้อมูลบุคลากร (User)' : 'เพิ่มรายชื่อบุคลากรใหม่ (User)',
        html: `
          <div style="text-align: left; display: flex; flex-direction: column; gap: 0.85rem; margin-top: 0.5rem;">
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">ชื่อ-นามสกุล บุคลากร *</label>
              <input id="swal-user-name" class="swal2-input" style="margin: 0; width: 100%; font-size: 0.95rem;" placeholder="เช่น นางสาวสมศรี ใจดี" value="${{existing ? existing.name : ''}}">
            </div>
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">ตำแหน่ง</label>
              <input id="swal-user-pos" class="swal2-input" style="margin: 0; width: 100%; font-size: 0.95rem;" placeholder="เช่น เจ้าหน้าบริการการศึกษา, เจ้าหน้าที่สำนักงาน (บริหารงานทั่วไป)" value="${{existing ? (existing.position || '') : ''}}">
            </div>
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">กลุ่มงาน / หน่วยงานที่สังกัด (สวท.) *</label>
              <select id="swal-user-dept" class="swal2-input" style="margin: 0; width: 100%; font-size: 0.9rem;" onchange="document.getElementById('swal-new-dept-wrap').style.display = this.value === '__NEW__' ? 'block' : 'none';">
                ${{deptOptionsHtml}}
              </select>
            </div>
            <div id="swal-new-dept-wrap" style="display: none;">
              <label style="font-size: 0.85rem; font-weight: 600; color: #1e40af; display: block; margin-bottom: 4px;">ระบุชื่อกลุ่มงาน / หน่วยงานใหม่ *</label>
              <input id="swal-user-new-dept" class="swal2-input" style="margin: 0; width: 100%; font-size: 0.95rem;" placeholder="เช่น กลุ่มงานพัฒนาวิชาการ">
            </div>
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">เบอร์โทรศัพท์ติดต่อ</label>
              <input id="swal-user-phone" class="swal2-input" style="margin: 0; width: 100%; font-size: 0.95rem;" placeholder="เช่น 081-234-5678" value="${{existing ? (existing.phone || '') : ''}}">
            </div>
          </div>
        `,
        showCancelButton: true,
        confirmButtonColor: '#1e40af',
        cancelButtonColor: '#64748b',
        confirmButtonText: existing ? 'บันทึกการแก้ไข' : 'เพิ่มรายชื่อบุคลากร',
        cancelButtonText: 'ยกเลิก',
        preConfirm: () => {{
          const name = document.getElementById('swal-user-name').value.trim();
          const position = document.getElementById('swal-user-pos').value.trim();
          const deptSel = document.getElementById('swal-user-dept').value;
          const newDept = document.getElementById('swal-user-new-dept').value.trim();
          const phone = document.getElementById('swal-user-phone').value.trim();
          const finalDept = deptSel === '__NEW__' ? newDept : deptSel;

          if (!name) {{
            Swal.showValidationMessage('กรุณาระบุชื่อ-นามสกุล บุคลากร');
            return false;
          }}
          if (!finalDept) {{
            Swal.showValidationMessage('กรุณาระบุกลุ่มงาน / หน่วยงานที่สังกัด');
            return false;
          }}
          return {{ name, position, dept: finalDept, phone }};
        }}
      }}).then((result) => {{
        if (!result.isConfirmed || !result.value) return;
        const val = result.value;
        ensureDeptExists(val.dept);

        const currentUsers = getUsersDB();
        let savedUser = null;
        if (existing) {{
          const idx = currentUsers.findIndex(u => Number(u.id) === Number(existing.id));
          if (idx !== -1) {{
            currentUsers[idx] = {{ ...currentUsers[idx], ...val }};
            savedUser = currentUsers[idx];
          }}
        }} else {{
          const maxId = currentUsers.reduce((m, u) => Math.max(m, Number(u.id) || 0), 0);
          savedUser = {{
            id: maxId + 1,
            name: val.name,
            position: val.position,
            dept: val.dept,
            phone: val.phone
          }};
          currentUsers.push(savedUser);
        }}

        saveUsersDB(currentUsers);
        if (savedUser) postToMySQLAPI('saveUser', savedUser);
        renderStaffUsersTable();

        Swal.fire({{
          icon: 'success',
          title: existing ? 'อัปเดตข้อมูลบุคลากรสำเร็จ' : 'เพิ่มรายชื่อบุคลากรสำเร็จ',
          text: `${{val.name}} (${{val.dept}}) พร้อมให้เลือกใช้งานในหน้าขอเบิกพัสดุทันที`,
          timer: 2000,
          showConfirmButton: false
        }});
      }});
    }}

    function deleteStaffUser(userId) {{
      const users = getUsersDB();
      const target = users.find(u => Number(u.id) === Number(userId));
      if (!target) return;

      Swal.fire({{
        title: 'ยืนยันการลบรายชื่อบุคลากร?',
        text: `ต้องการลบ "${{target.name}}" (${{target.dept}}) ออกจากระบบใช่หรือไม่`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ลบรายชื่อ',
        cancelButtonText: 'ยกเลิก'
      }}).then((result) => {{
        if (!result.isConfirmed) return;
        const updated = users.filter(u => Number(u.id) !== Number(userId));
        saveUsersDB(updated);
        postToMySQLAPI('deleteUser', {{ id: userId }});
        renderStaffUsersTable();
        Swal.fire({{
          icon: 'success',
          title: 'ลบรายชื่อเรียบร้อยแล้ว',
          timer: 1500,
          showConfirmButton: false
        }});
      }});
    }}

    function openAddDeptModal() {{
      Swal.fire({{
        title: 'เพิ่มกลุ่มงาน / หน่วยงานใหม่ (สวท.)',
        html: `
          <div style="text-align: left; margin-top: 0.5rem;">
            <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 6px;">ชื่อกลุ่มงาน / หน่วยงาน *</label>
            <input id="swal-dept-name" class="swal2-input" style="margin: 0; width: 100%; font-size: 0.95rem;" placeholder="เช่น กลุ่มงานพัฒนาวิชาการ">
          </div>
        `,
        showCancelButton: true,
        confirmButtonColor: '#1e40af',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'เพิ่มหน่วยงาน',
        cancelButtonText: 'ยกเลิก',
        preConfirm: () => {{
          const name = document.getElementById('swal-dept-name').value.trim();
          if (!name) {{
            Swal.showValidationMessage('กรุณาระบุชื่อกลุ่มงาน / หน่วยงาน');
            return false;
          }}
          return name;
        }}
      }}).then((result) => {{
        if (!result.isConfirmed || !result.value) return;
        ensureDeptExists(result.value);
        renderStaffUsersTable();
        Swal.fire({{
          icon: 'success',
          title: 'เพิ่มกลุ่มงาน/หน่วยงานสำเร็จ',
          text: `เพิ่ม "${{result.value}}" เข้าสู่ระบบเรียบร้อยแล้ว`,
          timer: 1800,
          showConfirmButton: false
        }});
      }});
    }}

    function loadStaffDashboard() {{
      renderStaffRequisitions(currentStaffStatus);
      renderInventoryTable();
      renderStaffUsersTable();
    }}

    document.addEventListener('DOMContentLoaded', () => {{
      getDeptsDB();
      getUsersDB();
      checkStaffAuth();
      syncFromMySQLAPI();
    }});

    // Real-time synchronization across tabs/windows
    window.addEventListener('storage', (e) => {{
      if (e.key === DB_REQS_KEY || e.key === DB_ITEMS_KEY || e.key === DB_USERS_KEY || e.key === DB_DEPTS_KEY) {{
        loadStaffDashboard();
      }}
    }});
  </script>
</body>
</html>
'''

with open(os.path.join(PROJECT_ROOT, 'staff.html'), 'w', encoding='utf-8') as f:
    f.write(staff_html)

print("Created staff.html (Inventory Staff & Admin Portal)")
