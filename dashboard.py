import streamlit as st
from advanced_stock_monitor import crew

st.set_page_config(page_title="Energy Futures Monitor", layout="wide", page_icon="📈")


st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        color: #1a1a2e;
        margin-bottom: 0.3rem;
    }
    .subtitle {
        font-size: 1.15rem !important;
        color: #4a4a4a;
        margin-bottom: 1.5rem;
    }
    .portfolio-card {
        background-color: #f8f9fa;
        padding: 20px 25px;
        border-radius: 12px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 1.5rem;
    }
    .section-header {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #1a1a2e;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 12px 28px;
        font-size: 1.05rem;
    }
</style>
""", unsafe_allow_html=True)


st.markdown('<h1 class="main-title">Autonomous Energy Futures Monitor</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Multi-Agent AI System • CrewAI + Real Market Data + LSTM Forecasting</p>', unsafe_allow_html=True)


st.markdown("### Current Portfolio")
st.markdown("""
<div class="portfolio-card">
    <b>WTI Crude Oil</b> • <b>Brent Crude Oil</b> • <b>Natural Gas</b> • <b>Heating Oil</b> • <b>RBOB Gasoline</b> • <b>Gold Futures</b>
</div>
""", unsafe_allow_html=True)


col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Generate Latest Report", type="primary", use_container_width=True):
        with st.spinner("Running multi-agent analysis... This may take 30–60 seconds"):
            result = crew.kickoff()
            st.session_state.report = str(result)
            st.rerun()


if "report" in st.session_state:
    st.markdown("### 📊 Daily AI-Generated Report")
    st.markdown(st.session_state.report, unsafe_allow_html=False)
    st.divider()


st.caption("Built with **3 specialized AI agents** • Real yfinance data • LSTM forecasting • Deployed on Streamlit Cloud")
