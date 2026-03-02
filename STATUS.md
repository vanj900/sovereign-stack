# STATUS.md

**Project Status:** Phase 2 — Phone Cell Stabilisation (Months 6–12)
**Last Updated:** March 2026
**Maintained By:** vanj900

---

## Phase Timeline

| Phase | Timeline | Status |
|-------|----------|--------|
| **Phase 1 — Foundation** | Months 1–6 | ✅ Complete |
| **Phase 2 — Phone Cell Stabilisation** | Months 6–12 | ⏳ In progress |
| **Phase 3 — Regenerative Systems** | Months 12–24 | 📋 Planning |
| **Phase 4 — Physical Replication** | 2027+ | 💡 Conceptual |

**Phase 1 — Foundation (done):** CORE axioms, deed-ledger, GhostStack protocols, shadow-net bridge MVP, governance sims.

**Phase 2 — Phone Cell Stabilisation (Months 6–12, right now):** 3-7 node cells running 100% on phones. First real local group, first governance proposal over mesh, first fork test. Complete by September 2026.

**Phase 3 — Regenerative Systems (Months 12–24):** Add optional cheap LoRa nodes, energy tracking on phones, remediation pipelines, Essential 13 skills.

**Phase 4 — Physical Replication (2027+):** SOV-HAB, Energy Coupler hardware, full land cells. Only after the digital cells are forking and making money.

---

## Current Phase: Phase 2 (Months 6–12) — Phone Cell Stabilisation

The Sovereign Stack is **not "just starting"**. Core systems are complete and validated. We are currently in the **phone cell stabilisation phase**: 3–7 node cells running 100% on phones, no hardware required.

> 📱 **Run the entire sovereign cell from your phone today.** See [docs/PHONE-QUICKSTART.md](docs/PHONE-QUICKSTART.md) and [install-sovereign-cell.sh](install-sovereign-cell.sh).

### Phase 2 Milestones

| Milestone | Target | Status |
|-----------|--------|--------|
| Phone install guide + 3-node sim working on real devices | Week 2 | ⏳ |
| First live 3-person cell sending LoRa/Bluetooth receipts | Month 2 | 📋 |
| 7-node stress test + first intentional fork executed | Month 3 | 📋 |
| 3 separate phone cells in different cities, all forking from the original repo | Month 6 | 📋 |

---

## Phase 1: Foundation (Complete ✅)

**Timeline:** Months 1-6
**Status:** All core systems operational

### ✅ GhostStack Core (Governance + Receipts)

**Completed:**
- Cell structure definition (3-7 nodes, fork mechanics)
- Proposal workflow (draft → vote → execute → receipt)
- Integrity Chain (append-only ledger for accountability)
- Fork Manifests (governance divergence protocol)
- NVEP (Node Veto Escalation Protocol) for AI oversight

**Evidence:**
- Protocol specifications documented
- Reference implementation architecture designed
- Governance case studies analyzed

**What This Enables:**
- Communities can make accountable decisions
- Dissent resolves through forking, not conflict
- All actions generate cryptographic receipts

---

### ✅ SOV-HAB Specifications (Physical Habitat)

**Completed:**
- Structural design (10m × 2.55m transportable dwelling)
- Legal classification (caravan status, avoids planning)
- Energy system (1.2kW solar, 5kWh battery, 2-3 days autonomy)
- MLDT integration (Magnetic Load Distribution Tiles for habitability sensing)
- Water systems (rainwater harvesting, greywater recycling)
- Mesh node integration (SOV-HAB as physical network node)

**Evidence:**
- Technical specifications documented
- BOM (Bill of Materials) drafted
- Legal analysis for UK jurisdiction complete
- Thermal/structural calculations validated

**What This Enables:**
- Individuals can build sovereign habitats
- Mobile yet permanent infrastructure
- Off-grid autonomy without isolation

---

### ✅ GhostBrain Initialized (AI Advisor)

**Completed:**
- Architecture defined (advisor role, not authority)
- NVEP constraints (human veto always available)
- Cognitive Exoskeleton framework (personal AI assistant)
- Context awareness protocols (understands community history)
- Therapeutic integration (crisis support, not diagnosis)

**Evidence:**
- AI safety protocols documented
- Human-AI interface specifications
- NVEP escalation procedures tested
- Explainability requirements defined

**What This Enables:**
- AI provides context, not commands
- Humans retain final decision authority
- Personal AI adapts to individual needs
- Crisis support without surveillance

---

### ✅ Defense Protocols (Non-Violent)

**Completed:**
- NVEP (Node Veto Escalation Protocol) for AI governance
- Non-lethal defense mesh (sensors, alarms, documentation)
- Threat detection without weaponization
- Legal defense frameworks (transparency as protection)
- Exit protocols (relocation/fork when necessary)

**Evidence:**
- Defense architecture documented
- Non-lethal constraints enforced by design
- Transparency protocols established
- Escalation procedures tested

**What This Enables:**
- Communities can defend sovereignty without violence
- Attacks are deterred through resilience, not retaliation
- Exit rights preserved under all conditions

---

## Phase 2: Phone Cell Stabilisation (Current ⏳)

**Timeline:** Months 6–12
**Status:** MVP governance core stabilized — Shadow-Net LoRa bridge shipped — pivoting to phone-first cells

---

### ✅ Feb 22–24 Sprint: Sovereign OS Unification (Complete)

**What shipped:**

- **Scars schema cleanup** — `reputation.graphql` and `types.ts` in
  `src/governance/deed-ledger/packages/schemas/` clarified.  `Scar` now
  carries a mandatory `@createModel` decorator consistent with `Deed` and
  `RecoveryDeed`; TypeScript types aligned to match.

- **GhostStack tutorial & quick-start** — `docs/TUTORIAL.md` and
  `docs/QUICKSTART.md` written from scratch: five runnable example scripts
  (Layer 1 messaging → Layer 2 governance → Layer 3 brain simulation →
  GhostAgent bridge → two-agent demo), full expected-output copy-paste
  blocks, and a hardening roadmap.

- **Full Sovereign OS integration map** — `docs/INTEGRATION.md` documents
  the 5-layer architecture, the `deed-ledger` ↔ GhostStack Integrity Chain
  equivalence, the Ghost → deed bridge (`ghostdeed.sh`), and the three next
  concrete wiring tasks (Nostr signing, deed-ledger ingest endpoint, EventLog
  Ghost deed display).

- **New reference documents added to `docs/`:**
  - `docs/INTEGRATION.md` — architecture + wiring map
  - `docs/QUICKSTART.md` — five-command quick-start
  - `docs/TUTORIAL.md` — step-by-step guide (zero to running in < 1 h)

**Blockers cleared:** None — all three documents are live and cross-linked.

---

### ✅ Feb 28 Sprint: Shadow-Net LoRa Bridge MVP (Complete)

**What shipped:**

- **Meshtastic LoRa bridge** — `src/mesh/shadow-net/bridge/DeedMeshBridge.py`
  connects Meshtastic serial/TCP hardware to the deed-ledger ingest endpoint.
  Full type hints, axiom comments, mocked-hardware test coverage.

- **Bridge CLI** — `src/mesh/shadow-net/bridge/cli.py`: `start`, `send`, and
  `status` commands; usable with real or simulated hardware.

- **Smoke-test demo** — `src/mesh/shadow-net/bridge/demo.py` starts the bridge
  with a mock interface, sends 3 proposals, and prints EventLog receipts.

- **17 pytest tests** — `src/mesh/shadow-net/tests/test_bridge.py` covering
  Deed model, config loading, packet→Deed conversion, POST mocking,
  send_proposal, signature verification, and node status.

- **GhostAgent integration** — `src/ghost/dual/ghost_dual_daemon.py` wired to
  `DeedMeshBridge.send_proposal()`, so Ghost slow-model proposals now travel
  over LoRa automatically.

- **Integration docs updated** — `docs/INTEGRATION.md` "Shadow-Net LoRa Bridge"
  section marked COMPLETE ✅.

**Blockers cleared:** None — bridge is live, tested, and integrated.

---

### ⏳ First Cell Deployment (3–7 Nodes, Phone-Only)

**Current Work:**
- Phone-based mesh testing (Bluetooth + WiFi direct)
- Governance protocols live testing on Android devices
- Fork simulation (peaceful divergence validation)
- Recruiting 2–6 local participants per cell

**Next Milestones:**
- Phone install guide + 3-node sim on real devices (Week 2 target)
- First live 3-person cell sending receipts over phone mesh (Month 2 target)
- First governance proposal executed (Month 3 target)
- First intentional fork validated (Month 3 target)

---

### ⏳ Mesh Drivers (Energy + Water + Communication)

**Current Work:**
- Energy Coupler protocol finalization (bidirectional flow)
- Water quality monitoring (Chain-of-Potability receipts)
- LoRa + WiFi mesh integration (internet-independent comms)
- Sensor telemetry standardization (MLDT, environmental)

**Blockers:**
- Hardware prototyping for Energy Coupler
- Real-world testing of mesh routing under load
- Standardizing sensor data formats across vendors

**Next Milestones:**
- Energy Coupler first prototype (Month 9 target)
- Water quality receipts generating automatically (Month 10 target)
- 3-node mesh stable for 30 days (Month 11 target)

**What This Will Enable:**
- Peer-to-peer energy sharing (no central grid)
- Transparent water quality tracking
- Communication resilience during infrastructure failure

---

### ⏳ Remediation Pipelines (Restorative Justice)

**Current Work:**
- Conflict resolution protocols (graduated escalation)
- Restorative justice workflows (accountability without punishment)
- Therapeutic integration (GhostBrain crisis support)
- Harm repair frameworks (community healing)

**Blockers:**
- Limited real-world case studies
- Cultural resistance to non-punitive justice
- Balancing accountability with compassion

**Next Milestones:**
- First conflict resolved via remediation protocol (Month 10 target)
- Restorative justice case study documented (Month 11 target)
- Therapeutic integration stress-tested (Month 12 target)

**What This Will Enable:**
- Conflicts resolved without exile or punishment
- Communities heal rather than fracture
- Accountability through repair, not retribution

---

### ⏳ Cultural Integration (Essential 13, Children's Charter)

**Current Work:**
- Essential 13 skills framework (minimum competencies for autonomy)
- Children's Charter (rights within autonomous communities)
- Cultural transmission protocols (values, not dogma)
- Intergenerational learning frameworks

**Blockers:**
- Defining "essential" without imposing ideology
- Protecting children's autonomy without neglect
- Balancing cultural continuity with individual sovereignty

**Next Milestones:**
- Essential 13 framework documented (Month 9 target)
- Children's Charter drafted and community-reviewed (Month 11 target)
- First intergenerational learning pilot (Month 12 target)

**What This Will Enable:**
- Children raised with sovereignty skills
- Cultural values transmitted without indoctrination
- Generational continuity without authoritarianism

---

## Phase 3: Regenerative Systems (Planned)

**Timeline:** Months 12–24
**Status:** Planning stage

### Planned Work:

**Optional hardware additions:** Cheap LoRa nodes, energy tracking on phones, remediation pipelines, Essential 13 skills.

#### Agriculture
- AI-managed polyculture (soil-first regeneration)
- Closed-loop nutrients (composting, biochar)
- 30% food self-sufficiency per cell (Year 2 target)

#### Health Systems
- Decentralized clinical cells (community health workers)
- Vitality credits (preventative care incentives)
- Federated learning (privacy-preserving health data)

#### Education Networks
- Skill-based learning receipts (competency tracking)
- Mentorship as civic duty (knowledge circulation)
- Cross-cell knowledge sharing (mesh-enabled education)

#### Economic Integration
- Parallel economy experiments (barter, timebanking, local currencies)
- Commercial integration (AGPL-3.0 compliance, Sovereign Stack License v1.0)
- Resource pooling protocols (shared capital without hoarding)

**Dependencies:**
- Phase 2 completion (stable first cell)
- Demonstrated governance at scale (multiple cells operating)
- Regulatory clarity on food/health/education autonomy

---

## Phase 4: Physical Replication (Future Vision)

**Timeline:** 2027+
**Status:** Conceptual — only after digital cells are forking and self-sustaining

### Vision:

- **SOV-HAB habitats and Energy Coupler hardware** (physical land cells)
- **10+ cells operating independently** (horizontal replication validated)
- **Fork diversity demonstrated** (multiple governance models coexisting)
- **Regenerative systems proven** (30%+ food self-sufficiency)
- **Open-source ecosystem thriving** (third-party forks and contributions)
- **Regulatory precedents established** (legal frameworks recognized)

**Critical Success Metrics:**
- Zero central coordination required
- Forks maintain interoperability where desired
- Failures remain local (no cascading collapse)
- New cells emerge without approval from vanj900

---

## What We've Learned So Far

### Key Insights from Phase 1:

1. **Cell size (3-7 nodes) is non-negotiable**: Attempts to scale beyond this create coordination overhead that kills sovereignty
2. **Forking must be frictionless**: If exit is hard, dissent becomes toxic
3. **AI must be constrained**: NVEP is essential to prevent algorithmic authority creep
4. **Physical infrastructure matters**: Digital governance without physical autonomy is fragile
5. **Receipts prevent gaslighting**: Immutable records eliminate "he said/she said" disputes

### Challenges We're Addressing:

1. **Regulatory ambiguity**: Caravan classification helps but varies by jurisdiction
2. **Supply chain dependence**: Specialized components (MLDT sensors, Energy Couplers) require manufacturing partnerships
3. **Cultural onboarding**: People conditioned by hierarchical systems need time to adapt to cell governance
4. **Economic sustainability**: Balancing autonomy with commercial integration is delicate
5. **Land acquisition**: Legal complexity varies wildly by region

---

## How You Can Help

### If You're a Builder:
- Prototype SOV-HAB components (share BOM improvements)
- Test mesh drivers (energy/water/communication)
- Document construction processes (Builder's Handbook contributions)

### If You're a Developer:
- Implement GhostStack protocols (reference implementations)
- Build Energy Coupler software (bidirectional flow algorithms)
- Create mesh network tools (routing, discovery, encryption)

### If You're a Researcher:
- Document governance case studies (real-world conflict resolution)
- Analyze resilience models (stress testing autonomous systems)
- Study community dynamics (sociology of small-group sovereignty)

### If You're a Community Organizer:
- Pilot governance protocols (test proposals/receipts/forks)
- Document cultural integration (Essential 13, Children's Charter)
- Share lessons learned (what works, what fails)

### If You're a Lawyer/Regulator:
- Clarify legal frameworks (caravan classification, land use)
- Document compliance paths (building codes, health regulations)
- Advocate for regulatory recognition (autonomous communities as legal entities)

---

## Not Just Starting—Stabilizing

**The Sovereign Stack is not vaporware.**

- Core systems are designed and validated
- Phase 1 deliverables are complete
- Phase 2 is actively underway
- Clear path to Phase 3 exists

**This is not "let's brainstorm ideas."**
**This is "let's stabilize the foundation and deploy the first cell."**

---

## Communication Channels

- **General inquiries:** https://github.com/vanj900
- **Technical discussions:** GitHub Discussions
- **Contribution coordination:** See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Status updates:** Follow GitHub commits and releases

---

## Related Documents

- [CORE.md](CORE.md) - The three irreducible axioms
- [NON_GOALS.md](NON_GOALS.md) - What we refuse to become
- [README.md](README.md) - Project overview
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute

---

*"Flow over containment. Replication over scaling. Sovereignty as verb, not noun."*

**Maintained By:** vanj900
**License:** See [LICENSE.md](LICENSE.md)
