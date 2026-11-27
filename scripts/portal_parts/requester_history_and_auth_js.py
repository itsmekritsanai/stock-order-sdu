"""
Requester Portal My Requisitions Modal, A4 PDF Printout & Auto-Role Login/SSO JS (scripts/portal_parts/requester_history_and_auth_js.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

REQUESTER_HISTORY_AND_AUTH_JS = r'''    function closeSuccessModal() {
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
      refreshAllMonthDropdowns();
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
      if (isSafeSignatureDataUrl(req.signature)) {
        sigBox.innerHTML = `<img src="${escapeHtml(req.signature.trim())}" class="sig-img-preview" alt="ลายเซ็นดิจิทัลผู้รับพัสดุ">`;
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
    const AUTH_SESSION_KEY = 'sdu_requester_auth_v1';

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
        const defaultTester = users.find(u => (u.username || '').toLowerCase() === 'somchai_jar') || users[0] || {
          id: 1,
          name: 'สมชัย จารุธนกิจพานิช',
          username: 'somchai_jar',
          position: 'กลุ่มงานเคาน์เตอร์บริการ',
          dept: 'กลุ่มงานเคาน์เตอร์บริการ',
          phone: '5174'
        };
        user = {
          id: defaultTester.id,
          name: defaultTester.name,
          username: defaultTester.username || 'somchai_jar',
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

      const staffSwitchBtn = document.getElementById('btnSwitchToStaffPortal');
      const staffSwitchText = document.getElementById('btnSwitchToStaffPortalText');
      if (staffSwitchBtn) {
        const uRole = String(user.role || sessionStorage.getItem('staff_role') || '').toUpperCase();
        if (['HEAD', 'STAFF', 'ADMIN'].includes(uRole)) {
          staffSwitchBtn.style.display = 'inline-flex';
          if (uRole === 'HEAD') {
            staffSwitchBtn.style.background = '#f5f3ff';
            staffSwitchBtn.style.color = '#5b21b6';
            staffSwitchBtn.style.borderColor = '#c4b5fd';
            if (staffSwitchText) staffSwitchText.innerText = 'หน้าอนุมัติคำขอ (หัวหน้า)';
          } else if (uRole === 'STAFF') {
            staffSwitchBtn.style.background = '#ecfdf5';
            staffSwitchBtn.style.color = '#047857';
            staffSwitchBtn.style.borderColor = '#a7f3d0';
            if (staffSwitchText) staffSwitchText.innerText = 'หน้าจัดการคลังพัสดุ';
          } else {
            staffSwitchBtn.style.background = '#f1f5f9';
            staffSwitchBtn.style.color = '#0f172a';
            staffSwitchBtn.style.borderColor = '#cbd5e1';
            if (staffSwitchText) staffSwitchText.innerText = 'หน้าผู้ดูแลระบบคลัง';
          }
        } else {
          staffSwitchBtn.style.display = 'none';
        }
      }

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

    function switchToStaffPortal() {
      const user = getLoggedInRequester();
      const role = String((user && user.role) || sessionStorage.getItem('staff_role') || '').toUpperCase();
      if (!['HEAD', 'STAFF', 'ADMIN'].includes(role)) {
        window.location.href = 'staff.html';
        return;
      }
      sessionStorage.setItem('staff_auth', 'true');
      sessionStorage.setItem('staff_username', (user && user.username) || sessionStorage.getItem('staff_username') || '');
      sessionStorage.setItem('staff_name', (user && user.name) || sessionStorage.getItem('staff_name') || '');
      sessionStorage.setItem('staff_role', role);
      sessionStorage.setItem('staff_active_role', role);
      window.location.href = 'staff.html';
    }

    const BUILTIN_STAFF_USERNAMES = ['admin_staff', 'admin', 'staff', 'warehouse_staff', 'screener', 'officer', 'head', 'head_approver', 'approver', 'director'];

    async function handleRequesterLogin(e) {
      if (e && e.preventDefault) e.preventDefault();
      const unameEl = document.getElementById('loginUsername');
      const passEl = document.getElementById('loginPassword');
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

      const uLow = username.toLowerCase();

      // Allow built-in staff/head/admin accounts to log into index.html for requisitions while enabling 1-click switch to staff.html
      if (BUILTIN_STAFF_USERNAMES.includes(uLow)) {
        let staffRes = await postToMySQLAPI('loginStaff', { username, password });
        if (staffRes === null) {
          let resolved = null;
          let dispName = username;
          if (['admin_staff', 'admin'].includes(uLow) && password === 'sdu1234') {
            resolved = 'ADMIN';
            dispName = 'ผู้ดูแลระบบคลังพัสดุ';
          } else if (['staff', 'warehouse_staff', 'screener', 'officer'].includes(uLow) && password === 'sdu1234') {
            resolved = 'STAFF';
            dispName = 'เจ้าหน้าที่พัสดุ สวท.';
          } else if (['head', 'head_approver', 'approver', 'director'].includes(uLow) && password === 'sdu1234') {
            resolved = 'HEAD';
            dispName = 'หัวหน้าหน่วยงาน สวท.';
          }
          staffRes = resolved
            ? {
                status: 'success',
                token: `${username}.${Math.floor(Date.now()/1000)}.offline`,
                requester_token: `${username}.${Math.floor(Date.now()/1000)}.offline`,
                requester_user: {
                  id: 0,
                  name: dispName,
                  username,
                  role: resolved,
                  position: resolved === 'HEAD' ? 'หัวหน้าหน่วยงาน' : (resolved === 'ADMIN' ? 'ผู้ดูแลระบบคลังพัสดุ' : 'เจ้าหน้าที่พัสดุ'),
                  dept: 'สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน',
                  phone: ''
                },
                username,
                name: dispName,
                role: resolved,
                active_role: resolved
              }
            : { status: 'error', message: 'ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง' };
        }
        if (staffRes && staffRes.status === 'success') {
          const finalRole = (staffRes.role || 'STAFF').toUpperCase();
          const activeRole = (staffRes.active_role || finalRole).toUpperCase();
          const reqUser = Object.assign({
            id: 0,
            name: staffRes.name || username,
            username: staffRes.username || username,
            role: finalRole,
            position: finalRole === 'HEAD' ? 'หัวหน้าหน่วยงาน' : (finalRole === 'ADMIN' ? 'ผู้ดูแลระบบคลังพัสดุ' : 'เจ้าหน้าที่พัสดุ'),
            dept: 'สำนักงานผู้อำนวยการสำนักส่งเสริมวิชาการและงานทะเบียน',
            phone: ''
          }, staffRes.requester_user || {}, { role: finalRole });
          const reqToken = staffRes.requester_token || staffRes.token || '';

          sessionStorage.setItem('staff_auth', 'true');
          sessionStorage.setItem('staff_token', staffRes.token || '');
          sessionStorage.setItem('staff_username', staffRes.username || username);
          sessionStorage.setItem('staff_name', staffRes.name || username);
          sessionStorage.setItem('staff_role', finalRole);
          sessionStorage.setItem('staff_active_role', activeRole);
          if (reqToken) sessionStorage.setItem('staff_requester_token', reqToken);
          sessionStorage.setItem('staff_requester_profile', JSON.stringify(reqUser));

          localStorage.setItem(AUTH_SESSION_KEY, JSON.stringify(reqUser));
          if (reqToken) {
            localStorage.setItem(AUTH_TOKEN_KEY, reqToken);
          } else {
            localStorage.removeItem(AUTH_TOKEN_KEY);
          }

          Swal.fire({
            icon: 'success',
            title: 'เข้าสู่ระบบสำเร็จ',
            text: 'ยินดีต้อนรับ ' + reqUser.name,
            timer: 1500,
            showConfirmButton: false
          });
          checkRequesterAuth();
          renderCatalog();
          syncFromMySQLAPI();
          return;
        }
        Swal.fire({
          icon: 'error',
          title: 'เข้าสู่ระบบไม่สำเร็จ',
          text: (staffRes && staffRes.message) || 'ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง',
          confirmButtonColor: '#1e40af',
          confirmButtonText: 'ลองใหม่อีกครั้ง'
        });
        return;
      }

      // 1. Try PostgreSQL/MySQL REST API for personnel / requester login
      let loginResult = await postToMySQLAPI('loginRequester', { username, password });

      // 2. Fallback to localStorage users DB ONLY when API server is unreachable (offline)
      if (loginResult === null) {
        const users = getUsersDB();
        const found = users.find(u =>
          (u.username && u.username.toLowerCase() === uLow) ||
          (u.name && u.name.toLowerCase() === uLow)
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
                role: (found.role || 'REQUESTER').toUpperCase(),
                position: found.position || '',
                dept: found.dept || '',
                phone: found.phone || ''
              }
            };
          }
        }
      }

      if (loginResult && loginResult.status === 'success') {
        const userObj = loginResult.user || {};
        localStorage.setItem(AUTH_SESSION_KEY, JSON.stringify(userObj));
        if (loginResult.token) {
          localStorage.setItem(AUTH_TOKEN_KEY, loginResult.token);
        } else {
          localStorage.removeItem(AUTH_TOKEN_KEY);
        }
        const resolvedStaffRole = String(loginResult.staff_role || userObj.role || '').toUpperCase();
        if (['HEAD', 'STAFF', 'ADMIN'].includes(resolvedStaffRole)) {
          if (loginResult.staff_token) sessionStorage.setItem('staff_token', loginResult.staff_token);
          sessionStorage.setItem('staff_role', resolvedStaffRole);
          sessionStorage.setItem('staff_active_role', resolvedStaffRole);
          sessionStorage.setItem('staff_username', userObj.username || username);
          sessionStorage.setItem('staff_name', userObj.name || username);
          sessionStorage.setItem('staff_requester_profile', JSON.stringify(userObj));
          if (loginResult.token) sessionStorage.setItem('staff_requester_token', loginResult.token);
        } else {
          sessionStorage.removeItem('staff_auth');
          sessionStorage.removeItem('staff_token');
          sessionStorage.removeItem('staff_role');
          sessionStorage.removeItem('staff_active_role');
        }
        Swal.fire({
          icon: 'success',
          title: 'เข้าสู่ระบบสำเร็จ',
          text: 'ยินดีต้อนรับ ' + userObj.name,
          timer: 1500,
          showConfirmButton: false
        });
        checkRequesterAuth();
        renderCatalog();
        syncFromMySQLAPI();
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
        text: 'ต้องการออกจากระบบจัดการวัสดุสำนักงานออนไลน์ใช่หรือไม่',
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'ออกจากระบบ',
        cancelButtonText: 'ยกเลิก'
      }).then((res) => {
        if (res.isConfirmed) {
          localStorage.removeItem(AUTH_SESSION_KEY);
          localStorage.removeItem('requester_session');
          localStorage.removeItem(AUTH_TOKEN_KEY);
          sessionStorage.removeItem('staff_auth');
          sessionStorage.removeItem('staff_token');
          sessionStorage.removeItem('staff_username');
          sessionStorage.removeItem('staff_name');
          sessionStorage.removeItem('staff_role');
          sessionStorage.removeItem('staff_active_role');
          sessionStorage.removeItem('staff_requester_token');
          sessionStorage.removeItem('staff_requester_profile');
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
      refreshAllMonthDropdowns();
      try {
        const params = new URLSearchParams(window.location.search);
        const roleParam = (params.get('role') || '').toUpperCase();
        if (['STAFF', 'HEAD', 'ADMIN'].includes(roleParam)) {
          window.location.href = `staff.html?role=${encodeURIComponent(roleParam)}`;
          return;
        }
      } catch (e) {}
      const isAuth = checkRequesterAuth();
      if (isAuth) {
        renderCatalog();
        updateMyReqsBadge();
        syncFromMySQLAPI();
      }
    });

__DYNAMIC_MONTH_JS__

__SEARCHABLE_SELECT_JS__

    // Real-time synchronization across tabs/windows
    window.addEventListener('storage', (e) => {
      if (e.key === DB_REQS_KEY || e.key === DB_ITEMS_KEY || e.key === DB_QUOTAS_KEY) {
        refreshAllMonthDropdowns();
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
