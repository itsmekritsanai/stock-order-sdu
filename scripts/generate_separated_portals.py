import json
import os

SYSTEM_VERSION = "3.6.0"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPT_DOCX_PATH = os.path.join(PROJECT_ROOT, 'data', 'รายนามบุคลากร สวท.docx')

# Read configuration and credentials from .env if available
MYSQL_API_URL = "/api"
DEFAULT_USER_PASSWORD = "password123"
STAFF_PASSWORD = "sdu1234"
STAFF_USERNAME = "admin_staff"
AUTH_BYPASS = False

env_path = os.path.join(PROJECT_ROOT, '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as ef:
        for line in ef:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k == 'API_BASE_URL':
                MYSQL_API_URL = v
            elif k == 'DEFAULT_USER_PASSWORD':
                DEFAULT_USER_PASSWORD = v
            elif k == 'STAFF_PASSWORD':
                STAFF_PASSWORD = v
            elif k == 'STAFF_USERNAME':
                STAFF_USERNAME = v
            elif k == 'AUTH_BYPASS':
                AUTH_BYPASS = v.lower() in ('true', '1', 'yes', 'on')

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
            idx = len(users) + 1
            default_unames = ['wasana.c', 'jeerawan.b', 'patcharaporn.k', 'sineenart.l']
            uname = default_unames[idx - 1] if idx <= len(default_unames) else f"user0{idx}"
            users.append({
                "id": idx,
                "name": full_name,
                "username": uname,
                "password": DEFAULT_USER_PASSWORD,
                "position": pos,
                "dept": unit,
                "phone": ""
            })

    # Demo User สำหรับผู้ขอเบิกเข้าใช้งาน
    users.append({
        "id": len(users) + 1,
        "name": "ผู้ขอเบิกทดสอบ",
        "username": "user",
        "password": DEFAULT_USER_PASSWORD,
        "position": "เจ้าหน้าที่บริการการศึกษา",
        "dept": "สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน",
        "phone": "089-123-4567"
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

SEARCHABLE_SELECT_CSS = r'''
    /* Universal Searchable Dropdown Widget */
    .sdu-ss-wrapper {
      position: relative;
      display: inline-block;
      width: 100%;
      font-family: inherit;
      text-align: left;
    }
    .sdu-ss-wrapper.sdu-ss-auto {
      width: auto;
      min-width: 160px;
    }
    .sdu-ss-trigger {
      width: 100%;
      min-height: 38px;
      padding: 0.45rem 0.7rem;
      background: white;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      color: #1e293b;
      font-family: inherit;
      font-size: 0.875rem;
      text-align: left;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      cursor: pointer;
      transition: border-color 0.15s, box-shadow 0.15s;
      box-sizing: border-box;
    }
    .sdu-ss-trigger:hover { border-color: #94a3b8; }
    .sdu-ss-trigger.open, .sdu-ss-trigger:focus {
      outline: none;
      border-color: #1e40af;
      box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.12);
    }
    .sdu-ss-trigger-label {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      flex: 1;
      min-width: 0;
    }
    .sdu-ss-chevron {
      width: 15px;
      height: 15px;
      color: #64748b;
      flex-shrink: 0;
      transition: transform 0.15s;
    }
    .sdu-ss-trigger.open .sdu-ss-chevron {
      transform: rotate(180deg);
      color: #1e40af;
    }
    .sdu-ss-panel {
      position: fixed;
      z-index: 99999;
      background: white;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      box-shadow: 0 12px 28px -4px rgba(15, 23, 42, 0.22), 0 4px 10px rgba(15, 23, 42, 0.08);
      display: none;
      flex-direction: column;
      overflow: hidden;
      font-family: 'Prompt', 'Sarabun', sans-serif;
      box-sizing: border-box;
    }
    .sdu-ss-panel.open { display: flex; }
    .sdu-ss-search-wrap {
      padding: 8px;
      background: #f8fafc;
      border-bottom: 1px solid #e2e8f0;
    }
    .sdu-ss-search-input {
      width: 100%;
      padding: 6px 10px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      font-family: inherit;
      font-size: 0.85rem;
      color: #0f172a;
      background: white;
      outline: none;
      box-sizing: border-box;
    }
    .sdu-ss-search-input:focus {
      border-color: #1e40af;
      box-shadow: 0 0 0 2px rgba(30, 64, 175, 0.12);
    }
    .sdu-ss-list {
      max-height: 230px;
      overflow-y: auto;
      padding: 4px;
    }
    .sdu-ss-item {
      padding: 7px 10px;
      border-radius: 6px;
      font-size: 0.85rem;
      color: #1e293b;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
      line-height: 1.35;
      text-align: left;
    }
    .sdu-ss-item:hover, .sdu-ss-item.highlighted {
      background: #eff6ff;
      color: #1e40af;
    }
    .sdu-ss-item.selected {
      background: #dbeafe;
      color: #1e40af;
      font-weight: 600;
    }
    .sdu-ss-empty {
      padding: 14px 10px;
      text-align: center;
      font-size: 0.825rem;
      color: #94a3b8;
    }
'''

SEARCHABLE_SELECT_JS = r'''
    // Universal Searchable Dropdown Enhancer (Zero-Build Vanilla JS)
    let _activeSearchablePanel = null;
    let _activeSearchableTrigger = null;

    function closeActiveSearchableSelect() {
      if (_activeSearchablePanel) {
        _activeSearchablePanel.classList.remove('open');
        if (_activeSearchablePanel.parentNode) {
          _activeSearchablePanel.parentNode.removeChild(_activeSearchablePanel);
        }
        _activeSearchablePanel = null;
      }
      if (_activeSearchableTrigger) {
        _activeSearchableTrigger.classList.remove('open');
        _activeSearchableTrigger = null;
      }
    }

    document.addEventListener('click', (e) => {
      if (_activeSearchableTrigger && !document.body.contains(_activeSearchableTrigger)) {
        closeActiveSearchableSelect();
        return;
      }
      if (_activeSearchablePanel && !_activeSearchablePanel.contains(e.target) && (!_activeSearchableTrigger || !_activeSearchableTrigger.contains(e.target))) {
        closeActiveSearchableSelect();
      }
    });

    document.addEventListener('scroll', (e) => {
      if (_activeSearchablePanel && !_activeSearchablePanel.contains(e.target)) {
        closeActiveSearchableSelect();
      }
    }, true);

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && _activeSearchablePanel) {
        closeActiveSearchableSelect();
      }
    });

    window.addEventListener('resize', closeActiveSearchableSelect);

    function enhanceSearchableSelect(selectEl) {
      if (!selectEl || selectEl.tagName !== 'SELECT') return;
      if (selectEl.getAttribute('data-searchable-enhanced') === 'true') {
        if (typeof selectEl._syncSearchableLabel === 'function') selectEl._syncSearchableLabel();
        return;
      }
      if (selectEl.getAttribute('data-no-search') === 'true' || selectEl.multiple) return;
      // Skip hidden placeholder selects such as SweetAlert2's empty built-in #swal2-select
      if (selectEl.style.display === 'none') return;
      if (selectEl.id === 'swal2-select' && (!selectEl.options || selectEl.options.length === 0)) return;
      selectEl.setAttribute('data-searchable-enhanced', 'true');

      const wrapper = document.createElement('div');
      const isAutoWidth = selectEl.style.width === 'auto' || selectEl.id === 'staffRoleSelect' || selectEl.id === 'staffReqMonthFilter' || selectEl.id === 'analyticsMonthSelect' || selectEl.id === 'myReqsMonthSelect';
      wrapper.className = 'sdu-ss-wrapper' + (isAutoWidth ? ' sdu-ss-auto' : '');
      if (selectEl.style.minWidth) wrapper.style.minWidth = selectEl.style.minWidth;

      const trigger = document.createElement('button');
      trigger.type = 'button';
      trigger.className = 'sdu-ss-trigger';
      if (selectEl.id) trigger.setAttribute('data-for-select', selectEl.id);
      if (selectEl.style.height) trigger.style.minHeight = selectEl.style.height;
      if (selectEl.style.fontSize) trigger.style.fontSize = selectEl.style.fontSize;
      if (selectEl.style.padding) trigger.style.padding = selectEl.style.padding;

      const labelSpan = document.createElement('span');
      labelSpan.className = 'sdu-ss-trigger-label';
      const chevronSvg = `<svg class="sdu-ss-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>`;
      trigger.appendChild(labelSpan);
      trigger.insertAdjacentHTML('beforeend', chevronSvg);

      const protoDesc = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value');
      const syncLabel = () => {
        const opts = Array.from(selectEl.options || []);
        const currentVal = protoDesc && protoDesc.get ? protoDesc.get.call(selectEl) : selectEl.value;
        const selectedOpt = opts.find(o => o.value === currentVal) || opts[selectEl.selectedIndex] || opts[0];
        labelSpan.textContent = selectedOpt ? selectedOpt.textContent : 'เลือกรายการ...';
        trigger.title = labelSpan.textContent;
      };
      selectEl._syncSearchableLabel = syncLabel;

      if (protoDesc && protoDesc.get && protoDesc.set) {
        Object.defineProperty(selectEl, 'value', {
          configurable: true,
          get() { return protoDesc.get.call(this); },
          set(v) {
            protoDesc.set.call(this, v);
            syncLabel();
          }
        });
      }

      const observer = new MutationObserver(() => syncLabel());
      observer.observe(selectEl, { childList: true, subtree: true, attributes: true });

      selectEl.parentNode.insertBefore(wrapper, selectEl);
      wrapper.appendChild(trigger);
      wrapper.appendChild(selectEl);
      selectEl.style.display = 'none';
      syncLabel();

      trigger.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (_activeSearchableTrigger === trigger) {
          closeActiveSearchableSelect();
          return;
        }
        closeActiveSearchableSelect();

        const panel = document.createElement('div');
        panel.className = 'sdu-ss-panel open';
        panel.innerHTML = `
          <div class="sdu-ss-search-wrap">
            <input type="text" class="sdu-ss-search-input" placeholder="พิมพ์คำค้นหาในรายการ..." autocomplete="off">
          </div>
          <div class="sdu-ss-list"></div>
        `;

        const mountHost = selectEl.closest('.swal2-popup') || document.body;
        mountHost.appendChild(panel);
        _activeSearchablePanel = panel;
        _activeSearchableTrigger = trigger;
        trigger.classList.add('open');

        const rect = trigger.getBoundingClientRect();
        const panelWidth = Math.max(rect.width, 230);
        const spaceBelow = window.innerHeight - rect.bottom - 10;
        const spaceAbove = rect.top - 10;
        const openAbove = spaceBelow < 220 && spaceAbove > spaceBelow;
        panel.style.width = `${Math.min(panelWidth, window.innerWidth - 20)}px`;
        panel.style.left = `${Math.max(10, Math.min(rect.left, window.innerWidth - Math.min(panelWidth, window.innerWidth - 20) - 10))}px`;
        if (openAbove) {
          panel.style.bottom = `${window.innerHeight - rect.top + 4}px`;
          panel.style.top = 'auto';
        } else {
          panel.style.top = `${rect.bottom + 4}px`;
          panel.style.bottom = 'auto';
        }

        const searchInput = panel.querySelector('.sdu-ss-search-input');
        const listEl = panel.querySelector('.sdu-ss-list');
        let highlightedIdx = -1;

        const renderOptions = (filterText = '') => {
          const clean = filterText.trim().toLowerCase();
          const currentVal = selectEl.value;
          const opts = Array.from(selectEl.options || []).filter(o => !o.disabled);
          const matched = opts.filter(o =>
            !clean ||
            (o.textContent && o.textContent.toLowerCase().includes(clean)) ||
            (o.value && o.value.toLowerCase().includes(clean))
          );
          if (matched.length === 0) {
            listEl.innerHTML = `<div class="sdu-ss-empty">ไม่พบตัวเลือกที่ตรงกับ "${filterText.replace(/</g, '&lt;')}"</div>`;
            highlightedIdx = -1;
            return;
          }
          listEl.innerHTML = '';
          matched.forEach((opt, idx) => {
            const item = document.createElement('div');
            const isSel = opt.value === currentVal;
            item.className = 'sdu-ss-item' + (isSel ? ' selected' : '') + (idx === highlightedIdx ? ' highlighted' : '');
            const textSpan = document.createElement('span');
            textSpan.textContent = opt.textContent;
            item.appendChild(textSpan);
            if (isSel) {
              item.insertAdjacentHTML('beforeend', `<svg style="width:14px;height:14px;flex-shrink:0;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`);
            }
            item.addEventListener('click', (ev) => {
              ev.stopPropagation();
              opt.selected = true;
              selectEl.value = opt.value;
              syncLabel();
              closeActiveSearchableSelect();
              selectEl.dispatchEvent(new Event('change', { bubbles: true }));
            });
            listEl.appendChild(item);
          });
        };

        renderOptions('');
        setTimeout(() => searchInput.focus(), 10);

        searchInput.addEventListener('click', (ev) => ev.stopPropagation());
        searchInput.addEventListener('input', () => {
          highlightedIdx = 0;
          renderOptions(searchInput.value);
        });
        searchInput.addEventListener('keydown', (ev) => {
          const items = listEl.querySelectorAll('.sdu-ss-item');
          if (ev.key === 'ArrowDown') {
            ev.preventDefault();
            if (items.length > 0) {
              highlightedIdx = (highlightedIdx + 1) % items.length;
              items.forEach((el, i) => el.classList.toggle('highlighted', i === highlightedIdx));
              if (items[highlightedIdx]) items[highlightedIdx].scrollIntoView({ block: 'nearest' });
            }
          } else if (ev.key === 'ArrowUp') {
            ev.preventDefault();
            if (items.length > 0) {
              highlightedIdx = highlightedIdx <= 0 ? items.length - 1 : highlightedIdx - 1;
              items.forEach((el, i) => el.classList.toggle('highlighted', i === highlightedIdx));
              if (items[highlightedIdx]) items[highlightedIdx].scrollIntoView({ block: 'nearest' });
            }
          } else if (ev.key === 'Enter') {
            ev.preventDefault();
            const targetItem = (highlightedIdx >= 0 && items[highlightedIdx]) ? items[highlightedIdx] : items[0];
            if (targetItem) targetItem.click();
          } else if (ev.key === 'Escape') {
            ev.preventDefault();
            closeActiveSearchableSelect();
          }
        });
      });
    }

    function enhanceAllSearchableSelects(root = document) {
      if (!root || !root.querySelectorAll) return;
      root.querySelectorAll('select').forEach(sel => enhanceSearchableSelect(sel));
    }

    document.addEventListener('DOMContentLoaded', () => {
      enhanceAllSearchableSelects(document);
      const bodyObserver = new MutationObserver((mutations) => {
        for (const m of mutations) {
          m.addedNodes.forEach(node => {
            if (node && node.nodeType === 1) {
              if (node.tagName === 'SELECT') enhanceSearchableSelect(node);
              else if (node.querySelectorAll) enhanceAllSearchableSelects(node);
            }
          });
        }
      });
      if (document.body) {
        bodyObserver.observe(document.body, { childList: true, subtree: true });
      }
    });
'''

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

# Official Vector Emblem for PDF (SVG)


# --------------------------------------------------------------------
# 1. REQUESTER TEMPLATE (index.html)
# --------------------------------------------------------------------
requester_template = r'''<!DOCTYPE html>
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
  <!-- University Brand Logo Tab Favicon -->
  <link rel="icon" type="image/png" href="assets/logo_sdu.png">
  <link rel="shortcut icon" type="image/x-icon" href="favicon.ico">
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

    function escapeHtml(str) {
      if (str === null || str === undefined) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }

    function getThaiDatetime(dateObj = new Date()) {
      const thaiMonths = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];
      const day = dateObj.getDate();
      const month = thaiMonths[dateObj.getMonth()];
      const thaiYear = dateObj.getFullYear() + 543;
      const hours = String(dateObj.getHours()).padStart(2, '0');
      const minutes = String(dateObj.getMinutes()).padStart(2, '0');
      return `${day} ${month} ${thaiYear} ${hours}:${minutes} น.`;
    }

    function formatThaiDatetime(dateObj = new Date()) {
      return getThaiDatetime(dateObj);
    }

    if (typeof Swal === 'undefined') {
      document.write('<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"><\/script>');
    }
  </script>
  
  <style>

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
    .pdf-page { background: white; width: 100%; max-width: 800px; min-height: 1050px; display: flex; flex-direction: column; box-sizing: border-box; padding: 2.8rem 3.2rem; box-shadow: 0 10px 25px rgba(0,0,0,0.3); font-family: 'Sarabun', sans-serif; color: #000; line-height: 1.6; }
    .pdf-header { text-align: center; margin-bottom: 1.75rem; position: relative; display: flex; flex-direction: column; align-items: center; }
    .pdf-header h2 { font-size: 1.35rem; font-weight: 700; margin-bottom: 0.25rem; }
    .pdf-header p { font-size: 0.9rem; color: #444; }
    .pdf-meta-table { width: 100%; margin-bottom: 1.25rem; font-size: 0.95rem; }
    .pdf-meta-table td { padding: 4px 0; }
    .pdf-items-table { width: 100%; border-collapse: collapse; margin: 1.25rem 0; font-size: 0.95rem; }
    .pdf-items-table th, .pdf-items-table td { border: 1px solid #333; padding: 8px 10px; }
    .pdf-items-table th { background: #f3f4f6; font-weight: 600; text-align: center; }
    .pdf-footer-section { margin-top: auto; width: 100%; page-break-inside: avoid; break-inside: avoid; }
    .pdf-ack-note { font-size: 0.85rem; margin-bottom: 0.75rem; }
    .pdf-signatures { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; margin-top: auto; text-align: center; font-size: 0.825rem; page-break-inside: avoid; break-inside: avoid; }
    .pdf-footer-section .pdf-signatures { margin-top: 0.75rem; }
    .sig-box { display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 140px; }
    .sig-img-preview { max-height: 60px; max-width: 130px; margin-bottom: 4px; }
    .sig-line { width: 80%; border-bottom: 1px dotted #333; margin-bottom: 6px; }

    /* Clean Print Isolation - Only the A4 document prints */
    @media print {
      @page {
        size: A4 portrait;
        margin: 1.2cm 1.5cm;
      }
      html, body {
        width: 100% !important;
        height: auto !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: visible !important;
        background: white !important;
      }
      header, footer, nav, .nav-container, .cart-drawer, .btn, .close-btn,
      .modal-header, .modal-footer, .pdf-preview-actions, #requesterLoginScreen,
      .category-tabs, .search-box, .stat-grid, .order-history-box {
        display: none !important;
      }
      .modal-overlay, #requisitionPdfModal {
        position: static !important;
        display: block !important;
        inset: auto !important;
        background: none !important;
        backdrop-filter: none !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: visible !important;
        opacity: 1 !important;
        visibility: visible !important;
      }
      .modal-card {
        position: static !important;
        max-width: 100% !important;
        width: 100% !important;
        box-shadow: none !important;
        border: none !important;
        border-radius: 0 !important;
        transform: none !important;
        overflow: visible !important;
        background: white !important;
      }
      .modal-body {
        padding: 0 !important;
        background: white !important;
        overflow: visible !important;
        display: block !important;
      }
      #printablePdf {
        position: static !important;
        width: 100% !important;
        max-width: 100% !important;
        min-height: calc(297mm - 2.5cm) !important;
        display: flex !important;
        flex-direction: column !important;
        box-sizing: border-box !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
        background: white !important;
        visibility: visible !important;
      }
      #printablePdf * {
        visibility: visible !important;
      }
      .pdf-footer-section {
        margin-top: auto !important;
        width: 100% !important;
        page-break-inside: avoid !important;
        break-inside: avoid !important;
      }
      .pdf-signatures {
        margin-top: auto !important;
        page-break-inside: avoid !important;
        break-inside: avoid !important;
      }
      .pdf-footer-section .pdf-signatures {
        margin-top: 0.5rem !important;
      }
    }


__SEARCHABLE_SELECT_CSS__

    /* Requester Login Screen */
    .login-wrapper {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
      background: linear-gradient(135deg, #eff6ff 0%, #f1f5f9 50%, #e2e8f0 100%);
    }
    .login-card {
      background: white;
      width: 100%;
      max-width: 440px;
      border-radius: 16px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
      border: 1px solid var(--neutral-200);
      overflow: hidden;
      animation: fadeIn 0.3s ease-out;
    }
    .login-header {
      background: white;
      padding: 2.25rem 2rem 1.5rem 2rem;
      text-align: center;
      border-bottom: 1px solid var(--neutral-100);
    }
    .login-body {
      padding: 1.75rem 2rem;
    }
    .login-input-group {
      margin-bottom: 1.25rem;
    }
    .login-input-group label {
      display: block;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--neutral-700);
      margin-bottom: 0.4rem;
    }
    .login-input-wrapper {
      position: relative;
      display: flex;
      align-items: center;
    }
    .login-input-wrapper .input-icon {
      position: absolute;
      left: 1rem;
      color: var(--neutral-400);
      display: flex;
      pointer-events: none;
    }
    .login-input {
      width: 100%;
      padding: 0.75rem 1rem 0.75rem 2.75rem;
      border: 1px solid var(--neutral-300);
      border-radius: 10px;
      font-family: inherit;
      font-size: 0.95rem;
      transition: all 0.2s;
    }
    .login-input:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 4px rgba(30, 64, 175, 0.12);
    }
    .btn-login {
      width: 100%;
      background: var(--primary);
      color: white;
      border: none;
      border-radius: 10px;
      padding: 0.8rem;
      font-family: inherit;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      box-shadow: 0 4px 12px rgba(30, 64, 175, 0.25);
      transition: all 0.2s;
    }
    .btn-login:hover {
      background: var(--primary-hover);
      box-shadow: 0 6px 16px rgba(30, 64, 175, 0.35);
    }
    .btn-login:active {
      transform: scale(0.99);
    }
    .login-notice-box {
      margin-top: 1.25rem;
      background: var(--neutral-50);
      border: 1px solid var(--neutral-200);
      border-radius: 8px;
      padding: 0.85rem;
      font-size: 0.8rem;
      color: var(--neutral-600);
      line-height: 1.5;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Requester Specific Styles */
    .requester-bar {
      background: white; border: 1px solid var(--neutral-200); border-radius: var(--radius);
      padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm);
      display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 1.25rem; align-items: flex-end;
    }
    @media (max-width: 900px) { .requester-bar { grid-template-columns: 1fr; } }

    .search-filter-bar { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
    .search-box-wrapper { flex: 1; min-width: 300px; position: relative; }
    .search-input {
      width: 100%; padding: 0.75rem 1rem 0.75rem 2.75rem; border: 1px solid var(--neutral-300);
      border-radius: 10px; font-family: inherit; font-size: 0.95rem; background: white;
      box-shadow: var(--shadow-sm); outline: none; transition: all 0.2s;
    }
    .search-input:focus { border-color: var(--primary); box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12); }
    .search-icon { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: var(--neutral-400); pointer-events: none; display: flex; }

    .category-pills { display: flex; gap: 0.5rem; overflow-x: auto; align-items: center; padding-bottom: 4px; }
    .pill-btn {
      padding: 0.5rem 1rem; background: white; border: 1px solid var(--neutral-200); border-radius: 999px;
      font-family: inherit; font-size: 0.825rem; font-weight: 500; color: var(--neutral-600);
      cursor: pointer; white-space: nowrap; transition: all 0.2s;
    }
    .pill-btn:hover { border-color: var(--neutral-300); background: var(--neutral-100); }
    .pill-btn.active { background: var(--primary); color: white; border-color: var(--primary); box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25); }

    .catalog-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 1.25rem; }
    .item-card {
      background: white; border: 1px solid var(--neutral-200); border-radius: var(--radius);
      overflow: hidden; box-shadow: var(--shadow-sm); display: flex; flex-direction: column;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .item-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); border-color: var(--primary-border); }
    .item-image-wrapper { height: 175px; background: var(--neutral-100); position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center; }
    .item-img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s ease; }
    .item-card:hover .item-img { transform: scale(1.03); }
    .image-toggle-pills {
      position: absolute; bottom: 8px; left: 8px; display: flex; gap: 4px;
      background: rgba(15, 23, 42, 0.75); padding: 3px; border-radius: 6px; backdrop-filter: blur(4px);
    }
    .img-pill-btn { background: transparent; border: none; color: white; font-family: inherit; font-size: 0.675rem; padding: 2px 6px; border-radius: 4px; cursor: pointer; opacity: 0.8; }
    .img-pill-btn.active { background: var(--primary); opacity: 1; font-weight: 600; }

    .card-body { padding: 1.15rem; display: flex; flex-direction: column; flex: 1; }
    .item-title { font-size: 0.95rem; font-weight: 600; color: var(--neutral-900); line-height: 1.4; margin-bottom: 0.5rem; min-height: 2.8rem; }
    .ratio-badge { display: inline-flex; align-items: center; gap: 5px; font-size: 0.75rem; color: var(--neutral-600); background: var(--neutral-100); padding: 4px 8px; border-radius: 6px; margin-bottom: 0.75rem; width: fit-content; }
    .stock-info { background: var(--primary-light); border: 1px solid var(--primary-border); border-radius: 8px; padding: 0.5rem 0.75rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s ease; }
    .stock-label { font-size: 0.75rem; color: var(--primary); font-weight: 500; }
    .stock-value { font-size: 0.875rem; font-weight: 700; color: var(--primary); }
    .stock-info.low {
      background: var(--danger-light);
      border-color: #fca5a5;
    }
    .stock-info.low .stock-label {
      color: #991b1b;
      font-weight: 600;
    }
    .stock-info.low .stock-value {
      color: var(--danger);
      font-weight: 700;
    }
    .card-actions { margin-top: auto; display: flex; flex-direction: column; gap: 0.6rem; }
    .qty-inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }
    .qty-col label { font-size: 0.7rem; color: var(--neutral-600); display: block; margin-bottom: 2px; }
    .qty-input { width: 100%; padding: 0.45rem; border: 1px solid var(--neutral-300); border-radius: 6px; font-family: inherit; font-size: 0.85rem; text-align: center; }
    .btn-add-cart {
      width: 100%; background: var(--primary); color: white; border: none; border-radius: 8px;
      padding: 0.6rem; font-family: inherit; font-size: 0.875rem; font-weight: 600; cursor: pointer;
      display: flex; align-items: center; justify-content: center; gap: 0.5rem; transition: background 0.2s, transform 0.1s;
    }
    .btn-add-cart:hover { background: var(--primary-hover); }
    .btn-add-cart:active { transform: scale(0.98); }

    /* Cart Button Trigger */
    .cart-trigger {
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
    }
    .cart-trigger:hover {
      background: var(--primary-hover);
      box-shadow: 0 4px 10px rgba(30, 64, 175, 0.35);
      transform: translateY(-1px);
    }
    .cart-trigger:active {
      transform: translateY(0);
    }
    .cart-badge {
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
    }

    /* Cart Drawer */
    .cart-drawer-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.5); backdrop-filter: blur(2px); z-index: 50; opacity: 0; pointer-events: none; transition: opacity 0.3s; }
    .cart-drawer-overlay.open { opacity: 1; pointer-events: auto; }
    .cart-drawer {
      position: fixed; top: 0; right: 0; bottom: 0; width: 440px; max-width: 90vw; background: white;
      box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15); z-index: 51; transform: translateX(100%); transition: transform 0.3s ease-out;
      display: flex; flex-direction: column;
    }
    .cart-drawer-overlay.open .cart-drawer { transform: translateX(0); }
    .cart-header { padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--neutral-200); display: flex; justify-content: space-between; align-items: center; }
    .cart-header h3 { font-size: 1.1rem; font-weight: 700; color: var(--neutral-900); display: flex; align-items: center; gap: 0.5rem; }
    .cart-items-list { flex: 1; overflow-y: auto; padding: 1rem 1.5rem; display: flex; flex-direction: column; gap: 0.75rem; }
    .cart-item-card { background: var(--neutral-50); border: 1px solid var(--neutral-200); border-radius: 8px; padding: 0.85rem; display: flex; justify-content: space-between; align-items: center; gap: 0.75rem; }
    .cart-item-details h4 { font-size: 0.875rem; font-weight: 600; color: var(--neutral-900); margin-bottom: 0.25rem; }
    .cart-item-qty { font-size: 0.8rem; color: var(--neutral-600); }
    .cart-item-remove { background: none; border: none; color: var(--danger); cursor: pointer; padding: 4px; opacity: 0.7; display: flex; align-items: center; }
    .cart-item-remove:hover { opacity: 1; }
    .cart-footer { padding: 1.25rem 1.5rem; border-top: 1px solid var(--neutral-200); background: white; display: flex; flex-direction: column; gap: 1rem; }
    .btn-submit-requisition {
      width: 100%; background: var(--accent); color: white; border: none; border-radius: 8px;
      padding: 0.85rem; font-family: inherit; font-size: 1rem; font-weight: 600; cursor: pointer;
      display: flex; align-items: center; justify-content: center; gap: 0.5rem; box-shadow: 0 4px 10px rgba(5, 150, 105, 0.25);
    }
    .btn-submit-requisition:hover { background: var(--accent-hover); }

    /* My Requisitions Modal & Card Styles */
    .req-modal-card {
      max-width: 840px !important;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
    }
    .req-filter-tabs {
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
      margin-bottom: 1rem;
    }
    .req-tab-btn {
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
    }
    .req-tab-btn:hover {
      background: var(--neutral-100);
      border-color: var(--neutral-400);
    }
    .req-tab-btn.active {
      background: var(--primary);
      color: white;
      border-color: var(--primary);
      box-shadow: 0 2px 6px rgba(30, 64, 175, 0.25);
    }
    .req-card-item {
      background: white;
      border: 1px solid var(--neutral-200);
      border-radius: 12px;
      padding: 1.25rem;
      margin-bottom: 1rem;
      box-shadow: var(--shadow-sm);
      transition: all 0.2s;
      border-left: 4px solid var(--primary);
    }
    .req-card-item:hover {
      border-color: var(--primary-border);
      box-shadow: var(--shadow-md);
      transform: translateY(-1px);
    }
    .req-card-item.status-border-pending { border-left-color: #d97706; }
    .req-card-item.status-border-verified { border-left-color: #0284c7; }
    .req-card-item.status-border-approved { border-left-color: #2563eb; }
    .req-card-item.status-border-completed { border-left-color: #059669; }
    .req-card-item.status-border-rejected { border-left-color: #dc2626; }

    .req-status-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.775rem;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 999px;
    }
    .pill-pending { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .pill-verified { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
    .pill-approved { background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }
    .pill-completed { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
    .pill-rejected { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }

    .req-item-mini-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 0.75rem;
      font-size: 0.85rem;
      background: var(--neutral-50);
      border-radius: 8px;
      overflow: hidden;
    }
    .req-item-mini-table th {
      background: #f1f5f9;
      color: var(--neutral-700);
      font-weight: 600;
      text-align: left;
      padding: 6px 12px;
      font-size: 0.8rem;
    }
    .req-item-mini-table td {
      padding: 7px 12px;
      border-top: 1px solid var(--neutral-200);
      color: var(--neutral-800);
    }

    footer {
      margin-top: auto; padding: 1.5rem; background: white; border-top: 1px solid var(--neutral-200);
      text-align: center; font-size: 0.85rem; color: var(--neutral-600);
      display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 1rem;
    }
  </style>
</head>
<body>

  <!-- 1. UNIFIED ROLE LOGIN SCREEN (SHOWN WHEN NOT LOGGED IN) -->
  <div id="requesterLoginScreen" class="login-wrapper">
    <div class="login-card" style="max-width: 480px;">
      <div class="login-header" style="padding: 1.75rem 1.75rem 1.25rem 1.75rem;">
        <img src="assets/logo_sdu.png" alt="มหาวิทยาลัยสวนดุสิต" style="height: 60px; margin-bottom: 0.6rem; object-fit: contain;">
        <h2 id="loginRoleTitle" style="font-size: 1.2rem; font-weight: 700; color: var(--neutral-900); margin-bottom: 0.25rem;">เข้าสู่ระบบผู้ขอเบิกพัสดุ</h2>
        <p style="font-size: 0.825rem; color: var(--neutral-500);">มหาวิทยาลัยสวนดุสิต | สำนักส่งเสริมวิชาการและงานทะเบียน</p>
        <div id="loginRoleBadge" style="margin-top: 0.65rem; display: inline-flex; align-items: center; gap: 6px; background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; padding: 4px 12px; border-radius: 999px; font-size: 0.75rem; font-weight: 600;">
          <svg class="svg-icon" style="width: 14px; height: 14px;" viewBox="0 0 24 24"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          <span>สำหรับบุคลากรและอาจารย์ สวท. (เลือกเบิกพัสดุและติดตามสถานะ)</span>
        </div>
      </div>
      <div class="login-body" style="padding: 1.25rem 1.75rem 1.75rem 1.75rem;">
        <div style="margin-bottom: 1.1rem;">
          <label style="display: block; font-size: 0.8rem; font-weight: 600; color: var(--neutral-600); margin-bottom: 0.45rem;">เลือกบทบาทผู้ใช้งาน:</label>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;" id="portalRoleTabs">
            <button type="button" class="role-tab-btn active" data-role="REQUESTER" onclick="selectPortalLoginRole('REQUESTER')" style="padding: 0.55rem 0.65rem; border-radius: 8px; border: 2px solid #1e40af; background: #eff6ff; color: #1e40af; font-family: inherit; font-size: 0.8rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; text-align: left; transition: all 0.15s;">
              <svg class="svg-icon" style="width: 16px; height: 16px; flex-shrink: 0;" viewBox="0 0 24 24"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <div>
                <div style="line-height: 1.2;">ผู้ขอเบิกพัสดุ</div>
                <div style="font-size: 0.68rem; font-weight: 400; opacity: 0.85;">ส่งคำขอเบิก</div>
              </div>
            </button>
            <button type="button" class="role-tab-btn" data-role="STAFF" onclick="selectPortalLoginRole('STAFF')" style="padding: 0.55rem 0.65rem; border-radius: 8px; border: 1px solid #cbd5e1; background: white; color: #334155; font-family: inherit; font-size: 0.8rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; text-align: left; transition: all 0.15s;">
              <svg class="svg-icon" style="width: 16px; height: 16px; flex-shrink: 0;" viewBox="0 0 24 24"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg>
              <div>
                <div style="line-height: 1.2;">เจ้าหน้าที่พัสดุ</div>
                <div style="font-size: 0.68rem; font-weight: 400; opacity: 0.85;">ผู้คัดกรอง</div>
              </div>
            </button>
            <button type="button" class="role-tab-btn" data-role="HEAD" onclick="selectPortalLoginRole('HEAD')" style="padding: 0.55rem 0.65rem; border-radius: 8px; border: 1px solid #cbd5e1; background: white; color: #334155; font-family: inherit; font-size: 0.8rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; text-align: left; transition: all 0.15s;">
              <svg class="svg-icon" style="width: 16px; height: 16px; flex-shrink: 0;" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/></svg>
              <div>
                <div style="line-height: 1.2;">หัวหน้าหน่วยงาน</div>
                <div style="font-size: 0.68rem; font-weight: 400; opacity: 0.85;">ผู้อนุมัติ</div>
              </div>
            </button>
            <button type="button" class="role-tab-btn" data-role="ADMIN" onclick="selectPortalLoginRole('ADMIN')" style="padding: 0.55rem 0.65rem; border-radius: 8px; border: 1px solid #cbd5e1; background: white; color: #334155; font-family: inherit; font-size: 0.8rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; text-align: left; transition: all 0.15s;">
              <svg class="svg-icon" style="width: 16px; height: 16px; flex-shrink: 0;" viewBox="0 0 24 24"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
              <div>
                <div style="line-height: 1.2;">ผู้ดูแลระบบสูงสุด</div>
                <div style="font-size: 0.68rem; font-weight: 400; opacity: 0.85;">ผู้ดูแลระบบ</div>
              </div>
            </button>
          </div>
          <input type="hidden" id="selectedLoginRole" value="REQUESTER">
        </div>

        <form id="requesterLoginForm" onsubmit="handleRequesterLogin(event)">
          <div class="login-input-group">
            <label for="loginUsername" id="loginUsernameLabel">ชื่อผู้ใช้งาน</label>
            <div class="login-input-wrapper">
              <span class="input-icon"><svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></span>
              <input type="text" id="loginUsername" class="login-input" placeholder="กรอกชื่อผู้ใช้งานผู้ขอเบิก" required autocomplete="username">
            </div>
          </div>
          <div class="login-input-group">
            <label for="loginPassword">รหัสผ่าน</label>
            <div class="login-input-wrapper">
              <span class="input-icon"><svg class="svg-icon" viewBox="0 0 24 24"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></span>
              <input type="password" id="loginPassword" class="login-input" placeholder="กรอกรหัสผ่านของคุณ" required autocomplete="current-password">
            </div>
          </div>
          <button type="submit" class="btn-login" id="btnLoginSubmit">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <span id="btnLoginSubmitText">เข้าสู่ระบบผู้ขอเบิกพัสดุ</span>
          </button>
        </form>

        <div class="login-notice-box" style="margin-top: 1rem;">
          <div style="font-weight: 600; color: var(--neutral-800); margin-bottom: 4px; display: flex; align-items: center; gap: 4px;">
            <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="16" y2="12"/><line x1="12" x2="12.01" y1="8" y2="8"/></svg> คำแนะนำการเข้าสู่ระบบตามบทบาท
          </div>
          <div id="loginNoticeRoleHint" style="font-size: 0.775rem; line-height: 1.5;">
            เลือกบทบาทด้านบนเพื่อเข้าสู่ระบบตามสิทธิ์ของท่าน หรือกลับไปที่ <a href="portal.html" style="color: var(--primary); font-weight: 600; text-decoration: none;">ศูนย์กลางพอร์ทัล</a>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 2. MAIN REQUESTER APPLICATION (SHOWN WHEN LOGGED IN) -->
  <div id="requesterApp" style="display: none; min-height: 100vh; flex-direction: column;">
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
          <div id="requesterUserDisplay" style="display: flex; align-items: center; gap: 0.5rem; background: var(--neutral-100); padding: 0.45rem 0.85rem; border-radius: 999px; border: 1px solid var(--neutral-200); font-size: 0.825rem; color: var(--neutral-700);">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            <span id="navRequesterName" style="font-weight: 600; color: var(--primary);">-</span>
            <span id="navRequesterDept" style="color: var(--neutral-500); font-size: 0.775rem;">-</span>
          </div>

          <span id="requesterAuthBypassBadge" style="display: none; align-items: center; gap: 4px; background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; padding: 0.35rem 0.7rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600;">
            โหมดทดสอบ: พักระบบ Login
          </span>

          <button class="btn btn-outline" id="btnSwitchTestRequester" onclick="switchTestRequester()" style="display: none; align-items: center; gap: 0.35rem; font-size: 0.78rem; padding: 0.4rem 0.7rem; border-color: #93c5fd; color: #1e40af; background: #eff6ff;">
            <svg class="svg-icon svg-icon-sm" viewBox="0 0 24 24"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg> สลับผู้ขอเบิก (ทดสอบ)
          </button>

          <button class="btn btn-outline" id="btnMyRequisitions" onclick="openMyRequisitionsModal()" style="display: inline-flex; align-items: center; gap: 0.5rem; font-weight: 600;">
            <svg class="svg-icon" viewBox="0 0 24 24"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg> รายการคำขอของฉัน
            <span class="count-tag" id="myReqsBadge" style="background: var(--primary-light); color: var(--primary); font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 999px; border: 1px solid var(--primary-border); margin-left: 2px;">0</span>
          </button>

          <button class="cart-trigger" onclick="toggleCartDrawer()">
            <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg> ตะกร้าของฉัน
            <span class="cart-badge" id="cartCount">0</span>
          </button>

          <button class="btn btn-outline" onclick="logoutRequester()" title="ออกจากระบบ" style="padding: 0.45rem 0.75rem; font-size: 0.8rem; color: var(--danger); border-color: var(--neutral-300); display: inline-flex; align-items: center; gap: 4px;">
            <svg class="svg-icon svg-icon-sm" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg> ออกจากระบบ
          </button>
        </div>
      </div>
    </header>

  <!-- Main Content Area -->
  <main>
    <!-- Requester Info Form with Pre-filled & Locked Authenticated Identity -->
    <div class="requester-bar">
      <div style="grid-column: 1 / -1; display: flex; align-items: center; gap: 6px; font-size: 0.825rem; color: var(--primary); background: var(--primary-light); padding: 7px 12px; border-radius: 8px; border: 1px solid var(--primary-border);">
        <svg class="svg-icon" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg> บัญชีผู้ขอเบิกเข้าสู่ระบบ: <strong id="barRequesterLabel">-</strong>
      </div>

      <div class="form-group custom-combobox-wrapper" id="deptComboboxWrapper">
        <label for="deptSearchInput">
          <svg class="svg-icon" viewBox="0 0 24 24"><line x1="3" x2="21" y1="22" y2="22"/><line x1="6" x2="6" y1="18" y2="11"/><line x1="10" x2="10" y1="18" y2="11"/><line x1="14" x2="14" y1="18" y2="11"/><line x1="18" x2="18" y1="18" y2="11"/><polygon points="12 2 20 7 4 7"/></svg> กลุ่มงาน / หน่วยงานที่สังกัด (สวท.) *
        </label>
        <div class="combobox-control" id="deptComboboxControl">
          <input type="text" id="deptSearchInput" class="form-control combobox-input" 
                 placeholder="กลุ่มงานที่สังกัด..." 
                 autocomplete="off" 
                 value="" 
                 readonly
                 style="background-color: var(--neutral-100); cursor: not-allowed;">
          <input type="hidden" id="deptSelect" value="">
        </div>
      </div>
      <div class="form-group custom-combobox-wrapper" id="userComboboxWrapper">
        <label for="requesterName">
          <svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> ชื่อ-นามสกุล ผู้ขอเบิก (บุคลากร สวท.) *
        </label>
        <div class="combobox-control" id="userComboboxControl">
          <input type="text" id="requesterName" class="form-control combobox-input" 
                 placeholder="ชื่อ-นามสกุล ผู้ขอเบิก..." 
                 autocomplete="off" 
                 value="" 
                 readonly
                 style="background-color: var(--neutral-100); cursor: not-allowed;">
        </div>
      </div>
      <div class="form-group">
        <label for="requesterPhone">
          <svg class="svg-icon" viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg> เบอร์โทรศัพท์ติดต่อ
        </label>
        <input type="tel" id="requesterPhone" class="form-control" placeholder="เช่น 081-234-5678" value="">
      </div>
    </div>

    <!-- Search & Filters -->
    <div class="search-filter-bar">
      <div class="search-box-wrapper">
        <span class="search-icon"><svg class="svg-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg></span>
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
        <h3><svg class="svg-icon" viewBox="0 0 24 24"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg> ตะกร้าขอเบิกพัสดุ</h3>
        <button class="close-btn" onclick="toggleCartDrawer()"><svg class="svg-icon" viewBox="0 0 24 24"><line x1="18" x2="6" y1="6" y2="18"/><line x1="6" x2="18" y1="6" y2="18"/></svg></button>
      </div>

      <div class="cart-items-list" id="cartItemsList">
        <!-- Rendered by JS -->
      </div>

      <div class="cart-footer">
        <div class="form-group">
          <label for="cartPurpose">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg> วัตถุประสงค์ในการเบิกใช้งาน *
          </label>
          <textarea id="cartPurpose" class="form-control" rows="2" placeholder="เช่น ใช้สำหรับการสอบปลายภาค, งานประชุมวิชาการ..."></textarea>
        </div>
        <button class="btn-submit-requisition" onclick="submitRequisition()">
          <svg class="svg-icon" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg> ยืนยันส่งคำขอเบิกพัสดุ
        </button>
      </div>
    </div>
  </div>

  <!-- Requisition Success Modal -->
  <div class="modal-overlay" id="successModal">
    <div class="modal-card">
      <div class="modal-header">
        <h3 style="color: var(--accent);"><svg class="svg-icon" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg> ส่งคำขอเบิกสำเร็จ</h3>
        <button class="close-btn" onclick="closeSuccessModal()"><svg class="svg-icon" viewBox="0 0 24 24"><line x1="18" x2="6" y1="6" y2="18"/><line x1="6" x2="18" y1="6" y2="18"/></svg></button>
      </div>
      <div class="modal-body" style="text-align: center; padding: 2rem 1.5rem;">
        <div style="font-size: 1.1rem; color: var(--neutral-600); margin-bottom: 0.5rem;">เลขที่เอกสารคำขอเบิกของคุณ:</div>
        <div style="font-size: 1.75rem; font-weight: 700; color: var(--primary); letter-spacing: 1px; background: var(--primary-light); padding: 0.75rem 1rem; border-radius: 8px; border: 1px dashed var(--primary-border); margin-bottom: 1rem;" id="successDocNo">
          REQ-256910-0000
        </div>
        <p style="font-size: 0.9rem; color: var(--neutral-600); line-height: 1.6;">
          คำขอของท่านถูกส่งไปยัง <strong>เจ้าหน้าที่แผนกพัสดุ</strong> เรียบร้อยแล้ว<br>
          เมื่อเจ้าหน้าที่อนุมัติและจัดของเสร็จสิ้น ท่านสามารถเดินทางมารับพัสดุได้ที่ห้องคลังพัสดุ
        </p>
      </div>
      <div class="modal-footer" style="justify-content: center; gap: 1rem;">
        <button class="btn btn-outline" onclick="closeSuccessModal(); openMyRequisitionsModal();">
          <svg class="svg-icon" viewBox="0 0 24 24"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg> ดูรายการคำขอของฉัน
        </button>
        <button class="btn btn-primary" onclick="closeSuccessModal()">ตกลง / เบิกรายการอื่นต่อ</button>
      </div>
    </div>
  </div>

  <!-- My Requisitions Modal -->
  <div class="modal-overlay" id="myRequisitionsModal">
    <div class="modal-card req-modal-card">
      <div class="modal-header">
        <h3 style="display: flex; align-items: center; gap: 0.5rem;">
          <svg class="svg-icon" viewBox="0 0 24 24"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg> รายการคำขอเบิกพัสดุของฉัน
          <span id="myReqsModalCount" style="font-size: 0.85rem; font-weight: normal; color: var(--neutral-600);">(0 รายการ)</span>
        </h3>
        <button class="close-btn" onclick="closeMyRequisitionsModal()"><svg class="svg-icon" viewBox="0 0 24 24"><line x1="18" x2="6" y1="6" y2="18"/><line x1="6" x2="18" y1="6" y2="18"/></svg></button>
      </div>

      <div class="modal-body" style="padding: 1.25rem; overflow-y: auto; max-height: calc(88vh - 130px);">
        <!-- Search and Filter Bar -->
        <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 0.85rem; align-items: center;">
          <div style="flex: 1; min-width: 260px; position: relative;">
            <span style="position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); color: var(--neutral-400); display: flex;">
              <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            </span>
            <input type="text" id="myReqsSearchInput" class="form-control" style="padding-left: 2.3rem;"
                   placeholder="ค้นหาเลขที่คำขอ, ชื่อผู้ขอ, หน่วยงาน, หรือชื่อพัสดุ..." 
                   oninput="handleMyReqsSearch()">
          </div>
          <div style="display: flex; align-items: center; gap: 6px;">
            <label style="font-size: 0.825rem; font-weight: 600; color: var(--neutral-600); white-space: nowrap;">เดือน:</label>
            <select id="myReqsMonthSelect" class="form-control" style="width: auto; min-width: 160px;" onchange="handleMyReqsSearch()">
              <option value="ALL">ทุกเดือนย้อนหลัง</option>
              <option value="2026-11" selected>พฤศจิกายน 2569</option>
              <option value="2026-10">ตุลาคม 2569</option>
              <option value="2026-09">กันยายน 2569</option>
            </select>
          </div>
        </div>

        <div class="req-filter-tabs">
          <button class="req-tab-btn active" onclick="filterMyReqsTab('ALL', this)">ทั้งหมด</button>
          <button class="req-tab-btn" onclick="filterMyReqsTab('PENDING', this)">รอคัดกรอง</button>
          <button class="req-tab-btn" onclick="filterMyReqsTab('VERIFIED', this)">รอหัวหน้าอนุมัติ</button>
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
          <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="16" y2="12"/><line x1="12" x2="12.01" y1="8" y2="8"/></svg> ข้อมูลอัปเดตแบบเรียลไทม์ ซิงค์กับระบบคลังพัสดุ
        </span>
        <button class="btn btn-outline" onclick="closeMyRequisitionsModal()">ปิดหน้าต่าง</button>
      </div>
    </div>
  </div>

  <!-- OFFICIAL REQUISITION PDF MODAL (REQUESTER PORTAL) -->
  <div class="modal-overlay" id="requisitionPdfModal" style="display: none; align-items: center; justify-content: center; z-index: 100;">
    <div class="modal-card" style="max-width: 880px; width: 95%; max-height: 94vh; padding: 0; display: flex; flex-direction: column; overflow: hidden; background: white;">
      <div class="modal-header" style="padding: 1rem 1.5rem; background: var(--neutral-50); border-bottom: 1px solid var(--neutral-200); display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <svg class="svg-icon" viewBox="0 0 24 24"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>
          <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--neutral-900);">ใบขอเบิกพัสดุ</h3>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <button class="btn btn-primary" onclick="printRequisitionPdf()" style="padding: 0.45rem 1rem; font-size: 0.85rem;">
            <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect width="12" height="8" x="6" y="14"/></svg> สั่งพิมพ์เอกสาร PDF
          </button>
          <button class="close-btn" onclick="closeRequisitionPdfModal()">
            <svg class="svg-icon" viewBox="0 0 24 24"><line x1="18" x2="6" y1="6" y2="18"/><line x1="6" x2="18" y1="6" y2="18"/></svg>
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

          <div class="pdf-footer-section">
            <div class="pdf-ack-note">
              * ข้าพเจ้าได้รับมอบพัสดุตามรายการและจำนวนที่ระบุข้างต้นไว้ในสภาพเรียบร้อยครบถ้วนแล้ว
            </div>
            <div class="pdf-signatures">
              <div class="sig-box">
                <div class="sig-line"></div>
                <div style="margin-top: 4px;">(<span id="pdfSigRequester">-</span>)</div>
                <div style="font-size: 0.78rem; color: #444; font-weight: 600;">ผู้ขอเบิกพัสดุ</div>
                <div style="font-size: 0.72rem; color: #666;" id="pdfSigReqDate">-</div>
              </div>

              <div class="sig-box">
                <div id="pdfSigVerifierStamp" style="font-size: 0.75rem; color: #0369a1; font-weight: 700; margin-bottom: 6px;"></div>
                <div class="sig-line"></div>
                <div style="margin-top: 4px;">(<span id="pdfSigVerifier">เจ้าหน้าที่พัสดุ</span>)</div>
                <div style="font-size: 0.78rem; color: #444; font-weight: 600;">เจ้าหน้าที่ผู้คัดกรอง</div>
                <div style="font-size: 0.72rem; color: #666;" id="pdfSigVerifiedDate">-</div>
              </div>

              <div class="sig-box">
                <div id="pdfSigApproverStamp" style="font-size: 0.75rem; color: #15803d; font-weight: 700; margin-bottom: 6px;"></div>
                <div class="sig-line"></div>
                <div style="margin-top: 4px;">(<span id="pdfSigApprover">หัวหน้าหน่วยงาน</span>)</div>
                <div style="font-size: 0.78rem; color: #444; font-weight: 600;">หัวหน้าผู้อนุมัติ</div>
                <div style="font-size: 0.72rem; color: #666;" id="pdfSigApprovedDate">-</div>
              </div>

              <div class="sig-box">
                <div id="pdfSigOfficerBox"></div>
                <div class="sig-line"></div>
                <div style="margin-top: 4px;">(<span id="pdfSigRecipient">-</span>)</div>
                <div style="font-size: 0.78rem; color: #444; font-weight: 600;">ผู้รับมอบพัสดุ</div>
                <div style="font-size: 0.72rem; color: #666;" id="pdfSigReceiveDate">-</div>
              </div>
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
      © 2569 ระบบขอเบิกพัสดุและคลังดิจิทัล มหาวิทยาลัยสวนดุสิต v__SYSTEM_VERSION__ | ใช้งานเฉพาะภายในสถาบัน
    </div>
  </footer>
  </div>

  <!-- Scripts -->
  <script>
    const APP_VERSION = '__SYSTEM_VERSION__';
    const MYSQL_API_URL = '/api';
    const AUTH_BYPASS = __AUTH_BYPASS__;
    const defaultDepts = __DEFAULT_DEPTS__;
    const defaultUsers = __DEFAULT_USERS__;

    const vIcons = {
      box: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>`,
      cart: `<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg>`,
      clipboard: `<svg class="svg-icon" viewBox="0 0 24 24"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg>`,
      search: `<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>`,
      layers: `<svg class="svg-icon" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>`,
      tag: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94.94-2.48 0-3.42L12 2Z"/><circle cx="7" cy="7" r=".5" fill="currentColor"/></svg>`,
      trash: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>`,
      check: `<svg class="svg-icon" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>`,
      clock: `<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
      info: `<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="16" y2="12"/><line x1="12" x2="12.01" y1="8" y2="8"/></svg>`,
      user: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`,
      lock: `<svg class="svg-icon" viewBox="0 0 24 24"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>`,
      log_out: `<svg class="svg-icon svg-icon-sm" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>`,
      building: `<svg class="svg-icon" viewBox="0 0 24 24"><line x1="3" x2="21" y1="22" y2="22"/><line x1="6" x2="6" y1="18" y2="11"/><line x1="10" x2="10" y1="18" y2="11"/><line x1="14" x2="14" y1="18" y2="11"/><line x1="18" x2="18" y1="18" y2="11"/><polygon points="12 2 20 7 4 7"/></svg>`,
      file_text: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>`,
      printer: `<svg class="svg-icon" viewBox="0 0 24 24"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect width="12" height="8" x="6" y="14"/></svg>`,
      calendar: `<svg class="svg-icon" viewBox="0 0 24 24"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>`,
      shield: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
      x: `<svg class="svg-icon" viewBox="0 0 24 24"><line x1="18" x2="6" y1="6" y2="18"/><line x1="6" x2="18" y1="6" y2="18"/></svg>`
    };

    // SHARED LOCAL STORAGE DB INITIALIZATION
    const DB_ITEMS_KEY = 'inventory_items';
    const DB_REQS_KEY = 'inventory_requisitions';
    const DB_USERS_KEY = 'inventory_users';
    const DB_DEPTS_KEY = 'inventory_departments';
    const DB_QUOTAS_KEY = 'inventory_quotas';

    function getQuotasDB() {
      try {
        const raw = localStorage.getItem(DB_QUOTAS_KEY);
        const parsed = raw ? JSON.parse(raw) : [];
        return Array.isArray(parsed) ? parsed : [];
      } catch (e) {
        return [];
      }
    }
    function saveQuotasDB(list) {
      localStorage.setItem(DB_QUOTAS_KEY, JSON.stringify(Array.isArray(list) ? list : []));
    }

    const defaultItems = __DEFAULT_ITEMS__;
    const defaultReqs = __DEFAULT_REQS__;

    function getDeptsDB() {
      const data = localStorage.getItem(DB_DEPTS_KEY);
      if (!data) {
        localStorage.setItem(DB_DEPTS_KEY, JSON.stringify(defaultDepts));
        return JSON.parse(JSON.stringify(defaultDepts));
      }
      try {
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed) && parsed.length > 0 && parsed[0].category && parsed[0].category.includes('สวท')) {
          return parsed;
        }
        localStorage.setItem(DB_DEPTS_KEY, JSON.stringify(defaultDepts));
        return JSON.parse(JSON.stringify(defaultDepts));
      } catch (e) {
        localStorage.setItem(DB_DEPTS_KEY, JSON.stringify(defaultDepts));
        return JSON.parse(JSON.stringify(defaultDepts));
      }
    }

    function saveDeptsDB(depts) {
      localStorage.setItem(DB_DEPTS_KEY, JSON.stringify(depts));
    }

    function getUsersDB() {
      const data = localStorage.getItem(DB_USERS_KEY);
      if (!data) {
        localStorage.setItem(DB_USERS_KEY, JSON.stringify(defaultUsers));
        return JSON.parse(JSON.stringify(defaultUsers));
      }
      try {
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed) && parsed.length > 0) {
          // Auto-migrate if localStorage still had the old 29-user list (contains ผอ.อังค์ริสา)
          if (parsed.some(u => u.name && u.name.includes('อังค์ริสา'))) {
            const customAdded = parsed.filter(u => Number(u.id) > 29);
            const migrated = [
              ...JSON.parse(JSON.stringify(defaultUsers)),
              ...customAdded.map((u, idx) => ({ ...u, id: defaultUsers.length + idx + 1 }))
            ];
            localStorage.setItem(DB_USERS_KEY, JSON.stringify(migrated));
            return migrated;
          }
          return parsed;
        }
        localStorage.setItem(DB_USERS_KEY, JSON.stringify(defaultUsers));
        return JSON.parse(JSON.stringify(defaultUsers));
      } catch (e) {
        localStorage.setItem(DB_USERS_KEY, JSON.stringify(defaultUsers));
        return JSON.parse(JSON.stringify(defaultUsers));
      }
    }

    function saveUsersDB(users) {
      localStorage.setItem(DB_USERS_KEY, JSON.stringify(users));
    }

    function getItemsDB() {
      const data = localStorage.getItem(DB_ITEMS_KEY);
      if (!data) {
        localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(defaultItems));
        return JSON.parse(JSON.stringify(defaultItems));
      }
      try {
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed) && parsed.length > 0) {
          const defMap = new Map(defaultItems.map(i => [i.id, i]));
          let needsSave = false;
          const upgraded = parsed.map(ex => {
            const defItem = defMap.get(ex.id);
            if (defItem && ex.image_piece && ex.image_piece.startsWith('assets/images/image')) {
              needsSave = true;
              return { ...defItem, on_hand_pieces: ex.on_hand_pieces, reserved_pieces: ex.reserved_pieces };
            }
            return ex;
          });
          if (needsSave) localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(upgraded));
          return upgraded;
        }
        return parsed;
      } catch (e) {
        localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(defaultItems));
        return JSON.parse(JSON.stringify(defaultItems));
      }
    }

    async function syncFromMySQLAPI() {
      if (!MYSQL_API_URL || !navigator.onLine) return;
      try {
        const [itemsRes, reqsRes, usersRes, deptsRes, quotasRes] = await Promise.all([
          fetch(`${MYSQL_API_URL}?action=getItems`).then(r => r.json()).catch(() => null),
          fetch(`${MYSQL_API_URL}?action=getRequisitions`).then(r => r.json()).catch(() => null),
          fetch(`${MYSQL_API_URL}?action=getUsers`).then(r => r.json()).catch(() => null),
          fetch(`${MYSQL_API_URL}?action=getDepartments`).then(r => r.json()).catch(() => null),
          fetch(`${MYSQL_API_URL}?action=getQuotas`).then(r => r.json()).catch(() => null)
        ]);
        if (quotasRes && quotasRes.status === 'success' && Array.isArray(quotasRes.data)) {
          saveQuotasDB(quotasRes.data);
          if (typeof renderCatalog === 'function') renderCatalog();
        }
        if (itemsRes && itemsRes.status === 'success' && Array.isArray(itemsRes.data) && itemsRes.data.length > 0) {
          saveItemsDB(itemsRes.data);
          renderCatalog();
        }
        if (reqsRes && reqsRes.status === 'success' && Array.isArray(reqsRes.data) && reqsRes.data.length > 0) {
          saveReqsDB(reqsRes.data);
          updateMyReqsBadge();
        }
        if (usersRes && usersRes.status === 'success' && Array.isArray(usersRes.data) && usersRes.data.length > 0) {
          saveUsersDB(usersRes.data);
        }
        if (deptsRes && deptsRes.status === 'success' && Array.isArray(deptsRes.data) && deptsRes.data.length > 0) {
          const grouped = {};
          deptsRes.data.forEach(d => {
            const cat = d.category || 'สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)';
            const lbl = d.full_label || d.name;
            if (!grouped[cat]) grouped[cat] = [];
            if (lbl && !grouped[cat].some(x => x.value === lbl)) {
              grouped[cat].push({ label: lbl, value: lbl, sub: false });
            }
          });
          const formattedDepts = Object.keys(grouped).map(k => ({ category: k, items: grouped[k] }));
          if (formattedDepts.length > 0) saveDeptsDB(formattedDepts);
        }
      } catch (err) {
        console.warn('Offline fallback active (localStorage):', err);
      }
    }

    async function postToMySQLAPI(action, payload) {
      if (!MYSQL_API_URL || !navigator.onLine) return null;
      try {
        const res = await fetch(MYSQL_API_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'text/plain;charset=utf-8' },
          body: JSON.stringify({ action, payload })
        });
        return await res.json();
      } catch (err) {
        console.warn('MySQL API unreachable, saved to localStorage fallback:', err);
        return null;
      }
    }

    function saveItemsDB(items) {
      localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(items));
    }

    function getReqsDB() {
      const data = localStorage.getItem(DB_REQS_KEY);
      if (!data) {
        localStorage.setItem(DB_REQS_KEY, JSON.stringify(defaultReqs));
        return defaultReqs;
      }
      try {
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed)) {
          const defMap = new Map(defaultReqs.map(r => [r.id, r]));
          let needsSave = false;
          const updated = parsed.map(r => {
            const defReq = defMap.get(r.id);
            if (defReq && (r.dept === 'โรงเรียนการเรือน' || r.dept === 'คณะพยาบาลศาสตร์')) {
              needsSave = true;
              return { ...r, dept: defReq.dept, requester: defReq.requester, purpose: defReq.purpose };
            }
            return r;
          });
          if (needsSave) localStorage.setItem(DB_REQS_KEY, JSON.stringify(updated));
          return updated;
        }
        return parsed;
      } catch (e) {
        return defaultReqs;
      }
    }

    function saveReqsDB(reqs) {
      localStorage.setItem(DB_REQS_KEY, JSON.stringify(reqs));
    }

    let cart = [];
    let currentCategory = 'ALL';

    // Department Combobox Logic
    function renderDeptDropdown(filterText = "") {
      const dropdown = document.getElementById('deptDropdownList');
      const cleanFilter = filterText.trim().toLowerCase();
      let totalMatches = 0;
      let html = "";
      const currentVal = document.getElementById('deptSelect').value;
      const deptsData = getDeptsDB();

      deptsData.forEach(cat => {
        const matchedItems = cat.items.filter(item => 
          item.label.toLowerCase().includes(cleanFilter) || item.value.toLowerCase().includes(cleanFilter)
        );

        if (matchedItems.length > 0) {
          totalMatches += matchedItems.length;
          html += `<div class="combobox-group-title">${cat.category}</div>`;
          matchedItems.forEach(item => {
            const isSelected = item.value === currentVal;
            const subClass = item.sub ? 'combobox-item-sub' : '';
            const safeVal = item.value.replace(/'/g, "\'");
            const safeLbl = item.label.replace(/'/g, "\'");
            html += `
              <div class="combobox-item ${subClass} ${isSelected ? 'selected' : ''}" 
                   onclick="selectDepartment('${safeVal}', '${safeLbl}')">
                <span>${item.label}</span>
                ${isSelected ? `<span style="color: var(--primary); font-size: 0.8rem;">${vIcons.check}</span>` : ''}
              </div>
            `;
          });
        }
      });

      if (totalMatches === 0) {
        html = `<div class="combobox-no-results">ไม่พบหน่วยงานที่ตรงกับ "${filterText}"</div>`;
      }
      dropdown.innerHTML = html;
    }

    function openDeptDropdown() {
      closeUserDropdown();
      const dd = document.getElementById('deptDropdownList');
      const ctrl = document.getElementById('deptComboboxControl');
      if (!dd) return;
      dd.classList.add('open');
      if (ctrl) ctrl.classList.add('open');
      renderDeptDropdown("");
    }

    function closeDeptDropdown() {
      const dd = document.getElementById('deptDropdownList');
      const ctrl = document.getElementById('deptComboboxControl');
      if (dd) dd.classList.remove('open');
      if (ctrl) ctrl.classList.remove('open');
    }

    function toggleDeptDropdown(e) {
      e.stopPropagation();
      const dropdown = document.getElementById('deptDropdownList');
      if (!dropdown) return;
      if (dropdown.classList.contains('open')) closeDeptDropdown();
      else {
        const searchIn = document.getElementById('deptSearchInput');
        if (searchIn) searchIn.focus();
        openDeptDropdown();
      }
    }

    function handleDeptSearch(text) {
      document.getElementById('deptSelect').value = text.trim();
      openDeptDropdown();
      renderDeptDropdown(text);
    }

    function selectDepartment(value, label) {
      document.getElementById('deptSelect').value = value;
      document.getElementById('deptSearchInput').value = label;
      closeDeptDropdown();
    }

    // User (Personnel) Combobox Logic
    function renderUserDropdown(filterText = "") {
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

      if (matched.length === 0) {
        dropdown.innerHTML = `<div class="combobox-no-results">ไม่พบรายชื่อในระบบ (สามารถพิมพ์ชื่อ "${filterText}" เพื่อขอเบิกได้ทันที)</div>`;
        return;
      }

      let html = "";
      // Group by department, putting selectedDept first if chosen
      const groups = {};
      matched.forEach(u => {
        const d = u.dept || 'ไม่ระบุกลุ่มงาน';
        if (!groups[d]) groups[d] = [];
        groups[d].push(u);
      });

      const deptKeys = Object.keys(groups);
      if (selectedDept && groups[selectedDept]) {
        deptKeys.sort((a, b) => (a === selectedDept ? -1 : b === selectedDept ? 1 : 0));
      }

      deptKeys.forEach(deptName => {
        const isCurrentDept = deptName === selectedDept;
        html += `<div class="combobox-group-title">${deptName}${isCurrentDept ? ' (กลุ่มงานที่เลือก)' : ''}</div>`;
        groups[deptName].forEach(u => {
          const isSelected = u.name === currentName;
          html += `
            <div class="combobox-item ${isSelected ? 'selected' : ''}"
                 onclick="selectRequesterUser(${u.id})"
                 style="display: flex; justify-content: space-between; align-items: center; gap: 0.5rem;">
              <div style="display: flex; flex-direction: column;">
                <span style="font-weight: 500; color: var(--neutral-900);">${u.name}</span>
                <span style="font-size: 0.75rem; color: var(--neutral-500);">${u.position || '-'}</span>
              </div>
              ${isSelected ? `<span style="color: var(--primary); font-size: 0.8rem;">${vIcons.check}</span>` : ''}
            </div>
          `;
        });
      });

      dropdown.innerHTML = html;
    }

    function openUserDropdown() {
      closeDeptDropdown();
      const dd = document.getElementById('userDropdownList');
      const ctrl = document.getElementById('userComboboxControl');
      if (!dd) return;
      dd.classList.add('open');
      if (ctrl) ctrl.classList.add('open');
      renderUserDropdown(document.getElementById('requesterName').value);
    }

    function closeUserDropdown() {
      const dd = document.getElementById('userDropdownList');
      const ctrl = document.getElementById('userComboboxControl');
      if (dd) dd.classList.remove('open');
      if (ctrl) ctrl.classList.remove('open');
    }

    function toggleUserDropdown(e) {
      e.stopPropagation();
      const dropdown = document.getElementById('userDropdownList');
      if (!dropdown) return;
      if (dropdown.classList.contains('open')) closeUserDropdown();
      else {
        const nameIn = document.getElementById('requesterName');
        if (nameIn) nameIn.focus();
        openUserDropdown();
      }
    }

    function handleUserSearch(text) {
      openUserDropdown();
      renderUserDropdown(text);
      renderCatalog();
    }

    function selectRequesterUser(userId) {
      const users = getUsersDB();
      const user = users.find(u => Number(u.id) === Number(userId));
      if (user) {
        document.getElementById('requesterName').value = user.name;
        if (user.dept) {
          document.getElementById('deptSelect').value = user.dept;
          document.getElementById('deptSearchInput').value = user.dept;
        }
        if (user.phone) {
          document.getElementById('requesterPhone').value = user.phone;
        }
      }
      closeUserDropdown();
      renderCatalog();
    }

    document.addEventListener('click', (e) => {
      const deptWrapper = document.getElementById('deptComboboxWrapper');
      if (deptWrapper && !deptWrapper.contains(e.target)) closeDeptDropdown();
      const userWrapper = document.getElementById('userComboboxWrapper');
      if (userWrapper && !userWrapper.contains(e.target)) closeUserDropdown();
    });

    // Catalog Rendering
    function formatStockDisplay(totalPieces, ratio, boxName, pieceName, isMulti) {
      const safePiece = escapeHtml(pieceName);
      const safeBox = escapeHtml(boxName);
      if (!isMulti || ratio <= 1) return `${totalPieces.toLocaleString()} ${safePiece}`;
      const boxes = Math.floor(totalPieces / ratio);
      const pieces = totalPieces % ratio;
      if (boxes > 0 && pieces > 0) return `${boxes} ${safeBox} ${pieces} ${safePiece}`;
      if (boxes > 0) return `${boxes} ${safeBox}`;
      return `${pieces} ${safePiece}`;
    }

    function getCurrentRequesterName() {
      const inputEl = document.getElementById('requesterName');
      if (inputEl && inputEl.value && inputEl.value.trim()) {
        return inputEl.value.trim();
      }
      if (typeof getLoggedInRequester === 'function') {
        const u = getLoggedInRequester();
        if (u && (u.name || u.username)) return String(u.name || u.username).trim();
      }
      return '';
    }

    function getCurrentRequesterDept() {
      const selEl = document.getElementById('deptSelect');
      if (selEl && selEl.value && selEl.value.trim()) return selEl.value.trim();
      const srchEl = document.getElementById('deptSearchInput');
      if (srchEl && srchEl.value && srchEl.value.trim()) return srchEl.value.trim();
      if (typeof getLoggedInRequester === 'function') {
        const u = getLoggedInRequester();
        if (u && u.dept) return String(u.dept).trim();
      }
      return '';
    }

    function getPersonalMonthlyQuotaInfo(item) {
      const itemId = Number(item.id);
      const currentPerson = getCurrentRequesterName();
      const currentDept = getCurrentRequesterDept();
      const quotas = getQuotasDB();

      const findRule = (tType, tKey, iId) => {
        if (!tKey) return null;
        const cleanKey = tKey.trim().toLowerCase();
        return quotas.find(q =>
          String(q.targetType || q.target_type || '').toUpperCase() === tType &&
          String(q.targetKey || q.target_key || '').trim().toLowerCase() === cleanKey &&
          Number(q.itemId ?? q.item_id ?? 0) === Number(iId)
        ) || null;
      };

      const userItemRule = findRule('USER', currentPerson, itemId);
      const userAllRule = findRule('USER', currentPerson, 0);
      const deptItemRule = findRule('DEPT', currentDept, itemId);
      const deptAllRule = findRule('DEPT', currentDept, 0);

      let limit = 0;
      let userSource = 'NONE';
      if (userItemRule) {
        limit = Number(userItemRule.monthlyLimit ?? userItemRule.monthly_limit ?? 0);
        userSource = 'USER_ITEM';
      } else if (userAllRule) {
        limit = Number(userAllRule.monthlyLimit ?? userAllRule.monthly_limit ?? 0);
        userSource = 'USER_ALL';
      } else if (Number(item.monthly_limit || 0) > 0) {
        limit = Number(item.monthly_limit || 0);
        userSource = 'ITEM_DEFAULT';
      }

      let deptLimit = 0;
      let deptSource = 'NONE';
      if (deptItemRule) {
        deptLimit = Number(deptItemRule.monthlyLimit ?? deptItemRule.monthly_limit ?? 0);
        deptSource = 'DEPT_ITEM';
      } else if (deptAllRule) {
        deptLimit = Number(deptAllRule.monthlyLimit ?? deptAllRule.monthly_limit ?? 0);
        deptSource = 'DEPT_ALL';
      }

      if (limit <= 0 && deptLimit <= 0) {
        return {
          limit: 0, used: 0, remaining: Infinity, requester: currentPerson, userSource,
          deptLimit: 0, deptUsed: 0, deptRemaining: Infinity, dept: currentDept, deptSource
        };
      }

      const curDate = new Date();
      const curYm = `${curDate.getFullYear()}-${String(curDate.getMonth() + 1).padStart(2, '0')}`;
      const curBeYm = `REQ-${curDate.getFullYear() + 543}${String(curDate.getMonth() + 1).padStart(2, '0')}`;
      const reqs = getReqsDB();
      let used = 0;
      let deptUsed = 0;
      reqs.forEach(r => {
        if (r.status !== 'REJECTED') {
          const isThisMonth = (r.created_at && r.created_at.startsWith(curYm)) || (r.id && r.id.startsWith(curBeYm));
          if (isThisMonth && Array.isArray(r.items)) {
            let itemSum = 0;
            r.items.forEach(ri => {
              if (Number(ri.itemId) === itemId) itemSum += Number(ri.totalPieces || 0);
            });
            if (itemSum > 0) {
              if (!currentPerson || (r.requester || '').trim() === currentPerson) used += itemSum;
              if (currentDept && (r.dept || '').trim() === currentDept) deptUsed += itemSum;
            }
          }
        }
      });
      if (typeof cart !== 'undefined' && Array.isArray(cart)) {
        const inCart = cart.find(c => Number(c.itemId) === itemId);
        if (inCart) {
          used += Number(inCart.totalPieces || 0);
          if (currentDept) deptUsed += Number(inCart.totalPieces || 0);
        }
      }
      return {
        limit,
        used,
        remaining: limit > 0 ? Math.max(0, limit - used) : Infinity,
        requester: currentPerson,
        userSource,
        deptLimit,
        deptUsed,
        deptRemaining: deptLimit > 0 ? Math.max(0, deptLimit - deptUsed) : Infinity,
        dept: currentDept,
        deptSource
      };
    }

    function renderCatalog() {
      const items = getItemsDB();
      const grid = document.getElementById('catalogGrid');
      const searchTerm = document.getElementById('itemSearchInput').value.trim().toLowerCase();

      const filtered = items.filter(item => {
        const matchesCategory = currentCategory === 'ALL' || item.category === currentCategory;
        const matchesSearch = item.name.toLowerCase().includes(searchTerm);
        return matchesCategory && matchesSearch;
      });

      if (filtered.length === 0) {
        grid.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--neutral-400);">
            <p style="font-size: 1.1rem; font-weight: 500;">ไม่พบรายการพัสดุที่ตรงกับ "${searchTerm}"</p>
          </div>
        `;
        return;
      }

      grid.innerHTML = filtered.map(item => {
        const availablePieces = Math.max(0, item.on_hand_pieces - item.reserved_pieces);
        const minAlert = (item.min_alert !== undefined && item.min_alert !== null) ? Number(item.min_alert) : 10;
        const isLow = availablePieces <= minAlert;
        const stockStr = formatStockDisplay(availablePieces, item.pieces_per_box, item.unit_box_name, item.unit_piece_name, item.is_multi_unit);
        const imgSrc = item.current_img_mode === 'box' ? item.image_box : item.image_piece;

        const safeName = escapeHtml(item.name);
        const safeBoxName = escapeHtml(item.unit_box_name);
        const safePieceName = escapeHtml(item.unit_piece_name);
        const safeImgSrc = escapeHtml(imgSrc);

        let statusLabel = 'พร้อมให้เบิก:';
        if (availablePieces === 0) {
          statusLabel = 'หมดสต๊อกชั่วคราว:';
        } else if (isLow) {
          statusLabel = 'พร้อมให้เบิก (เหลือน้อย):';
        }

        return `
          <div class="item-card">
            <div class="item-image-wrapper">
              <img src="${safeImgSrc}" class="item-img" alt="${safeName}" onerror="this.onerror=null; this.src='assets/logo_sdu.png'">
              ${item.is_multi_unit ? `
                <div class="image-toggle-pills">
                  <button class="img-pill-btn ${item.current_img_mode !== 'box' ? 'active' : ''}" 
                          onclick="toggleItemImg(${item.id}, 'piece')">รูปชิ้น</button>
                  <button class="img-pill-btn ${item.current_img_mode === 'box' ? 'active' : ''}" 
                          onclick="toggleItemImg(${item.id}, 'box')">รูป${safeBoxName}</button>
                </div>
              ` : ''}
            </div>
            <div class="card-body">
              <h3 class="item-title">${safeName}</h3>
              ${item.is_multi_unit ? `
                <span class="ratio-badge">${vIcons.layers} 1 ${safeBoxName} = ${item.pieces_per_box.toLocaleString()} ${safePieceName}</span>
              ` : `
                <span class="ratio-badge">${vIcons.tag} หน่วยเดี่ยว: ${safePieceName}</span>
              `}
              ${(() => {
                const qInfo = getPersonalMonthlyQuotaInfo(item);
                let quotaHtml = '';
                if (qInfo.limit > 0) {
                  const isQuotaEmpty = qInfo.remaining <= 0;
                  const srcTag = qInfo.userSource === 'USER_ITEM' || qInfo.userSource === 'USER_ALL' ? ' (เฉพาะบุคคล)' : '';
                  quotaHtml += `
                    <div style="font-size: 0.75rem; color: ${isQuotaEmpty ? '#991b1b' : '#b45309'}; background: ${isQuotaEmpty ? '#fef2f2' : '#fffbeb'}; border: 1px solid ${isQuotaEmpty ? '#fecaca' : '#fde68a'}; border-radius: 6px; padding: 4px 8px; margin-top: 4px; display: flex; flex-direction: column; gap: 2px;">
                      <span style="display: inline-flex; align-items: center; gap: 4px; font-weight: 600;">
                        ${vIcons.shield} โควตาบุคลากร${srcTag}: ${qInfo.limit.toLocaleString()} ${safePieceName}/ท่าน/เดือน
                      </span>
                      <span style="font-size: 0.72rem; color: ${isQuotaEmpty ? '#dc2626' : '#92400e'};">
                        โควตาคงเหลือของท่านในเดือนนี้: <strong>${qInfo.remaining.toLocaleString()} ${safePieceName}</strong> (เบิกแล้ว ${qInfo.used.toLocaleString()})
                      </span>
                    </div>
                  `;
                }
                if (qInfo.deptLimit > 0) {
                  const isDeptEmpty = qInfo.deptRemaining <= 0;
                  quotaHtml += `
                    <div style="font-size: 0.75rem; color: ${isDeptEmpty ? '#991b1b' : '#1e40af'}; background: ${isDeptEmpty ? '#fef2f2' : '#eff6ff'}; border: 1px solid ${isDeptEmpty ? '#fecaca' : '#bfdbfe'}; border-radius: 6px; padding: 4px 8px; margin-top: 4px; display: flex; flex-direction: column; gap: 2px;">
                      <span style="display: inline-flex; align-items: center; gap: 4px; font-weight: 600;">
                        ${vIcons.building} โควตากลุ่มงาน: ${qInfo.deptLimit.toLocaleString()} ${safePieceName}/หน่วยงาน/เดือน
                      </span>
                      <span style="font-size: 0.72rem; color: ${isDeptEmpty ? '#dc2626' : '#1e3a8a'};">
                        คงเหลือของกลุ่มงานเดือนนี้: <strong>${qInfo.deptRemaining.toLocaleString()} ${safePieceName}</strong> (เบิกรวมแล้ว ${qInfo.deptUsed.toLocaleString()})
                      </span>
                    </div>
                  `;
                }
                return quotaHtml;
              })()}
              <div class="stock-info ${isLow ? 'low' : ''}">
                <span class="stock-label">${statusLabel}</span>
                <span class="stock-value">${stockStr}</span>
              </div>
              <div class="card-actions">
                <div class="qty-inputs">
                  ${item.is_multi_unit ? `
                    <div class="qty-col">
                      <label>จำนวน (${safeBoxName})</label>
                      <input type="number" id="qty-box-${item.id}" class="qty-input" min="0" placeholder="0">
                    </div>
                  ` : ''}
                  <div class="qty-col" style="${!item.is_multi_unit ? 'grid-column: span 2;' : ''}">
                    <label>จำนวน (${safePieceName})</label>
                    <input type="number" id="qty-piece-${item.id}" class="qty-input" min="0" placeholder="0">
                  </div>
                </div>
                <button class="btn-add-cart" onclick="addToCart(${item.id})">
                  ${vIcons.cart} เพิ่มเข้าตะกร้า
                </button>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    function toggleItemImg(itemId, mode) {
      const items = getItemsDB();
      const itm = items.find(i => i.id === itemId);
      if (itm) {
        itm.current_img_mode = mode;
        saveItemsDB(items);
        renderCatalog();
      }
    }

    function handleSearch() { renderCatalog(); }
    function filterCategory(cat, btn) {
      currentCategory = cat;
      document.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderCatalog();
    }

    // Cart Logic
    function addToCart(itemId) {
      const items = getItemsDB();
      const item = items.find(i => i.id === itemId);
      if (!item) return;

      const boxInput = document.getElementById(`qty-box-${item.id}`);
      const pieceInput = document.getElementById(`qty-piece-${item.id}`);
      const qtyBoxes = boxInput ? parseInt(boxInput.value || 0) : 0;
      const qtyPieces = pieceInput ? parseInt(pieceInput.value || 0) : 0;

      if (qtyBoxes <= 0 && qtyPieces <= 0) {
        Swal.fire({
          icon: 'warning',
          title: 'กรุณาระบุจำนวน',
          text: 'กรุณาระบุจำนวนที่ต้องการเบิกอย่างน้อย 1 ชิ้นหรือกล่องครับ',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        });
        return;
      }

      const totalPieces = (qtyBoxes * item.pieces_per_box) + qtyPieces;
      const availablePieces = item.on_hand_pieces - item.reserved_pieces;

      if (totalPieces > availablePieces) {
        Swal.fire({
          icon: 'error',
          title: 'ยอดพัสดุไม่เพียงพอ',
          html: `คุณขอเบิกจำนวน <b>${totalPieces.toLocaleString()} ${item.unit_piece_name}</b><br>แต่มีพร้อมเบิกเพียง <b>${availablePieces.toLocaleString()} ${item.unit_piece_name}</b>`,
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'เข้าใจแล้ว'
        });
        return;
      }

      const qCheck = getPersonalMonthlyQuotaInfo(item);
      if (qCheck.limit > 0 && qCheck.used + totalPieces > qCheck.limit) {
        const rem = Math.max(0, qCheck.limit - qCheck.used);
        const personLabel = escapeHtml(qCheck.requester || 'ท่าน');
        Swal.fire({
          icon: 'warning',
          title: 'เกินโควตารายเดือนต่อบุคลากร',
          html: `พัสดุนี้ถูกจำกัดโควตาสำหรับ <b>${personLabel}</b> ไม่เกิน <b>${qCheck.limit.toLocaleString()} ${item.unit_piece_name}/เดือน</b><br>ในเดือนนี้มีการขอเบิก/อยู่ในตะกร้าแล้ว <b>${qCheck.used.toLocaleString()} ${item.unit_piece_name}</b><br>คงเหลือโควตาที่ขอได้อีก <b>${rem.toLocaleString()} ${item.unit_piece_name}</b>`,
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'เข้าใจแล้ว'
        });
        return;
      }
      if (qCheck.deptLimit > 0 && qCheck.deptUsed + totalPieces > qCheck.deptLimit) {
        const dRem = Math.max(0, qCheck.deptLimit - qCheck.deptUsed);
        const deptLabel = escapeHtml(qCheck.dept || 'กลุ่มงานของท่าน');
        Swal.fire({
          icon: 'warning',
          title: 'เกินโควตารายเดือนของกลุ่มงาน / หน่วยงาน',
          html: `กลุ่มงาน <b>${deptLabel}</b> ถูกจำกัดโควตาไม่เกิน <b>${qCheck.deptLimit.toLocaleString()} ${item.unit_piece_name}/เดือน</b><br>ในเดือนนี้กลุ่มงานขอเบิก/อยู่ในตะกร้าแล้วรวม <b>${qCheck.deptUsed.toLocaleString()} ${item.unit_piece_name}</b><br>คงเหลือโควตากลุ่มงานที่ขอได้อีก <b>${dRem.toLocaleString()} ${item.unit_piece_name}</b>`,
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'เข้าใจแล้ว'
        });
        return;
      }

      const existing = cart.find(c => c.itemId === itemId);
      if (existing) {
        existing.qtyBoxes += qtyBoxes;
        existing.qtyPieces += qtyPieces;
        existing.totalPieces += totalPieces;
      } else {
        cart.push({
          itemId: item.id,
          name: item.name,
          unitBox: item.unit_box_name,
          unitPiece: item.unit_piece_name,
          qtyBoxes: qtyBoxes,
          qtyPieces: qtyPieces,
          totalPieces: totalPieces,
          is_multi: item.is_multi_unit
        });
      }

      if (boxInput) boxInput.value = '';
      if (pieceInput) pieceInput.value = '';
      updateCartBadge();
      renderCartDrawer();
      toggleCartDrawer(true);

      Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 1800,
        timerProgressBar: true
      }).fire({
        icon: 'success',
        title: `เพิ่ม "${item.name}" ใส่ตะกร้าแล้ว`
      });
    }

    function updateCartBadge() {
      document.getElementById('cartCount').innerText = cart.length;
      renderCatalog();
    }

    function toggleCartDrawer(forceOpen) {
      const overlay = document.getElementById('cartOverlay');
      if (forceOpen === true) overlay.classList.add('open');
      else if (forceOpen === false) overlay.classList.remove('open');
      else overlay.classList.toggle('open');
    }

    function renderCartDrawer() {
      const list = document.getElementById('cartItemsList');
      if (cart.length === 0) {
        list.innerHTML = `<div style="text-align: center; padding: 3rem 1rem; color: var(--neutral-400);"><p>ยังไม่มีรายการพัสดุในตะกร้า</p></div>`;
        return;
      }

      list.innerHTML = cart.map((c, idx) => {
        const safeName = escapeHtml(c.name);
        const safeBox = escapeHtml(c.unitBox);
        const safePiece = escapeHtml(c.unitPiece);
        let qtyText = c.qtyBoxes > 0 && c.qtyPieces > 0 ? 
          `${c.qtyBoxes} ${safeBox} + ${c.qtyPieces} ${safePiece} (รวม ${c.totalPieces.toLocaleString()} ${safePiece})` :
          (c.qtyBoxes > 0 ? `${c.qtyBoxes} ${safeBox} (รวม ${c.totalPieces.toLocaleString()} ${safePiece})` : `${c.qtyPieces} ${safePiece}`);

        return `
          <div class="cart-item-card">
            <div class="cart-item-details">
              <h4>${safeName}</h4>
              <div class="cart-item-qty">จำนวนที่ขอเบิก: <strong>${qtyText}</strong></div>
            </div>
            <button class="cart-item-remove" onclick="removeCartItem(${idx})" title="ลบออก">${vIcons.trash}</button>
          </div>
        `;
      }).join('');
    }

    function removeCartItem(idx) {
      const removed = cart[idx];
      cart.splice(idx, 1);
      updateCartBadge();
      renderCartDrawer();
      if (removed) {
        Swal.mixin({
          toast: true,
          position: 'top-end',
          showConfirmButton: false,
          timer: 1800,
          timerProgressBar: true
        }).fire({
          icon: 'info',
          title: `ลบ "${removed.name}" ออกจากตะกร้าแล้ว`
        });
      }
    }

    function submitRequisition() {
      const currentUser = getLoggedInRequester();
      if (!currentUser) {
        Swal.fire({
          icon: 'warning',
          title: 'กรุณาเข้าสู่ระบบ',
          text: 'กรุณาเข้าสู่ระบบก่อนทำรายการขอเบิกพัสดุครับ',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        });
        checkRequesterAuth();
        return;
      }

      const dept = document.getElementById('deptSelect').value || currentUser.dept;
      const requester = document.getElementById('requesterName').value.trim() || currentUser.name;
      const phone = document.getElementById('requesterPhone').value.trim() || currentUser.phone || '';
      const purpose = document.getElementById('cartPurpose').value.trim();

      if (!dept) {
        Swal.fire({
          icon: 'warning',
          title: 'ข้อมูลไม่ครบถ้วน',
          text: 'กรุณาเลือกหน่วยงาน / คณะ / โรงเรียนที่สังกัดครับ',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        });
        return;
      }
      if (!requester) {
        Swal.fire({
          icon: 'warning',
          title: 'ข้อมูลไม่ครบถ้วน',
          text: 'กรุณากรอกชื่อ-นามสกุล ผู้ขอเบิกครับ',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        });
        return;
      }
      if (cart.length === 0) {
        Swal.fire({
          icon: 'warning',
          title: 'ไม่มีรายการในตะกร้า',
          text: 'กรุณาเลือกรายการพัสดุและระบุจำนวนก่อนส่งคำขอครับ',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        });
        return;
      }
      if (!purpose) {
        Swal.fire({
          icon: 'warning',
          title: 'ระบุวัตถุประสงค์',
          text: 'กรุณาระบุวัตถุประสงค์ในการเบิกใช้งานพัสดุครับ',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        });
        return;
      }

      Swal.fire({
        title: 'ยืนยันส่งคำขอเบิกพัสดุ?',
        html: `
          <div style="text-align: left; font-size: 0.95rem; margin-top: 0.5rem; color: #475569; line-height: 1.6;">
            <p><strong>หน่วยงาน:</strong> ${dept}</p>
            <p><strong>ผู้ขอเบิก:</strong> ${requester} ${phone ? `(${phone})` : ''}</p>
            <p><strong>จำนวนพัสดุ:</strong> ${cart.length} รายการ</p>
            <p><strong>วัตถุประสงค์:</strong> ${purpose}</p>
          </div>
        `,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#059669',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ยืนยันส่งคำขอ',
        cancelButtonText: 'ยกเลิก'
      }).then(async (result) => {
        if (result.isConfirmed) {
          const nowObj = new Date();
          const beYear = nowObj.getFullYear() + 543;
          const beMonth = String(nowObj.getMonth() + 1).padStart(2, '0');
          const randomNo = Math.floor(1000 + Math.random() * 9000);
          const newDocNo = `REQ-${beYear}${beMonth}-${randomNo}`;

          const nowIso = nowObj.toISOString();
          const newReq = {
            id: newDocNo,
            dept: dept,
            requester: requester,
            phone: phone,
            purpose: purpose,
            date: getThaiDatetime(),
            status: "PENDING",
            signature: null,
            reject_reason: "",
            completed_at: null,
            completed_date: "",
            rejected_at: null,
            rejected_date: "",
            created_at: nowIso,
            updated_at: nowIso,
            items: cart.map(c => ({
              itemId: c.itemId,
              name: c.name,
              qtyBoxes: c.qtyBoxes,
              qtyPieces: c.qtyPieces,
              totalPieces: c.totalPieces,
              unitBox: c.unitBox,
              unitPiece: c.unitPiece,
              approvedPieces: c.totalPieces
            }))
          };

          const apiRes = await postToMySQLAPI('createRequisition', newReq);
          if (apiRes && apiRes.status === 'error') {
            Swal.fire({
              icon: 'error',
              title: 'ส่งคำขอเบิกไม่สำเร็จ',
              text: apiRes.message || 'ไม่สามารถบันทึกคำขอเข้าสู่ระบบได้ กรุณาตรวจสอบข้อมูลหรือโควตาคงเหลือ',
              confirmButtonColor: '#1e40af',
              confirmButtonText: 'ตกลง'
            });
            return;
          }

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

          Swal.fire({
            icon: 'success',
            title: 'ส่งคำขอเบิกพัสดุสำเร็จ!',
            html: `
              <div style="margin: 0.75rem 0;">
                <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 0.5rem;">เลขที่เอกสารคำขอเบิกของคุณ:</p>
                <div style="font-size: 1.6rem; font-weight: 700; color: #1e40af; background: #eff6ff; padding: 0.75rem 1rem; border-radius: 8px; border: 1px dashed #bfdbfe; letter-spacing: 1px;">
                  ${newDocNo}
                </div>
                <p style="font-size: 0.85rem; color: #475569; margin-top: 0.85rem; line-height: 1.6;">
                  คำขอของท่านเข้าสู่สถานะ <b>"รออนุมัติ"</b> และถูกส่งต่อไปยังเจ้าหน้าที่แผนกพัสดุเรียบร้อยแล้ว<br>
                  เมื่อเจ้าหน้าที่อนุมัติ ท่านสามารถเดินทางไปรับพัสดุได้ที่ห้องคลังพัสดุ
                </p>
              </div>
            `,
            showCancelButton: true,
            confirmButtonColor: '#1e40af',
            cancelButtonColor: '#64748b',
            confirmButtonText: 'ดูในรายการคำขอของฉัน',
            cancelButtonText: 'ตกลง / เบิกรายการอื่นต่อ'
          }).then((res) => {
            if (res.isConfirmed) {
              openMyRequisitionsModal();
            }
          });
        }
      });
    }

    function closeSuccessModal() {
      document.getElementById('successModal').classList.remove('open');
      renderCatalog();
    }

    // My Requisitions Modal Logic
    let myReqsFilterStatus = 'ALL';

    function openMyRequisitionsModal() {
      const modal = document.getElementById('myRequisitionsModal');
      modal.classList.add('open');
      renderMyRequisitionsModal();
    }

    function closeMyRequisitionsModal() {
      const modal = document.getElementById('myRequisitionsModal');
      modal.classList.remove('open');
    }

    function filterMyReqsTab(status, btn) {
      myReqsFilterStatus = status;
      document.querySelectorAll('.req-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderMyRequisitionsModal();
    }

    function handleMyReqsSearch() {
      renderMyRequisitionsModal();
    }

    function updateMyReqsBadge() {
      const reqs = getReqsDB();
      const currentUser = getLoggedInRequester();
      const currentName = currentUser ? (currentUser.name || '').trim().toLowerCase() : '';
      const userReqs = currentName ? reqs.filter(r => (r.requester || '').trim().toLowerCase() === currentName) : reqs;
      const badge = document.getElementById('myReqsBadge');
      if (badge) {
        badge.innerText = userReqs.length;
      }
    }

    function copyDocNumber(docNo) {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(docNo);
      } else {
        const temp = document.createElement('input');
        temp.value = docNo;
        document.body.appendChild(temp);
        temp.select();
        document.execCommand('copy');
        document.body.removeChild(temp);
      }
      Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 1800,
        timerProgressBar: true
      }).fire({
        icon: 'success',
        title: `คัดลอกเลขที่เอกสาร ${docNo} แล้ว`
      });
    }

    function renderMyRequisitionsModal() {
      const listEl = document.getElementById('myRequisitionsList');
      const countEl = document.getElementById('myReqsModalCount');
      const searchVal = (document.getElementById('myReqsSearchInput')?.value || '').trim().toLowerCase();
      const monthVal = document.getElementById('myReqsMonthSelect')?.value || 'ALL';
      
      const reqs = getReqsDB();
      const currentUser = getLoggedInRequester();
      const currentName = currentUser ? (currentUser.name || '').trim().toLowerCase() : '';

      // Only display requisitions requested by the currently authenticated user
      const userReqs = currentName ? reqs.filter(r => (r.requester || '').trim().toLowerCase() === currentName) : reqs;

      let filtered = userReqs.filter(r => {
        if (myReqsFilterStatus !== 'ALL' && r.status !== myReqsFilterStatus) return false;
        if (monthVal !== 'ALL') {
          try {
            const parts = monthVal.split('-');
            const beYear = parseInt(parts[0], 10) + 543;
            const beMonth = parts[1];
            const bePattern = `REQ-${beYear}${beMonth}`;
            const matchesBeId = (r.id || '').startsWith(bePattern);
            const matchesCreatedAt = (r.created_at || '').startsWith(monthVal);
            if (!matchesBeId && !matchesCreatedAt) return false;
          } catch (e) {}
        }
        if (searchVal) {
          const matchId = (r.id || '').toLowerCase().includes(searchVal);
          const matchName = (r.requester || '').toLowerCase().includes(searchVal);
          const matchDept = (r.dept || '').toLowerCase().includes(searchVal);
          const matchPurpose = (r.purpose || '').toLowerCase().includes(searchVal);
          const matchItem = (r.items || []).some(it => (it.name || '').toLowerCase().includes(searchVal));
          return matchId || matchName || matchDept || matchPurpose || matchItem;
        }
        return true;
      });

      if (countEl) {
        countEl.innerText = `(พบ ${filtered.length} จาก ${userReqs.length} รายการ)`;
      }

      if (filtered.length === 0) {
        listEl.innerHTML = `
          <div style="text-align: center; padding: 3rem 1rem; color: var(--neutral-400);">
            <div style="margin-bottom: 0.75rem; color: var(--neutral-300);">
              ${vIcons.clipboard}
            </div>
            <h4 style="font-size: 1.05rem; font-weight: 600; color: var(--neutral-600); margin-bottom: 0.25rem;">
              ไม่พบรายการคำขอเบิกพัสดุ
            </h4>
            <p style="font-size: 0.85rem; color: var(--neutral-400); max-width: 360px; margin: 0 auto 1.25rem auto;">
              ${searchVal || myReqsFilterStatus !== 'ALL' || monthVal !== 'ALL' ? 'ลองเปลี่ยนคำค้นหาหรือตัวกรองเดือน/สถานะ' : 'คุณยังไม่มีประวัติการส่งคำขอเบิกพัสดุในระบบ'}
            </p>
            ${!searchVal && myReqsFilterStatus === 'ALL' && monthVal === 'ALL' ? `
              <button class="btn btn-primary" onclick="closeMyRequisitionsModal()">
                ${vIcons.cart} ไปที่แคตตาล็อกเลือกเบิกพัสดุ
              </button>
            ` : ''}
          </div>
        `;
        return;
      }

      listEl.innerHTML = filtered.map(req => {
        let statusBadge = '';
        let borderClass = 'status-border-pending';

        if (req.status === 'PENDING') {
          statusBadge = `<span class="req-status-pill pill-pending">${vIcons.clock} รอคัดกรอง</span>`;
          borderClass = 'status-border-pending';
        } else if (req.status === 'VERIFIED') {
          statusBadge = `<span class="req-status-pill pill-verified">${vIcons.clock} ผ่านการคัดกรอง (รอหัวหน้าอนุมัติ)</span>`;
          borderClass = 'status-border-verified';
        } else if (req.status === 'APPROVED') {
          statusBadge = `<span class="req-status-pill pill-approved">${vIcons.check} อนุมัติแล้ว (รอรับพัสดุ)</span>`;
          borderClass = 'status-border-approved';
        } else if (req.status === 'COMPLETED') {
          statusBadge = `<span class="req-status-pill pill-completed">${vIcons.check} รับมอบสำเร็จแล้ว</span>`;
          borderClass = 'status-border-completed';
        } else if (req.status === 'REJECTED') {
          statusBadge = `<span class="req-status-pill pill-rejected">${vIcons.x} ไม่อนุมัติ</span>`;
          borderClass = 'status-border-rejected';
        }

        const itemsRows = (req.items || []).map(it => {
          const safeName = escapeHtml(it.name);
          const safeBox = escapeHtml(it.unitBox);
          const safePiece = escapeHtml(it.unitPiece);
          let reqQty = it.qtyBoxes > 0 && it.qtyPieces > 0 ?
            it.qtyBoxes + ' ' + safeBox + ' + ' + it.qtyPieces + ' ' + safePiece :
            (it.qtyBoxes > 0 ? it.qtyBoxes + ' ' + safeBox : it.qtyPieces + ' ' + safePiece);
          let appQty = it.approvedPieces !== undefined ? it.approvedPieces.toLocaleString() + ' ' + safePiece : '-';
          let appColor = (req.status === 'APPROVED' || req.status === 'COMPLETED') ? 'var(--accent)' : 'var(--neutral-600)';
          return `
            <tr>
              <td>${safeName}</td>
              <td style="text-align: right; font-weight: 500;">${reqQty}</td>
              <td style="text-align: right; font-weight: 600; color: ${appColor};">${appQty}</td>
            </tr>
          `;
        }).join('');

        let phoneText = req.phone ? ' (' + req.phone + ')' : '';

        return `
          <div class="req-card-item ${borderClass}">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.75rem;">
              <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                <span style="font-weight: 700; font-size: 1.05rem; color: var(--neutral-900); font-family: monospace; letter-spacing: 0.5px;">
                  ${req.id}
                </span>
                <button class="btn btn-outline" style="padding: 2px 7px; font-size: 0.75rem;" onclick="copyDocNumber('${req.id}')" title="คัดลอกเลขที่เอกสาร">
                  ${vIcons.clipboard} คัดลอก
                </button>
                ${statusBadge}
              </div>
              <div style="font-size: 0.8rem; color: var(--neutral-400); display: flex; align-items: center; gap: 4px;">
                ${vIcons.clock} ${req.date}
              </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.6rem; font-size: 0.85rem; color: var(--neutral-700); margin-bottom: 0.75rem; background: var(--neutral-50); padding: 0.75rem; border-radius: 8px;">
              <div>
                <span style="color: var(--neutral-400); font-size: 0.8rem;">ผู้ขอเบิก:</span><br>
                <strong>${escapeHtml(req.requester)}</strong>${escapeHtml(phoneText)}
              </div>
              <div>
                <span style="color: var(--neutral-400); font-size: 0.8rem;">หน่วยงาน:</span><br>
                <span>${escapeHtml(req.dept)}</span>
              </div>
              <div style="grid-column: 1 / -1;">
                <span style="color: var(--neutral-400); font-size: 0.8rem;">วัตถุประสงค์:</span><br>
                <span>${escapeHtml(req.purpose || '-')}</span>
              </div>
              ${(req.verified_by || req.verifiedBy) ? `
              <div style="grid-column: 1 / -1; background: #f0fdf4; color: #166534; padding: 0.4rem 0.6rem; border-radius: 6px; font-size: 0.8rem; display: flex; align-items: center; gap: 6px;">
                ${vIcons.check} <strong>คัดกรองเบื้องต้นโดย:</strong> ${escapeHtml(req.verified_by || req.verifiedBy)} ${(req.verified_date || req.verifiedDate) ? `(${escapeHtml(req.verified_date || req.verifiedDate)})` : ''}
              </div>
              ` : ''}
              ${(req.approved_by || req.approvedBy) ? `
              <div style="grid-column: 1 / -1; background: #eff6ff; color: #1e40af; padding: 0.4rem 0.6rem; border-radius: 6px; font-size: 0.8rem; display: flex; align-items: center; gap: 6px;">
                ${vIcons.shield} <strong>อนุมัติขั้นสุดท้ายโดย:</strong> ${escapeHtml(req.approved_by || req.approvedBy)} ${(req.approved_date || req.approvedDate) ? `(${escapeHtml(req.approved_date || req.approvedDate)})` : ''}
              </div>
              ` : ''}
              ${req.status === 'COMPLETED' && (req.completed_date || req.completedDate) ? `
              <div style="grid-column: 1 / -1; background: #ecfdf5; color: #065f46; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid #a7f3d0; display: flex; align-items: center; gap: 6px;">
                ${vIcons.check} <strong>วันที่จ่ายของ:</strong> ${escapeHtml(req.completed_date || req.completedDate)}
              </div>
              ` : ''}
              ${req.status === 'REJECTED' && (req.reject_reason || req.rejectReason) ? `
              <div style="grid-column: 1 / -1; background: var(--danger-light); color: #991b1b; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid #fecaca;">
                <div style="margin-bottom: 3px;"><strong>เหตุผลที่ไม่อนุมัติ:</strong> ${escapeHtml(req.reject_reason || req.rejectReason)}</div>
                ${(req.rejected_date || req.rejectedDate) ? `
                <div style="font-size: 0.8rem; color: #7f1d1d; display: flex; align-items: center; gap: 4px;">
                  ${vIcons.clock} <strong>วันที่ยกเลิก:</strong> ${escapeHtml(req.rejected_date || req.rejectedDate)}
                </div>
                ` : ''}
              </div>
              ` : ''}
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
                ${itemsRows}
              </tbody>
            </table>

            <div style="margin-top: 0.85rem; display: flex; justify-content: flex-end; gap: 0.5rem; flex-wrap: wrap;">
              <button class="btn btn-primary" style="font-size: 0.8rem; padding: 0.4rem 0.85rem;" onclick="openRequisitionPdf('${req.id}')">
                ${vIcons.file_text} พิมพ์ใบเบิกพัสดุ PDF
              </button>
            </div>
          </div>
        `;
      }).join('');
    }

    // Requisition Official PDF Viewer (Requester Portal)
    function openRequisitionPdf(docNo) {
      const reqs = getReqsDB();
      const req = reqs.find(r => r.id === docNo);
      if (!req) {
        Swal.fire({
          icon: 'error',
          title: 'ไม่พบเอกสาร',
          text: `ไม่พบข้อมูลเอกสารเลขที่ ${docNo}`,
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        });
        return;
      }

      document.getElementById('pdfDocNo').innerText = req.id;
      document.getElementById('pdfDate').innerText = req.date || '21 ตุลาคม 2569';
      document.getElementById('pdfDept').innerText = req.dept;
      document.getElementById('pdfRequester').innerText = req.requester + (req.phone ? ` (โทร ${req.phone})` : '');
      document.getElementById('pdfPurpose').innerText = req.purpose || '-';
      document.getElementById('pdfSigRequester').innerText = req.requester;
      document.getElementById('pdfSigRecipient').innerText = req.requester;

      const reqDateEl = document.getElementById('pdfSigReqDate');
      if (reqDateEl) reqDateEl.innerText = req.date || '-';

      const verifierEl = document.getElementById('pdfSigVerifier');
      const verifiedDateEl = document.getElementById('pdfSigVerifiedDate');
      const verifierStampEl = document.getElementById('pdfSigVerifierStamp');
      const isVerifiedOrLater = ['VERIFIED', 'APPROVED', 'COMPLETED'].includes(req.status);
      if (verifierEl) verifierEl.innerText = req.verified_by || (isVerifiedOrLater ? 'เจ้าหน้าที่พัสดุ สวท.' : '.........................................');
      if (verifiedDateEl) verifiedDateEl.innerText = req.verified_date || req.verified_at || (isVerifiedOrLater ? (req.date || '-') : 'วันที่ ....../....../......');
      if (verifierStampEl) verifierStampEl.innerText = isVerifiedOrLater ? '[ ผ่านการคัดกรอง ]' : '';

      const approverEl = document.getElementById('pdfSigApprover');
      const approvedDateEl = document.getElementById('pdfSigApprovedDate');
      const approverStampEl = document.getElementById('pdfSigApproverStamp');
      const isApprovedOrCompleted = ['APPROVED', 'COMPLETED'].includes(req.status);
      if (approverEl) approverEl.innerText = req.approved_by || (isApprovedOrCompleted ? 'หัวหน้าสำนักงานผู้อำนวยการ สวท.' : '.........................................');
      if (approvedDateEl) approvedDateEl.innerText = req.approved_date || req.approved_at || (isApprovedOrCompleted ? (req.completed_date || req.date || '-') : 'วันที่ ....../....../......');
      if (approverStampEl) approverStampEl.innerText = isApprovedOrCompleted ? '[ อนุมัติขั้นสุดท้าย ]' : '';

      const tbody = document.getElementById('pdfItemsTbody');
      tbody.innerHTML = (req.items || []).map((it, idx) => {
        let reqQty = it.qtyBoxes > 0 && it.qtyPieces > 0 ?
          `${it.qtyBoxes} ${it.unitBox} + ${it.qtyPieces} ${it.unitPiece} (รวม ${it.totalPieces.toLocaleString()} ${it.unitPiece})` :
          (it.qtyBoxes > 0 ? `${it.qtyBoxes} ${it.unitBox} (${it.totalPieces.toLocaleString()} ${it.unitPiece})` : `${it.qtyPieces} ${it.unitPiece}`);
        
        let approvedQty = it.approvedPieces !== undefined ? `${it.approvedPieces.toLocaleString()} ${it.unitPiece}` : (req.status === 'COMPLETED' ? reqQty : '-');

        let noteText = 'รอคัดกรอง';
        if (req.status === 'VERIFIED') noteText = 'ผ่านการคัดกรอง';
        else if (req.status === 'APPROVED') noteText = 'อนุมัติแล้ว';
        else if (req.status === 'COMPLETED') noteText = 'จ่ายพัสดุครบถ้วน';
        else if (req.status === 'REJECTED') noteText = 'ไม่อนุมัติ';

        return `
          <tr>
            <td style="text-align: center;">${idx + 1}</td>
            <td><strong>${it.name}</strong></td>
            <td style="text-align: right;">${reqQty}</td>
            <td style="text-align: right; font-weight: 600; color: ${req.status === 'COMPLETED' ? '#059669' : '#000'};">${approvedQty}</td>
            <td style="text-align: center; font-size: 0.85rem; color: #555;">${noteText}</td>
          </tr>
        `;
      }).join('');

      const sigBox = document.getElementById('pdfSigOfficerBox');
      const recDateEl = document.getElementById('pdfSigReceiveDate');
      const payDate = req.completed_date || req.completedDate || (req.status === 'COMPLETED' ? req.date : '');
      if (req.signature && req.signature.startsWith('data:image')) {
        sigBox.innerHTML = `<img src="${req.signature}" class="sig-img-preview" alt="ลายเซ็นดิจิทัลผู้รับพัสดุ">`;
      } else if (req.status === 'COMPLETED') {
        sigBox.innerHTML = `<div style="font-size: 0.75rem; color: #059669; font-weight: 700; margin-bottom: 6px;">[ รับมอบพัสดุแล้ว ]</div>`;
      } else {
        sigBox.innerHTML = '';
      }
      if (recDateEl) {
        recDateEl.innerText = (req.status === 'COMPLETED' && payDate) ? `วันที่รับของ: ${payDate}` : 'วันที่ ....../....../......';
      }

      const modal = document.getElementById('requisitionPdfModal');
      modal.style.display = 'flex';
      modal.classList.add('open');
    }

    function closeRequisitionPdfModal() {
      const modal = document.getElementById('requisitionPdfModal');
      modal.style.display = 'none';
      modal.classList.remove('open');
    }

    function printRequisitionPdf() {
      const printContent = document.getElementById('printablePdf');
      if (!printContent) {
        window.print();
        return;
      }

      // Create an isolated hidden iframe to guarantee clean A4 printout without blank pages
      let iframe = document.getElementById('pdfPrintIframe');
      if (iframe) {
        iframe.remove();
      }
      iframe = document.createElement('iframe');
      iframe.id = 'pdfPrintIframe';
      iframe.style.position = 'fixed';
      iframe.style.right = '0';
      iframe.style.bottom = '0';
      iframe.style.width = '0';
      iframe.style.height = '0';
      iframe.style.border = 'none';
      iframe.style.visibility = 'hidden';
      document.body.appendChild(iframe);

      const doc = iframe.contentWindow.document;
      doc.open();
      doc.write(`
        <!DOCTYPE html>
        <html lang="th">
        <head>
          <meta charset="UTF-8">
          <title>ใบขอเบิกพัสดุ มหาวิทยาลัยสวนดุสิต</title>
          <link rel="preconnect" href="https://fonts.googleapis.com">
          <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
          <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap" rel="stylesheet">
          <style>
            @page {
              size: A4 portrait;
              margin: 1.2cm 1.5cm;
            }
            * {
              box-sizing: border-box;
              -webkit-print-color-adjust: exact !important;
              print-color-adjust: exact !important;
            }
            body {
              margin: 0;
              padding: 0;
              background: white;
              color: #000;
              font-family: 'Sarabun', sans-serif;
              font-size: 14px;
              line-height: 1.5;
            }
            .pdf-page {
              display: flex;
              flex-direction: column;
              min-height: calc(297mm - 2.5cm);
              width: 100%;
              max-width: 100%;
              margin: 0 auto;
              padding: 0;
              background: white;
              box-sizing: border-box;
            }
            .pdf-header {
              text-align: center;
              margin-bottom: 1.25rem;
              display: flex;
              flex-direction: column;
              align-items: center;
            }
            .pdf-header img {
              height: 70px;
              width: auto;
              object-fit: contain;
              margin-bottom: 0.4rem;
            }
            .pdf-header h2 {
              font-size: 1.35rem;
              font-weight: 700;
              margin: 0 0 0.25rem 0;
            }
            .pdf-header p {
              font-size: 0.9rem;
              color: #444;
              margin: 0;
            }
            .pdf-meta-table {
              width: 100%;
              margin-bottom: 1.25rem;
              border-collapse: collapse;
              font-size: 0.95rem;
            }
            .pdf-meta-table td {
              padding: 4px 0;
              vertical-align: top;
            }
            .pdf-items-table {
              width: 100%;
              border-collapse: collapse;
              margin: 1.25rem 0;
              font-size: 0.92rem;
            }
            .pdf-items-table th, .pdf-items-table td {
              border: 1px solid #333;
              padding: 7px 9px;
            }
            .pdf-items-table th {
              background-color: #f3f4f6 !important;
              font-weight: 600;
              text-align: center;
            }
            .pdf-footer-section {
              margin-top: auto;
              width: 100%;
              page-break-inside: avoid;
              break-inside: avoid;
            }
            .pdf-ack-note {
              font-size: 0.85rem;
              margin-bottom: 0.75rem;
            }
            .pdf-signatures {
              display: grid;
              grid-template-columns: repeat(4, 1fr);
              gap: 0.75rem;
              margin-top: auto;
              text-align: center;
              font-size: 0.82rem;
              page-break-inside: avoid;
              break-inside: avoid;
            }
            .pdf-footer-section .pdf-signatures {
              margin-top: 0.5rem;
            }
            .sig-box {
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: flex-end;
              height: 130px;
            }
            .sig-img-preview {
              max-height: 55px;
              max-width: 130px;
              margin-bottom: 4px;
            }
            .sig-line {
              width: 80%;
              border-bottom: 1px dotted #333;
              margin-bottom: 6px;
            }
          </style>
        </head>
        <body>
          <div class="pdf-page">
            ${printContent.innerHTML}
          </div>
        </body>
        </html>
      `);
      doc.close();

      setTimeout(() => {
        try {
          iframe.contentWindow.focus();
          iframe.contentWindow.print();
        } catch (e) {
          console.warn('Iframe print fallback to window.print():', e);
          window.print();
        }
      }, 250);
    }

    // Requester Authentication State & Handlers
    const AUTH_SESSION_KEY = 'requester_session';

    function getLoggedInRequester() {
      try {
        const raw = localStorage.getItem(AUTH_SESSION_KEY);
        return raw ? JSON.parse(raw) : null;
      } catch (e) {
        return null;
      }
    }

    function checkRequesterAuth(skipBypass = false) {
      let user = getLoggedInRequester();
      const loginScreen = document.getElementById('requesterLoginScreen');
      const appContainer = document.getElementById('requesterApp');
      const wantsLogin = window.location.search.includes('showLogin=1');

      if (!user && AUTH_BYPASS && !skipBypass && !wantsLogin) {
        const users = getUsersDB();
        const defaultTester = users.find(u => (u.username || '').toLowerCase() === 'user') || users[0] || {
          id: 5,
          name: 'ผู้ขอเบิกทดสอบ',
          username: 'user',
          position: 'เจ้าหน้าที่บริการการศึกษา',
          dept: 'สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน',
          phone: '089-123-4567'
        };
        user = {
          id: defaultTester.id,
          name: defaultTester.name,
          username: defaultTester.username || 'user',
          position: defaultTester.position || '',
          dept: defaultTester.dept || '',
          phone: defaultTester.phone || ''
        };
        localStorage.setItem(AUTH_SESSION_KEY, JSON.stringify(user));
      }

      if (!user) {
        if (loginScreen) loginScreen.style.display = 'flex';
        if (appContainer) appContainer.style.display = 'none';
        return false;
      }

      if (loginScreen) loginScreen.style.display = 'none';
      if (appContainer) appContainer.style.display = 'flex';

      const bypassBadge = document.getElementById('requesterAuthBypassBadge');
      const switchBtn = document.getElementById('btnSwitchTestRequester');
      if (bypassBadge) bypassBadge.style.display = AUTH_BYPASS ? 'inline-flex' : 'none';
      if (switchBtn) switchBtn.style.display = AUTH_BYPASS ? 'inline-flex' : 'none';

      applyRequesterSession(user);
      return true;
    }

    function switchTestRequester() {
      const users = getUsersDB();
      if (!users || users.length === 0) return;
      const cur = getLoggedInRequester();
      const opts = users.map(u => {
        const selected = cur && (u.username === cur.username || u.name === cur.name) ? 'selected' : '';
        return `<option value="${escapeHtml(String(u.id))}" ${selected}>${escapeHtml(u.name)} (${escapeHtml(u.dept || '-')})</option>`;
      }).join('');

      Swal.fire({
        title: 'สลับบัญชีผู้ขอเบิก (โหมดทดสอบ)',
        html: `<div style="text-align:left; font-size:0.875rem; color:#475569; margin-bottom:0.5rem;">เลือกบุคลากรเพื่อทดสอบโควตารายเดือนและการส่งคำขอได้ทันทีโดยไม่ต้องกรอกรหัสผ่าน:</div>
               <select id="swalSwitchRequesterSelect" class="form-control" style="width:100%;">${opts}</select>`,
        showCancelButton: true,
        confirmButtonColor: '#1e40af',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'สลับผู้ใช้งาน',
        cancelButtonText: 'ยกเลิก'
      }).then((res) => {
        if (!res.isConfirmed) return;
        const selEl = document.getElementById('swalSwitchRequesterSelect');
        const chosenId = selEl ? selEl.value : '';
        const picked = users.find(u => String(u.id) === String(chosenId));
        if (!picked) return;
        const sessionUser = {
          id: picked.id,
          name: picked.name,
          username: picked.username || '',
          position: picked.position || '',
          dept: picked.dept || '',
          phone: picked.phone || ''
        };
        localStorage.setItem(AUTH_SESSION_KEY, JSON.stringify(sessionUser));
        applyRequesterSession(sessionUser);
        renderCatalog();
        Swal.mixin({ toast: true, position: 'top-end', showConfirmButton: false, timer: 1600 })
          .fire({ icon: 'success', title: `สลับเป็นผู้ขอเบิก: ${picked.name}` });
      });
    }

    function applyRequesterSession(user) {
      const navName = document.getElementById('navRequesterName');
      const navDept = document.getElementById('navRequesterDept');
      const barLabel = document.getElementById('barRequesterLabel');

      if (navName) navName.innerText = user.name || user.username || 'ผู้ขอเบิก';
      if (navDept) navDept.innerText = user.dept ? '(' + user.dept + ')' : '';
      if (barLabel) barLabel.innerText = user.name + ' (' + (user.dept || 'สวท.') + ')';

      const nameInput = document.getElementById('requesterName');
      if (nameInput) {
        nameInput.value = user.name || '';
      }

      const deptSelect = document.getElementById('deptSelect');
      const deptSearchInput = document.getElementById('deptSearchInput');
      if (deptSelect) deptSelect.value = user.dept || '';
      if (deptSearchInput) deptSearchInput.value = user.dept || '';

      const phoneInput = document.getElementById('requesterPhone');
      if (phoneInput && user.phone && !phoneInput.value) {
        phoneInput.value = user.phone;
      }

      updateMyReqsBadge();
    }

    function selectPortalLoginRole(role) {
      const r = String(role || 'REQUESTER').toUpperCase();
      const hiddenEl = document.getElementById('selectedLoginRole');
      if (hiddenEl) hiddenEl.value = r;

      const titleEl = document.getElementById('loginRoleTitle');
      const badgeEl = document.getElementById('loginRoleBadge');
      const unameEl = document.getElementById('loginUsername');
      const btnEl = document.getElementById('btnLoginSubmit');
      const btnTextEl = document.getElementById('btnLoginSubmitText');

      const roleConfigs = {
        REQUESTER: {
          title: 'เข้าสู่ระบบผู้ขอเบิกพัสดุ',
          badgeText: 'สำหรับบุคลากรและอาจารย์ สวท. (เลือกเบิกพัสดุและติดตามสถานะ)',
          badgeBg: '#eff6ff',
          badgeColor: '#1e40af',
          badgeBorder: '#bfdbfe',
          placeholder: 'กรอกชื่อผู้ใช้งานผู้ขอเบิก',
          btnText: 'เข้าสู่ระบบผู้ขอเบิกพัสดุ',
          btnBg: '#1e40af'
        },
        STAFF: {
          title: 'เข้าสู่ระบบเจ้าหน้าที่พัสดุ',
          badgeText: 'สำหรับเจ้าหน้าที่พัสดุ (คัดกรองคำขอ, รับของเข้าคลัง และจ่ายพัสดุ)',
          badgeBg: '#ecfdf5',
          badgeColor: '#047857',
          badgeBorder: '#a7f3d0',
          placeholder: 'กรอกชื่อผู้ใช้งานเจ้าหน้าที่พัสดุ',
          btnText: 'เข้าสู่ระบบเจ้าหน้าที่พัสดุ',
          btnBg: '#059669'
        },
        HEAD: {
          title: 'เข้าสู่ระบบหัวหน้าหน่วยงาน',
          badgeText: 'สำหรับหัวหน้าหน่วยงาน (อนุมัติคำขอขั้นสุดท้าย Approve และดูรายงาน)',
          badgeBg: '#f5f3ff',
          badgeColor: '#6d28d9',
          badgeBorder: '#ddd6fe',
          placeholder: 'กรอกชื่อผู้ใช้งานหัวหน้าหน่วยงาน',
          btnText: 'เข้าสู่ระบบหัวหน้าผู้อนุมัติ',
          btnBg: '#4f46e5'
        },
        ADMIN: {
          title: 'เข้าสู่ระบบผู้ดูแลระบบสูงสุด',
          badgeText: 'สำหรับผู้ดูแลระบบ (บริหารจัดการคลัง บุคลากร กลุ่มงาน และทุกสิทธิ์)',
          badgeBg: '#f1f5f9',
          badgeColor: '#0f172a',
          badgeBorder: '#cbd5e1',
          placeholder: 'กรอกชื่อผู้ใช้งานผู้ดูแลระบบ',
          btnText: 'เข้าสู่ระบบผู้ดูแลระบบสูงสุด',
          btnBg: '#0f172a'
        }
      };

      const cfg = roleConfigs[r] || roleConfigs.REQUESTER;
      if (titleEl) titleEl.innerText = cfg.title;
      if (badgeEl) {
        badgeEl.style.background = cfg.badgeBg;
        badgeEl.style.color = cfg.badgeColor;
        badgeEl.style.borderColor = cfg.badgeBorder;
        badgeEl.innerHTML = `<svg class="svg-icon" style="width: 14px; height: 14px;" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/></svg><span>${cfg.badgeText}</span>`;
      }
      if (unameEl) unameEl.placeholder = cfg.placeholder;
      if (btnEl) btnEl.style.background = cfg.btnBg;
      if (btnTextEl) btnTextEl.innerText = cfg.btnText;

      document.querySelectorAll('#portalRoleTabs .role-tab-btn').forEach(btn => {
        const bRole = btn.getAttribute('data-role');
        if (bRole === r) {
          btn.classList.add('active');
          btn.style.border = `2px solid ${cfg.btnBg}`;
          btn.style.background = cfg.badgeBg;
          btn.style.color = cfg.badgeColor;
        } else {
          btn.classList.remove('active');
          btn.style.border = '1px solid #cbd5e1';
          btn.style.background = 'white';
          btn.style.color = '#334155';
        }
      });
    }

    async function handleRequesterLogin(e) {
      if (e && e.preventDefault) e.preventDefault();
      const unameEl = document.getElementById('loginUsername');
      const passEl = document.getElementById('loginPassword');
      const selectedRole = (document.getElementById('selectedLoginRole')?.value || 'REQUESTER').toUpperCase();
      const username = (unameEl ? unameEl.value : '').trim();
      const password = (passEl ? passEl.value : '').trim();

      if (!username || !password) {
        Swal.fire({
          icon: 'warning',
          title: 'กรุณากรอกข้อมูลให้ครบ',
          text: 'กรุณาระบุชื่อผู้ใช้งานและรหัสผ่าน',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        });
        return;
      }

      // If user selected STAFF, HEAD, or ADMIN on the login screen -> authenticate via loginStaff and redirect to staff.html
      if (['STAFF', 'HEAD', 'ADMIN'].includes(selectedRole)) {
        let staffRes = await postToMySQLAPI('loginStaff', { username, password, requested_role: selectedRole });
        if (!staffRes) {
          const uLow = username.toLowerCase();
          let resolved = null;
          let dispName = username;
          if (['admin_staff', 'admin'].includes(uLow) && password === 'sdu1234') {
            resolved = 'ADMIN';
            dispName = 'ผู้ดูแลระบบคลังพัสดุ';
          } else if (['staff', 'warehouse_staff', 'screener'].includes(uLow) && password === 'sdu1234') {
            resolved = 'STAFF';
            dispName = 'เจ้าหน้าที่พัสดุ สวท. (ผู้คัดกรอง)';
          } else if (['head', 'head_approver', 'approver', 'director', 'wasana.c', 'jeerawan.b', 'patcharaporn.k', 'sineenart.l'].includes(uLow) && password === 'sdu1234') {
            resolved = 'HEAD';
            dispName = 'หัวหน้าหน่วยงาน สวท. (ผู้อนุมัติ)';
          } else {
            const localUsers = getUsersDB();
            const foundUser = localUsers.find(u => (u.username && u.username.toLowerCase() === uLow) || (u.name && u.name.toLowerCase() === uLow));
            const validPass = foundUser ? (foundUser.password || 'sdu1234') : '';
            if (foundUser && (password === validPass || password === 'sdu1234')) {
              const uRole = String(foundUser.role || 'REQUESTER').toUpperCase();
              if (['ADMIN', 'HEAD', 'STAFF'].includes(uRole)) {
                resolved = uRole;
                dispName = foundUser.name || username;
              } else {
                staffRes = { status: 'error', message: `บัญชี '${username}' มีสิทธิ์เป็น REQUESTER กรุณาเลือกแท็บ 'ผู้ขอเบิกพัสดุ' เพื่อเข้าสู่ระบบ` };
              }
            }
          }
          if (!staffRes && resolved) {
            if (resolved !== 'ADMIN' && resolved !== selectedRole) {
              staffRes = { status: 'error', message: `บัญชี '${username}' มีสิทธิ์เป็น ${resolved} กรุณาเลือกแท็บบทบาทให้ตรงกับสิทธิ์ของท่าน` };
            } else {
              staffRes = { status: 'success', token: `${username}.${Math.floor(Date.now()/1000)}.offline`, username, name: dispName, role: resolved, active_role: selectedRole };
            }
          } else if (!staffRes) {
            staffRes = { status: 'error', message: 'ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้องสำหรับบทบาทที่เลือก' };
          }
        }
        if (staffRes && staffRes.status === 'success') {
          const finalRole = (staffRes.role || selectedRole).toUpperCase();
          const activeRole = (staffRes.active_role || selectedRole).toUpperCase();
          sessionStorage.setItem('staff_auth', 'true');
          sessionStorage.setItem('staff_token', staffRes.token || '');
          sessionStorage.setItem('staff_username', staffRes.username || username);
          sessionStorage.setItem('staff_name', staffRes.name || username);
          sessionStorage.setItem('staff_role', finalRole);
          sessionStorage.setItem('staff_active_role', activeRole);
          window.location.href = 'staff.html';
          return;
        } else {
          Swal.fire({
            icon: 'error',
            title: 'เข้าสู่ระบบไม่สำเร็จ',
            text: (staffRes && staffRes.message) || 'ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้องสำหรับบทบาทที่เลือก',
            confirmButtonColor: '#1e40af',
            confirmButtonText: 'ลองใหม่อีกครั้ง'
          });
          return;
        }
      }

      // 1. Try MySQL/Postgres REST API for REQUESTER
      let loginResult = await postToMySQLAPI('loginRequester', { username, password });

      // 2. Fallback to localStorage users DB
      if (!loginResult || loginResult.status !== 'success') {
        const users = getUsersDB();
        const cleanUname = username.toLowerCase();
        const found = users.find(u =>
          (u.username && u.username.toLowerCase() === cleanUname) ||
          (u.name && u.name.toLowerCase() === cleanUname)
        );
        if (found) {
          const validPass = found.password || 'password123';
          if (password === validPass || password === 'sdu1234') {
            loginResult = {
              status: 'success',
              user: {
                id: found.id,
                name: found.name,
                username: found.username || username,
                position: found.position || '',
                dept: found.dept || '',
                phone: found.phone || ''
              }
            };
          }
        }
      }

      if (loginResult && loginResult.status === 'success') {
        localStorage.setItem(AUTH_SESSION_KEY, JSON.stringify(loginResult.user));
        Swal.fire({
          icon: 'success',
          title: 'เข้าสู่ระบบสำเร็จ',
          text: 'ยินดีต้อนรับ ' + loginResult.user.name,
          timer: 1500,
          showConfirmButton: false
        });
        checkRequesterAuth();
        renderCatalog();
      } else {
        Swal.fire({
          icon: 'error',
          title: 'เข้าสู่ระบบไม่สำเร็จ',
          text: (loginResult && loginResult.message) || 'ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง หรือยังไม่ได้เปิดใช้งานบัญชี กรุณาติดต่อเจ้าหน้าที่พัสดุ',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ลองใหม่อีกครั้ง'
        });
      }
    }

    function logoutRequester() {
      Swal.fire({
        title: 'ยืนยันออกจากระบบ?',
        text: 'ต้องการออกจากระบบขอเบิกพัสดุใช่หรือไม่',
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ออกจากระบบ',
        cancelButtonText: 'ยกเลิก'
      }).then((res) => {
        if (res.isConfirmed) {
          localStorage.removeItem(AUTH_SESSION_KEY);
          if (AUTH_BYPASS) {
            checkRequesterAuth(true);
          } else {
            location.reload();
          }
        }
      });
    }

    // Initial Load
    document.addEventListener('DOMContentLoaded', () => {
      getDeptsDB();
      getUsersDB();
      getItemsDB();
      getReqsDB();
      try {
        const params = new URLSearchParams(window.location.search);
        const roleParam = (params.get('role') || '').toUpperCase();
        if (['REQUESTER', 'STAFF', 'HEAD', 'ADMIN'].includes(roleParam)) {
          if (roleParam !== 'REQUESTER') {
            localStorage.removeItem(AUTH_SESSION_KEY);
          }
          selectPortalLoginRole(roleParam);
        }
      } catch (e) {}
      const isAuth = checkRequesterAuth();
      if (isAuth) {
        renderCatalog();
        updateMyReqsBadge();
      }
      syncFromMySQLAPI();
    });

__SEARCHABLE_SELECT_JS__

    // Real-time synchronization across tabs/windows
    window.addEventListener('storage', (e) => {
      if (e.key === DB_REQS_KEY || e.key === DB_ITEMS_KEY || e.key === DB_QUOTAS_KEY) {
        updateMyReqsBadge();
        renderCatalog();
        const myReqModal = document.getElementById('myRequisitionsModal');
        if (myReqModal && myReqModal.classList.contains('open')) {
          renderMyRequisitionsModal();
        }
      }
      if (e.key === DB_USERS_KEY) {
        const userDd = document.getElementById('userDropdownList');
        if (userDd && userDd.classList.contains('open')) {
          renderUserDropdown(document.getElementById('requesterName').value);
        }
      }
      if (e.key === DB_DEPTS_KEY) {
        const deptDd = document.getElementById('deptDropdownList');
        if (deptDd && deptDd.classList.contains('open')) {
          renderDeptDropdown(document.getElementById('deptSearchInput').value);
        }
      }
    });
  </script>
</body>
</html>
'''

requester_html = (
    requester_template
    .replace('__SYSTEM_VERSION__', SYSTEM_VERSION)
    .replace('__AUTH_BYPASS__', 'true' if AUTH_BYPASS else 'false')
    .replace('__SEARCHABLE_SELECT_CSS__', SEARCHABLE_SELECT_CSS)
    .replace('__SEARCHABLE_SELECT_JS__', SEARCHABLE_SELECT_JS)
    .replace('__DEFAULT_ITEMS__', json.dumps(initial_items, ensure_ascii=False))
    .replace('__DEFAULT_REQS__', json.dumps(initial_requisitions, ensure_ascii=False))
    .replace('__DEFAULT_DEPTS__', dept_json_str)
    .replace('__DEFAULT_USERS__', users_json_str)
)

with open(os.path.join(PROJECT_ROOT, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(requester_html)

print("Created index.html (Requester Only Portal)")


# --------------------------------------------------------------------
# 2. STAFF TEMPLATE (staff.html)
# --------------------------------------------------------------------
staff_template = r'''<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ระบบบริหารคลังพัสดุ | มหาวิทยาลัยสวนดุสิต</title>
  
  <!-- PWA & Mobile Icons -->
  <meta name="theme-color" content="#1e40af">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="คลังพัสดุ มสด.">
  <!-- University Brand Logo Tab Favicon -->
  <link rel="icon" type="image/png" href="assets/logo_sdu.png">
  <link rel="shortcut icon" type="image/x-icon" href="favicon.ico">
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

    function escapeHtml(str) {
      if (str === null || str === undefined) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }

    function getThaiDatetime(dateObj = new Date()) {
      const thaiMonths = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];
      const day = dateObj.getDate();
      const month = thaiMonths[dateObj.getMonth()];
      const thaiYear = dateObj.getFullYear() + 543;
      const hours = String(dateObj.getHours()).padStart(2, '0');
      const minutes = String(dateObj.getMinutes()).padStart(2, '0');
      return `${day} ${month} ${thaiYear} ${hours}:${minutes} น.`;
    }

    function formatThaiDatetime(dateObj = new Date()) {
      return getThaiDatetime(dateObj);
    }

    if (typeof Swal === 'undefined') {
      document.write('<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"><\/script>');
    }
  </script>
  
  <style>

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
    .pdf-page { background: white; width: 100%; max-width: 800px; min-height: 1050px; display: flex; flex-direction: column; box-sizing: border-box; padding: 2.8rem 3.2rem; box-shadow: 0 10px 25px rgba(0,0,0,0.3); font-family: 'Sarabun', sans-serif; color: #000; line-height: 1.6; }
    .pdf-header { text-align: center; margin-bottom: 1.75rem; position: relative; display: flex; flex-direction: column; align-items: center; }
    .pdf-header h2 { font-size: 1.35rem; font-weight: 700; margin-bottom: 0.25rem; }
    .pdf-header p { font-size: 0.9rem; color: #444; }
    .pdf-meta-table { width: 100%; margin-bottom: 1.25rem; font-size: 0.95rem; }
    .pdf-meta-table td { padding: 4px 0; }
    .pdf-items-table { width: 100%; border-collapse: collapse; margin: 1.25rem 0; font-size: 0.95rem; }
    .pdf-items-table th, .pdf-items-table td { border: 1px solid #333; padding: 8px 10px; }
    .pdf-items-table th { background: #f3f4f6; font-weight: 600; text-align: center; }
    .pdf-footer-section { margin-top: auto; width: 100%; page-break-inside: avoid; break-inside: avoid; }
    .pdf-ack-note { font-size: 0.85rem; margin-bottom: 0.75rem; }
    .pdf-signatures { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; margin-top: auto; text-align: center; font-size: 0.825rem; page-break-inside: avoid; break-inside: avoid; }
    .pdf-footer-section .pdf-signatures { margin-top: 0.75rem; }
    .sig-box { display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 140px; }
    .sig-img-preview { max-height: 60px; max-width: 130px; margin-bottom: 4px; }
    .sig-line { width: 80%; border-bottom: 1px dotted #333; margin-bottom: 6px; }

    /* Clean Print Isolation - Only the A4 document prints */
    @media print {
      @page {
        size: A4 portrait;
        margin: 1.2cm 1.5cm;
      }
      html, body {
        width: 100% !important;
        height: auto !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: visible !important;
        background: white !important;
      }
      header, footer, nav, .nav-container, .btn, .close-btn,
      .modal-header, .modal-footer, .pdf-preview-actions,
      .dashboard-header, .sidebar, .sidebar-overlay, .tab-nav {
        display: none !important;
      }
      .pdf-preview-container {
        padding: 0 !important;
        background: white !important;
      }
      #printablePdf {
        position: static !important;
        width: 100% !important;
        max-width: 100% !important;
        min-height: calc(297mm - 2.5cm) !important;
        display: flex !important;
        flex-direction: column !important;
        box-sizing: border-box !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
        background: white !important;
        visibility: visible !important;
      }
      #printablePdf * {
        visibility: visible !important;
      }
      .pdf-footer-section {
        margin-top: auto !important;
        width: 100% !important;
        page-break-inside: avoid !important;
        break-inside: avoid !important;
      }
      .pdf-signatures {
        margin-top: auto !important;
        page-break-inside: avoid !important;
        break-inside: avoid !important;
      }
      .pdf-footer-section .pdf-signatures {
        margin-top: 0.5rem !important;
      }
    }


__SEARCHABLE_SELECT_CSS__

    /* Staff Specific Styles */
    .dashboard-header {
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem;
    }
    .dashboard-header h2 { font-size: 1.35rem; font-weight: 700; color: var(--neutral-900); }

    .status-tabs { display: flex; gap: 0.5rem; background: var(--neutral-100); padding: 4px; border-radius: 8px; }
    .status-tab {
      padding: 0.45rem 1rem; border: none; background: transparent; font-family: inherit;
      font-size: 0.85rem; font-weight: 500; color: var(--neutral-600); border-radius: 6px;
      cursor: pointer; display: flex; align-items: center; gap: 0.4rem;
    }
    .status-tab.active { background: white; color: var(--primary); font-weight: 600; box-shadow: var(--shadow-sm); }
    .count-tag { font-size: 0.7rem; padding: 1px 6px; border-radius: 999px; background: var(--neutral-200); color: var(--neutral-700); }
    .status-tab.active .count-tag { background: var(--primary-light); color: var(--primary); }

    .requisition-card {
      background: white; border: 1px solid var(--neutral-200); border-radius: var(--radius);
      padding: 1.25rem 1.5rem; margin-bottom: 1rem; box-shadow: var(--shadow-sm);
      display: flex; flex-direction: column; gap: 1rem; transition: border-color 0.2s;
    }
    .requisition-card:hover { border-color: var(--neutral-300); }
    .req-top-row { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem; }
    .req-doc-id { font-size: 1.05rem; font-weight: 700; color: var(--primary); display: flex; align-items: center; gap: 0.5rem; }
    .req-badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
    .badge-pending { background: var(--warning-light); color: var(--warning); }
    .badge-verified { background: #e0f2fe; color: #0369a1; }
    .badge-approved { background: #e0e7ff; color: #4338ca; }
    .badge-completed { background: #dcfce7; color: #15803d; }
    .badge-rejected { background: var(--danger-light); color: var(--danger); }

    .req-details-grid {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 0.75rem; font-size: 0.85rem; color: var(--neutral-600);
    }
    .req-details-grid div { display: flex; align-items: center; gap: 0.4rem; }
    .req-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; margin: 0.5rem 0; }
    .req-table th { background: var(--neutral-100); text-align: left; padding: 0.5rem 0.75rem; font-weight: 600; color: var(--neutral-700); border-bottom: 1px solid var(--neutral-200); }
    .req-table td { padding: 0.5rem 0.75rem; border-bottom: 1px solid var(--neutral-100); }
    .req-actions { display: flex; justify-content: flex-end; gap: 0.75rem; flex-wrap: wrap; padding-top: 0.5rem; border-top: 1px solid var(--neutral-100); }

    /* Navigation tabs */
    .view-switcher { display: flex; background: var(--neutral-100); padding: 4px; border-radius: 10px; gap: 4px; }
    .view-btn {
      padding: 0.5rem 1rem; border: none; background: transparent; font-family: inherit;
      font-size: 0.875rem; font-weight: 500; color: var(--neutral-600); border-radius: 8px;
      cursor: pointer; display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s ease;
    }
    .view-btn:hover { color: var(--neutral-900); }
    .view-btn.active { background: white; color: var(--primary); font-weight: 600; box-shadow: var(--shadow-sm); }

    .view-content { display: none; }
    .view-content.active { display: block; animation: fadeIn 0.25s ease-out; }

    /* Canvas Signature Pad */
    .signature-pad-container { border: 2px dashed var(--neutral-300); border-radius: 8px; background: #fafafa; position: relative; touch-action: none; }
    canvas#signaturePad { width: 100%; height: 200px; display: block; cursor: crosshair; }
    .signature-placeholder { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 0.9rem; color: var(--neutral-400); pointer-events: none; }



    /* Metrics */
    .metrics-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem; margin-bottom: 1.5rem; }
    .metric-card { background: white; border: 1px solid var(--neutral-200); border-radius: var(--radius); padding: 1.25rem; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; gap: 0.4rem; }
    .metric-header { display: flex; align-items: center; gap: 0.5rem; color: var(--neutral-600); font-size: 0.825rem; font-weight: 500; }
    .metric-val { font-size: 1.6rem; font-weight: 700; color: var(--neutral-900); }

    /* Login Screen Gate */
    .login-container {
      max-width: 480px; margin: 3rem auto; background: white; border-radius: 16px;
      padding: 2rem; border: 1px solid var(--neutral-200); box-shadow: var(--shadow-lg);
    }
  </style>
</head>
<body>

  <!-- LOGIN SCREEN (If not authenticated) -->
  <div id="loginScreen" class="login-container" style="display: none;">
    <div style="text-align: center; margin-bottom: 1.25rem;">
      <img src="assets/logo_sdu.png" alt="มหาวิทยาลัยสวนดุสิต" style="height: 64px; width: auto; object-fit: contain; margin-bottom: 0.6rem; filter: drop-shadow(0 2px 6px rgba(0,0,0,0.1));">
      <h2 id="staffLoginTitle" style="font-size: 1.2rem; font-weight: 700; color: var(--neutral-900);">เข้าสู่ระบบเจ้าหน้าที่พัสดุ</h2>
      <p style="font-size: 0.825rem; color: var(--neutral-600); margin-top: 4px;">ฝ่ายพัสดุและคลังสินค้ากลาง มหาวิทยาลัยสวนดุสิต</p>
      <div id="staffLoginBadge" style="margin-top: 0.6rem; display: inline-flex; align-items: center; gap: 6px; background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; padding: 4px 12px; border-radius: 999px; font-size: 0.75rem; font-weight: 600;">
        <svg class="svg-icon" style="width: 14px; height: 14px;" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/></svg>
        <span>สำหรับเจ้าหน้าที่พัสดุ (คัดกรองคำขอ, รับของเข้าคลัง และจ่ายพัสดุ)</span>
      </div>
    </div>

    <div style="margin-bottom: 1.1rem;">
      <label style="display: block; font-size: 0.8rem; font-weight: 600; color: var(--neutral-600); margin-bottom: 0.45rem;">เลือกบทบาทผู้ใช้งาน:</label>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;" id="staffRoleLoginTabs">
        <button type="button" class="staff-role-tab-btn active" data-role="STAFF" onclick="selectStaffLoginRole('STAFF')" style="padding: 0.55rem 0.65rem; border-radius: 8px; border: 2px solid #059669; background: #ecfdf5; color: #047857; font-family: inherit; font-size: 0.8rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; text-align: left; transition: all 0.15s;">
          <svg class="svg-icon" style="width: 16px; height: 16px; flex-shrink: 0;" viewBox="0 0 24 24"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg>
          <div>
            <div style="line-height: 1.2;">เจ้าหน้าที่พัสดุ</div>
            <div style="font-size: 0.68rem; font-weight: 400; opacity: 0.85;">ผู้คัดกรอง</div>
          </div>
        </button>
        <button type="button" class="staff-role-tab-btn" data-role="HEAD" onclick="selectStaffLoginRole('HEAD')" style="padding: 0.55rem 0.65rem; border-radius: 8px; border: 1px solid #cbd5e1; background: white; color: #334155; font-family: inherit; font-size: 0.8rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; text-align: left; transition: all 0.15s;">
          <svg class="svg-icon" style="width: 16px; height: 16px; flex-shrink: 0;" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/></svg>
          <div>
            <div style="line-height: 1.2;">หัวหน้าหน่วยงาน</div>
            <div style="font-size: 0.68rem; font-weight: 400; opacity: 0.85;">ผู้อนุมัติ</div>
          </div>
        </button>
        <button type="button" class="staff-role-tab-btn" data-role="ADMIN" onclick="selectStaffLoginRole('ADMIN')" style="padding: 0.55rem 0.65rem; border-radius: 8px; border: 1px solid #cbd5e1; background: white; color: #334155; font-family: inherit; font-size: 0.8rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; text-align: left; transition: all 0.15s;">
          <svg class="svg-icon" style="width: 16px; height: 16px; flex-shrink: 0;" viewBox="0 0 24 24"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
          <div>
            <div style="line-height: 1.2;">ผู้ดูแลระบบสูงสุด</div>
            <div style="font-size: 0.68rem; font-weight: 400; opacity: 0.85;">ผู้ดูแลระบบ</div>
          </div>
        </button>
        <button type="button" class="staff-role-tab-btn" data-role="REQUESTER" onclick="selectStaffLoginRole('REQUESTER')" style="padding: 0.55rem 0.65rem; border-radius: 8px; border: 1px solid #cbd5e1; background: white; color: #334155; font-family: inherit; font-size: 0.8rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; text-align: left; transition: all 0.15s;">
          <svg class="svg-icon" style="width: 16px; height: 16px; flex-shrink: 0;" viewBox="0 0 24 24"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          <div>
            <div style="line-height: 1.2;">ผู้ขอเบิกพัสดุ</div>
            <div style="font-size: 0.68rem; font-weight: 400; opacity: 0.85;">ส่งคำขอเบิก</div>
          </div>
        </button>
      </div>
      <input type="hidden" id="selectedStaffLoginRole" value="STAFF">
    </div>

    <form onsubmit="handleStaffLogin(event)" style="display: flex; flex-direction: column; gap: 1rem;">
      <div class="form-group">
        <label><svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> ชื่อผู้ใช้งาน</label>
        <input type="text" id="loginUsername" class="form-control" placeholder="กรอกชื่อผู้ใช้งานเจ้าหน้าที่" required autocomplete="username">
      </div>
      <div class="form-group">
        <label><svg class="svg-icon" viewBox="0 0 24 24"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg> รหัสผ่าน</label>
        <input type="password" id="loginPassword" class="form-control" placeholder="กรอกรหัสผ่านเจ้าหน้าที่" required autocomplete="current-password">
      </div>
      <button type="submit" id="btnStaffLoginSubmit" class="btn btn-primary" style="justify-content: center; padding: 0.75rem; margin-top: 0.5rem; background: #059669;">
        <span id="btnStaffLoginSubmitText">เข้าสู่ระบบเจ้าหน้าที่พัสดุ</span>
      </button>
    </form>

    <div style="margin-top: 1rem; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem; font-size: 0.775rem; color: #475569; line-height: 1.5;">
      <div style="font-weight: 600; color: #1e3a8a; margin-bottom: 4px;">สิทธิ์การเข้าใช้งานตามบทบาท:</div>
      <div>• <strong>staff</strong> : เจ้าหน้าที่พัสดุ (คัดกรองคำขอ / จัดการสต๊อก)</div>
      <div>• <strong>head</strong> : หัวหน้าหน่วยงาน (อนุมัติขั้นสุดท้าย)</div>
      <div>• <strong>admin_staff</strong> : ผู้ดูแลระบบสูงสุด (เข้าถึงและสลับมุมมองได้ทุกสิทธิ์)</div>
    </div>

    <div style="margin-top: 1.25rem; text-align: center; border-top: 1px solid var(--neutral-200); padding-top: 1rem; display: flex; justify-content: center; gap: 0.75rem; align-items: center;">
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
            <h1>ระบบบริหารคลังพัสดุ</h1>
            <p>ฝ่ายพัสดุและคลังสินค้ากลาง มหาวิทยาลัยสวนดุสิต</p>
          </div>
        </div>

        <!-- View Switcher Tabs -->
        <nav class="view-switcher">
          <button class="view-btn active" onclick="switchStaffView('requisitions')">
            <svg class="svg-icon" viewBox="0 0 24 24"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg> รายการคำขอเบิก <span class="count-tag" id="navPendingBadge">0</span>
          </button>
          <button class="view-btn" onclick="switchStaffView('inventory')">
            <svg class="svg-icon" viewBox="0 0 24 24"><line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/><line x1="2" x2="22" y1="20" y2="20"/></svg> สรุปยอดสต๊อกคลัง
          </button>
          <button class="view-btn" onclick="switchStaffView('users')">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> จัดการบุคลากร / หน่วยงาน <span class="count-tag" id="navUsersBadge">4</span>
          </button>
          <button class="view-btn" onclick="switchStaffView('analytics')">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg> สรุปยอดและสถิติรายเดือน
          </button>
        </nav>

        <div style="display: flex; align-items: center; gap: 0.65rem; flex-wrap: wrap;">
          <span id="staffAuthBypassBadge" style="display: none; align-items: center; gap: 4px; background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; padding: 0.35rem 0.7rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600;">
            โหมดทดสอบ: พักระบบ Login
          </span>
          <div id="staffRoleBadge" style="background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; padding: 0.35rem 0.75rem; border-radius: 999px; font-size: 0.775rem; font-weight: 600; display: inline-flex; align-items: center; gap: 5px;">
            <svg class="svg-icon svg-icon-sm" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/></svg>
            <span id="staffRoleLabelText">ผู้ดูแลระบบสูงสุด</span>
          </div>
          <div id="staffRoleSwitcherWrap" style="display: inline-flex; align-items: center; gap: 4px;">
            <select id="staffRoleSelect" class="form-control" style="width: auto; font-size: 0.775rem; padding: 0.32rem 0.6rem; height: auto; border-color: #cbd5e1;" onchange="switchActiveRole(this.value)" title="สลับมุมมองสิทธิ์การใช้งาน">
              <option value="ADMIN">มุมมอง: ผู้ดูแลระบบ</option>
              <option value="STAFF">มุมมอง: เจ้าหน้าที่พัสดุ</option>
              <option value="HEAD">มุมมอง: หัวหน้าผู้อนุมัติ</option>
            </select>
          </div>
          <a href="portal.html" class="btn btn-outline" style="font-size: 0.8rem; padding: 0.4rem 0.75rem;">
            <svg class="svg-icon" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg> ศูนย์กลางพอร์ทัล
          </a>
          <a href="index.html" target="_blank" class="btn btn-outline" style="font-size: 0.8rem; padding: 0.4rem 0.75rem;">
            เปิดหน้าผู้เบิก ↗
          </a>
          <button class="btn btn-outline" style="color: var(--danger); font-size: 0.8rem; padding: 0.4rem 0.75rem;" onclick="logoutStaff()">
            <svg class="svg-icon svg-icon-sm" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg> ออกจากระบบ
          </button>
        </div>
      </div>
    </header>

    <main>
      <!-- TAB 1: REQUISITION MANAGEMENT -->
      <section id="view-requisitions" class="view-content active">
        <div id="reqLowStockBanner" style="display: none; background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 1rem; align-items: center; justify-content: space-between; gap: 0.75rem; flex-wrap: wrap;">
          <div style="display: flex; align-items: center; gap: 0.5rem; color: #991b1b; font-size: 0.85rem;">
            <svg class="svg-icon" viewBox="0 0 24 24" style="color: #dc2626; flex-shrink: 0;"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>
            <span id="reqLowStockBannerText">แจ้งเตือนจุดสั่งซื้อใหม่: มีรายการพัสดุคงเหลือต่ำกว่าเกณฑ์ขั้นต่ำ</span>
          </div>
          <button class="btn btn-outline" style="font-size: 0.775rem; padding: 0.35rem 0.75rem; background: white; color: #b91c1c; border-color: #fca5a5;" onclick="jumpToLowStockInventory()">
            ตรวจสอบรายการสต๊อกต่ำ →
          </button>
        </div>

        <div class="dashboard-header" style="flex-wrap: wrap; gap: 0.75rem;">
          <div>
            <h2>จัดการและอนุมัติคำขอเบิกพัสดุ</h2>
            <p style="color: var(--neutral-600); font-size: 0.85rem;" id="reqRoleHintSubtitle">เจ้าหน้าที่คัดกรองคำขอ และหัวหน้าอนุมัติขั้นสุดท้าย ก่อนจ่ายพัสดุ</p>
          </div>
          <div style="display: flex; gap: 0.5rem; align-items: center; margin-left: auto;">
            <label style="font-size: 0.825rem; font-weight: 600; color: var(--neutral-600); display: flex; align-items: center; gap: 4px; white-space: nowrap;">
              <svg class="svg-icon" viewBox="0 0 24 24"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg> เดือน:
            </label>
            <select id="staffReqMonthFilter" class="form-control" style="width: auto; min-width: 170px;" onchange="handleStaffReqMonthChange()">
              <option value="ALL">ดูทุกเดือนย้อนหลัง</option>
              <option value="2026-11" selected>พฤศจิกายน 2569</option>
              <option value="2026-10">ตุลาคม 2569</option>
              <option value="2026-09">กันยายน 2569</option>
            </select>
          </div>
          <div class="status-tabs" style="width: 100%; margin-top: 0.5rem;">
            <button class="status-tab active" onclick="filterStaffRequisitionStatus('PENDING', this)">
              รอคัดกรอง <span class="count-tag" id="pendingCount">0</span>
            </button>
            <button class="status-tab" onclick="filterStaffRequisitionStatus('VERIFIED', this)">
              รอหัวหน้าอนุมัติ <span class="count-tag" id="verifiedCount">0</span>
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
            <div class="metric-header"><svg class="svg-icon" viewBox="0 0 24 24"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg> รายการพัสดุทั้งหมดในระบบ</div>
            <span class="metric-val" id="metricTotalItems">34 <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">รายการ</small></span>
          </div>
          <div class="metric-card" onclick="toggleLowStockFilter()" style="cursor: pointer;" title="คลิกเพื่อกรองเฉพาะรายการพัสดุที่ต่ำกว่าเกณฑ์ขั้นต่ำ">
            <div class="metric-header" style="color: var(--danger);"><svg class="svg-icon" viewBox="0 0 24 24"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg> พัสดุต่ำกว่าเกณฑ์ขั้นต่ำ (คลิกกรอง)</div>
            <span class="metric-val" style="color: var(--danger);" id="metricLowStock">12 <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">รายการ</small></span>
          </div>
          <div class="metric-card">
            <div class="metric-header" style="color: var(--primary);"><svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> ยอดจองรอจ่าย</div>
            <span class="metric-val" style="color: var(--primary);" id="metricReserved">0 <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">ชิ้น</small></span>
          </div>
          <div class="metric-card">
            <div class="metric-header" style="color: var(--accent);"><svg class="svg-icon" viewBox="0 0 24 24"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg> รอบบัญชีปัจจุบัน</div>
            <span class="metric-val" style="color: var(--accent);">พ.ย. 2569</span>
          </div>
        </div>

        <div id="lowStockAlertBanner" style="display: none; background: #fff1f2; border: 1px solid #fecdd3; border-radius: 10px; padding: 0.85rem 1.1rem; margin-bottom: 1.25rem; align-items: center; justify-content: space-between; gap: 0.75rem; flex-wrap: wrap;">
          <div style="display: flex; flex-direction: column; gap: 2px;">
            <div style="display: flex; align-items: center; gap: 6px; font-weight: 700; color: #be123c; font-size: 0.9rem;">
              <svg class="svg-icon" viewBox="0 0 24 24"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>
              <span id="lowStockBannerTitle">แจ้งเตือนจุดสั่งซื้อใหม่</span>
            </div>
            <div id="lowStockBannerItems" style="font-size: 0.8rem; color: #881337;"></div>
          </div>
          <button type="button" id="btnFilterLowStock" class="btn btn-outline" style="background: white; color: #be123c; border-color: #fda4af; font-size: 0.8rem;" onclick="toggleLowStockFilter()">
            แสดงเฉพาะรายการต่ำกว่าเกณฑ์
          </button>
        </div>

        <div style="background: white; border-radius: var(--radius); border: 1px solid var(--neutral-200); padding: 1.5rem; box-shadow: var(--shadow-sm);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
            <h3 style="font-size: 1.1rem; font-weight: 700;">ตารางรายการสต๊อกคงเหลือจริง</h3>
            <div id="inventoryActionButtonsWrap" style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
              <button class="btn btn-outline" onclick="openStockAdjustModal()">
                <svg class="svg-icon" viewBox="0 0 24 24"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg> ปรับยอดสต๊อก
              </button>
              <button class="btn btn-outline" onclick="openStockInModal()">
                <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="16"/><line x1="8" x2="16" y1="12" y2="12"/></svg> บันทึกรับเข้าพัสดุ (เติมสต๊อก)
              </button>
              <button class="btn btn-primary" onclick="openItemModal()">
                <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="16"/><line x1="8" x2="16" y1="12" y2="12"/></svg> เพิ่มรายการพัสดุใหม่
              </button>
            </div>
          </div>

          <div style="overflow-x: auto;">
            <table class="req-table" style="font-size: 0.9rem;">
              <thead>
                <tr>
                  <th style="width: 50px;">ลำดับ</th>
                  <th>ชื่อรายการพัสดุ</th>
                  <th>หน่วยบรรจุ</th>
                  <th>คงคลังจริง</th>
                  <th>ยอดจอง</th>
                  <th>พร้อมเบิก</th>
                  <th>โควตา/ท่าน/เดือน</th>
                  <th>สถานะสต๊อก <small style="font-size: 0.75rem; font-weight: normal; color: var(--neutral-500);">(เกณฑ์เตือน)</small></th>
                  <th>รับเข้าล่าสุด</th>
                  <th style="width: 210px; text-align: right;">จัดการ / ประวัติ</th>
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
            <div class="metric-header"><svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> บุคลากรผู้มีสิทธิ์เบิกทั้งหมด</div>
            <span class="metric-val" id="metricTotalUsers">4 <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">ท่าน</small></span>
          </div>
          <div class="metric-card" onclick="openManageDeptsModal()" style="cursor: pointer;" title="คลิกเพื่อเปิดหน้าต่างจัดการรายชื่อกลุ่มงาน/หน่วยงาน">
            <div class="metric-header" style="color: var(--primary);"><svg class="svg-icon" viewBox="0 0 24 24"><line x1="3" x2="21" y1="22" y2="22"/><line x1="6" x2="6" y1="18" y2="11"/><line x1="10" x2="10" y1="18" y2="11"/><line x1="14" x2="14" y1="18" y2="11"/><line x1="18" x2="18" y1="18" y2="11"/><polygon points="12 2 20 7 4 7"/></svg> กลุ่มงาน / หน่วยงานภายใน สวท. (คลิกจัดการ)</div>
            <span class="metric-val" style="color: var(--primary);" id="metricTotalDepts">5 <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">หน่วยงาน</small></span>
          </div>
          <div class="metric-card" onclick="openQuotaModal()" style="cursor: pointer;" title="คลิกเพื่อเพิ่มกฎโควต้าประจำเดือนสำหรับบุคลากรหรือกลุ่มงาน">
            <div class="metric-header" style="color: #b45309;"><svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg> กฎโควต้าเฉพาะ (บุคลากร / กลุ่มงาน)</div>
            <span class="metric-val" style="color: #b45309;" id="metricTotalQuotas">0 <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">กฎ</small></span>
          </div>
        </div>

        <div style="background: white; border-radius: var(--radius); border: 1px solid var(--neutral-200); padding: 1.5rem; box-shadow: var(--shadow-sm);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem;">
            <div>
              <h3 style="font-size: 1.1rem; font-weight: 700;">ทำเนียบรายชื่อบุคลากรและกลุ่มงาน สวท.</h3>
              <p style="font-size: 0.825rem; color: var(--neutral-600);">ข้อมูลตั้งต้นจากไฟล์ รายนามบุคลากร สวท.docx — เจ้าหน้าที่สามารถเพิ่ม แก้ไข ลบ และกำหนดโควตาเฉพาะบุคลากร/กลุ่มงานได้ตลอดเวลา</p>
            </div>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
              <button class="btn btn-outline" onclick="openManageDeptsModal()">
                <svg class="svg-icon" viewBox="0 0 24 24"><line x1="3" x2="21" y1="22" y2="22"/><line x1="6" x2="6" y1="18" y2="11"/><line x1="10" x2="10" y1="18" y2="11"/><line x1="14" x2="14" y1="18" y2="11"/><line x1="18" x2="18" y1="18" y2="11"/><polygon points="12 2 20 7 4 7"/></svg> จัดการกลุ่มงาน / หน่วยงาน
              </button>
              <button class="btn btn-outline" style="border-color: #f59e0b; color: #b45309; background: #fffbeb;" onclick="openQuotaModal()">
                <svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg> กำหนดโควตาบุคลากร / กลุ่มงาน
              </button>
              <button class="btn btn-primary" onclick="openUserModal()">
                <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="16"/><line x1="8" x2="16" y1="12" y2="12"/></svg> เพิ่มรายชื่อบุคลากร
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
                  <th style="width: 50px; text-align: center;">ลำดับ</th>
                  <th style="width: 140px;">ชื่อผู้ใช้งาน</th>
                  <th style="width: 150px;">บทบาทสิทธิ์</th>
                  <th>ชื่อ-นามสกุล</th>
                  <th>ตำแหน่ง</th>
                  <th>กลุ่มงาน / หน่วยงานที่สังกัด</th>
                  <th style="width: 120px;">เบอร์โทรศัพท์</th>
                  <th style="width: 170px;">โควตาเฉพาะบุคคล</th>
                  <th style="width: 195px; text-align: right;">จัดการ</th>
                </tr>
              </thead>
              <tbody id="staffUsersTableBody">
                <!-- Rendered by JS -->
              </tbody>
            </table>
          </div>
        </div>

        <!-- QUOTA RULES MANAGEMENT SECTION (DEPT & PERSONNEL) -->
        <div id="quotaRulesCard" style="background: white; border-radius: var(--radius); border: 1px solid var(--neutral-200); padding: 1.5rem; box-shadow: var(--shadow-sm); margin-top: 1.5rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem;">
            <div>
              <h3 style="font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 6px;">
                <svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                ระบบกำหนดโควต้าประจำเดือน (แยกตามกลุ่มงาน และรายบุคลากร)
              </h3>
              <p style="font-size: 0.825rem; color: var(--neutral-600);">กำหนดเพดานการเบิกพัสดุรายเดือนเฉพาะเจาะจง (รายบุคลากรมีผลสำคัญกว่าค่ามาตรฐานคลัง และกลุ่มงานคุมเพดานรวมทั้งหน่วยงาน)</p>
            </div>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
              <button class="btn btn-outline" style="border-color: #93c5fd; color: #1e40af; background: #eff6ff;" onclick="openQuotaModal('DEPT')">
                <svg class="svg-icon" viewBox="0 0 24 24"><line x1="3" x2="21" y1="22" y2="22"/><line x1="6" x2="6" y1="18" y2="11"/><line x1="10" x2="10" y1="18" y2="11"/><line x1="14" x2="14" y1="18" y2="11"/><line x1="18" x2="18" y1="18" y2="11"/><polygon points="12 2 20 7 4 7"/></svg> + กำหนดโควตากลุ่มงาน
              </button>
              <button class="btn btn-primary" onclick="openQuotaModal('USER')">
                <svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> + กำหนดโควตารายบุคลากร
              </button>
            </div>
          </div>

          <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap;">
            <button type="button" class="pill-btn active quota-filter-btn" data-qtype="ALL" onclick="filterQuotaRulesType('ALL', this)" style="padding: 6px 14px; border-radius: 999px; border: 1px solid #cbd5e1; background: var(--primary); color: white; font-size: 0.825rem; font-weight: 600; cursor: pointer;">ทั้งหมด</button>
            <button type="button" class="pill-btn quota-filter-btn" data-qtype="DEPT" onclick="filterQuotaRulesType('DEPT', this)" style="padding: 6px 14px; border-radius: 999px; border: 1px solid #cbd5e1; background: white; color: #334155; font-size: 0.825rem; font-weight: 600; cursor: pointer;">โควตากลุ่มงาน / หน่วยงาน</button>
            <button type="button" class="pill-btn quota-filter-btn" data-qtype="USER" onclick="filterQuotaRulesType('USER', this)" style="padding: 6px 14px; border-radius: 999px; border: 1px solid #cbd5e1; background: white; color: #334155; font-size: 0.825rem; font-weight: 600; cursor: pointer;">โควตารายบุคลากร</button>
          </div>

          <div style="overflow-x: auto;">
            <table class="req-table" style="font-size: 0.875rem;">
              <thead>
                <tr>
                  <th style="width: 130px;">ประเภท</th>
                  <th>กลุ่มงาน / บุคลากรเป้าหมาย</th>
                  <th>ขอบเขตรายการพัสดุ</th>
                  <th style="width: 150px;">โควตาสูงสุด / เดือน</th>
                  <th style="width: 150px;">เบิกใช้แล้วเดือนนี้</th>
                  <th>หมายเหตุ</th>
                  <th style="width: 130px; text-align: right;">จัดการ</th>
                </tr>
              </thead>
              <tbody id="quotaRulesTableBody">
                <!-- Rendered by JS -->
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- TAB 4: MONTHLY ANALYTICS & RETROSPECTIVE DASHBOARD -->
      <section id="view-analytics" class="view-content">
        <div class="dashboard-header" style="margin-bottom: 1.25rem; flex-wrap: wrap; gap: 0.75rem;">
          <div>
            <h2>สรุปยอดและสถิติการเบิกจ่ายรายเดือน</h2>
            <p style="color: var(--neutral-600); font-size: 0.85rem;">รายงานภาพรวมการเบิกจ่ายพัสดุ สถิติรายการพัสดุที่เบิกมาก-น้อย และการสืบค้นข้อมูลย้อนหลัง</p>
          </div>
          <div style="display: flex; gap: 0.5rem; align-items: center; margin-left: auto; flex-wrap: wrap;">
            <label style="font-size: 0.825rem; font-weight: 600; color: var(--neutral-600); display: flex; align-items: center; gap: 4px; white-space: nowrap;">
              <svg class="svg-icon" viewBox="0 0 24 24"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg> เลือกเดือนที่ต้องการดูรายงาน:
            </label>
            <select id="analyticsMonthSelect" class="form-control" style="width: auto; min-width: 190px;" onchange="handleAnalyticsMonthChange()">
              <option value="2026-11" selected>พฤศจิกายน 2569 (เดือนปัจจุบัน)</option>
              <option value="2026-10">ตุลาคม 2569</option>
              <option value="2026-09">กันยายน 2569</option>
              <option value="ALL">ภาพรวมข้อมูลย้อนหลังทั้งหมด</option>
            </select>
            <button type="button" class="btn btn-outline" style="font-size: 0.825rem; padding: 0.45rem 0.85rem;" onclick="exportMonthlyAnalyticsCsv()">
              <svg class="svg-icon" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg> ส่งออก Excel
            </button>
            <button type="button" class="btn btn-primary" style="font-size: 0.825rem; padding: 0.45rem 0.85rem;" onclick="printMonthlyAnalyticsPdf()">
              <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect width="12" height="8" x="6" y="14"/></svg> พิมพ์รายงานสรุปผู้บริหาร PDF
            </button>
          </div>
        </div>

        <!-- Analytics Metric Cards -->
        <div class="metrics-row" style="margin-bottom: 1.25rem;">
          <div class="metric-card">
            <div class="metric-header"><svg class="svg-icon" viewBox="0 0 24 24"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg> คำขอเบิกทั้งหมดในเดือน</div>
            <span class="metric-val" id="analyticsMetricTotalReqs">0 <small style="font-size: 0.85rem; font-weight: normal; color: var(--neutral-400);">คำขอ</small></span>
            <div style="font-size: 0.75rem; color: var(--neutral-500); margin-top: 4px;" id="analyticsReqBreakdown">รอคัดกรอง 0 | รออนุมัติ 0 | สำเร็จ 0</div>
          </div>
          <div class="metric-card">
            <div class="metric-header" style="color: var(--primary);"><svg class="svg-icon" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg> จำนวนชิ้นพัสดุที่ขอเบิก</div>
            <span class="metric-val" style="color: var(--primary);" id="analyticsMetricTotalRequested">0 <small style="font-size: 0.85rem; font-weight: normal; color: var(--neutral-400);">ชิ้น</small></span>
            <div style="font-size: 0.75rem; color: var(--neutral-500); margin-top: 4px;">ยอดรวมตามรายการคำขอที่เสนอ</div>
          </div>
          <div class="metric-card">
            <div class="metric-header" style="color: var(--accent);"><svg class="svg-icon" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg> จำนวนชิ้นที่อนุมัติ/จ่ายสำเร็จ</div>
            <span class="metric-val" style="color: var(--accent);" id="analyticsMetricTotalApproved">0 <small style="font-size: 0.85rem; font-weight: normal; color: var(--neutral-400);">ชิ้น</small></span>
            <div style="font-size: 0.75rem; color: var(--neutral-500); margin-top: 4px;">ตัดจ่ายจากคลังพัสดุจริง</div>
          </div>
          <div class="metric-card">
            <div class="metric-header" style="color: #0369a1;"><svg class="svg-icon" viewBox="0 0 24 24"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/></svg> ยอดเงินซื้อพัสดุเข้าคลัง</div>
            <span class="metric-val" style="color: #0369a1;" id="analyticsMetricTotalPurchaseCost">0.00 <small style="font-size: 0.85rem; font-weight: normal; color: var(--neutral-400);">บาท</small></span>
            <div style="font-size: 0.75rem; color: var(--neutral-500); margin-top: 4px;" id="analyticsPurchaseBreakdown">เติมเข้า 0 ครั้ง | รวม 0 ชิ้น</div>
          </div>
        </div>

        <!-- Top 5 vs Least 5 Grid -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 1.25rem; margin-bottom: 1.5rem;">
          <!-- Top 5 Most Requisitioned Items -->
          <div style="background: white; border-radius: var(--radius); border: 1px solid var(--neutral-200); padding: 1.25rem; box-shadow: var(--shadow-sm);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid var(--neutral-100); padding-bottom: 0.5rem;">
              <h3 style="font-size: 1rem; font-weight: 700; color: #1e3a8a; display: flex; align-items: center; gap: 6px;">
                <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg> 5 อันดับพัสดุที่มีการเบิกมากที่สุด
              </h3>
              <span class="status-tag" style="background: #eff6ff; color: #1e40af; font-size: 0.75rem; padding: 2px 8px; border-radius: 999px;">เบิกสูงสุด</span>
            </div>
            <div id="analyticsTopItemsList">
              <!-- Rendered by JS -->
            </div>
          </div>

          <!-- Least 5 Requisitioned Items -->
          <div style="background: white; border-radius: var(--radius); border: 1px solid var(--neutral-200); padding: 1.25rem; box-shadow: var(--shadow-sm);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid var(--neutral-100); padding-bottom: 0.5rem;">
              <h3 style="font-size: 1rem; font-weight: 700; color: #92400e; display: flex; align-items: center; gap: 6px;">
                <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="21 8 21 21 3 21 3 8"/><rect width="22" height="5" x="1" y="3"/><line x1="10" x2="14" y1="12" y2="12"/></svg> 5 อันดับพัสดุที่มีการเบิกน้อยที่สุด / สต๊อกนิ่ง
              </h3>
              <span class="status-tag" style="background: #fffbeb; color: #b45309; font-size: 0.75rem; padding: 2px 8px; border-radius: 999px;">เบิกน้อยสุด</span>
            </div>
            <div id="analyticsLeastItemsList">
              <!-- Rendered by JS -->
            </div>
          </div>
        </div>

        <!-- Full Breakdown Table -->
        <div style="background: white; border-radius: var(--radius); border: 1px solid var(--neutral-200); padding: 1.25rem; box-shadow: var(--shadow-sm);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
            <h3 style="font-size: 1rem; font-weight: 700; color: var(--neutral-800); display: flex; align-items: center; gap: 6px;">
              <svg class="svg-icon" viewBox="0 0 24 24"><line x1="8" x2="21" y1="6" y2="6"/><line x1="8" x2="21" y1="12" y2="12"/><line x1="8" x2="21" y1="18" y2="18"/><line x1="3" x2="3.01" y1="6" y2="6"/><line x1="3" x2="3.01" y1="12" y2="12"/><line x1="3" x2="3.01" y1="18" y2="18"/></svg> สรุปยอดการเบิกพัสดุทุกรายการประจำเดือน
            </h3>
            <span id="analyticsItemTotalCount" style="font-size: 0.85rem; color: var(--neutral-500);"></span>
          </div>
          <div style="overflow-x: auto;">
            <table class="req-table" style="font-size: 0.875rem;">
              <thead>
                <tr>
                  <th style="width: 60px; text-align: center;">ลำดับ</th>
                  <th>ชื่อรายการพัสดุ</th>
                  <th>หมวดหมู่</th>
                  <th style="text-align: right;">จำนวนที่เบิกในเดือน</th>
                  <th style="text-align: center;">จำนวนคำขอ</th>
                  <th style="text-align: center;">หน่วยนับ</th>
                </tr>
              </thead>
              <tbody id="analyticsAllItemsTbody">
                <!-- Rendered by JS -->
              </tbody>
            </table>
          </div>
        </div>

        <!-- Per-Personnel Breakdown Card -->
        <div id="analyticsByPersonCard" style="background: white; border-radius: var(--radius); border: 1px solid var(--neutral-200); padding: 1.25rem; box-shadow: var(--shadow-sm); margin-top: 1.5rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem;">
            <div>
              <h3 style="font-size: 1rem; font-weight: 700; color: #1e3a8a; display: flex; align-items: center; gap: 6px;">
                <svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> สรุปยอดการเบิกพัสดุจำแนกตามรายบุคคลประจำเดือน
              </h3>
              <p style="font-size: 0.825rem; color: var(--neutral-600); margin-top: 2px;">แสดงจำนวนคำขอ ปริมาณพัสดุที่ขอเบิก/จ่ายจริง และรายการพัสดุที่เบิกแยกตามบุคลากรแต่ละท่าน</p>
            </div>
            <span id="analyticsPersonTotalCount" style="font-size: 0.85rem; color: var(--neutral-500); font-weight: 600;"></span>
          </div>

          <div style="display: flex; gap: 0.75rem; margin-bottom: 1rem; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 220px;">
              <input type="text" id="analyticsPersonSearchInput" class="form-control"
                     placeholder="พิมพ์ค้นหาชื่อบุคลากร, หน่วยงาน หรือชื่อพัสดุ..."
                     oninput="renderAnalyticsPersonUsageTable()">
            </div>
            <div style="min-width: 240px;">
              <select id="analyticsPersonDeptFilter" class="form-control" onchange="renderAnalyticsPersonUsageTable()">
                <option value="ALL">ทุกกลุ่มงาน / หน่วยงานทั้งหมด</option>
              </select>
            </div>
          </div>

          <div style="overflow-x: auto;">
            <table class="req-table" style="font-size: 0.875rem;">
              <thead>
                <tr>
                  <th style="width: 55px; text-align: center;">ลำดับ</th>
                  <th style="min-width: 180px;">ชื่อ-นามสกุล ผู้ขอเบิก</th>
                  <th style="min-width: 180px;">กลุ่มงาน / หน่วยงาน</th>
                  <th style="width: 110px; text-align: center;">จำนวนคำขอ</th>
                  <th style="width: 130px; text-align: right;">จำนวนที่ขอเบิก</th>
                  <th style="width: 130px; text-align: right;">อนุมัติ / จ่ายจริง</th>
                  <th style="min-width: 220px;">รายการพัสดุที่เบิกหลัก</th>
                  <th style="width: 110px; text-align: right;">รายละเอียด</th>
                </tr>
              </thead>
              <tbody id="analyticsPersonUsageTbody">
                <!-- Rendered by JS -->
              </tbody>
            </table>
          </div>
        </div>

        <!-- Purchase / Restock Spending Summary Card -->
        <div id="analyticsPurchaseCard" style="background: white; border-radius: var(--radius); border: 1px solid var(--neutral-200); padding: 1.25rem; box-shadow: var(--shadow-sm); margin-top: 1.5rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem;">
            <div>
              <h3 style="font-size: 1rem; font-weight: 700; color: #0369a1; display: flex; align-items: center; gap: 6px;">
                <svg class="svg-icon" viewBox="0 0 24 24"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/></svg> สรุปยอดเงินซื้อพัสดุเข้าคลังประจำเดือน
              </h3>
              <p style="font-size: 0.825rem; color: var(--neutral-600); margin-top: 2px;">คำนวณยอดค่าใช้จ่ายจากการบันทึกเติมสต๊อกพัสดุเข้าคลัง แยกตามรายการและประวัติบิลซื้อเข้า</p>
            </div>
            <span id="analyticsPurchaseGrandTotalBadge" style="background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; padding: 6px 14px; border-radius: 999px; font-size: 0.875rem; font-weight: 700;">รวมทั้งหมด: 0.00 บาท</span>
          </div>

          <div style="margin-bottom: 1rem;">
            <input type="text" id="analyticsPurchaseSearchInput" class="form-control"
                   placeholder="พิมพ์ค้นหาชื่อพัสดุ, เลขที่ใบส่งของ หรือชื่อผู้บันทึก..."
                   oninput="renderAnalyticsPurchaseSection()">
          </div>

          <div style="margin-bottom: 1.25rem;">
            <h4 style="font-size: 0.9rem; font-weight: 700; color: var(--neutral-700); margin-bottom: 0.5rem;">ยอดเงินซื้อเข้าแยกตามรายการพัสดุ</h4>
            <div style="overflow-x: auto;">
              <table class="req-table" style="font-size: 0.875rem;">
                <thead>
                  <tr>
                    <th style="width: 55px; text-align: center;">ลำดับ</th>
                    <th>ชื่อรายการพัสดุ</th>
                    <th>หมวดหมู่</th>
                    <th style="width: 110px; text-align: center;">จำนวนครั้ง</th>
                    <th style="width: 130px; text-align: right;">รับเข้าทั้งหมด</th>
                    <th style="width: 140px; text-align: right;">เฉลี่ย/หน่วยย่อย</th>
                    <th style="width: 160px; text-align: right;">รวมเป็นเงิน (บาท)</th>
                  </tr>
                </thead>
                <tbody id="analyticsPurchaseSummaryTbody">
                  <!-- Rendered by JS -->
                </tbody>
              </table>
            </div>
          </div>

          <div>
            <h4 style="font-size: 0.9rem; font-weight: 700; color: var(--neutral-700); margin-bottom: 0.5rem;">ประวัติรายการเติมสต๊อกพร้อมราคา</h4>
            <div style="overflow-x: auto; max-height: 360px; overflow-y: auto;">
              <table class="req-table" style="font-size: 0.85rem;">
                <thead>
                  <tr>
                    <th style="min-width: 145px;">วัน-เวลา</th>
                    <th style="min-width: 200px;">รายการพัสดุ</th>
                    <th style="width: 120px; text-align: right;">จำนวนรับเข้า</th>
                    <th style="width: 125px; text-align: right;">ราคา/หน่วยย่อย</th>
                    <th style="width: 140px; text-align: right;">ยอดเงินรวม (บาท)</th>
                    <th style="min-width: 160px;">ใบส่งของ / หมายเหตุ</th>
                    <th style="min-width: 140px;">ผู้บันทึก</th>
                  </tr>
                </thead>
                <tbody id="analyticsPurchaseTxTbody">
                  <!-- Rendered by JS -->
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <!-- TAB 3: OFFICIAL PDF PRINTABLE PREVIEW -->
      <section id="view-pdf" class="view-content">
        <div class="pdf-preview-container">
          <div class="pdf-preview-actions" style="display: flex; gap: 1rem;">
            <button class="btn btn-success" onclick="printRequisitionPdf()">
              <svg class="svg-icon" viewBox="0 0 24 24"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect width="12" height="8" x="6" y="14"/></svg> สั่งพิมพ์เอกสารราชการ PDF
            </button>
            <button class="btn btn-outline" style="background: white;" onclick="switchStaffView('requisitions')">
              <svg class="svg-icon" viewBox="0 0 24 24"><line x1="19" x2="5" y1="12" y2="12"/><polyline points="12 19 5 12 12 5"/></svg> กลับหน้ารายการเบิก
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

            <div class="pdf-footer-section">
              <div class="pdf-ack-note">
                * ข้าพเจ้าได้รับมอบพัสดุตามรายการและจำนวนที่ระบุข้างต้นไว้ในสภาพเรียบร้อยครบถ้วนแล้ว
              </div>

              <!-- Signatures Section (4-Party Institutional Form) -->
              <div class="pdf-signatures">
                <div class="sig-box">
                  <div class="sig-line"></div>
                  <div>( <span id="pdfSignRequester">นางสาววาสนา จันทร์จ่าย</span> )</div>
                  <div style="font-size: 0.78rem; color: #444; font-weight: 600;">ผู้ขอเบิกพัสดุ</div>
                  <div style="font-size: 0.72rem; color: #666;" id="pdfSignReqDate">21 ต.ค. 2569</div>
                </div>

                <div class="sig-box">
                  <div id="pdfSignVerifierStamp" style="font-size: 0.75rem; color: #0369a1; font-weight: bold; margin-bottom: 6px;">[ ผ่านการคัดกรอง ]</div>
                  <div class="sig-line"></div>
                  <div>( <span id="pdfSignVerifier">เจ้าหน้าที่พัสดุ สวท.</span> )</div>
                  <div style="font-size: 0.78rem; color: #444; font-weight: 600;">เจ้าหน้าที่ผู้คัดกรอง</div>
                  <div style="font-size: 0.72rem; color: #666;" id="pdfSignVerifiedDate">-</div>
                </div>

                <div class="sig-box">
                  <div id="pdfSignApproverStamp" style="font-size: 0.75rem; color: #15803d; font-weight: bold; margin-bottom: 6px;">[ อนุมัติขั้นสุดท้าย ]</div>
                  <div class="sig-line"></div>
                  <div>( <span id="pdfSignApprover">หัวหน้าสำนักงานผู้อำนวยการ สวท.</span> )</div>
                  <div style="font-size: 0.78rem; color: #444; font-weight: 600;">หัวหน้าผู้อนุมัติ</div>
                  <div style="font-size: 0.72rem; color: #666;" id="pdfSignApprovedDate">-</div>
                </div>

                <div class="sig-box">
                  <div id="pdfReceiverSigArea"></div>
                  <div class="sig-line"></div>
                  <div>( <span id="pdfReceiverName">นางสาววาสนา จันทร์จ่าย</span> )</div>
                  <div style="font-size: 0.78rem; color: #444; font-weight: 600;">ผู้รับมอบพัสดุ</div>
                  <div style="font-size: 0.72rem; color: #666;" id="pdfReceiveTime">วันที่ ........../........../..........</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>



  <!-- Footer -->
  <footer style="text-align: center; padding: 2rem 1rem; color: var(--neutral-400); font-size: 0.85rem; border-top: 1px solid var(--neutral-200); margin-top: 3rem; background: white;">
    <div>
      © 2569 ระบบบริหารคลังพัสดุ มหาวิทยาลัยสวนดุสิต v__SYSTEM_VERSION__ | ใช้งานเฉพาะภายในสถาบัน
    </div>
  </footer>

  <!-- Scripts -->
  <script>
    const APP_VERSION = '__SYSTEM_VERSION__';
    const MYSQL_API_URL = '/api';
    const AUTH_BYPASS = __AUTH_BYPASS__;
    const vIcons = {
      box: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>`,
      cart: `<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg>`,
      layers: `<svg class="svg-icon" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>`,
      tag: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94.94-2.48 0-3.42L12 2Z"/><circle cx="7" cy="7" r=".5" fill="currentColor"/></svg>`,
      trash: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>`,
      pen: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="m18 2 4 4-12 12H6v-4L18 2z"/><path d="m15 5 4 4"/><path d="M2 22h20"/></svg>`,
      check: `<svg class="svg-icon" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>`,
      checkCircle: `<svg class="svg-icon" viewBox="0 0 24 24" style="width:14px;height:14px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`,
      alertTriangle: `<svg class="svg-icon" viewBox="0 0 24 24" style="width:14px;height:14px;"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>`,
      bell: `<svg class="svg-icon" viewBox="0 0 24 24" style="width:14px;height:14px;"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>`,
      x: `<svg class="svg-icon" viewBox="0 0 24 24"><line x1="18" x2="6" y1="6" y2="18"/><line x1="6" x2="18" y1="6" y2="18"/></svg>`,
      eye: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>`,
      printer: `<svg class="svg-icon" viewBox="0 0 24 24"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect width="12" height="8" x="6" y="14"/></svg>`,
      building: `<svg class="svg-icon" viewBox="0 0 24 24"><line x1="3" x2="21" y1="22" y2="22"/><line x1="6" x2="6" y1="18" y2="11"/><line x1="10" x2="10" y1="18" y2="11"/><line x1="14" x2="14" y1="18" y2="11"/><line x1="18" x2="18" y1="18" y2="11"/><polygon points="12 2 20 7 4 7"/></svg>`,
      user: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`,
      calendar: `<svg class="svg-icon" viewBox="0 0 24 24"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>`,
      shield: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
      trendingUp: `<svg class="svg-icon" viewBox="0 0 24 24"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>`,
      archive: `<svg class="svg-icon" viewBox="0 0 24 24"><polyline points="21 8 21 21 3 21 3 8"/><rect width="22" height="5" x="1" y="3"/><line x1="10" x2="14" y1="12" y2="12"/></svg>`,
      list: `<svg class="svg-icon" viewBox="0 0 24 24"><line x1="8" x2="21" y1="6" y2="6"/><line x1="8" x2="21" y1="12" y2="12"/><line x1="8" x2="21" y1="18" y2="18"/><line x1="3" x2="3.01" y1="6" y2="6"/><line x1="3" x2="3.01" y1="12" y2="12"/><line x1="3" x2="3.01" y1="18" y2="18"/></svg>`,
      fileText: `<svg class="svg-icon" viewBox="0 0 24 24"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>`
    };

    const DB_ITEMS_KEY = 'inventory_items';
    const DB_REQS_KEY = 'inventory_requisitions';
    const DB_USERS_KEY = 'inventory_users';
    const DB_DEPTS_KEY = 'inventory_departments';
    const DB_QUOTAS_KEY = 'inventory_quotas';

    function getQuotasDB() {
      try {
        const raw = localStorage.getItem(DB_QUOTAS_KEY);
        const parsed = raw ? JSON.parse(raw) : [];
        return Array.isArray(parsed) ? parsed : [];
      } catch (e) {
        return [];
      }
    }
    function saveQuotasDB(list) {
      localStorage.setItem(DB_QUOTAS_KEY, JSON.stringify(Array.isArray(list) ? list : []));
    }

    const defaultItems = __DEFAULT_ITEMS__;
    const defaultReqs = __DEFAULT_REQS__;
    const defaultDepts = __DEFAULT_DEPTS__;
    const defaultUsers = __DEFAULT_USERS__;

    function getDeptsDB() {
      const data = localStorage.getItem(DB_DEPTS_KEY);
      if (!data) {
        localStorage.setItem(DB_DEPTS_KEY, JSON.stringify(defaultDepts));
        return JSON.parse(JSON.stringify(defaultDepts));
      }
      try {
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed) && parsed.length > 0 && parsed[0].category && parsed[0].category.includes('สวท')) {
          return parsed;
        }
        localStorage.setItem(DB_DEPTS_KEY, JSON.stringify(defaultDepts));
        return JSON.parse(JSON.stringify(defaultDepts));
      } catch (e) {
        localStorage.setItem(DB_DEPTS_KEY, JSON.stringify(defaultDepts));
        return JSON.parse(JSON.stringify(defaultDepts));
      }
    }
    function saveDeptsDB(depts) { localStorage.setItem(DB_DEPTS_KEY, JSON.stringify(depts)); }

    function getUsersDB() {
      const data = localStorage.getItem(DB_USERS_KEY);
      if (!data) {
        localStorage.setItem(DB_USERS_KEY, JSON.stringify(defaultUsers));
        return JSON.parse(JSON.stringify(defaultUsers));
      }
      try {
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed) && parsed.length > 0) {
          // Auto-migrate if localStorage still had the old 29-user list (contains ผอ.อังค์ริสา)
          if (parsed.some(u => u.name && u.name.includes('อังค์ริสา'))) {
            const customAdded = parsed.filter(u => Number(u.id) > 29);
            const migrated = [
              ...JSON.parse(JSON.stringify(defaultUsers)),
              ...customAdded.map((u, idx) => ({ ...u, id: defaultUsers.length + idx + 1 }))
            ];
            localStorage.setItem(DB_USERS_KEY, JSON.stringify(migrated));
            return migrated;
          }
          return parsed;
        }
        localStorage.setItem(DB_USERS_KEY, JSON.stringify(defaultUsers));
        return JSON.parse(JSON.stringify(defaultUsers));
      } catch (e) {
        localStorage.setItem(DB_USERS_KEY, JSON.stringify(defaultUsers));
        return JSON.parse(JSON.stringify(defaultUsers));
      }
    }
    function saveUsersDB(users) { localStorage.setItem(DB_USERS_KEY, JSON.stringify(users)); }

    function getItemsDB() {
      const data = localStorage.getItem(DB_ITEMS_KEY);
      if (!data) {
        localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(defaultItems));
        return JSON.parse(JSON.stringify(defaultItems));
      }
      try {
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed) && parsed.length > 0) {
          const defMap = new Map(defaultItems.map(i => [i.id, i]));
          let needsSave = false;
          const upgraded = parsed.map(ex => {
            const defItem = defMap.get(ex.id);
            if (defItem && ex.image_piece && ex.image_piece.startsWith('assets/images/image')) {
              needsSave = true;
              return { ...defItem, on_hand_pieces: ex.on_hand_pieces, reserved_pieces: ex.reserved_pieces };
            }
            return ex;
          });
          if (needsSave) localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(upgraded));
          return upgraded;
        }
        return parsed;
      } catch (e) {
        localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(defaultItems));
        return JSON.parse(JSON.stringify(defaultItems));
      }
    }
    function saveItemsDB(items) { localStorage.setItem(DB_ITEMS_KEY, JSON.stringify(items)); }

    function getReqsDB() {
      const data = localStorage.getItem(DB_REQS_KEY);
      if (!data) {
        localStorage.setItem(DB_REQS_KEY, JSON.stringify(defaultReqs));
        return defaultReqs;
      }
      try {
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed)) {
          const defMap = new Map(defaultReqs.map(r => [r.id, r]));
          let needsSave = false;
          const updated = parsed.map(r => {
            const defReq = defMap.get(r.id);
            if (defReq && (r.dept === 'โรงเรียนการเรือน' || r.dept === 'คณะพยาบาลศาสตร์')) {
              needsSave = true;
              return { ...r, dept: defReq.dept, requester: defReq.requester, purpose: defReq.purpose };
            }
            return r;
          });
          if (needsSave) localStorage.setItem(DB_REQS_KEY, JSON.stringify(updated));
          return updated;
        }
        return parsed;
      } catch (e) {
        return defaultReqs;
      }
    }
    function saveReqsDB(reqs) { localStorage.setItem(DB_REQS_KEY, JSON.stringify(reqs)); }

    async function syncFromMySQLAPI() {
      if (!MYSQL_API_URL || !navigator.onLine) return;
      try {
        const [itemsRes, reqsRes, usersRes, deptsRes, quotasRes] = await Promise.all([
          fetch(`${MYSQL_API_URL}?action=getItems`).then(r => r.json()).catch(() => null),
          fetch(`${MYSQL_API_URL}?action=getRequisitions`).then(r => r.json()).catch(() => null),
          fetch(`${MYSQL_API_URL}?action=getUsers`).then(r => r.json()).catch(() => null),
          fetch(`${MYSQL_API_URL}?action=getDepartments`).then(r => r.json()).catch(() => null),
          fetch(`${MYSQL_API_URL}?action=getQuotas`).then(r => r.json()).catch(() => null)
        ]);
        if (quotasRes && quotasRes.status === 'success' && Array.isArray(quotasRes.data)) {
          saveQuotasDB(quotasRes.data);
          if (typeof renderCatalog === 'function') renderCatalog();
        }
        if (itemsRes && itemsRes.status === 'success' && Array.isArray(itemsRes.data) && itemsRes.data.length > 0) {
          saveItemsDB(itemsRes.data);
        }
        if (reqsRes && reqsRes.status === 'success' && Array.isArray(reqsRes.data) && reqsRes.data.length > 0) {
          saveReqsDB(reqsRes.data);
        }
        if (usersRes && usersRes.status === 'success' && Array.isArray(usersRes.data) && usersRes.data.length > 0) {
          saveUsersDB(usersRes.data);
        }
        if (deptsRes && deptsRes.status === 'success' && Array.isArray(deptsRes.data) && deptsRes.data.length > 0) {
          const grouped = {};
          deptsRes.data.forEach(d => {
            const cat = d.category || 'สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)';
            const lbl = d.full_label || d.name;
            if (!grouped[cat]) grouped[cat] = [];
            if (lbl && !grouped[cat].some(x => x.value === lbl)) {
              grouped[cat].push({ label: lbl, value: lbl, sub: false });
            }
          });
          const formattedDepts = Object.keys(grouped).map(k => ({ category: k, items: grouped[k] }));
          if (formattedDepts.length > 0) saveDeptsDB(formattedDepts);
        }
        loadStaffDashboard();
      } catch (err) {
        console.warn('Offline fallback active (localStorage):', err);
      }
    }

    const DB_TX_KEY = 'sdu_stock_tx_v3';
    const defaultTransactions = [
      { id: 4, itemId: 3, itemName: 'กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)', unitPiece: 'ใบ', transactionType: 'OUT', changePieces: -1000, balanceAfter: 32000, referenceType: 'REQUISITION', referenceId: 'REQ-256910-0003', reason: 'เบิกจ่ายสำเร็จ (คณะวิทยาศาสตร์และเทคโนโลยี)', recordedBy: 'เจ้าหน้าที่พัสดุ สวท.', formattedDate: '5 ต.ค. 2569 14:30 น.' },
      { id: 3, itemId: 3, itemName: 'กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)', unitPiece: 'ใบ', transactionType: 'OUT', changePieces: -1000, balanceAfter: 33000, referenceType: 'REQUISITION', referenceId: 'REQ-256910-0002', reason: 'เบิกจ่ายสำเร็จ (คณะพยาบาลศาสตร์)', recordedBy: 'เจ้าหน้าที่พัสดุ สวท.', formattedDate: '2 ต.ค. 2569 11:00 น.' },
      { id: 2, itemId: 3, itemName: 'กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)', unitPiece: 'ใบ', transactionType: 'OUT', changePieces: -500, balanceAfter: 34000, referenceType: 'REQUISITION', referenceId: 'REQ-256910-0001', reason: 'เบิกจ่ายสำเร็จ (โรงเรียนการเรือน)', recordedBy: 'เจ้าหน้าที่พัสดุ สวท.', formattedDate: '1 ต.ค. 2569 10:00 น.' },
      { id: 1, itemId: 7, itemName: 'กระดาษลายเส้น (ห่อละ 500 แผ่น)', unitPiece: 'แผ่น', transactionType: 'OUT', changePieces: -500, balanceAfter: 23000, referenceType: 'REQUISITION', referenceId: 'REQ-256910-0001', reason: 'เบิกจ่ายสำเร็จ (โรงเรียนการเรือน)', recordedBy: 'เจ้าหน้าที่พัสดุ สวท.', formattedDate: '1 ต.ค. 2569 10:00 น.' }
    ];

    function getTransactionsDB(itemId = null) {
      const raw = localStorage.getItem(DB_TX_KEY);
      let list = defaultTransactions;
      if (raw) {
        try {
          const parsed = JSON.parse(raw);
          if (Array.isArray(parsed) && parsed.length > 0) list = parsed;
        } catch (e) {}
      } else {
        localStorage.setItem(DB_TX_KEY, JSON.stringify(defaultTransactions));
      }
      if (itemId !== null && itemId !== undefined) {
        return list.filter(t => Number(t.itemId) === Number(itemId));
      }
      return list;
    }

    function recordLocalTransaction(tx) {
      const list = getTransactionsDB();
      const nextId = list.length > 0 ? Math.max(...list.map(t => Number(t.id) || 0)) + 1 : 1;
      const entry = {
        id: nextId,
        itemId: Number(tx.itemId),
        itemName: tx.itemName || '',
        unitPiece: tx.unitPiece || 'ชิ้น',
        transactionType: tx.transactionType || 'IN',
        changePieces: Number(tx.changePieces || 0),
        balanceAfter: Number(tx.balanceAfter || 0),
        unitPrice: Number((Number(tx.unitPrice || 0)).toFixed(2)),
        totalCost: Number((Number(tx.totalCost || 0)).toFixed(2)),
        referenceType: tx.referenceType || '',
        referenceId: tx.referenceId || '',
        reason: tx.reason || '',
        recordedBy: tx.recordedBy || 'เจ้าหน้าที่พัสดุ สวท.',
        formattedDate: tx.formattedDate || formatThaiDatetime(new Date()),
        createdAt: tx.createdAt || new Date().toISOString().slice(0, 19).replace('T', ' ')
      };
      list.unshift(entry);
      localStorage.setItem(DB_TX_KEY, JSON.stringify(list));
    }

    function resolveRoleFromUsername(username) {
      const u = String(username || '').trim().toLowerCase();
      if (['admin_staff', 'admin'].includes(u)) return 'ADMIN';
      if (['head', 'head_approver', 'approver', 'director', 'wasana.c', 'jeerawan.b', 'patcharaporn.k', 'sineenart.l'].includes(u)) return 'HEAD';
      return 'STAFF';
    }

    function getBaseStaffRole() {
      return (sessionStorage.getItem('staff_role') || 'ADMIN').toUpperCase();
    }

    function getActiveStaffRole() {
      return (sessionStorage.getItem('staff_active_role') || sessionStorage.getItem('staff_role') || 'ADMIN').toUpperCase();
    }

    function getLoggedInStaff() {
      const role = getActiveStaffRole();
      const username = sessionStorage.getItem('staff_username') || (role === 'HEAD' ? 'head_approver' : role === 'STAFF' ? 'staff' : 'admin_staff');
      let defaultName = 'ผู้ดูแลระบบคลังพัสดุ';
      if (role === 'STAFF') defaultName = 'เจ้าหน้าที่พัสดุ สวท. (ผู้คัดกรอง)';
      if (role === 'HEAD') defaultName = 'หัวหน้าสำนักงานผู้อำนวยการ สวท. (ผู้อนุมัติ)';
      const name = sessionStorage.getItem('staff_name') || defaultName;
      return { username, name: role !== getBaseStaffRole() ? defaultName : name, role };
    }

    function updateRoleUI() {
      const baseRole = getBaseStaffRole();
      const activeRole = getActiveStaffRole();
      const badgeEl = document.getElementById('staffRoleBadge');
      const labelEl = document.getElementById('staffRoleLabelText');
      const switcherWrap = document.getElementById('staffRoleSwitcherWrap');
      const selectEl = document.getElementById('staffRoleSelect');
      const subtitleEl = document.getElementById('reqRoleHintSubtitle');
      const invButtonsWrap = document.getElementById('inventoryActionButtonsWrap');

      if (selectEl) selectEl.value = activeRole;
      if (switcherWrap) {
        switcherWrap.style.display = (baseRole === 'ADMIN') ? 'inline-flex' : 'none';
      }

      if (badgeEl && labelEl) {
        if (activeRole === 'HEAD') {
          badgeEl.style.background = '#f5f3ff';
          badgeEl.style.color = '#6d28d9';
          badgeEl.style.borderColor = '#ddd6fe';
          labelEl.innerText = 'สิทธิ์: หัวหน้าผู้อนุมัติ';
        } else if (activeRole === 'STAFF') {
          badgeEl.style.background = '#ecfdf5';
          badgeEl.style.color = '#047857';
          badgeEl.style.borderColor = '#a7f3d0';
          labelEl.innerText = 'สิทธิ์: เจ้าหน้าที่พัสดุ';
        } else {
          badgeEl.style.background = '#eff6ff';
          badgeEl.style.color = '#1e40af';
          badgeEl.style.borderColor = '#bfdbfe';
          labelEl.innerText = 'สิทธิ์: ผู้ดูแลระบบสูงสุด';
        }
      }

      if (subtitleEl) {
        if (activeRole === 'STAFF') {
          subtitleEl.innerText = 'โหมดเจ้าหน้าที่พัสดุ: ตรวจสอบความถูกต้องของคำขอ, รับของเข้าคลัง, และบันทึกจ่ายพัสดุ';
        } else if (activeRole === 'HEAD') {
          subtitleEl.innerText = 'โหมดหัวหน้าหน่วยงาน: พิจารณาอนุมัติคำขอขั้นสุดท้าย สำหรับรายการที่ผ่านการคัดกรองแล้ว';
        } else {
          subtitleEl.innerText = 'โหมดผู้ดูแลระบบ: สามารถดำเนินการคัดกรอง, อนุมัติขั้นสุดท้าย, และบริหารจัดการระบบทั้งหมด';
        }
      }

      if (invButtonsWrap) {
        invButtonsWrap.style.display = (activeRole === 'HEAD') ? 'none' : 'flex';
      }
    }

    function switchActiveRole(newRole) {
      const r = String(newRole || 'ADMIN').toUpperCase();
      sessionStorage.setItem('staff_active_role', r);
      try {
        if (window.location.search && window.location.search.includes('role=')) {
          window.history.replaceState({}, '', window.location.pathname);
        }
      } catch (e) {}
      updateRoleUI();
      if (r === 'HEAD') {
        const tabs = document.querySelectorAll('.status-tab');
        if (tabs[1]) filterStaffRequisitionStatus('VERIFIED', tabs[1]);
        else renderStaffRequisitions(currentStaffStatus);
      } else if (r === 'STAFF') {
        const tabs = document.querySelectorAll('.status-tab');
        if (tabs[0]) filterStaffRequisitionStatus('PENDING', tabs[0]);
        else renderStaffRequisitions(currentStaffStatus);
      } else {
        renderStaffRequisitions(currentStaffStatus);
      }
      renderInventoryTable();
    }

    async function postToMySQLAPI(action, payload) {
      if (!MYSQL_API_URL || !navigator.onLine) return null;
      try {
        const token = sessionStorage.getItem('staff_token') || '';
        const activeRole = getActiveStaffRole();
        const headers = { 'Content-Type': 'application/json', 'X-Staff-Role': activeRole };
        if (token) headers['Authorization'] = 'Bearer ' + token;
        const enrichedPayload = (payload && typeof payload === 'object') ? { ...payload, caller_role: activeRole } : payload;
        const res = await fetch(MYSQL_API_URL, {
          method: 'POST',
          headers: headers,
          body: JSON.stringify({ action, payload: enrichedPayload, staff_token: token })
        });
        if (res.status === 401) {
          sessionStorage.removeItem('staff_auth');
          sessionStorage.removeItem('staff_token');
          checkStaffAuth();
          if (typeof Swal !== 'undefined') {
            Swal.fire({
              icon: 'warning',
              title: 'เซสชันหมดอายุ',
              text: 'กรุณาเข้าสู่ระบบเจ้าหน้าที่พัสดุใหม่อีกครั้ง'
            });
          }
          return null;
        }
        return await res.json();
      } catch (err) {
        console.warn('MySQL API unreachable, saved to localStorage fallback:', err);
        return null;
      }
    }

    function selectStaffLoginRole(role) {
      const r = String(role || 'STAFF').toUpperCase();
      const hiddenEl = document.getElementById('selectedStaffLoginRole');
      if (hiddenEl) hiddenEl.value = r;

      const titleEl = document.getElementById('staffLoginTitle');
      const badgeEl = document.getElementById('staffLoginBadge');
      const unameEl = document.getElementById('loginUsername');
      const passEl = document.getElementById('loginPassword');
      const btnEl = document.getElementById('btnStaffLoginSubmit');
      const btnTextEl = document.getElementById('btnStaffLoginSubmitText');

      const roleConfigs = {
        STAFF: {
          title: 'เข้าสู่ระบบเจ้าหน้าที่พัสดุ',
          badgeText: 'สำหรับเจ้าหน้าที่พัสดุ (คัดกรองคำขอ, รับของเข้าคลัง และจ่ายพัสดุ)',
          badgeBg: '#ecfdf5',
          badgeColor: '#047857',
          badgeBorder: '#a7f3d0',
          userPlaceholder: 'กรอกชื่อผู้ใช้งานเจ้าหน้าที่',
          passPlaceholder: 'กรอกรหัสผ่านเจ้าหน้าที่',
          btnText: 'เข้าสู่ระบบเจ้าหน้าที่พัสดุ',
          btnBg: '#059669'
        },
        HEAD: {
          title: 'เข้าสู่ระบบหัวหน้าหน่วยงาน',
          badgeText: 'สำหรับหัวหน้าหน่วยงาน (อนุมัติคำขอขั้นสุดท้าย Approve และดูสถิติ)',
          badgeBg: '#f5f3ff',
          badgeColor: '#6d28d9',
          badgeBorder: '#ddd6fe',
          userPlaceholder: 'กรอกชื่อผู้ใช้งานหัวหน้าหน่วยงาน',
          passPlaceholder: 'กรอกรหัสผ่านหัวหน้าหน่วยงาน',
          btnText: 'เข้าสู่ระบบหัวหน้าผู้อนุมัติ',
          btnBg: '#4f46e5'
        },
        ADMIN: {
          title: 'เข้าสู่ระบบผู้ดูแลระบบสูงสุด',
          badgeText: 'สำหรับผู้ดูแลระบบ (บริหารจัดการคลัง บุคลากร กลุ่มงาน และทุกสิทธิ์)',
          badgeBg: '#f1f5f9',
          badgeColor: '#0f172a',
          badgeBorder: '#cbd5e1',
          userPlaceholder: 'กรอกชื่อผู้ใช้งานผู้ดูแลระบบ',
          passPlaceholder: 'กรอกรหัสผ่านผู้ดูแลระบบ',
          btnText: 'เข้าสู่ระบบผู้ดูแลระบบสูงสุด',
          btnBg: '#0f172a'
        },
        REQUESTER: {
          title: 'เข้าสู่ระบบผู้ขอเบิกพัสดุ',
          badgeText: 'สำหรับบุคลากรและอาจารย์ สวท. (เลือกเบิกพัสดุและติดตามสถานะ)',
          badgeBg: '#eff6ff',
          badgeColor: '#1e40af',
          badgeBorder: '#bfdbfe',
          userPlaceholder: 'กรอกชื่อผู้ใช้งานผู้ขอเบิก',
          passPlaceholder: 'กรอกรหัสผ่านผู้ขอเบิก',
          btnText: 'เข้าสู่ระบบผู้ขอเบิกพัสดุ',
          btnBg: '#1e40af'
        }
      };

      const cfg = roleConfigs[r] || roleConfigs.STAFF;
      if (titleEl) titleEl.innerText = cfg.title;
      if (badgeEl) {
        badgeEl.style.background = cfg.badgeBg;
        badgeEl.style.color = cfg.badgeColor;
        badgeEl.style.borderColor = cfg.badgeBorder;
        badgeEl.innerHTML = `<svg class="svg-icon" style="width: 14px; height: 14px;" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/></svg><span>${cfg.badgeText}</span>`;
      }
      if (unameEl) unameEl.placeholder = cfg.userPlaceholder;
      if (passEl) passEl.placeholder = cfg.passPlaceholder;
      if (btnEl) btnEl.style.background = cfg.btnBg;
      if (btnTextEl) btnTextEl.innerText = cfg.btnText;

      document.querySelectorAll('#staffRoleLoginTabs .staff-role-tab-btn').forEach(btn => {
        const bRole = btn.getAttribute('data-role');
        if (bRole === r) {
          btn.classList.add('active');
          btn.style.border = `2px solid ${cfg.btnBg}`;
          btn.style.background = cfg.badgeBg;
          btn.style.color = cfg.badgeColor;
        } else {
          btn.classList.remove('active');
          btn.style.border = '1px solid #cbd5e1';
          btn.style.background = 'white';
          btn.style.color = '#334155';
        }
      });
    }

    // Auth Simulation
    function checkStaffAuth(skipBypass = false) {
      let isAuth = sessionStorage.getItem('staff_auth') === 'true';
      const wantsLogin = window.location.search.includes('showLogin=1');
      if (!isAuth && AUTH_BYPASS && !skipBypass && !wantsLogin) {
        let initialActiveRole = 'ADMIN';
        try {
          const urlRole = (new URLSearchParams(window.location.search).get('role') || '').toUpperCase();
          if (['STAFF', 'HEAD', 'ADMIN'].includes(urlRole)) {
            initialActiveRole = urlRole;
          }
        } catch (e) {}
        sessionStorage.setItem('staff_auth', 'true');
        sessionStorage.setItem('staff_username', 'admin_staff');
        sessionStorage.setItem('staff_name', 'ผู้ดูแลระบบคลังพัสดุ (โหมดทดสอบ)');
        sessionStorage.setItem('staff_role', 'ADMIN');
        sessionStorage.setItem('staff_active_role', initialActiveRole);
        isAuth = true;
      }
      if (!isAuth) {
        document.getElementById('loginScreen').style.display = 'block';
        document.getElementById('staffPortalApp').style.display = 'none';
      } else {
        document.getElementById('loginScreen').style.display = 'none';
        document.getElementById('staffPortalApp').style.display = 'block';
        const bypassBadge = document.getElementById('staffAuthBypassBadge');
        if (bypassBadge) bypassBadge.style.display = AUTH_BYPASS ? 'inline-flex' : 'none';
        updateRoleUI();
        loadStaffDashboard();
        const activeRole = getActiveStaffRole();
        if (AUTH_BYPASS && !skipBypass) {
          if (activeRole === 'HEAD') {
            const tabs = document.querySelectorAll('.status-tab');
            if (tabs[1]) filterStaffRequisitionStatus('VERIFIED', tabs[1]);
          } else if (activeRole === 'STAFF') {
            const tabs = document.querySelectorAll('.status-tab');
            if (tabs[0]) filterStaffRequisitionStatus('PENDING', tabs[0]);
          }
        }
      }
    }

    async function handleStaffLogin(e) {
      e.preventDefault();
      const usernameInput = document.getElementById('loginUsername');
      const passwordInput = document.getElementById('loginPassword');
      const selectedRole = (document.getElementById('selectedStaffLoginRole')?.value || 'STAFF').toUpperCase();
      const username = usernameInput ? usernameInput.value.trim() : '';
      const password = passwordInput ? passwordInput.value.trim() : '';

      if (selectedRole === 'REQUESTER') {
        try {
          const res = await fetch(MYSQL_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'loginRequester', username, password })
          });
          const data = await res.json();
          if (data && data.status === 'success' && data.user) {
            localStorage.setItem('sdu_requester_auth_v1', JSON.stringify(data.user));
            window.location.href = 'index.html';
            return;
          }
        } catch (err) {}
        const users = getUsersDB();
        const found = users.find(u => (u.username && u.username.toLowerCase() === username.toLowerCase()) || (u.name && u.name.toLowerCase() === username.toLowerCase()));
        if (found && (password === (found.password || 'sdu1234') || password === 'sdu1234')) {
          localStorage.setItem('sdu_requester_auth_v1', JSON.stringify(found));
          window.location.href = 'index.html';
          return;
        }
        Swal.fire({
          icon: 'error',
          title: 'เข้าสู่ระบบไม่สำเร็จ',
          text: 'ชื่อผู้ใช้งานหรือรหัสผ่านผู้ขอเบิกไม่ถูกต้อง',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ลองใหม่อีกครั้ง'
        });
        return;
      }

      try {
        const res = await fetch(MYSQL_API_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'loginStaff', username, password, requested_role: selectedRole })
        });
        const data = await res.json();
        if (data && data.status === 'success') {
          const baseRole = (data.role || resolveRoleFromUsername(username)).toUpperCase();
          const activeRole = (data.active_role || (baseRole === 'ADMIN' ? selectedRole : baseRole)).toUpperCase();
          sessionStorage.setItem('staff_auth', 'true');
          sessionStorage.setItem('staff_token', data.token || '');
          sessionStorage.setItem('staff_username', data.username || username);
          sessionStorage.setItem('staff_name', data.name || username);
          sessionStorage.setItem('staff_role', baseRole);
          sessionStorage.setItem('staff_active_role', activeRole);
          checkStaffAuth();
          if (activeRole === 'HEAD') {
            const tabs = document.querySelectorAll('.status-tab');
            if (tabs[1]) filterStaffRequisitionStatus('VERIFIED', tabs[1]);
          } else if (activeRole === 'STAFF') {
            const tabs = document.querySelectorAll('.status-tab');
            if (tabs[0]) filterStaffRequisitionStatus('PENDING', tabs[0]);
          }
        } else {
          Swal.fire({
            icon: 'error',
            title: 'เข้าสู่ระบบไม่สำเร็จ',
            text: (data && data.message) || 'ชื่อผู้ใช้หรือรหัสผ่านเจ้าหน้าที่ไม่ถูกต้อง'
          });
        }
      } catch (err) {
        console.warn('Login request failed or offline fallback:', err);
        const uLow = username.toLowerCase();
        let resolvedRole = null;
        let resolvedName = username;
        if (['admin_staff', 'admin'].includes(uLow) && password === 'sdu1234') {
          resolvedRole = 'ADMIN';
          resolvedName = 'ผู้ดูแลระบบคลังพัสดุ';
        } else if (['staff', 'warehouse_staff', 'screener', 'officer'].includes(uLow) && password === 'sdu1234') {
          resolvedRole = 'STAFF';
          resolvedName = 'เจ้าหน้าที่พัสดุ สวท. (ผู้คัดกรอง)';
        } else if (['head', 'head_approver', 'approver', 'director', 'wasana.c', 'jeerawan.b', 'patcharaporn.k', 'sineenart.l'].includes(uLow) && password === 'sdu1234') {
          resolvedRole = 'HEAD';
          resolvedName = 'หัวหน้าหน่วยงาน สวท. (ผู้อนุมัติ)';
        } else {
          const foundUser = getUsersDB().find(u => (u.username && u.username.toLowerCase() === uLow) || (u.name && u.name.toLowerCase() === uLow));
          const validPass = foundUser ? (foundUser.password || 'sdu1234') : '';
          if (foundUser && (password === validPass || password === 'sdu1234')) {
            const uRole = String(foundUser.role || 'REQUESTER').toUpperCase();
            if (['ADMIN', 'HEAD', 'STAFF'].includes(uRole)) {
              resolvedRole = uRole;
              resolvedName = foundUser.name || username;
            } else {
              Swal.fire({
                icon: 'error',
                title: 'สิทธิ์ไม่ตรงกับบทบาทที่เลือก',
                text: `บัญชี '${username}' มีสิทธิ์เป็น REQUESTER กรุณาเลือกแท็บ 'ผู้ขอเบิกพัสดุ'`
              });
              return;
            }
          }
        }
        if (!resolvedRole) {
          Swal.fire({
            icon: 'error',
            title: 'เข้าสู่ระบบไม่สำเร็จ',
            text: 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง โหมดออฟไลน์'
          });
          return;
        }
        if (resolvedRole !== 'ADMIN' && resolvedRole !== selectedRole) {
          Swal.fire({
            icon: 'error',
            title: 'สิทธิ์ไม่ตรงกับบทบาทที่เลือก',
            text: `บัญชี '${username}' มีสิทธิ์เป็น ${resolvedRole} กรุณาเลือกแท็บบทบาทให้ตรงกับสิทธิ์ของท่าน`
          });
          return;
        }
        const activeRole = resolvedRole === 'ADMIN' ? selectedRole : resolvedRole;
        sessionStorage.setItem('staff_auth', 'true');
        sessionStorage.setItem('staff_username', username || 'admin_staff');
        sessionStorage.setItem('staff_name', resolvedName);
        sessionStorage.setItem('staff_role', resolvedRole);
        sessionStorage.setItem('staff_active_role', activeRole);
        checkStaffAuth();
      }
    }

    function logoutStaff() {
      Swal.fire({
        title: 'ยืนยันออกจากระบบ?',
        text: 'คุณต้องการออกจากระบบเจ้าหน้าที่พัสดุใช่หรือไม่',
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ออกจากระบบ',
        cancelButtonText: 'ยกเลิก'
      }).then((result) => {
        if (result.isConfirmed) {
          sessionStorage.removeItem('staff_auth');
          sessionStorage.removeItem('staff_token');
          sessionStorage.removeItem('staff_username');
          sessionStorage.removeItem('staff_name');
          sessionStorage.removeItem('staff_role');
          sessionStorage.removeItem('staff_active_role');
          checkStaffAuth(true);
        }
      });
    }

    // Navigation
    function switchStaffView(viewName) {
      document.querySelectorAll('.view-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.view-btn').forEach(el => el.classList.remove('active'));
      
      const target = document.getElementById(`view-${viewName}`);
      if (target) target.classList.add('active');

      const btns = document.querySelectorAll('.view-btn');
      if (viewName === 'requisitions' && btns[0]) btns[0].classList.add('active');
      if (viewName === 'inventory' && btns[1]) btns[1].classList.add('active');
      if (viewName === 'users' && btns[2]) btns[2].classList.add('active');
      if (viewName === 'analytics' && btns[3]) btns[3].classList.add('active');
      if (viewName === 'analytics') renderMonthlyAnalyticsView();
    }

    // Requisition Management Logic
    let currentStaffStatus = 'PENDING';
    let currentActiveReqForSig = null;

    function handleStaffReqMonthChange() {
      renderStaffRequisitions(currentStaffStatus);
    }

    function filterStaffRequisitionStatus(status, btn) {
      currentStaffStatus = status;
      document.querySelectorAll('.status-tab').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderStaffRequisitions(status);
    }

    function renderStaffRequisitions(status) {
      const reqs = getReqsDB();
      const container = document.getElementById('requisitionsContainer');
      const monthVal = document.getElementById('staffReqMonthFilter')?.value || 'ALL';

      const monthFilteredReqs = reqs.filter(r => {
        if (monthVal === 'ALL') return true;
        try {
          const parts = monthVal.split('-');
          const beYear = parseInt(parts[0], 10) + 543;
          const beMonth = parts[1];
          const bePattern = `REQ-${beYear}${beMonth}`;
          const matchesBeId = (r.id || '').startsWith(bePattern);
          const matchesCreatedAt = (r.created_at || '').startsWith(monthVal);
          return matchesBeId || matchesCreatedAt;
        } catch (e) {
          return true;
        }
      });

      const filtered = monthFilteredReqs.filter(r => r.status === status);

      // Counters
      const pendingCount = monthFilteredReqs.filter(r => r.status === 'PENDING').length;
      const verifiedCount = monthFilteredReqs.filter(r => r.status === 'VERIFIED').length;
      const approvedCount = monthFilteredReqs.filter(r => r.status === 'APPROVED').length;
      const completedCount = monthFilteredReqs.filter(r => r.status === 'COMPLETED').length;
      const rejectedCount = monthFilteredReqs.filter(r => r.status === 'REJECTED').length;

      document.getElementById('pendingCount').innerText = pendingCount;
      document.getElementById('navPendingBadge').innerText = pendingCount + verifiedCount;
      const verifiedCountEl = document.getElementById('verifiedCount');
      if (verifiedCountEl) verifiedCountEl.innerText = verifiedCount;
      document.getElementById('approvedCount').innerText = approvedCount;
      document.getElementById('completedCount').innerText = completedCount;
      const rejectedEl = document.getElementById('rejectedCount');
      if (rejectedEl) rejectedEl.innerText = rejectedCount;

      if (filtered.length === 0) {
        container.innerHTML = `
          <div style="background: white; border-radius: var(--radius); padding: 3rem; text-align: center; color: var(--neutral-400); border: 1px dashed var(--neutral-300);">
            <div style="margin-bottom: 0.5rem;">${vIcons.fileText}</div>
            <p>ไม่มีรายการคำขอในสถานะนี้ประจำเดือนที่เลือก</p>
          </div>
        `;
        return;
      }

      container.innerHTML = filtered.map(req => {
        let badgeClass = 'badge-pending';
        let badgeText = 'รอคัดกรอง';
        if (req.status === 'VERIFIED') { badgeClass = 'badge-verified'; badgeText = 'รอหัวหน้าอนุมัติ'; }
        if (req.status === 'APPROVED') { badgeClass = 'badge-approved'; badgeText = 'อนุมัติแล้ว รอผู้เบิกมารับของ'; }
        if (req.status === 'COMPLETED') { badgeClass = 'badge-completed'; badgeText = 'จ่ายของสำเร็จแล้ว'; }
        if (req.status === 'REJECTED') { badgeClass = 'badge-rejected'; badgeText = 'ไม่อนุมัติ / ยกเลิก'; }
        const reasonStr = req.reject_reason || req.rejectReason || '';

        return `
          <div class="requisition-card">
            <div class="req-top-row">
              <div class="req-doc-id">
                ${vIcons.fileText} ${req.id}
                <span class="req-badge ${badgeClass}">${badgeText}</span>
              </div>
              <span style="font-size: 0.8rem; color: var(--neutral-400); display: flex; align-items: center; gap: 4px;">
                ${vIcons.calendar} วันที่ขอ: ${req.date}
              </span>
            </div>

            <div class="req-details-grid">
              <div>${vIcons.building} <strong>หน่วยงาน:</strong> ${escapeHtml(req.dept)}</div>
              <div>${vIcons.user} <strong>ผู้ขอเบิก:</strong> ${escapeHtml(req.requester)} (${escapeHtml(req.phone || '-')})</div>
              <div style="grid-column: 1 / -1;">${vIcons.fileText} <strong>วัตถุประสงค์:</strong> ${escapeHtml(req.purpose)}</div>
              ${(req.verified_by || req.verifiedBy) ? `
                <div style="grid-column: 1 / -1; background: #f0fdf4; color: #166534; padding: 0.4rem 0.6rem; border-radius: 6px; font-size: 0.85rem; display: flex; align-items: center; gap: 6px;">
                  ${vIcons.check} <strong>คัดกรองเบื้องต้นโดย:</strong> ${escapeHtml(req.verified_by || req.verifiedBy)} ${(req.verified_date || req.verifiedDate) ? `(${escapeHtml(req.verified_date || req.verifiedDate)})` : ''}
                </div>
              ` : ''}
              ${(req.approved_by || req.approvedBy) ? `
                <div style="grid-column: 1 / -1; background: #eff6ff; color: #1e40af; padding: 0.4rem 0.6rem; border-radius: 6px; font-size: 0.85rem; display: flex; align-items: center; gap: 6px;">
                  ${vIcons.shield} <strong>อนุมัติขั้นสุดท้ายโดย:</strong> ${escapeHtml(req.approved_by || req.approvedBy)} ${(req.approved_date || req.approvedDate) ? `(${escapeHtml(req.approved_date || req.approvedDate)})` : ''}
                </div>
              ` : ''}
              ${req.status === 'COMPLETED' && (req.completed_date || req.completedDate) ? `
                <div style="grid-column: 1 / -1; background: #ecfdf5; color: #065f46; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid #a7f3d0; display: flex; align-items: center; gap: 6px;">
                  ${vIcons.check} <strong>วันที่จ่ายของ:</strong> ${escapeHtml(req.completed_date || req.completedDate)}
                </div>
              ` : ''}
              ${req.status === 'REJECTED' ? `
                <div style="grid-column: 1 / -1; background: var(--danger-light); color: #991b1b; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid #fecaca;">
                  ${reasonStr ? `<div style="margin-bottom: 3px;"><strong>เหตุผลที่ไม่อนุมัติ / ยกเลิก:</strong> ${escapeHtml(reasonStr)}</div>` : ''}
                  ${(req.rejected_date || req.rejectedDate) ? `
                    <div style="font-size: 0.8rem; color: #7f1d1d; display: flex; align-items: center; gap: 4px;">
                      ${vIcons.clock} <strong>วันที่ยกเลิก:</strong> ${escapeHtml(req.rejected_date || req.rejectedDate)}
                    </div>
                  ` : ''}
                </div>
              ` : ''}
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
                ${req.items.map(item => {
                  const safeName = escapeHtml(item.name);
                  const safeBox = escapeHtml(item.unitBox);
                  const safePiece = escapeHtml(item.unitPiece);
                  return `
                  <tr>
                    <td><strong>${safeName}</strong></td>
                    <td>${item.qtyBoxes > 0 ? `${item.qtyBoxes} ${safeBox} ` : ''}${item.qtyPieces > 0 ? `${item.qtyPieces} ${safePiece}` : ''} (${item.totalPieces.toLocaleString()} ${safePiece})</td>
                    <td style="font-weight: 600; color: var(--accent);">
                      ${(req.status === 'PENDING' || req.status === 'VERIFIED') ? `
                        <div style="display: flex; align-items: center; gap: 6px;">
                          <input type="number" id="approve-qty-${req.id}-${item.itemId}"
                                 value="${item.approvedPieces ?? item.totalPieces}"
                                 min="0" max="${item.totalPieces}"
                                 style="width: 85px; padding: 4px 6px; border: 1px solid var(--neutral-300); border-radius: 6px; font-family: inherit; font-weight: 600; text-align: right;">
                          <span>${safePiece}</span>
                        </div>
                      ` : `${(item.approvedPieces ?? item.totalPieces).toLocaleString()} ${item.unitPiece}`}
                    </td>
                    <td>
                      ${req.status === 'REJECTED'
                        ? `<span style="color: var(--danger);">ยกเลิก</span>`
                        : `<span style="color: var(--accent);">พร้อมจ่าย</span>`}
                    </td>
                  </tr>
                  `;
                }).join('')}
              </tbody>
            </table>

            <div class="req-actions">
              ${(() => {
                const activeRole = getActiveStaffRole();
                if (req.status === 'PENDING') {
                  if (activeRole === 'HEAD') {
                    return `
                      <span style="font-size: 0.825rem; color: #b45309; background: #fffbeb; border: 1px solid #fde68a; padding: 0.45rem 0.85rem; border-radius: 8px; display: inline-flex; align-items: center; gap: 6px;">
                        ${vIcons.clock} รอเจ้าหน้าที่พัสดุ ตรวจสอบและคัดกรองเบื้องต้นก่อนเสนอหัวหน้าอนุมัติ
                      </span>
                    `;
                  }
                  return `
                    <button class="btn btn-outline" style="color: var(--danger);" onclick="rejectRequisition('${req.id}')">
                      ${vIcons.x} ปฏิเสธคำขอ
                    </button>
                    <button class="btn btn-primary" onclick="verifyRequisition('${req.id}')">
                      ${vIcons.check} คัดกรองและส่งต่อให้หัวหน้าอนุมัติ
                    </button>
                  `;
                }
                if (req.status === 'VERIFIED') {
                  if (activeRole === 'STAFF') {
                    return `
                      <span style="font-size: 0.825rem; color: #1e40af; background: #eff6ff; border: 1px solid #bfdbfe; padding: 0.45rem 0.85rem; border-radius: 8px; display: inline-flex; align-items: center; gap: 6px;">
                        ${vIcons.shield} ผ่านการคัดกรองแล้ว — รอหัวหน้าหน่วยงาน กดอนุมัติขั้นสุดท้าย
                      </span>
                    `;
                  }
                  return `
                    <button class="btn btn-outline" style="color: var(--danger);" onclick="rejectRequisition('${req.id}')">
                      ${vIcons.x} ปฏิเสธคำขอ
                    </button>
                    <button class="btn btn-primary" style="background: #1e3a8a;" onclick="approveRequisition('${req.id}')">
                      ${vIcons.shield} หัวหน้าอนุมัติขั้นสุดท้าย (กันสต๊อก)
                    </button>
                  `;
                }
                if (req.status === 'APPROVED') {
                  if (activeRole === 'HEAD') {
                    return `
                      <button class="btn btn-outline" onclick="previewDocInPdf('${req.id}')">
                        ${vIcons.eye} ดูตัวอย่างใบเบิก PDF
                      </button>
                      <span style="font-size: 0.825rem; color: #047857; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 0.45rem 0.85rem; border-radius: 8px; display: inline-flex; align-items: center; gap: 6px;">
                        ${vIcons.check} อนุมัติแล้ว — รอเจ้าหน้าที่พัสดุ ส่งมอบพัสดุ
                      </span>
                    `;
                  }
                  return `
                    <button class="btn btn-outline" style="color: var(--danger);" onclick="rejectRequisition('${req.id}')">
                      ${vIcons.x} ยกเลิก / คืนสต๊อกจอง
                    </button>
                    <button class="btn btn-outline" onclick="previewDocInPdf('${req.id}')">
                      ${vIcons.eye} ดูตัวอย่างใบเบิก PDF
                    </button>
                    <button class="btn btn-success" onclick="confirmCompleteRequisition('${req.id}')">
                      ${vIcons.check} จ่ายพัสดุเรียบร้อย
                    </button>
                  `;
                }
                if (req.status === 'COMPLETED') {
                  return `
                    <button class="btn btn-outline" onclick="previewDocInPdf('${req.id}')">
                      ${vIcons.printer} พิมพ์ใบเบิกทางการ PDF
                    </button>
                  `;
                }
                if (req.status === 'REJECTED') {
                  return `
                    <button class="btn btn-outline" onclick="previewDocInPdf('${req.id}')">
                      ${vIcons.eye} ดูใบคำขอ PDF
                    </button>
                  `;
                }
                return '';
              })()}
            </div>
          </div>
        `;
      }).join('');
    }

    function verifyRequisition(docNo) {
      if (getActiveStaffRole() === 'HEAD') {
        Swal.fire({
          icon: 'warning',
          title: 'จำกัดสิทธิ์ตามบทบาท',
          text: 'สิทธิ์หัวหน้าหน่วยงาน สำหรับอนุมัติขั้นสุดท้ายเท่านั้น การคัดกรองเบื้องต้นเป็นหน้าที่ของเจ้าหน้าที่พัสดุ',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        });
        return;
      }
      const reqs = getReqsDB();
      const req = reqs.find(r => r.id === docNo);
      if (!req) return;

      const updatedItems = (req.items || []).map(i => {
        const inputEl = document.getElementById(`approve-qty-${docNo}-${i.itemId}`);
        const val = inputEl ? parseInt(inputEl.value, 10) : (i.approvedPieces ?? i.totalPieces);
        const cleanVal = isNaN(val) || val < 0 ? 0 : val;
        return { ...i, approvedPieces: cleanVal };
      });

      Swal.fire({
        title: 'ยืนยันคัดกรองคำขอ?',
        html: `คุณกำลังคัดกรองคำขอเลขที่ <b>${docNo}</b> เพื่อเสนอให้หัวหน้าอนุมัติขั้นสุดท้าย`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#1e40af',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'คัดกรองและส่งต่อหัวหน้า',
        cancelButtonText: 'ยกเลิก'
      }).then(async (result) => {
        if (result.isConfirmed) {
          const now = new Date();
          const staffUser = getLoggedInStaff();
          const verifiedBy = staffUser ? (staffUser.name || staffUser.username) : 'เจ้าหน้าที่พัสดุ สวท.';
          const verifiedDate = formatThaiDatetime(now);

          const apiRes = await postToMySQLAPI('verifyRequisition', {
            docNo: docNo,
            verifiedBy: verifiedBy,
            verifiedDate: verifiedDate,
            items: updatedItems.map(i => ({ itemId: i.itemId, approvedPieces: i.approvedPieces }))
          });
          if (apiRes && apiRes.status === 'error' && apiRes.code && apiRes.code !== 'DB_ERROR' && apiRes.code !== 'MYSQL_CONNECTION_ERROR') {
            Swal.fire({
              icon: 'error',
              title: 'ไม่สามารถคัดกรองคำขอได้',
              text: apiRes.message || 'เกิดข้อผิดพลาดจากเซิร์ฟเวอร์',
              confirmButtonColor: '#1e40af',
              confirmButtonText: 'ตกลง'
            });
            return;
          }

          req.status = 'VERIFIED';
          req.items = updatedItems;
          req.verified_by = verifiedBy;
          req.verified_at = now.toISOString();
          req.verified_date = verifiedDate;
          req.updated_at = now.toISOString();
          saveReqsDB(reqs);

          renderStaffRequisitions(currentStaffStatus);
          Swal.fire({
            icon: 'success',
            title: 'คัดกรองสำเร็จ',
            text: `ส่งคำขอ ${docNo} ให้หัวหน้าพิจารณาอนุมัติแล้ว`,
            confirmButtonColor: '#1e40af',
            confirmButtonText: 'ตกลง'
          });
        }
      });
    }

    function approveRequisition(docNo) {
      if (getActiveStaffRole() === 'STAFF') {
        Swal.fire({
          icon: 'warning',
          title: 'จำกัดสิทธิ์ตามบทบาท',
          text: 'สิทธิ์เจ้าหน้าที่พัสดุ ไม่สามารถกดอนุมัติคำขอขั้นสุดท้ายได้ ต้องให้หัวหน้าหน่วยงาน เป็นผู้อนุมัติ',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        });
        return;
      }
      const reqs = getReqsDB();
      const items = getItemsDB();
      const req = reqs.find(r => r.id === docNo);
      if (!req) return;

      // Read partial or full approved quantities from inputs
      const updatedItems = req.items.map(i => {
        const inputEl = document.getElementById(`approve-qty-${docNo}-${i.itemId}`);
        const val = inputEl ? parseInt(inputEl.value, 10) : (i.approvedPieces ?? i.totalPieces);
        const cleanVal = isNaN(val) || val < 0 ? 0 : val;
        return { ...i, approvedPieces: cleanVal };
      });

      // Validate stock availability before locking Reserved
      for (const i of updatedItems) {
        const itm = items.find(si => si.id === i.itemId);
        if (itm) {
          const avail = Math.max(0, itm.on_hand_pieces - itm.reserved_pieces);
          if (i.approvedPieces > avail) {
            Swal.fire({
              icon: 'error',
              title: 'สต๊อกพร้อมเบิกไม่เพียงพอ',
              html: `รายการ <b>${itm.name}</b> มีพร้อมเบิกเพียง <b>${avail.toLocaleString()} ${itm.unit_piece_name}</b> (ต้องการอนุมัติ ${i.approvedPieces.toLocaleString()} ${itm.unit_piece_name})`,
              confirmButtonColor: '#1e40af',
              confirmButtonText: 'ตกลง'
            });
            return;
          }
        }
      }

      Swal.fire({
        title: 'ยืนยันการอนุมัติขั้นสุดท้าย (หัวหน้า)?',
        html: `
          <div style="text-align: left; font-size: 0.95rem; margin-top: 0.5rem; color: #475569; line-height: 1.6;">
            <p><strong>เลขที่เอกสาร:</strong> <span style="color: #1e40af; font-weight: 700;">${docNo}</span></p>
            <p><strong>ผู้ขอเบิก:</strong> ${escapeHtml(req.requester)} (${escapeHtml(req.dept)})</p>
            <p><strong>จำนวนพัสดุ:</strong> ${req.items.length} รายการ</p>
            <div style="margin-top: 0.5rem; padding: 0.5rem 0.75rem; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; color: #1e40af; font-size: 0.85rem;">
              • หัวหน้าอนุมัติคำขอขั้นสุดท้าย และระบบทำการกันยอดสต๊อก ทันที
            </div>
          </div>
        `,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#1e40af',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'อนุมัติขั้นสุดท้าย (กันสต๊อก)',
        cancelButtonText: 'ยกเลิก'
      }).then(async (result) => {
        if (result.isConfirmed) {
          const now = new Date();
          const staffUser = getLoggedInStaff();
          const approvedBy = staffUser ? (staffUser.name || staffUser.username) : 'หัวหน้า/ผู้อำนวยการ สวท.';
          const approvedDate = formatThaiDatetime(now);

          const apiRes = await postToMySQLAPI('approveRequisition', {
            docNo: docNo,
            approvedBy: approvedBy,
            approvedDate: approvedDate,
            items: updatedItems.map(i => ({ itemId: i.itemId, approvedPieces: i.approvedPieces }))
          });
          if (apiRes && apiRes.status === 'error' && apiRes.code && apiRes.code !== 'DB_ERROR' && apiRes.code !== 'MYSQL_CONNECTION_ERROR') {
            Swal.fire({
              icon: 'error',
              title: 'ไม่สามารถอนุมัติคำขอได้',
              text: apiRes.message || 'เกิดข้อผิดพลาดจากเซิร์ฟเวอร์',
              confirmButtonColor: '#1e40af',
              confirmButtonText: 'ตกลง'
            });
            return;
          }

          req.status = 'APPROVED';
          req.updated_at = now.toISOString();
          req.approved_at = now.toISOString();
          req.items = updatedItems;
          req.approved_by = approvedBy;
          req.approved_date = approvedDate;
          req.items.forEach(i => {
            const itm = items.find(si => si.id === i.itemId);
            if (itm) itm.reserved_pieces += i.approvedPieces;
          });
          saveReqsDB(reqs);
          saveItemsDB(items);
          renderStaffRequisitions(currentStaffStatus);
          renderInventoryTable();

          Swal.fire({
            icon: 'success',
            title: 'อนุมัติขั้นสุดท้ายสำเร็จ!',
            text: `คำขอเลขที่ ${docNo} ได้รับการอนุมัติและกันสต๊อกเรียบร้อยแล้ว`,
            confirmButtonColor: '#1e40af',
            confirmButtonText: 'ตกลง'
          });
        }
      });
    }

    function rejectRequisition(docNo) {
      const reqs = getReqsDB();
      const targetReq = reqs.find(r => r.id === docNo);
      if (!targetReq) return;
      const wasApproved = targetReq.status === 'APPROVED';

      Swal.fire({
        title: wasApproved ? 'ยกเลิกคำขอและคืนสต๊อกจอง' : 'ปฏิเสธคำขอเบิกพัสดุ',
        text: `ระบุเหตุผลในการ${wasApproved ? 'ยกเลิกและคืนยอดจอง' : 'ไม่อนุมัติ'}คำขอเลขที่ ${docNo}:`,
        input: 'textarea',
        inputPlaceholder: 'เช่น พัสดุในคลังไม่เพียงพอ, ผู้เบิกขอยกเลิก, เกินกำหนดเวลารับของ...',
        inputValue: wasApproved ? 'ผู้ขอเบิกขอยกเลิกรายการ / เกินกำหนดเวลารับพัสดุ (คืนยอดจองเข้าคลัง)' : 'พัสดุในคลังไม่เพียงพอสำหรับรอบการเบิกนี้',
        showCancelButton: true,
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#64748b',
        confirmButtonText: wasApproved ? 'ยืนยันยกเลิกและคืนสต๊อก' : 'ยืนยันปฏิเสธคำขอ',
        cancelButtonText: 'ยกเลิก',
        inputValidator: (val) => {
          if (!val || !val.trim()) {
            return 'กรุณาระบุเหตุผลครับ!';
          }
        }
      }).then((result) => {
        if (result.isConfirmed && result.value) {
          const items = getItemsDB();
          const req = reqs.find(r => r.id === docNo);
          if (req) {
            // If previously APPROVED, release reserved_pieces back to stock
            if (req.status === 'APPROVED') {
              req.items.forEach(i => {
                const itm = items.find(si => si.id === i.itemId);
                if (itm) {
                  itm.reserved_pieces = Math.max(0, itm.reserved_pieces - (i.approvedPieces ?? i.totalPieces));
                }
              });
              saveItemsDB(items);
            }
            const now = new Date();
            const thaiNow = getThaiDatetime(now);
            req.status = 'REJECTED';
            req.reject_reason = result.value.trim();
            req.rejectReason = result.value.trim();
            req.rejected_at = now.toISOString();
            req.rejected_date = thaiNow;
            req.rejectedDate = thaiNow;
            req.updated_at = now.toISOString();
            saveReqsDB(reqs);
            postToMySQLAPI('rejectRequisition', { docNo: docNo, reason: req.reject_reason, rejected_date: thaiNow });
            renderStaffRequisitions(currentStaffStatus);
            renderInventoryTable();

            Swal.fire({
              icon: 'warning',
              title: wasApproved ? 'ยกเลิกและคืนยอดสต๊อกเรียบร้อยแล้ว' : 'ปฏิเสธคำขอเรียบร้อยแล้ว',
              text: `คำขอ ${docNo} ถูกเปลี่ยนสถานะเป็นไม่อนุมัติ/ยกเลิกเรียบร้อยแล้ว`,
              confirmButtonColor: '#1e40af',
              confirmButtonText: 'ตกลง'
            });
          }
        }
      });
    }

    // Complete Requisition (No Signature required)
    function confirmCompleteRequisition(docNo) {
      const reqs = getReqsDB();
      const req = reqs.find(r => r.id === docNo);
      if (!req) return;

      Swal.fire({
        title: 'ยืนยันการจ่ายพัสดุ?',
        html: `
          <div style="font-size: 0.95rem; color: #475569; margin: 0.5rem 0; text-align: left;">
            <div>เลขที่คำขอ: <strong style="color: #0f172a;">${docNo}</strong></div>
            <div>ผู้ขอเบิก: <strong style="color: #0f172a;">${escapeHtml(req.requester)}</strong> (${escapeHtml(req.dept)})</div>
            <div style="margin-top: 8px; color: #16a34a; font-weight: 600;">
              ระบบจะทำการตัดยอดสต๊อกคงคลังจริงทันที
            </div>
          </div>
        `,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#059669',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ยืนยันจ่ายพัสดุ',
        cancelButtonText: 'ยกเลิก'
      }).then((res) => {
        if (!res.isConfirmed) return;

        const items = getItemsDB();
        const now = new Date();
        const thaiNow = getThaiDatetime(now);
        req.status = 'COMPLETED';
        req.completed_at = now.toISOString();
        req.completed_date = thaiNow;
        req.completedDate = thaiNow;
        req.updated_at = now.toISOString();

        // Deduct permanently from On-Hand and release Reserved
        const staffUser = getLoggedInStaff();
        const recBy = staffUser ? (staffUser.name || staffUser.username) : 'เจ้าหน้าที่พัสดุ สวท.';
        req.items.forEach(i => {
          const itm = items.find(si => si.id === i.itemId);
          if (itm) {
            const deductQty = i.approvedPieces ?? i.totalPieces;
            itm.on_hand_pieces = Math.max(0, itm.on_hand_pieces - deductQty);
            itm.reserved_pieces = Math.max(0, (itm.reserved_pieces || 0) - deductQty);
            recordLocalTransaction({
              itemId: itm.id,
              itemName: itm.name,
              unitPiece: itm.unit_piece_name,
              transactionType: 'OUT',
              changePieces: -deductQty,
              balanceAfter: itm.on_hand_pieces,
              referenceType: 'REQUISITION',
              referenceId: req.id,
              reason: `จ่ายพัสดุตามใบเบิก ${req.id} (${req.dept})`,
              recordedBy: recBy,
              formattedDate: thaiNow
            });
          }
        });

        saveReqsDB(reqs);
        saveItemsDB(items);
        postToMySQLAPI('completeRequisition', {
          docNo: req.id,
          completed_date: thaiNow,
          recordedBy: recBy
        });

        renderStaffRequisitions('APPROVED');
        renderInventoryTable();

        Swal.fire({
          icon: 'success',
          title: 'จ่ายพัสดุเรียบร้อยแล้ว',
          text: `คำขอ ${docNo} ดำเนินการตัดยอดสต๊อกคงคลังจริงเรียบร้อยแล้ว`,
          confirmButtonColor: '#059669',
          confirmButtonText: 'ดูใบเบิกทางการ PDF'
        }).then(() => {
          previewDocInPdf(req.id);
        });
      });
    }

    function openStockInModal(preselectedItemId = null) {
      const items = getItemsDB();

      Swal.fire({
        title: 'บันทึกรับเข้าพัสดุใหม่',
        html: `
          <div style="text-align: left; display: flex; flex-direction: column; gap: 0.85rem; margin-top: 0.5rem;">
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">
                เลือกรายการพัสดุ: *
              </label>
              <div style="position: relative;">
                <div style="position: relative; display: flex; align-items: center;">
                  <input type="text" id="swalStockSearchInput" class="swal2-input" 
                         placeholder="พิมพ์ชื่อพัสดุเพื่อค้นหา (เช่น ซอง, กระดาษ, แม็ก)..." 
                         autocomplete="off"
                         style="width: 100%; margin: 0; height: 42px; font-size: 0.95rem; padding: 0.5rem 2.4rem 0.5rem 0.75rem; border-radius: 8px; border: 1px solid #cbd5e1; box-sizing: border-box;">
                  <button type="button" id="swalStockToggleBtn" 
                          style="position: absolute; right: 8px; background: none; border: none; cursor: pointer; color: #64748b; padding: 4px; display: flex; align-items: center;">
                    <svg class="svg-icon" viewBox="0 0 24 24" style="width: 18px; height: 18px; stroke: currentColor; fill: none; stroke-width: 2;"><polyline points="6 9 12 15 18 9"/></svg>
                  </button>
                </div>
                <!-- Hidden input swalStockItem to maintain backward compatibility -->
                <input type="hidden" id="swalStockItem" value="">

                <!-- Dropdown list -->
                <div id="swalStockDropdownList" 
                     style="position: absolute; top: calc(100% + 4px); left: 0; right: 0; background: white; border: 1px solid #cbd5e1; border-radius: 8px; max-height: 220px; overflow-y: auto; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15); z-index: 9999; display: none;">
                </div>
              </div>

              <!-- Selected Item Info Badge -->
              <div id="swalStockItemBadge" 
                   style="margin-top: 6px; font-size: 0.825rem; color: #1e40af; background: #eff6ff; border: 1px solid #bfdbfe; padding: 6px 12px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
                <span>คงเหลือปัจจุบัน: <strong>0</strong></span>
                <span style="color: #64748b;">อัตราส่วน: -</span>
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
              <div>
                <label id="swalStockBoxLabel" style="font-size: 0.85rem; font-weight: 600; color: #475569; display: block; margin-bottom: 4px;">จำนวนหน่วยใหญ่:</label>
                <input type="number" id="swalStockBoxes" min="0" placeholder="0" class="swal2-input" style="width: 100%; margin: 0; height: 42px; font-size: 1rem; border-radius: 8px; border: 1px solid #cbd5e1; box-sizing: border-box; padding: 0.5rem 0.75rem;">
              </div>
              <div>
                <label id="swalStockPieceLabel" style="font-size: 0.85rem; font-weight: 600; color: #475569; display: block; margin-bottom: 4px;">จำนวนหน่วยย่อย:</label>
                <input type="number" id="swalStockQty" min="0" placeholder="0" class="swal2-input" style="width: 100%; margin: 0; height: 42px; font-size: 1rem; border-radius: 8px; border: 1px solid #cbd5e1; box-sizing: border-box; padding: 0.5rem 0.75rem;">
              </div>
            </div>

            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem;">
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                <div>
                  <label style="font-size: 0.825rem; font-weight: 600; color: #0369a1; display: block; margin-bottom: 4px;">วิธีระบุราคาสินค้าที่ซื้อเข้า:</label>
                  <select id="swalStockPriceMode" class="swal2-input" style="width: 100%; margin: 0; height: 40px; font-size: 0.875rem; border-radius: 8px; border: 1px solid #cbd5e1;">
                    <option value="TOTAL" selected>ยอดเงินรวมทั้งครั้ง</option>
                    <option value="PER_BOX">ราคาต่อหน่วยใหญ่</option>
                    <option value="PER_PIECE">ราคาต่อหน่วยย่อย</option>
                  </select>
                </div>
                <div>
                  <label id="swalStockPriceLabel" style="font-size: 0.825rem; font-weight: 600; color: #0369a1; display: block; margin-bottom: 4px;">ราคา / จำนวนเงิน (บาท):</label>
                  <input type="number" id="swalStockPriceInput" min="0" step="0.01" placeholder="0.00" class="swal2-input" style="width: 100%; margin: 0; height: 40px; font-size: 0.95rem; border-radius: 8px; border: 1px solid #cbd5e1; box-sizing: border-box; padding: 0.5rem 0.75rem;">
                </div>
              </div>
              <div id="swalStockPriceHint" style="font-size: 0.76rem; color: #64748b; margin-top: 6px;">ใส่ 0 หากยังไม่ทราบราคาหรือไม่คิดค่าใช้จ่าย</div>
              <div id="swalStockCostPreview" style="margin-top: 6px; padding: 6px 10px; border-radius: 6px; background: #e0f2fe; border: 1px solid #bae6fd; font-size: 0.8rem; color: #0369a1; font-weight: 600; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
                <span>รับเข้า: 0 ชิ้น</span>
                <span>เฉลี่ย: 0.00 บาท/ชิ้น | ยอดเงินรวม: 0.00 บาท</span>
              </div>
            </div>

            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #475569; display: block; margin-bottom: 4px;">หมายเหตุ / เลขที่ใบส่งของ:</label>
              <input type="text" id="swalStockNote" placeholder="เช่น PO-2569-001 หรือ รับเข้าประจำเดือน..." class="swal2-input" style="width: 100%; margin: 0; height: 42px; font-size: 0.9rem; border-radius: 8px; border: 1px solid #cbd5e1; box-sizing: border-box; padding: 0.5rem 0.75rem;">
            </div>
          </div>
        `,
        showCancelButton: true,
        confirmButtonColor: '#1e40af',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ยืนยันรับเข้าคลัง',
        cancelButtonText: 'ยกเลิก',
        didOpen: () => {
          const searchInput = document.getElementById('swalStockSearchInput');
          const dropdownList = document.getElementById('swalStockDropdownList');
          const hiddenInput = document.getElementById('swalStockItem');
          const badgeEl = document.getElementById('swalStockItemBadge');
          const toggleBtn = document.getElementById('swalStockToggleBtn');
          const boxLabelEl = document.getElementById('swalStockBoxLabel');
          const pieceLabelEl = document.getElementById('swalStockPieceLabel');
          const boxesEl = document.getElementById('swalStockBoxes');
          const piecesEl = document.getElementById('swalStockQty');
          const priceModeEl = document.getElementById('swalStockPriceMode');
          const priceInputEl = document.getElementById('swalStockPriceInput');
          const priceLabelEl = document.getElementById('swalStockPriceLabel');
          const priceHintEl = document.getElementById('swalStockPriceHint');
          const costPreviewEl = document.getElementById('swalStockCostPreview');

          function calcRestockPricing(itm) {
            const ratio = (itm && itm.is_multi_unit) ? (Number(itm.pieces_per_box) || 1) : 1;
            const boxes = parseInt(boxesEl?.value, 10) || 0;
            const pieces = parseInt(piecesEl?.value, 10) || 0;
            const totalAdded = (boxes * ratio) + pieces;
            const mode = priceModeEl ? priceModeEl.value : 'TOTAL';
            const rawPrice = parseFloat(priceInputEl?.value);
            const val = Number.isFinite(rawPrice) && rawPrice > 0 ? rawPrice : 0;

            let unitPrice = 0;
            let totalCost = 0;
            if (val > 0) {
              if (mode === 'PER_BOX') {
                unitPrice = ratio > 0 ? Math.round((val / ratio) * 100) / 100 : 0;
                totalCost = totalAdded > 0 ? Math.round(((totalAdded / ratio) * val) * 100) / 100 : 0;
              } else if (mode === 'PER_PIECE') {
                unitPrice = Math.round(val * 100) / 100;
                totalCost = Math.round((totalAdded * unitPrice) * 100) / 100;
              } else {
                totalCost = Math.round(val * 100) / 100;
                unitPrice = totalAdded > 0 ? Math.round((totalCost / totalAdded) * 100) / 100 : 0;
              }
            }
            return { totalAdded, unitPrice, totalCost, ratio, mode };
          }

          function updateCostPreview() {
            const id = parseInt(hiddenInput.value, 10);
            const itm = items.find(i => Number(i.id) === id);
            const pUnit = itm ? (itm.unit_piece_name || 'ชิ้น') : 'ชิ้น';
            const bUnit = itm ? (itm.unit_box_name || 'กล่อง') : 'กล่อง';
            const { totalAdded, unitPrice, totalCost, mode } = calcRestockPricing(itm);
            if (priceLabelEl) {
              if (mode === 'PER_BOX') priceLabelEl.innerText = `ราคาต่อ${bUnit} (บาท):`;
              else if (mode === 'PER_PIECE') priceLabelEl.innerText = `ราคาต่อ${pUnit} (บาท):`;
              else priceLabelEl.innerText = 'ยอดเงินรวมทั้งครั้ง (บาท):';
            }
            if (costPreviewEl) {
              const fmtUnit = unitPrice.toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
              const fmtTotal = totalCost.toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
              costPreviewEl.innerHTML = `
                <span>รับเข้า: <strong>${totalAdded.toLocaleString()}</strong> ${escapeHtml(pUnit)}</span>
                <span>เฉลี่ย: <strong>${fmtUnit}</strong> บาท/${escapeHtml(pUnit)} | ยอดเงินรวม: <strong style="color:#0c4a6e;">${fmtTotal}</strong> บาท</span>
              `;
            }
          }

          function renderList(query = '') {
            const cleanQuery = query.trim().toLowerCase();
            const filtered = items.filter(i =>
              !cleanQuery ||
              (i.name && i.name.toLowerCase().includes(cleanQuery)) ||
              (i.category && i.category.toLowerCase().includes(cleanQuery))
            );

            if (filtered.length === 0) {
              dropdownList.innerHTML = `
                <div style="padding: 1rem; text-align: center; color: #94a3b8; font-size: 0.875rem;">
                  ไม่พบรายการพัสดุที่ตรงกับ "${query}"
                </div>
              `;
              return;
            }

            dropdownList.innerHTML = filtered.map(i => {
              const isSelected = Number(hiddenInput.value) === Number(i.id);
              const ratioTxt = i.is_multi_unit ? `1 ${i.unit_box_name} = ${i.pieces_per_box} ${i.unit_piece_name}` : `1 ${i.unit_piece_name}`;
              return `
                <div class="swal-stock-item-row" data-id="${i.id}" style="
                  padding: 8px 12px;
                  cursor: pointer;
                  border-bottom: 1px solid #f1f5f9;
                  display: flex;
                  justify-content: space-between;
                  align-items: center;
                  background: ${isSelected ? '#eff6ff' : 'white'};
                  transition: background 0.15s;
                ">
                  <div style="text-align: left;">
                    <div style="font-weight: 600; font-size: 0.875rem; color: ${isSelected ? '#1e40af' : '#1e293b'};">${i.name}</div>
                    <div style="font-size: 0.75rem; color: #64748b;">${i.category || 'พัสดุทั่วไป'} • <span style="color: #475569;">[${ratioTxt}]</span></div>
                  </div>
                  <span style="font-size: 0.75rem; background: ${i.on_hand_pieces > 0 ? '#dcfce7' : '#fee2e2'}; color: ${i.on_hand_pieces > 0 ? '#166534' : '#991b1b'}; padding: 2px 8px; border-radius: 999px; font-weight: 600; white-space: nowrap; margin-left: 8px;">
                    ${Number(i.on_hand_pieces).toLocaleString()} ${i.unit_piece_name}
                  </span>
                </div>
              `;
            }).join('');

            dropdownList.querySelectorAll('.swal-stock-item-row').forEach(row => {
              row.addEventListener('click', () => {
                const id = parseInt(row.getAttribute('data-id'), 10);
                selectItem(id);
              });
              row.addEventListener('mouseenter', () => {
                row.style.background = '#f8fafc';
              });
              row.addEventListener('mouseleave', () => {
                const id = parseInt(row.getAttribute('data-id'), 10);
                row.style.background = (Number(hiddenInput.value) === id) ? '#eff6ff' : 'white';
              });
            });
          }

          function selectItem(id) {
            const itm = items.find(i => Number(i.id) === Number(id));
            if (!itm) return;
            hiddenInput.value = itm.id;
            searchInput.value = itm.name;

            const ratioTxt = itm.is_multi_unit ? `1 ${itm.unit_box_name} = ${itm.pieces_per_box} ${itm.unit_piece_name}` : `1 ${itm.unit_piece_name}`;
            if (badgeEl) {
              badgeEl.innerHTML = `
                <span>คงเหลือปัจจุบัน: <strong style="color: #1e40af;">${Number(itm.on_hand_pieces).toLocaleString()}</strong> ${itm.unit_piece_name}</span>
                <span style="font-size: 0.75rem; color: #64748b;">อัตราส่วน: ${ratioTxt}</span>
              `;
            }
            if (boxLabelEl) {
              boxLabelEl.innerHTML = `จำนวนหน่วยใหญ่ (<strong>${itm.unit_box_name || 'กล่อง'}</strong>):`;
            }
            if (pieceLabelEl) {
              pieceLabelEl.innerHTML = `จำนวนหน่วยย่อย (<strong>${itm.unit_piece_name || 'ชิ้น'}</strong>):`;
            }
            if (priceHintEl) {
              const lastP = Number(itm.last_unit_price || 0);
              priceHintEl.innerText = lastP > 0
                ? `ราคาล่าสุดในระบบ: ${lastP.toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} บาท/${itm.unit_piece_name || 'ชิ้น'} (ใส่ 0 หากไม่ระบุราคา)`
                : 'ใส่ 0 หากยังไม่ทราบราคาหรือไม่คิดค่าใช้จ่าย';
            }
            dropdownList.style.display = 'none';
            updateCostPreview();
          }

          if (boxesEl) boxesEl.addEventListener('input', updateCostPreview);
          if (piecesEl) piecesEl.addEventListener('input', updateCostPreview);
          if (priceModeEl) priceModeEl.addEventListener('change', updateCostPreview);
          if (priceInputEl) priceInputEl.addEventListener('input', updateCostPreview);
          enhanceAllSearchableSelects();

          searchInput.addEventListener('focus', () => {
            renderList(searchInput.value);
            dropdownList.style.display = 'block';
          });
          searchInput.addEventListener('input', (e) => {
            renderList(e.target.value);
            dropdownList.style.display = 'block';
          });
          toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (dropdownList.style.display === 'block') {
              dropdownList.style.display = 'none';
            } else {
              renderList(searchInput.value);
              dropdownList.style.display = 'block';
              searchInput.focus();
            }
          });

          document.addEventListener('click', (e) => {
            if (!e.target.closest('#swalStockDropdownList') && e.target !== searchInput && e.target !== toggleBtn) {
              dropdownList.style.display = 'none';
            }
          });

          // Preselect first item or preselectedItemId
          const initId = preselectedItemId || (items.length > 0 ? items[0].id : null);
          if (initId) {
            selectItem(initId);
          }
        },
        preConfirm: () => {
          const itemId = parseInt(document.getElementById('swalStockItem').value, 10);
          if (!itemId) {
            Swal.showValidationMessage('กรุณาเลือกรายการพัสดุจากรายการค้นหา');
            return false;
          }
          const boxes = parseInt(document.getElementById('swalStockBoxes').value, 10) || 0;
          const pieces = parseInt(document.getElementById('swalStockQty').value, 10) || 0;
          const priceMode = document.getElementById('swalStockPriceMode')?.value || 'TOTAL';
          const rawPriceInput = (document.getElementById('swalStockPriceInput')?.value || '').trim();
          const rawPrice = rawPriceInput === '' ? 0 : parseFloat(rawPriceInput);
          const note = (document.getElementById('swalStockNote')?.value || '').trim() || 'รับพัสดุเข้าคลัง';
          if (boxes <= 0 && pieces <= 0) {
            Swal.showValidationMessage('กรุณาระบุจำนวนที่รับเข้าอย่างน้อย 1 กล่องหรือ 1 ชิ้นครับ');
            return false;
          }
          if (!Number.isFinite(rawPrice) || rawPrice < 0) {
            Swal.showValidationMessage('กรุณาระบุราคาหรือยอดเงินตั้งแต่ 0 ขึ้นไป');
            return false;
          }
          return { itemId, boxes, pieces, priceMode, rawPrice, note };
        }
      }).then((res) => {
        if (res.isConfirmed && res.value) {
          const { itemId, boxes, pieces, priceMode, rawPrice, note } = res.value;
          const items = getItemsDB();
          const itm = items.find(i => i.id === itemId);
          if (itm) {
            const ratio = itm.is_multi_unit ? (itm.pieces_per_box || 1) : 1;
            const totalAdded = (boxes * ratio) + pieces;
            let unitPrice = 0;
            let totalCost = 0;
            if (rawPrice > 0) {
              if (priceMode === 'PER_BOX') {
                unitPrice = ratio > 0 ? Math.round((rawPrice / ratio) * 100) / 100 : 0;
                totalCost = totalAdded > 0 ? Math.round(((totalAdded / ratio) * rawPrice) * 100) / 100 : 0;
              } else if (priceMode === 'PER_PIECE') {
                unitPrice = Math.round(rawPrice * 100) / 100;
                totalCost = Math.round((totalAdded * unitPrice) * 100) / 100;
              } else {
                totalCost = Math.round(rawPrice * 100) / 100;
                unitPrice = totalAdded > 0 ? Math.round((totalCost / totalAdded) * 100) / 100 : 0;
              }
            }
            const nowStr = formatThaiDatetime(new Date());
            itm.on_hand_pieces += totalAdded;
            itm.last_restocked_at = nowStr;
            if (unitPrice > 0) {
              itm.last_unit_price = unitPrice;
            }
            saveItemsDB(items);
            const staffUser = getLoggedInStaff();
            const recBy = staffUser ? (staffUser.name || staffUser.username) : 'เจ้าหน้าที่พัสดุ สวท.';
            recordLocalTransaction({
              itemId: itm.id,
              itemName: itm.name,
              unitPiece: itm.unit_piece_name,
              transactionType: 'IN',
              changePieces: totalAdded,
              balanceAfter: itm.on_hand_pieces,
              unitPrice: unitPrice,
              totalCost: totalCost,
              referenceType: 'STOCK_IN',
              referenceId: '',
              reason: note,
              recordedBy: recBy,
              formattedDate: nowStr
            });
            postToMySQLAPI('restockItem', {
              itemId: itm.id,
              quantityPieces: totalAdded,
              unitPrice: unitPrice,
              totalCost: totalCost,
              note: note,
              recordedBy: recBy
            });
            renderInventoryTable();

            const costText = totalCost > 0
              ? ` มูลค่าซื้อเข้า ${totalCost.toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} บาท (เฉลี่ย ${unitPrice.toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} บาท/${itm.unit_piece_name})`
              : '';
            Swal.fire({
              icon: 'success',
              title: 'รับเข้าพัสดุสำเร็จ!',
              text: `เพิ่ม "${itm.name}" รวม ${totalAdded.toLocaleString()} ${itm.unit_piece_name} เข้าสต๊อกเรียบร้อยแล้ว${costText}`,
              confirmButtonColor: '#1e40af',
              confirmButtonText: 'ตกลง'
            });
          }
        }
      });
    }

    function openStockAdjustModal(preselectedItemId = null) {
      const items = getItemsDB();

      Swal.fire({
        title: 'ปรับยอดสต๊อกจริง',
        html: `
          <div style="text-align: left; display: flex; flex-direction: column; gap: 0.85rem; margin-top: 0.5rem;">
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">
                เลือกรายการพัสดุ: *
              </label>
              <div style="position: relative;">
                <div style="position: relative; display: flex; align-items: center;">
                  <input type="text" id="swalAdjSearchInput" class="swal2-input" 
                         placeholder="พิมพ์ชื่อพัสดุเพื่อค้นหา..." 
                         autocomplete="off"
                         style="width: 100%; margin: 0; height: 42px; font-size: 0.95rem; padding: 0.5rem 2.4rem 0.5rem 0.75rem; border-radius: 8px; border: 1px solid #cbd5e1; box-sizing: border-box;">
                  <button type="button" id="swalAdjToggleBtn" 
                          style="position: absolute; right: 8px; background: none; border: none; cursor: pointer; color: #64748b; padding: 4px; display: flex; align-items: center;">
                    <svg class="svg-icon" viewBox="0 0 24 24" style="width: 18px; height: 18px; stroke: currentColor; fill: none; stroke-width: 2;"><polyline points="6 9 12 15 18 9"/></svg>
                  </button>
                </div>
                <input type="hidden" id="swalAdjItem" value="">

                <!-- Dropdown list -->
                <div id="swalAdjDropdownList" 
                     style="position: absolute; top: calc(100% + 4px); left: 0; right: 0; background: white; border: 1px solid #cbd5e1; border-radius: 8px; max-height: 220px; overflow-y: auto; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15); z-index: 9999; display: none;">
                </div>
              </div>

              <!-- Selected Item Info Badge -->
              <div id="swalAdjItemBadge" 
                   style="margin-top: 6px; font-size: 0.825rem; color: #1e40af; background: #eff6ff; border: 1px solid #bfdbfe; padding: 6px 12px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
                <span>ยอดคงคลังปัจจุบัน: <strong>0</strong> ชิ้น</span>
                <span style="color: #64748b;">หมวด: -</span>
              </div>
            </div>

            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span>ยอดคงคลังจริงที่ตรวจนับได้ (หน่วยย่อย): *</span>
                <span id="swalAdjUnitBadge" style="font-size: 0.775rem; color: #475569; background: #f1f5f9; padding: 2px 8px; border-radius: 4px;">หน่วยนับ: <strong id="swalAdjUnitLabel">ชิ้น</strong></span>
              </label>
              <input type="number" id="swalAdjNewQty" min="0" placeholder="ระบุยอดคงคลังจริงจากการตรวจนับ" class="swal2-input" 
                     style="width: 100%; margin: 0; height: 42px; font-size: 1rem; border-radius: 8px; border: 1px solid #cbd5e1; box-sizing: border-box; padding: 0.5rem 0.75rem;">
            </div>

            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">เหตุผลในการปรับยอดสต๊อก: *</label>
              <select id="swalAdjReason" class="swal2-select" style="width: 100%; margin: 0; font-family: inherit; font-size: 0.9rem; padding: 0.55rem; border-radius: 8px; border: 1px solid #cbd5e1; box-sizing: border-box; background: white;">
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
        didOpen: () => {
          const searchInput = document.getElementById('swalAdjSearchInput');
          const dropdownList = document.getElementById('swalAdjDropdownList');
          const hiddenInput = document.getElementById('swalAdjItem');
          const badgeEl = document.getElementById('swalAdjItemBadge');
          const unitLabelEl = document.getElementById('swalAdjUnitLabel');
          const toggleBtn = document.getElementById('swalAdjToggleBtn');

          function renderList(query = '') {
            const cleanQuery = query.trim().toLowerCase();
            const filtered = items.filter(i =>
              !cleanQuery ||
              (i.name && i.name.toLowerCase().includes(cleanQuery)) ||
              (i.category && i.category.toLowerCase().includes(cleanQuery))
            );

            if (filtered.length === 0) {
              dropdownList.innerHTML = `
                <div style="padding: 1rem; text-align: center; color: #94a3b8; font-size: 0.875rem;">
                  ไม่พบรายการพัสดุที่ตรงกับคำค้น "${query}"
                </div>
              `;
              return;
            }

            dropdownList.innerHTML = filtered.map(i => {
              const isSelected = Number(hiddenInput.value) === Number(i.id);
              return `
                <div class="swal-adj-item-row" data-id="${i.id}" style="
                  padding: 8px 12px;
                  cursor: pointer;
                  border-bottom: 1px solid #f1f5f9;
                  display: flex;
                  justify-content: space-between;
                  align-items: center;
                  background: ${isSelected ? '#eff6ff' : 'white'};
                  transition: background 0.15s;
                ">
                  <div style="text-align: left;">
                    <div style="font-weight: 600; font-size: 0.875rem; color: ${isSelected ? '#1e40af' : '#1e293b'};">${i.name}</div>
                    <div style="font-size: 0.75rem; color: #64748b;">${i.category || 'พัสดุทั่วไป'}</div>
                  </div>
                  <span style="font-size: 0.75rem; background: ${i.on_hand_pieces > 0 ? '#dcfce7' : '#fee2e2'}; color: ${i.on_hand_pieces > 0 ? '#166534' : '#991b1b'}; padding: 2px 8px; border-radius: 999px; font-weight: 600; white-space: nowrap; margin-left: 8px;">
                    ${Number(i.on_hand_pieces).toLocaleString()} ${i.unit_piece_name}
                  </span>
                </div>
              `;
            }).join('');

            dropdownList.querySelectorAll('.swal-adj-item-row').forEach(row => {
              row.addEventListener('click', () => {
                const id = parseInt(row.getAttribute('data-id'), 10);
                selectItem(id);
              });
              row.addEventListener('mouseenter', () => {
                row.style.background = '#f8fafc';
              });
              row.addEventListener('mouseleave', () => {
                const id = parseInt(row.getAttribute('data-id'), 10);
                row.style.background = (Number(hiddenInput.value) === id) ? '#eff6ff' : 'white';
              });
            });
          }

          function selectItem(id) {
            const itm = items.find(i => Number(i.id) === Number(id));
            if (!itm) return;
            hiddenInput.value = itm.id;
            searchInput.value = itm.name;
            if (badgeEl) {
              badgeEl.innerHTML = `
                <span>ยอดคงคลังปัจจุบัน: <strong style="color: #1e40af;">${Number(itm.on_hand_pieces).toLocaleString()}</strong> ${itm.unit_piece_name}</span>
                <span style="font-size: 0.75rem; color: #64748b;">หมวด: ${itm.category || 'ทั่วไป'}</span>
              `;
            }
            if (unitLabelEl) {
              unitLabelEl.innerText = itm.unit_piece_name;
            }
            const qtyInput = document.getElementById('swalAdjNewQty');
            if (qtyInput) {
              qtyInput.placeholder = `ระบุยอดใหม่ (ปัจจุบัน: ${itm.on_hand_pieces.toLocaleString()} ${itm.unit_piece_name})`;
            }
            closeDropdown();
          }

          function openDropdown() {
            dropdownList.style.display = 'block';
            renderList(searchInput.value);
          }

          function closeDropdown() {
            dropdownList.style.display = 'none';
          }

          searchInput.addEventListener('focus', () => {
            openDropdown();
          });

          searchInput.addEventListener('input', (e) => {
            dropdownList.style.display = 'block';
            renderList(e.target.value);
          });

          if (toggleBtn) {
            toggleBtn.addEventListener('click', (e) => {
              e.stopPropagation();
              if (dropdownList.style.display === 'block') {
                closeDropdown();
              } else {
                searchInput.focus();
                openDropdown();
              }
            });
          }

          document.addEventListener('click', (e) => {
            if (!dropdownList.contains(e.target) && e.target !== searchInput && e.target !== toggleBtn && !toggleBtn.contains(e.target)) {
              closeDropdown();
            }
          });

          const defaultItem = (preselectedItemId !== null ? items.find(i => Number(i.id) === Number(preselectedItemId)) : null) || items[0];
          if (defaultItem) {
            selectItem(defaultItem.id);
          }
        },
        preConfirm: () => {
          const itemId = parseInt(document.getElementById('swalAdjItem').value, 10);
          const rawVal = document.getElementById('swalAdjNewQty').value;
          const newQty = parseInt(rawVal, 10);
          const reason = document.getElementById('swalAdjReason').value;
          if (!itemId) {
            Swal.showValidationMessage('กรุณาเลือกรายการพัสดุที่ต้องการปรับยอดครับ');
            return false;
          }
          if (rawVal === '' || isNaN(newQty) || newQty < 0) {
            Swal.showValidationMessage('กรุณาระบุยอดคงคลังจริงที่ถูกต้อง (ตั้งแต่ 0 ขึ้นไป) ครับ');
            return false;
          }
          return { itemId, newQty, reason };
        }
      }).then((res) => {
        if (res.isConfirmed && res.value) {
          const { itemId, newQty, reason } = res.value;
          const items = getItemsDB();
          const itm = items.find(i => i.id === itemId);
          if (itm) {
            const oldQty = itm.on_hand_pieces;
            const diff = newQty - oldQty;
            itm.on_hand_pieces = newQty;
            saveItemsDB(items);
            const staffUser = getLoggedInStaff();
            const recBy = staffUser ? (staffUser.name || staffUser.username) : 'เจ้าหน้าที่พัสดุ สวท.';
            recordLocalTransaction({
              itemId: itm.id,
              itemName: itm.name,
              unitPiece: itm.unit_piece_name,
              transactionType: 'ADJUST',
              changePieces: diff,
              balanceAfter: newQty,
              referenceType: 'ADJUSTMENT',
              referenceId: '',
              reason: reason,
              recordedBy: recBy,
              formattedDate: formatThaiDatetime(new Date())
            });
            postToMySQLAPI('adjustStock', { itemId: itm.id, newQty: newQty, reason: reason, recordedBy: recBy });
            renderInventoryTable();

            Swal.fire({
              icon: 'success',
              title: 'ปรับปรุงยอดสต๊อกสำเร็จ!',
              html: `รายการ <b>${itm.name}</b><br>ปรับยอดจาก ${oldQty.toLocaleString()} เป็น <b>${newQty.toLocaleString()} ${itm.unit_piece_name}</b><br><small style="color:#64748b;">เหตุผล: ${reason}</small>`,
              confirmButtonColor: '#1e40af',
              confirmButtonText: 'ตกลง'
            });
          }
        }
      });
    }

    // PDF Preview
    function printRequisitionPdf() {
      const printContent = document.getElementById('printablePdf');
      if (!printContent) {
        window.print();
        return;
      }

      let iframe = document.getElementById('pdfPrintIframe');
      if (iframe) {
        iframe.remove();
      }
      iframe = document.createElement('iframe');
      iframe.id = 'pdfPrintIframe';
      iframe.style.position = 'fixed';
      iframe.style.right = '0';
      iframe.style.bottom = '0';
      iframe.style.width = '0';
      iframe.style.height = '0';
      iframe.style.border = 'none';
      iframe.style.visibility = 'hidden';
      document.body.appendChild(iframe);

      const doc = iframe.contentWindow.document;
      doc.open();
      doc.write(`
        <!DOCTYPE html>
        <html lang="th">
        <head>
          <meta charset="UTF-8">
          <title>ใบขอเบิกพัสดุ มหาวิทยาลัยสวนดุสิต</title>
          <link rel="preconnect" href="https://fonts.googleapis.com">
          <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
          <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap" rel="stylesheet">
          <style>
            @page {
              size: A4 portrait;
              margin: 1.2cm 1.5cm;
            }
            * {
              box-sizing: border-box;
              -webkit-print-color-adjust: exact !important;
              print-color-adjust: exact !important;
            }
            body {
              margin: 0;
              padding: 0;
              background: white;
              color: #000;
              font-family: 'Sarabun', sans-serif;
              font-size: 14px;
              line-height: 1.5;
            }
            .pdf-page {
              display: flex;
              flex-direction: column;
              min-height: calc(297mm - 2.5cm);
              width: 100%;
              max-width: 100%;
              margin: 0 auto;
              padding: 0;
              background: white;
              box-sizing: border-box;
            }
            .pdf-header {
              text-align: center;
              margin-bottom: 1.25rem;
              display: flex;
              flex-direction: column;
              align-items: center;
            }
            .pdf-header img {
              height: 70px;
              width: auto;
              object-fit: contain;
              margin-bottom: 0.4rem;
            }
            .pdf-header h2 {
              font-size: 1.35rem;
              font-weight: 700;
              margin: 0 0 0.25rem 0;
            }
            .pdf-header p {
              font-size: 0.9rem;
              color: #444;
              margin: 0;
            }
            .pdf-meta-table {
              width: 100%;
              margin-bottom: 1.25rem;
              border-collapse: collapse;
              font-size: 0.95rem;
            }
            .pdf-meta-table td {
              padding: 4px 0;
              vertical-align: top;
            }
            .pdf-items-table {
              width: 100%;
              border-collapse: collapse;
              margin: 1.25rem 0;
              font-size: 0.92rem;
            }
            .pdf-items-table th, .pdf-items-table td {
              border: 1px solid #333;
              padding: 7px 9px;
            }
            .pdf-items-table th {
              background-color: #f3f4f6 !important;
              font-weight: 600;
              text-align: center;
            }
            .pdf-footer-section {
              margin-top: auto;
              width: 100%;
              page-break-inside: avoid;
              break-inside: avoid;
            }
            .pdf-ack-note {
              font-size: 0.85rem;
              margin-bottom: 0.75rem;
            }
            .pdf-signatures {
              display: grid;
              grid-template-columns: repeat(4, 1fr);
              gap: 0.75rem;
              margin-top: auto;
              text-align: center;
              font-size: 0.82rem;
              page-break-inside: avoid;
              break-inside: avoid;
            }
            .pdf-footer-section .pdf-signatures {
              margin-top: 0.5rem;
            }
            .sig-box {
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: flex-end;
              height: 130px;
            }
            .sig-img-preview {
              max-height: 55px;
              max-width: 130px;
              margin-bottom: 4px;
            }
            .sig-line {
              width: 80%;
              border-bottom: 1px dotted #333;
              margin-bottom: 6px;
            }
          </style>
        </head>
        <body>
          <div class="pdf-page">
            ${printContent.innerHTML}
          </div>
        </body>
        </html>
      `);
      doc.close();

      setTimeout(() => {
        try {
          iframe.contentWindow.focus();
          iframe.contentWindow.print();
        } catch (e) {
          console.warn('Iframe print fallback to window.print():', e);
          window.print();
        }
      }, 250);
    }

    function previewDocInPdf(docNo) {
      const reqs = getReqsDB();
      const req = reqs.find(r => r.id === docNo);
      if (!req) return;

      document.getElementById('pdfDocNo').innerText = req.id;
      const pdfDateEl = document.getElementById('pdfDate');
      if (pdfDateEl) pdfDateEl.innerText = req.date || '21 ต.ค. 2569';
      document.getElementById('pdfDept').innerText = req.dept;
      document.getElementById('pdfRequester').innerText = req.requester + (req.phone ? ` (โทร ${req.phone})` : '');
      document.getElementById('pdfPurpose').innerText = req.purpose;
      document.getElementById('pdfSignRequester').innerText = req.requester;
      document.getElementById('pdfReceiverName').innerText = req.requester;

      const reqDateEl = document.getElementById('pdfSignReqDate');
      if (reqDateEl) reqDateEl.innerText = req.date || '-';

      const isVerifiedOrLater = ['VERIFIED', 'APPROVED', 'COMPLETED'].includes(req.status);
      const verifierEl = document.getElementById('pdfSignVerifier');
      const verifiedDateEl = document.getElementById('pdfSignVerifiedDate');
      const verifierStampEl = document.getElementById('pdfSignVerifierStamp');
      if (verifierEl) verifierEl.innerText = req.verified_by || (isVerifiedOrLater ? 'เจ้าหน้าที่พัสดุ สวท.' : '.........................................');
      if (verifiedDateEl) verifiedDateEl.innerText = req.verified_date || req.verified_at || (isVerifiedOrLater ? (req.date || '-') : 'วันที่ ....../....../......');
      if (verifierStampEl) verifierStampEl.innerText = isVerifiedOrLater ? '[ ผ่านการคัดกรอง ]' : '';

      const isApprovedOrCompleted = ['APPROVED', 'COMPLETED'].includes(req.status);
      const approverEl = document.getElementById('pdfSignApprover');
      const approvedDateEl = document.getElementById('pdfSignApprovedDate');
      const approverStampEl = document.getElementById('pdfSignApproverStamp');
      if (approverEl) approverEl.innerText = req.approved_by || (isApprovedOrCompleted ? 'หัวหน้าสำนักงานผู้อำนวยการ สวท.' : '.........................................');
      if (approvedDateEl) approvedDateEl.innerText = req.approved_date || req.approved_at || (isApprovedOrCompleted ? (req.completed_date || req.date || '-') : 'วันที่ ....../....../......');
      if (approverStampEl) approverStampEl.innerText = isApprovedOrCompleted ? '[ อนุมัติขั้นสุดท้าย ]' : '';

      const tbody = document.getElementById('pdfItemsTbody');
      tbody.innerHTML = req.items.map((item, idx) => {
        const safeName = escapeHtml(item.name);
        const safeBox = escapeHtml(item.unitBox);
        const safePiece = escapeHtml(item.unitPiece);
        let noteTxt = 'ครบถ้วน';
        if (req.status === 'REJECTED') noteTxt = 'ไม่อนุมัติ';
        else if (req.status === 'PENDING') noteTxt = 'รอคัดกรอง';
        else if (req.status === 'VERIFIED') noteTxt = 'ผ่านการคัดกรอง';
        return `
        <tr>
          <td style="text-align: center;">${idx + 1}</td>
          <td>${safeName}</td>
          <td style="text-align: center;">${item.qtyBoxes > 0 ? `${item.qtyBoxes} ${safeBox} ` : ''}${item.qtyPieces > 0 ? `${item.qtyPieces} ${safePiece}` : ''}</td>
          <td style="text-align: center; font-weight: bold; color: #166534;">${(item.approvedPieces ?? item.totalPieces).toLocaleString()} ${safePiece}</td>
          <td style="text-align: center;">${noteTxt}</td>
        </tr>
        `;
      }).join('');

      const sigArea = document.getElementById('pdfReceiverSigArea');
      if (sigArea) {
        if (req.signature && req.signature.startsWith('data:image')) {
          sigArea.innerHTML = `<img src="${req.signature}" class="sig-img-preview" alt="ลายเซ็นผู้รับพัสดุ">`;
        } else if (req.status === 'COMPLETED') {
          sigArea.innerHTML = `<div style="font-size: 0.75rem; color: #059669; font-weight: 700; margin-bottom: 6px;">[ รับมอบพัสดุแล้ว ]</div>`;
        } else {
          sigArea.innerHTML = '';
        }
      }
      const recTimeEl = document.getElementById('pdfReceiveTime');
      if (recTimeEl) {
        const payDate = req.completed_date || req.completedDate;
        recTimeEl.innerText = req.status === 'COMPLETED' ? `วันที่รับของ: ${payDate || req.date || ''}` : 'วันที่ ........../........../..........';
      }
      switchStaffView('pdf');
    }

    // Inventory Table & Low Stock Filter
    let lowStockFilterActive = false;

    function toggleLowStockFilter() {
      lowStockFilterActive = !lowStockFilterActive;
      renderInventoryTable();
    }

    function jumpToLowStockInventory() {
      lowStockFilterActive = true;
      switchStaffView('inventory');
      renderInventoryTable();
    }

    function formatStockDisplay(totalPieces, ratio, boxName, pieceName, isMulti) {
      const safePiece = escapeHtml(pieceName);
      const safeBox = escapeHtml(boxName);
      if (!isMulti || ratio <= 1) return `${totalPieces.toLocaleString()} ${safePiece}`;
      const boxes = Math.floor(totalPieces / ratio);
      const pieces = totalPieces % ratio;
      if (boxes > 0 && pieces > 0) return `${boxes} ${safeBox} ${pieces} ${safePiece}`;
      if (boxes > 0) return `${boxes} ${safeBox}`;
      return `${pieces} ${safePiece}`;
    }

    function renderInventoryTable() {
      const items = getItemsDB();
      const tbody = document.getElementById('inventoryTableBody');
      const activeRole = getActiveStaffRole();

      let totalReserved = 0;
      const lowStockItems = [];

      items.forEach(item => {
        const available = Math.max(0, item.on_hand_pieces - item.reserved_pieces);
        const isLow = available <= item.min_alert;
        totalReserved += item.reserved_pieces;
        if (isLow) lowStockItems.push(item);
      });

      const lowStockCount = lowStockItems.length;
      const displayItems = lowStockFilterActive
        ? items.filter(item => Math.max(0, item.on_hand_pieces - item.reserved_pieces) <= item.min_alert)
        : items;

      const lowBanner = document.getElementById('lowStockAlertBanner');
      const lowBannerTitle = document.getElementById('lowStockBannerTitle');
      const lowBannerItems = document.getElementById('lowStockBannerItems');
      const btnFilterLow = document.getElementById('btnFilterLowStock');
      const reqLowBanner = document.getElementById('reqLowStockBanner');
      const reqLowBannerText = document.getElementById('reqLowStockBannerText');

      if (lowBanner) {
        if (lowStockCount > 0) {
          lowBanner.style.display = 'flex';
          if (lowBannerTitle) {
            lowBannerTitle.innerText = `แจ้งเตือนจุดสั่งซื้อใหม่: พบพัสดุต่ำกว่าเกณฑ์ขั้นต่ำ ${lowStockCount} รายการ`;
          }
          if (lowBannerItems) {
            const sampleNames = lowStockItems.slice(0, 5).map(i => i.name).join(', ');
            lowBannerItems.innerText = `รายการที่ควรสั่งซื้อเติมคลัง: ${sampleNames}${lowStockItems.length > 5 ? ` และอื่นๆ อีก ${lowStockItems.length - 5} รายการ` : ''}`;
          }
          if (btnFilterLow) {
            btnFilterLow.innerText = lowStockFilterActive ? 'แสดงพัสดุทั้งหมด (ยกเลิกตัวกรอง)' : `กรองเฉพาะรายการต่ำกว่าเกณฑ์ (${lowStockCount})`;
            btnFilterLow.style.background = lowStockFilterActive ? '#be123c' : 'white';
            btnFilterLow.style.color = lowStockFilterActive ? 'white' : '#be123c';
          }
        } else {
          lowBanner.style.display = 'none';
        }
      }

      if (reqLowBanner) {
        if (lowStockCount > 0) {
          reqLowBanner.style.display = 'flex';
          if (reqLowBannerText) {
            reqLowBannerText.innerHTML = `<strong>แจ้งเตือนจุดสั่งซื้อใหม่:</strong> มีรายการพัสดุคงเหลือต่ำกว่าเกณฑ์ขั้นต่ำจำนวน <strong>${lowStockCount} รายการ</strong>`;
          }
        } else {
          reqLowBanner.style.display = 'none';
        }
      }

      tbody.innerHTML = displayItems.map((item, idx) => {
        const available = Math.max(0, item.on_hand_pieces - item.reserved_pieces);
        const isLow = available <= item.min_alert;

        return `
          <tr>
            <td style="text-align: center;">${idx + 1}</td>
            <td><strong>${item.name}</strong></td>
            <td>${item.is_multi_unit ? `1 ${item.unit_box_name} = ${item.pieces_per_box} ${item.unit_piece_name}` : `หน่วยเดี่ยว (${item.unit_piece_name})`}</td>
            <td>${item.on_hand_pieces.toLocaleString()} ${item.unit_piece_name}</td>
            <td style="color: var(--primary); font-weight: 500;">${item.reserved_pieces.toLocaleString()} ${item.unit_piece_name}</td>
            <td style="font-weight: 700; color: ${isLow ? 'var(--danger)' : 'var(--accent)'};">
              ${formatStockDisplay(available, item.pieces_per_box, item.unit_box_name, item.unit_piece_name, item.is_multi_unit)}
            </td>
            <td>
              ${(item.monthly_limit && Number(item.monthly_limit) > 0) ? `<span style="font-weight: 600; color: #b45309;">${Number(item.monthly_limit).toLocaleString()} ${item.unit_piece_name}/ท่าน</span>` : '<span style="color: var(--neutral-400); font-size: 0.85rem;">ไม่จำกัด</span>'}
            </td>
            <td>
              <div style="display: flex; flex-direction: column; gap: 4px; align-items: flex-start;">
                <span style="background: ${isLow ? 'var(--danger-light)' : '#dcfce7'}; color: ${isLow ? 'var(--danger)' : '#166534'}; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 999px; display: inline-flex; align-items: center; gap: 4px;">
                  ${isLow ? `${vIcons.alertTriangle} ต่ำกว่าเกณฑ์` : `${vIcons.checkCircle} ปกติ`}
                </span>
                <button type="button" class="btn-min-alert-badge" onclick="promptSetMinAlert(${item.id})" 
                        style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 6px; padding: 2px 6px; font-size: 0.75rem; color: #334155; cursor: pointer; display: inline-flex; align-items: center; gap: 4px; transition: all 0.15s;"
                        onmouseover="this.style.background='#eff6ff'; this.style.borderColor='#3b82f6'; this.style.color='#1e40af';"
                        onmouseout="this.style.background='#f8fafc'; this.style.borderColor='#cbd5e1'; this.style.color='#334155';"
                        title="คลิกเพื่อปรับเกณฑ์เตือนจำนวนพัสดุ">
                  <span style="display: inline-flex; align-items: center; gap: 4px;">${vIcons.bell} เตือนที่: <strong>${(item.min_alert || 0).toLocaleString()}</strong> ${item.unit_piece_name}</span>
                  <span style="color: #3b82f6; display: inline-flex; align-items: center;">${vIcons.pen}</span>
                </button>
              </div>
            </td>
            <td>
              ${item.last_restocked_at ? `<span style="font-size: 0.775rem; color: var(--neutral-600); white-space: nowrap;">${escapeHtml(String(item.last_restocked_at))}</span>` : '<span style="color: var(--neutral-400); font-size: 0.8rem;">-</span>'}
            </td>
            <td style="text-align: right; white-space: nowrap;">
              <button class="btn btn-outline" style="padding: 4px 8px; font-size: 0.75rem; margin-right: 3px; color: #1e40af; border-color: #bfdbfe;" onclick="openItemHistoryModal(${item.id})" title="ดูประวัติความเคลื่อนไหวสต๊อกย้อนหลัง">
                ${vIcons.clock} ประวัติ
              </button>
              ${activeRole !== 'HEAD' ? `
                <button class="btn btn-outline" style="padding: 4px 8px; font-size: 0.75rem; margin-right: 3px;" onclick="openItemModal(${item.id})">
                  แก้ไข
                </button>
                <button class="btn btn-outline" style="padding: 4px 8px; font-size: 0.75rem; color: var(--danger);" onclick="deleteInventoryItem(${item.id})">
                  ลบ
                </button>
              ` : ''}
            </td>
          </tr>
        `;
      }).join('');

      const totalItemsEl = document.getElementById('metricTotalItems');
      if (totalItemsEl) {
        totalItemsEl.innerHTML = `${items.length.toLocaleString()} <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">รายการ</small>`;
      }
      document.getElementById('metricReserved').innerHTML = `${totalReserved.toLocaleString()} <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">ชิ้น</small>`;
      document.getElementById('metricLowStock').innerHTML = `${lowStockCount} <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">รายการ</small>`;
    }

    async function openItemHistoryModal(itemId) {
      const items = getItemsDB();
      const itm = items.find(i => Number(i.id) === Number(itemId));
      if (!itm) return;

      let txList = null;
      if (MYSQL_API_URL && navigator.onLine) {
        try {
          const res = await fetch(`${MYSQL_API_URL}?action=getItemTransactions&itemId=${encodeURIComponent(itemId)}`);
          if (res.ok) {
            const json = await res.json();
            if (json && json.status === 'success' && Array.isArray(json.data)) {
              txList = json.data;
            }
          }
        } catch (e) {
          console.warn('Fallback to local transactions DB:', e);
        }
      }
      if (!txList || txList.length === 0) {
        txList = getTransactionsDB(itemId);
      }

      const available = Math.max(0, itm.on_hand_pieces - itm.reserved_pieces);
      const totalSpent = txList.reduce((acc, t) => acc + (t.transactionType === 'IN' ? (Number(t.totalCost) || 0) : 0), 0);
      const rowsHtml = txList.length === 0
        ? `<tr><td colspan="7" style="text-align: center; padding: 2rem; color: #94a3b8;">ยังไม่มีประวัติความเคลื่อนไหวสำหรับพัสดุรายการนี้</td></tr>`
        : txList.map((t, idx) => {
            let typeBadge = `<span style="background:#dcfce7; color:#166534; padding:2px 8px; border-radius:999px; font-size:0.72rem; font-weight:600;">รับเข้า</span>`;
            if (t.transactionType === 'OUT') {
              typeBadge = `<span style="background:#dbeafe; color:#1e40af; padding:2px 8px; border-radius:999px; font-size:0.72rem; font-weight:600;">จ่ายออก</span>`;
            } else if (t.transactionType === 'ADJUST') {
              typeBadge = `<span style="background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:999px; font-size:0.72rem; font-weight:600;">ปรับยอด</span>`;
            }
            const chg = Number(t.changePieces || 0);
            const chgStr = chg > 0 ? `+${chg.toLocaleString()}` : `${chg.toLocaleString()}`;
            const chgColor = chg > 0 ? '#059669' : chg < 0 ? '#dc2626' : '#475569';
            const tCost = Number(t.totalCost || 0);
            const uPrice = Number(t.unitPrice || 0);
            const priceCellHtml = (t.transactionType === 'IN' && (tCost > 0 || uPrice > 0))
              ? `<div style="font-weight:700; color:#0369a1;">${tCost.toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} บาท</div><div style="font-size:0.72rem; color:#64748b;">@${uPrice.toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} บ./${escapeHtml(itm.unit_piece_name)}</div>`
              : `<span style="color:#94a3b8;">-</span>`;
            const refTxt = t.referenceId ? `<strong>${escapeHtml(t.referenceId)}</strong> — ${escapeHtml(t.reason || '')}` : escapeHtml(t.reason || '-');
            return `
              <tr>
                <td style="font-size: 0.78rem; white-space: nowrap; color: #475569;">${escapeHtml(t.formattedDate || t.createdAt || '-')}</td>
                <td style="text-align: center;">${typeBadge}</td>
                <td style="text-align: right; font-weight: 700; color: ${chgColor};">${chgStr} ${escapeHtml(itm.unit_piece_name)}</td>
                <td style="text-align: right; font-weight: 600;">${Number(t.balanceAfter || 0).toLocaleString()} ${escapeHtml(itm.unit_piece_name)}</td>
                <td style="text-align: right; white-space: nowrap;">${priceCellHtml}</td>
                <td style="font-size: 0.78rem; color: #334155;">${refTxt}</td>
                <td style="font-size: 0.78rem; color: #475569;">${escapeHtml(t.recordedBy || 'เจ้าหน้าที่พัสดุ สวท.')}</td>
              </tr>
            `;
          }).join('');

      Swal.fire({
        title: 'ประวัติความเคลื่อนไหวสต๊อก',
        width: 920,
        html: `
          <div style="text-align: left; margin-top: 0.5rem;">
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.85rem 1rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
              <div>
                <div style="font-size: 1rem; font-weight: 700; color: #0f172a;">${escapeHtml(itm.name)}</div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 2px;">
                  หมวดหมู่: ${escapeHtml(itm.category || '-')} • รับเข้าล่าสุด: <strong>${escapeHtml(itm.last_restocked_at || 'ยังไม่มีข้อมูล')}</strong>
                </div>
              </div>
              <div style="display: flex; gap: 0.55rem; font-size: 0.825rem; flex-wrap: wrap;">
                <span style="background: white; border: 1px solid #cbd5e1; padding: 4px 10px; border-radius: 6px;">คงคลัง: <strong>${itm.on_hand_pieces.toLocaleString()}</strong></span>
                <span style="background: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; padding: 4px 10px; border-radius: 6px;">จอง: <strong>${itm.reserved_pieces.toLocaleString()}</strong></span>
                <span style="background: #ecfdf5; border: 1px solid #a7f3d0; color: #047857; padding: 4px 10px; border-radius: 6px;">พร้อมเบิก: <strong>${available.toLocaleString()} ${escapeHtml(itm.unit_piece_name)}</strong></span>
                <span style="background: #e0f2fe; border: 1px solid #bae6fd; color: #0369a1; padding: 4px 10px; border-radius: 6px;">ซื้อเข้าสะสม: <strong>${totalSpent.toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} บาท</strong></span>
              </div>
            </div>
            <div style="max-height: 360px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 8px;">
              <table class="req-table" style="margin: 0; font-size: 0.825rem;">
                <thead style="position: sticky; top: 0; z-index: 1;">
                  <tr>
                    <th>วัน-เวลา</th>
                    <th style="text-align: center;">ประเภทรายการ</th>
                    <th style="text-align: right;">จำนวนเปลี่ยนแปลง</th>
                    <th style="text-align: right;">คงเหลือหลังทำรายการ</th>
                    <th style="text-align: right;">ราคา / ยอดเงินซื้อเข้า</th>
                    <th>เอกสารอ้างอิง / หมายเหตุ</th>
                    <th>ผู้บันทึก</th>
                  </tr>
                </thead>
                <tbody>
                  ${rowsHtml}
                </tbody>
              </table>
            </div>
          </div>
        `,
        confirmButtonColor: '#1e40af',
        confirmButtonText: 'ปิดหน้าต่าง'
      });
    }

    function handleAnalyticsMonthChange() {
      renderMonthlyAnalyticsView();
    }

    async function renderMonthlyAnalyticsView() {
      const monthSelect = document.getElementById('analyticsMonthSelect');
      const selectedMonth = monthSelect ? monthSelect.value : '2026-11';
      let analyticsData = null;

      // Try fetching from server API if online
      if (MYSQL_API_URL && navigator.onLine) {
        try {
          const res = await fetch(`${MYSQL_API_URL}?action=getMonthlyAnalytics&month=${encodeURIComponent(selectedMonth)}`);
          if (res.ok) {
            const json = await res.json();
            if (json && json.status === 'success' && json.data) {
              analyticsData = json.data;
            }
          }
        } catch (e) {
          console.warn('Could not fetch monthly analytics from API, falling back to local DB:', e);
        }
      }

      // Offline / LocalStorage calculation fallback
      if (!analyticsData) {
        const reqs = getReqsDB();
        const items = getItemsDB();
        const isAll = (selectedMonth === 'ALL');

        const monthReqs = reqs.filter(r => {
          if (isAll) return true;
          try {
            const parts = selectedMonth.split('-');
            const beYear = parseInt(parts[0], 10) + 543;
            const beMonth = parts[1];
            const bePattern = `REQ-${beYear}${beMonth}`;
            return (r.id || '').startsWith(bePattern) || (r.created_at || '').startsWith(selectedMonth);
          } catch (err) {
            return true;
          }
        });

        const statusMap = {};
        monthReqs.forEach(r => {
          statusMap[r.status] = (statusMap[r.status] || 0) + 1;
        });

        let totalRequested = 0;
        let totalApproved = 0;
        const itemUsageMap = {};
        const personMap = {};

        monthReqs.forEach(r => {
          const reqPerson = String(r.requester || 'ไม่ระบุผู้ขอเบิก').trim();
          const reqDept = String(r.dept || '').trim();
          if (r.status !== 'REJECTED') {
            if (!personMap[reqPerson]) {
              personMap[reqPerson] = {
                requester: reqPerson,
                dept: reqDept,
                requisitionCount: 0,
                completedCount: 0,
                totalRequestedPieces: 0,
                totalApprovedPieces: 0,
                itemsMap: {}
              };
            }
            if (reqDept && !personMap[reqPerson].dept) personMap[reqPerson].dept = reqDept;
            personMap[reqPerson].requisitionCount += 1;
            if (r.status === 'COMPLETED') personMap[reqPerson].completedCount += 1;
          }

          (r.items || []).forEach(it => {
            const itId = Number(it.itemId);
            const pTot = Number(it.totalPieces || 0);
            const pApp = Number(it.approvedPieces !== undefined ? it.approvedPieces : it.totalPieces || 0);
            totalRequested += pTot;
            if (r.status === 'APPROVED' || r.status === 'COMPLETED') {
              totalApproved += pApp;
            }
            if (r.status !== 'REJECTED') {
              if (!itemUsageMap[itId]) {
                itemUsageMap[itId] = { totalPieces: 0, reqCount: 0 };
              }
              itemUsageMap[itId].totalPieces += pTot;
              itemUsageMap[itId].reqCount += 1;

              const pRec = personMap[reqPerson];
              pRec.totalRequestedPieces += pTot;
              if (r.status === 'APPROVED' || r.status === 'COMPLETED') {
                pRec.totalApprovedPieces += pApp;
              }
              if (!pRec.itemsMap[itId]) {
                const catalogItem = items.find(x => Number(x.id) === itId);
                pRec.itemsMap[itId] = {
                  itemId: itId,
                  name: (catalogItem && catalogItem.name) || it.name || `พัสดุ #${itId}`,
                  unit: (catalogItem && catalogItem.unit_piece_name) || it.unitPiece || 'ชิ้น',
                  totalPieces: 0,
                  approvedPieces: 0
                };
              }
              pRec.itemsMap[itId].totalPieces += pTot;
              if (r.status === 'APPROVED' || r.status === 'COMPLETED') {
                pRec.itemsMap[itId].approvedPieces += pApp;
              }
            }
          });
        });

        const allItemsUsage = items.map(itm => {
          const usage = itemUsageMap[itm.id] || { totalPieces: 0, reqCount: 0 };
          return {
            itemId: itm.id,
            name: itm.name,
            category: itm.category,
            unit: itm.unit_piece_name,
            totalPieces: usage.totalPieces,
            requisitionCount: usage.reqCount
          };
        });

        allItemsUsage.sort((a, b) => b.totalPieces - a.totalPieces);

        const topItems = allItemsUsage.slice(0, 5);
        const leastItems = allItemsUsage.slice(-5).reverse();

        const personUsageList = Object.values(personMap).map(p => {
          const itemList = Object.values(p.itemsMap).sort((a, b) => b.totalPieces - a.totalPieces);
          return {
            requester: p.requester,
            dept: p.dept,
            requisitionCount: p.requisitionCount,
            completedCount: p.completedCount,
            totalRequestedPieces: p.totalRequestedPieces,
            totalApprovedPieces: p.totalApprovedPieces,
            items: itemList
          };
        }).sort((a, b) => (b.totalRequestedPieces - a.totalRequestedPieces) || (b.requisitionCount - a.requisitionCount));

        // Offline purchase spend calculation from local stock_transactions
        const allTx = getTransactionsDB();
        const thaiMonths = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'];
        let targetThaiFrag = '';
        if (!isAll && selectedMonth.includes('-')) {
          const mParts = selectedMonth.split('-');
          const mIdx = parseInt(mParts[1], 10) - 1;
          const beYr = parseInt(mParts[0], 10) + 543;
          if (thaiMonths[mIdx]) targetThaiFrag = `${thaiMonths[mIdx]} ${beYr}`;
        }
        const monthInTx = allTx.filter(tx => {
          if (tx.transactionType !== 'IN') return false;
          if (isAll) return true;
          if ((tx.createdAt || '').startsWith(selectedMonth)) return true;
          if (targetThaiFrag && (tx.formattedDate || '').includes(targetThaiFrag)) return true;
          return false;
        });

        let offTotalPurchaseCost = 0;
        let offTotalRestockedPieces = 0;
        const offPurchaseMap = {};
        const offPurchaseTx = monthInTx.map(tx => {
          const qPcs = Number(tx.changePieces || 0);
          const tCost = Number(tx.totalCost || 0);
          const uPrice = Number(tx.unitPrice || 0);
          offTotalRestockedPieces += qPcs;
          offTotalPurchaseCost = Math.round((offTotalPurchaseCost + tCost) * 100) / 100;
          const catItem = items.find(x => Number(x.id) === Number(tx.itemId));
          const itId = Number(tx.itemId);
          if (!offPurchaseMap[itId]) {
            offPurchaseMap[itId] = {
              itemId: itId,
              name: (catItem && catItem.name) || tx.itemName || `พัสดุ #${itId}`,
              category: (catItem && catItem.category) || '-',
              unit: (catItem && catItem.unit_piece_name) || tx.unitPiece || 'ชิ้น',
              restockCount: 0,
              restockedPieces: 0,
              totalCost: 0
            };
          }
          offPurchaseMap[itId].restockCount += 1;
          offPurchaseMap[itId].restockedPieces += qPcs;
          offPurchaseMap[itId].totalCost = Math.round((offPurchaseMap[itId].totalCost + tCost) * 100) / 100;
          return {
            id: tx.id,
            itemId: itId,
            itemName: (catItem && catItem.name) || tx.itemName || `พัสดุ #${itId}`,
            unit: (catItem && catItem.unit_piece_name) || tx.unitPiece || 'ชิ้น',
            quantityPieces: qPcs,
            unitPrice: uPrice,
            totalCost: tCost,
            reason: tx.reason || '',
            recordedBy: tx.recordedBy || 'เจ้าหน้าที่พัสดุ สวท.',
            formattedDate: tx.formattedDate || '',
            createdAt: tx.createdAt || ''
          };
        });
        const offPurchaseSummary = Object.values(offPurchaseMap).map(ps => ({
          ...ps,
          avgUnitPrice: ps.restockedPieces > 0 ? Math.round((ps.totalCost / ps.restockedPieces) * 100) / 100 : 0
        })).sort((a, b) => (b.totalCost - a.totalCost) || (b.restockedPieces - a.restockedPieces));

        analyticsData = {
          month: selectedMonth,
          totalRequisitions: monthReqs.length,
          totalPending: statusMap['PENDING'] || 0,
          totalVerified: statusMap['VERIFIED'] || 0,
          totalApproved: statusMap['APPROVED'] || 0,
          totalCompleted: statusMap['COMPLETED'] || 0,
          totalRejected: statusMap['REJECTED'] || 0,
          totalPiecesRequested: totalRequested,
          totalPiecesApproved: totalApproved,
          totalPurchaseCost: offTotalPurchaseCost,
          totalRestockCount: monthInTx.length,
          totalRestockedPieces: offTotalRestockedPieces,
          topItems: topItems,
          leastItems: leastItems,
          allItemUsage: allItemsUsage,
          personUsage: personUsageList,
          purchaseSummary: offPurchaseSummary,
          purchaseTransactions: offPurchaseTx
        };
      }

      // Update Metric Cards
      document.getElementById('analyticsMetricTotalReqs').innerHTML = `${analyticsData.totalRequisitions.toLocaleString()} <small style="font-size: 0.85rem; font-weight: normal; color: var(--neutral-400);">คำขอ</small>`;
      document.getElementById('analyticsReqBreakdown').innerText = `รอคัดกรอง ${analyticsData.totalPending || 0} | รออนุมัติ ${analyticsData.totalVerified || 0} | รอจ่าย ${analyticsData.totalApproved || 0} | สำเร็จ ${analyticsData.totalCompleted || 0} | ไม่อนุมัติ ${analyticsData.totalRejected || 0}`;
      document.getElementById('analyticsMetricTotalRequested').innerHTML = `${(analyticsData.totalPiecesRequested || 0).toLocaleString()} <small style="font-size: 0.85rem; font-weight: normal; color: var(--neutral-400);">ชิ้น</small>`;
      document.getElementById('analyticsMetricTotalApproved').innerHTML = `${(analyticsData.totalPiecesApproved || 0).toLocaleString()} <small style="font-size: 0.85rem; font-weight: normal; color: var(--neutral-400);">ชิ้น</small>`;
      const purchaseMetricEl = document.getElementById('analyticsMetricTotalPurchaseCost');
      if (purchaseMetricEl) {
        const pCostVal = Number(analyticsData.totalPurchaseCost || 0);
        purchaseMetricEl.innerHTML = `${pCostVal.toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} <small style="font-size: 0.85rem; font-weight: normal; color: var(--neutral-400);">บาท</small>`;
      }
      const purchaseBreakEl = document.getElementById('analyticsPurchaseBreakdown');
      if (purchaseBreakEl) {
        purchaseBreakEl.innerText = `เติมเข้า ${(analyticsData.totalRestockCount || 0).toLocaleString()} ครั้ง | รวม ${(analyticsData.totalRestockedPieces || 0).toLocaleString()} ชิ้น`;
      }

      // Render Top 5 Items
      const topContainer = document.getElementById('analyticsTopItemsList');
      if (topContainer) {
        if (!analyticsData.topItems || analyticsData.topItems.length === 0 || analyticsData.topItems.every(i => i.totalPieces === 0)) {
          topContainer.innerHTML = `<div style="text-align: center; color: var(--neutral-400); padding: 1.5rem 0;">ไม่มีรายการเบิกพัสดุในเดือนนี้</div>`;
        } else {
          topContainer.innerHTML = analyticsData.topItems.map((itm, idx) => `
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.6rem 0; border-bottom: 1px dashed var(--neutral-100); font-size: 0.875rem;">
              <div style="display: flex; align-items: center; gap: 0.65rem;">
                <span style="font-weight: 700; color: #1e3a8a; width: 22px; height: 22px; border-radius: 50%; background: #eff6ff; display: inline-flex; align-items: center; justify-content: center; font-size: 0.75rem;">${idx + 1}</span>
                <div>
                  <div style="font-weight: 600; color: var(--neutral-800);">${escapeHtml(itm.name)}</div>
                  <div style="font-size: 0.75rem; color: var(--neutral-400);">${escapeHtml(itm.category || '')}</div>
                </div>
              </div>
              <div style="text-align: right;">
                <div style="font-weight: 700; color: #1e3a8a;">${(itm.totalPieces || 0).toLocaleString()} ${escapeHtml(itm.unit || 'ชิ้น')}</div>
                <div style="font-size: 0.75rem; color: var(--neutral-500);">${(itm.requisitionCount || 0).toLocaleString()} คำขอ</div>
              </div>
            </div>
          `).join('');
        }
      }

      // Render Least 5 Items
      const leastContainer = document.getElementById('analyticsLeastItemsList');
      if (leastContainer) {
        if (!analyticsData.leastItems || analyticsData.leastItems.length === 0) {
          leastContainer.innerHTML = `<div style="text-align: center; color: var(--neutral-400); padding: 1.5rem 0;">ไม่มีรายการพัสดุ</div>`;
        } else {
          leastContainer.innerHTML = analyticsData.leastItems.map((itm, idx) => `
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.6rem 0; border-bottom: 1px dashed var(--neutral-100); font-size: 0.875rem;">
              <div style="display: flex; align-items: center; gap: 0.65rem;">
                <span style="font-weight: 700; color: #92400e; width: 22px; height: 22px; border-radius: 50%; background: #fffbeb; display: inline-flex; align-items: center; justify-content: center; font-size: 0.75rem;">${idx + 1}</span>
                <div>
                  <div style="font-weight: 600; color: var(--neutral-800);">${escapeHtml(itm.name)}</div>
                  <div style="font-size: 0.75rem; color: var(--neutral-400);">${escapeHtml(itm.category || '')}</div>
                </div>
              </div>
              <div style="text-align: right;">
                <div style="font-weight: 700; color: ${itm.totalPieces > 0 ? '#b45309' : 'var(--neutral-400)'};">${(itm.totalPieces || 0).toLocaleString()} ${escapeHtml(itm.unit || 'ชิ้น')}</div>
                <div style="font-size: 0.75rem; color: var(--neutral-500);">${(itm.requisitionCount || 0).toLocaleString()} คำขอ</div>
              </div>
            </div>
          `).join('');
        }
      }

      // Render All Items Breakdown
      const allTbody = document.getElementById('analyticsAllItemsTbody');
      if (allTbody) {
        const allItems = analyticsData.allItemUsage || [];
        const countSpan = document.getElementById('analyticsItemTotalCount');
        if (countSpan) countSpan.innerText = `(ทั้งหมด ${allItems.length.toLocaleString()} รายการ)`;

        allTbody.innerHTML = allItems.map((itm, idx) => `
          <tr>
            <td style="text-align: center; color: var(--neutral-500);">${idx + 1}</td>
            <td><strong>${escapeHtml(itm.name)}</strong></td>
            <td><span style="font-size: 0.8rem; background: var(--neutral-100); padding: 2px 8px; border-radius: 999px;">${escapeHtml(itm.category || '')}</span></td>
            <td style="text-align: right; font-weight: 700; color: ${itm.totalPieces > 0 ? '#1e40af' : 'var(--neutral-400)'};">${(itm.totalPieces || 0).toLocaleString()}</td>
            <td style="text-align: center;">${(itm.requisitionCount || 0).toLocaleString()}</td>
            <td style="text-align: center; color: var(--neutral-600);">${escapeHtml(itm.unit || 'ชิ้น')}</td>
          </tr>
        `).join('');
      }
      window.lastMonthlyAnalyticsData = analyticsData;
      renderAnalyticsPersonUsageTable();
      renderAnalyticsPurchaseSection();
    }

    function renderAnalyticsPurchaseSection() {
      const data = window.lastMonthlyAnalyticsData || {};
      const sumTbody = document.getElementById('analyticsPurchaseSummaryTbody');
      const txTbody = document.getElementById('analyticsPurchaseTxTbody');
      const badgeEl = document.getElementById('analyticsPurchaseGrandTotalBadge');
      const searchEl = document.getElementById('analyticsPurchaseSearchInput');
      const q = (searchEl ? searchEl.value : '').trim().toLowerCase();

      const summaryList = Array.isArray(data.purchaseSummary) ? data.purchaseSummary : [];
      const txList = Array.isArray(data.purchaseTransactions) ? data.purchaseTransactions : [];
      const filteredSum = summaryList.filter(ps =>
        !q ||
        (ps.name && ps.name.toLowerCase().includes(q)) ||
        (ps.category && ps.category.toLowerCase().includes(q))
      );
      const filteredTx = txList.filter(pt =>
        !q ||
        (pt.itemName && pt.itemName.toLowerCase().includes(q)) ||
        (pt.reason && pt.reason.toLowerCase().includes(q)) ||
        (pt.recordedBy && pt.recordedBy.toLowerCase().includes(q))
      );

      const grandTotal = filteredSum.reduce((acc, ps) => acc + (Number(ps.totalCost) || 0), 0);
      if (badgeEl) {
        badgeEl.innerText = `รวมทั้งหมด: ${grandTotal.toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} บาท`;
      }

      if (sumTbody) {
        if (filteredSum.length === 0) {
          sumTbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:1.5rem; color:var(--neutral-400);">ยังไม่มีรายการซื้อ/เติมพัสดุเข้าคลังในงวดที่เลือก</td></tr>`;
        } else {
          sumTbody.innerHTML = filteredSum.map((ps, idx) => `
            <tr>
              <td style="text-align: center; color: var(--neutral-500);">${idx + 1}</td>
              <td><strong>${escapeHtml(ps.name)}</strong></td>
              <td><span style="font-size: 0.78rem; background: var(--neutral-100); padding: 2px 8px; border-radius: 999px;">${escapeHtml(ps.category || '-')}</span></td>
              <td style="text-align: center;">${(ps.restockCount || 0).toLocaleString()}</td>
              <td style="text-align: right; font-weight: 600;">${(ps.restockedPieces || 0).toLocaleString()} ${escapeHtml(ps.unit || 'ชิ้น')}</td>
              <td style="text-align: right; color: var(--neutral-600);">${Number(ps.avgUnitPrice || 0).toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} บาท</td>
              <td style="text-align: right; font-weight: 700; color: #0369a1;">${Number(ps.totalCost || 0).toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
            </tr>
          `).join('');
        }
      }

      if (txTbody) {
        if (filteredTx.length === 0) {
          txTbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:1.5rem; color:var(--neutral-400);">ยังไม่มีประวัติรายการเติมสต๊อกในงวดที่เลือก</td></tr>`;
        } else {
          txTbody.innerHTML = filteredTx.map(pt => `
            <tr>
              <td style="font-size: 0.8rem; white-space: nowrap; color: var(--neutral-600);">${escapeHtml(pt.formattedDate || pt.createdAt || '-')}</td>
              <td><strong>${escapeHtml(pt.itemName)}</strong></td>
              <td style="text-align: right; font-weight: 600; color: #059669;">+${(pt.quantityPieces || 0).toLocaleString()} ${escapeHtml(pt.unit || 'ชิ้น')}</td>
              <td style="text-align: right; color: var(--neutral-600);">${Number(pt.unitPrice || 0).toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} บาท</td>
              <td style="text-align: right; font-weight: 700; color: #0369a1;">${Number(pt.totalCost || 0).toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
              <td style="font-size: 0.8rem; color: var(--neutral-700);">${escapeHtml(pt.reason || '-')}</td>
              <td style="font-size: 0.8rem; color: var(--neutral-600);">${escapeHtml(pt.recordedBy || '-')}</td>
            </tr>
          `).join('');
        }
      }
    }

    function renderAnalyticsPersonUsageTable() {
      const tbody = document.getElementById('analyticsPersonUsageTbody');
      const countEl = document.getElementById('analyticsPersonTotalCount');
      const deptFilterEl = document.getElementById('analyticsPersonDeptFilter');
      const searchEl = document.getElementById('analyticsPersonSearchInput');
      if (!tbody) return;

      const list = (window.lastMonthlyAnalyticsData && Array.isArray(window.lastMonthlyAnalyticsData.personUsage))
        ? window.lastMonthlyAnalyticsData.personUsage
        : [];

      if (deptFilterEl) {
        const prevVal = deptFilterEl.value || 'ALL';
        const deptSet = new Set(getAllDeptNames());
        list.forEach(p => { if (p.dept) deptSet.add(p.dept); });
        const allDepts = Array.from(deptSet);
        deptFilterEl.innerHTML = `<option value="ALL">ทุกกลุ่มงาน / หน่วยงานทั้งหมด (${allDepts.length})</option>` +
          allDepts.map(d => `<option value="${escapeHtml(d)}">${escapeHtml(d)}</option>`).join('');
        if (allDepts.includes(prevVal)) deptFilterEl.value = prevVal;
      }

      const selectedDept = deptFilterEl ? deptFilterEl.value : 'ALL';
      const q = (searchEl ? searchEl.value : '').trim().toLowerCase();

      const filtered = list.filter(p => {
        const matchDept = selectedDept === 'ALL' || p.dept === selectedDept;
        const matchSearch = !q ||
          (p.requester && p.requester.toLowerCase().includes(q)) ||
          (p.dept && p.dept.toLowerCase().includes(q)) ||
          (p.items || []).some(it => it.name && it.name.toLowerCase().includes(q));
        return matchDept && matchSearch;
      });

      if (countEl) {
        countEl.innerText = `(พบ ${filtered.length.toLocaleString()} จาก ${list.length.toLocaleString()} ท่าน)`;
      }

      if (filtered.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="8" style="text-align: center; padding: 2rem; color: var(--neutral-400);">
              ไม่พบข้อมูลการเบิกพัสดุรายบุคคลในเดือนหรือเงื่อนไขที่เลือก
            </td>
          </tr>
        `;
        return;
      }

      tbody.innerHTML = filtered.map((p, idx) => {
        const topSummary = (p.items || []).slice(0, 2).map(it =>
          `<span style="display:inline-block; background:#eff6ff; color:#1e40af; border:1px solid #bfdbfe; padding:2px 8px; border-radius:999px; font-size:0.74rem; margin:2px 4px 2px 0;">${escapeHtml(it.name)} (${(it.totalPieces || 0).toLocaleString()} ${escapeHtml(it.unit || 'ชิ้น')})</span>`
        ).join('');
        const extraCount = (p.items || []).length > 2 ? `<span style="font-size:0.74rem; color:#64748b;"> +อีก ${(p.items || []).length - 2} รายการ</span>` : '';
        const safeReqJs = String(p.requester || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'");

        return `
          <tr>
            <td style="text-align: center; color: var(--neutral-500);">${idx + 1}</td>
            <td><strong>${escapeHtml(p.requester)}</strong></td>
            <td>
              <span style="background: #f1f5f9; color: #334155; font-size: 0.78rem; padding: 3px 9px; border-radius: 999px; display: inline-block;">
                ${escapeHtml(p.dept || '-')}
              </span>
            </td>
            <td style="text-align: center;">
              <strong>${(p.requisitionCount || 0).toLocaleString()}</strong>
              <span style="font-size: 0.74rem; color: var(--accent); display: block;">สำเร็จ ${(p.completedCount || 0).toLocaleString()}</span>
            </td>
            <td style="text-align: right; font-weight: 700; color: #1e40af;">${(p.totalRequestedPieces || 0).toLocaleString()} ชิ้น</td>
            <td style="text-align: right; font-weight: 700; color: #059669;">${(p.totalApprovedPieces || 0).toLocaleString()} ชิ้น</td>
            <td>${topSummary || '-'}${extraCount}</td>
            <td style="text-align: right; white-space: nowrap;">
              <button type="button" class="btn btn-outline" style="padding: 4px 10px; font-size: 0.75rem;" onclick="openPersonAnalyticsDetailModal('${safeReqJs}')">
                ${vIcons.eye} ดูรายการ
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }

    function openPersonAnalyticsDetailModal(requesterName) {
      const list = (window.lastMonthlyAnalyticsData && Array.isArray(window.lastMonthlyAnalyticsData.personUsage))
        ? window.lastMonthlyAnalyticsData.personUsage
        : [];
      const person = list.find(p => p.requester === requesterName);
      if (!person) return;

      const monthSelect = document.getElementById('analyticsMonthSelect');
      const monthLabel = monthSelect && monthSelect.selectedIndex >= 0
        ? monthSelect.options[monthSelect.selectedIndex].text
        : (window.lastMonthlyAnalyticsData.thaiMonth || 'ทั้งหมด');

      const rowsHtml = (person.items || []).map((it, idx) => `
        <tr style="border-bottom: 1px solid #e2e8f0;">
          <td style="padding: 8px; text-align: center; color: #64748b;">${idx + 1}</td>
          <td style="padding: 8px; text-align: left; font-weight: 600; color: #0f172a;">${escapeHtml(it.name)}</td>
          <td style="padding: 8px; text-align: right; color: #1e40af; font-weight: 700;">${(it.totalPieces || 0).toLocaleString()} ${escapeHtml(it.unit || 'ชิ้น')}</td>
          <td style="padding: 8px; text-align: right; color: #059669; font-weight: 700;">${(it.approvedPieces || 0).toLocaleString()} ${escapeHtml(it.unit || 'ชิ้น')}</td>
        </tr>
      `).join('');

      Swal.fire({
        title: `รายละเอียดการเบิกพัสดุ: ${escapeHtml(person.requester)}`,
        width: '720px',
        html: `
          <div style="text-align: left; font-size: 0.9rem; margin-top: 0.5rem;">
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; margin-bottom: 1rem; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
              <div><strong>หน่วยงาน:</strong> ${escapeHtml(person.dept || '-')}</div>
              <div><strong>งวดรายงาน:</strong> ${escapeHtml(monthLabel)}</div>
              <div><strong>จำนวนคำขอ:</strong> ${(person.requisitionCount || 0).toLocaleString()} คำขอ (สำเร็จ ${(person.completedCount || 0).toLocaleString()})</div>
            </div>
            <div style="max-height: 320px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 8px;">
              <table style="width: 100%; border-collapse: collapse; font-size: 0.875rem;">
                <thead>
                  <tr style="background: #f1f5f9; border-bottom: 2px solid #cbd5e1;">
                    <th style="padding: 8px; width: 45px; text-align: center;">#</th>
                    <th style="padding: 8px; text-align: left;">รายการพัสดุ</th>
                    <th style="padding: 8px; width: 130px; text-align: right;">จำนวนที่ขอเบิก</th>
                    <th style="padding: 8px; width: 130px; text-align: right;">อนุมัติ / จ่ายจริง</th>
                  </tr>
                </thead>
                <tbody>${rowsHtml || '<tr><td colspan="4" style="text-align:center; padding:1.5rem; color:#94a3b8;">ไม่มีรายการพัสดุ</td></tr>'}</tbody>
              </table>
            </div>
          </div>
        `,
        confirmButtonColor: '#1e40af',
        confirmButtonText: 'ปิดหน้าต่าง'
      });
    }

    async function exportMonthlyAnalyticsCsv() {
      if (!window.lastMonthlyAnalyticsData) {
        await renderMonthlyAnalyticsView();
      }
      const data = window.lastMonthlyAnalyticsData;
      if (!data) return;

      const monthSelect = document.getElementById('analyticsMonthSelect');
      const selectedMonth = monthSelect ? monthSelect.value : (data.month || 'ALL');
      const monthLabel = monthSelect ? monthSelect.options[monthSelect.selectedIndex].text : (data.thaiMonth || data.month || 'ทั้งหมด');

      if (MYSQL_API_URL && navigator.onLine) {
        try {
          const res = await fetch(`${MYSQL_API_URL}?action=exportMonthlyAnalyticsExcel&month=${encodeURIComponent(selectedMonth)}`);
          const contentType = res.headers.get('Content-Type') || '';
          if (res.ok && contentType.includes('spreadsheetml')) {
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `SDU_Monthly_Analytics_${selectedMonth}.xlsx`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            Swal.fire({
              icon: 'success',
              title: 'ส่งออกไฟล์ Excel สำเร็จ',
              text: `ดาวน์โหลดรายงานประจำเดือน (${monthLabel}) แยก 4 ชีต จัดคอลัมน์และตัวกรองอัตโนมัติเรียบร้อยแล้ว`,
              confirmButtonColor: '#1e40af',
              confirmButtonText: 'ตกลง'
            });
            return;
          }
        } catch (err) {
          console.warn('Excel export endpoint unavailable, falling back to offline CSV:', err);
        }
      }

      const csvEscape = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;

      const rows = [
        ['รายงานสรุปยอดและสถิติการเบิกจ่ายพัสดุรายเดือน มหาวิทยาลัยสวนดุสิต'],
        ['งวดรายงาน', monthLabel],
        ['วันที่ส่งออกข้อมูล', formatThaiDatetime(new Date())],
        [],
        ['สรุปภาพรวมประจำเดือน', 'จำนวน'],
        ['คำขอเบิกทั้งหมด (คำขอ)', data.totalRequisitions || 0],
        ['รอคัดกรอง', data.totalPending || 0],
        ['รอหัวหน้าอนุมัติ', data.totalVerified || 0],
        ['อนุมัติแล้วรอจ่าย', data.totalApproved || 0],
        ['จ่ายพัสดุสำเร็จ', data.totalCompleted || 0],
        ['ไม่อนุมัติ/ยกเลิก', data.totalRejected || 0],
        ['จำนวนชิ้นพัสดุที่ขอเบิกรวม (ชิ้น)', data.totalPiecesRequested || 0],
        ['จำนวนชิ้นที่อนุมัติ/จ่ายสำเร็จรวม (ชิ้น)', data.totalPiecesApproved || 0],
        ['จำนวนครั้งที่ซื้อ/เติมพัสดุเข้าคลัง', data.totalRestockCount || 0],
        ['จำนวนชิ้นพัสดุที่ซื้อเข้าคลังรวม', data.totalRestockedPieces || 0],
        ['ยอดเงินซื้อพัสดุเข้าคลังรวม (บาท)', Number(data.totalPurchaseCost || 0).toFixed(2)],
        [],
        ['5 อันดับพัสดุที่มีการเบิกมากที่สุด 5 อันดับ'],
        ['อันดับ', 'ชื่อรายการพัสดุ', 'หมวดหมู่', 'จำนวนที่เบิก', 'จำนวนคำขอ', 'หน่วยนับ']
      ];

      (data.topItems || []).forEach((it, idx) => {
        rows.push([idx + 1, it.name, it.category || '', it.totalPieces || 0, it.requisitionCount || 0, it.unit || 'ชิ้น']);
      });

      rows.push([]);
      rows.push(['5 อันดับพัสดุที่มีการเบิกน้อยที่สุด 5 อันดับ']);
      rows.push(['อันดับ', 'ชื่อรายการพัสดุ', 'หมวดหมู่', 'จำนวนที่เบิก', 'จำนวนคำขอ', 'หน่วยนับ']);
      (data.leastItems || []).forEach((it, idx) => {
        rows.push([idx + 1, it.name, it.category || '', it.totalPieces || 0, it.requisitionCount || 0, it.unit || 'ชิ้น']);
      });

      rows.push([]);
      rows.push(['สรุปยอดการเบิกพัสดุทุกรายการประจำเดือน']);
      rows.push(['ลำดับ', 'ชื่อรายการพัสดุ', 'หมวดหมู่', 'จำนวนที่เบิกในเดือน', 'จำนวนคำขอ', 'หน่วยนับ']);
      (data.allItemUsage || []).forEach((it, idx) => {
        rows.push([idx + 1, it.name, it.category || '', it.totalPieces || 0, it.requisitionCount || 0, it.unit || 'ชิ้น']);
      });

      rows.push([]);
      rows.push(['สรุปยอดการเบิกพัสดุจำแนกตามรายบุคคลประจำเดือน']);
      rows.push(['ลำดับ', 'ชื่อ-นามสกุล ผู้ขอเบิก', 'กลุ่มงาน / หน่วยงาน', 'จำนวนคำขอ', 'จ่ายสำเร็จ', 'จำนวนชิ้นที่ขอเบิก', 'จำนวนชิ้นที่อนุมัติ/จ่ายจริง', 'รายการพัสดุที่เบิก']);
      (data.personUsage || []).forEach((p, idx) => {
        const itemsDesc = (p.items || []).map(it => `${it.name} (${it.totalPieces || 0} ${it.unit || 'ชิ้น'})`).join('; ');
        rows.push([idx + 1, p.requester, p.dept || '-', p.requisitionCount || 0, p.completedCount || 0, p.totalRequestedPieces || 0, p.totalApprovedPieces || 0, itemsDesc || '-']);
      });

      rows.push([]);
      rows.push(['สรุปยอดเงินซื้อพัสดุเข้าคลังประจำเดือน']);
      rows.push(['ลำดับ', 'ชื่อรายการพัสดุ', 'หมวดหมู่', 'จำนวนครั้งที่เติม', 'จำนวนรับเข้า', 'หน่วยนับ', 'ราคาเฉลี่ย/หน่วย (บาท)', 'ยอดเงินรวม (บาท)']);
      (data.purchaseSummary || []).forEach((ps, idx) => {
        rows.push([idx + 1, ps.name, ps.category || '', ps.restockCount || 0, ps.restockedPieces || 0, ps.unit || 'ชิ้น', Number(ps.avgUnitPrice || 0).toFixed(2), Number(ps.totalCost || 0).toFixed(2)]);
      });

      const csvContent = '\uFEFF' + rows.map(r => r.map(csvEscape).join(',')).join('\r\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `SDU_Monthly_Analytics_${data.month || 'ALL'}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      Swal.fire({
        icon: 'success',
        title: 'ส่งออกไฟล์ออฟไลน์สำเร็จ',
        text: `ดาวน์โหลดไฟล์สรุปยอดประจำเดือน (${monthLabel}) เรียบร้อยแล้ว`,
        confirmButtonColor: '#1e40af',
        confirmButtonText: 'ตกลง'
      });
    }

    async function printMonthlyAnalyticsPdf() {
      if (!window.lastMonthlyAnalyticsData) {
        await renderMonthlyAnalyticsView();
      }
      const data = window.lastMonthlyAnalyticsData;
      if (!data) return;

      const monthSelect = document.getElementById('analyticsMonthSelect');
      const monthLabel = monthSelect ? monthSelect.options[monthSelect.selectedIndex].text : (data.thaiMonth || data.month || 'ทั้งหมด');
      const staffUser = getLoggedInStaff();
      const printedBy = staffUser ? (staffUser.name || staffUser.username) : 'เจ้าหน้าที่พัสดุ สวท.';

      let iframe = document.getElementById('analyticsPrintIframe');
      if (iframe) iframe.remove();
      iframe = document.createElement('iframe');
      iframe.id = 'analyticsPrintIframe';
      iframe.style.position = 'fixed';
      iframe.style.width = '0';
      iframe.style.height = '0';
      iframe.style.border = 'none';
      iframe.style.visibility = 'hidden';
      document.body.appendChild(iframe);

      const topRows = (data.topItems || []).map((it, idx) => `
        <tr>
          <td style="text-align:center;">${idx + 1}</td>
          <td>${escapeHtml(it.name)}</td>
          <td style="text-align:center;">${escapeHtml(it.category || '-')}</td>
          <td style="text-align:right; font-weight:700;">${(it.totalPieces || 0).toLocaleString()} ${escapeHtml(it.unit || 'ชิ้น')}</td>
          <td style="text-align:center;">${(it.requisitionCount || 0).toLocaleString()}</td>
        </tr>
      `).join('');

      const leastRows = (data.leastItems || []).map((it, idx) => `
        <tr>
          <td style="text-align:center;">${idx + 1}</td>
          <td>${escapeHtml(it.name)}</td>
          <td style="text-align:center;">${escapeHtml(it.category || '-')}</td>
          <td style="text-align:right;">${(it.totalPieces || 0).toLocaleString()} ${escapeHtml(it.unit || 'ชิ้น')}</td>
          <td style="text-align:center;">${(it.requisitionCount || 0).toLocaleString()}</td>
        </tr>
      `).join('');

      const personRows = (data.personUsage || []).map((p, idx) => {
        const itemSummary = (p.items || []).slice(0, 3).map(it => `${escapeHtml(it.name)} (${(it.totalPieces || 0).toLocaleString()})`).join(', ');
        return `
        <tr>
          <td style="text-align:center;">${idx + 1}</td>
          <td>${escapeHtml(p.requester)}</td>
          <td>${escapeHtml(p.dept || '-')}</td>
          <td style="text-align:center;">${(p.requisitionCount || 0).toLocaleString()}</td>
          <td style="text-align:right; font-weight:700;">${(p.totalRequestedPieces || 0).toLocaleString()}</td>
          <td style="text-align:right;">${(p.totalApprovedPieces || 0).toLocaleString()}</td>
          <td style="font-size:11px;">${itemSummary || '-'}</td>
        </tr>
      `;}).join('');

      const doc = iframe.contentWindow.document;
      doc.open();
      doc.write(`
        <!DOCTYPE html>
        <html lang="th">
        <head>
          <meta charset="UTF-8">
          <title>รายงานสรุปยอดการเบิกจ่ายพัสดุประจำเดือน - มหาวิทยาลัยสวนดุสิต</title>
          <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700&display=swap" rel="stylesheet">
          <style>
            @page { size: A4 portrait; margin: 1.2cm 1.5cm; }
            body { font-family: 'Sarabun', sans-serif; font-size: 13px; color: #111; margin: 0; padding: 0; line-height: 1.45; }
            .report-header { text-align: center; margin-bottom: 1rem; }
            .report-header img { height: 64px; margin-bottom: 4px; }
            .report-header h2 { margin: 0; font-size: 1.25rem; font-weight: 700; }
            .report-header p { margin: 2px 0; font-size: 0.9rem; color: #444; }
            .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 1rem; }
            .kpi-box { border: 1px solid #333; padding: 8px; text-align: center; border-radius: 4px; }
            .kpi-box .val { font-size: 1.15rem; font-weight: 700; }
            h3 { font-size: 0.95rem; margin: 0.85rem 0 0.35rem 0; border-bottom: 1px solid #333; padding-bottom: 3px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 0.75rem; font-size: 12.5px; }
            th, td { border: 1px solid #333; padding: 5px 8px; }
            th { background: #f3f4f6; font-weight: 700; text-align: center; }
            .sig-row { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 2rem; text-align: center; page-break-inside: avoid; }
          </style>
        </head>
        <body>
          <div class="report-header">
            <img src="assets/logo_sdu.png" alt="SDU">
            <h2>รายงานสรุปยอดและสถิติการเบิกจ่ายพัสดุประจำเดือน</h2>
            <p>สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.) มหาวิทยาลัยสวนดุสิต</p>
            <p><strong>ประจำงวด:</strong> ${escapeHtml(monthLabel)} | <strong>วันที่พิมพ์รายงาน:</strong> ${escapeHtml(formatThaiDatetime(new Date()))}</p>
          </div>
          <div class="kpi-grid">
            <div class="kpi-box"><div>คำขอเบิกทั้งหมด</div><div class="val">${(data.totalRequisitions || 0).toLocaleString()} คำขอ</div></div>
            <div class="kpi-box"><div>จ่ายสำเร็จแล้ว</div><div class="val">${(data.totalCompleted || 0).toLocaleString()} คำขอ</div></div>
            <div class="kpi-box"><div>จำนวนชิ้นที่ขอเบิก</div><div class="val">${(data.totalPiecesRequested || 0).toLocaleString()} ชิ้น</div></div>
            <div class="kpi-box"><div>จำนวนชิ้นที่จ่ายจริง</div><div class="val">${(data.totalPiecesApproved || 0).toLocaleString()} ชิ้น</div></div>
          </div>
          <h3>1. อันดับพัสดุที่มีการเบิกจ่ายสูงสุด 5 อันดับแรก</h3>
          <table>
            <thead><tr><th style="width:50px;">อันดับ</th><th>ชื่อรายการพัสดุ</th><th style="width:130px;">หมวดหมู่</th><th style="width:120px;">จำนวนที่เบิก</th><th style="width:80px;">คำขอ</th></tr></thead>
            <tbody>${topRows}</tbody>
          </table>
          <h3>2. อันดับพัสดุที่มีการเบิกจ่ายน้อยที่สุด 5 อันดับแรก</h3>
          <table>
            <thead><tr><th style="width:50px;">อันดับ</th><th>ชื่อรายการพัสดุ</th><th style="width:130px;">หมวดหมู่</th><th style="width:120px;">จำนวนที่เบิก</th><th style="width:80px;">คำขอ</th></tr></thead>
            <tbody>${leastRows}</tbody>
          </table>
          <h3>3. สรุปยอดการเบิกพัสดุจำแนกตามรายบุคคล</h3>
          <table>
            <thead><tr><th style="width:45px;">อันดับ</th><th>ชื่อ-นามสกุล ผู้ขอเบิก</th><th>หน่วยงาน</th><th style="width:65px;">คำขอ</th><th style="width:90px;">ขอเบิก (ชิ้น)</th><th style="width:90px;">จ่ายจริง (ชิ้น)</th><th>รายการหลัก</th></tr></thead>
            <tbody>${personRows || '<tr><td colspan="7" style="text-align:center;">ไม่มีข้อมูลการเบิกในงวดนี้</td></tr>'}</tbody>
          </table>
          <h3>4. สรุปยอดเงินซื้อพัสดุเข้าคลังประจำเดือน (รวม ${Number(data.totalPurchaseCost || 0).toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} บาท)</h3>
          <table>
            <thead><tr><th style="width:45px;">อันดับ</th><th>ชื่อรายการพัสดุ</th><th style="width:80px;">เติมเข้า (ครั้ง)</th><th style="width:100px;">จำนวนรับเข้า</th><th style="width:100px;">เฉลี่ย/หน่วย (บาท)</th><th style="width:110px;">รวมเป็นเงิน (บาท)</th></tr></thead>
            <tbody>${(data.purchaseSummary || []).map((ps, idx) => `
              <tr>
                <td style="text-align:center;">${idx + 1}</td>
                <td>${escapeHtml(ps.name)}</td>
                <td style="text-align:center;">${(ps.restockCount || 0).toLocaleString()}</td>
                <td style="text-align:right;">${(ps.restockedPieces || 0).toLocaleString()} ${escapeHtml(ps.unit || 'ชิ้น')}</td>
                <td style="text-align:right;">${Number(ps.avgUnitPrice || 0).toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                <td style="text-align:right; font-weight:700;">${Number(ps.totalCost || 0).toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
              </tr>
            `).join('') || '<tr><td colspan="6" style="text-align:center;">ไม่มีรายการซื้อพัสดุเข้าคลังในงวดนี้</td></tr>'}</tbody>
          </table>
          <div class="sig-row">
            <div>
              <div style="margin-top: 2.2rem;">ลงชื่อ...........................................................</div>
              <div>( ${escapeHtml(printedBy)} )</div>
              <div style="font-size:11.5px; color:#555;">เจ้าหน้าที่พัสดุผู้จัดทำรายงาน</div>
            </div>
            <div>
              <div style="margin-top: 2.2rem;">ลงชื่อ...........................................................</div>
              <div>( นางสาววาสนา จันทร์จ่าย )</div>
              <div style="font-size:11.5px; color:#555;">หัวหน้าสำนักงานผู้อำนวยการ สวท. / ผู้รับรองรายงาน</div>
            </div>
          </div>
        </body>
        </html>
      `);
      doc.close();
      setTimeout(() => {
        try {
          iframe.contentWindow.focus();
          iframe.contentWindow.print();
        } catch (e) {
          window.print();
        }
      }, 250);
    }

    function readFileAsDataURL(fileInput) {
      return new Promise((resolve) => {
        if (!fileInput || !fileInput.files || !fileInput.files[0]) {
          resolve(null);
          return;
        }
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = () => resolve(null);
        reader.readAsDataURL(fileInput.files[0]);
      });
    }

    async function promptSetMinAlert(itemId) {
      const items = getItemsDB();
      const itm = items.find(i => Number(i.id) === Number(itemId));
      if (!itm) return;

      const currentMin = itm.min_alert !== undefined ? Number(itm.min_alert) : 20;

      const { value: newMin } = await Swal.fire({
        title: 'ตั้งค่าเกณฑ์แจ้งเตือนสต๊อกต่ำ',
        html: `
          <div style="text-align: left; font-size: 0.9rem; margin-top: 0.5rem;">
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; margin-bottom: 1rem;">
              <div style="font-weight: 700; color: #0f172a; margin-bottom: 4px;">${escapeHtml(itm.name)}</div>
              <div style="font-size: 0.8rem; color: #64748b;">
                หน่วยนับ: <strong>${escapeHtml(itm.unit_piece_name)}</strong> 
                ${itm.is_multi_unit ? `• อัตราส่วน: 1 ${escapeHtml(itm.unit_box_name)} = ${itm.pieces_per_box} ${escapeHtml(itm.unit_piece_name)}` : ''}
              </div>
              <div style="font-size: 0.8rem; color: #059669; margin-top: 4px;">
                ยอดพร้อมเบิกปัจจุบัน: <strong>${Math.max(0, itm.on_hand_pieces - itm.reserved_pieces).toLocaleString()}</strong> ${escapeHtml(itm.unit_piece_name)}
              </div>
            </div>

            <label style="font-weight: 600; color: #334155; display: block; margin-bottom: 6px;">
              แจ้งเตือนเมื่อยอดพร้อมเบิกเหลือน้อยกว่าหรือเท่ากับ (${escapeHtml(itm.unit_piece_name)}): *
            </label>
            <input type="number" id="swal-prompt-min-alert" class="swal2-input" min="0" value="${currentMin}" 
                   style="margin: 0; width: 100%; height: 42px; font-size: 1.05rem; font-weight: 600; text-align: center; border-radius: 8px;">
            <div style="font-size: 0.775rem; color: #64748b; margin-top: 6px;">
              เมื่อยอดพัสดุในห้องคลังลดลงจนเหลือเท่ากับหรือน้อยกว่าเกณฑ์นี้ ระบบจะเปลี่ยนแถบสถานะเป็น <strong style="color: #dc2626;">สีแดง</strong> ทั้งในหน้าเจ้าหน้าที่และหน้าขอเบิกพัสดุ
            </div>
          </div>
        `,
        showCancelButton: true,
        confirmButtonColor: '#1e40af',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'บันทึกเกณฑ์เตือน',
        cancelButtonText: 'ยกเลิก',
        preConfirm: () => {
          const val = document.getElementById('swal-prompt-min-alert').value;
          if (val === '' || isNaN(val) || Number(val) < 0) {
            Swal.showValidationMessage('กรุณาระบุจำนวนเกณฑ์เตือนเป็นตัวเลขตั้งแต่ 0 ขึ้นไป');
            return false;
          }
          return Math.max(0, parseInt(val, 10));
        }
      });

      if (newMin === undefined) return;

      itm.min_alert = newMin;
      saveItemsDB(items);
      await postToMySQLAPI('saveItem', { id: itm.id, min_alert: newMin });
      renderInventoryTable();

      Swal.fire({
        icon: 'success',
        title: 'บันทึกเกณฑ์เตือนสำเร็จ!',
        text: `ตั้งค่าเกณฑ์เตือนพัสดุ "${itm.name}" เป็น ${newMin.toLocaleString()} ${itm.unit_piece_name} เรียบร้อยแล้ว`,
        timer: 1600,
        showConfirmButton: false
      });
    }

    function openItemModal(itemId = null) {
      const items = getItemsDB();
      const existing = itemId !== null ? items.find(i => Number(i.id) === Number(itemId)) : null;
      const categories = ['ซองเอกสาร', 'กระดาษและแบบฟอร์ม', 'เครื่องเขียนและแฟ้ม'];
      const catOptions = categories.map(c =>
        `<option value="${c}" ${existing && existing.category === c ? 'selected' : ''}>${c}</option>`
      ).join('');
      const isMulti = existing ? Boolean(existing.is_multi_unit) : true;

      Swal.fire({
        title: existing ? 'แก้ไขรายการพัสดุ' : 'เพิ่มรายการพัสดุใหม่เข้าคลัง',
        width: 600,
        html: `
          <div style="text-align: left; display: flex; flex-direction: column; gap: 0.75rem; margin-top: 0.5rem; font-size: 0.9rem;">
            <div>
              <label style="font-size: 0.825rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">ชื่อรายการพัสดุ *</label>
              <input id="swal-item-name" class="swal2-input" style="margin: 0; width: 100%; height: 40px; font-size: 0.925rem;" placeholder="เช่น กระดาษ A4 80 แกรม (ห่อละ 500 แผ่น)" value="${existing ? existing.name : ''}">
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
              <div>
                <label style="font-size: 0.825rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">หมวดหมู่พัสดุ *</label>
                <select id="swal-item-cat" class="swal2-input" style="margin: 0; width: 100%; height: 40px; font-size: 0.9rem;">
                  ${catOptions}
                </select>
              </div>
              <div>
                <label style="font-size: 0.825rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">รูปแบบหน่วยนับ</label>
                <select id="swal-item-multi" class="swal2-input" style="margin: 0; width: 100%; height: 40px; font-size: 0.9rem;"
                        onchange="document.getElementById('swal-multi-box-wrap').style.display = this.value === '1' ? 'grid' : 'none';">
                  <option value="1" ${isMulti ? 'selected' : ''}>2 หน่วยนับ (เช่น กล่อง/ซอง)</option>
                  <option value="0" ${!isMulti ? 'selected' : ''}>หน่วยนับเดี่ยว (เช่น อัน, เล่ม)</option>
                </select>
              </div>
            </div>
            <div id="swal-multi-box-wrap" style="display: ${isMulti ? 'grid' : 'none'}; grid-template-columns: 1fr 1fr; gap: 0.75rem; background: #f8fafc; padding: 0.65rem; border-radius: 8px; border: 1px solid #e2e8f0;">
              <div>
                <label style="font-size: 0.8rem; font-weight: 600; color: #1e40af; display: block; margin-bottom: 4px;">ชื่อหน่วยใหญ่ (เช่น กล่อง/ห่อ)</label>
                <input id="swal-item-unit-box" class="swal2-input" style="margin: 0; width: 100%; height: 38px; font-size: 0.9rem;" placeholder="เช่น กล่อง, ห่อ, แพ็ค" value="${existing ? (existing.unit_box_name || 'กล่อง') : 'กล่อง'}">
              </div>
              <div>
                <label style="font-size: 0.8rem; font-weight: 600; color: #1e40af; display: block; margin-bottom: 4px;">จำนวนหน่วยย่อยต่อ 1 หน่วยใหญ่</label>
                <input type="number" id="swal-item-ratio" min="1" class="swal2-input" style="margin: 0; width: 100%; height: 38px; font-size: 0.9rem;" placeholder="เช่น 500" value="${existing ? (existing.pieces_per_box || 1) : 500}">
              </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.65rem;">
              <div>
                <label style="font-size: 0.8rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">ชื่อหน่วยย่อย *</label>
                <input id="swal-item-unit-piece" class="swal2-input" style="margin: 0; width: 100%; height: 38px; font-size: 0.9rem;" placeholder="เช่น ชิ้น, ซอง, ใบ" value="${existing ? (existing.unit_piece_name || 'ชิ้น') : 'ชิ้น'}">
              </div>
              <div>
                <label style="font-size: 0.8rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">ยอดคงคลัง (หน่วยย่อย) ${existing ? '<small style="color: #64748b; font-weight: normal;">(ปรับยอดที่ปุ่มปรับสต๊อก)</small>' : '*'}</label>
                <input type="number" id="swal-item-onhand" min="0" class="swal2-input" style="margin: 0; width: 100%; height: 38px; font-size: 0.9rem; ${existing ? 'background-color: #f1f5f9; cursor: not-allowed;' : ''}" value="${existing ? existing.on_hand_pieces : 100}" ${existing ? 'readonly disabled' : ''}>
              </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.65rem;">
              <div>
                <label style="font-size: 0.8rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">เกณฑ์เตือนขั้นต่ำ</label>
                <input type="number" id="swal-item-min" min="0" class="swal2-input" style="margin: 0; width: 100%; height: 38px; font-size: 0.9rem;" value="${existing ? existing.min_alert : 20}">
              </div>
              <div>
                <label style="font-size: 0.8rem; font-weight: 600; color: #1e40af; display: block; margin-bottom: 4px;">จำกัดโควตาต่อบุคลากร/เดือน (0 = ไม่จำกัด)</label>
                <input type="number" id="swal-item-monthly-limit" min="0" class="swal2-input" style="margin: 0; width: 100%; height: 38px; font-size: 0.9rem;" placeholder="0" value="${existing ? (existing.monthly_limit || 0) : 0}">
              </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
              <div>
                <label style="font-size: 0.8rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">รูปภาพหน่วยย่อย (อัปโหลดหรือระบุไฟล์)</label>
                <input type="file" id="swal-item-file-piece" accept="image/*" style="font-size: 0.75rem; width: 100%; margin-bottom: 4px;">
                <input id="swal-item-img-piece" class="swal2-input" style="margin: 0; width: 100%; height: 34px; font-size: 0.8rem;" placeholder="assets/images/..." value="${existing ? (existing.image_piece || '') : ''}">
              </div>
              <div>
                <label style="font-size: 0.8rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">รูปภาพหน่วยใหญ่/กล่อง</label>
                <input type="file" id="swal-item-file-box" accept="image/*" style="font-size: 0.75rem; width: 100%; margin-bottom: 4px;">
                <input id="swal-item-img-box" class="swal2-input" style="margin: 0; width: 100%; height: 34px; font-size: 0.8rem;" placeholder="assets/images/..." value="${existing ? (existing.image_box || '') : ''}">
              </div>
            </div>
          </div>
        `,
        showCancelButton: true,
        confirmButtonColor: '#1e40af',
        cancelButtonColor: '#64748b',
        confirmButtonText: existing ? 'บันทึกการแก้ไข' : 'เพิ่มรายการพัสดุ',
        cancelButtonText: 'ยกเลิก',
        preConfirm: async () => {
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
          const on_hand_pieces = existing
            ? Number(existing.on_hand_pieces)
            : Math.max(0, parseInt(document.getElementById('swal-item-onhand').value, 10) || 0);
          const min_alert = Math.max(0, parseInt(document.getElementById('swal-item-min').value, 10) || 0);
          const monthly_limit = Math.max(0, parseInt(document.getElementById('swal-item-monthly-limit').value, 10) || 0);

          if (!name) {
            Swal.showValidationMessage('กรุณาระบุชื่อรายการพัสดุ');
            return false;
          }

          const uploadedPiece = await readFileAsDataURL(document.getElementById('swal-item-file-piece'));
          const uploadedBox = await readFileAsDataURL(document.getElementById('swal-item-file-box'));
          const defaultFallbackImg = 'assets/images/แฟ้มเสนอ เล่ม.jpeg';
          const image_piece = uploadedPiece || document.getElementById('swal-item-img-piece').value.trim() || defaultFallbackImg;
          const image_box = uploadedBox || document.getElementById('swal-item-img-box').value.trim() || image_piece;

          return {
            name,
            category,
            is_multi_unit,
            unit_box_name,
            unit_piece_name,
            pieces_per_box,
            on_hand_pieces,
            min_alert,
            monthly_limit,
            image_piece,
            image_box
          };
        }
      }).then((result) => {
        if (!result.isConfirmed || !result.value) return;
        const val = result.value;
        const currentItems = getItemsDB();
        let savedItem = null;

        if (existing) {
          const idx = currentItems.findIndex(i => Number(i.id) === Number(existing.id));
          if (idx !== -1) {
            currentItems[idx] = { ...currentItems[idx], ...val };
            savedItem = currentItems[idx];
          }
        } else {
          const maxId = currentItems.reduce((m, i) => Math.max(m, Number(i.id) || 0), 0);
          savedItem = {
            id: maxId + 1,
            ...val,
            reserved_pieces: 0
          };
          currentItems.push(savedItem);
        }

        saveItemsDB(currentItems);
        if (savedItem) postToMySQLAPI('saveItem', savedItem);
        renderInventoryTable();

        Swal.fire({
          icon: 'success',
          title: existing ? 'แก้ไขรายการพัสดุสำเร็จ' : 'เพิ่มรายการพัสดุใหม่สำเร็จ',
          text: `"${val.name}" พร้อมให้เบิกใช้งานในหน้าแคตตาล็อกทันที`,
          timer: 2000,
          showConfirmButton: false
        });
      });
    }

    function deleteInventoryItem(itemId) {
      const items = getItemsDB();
      const target = items.find(i => Number(i.id) === Number(itemId));
      if (!target) return;

      Swal.fire({
        title: 'ยืนยันการลบรายการพัสดุ?',
        text: `ต้องการลบ "${target.name}" ออกจากคลังพัสดุใช่หรือไม่`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ลบรายการพัสดุ',
        cancelButtonText: 'ยกเลิก'
      }).then(async (result) => {
        if (!result.isConfirmed) return;
        const apiRes = await postToMySQLAPI('deleteItem', { id: itemId });
        if (apiRes && apiRes.status === 'error') {
          Swal.fire({
            icon: 'error',
            title: 'ลบรายการไม่สำเร็จ',
            text: apiRes.message || 'คุณไม่มีสิทธิ์หรือรายการไม่สามารถลบได้'
          });
          return;
        }
        const updated = items.filter(i => Number(i.id) !== Number(itemId));
        saveItemsDB(updated);
        renderInventoryTable();
        Swal.fire({
          icon: 'success',
          title: 'ลบรายการพัสดุเรียบร้อยแล้ว',
          timer: 1500,
          showConfirmButton: false
        });
      });
    }

    // User & Department Management (Staff Portal)
    function getAllDeptNames() {
      const deptsData = getDeptsDB();
      const names = [];
      deptsData.forEach(cat => {
        (cat.items || []).forEach(it => {
          if (it.value && !names.includes(it.value)) names.push(it.value);
        });
      });
      return names;
    }

    function ensureDeptExists(deptName) {
      const clean = (deptName || '').trim();
      if (!clean) return;
      const deptsData = getDeptsDB();
      if (deptsData.length === 0) {
        deptsData.push({ category: 'สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)', items: [] });
      }
      const exists = deptsData.some(c => (c.items || []).some(it => it.value === clean));
      if (!exists) {
        deptsData[0].items.push({ label: clean, value: clean, sub: false });
        saveDeptsDB(deptsData);
        postToMySQLAPI('addDepartment', { category: deptsData[0].category, name: clean });
      }
    }

    function renderStaffUsersTable() {
      const users = getUsersDB();
      const deptNames = getAllDeptNames();

      const navUsersBadge = document.getElementById('navUsersBadge');
      if (navUsersBadge) navUsersBadge.innerText = users.length;

      const totalUsersEl = document.getElementById('metricTotalUsers');
      if (totalUsersEl) {
        totalUsersEl.innerHTML = `${users.length.toLocaleString()} <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">ท่าน</small>`;
      }
      const totalDeptsEl = document.getElementById('metricTotalDepts');
      if (totalDeptsEl) {
        totalDeptsEl.innerHTML = `${deptNames.length.toLocaleString()} <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">หน่วยงาน</small>`;
      }
      const allQuotas = getQuotasDB();
      const totalQuotasEl = document.getElementById('metricTotalQuotas');
      if (totalQuotasEl) {
        totalQuotasEl.innerHTML = `${allQuotas.length.toLocaleString()} <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">กฎ</small>`;
      }

      const filterSelect = document.getElementById('staffUserDeptFilter');
      if (filterSelect) {
        const prevVal = filterSelect.value || 'ALL';
        filterSelect.innerHTML = `<option value="ALL">ทุกกลุ่มงาน / หน่วยงานทั้งหมด (${deptNames.length})</option>` +
          deptNames.map(d => `<option value="${d}">${d}</option>`).join('');
        if (deptNames.includes(prevVal)) filterSelect.value = prevVal;
      }

      const searchEl = document.getElementById('staffUserSearchInput');
      const q = (searchEl ? searchEl.value : '').trim().toLowerCase();
      const deptFilter = filterSelect ? filterSelect.value : 'ALL';

      const filtered = users.filter(u => {
        const matchDept = deptFilter === 'ALL' || u.dept === deptFilter;
        const matchSearch = !q ||
          (u.username && u.username.toLowerCase().includes(q)) ||
          (u.name && u.name.toLowerCase().includes(q)) ||
          (u.position && u.position.toLowerCase().includes(q)) ||
          (u.dept && u.dept.toLowerCase().includes(q)) ||
          (u.phone && u.phone.toLowerCase().includes(q));
        return matchDept && matchSearch;
      });

      const tbody = document.getElementById('staffUsersTableBody');
      if (!tbody) return;

      if (filtered.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="9" style="text-align: center; padding: 2.5rem; color: var(--neutral-400);">
              ไม่พบรายชื่อบุคลากรที่ตรงกับเงื่อนไขการค้นหา
            </td>
          </tr>
        `;
        renderQuotaRulesSection();
        return;
      }

      tbody.innerHTML = filtered.map((u, idx) => {
        const uRole = String(u.role || (['wasana.c', 'jeerawan.b', 'patcharaporn.k', 'sineenart.l'].includes((u.username || '').toLowerCase()) ? 'HEAD' : 'REQUESTER')).toUpperCase();
        let roleBadge = `<span style="background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 999px;">ผู้ขอเบิก</span>`;
        if (uRole === 'STAFF') {
          roleBadge = `<span style="background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 999px;">เจ้าหน้าที่พัสดุ</span>`;
        } else if (uRole === 'HEAD') {
          roleBadge = `<span style="background: #f5f3ff; color: #6d28d9; border: 1px solid #ddd6fe; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 999px;">หัวหน้าผู้อนุมัติ</span>`;
        } else if (uRole === 'ADMIN') {
          roleBadge = `<span style="background: #f1f5f9; color: #0f172a; border: 1px solid #cbd5e1; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 999px;">ผู้ดูแลระบบ</span>`;
        }
        const userRules = allQuotas.filter(q =>
          String(q.targetType || q.target_type || '').toUpperCase() === 'USER' &&
          String(q.targetKey || q.target_key || '').trim().toLowerCase() === String(u.name || '').trim().toLowerCase()
        );
        let userQuotaBadge = `<span style="color: var(--neutral-400); font-size: 0.78rem;">ตามมาตรฐานคลัง</span>`;
        if (userRules.length === 1) {
          const r = userRules[0];
          const lim = Number(r.monthlyLimit ?? r.monthly_limit ?? 0);
          const itemLbl = Number(r.itemId ?? r.item_id ?? 0) === 0 ? 'ทุกพัสดุ' : (r.itemName || 'เฉพาะรายการ');
          userQuotaBadge = `<span style="background: #fffbeb; color: #b45309; border: 1px solid #fde68a; font-size: 0.74rem; font-weight: 600; padding: 3px 8px; border-radius: 6px; display: inline-block;">${escapeHtml(itemLbl)}: ${lim > 0 ? lim.toLocaleString() + '/ด.' : 'ไม่จำกัด'}</span>`;
        } else if (userRules.length > 1) {
          userQuotaBadge = `<span style="background: #fffbeb; color: #b45309; border: 1px solid #fde68a; font-size: 0.74rem; font-weight: 600; padding: 3px 8px; border-radius: 6px; display: inline-block;">กำหนดเฉพาะ ${userRules.length} รายการ</span>`;
        }
        const safeJsName = String(u.name || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'");
        return `
        <tr>
          <td style="text-align: center; color: var(--neutral-600);">${idx + 1}</td>
          <td>
            <code style="background: var(--neutral-100); color: var(--primary); padding: 3px 8px; border-radius: 6px; font-size: 0.825rem; font-weight: 600; border: 1px solid var(--neutral-200);">${u.username || '-'}</code>
          </td>
          <td>${roleBadge}</td>
          <td><strong>${escapeHtml(u.name)}</strong></td>
          <td style="color: var(--neutral-700);">${escapeHtml(u.position || '-')}</td>
          <td>
            <span style="background: var(--primary-light); color: var(--primary); font-size: 0.775rem; font-weight: 600; padding: 3px 10px; border-radius: 999px; border: 1px solid var(--primary-border); display: inline-block;">
              ${escapeHtml(u.dept || '-')}
            </span>
          </td>
          <td style="color: var(--neutral-600);">${escapeHtml(u.phone || '-')}</td>
          <td>${userQuotaBadge}</td>
          <td style="text-align: right; white-space: nowrap;">
            <button class="btn btn-outline" style="padding: 4px 8px; font-size: 0.75rem; margin-right: 4px; color: #b45309; border-color: #fcd34d; background: #fffbeb;" onclick="openQuotaModal('USER', '${safeJsName}')">
              โควตา
            </button>
            <button class="btn btn-outline" style="padding: 4px 10px; font-size: 0.775rem; margin-right: 4px;" onclick="openUserModal(${u.id})">
              แก้ไข
            </button>
            <button class="btn btn-outline" style="padding: 4px 10px; font-size: 0.775rem; color: var(--danger);" onclick="deleteStaffUser(${u.id})">
              ลบ
            </button>
          </td>
        </tr>
      `;}).join('');
      renderQuotaRulesSection();
    }

    function openUserModal(userId = null) {
      const currentUsers = getUsersDB();
      const existing = userId !== null ? currentUsers.find(u => Number(u.id) === Number(userId)) : null;
      const deptNames = getAllDeptNames();
      const curRole = existing ? String(existing.role || (['wasana.c', 'jeerawan.b', 'patcharaporn.k', 'sineenart.l'].includes((existing.username || '').toLowerCase()) ? 'HEAD' : 'REQUESTER')).toUpperCase() : 'REQUESTER';

      const deptOptionsHtml = deptNames.map(d =>
        `<option value="${d}" ${existing && existing.dept === d ? 'selected' : ''}>${d}</option>`
      ).join('') + `<option value="__NEW__">+ เพิ่มกลุ่มงาน / หน่วยงานใหม่...</option>`;

      Swal.fire({
        title: existing ? 'แก้ไขข้อมูลบุคลากรและสิทธิ์' : 'เพิ่มรายชื่อบุคลากรและกำหนดสิทธิ์',
        html: `
          <div style="text-align: left; display: flex; flex-direction: column; gap: 0.8rem; margin-top: 0.5rem;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
              <div>
                <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">ชื่อผู้ใช้งาน *</label>
                <input id="swal-user-uname" class="swal2-input" style="margin: 0; width: 100%; font-size: 0.92rem; height: 40px;" placeholder="กรอกชื่อผู้ใช้งาน" value="${existing ? (existing.username || '') : ''}">
              </div>
              <div>
                <label style="font-size: 0.85rem; font-weight: 600; color: #1e40af; display: block; margin-bottom: 4px;">บทบาทสิทธิ์ในระบบ *</label>
                <select id="swal-user-role" class="swal2-input" style="margin: 0; width: 100%; font-size: 0.88rem; height: 40px;">
                  <option value="REQUESTER" ${curRole === 'REQUESTER' ? 'selected' : ''}>ผู้ขอเบิกพัสดุ</option>
                  <option value="STAFF" ${curRole === 'STAFF' ? 'selected' : ''}>เจ้าหน้าที่พัสดุ (ผู้คัดกรอง)</option>
                  <option value="HEAD" ${curRole === 'HEAD' ? 'selected' : ''}>หัวหน้าหน่วยงาน (ผู้อนุมัติ)</option>
                  <option value="ADMIN" ${curRole === 'ADMIN' ? 'selected' : ''}>ผู้ดูแลระบบสูงสุด</option>
                </select>
              </div>
            </div>
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">รหัสผ่านเข้าใช้งาน ${existing ? '<span style="font-weight: normal; color: #64748b;">(เว้นว่างหากไม่เปลี่ยน)</span>' : '*'}</label>
              <input type="password" id="swal-user-pass" class="swal2-input" style="margin: 0; width: 100%; font-size: 0.95rem; height: 40px;" placeholder="${existing ? 'กรอกรหัสผ่านใหม่เพื่อเปลี่ยน' : 'กำหนดรหัสผ่านเข้าสู่ระบบ'}">
            </div>
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">ชื่อ-นามสกุล บุคลากร *</label>
              <input id="swal-user-name" class="swal2-input" style="margin: 0; width: 100%; font-size: 0.95rem; height: 40px;" placeholder="กรอกชื่อ-นามสกุลจริง" value="${existing ? existing.name : ''}">
            </div>
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">ตำแหน่ง</label>
              <input id="swal-user-pos" class="swal2-input" style="margin: 0; width: 100%; font-size: 0.95rem; height: 40px;" placeholder="ระบุตำแหน่งงาน" value="${existing ? (existing.position || '') : ''}">
            </div>
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">กลุ่มงาน / หน่วยงานที่สังกัด (สวท.) *</label>
              <select id="swal-user-dept" class="swal2-input" style="margin: 0; width: 100%; font-size: 0.9rem; height: 40px;" onchange="document.getElementById('swal-new-dept-wrap').style.display = this.value === '__NEW__' ? 'block' : 'none';">
                ${deptOptionsHtml}
              </select>
            </div>
            <div id="swal-new-dept-wrap" style="display: none;">
              <label style="font-size: 0.85rem; font-weight: 600; color: #1e40af; display: block; margin-bottom: 4px;">ระบุชื่อกลุ่มงาน / หน่วยงานใหม่ *</label>
              <input id="swal-user-new-dept" class="swal2-input" style="margin: 0; width: 100%; font-size: 0.95rem; height: 40px;" placeholder="ระบุชื่อกลุ่มงานใหม่">
            </div>
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">เบอร์โทรศัพท์ติดต่อ</label>
              <input id="swal-user-phone" class="swal2-input" style="margin: 0; width: 100%; font-size: 0.95rem; height: 40px;" placeholder="กรอกเบอร์โทรศัพท์ติดต่อ" value="${existing ? (existing.phone || '') : ''}">
            </div>
          </div>
        `,
        showCancelButton: true,
        confirmButtonColor: '#1e40af',
        cancelButtonColor: '#64748b',
        confirmButtonText: existing ? 'บันทึกการแก้ไข' : 'เพิ่มรายชื่อบุคลากร',
        cancelButtonText: 'ยกเลิก',
        preConfirm: () => {
          const username = document.getElementById('swal-user-uname').value.trim();
          const role = document.getElementById('swal-user-role').value;
          const password = document.getElementById('swal-user-pass').value.trim();
          const name = document.getElementById('swal-user-name').value.trim();
          const position = document.getElementById('swal-user-pos').value.trim();
          const deptSel = document.getElementById('swal-user-dept').value;
          const newDept = document.getElementById('swal-user-new-dept').value.trim();
          const phone = document.getElementById('swal-user-phone').value.trim();
          const finalDept = deptSel === '__NEW__' ? newDept : deptSel;

          if (!username) {
            Swal.showValidationMessage('กรุณาระบุชื่อผู้ใช้งาน สำหรับเข้าสู่ระบบ');
            return false;
          }
          const duplicateUser = currentUsers.find(u =>
            u.username && u.username.toLowerCase() === username.toLowerCase() &&
            (!existing || Number(u.id) !== Number(existing.id))
          );
          if (duplicateUser) {
            Swal.showValidationMessage(`ชื่อผู้ใช้งาน "${username}" ซ้ำกับบุคลากรท่านอื่น กรุณาเลือกชื่อผู้ใช้งานอื่น`);
            return false;
          }
          if (!existing && !password) {
            Swal.showValidationMessage('กรุณากำหนดรหัสผ่าน สำหรับผู้ใช้งานใหม่');
            return false;
          }
          if (!name) {
            Swal.showValidationMessage('กรุณาระบุชื่อ-นามสกุล บุคลากร');
            return false;
          }
          if (!finalDept) {
            Swal.showValidationMessage('กรุณาระบุกลุ่มงาน / หน่วยงานที่สังกัด');
            return false;
          }
          return { username, role, password, name, position, dept: finalDept, phone };
        }
      }).then(async (result) => {
        if (!result.isConfirmed || !result.value) return;
        const val = result.value;
        ensureDeptExists(val.dept);

        const currentUsers = getUsersDB();
        let savedUser = null;
        if (existing) {
          const idx = currentUsers.findIndex(u => Number(u.id) === Number(existing.id));
          if (idx !== -1) {
            const updatedUser = {
              ...currentUsers[idx],
              name: val.name,
              username: val.username,
              role: val.role,
              position: val.position,
              dept: val.dept,
              phone: val.phone
            };
            if (val.password) updatedUser.password = val.password;
            currentUsers[idx] = updatedUser;
            savedUser = currentUsers[idx];
          }
        } else {
          const maxId = currentUsers.reduce((m, u) => Math.max(m, Number(u.id) || 0), 0);
          savedUser = {
            id: maxId + 1,
            name: val.name,
            username: val.username,
            role: val.role,
            password: val.password || 'sdu1234',
            position: val.position,
            dept: val.dept,
            phone: val.phone
          };
          currentUsers.push(savedUser);
        }

        if (savedUser) {
          const apiRes = await postToMySQLAPI('saveUser', { ...savedUser, role: val.role });
          if (apiRes && apiRes.status === 'error') {
            Swal.fire({
              icon: 'error',
              title: 'บันทึกข้อมูลบุคลากรไม่สำเร็จ',
              text: apiRes.message || 'ไม่สามารถบันทึกการเปลี่ยนแปลงสิทธิ์หรือข้อมูลบุคลากรได้'
            });
            return;
          }
          if (apiRes && apiRes.data) {
            savedUser = { ...savedUser, ...apiRes.data, role: (apiRes.data.role || val.role) };
            const hit = currentUsers.findIndex(u => Number(u.id) === Number(savedUser.id));
            if (hit !== -1) currentUsers[hit] = savedUser;
            else if (!existing && currentUsers.length > 0) currentUsers[currentUsers.length - 1] = savedUser;
          }
        }

        saveUsersDB(currentUsers);
        renderStaffUsersTable();

        Swal.fire({
          icon: 'success',
          title: existing ? 'อัปเดตข้อมูลบุคลากรสำเร็จ' : 'เพิ่มรายชื่อบุคลากรสำเร็จ',
          text: `${val.name} (${val.dept}) พร้อมให้ใช้ชื่อ ${val.username} เข้าสู่ระบบขอเบิกพัสดุทันที`,
          timer: 2000,
          showConfirmButton: false
        });
      });
    }

    function deleteStaffUser(userId) {
      const users = getUsersDB();
      const target = users.find(u => Number(u.id) === Number(userId));
      if (!target) return;

      Swal.fire({
        title: 'ยืนยันการลบรายชื่อบุคลากร?',
        text: `ต้องการลบ "${target.name}" (${target.dept}) ออกจากระบบใช่หรือไม่`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ลบรายชื่อ',
        cancelButtonText: 'ยกเลิก'
      }).then(async (result) => {
        if (!result.isConfirmed) return;
        const apiRes = await postToMySQLAPI('deleteUser', { id: userId });
        if (apiRes && apiRes.status === 'error') {
          Swal.fire({
            icon: 'error',
            title: 'ลบรายชื่อไม่สำเร็จ',
            text: apiRes.message || 'คุณไม่มีสิทธิ์ลบข้อมูลบุคลากร'
          });
          return;
        }
        const updated = users.filter(u => Number(u.id) !== Number(userId));
        saveUsersDB(updated);
        renderStaffUsersTable();
        Swal.fire({
          icon: 'success',
          title: 'ลบรายชื่อเรียบร้อยแล้ว',
          timer: 1500,
          showConfirmButton: false
        });
      });
    }

    async function openManageDeptsModal() {
      let deptsList = [];
      try {
        const res = await fetch(`${MYSQL_API_URL}?action=getDepartments`);
        const json = await res.json();
        if (json && json.status === 'success' && Array.isArray(json.data)) {
          deptsList = json.data;
        }
      } catch (e) {
        console.warn('API error, using local fallback:', e);
      }

      if (deptsList.length === 0) {
        const localDepts = getAllDeptNames();
        const users = getUsersDB();
        deptsList = localDepts.map((d, i) => ({
          id: i + 1,
          name: d,
          category: 'สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)',
          user_count: users.filter(u => u.dept === d).length
        }));
      }

      const allQuotas = getQuotasDB();
      const rowsHtml = deptsList.map((d, idx) => {
        const dRules = allQuotas.filter(q =>
          String(q.targetType || q.target_type || '').toUpperCase() === 'DEPT' &&
          String(q.targetKey || q.target_key || '').trim() === String(d.name || '').trim()
        );
        const quotaBadge = dRules.length > 0
          ? `<span style="background:#fffbeb; color:#b45309; border:1px solid #fde68a; padding:2px 8px; border-radius:999px; font-size:0.75rem; font-weight:600;">${dRules.length} กฎโควตา</span>`
          : `<span style="color:#94a3b8; font-size:0.75rem;">ไม่จำกัด</span>`;
        const safeJsDept = String(d.name || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'");
        return `
        <tr style="border-bottom: 1px solid #e2e8f0;">
          <td style="padding: 10px 8px; text-align: center; color: #64748b; font-weight: 500;">${idx + 1}</td>
          <td style="padding: 10px 8px; font-weight: 600; color: #1e293b; text-align: left;">
            ${escapeHtml(d.name)}
          </td>
          <td style="padding: 10px 8px; text-align: center;">
            <span style="background: ${(d.user_count || 0) > 0 ? '#dbeafe' : '#f1f5f9'}; color: ${(d.user_count || 0) > 0 ? '#1e40af' : '#64748b'}; padding: 3px 10px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600;">
              ${d.user_count || 0} ท่าน
            </span>
          </td>
          <td style="padding: 10px 8px; text-align: center;">${quotaBadge}</td>
          <td style="padding: 10px 8px; text-align: right; white-space: nowrap;">
            <button class="btn btn-outline" style="padding: 4px 10px; font-size: 0.775rem; margin-right: 4px; color: #b45309; border-color: #fcd34d; background: #fffbeb;" onclick="openQuotaModal('DEPT', '${safeJsDept}')">
              ตั้งโควตา
            </button>
            <button class="btn btn-outline" style="padding: 4px 10px; font-size: 0.775rem; margin-right: 4px;" onclick="promptEditDepartment(${d.id}, '${safeJsDept}')">
              ${vIcons.pen} แก้ไขชื่อ
            </button>
            <button class="btn btn-outline" style="padding: 4px 10px; font-size: 0.775rem; color: #dc2626; border-color: #fca5a5;" onclick="promptDeleteDepartment(${d.id}, '${safeJsDept}', ${d.user_count || 0})">
              ${vIcons.trash} ลบ
            </button>
          </td>
        </tr>
      `;}).join('');

      Swal.fire({
        title: 'จัดการกลุ่มงาน / หน่วยงาน (สวท.)',
        width: '880px',
        html: `
          <div style="text-align: left; margin-top: 0.5rem; font-size: 0.9rem;">
            <!-- เพิ่มกลุ่มงานใหม่ -->
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px; margin-bottom: 1rem;">
              <label style="font-weight: 600; color: #1e293b; display: block; margin-bottom: 6px;">+ เพิ่มกลุ่มงาน / หน่วยงานใหม่</label>
              <div style="display: flex; gap: 8px;">
                <input type="text" id="manage-new-dept-name" class="swal2-input" style="margin: 0; flex: 1; font-size: 0.9rem; height: 38px;" placeholder="ระบุชื่อกลุ่มงาน เช่น กลุ่มงานพัฒนาวิชาการ">
                <button type="button" class="btn btn-primary" style="padding: 0 16px; height: 38px; white-space: nowrap;" onclick="submitNewDeptFromManage()">+ เพิ่มหน่วยงาน</button>
              </div>
            </div>

            <!-- ตารางรายชื่อกลุ่มงาน -->
            <div style="max-height: 360px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 8px;">
              <table style="width: 100%; border-collapse: collapse; font-size: 0.875rem;">
                <thead>
                  <tr style="background: #f1f5f9; border-bottom: 2px solid #cbd5e1; position: sticky; top: 0; z-index: 1;">
                    <th style="padding: 10px 8px; text-align: center; width: 45px; color: #475569;">#</th>
                    <th style="padding: 10px 8px; text-align: left; color: #475569;">ชื่อกลุ่มงาน / หน่วยงาน</th>
                    <th style="padding: 10px 8px; text-align: center; width: 110px; color: #475569;">บุคลากร</th>
                    <th style="padding: 10px 8px; text-align: center; width: 120px; color: #475569;">โควตาประจำเดือน</th>
                    <th style="padding: 10px 8px; text-align: right; width: 245px; color: #475569;">จัดการ</th>
                  </tr>
                </thead>
                <tbody id="manageDeptsTbody">
                  ${rowsHtml || '<tr><td colspan="5" style="text-align: center; padding: 1.5rem; color: #94a3b8;">ยังไม่มีกลุ่มงานในระบบ</td></tr>'}
                </tbody>
              </table>
            </div>
          </div>
        `,
        showConfirmButton: false,
        showCloseButton: true,
        didOpen: () => {
          const input = document.getElementById('manage-new-dept-name');
          if (input) {
            input.addEventListener('keydown', (e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                submitNewDeptFromManage();
              }
            });
          }
        }
      });
    }

    async function submitNewDeptFromManage() {
      const input = document.getElementById('manage-new-dept-name');
      const name = input ? input.value.trim() : '';
      if (!name) {
        Swal.showValidationMessage('กรุณาระบุชื่อกลุ่มงาน / หน่วยงาน');
        return;
      }

      Swal.showLoading();
      try {
        const res = await postToMySQLAPI('addDepartment', { name });
        if (res && res.status === 'error') {
          Swal.fire({
            icon: 'error',
            title: 'ไม่สามารถเพิ่มหน่วยงานได้',
            text: res.message || 'ชื่อหน่วยงานนี้มีอยู่ในระบบแล้ว'
          });
          return;
        }

        ensureDeptExists(name);
        await syncFromMySQLAPI();
        loadStaffDashboard();

        Swal.fire({
          icon: 'success',
          title: 'เพิ่มหน่วยงานสำเร็จ',
          text: `เพิ่ม "${name}" เข้าสู่ระบบเรียบร้อยแล้ว`,
          timer: 1500,
          showConfirmButton: false
        }).then(() => {
          openManageDeptsModal();
        });
      } catch (err) {
        console.error('Error adding department:', err);
        ensureDeptExists(name);
        loadStaffDashboard();
        openManageDeptsModal();
      }
    }

    async function promptEditDepartment(id, currentName) {
      const { value: newName } = await Swal.fire({
        title: 'แก้ไขชื่อกลุ่มงาน / หน่วยงาน',
        input: 'text',
        inputValue: currentName,
        inputLabel: 'ชื่อกลุ่มงาน / หน่วยงานใหม่ *',
        showCancelButton: true,
        confirmButtonColor: '#1e40af',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'บันทึกการแก้ไข',
        cancelButtonText: 'ยกเลิก',
        inputValidator: (val) => {
          if (!val || !val.trim()) return 'กรุณาระบุชื่อกลุ่มงาน / หน่วยงาน';
          if (val.trim() === currentName) return 'ชื่อหน่วยงานไม่มีการเปลี่ยนแปลง';
        }
      });

      if (!newName || !newName.trim()) return;
      const cleanNew = newName.trim();

      Swal.showLoading();
      try {
        const res = await postToMySQLAPI('updateDepartment', {
          id: id,
          old_name: currentName,
          name: cleanNew
        });

        if (res && res.status === 'error') {
          Swal.fire({
            icon: 'error',
            title: 'ไม่สามารถแก้ไขได้',
            text: res.message || 'เกิดข้อผิดพลาดในการแก้ไขชื่อหน่วยงาน'
          });
          return;
        }

        // Update local storage depts
        const deptsData = getDeptsDB();
        deptsData.forEach(c => {
          (c.items || []).forEach(it => {
            if (it.value === currentName) {
              it.value = cleanNew;
              it.label = cleanNew;
            }
          });
        });
        saveDeptsDB(deptsData);

        // Cascade update local users
        const users = getUsersDB();
        users.forEach(u => {
          if (u.dept === currentName) {
            u.dept = cleanNew;
          }
        });
        saveUsersDB(users);

        await syncFromMySQLAPI();
        loadStaffDashboard();

        Swal.fire({
          icon: 'success',
          title: 'แก้ไขชื่อหน่วยงานสำเร็จ',
          text: `เปลี่ยนชื่อเป็น "${cleanNew}" เรียบร้อยแล้ว`,
          timer: 1600,
          showConfirmButton: false
        }).then(() => {
          openManageDeptsModal();
        });
      } catch (err) {
        console.error('Error updating department:', err);
        Swal.fire('ข้อผิดพลาด', 'ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้', 'error');
      }
    }

    async function promptDeleteDepartment(id, name, userCount) {
      if (userCount > 0) {
        Swal.fire({
          icon: 'warning',
          title: 'ไม่สามารถลบหน่วยงานนี้ได้',
          html: `
            <div style="text-align: left; font-size: 0.9rem;">
              <p>กลุ่มงาน <strong>"${escapeHtml(name)}"</strong> ยังมีบุคลากรสังกัดอยู่จำนวน <strong>${userCount} ท่าน</strong></p>
              <div style="background: #fef2f2; border: 1px solid #fee2e2; border-radius: 6px; padding: 10px; color: #991b1b; margin-top: 8px;">
                กรุณาแก้ไขหรือเปลี่ยนสังกัดของบุคลากรกลุ่มนี้ให้เรียบร้อยก่อน จึงจะสามารถลบหน่วยงานออกจากระบบได้
              </div>
            </div>
          `,
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'รับทราบ'
        }).then(() => {
          openManageDeptsModal();
        });
        return;
      }

      const result = await Swal.fire({
        title: 'ยืนยันการลบกลุ่มงาน / หน่วยงาน',
        text: `ต้องการลบกลุ่มงาน "${name}" ออกจากระบบใช่หรือไม่?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ใช่, ลบหน่วยงาน',
        cancelButtonText: 'ยกเลิก'
      });

      if (!result.isConfirmed) {
        openManageDeptsModal();
        return;
      }

      Swal.showLoading();
      try {
        const res = await postToMySQLAPI('deleteDepartment', { id: id, name: name });
        if (res && res.status === 'error') {
          Swal.fire('ข้อผิดพลาด', res.message || 'ไม่สามารถลบหน่วยงานได้', 'error');
          return;
        }

        // Remove from local storage depts
        const deptsData = getDeptsDB();
        deptsData.forEach(c => {
          if (c.items) {
            c.items = c.items.filter(it => it.value !== name);
          }
        });
        saveDeptsDB(deptsData);

        await syncFromMySQLAPI();
        loadStaffDashboard();

        Swal.fire({
          icon: 'success',
          title: 'ลบหน่วยงานสำเร็จ',
          text: `ลบกลุ่มงาน "${name}" เรียบร้อยแล้ว`,
          timer: 1600,
          showConfirmButton: false
        }).then(() => {
          openManageDeptsModal();
        });
      } catch (err) {
        console.error('Error deleting department:', err);
        Swal.fire('ข้อผิดพลาด', 'ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้', 'error');
      }
    }

    // Per-Personnel & Per-Department Quota Management (Staff Portal)
    let currentQuotaFilterType = 'ALL';

    function filterQuotaRulesType(qType, btn) {
      currentQuotaFilterType = qType || 'ALL';
      document.querySelectorAll('.quota-filter-btn').forEach(b => {
        const isActive = b.getAttribute('data-qtype') === currentQuotaFilterType;
        b.style.background = isActive ? 'var(--primary)' : 'white';
        b.style.color = isActive ? 'white' : '#334155';
        b.style.borderColor = isActive ? 'var(--primary)' : '#cbd5e1';
      });
      renderQuotaRulesSection();
    }

    function getMonthlyUsageForQuotaRule(targetType, targetKey, itemId) {
      const reqs = getReqsDB();
      const now = new Date();
      const curYm = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
      const curBeYm = `REQ-${now.getFullYear() + 543}${String(now.getMonth() + 1).padStart(2, '0')}`;
      const cleanTarget = String(targetKey || '').trim().toLowerCase();
      let totalUsed = 0;

      reqs.forEach(r => {
        if (r.status === 'REJECTED') return;
        const isThisMonth = (r.created_at && r.created_at.startsWith(curYm)) || (r.id && r.id.startsWith(curBeYm));
        if (!isThisMonth) return;
        const matchesTarget = targetType === 'DEPT'
          ? String(r.dept || '').trim().toLowerCase() === cleanTarget
          : String(r.requester || '').trim().toLowerCase() === cleanTarget;
        if (!matchesTarget) return;
        (r.items || []).forEach(it => {
          if (Number(itemId) === 0 || Number(it.itemId) === Number(itemId)) {
            totalUsed += Number(it.totalPieces || 0);
          }
        });
      });
      return totalUsed;
    }

    function renderQuotaRulesSection() {
      const tbody = document.getElementById('quotaRulesTableBody');
      if (!tbody) return;
      const quotas = getQuotasDB();
      const items = getItemsDB();
      const itemsMap = new Map(items.map(i => [Number(i.id), i]));

      const filtered = quotas.filter(q => {
        const t = String(q.targetType || q.target_type || '').toUpperCase();
        return currentQuotaFilterType === 'ALL' || t === currentQuotaFilterType;
      });

      if (filtered.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="7" style="text-align: center; padding: 2rem; color: var(--neutral-400);">
              ยังไม่มีกฎโควต้าเฉพาะตามบุคลากรหรือกลุ่มงาน (คลิก "+ กำหนดโควตากลุ่มงาน" หรือ "+ กำหนดโควตารายบุคลากร" เพื่อตั้งค่า)
            </td>
          </tr>
        `;
        return;
      }

      tbody.innerHTML = filtered.map(q => {
        const tType = String(q.targetType || q.target_type || 'DEPT').toUpperCase();
        const tKey = q.targetKey || q.target_key || '';
        const iId = Number(q.itemId ?? q.item_id ?? 0);
        const lim = Number(q.monthlyLimit ?? q.monthly_limit ?? 0);
        const itemObj = iId > 0 ? itemsMap.get(iId) : null;
        const itemName = iId === 0 ? 'ทุกพัสดุในคลัง (ค่าเริ่มต้นต่อรายการ)' : (itemObj ? itemObj.name : (q.itemName || `พัสดุ #${iId}`));
        const unitName = itemObj ? (itemObj.unit_piece_name || 'ชิ้น') : (q.unitPiece || 'ชิ้น');
        const used = getMonthlyUsageForQuotaRule(tType, tKey, iId);
        const pct = lim > 0 ? Math.min(100, Math.round((used / lim) * 100)) : 0;

        const typeBadge = tType === 'DEPT'
          ? `<span style="background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; padding: 3px 9px; border-radius: 999px; font-size: 0.75rem; font-weight: 600;">กลุ่มงาน</span>`
          : `<span style="background: #f5f3ff; color: #6d28d9; border: 1px solid #ddd6fe; padding: 3px 9px; border-radius: 999px; font-size: 0.75rem; font-weight: 600;">รายบุคลากร</span>`;

        const limitDisplay = lim > 0
          ? `<strong style="color: #b45309;">${lim.toLocaleString()} ${escapeHtml(unitName)}</strong>`
          : `<span style="background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; padding: 2px 8px; border-radius: 999px; font-size: 0.75rem; font-weight: 600;">ไม่จำกัด (ยกเว้น)</span>`;

        const usageColor = lim > 0 && used >= lim ? '#dc2626' : (lim > 0 && pct >= 80 ? '#d97706' : '#0f766e');

        return `
          <tr>
            <td>${typeBadge}</td>
            <td><strong>${escapeHtml(tKey)}</strong></td>
            <td style="color: var(--neutral-700);">${escapeHtml(itemName)}</td>
            <td>${limitDisplay}</td>
            <td>
              <span style="font-weight: 600; color: ${usageColor};">${used.toLocaleString()} ${escapeHtml(unitName)}</span>
              ${lim > 0 ? `<small style="color: var(--neutral-500);">(${pct}%)</small>` : ''}
            </td>
            <td style="color: var(--neutral-600); font-size: 0.825rem;">${escapeHtml(q.note || '-')}</td>
            <td style="text-align: right; white-space: nowrap;">
              <button class="btn btn-outline" style="padding: 4px 10px; font-size: 0.75rem; margin-right: 4px;" onclick="openQuotaModal('${tType}', '', ${q.id})">
                แก้ไข
              </button>
              <button class="btn btn-outline" style="padding: 4px 10px; font-size: 0.75rem; color: var(--danger);" onclick="deleteQuotaRule(${q.id})">
                ลบ
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }

    function openQuotaModal(defaultType = 'DEPT', defaultKey = '', ruleId = null) {
      const quotas = getQuotasDB();
      const existing = ruleId !== null ? quotas.find(q => Number(q.id) === Number(ruleId)) : null;
      const initType = existing ? String(existing.targetType || existing.target_type || 'DEPT').toUpperCase() : (defaultType || 'DEPT');
      const initKey = existing ? (existing.targetKey || existing.target_key || '') : (defaultKey || '');
      const initItemId = existing ? Number(existing.itemId ?? existing.item_id ?? 0) : 0;
      const initLimit = existing ? Number(existing.monthlyLimit ?? existing.monthly_limit ?? 0) : 500;
      const initNote = existing ? (existing.note || '') : '';

      const deptNames = getAllDeptNames();
      const users = getUsersDB();
      const items = getItemsDB();

      const buildTargetOptions = (tType, selectedKey) => {
        if (tType === 'DEPT') {
          return deptNames.map(d =>
            `<option value="${escapeHtml(d)}" ${d === selectedKey ? 'selected' : ''}>${escapeHtml(d)}</option>`
          ).join('');
        }
        return users.map(u =>
          `<option value="${escapeHtml(u.name)}" ${u.name === selectedKey ? 'selected' : ''}>${escapeHtml(u.name)} (${escapeHtml(u.dept || '-')})</option>`
        ).join('');
      };

      const itemOptions = `<option value="0" ${initItemId === 0 ? 'selected' : ''}>ทุกพัสดุในคลัง (กำหนดเพดานต่อรายการ)</option>` +
        items.map(it =>
          `<option value="${it.id}" ${Number(it.id) === initItemId ? 'selected' : ''}>${escapeHtml(it.name)} (หน่วย: ${escapeHtml(it.unit_piece_name || 'ชิ้น')})</option>`
        ).join('');

      Swal.fire({
        title: existing ? 'แก้ไขกฎโควตาประจำเดือน' : 'กำหนดโควต้าประจำเดือน (บุคลากร / กลุ่มงาน)',
        width: '560px',
        html: `
          <div style="text-align: left; display: flex; flex-direction: column; gap: 0.85rem; margin-top: 0.5rem;">
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">ประเภทเป้าหมาย *</label>
              <select id="swal-quota-type" class="swal2-input" style="margin: 0; width: 100%; height: 40px; font-size: 0.9rem;">
                <option value="DEPT" ${initType === 'DEPT' ? 'selected' : ''}>กลุ่มงาน / หน่วยงาน (ควบคุมยอดรวมทั้งหน่วยงาน)</option>
                <option value="USER" ${initType === 'USER' ? 'selected' : ''}>บุคลากรรายบุคคล (กำหนดสิทธิ์เฉพาะท่าน)</option>
              </select>
            </div>
            <div>
              <label id="swal-quota-target-label" style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">${initType === 'DEPT' ? 'เลือกกลุ่มงาน / หน่วยงาน *' : 'เลือกบุคลากร *'}</label>
              <select id="swal-quota-target" class="swal2-input" style="margin: 0; width: 100%; height: 40px; font-size: 0.9rem;">
                ${buildTargetOptions(initType, initKey)}
              </select>
            </div>
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">รายการพัสดุที่กำหนดโควตา *</label>
              <select id="swal-quota-item" class="swal2-input" style="margin: 0; width: 100%; height: 40px; font-size: 0.9rem;">
                ${itemOptions}
              </select>
            </div>
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #b45309; display: block; margin-bottom: 4px;">โควตาเบิกสูงสุดต่อเดือน (หน่วยย่อย / ชิ้น) *</label>
              <input type="number" id="swal-quota-limit" min="0" class="swal2-input" style="margin: 0; width: 100%; height: 40px; font-size: 0.95rem;" value="${initLimit}">
              <div style="font-size: 0.76rem; color: #64748b; margin-top: 4px;">ใส่ <strong>0</strong> หากต้องการยกเว้นไม่จำกัดโควตาเฉพาะเป้าหมายนี้ (สำหรับบุคลากร: จะแทนที่ค่ามาตรฐานของคลัง)</div>
            </div>
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">หมายเหตุ</label>
              <input type="text" id="swal-quota-note" class="swal2-input" style="margin: 0; width: 100%; height: 40px; font-size: 0.9rem;" placeholder="เช่น โควตาจัดสอบกลางภาค หรือ สิทธิ์หัวหน้างาน" value="${escapeHtml(initNote)}">
            </div>
          </div>
        `,
        showCancelButton: true,
        confirmButtonColor: '#1e40af',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'บันทึกกฎโควตา',
        cancelButtonText: 'ยกเลิก',
        didOpen: () => {
          const typeSel = document.getElementById('swal-quota-type');
          const targetSel = document.getElementById('swal-quota-target');
          const lbl = document.getElementById('swal-quota-target-label');
          if (typeSel && targetSel) {
            typeSel.addEventListener('change', () => {
              const t = typeSel.value;
              if (lbl) lbl.innerText = t === 'DEPT' ? 'เลือกกลุ่มงาน / หน่วยงาน *' : 'เลือกบุคลากร *';
              targetSel.innerHTML = buildTargetOptions(t, '');
            });
          }
        },
        preConfirm: () => {
          const targetType = document.getElementById('swal-quota-type').value;
          const targetKey = document.getElementById('swal-quota-target').value.trim();
          const itemId = Math.max(0, parseInt(document.getElementById('swal-quota-item').value, 10) || 0);
          const rawLimit = document.getElementById('swal-quota-limit').value;
          const monthlyLimit = Math.max(0, parseInt(rawLimit, 10));
          const note = document.getElementById('swal-quota-note').value.trim();
          if (!targetKey) {
            Swal.showValidationMessage('กรุณาเลือกกลุ่มงานหรือบุคลากร');
            return false;
          }
          if (isNaN(monthlyLimit) || monthlyLimit < 0) {
            Swal.showValidationMessage('จำนวนโควตาต้องเป็นตัวเลข 0 ขึ้นไป');
            return false;
          }
          return { id: existing ? existing.id : null, targetType, targetKey, itemId, monthlyLimit, note };
        }
      }).then(async (res) => {
        if (!res.isConfirmed || !res.value) return;
        const staff = getLoggedInStaff();
        const payload = { ...res.value, updatedBy: staff.name || staff.username || 'เจ้าหน้าที่พัสดุ สวท.' };
        const apiRes = await postToMySQLAPI('saveQuota', payload);
        if (apiRes && apiRes.status === 'error') {
          Swal.fire({ icon: 'error', title: 'บันทึกไม่สำเร็จ', text: apiRes.message || 'ไม่สามารถบันทึกกฎโควตาได้' });
          return;
        }
        const list = getQuotasDB();
        const itemMatch = items.find(i => Number(i.id) === Number(payload.itemId));
        const savedRecord = {
          id: (apiRes && apiRes.id) ? Number(apiRes.id) : (payload.id || (list.reduce((m, r) => Math.max(m, Number(r.id) || 0), 0) + 1)),
          targetType: payload.targetType,
          target_type: payload.targetType,
          targetKey: payload.targetKey,
          target_key: payload.targetKey,
          itemId: payload.itemId,
          item_id: payload.itemId,
          itemName: payload.itemId === 0 ? 'ทุกพัสดุในคลัง (ค่าเริ่มต้น)' : (itemMatch ? itemMatch.name : ''),
          unitPiece: itemMatch ? (itemMatch.unit_piece_name || 'ชิ้น') : 'ชิ้น',
          monthlyLimit: payload.monthlyLimit,
          monthly_limit: payload.monthlyLimit,
          note: payload.note,
          updatedBy: payload.updatedBy
        };
        const updatedList = list.filter(q =>
          Number(q.id) !== Number(savedRecord.id) &&
          !(String(q.targetType || q.target_type || '').toUpperCase() === payload.targetType &&
            String(q.targetKey || q.target_key || '').trim() === payload.targetKey &&
            Number(q.itemId ?? q.item_id ?? 0) === Number(payload.itemId))
        );
        updatedList.push(savedRecord);
        saveQuotasDB(updatedList);
        renderStaffUsersTable();
        Swal.fire({
          icon: 'success',
          title: 'บันทึกกฎโควตาสำเร็จ',
          text: `ตั้งค่าโควตาสำหรับ "${payload.targetKey}" เรียบร้อยแล้ว`,
          timer: 1600,
          showConfirmButton: false
        });
      });
    }

    function deleteQuotaRule(ruleId) {
      const list = getQuotasDB();
      const target = list.find(q => Number(q.id) === Number(ruleId));
      if (!target) return;
      Swal.fire({
        title: 'ยืนยันการลบกฎโควต้า?',
        text: `ต้องการลบกฎโควตาของ "${target.targetKey || target.target_key}" ใช่หรือไม่ (ระบบจะกลับไปใช้ค่ามาตรฐานของคลัง)`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ลบกฎโควตา',
        cancelButtonText: 'ยกเลิก'
      }).then(async (res) => {
        if (!res.isConfirmed) return;
        const apiRes = await postToMySQLAPI('deleteQuota', {
          id: ruleId,
          targetType: target.targetType || target.target_type,
          targetKey: target.targetKey || target.target_key,
          itemId: target.itemId ?? target.item_id ?? 0
        });
        if (apiRes && apiRes.status === 'error') {
          Swal.fire({ icon: 'error', title: 'ลบกฎไม่สำเร็จ', text: apiRes.message || 'ไม่สามารถลบกฎโควตาได้' });
          return;
        }
        saveQuotasDB(list.filter(q => Number(q.id) !== Number(ruleId)));
        renderStaffUsersTable();
        Swal.fire({ icon: 'success', title: 'ลบกฎโควตาเรียบร้อยแล้ว', timer: 1400, showConfirmButton: false });
      });
    }

    function openAddDeptModal() {
      openManageDeptsModal();
    }

    function loadStaffDashboard() {
      renderStaffRequisitions(currentStaffStatus);
      renderInventoryTable();
      renderStaffUsersTable();
      renderQuotaRulesSection();
    }

    document.addEventListener('DOMContentLoaded', () => {
      getDeptsDB();
      getUsersDB();
      try {
        const params = new URLSearchParams(window.location.search);
        const roleParam = (params.get('role') || '').toUpperCase();
        if (['STAFF', 'HEAD', 'ADMIN', 'REQUESTER'].includes(roleParam)) {
          if (AUTH_BYPASS && roleParam !== 'REQUESTER') {
            sessionStorage.setItem('staff_auth', 'true');
            sessionStorage.setItem('staff_username', 'admin_staff');
            sessionStorage.setItem('staff_name', 'ผู้ดูแลระบบคลังพัสดุ (โหมดทดสอบ)');
            sessionStorage.setItem('staff_role', 'ADMIN');
            sessionStorage.setItem('staff_active_role', roleParam);
          } else {
            sessionStorage.removeItem('staff_auth');
            sessionStorage.removeItem('staff_token');
            selectStaffLoginRole(roleParam);
          }
        }
      } catch (e) {}
      checkStaffAuth();
      syncFromMySQLAPI();
    });

__SEARCHABLE_SELECT_JS__

    // Real-time synchronization across tabs/windows
    window.addEventListener('storage', (e) => {
      if (e.key === DB_REQS_KEY || e.key === DB_ITEMS_KEY || e.key === DB_USERS_KEY || e.key === DB_DEPTS_KEY || e.key === DB_QUOTAS_KEY) {
        loadStaffDashboard();
      }
    });
  </script>
</body>
</html>
'''

staff_html = (
    staff_template
    .replace('__SYSTEM_VERSION__', SYSTEM_VERSION)
    .replace('__AUTH_BYPASS__', 'true' if AUTH_BYPASS else 'false')
    .replace('__SEARCHABLE_SELECT_CSS__', SEARCHABLE_SELECT_CSS)
    .replace('__SEARCHABLE_SELECT_JS__', SEARCHABLE_SELECT_JS)
    .replace('__DEFAULT_ITEMS__', json.dumps(initial_items, ensure_ascii=False))
    .replace('__DEFAULT_REQS__', json.dumps(initial_requisitions, ensure_ascii=False))
    .replace('__DEFAULT_DEPTS__', dept_json_str)
    .replace('__DEFAULT_USERS__', users_json_str)
)

with open(os.path.join(PROJECT_ROOT, 'staff.html'), 'w', encoding='utf-8') as f:
    f.write(staff_html)

print("Created staff.html (Inventory Staff & Admin Portal)")

# Also synchronize SYSTEM_VERSION in portal.html footer
portal_path = os.path.join(PROJECT_ROOT, 'portal.html')
if os.path.exists(portal_path):
    import re as _re
    with open(portal_path, 'r', encoding='utf-8') as f:
        portal_content = f.read()
    updated_portal = _re.sub(
        r'Stock Order SDU v[0-9]+\.[0-9]+\.[0-9]+',
        f'Stock Order SDU v{SYSTEM_VERSION}',
        portal_content
    )
    if updated_portal != portal_content:
        with open(portal_path, 'w', encoding='utf-8') as f:
            f.write(updated_portal)
        print(f"Updated portal.html footer version to v{SYSTEM_VERSION}")
