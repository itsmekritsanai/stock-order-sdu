"""
Requester Portal DB Sync, Searchable Selectors, Catalog, Quota & Cart JS (scripts/portal_parts/requester_catalog_and_cart_js.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

REQUESTER_CATALOG_AND_CART_JS = r'''  <script>
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

    const AUTH_TOKEN_KEY = 'sdu_requester_token_v1';

    function getRequesterAuthHeaders() {
      const token = localStorage.getItem(AUTH_TOKEN_KEY) || '';
      const headers = {};
      if (token) {
        headers['Authorization'] = 'Bearer ' + token;
        headers['X-Requester-Token'] = token;
      }
      return headers;
    }

    function isSafeSignatureDataUrl(sig) {
      return typeof sig === 'string' && /^data:image\/(png|jpeg|jpg|webp);base64,[A-Za-z0-9+/=\s]+$/i.test(sig.trim());
    }

    async function syncFromMySQLAPI() {
      if (!MYSQL_API_URL || !navigator.onLine) return;
      const isLoggedIn = Boolean(localStorage.getItem('sdu_requester_auth_v1')) || AUTH_BYPASS;
      const authHeaders = getRequesterAuthHeaders();
      try {
        const publicPromises = [
          fetch(`${MYSQL_API_URL}?action=getItems`).then(r => r.ok ? r.json() : null).catch(() => null),
          fetch(`${MYSQL_API_URL}?action=getDepartments`).then(r => r.ok ? r.json() : null).catch(() => null),
        ];
        const authPromises = isLoggedIn ? [
          fetch(`${MYSQL_API_URL}?action=getRequisitions`, { headers: authHeaders }).then(r => r.ok ? r.json() : null).catch(() => null),
          fetch(`${MYSQL_API_URL}?action=getUsers`, { headers: authHeaders }).then(r => r.ok ? r.json() : null).catch(() => null),
          fetch(`${MYSQL_API_URL}?action=getQuotas`, { headers: authHeaders }).then(r => r.ok ? r.json() : null).catch(() => null),
        ] : [Promise.resolve(null), Promise.resolve(null), Promise.resolve(null)];

        const [itemsRes, deptsRes, reqsRes, usersRes, quotasRes] = await Promise.all([...publicPromises, ...authPromises]);
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
          refreshAllMonthDropdowns();
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
        const token = localStorage.getItem(AUTH_TOKEN_KEY) || '';
        const headers = { 'Content-Type': 'application/json;charset=utf-8' };
        if (token) {
          headers['Authorization'] = 'Bearer ' + token;
          headers['X-Requester-Token'] = token;
        }
        const res = await fetch(MYSQL_API_URL, {
          method: 'POST',
          headers,
          body: JSON.stringify({ action, payload, requester_token: token })
        });
        if (res.status === 401 && action !== 'loginRequester' && action !== 'loginStaff') {
          localStorage.removeItem(AUTH_SESSION_KEY);
          localStorage.removeItem('requester_session');
          localStorage.removeItem(AUTH_TOKEN_KEY);
          if (typeof checkRequesterAuth === 'function') checkRequesterAuth();
          if (typeof Swal !== 'undefined') {
            Swal.fire({
              icon: 'warning',
              title: 'เซสชันหมดอายุ',
              text: 'กรุณาเข้าสู่ระบบผู้ขอเบิกพัสดุใหม่อีกครั้ง',
              confirmButtonColor: '#1e40af',
              confirmButtonText: 'ตกลง'
            });
          }
          return { status: 'error', code: 'UNAUTHORIZED', message: 'เซสชันหมดอายุ กรุณาเข้าสู่ระบบใหม่อีกครั้ง' };
        }
        return await res.json();
      } catch (err) {
        console.warn('API unreachable, saved to localStorage fallback:', err);
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
        dropdown.innerHTML = `<div class="combobox-no-results">ไม่พบรายชื่อในระบบ (สามารถพิมพ์ชื่อ "${escapeHtml(filterText)}" เพื่อขอเบิกได้ทันที)</div>`;
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
          const finalDocNo = (apiRes && apiRes.docNo) ? apiRes.docNo : newDocNo;
          newReq.id = finalDocNo;

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
                  ${finalDocNo}
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

'''
