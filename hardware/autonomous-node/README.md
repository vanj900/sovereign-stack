# Autonomous Node Platform

**A Unified Infrastructure System for Sovereign Communities**

---

## Overview

The **Autonomous Node** is a modular platform for off-grid living and food production that forms the physical foundation of the Sovereign Stack. It integrates energy independence, water autonomy, digital connectivity, and environmental control into variants optimized for specific functions.

All variants share a common subsystem architecture, enabling:
- **Interoperability**: Nodes connect via energy mesh and sovereign mesh
- **Maintainability**: Standardized components across variants
- **Scalability**: Proven subsystems replicate reliably
- **Evolution**: Learnings from one variant improve all others

---

## Platform Variants

### DOME-01: Food Production Node (Current Development)

**Status:** Active design phase, technical specification complete

**Form Factor:**
- Geodesic dome structure (Ø6.0m, height ≤2.45m)
- 28.27m² footprint
- Single-storey outbuilding classification

**Primary Function:**
- Autonomous food production (3-4 people at 100% RDA)
- Vertical agriculture (28m² growing surface)
- Year-round nutritional security

**Legal Strategy:**
- UK Permitted Development (outbuilding, incidental use)
- No planning permission required (site conditions permitting)

**Key Differentiators:**
- Transparent shell (polycarbonate dome) for natural light
- Vertical rack systems for intensive growing
- Mushroom cultivation in thermal buffer bay
- Optimized for plant production, not habitation

**Documentation:** [`dome-01/`](dome-01/)

---

### SOV-HAB: Dwelling Node (Future Development)

**Status:** Concept phase, informed by DOME-01 validation

**Form Factor:**
- Rectangular transportable structure (10m × 2.55m)
- ~25m² internal floor area
- Chassis-mounted, relocatable

**Primary Function:**
- Human habitation (sleeping, cooking, living)
- Energy/water/mesh node for community
- Mobile sovereignty (legal + physical)

**Legal Strategy:**
- UK Caravan Act compliance
- Classified as mobile home, avoids permanent planning restrictions
- Can be relocated without losing legal status

**Key Differentiators:**
- Opaque insulated envelope (thermal performance priority)
- Integrated living quarters (kitchen, bath, bedroom)
- Transportability via truck (not continuous towing)
- Optimized for habitation, not food production

**Documentation:** [`sov-hab/`](sov-hab/) *(coming soon)*

---

## Shared Subsystem Architecture

Both variants are built on the same foundational systems. This creates:
- **Reduced R&D cost**: Prove once, deploy everywhere
- **Supply chain efficiency**: Bulk purchasing of common components
- **Cross-training**: Installers/maintainers learn one system
- **Resilience**: If one variant succeeds, all variants benefit

### Common Subsystems

#### 1. Energy System
**Function:** Solar generation + battery storage + DC microgrid

**Core Components:**
- Solar array (1.2-7 kWp depending on variant/mode)
- LiFePO₄ battery bank (5-30 kWh)
- MPPT charge controller (48V)
- DC distribution (pumps, fans, LEDs native DC)
- Optional inverter (230V AC for tools/appliances)

**Innovation:** **48V DC Anderson couplers** enable peer-to-peer energy sharing between nodes.

**Documentation:** [`shared-subsystems/energy-system.md`](shared-subsystems/energy-system.md)

---

#### 2. Water System
**Function:** Rainwater harvesting + treatment + closed-loop recycling

**Core Components:**
- Collection (gutters, downpipes, first-flush diversion)
- Storage (raw water 500-1000L, potable 200-300L)
- Treatment (UV sterilization, activated carbon, optional RO for coastal)
- Distribution (12V pumps, manifold, color-coded quick-connect fittings)
- Greywater recovery (bio-filter + UV for non-potable reuse)

**Innovation:** Treats water as packet-switched resource, routes by quality and need.

**Documentation:** [`shared-subsystems/water-system.md`](shared-subsystems/water-system.md)

---

#### 3. Thermal Buffer Bay (TBB)
**Function:** Non-excavated underfloor utility vault providing thermal mass and service access

**Core Components:**
- Prefabricated insulated cassettes (600mm internal height)
- Water tanks, battery enclosure, storage bins
- Mushroom cultivation module (DOME-01)
- Service hatches (600×600mm) for maintenance

**Innovation:** Raised vault (not dug) means no excavation permits, relocatable if needed.

**Documentation:** [`shared-subsystems/thermal-buffer-bay.md`](shared-subsystems/thermal-buffer-bay.md)

---

#### 4. Control System
**Function:** Sensors + automation + AI advisor (GhostBrain)

**Core Components:**
- Industrial PLC or Raspberry Pi-based controller
- Sensor array (temperature, humidity, CO₂, pH, EC, water level, leak detection)
- 10" touchscreen display
- Optional connectivity (WiFi, 4G for remote monitoring)
- GhostBrain AI: advisor/simulator/auditor (not arbiter)

**Innovation:** Human override always available (Node Veto Escalation Protocol). AI suggests, humans decide.

**Documentation:** [`shared-subsystems/control-system.md`](shared-subsystems/control-system.md)

---

#### 5. Structural Base
**Function:** Anchoring + leveling + foundation interface

**Core Components:**
- Screw piles (6-10 piles, 1200-1800mm depth) OR ballasted ring beam
- Leveling brackets (±5mm tolerance)
- Ground preparation (geotextile, gravel drainage)
- Anti-creep anchoring (wind/seismic resistance)

**Innovation:** Touch the earth lightly. Designed for relocation if needed, minimal site disturbance.

**Documentation:** [`shared-subsystems/structural-base.md`](shared-subsystems/structural-base.md)

---

## Design Philosophy: Mutation, Not Fragmentation

The Autonomous Node platform is designed to **evolve**, not fork into incompatible products.

### Why DOME-01 First?

**DOME-01 serves as the proving ground** for the entire platform:

1. **Lower stakes**: Food production failure is recoverable; housing failure is catastrophic
2. **Regulatory simplicity**: Outbuilding classification easier than dwelling
3. **System validation**: Energy, water, thermal, control systems tested under real load
4. **Economic model**: Proves OPEX, maintenance intervals, user labor requirements
5. **Supply chain**: Establishes vendor relationships, bulk pricing, installer training

### The Mutation Path: DOME-01 → SOV-HAB

Once DOME-01 validates the core subsystems (12-24 months field testing), those systems migrate directly into SOV-HAB with minimal modification:

| Subsystem | DOME-01 Implementation | SOV-HAB Adaptation |
|-----------|------------------------|---------------------|
| **Energy** | 3-7 kWp solar, 10-30 kWh battery | Same components, different mounting (roof vs ground array) |
| **Water** | 500-1000L raw, 200-300L potable, greywater recycling | Add shower/sink drainage, same treatment chain |
| **Thermal Buffer Bay** | Mushroom cultivation + utility storage | Battery + water tanks + tool storage (no mushrooms) |
| **Control** | GhostBrain manages grow systems | GhostBrain manages HVAC + home systems |
| **Structure** | Geodesic dome shell | Rectangular SIP panels on chassis |

**Key insight:** The *guts* stay the same. Only the *skin* changes.

---

## Interoperability: Nodes in Community

### The Mesh Network

All Autonomous Nodes are designed to connect via:

**Energy Mesh:**
- 48V DC couplers between neighboring nodes
- AI-mediated power routing (give-when-able, receive-when-needed)
- Contribution credits + trust metrics (not price signals)

**Sovereign Mesh:**
- WiFi mesh (local intranet) + LoRa (long-range backbone)
- Operates independently of ISPs/internet
- Governance, chat, file sharing, service discovery

**GhostStack Integration:**
- Each node participates in cell governance
- Proposals, votes, receipts logged locally
- Forks peacefully when conflict arises

### Example: 3-Node Micro-Community

```
[SOV-HAB-01]───────[DOME-01-A]
  (Alice's home)    (Alice's food)
       │                │
       └────Energy──────┤
       └────Mesh────────┤
                        │
                   [SOV-HAB-02]
                   (Bob's home, shares
                    DOME-01-A surplus)
```

**Outcome:**
- Alice lives in SOV-HAB-01, grows food in DOME-01-A
- Bob lives in SOV-HAB-02, trades labor-hours for food from DOME-01-A
- Energy flows between all three nodes based on generation/need
- Mesh enables governance + communication without internet
- If disagreement arises, they fork peacefully rather than fight

---

## Development Status

### DOME-01 (Active)

✅ Technical specification complete
✅ BOM finalized (Sections 10-11)
✅ Regulatory pathway mapped (UK PD)
✅ Installation sequence documented
🔄 Demonstration unit construction (pending)
🔄 12-month field validation (pending)

**Next Actions:**
- Build first unit (see [`dome-01/specifications.md`](dome-01/specifications.md))
- Collect operational data
- Refine based on real-world performance

---

### SOV-HAB (Future)

📋 Concept phase
📋 Informed by DOME-01 learnings
⏳ Design specification: After DOME-01 validation
⏳ Prototype construction: 12-18 months post-DOME-01

**Waiting for:**
- DOME-01 energy system performance data (winter load, autonomy days)
- DOME-01 water system validation (closed-loop stability, treatment effectiveness)
- DOME-01 control system refinement (sensor reliability, GhostBrain UX)
- DOME-01 TBB thermal performance (passive temperature stability)

**Why wait:** Don't build a dwelling with unproven life-support systems.

---

## Economic Model

### Capital Cost Comparison

| Variant | Base Config | Enhanced Config | Target Market |
|---------|-------------|-----------------|---------------|
| **DOME-01** | £33,500-52,500 (Mode A) | £50,000-78,000 (Mode B) | Food security, homesteads, institutions |
| **SOV-HAB** | £45,000-65,000 (est.) | £60,000-85,000 (est.) | Off-grid living, mobile sovereignty |

### Operational Cost (Annual)

| Cost Category | DOME-01 | SOV-HAB (est.) |
|---------------|---------|----------------|
| Consumables | £850-1,500 | £300-600 |
| Maintenance | £500-980 | £800-1,200 |
| Utilities (if grid-tied backup) | £0-600 | £0-800 |
| **Total OPEX** | **£1,350-3,080** | **£1,100-2,600** |

### Combined Deployment

**Complete off-grid homestead:**
- 1× SOV-HAB (living quarters)
- 1× DOME-01 (food production)
- Total capital: £78,500-130,500
- Total OPEX: £2,450-5,680/year
- Supports: 2-4 people in complete autonomy

**Comparison:** UK household spending on rent + food = £15,000-25,000/year
**Payback:** Never, on pure economics. This is **resilience infrastructure**, not cost-saving.

---

## Why This Matters

The Autonomous Node platform is not about "tiny houses" or "urban farming."

It is about **building the physical infrastructure for communities that cannot be contained, co-opted, or collapsed** by centralized systems.

### The Test

Can a small group of humans, armed with these blueprints, build a thriving community that operates independently of—yet peacefully alongside—the industrial civilization that currently contains them?

- **If yes:** The Sovereign Stack succeeds by enabling others to fork it.
- **If no:** The documentation of this attempt becomes a learning resource for the next generation.

### The Path Forward

1. **Prove DOME-01** (food production autonomy)
2. **Evolve to SOV-HAB** (living quarters autonomy)
3. **Connect via mesh** (energy + data + governance autonomy)
4. **Replicate, not scale** (growth through forking, not hierarchy)

---

## Documentation Structure

```
autonomous-node/
├── README.md                    ← You are here
├── shared-subsystems/           ← Common to all variants
│   ├── energy-system.md
│   ├── water-system.md
│   ├── thermal-buffer-bay.md
│   ├── control-system.md
│   └── structural-base.md
├── dome-01/                     ← Food production variant
│   ├── README.md
│   ├── specifications.md        (Full spec from PDF)
│   ├── shell-structure.md       (Geodesic dome)
│   ├── vertical-agriculture.md  (Rack systems + hydroponics)
│   ├── bom.md                   (Bill of materials)
│   └── regulatory-compliance.md (UK PD pathway)
└── sov-hab/                     ← Dwelling variant (coming soon)
    ├── README.md
    ├── specifications.md
    ├── chassis-structure.md
    ├── habitation-layout.md
    ├── bom.md
    └── regulatory-compliance.md
```

---

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for:
- How to propose design improvements
- Component testing protocols
- Field data submission
- Installation documentation standards

---

## License

This platform design is released under the Sovereign Stack License v1.0 (AGPL-3.0 + Additional Sovereign Terms):

**Small Operators:** Full AGPL-3.0 rights plus explicit commercial rights (manufacture, sell, offer services).
**Large Entities:** Internal non-commercial use only; commercial deployment requires a paid license (sovereign@ghoststack.dev).

See [LICENSE.md](../../LICENSE.md) for full terms.

---

**Autonomous Node Platform**
*Version 1.0 - January 2026*
*Flow over containment. Replication over scaling. Sovereignty as verb, not noun.*
