# Phase 2: Integrations

**Status:** 📋 Planned  
**Gate:** Phase 1 Settings infrastructure  
**Spec source:** `POLLY_IOS_SPEC.md` §15.2.3, §15.3.2, §15.3.3, §4.8  
**Owners:** @frontend (iOS OAuth/native), @backend (gateway skill config)

## Goal

Google Workspace, GitHub, and Apple EventKit integrations. Each surfaces in Settings → Integrations as a connection card.

## Tasks

### Google Workspace OAuth
- [ ] OAuth 2.0 flow (Google Identity Services) — in-app browser, token capture
- [ ] Token forwarding to gateway (stored in gateway config, not device)
- [ ] Gmail access: summary surfacing in Today View, context injection
- [ ] Google Calendar: events in Today View, context injection for scheduling queries
- [ ] Settings → Integrations → Google: connect/disconnect, scope display, last synced
- [ ] Revoke on disconnect (token deleted from gateway + local)

### GitHub Integration
- [ ] PAT (Personal Access Token) entry in Settings → Integrations → GitHub
- [ ] Token forwarded to gateway skill config
- [ ] Gateway-side GitHub skill (PR list, issue list, file read)
- [ ] PR status in Today View (if user sets watched repos)
- [ ] Context injection: attach a PR or issue via `/` command

### Apple EventKit (Calendar + Reminders)
- [ ] `NSCalendarsUsageDescription` + `NSRemindersUsageDescription` permissions — contextual trigger only
- [ ] Read Calendar events for next 7 days → Today View
- [ ] Read Reminders due today/overdue → Today View
- [ ] Context injection: upcoming events injected when user asks scheduling questions
- [ ] Write path: create Reminder from conversation (agent suggests, user confirms) — Phase 3

### Settings UI
- [ ] Settings → Integrations section (new)
- [ ] Per-integration connection card: icon, name, status, connect/disconnect
- [ ] Error states: token expired, permission revoked, network offline

## Done When
At least Google Calendar + EventKit reading working. Settings connection flow complete. Tokens never in MMKV (gateway-only). @security_audit review of OAuth token handling.
