# Protocols

Specifications for communication, governance, and interoperability within the Sovereign Stack.

## Overview

This directory contains formal protocol specifications that define how Sovereign Stack components interact, how communities make decisions, and how the system maintains interoperability across forks and variations.

---

## Directory Contents

### Communication Protocols

**Network Layer:**
- `mesh-routing.md` - Peer-to-peer mesh network routing protocol
- `discovery.md` - Node and service discovery mechanisms
- `encryption.md` - End-to-end encryption standards

**Application Layer:**
- `inter-hab.md` - Communication between SOV-HABs
- `grid-interface.md` - Energy Coupler grid communication protocol
- `data-sync.md` - CRDT-based data synchronization

### Governance Protocols

**Decision-Making:**
- `consensus.md` - Community consensus mechanisms (various models)
- `conflict-resolution.md` - Structured conflict resolution procedures
- `amendments.md` - How communities modify their governance rules

**Resource Management:**
- `allocation.md` - Fair resource allocation algorithms
- `contribution-tracking.md` - Tracking member contributions
- `exit-protocols.md` - Procedures for leaving a community

### Technical Standards

**Data Formats:**
- `identity.md` - Cryptographic identity standard
- `resource-units.md` - Standardized units for tracking resources
- `telemetry.md` - Sensor data formats and reporting

**Interoperability:**
- `cross-fork.md` - How forked Sovereign Stacks can still communicate
- `legacy-compat.md` - Backward compatibility guidelines
- `version-negotiation.md` - Protocol version negotiation

### Hardware Interfaces

**Energy Systems:**
- `energy-coupler-api.md` - Software/hardware interface for Energy Coupler
- `battery-protocol.md` - Battery management system communication
- `solar-monitoring.md` - Solar panel monitoring protocol

**Environmental Sensors:**
- `mldt-sensors.md` - Sensor specifications for MLDT monitoring
- `water-quality.md` - Water quality sensor protocols
- `hvac-control.md` - Climate control system interfaces

---

## Protocol Design Philosophy

### Core Principles

1. **Simplicity:** Protocols should be understandable by implementers
2. **Robustness:** Graceful degradation when components fail
3. **Extensibility:** Easy to add new features without breaking existing implementations
4. **Interoperability:** Forks should remain compatible where possible
5. **Privacy:** Minimize data exposure, maximize local processing

### Anti-Patterns to Avoid

- **Chatty Protocols:** Minimize round-trips and bandwidth usage
- **Centralization:** No single points of failure or control
- **Ambiguity:** Specifications must be implementable without guesswork
- **Vendor Lock-In:** Avoid proprietary dependencies
- **Version Hell:** Design for graceful version negotiation

---

## Protocol Lifecycle

### 1. Proposal (Draft)
- Document the problem being solved
- Propose a solution with clear specification
- Open for community feedback

### 2. Implementation (Experimental)
- Prototype implementations in multiple codebases
- Document edge cases and issues discovered
- Gather real-world usage data

### 3. Standardization (Stable)
- Address feedback from implementations
- Lock down specification (version 1.0)
- Provide reference implementations

### 4. Evolution (Versioned)
- Backward-compatible extensions (1.1, 1.2, etc.)
- Non-compatible changes require new major version (2.0)
- Deprecation process for obsolete features

---

## Specification Format

Each protocol specification should include:

### 1. Metadata
```
Title: [Protocol Name]
Status: Draft | Experimental | Stable | Deprecated
Version: [Semantic Version]
Authors: [Contributors]
Created: [Date]
Last Modified: [Date]
```

### 2. Abstract
One-paragraph summary of what this protocol does.

### 3. Motivation
Why is this protocol necessary? What problem does it solve?

### 4. Specification
Detailed technical specification with:
- Message formats (use ABNF, JSON Schema, or similar)
- State machines (for stateful protocols)
- Error handling
- Security considerations
- Example exchanges

### 5. Rationale
Design decisions and tradeoffs explained.

### 6. Security Considerations
Threat model and mitigations.

### 7. Implementation Notes
Guidance for developers.

### 8. Test Vectors
Example inputs/outputs for validation.

### 9. References
Related protocols, standards, research papers.

---

## Protocol Versioning

### Semantic Versioning (SemVer)

**Format:** `MAJOR.MINOR.PATCH`

- **MAJOR:** Breaking changes (incompatible with previous version)
- **MINOR:** New features, backward-compatible
- **PATCH:** Bug fixes, backward-compatible

### Version Negotiation

All protocols MUST support version negotiation:
1. Client sends supported versions (e.g., "1.2, 1.1, 1.0")
2. Server responds with chosen version (highest mutually supported)
3. Communication proceeds using negotiated version

### Deprecation Policy

- Announce deprecation at least 12 months before removal
- Provide migration guide to new version
- Maintain compatibility during deprecation period

---

## Interoperability with Forks

### Cross-Fork Protocol Goals

When the Sovereign Stack is forked, protocols should enable:

1. **Basic Communication:** Forked communities can still communicate if desired
2. **Data Portability:** Users can migrate between forks
3. **Selective Adoption:** Forks can adopt subsets of protocols

### Namespace Strategy

Use namespaced protocol identifiers:
```
org.sovereign-stack.mesh.routing.v1
org.forked-project.mesh.routing.v2-custom
```

This allows:
- Clear identification of protocol origin
- Custom extensions without conflicts
- Negotiation between compatible versions

---

## Security and Privacy

### Threat Model Considerations

All protocols must address:

1. **Confidentiality:** Who can read the data?
2. **Integrity:** Can data be tampered with?
3. **Authentication:** How do we verify identity?
4. **Authorization:** Who can perform which actions?
5. **Availability:** How do we prevent denial-of-service?

### Privacy-by-Design

- **Data Minimization:** Collect only what's necessary
- **Local Processing:** Keep data on-device where possible
- **Encryption:** End-to-end by default
- **Anonymity:** Support pseudonymous participation where appropriate

---

## Contributing Protocols

### Proposing a New Protocol

1. **Check for existing work** (avoid duplication)
2. **Write a draft specification** (follow format above)
3. **Open a pull request** with `[Protocol Proposal]` tag
4. **Discuss with community** (incorporate feedback)
5. **Prototype implementation** (prove feasibility)

### Reviewing Protocol Proposals

Good reviews evaluate:
- **Necessity:** Is this needed, or does existing work suffice?
- **Clarity:** Can this be implemented unambiguously?
- **Security:** Are threat models addressed?
- **Complexity:** Is this the simplest approach?
- **Compatibility:** How does this interact with existing protocols?

---

## Testing and Validation

### Conformance Testing

Reference implementations should include:
- Unit tests (protocol message parsing)
- Integration tests (multi-node scenarios)
- Fuzzing (malformed input handling)
- Interoperability tests (multiple implementations)

### Test Networks

Before deploying protocols in production:
1. **Testnet:** Isolated test environment
2. **Staging:** Pre-production validation
3. **Canary:** Limited production rollout
4. **General Availability:** Full deployment

---

## Current Status

**⚠️ Specification Phase:** Most protocols are in draft or early proposal stage.

**Active Work:**
- Mesh routing protocol (draft)
- Energy Coupler API (specification)
- Consensus mechanisms (research)

**How to Contribute:**
- Review draft protocols and provide feedback
- Prototype implementations
- Document edge cases and failure modes
- Contribute test vectors

---

## Questions?

- **Protocol design discussions:** Open an issue with `[Protocol]` tag
- **Implementation questions:** hello@o1labs.community
- **Security concerns:** security@o1labs.community
- **Interoperability issues:** protocols@o1labs.community

---

## Further Reading

- [OSI Model](https://en.wikipedia.org/wiki/OSI_model) - Network protocol layers
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) - Key words for RFCs (MUST, SHOULD, etc.)
- [IETF Standards Process](https://www.ietf.org/standards/process/) - How internet standards evolve
- [Threat Modeling](https://owasp.org/www-community/Threat_Modeling) - OWASP guide
