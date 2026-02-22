# Raspberry Pi Deployment Guide

## Overview

This guide walks you through deploying the Sovereign Stack Governance Engine on a Raspberry Pi (Model 3B+ or 4) for a SOV-HAB cell.

## Requirements

- Raspberry Pi 3B+, 4, or Zero 2W
- Raspberry Pi OS (64-bit recommended for Pi 4)
- Python 3.10+ (pre-installed on Raspberry Pi OS Bookworm)
- Internet access for initial setup (works offline after install)

## Quick Start

### 1. Update the system

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Python dependencies

```bash
# Verify Python version (must be 3.10+)
python3 --version

# Install pip if not present
sudo apt install -y python3-pip python3-venv
```

### 3. Clone and set up the repository

```bash
git clone https://github.com/vanj900/sovereign-stack.git
cd sovereign-stack

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install governance engine dependencies
pip install -r src/ghoststack/governance/requirements.txt
```

### 4. Run the demo (no server required)

```bash
PYTHONPATH=src python src/ghoststack/governance/main.py --demo
```

Expected output:
```
============================================================
  Sovereign Stack Governance Engine — Demo
============================================================

--- Identity ---
  Alice:  did:sov:alice
  ...
✅  Governance engine demo completed successfully.
```

### 5. Start the REST API server

```bash
# Store data in /home/pi/gov-data/
mkdir -p ~/gov-data

GOV_DATABASE_URL="sqlite:////home/pi/gov-data/governance.db" \
GOV_API_HOST="0.0.0.0" \
GOV_API_PORT=8000 \
PYTHONPATH=src \
python src/ghoststack/governance/main.py
```

The API will be available at `http://<pi-ip>:8000`.

Interactive API docs: `http://<pi-ip>:8000/docs`

### 6. Run as a systemd service (auto-start on boot)

Create the service file:

```bash
sudo tee /etc/systemd/system/governance.service << 'EOF'
[Unit]
Description=Sovereign Stack Governance Engine
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/sovereign-stack
Environment=PYTHONPATH=/home/pi/sovereign-stack/src
Environment=GOV_DATABASE_URL=sqlite:////home/pi/gov-data/governance.db
Environment=GOV_API_HOST=0.0.0.0
Environment=GOV_API_PORT=8000
Environment=GOV_LOG_LEVEL=INFO
ExecStart=/home/pi/sovereign-stack/.venv/bin/python src/ghoststack/governance/main.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable governance
sudo systemctl start governance
sudo systemctl status governance
```

Check logs:

```bash
journalctl -u governance -f
```

## CLI Usage

The governance engine includes a CLI for direct interaction:

```bash
# Set up path
export PYTHONPATH=/home/pi/sovereign-stack/src
export GOV_DATABASE_URL=sqlite:////home/pi/gov-data/governance.db
alias gov="python /home/pi/sovereign-stack/src/ghoststack/governance/api/cli.py"

# Create DIDs
gov did create alice
gov did create bob

# Issue a credential
gov did issue-credential did:sov:alice did:sov:bob MeshMember '{"role": "relay"}'

# Create a proposal
gov gov propose did:sov:alice "Increase cell bandwidth quota"

# Vote
gov gov vote P-1 did:sov:alice APPROVE
gov gov vote P-1 did:sov:bob APPROVE

# Tally
gov gov tally P-1

# Reputation
gov rep endorse alice bob --weight 1.0
gov rep scores

# Incentives
gov incentive register alice --balance 100
gov incentive reward alice 10 --reason "proposal creation"
gov incentive balances
```

## REST API Examples

```bash
# Health check
curl http://localhost:8000/health

# Create a DID
curl -X POST http://localhost:8000/did \
  -H "Content-Type: application/json" \
  -d '{"owner": "alice"}'

# Create a proposal
curl -X POST http://localhost:8000/governance/proposals \
  -H "Content-Type: application/json" \
  -d '{"proposer_did": "did:sov:alice", "description": "Enable mesh relay mode"}'

# Vote
curl -X POST http://localhost:8000/governance/proposals/P-1/vote \
  -H "Content-Type: application/json" \
  -d '{"voter_did": "did:sov:alice", "choice": "APPROVE"}'

# Tally
curl -X POST http://localhost:8000/governance/proposals/P-1/tally \
  -H "Content-Type: application/json" \
  -d '{}'

# View audit chain
curl http://localhost:8000/chain
```

## Running Tests

```bash
cd sovereign-stack
pip install pytest pytest-asyncio httpx
PYTHONPATH=src python -m pytest src/ghoststack/tests/ -v
```

## Performance Notes (Raspberry Pi)

- **SQLite is sufficient** for cells of 3–20 nodes
- **RAM**: The engine uses ~50MB at idle
- **CPU**: Minimal; PageRank computation on 20 nodes takes <1ms
- **Storage**: SQLite DB grows ~1KB per proposal + votes
- **Pi Zero 2W**: Works, but may take 2–3 seconds to start the API server

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GOV_DATABASE_URL` | `sqlite:///governance.db` | Database location |
| `GOV_API_HOST` | `0.0.0.0` | API bind address |
| `GOV_API_PORT` | `8000` | API port |
| `GOV_QUORUM` | `0.5` | Minimum vote fraction |
| `GOV_INITIAL_BALANCE` | `100` | Starting token balance |
| `GOV_LOG_LEVEL` | `INFO` | Log verbosity |
| `GOV_REPUTATION_DECAY_HALF_LIFE_DAYS` | `30` | Trust decay rate (0 = no decay) |
