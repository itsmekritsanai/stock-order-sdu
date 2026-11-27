"""
Seed Data & DOCX Parser for Portal Generator (scripts/portal_parts/seed_data.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

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


    preferred_order = [
        'สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน',
        'กลุ่มงานส่งเสริมวิชาการ',
        'กลุ่มงานบริการวิชาการ',
        'กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ',
        'หน่วยงานศึกษาทั่วไปและการเรียนรู้ตลอดชีวิต',
        'กลุ่มงานเคาน์เตอร์บริการ'
    ]
    for extra_unit in preferred_order:
        if extra_unit not in units:
            units.append(extra_unit)
    ordered_units = [u for u in preferred_order if u in units] + [u for u in units if u not in preferred_order]

    # รายชื่อผู้ใช้งานตั้งต้น 15 ท่านจาก Book1.xlsx (ไม่ฝังรหัสผ่านแบบ plaintext ใน HTML)
    book1_users = [
        {"id": 1, "name": "สมชัย จารุธนกิจพานิช", "username": "somchai_jar", "role": "REQUESTER", "position": "กลุ่มงานเคาน์เตอร์บริการ", "dept": "กลุ่มงานเคาน์เตอร์บริการ", "phone": "5174"},
        {"id": 2, "name": "จิตราพร จันทรกูล", "username": "jittraporn_cha", "role": "HEAD", "position": "รองผู้อำนวยการ", "dept": "สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน", "phone": "5235"},
        {"id": 3, "name": "ทรรศนีย์ สุทธิภาพย์", "username": "tatsanee_soo", "role": "REQUESTER", "position": "กลุ่มงานบริการวิชาการ", "dept": "กลุ่มงานบริการวิชาการ", "phone": "5171"},
        {"id": 4, "name": "สุธางค์ หงษ์กลาง", "username": "sutang_hon", "role": "REQUESTER", "position": "กลุ่มงานบริการวิชาการ", "dept": "กลุ่มงานบริการวิชาการ", "phone": "5173"},
        {"id": 5, "name": "ธนธรณ์ ยิ้มแย้ม", "username": "thanathorn_yim", "role": "REQUESTER", "position": "งานเคาน์เตอร์บริการ", "dept": "กลุ่มงานเคาน์เตอร์บริการ", "phone": "5173"},
        {"id": 6, "name": "สรัลพรรษ ชมศรี", "username": "saranphat_cho", "role": "REQUESTER", "position": "กลุ่มงานบริการวิชาการ", "dept": "กลุ่มงานบริการวิชาการ", "phone": "5173"},
        {"id": 7, "name": "สาริกา เสือบำรุง", "username": "sarika_sua", "role": "REQUESTER", "position": "กลุ่มงานบริการวิชาการ", "dept": "กลุ่มงานบริการวิชาการ", "phone": "5173"},
        {"id": 8, "name": "ณัฐชา แก้ววิมล", "username": "natcha_kae", "role": "REQUESTER", "position": "กลุ่มงานส่งเสริมวิชาการ", "dept": "กลุ่มงานส่งเสริมวิชาการ", "phone": "5173"},
        {"id": 9, "name": "ธนพรรธน์ เอี่ยมสะอาด", "username": "thanaphat_aie", "role": "REQUESTER", "position": "กลุ่มงานส่งเสริมวิชาการ", "dept": "กลุ่มงานส่งเสริมวิชาการ", "phone": "5173"},
        {"id": 10, "name": "รัตติการณ์ คำแก้ววันดี", "username": "ratthikarn_kha", "role": "REQUESTER", "position": "หน่วยงานศึกษาทั่วไปและการเรียนรู้ตลอดชีวิต", "dept": "หน่วยงานศึกษาทั่วไปและการเรียนรู้ตลอดชีวิต", "phone": "5171"},
        {"id": 11, "name": "นายอภิชาติ กรมนา", "username": "apichart_kro", "role": "REQUESTER", "position": "กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ", "dept": "กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ", "phone": "5234"},
        {"id": 12, "name": "อธิพงศ์ อินโท", "username": "atipong_int", "role": "REQUESTER", "position": "กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ", "dept": "กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ", "phone": "5234"},
        {"id": 13, "name": "นายบุญธรรม สังขะเสน", "username": "boonthum_sun", "role": "REQUESTER", "position": "กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ", "dept": "กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ", "phone": "5235"},
        {"id": 14, "name": "จุริรัตน์ สิงอ่อน", "username": "Jabie_Sin", "role": "REQUESTER", "position": "กลุ่มงานบริการวิชาการ", "dept": "กลุ่มงานบริการวิชาการ", "phone": "5173"},
        {"id": 15, "name": "จุฑาธิป ปั้นทอง", "username": "chuthathip_pan", "role": "STAFF", "position": "กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ", "dept": "กลุ่มงานทะเบียนนักศึกษา ฐานข้อมูลฯ", "phone": "5175"},
    ]
    return {"สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)": ordered_units}, book1_users



def build_dept_js_items(depts_data):
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
    return dept_js_items

# Shared Database Initial Data (34 Stock Items aligned with Excel ยอดสต๊อก ตค.xlsx)
initial_items = [
  {"id": 1, "name": "ซองเอกสารสีขาว 7´10 (500 ซองต่อกล่อง)", "category": "ซองเอกสาร", "is_multi_unit": True, "unit_box_name": "กล่อง", "unit_piece_name": "ซอง", "pieces_per_box": 500, "on_hand_pieces": 0, "reserved_pieces": 0, "min_alert": 250, "image_piece": "assets/images/ซองเอกสารสีขาว 7´10 (500 ซองต่อกล่อง) ซอง.jpeg", "image_box": "assets/images/ซองเอกสารสีขาว 7´10 (500 ซองต่อกล่อง) กล่อง.jpeg"},
  {"id": 2, "name": "ซองเอกสารน้ำตาล (มสด) 9´12.3", "category": "ซองเอกสาร", "is_multi_unit": True, "unit_box_name": "กล่อง", "unit_piece_name": "ซอง", "pieces_per_box": 500, "on_hand_pieces": 0, "reserved_pieces": 0, "min_alert": 500, "image_piece": "assets/images/ซองเอกสารน้ำตาล (มสด) 9´12.3 ซอง.jpeg", "image_box": "assets/images/ซองเอกสารน้ำตาล (มสด) 9´12.3 กล่อง.jpeg"},
  {"id": 3, "name": "กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "กล่อง", "unit_piece_name": "ใบ", "pieces_per_box": 2000, "on_hand_pieces": 32000, "reserved_pieces": 0, "min_alert": 5000, "image_piece": "assets/images/กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ) ใบ.jpeg", "image_box": "assets/images/กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ) กล่อง.jpeg"},
  {"id": 4, "name": "ซองขยายข้างมีครุฑ 279´432 (กล่องละ 250 ซอง)", "category": "ซองเอกสาร", "is_multi_unit": True, "unit_box_name": "กล่อง", "unit_piece_name": "ซอง", "pieces_per_box": 250, "on_hand_pieces": 1250, "reserved_pieces": 0, "min_alert": 500, "image_piece": "assets/images/ซองขยายข้างมีครุฑ 279´432 (กล่องละ 250 ซอง) ซอง.jpeg", "image_box": "assets/images/ซองขยายข้างมีครุฑ 279´432 (กล่องละ 250 ซอง) กล่อง.jpeg"},
  {"id": 5, "name": "กระดาษสติ๊กเกอร์แนวนอน ตัดหน้าซองจดหมาย", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ซอง", "unit_piece_name": "แผ่น", "pieces_per_box": 500, "on_hand_pieces": 4500, "reserved_pieces": 0, "min_alert": 500, "image_piece": "assets/images/กระดาษสติ๊กเกอร์แนวนอน ตัดหน้าซองจดหมาย แผ่น.jpeg", "image_box": "assets/images/กระดาษสติ๊กเกอร์แนวนอน ตัดหน้าซองจดหมาย กล่อง.jpeg"},
  {"id": 6, "name": "กระดาษสติ๊กเกอร์แนวตั้ง ติดหน้าซองข้อสอบ", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ซอง", "unit_piece_name": "แผ่น", "pieces_per_box": 500, "on_hand_pieces": 500, "reserved_pieces": 0, "min_alert": 250, "image_piece": "assets/images/กระดาษสติ๊กเกอร์แนวตั้ง ติดหน้าซองข้อสอบ แผ่น.png", "image_box": "assets/images/กระดาษสติ๊กเกอร์แนวตั้ง ติดหน้าซองข้อสอบ กล่อง.jpeg"},
  {"id": 7, "name": "กระดาษลายเส้น (ห่อละ 500 แผ่น)", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ห่อ", "unit_piece_name": "แผ่น", "pieces_per_box": 500, "on_hand_pieces": 23000, "reserved_pieces": 0, "min_alert": 1000, "image_piece": "assets/images/กระดาษลายเส้น (ห่อละ 500 แผ่น) แผ่น.jpeg", "image_box": "assets/images/กระดาษลายเส้น (ห่อละ 500 แผ่น) กล่อง.jpeg"},
  {"id": 8, "name": "กระดาษสติ๊กเกอร์ เต็มแผ่น", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ห่อ", "unit_piece_name": "แผ่น", "pieces_per_box": 500, "on_hand_pieces": 0, "reserved_pieces": 0, "min_alert": 100, "image_piece": "assets/images/กระดาษสติ๊กเกอร์ เต็มแผ่น แผ่น.png", "image_box": "assets/images/กระดาษสติ๊กเกอร์ เต็มแผ่น กล่อง.jpeg"},
  {"id": 9, "name": "แบบฟอร์มแก้ I", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "กล่อง", "unit_piece_name": "ชิ้น", "pieces_per_box": 500, "on_hand_pieces": 2500, "reserved_pieces": 0, "min_alert": 500, "image_piece": "assets/images/แบบฟอร์มแก้ I ชิ้น.jpeg", "image_box": "assets/images/แบบฟอร์มแก้ I กล่อง.jpeg"},
  {"id": 10, "name": "ซองข้อสอบน้ำตาลไม่ขยายข้างพิมพ์ข้อความ (มสด)", "category": "ซองเอกสาร", "is_multi_unit": True, "unit_box_name": "กล่อง", "unit_piece_name": "ซอง", "pieces_per_box": 250, "on_hand_pieces": 3700, "reserved_pieces": 0, "min_alert": 1000, "image_piece": "assets/images/ซองข้อสอบน้ำตาลไม่ขยายข้างพิมพ์ข้อความ (มสด) ซอง.jpeg", "image_box": "assets/images/ซองข้อสอบน้ำตาลไม่ขยายข้างพิมพ์ข้อความ (มสด) กล่อง.jpeg"},
  {"id": 11, "name": "ซองเอกสารไม่ขยายข้าง สีน้ำตาล 10´15 นิ้ว (มสด) (กล่องละ 250 ซอง)", "category": "ซองเอกสาร", "is_multi_unit": True, "unit_box_name": "กล่อง", "unit_piece_name": "ซอง", "pieces_per_box": 250, "on_hand_pieces": 1500, "reserved_pieces": 0, "min_alert": 500, "image_piece": "assets/images/ซองเอกสารไม่ขยายข้าง สีน้ำตาล 10´15 นิ้ว (มสด) (กล่องละ 250 ซอง) ซอง.jpeg", "image_box": "assets/images/ซองเอกสารไม่ขยายข้าง สีน้ำตาล 10´15 นิ้ว (มสด) (กล่องละ 250 ซอง) กล่อง.jpeg"},
  {"id": 12, "name": "แบบฟอร์มทรานสคริป(ไทย)ป.ตรี ซองละ 500 ใบ", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ซอง", "unit_piece_name": "ใบ", "pieces_per_box": 500, "on_hand_pieces": 1500, "reserved_pieces": 0, "min_alert": 300, "image_piece": "assets/images/แบบฟอร์มทรานสคริป(ไทย)ป.ตรี ซองละ 500 ใบ ใบ.png", "image_box": "assets/images/แบบฟอร์มทรานสคริป(ไทย)ป.ตรี ซองละ 500 ใบ กล่อง.jpeg"},
  {"id": 13, "name": "แบบฟอร์มทรานสคริป(อังกฤษ)ป.ตรี ซองละ 500 ใบ", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ซอง", "unit_piece_name": "ใบ", "pieces_per_box": 500, "on_hand_pieces": 3500, "reserved_pieces": 0, "min_alert": 500, "image_piece": "assets/images/แบบฟอร์มทรานสคริป(อังกฤษ)ป.ตรี ซองละ 500 ใบ ใบ.jpeg", "image_box": "assets/images/แบบฟอร์มทรานสคริป(อังกฤษ)ป.ตรี ซองละ 500 ใบ กล่อง.jpeg"},
  {"id": 14, "name": "ทรานสคริป ป.โท(ไทย) ซองละ 500 ใบ", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ซอง", "unit_piece_name": "ใบ", "pieces_per_box": 500, "on_hand_pieces": 1000, "reserved_pieces": 0, "min_alert": 200, "image_piece": "assets/images/ทรานสคริป ป.โท(ไทย) ซองละ 500 ใบ ใบ.png", "image_box": "assets/images/ทรานสคริป ป.โท(ไทย) ซองละ 500 ใบ กล่อง.png"},
  {"id": 15, "name": "ทรานสคริป ป.โท(อังกฤษ) ซองละ 500 ใบ", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ซอง", "unit_piece_name": "ใบ", "pieces_per_box": 500, "on_hand_pieces": 1500, "reserved_pieces": 0, "min_alert": 300, "image_piece": "assets/images/ทรานสคริป ป.โท(อังกฤษ) ซองละ 500 ใบ ใบ.png", "image_box": "assets/images/ทรานสคริป ป.โท(อังกฤษ) ซองละ 500 ใบ กล่อง.jpeg"},
  {"id": 16, "name": "ใบรับรอง(ไทย)ซองละ 500 ใบ", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ซอง", "unit_piece_name": "ใบ", "pieces_per_box": 500, "on_hand_pieces": 2000, "reserved_pieces": 0, "min_alert": 400, "image_piece": "assets/images/ใบรับรอง(ไทย)ซองละ 500 ใบ ใบ.jpeg", "image_box": "assets/images/ใบรับรอง(ไทย)ซองละ 500 ใบ กล่อง.jpeg"},
  {"id": 17, "name": "ใบรับรอง(อังกฤษ)ซองละ 500 ใบ", "category": "กระดาษและแบบฟอร์ม", "is_multi_unit": True, "unit_box_name": "ซอง", "unit_piece_name": "ใบ", "pieces_per_box": 500, "on_hand_pieces": 3000, "reserved_pieces": 0, "min_alert": 500, "image_piece": "assets/images/ใบรับรอง(อังกฤษ)ซองละ 500 ใบ ใบ.png", "image_box": "assets/images/ใบรับรอง(อังกฤษ)ซองละ 500 ใบ กล่อง.png"},
  {"id": 18, "name": "คลิปดำNO.108", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": True, "unit_box_name": "ลัง", "unit_piece_name": "กล่อง", "pieces_per_box": 12, "on_hand_pieces": 72, "reserved_pieces": 0, "min_alert": 24, "image_piece": "assets/images/คลิปดำNO.108 กล่อง.jpeg", "image_box": "assets/images/คลิปดำNO.108 ลัง.jpeg"},
  {"id": 19, "name": "คลิปดำNO.110", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": True, "unit_box_name": "ลัง", "unit_piece_name": "กล่อง", "pieces_per_box": 12, "on_hand_pieces": 60, "reserved_pieces": 0, "min_alert": 24, "image_piece": "assets/images/คลิปดำNO.110 กล่อง.jpeg", "image_box": "assets/images/คลิปดำNO.110 ลัง.jpeg"},
  {"id": 20, "name": "ไส้MAX 10 MM", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": True, "unit_box_name": "ลัง", "unit_piece_name": "กล่อง", "pieces_per_box": 20, "on_hand_pieces": 20, "reserved_pieces": 0, "min_alert": 5, "image_piece": "assets/images/ไส้MAX 10 MM กล่อง.jpeg", "image_box": "assets/images/ไส้MAX 10 MM ลัง.jpeg"},
  {"id": 21, "name": "ไส้MAX 12", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": True, "unit_box_name": "ลัง", "unit_piece_name": "กล่อง", "pieces_per_box": 20, "on_hand_pieces": 20, "reserved_pieces": 0, "min_alert": 5, "image_piece": "assets/images/ไส้MAX 12 กล่อง.jpeg", "image_box": "assets/images/ไส้MAX 12 ลัง.jpeg"},
  {"id": 22, "name": "ซองกันกระแทก 270´327", "category": "ซองเอกสาร", "is_multi_unit": True, "unit_box_name": "กล่อง", "unit_piece_name": "ซอง", "pieces_per_box": 80, "on_hand_pieces": 2400, "reserved_pieces": 0, "min_alert": 500, "image_piece": "assets/images/ซองกันกระแทก 270´327 ซอง.jpeg", "image_box": "assets/images/ซองกันกระแทก 270´327 ซอง.jpeg"},
  {"id": 23, "name": "แฟ้มเสนอ", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "เล่ม", "unit_piece_name": "เล่ม", "pieces_per_box": 1, "on_hand_pieces": 5, "reserved_pieces": 0, "min_alert": 5, "image_piece": "assets/images/แฟ้มเสนอ เล่ม.jpeg", "image_box": "assets/images/แฟ้มเสนอ เล่ม.jpeg"},
  {"id": 24, "name": "แม็กเล็ก", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "กล่อง", "unit_piece_name": "อัน", "pieces_per_box": 1, "on_hand_pieces": 7, "reserved_pieces": 0, "min_alert": 2, "image_piece": "assets/images/แม็กเล็ก อัน.jpeg", "image_box": "assets/images/แม็กเล็ก กล่อง.jpeg"},
  {"id": 25, "name": "แม็กใหญ่", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "กล่อง", "unit_piece_name": "อัน", "pieces_per_box": 1, "on_hand_pieces": 5, "reserved_pieces": 0, "min_alert": 2, "image_piece": "assets/images/แม็กใหญ่ อัน.jpeg", "image_box": "assets/images/แม็กใหญ่ กล่อง.png"},
  {"id": 26, "name": "สก็อตเทปใส", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": True, "unit_box_name": "แพ็ค", "unit_piece_name": "ม้วน", "pieces_per_box": 6, "on_hand_pieces": 4, "reserved_pieces": 0, "min_alert": 6, "image_piece": "assets/images/สก็อตเทปใส ม้วน.jpeg", "image_box": "assets/images/สก็อตเทปใส กล่อง.jpeg"},
  {"id": 27, "name": "สก็อตเทปขุ่น", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": True, "unit_box_name": "แพ็ค", "unit_piece_name": "ม้วน", "pieces_per_box": 6, "on_hand_pieces": 25, "reserved_pieces": 0, "min_alert": 6, "image_piece": "assets/images/สก็อตเทปขุ่น ม้วน.jpeg", "image_box": "assets/images/สก็อตเทปขุ่น กล่อง.png"},
  {"id": 28, "name": "สก็อตเทปย่น", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": True, "unit_box_name": "แพ็ค", "unit_piece_name": "ม้วน", "pieces_per_box": 6, "on_hand_pieces": 0, "reserved_pieces": 0, "min_alert": 6, "image_piece": "assets/images/สก็อตเทปย่น ม้วน.jpeg", "image_box": "assets/images/สก็อตเทปย่น กล่อง.jpeg"},
  {"id": 29, "name": "กาวแท่ง", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "กล่อง", "unit_piece_name": "แท่ง", "pieces_per_box": 1, "on_hand_pieces": 8, "reserved_pieces": 0, "min_alert": 5, "image_piece": "assets/images/กาวแท่ง แท่ง.jpeg", "image_box": "assets/images/กาวแท่ง กล่อง.png"},
  {"id": 30, "name": "กาวขวด", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "กล่อง", "unit_piece_name": "ขวด", "pieces_per_box": 1, "on_hand_pieces": 4, "reserved_pieces": 0, "min_alert": 2, "image_piece": "assets/images/กาวขวด ขวด.jpeg", "image_box": "assets/images/กาวขวด กล่อง.png"},
  {"id": 31, "name": "กรรไกร", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "กล่อง", "unit_piece_name": "อัน", "pieces_per_box": 1, "on_hand_pieces": 20, "reserved_pieces": 0, "min_alert": 5, "image_piece": "assets/images/กรรไกร อัน.jpeg", "image_box": "assets/images/กรรไกร กล่อง.png"},
  {"id": 32, "name": "คัตเตอร์", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "กล่อง", "unit_piece_name": "อัน", "pieces_per_box": 1, "on_hand_pieces": 12, "reserved_pieces": 0, "min_alert": 3, "image_piece": "assets/images/คัตเตอร์ อัน.jpeg", "image_box": "assets/images/คัตเตอร์ กล่อง.png"},
  {"id": 33, "name": "เครื่องเจาะกระดาษ", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "กล่อง", "unit_piece_name": "เครื่อง", "pieces_per_box": 1, "on_hand_pieces": 2, "reserved_pieces": 0, "min_alert": 1, "image_piece": "assets/images/เครื่องเจาะกระดาษ เครื่อง.jpeg", "image_box": "assets/images/เครื่องเจาะกระดาษ กล่อง.png"},
  {"id": 34, "name": "ไม้บรรทัด", "category": "เครื่องเขียนและแฟ้ม", "is_multi_unit": False, "unit_box_name": "กล่อง", "unit_piece_name": "อัน", "pieces_per_box": 1, "on_hand_pieces": 7, "reserved_pieces": 0, "min_alert": 2, "image_piece": "assets/images/ไม้บรรทัด อัน.jpeg", "image_box": "assets/images/ไม้บรรทัด กล่อง.png"}
]

# Initial Requisitions (Aligned with Excel October 2569 actual completed requisitions)
initial_requisitions = [
  {
    "id": "REQ-256910-0001",
    "dept": "โรงเรียนการเรือน",
    "requester": "อาจารย์ผู้แทน โรงเรียนการเรือน",
    "phone": "",
    "purpose": "ใช้สำหรับการจัดการเรียนการสอนและการสอบปฏิบัติการ ประจำภาคการศึกษา 1/2569",
    "date": "1 ต.ค. 2569 09:30 น.",
    "status": "COMPLETED",
    "signature": "ผู้รับพัสดุ: อ.ผู้แทน โรงเรียนการเรือน",
    "reject_reason": "",
    "completed_at": "2026-10-01T03:00:00.000Z",
    "completed_date": "1 ต.ค. 2569 10:00 น.",
    "rejected_at": None,
    "rejected_date": "",
    "created_at": "2026-10-01T02:30:00.000Z",
    "updated_at": "2026-10-01T03:00:00.000Z",
    "items": [
      { "itemId": 3, "name": "กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)", "qtyBoxes": 0, "qtyPieces": 500, "totalPieces": 500, "unitBox": "กล่อง", "unitPiece": "ใบ", "approvedPieces": 500, "piecesPerBoxSnapshot": 2000 },
      { "itemId": 7, "name": "กระดาษลายเส้น (ห่อละ 500 แผ่น)", "qtyBoxes": 1, "qtyPieces": 0, "totalPieces": 500, "unitBox": "ห่อ", "unitPiece": "แผ่น", "approvedPieces": 500, "piecesPerBoxSnapshot": 500 }
    ]
  },
  {
    "id": "REQ-256910-0002",
    "dept": "คณะพยาบาลศาสตร์",
    "requester": "อาจารย์ผู้แทน คณะพยาบาลศาสตร์",
    "phone": "",
    "purpose": "ใช้สำหรับการสอบประเมินความรู้ทางการพยาบาล ภาคเรียน 1/2569",
    "date": "2 ต.ค. 2569 10:15 น.",
    "status": "COMPLETED",
    "signature": "ผู้รับพัสดุ: อ.ผู้แทน คณะพยาบาลศาสตร์",
    "reject_reason": "",
    "completed_at": "2026-10-02T04:00:00.000Z",
    "completed_date": "2 ต.ค. 2569 11:00 น.",
    "rejected_at": None,
    "rejected_date": "",
    "created_at": "2026-10-02T03:15:00.000Z",
    "updated_at": "2026-10-02T04:00:00.000Z",
    "items": [
      { "itemId": 3, "name": "กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)", "qtyBoxes": 0, "qtyPieces": 1000, "totalPieces": 1000, "unitBox": "กล่อง", "unitPiece": "ใบ", "approvedPieces": 1000, "piecesPerBoxSnapshot": 2000 }
    ]
  },
  {
    "id": "REQ-256910-0003",
    "dept": "คณะวิทยาศาสตร์และเทคโนโลยี",
    "requester": "อาจารย์ผู้แทน คณะวิทยาศาสตร์และเทคโนโลยี",
    "phone": "",
    "purpose": "ใช้สำหรับการจัดสอบวัดผลภาคบรรยายและปฏิบัติการ ประจำภาคการศึกษา 1/2569",
    "date": "5 ต.ค. 2569 13:45 น.",
    "status": "COMPLETED",
    "signature": "ผู้รับพัสดุ: อ.ผู้แทน คณะวิทยาศาสตร์และเทคโนโลยี",
    "reject_reason": "",
    "completed_at": "2026-10-05T07:30:00.000Z",
    "completed_date": "5 ต.ค. 2569 14:30 น.",
    "rejected_at": None,
    "rejected_date": "",
    "created_at": "2026-10-05T06:45:00.000Z",
    "updated_at": "2026-10-05T07:30:00.000Z",
    "items": [
      { "itemId": 3, "name": "กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)", "qtyBoxes": 0, "qtyPieces": 1000, "totalPieces": 1000, "unitBox": "กล่อง", "unitPiece": "ใบ", "approvedPieces": 1000, "piecesPerBoxSnapshot": 2000 }
    ]
  },
  {
    "id": "REQ-256911-0004",
    "dept": "สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน",
    "requester": "อาจารย์ผู้แทน สำนักงานผู้อำนวยการ สวท.",
    "phone": "02-244-5200",
    "purpose": "ใช้สำหรับงานประชุมวิชาการและการจัดสอบภาคเรียนที่ 1/2569",
    "date": "10 พ.ย. 2569 11:20 น.",
    "status": "VERIFIED",
    "signature": "",
    "reject_reason": "",
    "completed_at": None,
    "completed_date": "",
    "rejected_at": None,
    "rejected_date": "",
    "verified_by": "เจ้าหน้าที่พัสดุ สวท.",
    "verified_at": "2026-11-10T04:30:00.000Z",
    "verified_date": "10 พ.ย. 2569 11:30 น.",
    "approved_by": "",
    "approved_at": None,
    "approved_date": "",
    "created_at": "2026-11-10T04:20:00.000Z",
    "updated_at": "2026-11-10T04:30:00.000Z",
    "items": [
      { "itemId": 3, "name": "กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)", "qtyBoxes": 0, "qtyPieces": 200, "totalPieces": 200, "unitBox": "กล่อง", "unitPiece": "ใบ", "approvedPieces": 200, "piecesPerBoxSnapshot": 2000 }
    ]
  }
]
