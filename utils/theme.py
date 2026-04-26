import streamlit as st
import base64
import os

def inject_theme():
    img_path = os.path.join(os.path.dirname(__file__), '..', 'img', 'YUVAK_MANDAL.jpg')
    img_b64 = ""
    if os.path.exists(img_path):
        with open(img_path, 'rb') as f:
            img_b64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    * {{ font-family: 'Inter', sans-serif; }}

    /* ===== BACKGROUND ===== */
    .stApp {{
        background: linear-gradient(160deg, #FFF0F0 0%, #FFE4E4 50%, #FFF0F0 100%) !important;
        background-attachment: fixed !important;
    }}

    /* ===== HEADER ===== */
    header[data-testid="stHeader"] {{
        background: linear-gradient(90deg, #8B0000, #C0392B) !important;
        border-bottom: none !important;
    }}
    header[data-testid="stHeader"] button,
    header[data-testid="stHeader"] svg {{
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }}

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #8B0000 0%, #6B0000 100%) !important;
        border-right: none !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: #FFFFFF !important;
    }}
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] label {{
        color: #FFD0D0 !important;
        font-weight: 600;
    }}
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {{
        color: #FFFFFF !important;
        font-weight: 600;
        border-radius: 8px;
        padding: 6px 12px;
    }}
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {{
        background: rgba(255,255,255,0.15) !important;
    }}

    /* ===== IMAGE ABOVE NAV using pseudo-element ===== */
    section[data-testid="stSidebar"] > div::before {{
        content: "";
        display: block;
        width: 100%;
        height: 160px;
        background-image: url("data:image/jpeg;base64,{img_b64}");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        margin-bottom: 10px;
    }}

    /* ===== MAIN CONTENT ===== */
    .block-container {{
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }}

    /* ===== TYPOGRAPHY ===== */
    h1 {{ color: #8B0000 !important; font-weight: 800 !important; letter-spacing: -0.5px; }}
    h2, h3 {{ color: #6B0000 !important; font-weight: 700 !important; }}
    p, li, label, .stMarkdown {{ color: #2C0000 !important; }}

    /* ===== BUTTONS ===== */
    div.stButton > button {{
        background: linear-gradient(135deg, #8B0000, #C0392B) !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 12px 40px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        position: relative !important;
        overflow: hidden !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        box-shadow: 0 4px 15px rgba(139,0,0,0.3) !important;
    }}
    div.stButton > button p,
    div.stButton > button span,
    div.stButton > button div {{ color: #FFFFFF !important; }}
    div.stButton > button::after {{
        content: "";
        position: absolute;
        top: 0; left: 150%;
        width: 100%; height: 100%;
        background: linear-gradient(to left, rgba(255,255,255,0) 0%, rgba(255,255,255,0.35) 50%, rgba(255,255,255,0) 100%);
        transform: skewX(-30deg);
        z-index: 2;
    }}
    div.stButton > button:hover::after {{
        left: -150%;
        transition: left 0.6s ease-in-out !important;
    }}
    div.stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(139,0,0,0.4) !important;
        color: #FFFFFF !important;
    }}

    /* ===== INPUTS ===== */
    input, textarea, [data-baseweb="select"] {{
        border: 2px solid #FFCCCC !important;
        border-radius: 8px !important;
        background: #FFFFFF !important;
    }}
    input:focus, textarea:focus {{
        border-color: #8B0000 !important;
        box-shadow: 0 0 0 3px rgba(139,0,0,0.1) !important;
    }}

    /* ===== METRICS ===== */
    [data-testid="stMetric"] {{
        background: rgba(255,255,255,0.75);
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #FFCCCC;
        border-top: 4px solid #8B0000;
        box-shadow: 0 2px 8px rgba(139,0,0,0.08);
    }}
    [data-testid="stMetricValue"] {{ color: #8B0000 !important; font-weight: 800 !important; }}
    [data-testid="stMetricLabel"] {{ color: #6B0000 !important; font-weight: 600 !important; }}

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {{ border-bottom: 2px solid #FFCCCC; }}
    .stTabs [data-baseweb="tab"] {{ color: #8B0000 !important; font-weight: 600; }}
    .stTabs [aria-selected="true"] {{ border-bottom: 3px solid #8B0000 !important; color: #8B0000 !important; }}

    /* ===== DIVIDER ===== */
    hr {{ border-color: #FFCCCC !important; }}

    /* ===== SOFT TABLE ===== */
    .soft-table-row {{ background:#FFFFFF; border:1px solid #EEEEEE; border-radius:10px; margin-bottom:8px; padding:12px 20px; transition:all 0.2s ease; }}
    .soft-table-row:hover {{ border-color:#8B0000; background-color:#FFF9F9; }}
    .table-header {{ font-weight:700; color:#8B0000; text-transform:uppercase; font-size:13px; padding:10px 20px; }}

    /* ===== STATUS PILLS ===== */
    .status-pill {{ padding:4px 12px; border-radius:6px; font-size:12px; font-weight:700; }}
    .pill-accepted {{ background:#E8F5E9; color:#2E7D32; border:1px solid #2E7D32; }}
    .pill-rejected {{ background:#FFEBEE; color:#C62828; border:1px solid #C62828; }}
    .pill-pending {{ background:#FFF3E0; color:#EF6C00; border:1px solid #EF6C00; }}

    /* ===== ICON BUTTON ===== */
    div[data-testid="stButton"] button[kind="secondary"] {{
        background:transparent !important; border:none !important;
        box-shadow:none !important; padding:0 !important;
        font-size:20px !important; min-height:unset !important;
        width:auto !important; letter-spacing:0 !important;
        text-transform:none !important;
    }}
    div[data-testid="stButton"] button[kind="secondary"]:hover {{
        background:transparent !important; transform:scale(1.2) !important; box-shadow:none !important;
    }}

    /* ===== NAV BUTTONS ===== */
    .nav-btn div.stButton > button {{
        background: transparent !important; color: #8B0000 !important;
        border: 2px solid #8B0000 !important; box-shadow: none !important;
        font-weight: 700 !important; text-transform: none !important;
        letter-spacing: 0 !important; font-size: 14px !important; padding: 6px 20px !important;
    }}
    .nav-btn div.stButton > button:hover {{ background: #8B0000 !important; color: #FFFFFF !important; }}
    .nav-btn div.stButton > button p,
    .nav-btn div.stButton > button span {{ color: #8B0000 !important; }}
    .nav-btn div.stButton > button:hover p,
    .nav-btn div.stButton > button:hover span {{ color: #FFFFFF !important; }}

    /* ===== HIDE GITHUB ICON ===== */
    a[href="https://github.com/streamlit/streamlit"],
    a[href="https://github.com/streamlit/streamlit"] > * {{
        display: none !important; visibility: hidden !important;
    }}
    [data-testid="stToolbarActionButton"] {{ display: none !important; }}

    </style>
    """, unsafe_allow_html=True)
