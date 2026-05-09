import streamlit as st
from advanced_futures_monitor import crew

st.set_page_config(page_title="Energy Futures Monitor", layout="wide")

st.title("Autonomous Energy Futures Monitor")
st.markdown("**Multi-Agent AI System • CrewAI + Real Market Data + LSTM Forecasting**")

st.markdown("---")

PORTFOLIO = ["CL=F", "BZ=F", "NG=F", "HO=F", "RB=F", "GC=F"]

TICKER_DISPLAY = {
    "CL=F": "WTI Crude Oil",
    "BZ=F": "Brent Crude Oil",
    "NG=F": "Natural Gas",
    "HO=F": "Heating Oil",
    "RB=F": "RBOB Gasoline",
    "GC=F": "Gold Futures"
}

st.subheader("Current Portfolio")
st.write(" • ".join([TICKER_DISPLAY[t] for t in PORTFOLIO]))

st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Generate Latest Report", type="primary", use_container_width=True):
        with st.spinner("Running multi-agent analysis... Please wait"):
            result = crew.kickoff()
            st.session_state.report = str(result)
            st.rerun()

if "report" in st.session_state:
    st.markdown("---")
    st.subheader("Daily AI-Generated Report")
    st.markdown(st.session_state.report, unsafe_allow_html=True)

st.caption("Built with **3 specialized AI agents** • Real yfinance data • LSTM forecasting • Deployed on Streamlit Cloud")
