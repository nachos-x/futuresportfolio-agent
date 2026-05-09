import streamlit as st
from advanced_stock_monitor import crew

st.set_page_config(page_title="Energy Futures Monitor", layout="wide")
st.title("Autonomous Energy Futures Monitor")
st.markdown("**Multi-Agent AI System • CrewAI + Real Market Data + LSTM Forecasting**")

# Clean tickers (for the crew)
PORTFOLIO = ["CL=F", "BZ=F", "NG=F", "HO=F", "RB=F", "GC=F"]

# Nice display names
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
    cols = st.columns(3)
    for i, ticker in enumerate(PORTFOLIO):
        with cols[i % 3]:
            st.metric(
                label=TICKER_DISPLAY[ticker],
                value=ticker,
                delta="Energy Futures"
            )

if "report" in st.session_state:
    st.markdown("### Daily AI-Generated Report")
    # Better formatting
    st.markdown(st.session_state.report)

st.caption("Built with **3 specialized AI agents** • Real yfinance data • LSTM forecasting • Deployed on Streamlit Cloud")
