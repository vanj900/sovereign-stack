# Sovereign Stack Licensing FAQ

## Quick Reference

**TL;DR:**
- **Non-commercial use** (personal, education, community) → **AGPL-3.0** (free, open-source)
- **Commercial use** (selling products/services) → **Class B license** (requires approval)

---

## Understanding the Dual-License Structure

### Why two licenses?

The Sovereign Stack exists to serve **autonomous communities**, not extractive profit. The dual-license model:

1. **Keeps community use free** (AGPL-3.0 ensures open access)
2. **Prevents proprietary capture** (copyleft requirements)
3. **Controls commercialization** (Class B approval process)
4. **Funds ongoing development** (Class B revenue sharing)

This structure aligns with vanj900's dual-license model.

---

## Class A: AGPL-3.0 (Non-Commercial)

### What is AGPL-3.0?

The **GNU Affero General Public License v3.0** is a strong copyleft license that:
- Grants you freedom to use, study, modify, and distribute the software
- Requires you to share source code of modifications (even when running as a service)
- Prevents proprietary lock-in
- Ensures improvements benefit the entire community

**Full license text:** See the `LICENSE` file in this repository

### What counts as "non-commercial"?

You're covered by AGPL-3.0 (Class A) if you're:

✅ **Building for yourself/family**
- Constructing a SOV-HAB for personal habitation
- Deploying GhostStack on your own hardware
- Experimenting with Energy Coupler prototypes

✅ **Running a community cooperative**
- Non-profit intentional communities
- Ecovillages, cohousing projects
- Mutual aid networks

✅ **Educational/Research use**
- University courses on sustainable infrastructure
- Academic research on resilience systems
- Training programs for builders

✅ **Contributing to open-source**
- Pull requests improving the codebase
- Documentation, translations, bug fixes
- Creating educational content

✅ **Civic/Government pilots** (non-commercial)
- Local government disaster relief projects
- Public housing pilot programs (if non-profit)
- Community land trusts

### Key AGPL-3.0 requirements

If you modify and distribute the Sovereign Stack:

1. **Share your source code** (including for network services)
2. **Keep the AGPL-3.0 license** on derivatives
3. **Provide attribution** to the original project
4. **Document modifications** clearly

This prevents someone from taking Sovereign Stack, making proprietary changes, and locking communities into closed systems.

---

## Class B: Commercial Licensing

### What counts as "commercial"?

You need Class B approval if you're:

❌ **Manufacturing for sale**
- Building SOV-HABs to sell to customers
- Fabricating Energy Couplers commercially
- Mass-producing mesh network hardware

❌ **Offering paid services**
- Turnkey community deployment consulting
- Paid training/certification programs
- Managed hosting of GhostStack instances

❌ **Licensing/franchising**
- Franchising the Sovereign Stack methodology
- Sublicensing to third parties
- White-labeling the technology

❌ **Proprietary integration**
- Embedding GhostStack in closed-source products
- Using trademarked terms in commercial branding
- Creating SaaS platforms around Sovereign Stack

### How do I apply for Class B?

Contact vanj900 directly on GitHub: https://github.com/vanj900

Include:
   - Legal entity details (company name, registration, jurisdiction)
   - Intended use case (what you're building/selling)
   - Revenue model (how you'll make money)
   - Community benefit (how this advances Sovereign Stack goals)

### What are the terms?

Class B licenses typically include:

- **Revenue sharing:** 5-15% of gross revenue from Sovereign Stack-derived products/services
- **Sliding scale:** Higher for purely extractive use, lower for community-aligned ventures
- **Waived fees:** Possible for exceptional community benefit
- **Revocation clauses:** If terms are violated or use becomes harmful

All Class B revenue is reinvested in Sovereign Stack development per vanj900's licensing terms.

### Can my application be denied?

**Yes.** vanj900 evaluates applications against:

- **Alignment with principles** (flow over containment, community sovereignty)
- **Risk of harm** (surveillance, coercion, centralized control)
- **Community benefit** (does commercialization help or hinder adoption?)
- **Resource capacity** (can we support this use case?)

vanj900 prioritizes community benefit over profit maximization.

---

## Common Scenarios

### Scenario 1: "I'm building a SOV-HAB for my family"

**License:** Class A (AGPL-3.0)
**Action:** Build freely! No approval needed.
**Requirement:** If you modify designs and share them, release under AGPL-3.0.

### Scenario 2: "I want to start a company building SOV-HABs for clients"

**License:** Class B (commercial approval required)
**Action:** Apply for Class B license before starting operations.
**Why:** You're manufacturing for commercial sale.

### Scenario 3: "Our non-profit is deploying Sovereign Stack in a refugee camp"

**License:** Class A (AGPL-3.0)
**Action:** Proceed freely! This is civic/humanitarian use.
**Requirement:** Share any improvements back with the community.

### Scenario 4: "I'm writing a book about building SOV-HABs"

**License:** Class A (AGPL-3.0) for technical content
**Action:** Educational content is permitted. Attribute properly.
**Note:** If selling the book commercially, mention Sovereign Stack™ trademarks require permission for branding (descriptive use is fine).

### Scenario 5: "Can I fork Sovereign Stack and start a competing project?"

**License:** Class A (AGPL-3.0) allows forking!
**Action:** Fork freely, but:
- Change the name (can't use "Sovereign Stack" trademark)
- Maintain attribution to original project
- Keep AGPL-3.0 or more permissive license
- Document how your fork differs

**Why encouraged:** Forks enable community autonomy and experimentation.

### Scenario 6: "I built a SOV-HAB and want to sell it when I move"

**License:** Class A (AGPL-3.0)
**Action:** Selling a single built unit is personal property transfer, not commercial manufacturing.
**Note:** If you start building multiple units for resale, that's commercial activity (Class B).

### Scenario 7: "My government wants to deploy 1,000 SOV-HABs"

**License:** Class B (likely required)
**Action:** Contact us for Class B discussion.
**Why:** Scale and contract terms likely require commercial licensing, even if government is non-profit.

---

## Trademark Usage

The following terms are **trademarks of vanj900:**
- Sovereign Stack™
- SOV-HAB™
- GhostStack™

### Allowed without permission (Class A):
✅ "Built using Sovereign Stack technology"
✅ "Compatible with GhostStack protocol"
✅ "Based on SOV-HAB designs by vanj900"

### Requires written permission (Class B):
❌ "Sovereign Stack Certified Builder"
❌ Using logos in commercial products
❌ "Official SOV-HAB by [Your Company]"

**Descriptive use** (explaining what you're doing) is always fine.
**Commercial branding** (implying endorsement/official status) requires approval.

---

## GitHub's "Unknown License" Warning

GitHub shows "Unknown licenses found" because we use a **custom dual-license structure**. This is intentional.

**What GitHub sees:**
- `LICENSE` → AGPL-3.0 ✓ (recognized)
- `LICENSE.md` → Custom dual-license structure (not in SPDX database)

**This is normal** for projects with commercial licensing tiers. See also:
- [Qt's dual licensing](https://www.qt.io/licensing/)
- [MySQL's commercial licensing](https://www.mysql.com/about/legal/licensing/)
- [GitLab's dual licensing](https://about.gitlab.com/install/ce-or-ee/)

The AGPL-3.0 `LICENSE` file satisfies GitHub's license detection for the open-source tier.

---

## Contributing to Sovereign Stack

By contributing (pull requests, issues, designs, documentation), you agree:

1. **License grant:** Your contributions are licensed under AGPL-3.0 (Class A) + Class B terms
2. **Copyright:** You retain copyright but grant vanj900 perpetual rights to use/sublicense
3. **Patent grant:** Royalty-free patent license for any patents covering your contributions
4. **Warranty:** You have the right to contribute (not violating employer IP, etc.)

See `CONTRIBUTING.md` for detailed contribution guidelines.

---

## Still Confused?

### General questions
**GitHub:** https://github.com/vanj900
**Docs:** https://github.com/vanj900/sovereign-stack

### Class B licensing inquiries
Contact vanj900 directly on **GitHub:** https://github.com/vanj900

### Report license violations
**GitHub Issues:** https://github.com/vanj900/sovereign-stack/issues

### Quick decision flowchart

```
Are you making money from Sovereign Stack?
├─ No → Class A (AGPL-3.0) ✓ Proceed freely
└─ Yes
   ├─ Selling built units/products → Class B (apply for approval)
   ├─ Offering paid services → Class B (apply for approval)
   ├─ Licensing to third parties → Class B (apply for approval)
   └─ Accepting donations for non-profit work → Class A (AGPL-3.0) ✓
```

---

## Philosophy

The Sovereign Stack dual-license model embodies our core principle:

**"Flow over containment. Replication over scaling. Sovereignty as verb, not noun."**

- **Class A (AGPL-3.0)** enables flow: Communities can freely replicate and adapt
- **Class B (commercial control)** prevents containment: Extractive commercialization is managed
- **Both together** protect sovereignty: No single entity can capture the commons

This structure ensures Sovereign Stack remains a **community resource**, not a **venture-backed product**.

---

**Last Updated:** January 22, 2026
**License Version:** Sovereign Stack Dual License v1.0
**Maintained By:** vanj900
