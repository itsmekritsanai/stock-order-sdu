"""
Shared Vector SVG Icons, Universal Searchable Dropdown & Dynamic Calendar Month Helpers
(scripts/portal_parts/shared_ui.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

# Common SVG vector icons
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
    "edit": '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>',
    "lock": '<svg class="svg-icon" viewBox="0 0 24 24"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
    "log_out": '<svg class="svg-icon svg-icon-sm" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>',
    "info": '<svg class="svg-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="16" y2="12"/><line x1="12" x2="12.01" y1="8" y2="8"/></svg>',
    "list": '<svg class="svg-icon" viewBox="0 0 24 24"><line x1="8" x2="21" y1="6" y2="6"/><line x1="8" x2="21" y1="12" y2="12"/><line x1="8" x2="21" y1="18" y2="18"/><line x1="3" x2="3.01" y1="6" y2="6"/><line x1="3" x2="3.01" y1="12" y2="12"/><line x1="3" x2="3.01" y1="18" y2="18"/></svg>'
}

SEARCHABLE_SELECT_CSS = r'''
    /* Universal Searchable Dropdown Widget */
    .sdu-ss-wrapper {
      position: relative;
      display: inline-block;
      width: 100%;
      font-family: inherit;
      text-align: left;
    }
    .sdu-ss-wrapper.sdu-ss-auto {
      width: auto;
      min-width: 160px;
    }
    .sdu-ss-trigger {
      width: 100%;
      min-height: 38px;
      padding: 0.45rem 0.7rem;
      background: white;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      color: #1e293b;
      font-family: inherit;
      font-size: 0.875rem;
      text-align: left;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      cursor: pointer;
      transition: border-color 0.15s, box-shadow 0.15s;
      box-sizing: border-box;
    }
    .sdu-ss-trigger:hover { border-color: #94a3b8; }
    .sdu-ss-trigger.open, .sdu-ss-trigger:focus {
      outline: none;
      border-color: #1e40af;
      box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.12);
    }
    .sdu-ss-trigger-label {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      flex: 1;
      min-width: 0;
    }
    .sdu-ss-chevron {
      width: 15px;
      height: 15px;
      color: #64748b;
      flex-shrink: 0;
      transition: transform 0.15s;
    }
    .sdu-ss-trigger.open .sdu-ss-chevron {
      transform: rotate(180deg);
      color: #1e40af;
    }
    .sdu-ss-panel {
      position: fixed;
      z-index: 99999;
      background: white;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      box-shadow: 0 12px 28px -4px rgba(15, 23, 42, 0.22), 0 4px 10px rgba(15, 23, 42, 0.08);
      display: none;
      flex-direction: column;
      overflow: hidden;
      font-family: 'Prompt', 'Sarabun', sans-serif;
      box-sizing: border-box;
    }
    .sdu-ss-panel.open { display: flex; }
    .sdu-ss-search-wrap {
      padding: 8px;
      background: #f8fafc;
      border-bottom: 1px solid #e2e8f0;
    }
    .sdu-ss-search-input {
      width: 100%;
      padding: 6px 10px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      font-family: inherit;
      font-size: 0.85rem;
      color: #0f172a;
      background: white;
      outline: none;
      box-sizing: border-box;
    }
    .sdu-ss-search-input:focus {
      border-color: #1e40af;
      box-shadow: 0 0 0 2px rgba(30, 64, 175, 0.12);
    }
    .sdu-ss-list {
      max-height: 230px;
      overflow-y: auto;
      padding: 4px;
    }
    .sdu-ss-item {
      padding: 7px 10px;
      border-radius: 6px;
      font-size: 0.85rem;
      color: #1e293b;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
      line-height: 1.35;
      text-align: left;
    }
    .sdu-ss-item:hover, .sdu-ss-item.highlighted {
      background: #eff6ff;
      color: #1e40af;
    }
    .sdu-ss-item.selected {
      background: #dbeafe;
      color: #1e40af;
      font-weight: 600;
    }
    .sdu-ss-empty {
      padding: 14px 10px;
      text-align: center;
      font-size: 0.825rem;
      color: #94a3b8;
    }
'''

SEARCHABLE_SELECT_JS = r'''
    // Universal Searchable Dropdown Enhancer (Zero-Build Vanilla JS)
    let _activeSearchablePanel = null;
    let _activeSearchableTrigger = null;

    function closeActiveSearchableSelect() {
      if (_activeSearchablePanel) {
        _activeSearchablePanel.classList.remove('open');
        if (_activeSearchablePanel.parentNode) {
          _activeSearchablePanel.parentNode.removeChild(_activeSearchablePanel);
        }
        _activeSearchablePanel = null;
      }
      if (_activeSearchableTrigger) {
        _activeSearchableTrigger.classList.remove('open');
        _activeSearchableTrigger = null;
      }
    }

    document.addEventListener('click', (e) => {
      if (_activeSearchableTrigger && !document.body.contains(_activeSearchableTrigger)) {
        closeActiveSearchableSelect();
        return;
      }
      if (_activeSearchablePanel && !_activeSearchablePanel.contains(e.target) && (!_activeSearchableTrigger || !_activeSearchableTrigger.contains(e.target))) {
        closeActiveSearchableSelect();
      }
    });

    document.addEventListener('scroll', (e) => {
      if (_activeSearchablePanel && !_activeSearchablePanel.contains(e.target)) {
        closeActiveSearchableSelect();
      }
    }, true);

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && _activeSearchablePanel) {
        closeActiveSearchableSelect();
      }
    });

    window.addEventListener('resize', closeActiveSearchableSelect);

    function enhanceSearchableSelect(selectEl) {
      if (!selectEl || selectEl.tagName !== 'SELECT') return;
      if (selectEl.getAttribute('data-searchable-enhanced') === 'true') {
        if (typeof selectEl._syncSearchableLabel === 'function') selectEl._syncSearchableLabel();
        return;
      }
      if (selectEl.getAttribute('data-no-search') === 'true' || selectEl.multiple) return;
      // Skip hidden placeholder selects such as SweetAlert2's empty built-in #swal2-select
      if (selectEl.style.display === 'none') return;
      if (selectEl.id === 'swal2-select' && (!selectEl.options || selectEl.options.length === 0)) return;
      selectEl.setAttribute('data-searchable-enhanced', 'true');

      const wrapper = document.createElement('div');
      const isAutoWidth = selectEl.style.width === 'auto' || selectEl.id === 'staffRoleSelect' || selectEl.id === 'staffReqMonthFilter' || selectEl.id === 'analyticsMonthSelect' || selectEl.id === 'myReqsMonthSelect';
      wrapper.className = 'sdu-ss-wrapper' + (isAutoWidth ? ' sdu-ss-auto' : '');
      if (selectEl.style.minWidth) wrapper.style.minWidth = selectEl.style.minWidth;

      const trigger = document.createElement('button');
      trigger.type = 'button';
      trigger.className = 'sdu-ss-trigger';
      if (selectEl.id) trigger.setAttribute('data-for-select', selectEl.id);
      if (selectEl.style.height) trigger.style.minHeight = selectEl.style.height;
      if (selectEl.style.fontSize) trigger.style.fontSize = selectEl.style.fontSize;
      if (selectEl.style.padding) trigger.style.padding = selectEl.style.padding;

      const labelSpan = document.createElement('span');
      labelSpan.className = 'sdu-ss-trigger-label';
      const chevronSvg = `<svg class="sdu-ss-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>`;
      trigger.appendChild(labelSpan);
      trigger.insertAdjacentHTML('beforeend', chevronSvg);

      const protoDesc = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value');
      const syncLabel = () => {
        const opts = Array.from(selectEl.options || []);
        const currentVal = protoDesc && protoDesc.get ? protoDesc.get.call(selectEl) : selectEl.value;
        const selectedOpt = opts.find(o => o.value === currentVal) || opts[selectEl.selectedIndex] || opts[0];
        labelSpan.textContent = selectedOpt ? selectedOpt.textContent : 'เลือกรายการ...';
        trigger.title = labelSpan.textContent;
      };
      selectEl._syncSearchableLabel = syncLabel;

      if (protoDesc && protoDesc.get && protoDesc.set) {
        Object.defineProperty(selectEl, 'value', {
          configurable: true,
          get() { return protoDesc.get.call(this); },
          set(v) {
            protoDesc.set.call(this, v);
            syncLabel();
          }
        });
      }

      const observer = new MutationObserver(() => syncLabel());
      observer.observe(selectEl, { childList: true, subtree: true, attributes: true });

      selectEl.parentNode.insertBefore(wrapper, selectEl);
      wrapper.appendChild(trigger);
      wrapper.appendChild(selectEl);
      selectEl.style.display = 'none';
      syncLabel();

      trigger.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (_activeSearchableTrigger === trigger) {
          closeActiveSearchableSelect();
          return;
        }
        closeActiveSearchableSelect();

        const panel = document.createElement('div');
        panel.className = 'sdu-ss-panel open';
        panel.innerHTML = `
          <div class="sdu-ss-search-wrap">
            <input type="text" class="sdu-ss-search-input" placeholder="พิมพ์คำค้นหาในรายการ..." autocomplete="off">
          </div>
          <div class="sdu-ss-list"></div>
        `;

        const mountHost = selectEl.closest('.swal2-popup') || document.body;
        mountHost.appendChild(panel);
        _activeSearchablePanel = panel;
        _activeSearchableTrigger = trigger;
        trigger.classList.add('open');

        const rect = trigger.getBoundingClientRect();
        const panelWidth = Math.max(rect.width, 230);
        const spaceBelow = window.innerHeight - rect.bottom - 10;
        const spaceAbove = rect.top - 10;
        const openAbove = spaceBelow < 220 && spaceAbove > spaceBelow;
        panel.style.width = `${Math.min(panelWidth, window.innerWidth - 20)}px`;
        panel.style.left = `${Math.max(10, Math.min(rect.left, window.innerWidth - Math.min(panelWidth, window.innerWidth - 20) - 10))}px`;
        if (openAbove) {
          panel.style.bottom = `${window.innerHeight - rect.top + 4}px`;
          panel.style.top = 'auto';
        } else {
          panel.style.top = `${rect.bottom + 4}px`;
          panel.style.bottom = 'auto';
        }

        const searchInput = panel.querySelector('.sdu-ss-search-input');
        const listEl = panel.querySelector('.sdu-ss-list');
        let highlightedIdx = -1;

        const renderOptions = (filterText = '') => {
          const clean = filterText.trim().toLowerCase();
          const currentVal = selectEl.value;
          const opts = Array.from(selectEl.options || []).filter(o => !o.disabled);
          const matched = opts.filter(o =>
            !clean ||
            (o.textContent && o.textContent.toLowerCase().includes(clean)) ||
            (o.value && o.value.toLowerCase().includes(clean))
          );
          if (matched.length === 0) {
            listEl.innerHTML = `<div class="sdu-ss-empty">ไม่พบตัวเลือกที่ตรงกับ "${filterText.replace(/</g, '&lt;')}"</div>`;
            highlightedIdx = -1;
            return;
          }
          listEl.innerHTML = '';
          matched.forEach((opt, idx) => {
            const item = document.createElement('div');
            const isSel = opt.value === currentVal;
            item.className = 'sdu-ss-item' + (isSel ? ' selected' : '') + (idx === highlightedIdx ? ' highlighted' : '');
            const textSpan = document.createElement('span');
            textSpan.textContent = opt.textContent;
            item.appendChild(textSpan);
            if (isSel) {
              item.insertAdjacentHTML('beforeend', `<svg style="width:14px;height:14px;flex-shrink:0;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`);
            }
            item.addEventListener('click', (ev) => {
              ev.stopPropagation();
              opt.selected = true;
              selectEl.value = opt.value;
              syncLabel();
              closeActiveSearchableSelect();
              selectEl.dispatchEvent(new Event('change', { bubbles: true }));
            });
            listEl.appendChild(item);
          });
        };

        renderOptions('');
        setTimeout(() => searchInput.focus(), 10);

        searchInput.addEventListener('click', (ev) => ev.stopPropagation());
        searchInput.addEventListener('input', () => {
          highlightedIdx = 0;
          renderOptions(searchInput.value);
        });
        searchInput.addEventListener('keydown', (ev) => {
          const items = listEl.querySelectorAll('.sdu-ss-item');
          if (ev.key === 'ArrowDown') {
            ev.preventDefault();
            if (items.length > 0) {
              highlightedIdx = (highlightedIdx + 1) % items.length;
              items.forEach((el, i) => el.classList.toggle('highlighted', i === highlightedIdx));
              if (items[highlightedIdx]) items[highlightedIdx].scrollIntoView({ block: 'nearest' });
            }
          } else if (ev.key === 'ArrowUp') {
            ev.preventDefault();
            if (items.length > 0) {
              highlightedIdx = highlightedIdx <= 0 ? items.length - 1 : highlightedIdx - 1;
              items.forEach((el, i) => el.classList.toggle('highlighted', i === highlightedIdx));
              if (items[highlightedIdx]) items[highlightedIdx].scrollIntoView({ block: 'nearest' });
            }
          } else if (ev.key === 'Enter') {
            ev.preventDefault();
            const targetItem = (highlightedIdx >= 0 && items[highlightedIdx]) ? items[highlightedIdx] : items[0];
            if (targetItem) targetItem.click();
          } else if (ev.key === 'Escape') {
            ev.preventDefault();
            closeActiveSearchableSelect();
          }
        });
      });
    }

    function enhanceAllSearchableSelects(root = document) {
      if (!root || !root.querySelectorAll) return;
      root.querySelectorAll('select').forEach(sel => enhanceSearchableSelect(sel));
    }

    document.addEventListener('DOMContentLoaded', () => {
      enhanceAllSearchableSelects(document);
      const bodyObserver = new MutationObserver((mutations) => {
        for (const m of mutations) {
          m.addedNodes.forEach(node => {
            if (node && node.nodeType === 1) {
              if (node.tagName === 'SELECT') enhanceSearchableSelect(node);
              else if (node.querySelectorAll) enhanceAllSearchableSelects(node);
            }
          });
        }
      });
      if (document.body) {
        bodyObserver.observe(document.body, { childList: true, subtree: true });
      }
    });
'''

DYNAMIC_MONTH_JS = r'''
    // Dynamic Auto-Updating Month Dropdowns (Current Calendar Month + Rolling 12 Months + Historical Data)
    const THAI_FULL_MONTH_NAMES = [
      'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
      'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม'
    ];

    function getCurrentMonthKey() {
      const now = new Date();
      const y = now.getFullYear();
      const m = String(now.getMonth() + 1).padStart(2, '0');
      return `${y}-${m}`;
    }

    function formatThaiMonthOption(ymKey, currentKey, markCurrent = false) {
      const m = /^(\d{4})-(\d{2})$/.exec(String(ymKey || ''));
      if (!m) return String(ymKey || '');
      const yr = parseInt(m[1], 10);
      const mo = parseInt(m[2], 10);
      const mName = THAI_FULL_MONTH_NAMES[mo - 1] || m[2];
      const beYear = yr + 543;
      return `${mName} ${beYear}${markCurrent && ymKey === currentKey ? ' (เดือนปัจจุบัน)' : ''}`;
    }

    function extractMonthKeyFromRecord(rec) {
      if (!rec || typeof rec !== 'object') return null;
      const iso = String(rec.created_at || rec.createdAt || '').trim();
      const isoMatch = /^(\d{4})-(\d{2})/.exec(iso);
      if (isoMatch) {
        const mo = parseInt(isoMatch[2], 10);
        if (mo >= 1 && mo <= 12) return `${isoMatch[1]}-${isoMatch[2]}`;
      }
      const docId = String(rec.id || rec.referenceId || '').trim().toUpperCase();
      const idMatch = /^REQ-(\d{4})(\d{2})/.exec(docId);
      if (idMatch) {
        const rawYr = parseInt(idMatch[1], 10);
        const ceYr = rawYr > 2400 ? rawYr - 543 : rawYr;
        const mo = parseInt(idMatch[2], 10);
        if (ceYr >= 2000 && ceYr <= 2150 && mo >= 1 && mo <= 12) {
          return `${ceYr}-${String(mo).padStart(2, '0')}`;
        }
      }
      return null;
    }

    function collectAvailableMonthKeys(lookbackMonths = 12) {
      const now = new Date();
      const monthSet = new Set();
      for (let i = 0; i < lookbackMonths; i++) {
        const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        monthSet.add(`${y}-${m}`);
      }
      try {
        if (typeof getReqsDB === 'function') {
          (getReqsDB() || []).forEach(r => {
            const k = extractMonthKeyFromRecord(r);
            if (k) monthSet.add(k);
          });
        }
      } catch (e) {}
      try {
        if (typeof getTransactionsDB === 'function') {
          (getTransactionsDB() || []).forEach(tx => {
            const k = extractMonthKeyFromRecord(tx);
            if (k) monthSet.add(k);
          });
        }
      } catch (e) {}
      return Array.from(monthSet).sort((a, b) => b.localeCompare(a));
    }

    function populateDynamicMonthSelect(selectId, config = {}) {
      const selectEl = document.getElementById(selectId);
      if (!selectEl) return;
      const currentKey = getCurrentMonthKey();
      const monthKeys = collectAvailableMonthKeys(config.lookbackMonths || 12);
      const allLabel = config.allLabel || 'ดูทุกเดือนย้อนหลัง';
      const allPosition = config.allPosition || 'top';
      const markCurrent = Boolean(config.markCurrent);

      const wasInit = selectEl.dataset.monthInitialized === 'true';
      const prevVal = wasInit ? selectEl.value : currentKey;

      const options = [];
      if (allPosition === 'top') {
        options.push({ value: 'ALL', label: allLabel });
      }
      monthKeys.forEach(k => {
        options.push({ value: k, label: formatThaiMonthOption(k, currentKey, markCurrent) });
      });
      if (allPosition === 'bottom') {
        options.push({ value: 'ALL', label: allLabel });
      }

      const signature = options.map(o => `${o.value}:${o.label}`).join('|');
      if (selectEl.dataset.monthOptionsSig !== signature) {
        selectEl.innerHTML = options.map(o => `<option value="${o.value}">${o.label}</option>`).join('');
        selectEl.dataset.monthOptionsSig = signature;
      }

      const hasPrev = options.some(o => o.value === prevVal);
      selectEl.value = hasPrev ? prevVal : currentKey;
      selectEl.dataset.monthInitialized = 'true';
      if (typeof selectEl._syncSearchableLabel === 'function') {
        selectEl._syncSearchableLabel();
      }
    }

    function refreshAllMonthDropdowns() {
      populateDynamicMonthSelect('myReqsMonthSelect', {
        allPosition: 'top',
        allLabel: 'ทุกเดือนย้อนหลัง',
        markCurrent: true
      });
      populateDynamicMonthSelect('staffReqMonthFilter', {
        allPosition: 'top',
        allLabel: 'ดูทุกเดือนย้อนหลัง',
        markCurrent: true
      });
      populateDynamicMonthSelect('analyticsMonthSelect', {
        allPosition: 'bottom',
        allLabel: 'ภาพรวมข้อมูลย้อนหลังทั้งหมด',
        markCurrent: true
      });
    }
'''
