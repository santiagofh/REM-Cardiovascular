from pathlib import Path
import streamlit as st
from dashboard_cardiovascular_pages import get_navigation_pages

st.set_page_config(
    page_title="Dashboard REM Cardiovascular",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #F0F5FA 0%, #FFFFFF 14%, #FFFFFF 100%);
    }
    .stApp h1, .stApp h2, .stApp h3 {
        color: #006FB3;
        font-weight: 700;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #C8DDED;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        box-shadow: 0 6px 16px rgba(31, 78, 121, 0.06);
    }
    div[data-testid="stMetric"] label {
        color: #1F4E79 !important;
        font-weight: 600 !important;
    }
    .stDataFrame {
        border: 1px solid #D9E6F2;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

logo_path = Path(__file__).resolve().parent / "assets" / "seremi_sidebar_logo.svg"
icon_path = Path(__file__).resolve().parent / "assets" / "seremi_sidebar_icon.svg"
if logo_path.exists() and icon_path.exists():
    st.logo(str(logo_path), size="large", icon_image=str(icon_path))

navigation = st.navigation(get_navigation_pages(), position="sidebar", expanded=True)
navigation.run()
