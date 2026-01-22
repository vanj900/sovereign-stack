# Autonomous Node: Unified Platform Architecture

**A single infrastructure platform. Multiple configurations. Complete sovereignty.**

---

## The Core Concept

The **Autonomous Node** is not a single product—it's a **unified platform** of shared subsystems that can be configured for different purposes:

- **DOME-01** → Food production (geodesic greenhouse)
- **SOV-HAB** → Habitation (transportable dwelling)
- **Future variants** → Workshops, clinics, schools, storage

All variants share:
- Energy independence (solar + battery + DC microgrid)
- Water autonomy (harvesting + treatment + storage)
- Thermal regulation (thermal buffer bay + heat distribution)
- Intelligent control (sensors + automation + GhostBrain integration)
- Modular construction (standardized mounting points, interfaces, protocols)

**This is not "one size fits all." This is "one infrastructure, many applications."**

---

## Design Philosophy

### 1. Shared Infrastructure, Not Shared Purpose

Traditional modular systems fail because they try to make one thing do everything poorly. The Autonomous Node succeeds because it provides **common infrastructure** while allowing **specialized superstructures**.

**What's shared:**
- Energy generation and storage
- Water collection and treatment
- Foundation and anchoring systems
- Control and monitoring electronics
- Thermal management

**What's variant-specific:**
- Shell structure (dome vs. container vs. custom)
- Interior layout (agriculture vs. living vs. work)
- Regulatory pathway (Permitted Development vs. Caravan Act vs. full planning)
- Use case optimization (light levels, climate control, access patterns)

### 2. Standardized Interfaces, Not Standardized Forms

Like USB-C ports work with infinite devices, Autonomous Node subsystems use **standardized interfaces**:

- **Power:** 48V DC microgrid with standard connectors
- **Water:** Standardized pipe fittings and flow sensors
- **Data:** Mesh network protocols for sensor/control
- **Mounting:** Bolt patterns and load-bearing specifications

This means:
- Subsystems can be upgraded independently
- Third-party components can integrate (if they follow specs)
- Failures are local, not cascading
- Communities can fork designs without breaking interoperability

### 3. Anti-Fragile Through Diversity

By supporting multiple variants, the Autonomous Node ecosystem becomes **anti-fragile**:

- **Regulatory resilience:** If one pathway closes (e.g., UK bans caravans), other variants remain viable
- **Supply chain resilience:** If one shell material becomes unavailable, communities switch variants
- **Use case diversity:** Food production, habitation, and workspace all contribute to community resilience
- **Innovation diversity:** Forked designs explore different approaches without breaking the core platform

---

## Shared Subsystems

All Autonomous Node variants integrate these core systems:

### [Energy System](shared-subsystems/energy-system.md)
- **Solar array:** 1.2-3kW depending on variant
- **Battery storage:** 5-15kWh (2-3 days autonomy)
- **DC microgrid:** 48V distribution with inverter for AC loads
- **Energy Coupler:** Bidirectional grid interface (import/export)
- **Monitoring:** Per-circuit power metering

### [Water System](shared-subsystems/water-system.md)
- **Rainwater harvesting:** Roof catchment + filtration
- **Treatment:** UV sterilization + optional reverse osmosis
- **Storage:** 500-2000L depending on variant
- **Chain-of-Potability:** Sensor-based quality receipts
- **Greywater recycling:** Optional for high-usage variants

### [Thermal Buffer Bay](shared-subsystems/thermal-buffer-bay.md)
- **Underfloor utility vault:** Houses batteries, water tanks, pumps
- **Thermal mass:** Water tanks act as heat/cold storage
- **Heat distribution:** Pipes circulate warm water from solar thermal or waste heat
- **Condensation management:** Prevents moisture buildup
- **Access:** Removable floor panels for maintenance

### [Control System](shared-subsystems/control-system.md)
- **Environmental sensors:** Temperature, humidity, CO2, light levels
- **Resource monitoring:** Energy production/consumption, water levels
- **Automation:** Climate control, pump scheduling, alert thresholds
- **GhostBrain integration:** AI-optimized resource management
- **Mesh networking:** Connects to Sovereign Mesh for community coordination

### [Structural Base](shared-subsystems/structural-base.md)
- **Foundation options:** Concrete pads, ground screws, or ballast
- **Anchoring:** Wind load resistance (varies by shell type)
- **Mounting points:** Standardized interfaces for shell attachment
- **Leveling:** Adjustable supports for uneven terrain
- **Modularity:** Subsystems bolt on/off without structural modifications

---

## Current Variants

### [DOME-01: Food Production Node](dome-01/)

**Purpose:** Autonomous greenhouse for year-round food production

**Shell:** Geodesic dome (hemispherical, self-supporting)
**Footprint:** 4.5m diameter (15.9m² internal)
**Height:** 2.25m (suitable for vertical agriculture racks)
**Regulatory:** UK Permitted Development (no planning permission)

**Optimizations:**
- High light transmission (polycarbonate glazing)
- Vertical growing racks (5 tiers, hydroponics)
- Climate control (ventilation, heating, cooling)
- Water integration (nutrient delivery, recirculation)

**Status:** Phase 2 - Design refinement, first prototype planned

**[Full specifications →](dome-01/specifications.md)**

---

### [SOV-HAB: Autonomous Dwelling](sov-hab/)

**Purpose:** Mobile yet permanent habitation with full autonomy

**Shell:** Shipping container or custom chassis (10m × 2.55m)
**Footprint:** 25.5m² internal
**Height:** 2.6m (standing room)
**Regulatory:** UK Caravan Act (avoids planning permission)

**Optimizations:**
- Habitable interior (sleeping, cooking, working, living)
- Insulation (thermal comfort year-round)
- Privacy (opaque walls, window placement)
- Mobility (transportable on truck, semi-permanent once placed)

**Status:** Phase 3 - Planned for deployment after DOME-01 validation

**[Full specifications →](sov-hab/specifications.md)** *(coming soon)*

---

## How to Use This Documentation

### If you're building DOME-01:
1. Read [dome-01/README.md](dome-01/README.md) for overview
2. Review [dome-01/specifications.md](dome-01/specifications.md) for full specs
3. Study shared subsystems (energy, water, thermal, control)
4. Check [dome-01/bom.md](dome-01/bom.md) for Bill of Materials
5. Follow [dome-01/regulatory-compliance.md](dome-01/regulatory-compliance.md) for UK PD pathway

### If you're designing a new variant:
1. Understand shared subsystem interfaces (standardized power, water, data, mounting)
2. Review existing variants to see what's already solved
3. Define your variant's unique requirements (shell, layout, regulatory pathway)
4. Fork this repo and create `hardware/autonomous-node/your-variant/`
5. Document deviations from shared subsystems (if any)

### If you're contributing to shared subsystems:
1. Improvements to energy/water/thermal/control benefit ALL variants
2. Maintain backward compatibility (or version your changes)
3. Test across multiple variants (don't optimize for just one)
4. Document interface changes clearly (breaking changes require major version bump)

---

## Interoperability and Forking

### Fork-Compatible Design

Any variant can fork the Autonomous Node platform as long as it:
- **Respects interface standards** (power, water, data, mounting)
- **Documents deviations** (if any subsystems are modified)
- **Maintains attribution** (links back to original Sovereign Stack project)

Forked variants can:
- Use different shell structures (triangular, rectangular, custom)
- Modify subsystem sizing (more/less solar, larger/smaller water tanks)
- Add entirely new subsystems (e.g., aquaponics, composting toilets)
- Diverge regulatory pathways (non-UK jurisdictions)

**Forking is encouraged.** Diversity strengthens the ecosystem.

### Cross-Variant Learning

Innovations in one variant often benefit others:
- **DOME-01's vertical racks** → Could be adapted for SOV-HAB vertical storage
- **SOV-HAB's insulation strategy** → Could reduce DOME-01 heating costs
- **New control algorithms** → Apply across all variants
- **Third-party integrations** → Benefit everyone if they follow interface standards

---

## Regulatory Strategy

Different variants = different regulatory pathways:

### DOME-01 (UK Permitted Development)
- **No planning permission** if under 5m² and under 2.5m height
- **Outbuilding classification** (not habitable dwelling)
- **Temporary structure** (designed for disassembly)

### SOV-HAB (UK Caravan Act)
- **No planning permission** if not permanent foundation
- **Caravan classification** (mobile structure on wheels or skids)
- **28-day rule** (can occupy without consent for up to 28 days/year, or longer with permission)

### Future Variants
- **Workshop:** Industrial shed regulations
- **Clinic:** Healthcare facility compliance
- **School:** Educational building standards

**Key insight:** By supporting multiple regulatory pathways, the Autonomous Node ecosystem is resilient to policy changes in any single category.

---

## Technical Specifications (Cross-Variant)

### Power System
- **Voltage:** 48V DC (safe, efficient, standard for off-grid)
- **Solar capacity:** 1.2-3kW (variant-dependent)
- **Battery capacity:** 5-15kWh (2-3 days autonomy)
- **Grid interface:** Energy Coupler (bidirectional, optional)

### Water System
- **Catchment area:** Roof surface (variant-dependent)
- **Storage capacity:** 500-2000L (variant-dependent)
- **Treatment:** UV sterilization + filtration
- **Monitoring:** Flow sensors + quality sensors (turbidity, pH, temperature)

### Data/Control
- **Mesh network:** WiFi + LoRa (Sovereign Mesh compatible)
- **Sensors:** Temperature, humidity, CO2, light, power, water
- **Automation:** Programmable logic (GhostBrain integration)
- **Receipts:** All sensor readings logged to Integrity Chain

### Structural
- **Foundation:** Modular (concrete pads, ground screws, or ballast)
- **Wind resistance:** Engineered per variant (dome vs. box vs. custom)
- **Snow load:** Designed for UK climate (40 kg/m² minimum)
- **Seismic:** Not required for UK, but can be specified for other regions

---

## Bill of Materials (Shared Components)

**Full BOM varies by variant.** Shared components across all variants:

| Component | Specification | Quantity | Approx. Cost |
|-----------|---------------|----------|--------------|
| Solar panels | 300W monocrystalline | 4-10 | £200 each |
| Battery bank | 48V lithium (LiFePO4) | 5-15kWh | £1500-4000 |
| Charge controller | MPPT 60A | 1 | £300 |
| DC-DC converters | 48V → 12V/5V | 2 | £50 each |
| Inverter | 48V DC → 230V AC | 1 | £400 |
| Water tank | Food-grade IBC (1000L) | 1-2 | £100 each |
| UV sterilizer | 10-20 GPM flow rate | 1 | £200 |
| Submersible pump | 12V DC | 2 | £50 each |
| Environmental sensors | Temp/humidity/CO2 | 3-5 | £30 each |
| Mesh node | Raspberry Pi 4 + LoRa HAT | 1 | £100 |

**Total shared infrastructure cost: £3,000-6,000** (varies by sizing)

**Variant-specific costs (shell, interior, etc.): £2,000-8,000**

**Total Autonomous Node: £5,000-14,000** depending on variant and specifications.

---

## Safety and Compliance

All variants must address:

### Electrical Safety
- **48V DC:** Safer than mains voltage, but still requires proper wiring
- **Fusing:** Every circuit protected with appropriate fuses
- **Grounding:** All metal components bonded to earth
- **Waterproofing:** IP65+ rated for outdoor components

### Structural Safety
- **Load calculations:** Engineer-verified for roof loads (solar, snow, wind)
- **Anchoring:** Adequate for worst-case wind speeds (UK: 120 mph gusts)
- **Fire resistance:** Materials meet building regulations (where applicable)
- **Emergency egress:** All habitable variants have multiple exits

### Water Safety
- **Potable water:** UV sterilization + filtration (meets WHO standards)
- **Legionella prevention:** Water temperature management
- **Backflow prevention:** Check valves prevent contamination
- **Regular testing:** Chain-of-Potability sensors + manual lab tests

---

## Contributing to Autonomous Node

We need:
- **Variant designs:** New configurations for different use cases
- **Subsystem improvements:** Better batteries, more efficient solar, advanced sensors
- **Regional adaptations:** Non-UK regulatory pathways, climate-specific modifications
- **Real-world testing:** Deploy prototypes, document failures and successes
- **Cost optimization:** Cheaper materials, local sourcing, DIY-friendly designs

See [CONTRIBUTING.md](../../../CONTRIBUTING.md) for guidelines.

---

## Questions?

- **General:** hello@o1labs.community
- **Technical:** Open a GitHub Discussion
- **Hardware-specific:** hardware@o1labs.community

---

## Related Documentation

- **[CORE.md](../../../CORE.md)** - Three irreducible axioms
- **[NON_GOALS.md](../../../NON_GOALS.md)** - What we refuse to become
- **[STATUS.md](../../../STATUS.md)** - Current project phase

---

*"Flow over containment. Replication over scaling. Sovereignty as verb, not noun."*

**Maintained By:** O1 Labs CIC
**License:** See [LICENSE.md](../../../LICENSE.md)
