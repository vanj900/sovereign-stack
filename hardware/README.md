# Hardware

Physical infrastructure designs for the Sovereign Stack.

## Directory Structure

### `/sov-hab`
**SOV-HAB** - Sovereign Habitat Module

Complete designs for autonomous living units (12m x 3m x 3m shipping container conversions).

**Contents:**
- CAD files (structural modifications)
- Electrical system diagrams
- Plumbing and water system layouts
- Insulation and climate control specs
- Assembly instructions
- Bill of materials (BOM)

**Status:** Design phase
**File Formats:** FreeCAD, DXF, PDF

### `/habcal`
**HabCal** - Habitability Calculator

Hardware specifications and sensor systems for monitoring dwelling habitability.

**Contents:**
- Environmental sensor specifications
- Data logging hardware
- Display/interface designs
- Calibration procedures
- Mounting and installation guides

**Status:** Specification phase
**File Formats:** KiCAD (PCB), STL (enclosures)

### `/mldt`
**MLDT** - Magnetic Load-Distribution Tile System

Passive magnetic levitation floor system for seismic protection and vibration isolation.

**Contents:**
- Complete technical specifications
- Cassette module designs
- Engineering calculations and load tables
- Installation procedures
- Safety and compliance documentation

**Status:** Specification phase
**File Formats:** Technical documentation (Markdown), CAD designs

### `/water`
**Water Systems** - Water collection, treatment, and distribution

Designs for autonomous water infrastructure.

**Contents:**
- Rainwater collection systems
- Greywater treatment designs
- Storage tank specifications
- Filtration system schematics
- Plumbing diagrams

**Status:** Design phase
**File Formats:** CAD, PDF

### `/energy`
**Energy Systems** - Power generation, storage, and distribution

Complete energy infrastructure designs.

**Contents:**
- Solar panel mounting systems
- Battery bank configurations
- Inverter/charge controller specs
- Wiring diagrams
- Energy Coupler hardware interface
- Wind turbine designs (optional)

**Status:** Specification phase
**File Formats:** CAD, electrical schematics

---

## Hardware Philosophy

### Design Principles

1. **Open Source:** All designs freely available (Class A AGPL-3.0)
2. **Repairable:** Standard components, minimal proprietary parts
3. **Modular:** Interchangeable subsystems
4. **Resilient:** Graceful degradation, redundancy where critical
5. **Local Manufacturing:** Designs optimized for regional fabrication

### Anti-Patterns to Avoid

- **Vendor Lock-In:** No proprietary components that force single-source purchasing
- **Planned Obsolescence:** Design for 20+ year lifespan
- **Over-Engineering:** Complexity is the enemy of repairability
- **Non-Standard Fasteners:** Use metric where possible, clearly document exceptions

---

## Manufacturing Considerations

### DIY vs. Professional Build

**DIY-Friendly Components:**
- Structural assembly (basic welding/carpentry skills)
- Electrical rough-in (with licensed electrician final inspection)
- Plumbing installation (with licensed plumber final inspection)
- Solar panel mounting

**Requires Professional:**
- Structural welding (load-bearing modifications)
- High-voltage electrical (grid interconnection)
- Pressure systems (water, HVAC)
- Regulatory inspections

### Supply Chain

**Prefer:**
- Off-the-shelf components (reduce lead times)
- Multiple supplier options (avoid single points of failure)
- Locally available materials (reduce shipping costs/emissions)
- Commodity standards (2x4 lumber, schedule 40 PVC, etc.)

**Avoid:**
- Custom fabrication where standard parts suffice
- Rare materials with limited suppliers
- Import-dependent components (tariff/supply chain risk)

---

## File Formats and Tools

### CAD (Mechanical Design)
- **FreeCAD** (primary, FOSS)
- **OpenSCAD** (parametric designs)
- **DXF/STEP** (interchange formats)

### CAD (Electrical)
- **KiCAD** (PCB design, FOSS)
- **Fritzing** (simple prototypes)

### Documentation
- **PDF** (build instructions, specifications)
- **Markdown** (text documentation)
- **SVG** (diagrams, schematics)

### 3D Printing
- **STL** (enclosures, brackets, fixtures)
- **OpenSCAD** (source files for printable parts)

---

## Safety and Compliance

### ⚠️ CRITICAL SAFETY NOTICE

**Modifying shipping containers and constructing habitable structures involves:**
- Structural engineering (load-bearing calculations)
- Electrical safety (fire/shock hazards)
- Plumbing codes (contamination prevention)
- Building codes (habitability standards)

**Do not attempt construction without:**
1. Reviewing local building codes and regulations
2. Consulting licensed professionals (engineer, electrician, plumber)
3. Obtaining required permits
4. Passing inspections

**vanj900 provides these designs "AS IS" without warranty. You assume all risk.**

See [/docs/legal/liability-disclaimer.md](../docs/legal/liability-disclaimer.md)

---

## Bill of Materials (BOM)

Each subsystem includes detailed BOMs with:
- Part numbers and specifications
- Supplier recommendations (multiple sources)
- Estimated costs (USD, updated periodically)
- Alternative/substitute parts
- Critical vs. optional components

**Example BOM Location:** `/hardware/sov-hab/bom/structural-components.csv`

---

## Testing and Validation

Before deploying hardware:

1. **Load Testing:** Verify structural integrity
2. **Electrical Testing:** Insulation resistance, ground continuity
3. **Pressure Testing:** Water systems, HVAC
4. **Environmental Testing:** Temperature extremes, humidity
5. **Longevity Testing:** Accelerated aging for critical components

Document all test procedures in `/docs/technical/testing/`

---

## Contributing Hardware Designs

When submitting designs:

1. **Include source files** (not just exported PDFs/STLs)
2. **Document design decisions** (why this approach?)
3. **Provide assembly instructions** (step-by-step with photos/diagrams)
4. **List tested suppliers** (where you sourced parts)
5. **Share build experience** (what worked, what didn't)

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution workflow.

---

## Licensing

All hardware designs are dual-licensed:

- **Class A (AGPL-3.0):** Free for personal, community, educational use
- **Class B (Commercial):** Manufacturing for sale requires approval

See [LICENSE.md](../LICENSE.md) for details.

**Trademark Notice:** "SOV-HAB" is a trademark of vanj900.

---

## Current Status

**⚠️ Design Phase:** Hardware designs are in active development. Prototypes are not yet validated.

**Do not begin construction** without:
- Reviewing latest designs (check commit history)
- Consulting local building professionals
- Understanding regulatory requirements in your jurisdiction

**Timeline (Tentative):**
- Q2 2026: Prototype SOV-HAB (single unit for testing)
- Q3 2026: First community deployment (3-5 units)
- Q4 2026: Public release of validated designs

---

## Questions?

- **Design feedback:** Open an issue with `[Hardware]` tag
- **Build questions:** https://github.com/vanj900
- **Safety concerns:** https://github.com/vanj900/sovereign-stack/issues
- **Commercial licensing:** https://github.com/vanj900
