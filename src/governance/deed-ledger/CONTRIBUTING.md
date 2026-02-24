# Contributing to Deed Ledger

## Development Setup

```bash
# Install dependencies
pnpm install

# Build all packages
pnpm build

# Start development server
pnpm dev

# Type check
pnpm type-check
```

## Project Structure

- `/packages/schemas` - Ceramic ComposeDB GraphQL models and TypeScript types
- `/packages/backend` - Node.js backend with Supabase and Nostr integrations
- `/packages/frontend` - Next.js 14 PWA with App Router
- `/scripts` - Ceramic model deployment scripts

## Development Guidelines

### Code Style

- Use TypeScript for all new code
- Follow existing patterns in the codebase
- Keep components small and focused
- Prefer functional components with hooks

### Commits

Use conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `chore:` - Build process or auxiliary tool changes

### Testing

Before submitting changes:
1. Run `pnpm build` to ensure everything builds
2. Run `pnpm type-check` to ensure types are valid
3. Test manually in the browser

## Philosophy

Remember the core principles:
- **Behavior over labels** - Show deeds, not credentials
- **Scars over bans** - Mistakes are visible but not fatal
- **Demurrage** - Reputation decays without contribution
- **Skin in the game** - Effort-based commitment, not cash

Keep the codebase boring, reliable, and effective.
