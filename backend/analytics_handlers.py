"""
Monthly Analytics & Native Excel (.xlsx) Export Handlers (backend/analytics_handlers.py)
Project: ระบบจัดการวัสดุสำนักงานออนไลน์ มหาวิทยาลัยสวนดุสิต
"""

from datetime import datetime

try:
    from config import IS_POSTGRES, STATUS_THAI_LABELS, THAI_MONTHS, format_thai_datetime, get_server_attr, parse_month_date_range
    from database import call_get_db_connection, dict_cursor
    from excel_export import build_monthly_analytics_xlsx  # type: ignore[import-not-found]
    from requisition_handlers import handle_get_requisitions
except ImportError:
    from backend.config import IS_POSTGRES, STATUS_THAI_LABELS, THAI_MONTHS, format_thai_datetime, get_server_attr, parse_month_date_range
    from backend.database import call_get_db_connection, dict_cursor
    from backend.excel_export import build_monthly_analytics_xlsx
    from backend.requisition_handlers import handle_get_requisitions


def handle_get_monthly_analytics(params):
    month_filter = params.get("month", [""])[0].strip() if isinstance(params.get("month"), list) else str(params.get("month") or "").strip()
    cur_now = datetime.now()
    if not month_filter:
        month_filter = cur_now.strftime("%Y-%m")

    is_all = (month_filter.lower() == "all")

    thai_month_label = "ข้อมูลย้อนหลังทั้งหมด"
    if not is_all:
        try:
            parts = month_filter.split("-")
            year = int(parts[0])
            m = int(parts[1])
            thai_year = year + 543
            thai_m_name = THAI_MONTHS[m - 1]
            thai_month_label = f"{thai_m_name} {thai_year}"
        except Exception:
            thai_month_label = month_filter

    conn = call_get_db_connection()
    try:
        with dict_cursor(conn) as cur:
            where_req_clause = ""
            query_args = []
            be_doc_pattern = "REQ-%"
            start_dt, end_dt, parsed_doc_pfx = (None, None, None)
            if not is_all:
                start_dt, end_dt, parsed_doc_pfx = parse_month_date_range(month_filter)
                if start_dt and end_dt:
                    be_doc_pattern = f"{parsed_doc_pfx}%"
                    where_req_clause = """
                    WHERE (
                        (r.created_at IS NOT NULL AND r.created_at >= %s AND r.created_at < %s)
                        OR (r.created_at IS NULL AND r.id LIKE %s)
                    )
                    """
                    query_args = [start_dt, end_dt, be_doc_pattern]
                else:
                    where_req_clause = "WHERE r.id LIKE %s"
                    query_args = [f"REQ-%{month_filter}%"]

            status_query = f"""
                SELECT r.status, COUNT(*) as count
                FROM requisitions r
                {where_req_clause}
                GROUP BY r.status
            """
            cur.execute(status_query, tuple(query_args))
            status_rows = cur.fetchall()
            status_map = {row["status"]: int(row["count"]) for row in status_rows}

            total_reqs = sum(status_map.values())
            total_pending = status_map.get("PENDING", 0)
            total_verified = status_map.get("VERIFIED", 0)
            total_approved = status_map.get("APPROVED", 0)
            total_completed = status_map.get("COMPLETED", 0)
            total_rejected = status_map.get("REJECTED", 0)

            pieces_query = f"""
                SELECT 
                    COALESCE(SUM(ri.total_pieces), 0) as total_requested,
                    COALESCE(SUM(CASE WHEN r.status IN ('APPROVED', 'COMPLETED') THEN COALESCE(ri.approved_pieces, ri.total_pieces) ELSE 0 END), 0) as total_approved
                FROM requisitions r
                JOIN requisition_items ri ON r.id = ri.requisition_id
                {where_req_clause}
            """
            cur.execute(pieces_query, tuple(query_args))
            p_row = cur.fetchone()
            total_pieces_requested = int(p_row["total_requested"] or 0) if p_row else 0
            total_pieces_approved = int(p_row["total_approved"] or 0) if p_row else 0

            if is_all:
                item_join_cond = ""
                item_args = []
            elif start_dt and end_dt:
                item_join_cond = "AND ((r.created_at IS NOT NULL AND r.created_at >= %s AND r.created_at < %s) OR (r.created_at IS NULL AND r.id LIKE %s))"
                item_args = [start_dt, end_dt, be_doc_pattern]
            else:
                item_join_cond = "AND r.id LIKE %s"
                item_args = [f"REQ-%{month_filter}%"]

            items_query = f"""
                SELECT 
                    i.id as item_id,
                    i.name,
                    i.category,
                    i.unit_piece_name,
                    COALESCE(SUM(ri.total_pieces), 0) as total_pieces,
                    COUNT(DISTINCT r.id) as req_count
                FROM inventory_items i
                LEFT JOIN requisition_items ri ON i.id = ri.item_id
                LEFT JOIN requisitions r ON ri.requisition_id = r.id AND r.status != 'REJECTED' {item_join_cond}
                WHERE i.is_active = 1
                GROUP BY i.id, i.name, i.category, i.unit_piece_name
                ORDER BY total_pieces DESC, i.id ASC
            """
            cur.execute(items_query, tuple(item_args))
            item_rows = cur.fetchall()

            all_items = [
                {
                    "itemId": int(row["item_id"]),
                    "name": row["name"],
                    "category": row["category"],
                    "unit": row["unit_piece_name"] or "ชิ้น",
                    "totalPieces": int(row["total_pieces"] or 0),
                    "requisitionCount": int(row["req_count"] or 0),
                }
                for row in item_rows
            ]

            top_items = all_items[:5] if all_items else []
            least_items = list(reversed(all_items[-5:])) if len(all_items) >= 5 else list(reversed(all_items))

            person_usage = []
            try:
                person_where_and = ""
                if not is_all:
                    if start_dt and end_dt:
                        person_where_and = "AND ((r.created_at IS NOT NULL AND r.created_at >= %s AND r.created_at < %s) OR (r.created_at IS NULL AND r.id LIKE %s))"
                    else:
                        person_where_and = "AND r.id LIKE %s"

                person_summary_query = f"""
                    SELECT
                        r.requester,
                        MAX(r.dept) AS dept,
                        COUNT(DISTINCT r.id) AS req_count,
                        COUNT(DISTINCT CASE WHEN r.status = 'COMPLETED' THEN r.id END) AS completed_count,
                        COALESCE(SUM(ri.total_pieces), 0) AS total_requested_pieces,
                        COALESCE(SUM(CASE WHEN r.status IN ('APPROVED', 'COMPLETED') THEN COALESCE(ri.approved_pieces, ri.total_pieces) ELSE 0 END), 0) AS total_approved_pieces
                    FROM requisitions r
                    JOIN requisition_items ri ON r.id = ri.requisition_id
                    WHERE r.status != 'REJECTED' {person_where_and}
                    GROUP BY r.requester
                    ORDER BY total_requested_pieces DESC, req_count DESC, r.requester ASC
                """
                cur.execute(person_summary_query, tuple(query_args))
                person_rows = cur.fetchall()

                person_items_map = {}
                if isinstance(person_rows, list) and len(person_rows) > 0:
                    person_items_query = f"""
                        SELECT
                            r.requester,
                            ri.item_id,
                            COALESCE(MAX(i.name), MAX(ri.name)) AS item_name,
                            COALESCE(MAX(i.unit_piece_name), MAX(ri.unit_piece), 'ชิ้น') AS unit_name,
                            COALESCE(SUM(ri.total_pieces), 0) AS total_pieces,
                            COALESCE(SUM(CASE WHEN r.status IN ('APPROVED', 'COMPLETED') THEN COALESCE(ri.approved_pieces, ri.total_pieces) ELSE 0 END), 0) AS approved_pieces
                        FROM requisitions r
                        JOIN requisition_items ri ON r.id = ri.requisition_id
                        LEFT JOIN inventory_items i ON ri.item_id = i.id
                        WHERE r.status != 'REJECTED' {person_where_and}
                        GROUP BY r.requester, ri.item_id
                        ORDER BY total_pieces DESC, ri.item_id ASC
                    """
                    cur.execute(person_items_query, tuple(query_args))
                    p_item_rows = cur.fetchall()
                    if isinstance(p_item_rows, list):
                        for pi in p_item_rows:
                            req_name = pi["requester"]
                            person_items_map.setdefault(req_name, []).append({
                                "itemId": int(pi["item_id"]),
                                "name": pi.get("item_name") or "",
                                "unit": pi.get("unit_name") or "ชิ้น",
                                "totalPieces": int(pi.get("total_pieces") or 0),
                                "approvedPieces": int(pi.get("approved_pieces") or 0),
                            })

                if isinstance(person_rows, list):
                    for pr in person_rows:
                        r_name = pr["requester"]
                        person_usage.append({
                            "requester": r_name,
                            "dept": pr.get("dept") or "",
                            "requisitionCount": int(pr.get("req_count") or 0),
                            "completedCount": int(pr.get("completed_count") or 0),
                            "totalRequestedPieces": int(pr.get("total_requested_pieces") or 0),
                            "totalApprovedPieces": int(pr.get("total_approved_pieces") or 0),
                            "items": person_items_map.get(r_name, []),
                        })
            except StopIteration:
                person_usage = []

            total_purchase_cost = 0.0
            total_restock_count = 0
            total_restocked_pieces = 0
            purchase_summary = []
            purchase_transactions = []
            try:
                purchase_where_and = ""
                purchase_args = []
                if not is_all and start_dt and end_dt:
                    purchase_where_and = "AND st.created_at IS NOT NULL AND st.created_at >= %s AND st.created_at < %s"
                    purchase_args = [start_dt, end_dt]

                purchase_summary_query = f"""
                    SELECT
                        st.item_id,
                        COALESCE(MAX(i.name), 'พัสดุ #' || CAST(st.item_id AS VARCHAR)) AS item_name,
                        COALESCE(MAX(i.category), '-') AS category,
                        COALESCE(MAX(i.unit_piece_name), 'ชิ้น') AS unit_name,
                        COUNT(*) AS restock_count,
                        COALESCE(SUM(st.change_pieces), 0) AS restocked_pieces,
                        COALESCE(SUM(COALESCE(st.total_cost, 0)), 0) AS total_cost
                    FROM stock_transactions st
                    LEFT JOIN inventory_items i ON st.item_id = i.id
                    WHERE st.transaction_type = 'IN' {purchase_where_and}
                    GROUP BY st.item_id
                    ORDER BY total_cost DESC, restocked_pieces DESC, st.item_id ASC
                """ if IS_POSTGRES else f"""
                    SELECT
                        st.item_id,
                        COALESCE(MAX(i.name), CONCAT('พัสดุ #', st.item_id)) AS item_name,
                        COALESCE(MAX(i.category), '-') AS category,
                        COALESCE(MAX(i.unit_piece_name), 'ชิ้น') AS unit_name,
                        COUNT(*) AS restock_count,
                        COALESCE(SUM(st.change_pieces), 0) AS restocked_pieces,
                        COALESCE(SUM(COALESCE(st.total_cost, 0)), 0) AS total_cost
                    FROM stock_transactions st
                    LEFT JOIN inventory_items i ON st.item_id = i.id
                    WHERE st.transaction_type = 'IN' {purchase_where_and}
                    GROUP BY st.item_id
                    ORDER BY total_cost DESC, restocked_pieces DESC, st.item_id ASC
                """
                cur.execute(purchase_summary_query, tuple(purchase_args))
                p_sum_rows = cur.fetchall()
                if isinstance(p_sum_rows, list):
                    for ps in p_sum_rows:
                        r_cnt = int(ps.get("restock_count") or 0)
                        r_pcs = int(ps.get("restocked_pieces") or 0)
                        t_cost = round(float(ps.get("total_cost") or 0), 2)
                        avg_up = round(t_cost / r_pcs, 2) if r_pcs > 0 else 0.0
                        total_restock_count += r_cnt
                        total_restocked_pieces += r_pcs
                        total_purchase_cost = round(total_purchase_cost + t_cost, 2)
                        purchase_summary.append({
                            "itemId": int(ps["item_id"]),
                            "name": ps.get("item_name") or "",
                            "category": ps.get("category") or "-",
                            "unit": ps.get("unit_name") or "ชิ้น",
                            "restockCount": r_cnt,
                            "restockedPieces": r_pcs,
                            "avgUnitPrice": avg_up,
                            "totalCost": t_cost,
                        })

                purchase_tx_query = f"""
                    SELECT
                        st.id,
                        st.item_id,
                        i.name AS item_name,
                        i.unit_piece_name AS unit_name,
                        st.change_pieces,
                        COALESCE(st.unit_price, 0) AS unit_price,
                        COALESCE(st.total_cost, 0) AS total_cost,
                        st.reason,
                        st.recorded_by,
                        st.created_at
                    FROM stock_transactions st
                    LEFT JOIN inventory_items i ON st.item_id = i.id
                    WHERE st.transaction_type = 'IN' {purchase_where_and}
                    ORDER BY st.created_at DESC, st.id DESC
                    LIMIT 200
                """
                cur.execute(purchase_tx_query, tuple(purchase_args))
                p_tx_rows = cur.fetchall()
                if isinstance(p_tx_rows, list):
                    for pt in p_tx_rows:
                        dt_val = pt.get("created_at")
                        if isinstance(dt_val, datetime):
                            fmt_dt = format_thai_datetime(dt_val)
                            iso_dt = dt_val.strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            iso_dt = str(dt_val or "")
                            fmt_dt = iso_dt
                        purchase_transactions.append({
                            "id": int(pt["id"]),
                            "itemId": int(pt["item_id"]),
                            "itemName": pt.get("item_name") or f"พัสดุ #{pt['item_id']}",
                            "unit": pt.get("unit_name") or "ชิ้น",
                            "quantityPieces": int(pt.get("change_pieces") or 0),
                            "unitPrice": round(float(pt.get("unit_price") or 0), 2),
                            "totalCost": round(float(pt.get("total_cost") or 0), 2),
                            "reason": pt.get("reason") or "",
                            "recordedBy": pt.get("recorded_by") or "เจ้าหน้าที่พัสดุ สวท.",
                            "formattedDate": fmt_dt,
                            "createdAt": iso_dt,
                        })
            except StopIteration:
                total_purchase_cost = 0.0
                total_restock_count = 0
                total_restocked_pieces = 0
                purchase_summary = []
                purchase_transactions = []

            month_requisitions = []
            try:
                req_list_query = f"""
                    SELECT
                        r.id, r.date, r.requester, r.dept, r.phone, r.purpose, r.status,
                        r.signature, r.reject_reason, r.verified_by, r.verified_date,
                        r.approved_by, r.approved_date, r.completed_date, r.rejected_date,
                        r.created_at
                    FROM requisitions r
                    {where_req_clause}
                    ORDER BY r.created_at DESC, r.id DESC
                    LIMIT 500
                """
                cur.execute(req_list_query, tuple(query_args))
                m_req_rows = cur.fetchall()
                if isinstance(m_req_rows, list) and len(m_req_rows) > 0:
                    req_ids = [r["id"] for r in m_req_rows if r.get("id")]
                    items_by_req = {}
                    if req_ids:
                        placeholders = ", ".join(["%s"] * len(req_ids))
                        cur.execute(
                            f"""
                            SELECT requisition_id, item_id, name, qty_boxes, qty_pieces,
                                   total_pieces, unit_box, unit_piece, approved_pieces
                            FROM requisition_items
                            WHERE requisition_id IN ({placeholders})
                            ORDER BY id ASC
                            """,
                            tuple(req_ids),
                        )
                        ri_rows = cur.fetchall()
                        if isinstance(ri_rows, list):
                            for ri in ri_rows:
                                items_by_req.setdefault(ri["requisition_id"], []).append({
                                    "itemId": int(ri.get("item_id") or 0),
                                    "name": ri.get("name") or "",
                                    "qtyBoxes": int(ri.get("qty_boxes") or 0),
                                    "qtyPieces": int(ri.get("qty_pieces") or 0),
                                    "totalPieces": int(ri.get("total_pieces") or 0),
                                    "unitBox": ri.get("unit_box") or "",
                                    "unitPiece": ri.get("unit_piece") or "ชิ้น",
                                    "approvedPieces": int(ri.get("approved_pieces") or 0),
                                })
                    for r in m_req_rows:
                        dt_val = r.get("created_at")
                        iso_dt = dt_val.strftime("%Y-%m-%d %H:%M:%S") if isinstance(dt_val, datetime) else str(dt_val or "")
                        r_items = items_by_req.get(r["id"], [])
                        month_requisitions.append({
                            "id": r["id"],
                            "date": r.get("date") or "",
                            "requester": r.get("requester") or "",
                            "dept": r.get("dept") or "",
                            "phone": r.get("phone") or "",
                            "purpose": r.get("purpose") or "",
                            "status": r.get("status") or "PENDING",
                            "signature": r.get("signature") or "",
                            "reject_reason": r.get("reject_reason") or "",
                            "verified_by": r.get("verified_by") or "",
                            "verified_date": r.get("verified_date") or "",
                            "approved_by": r.get("approved_by") or "",
                            "approved_date": r.get("approved_date") or "",
                            "completed_date": r.get("completed_date") or "",
                            "rejected_date": r.get("rejected_date") or "",
                            "created_at": iso_dt,
                            "items": r_items,
                            "totalPieces": sum(int(i["totalPieces"]) for i in r_items),
                            "approvedPieces": sum(int(i["approvedPieces"]) for i in r_items),
                        })
            except StopIteration:
                month_requisitions = []

            return {
                "status": "success",
                "data": {
                    "month": month_filter,
                    "thaiMonth": thai_month_label,
                    "totalRequisitions": total_reqs,
                    "totalPending": total_pending,
                    "totalVerified": total_verified,
                    "totalApproved": total_approved,
                    "totalCompleted": total_completed,
                    "totalRejected": total_rejected,
                    "totalPiecesRequested": total_pieces_requested,
                    "totalPiecesApproved": total_pieces_approved,
                    "totalPurchaseCost": round(total_purchase_cost, 2),
                    "totalRestockCount": total_restock_count,
                    "totalRestockedPieces": total_restocked_pieces,
                    "topItems": top_items,
                    "leastItems": least_items,
                    "allItemUsage": all_items,
                    "personUsage": person_usage,
                    "purchaseSummary": purchase_summary,
                    "purchaseTransactions": purchase_transactions,
                    "monthRequisitions": month_requisitions,
                }
            }
    finally:
        conn.close()


def handle_export_monthly_analytics_excel(params):
    """Build styled multi-sheet native Excel (.xlsx) workbook for monthly analytics."""
    fn_analytics = get_server_attr("handle_get_monthly_analytics", handle_get_monthly_analytics)
    fn_reqs = get_server_attr("handle_get_requisitions", handle_get_requisitions)

    analytics_res = fn_analytics(params)
    analytics_data = analytics_res.get("data", {})
    resolved_month = analytics_data.get("month") or "ALL"

    reqs_res = fn_reqs({"month": [resolved_month]})
    req_list = reqs_res.get("data", []) if isinstance(reqs_res, dict) else []

    detail_rows = []
    for req in req_list:
        status_code = req.get("status") or ""
        status_thai = STATUS_THAI_LABELS.get(status_code, status_code)
        is_approved = status_code in ("APPROVED", "COMPLETED")
        for it in (req.get("items") or []):
            detail_rows.append({
                "docNo": req.get("id") or "",
                "date": req.get("date") or "",
                "statusThai": status_thai,
                "requester": req.get("requester") or "",
                "dept": req.get("dept") or "",
                "itemName": it.get("name") or "",
                "totalPieces": int(it.get("totalPieces") or 0),
                "approvedPieces": int(it.get("approvedPieces") or 0) if is_approved else 0,
                "unit": it.get("unitPiece") or "ชิ้น",
            })

    xlsx_bytes = build_monthly_analytics_xlsx(analytics_data, format_thai_datetime(), detail_rows=detail_rows)
    safe_month = "".join(ch for ch in str(resolved_month) if ch.isalnum() or ch in ("-", "_")) or "ALL"
    filename = f"SDU_Monthly_Analytics_{safe_month}.xlsx"
    return xlsx_bytes, filename
