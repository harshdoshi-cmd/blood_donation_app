import streamlit as st
import pandas as pd
import io
from config.database import explorar_data
from utils.theme import inject_theme

st.set_page_config(layout="wide")
inject_theme()
st.title("🔍 Donor Data Explorer")

df = explorar_data()

if not df.empty:
    # Force all object columns to string to avoid PyArrow mixed type error
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).replace({'nan': '', 'None': '', '0': ''})

    # --- Filter Logic ---
    st.sidebar.header("Filter Criteria")
    f_year = st.sidebar.multiselect("Year", sorted([y for y in df['year'].dropna().unique() if y != 0]))
    f_source = st.sidebar.multiselect("Data Source", sorted([s for s in df['data_source'].unique() if str(s).strip() != '']))
    f_area = st.sidebar.multiselect("Area", sorted([a for a in df['area'].unique() if str(a).strip() != '']))

    temp_df = df.copy()
    if f_year: temp_df = temp_df[temp_df['year'].isin(f_year)]
    if f_source: temp_df = temp_df[temp_df['data_source'].isin(f_source)]
    if f_area: temp_df = temp_df[temp_df['area'].isin(f_area)]

    # --- Column Selection ---
    st.subheader("Custom View")
    all_columns = df.columns.tolist()
    selected_cols = st.multiselect("Select Columns to Display/Export", all_columns, default=['first_name', 'last_name', 'mobile_no', 'area', 'camp_date', 'data_source'])

    display_df = temp_df[selected_cols].copy()

    # Ensure camp_date is always string for display
    if 'camp_date' in display_df.columns:
        display_df['camp_date'] = display_df['camp_date'].astype(str).replace({'nan': '', 'None': ''})

    st.dataframe(display_df, use_container_width=True)

    # --- Export to Excel ---
    st.subheader("Export Data")
    if st.button("Generate Excel File", type="primary"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            display_df.to_excel(writer, index=False, sheet_name='Donors')

        st.download_button(
            label="📥 Download Excel",
            data=output.getvalue(),
            file_name="donor_list_filtered.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("No data found in the database. Please initialize the database.")
