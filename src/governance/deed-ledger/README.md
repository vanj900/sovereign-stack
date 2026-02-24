# Deed Ledger

Portable deed-based reputation ledger on Ceramic + Nostr. Verify actions, earn trust, exit credentials.

## Philosophy

**Behavior over labels.** Reputation emerges from verifiable deeds, not self-asserted credentials or centralized badges. Show what you've done, not who vouched for you.

**Scars over bans.** Mistakes leave marks but don't destroy identity. Disputes and recoveries are visible, enabling rehabilitation instead of permanent exile.

**Demurrage by design.** Influence decays without ongoing contribution. Dormant reputation fades, preventing legacy capture and ensuring active participation matters.

**Skin in the game, not cash.** Alpha MVP uses effort-based commitment (signal upload, deed verification, observer contributions) instead of financial deposits. Trust is earned through work, not wealth.

## Stack

- **Ceramic + ComposeDB**: Decentralized, verifiable data layer for reputation records
- **Nostr relays**: Broadcast deed announcements and reputation updates
- **Supabase**: Indexing and caching layer for fast queries (optional)
- **Next.js 14 PWA**: Mobile-first progressive web app with App Router
- **Tailwind CSS**: Utility-first styling

## Monorepo Structure

```
deed-ledger/
├── packages/
│   ├── schemas/          # ComposeDB GraphQL models
│   ├── frontend/         # Next.js PWA
│   └── backend/          # Node.js indexing/auth helpers
├── scripts/              # Ceramic model deployment
└── pnpm-workspace.yaml   # Workspace configuration
```

## Onboarding Flow

Progressive trust ladder with increasing commitment and influence:

1. **Invite** → Receive invitation from existing Node
2. **Signal** → Upload proof of work/expertise (hash commitment)
3. **Observer** → Review and verify others' deeds, learn system norms
4. **Node** → Complete 2-3 verified deeds + Observer contributions → Full participation

## Seed Target

Fintech ops, DevOps engineers, and growth marketers who get skin-in-the-game, want portable reputation, and hate centralized bullshit.

## Quick Start

### Prerequisites

- Node.js 18+
- pnpm 8+
- (Optional) Ceramic node for local development

### Installation

```bash
# Clone repository
git clone https://github.com/vanj900/deed-ledger.git
cd deed-ledger

# Install dependencies
pnpm install

# Copy environment template
cp packages/backend/.env.example packages/backend/.env
# Edit .env with your Supabase and Ceramic credentials

# Build all packages
pnpm build

# Start frontend development server
pnpm dev
```

### Deploying Ceramic Models

```bash
# Deploy reputation schema to Clay testnet
pnpm deploy:models
```

## Development

```bash
# Run all packages in watch mode
pnpm -r dev

# Type check all packages
pnpm type-check

# Build for production
pnpm build
```

## MVP Status — COMPLETE (Feb 2026)

**✅ Shipped**
- Monorepo structure with pnpm workspaces
- Core Ceramic schema for Deed + UserReputation + RecoveryDeed
- DID authentication (keypair or wagmi)
- Signal upload form with hash proof
- Event log viewer showing deed history
- Influence dashboard with decay visualization
- Observer review interface + scars
- Nostr event broadcasting for all actions
- Visible scars recovery / rehabilitation flow

**Note for developers:**
After any schema change (new models like RecoveryDeed), run `pnpm deploy:models` locally to update Ceramic Clay testnet.
Then `pnpm dev` and test end-to-end: create scar → submit recovery → observer approve.

Supabase indexing remains optional (fast queries only).

## Contributing

This is alpha software. Contributions welcome via pull requests. Focus on:
- Clean, minimal implementations
- Composability over features
- Quiet competence over hype
- Verifiable deeds and regenerative mechanisms

## License

MIT License - see [LICENSE](./LICENSE)

---

*Trust is earned through work, not wealth. Reputation fades without contribution. Exit is always possible.*
