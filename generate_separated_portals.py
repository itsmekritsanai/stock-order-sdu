import json

# Read department options and structure
with open('departments_structured.json', 'r', encoding='utf-8') as f:
    depts_data = json.load(f)

# Build department data array for JS
dept_js_items = []
for cat_name, parent_dict in depts_data.items():
    cat_items = []
    for parent_name, subs in parent_dict.items():
        if subs:
            cat_items.append({
                "label": f"{parent_name} (ภาพรวม)",
                "value": parent_name,
                "sub": False
            })
            for s in subs:
                cat_items.append({
                    "label": f"{s} ({parent_name})",
                    "value": f"{parent_name} - {s}",
                    "sub": True
                })
        else:
            cat_items.append({
                "label": parent_name,
                "value": parent_name,
                "sub": False
            })
    dept_js_items.append({
        "category": cat_name,
        "items": cat_items
    })

dept_json_str = json.dumps(dept_js_items, ensure_ascii=False, indent=2)

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

# Shared Database Initial Data
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
      display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;
    }}
    footer a {{ color: var(--primary); text-decoration: none; }}
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
          {svg_icons['building']} หน่วยงาน / คณะ / โรงเรียนที่สังกัด *
        </label>
        <div class="combobox-control" id="deptComboboxControl">
          <input type="text" id="deptSearchInput" class="form-control combobox-input" 
                 placeholder="พิมพ์ค้นหาคณะ หรือหน่วยงาน... (เช่น การเรือน, คอม, กองคลัง)" 
                 autocomplete="off" 
                 value="โรงเรียนการเรือน - เทคโนโลยีการประกอบอาหารและการบริการ"
                 onfocus="openDeptDropdown()" 
                 oninput="handleDeptSearch(this.value)">
          <input type="hidden" id="deptSelect" value="โรงเรียนการเรือน - เทคโนโลยีการประกอบอาหารและการบริการ">
          <button type="button" class="combobox-toggle-btn" onclick="toggleDeptDropdown(event)" title="เปิด/ปิด รายการ">
            {svg_icons['chevron_down']}
          </button>
        </div>
        <div class="combobox-dropdown" id="deptDropdownList">
          <!-- Populated and filtered by JS -->
        </div>
      </div>
      <div class="form-group">
        <label for="requesterName">
          {svg_icons['user']} ชื่อ-นามสกุล ผู้ขอเบิก *
        </label>
        <input type="text" id="requesterName" class="form-control" placeholder="เช่น อ.สมชาย ใจดี" value="อ.สมชาย ใจดี">
      </div>
      <div class="form-group">
        <label for="requesterPhone">
          {svg_icons['phone']} เบอร์โทรศัพท์ติดต่อ
        </label>
        <input type="tel" id="requesterPhone" class="form-control" placeholder="เช่น 081-234-5678" value="081-998-7766">
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
          <label>ระบุเลขที่เอกสาร (เช่น REQ-256910-0042)</label>
          <div style="display: flex; gap: 0.5rem;">
            <input type="text" id="trackingInput" class="form-control" placeholder="REQ-...">
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

  <!-- Footer with isolated Staff Portal Link -->
  <footer>
    <div>
      © 2569 ระบบเบิกพัสดุและคลังดิจิทัล มหาวิทยาลัยสวนดุสิต | ใช้งานเฉพาะภายในสถาบัน
    </div>
    <div>
      <a href="staff.html" style="display: inline-flex; align-items: center; gap: 4px; color: var(--neutral-600); font-weight: 500;">
        {svg_icons['lock']} สำหรับเจ้าหน้าที่พัสดุ (Staff Portal) →
      </a>
    </div>
  </footer>

  <!-- Scripts -->
  <script>
    const departmentsData = {dept_json_str};

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
      x: `{svg_icons['x']}`
    }};

    // SHARED LOCAL STORAGE DB INITIALIZATION
    const DB_ITEMS_KEY = 'inventory_items';
    const DB_REQS_KEY = 'inventory_requisitions';

    const defaultItems = {json.dumps(initial_items, ensure_ascii=False)};
    const defaultReqs = {json.dumps(initial_requisitions, ensure_ascii=False)};

    function getItemsDB() {{
      const data = localStorage.getItem(DB_ITEMS_KEY);
      if (!data) {{
        localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(defaultItems));
        return defaultItems;
      }}
      return JSON.parse(data);
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
      return JSON.parse(data);
    }}

    function saveReqsDB(reqs) {{
      localStorage.setItem(DB_REQS_KEY, JSON.stringify(reqs));
    }}

    let cart = [];
    let currentCategory = 'ALL';

    // Combobox Logic
    function renderDeptDropdown(filterText = "") {{
      const dropdown = document.getElementById('deptDropdownList');
      const cleanFilter = filterText.trim().toLowerCase();
      let totalMatches = 0;
      let html = "";
      const currentVal = document.getElementById('deptSelect').value;

      departmentsData.forEach(cat => {{
        const matchedItems = cat.items.filter(item => 
          item.label.toLowerCase().includes(cleanFilter) || item.value.toLowerCase().includes(cleanFilter)
        );

        if (matchedItems.length > 0) {{
          totalMatches += matchedItems.length;
          html += `<div class="combobox-group-title">${{cat.category}}</div>`;
          matchedItems.forEach(item => {{
            const isSelected = item.value === currentVal;
            const subClass = item.sub ? 'combobox-item-sub' : '';
            html += `
              <div class="combobox-item ${{subClass}} ${{isSelected ? 'selected' : ''}}" 
                   onclick="selectDepartment('${{item.value}}', '${{item.label}}')">
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
      document.getElementById('deptDropdownList').classList.add('open');
      document.getElementById('deptComboboxControl').classList.add('open');
      renderDeptDropdown(document.getElementById('deptSearchInput').value);
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
      openDeptDropdown();
      renderDeptDropdown(text);
    }}

    function selectDepartment(value, label) {{
      document.getElementById('deptSelect').value = value;
      document.getElementById('deptSearchInput').value = label;
      closeDeptDropdown();
    }}

    document.addEventListener('click', (e) => {{
      const wrapper = document.getElementById('deptComboboxWrapper');
      if (wrapper && !wrapper.contains(e.target)) closeDeptDropdown();
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
              <img src="${{imgSrc}}" class="item-img" alt="${{item.name}}" onerror="this.src='assets/images/image1.jpeg'">
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

          const newReq = {{
            id: newDocNo,
            dept: dept,
            requester: requester,
            phone: phone,
            purpose: purpose,
            date: "21 ต.ค. 2569 " + new Date().toLocaleTimeString('th-TH', {{hour: '2-digit', minute:'2-digit'}}) + " น.",
            status: "PENDING",
            signature: null,
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

          // Save to shared localStorage DB
          const reqs = getReqsDB();
          reqs.unshift(newReq);
          saveReqsDB(reqs);

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

            <div style="margin-top: 0.85rem; display: flex; justify-content: flex-end; gap: 0.5rem;">
              <button class="btn btn-outline" style="font-size: 0.8rem; padding: 0.4rem 0.85rem;" onclick="viewTrackingForDoc('${{req.id}}')">
                ${{vIcons.search}} ติดตามไทม์ไลน์สถานะ
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
      const docNo = document.getElementById('trackingInput').value.trim();
      const area = document.getElementById('trackingResultArea');
      const reqs = getReqsDB();
      const req = reqs.find(r => r.id.toLowerCase() === docNo.toLowerCase());

      if (!req) {{
        Swal.fire({{
          icon: 'error',
          title: 'ไม่พบข้อมูลเอกสาร',
          text: `ไม่พบข้อมูลคำขอเบิกเลขที่ "${{docNo}}" ในระบบ กรุณาตรวจสอบเลขที่เอกสารอีกครั้งครับ`,
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        }});
        area.innerHTML = `<p style="color: var(--danger); text-align: center; padding: 1rem;">ไม่พบข้อมูลเอกสารเลขที่ "${{docNo}}"</p>`;
        return;
      }}

      let statusBadge = '<span style="color: var(--warning); font-weight: bold;">[ รอเจ้าหน้าที่พัสดุอนุมัติ ]</span>';
      if (req.status === 'APPROVED') statusBadge = '<span style="color: var(--primary); font-weight: bold;">[ อนุมัติแล้ว! เชิญมารับของที่ห้องพัสดุ ]</span>';
      if (req.status === 'COMPLETED') statusBadge = '<span style="color: var(--accent); font-weight: bold;">[ รับพัสดุเรียบร้อยแล้ว ]</span>';
      if (req.status === 'REJECTED') statusBadge = '<span style="color: var(--danger); font-weight: bold;">[ ไม่อนุมัติ ]</span>';

      area.innerHTML = `
        <div style="background: var(--neutral-50); border: 1px solid var(--neutral-200); border-radius: 8px; padding: 1rem; margin-top: 1rem;">
          <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <strong>${{req.id}}</strong>
            ${{statusBadge}}
          </div>
          <div style="font-size: 0.85rem; color: var(--neutral-600); margin-bottom: 0.5rem; display: flex; flex-direction: column; gap: 4px;">
            <div style="display: flex; align-items: center; gap: 6px;">${{vIcons.user}} ผู้เบิก: ${{req.requester}} (${{req.dept}})</div>
            <div style="display: flex; align-items: center; gap: 6px;">${{vIcons.clock}} วันที่: ${{req.date}}</div>
          </div>
          <div style="font-size: 0.85rem; border-top: 1px dashed var(--neutral-200); padding-top: 0.5rem;">
            <strong>รายการที่ขอ:</strong>
            <ul style="padding-left: 1.25rem; margin-top: 4px;">
              ${{req.items.map(i => `<li>${{i.name}}: ${{i.totalPieces.toLocaleString()}} ${{i.unitPiece}}</li>`).join('')}}
            </ul>
          </div>
        </div>
      `;
    }}

    // Initial Load
    document.addEventListener('DOMContentLoaded', () => {{
      getItemsDB();
      getReqsDB();
      renderCatalog();
      updateMyReqsBadge();
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
    }});
  </script>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
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

    /* PDF View */
    .pdf-preview-container {{ background: #525659; padding: 2rem; border-radius: 12px; display: flex; flex-direction: column; align-items: center; gap: 1.5rem; }}
    .pdf-page {{ background: white; width: 100%; max-width: 800px; padding: 3rem 3.5rem; box-shadow: 0 10px 25px rgba(0,0,0,0.3); font-family: 'Sarabun', sans-serif; color: #000; line-height: 1.6; }}
    .pdf-header {{ text-align: center; margin-bottom: 2rem; position: relative; display: flex; flex-direction: column; align-items: center; }}
    .pdf-vector-seal {{ margin-bottom: 0.75rem; }}
    .pdf-header h2 {{ font-size: 1.35rem; font-weight: 700; margin-bottom: 0.25rem; }}
    .pdf-header p {{ font-size: 0.9rem; color: #444; }}
    .pdf-meta-table {{ width: 100%; margin-bottom: 1.5rem; font-size: 0.95rem; }}
    .pdf-meta-table td {{ padding: 4px 0; }}
    .pdf-items-table {{ width: 100%; border-collapse: collapse; margin: 1.5rem 0; font-size: 0.95rem; }}
    .pdf-items-table th, .pdf-items-table td {{ border: 1px solid #333; padding: 8px 10px; }}
    .pdf-items-table th {{ background: #f3f4f6; font-weight: 600; text-align: center; }}
    .pdf-signatures {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 3rem; text-align: center; font-size: 0.875rem; }}
    .sig-box {{ display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 140px; }}
    .sig-img-preview {{ max-height: 60px; max-width: 130px; margin-bottom: 4px; }}
    .sig-line {{ width: 80%; border-bottom: 1px dotted #333; margin-bottom: 6px; }}

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

    <div style="margin-top: 1.5rem; text-align: center; border-top: 1px solid var(--neutral-200); padding-top: 1rem;">
      <a href="index.html" style="font-size: 0.85rem; color: var(--primary); text-decoration: none;">
        ← กลับหน้าขอเบิกพัสดุ (สำหรับผู้เบิก)
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
          <button class="view-btn" onclick="switchStaffView('pdf')">
            {svg_icons['file_text']} ใบเบิก PDF (พร้อมลายเซ็น)
          </button>
        </nav>

        <div style="display: flex; align-items: center; gap: 0.75rem;">
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
            <span class="metric-val" id="metricTotalItems">4,045 <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">รายการ</small></span>
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
            <div style="display: flex; gap: 0.5rem;">
              <button class="btn btn-outline" onclick="simulateExcelImport()">
                {svg_icons['upload']} นำเข้าจาก Excel
              </button>
              <button class="btn btn-primary" onclick="openStockInModal()">
                {svg_icons['plus']} บันทึกรับเข้าพัสดุ
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
                </tr>
              </thead>
              <tbody id="inventoryTableBody">
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
                <td><strong>วันที่ขอเบิก:</strong> 21 ตุลาคม 2569</td>
              </tr>
              <tr>
                <td><strong>หน่วยงาน/คณะ:</strong> <span id="pdfDept">โรงเรียนการเรือน</span></td>
                <td><strong>ชื่อผู้ขอเบิก:</strong> <span id="pdfRequester">อ.สมชาย ใจดี</span></td>
              </tr>
              <tr>
                <td colspan="2"><strong>วัตถุประสงค์ในการขอเบิก:</strong> <span id="pdfPurpose">ใช้สำหรับการจัดการเรียนการสอนและสอบปฏิบัติการ ประจำภาคการศึกษา 1/2569</span></td>
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
                <div>( <span id="pdfSignRequester">อ.สมชาย ใจดี</span> )</div>
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
                <div>( <span id="pdfReceiverName">อ.สมชาย ใจดี</span> )</div>
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
          ผู้รับของ: <strong id="sigModalRequesterName" style="color: var(--neutral-900);">อ.สมชาย ใจดี</strong> 
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

  <!-- Scripts -->
  <script>
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

    const defaultItems = {json.dumps(initial_items, ensure_ascii=False)};
    const defaultReqs = {json.dumps(initial_requisitions, ensure_ascii=False)};

    function getItemsDB() {{
      const data = localStorage.getItem(DB_ITEMS_KEY);
      if (!data) {{
        localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(defaultItems));
        return defaultItems;
      }}
      return JSON.parse(data);
    }}
    function saveItemsDB(items) {{ localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(items)); }}

    function getReqsDB() {{
      const data = localStorage.getItem(DB_REQS_KEY);
      if (!data) {{
        localStorage.setItem(DB_REQS_KEY, JSON.stringify(defaultReqs));
        return defaultReqs;
      }}
      return JSON.parse(data);
    }}
    function saveReqsDB(reqs) {{ localStorage.setItem(DB_REQS_KEY, JSON.stringify(reqs)); }}

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
      if (viewName === 'requisitions') btns[0].classList.add('active');
      if (viewName === 'inventory') btns[1].classList.add('active');
      if (viewName === 'pdf') btns[2].classList.add('active');
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
            </div>

            <table class="req-table">
              <thead>
                <tr>
                  <th>รายการพัสดุ</th>
                  <th style="width: 140px;">จำนวนที่ขอ</th>
                  <th style="width: 140px;">จำนวนจ่ายจริง</th>
                  <th style="width: 100px;">สถานะ</th>
                </tr>
              </thead>
              <tbody>
                ${{req.items.map(item => `
                  <tr>
                    <td><strong>${{item.name}}</strong></td>
                    <td>${{item.qtyBoxes > 0 ? `${{item.qtyBoxes}} ${{item.unitBox}} ` : ''}}${{item.qtyPieces > 0 ? `${{item.qtyPieces}} ${{item.unitPiece}}` : ''}}</td>
                    <td style="font-weight: 600; color: var(--accent);">${{item.approvedPieces.toLocaleString()}} ${{item.unitPiece}}</td>
                    <td><span style="color: var(--accent);">พร้อมจ่าย</span></td>
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

      Swal.fire({{
        title: 'ยืนยันการอนุมัติคำขอเบิก?',
        html: `
          <div style="text-align: left; font-size: 0.95rem; margin-top: 0.5rem; color: #475569; line-height: 1.6;">
            <p><strong>เลขที่เอกสาร:</strong> <span style="color: #1e40af; font-weight: 700;">${{docNo}}</span></p>
            <p><strong>ผู้ขอเบิก:</strong> ${{req.requester}} (${{req.dept}})</p>
            <p><strong>จำนวนพัสดุ:</strong> ${{req.items.length}} รายการ</p>
            <div style="margin-top: 0.5rem; padding: 0.5rem 0.75rem; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; color: #166534; font-size: 0.85rem;">
              • ระบบจะทำการกันยอดสต๊อก (Reserved Stock) ทันที
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
          req.items.forEach(i => {{
            const itm = items.find(si => si.id === i.itemId);
            if (itm) itm.reserved_pieces += i.approvedPieces;
          }});
          saveReqsDB(reqs);
          saveItemsDB(items);
          renderStaffRequisitions('PENDING');
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
      Swal.fire({{
        title: 'ปฏิเสธคำขอเบิกพัสดุ',
        text: `ระบุเหตุผลในการไม่อนุมัติคำขอเลขที่ ${{docNo}}:`,
        input: 'textarea',
        inputPlaceholder: 'เช่น พัสดุในคลังไม่เพียงพอ, รายละเอียดไม่ชัดเจน...',
        inputValue: 'พัสดุในคลังไม่เพียงพอสำหรับรอบการเบิกนี้',
        showCancelButton: true,
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ยืนยันปฏิเสธคำขอ',
        cancelButtonText: 'ยกเลิก',
        inputValidator: (val) => {{
          if (!val || !val.trim()) {{
            return 'กรุณาระบุเหตุผลในการปฏิเสธคำขอครับ!';
          }}
        }}
      }}).then((result) => {{
        if (result.isConfirmed && result.value) {{
          const reqs = getReqsDB();
          const req = reqs.find(r => r.id === docNo);
          if (req) {{
            req.status = 'REJECTED';
            req.rejectReason = result.value.trim();
            saveReqsDB(reqs);
            renderStaffRequisitions('PENDING');

            Swal.fire({{
              icon: 'warning',
              title: 'ปฏิเสธคำขอเรียบร้อยแล้ว',
              text: `คำขอ ${{docNo}} ถูกปฏิเสธเรียบร้อยแล้ว`,
              confirmButtonColor: '#1e40af',
              confirmButtonText: 'ตกลง'
            }});
          }}
        }}
      }});
    }}

    // E-Signature
    let canvas, ctx, isDrawing = false;
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
        e.preventDefault(); isDrawing = true;
        const pos = getPos(e); ctx.beginPath(); ctx.moveTo(pos.x, pos.y);
        document.getElementById('sigPlaceholder').style.display = 'none';
      }}
      function draw(e) {{
        if (!isDrawing) return; e.preventDefault();
        const pos = getPos(e); ctx.lineTo(pos.x, pos.y); ctx.stroke();
      }}
      function stopDraw(e) {{ if (isDrawing) {{ isDrawing = false; ctx.closePath(); }} }}

      canvas.addEventListener('mousedown', startDraw);
      canvas.addEventListener('mousemove', draw);
      canvas.addEventListener('mouseup', stopDraw);
      canvas.addEventListener('mouseleave', stopDraw);
      canvas.addEventListener('touchstart', startDraw, {{ passive: false }});
      canvas.addEventListener('touchmove', draw, {{ passive: false }});
      canvas.addEventListener('touchend', stopDraw);
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
      if (ctx && canvas) {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        document.getElementById('sigPlaceholder').style.display = 'block';
      }}
    }}

    function confirmSignatureAndComplete() {{
      if (!currentActiveReqForSig) return;
      const sigDataUrl = canvas.toDataURL('image/png');
      const reqs = getReqsDB();
      const items = getItemsDB();

      const req = reqs.find(r => r.id === currentActiveReqForSig.id);
      if (req) {{
        req.signature = sigDataUrl;
        req.status = 'COMPLETED';

        // Deduct permanently
        req.items.forEach(i => {{
          const itm = items.find(si => si.id === i.itemId);
          if (itm) {{
            itm.on_hand_pieces -= i.approvedPieces;
            itm.reserved_pieces -= i.approvedPieces;
          }}
        }});

        saveReqsDB(reqs);
        saveItemsDB(items);
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
      Swal.fire({{
        title: 'นำเข้าข้อมูลจาก Excel',
        html: `
          <div style="text-align: left; margin: 0.5rem 0; color: #475569; font-size: 0.95rem;">
            <p style="margin-bottom: 0.5rem;">กำลังประมวลผลไฟล์ <b>"ยอดสต๊อก ตค.xlsx"</b>...</p>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem; font-size: 0.85rem; color: #334155; line-height: 1.6;">
              • จำนวนพัสดุในไฟล์: <b>4,045 รายการ</b><br>
              • สถานะการซิงค์: <b>นำเข้าข้อมูลสต๊อกสมบูรณ์</b><br>
              • เชื่อมโยงหมวดหมู่: <b>สำนักงาน, งานบ้าน, ไฟฟ้า, คอมพิวเตอร์</b>
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
      const options = items.map(i => `<option value="${{i.id}}">${{i.name}} (คงเหลือ: ${{i.on_hand_pieces.toLocaleString()}} ${{i.unit_piece_name}})</option>`).join('');

      Swal.fire({{
        title: 'บันทึกรับเข้าพัสดุใหม่',
        html: `
          <div style="text-align: left; display: flex; flex-direction: column; gap: 0.75rem; margin-top: 0.5rem;">
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #475569;">เลือกรายการพัสดุ:</label>
              <select id="swalStockItem" class="swal2-select" style="width: 100%; margin: 4px 0 0 0; font-family: inherit; font-size: 0.9rem; padding: 0.5rem; border-radius: 8px; border: 1px solid #cbd5e1;">
                ${{options}}
              </select>
            </div>
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #475569;">จำนวนที่รับเข้า (ชิ้น):</label>
              <input type="number" id="swalStockQty" min="1" placeholder="ระบุจำนวน" class="swal2-input" style="width: 100%; margin: 4px 0 0 0; height: 42px; font-size: 1rem; border-radius: 8px;">
            </div>
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #475569;">หมายเหตุ / เลขที่ใบส่งของ (ถ้ามี):</label>
              <input type="text" id="swalStockNote" placeholder="เช่น PO-2569-001 หรือ ใบส่งของ..." class="swal2-input" style="width: 100%; margin: 4px 0 0 0; height: 42px; font-size: 0.9rem; border-radius: 8px;">
            </div>
          </div>
        `,
        showCancelButton: true,
        confirmButtonColor: '#1e40af',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ยืนยันรับเข้า',
        cancelButtonText: 'ยกเลิก',
        preConfirm: () => {{
          const itemId = parseInt(document.getElementById('swalStockItem').value);
          const qty = parseInt(document.getElementById('swalStockQty').value) || 0;
          if (qty <= 0) {{
            Swal.showValidationMessage('กรุณาระบุจำนวนที่รับเข้ามากกว่า 0 ครับ');
            return false;
          }}
          return {{ itemId, qty }};
        }}
      }}).then((res) => {{
        if (res.isConfirmed && res.value) {{
          const {{ itemId, qty }} = res.value;
          const items = getItemsDB();
          const itm = items.find(i => i.id === itemId);
          if (itm) {{
            itm.on_hand_pieces += qty;
            saveItemsDB(items);
            renderInventoryTable();

            Swal.fire({{
              icon: 'success',
              title: 'รับเข้าพัสดุสำเร็จ!',
              text: `เพิ่ม ${{itm.name}} จำนวน ${{qty.toLocaleString()}} ${{itm.unit_piece_name}} เข้าสต๊อกเรียบร้อย`,
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
      document.getElementById('pdfDept').innerText = req.dept;
      document.getElementById('pdfRequester').innerText = req.requester;
      document.getElementById('pdfPurpose').innerText = req.purpose;
      document.getElementById('pdfSignRequester').innerText = req.requester;
      document.getElementById('pdfReceiverName').innerText = req.requester;

      const tbody = document.getElementById('pdfItemsTbody');
      tbody.innerHTML = req.items.map((item, idx) => `
        <tr>
          <td style="text-align: center;">${{idx + 1}}</td>
          <td>${{item.name}}</td>
          <td style="text-align: center;">${{item.qtyBoxes > 0 ? `${{item.qtyBoxes}} ${{item.unitBox}} ` : ''}}${{item.qtyPieces > 0 ? `${{item.qtyPieces}} ${{item.unitPiece}}` : ''}}</td>
          <td style="text-align: center; font-weight: bold; color: #166534;">${{item.approvedPieces.toLocaleString()}} ${{item.unitPiece}}</td>
          <td style="text-align: center;">ครบถ้วน</td>
        </tr>
      `).join('');

      const sigArea = document.getElementById('pdfReceiverSigArea');
      if (req.signature) {{
        sigArea.innerHTML = `<img src="${{req.signature}}" class="sig-img-preview" alt="ลายเซ็นดิจิทัล">`;
        document.getElementById('pdfReceiveTime').innerText = `เซ็นรับเมื่อ: 21 ต.ค. 2569 (E-Signature)`;
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
          </tr>
        `;
      }}).join('');

      document.getElementById('metricReserved').innerHTML = `${{totalReserved.toLocaleString()}} <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">ชิ้น</small>`;
      document.getElementById('metricLowStock').innerHTML = `${{lowStockCount}} <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">รายการ</small>`;
    }}

    function loadStaffDashboard() {{
      renderStaffRequisitions(currentStaffStatus);
      renderInventoryTable();
    }}

    document.addEventListener('DOMContentLoaded', () => {{
      // Auto authenticate for demo or check session
      if (!sessionStorage.getItem('staff_auth')) {{
        sessionStorage.setItem('staff_auth', 'true'); // Default logged in for immediate preview
      }}
      checkStaffAuth();
    }});

    // Real-time synchronization across tabs/windows
    window.addEventListener('storage', (e) => {{
      if (e.key === DB_REQS_KEY || e.key === DB_ITEMS_KEY) {{
        loadStaffDashboard();
      }}
    }});
  </script>
</body>
</html>
'''

with open('staff.html', 'w', encoding='utf-8') as f:
    f.write(staff_html)

print("Created staff.html (Inventory Staff & Admin Portal)")
