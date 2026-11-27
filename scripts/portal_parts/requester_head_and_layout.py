"""
Requester Portal HTML Head, CSS Styles & Body Layout (scripts/portal_parts/requester_head_and_layout.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

REQUESTER_HEAD_AND_LAYOUT = r'''<!DOCTYPE html>
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

  <!-- 1. AUTO-ROLE LOGIN SCREEN (SHOWN WHEN NOT LOGGED IN) -->
  <div id="requesterLoginScreen" class="login-wrapper">
    <div class="login-card" style="max-width: 440px;">
      <div class="login-header" style="padding: 1.85rem 1.75rem 1.25rem 1.75rem;">
        <img src="assets/logo_sdu.png" alt="มหาวิทยาลัยสวนดุสิต" style="height: 62px; margin-bottom: 0.65rem; object-fit: contain;">
        <h2 id="loginRoleTitle" style="font-size: 1.22rem; font-weight: 700; color: var(--neutral-900); margin-bottom: 0.25rem;">เข้าสู่ระบบจัดการวัสดุสำนักงานออนไลน์</h2>
        <p style="font-size: 0.825rem; color: var(--neutral-500);">มหาวิทยาลัยสวนดุสิต | สำนักส่งเสริมวิชาการและงานทะเบียน</p>
        <div id="loginRoleBadge" style="margin-top: 0.65rem; display: inline-flex; align-items: center; gap: 6px; background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; padding: 4px 12px; border-radius: 999px; font-size: 0.75rem; font-weight: 600;">
          <svg class="svg-icon" style="width: 14px; height: 14px;" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/></svg>
          <span>กรอกชื่อผู้ใช้งานและรหัสผ่าน ระบบจะเข้าตามสิทธิ์อัตโนมัติ</span>
        </div>
      </div>
      <div class="login-body" style="padding: 1.25rem 1.75rem 1.75rem 1.75rem;">
        <form id="requesterLoginForm" onsubmit="handleRequesterLogin(event)">
          <div class="login-input-group">
            <label for="loginUsername" id="loginUsernameLabel">ชื่อผู้ใช้งาน</label>
            <div class="login-input-wrapper">
              <span class="input-icon"><svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></span>
              <input type="text" id="loginUsername" class="login-input" placeholder="กรอกชื่อผู้ใช้งานของท่าน" required autocomplete="username">
            </div>
          </div>
          <div class="login-input-group">
            <label for="loginPassword">รหัสผ่าน</label>
            <div class="login-input-wrapper">
              <span class="input-icon"><svg class="svg-icon" viewBox="0 0 24 24"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></span>
              <input type="password" id="loginPassword" class="login-input" placeholder="กรอกรหัสผ่านของท่าน" required autocomplete="current-password">
            </div>
          </div>
          <button type="submit" class="btn-login" id="btnLoginSubmit">
            <svg class="svg-icon" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <span id="btnLoginSubmitText">เข้าสู่ระบบ</span>
          </button>
        </form>

        <div class="login-notice-box" style="margin-top: 1rem;">
          <div style="font-weight: 600; color: var(--neutral-800); margin-bottom: 4px; display: flex; align-items: center; gap: 4px;">
            <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="16" y2="12"/><line x1="12" x2="12.01" y1="8" y2="8"/></svg> การเข้าสู่ระบบอัตโนมัติตามสิทธิ์
          </div>
          <div id="loginNoticeRoleHint" style="font-size: 0.775rem; line-height: 1.5;">
            ระบบจะตรวจสอบบทบาทจากบัญชีของท่านโดยอัตโนมัติ หรือกลับไปที่ <a href="portal.html" style="color: var(--primary); font-weight: 600; text-decoration: none;">ศูนย์กลางพอร์ทัล</a>
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
            <h1>ระบบจัดการวัสดุสำนักงานออนไลน์</h1>
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

          <button class="btn btn-outline" id="btnSwitchToStaffPortal" onclick="switchToStaffPortal()" style="display: none; align-items: center; gap: 0.4rem; font-size: 0.8rem; padding: 0.45rem 0.85rem; border-color: #c4b5fd; color: #5b21b6; background: #f5f3ff; font-weight: 600;">
            <svg class="svg-icon svg-icon-sm" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/></svg>
            <span id="btnSwitchToStaffPortalText">หน้าอนุมัติ</span>
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
            <select id="myReqsMonthSelect" class="form-control" style="width: auto; min-width: 175px;" onchange="handleMyReqsSearch()">
              <option value="ALL">ทุกเดือนย้อนหลัง</option>
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
          <svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="16" y2="12"/><line x1="12" x2="12.01" y1="8" y2="8"/></svg> ข้อมูลอัปเดตแบบเรียลไทม์ ซิงค์กับระบบจัดการวัสดุสำนักงานออนไลน์
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
      © 2569 ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต v__SYSTEM_VERSION__ | ใช้งานเฉพาะภายในสถาบัน
    </div>
  </footer>
  </div>

  <!-- Scripts -->
'''
