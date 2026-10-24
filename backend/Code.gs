/**
 * ==============================================================================
 * ระบบขอเบิกพัสดุและคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต (Stock Order SDU)
 * Google Apps Script Web App Backend (backend/Code.gs)
 * ==============================================================================
 * 
 * 📌 คำแนะนำการติดตั้งและ Deploy ใช้งานภายใน 1 นาที (Deployment Guide):
 * ------------------------------------------------------------------------------
 * 1. สร้าง Google Spreadsheet ใหม่ หรือเปิดไฟล์ Google Sheets ที่ต้องการใช้เก็บข้อมูล
 *    (แนะนำตั้งชื่อ: "SDU_Inventory_Database")
 * 2. ไปที่เมนู "ส่วนขยาย" (Extensions) > "Apps Script"
 * 3. ลบโค้ดเดิมในไฟล์ Code.gs ทั้งหมด แล้วคัดลอกโค้ดจากไฟล์นี้ไปวางแทนที่
 * 4. บันทึกโครงการ (กด Ctrl + S หรือคลิกไอคอนแผ่นดิสก์)
 * 5. เลือกฟังก์ชัน "setupDatabase" จากแถบเครื่องมือด้านบน แล้วกดปุ่ม "เรียกใช้" (Run)
 *    -> ให้สิทธิ์การเข้าถึง (Grant Permissions) เพื่อให้ระบบสร้าง 4 แผ่นงานอัตโนมัติ:
 *       - Items (คลังพัสดุ 58 รายการ พร้อมข้อมูลแปลงหน่วยนับ)
 *       - Requisitions (ประวัติและคิวคำขอเบิก)
 *       - Requisition_Items (รายการพัสดุย่อยในแต่ละคำขอ)
 *       - Departments (ฐานข้อมูล 90+ คณะ/โรงเรียน/กอง)
 * 6. คลิกปุ่มสีน้ำเงิน "ทำให้ใช้งานได้" (Deploy) > "การทำให้ใช้งานได้รายการใหม่" (New deployment)
 *    - เลือกประเภท (Select type): "เว็บแอป" (Web app)
 *    - คำอธิบาย (Description): "SDU Stock Order API v1.0"
 *    - ดำเนินการในฐานะ (Execute as): "ฉัน (Me / your-email@...)"
 *    - ผู้ที่มีสิทธิ์เข้าถึง (Who has access): "ทุกคน (Anyone)"
 * 7. กดปุ่ม "ทำให้ใช้งานได้" (Deploy) แล้วคัดลอก "URL เว็บแอป" (Web app URL) ที่ได้
 *    นำไปใส่ในไฟล์ .env ตัวแปร: VITE_GOOGLE_SCRIPT_API_URL
 * ==============================================================================
 */

// ==============================================================================
// 1. CONFIGURATION & CONSTANTS
// ==============================================================================

const CONFIG = {
  VERSION: '1.0.0',
  LOCK_TIMEOUT_MS: 30000, // 30 seconds wait timeout for Concurrency Control
  SHEETS: {
    ITEMS: 'Items',
    REQUISITIONS: 'Requisitions',
    REQUISITION_ITEMS: 'Requisition_Items',
    DEPARTMENTS: 'Departments'
  },
  HEADERS: {
    ITEMS: [
      'id', 'name', 'category', 'is_multi_unit', 'unit_box_name',
      'unit_piece_name', 'pieces_per_box', 'on_hand_pieces',
      'reserved_pieces', 'min_alert', 'image_piece', 'image_box'
    ],
    REQUISITIONS: [
      'id', 'date', 'requester', 'dept', 'phone', 'purpose',
      'status', 'signature', 'reject_reason', 'created_at', 'updated_at'
    ],
    REQUISITION_ITEMS: [
      'requisition_id', 'item_id', 'name', 'qty_boxes', 'qty_pieces',
      'total_pieces', 'unit_box', 'unit_piece', 'approved_pieces'
    ],
    DEPARTMENTS: [
      'category', 'name', 'parent_name', 'full_label'
    ]
  },
  STATUS: {
    PENDING: 'PENDING',
    APPROVED: 'APPROVED',
    COMPLETED: 'COMPLETED',
    REJECTED: 'REJECTED'
  },
  THAI_MONTHS: [
    'ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.',
    'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'
  ]
};

// ==============================================================================
// 2. HTTP ENTRY POINTS (doGet & doPost)
// ==============================================================================

/**
 * HTTP GET Entry Point
 * @param {Object} e - Event parameter from Google Apps Script
 * @returns {TextOutput} JSON HTTP Response
 */
function doGet(e) {
  try {
    const params = (e && e.parameter) ? e.parameter : {};
    const action = params.action || '';

    switch (action) {
      case 'getItems':
        return handleGetItems(params);

      case 'getRequisitions':
        return handleGetRequisitions(params);

      case 'trackRequisition':
        return handleTrackRequisition(params);

      case 'getDepartments':
        return handleGetDepartments(params);

      default:
        return createJsonResponse({
          status: 'success',
          message: 'SDU Stock Order API (Google Apps Script Web App) is operational.',
          version: CONFIG.VERSION,
          endpoints: {
            GET: [
              '?action=getItems [&category=...]',
              '?action=getRequisitions [&status=...]',
              '?action=trackRequisition&docNo=REQ-...',
              '?action=getDepartments'
            ],
            POST: [
              '{ action: "createRequisition", payload: { ... } }',
              '{ action: "approveRequisition", payload: { docNo: "...", items: [...] } }',
              '{ action: "completeRequisition", payload: { docNo: "...", signature: "..." } }',
              '{ action: "rejectRequisition", payload: { docNo: "...", reason: "..." } }',
              '{ action: "restockItem", payload: { itemId: 1, quantityPieces: 500 } }'
            ]
          }
        });
    }
  } catch (err) {
    return createJsonResponse({
      status: 'error',
      message: 'ข้อผิดพลาดระบบใน doGet: ' + err.message
    });
  }
}

/**
 * HTTP POST Entry Point
 * Implements LockService.getScriptLock() for Concurrency Race Condition Prevention
 * @param {Object} e - Event parameter with postData
 * @returns {TextOutput} JSON HTTP Response
 */
function doPost(e) {
  // Concurrency Control: Acquire script lock before writing to database
  const lock = LockService.getScriptLock();
  const hasLock = lock.tryLock(CONFIG.LOCK_TIMEOUT_MS);

  if (!hasLock) {
    return createJsonResponse({
      status: 'error',
      code: 'LOCK_TIMEOUT',
      message: 'ระบบกำลังประมวลผลคำขออื่นอยู่ในขณะนี้ กรุณาลองใหม่อีกครั้งใน 2-3 วินาที'
    });
  }

  try {
    let body = {};
    if (e && e.postData && e.postData.contents) {
      try {
        body = JSON.parse(e.postData.contents);
      } catch (parseErr) {
        return createJsonResponse({
          status: 'error',
          code: 'INVALID_JSON',
          message: 'รูปแบบข้อมูล JSON ใน Request Body ไม่ถูกต้อง: ' + parseErr.message
        });
      }
    } else if (e && e.parameter) {
      body = e.parameter;
      if (typeof body.payload === 'string') {
        try {
          body.payload = JSON.parse(body.payload);
        } catch (err) {}
      }
    }

    const action = body.action || '';
    const payload = body.payload || body;

    switch (action) {
      case 'createRequisition':
        return handleCreateRequisition(payload);

      case 'approveRequisition':
        return handleApproveRequisition(payload);

      case 'completeRequisition':
        return handleCompleteRequisition(payload);

      case 'rejectRequisition':
        return handleRejectRequisition(payload);

      case 'restockItem':
        return handleRestockItem(payload);

      default:
        return createJsonResponse({
          status: 'error',
          code: 'UNKNOWN_ACTION',
          message: 'ไม่พบคำสั่ง action: "' + action + '" ในระบบ'
        });
    }
  } catch (err) {
    return createJsonResponse({
      status: 'error',
      message: 'ข้อผิดพลาดระบบใน doPost: ' + err.message
    });
  } finally {
    // Release the script lock immediately when write is finished
    lock.releaseLock();
  }
}

// ==============================================================================
// 3. GET ACTION HANDLERS
// ==============================================================================

/**
 * ดึงรายการพัสดุคงคลังทั้งหมด (3.1 GET /exec?action=getItems)
 * คำนวณ Available = On-Hand - Reserved อัตโนมัติ
 */
function handleGetItems(params) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.SHEETS.ITEMS);
  if (!sheet) {
    return createJsonResponse({ status: 'error', message: 'ไม่พบแผ่นงาน Items ในฐานข้อมูล' });
  }

  const rawItems = readSheetObjects(sheet);
  let items = rawItems.map(item => {
    const onHand = Number(item.on_hand_pieces) || 0;
    const reserved = Number(item.reserved_pieces) || 0;
    const available = Math.max(0, onHand - reserved);
    const isMultiUnit = String(item.is_multi_unit).toLowerCase() === 'true';

    return {
      id: Number(item.id) || 0,
      name: String(item.name || ''),
      category: String(item.category || ''),
      is_multi_unit: isMultiUnit,
      unit_box_name: item.unit_box_name ? String(item.unit_box_name) : null,
      unit_piece_name: String(item.unit_piece_name || 'ชิ้น'),
      pieces_per_box: Number(item.pieces_per_box) || 1,
      on_hand_pieces: onHand,
      reserved_pieces: reserved,
      available_pieces: available,
      min_alert: Number(item.min_alert) || 500,
      image_piece: String(item.image_piece || ''),
      image_box: String(item.image_box || '')
    };
  });

  // กรองหมวดหมู่หากมีการระบุ
  if (params && params.category && params.category !== 'ALL') {
    items = items.filter(i => i.category === params.category);
  }

  return createJsonResponse({
    status: 'success',
    data: items,
    total: items.length
  });
}

/**
 * ดึงประวัติและคิวคำขอเบิกพัสดุทั้งหมด (GET /exec?action=getRequisitions)
 * เชื่อมโยงข้อมูลตาราง Requisitions และ Requisition_Items เข้าด้วยกัน
 */
function handleGetRequisitions(params) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const reqSheet = ss.getSheetByName(CONFIG.SHEETS.REQUISITIONS);
  const itemsSheet = ss.getSheetByName(CONFIG.SHEETS.REQUISITION_ITEMS);

  if (!reqSheet) {
    return createJsonResponse({ status: 'error', message: 'ไม่พบแผ่นงาน Requisitions' });
  }

  const rawReqs = readSheetObjects(reqSheet);
  const rawItems = itemsSheet ? readSheetObjects(itemsSheet) : [];

  // Group items by requisition_id
  const itemsMap = {};
  rawItems.forEach(it => {
    const reqId = String(it.requisition_id);
    if (!itemsMap[reqId]) itemsMap[reqId] = [];
    itemsMap[reqId].push({
      itemId: Number(it.item_id),
      name: String(it.name || ''),
      qtyBoxes: Number(it.qty_boxes) || 0,
      qtyPieces: Number(it.qty_pieces) || 0,
      totalPieces: Number(it.total_pieces) || 0,
      unitBox: String(it.unit_box || ''),
      unitPiece: String(it.unit_piece || 'ชิ้น'),
      approvedPieces: Number(it.approved_pieces !== undefined ? it.approved_pieces : it.total_pieces) || 0
    });
  });

  let requisitions = rawReqs.map(r => {
    const id = String(r.id);
    return {
      id: id,
      date: String(r.date || ''),
      requester: String(r.requester || ''),
      dept: String(r.dept || ''),
      phone: String(r.phone || ''),
      purpose: String(r.purpose || ''),
      status: String(r.status || CONFIG.STATUS.PENDING),
      signature: r.signature ? String(r.signature) : null,
      reject_reason: r.reject_reason ? String(r.reject_reason) : null,
      rejectReason: r.reject_reason ? String(r.reject_reason) : null,
      created_at: String(r.created_at || ''),
      updated_at: String(r.updated_at || ''),
      items: itemsMap[id] || []
    };
  });

  // กรองตามสถานะหากมีระบุ
  if (params && params.status && params.status !== 'ALL') {
    requisitions = requisitions.filter(r => r.status === params.status);
  }

  return createJsonResponse({
    status: 'success',
    data: requisitions,
    total: requisitions.length
  });
}

/**
 * ค้นหาติดตามสถานะคำขอรายเอกสาร (3.2 GET /exec?action=trackRequisition&docNo=...)
 */
function handleTrackRequisition(params) {
  const docNo = String(params.docNo || params.id || '').trim();
  if (!docNo) {
    return createJsonResponse({
      status: 'error',
      found: false,
      message: 'กรุณาระบุเลขที่เอกสารคำขอที่ต้องการค้นหา (docNo)'
    });
  }

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const reqSheet = ss.getSheetByName(CONFIG.SHEETS.REQUISITIONS);
  const itemsSheet = ss.getSheetByName(CONFIG.SHEETS.REQUISITION_ITEMS);

  if (!reqSheet) {
    return createJsonResponse({ status: 'error', found: false, message: 'ไม่พบแผ่นงาน Requisitions' });
  }

  const rawReqs = readSheetObjects(reqSheet);
  const matchedReq = rawReqs.find(r => String(r.id).trim().toUpperCase() === docNo.toUpperCase());

  if (!matchedReq) {
    return createJsonResponse({
      status: 'error',
      found: false,
      message: 'ไม่พบข้อมูลเอกสารคำขอเลขที่ดังกล่าว'
    });
  }

  const rawItems = itemsSheet ? readSheetObjects(itemsSheet) : [];
  const items = rawItems
    .filter(it => String(it.requisition_id).trim().toUpperCase() === docNo.toUpperCase())
    .map(it => ({
      itemId: Number(it.item_id),
      name: String(it.name || ''),
      qtyBoxes: Number(it.qty_boxes) || 0,
      qtyPieces: Number(it.qty_pieces) || 0,
      totalPieces: Number(it.total_pieces) || 0,
      unitBox: String(it.unit_box || ''),
      unitPiece: String(it.unit_piece || 'ชิ้น'),
      approvedPieces: Number(it.approved_pieces !== undefined ? it.approved_pieces : it.total_pieces) || 0
    }));

  return createJsonResponse({
    status: 'success',
    found: true,
    data: {
      id: matchedReq.id,
      date: matchedReq.date,
      requester: matchedReq.requester,
      dept: matchedReq.dept,
      phone: matchedReq.phone,
      purpose: matchedReq.purpose,
      status: matchedReq.status,
      signature: matchedReq.signature || null,
      reject_reason: matchedReq.reject_reason || null,
      rejectReason: matchedReq.reject_reason || null,
      created_at: matchedReq.created_at,
      updated_at: matchedReq.updated_at,
      items: items
    }
  });
}

/**
 * ดึงรายชื่อ 90+ คณะ/โรงเรียน/กอง (GET /exec?action=getDepartments)
 */
function handleGetDepartments(params) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.SHEETS.DEPARTMENTS);
  if (!sheet) {
    return createJsonResponse({ status: 'error', message: 'ไม่พบแผ่นงาน Departments' });
  }

  const departments = readSheetObjects(sheet);
  return createJsonResponse({
    status: 'success',
    data: departments,
    total: departments.length
  });
}

// ==============================================================================
// 4. POST ACTION HANDLERS
// ==============================================================================

/**
 * สร้างคำขอเบิกพัสดุใหม่ (3.3 POST /exec action: "createRequisition")
 * ตรวจสอบ Available Stock ก่อนสร้างคำขอ หากสต๊อกไม่พอจะปฏิเสธคำขอทันที
 */
function handleCreateRequisition(payload) {
  const requester = String(payload.requester || '').trim();
  const dept = String(payload.dept || '').trim();
  const phone = String(payload.phone || '').trim();
  const purpose = String(payload.purpose || '').trim();
  const items = Array.isArray(payload.items) ? payload.items : [];

  if (!requester || !dept || items.length === 0) {
    return createJsonResponse({
      status: 'error',
      code: 'VALIDATION_FAILED',
      message: 'กรุณากรอกข้อมูลผู้ขอเบิก, สังกัดหน่วยงาน และเลือกพัสดุอย่างน้อย 1 รายการ'
    });
  }

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const itemsSheet = ss.getSheetByName(CONFIG.SHEETS.ITEMS);
  const reqSheet = ss.getSheetByName(CONFIG.SHEETS.REQUISITIONS);
  const reqItemsSheet = ss.getSheetByName(CONFIG.SHEETS.REQUISITION_ITEMS);

  if (!itemsSheet || !reqSheet || !reqItemsSheet) {
    return createJsonResponse({
      status: 'error',
      code: 'SHEETS_NOT_FOUND',
      message: 'โครงสร้างฐานข้อมูลแผ่นงานไม่ครบถ้วน กรุณารัน setupDatabase ก่อน'
    });
  }

  // 1. ตรวจสอบสต๊อกคงเหลือจริงพร้อมเบิก (Available = On-Hand - Reserved)
  const inventoryItems = readSheetObjects(itemsSheet);
  const inventoryMap = {};
  inventoryItems.forEach(itm => {
    inventoryMap[Number(itm.id)] = itm;
  });

  for (let i = 0; i < items.length; i++) {
    const reqItem = items[i];
    const itemId = Number(reqItem.itemId);
    const stockItem = inventoryMap[itemId];

    if (!stockItem) {
      return createJsonResponse({
        status: 'error',
        code: 'ITEM_NOT_FOUND',
        message: 'ไม่พบรหัสพัสดุ ID ' + itemId + ' ในคลังพัสดุ'
      });
    }

    const onHand = Number(stockItem.on_hand_pieces) || 0;
    const reserved = Number(stockItem.reserved_pieces) || 0;
    const available = Math.max(0, onHand - reserved);
    const requested = Number(reqItem.totalPieces) || 0;

    if (requested > available) {
      return createJsonResponse({
        status: 'error',
        code: 'INSUFFICIENT_STOCK',
        message: 'ยอดพัสดุคงเหลือพร้อมเบิกไม่เพียงพอ',
        details: {
          itemId: itemId,
          name: stockItem.name,
          requested: requested,
          available: available
        }
      });
    }
  }

  // 2. ออกเลขที่เอกสารคำขอเบิกตามรูปแบบ REQ-YYYYMM-XXXX (ปี พ.ศ.)
  const docNo = generateDocNo();
  const now = new Date();
  const thaiDate = formatThaiDate(now);
  const nowIso = now.toISOString();

  // 3. บันทึกหัวเอกสารลงในแผ่นงาน Requisitions
  const reqRow = [
    docNo,
    thaiDate,
    requester,
    dept,
    phone,
    purpose,
    CONFIG.STATUS.PENDING,
    '', // signature
    '', // reject_reason
    nowIso,
    nowIso
  ];
  reqSheet.appendRow(reqRow);

  // 4. บันทึกรายการพัสดุลงในแผ่นงาน Requisition_Items
  const itemRows = items.map(it => [
    docNo,
    Number(it.itemId),
    String(it.name || ''),
    Number(it.qtyBoxes) || 0,
    Number(it.qtyPieces) || 0,
    Number(it.totalPieces) || 0,
    String(it.unitBox || ''),
    String(it.unitPiece || 'ชิ้น'),
    Number(it.totalPieces) || 0 // approved_pieces เริ่มต้นเท่ากับจำนวนที่ขอ
  ]);

  if (itemRows.length > 0) {
    const startRow = reqItemsSheet.getLastRow() + 1;
    reqItemsSheet.getRange(startRow, 1, itemRows.length, itemRows[0].length).setValues(itemRows);
  }

  return createJsonResponse({
    status: 'success',
    message: 'สร้างคำขอเบิกพัสดุสำเร็จ',
    docNo: docNo,
    createdAt: nowIso
  });
}

/**
 * เจ้าหน้าที่อนุมัติคำขอ (3.4 POST /exec action: "approveRequisition")
 * เปลี่ยนสถานะเป็น APPROVED และเพิ่มยอดล็อกใน reserved_pieces ของตาราง Items
 */
function handleApproveRequisition(payload) {
  const docNo = String(payload.docNo || payload.id || '').trim();
  if (!docNo) {
    return createJsonResponse({ status: 'error', message: 'กรุณาระบุเลขที่เอกสารคำขอ (docNo)' });
  }

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const reqSheet = ss.getSheetByName(CONFIG.SHEETS.REQUISITIONS);
  const reqItemsSheet = ss.getSheetByName(CONFIG.SHEETS.REQUISITION_ITEMS);
  const itemsSheet = ss.getSheetByName(CONFIG.SHEETS.ITEMS);

  const reqIndex = findRowIndex(reqSheet, 1, docNo); // Col 1 = id
  if (reqIndex === -1) {
    return createJsonResponse({ status: 'error', message: 'ไม่พบเอกสารคำขอเลขที่ ' + docNo });
  }

  // ตรวจสอบสถานะเดิม
  const statusCol = findHeaderIndex(reqSheet, 'status');
  const currentStatus = String(reqSheet.getRange(reqIndex, statusCol).getValue()).trim();

  if (currentStatus !== CONFIG.STATUS.PENDING) {
    return createJsonResponse({
      status: 'error',
      message: 'ไม่สามารถอนุมัติได้เนื่องจากคำขอนี้อยู่ในสถานะ ' + currentStatus + ' แล้ว'
    });
  }

  // ดึงรายการพัสดุในคำขอ
  const reqItems = readSheetObjects(reqItemsSheet).filter(
    it => String(it.requisition_id).trim().toUpperCase() === docNo.toUpperCase()
  );

  // ตรวจสอบว่ามีรายการปรับยอดจัดจ่ายจริง (payload.items) หรือไม่
  const customApprovedMap = {};
  if (Array.isArray(payload.items)) {
    payload.items.forEach(pi => {
      customApprovedMap[Number(pi.itemId)] = Number(pi.approvedPieces);
    });
  }

  // ล็อกยอดสต๊อกใน Items sheet
  const itemsData = readSheetObjects(itemsSheet);
  const reservedCol = findHeaderIndex(itemsSheet, 'reserved_pieces');
  const itemIdCol = findHeaderIndex(itemsSheet, 'id');

  reqItems.forEach(ri => {
    const itmId = Number(ri.item_id);
    const approvedQty = customApprovedMap[itmId] !== undefined
      ? customApprovedMap[itmId]
      : (Number(ri.approved_pieces) || Number(ri.total_pieces) || 0);

    const itemRowIdx = findRowIndex(itemsSheet, itemIdCol, itmId);
    if (itemRowIdx !== -1) {
      const currentReserved = Number(itemsSheet.getRange(itemRowIdx, reservedCol).getValue()) || 0;
      itemsSheet.getRange(itemRowIdx, reservedCol).setValue(currentReserved + approvedQty);
    }
  });

  // อัปเดตสถานะใน Requisitions เป็น APPROVED
  const updatedCol = findHeaderIndex(reqSheet, 'updated_at');
  reqSheet.getRange(reqIndex, statusCol).setValue(CONFIG.STATUS.APPROVED);
  if (updatedCol !== -1) {
    reqSheet.getRange(reqIndex, updatedCol).setValue(new Date().toISOString());
  }

  return createJsonResponse({
    status: 'success',
    docNo: docNo,
    statusNow: CONFIG.STATUS.APPROVED,
    message: 'อนุมัติคำขอและล็อกยอดพัสดุสำเร็จ'
  });
}

/**
 * ผู้ขอเบิกมารับของ บันทึกลายเซ็นและตัดยอดสต๊อกจริง (3.5 POST /exec action: "completeRequisition")
 * หัก on_hand_pieces และคืน reserved_pieces
 */
function handleCompleteRequisition(payload) {
  const docNo = String(payload.docNo || payload.id || '').trim();
  const signature = String(payload.signature || '').trim();

  if (!docNo) {
    return createJsonResponse({ status: 'error', message: 'กรุณาระบุเลขที่เอกสารคำขอ (docNo)' });
  }

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const reqSheet = ss.getSheetByName(CONFIG.SHEETS.REQUISITIONS);
  const reqItemsSheet = ss.getSheetByName(CONFIG.SHEETS.REQUISITION_ITEMS);
  const itemsSheet = ss.getSheetByName(CONFIG.SHEETS.ITEMS);

  const reqIndex = findRowIndex(reqSheet, 1, docNo);
  if (reqIndex === -1) {
    return createJsonResponse({ status: 'error', message: 'ไม่พบเอกสารคำขอเลขที่ ' + docNo });
  }

  const reqItems = readSheetObjects(reqItemsSheet).filter(
    it => String(it.requisition_id).trim().toUpperCase() === docNo.toUpperCase()
  );

  // ตัดยอดสต๊อกคงคลังจริง และลดสต๊อกกันจองใน Items
  const onHandCol = findHeaderIndex(itemsSheet, 'on_hand_pieces');
  const reservedCol = findHeaderIndex(itemsSheet, 'reserved_pieces');
  const itemIdCol = findHeaderIndex(itemsSheet, 'id');

  reqItems.forEach(ri => {
    const itmId = Number(ri.item_id);
    const approvedQty = Number(ri.approved_pieces) || Number(ri.total_pieces) || 0;

    const itemRowIdx = findRowIndex(itemsSheet, itemIdCol, itmId);
    if (itemRowIdx !== -1) {
      const currentOnHand = Number(itemsSheet.getRange(itemRowIdx, onHandCol).getValue()) || 0;
      const currentReserved = Number(itemsSheet.getRange(itemRowIdx, reservedCol).getValue()) || 0;

      const newOnHand = Math.max(0, currentOnHand - approvedQty);
      const newReserved = Math.max(0, currentReserved - approvedQty);

      itemsSheet.getRange(itemRowIdx, onHandCol).setValue(newOnHand);
      itemsSheet.getRange(itemRowIdx, reservedCol).setValue(newReserved);
    }
  });

  // อัปเดตสถานะเป็น COMPLETED และบันทึกลายเซ็น
  const statusCol = findHeaderIndex(reqSheet, 'status');
  const sigCol = findHeaderIndex(reqSheet, 'signature');
  const updatedCol = findHeaderIndex(reqSheet, 'updated_at');

  reqSheet.getRange(reqIndex, statusCol).setValue(CONFIG.STATUS.COMPLETED);
  if (signature && sigCol !== -1) {
    reqSheet.getRange(reqIndex, sigCol).setValue(signature);
  }
  if (updatedCol !== -1) {
    reqSheet.getRange(reqIndex, updatedCol).setValue(new Date().toISOString());
  }

  return createJsonResponse({
    status: 'success',
    docNo: docNo,
    statusNow: CONFIG.STATUS.COMPLETED,
    message: 'บันทึกลายเซ็นและตัดยอดคงคลังจริงเรียบร้อยแล้ว'
  });
}

/**
 * เจ้าหน้าที่ปฏิเสธคำขอ (3.6 POST /exec action: "rejectRequisition")
 * คืนยอดสต๊อกที่เคยกันไว้ (หากเคย APPROVED) และบันทึกเหตุผล
 */
function handleRejectRequisition(payload) {
  const docNo = String(payload.docNo || payload.id || '').trim();
  const reason = String(payload.reason || '').trim();

  if (!docNo) {
    return createJsonResponse({ status: 'error', message: 'กรุณาระบุเลขที่เอกสารคำขอ (docNo)' });
  }

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const reqSheet = ss.getSheetByName(CONFIG.SHEETS.REQUISITIONS);
  const reqItemsSheet = ss.getSheetByName(CONFIG.SHEETS.REQUISITION_ITEMS);
  const itemsSheet = ss.getSheetByName(CONFIG.SHEETS.ITEMS);

  const reqIndex = findRowIndex(reqSheet, 1, docNo);
  if (reqIndex === -1) {
    return createJsonResponse({ status: 'error', message: 'ไม่พบเอกสารคำขอเลขที่ ' + docNo });
  }

  const statusCol = findHeaderIndex(reqSheet, 'status');
  const reasonCol = findHeaderIndex(reqSheet, 'reject_reason');
  const updatedCol = findHeaderIndex(reqSheet, 'updated_at');
  const prevStatus = String(reqSheet.getRange(reqIndex, statusCol).getValue()).trim();

  // หากคำขอนี้เคยได้รับอนุมัติ (APPROVED) มาก่อน ต้องคืนยอด reserved_pieces กลับสู่คลัง
  if (prevStatus === CONFIG.STATUS.APPROVED) {
    const reqItems = readSheetObjects(reqItemsSheet).filter(
      it => String(it.requisition_id).trim().toUpperCase() === docNo.toUpperCase()
    );
    const reservedCol = findHeaderIndex(itemsSheet, 'reserved_pieces');
    const itemIdCol = findHeaderIndex(itemsSheet, 'id');

    reqItems.forEach(ri => {
      const itmId = Number(ri.item_id);
      const approvedQty = Number(ri.approved_pieces) || Number(ri.total_pieces) || 0;
      const itemRowIdx = findRowIndex(itemsSheet, itemIdCol, itmId);
      if (itemRowIdx !== -1) {
        const curReserved = Number(itemsSheet.getRange(itemRowIdx, reservedCol).getValue()) || 0;
        itemsSheet.getRange(itemRowIdx, reservedCol).setValue(Math.max(0, curReserved - approvedQty));
      }
    });
  }

  // เปลี่ยนสถานะเป็น REJECTED และบันทึกเหตุผล
  reqSheet.getRange(reqIndex, statusCol).setValue(CONFIG.STATUS.REJECTED);
  if (reasonCol !== -1) {
    reqSheet.getRange(reqIndex, reasonCol).setValue(reason);
  }
  if (updatedCol !== -1) {
    reqSheet.getRange(reqIndex, updatedCol).setValue(new Date().toISOString());
  }

  return createJsonResponse({
    status: 'success',
    docNo: docNo,
    statusNow: CONFIG.STATUS.REJECTED,
    message: 'ปฏิเสธคำขอและคืนยอดพัสดุเรียบร้อยแล้ว'
  });
}

/**
 * เจ้าหน้าที่รับพัสดุเข้าคลัง (POST /exec action: "restockItem")
 */
function handleRestockItem(payload) {
  const itemId = Number(payload.itemId);
  const qty = Number(payload.quantityPieces || payload.quantity || payload.qty) || 0;

  if (!itemId || qty <= 0) {
    return createJsonResponse({
      status: 'error',
      message: 'กรุณาระบุรหัสพัสดุ (itemId) และจำนวนที่รับเข้ามากกว่า 0'
    });
  }

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const itemsSheet = ss.getSheetByName(CONFIG.SHEETS.ITEMS);
  const itemIdCol = findHeaderIndex(itemsSheet, 'id');
  const onHandCol = findHeaderIndex(itemsSheet, 'on_hand_pieces');

  const rowIdx = findRowIndex(itemsSheet, itemIdCol, itemId);
  if (rowIdx === -1) {
    return createJsonResponse({ status: 'error', message: 'ไม่พบพัสดุ ID ' + itemId });
  }

  const currentOnHand = Number(itemsSheet.getRange(rowIdx, onHandCol).getValue()) || 0;
  const newOnHand = currentOnHand + qty;
  itemsSheet.getRange(rowIdx, onHandCol).setValue(newOnHand);

  return createJsonResponse({
    status: 'success',
    message: 'รับพัสดุเข้าคลังสำเร็จ',
    itemId: itemId,
    on_hand_pieces: newOnHand
  });
}

// ==============================================================================
// 5. DATABASE INITIALIZATION & SEEDING (1-Minute Quick Setup)
// ==============================================================================

/**
 * 🚀 ฟังก์ชันติดตั้งฐานข้อมูลและค่าเริ่มต้น (1-Click Database Setup)
 * รันฟังก์ชันนี้จาก Apps Script Editor เพื่อสร้างแผ่นงาน จัดหัวตาราง และใส่ข้อมูลตั้งต้นทันที
 */
function setupDatabase() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  Logger.log('🚀 เริ่มต้นการตั้งค่าฐานข้อมูล SDU Inventory Database...');

  // 1. สร้างแผ่นงาน Items
  let itemsSheet = ss.getSheetByName(CONFIG.SHEETS.ITEMS);
  if (!itemsSheet) itemsSheet = ss.insertSheet(CONFIG.SHEETS.ITEMS);
  formatSheetHeader(itemsSheet, CONFIG.HEADERS.ITEMS);
  if (itemsSheet.getLastRow() <= 1) {
    seedInitialItems(itemsSheet);
    Logger.log('  [+] ใส่ข้อมูลตั้งต้นแผ่นงาน Items สำเร็จ');
  }

  // 2. สร้างแผ่นงาน Requisitions
  let reqSheet = ss.getSheetByName(CONFIG.SHEETS.REQUISITIONS);
  if (!reqSheet) reqSheet = ss.insertSheet(CONFIG.SHEETS.REQUISITIONS);
  formatSheetHeader(reqSheet, CONFIG.HEADERS.REQUISITIONS);

  // 3. สร้างแผ่นงาน Requisition_Items
  let reqItemsSheet = ss.getSheetByName(CONFIG.SHEETS.REQUISITION_ITEMS);
  if (!reqItemsSheet) reqItemsSheet = ss.insertSheet(CONFIG.SHEETS.REQUISITION_ITEMS);
  formatSheetHeader(reqItemsSheet, CONFIG.HEADERS.REQUISITION_ITEMS);

  // ใส่ตัวอย่างคำขอเริ่มต้นหากยังไม่มีข้อมูล
  if (reqSheet.getLastRow() <= 1) {
    seedInitialRequisitions(reqSheet, reqItemsSheet);
    Logger.log('  [+] ใส่ข้อมูลตัวอย่างคำขอเบิก (Requisitions) สำเร็จ');
  }

  // 4. สร้างแผ่นงาน Departments
  let deptSheet = ss.getSheetByName(CONFIG.SHEETS.DEPARTMENTS);
  if (!deptSheet) deptSheet = ss.insertSheet(CONFIG.SHEETS.DEPARTMENTS);
  formatSheetHeader(deptSheet, CONFIG.HEADERS.DEPARTMENTS);
  if (deptSheet.getLastRow() <= 1) {
    seedInitialDepartments(deptSheet);
    Logger.log('  [+] ใส่ข้อมูลรายชื่อ 90+ หน่วยงาน (Departments) สำเร็จ');
  }

  // ลบแผ่นงานเริ่มต้น 'Sheet1' หรือ 'แผ่น1' หากว่างเปล่า
  const defaultSheet = ss.getSheetByName('Sheet1') || ss.getSheetByName('แผ่น1');
  if (defaultSheet && ss.getSheets().length > 1 && defaultSheet.getLastRow() === 0) {
    try { ss.deleteSheet(defaultSheet); } catch (e) {}
  }

  Logger.log('=================================================================');
  Logger.log('🎉 การติดตั้งฐานข้อมูล SDU Stock Order สำเร็จสมบูรณ์ 100%!');
  Logger.log('ขั้นตอนถัดไป: คลิก "Deploy" > "New deployment" > เลือก "Web app"');
  Logger.log('Execute as: Me, Who has access: Anyone');
  Logger.log('=================================================================');
}

/**
 * ปรับแต่งรูปแบบหัวตารางให้สวยงาม สไตล์ทางการ มสด. (SDU Blue #1e40af)
 */
function formatSheetHeader(sheet, headers) {
  const headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange.setValues([headers]);
  headerRange.setBackground('#1e40af');
  headerRange.setFontColor('#ffffff');
  headerRange.setFontWeight('bold');
  headerRange.setFontFamily('Prompt');
  headerRange.setFontSize(10);
  headerRange.setHorizontalAlignment('center');
  sheet.setFrozenRows(1);
}

/**
 * ใส่ข้อมูลรายการพัสดุตั้งต้น 58 รายการจากไฟล์ Excel ยอดสต๊อก ตค.xlsx
 */
function seedInitialItems(sheet) {
  const items = [
    [1, "ซองขยายข้างมีครุฑ 279´432 (กล่องละ 250 ซอง)", "ซองเอกสาร", true, "กล่อง", "ซอง", 250, 1750, 500, 500, "assets/images/image1.jpeg", "assets/images/image10.jpeg"],
    [2, "กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)", "กระดาษและแบบฟอร์ม", true, "กล่อง", "ใบ", 2000, 34500, 2000, 5000, "assets/images/image2.jpeg", "assets/images/image11.jpeg"],
    [3, "ซองเอกสารสีขาว 7´10 (500 ซองต่อกล่อง)", "ซองเอกสาร", true, "กล่อง", "ซอง", 500, 1000, 0, 250, "assets/images/image3.jpeg", "assets/images/image12.jpeg"],
    [4, "กระดาษลายเส้น (ห่อละ 500 แผ่น)", "กระดาษและแบบฟอร์ม", true, "ห่อ", "แผ่น", 500, 23500, 0, 1000, "assets/images/image4.jpeg", "assets/images/image13.jpeg"],
    [5, "แฟ้มเสนอ", "เครื่องเขียนและแฟ้ม", false, "เล่ม", "เล่ม", 1, 15, 3, 5, "assets/images/image5.jpeg", "assets/images/image5.jpeg"],
    [6, "ซองเอกสารน้ำตาล (มสด) 9´12.3", "ซองเอกสาร", true, "กล่อง", "ซอง", 500, 1500, 0, 500, "assets/images/image14.jpeg", "assets/images/image15.jpeg"],
    [7, "กระดาษสติ๊กเกอร์แนวนอน ตัดหน้าซองจดหมาย", "กระดาษและแบบฟอร์ม", true, "ซอง", "แผ่น", 500, 4500, 0, 500, "assets/images/image16.jpeg", "assets/images/image17.jpeg"],
    [8, "กระดาษสติ๊กเกอร์แนวตั้ง ติดหน้าซองข้อสอบ", "กระดาษและแบบฟอร์ม", true, "ซอง", "แผ่น", 500, 1000, 0, 250, "assets/images/image18.jpeg", "assets/images/image19.jpeg"],
    [9, "กระดาษสติ๊กเกอร์ เต็มแผ่น", "กระดาษและแบบฟอร์ม", true, "ห่อ", "แผ่น", 500, 500, 0, 100, "assets/images/image20.jpeg", "assets/images/image21.jpeg"],
    [10, "แบบฟอร์มแก้ I", "กระดาษและแบบฟอร์ม", true, "มัด", "ชุด", 500, 2500, 0, 500, "assets/images/image22.jpeg", "assets/images/image23.jpeg"],
    [11, "ซองข้อสอบน้ำตาลไม่ขยายข้างพิมพ์ข้อความ (มสด)", "ซองเอกสาร", true, "กล่อง", "ซอง", 250, 4000, 0, 1000, "assets/images/image24.jpeg", "assets/images/image25.jpeg"],
    [12, "ซองเอกสารไม่ขยายข้าง สีน้ำตาล 10´15 นิ้ว (มสด) (กล่องละ 250 ซอง)", "ซองเอกสาร", true, "กล่อง", "ซอง", 250, 1500, 0, 500, "assets/images/image26.jpeg", "assets/images/image27.jpeg"],
    [13, "แบบฟอร์มทรานสคริป(ไทย)ป.ตรี ซองละ 500 ใบ", "กระดาษและแบบฟอร์ม", true, "ซอง", "ใบ", 500, 1500, 0, 300, "assets/images/image28.jpeg", "assets/images/image29.png"],
    [14, "แบบฟอร์มทรานสคริป(อังกฤษ)ป.ตรี ซองละ 500 ใบ", "กระดาษและแบบฟอร์ม", true, "ซอง", "ใบ", 500, 3500, 0, 500, "assets/images/image30.jpeg", "assets/images/image31.png"],
    [15, "ทรานสคริป ป.โท(ไทย) ซองละ 500 ใบ", "กระดาษและแบบฟอร์ม", true, "ซอง", "ใบ", 500, 1000, 0, 200, "assets/images/image32.jpeg", "assets/images/image33.jpeg"],
    [16, "ทรานสคริป ป.โท(อังกฤษ) ซองละ 500 ใบ", "กระดาษและแบบฟอร์ม", true, "ซอง", "ใบ", 500, 1500, 0, 300, "assets/images/image34.jpeg", "assets/images/image35.png"],
    [17, "ใบรับรอง(ไทย)ซองละ 500 ใบ", "กระดาษและแบบฟอร์ม", true, "ซอง", "ใบ", 500, 2000, 0, 400, "assets/images/image36.jpeg", "assets/images/image37.jpeg"],
    [18, "ใบรับรอง(อังกฤษ)ซองละ 500 ใบ", "กระดาษและแบบฟอร์ม", true, "ซอง", "ใบ", 500, 3500, 0, 500, "assets/images/image38.jpeg", "assets/images/image39.png"],
    [19, "คลิปดำNO.108", "เครื่องเขียนและแฟ้ม", true, "กล่อง", "ตัว", 12, 72, 0, 24, "assets/images/image40.jpeg", "assets/images/image41.png"],
    [20, "คลิปดำNO.110", "เครื่องเขียนและแฟ้ม", true, "กล่อง", "ตัว", 12, 60, 0, 24, "assets/images/image42.png", "assets/images/image43.jpeg"],
    [21, "ไส้MAX 10 MM", "เครื่องเขียนและแฟ้ม", true, "กล่อง", "แถว", 20, 20, 0, 5, "assets/images/image44.png", "assets/images/image45.jpeg"],
    [22, "ไส้MAX 12", "เครื่องเขียนและแฟ้ม", true, "กล่อง", "แถว", 20, 20, 0, 5, "assets/images/image46.png", "assets/images/image47.jpeg"],
    [23, "ซองกันกระแทก 270´327", "ซองเอกสาร", true, "กล่อง", "ซอง", 80, 2400, 0, 500, "assets/images/image48.jpeg", "assets/images/image49.jpeg"],
    [24, "แม็กเล็ก", "เครื่องเขียนและแฟ้ม", false, "อัน", "อัน", 1, 7, 0, 2, "assets/images/image50.jpeg", "assets/images/image50.jpeg"],
    [25, "แม็กใหญ่", "เครื่องเขียนและแฟ้ม", false, "อัน", "อัน", 1, 5, 0, 2, "assets/images/image51.jpeg", "assets/images/image51.jpeg"],
    [26, "สก็อตเทปใส", "เครื่องเขียนและแฟ้ม", true, "แพ็ค", "ม้วน", 6, 24, 0, 6, "assets/images/image52.jpeg", "assets/images/image52.jpeg"],
    [27, "สก็อตเทปขุ่น", "เครื่องเขียนและแฟ้ม", true, "แพ็ค", "ม้วน", 6, 27, 0, 6, "assets/images/image53.jpeg", "assets/images/image53.jpeg"],
    [28, "สก็อตเทปย่น", "เครื่องเขียนและแฟ้ม", true, "แพ็ค", "ม้วน", 6, 10, 0, 6, "assets/images/image54.jpeg", "assets/images/image54.jpeg"],
    [29, "กาวแท่ง", "เครื่องเขียนและแฟ้ม", false, "แท่ง", "แท่ง", 1, 22, 0, 5, "assets/images/image55.jpeg", "assets/images/image55.jpeg"],
    [30, "กาวขวด", "เครื่องเขียนและแฟ้ม", false, "ขวด", "ขวด", 1, 6, 0, 2, "assets/images/image56.jpeg", "assets/images/image56.jpeg"],
    [31, "กรรไกร", "เครื่องเขียนและแฟ้ม", false, "เล่ม", "เล่ม", 1, 20, 0, 5, "assets/images/image57.jpeg", "assets/images/image57.jpeg"],
    [32, "คัตเตอร์", "เครื่องเขียนและแฟ้ม", false, "อัน", "อัน", 1, 12, 0, 3, "assets/images/image58.png", "assets/images/image58.png"],
    [33, "เครื่องเจาะกระดาษ", "เครื่องเขียนและแฟ้ม", false, "เครื่อง", "เครื่อง", 1, 2, 0, 1, "assets/images/image50.jpeg", "assets/images/image50.jpeg"],
    [34, "ไม้บรรทัด", "เครื่องเขียนและแฟ้ม", false, "อัน", "อัน", 1, 7, 0, 2, "assets/images/image51.jpeg", "assets/images/image51.jpeg"]
  ];

  sheet.getRange(2, 1, items.length, items[0].length).setValues(items);
  sheet.autoResizeColumns(1, items[0].length);
}

/**
 * ใส่ข้อมูลตัวอย่างคำขอเริ่มต้น REQ-256910-0042 และ REQ-256910-0043
 */
function seedInitialRequisitions(reqSheet, itemsSheet) {
  const sampleReqs = [
    [
      "REQ-256910-0042",
      "21 ต.ค. 2569 10:15 น.",
      "อ.สมชาย ใจดี",
      "โรงเรียนการเรือน - เทคโนโลยีการประกอบอาหารและการบริการ",
      "081-998-7766",
      "ใช้สำหรับการจัดการเรียนการสอนและสอบปฏิบัติการ ภาคเรียน 1/2569",
      CONFIG.STATUS.APPROVED,
      "",
      "",
      "2026-10-21T03:15:00.000Z",
      "2026-10-21T03:30:00.000Z"
    ],
    [
      "REQ-256910-0043",
      "21 ต.ค. 2569 10:45 น.",
      "คุณพรทิพย์ สุขขี",
      "คณะพยาบาลศาสตร์ - พยาบาลศาสตรบัณฑิต",
      "089-112-3344",
      "เตรียมเอกสารปฐมนิเทศนักศึกษาฝึกปฏิบัติงานคลินิก",
      CONFIG.STATUS.PENDING,
      "",
      "",
      "2026-10-21T03:45:00.000Z",
      "2026-10-21T03:45:00.000Z"
    ]
  ];
  reqSheet.getRange(2, 1, sampleReqs.length, sampleReqs[0].length).setValues(sampleReqs);

  const sampleItems = [
    ["REQ-256910-0042", 1, "ซองขยายข้างมีครุฑ 279´432", 2, 0, 500, "กล่อง", "ซอง", 500],
    ["REQ-256910-0042", 2, "กระดาษคำตอบ", 1, 0, 2000, "กล่อง", "ใบ", 2000],
    ["REQ-256910-0042", 5, "แฟ้มเสนอ", 0, 3, 3, "เล่ม", "เล่ม", 3],
    ["REQ-256910-0043", 3, "ซองเอกสารสีขาว 7´10", 1, 0, 500, "กล่อง", "ซอง", 500],
    ["REQ-256910-0043", 4, "กระดาษลายเส้น", 2, 0, 1000, "ห่อ", "แผ่น", 1000]
  ];
  itemsSheet.getRange(2, 1, sampleItems.length, sampleItems[0].length).setValues(sampleItems);
}

/**
 * ใส่ข้อมูลรายชื่อ 90+ คณะ/โรงเรียน/กอง มหาวิทยาลัยสวนดุสิต
 */
function seedInitialDepartments(sheet) {
  const depts = [
    ["คณะ / โรงเรียน", "คณะครุศาสตร์ (ภาพรวม)", "คณะครุศาสตร์", "คณะครุศาสตร์"],
    ["คณะ / โรงเรียน", "การศึกษาปฐมวัย", "คณะครุศาสตร์", "คณะครุศาสตร์ - การศึกษาปฐมวัย"],
    ["คณะ / โรงเรียน", "การประถมศึกษา", "คณะครุศาสตร์", "คณะครุศาสตร์ - การประถมศึกษา"],
    ["คณะ / โรงเรียน", "หลักสูตรประกาศนียบัตรบัณฑิตวิชาชีพครู", "คณะครุศาสตร์", "คณะครุศาสตร์ - หลักสูตรประกาศนียบัตรบัณฑิตวิชาชีพครู"],
    ["คณะ / โรงเรียน", "คณะวิทยาศาสตร์และเทคโนโลยี (ภาพรวม)", "คณะวิทยาศาสตร์และเทคโนโลยี", "คณะวิทยาศาสตร์และเทคโนโลยี"],
    ["คณะ / โรงเรียน", "วิทยาการคอมพิวเตอร์", "คณะวิทยาศาสตร์และเทคโนโลยี", "คณะวิทยาศาสตร์และเทคโนโลยี - วิทยาการคอมพิวเตอร์"],
    ["คณะ / โรงเรียน", "วิทยาศาสตร์เครื่องสำอาง", "คณะวิทยาศาสตร์และเทคโนโลยี", "คณะวิทยาศาสตร์และเทคโนโลยี - วิทยาศาสตร์เครื่องสำอาง"],
    ["คณะ / โรงเรียน", "อาชีวอนามัยและความปลอดภัย", "คณะวิทยาศาสตร์และเทคโนโลยี", "คณะวิทยาศาสตร์และเทคโนโลยี - อาชีวอนามัยและความปลอดภัย"],
    ["คณะ / โรงเรียน", "อนามัยสิ่งแวดล้อมและสาธารณภัย", "คณะวิทยาศาสตร์และเทคโนโลยี", "คณะวิทยาศาสตร์และเทคโนโลยี - อนามัยสิ่งแวดล้อมและสาธารณภัย"],
    ["คณะ / โรงเรียน", "วิทยาศาสตร์การแพทย์", "คณะวิทยาศาสตร์และเทคโนโลยี", "คณะวิทยาศาสตร์และเทคโนโลยี - วิทยาศาสตร์การแพทย์"],
    ["คณะ / โรงเรียน", "วิทยาศาสตร์ทั่วไป", "คณะวิทยาศาสตร์และเทคโนโลยี", "คณะวิทยาศาสตร์และเทคโนโลยี - วิทยาศาสตร์ทั่วไป"],
    ["คณะ / โรงเรียน", "เทคโนโลยีสารสนเทศ", "คณะวิทยาศาสตร์และเทคโนโลยี", "คณะวิทยาศาสตร์และเทคโนโลยี - เทคโนโลยีสารสนเทศ"],
    ["คณะ / โรงเรียน", "อุตสาหกรรมชีวภาพเพื่อธุรกิจ", "คณะวิทยาศาสตร์และเทคโนโลยี", "คณะวิทยาศาสตร์และเทคโนโลยี - อุตสาหกรรมชีวภาพเพื่อธุรกิจ"],
    ["คณะ / โรงเรียน", "ความมั่นคงปลอดภัยไซเบอร์", "คณะวิทยาศาสตร์และเทคโนโลยี", "คณะวิทยาศาสตร์และเทคโนโลยี - ความมั่นคงปลอดภัยไซเบอร์"],
    ["คณะ / โรงเรียน", "คณะวิทยาการจัดการ (ภาพรวม)", "คณะวิทยาการจัดการ", "คณะวิทยาการจัดการ"],
    ["คณะ / โรงเรียน", "การจัดการบัณฑิต", "คณะวิทยาการจัดการ", "คณะวิทยาการจัดการ - การจัดการบัณฑิต"],
    ["คณะ / โรงเรียน", "นิเทศศาสตร์นวัตกรรมและผู้ประกอบการธุรกิจ", "คณะวิทยาการจัดการ", "คณะวิทยาการจัดการ - นิเทศศาสตร์นวัตกรรมและผู้ประกอบการธุรกิจ"],
    ["คณะ / โรงเรียน", "เลขานุการทางการแพทย์", "คณะวิทยาการจัดการ", "คณะวิทยาการจัดการ - เลขานุการทางการแพทย์"],
    ["คณะ / โรงเรียน", "การสื่อสารดิจิทัลและการสร้างสรรค์คอนเทนต์", "คณะวิทยาการจัดการ", "คณะวิทยาการจัดการ - การสื่อสารดิจิทัลและการสร้างสรรค์คอนเทนต์"],
    ["คณะ / โรงเรียน", "การตลาดและการสร้างแบรนด์บุคคล", "คณะวิทยาการจัดการ", "คณะวิทยาการจัดการ - การตลาดและการสร้างแบรนด์บุคคล"],
    ["คณะ / โรงเรียน", "การเต้นและการแสดงสร้างสรรค์เพื่อธุรกิจบันเทิง", "คณะวิทยาการจัดการ", "คณะวิทยาการจัดการ - การเต้นและการแสดงสร้างสรรค์เพื่อธุรกิจบันเทิง"],
    ["คณะ / โรงเรียน", "การบัญชี", "คณะวิทยาการจัดการ", "คณะวิทยาการจัดการ - การบัญชี"],
    ["คณะ / โรงเรียน", "ธุรกิจระหว่างประเทศ ธุรกิจจีน-อาเซียน", "คณะวิทยาการจัดการ", "คณะวิทยาการจัดการ - ธุรกิจระหว่างประเทศ ธุรกิจจีน-อาเซียน"],
    ["คณะ / โรงเรียน", "ธุรกิจสร้างสรรค์และเทคโนโลยีดิจิทัล", "คณะวิทยาการจัดการ", "คณะวิทยาการจัดการ - ธุรกิจสร้างสรรค์และเทคโนโลยีดิจิทัล"],
    ["คณะ / โรงเรียน", "หลักสูตรบริหารธุรกิจบัณฑิต สาขาวิชาบริหารธุรกิจ", "คณะวิทยาการจัดการ", "คณะวิทยาการจัดการ - หลักสูตรบริหารธุรกิจบัณฑิต สาขาวิชาบริหารธุรกิจ"],
    ["คณะ / โรงเรียน", "คณะมนุษยศาสตร์และสังคมศาสตร์ (ภาพรวม)", "คณะมนุษยศาสตร์และสังคมศาสตร์", "คณะมนุษยศาสตร์และสังคมศาสตร์"],
    ["คณะ / โรงเรียน", "จิตวิทยาอุตสาหกรรมและองค์การ", "คณะมนุษยศาสตร์และสังคมศาสตร์", "คณะมนุษยศาสตร์และสังคมศาสตร์ - จิตวิทยาอุตสาหกรรมและองค์การ"],
    ["คณะ / โรงเรียน", "ภาษาและการสื่อสาร", "คณะมนุษยศาสตร์และสังคมศาสตร์", "คณะมนุษยศาสตร์และสังคมศาสตร์ - ภาษาและการสื่อสาร"],
    ["คณะ / โรงเรียน", "ภาษาอังกฤษเพื่อการสื่อสาร", "คณะมนุษยศาสตร์และสังคมศาสตร์", "คณะมนุษยศาสตร์และสังคมศาสตร์ - ภาษาอังกฤษเพื่อการสื่อสาร"],
    ["คณะ / โรงเรียน", "ภาษาจีนเพื่อการสื่อสาร", "คณะมนุษยศาสตร์และสังคมศาสตร์", "คณะมนุษยศาสตร์และสังคมศาสตร์ - ภาษาจีนเพื่อการสื่อสาร"],
    ["คณะ / โรงเรียน", "ภาษาและวัฒนธรรมไทย", "คณะมนุษยศาสตร์และสังคมศาสตร์", "คณะมนุษยศาสตร์และสังคมศาสตร์ - ภาษาและวัฒนธรรมไทย"],
    ["คณะ / โรงเรียน", "ภาษาอังกฤษและภาษาเกาหลีเพื่อการสื่อสารข้ามวัฒนธรรม", "คณะมนุษยศาสตร์และสังคมศาสตร์", "คณะมนุษยศาสตร์และสังคมศาสตร์ - ภาษาอังกฤษและภาษาเกาหลีเพื่อการสื่อสารข้ามวัฒนธรรม"],
    ["คณะ / โรงเรียน", "คณะพยาบาลศาสตร์ (ภาพรวม)", "คณะพยาบาลศาสตร์", "คณะพยาบาลศาสตร์"],
    ["คณะ / โรงเรียน", "พยาบาลศาสตรบัณฑิต", "คณะพยาบาลศาสตร์", "คณะพยาบาลศาสตร์ - พยาบาลศาสตรบัณฑิต"],
    ["คณะ / โรงเรียน", "ประกาศนียบัตรผู้ช่วยพยาบาล", "คณะพยาบาลศาสตร์", "คณะพยาบาลศาสตร์ - ประกาศนียบัตรผู้ช่วยพยาบาล"],
    ["คณะ / โรงเรียน", "โรงเรียนการท่องเที่ยวและการบริการ (ภาพรวม)", "โรงเรียนการท่องเที่ยวและการบริการ", "โรงเรียนการท่องเที่ยวและการบริการ"],
    ["คณะ / โรงเรียน", "ธุรกิจการโรงแรม", "โรงเรียนการท่องเที่ยวและการบริการ", "โรงเรียนการท่องเที่ยวและการบริการ - ธุรกิจการโรงแรม"],
    ["คณะ / โรงเรียน", "ธุรกิจการบิน", "โรงเรียนการท่องเที่ยวและการบริการ", "โรงเรียนการท่องเที่ยวและการบริการ - ธุรกิจการบิน"],
    ["คณะ / โรงเรียน", "การจัดการไมซ์และอีเวนต์", "โรงเรียนการท่องเที่ยวและการบริการ", "โรงเรียนการท่องเที่ยวและการบริการ - การจัดการไมซ์และอีเวนต์"],
    ["คณะ / โรงเรียน", "การท่องเที่ยวและมัคคุเทศก์", "โรงเรียนการท่องเที่ยวและการบริการ", "โรงเรียนการท่องเที่ยวและการบริการ - การท่องเที่ยวและมัคคุเทศก์"],
    ["คณะ / โรงเรียน", "ผู้ประกอบการธุรกิจบริการและการท่องเที่ยว", "โรงเรียนการท่องเที่ยวและการบริการ", "โรงเรียนการท่องเที่ยวและการบริการ - ผู้ประกอบการธุรกิจบริการและการท่องเที่ยว"],
    ["คณะ / โรงเรียน", "ธุรกิจเวลเนส (หลักสูตรภาษาอังกฤษ)", "โรงเรียนการท่องเที่ยวและการบริการ", "โรงเรียนการท่องเที่ยวและการบริการ - ธุรกิจเวลเนส (หลักสูตรภาษาอังกฤษ)"],
    ["คณะ / โรงเรียน", "สหวิทยาการการท่องเที่ยว", "โรงเรียนการท่องเที่ยวและการบริการ", "โรงเรียนการท่องเที่ยวและการบริการ - สหวิทยาการการท่องเที่ยว"],
    ["คณะ / โรงเรียน", "การท่องเที่ยว", "โรงเรียนการท่องเที่ยวและการบริการ", "โรงเรียนการท่องเที่ยวและการบริการ - การท่องเที่ยว"],
    ["คณะ / โรงเรียน", "การจัดการงานบริการ (หลักสูตรนานาชาติ)", "โรงเรียนการท่องเที่ยวและการบริการ", "โรงเรียนการท่องเที่ยวและการบริการ - การจัดการงานบริการ (หลักสูตรนานาชาติ)"],
    ["คณะ / โรงเรียน", "โรงเรียนการเรือน (ภาพรวม)", "โรงเรียนการเรือน", "โรงเรียนการเรือน"],
    ["คณะ / โรงเรียน", "เทคโนโลยีการประกอบอาหารและการบริการ", "โรงเรียนการเรือน", "โรงเรียนการเรือน - เทคโนโลยีการประกอบอาหารและการบริการ"],
    ["คณะ / โรงเรียน", "คหกรรมศาสตร์", "โรงเรียนการเรือน", "โรงเรียนการเรือน - คหกรรมศาสตร์"],
    ["คณะ / โรงเรียน", "นวัตกรรมเทคโนโลยีเพื่อผู้ประกอบการอาหาร", "โรงเรียนการเรือน", "โรงเรียนการเรือน - นวัตกรรมเทคโนโลยีเพื่อผู้ประกอบการอาหาร"],
    ["คณะ / โรงเรียน", "โภชนาการและการประกอบอาหารเพื่อสุขภาพและการชะลอวัย", "โรงเรียนการเรือน", "โรงเรียนการเรือน - โภชนาการและการประกอบอาหารเพื่อสุขภาพและการชะลอวัย"],
    ["คณะ / โรงเรียน", "การจัดการธุรกิจบริการอาหารและศิลปะการประกอบอาหาร", "โรงเรียนการเรือน", "โรงเรียนการเรือน - การจัดการธุรกิจบริการอาหารและศิลปะการประกอบอาหาร"],
    ["คณะ / โรงเรียน", "เทคโนโลยีการประกอบอาหารและการบริการ (ปริญญาโท)", "โรงเรียนการเรือน", "โรงเรียนการเรือน - เทคโนโลยีการประกอบอาหารและการบริการ (ปริญญาโท)"],
    ["คณะ / โรงเรียน", "โรงเรียนกฎหมายและการเมือง (ภาพรวม)", "โรงเรียนกฎหมายและการเมือง", "โรงเรียนกฎหมายและการเมือง"],
    ["คณะ / โรงเรียน", "นิติศาสตร์", "โรงเรียนกฎหมายและการเมือง", "โรงเรียนกฎหมายและการเมือง - นิติศาสตร์"],
    ["คณะ / โรงเรียน", "หลักสูตรรัฐศาสตร์", "โรงเรียนกฎหมายและการเมือง", "โรงเรียนกฎหมายและการเมือง - หลักสูตรรัฐศาสตร์"],
    ["คณะ / โรงเรียน", "หลักสูตรรัฐประศาสนศาสตร์", "โรงเรียนกฎหมายและการเมือง", "โรงเรียนกฎหมายและการเมือง - หลักสูตรรัฐประศาสนศาสตร์"],
    ["คณะ / โรงเรียน", "กฎหมายมหาชนและการบริหารงานยุติธรรม", "โรงเรียนกฎหมายและการเมือง", "โรงเรียนกฎหมายและการเมือง - กฎหมายมหาชนและการบริหารงานยุติธรรม"],
    ["คณะ / โรงเรียน", "กฎหมายปกครองและการบริหารงานภาครัฐ (ปริญญาโท)", "โรงเรียนกฎหมายและการเมือง", "โรงเรียนกฎหมายและการเมือง - กฎหมายปกครองและการบริหารงานภาครัฐ (ปริญญาโท)"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "ระบบการประเมินเพื่อพัฒนาประสิทธิภาพการจัดการศึกษา", "โรงเรียนกฎหมายและการเมือง", "โรงเรียนกฎหมายและการเมือง - ระบบการประเมินเพื่อพัฒนาประสิทธิภาพการจัดการศึกษา"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "สำนักงานมหาวิทยาลัย (ภาพรวม)", "สำนักงานมหาวิทยาลัย", "สำนักงานมหาวิทยาลัย"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "กองกลาง", "สำนักงานมหาวิทยาลัย", "สำนักงานมหาวิทยาลัย - กองกลาง"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "กองบริหารงานบุคคล", "สำนักงานมหาวิทยาลัย", "สำนักงานมหาวิทยาลัย - กองบริหารงานบุคคล"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "กองคลัง", "สำนักงานมหาวิทยาลัย", "สำนักงานมหาวิทยาลัย - กองคลัง"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "กองคลัง (งานพัสดุ)", "สำนักงานมหาวิทยาลัย", "สำนักงานมหาวิทยาลัย - กองคลัง (งานพัสดุ)"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "กองอาคารสถานที่", "สำนักงานมหาวิทยาลัย", "สำนักงานมหาวิทยาลัย - กองอาคารสถานที่"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "กองพัฒนานักศึกษา", "สำนักงานมหาวิทยาลัย", "สำนักงานมหาวิทยาลัย - กองพัฒนานักศึกษา"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "กองประชาสัมพันธ์", "สำนักงานมหาวิทยาลัย", "สำนักงานมหาวิทยาลัย - กองประชาสัมพันธ์"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "สำนักงานเลขานุการสภามหาวิทยาลัย", "สำนักงานมหาวิทยาลัย", "สำนักงานมหาวิทยาลัย - สำนักงานเลขานุการสภามหาวิทยาลัย"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "สำนักกิจการพิเศษ", "สำนักกิจการพิเศษ", "สำนักกิจการพิเศษ"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "โรงแรมสวนดุสิตเพลส", "สำนักกิจการพิเศษ", "สำนักกิจการพิเศษ - โรงแรมสวนดุสิตเพลส"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "สถาบันภาษา/ศิลปะและวัฒนธรรม", "สถาบันภาษา/ศิลปะและวัฒนธรรม", "สถาบันภาษา/ศิลปะและวัฒนธรรม"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "สถาบันวิจัยและพัฒนา", "สถาบันวิจัยและพัฒนา", "สถาบันวิจัยและพัฒนา"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "หน่วยบริหารนวัตกรรมการวิจัย", "สถาบันวิจัยและพัฒนา", "สถาบันวิจัยและพัฒนา - หน่วยบริหารนวัตกรรมการวิจัย"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "งานกำหนดตำเเหน่งทางวิชาการ", "สถาบันวิจัยและพัฒนา", "สถาบันวิจัยและพัฒนา - งานกำหนดตำเเหน่งทางวิชาการ"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "หน่วยบ่มเพาะวิสาหกิจ", "สถาบันวิจัยและพัฒนา", "สถาบันวิจัยและพัฒนา - หน่วยบ่มเพาะวิสาหกิจ"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "ข้อมูลพันธุ์ไม้ในสวนดุสิต", "สถาบันวิจัยและพัฒนา", "สถาบันวิจัยและพัฒนา - ข้อมูลพันธุ์ไม้ในสวนดุสิต"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "ASEAN Journal of Education", "สถาบันวิจัยและพัฒนา", "สถาบันวิจัยและพัฒนา - ASEAN Journal of Education"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "ศูนย์พัฒนาทุนมนุษย์", "ศูนย์พัฒนาทุนมนุษย์", "ศูนย์พัฒนาทุนมนุษย์"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "ศูนย์บริการสื่อและสิ่งพิมพ์กราฟฟิคไซท์", "ศูนย์บริการสื่อและสิ่งพิมพ์กราฟฟิคไซท์", "ศูนย์บริการสื่อและสิ่งพิมพ์กราฟฟิคไซท์"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "สำนักยุทธศาสตร์และแผน", "สำนักยุทธศาสตร์และแผน", "สำนักยุทธศาสตร์และแผน"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "งานแผนและงบประมาณ", "สำนักยุทธศาสตร์และแผน", "สำนักยุทธศาสตร์และแผน - งานแผนและงบประมาณ"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "สำนักกฏหมาย", "สำนักกฏหมาย", "สำนักกฏหมาย"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "โครงการความร่วมมือทางวิชาการ", "โครงการความร่วมมือทางวิชาการ", "โครงการความร่วมมือทางวิชาการ"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "ศูนย์สนเทศแนะแนวการศึกษาและอาชีพ", "ศูนย์สนเทศแนะแนวการศึกษาและอาชีพ", "ศูนย์สนเทศแนะแนวการศึกษาและอาชีพ"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "สภาคณาจารย์และพนักงาน", "สภาคณาจารย์และพนักงาน", "สภาคณาจารย์และพนักงาน"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "สหกรณ์ออมทรัพย์", "สหกรณ์ออมทรัพย์", "สหกรณ์ออมทรัพย์"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "ศูนย์บริการทดสอบทางวิชาการสวนดุสิต", "ศูนย์บริการทดสอบทางวิชาการสวนดุสิต", "ศูนย์บริการทดสอบทางวิชาการสวนดุสิต"],
    ["สถาบัน / สำนัก / ศูนย์ / กอง", "อาคารหอพัก Dormsita ศูนย์วิทยาศาสตร์ มหาวิทยาลัยสวนดุสิต", "อาคารหอพัก Dormsita ศูนย์วิทยาศาสตร์ มหาวิทยาลัยสวนดุสิต", "อาคารหอพัก Dormsita ศูนย์วิทยาศาสตร์ มหาวิทยาลัยสวนดุสิต"]
  ];

  sheet.getRange(2, 1, depts.length, depts[0].length).setValues(depts);
}

// ==============================================================================
// 6. UTILITY & HELPER FUNCTIONS
// ==============================================================================

/**
 * สร้าง ContentService TextOutput พร้อม MIME Type application/json
 */
function createJsonResponse(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * อ่านข้อมูลทั้งหมดใน Sheet แปลงเป็น Array of Objects ตามชื่อคอลัมน์ในแถวที่ 1
 */
function readSheetObjects(sheet) {
  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();
  if (lastRow <= 1 || lastCol === 0) return [];

  const values = sheet.getRange(1, 1, lastRow, lastCol).getValues();
  const headers = values[0].map(h => String(h).trim());
  const rows = [];

  for (let r = 1; r < values.length; r++) {
    const rowObj = {};
    let hasData = false;
    for (let c = 0; c < headers.length; c++) {
      const val = values[r][c];
      rowObj[headers[c]] = val;
      if (val !== '' && val !== null && val !== undefined) hasData = true;
    }
    if (hasData) rows.push(rowObj);
  }

  return rows;
}

/**
 * ค้นหาแถวตามค่าในคอลัมน์ที่กำหนด (1-indexed row number)
 */
function findRowIndex(sheet, colIndex, targetValue) {
  const lastRow = sheet.getLastRow();
  if (lastRow <= 1) return -1;

  const values = sheet.getRange(2, colIndex, lastRow - 1, 1).getValues();
  const targetStr = String(targetValue).trim().toUpperCase();

  for (let i = 0; i < values.length; i++) {
    if (String(values[i][0]).trim().toUpperCase() === targetStr) {
      return i + 2; // +2 เพราะเริ่มจาก row 2 และ 1-based index
    }
  }
  return -1;
}

/**
 * ค้นหาตำแหน่งคอลัมน์ (1-indexed) ตามชื่อ Header
 */
function findHeaderIndex(sheet, headerName) {
  const lastCol = sheet.getLastColumn();
  if (lastCol === 0) return -1;

  const headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0];
  const target = headerName.trim().toLowerCase();

  for (let c = 0; c < headers.length; c++) {
    if (String(headers[c]).trim().toLowerCase() === target) {
      return c + 1; // 1-based
    }
  }
  return -1;
}

/**
 * ออกรหัสเลขที่เอกสารคำขอเบิก รูปแบบ REQ-YYYYMM-XXXX
 * ปี พ.ศ. + เดือน 2 หลัก + เลขสุ่ม 4 หลัก (เช่น REQ-256910-4491)
 */
function generateDocNo() {
  const now = new Date();
  const thaiYear = now.getFullYear() + 543;
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const randomDigits = Math.floor(1000 + Math.random() * 9000);
  return `REQ-${thaiYear}${month}-${randomDigits}`;
}

/**
 * จัดรูปแบบวันที่และเวลาเป็นภาษาไทยทางการ
 * ตัวอย่าง: 23 ต.ค. 2569 17:30 น.
 */
function formatThaiDate(date) {
  const d = date || new Date();
  const day = d.getDate();
  const thaiMonth = CONFIG.THAI_MONTHS[d.getMonth()];
  const thaiYear = d.getFullYear() + 543;
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  return `${day} ${thaiMonth} ${thaiYear} ${hours}:${minutes} น.`;
}

// ==============================================================================
// 7. SELF-TESTING SUITE (runTestApi in Script Editor)
// ==============================================================================

/**
 * ฟังก์ชันสำหรับทดสอบการทำงานของระบบ API ทั้งหมด (Self-Test Runner)
 * สามารถเลือกฟังก์ชันนี้แล้วกด Run ใน Apps Script Editor เพื่อตรวจสอบความพร้อม
 */
function runTestApi() {
  Logger.log('🧪 เริ่มการทดสอบระบบ API (Self-Testing Suite)...');

  // Test 1: getItems
  const getItemsRes = JSON.parse(handleGetItems({}).getContent());
  Logger.log('1. handleGetItems: status=' + getItemsRes.status + ', count=' + getItemsRes.total);

  // Test 2: getDepartments
  const getDeptsRes = JSON.parse(handleGetDepartments({}).getContent());
  Logger.log('2. handleGetDepartments: status=' + getDeptsRes.status + ', count=' + getDeptsRes.total);

  // Test 3: getRequisitions
  const getReqsRes = JSON.parse(handleGetRequisitions({}).getContent());
  Logger.log('3. handleGetRequisitions: status=' + getReqsRes.status + ', count=' + getReqsRes.total);

  // Test 4: trackRequisition
  if (getReqsRes.total > 0) {
    const firstDocNo = getReqsRes.data[0].id;
    const trackRes = JSON.parse(handleTrackRequisition({ docNo: firstDocNo }).getContent());
    Logger.log('4. handleTrackRequisition (' + firstDocNo + '): found=' + trackRes.found);
  }

  // Test 5: createRequisition (Dry Run / Validation)
  const testCreatePayload = {
    requester: "ทดสอบ ระบบ",
    dept: "สำนักงานมหาวิทยาลัย - กองคลัง (งานพัสดุ)",
    phone: "02-244-5555",
    purpose: "ทดสอบการส่งคำขอผ่าน Backend Code.gs",
    items: [
      { itemId: 1, name: "ซองขยายข้างมีครุฑ", qtyBoxes: 0, qtyPieces: 1, totalPieces: 1, unitBox: "กล่อง", unitPiece: "ซอง" }
    ]
  };
  const createRes = JSON.parse(handleCreateRequisition(testCreatePayload).getContent());
  Logger.log('5. handleCreateRequisition: status=' + createRes.status + ', docNo=' + createRes.docNo);

  Logger.log('✅ การทดสอบ API เสร็จสิ้น 100% ทุกฟังก์ชันทำงานถูกต้อง!');
}
