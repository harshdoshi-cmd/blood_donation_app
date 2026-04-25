import streamlit as st
import pandas as pd
import io
from config.database import load_data, explorar_data, load_combined_data
from utils.utils import process_data
from utils.theme import inject_theme

st.set_page_config(layout="wide")
inject_theme()
st.title("🔍 Donor Data Explorer")

df = explorar_data()
df = process_data(df)

if not df.empty:
    # --- Filter Logic ---
    st.sidebar.header("Filter Criteria")
    # f_year = st.sidebar.multiselect("Year", sorted(df['year'].unique()))
    f_year = st.sidebar.multiselect("Year", sorted(df['year'].dropna().unique()))
    f_source = st.sidebar.multiselect("Data Source", df['data_source'].unique())
    f_area = st.sidebar.multiselect("Area", df['area'].unique())
    
    # Apply filters
    temp_df = df.copy()
    if f_year: temp_df = temp_df[temp_df['year'].isin(f_year)]
    if f_source: temp_df = temp_df[temp_df['data_source'].isin(f_source)]
    if f_area: temp_df = temp_df[temp_df['area'].isin(f_area)]

    # --- Column Selection ---
    st.subheader("Custom View")
    all_columns = df.columns.tolist()
    selected_cols = st.multiselect("Select Columns to Display/Export", all_columns, default=['first_name', 'last_name', 'mobile_no', 'area', 'camp_date', 'data_source'])

    display_df = temp_df[selected_cols]
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
        
        