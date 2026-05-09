import streamlit as st
from advanced_stock_monitor import crew

st.set_page_config(page_title="Energy Futures Monitor", layout="wide")

st.title("Autonomous Energy Futures Monitor")
st.markdown("**Multi-Agent AI System • CrewAI + Real Market Data + LSTM Forecasting**")

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
    st.markdown(st.session_state.report, unsafe_allow_html=True)

st.caption("Built with **3 specialized AI agents** • Real yfinance data • LSTM forecasting • Deployed on Streamlit Cloud")col1, col2 = st.columns([1, 3])

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
    st.markdown(st.session_state.report, unsafe_allow_html=True)

st.caption("Built with **3 specialized AI agents** • Real yfinance data • LSTM forecasting • Deployed on Streamlit Cloud")        font-weight: 600;
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
    st.markdown("### Daily AI-Generated Report")
    st.markdown(st.session_state.report, unsafe_allow_html=False)
    st.divider()


st.caption("Built with **3 specialized AI agents** • Real yfinance data • LSTM forecasting • Deployed on Streamlit Cloud")
