import streamlit as st
from advanced_stock_monitor import crew

st.set_page_config(page_title="Energy Futures Monitor", layout="wide")

# Custom CSS for bigger headings
st.markdown("""
<style>
h1, h2, h3, h4, h5 {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    margin-top: 1.2rem !important;
    margin-bottom: 0.6rem !important;
    color: #1f77b4;
}
h4 {
    font-size: 1.35rem !important;
    border-bottom: 2px solid #1f77b4;
    padding-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

st.title("Autonomous Energy Futures Monitor")
st.markdown("**Multi-Agent AI System • CrewAI + Real Market Data + LSTM Forecasting**")

# Clean tickers
PORTFOLIO = ["CL=F", "BZ=F", "NG=F", "HO=F", "RB=F", "GC=F"]

TICKER_DISPLAY = {
    "CL=F": "WTI Crude Oil",
    "BZ=F": "Brent Crude Oil",
    "NG=F": "Natural Gas",
    "HO=F": "Heating Oil",
    "RB=F": "RBOB Gasoline",
    "GC=F": "Gold Futures"
}

col1, col2 = st.columns([1, 3])

with col1:
    if st.button("Generate Latest Report", type="primary", use_container_width=True):
        with st.spinner("Running multi-agent analysis..."):
            result = crew.kickoff()
            st.session_state.report = str(result)

with col2:
    st.markdown("### Current Portfolio")
    display_names = [TICKER_DISPLAY[t] for t in PORTFOLIO]
    st.write(" • ".join(display_names))

if "report" in st.session_state:
    st.markdown("### Daily AI-Generated Report")
    st.markdown(st.session_state.report, unsafe_allow_html=False)

st.caption("Built with **3 specialized AI agents** • Real yfinance data • LSTM forecasting • Deployed on Streamlit Cloud")
