"""
Staff Portal Restock Pricing, Stock Adjust, PDF Preview & Inventory History JS (scripts/portal_parts/staff_stock_and_inventory_js.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

STAFF_STOCK_AND_INVENTORY_JS = r'''    function openStockInModal(preselectedItemId = null) {
      const items = getItemsDB();
      const defaultItem = (preselectedItemId !== null ? items.find(i => Number(i.id) === Number(preselectedItemId)) : null) || items[0];
      const initId = defaultItem ? Number(defaultItem.id) : '';
      const stockItemOptions = items.length > 0
        ? items.map(i => {
            const ratioTxt = i.is_multi_unit ? `1 ${i.unit_box_name} = ${i.pieces_per_box} ${i.unit_piece_name}` : `1 ${i.unit_piece_name}`;
            return `<option value="${i.id}" ${Number(i.id) === initId ? 'selected' : ''}>${escapeHtml(i.name)} (${escapeHtml(i.category || 'พัสดุทั่วไป')} • ${escapeHtml(ratioTxt)} • คงเหลือ ${Number(i.on_hand_pieces).toLocaleString()} ${escapeHtml(i.unit_piece_name || 'ชิ้น')})</option>`;
          }).join('')
        : '<option value="">-- ไม่มีรายการพัสดุ --</option>';

      Swal.fire({
        title: 'บันทึกรับเข้าพัสดุใหม่',
        html: `
          <div style="text-align: left; display: flex; flex-direction: column; gap: 0.85rem; margin-top: 0.5rem;">
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">
                เลือกรายการพัสดุ: *
              </label>
              <select id="swalStockItem" class="swal2-input" style="margin: 0; width: 100%; height: 42px; font-size: 0.925rem;">
                ${stockItemOptions}
              </select>

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
          const itemSelectEl = document.getElementById('swalStockItem');
          const badgeEl = document.getElementById('swalStockItemBadge');
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
            const id = parseInt(itemSelectEl?.value, 10);
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

          function selectItem(id) {
            const itm = items.find(i => Number(i.id) === Number(id));
            if (!itm) return;
            if (itemSelectEl && Number(itemSelectEl.value) !== Number(itm.id)) {
              itemSelectEl.value = String(itm.id);
            }

            const safeBoxUnit = escapeHtml(itm.unit_box_name || 'กล่อง');
            const safePieceUnit = escapeHtml(itm.unit_piece_name || 'ชิ้น');
            const ratioTxt = itm.is_multi_unit ? `1 ${safeBoxUnit} = ${itm.pieces_per_box} ${safePieceUnit}` : `1 ${safePieceUnit}`;
            if (badgeEl) {
              badgeEl.innerHTML = `
                <span>คงเหลือปัจจุบัน: <strong style="color: #1e40af;">${Number(itm.on_hand_pieces).toLocaleString()}</strong> ${safePieceUnit}</span>
                <span style="font-size: 0.75rem; color: #64748b;">อัตราส่วน: ${ratioTxt}</span>
              `;
            }
            if (boxLabelEl) {
              boxLabelEl.innerHTML = `จำนวนหน่วยใหญ่ (<strong>${safeBoxUnit}</strong>):`;
            }
            if (pieceLabelEl) {
              pieceLabelEl.innerHTML = `จำนวนหน่วยย่อย (<strong>${safePieceUnit}</strong>):`;
            }
            if (priceHintEl) {
              const lastP = Number(itm.last_unit_price || 0);
              priceHintEl.innerText = lastP > 0
                ? `ราคาล่าสุดในระบบ: ${lastP.toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} บาท/${itm.unit_piece_name || 'ชิ้น'} (ใส่ 0 หากไม่ระบุราคา)`
                : 'ใส่ 0 หากยังไม่ทราบราคาหรือไม่คิดค่าใช้จ่าย';
            }
            updateCostPreview();
          }

          if (boxesEl) boxesEl.addEventListener('input', updateCostPreview);
          if (piecesEl) piecesEl.addEventListener('input', updateCostPreview);
          if (priceModeEl) priceModeEl.addEventListener('change', updateCostPreview);
          if (priceInputEl) priceInputEl.addEventListener('input', updateCostPreview);
          if (itemSelectEl) itemSelectEl.addEventListener('change', () => selectItem(itemSelectEl.value));
          enhanceAllSearchableSelects(Swal.getPopup() || document);

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
      }).then(async (res) => {
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
            const staffUser = getLoggedInStaff();
            const recBy = staffUser ? (staffUser.name || staffUser.username) : 'เจ้าหน้าที่พัสดุ สวท.';

            const apiRes = await postToMySQLAPI('restockItem', {
              itemId: itm.id,
              quantityPieces: totalAdded,
              unitPrice: unitPrice,
              totalCost: totalCost,
              note: note,
              recordedBy: recBy
            });
            if (apiRes && apiRes.status === 'error') {
              Swal.fire({
                icon: 'error',
                title: 'รับพัสดุเข้าคลังไม่สำเร็จ',
                text: apiRes.message || 'เกิดข้อผิดพลาดในการบันทึกข้อมูลลงฐานข้อมูล',
                confirmButtonColor: '#1e40af',
                confirmButtonText: 'ตกลง'
              });
              return;
            }

            itm.on_hand_pieces = (apiRes && typeof apiRes.on_hand_pieces === 'number') ? apiRes.on_hand_pieces : (itm.on_hand_pieces + totalAdded);
            itm.last_restocked_at = (apiRes && apiRes.last_restocked_at) ? apiRes.last_restocked_at : nowStr;
            if (unitPrice > 0) {
              itm.last_unit_price = unitPrice;
            }
            saveItemsDB(items);
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
      const defaultItem = (preselectedItemId !== null ? items.find(i => Number(i.id) === Number(preselectedItemId)) : null) || items[0];
      const initItemId = defaultItem ? Number(defaultItem.id) : '';
      const adjItemOptions = items.length > 0
        ? items.map(i =>
            `<option value="${i.id}" ${Number(i.id) === initItemId ? 'selected' : ''}>${escapeHtml(i.name)} (${escapeHtml(i.category || 'พัสดุทั่วไป')} • คงเหลือ ${Number(i.on_hand_pieces).toLocaleString()} ${escapeHtml(i.unit_piece_name || 'ชิ้น')})</option>`
          ).join('')
        : '<option value="">-- ไม่มีรายการพัสดุ --</option>';

      Swal.fire({
        title: 'ปรับยอดสต๊อกจริง',
        html: `
          <div style="text-align: left; display: flex; flex-direction: column; gap: 0.85rem; margin-top: 0.5rem;">
            <div>
              <label style="font-size: 0.85rem; font-weight: 600; color: #334155; display: block; margin-bottom: 4px;">
                เลือกรายการพัสดุ: *
              </label>
              <select id="swalAdjItem" class="swal2-input" style="margin: 0; width: 100%; height: 42px; font-size: 0.925rem;">
                ${adjItemOptions}
              </select>

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
          const itemSelectEl = document.getElementById('swalAdjItem');
          const badgeEl = document.getElementById('swalAdjItemBadge');
          const unitLabelEl = document.getElementById('swalAdjUnitLabel');

          function selectItem(id) {
            const itm = items.find(i => Number(i.id) === Number(id));
            if (!itm) return;
            if (itemSelectEl && Number(itemSelectEl.value) !== Number(itm.id)) {
              itemSelectEl.value = String(itm.id);
            }
            if (badgeEl) {
              badgeEl.innerHTML = `
                <span>ยอดคงคลังปัจจุบัน: <strong style="color: #1e40af;">${Number(itm.on_hand_pieces).toLocaleString()}</strong> ${escapeHtml(itm.unit_piece_name)}</span>
                <span style="font-size: 0.75rem; color: #64748b;">หมวด: ${escapeHtml(itm.category || 'ทั่วไป')}</span>
              `;
            }
            if (unitLabelEl) {
              unitLabelEl.innerText = itm.unit_piece_name;
            }
            const qtyInput = document.getElementById('swalAdjNewQty');
            if (qtyInput) {
              qtyInput.placeholder = `ระบุยอดใหม่ (ปัจจุบัน: ${itm.on_hand_pieces.toLocaleString()} ${itm.unit_piece_name})`;
            }
          }

          if (itemSelectEl) {
            itemSelectEl.addEventListener('change', () => selectItem(itemSelectEl.value));
          }
          enhanceAllSearchableSelects(Swal.getPopup() || document);

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
      }).then(async (res) => {
        if (res.isConfirmed && res.value) {
          const { itemId, newQty, reason } = res.value;
          const items = getItemsDB();
          const itm = items.find(i => i.id === itemId);
          if (itm) {
            const oldQty = itm.on_hand_pieces;
            const diff = newQty - oldQty;
            const staffUser = getLoggedInStaff();
            const recBy = staffUser ? (staffUser.name || staffUser.username) : 'เจ้าหน้าที่พัสดุ สวท.';

            const apiRes = await postToMySQLAPI('adjustStock', { itemId: itm.id, newQty: newQty, reason: reason, recordedBy: recBy });
            if (apiRes && apiRes.status === 'error') {
              Swal.fire({
                icon: 'error',
                title: 'ปรับปรุงยอดสต๊อกไม่สำเร็จ',
                text: apiRes.message || 'เกิดข้อผิดพลาดในการบันทึกข้อมูลลงฐานข้อมูล',
                confirmButtonColor: '#1e40af',
                confirmButtonText: 'ตกลง'
              });
              return;
            }

            itm.on_hand_pieces = newQty;
            saveItemsDB(items);
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
            renderInventoryTable();

            Swal.fire({
              icon: 'success',
              title: 'ปรับปรุงยอดสต๊อกสำเร็จ!',
              html: `รายการ <b>${escapeHtml(itm.name)}</b><br>ปรับยอดจาก ${oldQty.toLocaleString()} เป็น <b>${newQty.toLocaleString()} ${escapeHtml(itm.unit_piece_name)}</b><br><small style="color:#64748b;">เหตุผล: ${escapeHtml(reason)}</small>`,
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
      let req = reqs.find(r => r.id === docNo);
      if (!req && window.lastMonthlyAnalyticsData && Array.isArray(window.lastMonthlyAnalyticsData.monthRequisitions)) {
        req = window.lastMonthlyAnalyticsData.monthRequisitions.find(r => r.id === docNo);
      }
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
        if (isSafeSignatureDataUrl(req.signature)) {
          sigArea.innerHTML = `<img src="${escapeHtml(req.signature.trim())}" class="sig-img-preview" alt="ลายเซ็นผู้รับพัสดุ">`;
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
          const res = await fetch(`${MYSQL_API_URL}?action=getItemTransactions&itemId=${encodeURIComponent(itemId)}`, {
            headers: getStaffAuthHeaders()
          });
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

'''
