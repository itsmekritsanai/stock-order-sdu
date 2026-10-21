import json

# Vector icons SVG dictionary for clean inline usage
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
    "edit": '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>'
}

# Official Vector Emblem for PDF (SVG)
pdf_seal_svg = '''
<svg class="pdf-vector-seal" viewBox="0 0 100 100" width="70" height="70" fill="none" stroke="#991b1b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="50" cy="50" r="45" stroke-dasharray="3 3"/>
  <circle cx="50" cy="50" r="40"/>
  <path d="M50 18 L70 32 L70 56 L50 78 L30 56 L30 32 Z" fill="#fef2f2"/>
  <line x1="38" x2="62" y1="46" y2="46"/>
  <line x1="42" x2="58" y1="52" y2="52"/>
  <line x1="46" x2="54" y1="58" y2="58"/>
  <polygon points="50,26 54,36 64,36 56,42 59,52 50,46 41,52 44,42 36,36 46,36" fill="#991b1b" stroke="none"/>
</svg>
'''

html_content = f'''<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ระบบเบิกพัสดุและคลังพัสดุดิจิทัล (e-Inventory & Requisition)</title>
  <!-- Google Fonts: Prompt for modern UI, Sarabun for official doc/text -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&family=Sarabun:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  
  <style>
    :root {{
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
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Prompt', 'Sarabun', sans-serif;
      background-color: var(--neutral-50);
      color: var(--neutral-800);
      line-height: 1.5;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    /* Clean Vector Icons Style */
    .svg-icon {{
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
    }}

    .svg-icon-lg {{
      width: 1.6rem;
      height: 1.6rem;
    }}

    .svg-icon-sm {{
      width: 0.95rem;
      height: 0.95rem;
    }}

    /* Top Navigation */
    header {{
      background: white;
      border-bottom: 1px solid var(--neutral-200);
      position: sticky;
      top: 0;
      z-index: 40;
      box-shadow: var(--shadow-sm);
    }}

    .nav-container {{
      max-width: 1380px;
      margin: 0 auto;
      padding: 0.75rem 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .brand-icon {{
      width: 42px;
      height: 42px;
      background: linear-gradient(135deg, var(--primary), #3b82f6);
      color: white;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25);
    }}

    .brand-text h1 {{
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--neutral-900);
      line-height: 1.2;
    }}

    .brand-text p {{
      font-size: 0.8rem;
      color: var(--neutral-400);
    }}

    /* View Switcher Tabs */
    .view-switcher {{
      display: flex;
      background: var(--neutral-100);
      padding: 4px;
      border-radius: 10px;
      gap: 4px;
    }}

    .view-btn {{
      padding: 0.5rem 1rem;
      border: none;
      background: transparent;
      font-family: inherit;
      font-size: 0.875rem;
      font-weight: 500;
      color: var(--neutral-600);
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.2s ease;
    }}

    .view-btn:hover {{
      color: var(--neutral-900);
    }}

    .view-btn.active {{
      background: white;
      color: var(--primary);
      font-weight: 600;
      box-shadow: var(--shadow-sm);
    }}

    .cart-trigger {{
      position: relative;
      background: var(--primary);
      color: white;
      border: none;
      border-radius: 8px;
      padding: 0.5rem 1.1rem;
      font-family: inherit;
      font-weight: 500;
      font-size: 0.875rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: background 0.2s;
    }}

    .cart-trigger:hover {{
      background: var(--primary-hover);
    }}

    .cart-badge {{
      background: #ef4444;
      color: white;
      font-size: 0.75rem;
      font-weight: 700;
      padding: 1px 7px;
      border-radius: 999px;
    }}

    /* Main Container */
    main {{
      max-width: 1380px;
      margin: 1.5rem auto;
      padding: 0 1.5rem;
      flex: 1;
      width: 100%;
    }}

    /* Sections / Views */
    .view-content {{
      display: none;
    }}

    .view-content.active {{
      display: block;
      animation: fadeIn 0.25s ease-out;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Requester Info Bar */
    .requester-bar {{
      background: white;
      border: 1px solid var(--neutral-200);
      border-radius: var(--radius);
      padding: 1.25rem 1.5rem;
      margin-bottom: 1.5rem;
      box-shadow: var(--shadow-sm);
      display: grid;
      grid-template-columns: 2fr 1fr 1fr;
      gap: 1.25rem;
      align-items: flex-end;
    }}

    @media (max-width: 900px) {{
      .requester-bar {{
        grid-template-columns: 1fr;
      }}
    }}

    .form-group {{
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
    }}

    .form-group label {{
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--neutral-700);
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .form-control {{
      padding: 0.6rem 0.85rem;
      border: 1px solid var(--neutral-300);
      border-radius: 8px;
      font-family: inherit;
      font-size: 0.9rem;
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
      background: white;
    }}

    .form-control:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
    }}

    /* ================================================= */
    /* SEARCHABLE COMBOBOX FOR DEPARTMENTS              */
    /* ================================================= */
    .custom-combobox-wrapper {{
      position: relative;
    }}

    .combobox-control {{
      position: relative;
      display: flex;
      align-items: center;
    }}

    .combobox-input {{
      width: 100%;
      padding-right: 2.4rem;
      cursor: text;
    }}

    .combobox-toggle-btn {{
      position: absolute;
      right: 0.5rem;
      background: none;
      border: none;
      color: var(--neutral-400);
      cursor: pointer;
      padding: 4px;
      display: flex;
      align-items: center;
      transition: transform 0.2s;
    }}

    .combobox-control.open .combobox-toggle-btn {{
      transform: rotate(180deg);
    }}

    .combobox-dropdown {{
      position: absolute;
      top: calc(100% + 4px);
      left: 0;
      right: 0;
      background: white;
      border: 1px solid var(--neutral-300);
      border-radius: 8px;
      max-height: 310px;
      overflow-y: auto;
      box-shadow: var(--shadow-lg);
      z-index: 60;
      display: none;
    }}

    .combobox-dropdown.open {{
      display: block;
      animation: fadeIn 0.15s ease-out;
    }}

    .combobox-group-title {{
      padding: 8px 12px 4px 12px;
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--primary);
      background: var(--neutral-50);
      border-top: 1px solid var(--neutral-200);
      border-bottom: 1px solid var(--neutral-200);
      position: sticky;
      top: 0;
      z-index: 2;
    }}

    .combobox-group-title:first-child {{
      border-top: none;
    }}

    .combobox-item {{
      padding: 8px 14px;
      font-size: 0.875rem;
      color: var(--neutral-800);
      cursor: pointer;
      transition: background 0.15s;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .combobox-item:hover, .combobox-item.focused {{
      background: var(--primary-light);
      color: var(--primary);
    }}

    .combobox-item.selected {{
      background: #eff6ff;
      font-weight: 600;
      color: var(--primary);
    }}

    .combobox-item-sub {{
      padding-left: 28px;
      color: var(--neutral-600);
      font-size: 0.825rem;
      border-left: 2px solid var(--neutral-200);
      margin-left: 14px;
    }}

    .combobox-item-sub:hover {{
      border-left-color: var(--primary);
    }}

    .combobox-no-results {{
      padding: 1.25rem 1rem;
      text-align: center;
      color: var(--neutral-400);
      font-size: 0.85rem;
    }}

    /* Search & Filter Bar */
    .search-filter-bar {{
      display: flex;
      gap: 1rem;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
    }}

    .search-box-wrapper {{
      flex: 1;
      min-width: 300px;
      position: relative;
    }}

    .search-input {{
      width: 100%;
      padding: 0.75rem 1rem 0.75rem 2.75rem;
      border: 1px solid var(--neutral-300);
      border-radius: 10px;
      font-family: inherit;
      font-size: 0.95rem;
      background: white;
      box-shadow: var(--shadow-sm);
      outline: none;
      transition: all 0.2s;
    }}

    .search-input:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
    }}

    .search-icon {{
      position: absolute;
      left: 1rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--neutral-400);
      pointer-events: none;
      display: flex;
      align-items: center;
    }}

    .category-pills {{
      display: flex;
      gap: 0.5rem;
      overflow-x: auto;
      align-items: center;
      padding-bottom: 4px;
    }}

    .pill-btn {{
      padding: 0.5rem 1rem;
      background: white;
      border: 1px solid var(--neutral-200);
      border-radius: 999px;
      font-family: inherit;
      font-size: 0.825rem;
      font-weight: 500;
      color: var(--neutral-600);
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s;
    }}

    .pill-btn:hover {{
      border-color: var(--neutral-300);
      background: var(--neutral-100);
    }}

    .pill-btn.active {{
      background: var(--primary);
      color: white;
      border-color: var(--primary);
      box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
    }}

    /* Catalog Grid */
    .catalog-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
      gap: 1.25rem;
    }}

    .item-card {{
      background: white;
      border: 1px solid var(--neutral-200);
      border-radius: var(--radius);
      overflow: hidden;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      transition: transform 0.2s, box-shadow 0.2s;
      position: relative;
    }}

    .item-card:hover {{
      transform: translateY(-3px);
      box-shadow: var(--shadow-md);
      border-color: var(--primary-border);
    }}

    .item-image-wrapper {{
      height: 175px;
      background: var(--neutral-100);
      position: relative;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .item-img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.3s ease;
    }}

    .item-card:hover .item-img {{
      transform: scale(1.03);
    }}

    .image-toggle-pills {{
      position: absolute;
      bottom: 8px;
      left: 8px;
      display: flex;
      gap: 4px;
      background: rgba(15, 23, 42, 0.75);
      padding: 3px;
      border-radius: 6px;
      backdrop-filter: blur(4px);
    }}

    .img-pill-btn {{
      background: transparent;
      border: none;
      color: white;
      font-family: inherit;
      font-size: 0.675rem;
      padding: 2px 6px;
      border-radius: 4px;
      cursor: pointer;
      opacity: 0.8;
      transition: all 0.2s;
    }}

    .img-pill-btn.active {{
      background: var(--primary);
      opacity: 1;
      font-weight: 600;
    }}

    .card-body {{
      padding: 1.15rem;
      display: flex;
      flex-direction: column;
      flex: 1;
    }}

    .item-title {{
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--neutral-900);
      line-height: 1.4;
      margin-bottom: 0.5rem;
      min-height: 2.8rem;
    }}

    .ratio-badge {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 0.75rem;
      color: var(--neutral-600);
      background: var(--neutral-100);
      padding: 4px 8px;
      border-radius: 6px;
      margin-bottom: 0.75rem;
      width: fit-content;
    }}

    .stock-info {{
      background: var(--primary-light);
      border: 1px solid var(--primary-border);
      border-radius: 8px;
      padding: 0.5rem 0.75rem;
      margin-bottom: 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .stock-label {{
      font-size: 0.75rem;
      color: var(--primary);
      font-weight: 500;
    }}

    .stock-value {{
      font-size: 0.875rem;
      font-weight: 700;
      color: var(--primary);
    }}

    .card-actions {{
      margin-top: auto;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
    }}

    .qty-inputs {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.5rem;
    }}

    .qty-col label {{
      font-size: 0.7rem;
      color: var(--neutral-600);
      display: block;
      margin-bottom: 2px;
    }}

    .qty-input {{
      width: 100%;
      padding: 0.45rem;
      border: 1px solid var(--neutral-300);
      border-radius: 6px;
      font-family: inherit;
      font-size: 0.85rem;
      text-align: center;
    }}

    .btn-add-cart {{
      width: 100%;
      background: var(--primary);
      color: white;
      border: none;
      border-radius: 8px;
      padding: 0.6rem;
      font-family: inherit;
      font-size: 0.875rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      transition: background 0.2s, transform 0.1s;
    }}

    .btn-add-cart:hover {{
      background: var(--primary-hover);
    }}

    .btn-add-cart:active {{
      transform: scale(0.98);
    }}

    /* Cart Drawer / Slide-Over */
    .cart-drawer-overlay {{
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.5);
      backdrop-filter: blur(2px);
      z-index: 50;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s;
    }}

    .cart-drawer-overlay.open {{
      opacity: 1;
      pointer-events: auto;
    }}

    .cart-drawer {{
      position: fixed;
      top: 0;
      right: 0;
      bottom: 0;
      width: 440px;
      max-width: 90vw;
      background: white;
      box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
      z-index: 51;
      transform: translateX(100%);
      transition: transform 0.3s ease-out;
      display: flex;
      flex-direction: column;
    }}

    .cart-drawer-overlay.open .cart-drawer {{
      transform: translateX(0);
    }}

    .cart-header {{
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid var(--neutral-200);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .cart-header h3 {{
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--neutral-900);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .close-btn {{
      background: none;
      border: none;
      color: var(--neutral-400);
      cursor: pointer;
      padding: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 6px;
    }}

    .close-btn:hover {{
      color: var(--neutral-800);
      background: var(--neutral-100);
    }}

    .cart-items-list {{
      flex: 1;
      overflow-y: auto;
      padding: 1rem 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }}

    .cart-item-card {{
      background: var(--neutral-50);
      border: 1px solid var(--neutral-200);
      border-radius: 8px;
      padding: 0.85rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 0.75rem;
    }}

    .cart-item-details h4 {{
      font-size: 0.875rem;
      font-weight: 600;
      color: var(--neutral-900);
      margin-bottom: 0.25rem;
    }}

    .cart-item-qty {{
      font-size: 0.8rem;
      color: var(--neutral-600);
    }}

    .cart-item-remove {{
      background: none;
      border: none;
      color: var(--danger);
      cursor: pointer;
      padding: 4px;
      opacity: 0.7;
      display: flex;
      align-items: center;
    }}

    .cart-item-remove:hover {{
      opacity: 1;
    }}

    .cart-footer {{
      padding: 1.25rem 1.5rem;
      border-top: 1px solid var(--neutral-200);
      background: white;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }}

    .btn-submit-requisition {{
      width: 100%;
      background: var(--accent);
      color: white;
      border: none;
      border-radius: 8px;
      padding: 0.85rem;
      font-family: inherit;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      box-shadow: 0 4px 10px rgba(5, 150, 105, 0.25);
      transition: background 0.2s;
    }}

    .btn-submit-requisition:hover {{
      background: var(--accent-hover);
    }}

    /* Staff / Management View */
    .dashboard-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
      gap: 1rem;
    }}

    .dashboard-header h2 {{
      font-size: 1.35rem;
      font-weight: 700;
      color: var(--neutral-900);
    }}

    .status-tabs {{
      display: flex;
      gap: 0.5rem;
      background: var(--neutral-100);
      padding: 4px;
      border-radius: 8px;
    }}

    .status-tab {{
      padding: 0.45rem 1rem;
      border: none;
      background: transparent;
      font-family: inherit;
      font-size: 0.85rem;
      font-weight: 500;
      color: var(--neutral-600);
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .status-tab.active {{
      background: white;
      color: var(--primary);
      font-weight: 600;
      box-shadow: var(--shadow-sm);
    }}

    .count-tag {{
      font-size: 0.7rem;
      padding: 1px 6px;
      border-radius: 999px;
      background: var(--neutral-200);
      color: var(--neutral-700);
    }}

    .status-tab.active .count-tag {{
      background: var(--primary-light);
      color: var(--primary);
    }}

    .requisition-card {{
      background: white;
      border: 1px solid var(--neutral-200);
      border-radius: var(--radius);
      padding: 1.25rem 1.5rem;
      margin-bottom: 1rem;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      gap: 1rem;
      transition: border-color 0.2s;
    }}

    .requisition-card:hover {{
      border-color: var(--neutral-300);
    }}

    .req-top-row {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}

    .req-doc-id {{
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--primary);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .req-badge {{
      display: inline-block;
      padding: 0.25rem 0.75rem;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 600;
    }}

    .badge-pending {{
      background: var(--warning-light);
      color: var(--warning);
    }}

    .badge-approved {{
      background: #e0e7ff;
      color: #4338ca;
    }}

    .badge-completed {{
      background: #dcfce7;
      color: #15803d;
    }}

    .req-details-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 0.75rem;
      font-size: 0.85rem;
      color: var(--neutral-600);
    }}

    .req-details-grid div {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .req-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      margin: 0.5rem 0;
    }}

    .req-table th {{
      background: var(--neutral-100);
      text-align: left;
      padding: 0.5rem 0.75rem;
      font-weight: 600;
      color: var(--neutral-700);
      border-bottom: 1px solid var(--neutral-200);
    }}

    .req-table td {{
      padding: 0.5rem 0.75rem;
      border-bottom: 1px solid var(--neutral-100);
    }}

    .req-actions {{
      display: flex;
      justify-content: flex-end;
      gap: 0.75rem;
      flex-wrap: wrap;
      padding-top: 0.5rem;
      border-top: 1px solid var(--neutral-100);
    }}

    .btn {{
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
    }}

    .btn-outline {{
      background: white;
      border-color: var(--neutral-300);
      color: var(--neutral-700);
    }}

    .btn-outline:hover {{
      background: var(--neutral-50);
      border-color: var(--neutral-400);
    }}

    .btn-primary {{
      background: var(--primary);
      color: white;
    }}

    .btn-primary:hover {{
      background: var(--primary-hover);
    }}

    .btn-success {{
      background: var(--accent);
      color: white;
    }}

    .btn-success:hover {{
      background: var(--accent-hover);
    }}

    .btn-danger {{
      background: var(--danger);
      color: white;
    }}

    /* Modal Styles */
    .modal-overlay {{
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(3px);
      z-index: 100;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s;
    }}

    .modal-overlay.open {{
      opacity: 1;
      pointer-events: auto;
    }}

    .modal-card {{
      background: white;
      border-radius: 12px;
      width: 100%;
      max-width: 540px;
      box-shadow: var(--shadow-lg);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transform: scale(0.95);
      transition: transform 0.25s;
    }}

    .modal-overlay.open .modal-card {{
      transform: scale(1);
    }}

    .modal-header {{
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid var(--neutral-200);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .modal-header h3 {{
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--neutral-900);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .modal-body {{
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }}

    /* E-Signature Canvas Pad */
    .signature-pad-container {{
      border: 2px dashed var(--neutral-300);
      border-radius: 8px;
      background: #fafafa;
      position: relative;
      touch-action: none;
    }}

    canvas#signaturePad {{
      width: 100%;
      height: 200px;
      display: block;
      cursor: crosshair;
    }}

    .signature-placeholder {{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-size: 0.9rem;
      color: var(--neutral-400);
      pointer-events: none;
    }}

    .modal-footer {{
      padding: 1rem 1.5rem;
      background: var(--neutral-50);
      border-top: 1px solid var(--neutral-200);
      display: flex;
      justify-content: flex-end;
      gap: 0.75rem;
    }}

    /* PDF Printable Preview Styling */
    .pdf-preview-container {{
      background: #525659;
      padding: 2rem;
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1.5rem;
    }}

    .pdf-page {{
      background: white;
      width: 100%;
      max-width: 800px;
      padding: 3rem 3.5rem;
      box-shadow: 0 10px 25px rgba(0,0,0,0.3);
      font-family: 'Sarabun', sans-serif;
      color: #000;
      line-height: 1.6;
    }}

    .pdf-header {{
      text-align: center;
      margin-bottom: 2rem;
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}

    .pdf-vector-seal {{
      margin-bottom: 0.75rem;
    }}

    .pdf-header h2 {{
      font-size: 1.35rem;
      font-weight: 700;
      margin-bottom: 0.25rem;
    }}

    .pdf-header p {{
      font-size: 0.9rem;
      color: #444;
    }}

    .pdf-meta-table {{
      width: 100%;
      margin-bottom: 1.5rem;
      font-size: 0.95rem;
    }}

    .pdf-meta-table td {{
      padding: 4px 0;
    }}

    .pdf-items-table {{
      width: 100%;
      border-collapse: collapse;
      margin: 1.5rem 0;
      font-size: 0.95rem;
    }}

    .pdf-items-table th, .pdf-items-table td {{
      border: 1px solid #333;
      padding: 8px 10px;
    }}

    .pdf-items-table th {{
      background: #f3f4f6;
      font-weight: 600;
      text-align: center;
    }}

    .pdf-signatures {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 1rem;
      margin-top: 3rem;
      text-align: center;
      font-size: 0.875rem;
    }}

    .sig-box {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-end;
      height: 140px;
    }}

    .sig-img-preview {{
      max-height: 60px;
      max-width: 130px;
      margin-bottom: 4px;
    }}

    .sig-line {{
      width: 80%;
      border-bottom: 1px dotted #333;
      margin-bottom: 6px;
    }}

    /* Inventory View Metrics */
    .metrics-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1.25rem;
      margin-bottom: 1.5rem;
    }}

    .metric-card {{
      background: white;
      border: 1px solid var(--neutral-200);
      border-radius: var(--radius);
      padding: 1.25rem;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
    }}

    .metric-header {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: var(--neutral-600);
      font-size: 0.825rem;
      font-weight: 500;
    }}

    .metric-val {{
      font-size: 1.6rem;
      font-weight: 700;
      color: var(--neutral-900);
    }}

    /* Responsive */
    @media (max-width: 768px) {{
      .nav-container {{
        flex-direction: column;
        align-items: stretch;
      }}
      .view-switcher {{
        overflow-x: auto;
      }}
      .pdf-page {{
        padding: 1.5rem;
      }}
      .pdf-signatures {{
        grid-template-columns: 1fr;
        gap: 2rem;
      }}
    }}

    @media print {{
      body * {{
        visibility: hidden;
      }}
      header, .view-switcher, .btn, .pdf-preview-actions {{
        display: none !important;
      }}
      .pdf-page, .pdf-page * {{
        visibility: visible;
      }}
      .pdf-page {{
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        max-width: none;
        padding: 0;
        box-shadow: none;
      }}
    }}
  </style>
</head>
<body>

  <!-- Top Navigation Header -->
  <header>
    <div class="nav-container">
      <div class="brand">
        <div class="brand-icon">
          {svg_icons['box']}
        </div>
        <div class="brand-text">
          <h1>ระบบเบิกพัสดุและคลังดิจิทัล</h1>
          <p>e-Inventory & Requisition System</p>
        </div>
      </div>

      <!-- View Switcher Tabs (All Vector Icons) -->
      <nav class="view-switcher">
        <button class="view-btn active" onclick="switchView('catalog')">
          {svg_icons['cart']} สำหรับผู้เบิก (แคตตาล็อก)
        </button>
        <button class="view-btn" onclick="switchView('staff')">
          {svg_icons['clipboard']} เจ้าหน้าที่พัสดุ (อนุมัติ/จ่ายของ)
        </button>
        <button class="view-btn" onclick="switchView('inventory')">
          {svg_icons['chart']} สรุปยอดสต๊อกคลัง
        </button>
        <button class="view-btn" onclick="switchView('pdf')">
          {svg_icons['file_text']} ใบเบิก PDF (พร้อมลายเซ็น)
        </button>
      </nav>

      <button class="cart-trigger" onclick="toggleCartDrawer()">
        {svg_icons['cart']} ตะกร้าของฉัน
        <span class="cart-badge" id="cartCount">0</span>
      </button>
    </div>
  </header>

  <!-- Main Content Area -->
  <main>

    <!-- ============================================== -->
    <!-- VIEW 1: REQUISITION CATALOG (สำหรับผู้เบิก)      -->
    <!-- ============================================== -->
    <section id="view-catalog" class="view-content active">
      <!-- Requester Info Form with SEARCHABLE Combobox -->
      <div class="requester-bar">
        <div class="form-group custom-combobox-wrapper" id="deptComboboxWrapper">
          <label for="deptSearchInput">
            {svg_icons['building']} หน่วยงาน / คณะ / โรงเรียนที่สังกัด *
          </label>
          <div class="combobox-control" id="deptComboboxControl">
            <input type="text" id="deptSearchInput" class="form-control combobox-input" 
                   placeholder="พิมพ์ค้นหาคณะ หรือหน่วยงาน... (เช่น การเรือน, คอม, กองคลัง)" 
                   autocomplete="off" 
                   value="โรงเรียนการเรือน - เทคโนโลยีการประกอบอาหารและการบริการ"
                   onfocus="openDeptDropdown()" 
                   oninput="handleDeptSearch(this.value)">
            <!-- Hidden input that holds the actual selected value -->
            <input type="hidden" id="deptSelect" value="โรงเรียนการเรือน - เทคโนโลยีการประกอบอาหารและการบริการ">
            <button type="button" class="combobox-toggle-btn" onclick="toggleDeptDropdown(event)" title="เปิด/ปิด รายการ">
              {svg_icons['chevron_down']}
            </button>
          </div>
          <div class="combobox-dropdown" id="deptDropdownList">
            <!-- Populated and filtered by JS -->
          </div>
        </div>
        <div class="form-group">
          <label for="requesterName">
            {svg_icons['user']} ชื่อ-นามสกุล ผู้ขอเบิก *
          </label>
          <input type="text" id="requesterName" class="form-control" placeholder="เช่น อ.สมชาย ใจดี" value="อ.สมชาย ใจดี">
        </div>
        <div class="form-group">
          <label for="requesterPhone">
            {svg_icons['phone']} เบอร์โทรศัพท์ติดต่อ
          </label>
          <input type="tel" id="requesterPhone" class="form-control" placeholder="เช่น 081-234-5678" value="081-998-7766">
        </div>
      </div>

      <!-- Search & Filters -->
      <div class="search-filter-bar">
        <div class="search-box-wrapper">
          <span class="search-icon">{svg_icons['search']}</span>
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
    </section>


    <!-- ============================================== -->
    <!-- VIEW 2: STAFF DASHBOARD (สำหรับเจ้าหน้าที่พัสดุ)  -->
    <!-- ============================================== -->
    <section id="view-staff" class="view-content">
      <div class="dashboard-header">
        <div>
          <h2>จัดการคำขอเบิกพัสดุ</h2>
          <p style="color: var(--neutral-600); font-size: 0.85rem;">ตรวจสอบ อนุมัติ ปรับยอดจ่าย และเซ็นรับของจริง</p>
        </div>
        <div class="status-tabs">
          <button class="status-tab active" onclick="filterRequisitionStatus('PENDING', this)">
            รออนุมัติ <span class="count-tag" id="pendingCount">1</span>
          </button>
          <button class="status-tab" onclick="filterRequisitionStatus('APPROVED', this)">
            รอจ่ายของ <span class="count-tag" id="approvedCount">1</span>
          </button>
          <button class="status-tab" onclick="filterRequisitionStatus('COMPLETED', this)">
            จ่ายสำเร็จแล้ว <span class="count-tag" id="completedCount">1</span>
          </button>
        </div>
      </div>

      <!-- Requisition Cards Container -->
      <div id="requisitionsContainer">
        <!-- Rendered dynamically by JS -->
      </div>
    </section>


    <!-- ============================================== -->
    <!-- VIEW 3: INVENTORY OVERVIEW (คลังและสต๊อก)        -->
    <!-- ============================================== -->
    <section id="view-inventory" class="view-content">
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-header">{svg_icons['box']} รายการพัสดุทั้งหมดในระบบ</div>
          <span class="metric-val">4,045 <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">รายการ</small></span>
        </div>
        <div class="metric-card">
          <div class="metric-header" style="color: var(--danger);">{svg_icons['alert_triangle']} พัสดุต่ำกว่าเกณฑ์ขั้นต่ำ (Reorder Alert)</div>
          <span class="metric-val" style="color: var(--danger);">12 <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">รายการ</small></span>
        </div>
        <div class="metric-card">
          <div class="metric-header" style="color: var(--primary);">{svg_icons['clock']} ยอดจองรอจ่าย (Reserved Stock)</div>
          <span class="metric-val" style="color: var(--primary);">2,250 <small style="font-size: 0.9rem; font-weight: normal; color: var(--neutral-400);">ชิ้น</small></span>
        </div>
        <div class="metric-card">
          <div class="metric-header" style="color: var(--accent);">{svg_icons['calendar']} รอบบัญชีปัจจุบัน</div>
          <span class="metric-val" style="color: var(--accent);">ต.ค. 2569</span>
        </div>
      </div>

      <div style="background: white; border-radius: var(--radius); border: 1px solid var(--neutral-200); padding: 1.5rem; box-shadow: var(--shadow-sm);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
          <h3 style="font-size: 1.1rem; font-weight: 700;">ตารางรายการสต๊อกคงเหลือจริง (On-Hand vs Available)</h3>
          <div style="display: flex; gap: 0.5rem;">
            <button class="btn btn-outline" onclick="alert('จำลองการนำเข้าไฟล์ ยอดสต๊อก ตค.xlsx สำเร็จ!')">
              {svg_icons['upload']} นำเข้าจาก Excel
            </button>
            <button class="btn btn-primary" onclick="alert('เปิดฟอร์มรับเข้าพัสดุใหม่')">
              {svg_icons['plus']} บันทึกรับเข้าพัสดุ
            </button>
          </div>
        </div>

        <div style="overflow-x: auto;">
          <table class="req-table" style="font-size: 0.9rem;">
            <thead>
              <tr>
                <th style="width: 60px;">ลำดับ</th>
                <th>ชื่อรายการพัสดุ</th>
                <th>หน่วยบรรจุ</th>
                <th>คงคลังจริง (On-Hand)</th>
                <th>ยอดจอง (Reserved)</th>
                <th>พร้อมเบิก (Available)</th>
                <th>สถานะสต๊อก</th>
              </tr>
            </thead>
            <tbody id="inventoryTableBody">
              <!-- Rendered by JS -->
            </tbody>
          </table>
        </div>
      </div>
    </section>


    <!-- ============================================== -->
    <!-- VIEW 4: PDF PRINTABLE PREVIEW (ใบเบิกพัสดุ)      -->
    <!-- ============================================== -->
    <section id="view-pdf" class="view-content">
      <div class="pdf-preview-container">
        <div class="pdf-preview-actions" style="display: flex; gap: 1rem;">
          <button class="btn btn-success" onclick="window.print()">
            {svg_icons['printer']} สั่งพิมพ์เอกสารราชการ (Print PDF)
          </button>
          <button class="btn btn-outline" style="background: white;" onclick="switchView('staff')">
            {svg_icons['arrow_left']} กลับหน้ารายการเบิก
          </button>
        </div>

        <!-- The A4 Sheet -->
        <div class="pdf-page" id="printablePdf">
          <div class="pdf-header">
            {pdf_seal_svg}
            <h2>ใบขอเบิกพัสดุ</h2>
            <p>ฝ่ายพัสดุและคลังสินค้ากลาง มหาวิทยาลัยสวนดุสิต</p>
          </div>

          <table class="pdf-meta-table">
            <tr>
              <td style="width: 55%;"><strong>เลขที่เอกสาร:</strong> <span id="pdfDocNo">REQ-256910-0042</span></td>
              <td><strong>วันที่ขอเบิก:</strong> 21 ตุลาคม 2569</td>
            </tr>
            <tr>
              <td><strong>หน่วยงาน/คณะ:</strong> <span id="pdfDept">โรงเรียนการเรือน</span></td>
              <td><strong>ชื่อผู้ขอเบิก:</strong> <span id="pdfRequester">อ.สมชาย ใจดี</span></td>
            </tr>
            <tr>
              <td colspan="2"><strong>วัตถุประสงค์ในการขอเบิก:</strong> <span id="pdfPurpose">ใช้สำหรับการจัดการเรียนการสอนและสอบปฏิบัติการ ประจำภาคการศึกษา 1/2569</span></td>
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

          <div style="font-size: 0.85rem; margin-top: 1rem;">
            * ข้าพเจ้าได้รับมอบพัสดุตามรายการและจำนวนที่ระบุข้างต้นไว้ในสภาพเรียบร้อยครบถ้วนแล้ว
          </div>

          <!-- Signatures Section -->
          <div class="pdf-signatures">
            <div class="sig-box">
              <div class="sig-line"></div>
              <div>( <span id="pdfSignRequester">อ.สมชาย ใจดี</span> )</div>
              <div style="font-size: 0.75rem; color: #666;">ผู้ขอเบิกพัสดุ</div>
              <div style="font-size: 0.75rem; color: #666;">21 ต.ค. 2569</div>
            </div>

            <div class="sig-box">
              <div style="font-size: 0.8rem; color: #0284c7; font-weight: bold; margin-bottom: 8px;">[ ประทับตราอนุมัติ ]</div>
              <div class="sig-line"></div>
              <div>( นางสมศรี พัสดุดี )</div>
              <div style="font-size: 0.75rem; color: #666;">เจ้าหน้าที่พัสดุผู้จ่ายของ</div>
              <div style="font-size: 0.75rem; color: #666;">21 ต.ค. 2569 11:15 น.</div>
            </div>

            <div class="sig-box">
              <div id="pdfReceiverSigArea">
                <!-- Signature will be placed here -->
                <div style="height: 50px; display: flex; align-items: center; justify-content: center; color: #999; font-style: italic;">
                  [ ยังไม่ได้เซ็นรับของ ]
                </div>
              </div>
              <div class="sig-line"></div>
              <div>( <span id="pdfReceiverName">อ.สมชาย ใจดี</span> )</div>
              <div style="font-size: 0.75rem; color: #666;">ผู้รับพัสดุ</div>
              <div style="font-size: 0.75rem; color: #666;" id="pdfReceiveTime">21 ต.ค. 2569</div>
            </div>
          </div>
        </div>
      </div>
    </section>

  </main>


  <!-- ============================================== -->
  <!-- SLIDE-OVER CART DRAWER                         -->
  <!-- ============================================== -->
  <div class="cart-drawer-overlay" id="cartOverlay" onclick="toggleCartDrawer()">
    <div class="cart-drawer" onclick="event.stopPropagation()">
      <div class="cart-header">
        <h3>{svg_icons['cart']} ตะกร้าขอเบิกพัสดุ</h3>
        <button class="close-btn" onclick="toggleCartDrawer()">{svg_icons['x']}</button>
      </div>

      <div class="cart-items-list" id="cartItemsList">
        <!-- Rendered by JS -->
      </div>

      <div class="cart-footer">
        <div class="form-group">
          <label for="cartPurpose">
            {svg_icons['edit']} วัตถุประสงค์ในการเบิกใช้งาน *
          </label>
          <textarea id="cartPurpose" class="form-control" rows="2" placeholder="เช่น ใช้สำหรับการสอบปลายภาค, งานประชุมวิชาการ..."></textarea>
        </div>
        <button class="btn-submit-requisition" onclick="submitRequisition()">
          {svg_icons['check_circle']} ยืนยันส่งคำขอเบิกพัสดุ
        </button>
      </div>
    </div>
  </div>


  <!-- ============================================== -->
  <!-- MODAL: E-SIGNATURE PAD (กระดานเซ็นชื่อรับของ)     -->
  <!-- ============================================== -->
  <div class="modal-overlay" id="signatureModal">
    <div class="modal-card">
      <div class="modal-header">
        <h3>{svg_icons['pen_tool']} ลงนามรับมอบพัสดุ (E-Signature)</h3>
        <button class="close-btn" onclick="closeSignatureModal()">{svg_icons['x']}</button>
      </div>
      <div class="modal-body">
        <p style="font-size: 0.875rem; color: var(--neutral-600);">
          ผู้รับของ: <strong id="sigModalRequesterName" style="color: var(--neutral-900);">อ.สมชาย ใจดี</strong> 
          (<span id="sigModalDocNo">REQ-256910-0042</span>)
        </p>

        <div class="signature-pad-container">
          <canvas id="signaturePad"></canvas>
          <div class="signature-placeholder" id="sigPlaceholder">ใช้นิ้วหรือเมาส์เซ็นลายมือชื่อที่นี่</div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 0.75rem; color: var(--neutral-400);">ระบบจะนำลายเซ็นไปประทับในเอกสารใบเบิก PDF ทันที</span>
          <button class="btn btn-outline" style="font-size: 0.75rem; padding: 4px 8px;" onclick="clearSignature()">
            ล้างลายเซ็น
          </button>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-outline" onclick="closeSignatureModal()">ยกเลิก</button>
        <button class="btn btn-success" onclick="confirmSignatureAndComplete()">
          {svg_icons['check']} ยืนยันจ่ายของและบันทึกลายเซ็น
        </button>
      </div>
    </div>
  </div>


  <!-- JAVASCRIPT LOGIC -->
  <script>
    // Vector Icons Helper for dynamic rendering in JS
    const vIcons = {{
      box: `{svg_icons['box']}`,
      cart: `{svg_icons['cart']}`,
      layers: `{svg_icons['layers']}`,
      tag: `{svg_icons['tag']}`,
      trash: `{svg_icons['trash']}`,
      pen: `{svg_icons['pen_tool']}`,
      check: `{svg_icons['check']}`,
      x: `{svg_icons['x']}`,
      eye: `{svg_icons['eye']}`,
      printer: `{svg_icons['printer']}`,
      building: `{svg_icons['building']}`,
      user: `{svg_icons['user']}`,
      calendar: `{svg_icons['calendar']}`,
      fileText: `{svg_icons['file_text']}`
    }};

    // ====================================================
    // SEARCHABLE DEPARTMENTS DATA (from คณะและหน่วยงาน.txt)
    // ====================================================
    const departmentsData = [
      {{
        category: "คณะและโรงเรียน (Faculties & Schools)",
        items: [
          {{ label: "คณะครุศาสตร์ (ภาพรวม)", value: "คณะครุศาสตร์", sub: false }},
          {{ label: "การศึกษาปฐมวัย (คณะครุศาสตร์)", value: "คณะครุศาสตร์ - การศึกษาปฐมวัย", sub: true }},
          {{ label: "การประถมศึกษา (คณะครุศาสตร์)", value: "คณะครุศาสตร์ - การประถมศึกษา", sub: true }},
          {{ label: "หลักสูตรประกาศนียบัตรบัณฑิตวิชาชีพครู (คณะครุศาสตร์)", value: "คณะครุศาสตร์ - หลักสูตรประกาศนียบัตรบัณฑิตวิชาชีพครู", sub: true }},
          {{ label: "หลักสูตรประกาศนียบัตรบัณฑิต สาขาวิชาล่ามภาษามือ (คณะครุศาสตร์)", value: "คณะครุศาสตร์ - สาขาวิชาล่ามภาษามือ", sub: true }},
          {{ label: "หลักสูตรศึกษาศาสตรมหาบัณฑิต สาขาวิชาการจัดการการศึกษาปฐมวัยและประถมศึกษา (คณะครุศาสตร์)", value: "คณะครุศาสตร์ - มหาบัณฑิตปฐมวัย", sub: true }},
          {{ label: "หลักสูตรศึกษาศาสตรมหาบัณฑิต สาขาวิชาการสอนภาษาอังกฤษระดับประถมศึกษา (คณะครุศาสตร์)", value: "คณะครุศาสตร์ - มหาบัณฑิตสอนภาษาอังกฤษ", sub: true }},
          
          {{ label: "คณะวิทยาศาสตร์และเทคโนโลยี (ภาพรวม)", value: "คณะวิทยาศาสตร์และเทคโนโลยี", sub: false }},
          {{ label: "วิทยาการคอมพิวเตอร์ (คณะวิทยาศาสตร์และเทคโนโลยี)", value: "คณะวิทยาศาสตร์และเทคโนโลยี - วิทยาการคอมพิวเตอร์", sub: true }},
          {{ label: "วิทยาศาสตร์เครื่องสำอาง (คณะวิทยาศาสตร์และเทคโนโลยี)", value: "คณะวิทยาศาสตร์และเทคโนโลยี - วิทยาศาสตร์เครื่องสำอาง", sub: true }},
          {{ label: "อาชีวอนามัยและความปลอดภัย (คณะวิทยาศาสตร์และเทคโนโลยี)", value: "คณะวิทยาศาสตร์และเทคโนโลยี - อาชีวอนามัยและความปลอดภัย", sub: true }},
          {{ label: "อนามัยสิ่งแวดล้อมและสาธารณภัย (คณะวิทยาศาสตร์และเทคโนโลยี)", value: "คณะวิทยาศาสตร์และเทคโนโลยี - อนามัยสิ่งแวดล้อม", sub: true }},
          {{ label: "วิทยาศาสตร์การแพทย์ (คณะวิทยาศาสตร์และเทคโนโลยี)", value: "คณะวิทยาศาสตร์และเทคโนโลยี - วิทยาศาสตร์การแพทย์", sub: true }},
          {{ label: "วิทยาศาสตร์ทั่วไป (คณะวิทยาศาสตร์และเทคโนโลยี)", value: "คณะวิทยาศาสตร์และเทคโนโลยี - วิทยาศาสตร์ทั่วไป", sub: true }},
          {{ label: "เทคโนโลยีสารสนเทศ (คณะวิทยาศาสตร์และเทคโนโลยี)", value: "คณะวิทยาศาสตร์และเทคโนโลยี - เทคโนโลยีสารสนเทศ", sub: true }},
          {{ label: "อุตสาหกรรมชีวภาพเพื่อธุรกิจ (คณะวิทยาศาสตร์และเทคโนโลยี)", value: "คณะวิทยาศาสตร์และเทคโนโลยี - อุตสาหกรรมชีวภาพ", sub: true }},
          {{ label: "ความมั่นคงปลอดภัยไซเบอร์ (คณะวิทยาศาสตร์และเทคโนโลยี)", value: "คณะวิทยาศาสตร์และเทคโนโลยี - ความมั่นคงปลอดภัยไซเบอร์", sub: true }},
          
          {{ label: "คณะวิทยาการจัดการ (ภาพรวม)", value: "คณะวิทยาการจัดการ", sub: false }},
          {{ label: "การจัดการบัณฑิต (คณะวิทยาการจัดการ)", value: "คณะวิทยาการจัดการ - การจัดการบัณฑิต", sub: true }},
          {{ label: "นิเทศศาสตร์นวัตกรรมและผู้ประกอบการธุรกิจ (คณะวิทยาการจัดการ)", value: "คณะวิทยาการจัดการ - นิเทศศาสตร์นวัตกรรม", sub: true }},
          {{ label: "เลขานุการทางการแพทย์ (คณะวิทยาการจัดการ)", value: "คณะวิทยาการจัดการ - เลขานุการทางการแพทย์", sub: true }},
          {{ label: "การสื่อสารดิจิทัลและการสร้างสรรค์คอนเทนต์ (คณะวิทยาการจัดการ)", value: "คณะวิทยาการจัดการ - การสื่อสารดิจิทัล", sub: true }},
          {{ label: "การตลาดและการสร้างแบรนด์บุคคล (คณะวิทยาการจัดการ)", value: "คณะวิทยาการจัดการ - การตลาด", sub: true }},
          {{ label: "การเต้นและการแสดงสร้างสรรค์เพื่อธุรกิจบันเทิง (คณะวิทยาการจัดการ)", value: "คณะวิทยาการจัดการ - การเต้นและการแสดง", sub: true }},
          {{ label: "การบัญชี (คณะวิทยาการจัดการ)", value: "คณะวิทยาการจัดการ - การบัญชี", sub: true }},
          {{ label: "ธุรกิจระหว่างประเทศ ธุรกิจจีน-อาเซียน (คณะวิทยาการจัดการ)", value: "คณะวิทยาการจัดการ - ธุรกิจจีน-อาเซียน", sub: true }},
          {{ label: "ธุรกิจสร้างสรรค์และเทคโนโลยีดิจิทัล (คณะวิทยาการจัดการ)", value: "คณะวิทยาการจัดการ - ธุรกิจสร้างสรรค์", sub: true }},
          {{ label: "บริหารธุรกิจบัณฑิต (คณะวิทยาการจัดการ)", value: "คณะวิทยาการจัดการ - บริหารธุรกิจบัณฑิต", sub: true }},

          {{ label: "คณะมนุษยศาสตร์และสังคมศาสตร์ (ภาพรวม)", value: "คณะมนุษยศาสตร์และสังคมศาสตร์", sub: false }},
          {{ label: "จิตวิทยาอุตสาหกรรมและองค์การ (คณะมนุษยศาสตร์ฯ)", value: "คณะมนุษยศาสตร์และสังคมศาสตร์ - จิตวิทยาอุตสาหกรรม", sub: true }},
          {{ label: "ภาษาและการสื่อสาร (คณะมนุษยศาสตร์ฯ)", value: "คณะมนุษยศาสตร์และสังคมศาสตร์ - ภาษาและการสื่อสาร", sub: true }},
          {{ label: "ภาษาอังกฤษเพื่อการสื่อสาร (คณะมนุษยศาสตร์ฯ)", value: "คณะมนุษยศาสตร์และสังคมศาสตร์ - ภาษาอังกฤษ", sub: true }},
          {{ label: "ภาษาจีนเพื่อการสื่อสาร (คณะมนุษยศาสตร์ฯ)", value: "คณะมนุษยศาสตร์และสังคมศาสตร์ - ภาษาจีน", sub: true }},
          {{ label: "ภาษาและวัฒนธรรมไทย (คณะมนุษยศาสตร์ฯ)", value: "คณะมนุษยศาสตร์และสังคมศาสตร์ - ภาษาและวัฒนธรรมไทย", sub: true }},
          {{ label: "ภาษาอังกฤษและภาษาเกาหลี (คณะมนุษยศาสตร์ฯ)", value: "คณะมนุษยศาสตร์และสังคมศาสตร์ - ภาษาเกาหลี", sub: true }},

          {{ label: "คณะพยาบาลศาสตร์ (ภาพรวม)", value: "คณะพยาบาลศาสตร์", sub: false }},
          {{ label: "พยาบาลศาสตรบัณฑิต (คณะพยาบาลศาสตร์)", value: "คณะพยาบาลศาสตร์ - พยาบาลศาสตรบัณฑิต", sub: true }},
          {{ label: "ประกาศนียบัตรผู้ช่วยพยาบาล (คณะพยาบาลศาสตร์)", value: "คณะพยาบาลศาสตร์ - ประกาศนียบัตรผู้ช่วยพยาบาล", sub: true }},

          {{ label: "โรงเรียนการท่องเที่ยวและการบริการ (ภาพรวม)", value: "โรงเรียนการท่องเที่ยวและการบริการ", sub: false }},
          {{ label: "ธุรกิจการโรงแรม (โรงเรียนการท่องเที่ยวฯ)", value: "โรงเรียนการท่องเที่ยวและการบริการ - ธุรกิจการโรงแรม", sub: true }},
          {{ label: "ธุรกิจการบิน (โรงเรียนการท่องเที่ยวฯ)", value: "โรงเรียนการท่องเที่ยวและการบริการ - ธุรกิจการบิน", sub: true }},
          {{ label: "การจัดการไมซ์และอีเวนต์ (โรงเรียนการท่องเที่ยวฯ)", value: "โรงเรียนการท่องเที่ยวและการบริการ - ไมซ์และอีเวนต์", sub: true }},
          {{ label: "การท่องเที่ยวและมัคคุเทศก์ (โรงเรียนการท่องเที่ยวฯ)", value: "โรงเรียนการท่องเที่ยวและการบริการ - มัคคุเทศก์", sub: true }},
          {{ label: "ธุรกิจเวลเนส (โรงเรียนการท่องเที่ยวฯ)", value: "โรงเรียนการท่องเที่ยวและการบริการ - เวลเนส", sub: true }},

          {{ label: "โรงเรียนการเรือน (ภาพรวม)", value: "โรงเรียนการเรือน", sub: false }},
          {{ label: "เทคโนโลยีการประกอบอาหารและการบริการ (โรงเรียนการเรือน)", value: "โรงเรียนการเรือน - เทคโนโลยีการประกอบอาหารและการบริการ", sub: true }},
          {{ label: "คหกรรมศาสตร์ (โรงเรียนการเรือน)", value: "โรงเรียนการเรือน - คหกรรมศาสตร์", sub: true }},
          {{ label: "นวัตกรรมเทคโนโลยีเพื่อผู้ประกอบการอาหาร (โรงเรียนการเรือน)", value: "โรงเรียนการเรือน - นวัตกรรมอาหาร", sub: true }},
          {{ label: "โภชนาการและการประกอบอาหารเพื่อสุขภาพ (โรงเรียนการเรือน)", value: "โรงเรียนการเรือน - โภชนาการ", sub: true }},
          {{ label: "การจัดการธุรกิจบริการอาหารและศิลปะ (โรงเรียนการเรือน)", value: "โรงเรียนการเรือน - ศิลปะการประกอบอาหาร", sub: true }},

          {{ label: "โรงเรียนกฎหมายและการเมือง (ภาพรวม)", value: "โรงเรียนกฎหมายและการเมือง", sub: false }},
          {{ label: "นิติศาสตร์ (โรงเรียนกฎหมายและการเมือง)", value: "โรงเรียนกฎหมายและการเมือง - นิติศาสตร์", sub: true }},
          {{ label: "หลักสูตรรัฐศาสตร์ (โรงเรียนกฎหมายและการเมือง)", value: "โรงเรียนกฎหมายและการเมือง - รัฐศาสตร์", sub: true }},
          {{ label: "หลักสูตรรัฐประศาสนศาสตร์ (โรงเรียนกฎหมายและการเมือง)", value: "โรงเรียนกฎหมายและการเมือง - รัฐประศาสนศาสตร์", sub: true }},

          {{ label: "บัณฑิตวิทยาลัย", value: "บัณฑิตวิทยาลัย", sub: false }},
          {{ label: "โรงเรียนสาธิตละอออุทิศ", value: "โรงเรียนสาธิตละอออุทิศ", sub: false }}
        ]
      }},
      {{
        category: "สถาบัน / สำนัก / ศูนย์ / กอง (Institutes & Offices)",
        items: [
          {{ label: "สวนดุสิตโพล", value: "สวนดุสิตโพล", sub: false }},
          {{ label: "สำนักวิทยบริการและเทคโนโลยีสารสนเทศ", value: "สำนักวิทยบริการและเทคโนโลยีสารสนเทศ", sub: false }},
          {{ label: "สำนักส่งเสริมวิชาการและงานทะเบียน", value: "สำนักส่งเสริมวิชาการและงานทะเบียน", sub: false }},
          
          {{ label: "สำนักงานมหาวิทยาลัย - กองกลาง", value: "สำนักงานมหาวิทยาลัย - กองกลาง", sub: false }},
          {{ label: "สำนักงานมหาวิทยาลัย - กองบริหารงานบุคคล", value: "สำนักงานมหาวิทยาลัย - กองบริหารงานบุคคล", sub: false }},
          {{ label: "สำนักงานมหาวิทยาลัย - กองคลัง", value: "สำนักงานมหาวิทยาลัย - กองคลัง", sub: false }},
          {{ label: "สำนักงานมหาวิทยาลัย - กองคลัง (งานพัสดุ)", value: "สำนักงานมหาวิทยาลัย - กองคลัง (งานพัสดุ)", sub: false }},
          {{ label: "สำนักงานมหาวิทยาลัย - กองอาคารสถานที่", value: "สำนักงานมหาวิทยาลัย - กองอาคารสถานที่", sub: false }},
          {{ label: "สำนักงานมหาวิทยาลัย - กองพัฒนานักศึกษา", value: "สำนักงานมหาวิทยาลัย - กองพัฒนานักศึกษา", sub: false }},
          {{ label: "สำนักงานมหาวิทยาลัย - กองประชาสัมพันธ์", value: "สำนักงานมหาวิทยาลัย - กองประชาสัมพันธ์", sub: false }},
          {{ label: "สำนักงานมหาวิทยาลัย - สำนักงานเลขานุการสภามหาวิทยาลัย", value: "สำนักงานมหาวิทยาลัย - สำนักงานเลขานุการสภา", sub: false }},

          {{ label: "สำนักกิจการพิเศษ", value: "สำนักกิจการพิเศษ", sub: false }},
          {{ label: "โรงแรมสวนดุสิตเพลส (สำนักกิจการพิเศษ)", value: "สำนักกิจการพิเศษ - โรงแรมสวนดุสิตเพลส", sub: true }},
          {{ label: "สถาบันภาษา/ศิลปะและวัฒนธรรม", value: "สถาบันภาษา/ศิลปะและวัฒนธรรม", sub: false }},
          {{ label: "สถาบันวิจัยและพัฒนา", value: "สถาบันวิจัยและพัฒนา", sub: false }},
          {{ label: "ศูนย์พัฒนาทุนมนุษย์", value: "ศูนย์พัฒนาทุนมนุษย์", sub: false }},
          {{ label: "ศูนย์บริการสื่อและสิ่งพิมพ์กราฟฟิคไซท์", value: "ศูนย์บริการสื่อและสิ่งพิมพ์กราฟฟิคไซท์", sub: false }},
          {{ label: "สำนักยุทธศาสตร์และแผน", value: "สำนักยุทธศาสตร์และแผน", sub: false }},
          {{ label: "สำนักกฎหมาย", value: "สำนักกฎหมาย", sub: false }},
          {{ label: "โครงการความร่วมมือทางวิชาการ", value: "โครงการความร่วมมือทางวิชาการ", sub: false }},
          {{ label: "ศูนย์สนเทศแนะแนวการศึกษาและอาชีพ", value: "ศูนย์สนเทศแนะแนวการศึกษาและอาชีพ", sub: false }},
          {{ label: "สภาคณาจารย์และพนักงาน", value: "สภาคณาจารย์และพนักงาน", sub: false }},
          {{ label: "สหกรณ์ออมทรัพย์", value: "สหกรณ์ออมทรัพย์", sub: false }},
          {{ label: "ศูนย์บริการทดสอบทางวิชาการสวนดุสิต", value: "ศูนย์บริการทดสอบทางวิชาการสวนดุสิต", sub: false }},
          {{ label: "โครงการปฏิบัติการอาหารแปรรูป มสด.", value: "โครงการปฏิบัติการอาหารแปรรูป มสด.", sub: false }},
          {{ label: "อาคารหอพัก Dormsita ศูนย์วิทยาศาสตร์", value: "อาคารหอพัก Dormsita", sub: false }}
        ]
      }}
    ];

    // Combobox Functions
    function renderDeptDropdown(filterText = "") {{
      const dropdown = document.getElementById('deptDropdownList');
      const cleanFilter = filterText.trim().toLowerCase();
      let totalMatches = 0;
      let html = "";

      const currentVal = document.getElementById('deptSelect').value;

      departmentsData.forEach(cat => {{
        const matchedItems = cat.items.filter(item => 
          item.label.toLowerCase().includes(cleanFilter) || item.value.toLowerCase().includes(cleanFilter)
        );

        if (matchedItems.length > 0) {{
          totalMatches += matchedItems.length;
          html += `<div class="combobox-group-title">${{cat.category}}</div>`;
          matchedItems.forEach(item => {{
            const isSelected = item.value === currentVal;
            const subClass = item.sub ? 'combobox-item-sub' : '';
            html += `
              <div class="combobox-item ${{subClass}} ${{isSelected ? 'selected' : ''}}" 
                   onclick="selectDepartment('${{item.value}}', '${{item.label}}')">
                <span>${{item.label}}</span>
                ${{isSelected ? `<span style="color: var(--primary); font-size: 0.8rem;">${{vIcons.check}}</span>` : ''}}
              </div>
            `;
          }});
        }}
      }});

      if (totalMatches === 0) {{
        html = `
          <div class="combobox-no-results">
            ${{vIcons.search}}<br>
            ไม่พบหน่วยงานที่ตรงกับ "<strong>${{filterText}}</strong>"
          </div>
        `;
      }}

      dropdown.innerHTML = html;
    }}

    function openDeptDropdown() {{
      const dropdown = document.getElementById('deptDropdownList');
      const control = document.getElementById('deptComboboxControl');
      dropdown.classList.add('open');
      control.classList.add('open');
      renderDeptDropdown(document.getElementById('deptSearchInput').value);
    }}

    function closeDeptDropdown() {{
      const dropdown = document.getElementById('deptDropdownList');
      const control = document.getElementById('deptComboboxControl');
      dropdown.classList.remove('open');
      control.classList.remove('open');
    }}

    function toggleDeptDropdown(e) {{
      e.stopPropagation();
      const dropdown = document.getElementById('deptDropdownList');
      if (dropdown.classList.contains('open')) {{
        closeDeptDropdown();
      }} else {{
        document.getElementById('deptSearchInput').focus();
        openDeptDropdown();
      }}
    }}

    function handleDeptSearch(text) {{
      openDeptDropdown();
      renderDeptDropdown(text);
    }}

    function selectDepartment(value, label) {{
      document.getElementById('deptSelect').value = value;
      document.getElementById('deptSearchInput').value = label;
      closeDeptDropdown();
    }}

    // Close on click outside
    document.addEventListener('click', (e) => {{
      const wrapper = document.getElementById('deptComboboxWrapper');
      if (wrapper && !wrapper.contains(e.target)) {{
        closeDeptDropdown();
      }}
    }});

    // Sample Data extracted from real Excel 'ยอดสต๊อก ตค.xlsx'
    const sampleItems = [
      {{
        id: 1,
        name: "ซองขยายข้างมีครุฑ 279´432 (กล่องละ 250 ซอง)",
        category: "ซองเอกสาร",
        is_multi_unit: true,
        unit_box_name: "กล่อง",
        unit_piece_name: "ซอง",
        pieces_per_box: 250,
        on_hand_pieces: 1750,
        reserved_pieces: 500,
        min_alert: 500,
        image_piece: "assets/images/image1.jpeg",
        image_box: "assets/images/image10.jpeg",
        current_img_mode: "piece"
      }},
      {{
        id: 2,
        name: "กระดาษคำตอบ (กล่องละ 2000 ใบ 1 กล่องมี 4 ห่อ ห่อละ 500 ใบ)",
        category: "กระดาษและแบบฟอร์ม",
        is_multi_unit: true,
        unit_box_name: "กล่อง",
        unit_piece_name: "ใบ",
        pieces_per_box: 2000,
        on_hand_pieces: 34500,
        reserved_pieces: 2000,
        min_alert: 5000,
        image_piece: "assets/images/image2.jpeg",
        image_box: "assets/images/image11.jpeg",
        current_img_mode: "piece"
      }},
      {{
        id: 3,
        name: "ซองเอกสารสีขาว 7´10 (500 ซองต่อกล่อง)",
        category: "ซองเอกสาร",
        is_multi_unit: true,
        unit_box_name: "กล่อง",
        unit_piece_name: "ซอง",
        pieces_per_box: 500,
        on_hand_pieces: 1000,
        reserved_pieces: 0,
        min_alert: 250,
        image_piece: "assets/images/image3.jpeg",
        image_box: "assets/images/image12.jpeg",
        current_img_mode: "piece"
      }},
      {{
        id: 4,
        name: "กระดาษลายเส้น (ห่อละ 500 แผ่น)",
        category: "กระดาษและแบบฟอร์ม",
        is_multi_unit: true,
        unit_box_name: "ห่อ",
        unit_piece_name: "แผ่น",
        pieces_per_box: 500,
        on_hand_pieces: 23500,
        reserved_pieces: 0,
        min_alert: 1000,
        image_piece: "assets/images/image4.jpeg",
        image_box: "assets/images/image13.jpeg",
        current_img_mode: "piece"
      }},
      {{
        id: 5,
        name: "แฟ้มเสนอ",
        category: "เครื่องเขียนและแฟ้ม",
        is_multi_unit: false,
        unit_box_name: "เล่ม",
        unit_piece_name: "เล่ม",
        pieces_per_box: 1,
        on_hand_pieces: 15,
        reserved_pieces: 3,
        min_alert: 5,
        image_piece: "assets/images/image5.jpeg",
        image_box: "assets/images/image5.jpeg",
        current_img_mode: "piece"
      }},
      {{
        id: 6,
        name: "ซองเอกสารน้ำตาล (มสด) 9´12.3",
        category: "ซองเอกสาร",
        is_multi_unit: true,
        unit_box_name: "กล่อง",
        unit_piece_name: "ซอง",
        pieces_per_box: 500,
        on_hand_pieces: 1500,
        reserved_pieces: 0,
        min_alert: 500,
        image_piece: "assets/images/image14.jpeg",
        image_box: "assets/images/image15.jpeg",
        current_img_mode: "piece"
      }}
    ];

    // Requisition Requests (Sample Database)
    let requisitions = [
      {{
        id: "REQ-256910-0042",
        dept: "โรงเรียนการเรือน - เทคโนโลยีการประกอบอาหารและการบริการ",
        requester: "อ.สมชาย ใจดี",
        phone: "081-998-7766",
        purpose: "ใช้สำหรับการจัดการเรียนการสอนและสอบปฏิบัติการ ภาคเรียน 1/2569",
        date: "21 ต.ค. 2569 10:15 น.",
        status: "APPROVED",
        signature: null,
        items: [
          {{ itemId: 1, name: "ซองขยายข้างมีครุฑ 279´432", qtyBoxes: 2, qtyPieces: 0, totalPieces: 500, unitBox: "กล่อง", unitPiece: "ซอง", approvedPieces: 500 }},
          {{ itemId: 2, name: "กระดาษคำตอบ", qtyBoxes: 1, qtyPieces: 0, totalPieces: 2000, unitBox: "กล่อง", unitPiece: "ใบ", approvedPieces: 2000 }},
          {{ itemId: 5, name: "แฟ้มเสนอ", qtyBoxes: 0, qtyPieces: 3, totalPieces: 3, unitBox: "เล่ม", unitPiece: "เล่ม", approvedPieces: 3 }}
        ]
      }},
      {{
        id: "REQ-256910-0043",
        dept: "คณะพยาบาลศาสตร์ - พยาบาลศาสตรบัณฑิต",
        requester: "คุณพรทิพย์ สุขขี",
        phone: "089-112-3344",
        purpose: "เตรียมเอกสารปฐมนิเทศนักศึกษาฝึกปฏิบัติงานคลินิก",
        date: "21 ต.ค. 2569 10:45 น.",
        status: "PENDING",
        signature: null,
        items: [
          {{ itemId: 3, name: "ซองเอกสารสีขาว 7´10", qtyBoxes: 1, qtyPieces: 0, totalPieces: 500, unitBox: "กล่อง", unitPiece: "ซอง", approvedPieces: 500 }},
          {{ itemId: 4, name: "กระดาษลายเส้น", qtyBoxes: 2, qtyPieces: 0, totalPieces: 1000, unitBox: "ห่อ", unitPiece: "แผ่น", approvedPieces: 1000 }}
        ]
      }}
    ];

    let cart = [];
    let currentCategory = 'ALL';
    let currentActiveReqForSig = null;

    // View Switching
    function switchView(viewName) {{
      document.querySelectorAll('.view-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.view-btn').forEach(el => el.classList.remove('active'));
      
      const targetView = document.getElementById(`view-${{viewName}}`);
      if (targetView) targetView.classList.add('active');

      const buttons = document.querySelectorAll('.view-btn');
      if (viewName === 'catalog') buttons[0].classList.add('active');
      if (viewName === 'staff') buttons[1].classList.add('active');
      if (viewName === 'inventory') buttons[2].classList.add('active');
      if (viewName === 'pdf') buttons[3].classList.add('active');
    }}

    // Format Stock Display
    function formatStockDisplay(totalPieces, ratio, boxName, pieceName, isMulti) {{
      if (!isMulti || ratio <= 1) {{
        return `${{totalPieces.toLocaleString()}} ${{pieceName}}`;
      }}
      const boxes = Math.floor(totalPieces / ratio);
      const pieces = totalPieces % ratio;
      if (boxes > 0 && pieces > 0) {{
        return `${{boxes}} ${{boxName}} ${{pieces}} ${{pieceName}}`;
      }} else if (boxes > 0) {{
        return `${{boxes}} ${{boxName}}`;
      }} else {{
        return `${{pieces}} ${{pieceName}}`;
      }}
    }}

    // Render Catalog Items
    function renderCatalog() {{
      const grid = document.getElementById('catalogGrid');
      const searchTerm = document.getElementById('itemSearchInput').value.trim().toLowerCase();

      const filtered = sampleItems.filter(item => {{
        const matchesCategory = currentCategory === 'ALL' || item.category === currentCategory;
        const matchesSearch = item.name.toLowerCase().includes(searchTerm);
        return matchesCategory && matchesSearch;
      }});

      if (filtered.length === 0) {{
        grid.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--neutral-400);">
            <div style="margin-bottom: 0.5rem;">${{vIcons.box}}</div>
            <p style="font-size: 1.1rem; font-weight: 500;">ไม่พบรายการพัสดุที่ตรงกับ "${{searchTerm}}"</p>
            <p style="font-size: 0.85rem;">ลองค้นหาด้วยคำอื่น เช่น ซอง, กระดาษ, แฟ้ม, 279, ครุฑ</p>
          </div>
        `;
        return;
      }}

      grid.innerHTML = filtered.map(item => {{
        const availablePieces = Math.max(0, item.on_hand_pieces - item.reserved_pieces);
        const stockStr = formatStockDisplay(
          availablePieces, item.pieces_per_box, item.unit_box_name, item.unit_piece_name, item.is_multi_unit
        );
        const imgSrc = item.current_img_mode === 'box' ? item.image_box : item.image_piece;

        return `
          <div class="item-card">
            <div class="item-image-wrapper">
              <img src="${{imgSrc}}" class="item-img" alt="${{item.name}}" onerror="this.src='assets/images/image1.jpeg'">
              ${{item.is_multi_unit ? `
                <div class="image-toggle-pills">
                  <button class="img-pill-btn ${{item.current_img_mode === 'piece' ? 'active' : ''}}" 
                          onclick="toggleItemImg(${{item.id}}, 'piece')">รูปชิ้น</button>
                  <button class="img-pill-btn ${{item.current_img_mode === 'box' ? 'active' : ''}}" 
                          onclick="toggleItemImg(${{item.id}}, 'box')">รูป${{item.unit_box_name}}</button>
                </div>
              ` : ''}}
            </div>

            <div class="card-body">
              <h3 class="item-title">${{item.name}}</h3>

              ${{item.is_multi_unit ? `
                <span class="ratio-badge">
                  ${{vIcons.layers}} 1 ${{item.unit_box_name}} = ${{item.pieces_per_box.toLocaleString()}} ${{item.unit_piece_name}}
                </span>
              ` : `
                <span class="ratio-badge">${{vIcons.tag}} หน่วยเดี่ยว: ${{item.unit_piece_name}}</span>
              `}}

              <div class="stock-info">
                <span class="stock-label">พร้อมเบิก (Available):</span>
                <span class="stock-value">${{stockStr}}</span>
              </div>

              <div class="card-actions">
                <div class="qty-inputs">
                  ${{item.is_multi_unit ? `
                    <div class="qty-col">
                      <label>จำนวน (${{item.unit_box_name}})</label>
                      <input type="number" id="qty-box-${{item.id}}" class="qty-input" min="0" placeholder="0">
                    </div>
                  ` : ''}}
                  <div class="qty-col" style="${{!item.is_multi_unit ? 'grid-column: span 2;' : ''}}">
                    <label>จำนวน (${{item.unit_piece_name}})</label>
                    <input type="number" id="qty-piece-${{item.id}}" class="qty-input" min="0" placeholder="0">
                  </div>
                </div>

                <button class="btn-add-cart" onclick="addToCart(${{item.id}})">
                  ${{vIcons.cart}} เพิ่มเข้าตะกร้า
                </button>
              </div>
            </div>
          </div>
        `;
      }}).join('');
    }}

    function toggleItemImg(itemId, mode) {{
      const item = sampleItems.find(i => i.id === itemId);
      if (item) {{
        item.current_img_mode = mode;
        renderCatalog();
      }}
    }}

    function handleSearch() {{
      renderCatalog();
    }}

    function filterCategory(cat, btn) {{
      currentCategory = cat;
      document.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderCatalog();
    }}

    // Cart Handlers
    function addToCart(itemId) {{
      const item = sampleItems.find(i => i.id === itemId);
      if (!item) return;

      const boxInput = document.getElementById(`qty-box-${{item.id}}`);
      const pieceInput = document.getElementById(`qty-piece-${{item.id}}`);

      const qtyBoxes = boxInput ? parseInt(boxInput.value || 0) : 0;
      const qtyPieces = pieceInput ? parseInt(pieceInput.value || 0) : 0;

      if (qtyBoxes <= 0 && qtyPieces <= 0) {{
        alert("กรุณาระบุจำนวนที่ต้องการเบิกอย่างน้อย 1 ชิ้นหรือกล่องครับ");
        return;
      }}

      const totalPieces = (qtyBoxes * item.pieces_per_box) + qtyPieces;
      const availablePieces = item.on_hand_pieces - item.reserved_pieces;

      if (totalPieces > availablePieces) {{
        alert(`ยอดคงเหลือพร้อมเบิกไม่เพียงพอ! (ขอเบิก ${{totalPieces}} ${{item.unit_piece_name}} แต่มีพร้อมเบิกเพียง ${{availablePieces}} ${{item.unit_piece_name}})`);
        return;
      }}

      const existing = cart.find(c => c.itemId === itemId);
      if (existing) {{
        existing.qtyBoxes += qtyBoxes;
        existing.qtyPieces += qtyPieces;
        existing.totalPieces += totalPieces;
      }} else {{
        cart.push({{
          itemId: item.id,
          name: item.name,
          unitBox: item.unit_box_name,
          unitPiece: item.unit_piece_name,
          qtyBoxes: qtyBoxes,
          qtyPieces: qtyPieces,
          totalPieces: totalPieces,
          is_multi: item.is_multi_unit
        }});
      }}

      if (boxInput) boxInput.value = '';
      if (pieceInput) pieceInput.value = '';

      updateCartBadge();
      renderCartDrawer();
      toggleCartDrawer(true);
    }}

    function updateCartBadge() {{
      document.getElementById('cartCount').innerText = cart.length;
    }}

    function toggleCartDrawer(forceOpen) {{
      const overlay = document.getElementById('cartOverlay');
      if (forceOpen === true) {{
        overlay.classList.add('open');
      }} else if (forceOpen === false) {{
        overlay.classList.remove('open');
      }} else {{
        overlay.classList.toggle('open');
      }}
    }}

    function renderCartDrawer() {{
      const list = document.getElementById('cartItemsList');
      if (cart.length === 0) {{
        list.innerHTML = `
          <div style="text-align: center; padding: 3rem 1rem; color: var(--neutral-400);">
            <div style="margin-bottom: 0.5rem;">${{vIcons.cart}}</div>
            <p>ยังไม่มีรายการพัสดุในตะกร้า</p>
          </div>
        `;
        return;
      }}

      list.innerHTML = cart.map((c, idx) => {{
        let qtyText = "";
        if (c.qtyBoxes > 0 && c.qtyPieces > 0) {{
          qtyText = `${{c.qtyBoxes}} ${{c.unitBox}} + ${{c.qtyPieces}} ${{c.unitPiece}} (รวม ${{c.totalPieces.toLocaleString()}} ${{c.unitPiece}})`;
        }} else if (c.qtyBoxes > 0) {{
          qtyText = `${{c.qtyBoxes}} ${{c.unitBox}} (รวม ${{c.totalPieces.toLocaleString()}} ${{c.unitPiece}})`;
        }} else {{
          qtyText = `${{c.qtyPieces}} ${{c.unitPiece}}`;
        }}

        return `
          <div class="cart-item-card">
            <div class="cart-item-details">
              <h4>${{c.name}}</h4>
              <div class="cart-item-qty">จำนวนที่ขอเบิก: <strong>${{qtyText}}</strong></div>
            </div>
            <button class="cart-item-remove" onclick="removeCartItem(${{idx}})" title="ลบออก">
              ${{vIcons.trash}}
            </button>
          </div>
        `;
      }}).join('');
    }}

    function removeCartItem(idx) {{
      cart.splice(idx, 1);
      updateCartBadge();
      renderCartDrawer();
    }}

    function submitRequisition() {{
      const dept = document.getElementById('deptSelect').value;
      const requester = document.getElementById('requesterName').value.trim();
      const phone = document.getElementById('requesterPhone').value.trim();
      const purpose = document.getElementById('cartPurpose').value.trim();

      if (!requester) {{
        alert("กรุณากรอกชื่อ-นามสกุล ผู้ขอเบิกครับ");
        return;
      }}
      if (cart.length === 0) {{
        alert("ไม่มีรายการพัสดุในตะกร้า");
        return;
      }}
      if (!purpose) {{
        alert("กรุณาระบุวัตถุประสงค์ในการเบิกใช้งานครับ");
        return;
      }}

      const randomNo = Math.floor(1000 + Math.random() * 9000);
      const newDocNo = `REQ-256910-${{randomNo}}`;

      const newReq = {{
        id: newDocNo,
        dept: dept,
        requester: requester,
        phone: phone,
        purpose: purpose,
        date: "21 ต.ค. 2569 11:10 น.",
        status: "PENDING",
        signature: null,
        items: cart.map(c => ({{
          itemId: c.itemId,
          name: c.name,
          qtyBoxes: c.qtyBoxes,
          qtyPieces: c.qtyPieces,
          totalPieces: c.totalPieces,
          unitBox: c.unitBox,
          unitPiece: c.unitPiece,
          approvedPieces: c.totalPieces
        }}))
      }};

      requisitions.unshift(newReq);
      cart = [];
      document.getElementById('cartPurpose').value = '';
      updateCartBadge();
      toggleCartDrawer(false);

      alert(`ส่งคำขอเบิกพัสดุสำเร็จ!\nเลขที่เอกสาร: ${{newDocNo}}\nระบบได้ส่งคำขอไปยังเจ้าหน้าที่พัสดุเรียบร้อยแล้ว`);

      renderRequisitions('PENDING');
      switchView('staff');
    }}

    // Staff Requisition View
    function filterRequisitionStatus(status, btn) {{
      document.querySelectorAll('.status-tab').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderRequisitions(status);
    }}

    function renderRequisitions(status) {{
      const container = document.getElementById('requisitionsContainer');
      const filtered = requisitions.filter(r => r.status === status);

      document.getElementById('pendingCount').innerText = requisitions.filter(r => r.status === 'PENDING').length;
      document.getElementById('approvedCount').innerText = requisitions.filter(r => r.status === 'APPROVED').length;
      document.getElementById('completedCount').innerText = requisitions.filter(r => r.status === 'COMPLETED').length;

      if (filtered.length === 0) {{
        container.innerHTML = `
          <div style="background: white; border-radius: var(--radius); padding: 3rem; text-align: center; color: var(--neutral-400); border: 1px dashed var(--neutral-300);">
            <div style="margin-bottom: 0.5rem;">${{vIcons.fileText}}</div>
            <p>ไม่มีรายการคำขอในสถานะนี้</p>
          </div>
        `;
        return;
      }}

      container.innerHTML = filtered.map(req => {{
        let badgeClass = 'badge-pending';
        let badgeText = 'รออนุมัติ (Pending)';
        if (req.status === 'APPROVED') {{
          badgeClass = 'badge-approved';
          badgeText = 'อนุมัติแล้ว รอผู้เบิกมารับของ';
        }} else if (req.status === 'COMPLETED') {{
          badgeClass = 'badge-completed';
          badgeText = 'จ่ายของสำเร็จแล้ว (Completed)';
        }}

        return `
          <div class="requisition-card">
            <div class="req-top-row">
              <div class="req-doc-id">
                ${{vIcons.fileText}} ${{req.id}}
                <span class="req-badge ${{badgeClass}}">${{badgeText}}</span>
              </div>
              <span style="font-size: 0.8rem; color: var(--neutral-400); display: flex; align-items: center; gap: 4px;">
                ${{vIcons.calendar}} วันที่ขอ: ${{req.date}}
              </span>
            </div>

            <div class="req-details-grid">
              <div>${{vIcons.building}} <strong>หน่วยงาน:</strong> ${{req.dept}}</div>
              <div>${{vIcons.user}} <strong>ผู้ขอเบิก:</strong> ${{req.requester}} (${{req.phone || '-'}})</div>
              <div style="grid-column: 1 / -1;">${{vIcons.fileText}} <strong>วัตถุประสงค์:</strong> ${{req.purpose}}</div>
            </div>

            <table class="req-table">
              <thead>
                <tr>
                  <th>รายการพัสดุ</th>
                  <th style="width: 140px;">จำนวนที่ขอ</th>
                  <th style="width: 140px;">จำนวนจ่ายจริง</th>
                  <th style="width: 100px;">สถานะ</th>
                </tr>
              </thead>
              <tbody>
                ${{req.items.map(item => `
                  <tr>
                    <td><strong>${{item.name}}</strong></td>
                    <td>${{item.qtyBoxes > 0 ? `${{item.qtyBoxes}} ${{item.unitBox}} ` : ''}}${{item.qtyPieces > 0 ? `${{item.qtyPieces}} ${{item.unitPiece}}` : ''}}</td>
                    <td style="font-weight: 600; color: var(--accent);">${{item.approvedPieces.toLocaleString()}} ${{item.unitPiece}}</td>
                    <td><span style="color: var(--accent);">พร้อมจ่าย</span></td>
                  </tr>
                `).join('')}}
              </tbody>
            </table>

            <div class="req-actions">
              ${{req.status === 'PENDING' ? `
                <button class="btn btn-outline" style="color: var(--danger);" onclick="rejectRequisition('${{req.id}}')">
                  ${{vIcons.x}} ปฏิเสธคำขอ
                </button>
                <button class="btn btn-primary" onclick="approveRequisition('${{req.id}}')">
                  ${{vIcons.check}} อนุมัติคำขอ (กันสต๊อก)
                </button>
              ` : ''}}

              ${{req.status === 'APPROVED' ? `
                <button class="btn btn-outline" onclick="previewDocInPdf('${{req.id}}')">
                  ${{vIcons.eye}} ดูตัวอย่างใบเบิก PDF
                </button>
                <button class="btn btn-success" onclick="openSignatureModal('${{req.id}}')">
                  ${{vIcons.pen}} จ่ายของและเซ็นชื่อรับ (E-Signature)
                </button>
              ` : ''}}

              ${{req.status === 'COMPLETED' ? `
                <button class="btn btn-outline" onclick="previewDocInPdf('${{req.id}}')">
                  ${{vIcons.printer}} พิมพ์ใบเบิก PDF (มีลายเซ็นแล้ว)
                </button>
              ` : ''}}
            </div>
          </div>
        `;
      }}).join('');
    }}

    function approveRequisition(docNo) {{
      const req = requisitions.find(r => r.id === docNo);
      if (req) {{
        req.status = 'APPROVED';
        req.items.forEach(i => {{
          const itm = sampleItems.find(si => si.id === i.itemId);
          if (itm) itm.reserved_pieces += i.approvedPieces;
        }});
        alert(`อนุมัติคำขอ ${{docNo}} สำเร็จ! ระบบได้กันยอดสต๊อก (Reserved) ไว้เรียบร้อย`);
        renderRequisitions('PENDING');
        renderInventoryTable();
        renderCatalog();
      }}
    }}

    function rejectRequisition(docNo) {{
      const reason = prompt("ระบุเหตุผลในการปฏิเสธคำขอเบิก:", "พัสดุในคลังไม่เพียงพอ");
      if (reason) {{
        const req = requisitions.find(r => r.id === docNo);
        if (req) {{
          req.status = 'REJECTED';
          alert(`ปฏิเสธคำขอ ${{docNo}} เรียบร้อยแล้ว`);
          renderRequisitions('PENDING');
        }}
      }}
    }}

    // ==========================================
    // E-SIGNATURE CANVAS LOGIC
    // ==========================================
    let canvas, ctx, isDrawing = false;

    function initSignaturePad() {{
      canvas = document.getElementById('signaturePad');
      ctx = canvas.getContext('2d');

      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * 2;
      canvas.height = rect.height * 2;
      ctx.scale(2, 2);

      ctx.strokeStyle = '#0f172a';
      ctx.lineWidth = 2.5;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      function getPos(e) {{
        const r = canvas.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        return {{
          x: clientX - r.left,
          y: clientY - r.top
        }};
      }}

      function startDraw(e) {{
        e.preventDefault();
        isDrawing = true;
        const pos = getPos(e);
        ctx.beginPath();
        ctx.moveTo(pos.x, pos.y);
        document.getElementById('sigPlaceholder').style.display = 'none';
      }}

      function draw(e) {{
        if (!isDrawing) return;
        e.preventDefault();
        const pos = getPos(e);
        ctx.lineTo(pos.x, pos.y);
        ctx.stroke();
      }}

      function stopDraw(e) {{
        if (isDrawing) {{
          isDrawing = false;
          ctx.closePath();
        }}
      }}

      canvas.addEventListener('mousedown', startDraw);
      canvas.addEventListener('mousemove', draw);
      canvas.addEventListener('mouseup', stopDraw);
      canvas.addEventListener('mouseleave', stopDraw);

      canvas.addEventListener('touchstart', startDraw, {{ passive: false }});
      canvas.addEventListener('touchmove', draw, {{ passive: false }});
      canvas.addEventListener('touchend', stopDraw);
    }}

    function openSignatureModal(docNo) {{
      currentActiveReqForSig = requisitions.find(r => r.id === docNo);
      if (!currentActiveReqForSig) return;

      document.getElementById('sigModalRequesterName').innerText = currentActiveReqForSig.requester;
      document.getElementById('sigModalDocNo').innerText = currentActiveReqForSig.id;

      const modal = document.getElementById('signatureModal');
      modal.classList.add('open');

      setTimeout(() => {{
        initSignaturePad();
        clearSignature();
      }}, 100);
    }}

    function closeSignatureModal() {{
      document.getElementById('signatureModal').classList.remove('open');
    }}

    function clearSignature() {{
      if (ctx && canvas) {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        document.getElementById('sigPlaceholder').style.display = 'block';
      }}
    }}

    function confirmSignatureAndComplete() {{
      if (!currentActiveReqForSig) return;

      const sigDataUrl = canvas.toDataURL('image/png');
      currentActiveReqForSig.signature = sigDataUrl;
      currentActiveReqForSig.status = 'COMPLETED';

      currentActiveReqForSig.items.forEach(i => {{
        const itm = sampleItems.find(si => si.id === i.itemId);
        if (itm) {{
          itm.on_hand_pieces -= i.approvedPieces;
          itm.reserved_pieces -= i.approvedPieces;
        }}
      }});

      closeSignatureModal();
      alert(`บันทึกการจ่ายของและเซ็นชื่อรับมอบสำเร็จ!\nตัดยอดสต๊อกเรียบร้อยแล้ว`);

      previewDocInPdf(currentActiveReqForSig.id);
      renderRequisitions('APPROVED');
      renderInventoryTable();
      renderCatalog();
    }}

    // View PDF Preview
    function previewDocInPdf(docNo) {{
      const req = requisitions.find(r => r.id === docNo);
      if (!req) return;

      document.getElementById('pdfDocNo').innerText = req.id;
      document.getElementById('pdfDept').innerText = req.dept;
      document.getElementById('pdfRequester').innerText = req.requester;
      document.getElementById('pdfPurpose').innerText = req.purpose;
      document.getElementById('pdfSignRequester').innerText = req.requester;
      document.getElementById('pdfReceiverName').innerText = req.requester;

      const tbody = document.getElementById('pdfItemsTbody');
      tbody.innerHTML = req.items.map((item, idx) => `
        <tr>
          <td style="text-align: center;">${{idx + 1}}</td>
          <td>${{item.name}}</td>
          <td style="text-align: center;">${{item.qtyBoxes > 0 ? `${{item.qtyBoxes}} ${{item.unitBox}} ` : ''}}${{item.qtyPieces > 0 ? `${{item.qtyPieces}} ${{item.unitPiece}}` : ''}}</td>
          <td style="text-align: center; font-weight: bold; color: #166534;">${{item.approvedPieces.toLocaleString()}} ${{item.unitPiece}}</td>
          <td style="text-align: center;">ครบถ้วน</td>
        </tr>
      `).join('');

      const sigArea = document.getElementById('pdfReceiverSigArea');
      if (req.signature) {{
        sigArea.innerHTML = `<img src="${{req.signature}}" class="sig-img-preview" alt="ลายเซ็นดิจิทัล">`;
        document.getElementById('pdfReceiveTime').innerText = `เซ็นรับเมื่อ: 21 ต.ค. 2569 (E-Signature)`;
      }} else {{
        sigArea.innerHTML = `
          <div style="height: 50px; display: flex; align-items: center; justify-content: center; color: #999; font-style: italic;">
            [ ยังไม่ได้เซ็นรับของ ]
          </div>
        `;
        document.getElementById('pdfReceiveTime').innerText = `วันที่รับของจริง: .......................................`;
      }}

      switchView('pdf');
    }}

    // Render Inventory Table
    function renderInventoryTable() {{
      const tbody = document.getElementById('inventoryTableBody');
      tbody.innerHTML = sampleItems.map((item, idx) => {{
        const available = Math.max(0, item.on_hand_pieces - item.reserved_pieces);
        const isLowStock = available <= item.min_alert;

        return `
          <tr>
            <td style="text-align: center;">${{idx + 1}}</td>
            <td><strong>${{item.name}}</strong></td>
            <td>${{item.is_multi_unit ? `1 ${{item.unit_box_name}} = ${{item.pieces_per_box}} ${{item.unit_piece_name}}` : `หน่วยเดี่ยว (${{item.unit_piece_name}})`}}</td>
            <td>${{item.on_hand_pieces.toLocaleString()}} ${{item.unit_piece_name}}</td>
            <td style="color: var(--primary); font-weight: 500;">${{item.reserved_pieces.toLocaleString()}} ${{item.unit_piece_name}}</td>
            <td style="font-weight: 700; color: ${{isLowStock ? 'var(--danger)' : 'var(--accent)'}};">
              ${{formatStockDisplay(available, item.pieces_per_box, item.unit_box_name, item.unit_piece_name, item.is_multi_unit)}}
            </td>
            <td>
              ${{isLowStock ? `
                <span style="background: var(--danger-light); color: var(--danger); font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 999px;">
                  ต่ำกว่าเกณฑ์ (${{item.min_alert}})
                </span>
              ` : `
                <span style="background: #dcfce7; color: #166534; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 999px;">
                  ปกติ
                </span>
              `}}
            </td>
          </tr>
        `;
      }}).join('');
    }}

    // Initial Load
    document.addEventListener('DOMContentLoaded', () => {{
      renderCatalog();
      renderRequisitions('PENDING');
      renderInventoryTable();
    }});
  </script>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Successfully updated index.html with searchable department combobox!")
