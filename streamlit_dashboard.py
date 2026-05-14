from pathlib import Path

import streamlit as st

from dashboard_cardiovascular_pages import get_navigation_pages


BASE_DIR = Path(__file__).resolve().parent


st.set_page_config(
    page_title="Dashboard Cardiovascular Calculado",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --cardio-primary: #005f8f;
        --cardio-secondary: #1676a8;
        --cardio-accent: #d95d39;
        --cardio-ink: #17384c;
        --cardio-soft: #eef7fb;
        --cardio-border: #cee0eb;
        --cardio-gold: #fff4d6;
    }
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(22, 118, 168, 0.14), transparent 28%),
            linear-gradient(180deg, #f7fbfe 0%, #ffffff 22%, #ffffff 100%);
    }
    .stApp h1, .stApp h2, .stApp h3 {
        color: var(--cardio-primary);
        font-weight: 780;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .hero-panel {
        background: linear-gradient(135deg, #0d4f75 0%, #156d9b 55%, #3f9ec1 100%);
        border-radius: 22px;
        padding: 1.5rem 1.55rem;
        color: #ffffff;
        box-shadow: 0 20px 44px rgba(13, 79, 117, 0.18);
        margin-bottom: 1rem;
    }
    .hero-title {
        font-size: 1.75rem;
        font-weight: 800;
        margin-bottom: 0.45rem;
        letter-spacing: -0.01em;
    }
    .hero-copy {
        font-size: 1rem;
        line-height: 1.55;
        margin: 0;
        opacity: 0.97;
    }
    .info-card {
        background: linear-gradient(180deg, #ffffff 0%, #f8fbfd 100%);
        border: 1px solid var(--cardio-border);
        border-radius: 16px;
        padding: 1.1rem 1.15rem;
        box-shadow: 0 12px 28px rgba(23, 56, 76, 0.06);
    }
    .info-card-title {
        color: var(--cardio-ink);
        font-size: 1.02rem;
        font-weight: 760;
        margin-bottom: 0.45rem;
    }
    .info-card-copy {
        color: #35566f;
        line-height: 1.5;
        margin: 0;
        font-size: 0.96rem;
    }
    .status-badge {
        display: inline-block;
        margin: 0.2rem 0 0.8rem 0;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        background: var(--cardio-gold);
        border: 1px solid #efc25f;
        color: #7a5400;
        font-size: 0.9rem;
        font-weight: 730;
    }
    .soft-note {
        color: #48697f;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #d8e7f0;
        border-radius: 14px;
        padding: 0.85rem 0.95rem;
        box-shadow: 0 10px 24px rgba(23, 56, 76, 0.05);
    }
    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid #d9e8f1;
        box-shadow: 0 8px 24px rgba(23, 56, 76, 0.05);
    }
    div[data-testid="stDownloadButton"] button,
    div[data-testid="stLinkButton"] a {
        border-radius: 999px;
    }
    section[data-testid="stSidebar"] {
        border-right: 1px solid var(--cardio-border);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

logo_path = BASE_DIR / "assets" / "seremi_sidebar_logo.svg"
icon_path = BASE_DIR / "assets" / "seremi_sidebar_icon.svg"
if logo_path.exists() and icon_path.exists():
    st.logo(str(logo_path), size="large", icon_image=str(icon_path))

navigation = st.navigation(get_navigation_pages(), position="sidebar", expanded=True)
navigation.run()

st.markdown(
    """
    <div style="
        position: fixed;
        bottom: 24px;
        right: 24px;
        background-color: #FFF3CD;
        border: 1px solid #FFC107;
        border-radius: 6px;
        padding: 6px 14px;
        font-size: 13px;
        font-weight: 600;
        color: #856404;
        z-index: 9999;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    ">
        Datos Provisorios
    </div>
    """,
    unsafe_allow_html=True,
)
