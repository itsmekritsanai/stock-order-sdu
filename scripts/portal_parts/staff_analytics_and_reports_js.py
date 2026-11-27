"""
Staff Portal Monthly Analytics, Purchase Costs, Per-Person Usage & Excel/PDF Export JS (scripts/portal_parts/staff_analytics_and_reports_js.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

STAFF_ANALYTICS_AND_REPORTS_JS = r'''    function handleAnalyticsMonthChange() {
      renderMonthlyAnalyticsView();
    }

    async function renderMonthlyAnalyticsView() {
      refreshAllMonthDropdowns();
      const monthSelect = document.getElementById('analyticsMonthSelect');
      const selectedMonth = (monthSelect && monthSelect.value) ? monthSelect.value : getCurrentMonthKey();
      let analyticsData = null;

      // Try fetching from server API if online
      if (MYSQL_API_URL && navigator.onLine) {
        try {
          const res = await fetch(`${MYSQL_API_URL}?action=getMonthlyAnalytics&month=${encodeURIComponent(selectedMonth)}`, {
            headers: getStaffAuthHeaders()
          });
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
          purchaseTransactions: offPurchaseTx,
          monthRequisitions: monthReqs.map(r => {
            const rItems = Array.isArray(r.items) ? r.items : [];
            return {
              ...r,
              items: rItems,
              totalPieces: rItems.reduce((sum, it) => sum + Number(it.totalPieces || 0), 0),
              approvedPieces: rItems.reduce((sum, it) => sum + Number(it.approvedPieces !== undefined ? it.approvedPieces : (it.totalPieces || 0)), 0)
            };
          })
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
      renderAnalyticsRequisitionsTable();
      renderAnalyticsPersonUsageTable();
      renderAnalyticsPurchaseSection();
    }

    function getAnalyticsStatusMeta(status) {
      const st = String(status || 'PENDING').toUpperCase();
      if (st === 'PENDING') return { label: 'รอคัดกรอง', bg: '#fffbeb', color: '#b45309', border: '#fde68a' };
      if (st === 'VERIFIED') return { label: 'รอหัวหน้าอนุมัติ', bg: '#f5f3ff', color: '#6d28d9', border: '#ddd6fe' };
      if (st === 'APPROVED') return { label: 'อนุมัติแล้ว รอรับของ', bg: '#eff6ff', color: '#1d4ed8', border: '#bfdbfe' };
      if (st === 'COMPLETED') return { label: 'จ่ายสำเร็จแล้ว', bg: '#ecfdf5', color: '#047857', border: '#a7f3d0' };
      if (st === 'REJECTED') return { label: 'ไม่อนุมัติ / ยกเลิก', bg: '#fef2f2', color: '#b91c1c', border: '#fecaca' };
      return { label: st, bg: '#f1f5f9', color: '#334155', border: '#cbd5e1' };
    }

    function getMonthlyRequisitionsList() {
      if (window.lastMonthlyAnalyticsData && Array.isArray(window.lastMonthlyAnalyticsData.monthRequisitions)) {
        return window.lastMonthlyAnalyticsData.monthRequisitions;
      }
      const monthSelect = document.getElementById('analyticsMonthSelect');
      const selectedMonth = monthSelect ? monthSelect.value : 'ALL';
      const reqs = getReqsDB();
      if (selectedMonth === 'ALL') return reqs;
      try {
        const parts = selectedMonth.split('-');
        const beYear = parseInt(parts[0], 10) + 543;
        const bePattern = `REQ-${beYear}${parts[1]}`;
        return reqs.filter(r => (r.id || '').startsWith(bePattern) || (r.created_at || '').startsWith(selectedMonth));
      } catch (e) {
        return reqs;
      }
    }

    function buildAnalyticsReqRowHtml(r, inModal = false) {
      const meta = getAnalyticsStatusMeta(r.status);
      const itemsArr = Array.isArray(r.items) ? r.items : [];
      const itemChips = itemsArr.slice(0, 2).map(it =>
        `<span style="display:inline-block; background:#eff6ff; color:#1e40af; border:1px solid #bfdbfe; padding:2px 8px; border-radius:999px; font-size:0.73rem; margin:2px 4px 2px 0;">${escapeHtml(it.name || '-')} (${Number(it.totalPieces || 0).toLocaleString()} ${escapeHtml(it.unitPiece || 'ชิ้น')})</span>`
      ).join('');
      const extraCnt = itemsArr.length > 2 ? `<span style="font-size:0.73rem; color:#64748b;"> +อีก ${itemsArr.length - 2} รายการ</span>` : '';
      const totalPcs = Number(r.totalPieces !== undefined ? r.totalPieces : itemsArr.reduce((s, x) => s + Number(x.totalPieces || 0), 0));
      const safeIdJs = String(r.id || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'");
      const pdfClick = inModal
        ? `Swal.close(); previewDocInPdf('${safeIdJs}');`
        : `previewDocInPdf('${safeIdJs}');`;

      return `
        <tr>
          <td style="white-space: nowrap;">
            <strong style="color: #1e3a8a;">${escapeHtml(r.id || '-')}</strong>
            <div style="font-size: 0.74rem; color: var(--neutral-500); margin-top: 2px;">${escapeHtml(r.date || r.created_at || '-')}</div>
          </td>
          <td>
            <div style="font-weight: 600; color: var(--neutral-900);">${escapeHtml(r.requester || '-')}</div>
            <div style="font-size: 0.74rem; color: var(--neutral-500); margin-top: 2px;">${escapeHtml(r.dept || '-')}</div>
          </td>
          <td>
            <div>${itemChips || '-'}${extraCnt}</div>
            <div style="font-size: 0.73rem; color: var(--neutral-500); margin-top: 3px;">รวม ${itemsArr.length.toLocaleString()} รายการ (${totalPcs.toLocaleString()} ชิ้น)</div>
          </td>
          <td style="font-size: 0.8rem; color: var(--neutral-700); max-width: 210px;">
            ${escapeHtml(r.purpose || '-')}
          </td>
          <td style="text-align: center; white-space: nowrap;">
            <span style="display: inline-block; background: ${meta.bg}; color: ${meta.color}; border: 1px solid ${meta.border}; padding: 3px 10px; border-radius: 999px; font-size: 0.74rem; font-weight: 600;">
              ${escapeHtml(meta.label)}
            </span>
          </td>
          <td style="text-align: right; white-space: nowrap;">
            <button type="button" class="btn btn-outline" style="padding: 4px 9px; font-size: 0.74rem; margin-right: 4px;" onclick="openMonthlyRequisitionDetailModal('${safeIdJs}')">
              ${vIcons.eye} รายละเอียด
            </button>
            <button type="button" class="btn btn-outline" style="padding: 4px 9px; font-size: 0.74rem;" onclick="${pdfClick}">
              ${vIcons.printer} PDF
            </button>
          </td>
        </tr>
      `;
    }

    function renderAnalyticsRequisitionsTable() {
      const tbody = document.getElementById('analyticsReqsTbody');
      const countEl = document.getElementById('analyticsReqsListCount');
      const searchEl = document.getElementById('analyticsReqSearchInput');
      const statusEl = document.getElementById('analyticsReqStatusFilter');
      if (!tbody) return;

      const list = getMonthlyRequisitionsList();
      const q = (searchEl ? searchEl.value : '').trim().toLowerCase();
      const selectedStatus = statusEl ? statusEl.value : 'ALL';

      const filtered = list.filter(r => {
        const matchStatus = selectedStatus === 'ALL' || String(r.status || '').toUpperCase() === selectedStatus;
        const matchQuery = !q ||
          (r.id && r.id.toLowerCase().includes(q)) ||
          (r.requester && r.requester.toLowerCase().includes(q)) ||
          (r.dept && r.dept.toLowerCase().includes(q)) ||
          (r.purpose && r.purpose.toLowerCase().includes(q)) ||
          (r.items || []).some(it => it.name && it.name.toLowerCase().includes(q));
        return matchStatus && matchQuery;
      });

      if (countEl) {
        countEl.innerText = `(แสดง ${filtered.length.toLocaleString()} จาก ${list.length.toLocaleString()} คำขอ)`;
      }

      if (filtered.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="6" style="text-align: center; padding: 2rem; color: var(--neutral-400);">
              ไม่พบรายการคำขอเบิกพัสดุในงวดเดือนหรือเงื่อนไขที่เลือก
            </td>
          </tr>
        `;
        return;
      }

      tbody.innerHTML = filtered.map(r => buildAnalyticsReqRowHtml(r, false)).join('');
    }

    function openMonthlyRequisitionsModal(initialStatus = 'ALL') {
      const list = getMonthlyRequisitionsList();
      const monthSelect = document.getElementById('analyticsMonthSelect');
      const monthLabel = monthSelect && monthSelect.selectedIndex >= 0
        ? monthSelect.options[monthSelect.selectedIndex].text
        : ((window.lastMonthlyAnalyticsData && window.lastMonthlyAnalyticsData.thaiMonth) || 'ทั้งหมด');

      const counts = { ALL: list.length, PENDING: 0, VERIFIED: 0, APPROVED: 0, COMPLETED: 0, REJECTED: 0 };
      list.forEach(r => {
        const st = String(r.status || '').toUpperCase();
        if (counts[st] !== undefined) counts[st] += 1;
      });

      const filterButtons = [
        { key: 'ALL', label: `ทั้งหมด (${counts.ALL})` },
        { key: 'PENDING', label: `รอคัดกรอง (${counts.PENDING})` },
        { key: 'VERIFIED', label: `รอหัวหน้าอนุมัติ (${counts.VERIFIED})` },
        { key: 'APPROVED', label: `รอรับของ (${counts.APPROVED})` },
        { key: 'COMPLETED', label: `จ่ายสำเร็จ (${counts.COMPLETED})` },
        { key: 'REJECTED', label: `ไม่อนุมัติ (${counts.REJECTED})` }
      ];

      Swal.fire({
        title: `รายการคำขอเบิกทั้งหมดในเดือน (${escapeHtml(monthLabel)})`,
        width: '1020px',
        html: `
          <div style="text-align: left; font-size: 0.875rem; margin-top: 0.5rem;">
            <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 0.75rem;" id="modalMonthlyReqStatusBar">
              ${filterButtons.map(b => `
                <button type="button" data-status="${b.key}" class="btn ${b.key === initialStatus ? 'btn-primary' : 'btn-outline'}"
                        style="padding: 5px 11px; font-size: 0.76rem; border-radius: 999px;">
                  ${b.label}
                </button>
              `).join('')}
            </div>
            <div style="margin-bottom: 0.75rem;">
              <input type="text" id="modalMonthlyReqSearch" class="form-control"
                     placeholder="พิมพ์ค้นหาเลขที่คำขอ, ผู้ขอเบิก, หน่วยงาน, วัตถุประสงค์ หรือชื่อพัสดุ...">
            </div>
            <div style="max-height: 440px; overflow: auto; border: 1px solid #e2e8f0; border-radius: 10px;">
              <table class="req-table" style="font-size: 0.84rem; margin: 0;">
                <thead style="position: sticky; top: 0; background: #f8fafc; z-index: 2;">
                  <tr>
                    <th style="min-width: 140px;">เลขที่คำขอ / วันที่</th>
                    <th style="min-width: 175px;">ผู้ขอเบิก / หน่วยงาน</th>
                    <th style="min-width: 210px;">รายการพัสดุ</th>
                    <th style="min-width: 140px;">วัตถุประสงค์</th>
                    <th style="width: 130px; text-align: center;">สถานะ</th>
                    <th style="width: 165px; text-align: right;">การดำเนินการ</th>
                  </tr>
                </thead>
                <tbody id="modalMonthlyReqTbody"></tbody>
              </table>
            </div>
          </div>
        `,
        confirmButtonColor: '#1e40af',
        confirmButtonText: 'ปิดหน้าต่าง',
        didOpen: () => {
          let activeSt = initialStatus;
          const tbodyEl = document.getElementById('modalMonthlyReqTbody');
          const searchInput = document.getElementById('modalMonthlyReqSearch');
          const barEl = document.getElementById('modalMonthlyReqStatusBar');

          const renderModalRows = () => {
            if (!tbodyEl) return;
            const q = (searchInput ? searchInput.value : '').trim().toLowerCase();
            const rows = list.filter(r => {
              const okSt = activeSt === 'ALL' || String(r.status || '').toUpperCase() === activeSt;
              const okQ = !q ||
                (r.id && r.id.toLowerCase().includes(q)) ||
                (r.requester && r.requester.toLowerCase().includes(q)) ||
                (r.dept && r.dept.toLowerCase().includes(q)) ||
                (r.purpose && r.purpose.toLowerCase().includes(q)) ||
                (r.items || []).some(it => it.name && it.name.toLowerCase().includes(q));
              return okSt && okQ;
            });
            if (rows.length === 0) {
              tbodyEl.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:2rem; color:#94a3b8;">ไม่พบรายการคำขอเบิกพัสดุที่ตรงเงื่อนไข</td></tr>`;
            } else {
              tbodyEl.innerHTML = rows.map(r => buildAnalyticsReqRowHtml(r, true)).join('');
            }
          };

          if (barEl) {
            barEl.querySelectorAll('button[data-status]').forEach(btn => {
              btn.addEventListener('click', () => {
                activeSt = btn.getAttribute('data-status') || 'ALL';
                barEl.querySelectorAll('button[data-status]').forEach(b => {
                  b.classList.toggle('btn-primary', b === btn);
                  b.classList.toggle('btn-outline', b !== btn);
                });
                renderModalRows();
              });
            });
          }
          if (searchInput) searchInput.addEventListener('input', renderModalRows);
          renderModalRows();
        }
      });
    }

    function openMonthlyRequisitionDetailModal(docNo) {
      const list = getMonthlyRequisitionsList();
      let req = list.find(r => r.id === docNo);
      if (!req) req = getReqsDB().find(r => r.id === docNo);
      if (!req) return;

      const meta = getAnalyticsStatusMeta(req.status);
      const itemsArr = Array.isArray(req.items) ? req.items : [];
      const rowsHtml = itemsArr.map((it, idx) => {
        const reqDesc = `${Number(it.qtyBoxes || 0) > 0 ? `${Number(it.qtyBoxes).toLocaleString()} ${escapeHtml(it.unitBox || 'กล่อง')} ` : ''}${Number(it.qtyPieces || 0) > 0 ? `${Number(it.qtyPieces).toLocaleString()} ${escapeHtml(it.unitPiece || 'ชิ้น')}` : ''}`.trim() || `${Number(it.totalPieces || 0).toLocaleString()} ${escapeHtml(it.unitPiece || 'ชิ้น')}`;
        const appQty = (req.status === 'APPROVED' || req.status === 'COMPLETED')
          ? `${Number(it.approvedPieces !== undefined ? it.approvedPieces : it.totalPieces || 0).toLocaleString()} ${escapeHtml(it.unitPiece || 'ชิ้น')}`
          : '-';
        return `
          <tr style="border-bottom: 1px solid #e2e8f0;">
            <td style="padding: 8px; text-align: center; color: #64748b;">${idx + 1}</td>
            <td style="padding: 8px; text-align: left; font-weight: 600; color: #0f172a;">${escapeHtml(it.name || '-')}</td>
            <td style="padding: 8px; text-align: right; color: #1e40af; font-weight: 600;">${reqDesc} <span style="font-size:0.75rem; color:#64748b;">(${Number(it.totalPieces || 0).toLocaleString()} ${escapeHtml(it.unitPiece || 'ชิ้น')})</span></td>
            <td style="padding: 8px; text-align: right; color: #059669; font-weight: 700;">${appQty}</td>
          </tr>
        `;
      }).join('');

      const safeIdJs = String(req.id || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'");
      const trailParts = [];
      if (req.verified_by) trailParts.push(`<div><strong>ผู้คัดกรอง:</strong> ${escapeHtml(req.verified_by)}${req.verified_date ? ` (${escapeHtml(req.verified_date)})` : ''}</div>`);
      if (req.approved_by) trailParts.push(`<div><strong>ผู้อนุมัติ:</strong> ${escapeHtml(req.approved_by)}${req.approved_date ? ` (${escapeHtml(req.approved_date)})` : ''}</div>`);
      if (req.completed_date) trailParts.push(`<div><strong>วันที่จ่ายพัสดุ:</strong> ${escapeHtml(req.completed_date)}</div>`);
      if (req.reject_reason) trailParts.push(`<div style="color:#b91c1c;"><strong>เหตุผลไม่อนุมัติ/ยกเลิก:</strong> ${escapeHtml(req.reject_reason)}</div>`);

      Swal.fire({
        title: `รายละเอียดคำขอเบิก ${escapeHtml(req.id)}`,
        width: '760px',
        html: `
          <div style="text-align: left; font-size: 0.88rem; margin-top: 0.5rem;">
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 14px; margin-bottom: 1rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 6px 14px;">
              <div><strong>ผู้ขอเบิก:</strong> ${escapeHtml(req.requester || '-')}</div>
              <div><strong>สถานะ:</strong> <span style="background:${meta.bg}; color:${meta.color}; border:1px solid ${meta.border}; padding:2px 9px; border-radius:999px; font-size:0.76rem; font-weight:600;">${escapeHtml(meta.label)}</span></div>
              <div><strong>หน่วยงาน:</strong> ${escapeHtml(req.dept || '-')}</div>
              <div><strong>วันที่ส่งคำขอ:</strong> ${escapeHtml(req.date || req.created_at || '-')}</div>
              ${req.phone ? `<div><strong>เบอร์ติดต่อ:</strong> ${escapeHtml(req.phone)}</div>` : ''}
              <div style="grid-column: 1 / -1;"><strong>วัตถุประสงค์:</strong> ${escapeHtml(req.purpose || '-')}</div>
              ${trailParts.length > 0 ? `<div style="grid-column: 1 / -1; border-top: 1px dashed #cbd5e1; padding-top: 6px; margin-top: 2px; display: flex; flex-direction: column; gap: 3px;">${trailParts.join('')}</div>` : ''}
            </div>
            <div style="max-height: 300px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 10px;">
              <table style="width: 100%; border-collapse: collapse; font-size: 0.86rem;">
                <thead>
                  <tr style="background: #f1f5f9; border-bottom: 2px solid #cbd5e1;">
                    <th style="padding: 8px; width: 45px; text-align: center;">#</th>
                    <th style="padding: 8px; text-align: left;">รายการพัสดุ</th>
                    <th style="padding: 8px; width: 195px; text-align: right;">จำนวนที่ขอเบิก</th>
                    <th style="padding: 8px; width: 130px; text-align: right;">อนุมัติ / จ่ายจริง</th>
                  </tr>
                </thead>
                <tbody>${rowsHtml || '<tr><td colspan="4" style="text-align:center; padding:1.5rem; color:#94a3b8;">ไม่มีรายการพัสดุ</td></tr>'}</tbody>
              </table>
            </div>
          </div>
        `,
        showDenyButton: true,
        denyButtonColor: '#059669',
        denyButtonText: 'เปิดใบเบิก PDF',
        confirmButtonColor: '#1e40af',
        confirmButtonText: 'ปิดหน้าต่าง'
      }).then((res) => {
        if (res.isDenied) {
          previewDocInPdf(safeIdJs);
        }
      });
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
          const res = await fetch(`${MYSQL_API_URL}?action=exportMonthlyAnalyticsExcel&month=${encodeURIComponent(selectedMonth)}`, {
            headers: getStaffAuthHeaders()
          });
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
              <div>( จิตราพร จันทรกูล )</div>
              <div style="font-size:11.5px; color:#555;">รองผู้อำนวยการ สวท. / ผู้รับรองรายงาน</div>
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

'''
