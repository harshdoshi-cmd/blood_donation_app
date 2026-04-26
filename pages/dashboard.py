import streamlit as st
import plotly.express as px
from config.database import load_data, explorar_data
from utils.utils import process_data
from utils.theme import inject_theme

st.set_page_config(layout="wide")
inject_theme()
st.title("📊 Donation Analytics Dashboard")

df = explorar_data()
df = process_data(df)

if not df.empty:
    # --- Sidebar Filters ---
    st.sidebar.header("Global Filters")
    # years = sorted(df['year'].unique().tolist())
    years = sorted([y for y in df['year'].dropna().unique().tolist() if y != 0])
    selected_year = st.sidebar.multiselect("Select Years", years, default=years)
    
    # Filter data
    filtered_df = df[df['Year'].isin(selected_year)]
    
    # --- KPI Cards (Enhanced) ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Donors", f"👥 {len(filtered_df)}")
    with col2:
            repeat_donors = filtered_df[filtered_df['mobile_no'] != ''].groupby('mobile_no')['Year'].nunique()
            repeat_count = (repeat_donors > 1).sum()
            st.metric("Repeat Donors", f"🔁 {repeat_count}")
    with col3:
        st.metric("Unique Areas", f"📍 {filtered_df['area'].nunique()}")
    with col4:
        top_bg = filtered_df[filtered_df['abo_rh'] != '']['abo_rh'].value_counts()
        top_bg_label = f"{top_bg.index[0]} ({top_bg.iloc[0]})" if not top_bg.empty else "N/A"
        st.metric("Top Blood Group", f"🩸 {top_bg_label}")

    # --- Charts ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Donations per Year")
        year_counts = filtered_df.groupby('Year').size().reset_index(name='counts')
        fig_year = px.bar(year_counts, x='Year', y='counts', color='Year', text_auto=True)
        st.plotly_chart(fig_year, use_container_width=True)

        with c2:
            st.subheader("Top 10 Areas")
            area_counts = (
                filtered_df[filtered_df['area'].str.strip() != '']['area']
                .value_counts()
                .nlargest(10)
                .reset_index()
            )
            fig_area = px.pie(area_counts, values='count', names='area', hole=0.3)
            st.plotly_chart(fig_area, use_container_width=True)

    
    st.subheader("Blood Group Distribution")
    bg_counts = filtered_df[filtered_df['abo_rh'] != '']['abo_rh'].value_counts().reset_index()
    fig_bg = px.bar(bg_counts, x='abo_rh', y='count', color='abo_rh', text_auto=True)
    st.plotly_chart(fig_bg, use_container_width=True)
else:
    st.warning("No data found in the database. Please initialize the database.")