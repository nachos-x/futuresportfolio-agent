import streamlit as st
from advanced_futures_monitor import (
    run_cross_checker,
    run_backtester,
    run_news_fetcher,
    run_lstm_forecaster,
)

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
    "GC=F": "Gold Futures",
}

st.subheader("Current Portfolio")
st.write(" • ".join([TICKER_DISPLAY[t] for t in PORTFOLIO]))
st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Generate Latest Report", type="primary", use_container_width=True):
        with st.spinner("Running analysis... Please wait"):
            cross_out    = run_cross_checker()
            backtest_out = run_backtester()
            news_out     = run_news_fetcher()
            lstm_out     = run_lstm_forecaster()

            report = (
                "## SMA Crossover Analysis\n\n"
                f"{cross_out}\n\n"
                "---\n\n"
                "## 5-Year Backtest Summary\n\n"
                f"{backtest_out}\n\n"
                "---\n\n"
                "## Latest News\n\n"
                f"{news_out}\n\n"
                "---\n\n"
                "## LSTM Price Forecasts\n\n"
                f"{lstm_out}"
            )

            st.session_state.report = report
            st.rerun()

if "report" in st.session_state:
    st.markdown("---")
    st.subheader("Daily AI-Generated Report")
    st.markdown(st.session_state.report, unsafe_allow_html=True)

st.caption("Built with **3 specialized AI agents** • Real yfinance data • LSTM forecasting • Deployed on Streamlit Cloud")            # Build report from direct function calls — LLM never touches formatting
            cross_out    = run_cross_checker()
            backtest_out = run_backtester()
            news_out     = run_news_fetcher()
            lstm_out     = run_lstm_forecaster()

            report = (
                "## SMA Crossover Analysis\n\n"
                f"{cross_out}\n\n"
                "---\n\n"
                "## 5-Year Backtest Summary\n\n"
                f"{backtest_out}\n\n"
                "---\n\n"
                "## Latest News\n\n"
                f"{news_out}\n\n"
                "---\n\n"
                "## LSTM Price Forecasts\n\n"
                f"{lstm_out}"
            )

            st.session_state.report = report
            st.rerun()

if "report" in st.session_state:
    st.markdown("---")
    st.subheader("Daily AI-Generated Report")
    st.markdown(st.session_state.report, unsafe_allow_html=True)

st.caption("Built with **3 specialized AI agents** • Real yfinance data • LSTM forecasting • Deployed on Streamlit Cloud")                "## Technical Analysis\n\n"
                f"{technical_out}\n\n"
                "---\n\n"
                "## Latest News\n\n"
                f"{news_out}\n\n"
                "---\n\n"
                "## LSTM Price Forecasts\n\n"
                f"{forecast_out}"
            )

            st.session_state.report = report
            st.rerun()

if "report" in st.session_state:
    st.markdown("---")
    st.subheader("Daily AI-Generated Report")
    st.markdown(st.session_state.report, unsafe_allow_html=True)

st.caption("Built with **3 specialized AI agents** • Real yfinance data • LSTM forecasting • Deployed on Streamlit Cloud")
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
