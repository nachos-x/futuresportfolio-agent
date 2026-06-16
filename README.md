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
- Deployment-Ready: Self-hosted on Google Cloud Compute Engine (systemd) with fallback support for Streamlit Cloud via `OPENROUTER_API_KEY` env var or `st.secrets`.

## Demo

**Current self-hosted deployment:** http://136.114.12.153:8501 (Google Cloud Compute Engine)

Previous Streamlit Cloud version: [futuresportfolio-agent.streamlit.app](https://futuresportfolio-agent.streamlit.app)

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

## Deployment

### Streamlit Cloud (previous / legacy)
The app was previously deployed at [futuresportfolio-agent.streamlit.app](https://futuresportfolio-agent.streamlit.app).  
Secrets (OPENROUTER_API_KEY) were configured in the Streamlit Cloud dashboard.

### GCP VM (current primary deployment)

This is the current production deployment of the app. The repo is fully set up to run on a Google Compute Engine VM (recommended if you want full control, custom compute, or to avoid Streamlit Cloud costs/limits).

#### Recommended VM specs
- Machine type: `e2-standard-4` (4 vCPU, 16 GB) or `e2-highmem-2` minimum.  
  The report generation runs PyTorch LSTM training (6 models) + CrewAI (LLM calls) — CPU heavy and memory hungry.
- Boot disk: 50 GB SSD persistent disk.
- Image: Ubuntu 22.04 LTS or Debian 12.
- Allow HTTP traffic (or manually open port 8501).

#### Quick start (bare VM + systemd)

There's also a helper `gcp-vm-setup.sh` in the repo (edit the clone URL and run as root). Prefer the manual steps below for safety.

1. Create the VM:
   ```bash
   gcloud compute instances create futures-monitor \
     --zone=us-central1-a \
     --machine-type=e2-standard-4 \
     --image-family=ubuntu-2204-lts \
     --image-project=ubuntu-os-cloud \
     --boot-disk-size=50GB \
     --boot-disk-type=pd-ssd \
     --tags=streamlit \
     --metadata=startup-script='#! /bin/bash
       apt-get update && apt-get install -y python3-pip python3-venv git
     '
   ```

2. SSH in:
   ```bash
   gcloud compute ssh futures-monitor --zone=us-central1-a
   ```

3. On the VM — clone and set up:
   ```bash
   git clone https://github.com/<your-org>/stockportfolio-agent.git /opt/stockportfolio-agent
   cd /opt/stockportfolio-agent

   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip

   # Install CPU-only torch first (avoids huge CUDA download)
   pip install torch --index-url https://download.pytorch.org/whl/cpu

   pip install -r requirements.txt
   ```

4. Configure your OpenRouter key (never commit it):
   ```bash
   # Option A (simple)
   mkdir -p /etc/stockportfolio-agent
   echo 'OPENROUTER_API_KEY=sk-or-XXXXXXXXXXXXXXXX' | sudo tee /etc/stockportfolio-agent/secrets.env
   sudo chmod 600 /etc/stockportfolio-agent/secrets.env
   sudo chown $(whoami):$(whoami) /etc/stockportfolio-agent/secrets.env
   ```

5. Create a dedicated service user (recommended) and install the unit:
   ```bash
   sudo useradd -r -s /bin/false streamlit || true
   sudo mkdir -p /opt/stockportfolio-agent
   sudo cp -r . /opt/stockportfolio-agent/
   sudo chown -R streamlit:streamlit /opt/stockportfolio-agent

   # Copy the example service and edit it
   sudo cp streamlit.service /etc/systemd/system/streamlit-futures.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now streamlit-futures
   sudo systemctl status streamlit-futures
   ```

6. Open the firewall (from your laptop, or use a more restrictive source IP):
   ```bash
   gcloud compute firewall-rules create allow-streamlit \
     --target-tags=streamlit \
     --allow tcp:8501 \
     --description="Allow Streamlit dashboard (8501)"
   ```

7. Access the app at `http://<EXTERNAL_IP>:8501`

#### Docker on the VM (cleaner, recommended)

```bash
# On the VM after cloning
docker build -t futures-monitor .

# Run with your key
docker run -d \
  --name futures-monitor \
  -p 8501:8501 \
  -e OPENROUTER_API_KEY=sk-or-XXXXXXXXXXXXXXXX \
  --restart unless-stopped \
  futures-monitor
```

Or use `docker compose` (add a compose file if desired).

#### Using Google Secret Manager (production)

Instead of env vars, fetch the key at startup using the metadata server + Secret Manager.  
See the example in `gcp/` folder (you can add one) or use a small wrapper script.

#### Updating the app on the VM
```bash
cd /opt/stockportfolio-agent
git pull
sudo systemctl restart streamlit-futures   # or docker restart
```

#### Notes / gotchas
- The "Generate Latest Report" button triggers significant CPU work (LSTM training + 3x LLM calls via CrewAI). It can take 30–90 seconds.
- Caching (`@st.cache_data`) is per-process. Restarting the service clears it.
- For HTTPS + domain: put nginx in front + certbot, or use a Google Cloud Load Balancer + Cloud Armor.
- Monitor with `journalctl -u streamlit-futures -f` or `docker logs -f`.
- Cost: A e2-standard-4 running 24/7 is modest but add a shutdown schedule if you only need it occasionally.

### Environment Variables
- `OPENROUTER_API_KEY` (required) — your OpenRouter key for Llama 3.3 70B.

The code supports both:
- Environment variable (GCP VM / Docker / most CI)
- `st.secrets["OPENROUTER_API_KEY"]` (Streamlit Cloud / local `.streamlit/secrets.toml`)
