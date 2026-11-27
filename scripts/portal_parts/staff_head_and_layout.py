"""
Staff Portal HTML Head, CSS Styles, Login Card & Dashboard Layout (scripts/portal_parts/staff_head_and_layout.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

STAFF_HEAD_AND_LAYOUT = r'''<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ระบบจัดการวัสดุสำนักงานออนไลน์ | มหาวิทยาลัยสวนดุสิต</title>
  
  <!-- PWA & Mobile Icons -->
  <meta name="theme-color" content="#1e40af">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="ระบบจัดการวัสดุสำนักงานออนไลน์">
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
    <div style="text-align: center; margin-bottom: 1.4rem;">
      <img src="assets/logo_sdu.png" alt="มหาวิทยาลัยสวนดุสิต" style="height: 64px; width: auto; object-fit: contain; margin-bottom: 0.65rem; filter: drop-shadow(0 2px 6px rgba(0,0,0,0.1));">
      <h2 id="staffLoginTitle" style="font-size: 1.22rem; font-weight: 700; color: var(--neutral-900);">เข้าสู่ระบบจัดการวัสดุสำนักงานออนไลน์</h2>
      <p style="font-size: 0.825rem; color: var(--neutral-600); margin-top: 4px;">ฝ่ายพัสดุและคลังสินค้ากลาง มหาวิทยาลัยสวนดุสิต</p>
      <div id="staffLoginBadge" style="margin-top: 0.65rem; display: inline-flex; align-items: center; gap: 6px; background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; padding: 4px 12px; border-radius: 999px; font-size: 0.75rem; font-weight: 600;">
        <svg class="svg-icon" style="width: 14px; height: 14px;" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/></svg>
        <span>กรอกชื่อผู้ใช้งานและรหัสผ่าน ระบบจะตรวจสอบบทบาทให้อัตโนมัติ</span>
      </div>
    </div>

    <form onsubmit="handleStaffLogin(event)" style="display: flex; flex-direction: column; gap: 1rem;">
      <div class="form-group">
        <label><svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> ชื่อผู้ใช้งาน</label>
        <input type="text" id="loginUsername" class="form-control" placeholder="กรอกชื่อผู้ใช้งานของท่าน" required autocomplete="username">
      </div>
      <div class="form-group">
        <label><svg class="svg-icon" viewBox="0 0 24 24"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg> รหัสผ่าน</label>
        <input type="password" id="loginPassword" class="form-control" placeholder="กรอกรหัสผ่านของท่าน" required autocomplete="current-password">
      </div>
      <button type="submit" id="btnStaffLoginSubmit" class="btn btn-primary" style="justify-content: center; padding: 0.78rem; margin-top: 0.35rem;">
        <span id="btnStaffLoginSubmitText">เข้าสู่ระบบ</span>
      </button>
    </form>

    <div style="margin-top: 1.1rem; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem 0.9rem; font-size: 0.775rem; color: #475569; line-height: 1.55;">
      <div style="font-weight: 600; color: #1e3a8a; margin-bottom: 4px;">ระบบตรวจสอบสิทธิ์อัตโนมัติตามบัญชี:</div>
      <div>• เจ้าหน้าที่พัสดุ, หัวหน้าหน่วยงาน, และผู้ดูแลระบบจะเข้าสู่หน้าจัดการตามสิทธิ์ทันที</div>
      <div>• บัญชีผู้ขอเบิกพัสดุจะถูกนำไปยังหน้าขอเบิกพัสดุโดยอัตโนมัติ</div>
    </div>

    <div style="margin-top: 1.25rem; text-align: center; border-top: 1px solid var(--neutral-200); padding-top: 1rem; display: flex; justify-content: center; gap: 0.75rem; align-items: center;">
      <a href="portal.html" style="font-size: 0.85rem; color: var(--primary); text-decoration: none; font-weight: 500;">
        ศูนย์กลางพอร์ทัล
      </a>
      <span style="color: var(--neutral-300);">|</span>
      <a href="index.html" style="font-size: 0.85rem; color: var(--neutral-600); text-decoration: none;">
        หน้าขอเบิกพัสดุ
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
            <h1>ระบบจัดการวัสดุสำนักงานออนไลน์</h1>
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
          <button type="button" id="btnSwitchToRequesterPortal" class="btn btn-outline" onclick="switchToRequesterPortal()" style="font-size: 0.8rem; padding: 0.42rem 0.8rem; border-color: #93c5fd; color: #1e40af; background: #eff6ff; font-weight: 600; display: inline-flex; align-items: center; gap: 5px;">
            <svg class="svg-icon svg-icon-sm" viewBox="0 0 24 24"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg> ขอเบิกพัสดุ
          </button>
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
            <select id="staffReqMonthFilter" class="form-control" style="width: auto; min-width: 190px;" onchange="handleStaffReqMonthChange()">
              <option value="ALL">ดูทุกเดือนย้อนหลัง</option>
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
            <select id="analyticsMonthSelect" class="form-control" style="width: auto; min-width: 210px;" onchange="handleAnalyticsMonthChange()">
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
          <div class="metric-card" id="analyticsTotalReqsCard" onclick="openMonthlyRequisitionsModal()" style="cursor: pointer;" title="คลิกเพื่อดูรายการคำขอเบิกทั้งหมดในเดือน">
            <div class="metric-header"><svg class="svg-icon" viewBox="0 0 24 24"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg> คำขอเบิกทั้งหมดในเดือน</div>
            <span class="metric-val" id="analyticsMetricTotalReqs">0 <small style="font-size: 0.85rem; font-weight: normal; color: var(--neutral-400);">คำขอ</small></span>
            <div style="font-size: 0.75rem; color: var(--neutral-500); margin-top: 4px;" id="analyticsReqBreakdown">รอคัดกรอง 0 | รออนุมัติ 0 | สำเร็จ 0</div>
            <div style="font-size: 0.76rem; font-weight: 600; color: var(--primary); margin-top: 8px; display: inline-flex; align-items: center; gap: 4px;">
              <svg class="svg-icon" viewBox="0 0 24 24" style="width: 14px; height: 14px;"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg> คลิกเพื่อดูรายการคำขอทั้งหมด
            </div>
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

        <!-- Monthly Requisitions List Card -->
        <div id="analyticsRequisitionsCard" style="background: white; border-radius: var(--radius); border: 1px solid var(--neutral-200); padding: 1.25rem; box-shadow: var(--shadow-sm); margin-bottom: 1.5rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem;">
            <div>
              <h3 style="font-size: 1rem; font-weight: 700; color: #1e3a8a; display: flex; align-items: center; gap: 6px;">
                <svg class="svg-icon" viewBox="0 0 24 24"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg> รายการคำขอเบิกทั้งหมดในเดือน
              </h3>
              <p style="font-size: 0.825rem; color: var(--neutral-600); margin-top: 2px;">ตรวจสอบเลขที่เอกสาร ผู้ขอเบิก รายการพัสดุ สถานะ และเปิดดูใบขอเบิกทางการ (PDF) ของงวดที่เลือก</p>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
              <span id="analyticsReqsListCount" style="font-size: 0.85rem; color: var(--neutral-500); font-weight: 600;"></span>
              <button type="button" class="btn btn-outline" style="font-size: 0.8rem; padding: 0.35rem 0.75rem;" onclick="openMonthlyRequisitionsModal()">
                <svg class="svg-icon" viewBox="0 0 24 24" style="width: 14px; height: 14px;"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg> เปิดดูแบบเต็มจอ
              </button>
            </div>
          </div>

          <div style="display: flex; gap: 0.75rem; margin-bottom: 1rem; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 240px;">
              <input type="text" id="analyticsReqSearchInput" class="form-control"
                     placeholder="พิมพ์ค้นหาเลขที่คำขอ, ชื่อผู้ขอเบิก, หน่วยงาน, วัตถุประสงค์ หรือชื่อพัสดุ..."
                     oninput="renderAnalyticsRequisitionsTable()">
            </div>
            <div style="min-width: 220px;">
              <select id="analyticsReqStatusFilter" class="form-control" onchange="renderAnalyticsRequisitionsTable()">
                <option value="ALL">ทุกสถานะคำขอทั้งหมด</option>
                <option value="PENDING">รอคัดกรอง (PENDING)</option>
                <option value="VERIFIED">รอหัวหน้าอนุมัติ (VERIFIED)</option>
                <option value="APPROVED">อนุมัติแล้ว รอรับของ (APPROVED)</option>
                <option value="COMPLETED">จ่ายสำเร็จแล้ว (COMPLETED)</option>
                <option value="REJECTED">ไม่อนุมัติ / ยกเลิก (REJECTED)</option>
              </select>
            </div>
          </div>

          <div style="overflow-x: auto; max-height: 420px; overflow-y: auto;">
            <table class="req-table" style="font-size: 0.86rem;">
              <thead>
                <tr>
                  <th style="min-width: 145px;">เลขที่คำขอ / วันที่</th>
                  <th style="min-width: 185px;">ผู้ขอเบิก / หน่วยงาน</th>
                  <th style="min-width: 220px;">รายการพัสดุที่ขอเบิก</th>
                  <th style="min-width: 155px;">วัตถุประสงค์</th>
                  <th style="width: 135px; text-align: center;">สถานะ</th>
                  <th style="width: 170px; text-align: right;">การดำเนินการ</th>
                </tr>
              </thead>
              <tbody id="analyticsReqsTbody">
                <!-- Rendered by JS -->
              </tbody>
            </table>
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
                <td><strong>ชื่อผู้ขอเบิก:</strong> <span id="pdfRequester">สมชัย จารุธนกิจพานิช</span></td>
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
                  <div>( <span id="pdfSignRequester">สมชัย จารุธนกิจพานิช</span> )</div>
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
                  <div>( <span id="pdfReceiverName">สมชัย จารุธนกิจพานิช</span> )</div>
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
      © 2569 ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต v__SYSTEM_VERSION__ | ใช้งานเฉพาะภายในสถาบัน
    </div>
  </footer>

  <!-- Scripts -->
'''
