# Shadow-Net LoRa Bridge — Sovereign Stack

## Overview

Shadow-Net adds a **Meshtastic LoRa mesh layer** to the Sovereign Stack,
letting off-grid nodes exchange governance proposals and deed receipts without
any internet connection.

Every packet received on the mesh is converted to a **Sovereign Deed** (the
same schema used by `deed-ledger`) and posted to the ingest endpoint.  Every
proposal sent by the **GhostAgent AI advisor** travels back over the mesh so
off-grid nodes stay in sync.

Key motivations:

- **Meshtastic fork** — uses the stable Meshtastic Python API for hardware
  portability; the bridge abstraction means we can swap LoRa for BLE or WiFi
  without touching deed-ledger logic.
- **Deed receipts** — every mesh action produces a cryptographically signed
  `Deed` entry on the Integrity Chain.  No receipt = no accountability.
- **No ISP needed** — three Heltec V4 nodes within ~10 km form a resilient
  cell mesh.

---

## Architecture

```
  GhostAgent  ──send_proposal──►  DeedMeshBridge
                                       │
              ◄──deed_receipt──────────┤
                                       │  serial / TCP
                                   Meshtastic
                                    Interface
                                       │  LoRa 915 MHz
                              ┌────────┴────────┐
                           Node-A           Node-B
                              └────────┬────────┘
                                   Node-C
                                       │
                              deed-ledger ingest
                              (POST /api/deeds/ingest)
                                       │
                              Nostr relay broadcast
```

---

## Axiom Compliance

| CORE Axiom | Bridge mechanism |
|-----------|-----------------|
| **Flow over Containment** | Packets circulate; bridge never pools state |
| **Sovereignty via Forkability** | Swap serial/TCP/mock transport in one line |
| **Truth by Receipts** | Every received packet + sent proposal → signed Deed |

---

## Hardware BOM

| Component | Link | Notes |
|-----------|------|-------|
| Heltec WiFi LoRa 32 V4 | https://heltec.org/project/wifi-lora-32-v4/ | 915 MHz, SX1262, USB-C |
| LilyGo T-Beam v1.2 | https://www.lilygo.cc/products/t-beam | GPS + LoRa, solar-charge ready |
| 18650 LiPo cell | Any | 3000 mAh minimum recommended |
| USB-C cable | Any | Firmware flash + power |

Minimum for a 3-node cell: **2× Heltec V4 + 1× T-Beam**.

---

## Quickstart

### 1. Flash Meshtastic firmware

```bash
pip install esptool meshtastic
# Heltec V4
esptool.py --chip esp32s3 write_flash 0x0 \
  firmware-2.5.x.heltec-wifi-lora-32-V3.bin
```

### 2. Install bridge dependencies

```bash
cd src/mesh/shadow-net/bridge
pip install -r requirements.txt
```

### 3. Configure

Copy and edit `config.yaml`:

```bash
cp config.yaml.example config.yaml   # or edit config.yaml directly
# set meshtastic_port, deed_ingest_url, cell_id
```

### 4. Run the bridge

```bash
# blocking — listens for mesh packets and posts deeds
python cli.py start

# send a single proposal
python cli.py send "Proposal: share 50W solar"

# show mesh nodes + last 10 deeds
python cli.py status
```

### 5. Smoke-test with mock hardware

```bash
python demo.py
```

---

## Future: native ESP32 MicroPython version

The next evolution removes the laptop/SBC bridge entirely:

- **MicroPython firmware** running directly on the ESP32S3
- Deed schema encoded as compact CBOR messages
- LoRa packet → deed hash stored in flash; synced to deed-ledger on WiFi
  reconnect
- Target hardware: Heltec V4 (4 MB PSRAM, 8 MB flash — sufficient for
  MicroPython + deed store)

See `docs/FUTURE_MICROPYTHON.md` (planned) for the design spec.
