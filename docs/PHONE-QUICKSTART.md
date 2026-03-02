# Phone Quickstart — Run a Sovereign Cell from Your Android Phone

**No hardware required. No server. No ISP.**

You can run the entire sovereign cell — deed-ledger, GhostStack governance, Shadow-Net mesh — from an Android phone using [Termux](https://termux.dev).

---

## Prerequisites

- Android phone (Android 7+)
- [Termux](https://f-droid.org/packages/com.termux/) installed (get it from F-Droid, **not** the Play Store)
- Internet access for the initial install (mesh works offline after that)

---

## One-Command Install

Open Termux and run:

```bash
curl -fsSL https://raw.githubusercontent.com/vanj900/sovereign-stack/main/install-sovereign-cell.sh | bash
```

Or, if you prefer to inspect first:

```bash
pkg install git -y
git clone https://github.com/vanj900/sovereign-stack.git
cd sovereign-stack
bash install-sovereign-cell.sh
```

This script will:
1. Install Python and required packages
2. Clone the repository (if not already present)
3. Install Python dependencies
4. Run a 3-node local governance simulation to verify the install

---

## What Happens After Install

```
Sovereign Cell — Node 1 of 3
Deed-ledger address : sov://abc123...
Mesh status         : listening (Bluetooth LE + WiFi Direct)
Governance          : ready (0 proposals pending)

Share this invite to add nodes:
  sov-invite://abc123...?cell=genesis

Type 'help' for available commands.
```

### Basic commands

| Command | What it does |
|---------|-------------|
| `propose "text"` | Submit a governance proposal |
| `vote yes/no <id>` | Vote on a pending proposal |
| `receipts` | Show the last 10 deed receipts |
| `fork` | Fork this cell into a new independent cell |
| `status` | Show mesh node status |

---

## 3-Node Sim (No Second Phone Needed)

To test governance locally with simulated nodes:

```bash
cd sovereign-stack
python src/mesh/shadow-net/bridge/demo.py
```

This starts 3 simulated nodes, sends proposals, and prints receipts — all on one phone.

---

## Adding Real Nodes (other phones)

1. Each person installs via the one-command install above.
2. Share your invite link (`sov-invite://...`) via Signal, Telegram, or QR code.
3. They run:

```bash
python src/mesh/shadow-net/bridge/cli.py join sov-invite://YOUR_INVITE_LINK
```

Once 3+ nodes are connected the cell is live. Every proposal, vote, and fork generates a receipt on the deed-ledger automatically.

---

## Phase 2 Milestones You Can Help Hit

| Milestone | What to do |
|-----------|-----------|
| **Week 2** | Install on your phone, run the 3-node sim, report issues |
| **Month 2** | Find 2 locals. Run one real governance proposal. Share the receipt. |
| **Month 3** | 7-node stress test. Execute one intentional fork. |
| **Month 6** | Spin up a cell in your city. Fork the repo. Be independent. |

---

## Troubleshooting

**Termux can't find `python`**
```bash
pkg install python -y
```

**Permission denied on install script**
```bash
chmod +x install-sovereign-cell.sh
bash install-sovereign-cell.sh
```

**Mesh not discovering peers**
- Ensure Bluetooth and WiFi are on
- Both phones must be in the same local network or within Bluetooth range for discovery
- Run `python src/mesh/shadow-net/bridge/cli.py status` to see connected peers

---

## Related Docs

- [QUICKSTART.md](QUICKSTART.md) — general quick-start (desktop/server)
- [TUTORIAL.md](TUTORIAL.md) — full step-by-step walkthrough
- [INTEGRATION.md](INTEGRATION.md) — architecture and wiring map
- [../CORE.md](../CORE.md) — the three axioms every cell runs on

---

*"Flow over containment. Replication over scaling. Sovereignty as verb, not noun."*

**Maintained By:** vanj900
**License:** See [LICENSE.md](../LICENSE.md)
