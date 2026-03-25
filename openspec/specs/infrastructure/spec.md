# Infrastructure — Spec Domain

Infrastructure covers the platform layer beneath the product features — the skill ecosystem, protocol adapters, security systems, and multi-device/multi-user capabilities.

## Specs in this domain

| File | What it covers | Status |
|------|---------------|--------|
| `skills-marketplace.md` | 700+ skills ecosystem — skill manifest format, distribution, install/uninstall, permission model | Active |
| `mcp-adapter.md` | MCP (Model Context Protocol) adapter — exposes Polly agents as MCP tools | Planned |
| `distributed-nodes.md` | Multi-machine gateway federation — sync, routing, conflict resolution | Planned |
| `federated-collaboration.md` | Multi-user collaboration on shared knowledge and agent sessions | Planned |
| `lockdown-mode.md` | Air-gap mode — disables all network skills, enforces local-only operation | Planned |
| `creative-code-skill.md` | Creative Code skill — sandboxed code execution for creative/generative work | Planned |

## Key decisions locked

- All data local-only by default. Network features are opt-in with explicit manifest permissions.
- `network: []` constraint applies strictly to conversation history data — never leaves the machine.
- Skill manifests must declare `read:filesystem:{path}` permissions for any file system access.
- Security acceptance criteria (@security_audit gate) required for all skill and network features.

## Cross-domain dependencies

- Skills marketplace → Knowledge Skill as a first-party skill (must conform to skill manifest format)
- Lockdown Mode → Knowledge Skill network constraint enforcement
- MCP Adapter → Agent manifest schema (`agent-system/agent-templates.md`)
