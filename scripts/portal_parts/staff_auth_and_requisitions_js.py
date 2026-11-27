"""
Staff Portal DB/API Sync, RBAC, SSO & Two-Tier Requisition Queue JS (scripts/portal_parts/staff_auth_and_requisitions_js.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

STAFF_AUTH_AND_REQUISITIONS_JS = r'''  <script>
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
      clock: `<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
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

    function getStaffAuthHeaders() {
      const token = sessionStorage.getItem('staff_token') || '';
      const activeRole = typeof getActiveStaffRole === 'function' ? getActiveStaffRole() : 'STAFF';
      const headers = { 'X-Staff-Role': activeRole };
      if (token) {
        headers['Authorization'] = 'Bearer ' + token;
        headers['X-Staff-Token'] = token;
      }
      return headers;
    }

    function isSafeSignatureDataUrl(sig) {
      return typeof sig === 'string' && /^data:image\/(png|jpeg|jpg|webp);base64,[A-Za-z0-9+/=\s]+$/i.test(sig.trim());
    }

    async function syncFromMySQLAPI() {
      if (!MYSQL_API_URL || !navigator.onLine) return;
      if (sessionStorage.getItem('staff_auth') !== 'true' && !AUTH_BYPASS) return;
      const authHeaders = getStaffAuthHeaders();
      try {
        const [itemsRes, reqsRes, usersRes, deptsRes, quotasRes] = await Promise.all([
          fetch(`${MYSQL_API_URL}?action=getItems`, { headers: authHeaders }).then(r => r.ok ? r.json() : null).catch(() => null),
          fetch(`${MYSQL_API_URL}?action=getRequisitions`, { headers: authHeaders }).then(r => r.ok ? r.json() : null).catch(() => null),
          fetch(`${MYSQL_API_URL}?action=getUsers`, { headers: authHeaders }).then(r => r.ok ? r.json() : null).catch(() => null),
          fetch(`${MYSQL_API_URL}?action=getDepartments`, { headers: authHeaders }).then(r => r.ok ? r.json() : null).catch(() => null),
          fetch(`${MYSQL_API_URL}?action=getQuotas`, { headers: authHeaders }).then(r => r.ok ? r.json() : null).catch(() => null)
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
      if (['head', 'head_approver', 'approver', 'director', 'jittraporn_cha'].includes(u)) return 'HEAD';
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

    // Auth & Auto-Role Detection
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
        if (!skipBypass) {
          if (activeRole === 'HEAD' && currentStaffStatus === 'PENDING') {
            const tabs = document.querySelectorAll('.status-tab');
            if (tabs[1]) filterStaffRequisitionStatus('VERIFIED', tabs[1]);
          } else if (activeRole === 'STAFF' && AUTH_BYPASS) {
            const tabs = document.querySelectorAll('.status-tab');
            if (tabs[0]) filterStaffRequisitionStatus('PENDING', tabs[0]);
          }
        }
      }
    }

    function switchToRequesterPortal() {
      const staffUsername = sessionStorage.getItem('staff_username') || '';
      const staffName = sessionStorage.getItem('staff_name') || staffUsername || 'บุคลากร สวท.';
      const staffRole = (sessionStorage.getItem('staff_role') || 'STAFF').toUpperCase();
      let reqProfile = null;
      try {
        const raw = sessionStorage.getItem('staff_requester_profile');
        if (raw) reqProfile = JSON.parse(raw);
      } catch (e) {}

      if (!reqProfile || !reqProfile.name) {
        const users = getUsersDB();
        const matched = users.find(u =>
          (u.username && u.username.toLowerCase() === staffUsername.toLowerCase()) ||
          (u.name && u.name.toLowerCase() === staffName.toLowerCase())
        );
        if (matched) {
          reqProfile = {
            id: matched.id,
            name: matched.name,
            username: matched.username || staffUsername,
            role: staffRole,
            position: matched.position || '',
            dept: matched.dept || 'สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน',
            phone: matched.phone || ''
          };
        } else {
          reqProfile = {
            id: 0,
            name: staffName,
            username: staffUsername,
            role: staffRole,
            position: staffRole === 'HEAD' ? 'หัวหน้าหน่วยงาน' : (staffRole === 'ADMIN' ? 'ผู้ดูแลระบบคลังพัสดุ' : 'เจ้าหน้าที่พัสดุ'),
            dept: 'สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน',
            phone: ''
          };
        }
      } else {
        reqProfile.role = staffRole;
      }

      const tokenToUse = sessionStorage.getItem('staff_requester_token') || sessionStorage.getItem('staff_token') || '';
      localStorage.setItem('sdu_requester_auth_v1', JSON.stringify(reqProfile));
      if (tokenToUse) {
        localStorage.setItem('sdu_requester_token_v1', tokenToUse);
      }
      window.location.href = 'index.html';
    }

    async function handleStaffLogin(e) {
      e.preventDefault();
      const usernameInput = document.getElementById('loginUsername');
      const passwordInput = document.getElementById('loginPassword');
      const username = usernameInput ? usernameInput.value.trim() : '';
      const password = passwordInput ? passwordInput.value.trim() : '';

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

      try {
        // Authenticate without requested_role so backend automatically detects the account's actual role
        const res = await fetch(MYSQL_API_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'loginStaff', username, password })
        });
        const data = await res.json();
        if (data && data.status === 'success') {
          const baseRole = (data.role || resolveRoleFromUsername(username)).toUpperCase();
          const activeRole = (data.active_role || baseRole).toUpperCase();
          sessionStorage.setItem('staff_auth', 'true');
          sessionStorage.setItem('staff_token', data.token || '');
          sessionStorage.setItem('staff_username', data.username || username);
          sessionStorage.setItem('staff_name', data.name || username);
          sessionStorage.setItem('staff_role', baseRole);
          sessionStorage.setItem('staff_active_role', activeRole);
          if (data.requester_token) sessionStorage.setItem('staff_requester_token', data.requester_token);
          if (data.requester_user) sessionStorage.setItem('staff_requester_profile', JSON.stringify(data.requester_user));
          checkStaffAuth();
          syncFromMySQLAPI();
          if (activeRole === 'HEAD') {
            const tabs = document.querySelectorAll('.status-tab');
            if (tabs[1]) filterStaffRequisitionStatus('VERIFIED', tabs[1]);
          } else if (activeRole === 'STAFF') {
            const tabs = document.querySelectorAll('.status-tab');
            if (tabs[0]) filterStaffRequisitionStatus('PENDING', tabs[0]);
          }
          return;
        }

        // If account is a REQUESTER role, automatically sign in via loginRequester and redirect to index.html
        if (data && data.code === 'ROLE_MISMATCH') {
          const reqRes = await fetch(MYSQL_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'loginRequester', username, password })
          });
          const reqData = await reqRes.json();
          if (reqData && reqData.status === 'success' && reqData.user) {
            localStorage.setItem('sdu_requester_auth_v1', JSON.stringify(reqData.user));
            if (reqData.token) {
              localStorage.setItem('sdu_requester_token_v1', reqData.token);
            }
            window.location.href = 'index.html';
            return;
          }
        }

        Swal.fire({
          icon: 'error',
          title: 'เข้าสู่ระบบไม่สำเร็จ',
          text: (data && data.message) || 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ลองใหม่อีกครั้ง'
        });
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
          resolvedName = 'เจ้าหน้าที่พัสดุ สวท.';
        } else if (['head', 'head_approver', 'approver', 'director', 'jittraporn_cha'].includes(uLow) && password === 'sdu1234') {
          resolvedRole = 'HEAD';
          resolvedName = 'หัวหน้าหน่วยงาน สวท.';
        } else {
          const foundUser = getUsersDB().find(u => (u.username && u.username.toLowerCase() === uLow) || (u.name && u.name.toLowerCase() === uLow));
          const validPass = foundUser ? (foundUser.password || 'sdu1234') : '';
          if (foundUser && (password === validPass || password === 'sdu1234')) {
            const uRole = String(foundUser.role || 'REQUESTER').toUpperCase();
            if (['ADMIN', 'HEAD', 'STAFF'].includes(uRole)) {
              resolvedRole = uRole;
              resolvedName = foundUser.name || username;
            } else {
              localStorage.setItem('sdu_requester_auth_v1', JSON.stringify(foundUser));
              window.location.href = 'index.html';
              return;
            }
          }
        }
        if (!resolvedRole) {
          Swal.fire({
            icon: 'error',
            title: 'เข้าสู่ระบบไม่สำเร็จ',
            text: 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง โหมดออฟไลน์',
            confirmButtonColor: '#1e40af',
            confirmButtonText: 'ลองใหม่อีกครั้ง'
          });
          return;
        }
        sessionStorage.setItem('staff_auth', 'true');
        sessionStorage.setItem('staff_username', username || 'admin_staff');
        sessionStorage.setItem('staff_name', resolvedName);
        sessionStorage.setItem('staff_role', resolvedRole);
        sessionStorage.setItem('staff_active_role', resolvedRole);
        checkStaffAuth();
        if (resolvedRole === 'HEAD') {
          const tabs = document.querySelectorAll('.status-tab');
          if (tabs[1]) filterStaffRequisitionStatus('VERIFIED', tabs[1]);
        } else if (resolvedRole === 'STAFF') {
          const tabs = document.querySelectorAll('.status-tab');
          if (tabs[0]) filterStaffRequisitionStatus('PENDING', tabs[0]);
        }
      }
    }

    function logoutStaff() {
      Swal.fire({
        title: 'ยืนยันออกจากระบบ?',
        text: 'คุณต้องการออกจากระบบจัดการวัสดุสำนักงานออนไลน์ใช่หรือไม่',
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
          sessionStorage.removeItem('staff_requester_token');
          sessionStorage.removeItem('staff_requester_profile');
          localStorage.removeItem('sdu_requester_auth_v1');
          localStorage.removeItem('requester_session');
          localStorage.removeItem('sdu_requester_token_v1');
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
          if (apiRes && apiRes.status === 'error') {
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
          if (apiRes && apiRes.status === 'error') {
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
      }).then(async (result) => {
        if (result.isConfirmed && result.value) {
          const items = getItemsDB();
          const req = reqs.find(r => r.id === docNo);
          if (req) {
            const now = new Date();
            const thaiNow = getThaiDatetime(now);
            const reasonText = result.value.trim();

            const apiRes = await postToMySQLAPI('rejectRequisition', { docNo: docNo, reason: reasonText, rejected_date: thaiNow });
            if (apiRes && apiRes.status === 'error') {
              Swal.fire({
                icon: 'error',
                title: 'ไม่สามารถปฏิเสธคำขอได้',
                text: apiRes.message || 'เกิดข้อผิดพลาดในการบันทึกฐานข้อมูล',
                confirmButtonColor: '#1e40af',
                confirmButtonText: 'ตกลง'
              });
              return;
            }

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
            req.status = 'REJECTED';
            req.reject_reason = reasonText;
            req.rejectReason = reasonText;
            req.rejected_at = now.toISOString();
            req.rejected_date = thaiNow;
            req.rejectedDate = thaiNow;
            req.updated_at = now.toISOString();
            saveReqsDB(reqs);
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
      }).then(async (res) => {
        if (!res.isConfirmed) return;

        const now = new Date();
        const thaiNow = getThaiDatetime(now);
        const staffUser = getLoggedInStaff();
        const recBy = staffUser ? (staffUser.name || staffUser.username) : 'เจ้าหน้าที่พัสดุ สวท.';

        const apiRes = await postToMySQLAPI('completeRequisition', {
          docNo: req.id,
          completed_date: thaiNow,
          recordedBy: recBy
        });
        if (apiRes && apiRes.status === 'error') {
          Swal.fire({
            icon: 'error',
            title: 'ไม่สามารถบันทึกจ่ายพัสดุได้',
            text: apiRes.message || 'เกิดข้อผิดพลาดในการตัดสต๊อกบนฐานข้อมูล',
            confirmButtonColor: '#1e40af',
            confirmButtonText: 'ตกลง'
          });
          return;
        }

        const items = getItemsDB();
        req.status = 'COMPLETED';
        req.completed_at = now.toISOString();
        req.completed_date = thaiNow;
        req.completedDate = thaiNow;
        req.updated_at = now.toISOString();

        // Deduct permanently from On-Hand and release Reserved
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

'''
