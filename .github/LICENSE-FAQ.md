# Sovereign Stack Licensing FAQ

## Quick Reference

**TL;DR:**
- **Small Operators** (individuals, families, co-ops, non-profits, or for-profit entities with <20 FTE employees AND <$1M annual revenue) → **Full AGPL-3.0 + commercial rights** (free, open-source)
- **Large Entities** (anyone not a Small Operator) → **AGPL-3.0 for internal non-commercial use only** — commercial use requires a paid license

---

## Understanding the Sovereign Stack License v1.0

### Why this structure?

The Sovereign Stack exists to serve **autonomous communities**, not extractive profit. The Sovereign Stack License v1.0:

1. **Keeps community use free** (AGPL-3.0 ensures open access)
2. **Prevents proprietary capture** (copyleft requirements)
3. **Enables small-operator commerce** (explicitly grants commercial rights to small operators)
4. **Controls large-entity commercialization** (requires paid license for large commercial actors)

This structure is defined in [LICENSE.md](../LICENSE.md).

---

## Small Operators: Full Commercial Rights

### Who qualifies as a Small Operator?

You are a **Small Operator** if you are:
- A natural person (individual), family, sole proprietor, partnership, co-op, non-profit, educational or research entity.
- Any for-profit entity (LLC, corp, etc.) with **fewer than 20 full-time equivalent employees** AND **gross annual revenue under $1,000,000 USD** in its most recent completed fiscal year.

### What can Small Operators do?

✅ **Build for yourself/family**
- Constructing a SOV-HAB for personal habitation
- Deploying GhostStack on your own hardware
- Experimenting with Energy Coupler prototypes

✅ **Run a community cooperative**
- Non-profit intentional communities
- Ecovillages, cohousing projects
- Mutual aid networks

✅ **Educational/Research use**
- University courses on sustainable infrastructure
- Academic research on resilience systems
- Training programs for builders

✅ **Commercial activity (explicitly granted)**
- Manufacture, sell, or distribute hardware/products based on the blueprints
- Offer paid services, consulting, installs, training, support, or hosted cells
- Deploy, operate, and charge for local meshes, stacks, or derivatives
- Fork and redistribute (must rename the project, keep full attribution + terms unchanged)

✅ **Contributing to open-source**
- Pull requests improving the codebase
- Documentation, translations, bug fixes
- Creating educational content

### Key AGPL-3.0 requirements for all users

If you modify and distribute the Sovereign Stack:

1. **Share your source code** (including for network services)
2. **Keep the AGPL-3.0 license** on derivatives
3. **Provide attribution** to the original project
4. **Document modifications** clearly

This prevents someone from taking Sovereign Stack, making proprietary changes, and locking communities into closed systems.

---

## Large Entities: Internal Non-Commercial Use Only

### Who is a Large Entity?

Anyone who is **not** a Small Operator — typically for-profit entities with 20+ FTE employees or over $1,000,000 USD in annual gross revenue.

### What can Large Entities do without a paid license?

Large Entities may use the Sovereign Stack under AGPL-3.0 **strictly for**:
- Private internal testing and R&D
- No customer-facing deployment
- No manufacturing for resale
- No paid services based on it

### What requires a paid commercial license?

❌ **Manufacturing for sale**
- Building SOV-HABs to sell to customers
- Fabricating Energy Couplers commercially
- Mass-producing mesh network hardware

❌ **Offering paid services**
- Turnkey community deployment consulting
- Paid training/certification programs
- Managed hosting of GhostStack instances

❌ **Scaling or profiteering**
- Embedding GhostStack in closed-source products
- Using trademarked terms in commercial branding
- Creating SaaS platforms around Sovereign Stack

### How do Large Entities apply for a commercial license?

Contact: **sovereign@ghoststack.dev**

Include:
   - Legal entity details (company name, registration, jurisdiction)
   - Intended use case (what you're building/selling)
   - Revenue model (how you'll make money)
   - Community benefit (how this advances Sovereign Stack goals)

### What are the terms?

Commercial licenses for Large Entities typically include:

- **Revenue sharing/royalties** proportional to use
- **Back-contribution requirements** to the open-source project
- **Revocation clauses** if terms are violated or use becomes harmful

We may grant on reasonable terms or deny if it risks enclosure. No exceptions for subsidiaries or workarounds.

---

## Common Scenarios

### Scenario 1: "I'm building a SOV-HAB for my family"

**Status:** Small Operator ✓
**Action:** Build freely! No approval needed.
**Requirement:** If you modify designs and share them, release under AGPL-3.0.

### Scenario 2: "I want to start a small company building SOV-HABs for clients"

**Status:** Small Operator (if <20 FTE and <$1M revenue) ✓
**Action:** Proceed! Commercial rights are explicitly granted to Small Operators.
**Requirement:** Comply with AGPL-3.0 (share source for any distributed mods), retain all notices.

### Scenario 3: "Our non-profit is deploying Sovereign Stack in a refugee camp"

**Status:** Small Operator ✓
**Action:** Proceed freely! This is civic/humanitarian use.
**Requirement:** Share any improvements back with the community.

### Scenario 4: "I'm writing a book about building SOV-HABs"

**Status:** Small Operator ✓
**Action:** Educational content is permitted. Attribute properly.
**Note:** Sovereign Stack™ trademarks require permission for branding; descriptive use is fine.

### Scenario 5: "Can I fork Sovereign Stack and start a competing project?"

**Status:** Small Operator ✓
**Action:** Fork freely, but:
- Change the name (can't use "Sovereign Stack" or "GhostStack" trademarks)
- Maintain attribution to original project
- Keep these terms unchanged
- Use distinct branding

**Why encouraged:** Forks enable community autonomy and experimentation.

### Scenario 6: "I built a SOV-HAB and want to sell it when I move"

**Status:** Small Operator ✓
**Action:** Selling a single built unit is personal property transfer.
**Note:** If you start building multiple units for resale as a business, check whether you remain a Small Operator.

### Scenario 7: "A large corporation wants to deploy 1,000 SOV-HABs"

**Status:** Large Entity — commercial license required
**Action:** Contact sovereign@ghoststack.dev before starting commercial operations.
**Why:** Scale and commercial intent require a paid license.

---

## Trademark Usage

The following terms are **reserved marks of vanj900 and Sovereign Stack Contributors:**
- Sovereign Stack™
- GhostStack™
- SOV-HAB™
- The glowing blue ghost logo
- Crossed swords mark

### Small Operators — allowed in good faith with clear attribution:
✅ "Built using Sovereign Stack technology"
✅ "Compatible with GhostStack protocol"
✅ "Based on SOV-HAB designs by vanj900"

### Large Entities — not permitted:
❌ Any use of reserved marks without a paid commercial license

**Descriptive use** (explaining what you're doing) is always fine.
**Commercial branding** (implying endorsement/official status) requires approval for Large Entities.

---

## GitHub's "Unknown License" Warning

GitHub shows "Unknown licenses found" because we use a **custom license structure** layered on AGPL-3.0. This is intentional.

**What GitHub sees:**
- `LICENSE` → AGPL-3.0 ✓ (recognized)
- `LICENSE.md` → Sovereign Stack License v1.0 (custom additional terms, not in SPDX database)

**This is normal** for projects with supplemental commercial licensing terms.

The AGPL-3.0 `LICENSE` file satisfies GitHub's license detection for the open-source tier.

---

## Contributing to Sovereign Stack

By contributing (pull requests, issues, designs, documentation), you agree:

1. **License grant:** Your contributions are licensed under AGPL-3.0 and subject to the Additional Sovereign Terms in LICENSE.md
2. **Copyright:** You retain copyright but grant vanj900 perpetual rights to use/sublicense
3. **Patent grant:** Royalty-free patent license for any patents covering your contributions
4. **Warranty:** You have the right to contribute (not violating employer IP, etc.)

See `CONTRIBUTING.md` for detailed contribution guidelines.

---

## Still Confused?

### General questions
**GitHub:** https://github.com/vanj900
**Docs:** https://github.com/vanj900/sovereign-stack

### Large Entity commercial licensing inquiries
**Email:** sovereign@ghoststack.dev

### Report license violations
**GitHub Issues:** https://github.com/vanj900/sovereign-stack/issues

### Quick decision flowchart

```
Are you a Small Operator?
(individual/family/co-op/non-profit, OR for-profit with <20 FTE AND <$1M revenue)
├─ Yes → Full AGPL-3.0 + commercial rights ✓ Proceed freely
└─ No (Large Entity)
   ├─ Internal non-commercial use (testing/R&D) → AGPL-3.0 ✓
   └─ Any commercial use → Paid license required
      └─ Contact: sovereign@ghoststack.dev
```

---

## Philosophy

The Sovereign Stack License v1.0 embodies our core principle:

**"Flow over containment. Replication over scaling. Sovereignty as verb, not noun."**

- **Small Operators** get full flow: freely replicate, adapt, and monetize
- **Large Entities** are prevented from containment: extractive commercialization requires a paid license
- **Together** they protect sovereignty: no single large entity can capture the commons

This structure ensures Sovereign Stack remains a **community resource**, not a **venture-backed product**.

---

**Last Updated:** February 2026
**License Version:** Sovereign Stack License v1.0
**Maintained By:** vanj900 and Sovereign Stack Contributors
