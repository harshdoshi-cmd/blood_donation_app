import streamlit as st
import time
from utils.theme import inject_theme

st.set_page_config(
    page_title="Blood Donation Management",
    page_icon="🩸",
    layout="wide"
)

def main():
    inject_theme()
    
    st.sidebar.title("🩸 Navigation")
    st.sidebar.info("Select a module to manage the donor network.")

    st.title("🩸 Blood Donation Management System")

    c1, c2 = st.columns([1.3, 1])

    with c1:
        st.markdown("### Life-Saving Data at Your Fingertips")
        st.markdown("Our centralized system ensures that every drop counts.")
        st.markdown("""
        <div style="display:flex; gap:16px; margin:24px 0; flex-wrap:wrap;">
            <div style="flex:1; min-width:160px; background:#FFFFFF; border-radius:14px; padding:22px 18px;
                        border-top:5px solid #8B0000; box-shadow:0 4px 18px rgba(139,0,0,0.10);
                        transition:transform 0.2s; cursor:default;">
                <div style="font-size:28px; margin-bottom:8px;">📊</div>
                <div style="font-weight:800; color:#8B0000; font-size:15px; margin-bottom:6px;">Analytics Dashboard</div>
                <div style="color:#555; font-size:13px;">Monitor real-time donation trends and yearly statistics.</div>
            </div>
            <div style="flex:1; min-width:160px; background:#FFFFFF; border-radius:14px; padding:22px 18px;
                        border-top:5px solid #C0392B; box-shadow:0 4px 18px rgba(139,0,0,0.10);
                        transition:transform 0.2s; cursor:default;">
                <div style="font-size:28px; margin-bottom:8px;">🔎</div>
                <div style="font-weight:800; color:#C0392B; font-size:15px; margin-bottom:6px;">Donor Discovery</div>
                <div style="color:#555; font-size:13px;">Filter, search and export donor data for outreach campaigns.</div>
            </div>
            <div style="flex:1; min-width:160px; background:#FFFFFF; border-radius:14px; padding:22px 18px;
                        border-top:5px solid #6B0000; box-shadow:0 4px 18px rgba(139,0,0,0.10);
                        transition:transform 0.2s; cursor:default;">
                <div style="font-size:28px; margin-bottom:8px;">⚙️</div>
                <div style="font-weight:800; color:#6B0000; font-size:15px; margin-bottom:6px;">Record Management</div>
                <div style="color:#555; font-size:13px;">Maintain up-to-date donor medical history and registrations.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Explore Dashboard", type="primary"):
            st.toast("Accessing Secure Modules...")
            time.sleep(1.5)
            st.switch_page("pages/dashboard.py")

    with c2:
        st.markdown('<div class="home-image">', unsafe_allow_html=True)
        st.image("img/bd.jpg", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
