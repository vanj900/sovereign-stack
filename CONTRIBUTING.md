# Contributing to Sovereign Stack

Thank you for your interest in contributing to the Sovereign Stack! This project exists to serve autonomous communities, and we welcome contributions from builders, designers, developers, researchers, and community organizers.

---

## Table of Contents

- [How to Contribute](#how-to-contribute)
- [Contribution Types](#contribution-types)
- [Getting Started](#getting-started)
- [Contribution Workflow](#contribution-workflow)
- [Coding Standards](#coding-standards)
- [Documentation Standards](#documentation-standards)
- [Hardware Design Standards](#hardware-design-standards)
- [Review Process](#review-process)
- [License Agreement](#license-agreement)
- [Community Guidelines](#community-guidelines)
- [Getting Help](#getting-help)

---

## How to Contribute

Contributions can take many forms:

- **Code**: Software improvements to GhostStack, Energy Coupler, mesh networking
- **Hardware designs**: SOV-HAB modifications, MLDT sensors, energy systems
- **Documentation**: Guides, tutorials, API docs, translations
- **Protocols**: Specifications for governance, communication, interoperability
- **Research**: Academic papers, feasibility studies, case studies
- **Testing**: Bug reports, security audits, usability testing
- **Community support**: Answering questions, helping newcomers

**All contributions are valued**, whether you're fixing a typo or architecting a new subsystem.

---

## Contribution Types

### 1. Software (src/)

**Languages & Tools:**
- Primary: Python, Rust, JavaScript/TypeScript
- DevOps: Docker, Kubernetes, Ansible
- Databases: PostgreSQL, SQLite, IPFS

**What we need:**
- GhostStack civic OS implementation
- Energy Coupler control software
- Mesh network protocols
- Data synchronization (CRDTs)
- Security hardening

**Before contributing code:**
1. Open an issue describing your proposed change
2. Discuss approach with maintainers
3. Follow coding standards (see below)
4. Include tests and documentation

### 2. Hardware Designs (hardware/)

**File Formats:**
- CAD: FreeCAD (.FCStd preferred), STEP, IGES
- PCB: KiCad (.kicad_pro preferred), Gerber files
- Schematics: SVG, PDF (editable sources required)
- Documentation: Markdown, PDF

**What we need:**
- SOV-HAB container conversion designs
- MLDT sensor specifications
- Water treatment system designs
- Solar/battery configurations
- Manufacturing documentation

**Before contributing hardware:**
1. Ensure designs are buildable by individuals/small teams
2. Prioritize off-the-shelf components
3. Document safety considerations
4. Include bill of materials (BOM)
5. Provide assembly instructions

### 3. Documentation (docs/)

**Structure:**
- `/docs/technical` - Architecture, API specs, technical references
- `/docs/builders` - Construction guides, assembly instructions
- `/docs/governance` - Community decision-making frameworks
- `/docs/legal` - Compliance, regulations, legal considerations
- `/docs/research` - Academic papers, studies, analysis

**What we need:**
- Step-by-step build guides
- Architecture decision records (ADRs)
- API documentation
- Governance case studies
- Regulatory compliance guides
- Translations (all languages welcome)

**Documentation standards:**
- Use Markdown (.md) for text content
- Include diagrams (Mermaid, SVG, or PNG)
- Write for diverse audiences (technical and non-technical)
- Test all instructions by following them exactly

### 4. Protocols (protocols/)

**What we need:**
- Mesh routing protocols
- Consensus mechanisms for governance
- Energy Coupler APIs
- Identity and authentication standards
- Data formats and serialization

**Protocol specification format:**
- Follow RFC-style structure (see `protocols/README.md`)
- Include threat model and security analysis
- Provide test vectors
- Document version negotiation
- Consider fork compatibility

---

## Getting Started

### 1. Set Up Your Environment

**Fork and clone:**
```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/sovereign-stack.git
cd sovereign-stack
git remote add upstream https://github.com/vanj900/sovereign-stack.git
```

**Install dependencies:**
```bash
# For software development (example - adjust based on actual tech stack)
pip install -r requirements.txt  # Python
cargo build                       # Rust
npm install                       # JavaScript

# For hardware design
# Install FreeCAD, KiCad, or other CAD tools
```

**Run tests:**
```bash
# Run the test suite to ensure everything works
make test
# OR
pytest
# OR
cargo test
```

### 2. Find Something to Work On

**Good first issues:**
- Look for issues labeled `good-first-issue`
- Check `help-wanted` label for community priorities
- Review `documentation` label for writing opportunities

**Ask questions:**
- Open a discussion in GitHub Discussions
- Comment on issues to ask for clarification
- Join community channels (see Getting Help section)

### 3. Create a Branch

```bash
git checkout -b feature/your-descriptive-name
# OR
git checkout -b fix/bug-description
# OR
git checkout -b docs/documentation-improvement
```

**Branch naming conventions:**
- `feature/` - New functionality
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `refactor/` - Code restructuring
- `test/` - Test improvements
- `hardware/` - Physical design changes
- `protocol/` - Protocol specifications

---

## Contribution Workflow

### 1. Make Your Changes

- Write clear, focused commits
- Follow coding/design standards (see below)
- Add tests for new functionality
- Update documentation as needed

### 2. Commit Your Work

**Commit message format:**
```
[type]: Brief description (50 chars or less)

Detailed explanation of what changed and why (wrap at 72 chars).

- List specific changes as bullet points
- Reference related issues (#123)
- Explain tradeoffs if applicable

Fixes #123
```

**Commit types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `refactor:` Code restructuring
- `test:` Test improvements
- `chore:` Maintenance tasks
- `hardware:` Physical design changes
- `protocol:` Protocol specifications

**Example:**
```
feat: Add MLDT temperature sensor integration

Implements temperature monitoring for the Multi-Level Diagnostic Tool:
- Adds DS18B20 sensor driver
- Updates MLDT protocol spec with temperature data format
- Includes calibration routine
- Documents wiring and installation

Fixes #42
```

### 3. Push to Your Fork

```bash
git push origin feature/your-descriptive-name
```

### 4. Open a Pull Request

1. Go to your fork on GitHub
2. Click "Compare & pull request"
3. Fill out the PR template (see below)
4. Link related issues
5. Request review from maintainers

**PR Title Format:**
```
[Type] Brief description
```

**PR Description Template:**
```markdown
## Summary
Brief description of what this PR does.

## Motivation
Why is this change needed? What problem does it solve?

## Changes
- List specific changes made
- Include file-level changes if helpful
- Note any breaking changes

## Testing
How was this tested? What scenarios were covered?

## Documentation
- [ ] Code comments added/updated
- [ ] README updated (if needed)
- [ ] API docs updated (if needed)
- [ ] User-facing docs updated (if needed)

## Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Commit messages are clear
- [ ] License terms accepted (see CONTRIBUTING.md)

## Related Issues
Fixes #123
Relates to #456
```

---

## Coding Standards

### General Principles

1. **Simplicity**: Prefer simple, understandable code over clever optimizations
2. **Modularity**: Write small, focused functions/modules
3. **Testability**: Design for easy testing
4. **Documentation**: Comment the "why," not the "what"
5. **Security**: Assume all input is malicious

### Python

- Follow PEP 8 style guide
- Use type hints (Python 3.9+)
- Maximum line length: 88 characters (Black formatter)
- Use descriptive variable names
- Write docstrings for public APIs

**Example:**
```python
def calculate_energy_surplus(
    production_kwh: float,
    consumption_kwh: float,
    battery_capacity_kwh: float
) -> float:
    """
    Calculate available energy surplus after consumption and storage.

    Args:
        production_kwh: Total energy produced
        consumption_kwh: Energy consumed by SOV-HAB
        battery_capacity_kwh: Maximum battery storage

    Returns:
        Available surplus energy in kWh
    """
    net_energy = production_kwh - consumption_kwh
    return max(0, net_energy - battery_capacity_kwh)
```

### Rust

- Follow Rust standard style (rustfmt)
- Use `cargo clippy` for linting
- Prefer explicit over implicit
- Handle errors explicitly (avoid unwrap in production)
- Write comprehensive tests

### JavaScript/TypeScript

- Use TypeScript for type safety
- Follow Airbnb JavaScript Style Guide
- Use ESLint and Prettier
- Prefer functional patterns
- Write JSDoc comments

---

## Documentation Standards

### Markdown Guidelines

- Use proper heading hierarchy (# → ## → ###)
- Include a table of contents for long documents
- Use code blocks with language specifiers
- Include diagrams where helpful
- Provide examples and use cases

### Technical Writing

**Be clear and concise:**
- Use active voice
- Avoid jargon (or define it when necessary)
- Write for diverse audiences
- Test instructions by following them exactly

**Structure:**
1. **Overview** - What is this about?
2. **Motivation** - Why does this matter?
3. **Details** - How does it work?
4. **Examples** - Show concrete usage
5. **References** - Link to related docs

### API Documentation

- Document all public APIs
- Include parameter types and return values
- Provide usage examples
- Document error conditions
- Note any security considerations

---

## Hardware Design Standards

### Design Philosophy

1. **Buildable**: Can be constructed by individuals/small teams
2. **Repairable**: Use off-the-shelf components, avoid proprietary parts
3. **Modular**: Components can be replaced independently
4. **Safe**: Meet relevant safety standards
5. **Documented**: Include clear assembly instructions

### CAD File Standards

- **Preferred format**: FreeCAD (.FCStd) for open-source compatibility
- **Alternative formats**: STEP, IGES for interoperability
- **Organization**: Logical part naming, use assemblies
- **Version control**: Save as ASCII where possible
- **Units**: Metric (mm) unless region-specific requirements dictate otherwise

### Bill of Materials (BOM)

Include for all hardware designs:
```markdown
| Part | Quantity | Specification | Source | Approx. Cost |
|------|----------|---------------|--------|--------------|
| Solar Panel | 4 | 300W monocrystalline | Generic | $200 |
| Charge Controller | 1 | MPPT 60A | Victron Energy | $300 |
| ... | ... | ... | ... | ... |
```

### Safety Documentation

**Required for all designs:**
- Electrical safety considerations
- Structural load calculations
- Material toxicity warnings
- Installation hazards
- Emergency procedures

**Example:**
```markdown
## Safety Warnings

⚠️ **ELECTRICAL HAZARD**: This system operates at 48V DC. Follow all electrical codes.

⚠️ **STRUCTURAL**: Maximum roof load is 50 kg/m². Verify before installation.

⚠️ **WATER**: Ensure proper drainage to prevent water intrusion.
```

---

## Review Process

### What Reviewers Look For

1. **Correctness**: Does it work as intended?
2. **Clarity**: Is the code/design understandable?
3. **Completeness**: Are tests, docs, and examples included?
4. **Security**: Are there vulnerabilities?
5. **Compatibility**: Does it work with existing systems?
6. **Style**: Does it follow conventions?

### Timeline Expectations

- **Initial review**: Within 1 week
- **Follow-up reviews**: Within 3 days
- **Merge decision**: After approval from 2+ maintainers

**Note**: Complex changes may require longer review. Be patient and responsive to feedback.

### Addressing Feedback

- Respond to all comments (even if just "acknowledged")
- Ask questions if feedback is unclear
- Make requested changes in new commits (don't force-push)
- Request re-review when ready

---

## License Agreement

By contributing to Sovereign Stack, you agree:

1. **License Grant**: Your contributions are licensed under AGPL-3.0 (Class A) and subject to Class B commercial terms
2. **Copyright**: You retain copyright but grant O1 Labs CIC perpetual rights to use, modify, and sublicense
3. **Patent Grant**: You grant a royalty-free patent license for any patents covering your contributions
4. **Originality**: You have the right to contribute (not violating employer IP, third-party rights, etc.)
5. **No Warranty**: Contributions are provided "as is" without warranty

**If you cannot agree to these terms, do not contribute.** Contact O1 Labs CIC for alternative arrangements.

See [LICENSE.md](LICENSE.md) for complete licensing terms.

---

## Community Guidelines

### Code of Conduct

The Sovereign Stack community is committed to:

- **Respect**: Value diverse perspectives and experiences
- **Collaboration**: Work together toward shared goals
- **Constructive feedback**: Critique ideas, not people
- **Inclusion**: Welcome contributors of all backgrounds
- **Safety**: Maintain a harassment-free environment

**Unacceptable behavior:**
- Harassment, discrimination, or personal attacks
- Trolling, inflammatory comments, or sustained disruption
- Publishing private information without consent
- Any conduct that violates the project's mission

**Enforcement**: Maintainers may remove, edit, or reject contributions that violate these guidelines.

### Philosophy Alignment

Contributions should align with Sovereign Stack principles:

- **Flow over containment**: Enable energy circulation, not hoarding
- **Replication over scaling**: Support community autonomy, not centralized growth
- **Sovereignty as verb**: Design for active self-governance, not passive consumption
- **Community benefit**: Prioritize collective good over individual profit

If your contribution contradicts these principles, discuss with maintainers before proceeding.

---

## Getting Help

### Questions and Discussions

- **GitHub Discussions**: Best for general questions, ideas, and community chat
- **GitHub Issues**: For bug reports, feature requests, and specific problems
- **Email**: hello@o1labs.community for direct inquiries

### Before Asking for Help

1. Search existing issues and discussions
2. Read relevant documentation
3. Try to reproduce the problem
4. Gather relevant details (error messages, system info, steps to reproduce)

### When Asking for Help

**Provide context:**
```markdown
## Description
Brief description of the problem or question.

## Steps to Reproduce (for bugs)
1. Step one
2. Step two
3. Expected vs. actual result

## Environment
- OS: Ubuntu 22.04
- Software version: GhostStack v0.1.0
- Hardware: Raspberry Pi 4

## What I've Tried
- Searched documentation (found X, but Y is unclear)
- Tried A, B, C approaches
- Relevant error messages (paste below)

## Error Messages
```
[Paste error messages here]
```
```

---

## Recognition

Contributors are recognized in several ways:

- **Git history**: Permanent record of contributions
- **CONTRIBUTORS.md**: List of all contributors (coming soon)
- **Release notes**: Major contributions highlighted in releases
- **Community gratitude**: Appreciation from users and maintainers

**Note**: O1 Labs CIC does not provide financial compensation for contributions. All work is voluntary under open-source principles.

---

## Special Contribution Areas

### Security Vulnerabilities

**Do not open public issues for security vulnerabilities.**

**Instead:**
1. Email: security@o1labs.community
2. Include: Description, impact, reproduction steps
3. Allow: 90 days for fix before public disclosure

We will acknowledge receipt within 48 hours and provide a timeline for resolution.

### Governance and Community Structure

Contributions to governance frameworks:
- Propose new consensus mechanisms
- Document conflict resolution processes
- Share case studies from real communities
- Develop resource allocation algorithms

See `docs/governance/` for current work.

### Research and Academic Contributions

We welcome academic research:
- Feasibility studies
- Resilience modeling
- Social science research on community dynamics
- Economic analysis

See `docs/research/` for current work.

---

## Questions About Contributing?

- **General**: hello@o1labs.community
- **Technical**: Open a GitHub Discussion
- **Licensing**: licensing@o1labs.community
- **Security**: security@o1labs.community

---

## Thank You

Every contribution, no matter how small, helps build autonomous communities and systems that serve human flourishing over extractive profit.

**Your work matters.**

---

*"Flow over containment. Replication over scaling. Sovereignty as verb, not noun."*

**Version**: 1.0
**Last Updated**: January 22, 2026
**Maintained By**: O1 Labs CIC
