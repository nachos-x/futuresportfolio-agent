import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import torch
import torch.nn as nn
import torch.optim as optim
import yfinance as yf
import requests
from xml.etree import ElementTree as ET
import streamlit as st
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool

PORTFOLIO = ["CL=F", "BZ=F", "NG=F", "HO=F", "RB=F", "GC=F"]

TICKER_DISPLAY = {
    "CL=F": "WTI Crude Oil",
    "BZ=F": "Brent Crude Oil",
    "NG=F": "Natural Gas",
    "HO=F": "Heating Oil",
    "RB=F": "RBOB Gasoline",
    "GC=F": "Gold Futures"
}

# ---------------------------------------------------------------------------
# Cached data fetchers — @st.cache_data stores results for 1 hour so repeated
# report runs within the same day skip the network round-trips entirely.
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ohlcv(ticker: str, period: str) -> pd.DataFrame:
    """Download OHLCV data from yfinance with 1-hour cache."""
    return yf.download(ticker, period=period, progress=False)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_close(ticker: str, period: str) -> pd.Series:
    """Download closing prices from yfinance with 1-hour cache."""
    return yf.download(ticker, period=period, progress=False)["Close"].squeeze()


def get_openrouter_api_key() -> str:
    """Get API key from env var (preferred for VMs/Docker) or Streamlit secrets (Cloud)."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    try:
        return st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        raise RuntimeError(
            "OPENROUTER_API_KEY not found. "
            "Set the OPENROUTER_API_KEY environment variable (recommended for GCP VM) "
            "or add it to .streamlit/secrets.toml for local/Streamlit Cloud."
        )


llm = LLM(
    model="openrouter/meta-llama/llama-3.3-70b-instruct",
    base_url="https://openrouter.ai/api/v1",
    api_key=get_openrouter_api_key(),
    temperature=0.0,
)


def run_cross_checker() -> str:
    """Detects golden/death crosses and imminent crossovers using 50/200 SMA."""
    crosses = []
    imminent = []
    status = []
    for ticker in PORTFOLIO:
        display_name = TICKER_DISPLAY[ticker]
        try:
            raw = fetch_ohlcv(ticker, "730d")
            data = pd.DataFrame({"Close": raw["Close"].squeeze()})
            if len(data) < 200:
                continue
            data["SMA50"] = data["Close"].rolling(50).mean()
            data["SMA200"] = data["Close"].rolling(200).mean()
            data = data.dropna()
            if len(data) < 2:
                continue
            prev, latest = data.iloc[-2], data.iloc[-1]
            date = latest.name.strftime("%Y-%m-%d")
            sma50 = float(latest["SMA50"])
            sma200 = float(latest["SMA200"])
            gap_pct = ((sma50 - sma200) / sma200) * 100

            # Confirmed cross today
            if prev["SMA50"] <= prev["SMA200"] and latest["SMA50"] > latest["SMA200"]:
                crosses.append(f"🟡 **GOLDEN CROSS — {display_name} ({ticker})** on {date} (bullish)")
            elif prev["SMA50"] >= prev["SMA200"] and latest["SMA50"] < latest["SMA200"]:
                crosses.append(f"💀 **DEATH CROSS — {display_name} ({ticker})** on {date} (bearish)")
            # Imminent: SMAs within 1.5% of each other but not yet crossed
            elif abs(gap_pct) <= 1.5:
                direction = "approaching Golden Cross 🟡" if gap_pct > 0 else "approaching Death Cross 💀"
                trend = "bullish" if gap_pct > 0 else "bearish"
                imminent.append(
                    f"⚠️ **{display_name} ({ticker})** — SMA50 is {abs(gap_pct):.2f}% {direction} ({trend} signal imminent)"
                )
            # Normal status
            else:
                trend = "Bullish" if gap_pct > 0 else "Bearish"
                color = "green" if gap_pct > 0 else "red"
                status.append(
                    f'- {display_name} ({ticker}): {trend} trend | SMA gap '
                    f'<span style="color:{color}">{gap_pct:+.2f}%</span>'
                )
        except Exception:
            pass

    sections = []
    if crosses:
        sections.append("**Crosses Detected Today**\n" + "\n".join(crosses))
    if imminent:
        sections.append("**Imminent Crossovers (within 1.5%)**\n" + "\n".join(imminent))
    if status:
        sections.append("**Current SMA Status**\n" + "\n".join(status))
    return "\n\n".join(sections) if sections else "No data available."


def run_backtester() -> str:
    """5-year SMA crossover backtest vs buy and hold."""
    results = []
    for ticker in PORTFOLIO:
        display_name = TICKER_DISPLAY[ticker]
        try:
            raw = fetch_ohlcv(ticker, "5y")
            close = raw["Close"].squeeze()
            data = pd.DataFrame({"Close": close})
            if len(data) < 250:
                results.append(f"- {display_name} ({ticker}): Insufficient data")
                continue
            data["SMA50"] = data["Close"].rolling(50).mean()
            data["SMA200"] = data["Close"].rolling(200).mean()
            data = data.dropna()
            data["position"] = np.where(data["SMA50"] > data["SMA200"], 1, 0)
            data["strategy_ret"] = data["position"].shift(1) * data["Close"].pct_change()
            strategy_return = (1 + data["strategy_ret"].dropna()).prod() - 1
            bh_return = float(data["Close"].iloc[-1]) / float(data["Close"].iloc[0]) - 1
            s_pct = strategy_return * 100
            b_pct = bh_return * 100
            s_color = "green" if s_pct > 0 else "red"
            b_color = "green" if b_pct > 0 else "red"
            results.append(
                f'- {display_name} ({ticker}): '
                f'Strategy <span style="color:{s_color}">{s_pct:+.2f}%</span> | '
                f'Buy&amp;Hold <span style="color:{b_color}">{b_pct:+.2f}%</span>'
            )
        except Exception as e:
            results.append(f"- {display_name} ({ticker}): Calculation error — {e}")
    return "5-Year Backtest Summary\n" + "\n".join(results)


def run_news_fetcher() -> str:
    """Fetches recent news for energy futures with clickable links."""
    TICKER_QUERIES = {
        "CL=F": "WTI crude oil futures price",
        "BZ=F": "Brent crude oil futures price",
        "NG=F": "natural gas futures price",
        "HO=F": "heating oil futures price",
        "RB=F": "RBOB gasoline futures price",
        "GC=F": "gold futures price",
    }
    all_news = []
    for ticker in PORTFOLIO:
        try:
            display_name = TICKER_DISPLAY[ticker]
            query = TICKER_QUERIES[ticker].replace(" ", "+")
            rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            response = requests.get(rss_url, timeout=6)
            if response.status_code != 200:
                continue
            root = ET.fromstring(response.content)
            items = []
            for item in root.findall(".//item")[:3]:
                title = item.find("title").text
                link = item.find("link").text
                if " - " in title:
                    title = title.split(" - ")[0]
                items.append(f"- [{title}]({link})")
            if items:
                all_news.append(f"**{display_name} ({ticker})**\n" + "\n".join(items))
        except Exception:
            pass
    return "\n\n".join(all_news) if all_news else "No recent news found."


def run_lstm_forecaster() -> str:
    """Generates 5-day LSTM forecasts with green/red colors."""
    forecasts = []
    for ticker in PORTFOLIO:
        display_name = TICKER_DISPLAY[ticker]
        try:
            df = fetch_close(ticker, "3y")
            if len(df) < 200:
                forecasts.append(f"**{display_name} ({ticker})**: Insufficient data")
                continue
            current_price = float(df.iloc[-1])
            data = df.values.reshape(-1, 1)
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_data = scaler.fit_transform(data)
            seq_length = 60
            x = np.array([
                scaled_data[i - seq_length:i, 0]
                for i in range(seq_length, len(scaled_data))
            ]).reshape(-1, seq_length, 1)
            y = scaled_data[seq_length:]
            x_train = torch.from_numpy(x).float()
            y_train = torch.from_numpy(y).float()

            class LSTMModel(nn.Module):
                def __init__(self):
                    super().__init__()
                    self.lstm = nn.LSTM(1, 50, 1, batch_first=True)
                    self.fc = nn.Linear(50, 1)

                def forward(self, x):
                    out, _ = self.lstm(x)
                    return self.fc(out[:, -1, :])

            model = LSTMModel()
            optimizer = optim.Adam(model.parameters(), lr=0.001)
            criterion = nn.MSELoss()
            model.train()
            for _ in range(15):
                outputs = model(x_train)
                loss = criterion(outputs, y_train)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            predictions = []
            current_seq = scaled_data[-seq_length:].copy()
            current_tensor = torch.from_numpy(current_seq.reshape(1, seq_length, 1)).float()
            model.eval()
            for _ in range(5):
                with torch.no_grad():
                    next_pred = model(current_tensor)
                pred_val = next_pred.item()
                predictions.append(pred_val)
                current_seq = np.append(current_seq[1:], [[pred_val]], axis=0)
                current_tensor = torch.from_numpy(current_seq.reshape(1, seq_length, 1)).float()

            predictions = scaler.inverse_transform(
                np.array(predictions).reshape(-1, 1)
            ).flatten()
            last_date = df.index[-1]
            future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=5, freq="B")
            lines = [f"**{display_name} ({ticker}) 5-Day Forecast**"]
            for date, price in zip(future_dates, predictions):
                color = "green" if price > current_price else "red"
                lines.append(f'- {date.strftime("%Y-%m-%d")}: <span style="color:{color}">${price:.2f}</span>')
            forecasts.append("\n".join(lines))
        except Exception as e:
            forecasts.append(f"**{display_name} ({ticker})**: Forecast failed — {e}")
    return "\n\n".join(forecasts) if forecasts else "No forecasts."


# Thin CrewAI tool wrappers — agents use these; report assembly calls the plain functions directly
@tool("Stock Cross Checker")
def stock_cross_checker() -> str:
    """Detects golden and death crosses using 50/200 SMA."""
    return run_cross_checker()

@tool("Backtester")
def backtester() -> str:
    """5-year SMA crossover backtest vs buy and hold."""
    return run_backtester()

@tool("News Fetcher")
def news_fetcher() -> str:
    """Fetches recent news for energy futures with clickable links."""
    return run_news_fetcher()

@tool("LSTM Price Forecaster")
def lstm_price_forecaster() -> str:
    """Generates 5-day LSTM forecasts with green/red colors."""
    return run_lstm_forecaster()


technical_analyst = Agent(
    role="Technical Analyst",
    goal="Run cross checker and backtester.",
    backstory="An expert in technical analysis of commodity futures markets.",
    tools=[stock_cross_checker, backtester],
    llm=llm,
)

news_researcher = Agent(
    role="Financial News Researcher",
    goal="Run news fetcher.",
    backstory="A researcher who tracks breaking news across energy and commodity markets.",
    tools=[news_fetcher],
    llm=llm,
)

forecast_agent = Agent(
    role="ML Price Forecaster",
    goal="Run LSTM forecaster and assemble the report.",
    backstory="A machine learning engineer who builds price forecasting models for futures markets.",
    tools=[lstm_price_forecaster],
    llm=llm,
)

technical_task = Task(
    description="Run the cross checker and backtester tools and return only the raw output.",
    expected_output="Raw text output from the cross checker and backtester tools.",
    agent=technical_analyst,
)

news_task = Task(
    description="Run the news fetcher tool and return only the raw output.",
    expected_output="Raw text output from the news fetcher tool.",
    agent=news_researcher,
)

forecast_task = Task(
    description="Run the LSTM forecaster tool and return only the raw output. Do not add any commentary.",
    expected_output="Raw text output from the LSTM forecaster tool only.",
    agent=forecast_agent,
)

crew = Crew(
    agents=[technical_analyst, news_researcher, forecast_agent],
    tasks=[technical_task, news_task, forecast_task],
    verbose=True,
    memory=False,
)
