# GitHub Copilot Instructions for Deed Ledger

## Project Context

Deed Ledger is a portable, pseudonymous reputation system built on verifiable deeds rather than credentials. This is boring, effective trust infrastructure—no hype, no tokens, no cash deposits in alpha.

## Core Principles

1. **Focus on verifiable deeds**: Every reputation update must be tied to a concrete, verifiable action
2. **Pseudonymous by design**: DIDs, not real names. Behavior speaks louder than identity
3. **No cash in alpha**: Use effort-based skin-in-the-game (signal uploads, deed verification work)
4. **Regenerative rehabilitation**: Disputes and recoveries are visible; mistakes leave scars, not bans
5. **Demurrage**: Reputation decays without ongoing contribution

## Technical Guidelines

- **Ceramic/ComposeDB**: Primary data layer for immutable deed records
- **Nostr**: Broadcast layer for announcements and updates
- **TypeScript**: Strongly typed throughout
- **Minimal dependencies**: Only add what's strictly necessary
- **Composability**: Build small, reusable components
- **Progressive enhancement**: Mobile-first, works offline (PWA)

## Code Style

- Conventional commits
- Clear variable names, minimal comments
- Pure functions where possible
- Error handling at boundaries
- No magic numbers or strings

## What to Avoid

- Marketing language or hype
- Over-engineering or premature abstraction
- Financial mechanisms (cash deposits, tokens) in alpha
- Centralized trust assumptions
- Permanent bans or deletions

## Reputation Design

- **Deeds** are immutable records of actions
- **UserReputation** aggregates deeds with decay
- **Observers** verify and moderate
- **Nodes** have full participation rights after proving commitment
- **Influence** decays logarithmically without contribution

When suggesting code, prioritize boring reliability over clever features. Trust is built through consistent, verifiable action.
