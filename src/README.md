# Source Code

Software components of the Sovereign Stack.

## Directory Structure

### `/ghoststack`
**GhostStack** - The Civic Operating System

Distributed operating system for autonomous community infrastructure.

**Key Components:**
- Core OS kernel and services
- Identity management (cryptographic)
- Resource allocation systems
- Mesh network integration
- Data sovereignty layer

**Status:** Design phase
**Language:** TBD (likely Rust or Go for core, with language-agnostic protocols)

### `/energy-coupler`
**Energy Coupler** - Bidirectional Energy Flow Protocol

Software for managing energy sharing between SOV-HABs and the broader grid.

**Key Components:**
- Energy flow algorithms (import/export decisions)
- Grid interface protocols
- Battery management system integration
- Demand forecasting
- Price signal processing

**Status:** Specification phase
**Language:** TBD (embedded systems consideration required)

### `/mesh`
**Mesh Network Stack** - Decentralized Communication Layer

Peer-to-peer communication infrastructure independent of ISP control.

**Key Components:**
- Routing protocols (mesh topology)
- Encryption layer (end-to-end)
- Discovery mechanisms
- Fallback systems (radio, etc.)
- Protocol bridges (to clearnet)

**Status:** Research phase
**Language:** TBD (cross-platform requirement)

---

## Development Guidelines

### Getting Started

1. Read the [Technical Architecture](../docs/technical/architecture-overview.md)
2. Review component-specific READMEs in subdirectories
3. Check open issues and project boards
4. Join development discussions (see CONTRIBUTING.md)

### Code Standards

- **Licensing:** All code is dual-licensed (AGPL-3.0 + Class B)
- **Security:** No hardcoded secrets, credentials, or API keys
- **Testing:** Minimum 80% code coverage for core components
- **Documentation:** Inline comments for complex logic, README for setup
- **Style:** Follow language-specific conventions (enforce with linters)

### Architecture Principles

1. **Modularity:** Components should be loosely coupled
2. **Interoperability:** Use open protocols and standards
3. **Offline-first:** Assume intermittent connectivity
4. **Privacy:** Minimize data collection, maximize local processing
5. **Resilience:** Graceful degradation when systems fail

---

## Technology Stack (Proposed)

This is preliminary and subject to community discussion.

**Systems Programming:**
- Rust (safety, performance, embedded targets)
- Go (networking, distributed systems)

**Application Layer:**
- Python (rapid prototyping, data processing)
- TypeScript (user interfaces)

**Data:**
- SQLite (local-first)
- CRDTs (distributed sync)

**Communication:**
- gRPC (inter-service)
- WebRTC (peer-to-peer)
- MQTT (IoT devices)

**Infrastructure:**
- Docker (containerization)
- Kubernetes (orchestration, optional)
- NixOS (reproducible builds)

---

## Repository Structure

```
src/
├── ghoststack/
│   ├── core/           # OS kernel and base services
│   ├── identity/       # Cryptographic identity management
│   ├── resources/      # Resource allocation algorithms
│   └── protocols/      # Communication protocols
├── energy-coupler/
│   ├── algorithms/     # Energy flow decision logic
│   ├── interfaces/     # Hardware abstraction layers
│   └── forecasting/    # Demand prediction models
└── mesh/
    ├── routing/        # Mesh routing protocols
    ├── crypto/         # Encryption layer
    └── discovery/      # Peer discovery mechanisms
```

---

## Contributing Code

See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- Development workflow (branching, PRs, reviews)
- Testing requirements
- Security review process
- Contributor License Agreement

By contributing, you agree to dual-license your code under AGPL-3.0 (Class A) and vanj900's commercial terms (Class B).

---

## Current Status

**⚠️ Early Development:** This repository is in active design and prototyping phase. APIs and architecture are subject to significant changes.

**How to help:**
- Review architecture proposals in `/docs/technical`
- Prototype key components
- Contribute to specification documents
- Test assumptions and edge cases

**Not ready yet:**
- Production deployments
- Stable API guarantees
- Long-term support commitments

---

## Security

Report security vulnerabilities to: https://github.com/vanj900/sovereign-stack/issues

**Do not** open public issues for security vulnerabilities.

---

## Questions?

- **Technical discussions:** Open an issue with `[Discussion]` tag
- **Architecture decisions:** See `/docs/technical/adr/` (Architecture Decision Records)
- **General questions:** https://github.com/vanj900
