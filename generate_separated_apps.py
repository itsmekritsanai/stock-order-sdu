import json

# Vector icons SVG dictionary for clean inline usage
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
    "external_link": '<svg class="svg-icon svg-icon-sm" viewBox="0 0 24 24"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" x2="21" y1="14" y2="3"/></svg>',
    "lock": '<svg class="svg-icon svg-icon-sm" viewBox="0 0 24 24"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>'
}

# Shared Database Initial Data in JSON string
initial_items = [
  {
    "id": 1,
    "name": "ซองขยายข้างมีครุฑ 279´432 (กล่องละ 250 ซอง)",
    "category": "ซองเอกสาร",
    "is_multi_unit": True,
    "unit_box_name": "กล่อง",
    "unit_piece_name": "ซอง",
    "pieces_per_box": 250,
    "on_hand_pieces": 1750,
    "reserved_pieces": 500,
    "min_alert": 500,
    "image_piece": "assets/images/image1.jpeg",
    "image_box": "assets/images/image10.jpeg"
  },
  {
    "id": 2,
    "name": "กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)",
    "category": "กระดาษและแบบฟอร์ม",
    "is_multi_unit": True,
    "unit_box_name": "กล่อง",
    "unit_piece_name": "ใบ",
    "pieces_per_box": 2000,
    "on_hand_pieces": 34500,
    "reserved_pieces": 2000,
    "min_alert": 5000,
    "image_piece": "assets/images/image2.jpeg",
    "image_box": "assets/images/image11.jpeg"
  },
  {
    "id": 3,
    "name": "ซองเอกสารสีขาว 7´10 (500 ซองต่อกล่อง)",
    "category": "ซองเอกสาร",
    "is_multi_unit": True,
    "unit_box_name": "กล่อง",
    "unit_piece_name": "ซอง",
    "pieces_per_box": 500,
    "on_hand_pieces": 1000,
    "reserved_pieces": 0,
    "min_alert": 250,
    "image_piece": "assets/images/image3.jpeg",
    "image_box": "assets/images/image12.jpeg"
  },
  {
    "id": 4,
    "name": "กระดาษลายเส้น (ห่อละ 500 แผ่น)",
    "category": "กระดาษและแบบฟอร์ม",
    "is_multi_unit": True,
    "unit_box_name": "ห่อ",
    "unit_piece_name": "แผ่น",
    "pieces_per_box": 500,
    "on_hand_pieces": 23500,
    "reserved_pieces": 0,
    "min_alert": 1000,
    "image_piece": "assets/images/image4.jpeg",
    "image_box": "assets/images/image13.jpeg"
  },
  {
    "id": 5,
    "name": "แฟ้มเสนอ",
    "category": "เครื่องเขียนและแฟ้ม",
    "is_multi_unit": False,
    "unit_box_name": "เล่ม",
    "unit_piece_name": "เล่ม",
    "pieces_per_box": 1,
    "on_hand_pieces": 15,
    "reserved_pieces": 3,
    "min_alert": 5,
    "image_piece": "assets/images/image5.jpeg",
    "image_box": "assets/images/image5.jpeg"
  },
  {
    "id": 6,
    "name": "ซองเอกสารน้ำตาล (มสด) 9´12.3",
    "category": "ซองเอกสาร",
    "is_multi_unit": True,
    "unit_box_name": "กล่อง",
    "unit_piece_name": "ซอง",
    "pieces_per_box": 500,
    "on_hand_pieces": 1500,
    "reserved_pieces": 0,
    "min_alert": 500,
    "image_piece": "assets/images/image14.jpeg",
    "image_box": "assets/images/image15.jpeg"
  }
]

initial_requisitions = [
  {
    "id": "REQ-256910-0042",
    "dept": "โรงเรียนการเรือน - เทคโนโลยีการประกอบอาหารและการบริการ",
    "requester": "อ.สมชาย ใจดี",
    "phone": "081-998-7766",
    "purpose": "ใช้สำหรับการจัดการเรียนการสอนและสอบปฏิบัติการ ภาคเรียน 1/2569",
    "date": "21 ต.ค. 2569 10:15 น.",
    "status": "APPROVED",
    "signature": None,
    "items": [
      { "itemId": 1, "name": "ซองขยายข้างมีครุฑ 279´432", "qtyBoxes": 2, "qtyPieces": 0, "totalPieces": 500, "unitBox": "กล่อง", "unitPiece": "ซอง", "approvedPieces": 500 },
      { "itemId": 2, "name": "กระดาษคำตอบ", "qtyBoxes": 1, "qtyPieces": 0, "totalPieces": 2000, "unitBox": "กล่อง", "unitPiece": "ใบ", "approvedPieces": 2000 },
      { "itemId": 5, "name": "แฟ้มเสนอ", "qtyBoxes": 0, "qtyPieces": 3, "totalPieces": 3, "unitBox": "เล่ม", "unitPiece": "เล่ม", "approvedPieces": 3 }
    ]
  },
  {
    "id": "REQ-256910-0043",
    "dept": "คณะพยาบาลศาสตร์ - พยาบาลศาสตรบัณฑิต",
    "requester": "คุณพรทิพย์ สุขขี",
    "phone": "089-112-3344",
    "purpose": "เตรียมเอกสารปฐมนิเทศนักศึกษาฝึกปฏิบัติงานคลินิก",
    "date": "21 ต.ค. 2569 10:45 น.",
    "status": "PENDING",
    "signature": None,
    "items": [
      { "itemId": 3, "name": "ซองเอกสารสีขาว 7´10", "qtyBoxes": 1, "qtyPieces": 0, "totalPieces": 500, "unitBox": "กล่อง", "unitPiece": "ซอง", "approvedPieces": 500 },
      { "itemId": 4, "name": "กระดาษลายเส้น", "qtyBoxes": 2, "qtyPieces": 0, "totalPieces": 1000, "unitBox": "ห่อ", "unitPiece": "แผ่น", "approvedPieces": 1000 }
    ]
  }
]

print("Ready to generate separated index.html (Requester Portal) and staff.html (Staff Portal).")
