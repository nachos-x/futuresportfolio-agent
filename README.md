# Autonomous Multi-Agent Energy Futures Monitor

A multi-agent AI-powered dashboard built with Streamlit and CrewAI that autonomously generates daily reports for a portfolio of energy and commodity futures (CL=F, BZ=F, NG=F, HO=F, RB=F, GC=F). It combines real-time market data from yfinance, SMA golden/death cross detection, 5-year backtesting, recent news from Google News RSS, and 5-day LSTM price forecasts using PyTorch.

## Features

- Multi-Agent System: 3 specialized CrewAI agents (Technical Analyst, News Researcher, ML Forecaster) collaborate to generate reports.
- Technical Analysis: Detects golden/death crosses using 50/200-day SMAs with imminent crossover alerts.
- Backtesting: Compares SMA crossover strategy vs. buy-and-hold over 5 years.
- News Aggregation: Fetches latest headlines with clickable links from Google News RSS (top 3 per ticker).
- LSTM Forecasting: Trains PyTorch LSTM models for 5-day price predictions per futures contract.
- Streamlit Dashboard: One-click report generation with markdown rendering for clean output.
- Optimizations: Caching for yfinance data, reduced LSTM epochs for speed, secrets management for API keys.
- Deployment-Ready: Securely deployable on Streamlit Cloud with no hardcoded keys.

## Demo

Live app: [futures-agent.streamlit.app](https://futuresportfolio-agent.streamlit.app)

## Example Report Output:

### SMA Crossover Analysis
Crosses Detected Today

GOLDEN CROSS — WTI Crude Oil (CL=F) on 2026-05-08 (bullish)

Imminent Crossovers (within 1.5%)

Natural Gas (NG=F) — SMA50 is 1.23% approaching Golden Cross (bullish signal imminent)

Current SMA Status

Brent Crude Oil (BZ=F): Bullish trend | SMA gap +4.87%

## 5-Year Backtest Summary

CL=F: Strategy +87.45% | Buy&Hold +62.31%

BZ=F: Strategy -12.18% | Buy&Hold +58.92%

NG=F: Strategy +34.67% | Buy&Hold -41.55%

... (full per-ticker results)

## Latest News

CL=F: [OPEC+ Signals Potential Production Cut Amid Rising Demand (Reuters)](https://www.reuters.com/business/energy/opec-agrees-principle-small-oil-output-quota-hike-without-uae-sources-say-2026-05-02/)

NG=F: [U.S. Natural Gas Inventories Rise More Than Expected (Bloomberg)](https://www.bloomberg.com/news/articles/2026-04-21/us-natural-gas-ticks-down-on-mild-weather-growing-surplus)

## LSTM Price Forecasts

CL=F 5-Day LSTM Forecast:

2026-05-12: $78.45

2026-05-13: $77.92

... (per-ticker predictions)

## Tech Stack

- Frontend: Streamlit

- AI Agents: CrewAI

- LLM: Llama 3.3 70B via OpenRouter

- Data: yfinance for market data, Google News RSS for news

- ML: PyTorch for LSTM forecasting, NumPy/Pandas for data processing

- Other: Requests/XML for RSS parsing, scikit-learn for scaling
