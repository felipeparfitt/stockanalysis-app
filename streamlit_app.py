import streamlit as st

st.set_page_config(
    page_title="B3 Stock Market Analysis - Felipe Parfitt",
    page_icon=":bar_chart",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar Header all pages
# st.sidebar.header("B3 Stock Market Analysis")

pg = st.navigation(
    {
        "Pages Navegation": [
            st.Page("./pages/1_home.py", title="Home", icon="👋"),
            st.Page("./pages/2_stock_analysis.py", title="Stock Analysis", icon="🔥"),
        ]
    }
)
pg.run()
