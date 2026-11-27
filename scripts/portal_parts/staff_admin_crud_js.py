"""
Staff Portal Item CRUD, User CRUD, Department CRUD & Quota Rules CRUD JS (scripts/portal_parts/staff_admin_crud_js.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

STAFF_ADMIN_CRUD_JS = r'''    function readFileAsDataURL(fileInput) {
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

      const apiRes = await postToMySQLAPI('saveItem', { id: itm.id, min_alert: newMin });
      if (apiRes && apiRes.status === 'error') {
        Swal.fire({
          icon: 'error',
          title: 'บันทึกเกณฑ์เตือนไม่สำเร็จ',
          text: apiRes.message || 'เกิดข้อผิดพลาดในการบันทึกข้อมูลลงฐานข้อมูล',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ตกลง'
        });
        return;
      }
      itm.min_alert = newMin;
      saveItemsDB(items);
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
      }).then(async (result) => {
        if (!result.isConfirmed || !result.value) return;
        const val = result.value;
        const currentItems = getItemsDB();
        const staffUser = getLoggedInStaff();
        const recBy = staffUser ? (staffUser.name || staffUser.username) : 'เจ้าหน้าที่พัสดุ สวท.';

        // Send id: null when creating a new item so PostgreSQL SERIAL RETURNING id generates the real ID
        const apiPayload = existing
          ? { id: existing.id, ...val, recordedBy: recBy }
          : { id: null, ...val, recordedBy: recBy };

        const apiRes = await postToMySQLAPI('saveItem', apiPayload);
        if (apiRes && apiRes.status === 'error') {
          Swal.fire({
            icon: 'error',
            title: 'บันทึกรายการพัสดุไม่สำเร็จ',
            text: apiRes.message || 'เกิดข้อผิดพลาดในการบันทึกข้อมูลลงฐานข้อมูล',
            confirmButtonColor: '#1e40af',
            confirmButtonText: 'ตกลง'
          });
          return;
        }

        let savedItem = null;
        if (existing) {
          const idx = currentItems.findIndex(i => Number(i.id) === Number(existing.id));
          if (idx !== -1) {
            currentItems[idx] = { ...currentItems[idx], ...val };
            savedItem = currentItems[idx];
          }
        } else {
          const maxId = currentItems.reduce((m, i) => Math.max(m, Number(i.id) || 0), 0);
          const newId = (apiRes && apiRes.id) ? Number(apiRes.id) : (maxId + 1);
          savedItem = {
            id: newId,
            ...val,
            reserved_pieces: 0
          };
          currentItems.push(savedItem);
        }

        saveItemsDB(currentItems);
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

    async function ensureDeptExists(deptName, syncToApi = true) {
      const clean = (deptName || '').trim();
      if (!clean) return;
      const deptsData = getDeptsDB();
      if (deptsData.length === 0) {
        deptsData.push({ category: 'สำนักส่งเสริมวิชาการและงานทะเบียน (สวท.)', items: [] });
      }
      const exists = deptsData.some(c => (c.items || []).some(it => it.value === clean));
      if (!exists) {
        if (syncToApi) {
          await postToMySQLAPI('addDepartment', { category: deptsData[0].category, name: clean });
        }
        deptsData[0].items.push({ label: clean, value: clean, sub: false });
        saveDeptsDB(deptsData);
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
        const uRole = String(u.role || ((u.username || '').toLowerCase() === 'jittraporn_cha' ? 'HEAD' : ((u.username || '').toLowerCase() === 'chuthathip_pan' ? 'STAFF' : 'REQUESTER'))).toUpperCase();
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
      const curRole = existing ? String(existing.role || ((existing.username || '').toLowerCase() === 'jittraporn_cha' ? 'HEAD' : ((existing.username || '').toLowerCase() === 'chuthathip_pan' ? 'STAFF' : 'REQUESTER'))).toUpperCase() : 'REQUESTER';

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

        const currentUsers = getUsersDB();
        const apiPayload = existing
          ? {
              id: existing.id,
              name: val.name,
              username: val.username,
              role: val.role,
              ...(val.password ? { password: val.password } : {}),
              position: val.position,
              dept: val.dept,
              phone: val.phone
            }
          : {
              // Send id: null on creation so PostgreSQL SERIAL RETURNING id generates the authoritative ID
              id: null,
              name: val.name,
              username: val.username,
              role: val.role,
              password: val.password || 'sdu1234',
              position: val.position,
              dept: val.dept,
              phone: val.phone
            };

        const apiRes = await postToMySQLAPI('saveUser', apiPayload);
        if (apiRes && apiRes.status === 'error') {
          Swal.fire({
            icon: 'error',
            title: 'บันทึกข้อมูลบุคลากรไม่สำเร็จ',
            text: apiRes.message || 'ไม่สามารถบันทึกการเปลี่ยนแปลงสิทธิ์หรือข้อมูลบุคลากรได้'
          });
          return;
        }

        await ensureDeptExists(val.dept, false);

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
            if (apiRes && apiRes.data) {
              Object.assign(updatedUser, apiRes.data, { role: apiRes.data.role || val.role });
            }
            currentUsers[idx] = updatedUser;
            savedUser = currentUsers[idx];
          }
        } else {
          const maxId = currentUsers.reduce((m, u) => Math.max(m, Number(u.id) || 0), 0);
          const realId = (apiRes && apiRes.data && apiRes.data.id)
            ? Number(apiRes.data.id)
            : ((apiRes && apiRes.id) ? Number(apiRes.id) : (maxId + 1));
          savedUser = {
            id: realId,
            name: val.name,
            username: val.username,
            role: (apiRes && apiRes.data && apiRes.data.role) ? apiRes.data.role : val.role,
            password: val.password || 'sdu1234',
            position: val.position,
            dept: val.dept,
            phone: val.phone
          };
          currentUsers.push(savedUser);
        }

        saveUsersDB(currentUsers);
        renderStaffUsersTable();

        Swal.fire({
          icon: 'success',
          title: existing ? 'อัปเดตข้อมูลบุคลากรสำเร็จ' : 'เพิ่มรายชื่อบุคลากรสำเร็จ',
          text: `${val.name} (${val.dept}) พร้อมให้ใช้ชื่อ ${val.username} เข้าสู่ระบบจัดการวัสดุสำนักงานออนไลน์ทันที`,
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
      refreshAllMonthDropdowns();
      renderStaffRequisitions(currentStaffStatus);
      renderInventoryTable();
      renderStaffUsersTable();
      renderQuotaRulesSection();
    }

    document.addEventListener('DOMContentLoaded', () => {
      getDeptsDB();
      getUsersDB();
      refreshAllMonthDropdowns();
      try {
        const params = new URLSearchParams(window.location.search);
        const roleParam = (params.get('role') || '').toUpperCase();
        if (roleParam === 'REQUESTER') {
          window.location.href = 'index.html';
          return;
        }
        if (['STAFF', 'HEAD', 'ADMIN'].includes(roleParam)) {
          if (AUTH_BYPASS) {
            sessionStorage.setItem('staff_auth', 'true');
            sessionStorage.setItem('staff_username', 'admin_staff');
            sessionStorage.setItem('staff_name', 'ผู้ดูแลระบบคลังพัสดุ (โหมดทดสอบ)');
            sessionStorage.setItem('staff_role', 'ADMIN');
            sessionStorage.setItem('staff_active_role', roleParam);
          } else if (sessionStorage.getItem('staff_auth') === 'true' && (sessionStorage.getItem('staff_role') || '').toUpperCase() === 'ADMIN') {
            sessionStorage.setItem('staff_active_role', roleParam);
          }
        }
      } catch (e) {}
      checkStaffAuth();
      if (sessionStorage.getItem('staff_auth') === 'true' || AUTH_BYPASS) {
        syncFromMySQLAPI();
      }
    });

__DYNAMIC_MONTH_JS__

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
