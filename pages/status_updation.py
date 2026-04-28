import streamlit as st
import pandas as pd
from datetime import datetime
from config.database import load_2026_data, run_query
import time
from utils.theme import inject_theme

st.set_page_config(layout="wide")
inject_theme()

def inject_screening_styles():
    st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF !important;
    }
    .kpi-container {
        display: flex;
        gap: 15px;
        margin-bottom: 25px;
    }
    .kpi-card {
        background: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #EEEEEE;
        border-top: 5px solid #8B0000;
        flex: 1;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .kpi-value { font-size: 32px; font-weight: 800; color: #8B0000; margin: 5px 0; }
    .kpi-label { font-size: 12px; color: #444; font-weight: 600; text-transform: uppercase; }
    .soft-table-row {
        background: #FFFFFF;
        border: 1px solid #EEEEEE;
        border-radius: 10px;
        margin-bottom: 8px;
        padding: 12px 20px;
        transition: all 0.2s ease;
    }
    .soft-table-row:hover {
        border-color: #8B0000;
        background-color: #FFF9F9;
    }
    .table-header {
        font-weight: 700;
        color: #8B0000;
        text-transform: uppercase;
        font-size: 13px;
        padding: 10px 20px;
    }
    .status-pill {
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
    }
    .pill-accepted { background: #E8F5E9; color: #2E7D32; border: 1px solid #2E7D32; }
    .pill-rejected { background: #FFEBEE; color: #C62828; border: 1px solid #C62828; }
    .pill-pending { background: #FFF3E0; color: #EF6C00; border: 1px solid #EF6C00; }
    </style>
    """, unsafe_allow_html=True)


# --- Rejection reason dialog ---
@st.dialog("❌ Rejection Reason")
def rejection_reason_dialog(created_at, mobile_no, donor_full_name):
    st.warning(f"You are rejecting **{donor_full_name}**. Please provide a reason.")
    reason = st.text_area("Reason for Rejection*", placeholder="e.g. Low HB, High BP, Fever...")
    col1, col2 = st.columns(2)
    if col1.button("Submit Rejection", type="primary"):
        if not reason.strip():
            st.error("Reason is required.")
        else:
            curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            q = """UPDATE registration_2026 
                   SET status=%s, rejection_reason=%s, updated_at=%s 
                   WHERE created_at=%s AND mobile_no=%s AND donor_full_name=%s"""
            p = ("REJECTED", reason.strip(), curr_time, created_at, mobile_no, donor_full_name)
            if run_query(q, p):
                st.success("Rejected & reason saved.")
                time.sleep(0.8)
                st.rerun()
    if col2.button("Cancel", type="primary"):
        st.rerun()


def safe_val(val):
    """Return empty string instead of None/NaN/nan string."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    s = str(val).strip()
    return "" if s.lower() in ("none", "nan") else s


def medical_screening_window():
    inject_screening_styles()
    st.title("🏥 Medical Screening & Status Update")

    # 1. Fetch & Sort Data
    df = load_2026_data()
    if not df.empty and 'created_at' in df.columns:
        df = df.sort_values(by='created_at', ascending=False)

    # 2. KPI Section
    acc = len(df[df['status'] == 'ACCEPTED'])
    rej = len(df[df['status'] == 'REJECTED'])
    pen = len(df[df['status'] == 'PENDING'])

    st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-card"><div class="kpi-label">Registered</div><div class="kpi-value">{len(df)}</div></div>
            <div class="kpi-card" style="border-top-color: #2E7D32;"><div class="kpi-label">Accepted</div><div class="kpi-value" style="color: #2E7D32;">{acc}</div></div>
            <div class="kpi-card" style="border-top-color: #C62828;"><div class="kpi-label">Rejected</div><div class="kpi-value" style="color: #C62828;">{rej}</div></div>
            <div class="kpi-card" style="border-top-color: #EF6C00;"><div class="kpi-label">Pending</div><div class="kpi-value" style="color: #EF6C00;">{pen}</div></div>
        </div>
    """, unsafe_allow_html=True)

    # 3. Pagination
    PAGE_SIZE = 10
    total_pages = max(1, -(-len(df) // PAGE_SIZE))
    if 'page' not in st.session_state:
        st.session_state.page = 1

    page_df = df.iloc[(st.session_state.page - 1) * PAGE_SIZE : st.session_state.page * PAGE_SIZE]

    # 4. Table Headers
    st.markdown("""
        <div class="table-header">
            <div style="display: flex; justify-content: space-between;">
                <span style="width: 30%;">Donor Full Name</span>
                <span style="width: 20%;">Mobile No</span>
                <span style="width: 20%;">Area</span>
                <span style="width: 15%;">Status</span>
                <span style="width: 15%;">Action</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 5. Table Rows
    status_options = ["PENDING", "ACCEPTED", "REJECTED"]

    for _, row in page_df.iterrows():
        db_status = safe_val(row['status']) or "PENDING"
        pill_class = "pill-accepted" if db_status == 'ACCEPTED' else \
                     "pill-rejected" if db_status == 'REJECTED' else "pill-pending"

        with st.container():
            st.markdown('<div class="soft-table-row">', unsafe_allow_html=True)
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 1.5, 1.5])

            c1.markdown(f"**{safe_val(row['donor_full_name'])}**")
            c2.write(safe_val(row['mobile_no']))
            c3.write(safe_val(row['area']))
            c4.markdown(f'<span class="status-pill {pill_class}">{db_status}</span>', unsafe_allow_html=True)

            with c5:
                new_status = st.selectbox(
                    "Update",
                    status_options,
                    index=status_options.index(db_status) if db_status in status_options else 0,
                    key=f"status_sel_{row['created_at']}_{row['mobile_no']}_{row['donor_full_name']}",
                    label_visibility="collapsed"
                )

                if new_status != db_status:
                    if new_status == "REJECTED":
                        # Open dialog to capture reason before saving
                        rejection_reason_dialog(row['created_at'], row['mobile_no'], row['donor_full_name'])
                    else:
                        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        q = "UPDATE registration_2026 SET status=%s, updated_at=%s WHERE created_at=%s AND mobile_no=%s AND donor_full_name=%s"
                        p = (new_status, curr_time, row['created_at'], row['mobile_no'], row['donor_full_name'])
                        if run_query(q, p):
                            st.toast(f"Status Updated: {new_status}")
                            time.sleep(0.3)
                            st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    # 6. Pagination Controls
    st.markdown("<br>", unsafe_allow_html=True)
    p1, p2, p3 = st.columns([1, 2, 1])
    with p1:
        if st.button("◀ Prev", type="primary", disabled=st.session_state.page <= 1):
            st.session_state.page -= 1
            st.rerun()
    with p2:
        st.markdown(f"<div style='text-align:center; color:#8B0000; font-weight:700; padding-top:8px;'>Page {st.session_state.page} of {total_pages}</div>", unsafe_allow_html=True)
    with p3:
        if st.button("Next ▶", type="primary", disabled=st.session_state.page >= total_pages):
            st.session_state.page += 1
            st.rerun()


if __name__ == "__main__":
    medical_screening_window()
