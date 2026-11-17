"""
Zero-Dependency Native OpenXML (.xlsx) Generator (backend/excel_export.py)
Generates clean, multi-sheet Microsoft Excel workbooks (.xlsx) using Python's
built-in zipfile and xml.sax.saxutils without external packages.
"""

import io
import re
import zipfile
from xml.sax.saxutils import escape

_INVALID_XML_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _xml_safe(value) -> str:
    txt = "" if value is None else str(value)
    return escape(_INVALID_XML_RE.sub("", txt))


def _col_letter(idx: int) -> str:
    result = []
    n = idx
    while n > 0:
        n, rem = divmod(n - 1, 26)
        result.append(chr(65 + rem))
    return "".join(reversed(result))


def _visual_len(value) -> float:
    """Estimate Excel column width accounting for Thai combining vowel/tone marks."""
    txt = "" if value is None else str(value)
    lines = txt.splitlines() or [""]
    best = 0.0
    for line in lines:
        score = 0.0
        for ch in line:
            code = ord(ch)
            # Thai tone/upper/lower marks occupy zero horizontal width
            if code in (0x0E31, 0x0E34, 0x0E35, 0x0E36, 0x0E37, 0x0E38, 0x0E39, 0x0E3A) or (0x0E47 <= code <= 0x0E4E):
                continue
            score += 1.08
        if score > best:
            best = score
    return best


def _estimate_widths(rows_spec, base_widths):
    widths = dict(base_widths)
    for _r, _h, cells in rows_spec:
        for col_idx, val, style_id, is_num in cells:
            # Skip wide merged banner rows from blowing up col A width
            if style_id in (1, 2, 3):
                continue
            v_len = _visual_len(f"{val:,}" if is_num and isinstance(val, (int, float)) else val) + 4.0
            if col_idx not in widths or v_len > widths[col_idx]:
                widths[col_idx] = min(56.0, max(widths.get(col_idx, 10.0), v_len))
    return widths


def _build_styles_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <numFmts count="1">
    <numFmt numFmtId="164" formatCode="#,##0"/>
  </numFmts>
  <fonts count="6">
    <font><sz val="11"/><name val="Tahoma"/></font>
    <font><b/><sz val="14"/><color rgb="FFFFFFFF"/><name val="Tahoma"/></font>
    <font><b/><sz val="11"/><color rgb="FF1E3A8A"/><name val="Tahoma"/></font>
    <font><b/><sz val="11"/><color rgb="FF0F172A"/><name val="Tahoma"/></font>
    <font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Tahoma"/></font>
    <font><b/><sz val="11"/><color rgb="FFB45309"/><name val="Tahoma"/></font>
  </fonts>
  <fills count="8">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF1E40AF"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFEFF6FF"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFE2E8F0"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF1E3A8A"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFF8FAFC"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFDBEAFE"/></patternFill></fill>
  </fills>
  <borders count="3">
    <border><left/><right/><top/><bottom/><diagonal/></border>
    <border>
      <left style="thin"><color rgb="FFCBD5E1"/></left>
      <right style="thin"><color rgb="FFCBD5E1"/></right>
      <top style="thin"><color rgb="FFCBD5E1"/></top>
      <bottom style="thin"><color rgb="FFCBD5E1"/></bottom>
      <diagonal/>
    </border>
    <border>
      <left style="thin"><color rgb="FF93C5FD"/></left>
      <right style="thin"><color rgb="FF93C5FD"/></right>
      <top style="medium"><color rgb="FF1E40AF"/></top>
      <bottom style="medium"><color rgb="FF1E40AF"/></bottom>
      <diagonal/>
    </border>
  </borders>
  <cellStyleXfs count="1">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>
  </cellStyleXfs>
  <cellXfs count="13">
    <!-- 0: Default -->
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <!-- 1: SDU Banner Title -->
    <xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
    <!-- 2: SDU Banner Subtitle -->
    <xf numFmtId="0" fontId="2" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="left" vertical="center" wrapText="1"/></xf>
    <!-- 3: Section Heading -->
    <xf numFmtId="0" fontId="3" fillId="4" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="left" vertical="center"/></xf>
    <!-- 4: Table Column Header -->
    <xf numFmtId="0" fontId="4" fillId="5" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
    <!-- 5: Data Text Left -->
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment horizontal="left" vertical="center" wrapText="1"/></xf>
    <!-- 6: Data Text Center -->
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
    <!-- 7: Data Integer Right -->
    <xf numFmtId="164" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <!-- 8: Data Text Left Zebra -->
    <xf numFmtId="0" fontId="0" fillId="6" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="left" vertical="center" wrapText="1"/></xf>
    <!-- 9: Data Text Center Zebra -->
    <xf numFmtId="0" fontId="0" fillId="6" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
    <!-- 10: Data Integer Right Zebra -->
    <xf numFmtId="164" fontId="0" fillId="6" borderId="1" xfId="0" applyNumberFormat="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <!-- 11: Total Label Bold -->
    <xf numFmtId="0" fontId="2" fillId="7" borderId="2" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <!-- 12: Total Number Bold -->
    <xf numFmtId="164" fontId="2" fillId="7" borderId="2" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
  </cellXfs>
  <cellStyles count="1">
    <cellStyle name="Normal" xfId="0" builtinId="0"/>
  </cellStyles>
</styleSheet>'''


def _build_sheet_xml(rows_spec, base_widths, merges=None, freeze_row=0, autofilter_ref=None) -> str:
    widths = _estimate_widths(rows_spec, base_widths)
    parts = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    parts.append('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">')

    if freeze_row > 0:
        parts.append(
            f'<sheetViews><sheetView workbookViewId="0">'
            f'<pane ySplit="{freeze_row}" topLeftCell="A{freeze_row + 1}" activePane="bottomLeft" state="frozen"/>'
            f'</sheetView></sheetViews>'
        )
    else:
        parts.append('<sheetViews><sheetView workbookViewId="0"/></sheetViews>')

    parts.append('<sheetFormatPr defaultRowHeight="20"/>')

    if widths:
        parts.append("<cols>")
        for c_idx in sorted(widths.keys()):
            w = round(widths[c_idx], 2)
            parts.append(f'<col min="{c_idx}" max="{c_idx}" width="{w}" customWidth="1"/>')
        parts.append("</cols>")

    parts.append("<sheetData>")
    for r_num, r_ht, cells in rows_spec:
        ht_attr = f' ht="{r_ht}" customHeight="1"' if r_ht else ""
        parts.append(f'<row r="{r_num}"{ht_attr}>')
        for c_idx, val, style_id, is_num in cells:
            ref = f"{_col_letter(c_idx)}{r_num}"
            if is_num:
                num_val = int(val or 0) if isinstance(val, int) else float(val or 0)
                parts.append(f'<c r="{ref}" s="{style_id}"><v>{num_val}</v></c>')
            else:
                parts.append(
                    f'<c r="{ref}" s="{style_id}" t="inlineStr"><is><t xml:space="preserve">{_xml_safe(val)}</t></is></c>'
                )
        parts.append("</row>")
    parts.append("</sheetData>")

    if autofilter_ref:
        parts.append(f'<autoFilter ref="{autofilter_ref}"/>')

    if merges:
        parts.append(f'<mergeCells count="{len(merges)}">')
        for m_ref in merges:
            parts.append(f'<mergeCell ref="{m_ref}"/>')
        parts.append("</mergeCells>")

    parts.append('<pageMargins left="0.5" right="0.5" top="0.6" bottom="0.6" header="0.3" footer="0.3"/>')
    parts.append("</worksheet>")
    return "".join(parts)


def _banner_rows(title: str, subtitle: str, col_count: int):
    last_col = _col_letter(col_count)
    rows = [
        (1, 30, [(1, title, 1, False)] + [(c, "", 1, False) for c in range(2, col_count + 1)]),
        (2, 22, [(1, subtitle, 2, False)] + [(c, "", 2, False) for c in range(2, col_count + 1)]),
    ]
    merges = [f"A1:{last_col}1", f"A2:{last_col}2"]
    return rows, merges


def build_monthly_analytics_xlsx(data: dict, exported_at: str, detail_rows=None) -> bytes:
    """Build a multi-sheet styled Excel (.xlsx) workbook for Monthly Analytics."""
    thai_month = data.get("thaiMonth") or data.get("month") or "ทั้งหมด"
    subtitle = f"งวดรายงาน: {thai_month}   |   วันที่ส่งออกข้อมูล: {exported_at}"

    # ------------------------------------------------------------------
    # Sheet 1: ภาพรวมประจำเดือน
    # ------------------------------------------------------------------
    s1_rows, s1_merges = _banner_rows("รายงานสรุปยอดและสถิติการเบิกจ่ายพัสดุรายเดือน มหาวิทยาลัยสวนดุสิต", subtitle, 6)
    s1_merges.append("A4:F4")
    s1_rows.append((4, 24, [(1, "1. สรุปภาพรวมคำขอเบิกและปริมาณพัสดุ", 3, False)] + [(c, "", 3, False) for c in range(2, 7)]))
    s1_rows.append((5, 24, [(1, "รายการตัวชี้วัด", 4, False), (2, "", 4, False), (3, "", 4, False), (4, "จำนวน", 4, False), (5, "หน่วย", 4, False), (6, "หมายเหตุ", 4, False)]))
    s1_merges.append("A5:C5")

    kpi_items = [
        ("คำขอเบิกทั้งหมดในงวด", data.get("totalRequisitions", 0), "คำขอ", "นับรวมทุกสถานะ"),
        ("รอคัดกรองเบื้องต้น", data.get("totalPending", 0), "คำขอ", "รอเจ้าหน้าที่พัสดุตรวจสอบ"),
        ("รอหัวหน้าหน่วยงานอนุมัติ", data.get("totalVerified", 0), "คำขอ", "ผ่านการคัดกรองแล้ว"),
        ("อนุมัติแล้ว รอผู้เบิกรับของ", data.get("totalApproved", 0), "คำขอ", "กันยอดจองในคลังเรียบร้อย"),
        ("จ่ายพัสดุสำเร็จแล้ว", data.get("totalCompleted", 0), "คำขอ", "ตัดสต๊อกจริงครบถ้วน"),
        ("ไม่อนุมัติ / ยกเลิก", data.get("totalRejected", 0), "คำขอ", "คืนยอดจองหรือยกเลิกคำขอ"),
        ("ปริมาณพัสดุที่ขอเบิกรวม", data.get("totalPiecesRequested", 0), "ชิ้น", "ผลรวมคำขอทั้งหมด"),
        ("ปริมาณพัสดุที่อนุมัติ / จ่ายจริงรวม", data.get("totalPiecesApproved", 0), "ชิ้น", "คำขอสถานะอนุมัติและจ่ายสำเร็จ"),
    ]
    r_idx = 6
    for idx, (label, val, unit, note) in enumerate(kpi_items):
        is_z = idx % 2 == 1
        st_txt = 8 if is_z else 5
        st_ctr = 9 if is_z else 6
        st_num = 10 if is_z else 7
        s1_merges.append(f"A{r_idx}:C{r_idx}")
        s1_rows.append((r_idx, 20, [
            (1, label, st_txt, False), (2, "", st_txt, False), (3, "", st_txt, False),
            (4, val, st_num, True), (5, unit, st_ctr, False), (6, note, st_txt, False)
        ]))
        r_idx += 1

    def _append_rank_section(rows_acc, merges_acc, start_row, section_title, item_list):
        merges_acc.append(f"A{start_row}:F{start_row}")
        rows_acc.append((start_row, 24, [(1, section_title, 3, False)] + [(c, "", 3, False) for c in range(2, 7)]))
        hdr_row = start_row + 1
        rows_acc.append((hdr_row, 24, [
            (1, "อันดับ", 4, False), (2, "ชื่อรายการพัสดุ", 4, False), (3, "หมวดหมู่", 4, False),
            (4, "จำนวนที่เบิก", 4, False), (5, "จำนวนคำขอ", 4, False), (6, "หน่วยนับ", 4, False)
        ]))
        cur_r = hdr_row + 1
        if not item_list:
            merges_acc.append(f"A{cur_r}:F{cur_r}")
            rows_acc.append((cur_r, 20, [(1, "ไม่มีรายการในงวดนี้", 6, False)] + [(c, "", 6, False) for c in range(2, 7)]))
            return cur_r + 2
        for i, it in enumerate(item_list):
            is_z = i % 2 == 1
            st_txt = 8 if is_z else 5
            st_ctr = 9 if is_z else 6
            st_num = 10 if is_z else 7
            rows_acc.append((cur_r, 20, [
                (1, i + 1, st_ctr, True),
                (2, it.get("name", ""), st_txt, False),
                (3, it.get("category", "-"), st_ctr, False),
                (4, it.get("totalPieces", 0), st_num, True),
                (5, it.get("requisitionCount", 0), st_num, True),
                (6, it.get("unit", "ชิ้น"), st_ctr, False),
            ]))
            cur_r += 1
        return cur_r + 1

    r_idx += 1
    r_idx = _append_rank_section(s1_rows, s1_merges, r_idx, "2. 5 อันดับพัสดุที่มีการเบิกจ่ายมากที่สุด", data.get("topItems", []))
    _append_rank_section(s1_rows, s1_merges, r_idx, "3. 5 อันดับพัสดุที่มีการเบิกจ่ายน้อยที่สุด", data.get("leastItems", []))
    sheet1_xml = _build_sheet_xml(s1_rows, {1: 10, 2: 44, 3: 22, 4: 16, 5: 14, 6: 26}, merges=s1_merges)

    # ------------------------------------------------------------------
    # Sheet 2: สรุปรายบุคคล
    # ------------------------------------------------------------------
    person_list = data.get("personUsage", [])
    s2_sub = f"{subtitle}   |   จำนวนบุคลากรที่มีการขอเบิก: {len(person_list)} ท่าน"
    s2_rows, s2_merges = _banner_rows("สรุปยอดการเบิกพัสดุจำแนกตามรายบุคคล", s2_sub, 8)
    s2_rows.append((4, 26, [
        (1, "ลำดับ", 4, False), (2, "ชื่อ-นามสกุล ผู้ขอเบิก", 4, False), (3, "กลุ่มงาน / หน่วยงาน", 4, False),
        (4, "จำนวนคำขอ", 4, False), (5, "จ่ายสำเร็จ", 4, False), (6, "จำนวนที่ขอเบิก", 4, False),
        (7, "อนุมัติ / จ่ายจริง", 4, False), (8, "รายการพัสดุที่เบิกในเดือน", 4, False),
    ]))
    cur_r = 5
    sum_req = sum_comp = sum_req_pcs = sum_app_pcs = 0
    for idx, p in enumerate(person_list):
        is_z = idx % 2 == 1
        st_txt = 8 if is_z else 5
        st_ctr = 9 if is_z else 6
        st_num = 10 if is_z else 7
        items_lines = [f"- {it.get('name', '')}: {int(it.get('totalPieces') or 0):,} {it.get('unit', 'ชิ้น')}" for it in (p.get("items") or [])]
        items_text = "\n".join(items_lines) if items_lines else "-"
        row_ht = max(22, min(120, 18 * max(1, len(items_lines))))
        rc = int(p.get("requisitionCount") or 0)
        cc = int(p.get("completedCount") or 0)
        rp = int(p.get("totalRequestedPieces") or 0)
        ap = int(p.get("totalApprovedPieces") or 0)
        sum_req += rc
        sum_comp += cc
        sum_req_pcs += rp
        sum_app_pcs += ap
        s2_rows.append((cur_r, row_ht, [
            (1, idx + 1, st_ctr, True),
            (2, p.get("requester", ""), st_txt, False),
            (3, p.get("dept", "-"), st_txt, False),
            (4, rc, st_num, True),
            (5, cc, st_num, True),
            (6, rp, st_num, True),
            (7, ap, st_num, True),
            (8, items_text, st_txt, False),
        ]))
        cur_r += 1
    if not person_list:
        s2_merges.append("A5:H5")
        s2_rows.append((5, 22, [(1, "ไม่มีข้อมูลการเบิกพัสดุรายบุคคลในงวดนี้", 6, False)] + [(c, "", 6, False) for c in range(2, 9)]))
        cur_r = 6
    else:
        s2_merges.append(f"A{cur_r}:C{cur_r}")
        s2_rows.append((cur_r, 24, [
            (1, "รวมทั้งหมด", 11, False), (2, "", 11, False), (3, "", 11, False),
            (4, sum_req, 12, True), (5, sum_comp, 12, True),
            (6, sum_req_pcs, 12, True), (7, sum_app_pcs, 12, True),
            (8, "", 11, False),
        ]))
    sheet2_xml = _build_sheet_xml(
        s2_rows,
        {1: 8, 2: 26, 3: 36, 4: 13, 5: 13, 6: 16, 7: 17, 8: 48},
        merges=s2_merges,
        freeze_row=4,
        autofilter_ref=f"A4:H{max(4, cur_r - (1 if person_list else 0))}" if person_list else None,
    )

    # ------------------------------------------------------------------
    # Sheet 3: สรุปทุกพัสดุ
    # ------------------------------------------------------------------
    all_items = data.get("allItemUsage", [])
    s3_sub = f"{subtitle}   |   รายการพัสดุในคลังทั้งหมด: {len(all_items)} รายการ"
    s3_rows, s3_merges = _banner_rows("สรุปยอดการเบิกพัสดุทุกรายการประจำงวด", s3_sub, 6)
    s3_rows.append((4, 26, [
        (1, "ลำดับ", 4, False), (2, "ชื่อรายการพัสดุ", 4, False), (3, "หมวดหมู่", 4, False),
        (4, "จำนวนที่เบิกในเดือน", 4, False), (5, "จำนวนคำขอ", 4, False), (6, "หน่วยนับ", 4, False),
    ]))
    cur_r3 = 5
    sum_item_pcs = sum_item_reqs = 0
    for idx, it in enumerate(all_items):
        is_z = idx % 2 == 1
        st_txt = 8 if is_z else 5
        st_ctr = 9 if is_z else 6
        st_num = 10 if is_z else 7
        tp = int(it.get("totalPieces") or 0)
        rc = int(it.get("requisitionCount") or 0)
        sum_item_pcs += tp
        sum_item_reqs += rc
        s3_rows.append((cur_r3, 20, [
            (1, idx + 1, st_ctr, True),
            (2, it.get("name", ""), st_txt, False),
            (3, it.get("category", "-"), st_ctr, False),
            (4, tp, st_num, True),
            (5, rc, st_num, True),
            (6, it.get("unit", "ชิ้น"), st_ctr, False),
        ]))
        cur_r3 += 1
    if all_items:
        s3_merges.append(f"A{cur_r3}:C{cur_r3}")
        s3_rows.append((cur_r3, 24, [
            (1, "รวมทั้งหมด", 11, False), (2, "", 11, False), (3, "", 11, False),
            (4, sum_item_pcs, 12, True), (5, sum_item_reqs, 12, True), (6, "", 11, False),
        ]))
    sheet3_xml = _build_sheet_xml(
        s3_rows,
        {1: 8, 2: 46, 3: 22, 4: 18, 5: 14, 6: 12},
        merges=s3_merges,
        freeze_row=4,
        autofilter_ref=f"A4:F{max(4, cur_r3 - 1)}" if all_items else None,
    )

    # ------------------------------------------------------------------
    # Sheet 4: รายการคำขอทั้งหมด (Detail Ledger)
    # ------------------------------------------------------------------
    d_rows = detail_rows or []
    s4_sub = f"{subtitle}   |   รายการเบิกรายละเอียด: {len(d_rows)} รายการ"
    s4_rows, s4_merges = _banner_rows("รายละเอียดใบคำขอเบิกและรายการพัสดุประจำงวด", s4_sub, 9)
    s4_rows.append((4, 26, [
        (1, "เลขที่เอกสาร", 4, False), (2, "วันที่ขอเบิก", 4, False), (3, "สถานะคำขอ", 4, False),
        (4, "ชื่อ-นามสกุล ผู้ขอเบิก", 4, False), (5, "กลุ่มงาน / หน่วยงาน", 4, False),
        (6, "รายการพัสดุ", 4, False), (7, "จำนวนที่ขอ", 4, False),
        (8, "อนุมัติ / จ่ายจริง", 4, False), (9, "หน่วยนับ", 4, False),
    ]))
    cur_r4 = 5
    for idx, dr in enumerate(d_rows):
        is_z = idx % 2 == 1
        st_txt = 8 if is_z else 5
        st_ctr = 9 if is_z else 6
        st_num = 10 if is_z else 7
        s4_rows.append((cur_r4, 20, [
            (1, dr.get("docNo", ""), st_ctr, False),
            (2, dr.get("date", ""), st_ctr, False),
            (3, dr.get("statusThai", ""), st_ctr, False),
            (4, dr.get("requester", ""), st_txt, False),
            (5, dr.get("dept", ""), st_txt, False),
            (6, dr.get("itemName", ""), st_txt, False),
            (7, int(dr.get("totalPieces") or 0), st_num, True),
            (8, int(dr.get("approvedPieces") or 0), st_num, True),
            (9, dr.get("unit", "ชิ้น"), st_ctr, False),
        ]))
        cur_r4 += 1
    if not d_rows:
        s4_merges.append("A5:I5")
        s4_rows.append((5, 22, [(1, "ไม่มีรายการคำขอเบิกในงวดที่เลือก", 6, False)] + [(c, "", 6, False) for c in range(2, 10)]))
    sheet4_xml = _build_sheet_xml(
        s4_rows,
        {1: 18, 2: 20, 3: 18, 4: 26, 5: 34, 6: 42, 7: 14, 8: 16, 9: 11},
        merges=s4_merges,
        freeze_row=4,
        autofilter_ref=f"A4:I{max(4, cur_r4 - 1)}" if d_rows else None,
    )

    # Package as standard OpenXML .xlsx archive
    sheets_meta = [
        ("ภาพรวมประจำเดือน", sheet1_xml),
        ("สรุปรายบุคคล", sheet2_xml),
        ("สรุปทุกพัสดุ", sheet3_xml),
        ("รายละเอียดคำขอเบิก", sheet4_xml),
    ]

    content_types = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
                     '<Default Extension="xml" ContentType="application/xml"/>',
                     '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
                     '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>']
    wb_sheets = []
    wb_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
               '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']

    for i, (s_name, _s_xml) in enumerate(sheets_meta, 1):
        clean_name = re.sub(r'[\\/*?:\[\]]', "", s_name)[:31]
        content_types.append(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
        wb_sheets.append(f'<sheet name="{_xml_safe(clean_name)}" sheetId="{i}" r:id="rId{i}"/>')
        wb_rels.append(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>')

    wb_rels.append(f'<Relationship Id="rId{len(sheets_meta) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>')
    wb_rels.append("</Relationships>")
    content_types.append("</Types>")

    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<bookViews><workbookView xWindow="0" yWindow="0" windowWidth="24000" windowHeight="15000"/></bookViews>'
        f'<sheets>{"".join(wb_sheets)}</sheets>'
        '</workbook>'
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>'
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", "".join(content_types))
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", "".join(wb_rels))
        zf.writestr("xl/styles.xml", _build_styles_xml())
        for i, (_s_name, s_xml) in enumerate(sheets_meta, 1):
            zf.writestr(f"xl/worksheets/sheet{i}.xml", s_xml)

    return buf.getvalue()
