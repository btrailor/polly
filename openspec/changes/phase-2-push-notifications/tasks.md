# Phase 2: Push Notifications

**Status:** 📋 Planned  
**Gate:** `phase-2-push-security` must ship first (C1 auth-gate, C2 sendKey encryption)  
**Spec source:** `POLLY_IOS_SPEC.md` §3.14, §8.2, §4.8  
**Owners:** @frontend (iOS), @backend (gateway payload + routing)

## Goal

Full push notification system. Registration flow, gateway validation, APNs payload handling, deep link on tap, notification preferences UI.

## Tasks

### Registration Flow
- [ ] Install `expo-notifications`
- [ ] Push permission request — contextual only (trigger: user enables in Settings, or first cron-triggered event) — never upfront
- [ ] `push.status` gateway validation before registering (confirm C1 fix ships first)
- [ ] APNs token capture + `aight.push.register` RPC with deviceId + sendKey
- [ ] Registration error handling: gateway unavailable, permission denied, APNs failure

### Payload Handling
- [ ] Agent message notification payload: tap → open agent session deep link
- [ ] Cron completion notification: tap → open Today View process card
- [ ] System event notification: tap → relevant screen
- [ ] Background notification handling (silent push for state sync)
- [ ] Notification grouping by agent

### Preferences UI
- [ ] Settings → Notifications: master on/off toggle
- [ ] Per-agent notification toggle
- [ ] Per-type toggles: agent messages, cron completions, system events
- [ ] Quiet hours configuration
- [ ] Lockdown Mode: push notifications disabled (APNs creates outbound metadata)

### Gateway Integration
- [ ] `push.send` RPC from gateway → APNs via push relay
- [ ] Push relay certificate management (@backend)
- [ ] Payload size validation (APNs 4KB limit)

## Done When
Push notifications work end-to-end. Tap on notification opens correct screen. Preferences respected. @security_audit confirms no registration before C1 auth-gate fix.
