# Infrastructure — Current State

*Skill manifest format is defined. Marketplace and MCP adapter ship in Phase 2.*

## Skill Manifest Format (§8.8)

```json
{
  "id": "string",
  "type": "native | mcp",
  "permissions": ["read:filesystem:{path}", "network:{domain}"],
  "network": [],
  "data_destination": "local | cloud",
  "cloud_domains": []
}
```

`network: []` is strictly enforced for all local-only skills. Conversation history data must never have network permissions.

## Security Model

- **Verified tier:** cryptographic signature, trust anchor baked into gateway at install
- **Community tier:** explicit two-step user confirmation for cloud skills
- **Blocked tier:** gateway-level rejection, signed blocklist, 7-day staleness window, fail-closed offline
- Permission-adding updates trigger full re-consent flow

## Open Pre-Production Gate

Push registration security fix (C1: unauthenticated push registration, C2: cleartext `sendKey` in `devices.json`) — @backend owns, @security_audit sign-off required before Phase 2 ships to production. See `PUSH_SECURITY_FIX.md`.
