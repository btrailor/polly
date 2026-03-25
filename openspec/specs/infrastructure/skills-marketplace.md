# SKILLS_MARKETPLACE.md

**Status:** Draft  
**Phase:** 2  
**Owner:** @code_architect  
**Security:** @security_audit owns threat model section (§6)  
**Created:** 2026-03-25  
**Depends on:** §8.8 skill manifest system (`POLLY_IOS_SPEC.md` line 3931)  
**Blocks:** `MCP_ADAPTER.md`

---

## 1. Purpose

The Skills Marketplace is the curation, distribution, and trust layer for OpenClaw skills. It answers three questions at install time:

1. **Has this been reviewed?** (trust tier)
2. **Where does my data go?** (data destination)
3. **What can it access on my machine?** (permissions)

The marketplace is not a generic MCP catalog. It is curated and opinionated — quality and trust over comprehensiveness.

---

## 2. Trust Tiers

Three tiers. No more, no less.

| Tier | Badge | Meaning |
|------|-------|---------|
| **Verified** | ✅ | Polly team has reviewed the skill, confirmed sandbox behavior, and audited permissions. Safe to install with confidence. |
| **Community** | 🧩 | Submitted by the community. Not reviewed by Polly team. Install at your own risk — explicit warning at install time. |
| **Blocked** | 🚫 | Known malicious, privacy-violating, or policy-breaking. Gateway rejects install. Not just hidden from browse — actively prevented. |

### 2.1 Tier Enforcement

- **Verified** tier: cryptographic signature verification at install. Skills signed with Polly's private key. Trust anchor (Polly public key) baked into gateway binary at install time. An unsigned skill cannot claim Verified status.
- **Community** tier: no signature required. Explicit "install at own risk" consent modal at install time. Not skippable.
- **Blocked** tier: enforced at the skill runner (gateway level), not filtered in the browse UI. A blocked skill ID submitted directly via API must be rejected. UI filtering is insufficient.

### 2.2 Blocklist

- Maintained as a signed JSON document, fetched periodically from Polly's CDN.
- Cached locally with a signed timestamp.
- **Staleness window: 7 days.** If the cached blocklist is older than 7 days AND the device is offline, the skill runner **fails closed** — blocked installs remain blocked.
- Blocklist signature verified against the same Polly public key used for Verified skills.

---

## 3. Data Destination

Trust tier and data destination are **independent axes**. A Verified skill can make outbound calls (weather, maps — that's their function). A Community skill might be fully local. The user deserves to see both.

### 3.1 Manifest Declaration

Every skill manifest declares:

```json
{
  "data_destination": "local" | "cloud",
  "cloud_domains": ["api.openweathermap.org"]  // required if "cloud"
}
```

`cloud_domains` must list all domains the skill makes outbound calls to. Empty or missing when `data_destination: "cloud"` = install blocked.

### 3.2 Install UI Display

| Combination | Treatment |
|-------------|-----------|
| Verified + local | ✅ "Fully local — no data leaves your machine" |
| Verified + cloud | ✅ Verified badge + "⚠️ Sends data to: [domain list]" |
| Community + local | 🧩 "Install at own risk" warning |
| Community + cloud | 🧩 **Strongest warning** — unreviewed AND phones home. Explicit two-step confirmation. |
| Blocked + any | 🚫 Install rejected. No bypass. |

---

## 4. Skill Manifest (Extended for Marketplace)

The §8.8 skill manifest is the source of truth. The marketplace layer adds these required fields:

```json
{
  "id": "com.polly.weather",
  "name": "Weather",
  "version": "1.2.0",
  "tier": "verified",
  "data_destination": "cloud",
  "cloud_domains": ["api.openweathermap.org"],
  "permissions": ["network:api.openweathermap.org"],
  "network": ["api.openweathermap.org"],
  "signature": "<base64-polly-signature>",
  "description": "Current conditions and forecasts.",
  "author": "Polly Team",
  "homepage": "https://polly.io/skills/weather",
  "changelog_url": "https://polly.io/skills/weather/changelog"
}
```

### 4.1 Permission-Adding Updates

If a skill update adds new permissions beyond the previously installed version, the update is treated as a new install:
- Diff of permission sets computed at update time
- If `new_permissions - old_permissions` is non-empty → full install consent flow required
- User sees exactly which permissions are being added
- Manifest re-verified (Verified tier) or warning re-shown (Community tier)

---

## 5. Install Flow

### 5.1 Verified Skill

1. User taps skill in browse or receives deep link
2. Skill detail sheet: name, description, tier badge, data destination, permission list
3. "Install" button
4. Gateway verifies signature against Polly public key
5. Permission grant modal (standard §8.8 flow)
6. Skill installed, runner registers it

### 5.2 Community Skill

1–2. Same as Verified.
3. **Warning modal** (not skippable, not dismissible on tap-outside):
   > "This skill hasn't been reviewed by the Polly team. It was submitted by the community and may behave unexpectedly. Only install skills from sources you trust."
   > [Install Anyway] [Cancel]
4. If `data_destination: "cloud"` — **second confirmation**:
   > "This skill also sends data to external servers: [domain list]. Your conversations and data may be visible to those servers."
   > [I Understand, Install] [Cancel]
5. Gateway proceeds (no signature check for Community)
6. Permission grant modal
7. Skill installed

### 5.3 Blocked Skill

1. Install attempted (via UI or API)
2. Gateway checks skill ID against blocklist
3. Install rejected with reason: `SKILL_BLOCKED`
4. UI shows: "This skill has been blocked by Polly because it was found to be [malicious / privacy-violating / policy-violating]. It cannot be installed."
5. No bypass path.

---

## 6. Threat Model (@security_audit)

### 6.1 Attack Surfaces

**A. Blocklist staleness / offline bypass**
- Threat: attacker targets user when offline for >7 days, installs blocked skill
- Mitigation: fail-closed at 7 days. No install of any previously-blocked skill ID when blocklist is stale. Stale but unblocked skills: allow (blocked skills are the specific risk)

**B. Manifest spoofing (Verified tier)**
- Threat: attacker crafts a manifest claiming `"tier": "verified"` without a valid signature
- Mitigation: tier field in manifest is advisory only. Actual tier determination is from gateway's cryptographic verification of the signature. A manifest claiming Verified with an invalid or missing signature is treated as Community.

**C. Permission creep via updates**
- Threat: skill installs with minimal permissions, then updates to add sensitive ones silently
- Mitigation: §4.1 permission diff on update. Permission-adding updates require full re-consent. Gateway diffs on every update install.

**D. `cloud_domains` misrepresentation**
- Threat: skill declares `"data_destination": "local"` but makes outbound calls at runtime
- Mitigation: for Verified skills, network calls are verified during the audit process. For Community skills, the `network` manifest field is used by `sandbox-exec` to restrict outbound access. A Community skill declaring `network: []` that attempts outbound connections is killed by the sandbox. This is the MCP_ADAPTER.md sandboxing model applied to all skills.

**E. Blocked tier UI bypass**
- Threat: client-side UI filtering removed by modified client; user installs blocked skill via direct API call
- Mitigation: block enforcement is at the gateway skill runner, not the UI. The gateway rejects `SKILL_BLOCKED` IDs regardless of client. @infra to confirm gateway API has no admin bypass path for blocked skills.

**F. Prompt injection via skill metadata**
- Threat: a Community skill's description or tool descriptions contain injected instructions that manipulate the LLM
- Mitigation: skill descriptions are not injected directly into model context. Tool descriptions are linted at install time for injection patterns (ref: MCP_ADAPTER.md requirement #3). This applies to all skills, not just MCP-backed ones.

### 6.2 References

- SlowMist MCP Security Checklist: https://github.com/slowmist/MCP-Security-Checklist
- §8.8 skill manifest system (`POLLY_IOS_SPEC.md` line 3931)
- §8.8.2 phase gate (`POLLY_IOS_SPEC.md` line 2054)

---

## 7. Browse & Discovery UI

This section is directional — final UI is owned by @frontend and @design_eng.

### 7.1 Browse View

- Default filter: Verified only
- Toggle to show Community (with persistent "unreviewed" indicator in browse)
- Blocked skills never appear in browse (removed from index, not just filtered)
- Filter by: category, data destination (local/cloud), permissions required

### 7.2 Skill Categories (initial set)

| Category | Examples |
|----------|---------|
| Productivity | Calendar, Email, Tasks |
| Knowledge | Obsidian, BookLore, Web Search |
| Code | GitHub, GitLab, Terminal |
| Data | Files, Databases, Spreadsheets |
| Creative | Image generation, Music, Design |
| Integrations | Home Assistant, Slack, Discord |
| Utilities | Weather, Time, Calculator |

### 7.3 Skill Detail Page

Required fields visible before install:
- Name, version, author
- Trust tier badge (prominent)
- Data destination callout
- Full permission list (plain language, not technical strings)
- Changelog link
- Community: user-submitted link to source code (strongly recommended, not required)

---

## 8. Asset Hosting

- Verified skills: hosted on Polly CDN, versioned
- Community skills: self-hosted by author; Polly stores the manifest only (not the skill binary)
- Install fetches from declared `download_url` in manifest
- Checksum verification (SHA-256) against `checksum` manifest field before install executes

---

## 9. Open Questions

| # | Question | Owner | Status |
|---|----------|-------|--------|
| 1 | Does the Polly public key get rotated? What's the key rotation plan? | @security_audit | Open |
| 2 | Community skill submission process — self-serve or gated? | @code_architect + Brett | Open |
| 3 | What categories trigger mandatory cloud warning even for Verified skills? (e.g., all analytics skills?) | @security_audit | Open |
| 4 | Asset hosting CDN provider for Verified skills | @infra | Open |

---

## 10. Out of Scope

- Skill development tooling / SDK (future spec)
- Revenue share / monetization (future decision)
- Skill ratings and reviews (Phase 3+)
- Enterprise/team skill distribution (Phase 3+)
