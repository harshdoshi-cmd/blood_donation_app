import re
import time
import streamlit as st
import pandas as pd
from datetime import date, datetime
from config.database import run_query, load_data, load_online_registration_2026_data, get_connection, load_2026_data, load_combined_data
from utils.theme import inject_theme

st.set_page_config(layout="wide")
inject_theme()

# # Clear edit dialog state on every fresh page load/navigation
# if "edit_row" in st.session_state:
#     st.session_state.pop("edit_row", None)

if st.session_state.get("_current_page") != "registration":
    st.session_state["_current_page"] = "registration"
    if "edit_row" in st.session_state:
        st.session_state.pop("edit_row", None)


import json

with open("utils/areas.json", "r") as f:
    _area_data = json.load(f)
AREA_OPTIONS = sorted(set(a for areas in _area_data.values() for a in areas)) + ["OTHER (TYPE MANUALLY)"]


def _s(v): return "" if str(v).strip() in ("NONE", "NAN") else v


def clear_form():
    if "search_reg" in st.session_state:
        st.session_state["search_reg"] = ""
            # "ufn", "umn", "ulnm", "um", "us", "uarea", "uaddr", "ubg"
    for key in list(st.session_state.keys()):
        if key.startswith("reg_"):
            if any(num_field in key for num_field in ["uwt", "uhb", "upul", "utemp", "uage"]):
                st.session_state[key] = 0.0 if "reg_uage" not in key else 0
            elif "reg_udob" in key:
                st.session_state[key] = date.today()
            else:
                if key in ("reg_ubg", "reg_us"):
                    st.session_state[key] = None
                else:
                    st.session_state[key] = ''
    st.session_state["reg_uarea_sel"] = None
    st.session_state["reg_uarea_manual"] = ""



def refresh_data():
    st.cache_data.clear()
    
def run_query(query, params):
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute(query, params)
        conn.commit() 
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False
    finally:
        conn.close()


# --- 1. Dialog Definitions ---
@st.dialog("Confirm Action")
def confirm_action_dialog(action_type, query, params, success_msg):
    st.warning(f"Are you sure you want to proceed with this **{action_type}**?")
    col1, col2 = st.columns(2)
    if col1.button("Yes, Confirm", type="primary"):
        if run_query(query, params):
            st.success(success_msg)
            st.balloons()
            time.sleep(1.5)
            clear_form()
            st.rerun()
    if col2.button("Cancel", type="primary"):
        st.rerun()


@st.dialog("Confirm Registration")
def confirm_registration(data_tuple):
    st.warning("Are you sure you want to register this donor?")
    col1, col2 = st.columns(2)
    
    if col1.button("Yes, Register"):
        # Fixed: Added backticks to 'abo_rh', 'Unit_no', 'Camp_date', 'donor_full_name', etc.
        query = """
            INSERT INTO registration_2026 
            (unit_no, camp_date, year, donor_full_name, first_name, middle_name, last_name, 
             mobile_no, sex, area, address, birth_date, age, abo_rh, weight, hb, bp, pulse, temp, data_source, created_at, updated_at, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            if run_query(query, data_tuple):
                st.success("✅ Donor Registered Successfully!")
                st.balloons()
                time.sleep(1.5)
                clear_form()
                st.rerun()
        except Exception as e:
            st.error(f"Database Error: {e}")

    if col2.button("Cancel"):
        st.rerun()


@st.dialog("✏️ Edit Donor Record", width="large")
def edit_donor_dialog(row, bg_list):
    st.markdown("""
        <style>
        div[data-testid="stDialog"] > div {
            background: linear-gradient(160deg, #FFF0F0 0%, #FFE4E4 50%, #FFF0F0 100%) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # unique suffix per donor to avoid stale session state
    uid = str(row['created_at']).replace(" ", "_").replace(":", "-").replace(".", "-")

    st.subheader(f"Editing: {row['donor_full_name']}")
    orig_name = str(row['donor_full_name']).upper().strip()
    orig_mobile = str(row['mobile_no']).strip()

    e1, e2, e3 = st.columns(3)
    up_fn = e1.text_input("First Name", value=str(row['first_name']).upper(), key=f"d_fn_{uid}")
    up_mn = e2.text_input("Middle Name", value=str(row['middle_name']).upper(), key=f"d_mn_{uid}")
    up_ln = e3.text_input("Last Name", value=str(row['last_name']).upper(), key=f"d_ln_{uid}")

    e4, e5, e6 = st.columns(3)
    up_mb = e4.text_input("Mobile No", value=str(row['mobile_no']), key=f"d_mb_{uid}")
    sex_options = ["MALE", "FEMALE", "OTHER"]
    current_sex = str(row['sex']).upper()
    up_sex = e5.selectbox("Sex", sex_options, index=sex_options.index(current_sex) if current_sex in sex_options else 0, key=f"d_sex_{uid}")
    # up_dob = e6.date_input("Birth Date", value=pd.to_datetime(row['birth_date']).date() if row['birth_date'] not in ("", None) else date.today(), key=f"d_dob_{uid}")
    try:
        _dob_val = pd.to_datetime(row['birth_date']).date() if row['birth_date'] not in ("", None) else date.today()
        if not isinstance(_dob_val, date):
            _dob_val = date.today()
    except:
        _dob_val = date.today()
    up_dob = e6.date_input("Birth Date", value=_dob_val, key=f"d_dob_{uid}")
    up_age = st.number_input("Age", value=int(row['age']) if (pd.notnull(row['age']) and row['age'] != "") else 0, key=f"d_age_{uid}")

    current_area = str(row['area']).upper().strip()
    area_sel_index = AREA_OPTIONS.index(current_area) if current_area in AREA_OPTIONS else len(AREA_OPTIONS) - 1
    up_area_sel = st.selectbox("Area", AREA_OPTIONS, index=area_sel_index, key=f"d_area_sel_{uid}")
    up_area = st.text_input("Specify Area", value=current_area if up_area_sel == "OTHER (TYPE MANUALLY)" else "", key=f"d_area_manual_{uid}").upper() if up_area_sel == "OTHER (TYPE MANUALLY)" else up_area_sel

    up_addr = st.text_area("Address", value=str(row['address']).upper(), key=f"d_addr_{uid}")

    st.divider()
    st.subheader("🩺 Medical Vitals")
    v1, v2, v3 = st.columns(3)
    bg_idx = bg_list.index(row['abo_rh']) if row['abo_rh'] in bg_list else None
    up_bg = v1.selectbox("Blood Group", bg_list, index=bg_idx, key=f"d_bg_{uid}")
    up_wt = v2.number_input("Weight", value=float(row['weight']) if (pd.notnull(row['weight']) and row['weight'] != "") else 0.0, key=f"d_wt_{uid}")
    up_hb = v3.number_input("HB", value=float(row['hb']) if (pd.notnull(row['hb']) and row['hb'] != "") else 0.0, key=f"d_hb_{uid}")

    v4, v5, v6 = st.columns(3)
    up_bp = v4.text_input("BP", value=str(row['bp']) if (pd.notnull(row['bp']) and row['bp'] != "") else "", key=f"d_bp_{uid}")
    up_pulse = v5.number_input("Pulse", value=float(row['pulse']) if (pd.notnull(row['pulse']) and row['pulse'] != "") else 0.0, key=f"d_pulse_{uid}")
    up_temp = v6.number_input("Temp", value=float(row['temp']) if (pd.notnull(row['temp']) and row['temp'] != "") else 0.0, key=f"d_temp_{uid}")

    st.divider()
    col1, col2 = st.columns(2)
    if col1.button("💾 Save Changes", type="primary", key=f"d_save_{uid}"):
        up_full = " ".join(part for part in [up_fn, up_mn, up_ln] if part.strip() and part.strip() != "NONE").upper()
        now = datetime.now()
        standard_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        q = """UPDATE registration_2026 SET 
               first_name=%s, middle_name=%s, last_name=%s, donor_full_name=%s, mobile_no=%s, 
               sex=%s, birth_date=%s, age=%s, area=%s, address=%s, abo_rh=%s, weight=%s, hb=%s, bp=%s, pulse=%s, temp=%s, updated_at=%s
               WHERE donor_full_name=%s AND mobile_no=%s"""
        p = (
            _s(str(up_fn).upper().strip()), _s(str(up_mn).upper().strip()), _s(str(up_ln).upper().strip()),
            _s(up_full), str(up_mb).strip(), str(up_sex).upper(), up_dob, int(up_age),
            _s(str(up_area).upper().strip()), _s(str(up_addr).upper().strip()),
            str(up_bg).upper() if up_bg else None, float(up_wt), float(up_hb),
            _s(str(up_bp).upper().strip()), float(up_pulse), float(up_temp),
            standard_time, orig_name, orig_mobile
        )
        if run_query(q, p):
            st.success("✅ Record updated successfully!")
            st.balloons()
            time.sleep(1)
            st.session_state.pop("edit_row", None)
            st.rerun()
    if col2.button("Cancel", key=f"d_cancel_{uid}"):
        st.session_state.pop("edit_row", None)
        st.rerun()


st.title("🩸 Donor Records & Registration")
tab1, tab2, tab3 = st.tabs(["🆕 New Registration (2025)", "✏️ Edit Record", "🗑️ Delete Record"])

# --- TAB 1: ALL REGISTRATION LOGIC ---
with tab1:
    with tab1:
        if st.session_state.get("_active_tab") != "reg":
            st.session_state["_active_tab"] = "reg"
            if "edit_row" in st.session_state:
                st.session_state.pop("edit_row", None)

    st.subheader("🔍 Search Past Records")
    search_query = st.text_input("Search by Name or Mobile No", placeholder="Search to pre-fill details...", key="search_reg").upper()

    # --- ROBUST STATE INITIALIZATION ---
    if "loaded_donor_id" not in st.session_state:
        st.session_state["loaded_donor_id"] = None

    prefill = {
        "fn": "", "mn": "", "ln": "", "mb": "", "sex": None, "area": "", "addr": "", 
        "dob": date.today(), "age": 0, "bg": None, "wt": 0.0, "hb": 0.0, "bp": "0/0", "pulse": 0.0, "temp": 0.0
    }
    dob_missing_warning = False

    if search_query:
        try:
            df = load_combined_data()
            mask = (df['donor_full_name'].str.contains(search_query, na=False, case=False)) | \
                   (df['mobile_no'].astype(str).str.contains(search_query, na=False))
            results = df[mask].copy()
            
            if not results.empty:
                # results['completeness'] = results.notnull().sum(axis=1)
                results['completeness'] = results.apply(lambda row: (row != "").sum(), axis=1)
                results = results.sort_values(by='completeness', ascending=False)
                
                selected_idx = st.selectbox("Select Record:", results.index, 
                                            format_func=lambda x: f"{results.loc[x, 'donor_full_name']} | {results.loc[x, 'mobile_no']} | {results.loc[x, 'data_source']} | {results.loc[x, 'area']}")
                
                # --- CORE FIX: ONLY PRE-FILL IF THE SELECTION HAS CHANGED ---
                if st.session_state["loaded_donor_id"] != selected_idx:
                    row = results.loc[selected_idx]
                    
                    db_dob = row.get('birth_date')
                    db_age = row.get('age')
                    
                    # if pd.isnull(db_dob) and pd.notnull(db_age) and db_age > 0:
                    if (db_dob == "" or pd.isnull(db_dob)) and db_age not in ("", 0) and pd.notnull(db_age):
                        dob_missing_warning = True
                    
                    # try:
                    #     valid_dob = pd.to_datetime(db_dob).date() if pd.notnull(db_dob) else date.today()
                    # except:
                    #     valid_dob = date.today()
                    
                    try:
                        valid_dob = pd.to_datetime(db_dob).date() if (db_dob not in ("", None) and pd.notnull(db_dob)) else date.today()
                        if not isinstance(valid_dob, date):
                            valid_dob = date.today()
                    except:
                        valid_dob = date.today()

                    # Push database values into session state keys
                    st.session_state["reg_ufn"] = str(row.get('first_name', '')).upper()
                    st.session_state["reg_umn"] = str(row.get('middle_name', '')).upper()
                    st.session_state["reg_ulnm"] = str(row.get('last_name', '')).upper()
                    st.session_state["reg_um"] = str(row.get('mobile_no', ''))
                    # st.session_state["reg_us"] = str(row.get('sex', None)).upper()
                    raw_sex = str(row.get('sex', '')).upper().strip()
                    st.session_state["reg_us"] = raw_sex if raw_sex in ("MALE", "FEMALE", "OTHER") else None
                    st.session_state["reg_udob"] = valid_dob
                    st.session_state["reg_uage"] = int(db_age) if pd.notnull(db_age) else 0
                    st.session_state["reg_uarea"] = str(row.get('area', '')).upper()
                    st.session_state["reg_uarea_sel"] = st.session_state["reg_uarea"] if st.session_state["reg_uarea"] in AREA_OPTIONS else "OTHER (TYPE MANUALLY)"
                    st.session_state["reg_uaddr"] = str(row.get('address', '') if row.get('address') else row.get('area', '')).upper()
                    
                    bg_val = str(row.get('abo_rh', '')).strip().upper()
                    st.session_state["reg_ubg"] = bg_val if bg_val in ["A +VE", "A -VE", "B +VE", "B -VE", "O +VE", "O -VE", "AB +VE", "AB -VE"] else None

                    # Lock the state to this ID
                    st.session_state["loaded_donor_id"] = selected_idx
                    st.session_state["form_dirty"] = True 
                    st.rerun() # Refresh to update widget values immediately

                st.success("Donor data found and loaded.")
                if dob_missing_warning:
                    st.warning(f"⚠️ Note: Past record has age ({st.session_state['reg_uage']}) but no birth_date. Please provide a birth_date.")
            
            else:
                st.warning("⚠️ Record not found from the history.")
                st.info("Please fill out the entire form for the new donor.")
                if st.session_state["loaded_donor_id"] is None:
                    st.session_state["loaded_donor_id"] = None 
                    st.session_state["reg_um"] = search_query if (search_query.isdigit() and len(search_query) == 10) else ""
                # Ensure the mobile number entered in search is at least carried over to the form
                if search_query.isdigit() and len(search_query) == 10:
                    prefill["mb"] = search_query
                    st.session_state["reg_um"] = prefill["mb"]
                else:
                    st.session_state["reg_um"] = ""
        except Exception as e:
            st.error(f"Search error: {e}")
        
    else:
        st.info("Please search the donor record from the database...")
        st.error("Always check the Birth Date and AGE for every donor and after validating it register the donor.")
        if st.session_state.get("form_dirty", False):
            st.session_state["form_dirty"] = False
            st.session_state["loaded_donor_id"] = None
            st.session_state["reg_ufn"] = ""
            st.session_state["reg_umn"] = ""
            st.session_state["reg_ulnm"] = ""
            st.session_state["reg_um"] = ""
            st.session_state["reg_us"] = None
            st.session_state["reg_udob"] = date.today()
            st.session_state["reg_uage"] = 0
            st.session_state["reg_uarea"] = ""
            st.session_state["reg_uarea_manual"] = ""
            st.session_state["reg_uarea_sel"] = None
            st.session_state["reg_uaddr"] = ""
            st.session_state["reg_ubg"] = None



    st.divider()
    # --- FORM CONTAINER ---
    with st.container(border=True):
        st.subheader("👤 Personal Details")
        c1, c2, c3 = st.columns(3)
        f_name = c1.text_input("First Name*", key="reg_ufn").upper()
        m_name = c2.text_input("Middle Name*", key="reg_umn").upper()
        l_name = c3.text_input("Last Name*", key="reg_ulnm").upper()

        c4, c5, c6 = st.columns(3)
        u_mobile = c4.text_input("Mobile No*", key="reg_um")
        # u_sex = c5.selectbox("Sex*", ["MALE", "FEMALE", "OTHER"], key="reg_us")
        u_sex = c5.selectbox("Sex*", [None, "MALE", "FEMALE", "OTHER"], format_func=lambda x: "-- Select Gender --" if x is None else x, key="reg_us")
        u_dob = c6.date_input("Birth Date*", min_value=date(1940, 1, 1), max_value=date.today(), key="reg_udob")
        
        today = date.today()
        # Only auto-calculate age if it hasn't been manually tweaked or if DOB changed
        # live_calc_age = today.year - u_dob.year - ((today.month, today.day) < (u_dob.month, u_dob.day))
        
        # # We use session state for age to allow manual updates to "stick"
        # u_age = st.number_input("Age*", min_value=0, max_value=120, key="reg_uage")

        if u_dob:
            live_calc_age = today.year - u_dob.year - ((today.month, today.day) < (u_dob.month, u_dob.day))
            age_display = prefill["age"] if u_dob == date.today() and prefill["age"] > 0 else live_calc_age
            st.session_state['reg_uage'] = int(age_display)
            u_age = st.number_input("Age*", min_value=0, max_value=120, key="reg_uage")


        # u_area = st.text_input("Area*", key="reg_uarea").upper()
        prefilled_area = st.session_state.get("reg_uarea", "")
        # area_index = AREA_OPTIONS.index(prefilled_area) if prefilled_area in AREA_OPTIONS else len(AREA_OPTIONS) - 1
        # u_area_sel = st.selectbox("Area*", AREA_OPTIONS, index=area_index, key="reg_uarea_sel")
        
        # u_area_sel = st.selectbox("Area*", AREA_OPTIONS, key="reg_uarea_sel")
        u_area_sel = st.selectbox("Area*", [None] + AREA_OPTIONS, format_func=lambda x: "-- Select Area --" if x is None else x, key="reg_uarea_sel")
        u_area = st.text_input("Specify Area*", key="reg_uarea_manual").upper() if u_area_sel == "OTHER (TYPE MANUALLY)" else u_area_sel
        
        u_addr = st.text_area("Full Address*", key="reg_uaddr").upper()

        st.divider()
        st.subheader("🩺 Medical Vitals (Fresh Checkup Required)")
        m1, m2, m3 = st.columns(3)
        bg_list = ["A +VE", "A -VE", "B +VE", "B -VE", "O +VE", "O -VE", "AB +VE", "AB -VE"]
        # u_bg = m1.selectbox("Blood Group", bg_list, key="reg_ubg")
        u_bg = m1.selectbox("Blood Group", [None] + bg_list, format_func=lambda x: "-- Select Blood Group --" if x is None else x, key="reg_ubg")
        u_wt = m2.number_input("Weight (kg)", min_value=0.0, step=0.1, key="reg_uwt")
        u_hb = m3.number_input("HB (g/dL)", min_value=0.0, step=0.1, key="reg_uhb")

        m4, m5, m6 = st.columns(3)
        u_bp = m4.text_input("BP (e.g. 120/80)", key="reg_ubp") # Removed 'value=0.0' to prevent string/float conflict
        u_pulse = m5.number_input("Pulse (bpm)", min_value=0.0, step=1.0, key="reg_upul") 
        u_temp = m6.number_input("Temp (°F)", min_value=0.0, step=0.1, key="reg_utemp")

        st.divider()
        s1, s2, s3 = st.columns(3)
        s1.text_input("Camp Date", value=str(today), disabled=True)
        s2.text_input("Year", value="2026", disabled=True)
        s3.text_input("Data Source", value="BD_2026", disabled=True)

        if st.button("Register Donor", type="primary"):
            if not all([f_name, m_name, l_name, u_mobile, u_area, u_addr]):
                st.error("❌ Please fill all mandatory fields marked with *.")
            elif len(u_mobile) != 10 or not u_mobile.isdigit():
                st.error("❌ Mobile Number must be exactly 10 digits.")
            else:
                try:
                    # full_name = f"{f_name} {m_name} {l_name}".upper()
                    full_name = " ".join(part for part in [f_name, m_name, l_name] if part.strip() and part.strip() != "NONE").upper()
                    now = datetime.now()
                    standard_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
                    status='PENDING'
                    final_data = (None, today, 2026, full_name, f_name, m_name, l_name,
                                 u_mobile, u_sex, u_area, u_addr, u_dob, int(u_age),
                                 u_bg, float(u_wt), float(u_hb), u_bp, float(u_pulse), float(u_temp), "BD_2026", standard_time, standard_time, status)
                    final_data = tuple(_s(v) if isinstance(v, str) else v for v in final_data)
                    confirm_registration(final_data)
                except Exception as e:
                    st.error(f"Logic Error: {e}")


# --- TAB 2: EDIT RECORD ---
with tab2:

    if st.session_state.get("_active_tab") != "edit":
        st.session_state["_active_tab"] = "edit"
        if "edit_row" in st.session_state:
            st.session_state.pop("edit_row", None)

    df2 = load_2026_data()
    today_str = str(date.today())
    bg_list = ["A +VE", "A -VE", "B +VE", "B -VE", "O +VE", "O -VE", "AB +VE", "AB -VE"]

    today_df = df2[df2['camp_date'].astype(str).str.startswith(today_str)].copy()
    
    if not today_df.empty and 'created_at' in today_df.columns:
        today_df = today_df.sort_values(by='created_at', ascending=False)

    st.subheader(f"📋 Today's Registrations — {today_str} ({len(today_df)} donors)")
    today_df = today_df[today_df['status'] == 'PENDING']

    # Table CSS
    st.markdown("""
        <style>
        div[data-testid="stButton"] button[kind="secondary"] {
            background: transparent !important; border: none !important;
            box-shadow: none !important; padding: 0 !important;
            font-size: 20px !important; min-height: unset !important;
            width: auto !important; letter-spacing: 0 !important;
            text-transform: none !important;
        }
        div[data-testid="stButton"] button[kind="secondary"]:hover {
            background: transparent !important; transform: scale(1.2) !important;
            box-shadow: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    def render_table(data_df, key_prefix):
        st.markdown("""
            <div class="table-header">
                <div style="display:flex; justify-content:space-between;">
                    <span style="width:35%;">Donor Full Name</span>
                    <span style="width:25%;">Mobile No</span>
                    <span style="width:25%;">Area</span>
                    <span style="width:15%;">Edit</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        for idx, row in data_df.iterrows():
            with st.container():
                st.markdown('<div class="soft-table-row">', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([3.5, 2.5, 2.5, 1.7])
                c1.markdown(f"**{row['donor_full_name']}**")
                c2.write(row['mobile_no'])
                c3.write(row['area'])
                with c4:
                    if st.button("✏️", key=f"{key_prefix}_{idx}", type="secondary"):
                        st.session_state["edit_row"] = row.to_dict()
                st.markdown('</div>', unsafe_allow_html=True)


    if today_df.empty:
        st.info("No registrations found for today.")
    else:
        PAGE_SIZE = 10
        total_pages = max(1, -(-len(today_df) // PAGE_SIZE))
        if "edit_tab_page" not in st.session_state:
            st.session_state["edit_tab_page"] = 1
        st.session_state["edit_tab_page"] = min(st.session_state["edit_tab_page"], total_pages)
        page_df = today_df.iloc[(st.session_state["edit_tab_page"] - 1) * PAGE_SIZE : st.session_state["edit_tab_page"] * PAGE_SIZE]
        render_table(page_df, "today")

        # Pagination controls
        st.markdown("<br>", unsafe_allow_html=True)
        p1, p2, p3 = st.columns([1, 2, 1])
        with p1:
            if st.button("◀ Prev", key="edit_prev", type="primary", disabled=st.session_state["edit_tab_page"] <= 1):
                st.session_state["edit_tab_page"] -= 1
                st.rerun()
        with p2:
            st.markdown(f"<div style='text-align:center; color:#8B0000; font-weight:700; padding-top:8px;'>Page {st.session_state['edit_tab_page']} of {total_pages}</div>", unsafe_allow_html=True)
        with p3:
            if st.button("Next ▶", key="edit_next", type="primary", disabled=st.session_state["edit_tab_page"] >= total_pages):
                st.session_state["edit_tab_page"] += 1
                st.rerun()


    st.divider()
    st.subheader("🔍 Search & Edit Any Record")
    search_term = st.text_input("Search by Name or Mobile", key="edit_search").upper()
    if search_term and not df2.empty:
        match = df2[(df2['donor_full_name'].str.contains(search_term, na=False)) |
                    (df2['mobile_no'].astype(str).str.contains(search_term, na=False))]
        if not match.empty:
            render_table(match, "search")
        else:
            st.warning("⚠️ No matching records found.")

    # DIALOG — fires when edit_row is set in session state
    if "edit_row" in st.session_state:
        edit_donor_dialog(st.session_state["edit_row"], bg_list)




# --- TAB 3: DELETE RECORD ---
with tab3:
    with tab3:
        if st.session_state.get("_active_tab") != "del":
            st.session_state["_active_tab"] = "del"
            if "edit_row" in st.session_state:
                st.session_state.pop("edit_row", None)

    st.warning("⚠️ Critical: Deletions are permanent. Please ensure you select the correct record.")
    df = load_2026_data()
    search_del = st.text_input("Search Name/Mobile for Deletion", key="del_search").upper()
    
    if search_del and not df.empty:
        # Filtering records based on search
        match_del = df[(df['donor_full_name'].str.contains(search_del, na=False)) | 
                       (df['mobile_no'].astype(str).str.contains(search_del, na=False))]
        
        if not match_del.empty:
            # Dropdown that shows Name, Mobile, and Camp Date to identify the specific record
            target_idx = st.selectbox(
                "Select specific record to remove:", 
                match_del.index, 
                key="del_sel",
                format_func=lambda x: f"{match_del.loc[x, 'donor_full_name']} | {match_del.loc[x, 'mobile_no']} | Date: {match_del.loc[x, 'camp_date']}"
            )
            # Retrieve the selected record's details
            selected_row = match_del.loc[target_idx]
            
            # Display a small summary of the selection so the user is sure
            st.error(f"Selected for deletion: **{selected_row['donor_full_name']}** (Registered on {selected_row['camp_date']})")
            
            if st.button("🔥 Permanently Delete Record", type="primary"):
                # Using Name, Mobile, and Date to ensure we delete only THIS specific entry
                # Removed single quotes from column names for standard SQL compatibility
                q = """DELETE FROM registration_2026 
                       WHERE donor_full_name=%s 
                       AND mobile_no=%s 
                       AND camp_date=%s""" 
                p = (
                    str(selected_row['donor_full_name']).upper().strip(), 
                    str(selected_row['mobile_no']).strip(),
                    # selected_row['camp_date']
                    selected_row['camp_date'] if selected_row['camp_date'] != "" else None
                )
                confirm_action_dialog("DELETE", q, p, "Donor record removed successfully.")
        else:
            st.info("No matching records found for deletion.")
