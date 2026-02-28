# Sovereign OS — Unified Monorepo

**One repository. Every layer of the sovereign civilization stack.**

This is the single unified home of the **Sovereign OS**: the complete, forkable blueprint for small sovereign communities to control their own energy, water, food, governance, AI, and communication — with no dependency on centralised institutions.

The monorepo integrates all layers:

| Layer | Path | What it is |
|-------|------|------------|
| **Governance / Integrity Chain** | `src/governance/deed-ledger` | GhostStack civic OS — deed ledger, scars, demurrage, portable exit, Nostr broadcast |
| **AI Advisor** | `src/ai/ghost` | Ghost daemon — ephemeral RAM-based AI with deed posting bridge |
| **Thermodynamic AI** | `src/ai/thermo-ai` | Bio-digital organism under real metabolic constraints |
| **Mesh** | `src/mesh/shadow-net` | Peer-to-peer routing without ISP or internet |
| **Psych / Integrity** | `src/psych/precisionlocked` | Cognitive integrity and pattern analysis |
| **Audit Tools** | `src/tools/red-flag-auditor` | Red-flag detection and governance auditing |

See [docs/INTEGRATION.md](docs/INTEGRATION.md) for the full 5-layer architecture map, the deed-ledger ↔ Ghost bridge design, and wiring notes.

It is built on three irreducible principles—Flow Over Containment, Sovereignty via Forkability, and Truth by Receipts—that are architectural constraints, not aspirations. See [CORE.md](CORE.md).

> ⚠️ **Design Phase** — Core systems are specified and Phase 1 is complete. This is not yet production-ready. Do not begin construction without reading the current [STATUS.md](STATUS.md) and consulting local professionals.

---

## Table of Contents

- [What Is This?](#what-is-this)
- [Three Core Axioms](#three-core-axioms)
- [Five-Layer Architecture](#five-layer-architecture)
- [Hardware Subsystems](#hardware-subsystems)
- [Software Components](#software-components)
- [Project Status & Timeline](#project-status--timeline)
- [Documentation](#documentation)
- [Where to Start (by role)](#where-to-start-by-role)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## What Is This?

Modern infrastructure concentrates control: energy grids, financial systems, and governance structures all funnel power upward. The Sovereign Stack is a counter-architecture—a complete, forkable blueprint for communities that want to control their own energy, water, food, governance, and communication without depending on centralised institutions.

The basic unit is a **Cell**: 3–7 nodes (households or individuals). When a Cell grows beyond that, it forks horizontally into new Cells rather than scaling into hierarchy. Every action—every vote, energy transfer, or water quality reading—generates a cryptographic **Receipt** on an append-only **Integrity Chain**, replacing institutional trust with mathematical accountability.

This is not a startup, a government, a blockchain project, or a utopia. See [NON_GOALS.md](NON_GOALS.md) for the four boundaries we actively defend.

---

## Three Core Axioms

These are described in full in [CORE.md](CORE.md). They function as the physics of the system: breaking them breaks the stack.

### 1. Flow Over Containment
> *"Containment breeds stagnation; flow breeds resilience."*

Energy, data, and trust must circulate rather than accumulate. Resources route to where they create value or convert to other forms; static hoarding is structurally prevented.

### 2. Sovereignty via Forkability
> *"Everything forks, nothing centralises."*

The Cell (3–7 nodes) is the maximum unit. Growth happens by replication, not hierarchy. Any community can fork code, governance, and ledgers at any time—exit rights are unconditional.

### 3. Truth by Receipts
> *"Receipts replace bureaucracy."*

Every meaningful action generates a cryptographically signed Receipt on the Integrity Chain. Power requires proof, not proclamation.

---

## Five-Layer Architecture

The Sovereign Stack has five interdependent layers:

| Layer | What It Does |
|-------|-------------|
| **Energy** | Bidirectional energy sharing between nodes via the Energy Coupler; solar/battery at each site |
| **Mesh** | Peer-to-peer communication (LoRa + WiFi) that functions without ISP or internet |
| **GhostStack** | Civic OS: proposals, voting, the Integrity Chain, fork mechanics, and governance receipts |
| **GhostBrain** | AI advisor (not ruler): context-aware recommendations with mandatory human veto (NVEP) |
| **Physical** | SOV-HAB habitats, MLDT floor system, water and energy hardware |

See [docs/01_Core_Architecture/](docs/01_Core_Architecture/) for the full architectural design.

---

## Hardware Subsystems

Physical designs live in [hardware/](hardware/). All are open-source (AGPL-3.0) and in active design/specification phase.

| Subsystem | Description | Status |
|-----------|-------------|--------|
| **SOV-HAB** | Transportable sovereign habitat (10 m × 2.55 m, caravan-legal in UK) | Design phase |
| **MLDT** | Magnetic Load-Distribution Tile System — passive seismic/vibration isolation floor | Specification phase |
| **HabCal** | Habitability Calculator — environmental sensors and data logging | Specification phase |
| **Energy Systems** | Solar panels, battery banks, inverters, Energy Coupler interface | Specification phase |
| **Water Systems** | Rainwater harvesting, greywater recycling, Chain-of-Potability receipts | Design phase |

> ⚠️ Hardware designs are provided "AS IS." Review local building codes, consult licensed professionals, and obtain required permits before construction. See [hardware/README.md](hardware/README.md) for full safety notices.

---

## Software Components

Source code lives in [src/](src/). All are early-stage; APIs and architecture are subject to change.

| Component | Description | Language | Status |
|-----------|-------------|----------|--------|
| **GhostStack** | Civic OS — governance, identity, Integrity Chain, resource allocation | TBD (Rust/Go) | Design phase |
| **Energy Coupler** | Bidirectional energy flow control, demand forecasting, grid interface | TBD (embedded) | Specification phase |
| **Mesh** | Peer-to-peer routing, encryption, discovery, clearnet bridge | TBD (cross-platform) | Research phase |

See [src/README.md](src/README.md) for the proposed technology stack and contribution guidelines.

---

## Project Status & Timeline

Full details in [STATUS.md](STATUS.md).

| Phase | Timeline | Status |
|-------|----------|--------|
| **Phase 1 — Foundation** | Months 1–6 | ✅ Complete |
| **Phase 2 — Stabilisation & First Cell** | Months 6–12 | ⏳ In progress |
| **Phase 3 — Regenerative Systems** | Months 12–24 | 📋 Planning |
| **Phase 4 — Replication** | Months 24+ | 💡 Conceptual |

**Phase 1 deliverables (complete):** GhostStack core, SOV-HAB specifications, GhostBrain architecture, defense protocols.

**Phase 2 current work:** First SOV-HAB prototype, multi-node mesh testing, governance protocols live testing, Energy Coupler hardware prototype.

---

## Documentation

```
docs/
├── 00_Foundation/          # Philosophy, crisis context, manifesto
├── 01_Core_Architecture/   # Five layers, GhostStack, GhostBrain, security
├── 02_System_Protocols/    # Cell cooperation, crisis handling, governance
├── 03_Living_Meshes/       # Energy, food, water, health, learning subsystems
├── 04_Implementation/      # Build guides, BOM, code architecture
└── QUICKSTART.md           # Fastest path to getting started
```

Start at [docs/README.md](docs/README.md) for a guided path through all documentation.

---

## Where to Start (by role)

### 🆕 Brand new?
1. [CORE.md](CORE.md) (15 min) — understand the three axioms
2. [docs/00_Foundation/](docs/00_Foundation/) (30 min) — learn the philosophy
3. [STATUS.md](STATUS.md) (10 min) — see where things stand

### 🔨 Builder (physical construction)
1. [CORE.md](CORE.md) — understand the principles
2. [hardware/README.md](hardware/README.md) — hardware overview and safety notices
3. [docs/04_Implementation/](docs/04_Implementation/) — build guides and BOMs

### 💻 Developer (software/protocols)
1. [CORE.md](CORE.md) — understand the constraints
2. [docs/01_Core_Architecture/](docs/01_Core_Architecture/) — system design
3. [src/README.md](src/README.md) — code overview and contribution workflow

### 🔬 Researcher
1. [docs/00_Foundation/](docs/00_Foundation/) — theoretical foundations
2. [docs/01_Core_Architecture/](docs/01_Core_Architecture/) — system design
3. [docs/03_Living_Meshes/](docs/03_Living_Meshes/) — subsystem details

### 🤝 Community organiser
1. [CORE.md](CORE.md) — governance principles
2. [docs/02_System_Protocols/](docs/02_System_Protocols/) — governance protocols
3. [STATUS.md](STATUS.md) — how to get involved

### 🤨 Sceptical?
1. [NON_GOALS.md](NON_GOALS.md) — what we explicitly refuse to become
2. [CORE.md](CORE.md) — the constraints, not the promises
3. [GitHub Discussions](https://github.com/vanj900/sovereign-stack/discussions) — ask questions

---

## Contributing

All contributions are welcome: code, hardware designs, documentation, protocols, governance research, and community support.

**Before contributing, read [CORE.md](CORE.md).** Understanding the three irreducible axioms is essential for meaningful contribution.

Full contribution guidelines, coding standards, hardware design standards, and the PR workflow are in [CONTRIBUTING.md](CONTRIBUTING.md).

**Quick summary:**
- Software: Python, Rust, TypeScript (see [src/README.md](src/README.md))
- Hardware: FreeCAD, KiCad (see [hardware/README.md](hardware/README.md))
- Docs: Markdown, SVG diagrams (see [docs/README.md](docs/README.md))
- Security vulnerabilities: report via [GitHub Issues](https://github.com/vanj900/sovereign-stack/issues) (not public issues)

---

## License

**Dual-licensed by vanj900 (@vanj900)**

| Use Case                              | License                          |
|---------------------------------------|----------------------------------|
| Personal, family, community, education, research, non-profit | **Class A — AGPL-3.0** (free)   |
| Manufacturing, paid services, proprietary integration, for-profit | **Class B** — requires explicit written approval from vanj900 |

Forking is explicitly encouraged. Forks must rename the project and keep full attribution.  
See [LICENSE.md](LICENSE.md) for full terms.

---

## Contact

| Purpose | Channel |
|---------|---------|
| General inquiries | [GitHub](https://github.com/vanj900) |
| Commercial licensing (Class B) | [GitHub](https://github.com/vanj900) |
| Security vulnerabilities | [GitHub Issues](https://github.com/vanj900/sovereign-stack/issues) (use private disclosure if sensitive) |
| Technical discussions | [GitHub Discussions](https://github.com/vanj900/sovereign-stack/discussions) |
| Bug reports / feature requests | [GitHub Issues](https://github.com/vanj900/sovereign-stack/issues) |

---

*"Flow over containment. Replication over scaling. Sovereignty as verb, not noun."*

**Maintained By:** vanj900 (https://github.com/vanj900)
**License:** See [LICENSE.md](LICENSE.md)
**Last Updated:** January 2026