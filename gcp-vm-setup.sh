#!/bin/bash
# gcp-vm-setup.sh
# One-time setup script you can run (or use as startup script) on a fresh Ubuntu/Debian GCP VM.
# Usage (after ssh):
#   chmod +x gcp-vm-setup.sh
#   sudo ./gcp-vm-setup.sh /opt/stockportfolio-agent sk-or-YOURKEYHERE

set -euo pipefail

APP_DIR="${1:-/opt/stockportfolio-agent}"
API_KEY="${2:-}"

if [ -z "$API_KEY" ]; then
  echo "Usage: $0 <app-dir> <openrouter-api-key>"
  echo "Example: sudo $0 /opt/stockportfolio-agent sk-or-abc123..."
  exit 1
fi

echo "==> Updating system packages"
apt-get update -y
apt-get install -y python3-pip python3-venv git curl ca-certificates

echo "==> Cloning/updating app into $APP_DIR"
mkdir -p "$(dirname "$APP_DIR")"
if [ -d "$APP_DIR/.git" ]; then
  cd "$APP_DIR"
  git pull --ff-only || true
else
  git clone https://github.com/$(git config --global user.name || echo "YOUR_GITHUB")/stockportfolio-agent.git "$APP_DIR" || \
  git clone https://github.com/nachos/stockportfolio-agent.git "$APP_DIR" 2>/dev/null || true
  # If the above fails because of private repo or different org, user should clone manually first.
fi

cd "$APP_DIR"

echo "==> Creating venv and installing dependencies (CPU torch)"
python3 -m venv venv
# shellcheck disable=SC1091
source venv/bin/activate
pip install --upgrade pip wheel
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

echo "==> Setting up secrets"
mkdir -p /etc/stockportfolio-agent
echo "OPENROUTER_API_KEY=$API_KEY" > /etc/stockportfolio-agent/secrets.env
chmod 600 /etc/stockportfolio-agent/secrets.env
chown root:root /etc/stockportfolio-agent/secrets.env

echo "==> Creating streamlit user and copying app"
id -u streamlit &>/dev/null || useradd -r -s /bin/false -d /nonexistent streamlit
mkdir -p "$APP_DIR"
cp -r . "$APP_DIR" 2>/dev/null || true   # already there
chown -R streamlit:streamlit "$APP_DIR"

echo "==> Installing systemd service"
cp streamlit.service /etc/systemd/system/streamlit-futures.service || true
# Patch the service to use the right paths and env file
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$APP_DIR|" /etc/systemd/system/streamlit-futures.service || true
sed -i 's|ExecStart=.*|ExecStart=/opt/stockportfolio-agent/venv/bin/streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true|' /etc/systemd/system/streamlit-futures.service || true
sed -i 's|Environment="OPENROUTER.*|# Environment line moved to EnvironmentFile|' /etc/systemd/system/streamlit-futures.service || true
sed -i '/EnvironmentFile=/d' /etc/systemd/system/streamlit-futures.service || true
sed -i '/\[Service\]/a EnvironmentFile=/etc/stockportfolio-agent/secrets.env' /etc/systemd/system/streamlit-futures.service || true

systemctl daemon-reload
systemctl enable --now streamlit-futures || true

echo "==> Opening local port (you still need gcloud firewall rule)"
echo "Done."
echo ""
echo "Next steps:"
echo "  1. From your laptop, create firewall rule if not done:"
echo "     gcloud compute firewall-rules create allow-streamlit --target-tags=streamlit --allow tcp:8501"
echo "  2. Get the external IP:"
echo "     gcloud compute instances describe <vm-name> --format='get(networkInterfaces[0].accessConfigs[0].natIP)'"
echo "  3. Visit http://IP:8501"
echo "  4. Logs: journalctl -u streamlit-futures -f"
echo ""
systemctl status streamlit-futures --no-pager || true
