# Phase 2: Gateway Discovery (mDNS)

**Status:** 📋 Planned  
**Gate:** Phase 1 LAN WebSocket working  
**Spec source:** `POLLY_IOS_SPEC.md` §7.10, §3.14  
**Owners:** @frontend, @backend (gateway mDNS advertisement)

## Goal

Auto-discover the OpenClaw gateway on the local network via mDNS/Bonjour. Eliminates manual URL entry for LAN connections. Reduces onboarding friction for home network users.

## Tasks

### iOS (mDNS Browser)
- [ ] Install `react-native-zeroconf` (or `@nozbe/watermelondb` mDNS if compatible)
- [ ] Scan for `_openclaw._tcp.local.` service records on LAN
- [ ] Discovery UI: animated scan screen, discovered gateway list (hostname + port)
- [ ] One-tap connect from discovered gateway (pre-fills URL field, runs auth flow)
- [ ] Manual URL entry preserved as fallback
- [ ] `NSLocalNetworkUsageDescription` permission string (required iOS 14+)
- [ ] Discovery runs only when user initiates (not background scanning)

### Gateway (@backend)
- [ ] OpenClaw gateway advertises `_openclaw._tcp.local.` with `port`, `deviceId`, `version` TXT records
- [ ] Advertisement togglable in gateway config (`polly.gateway.mdns: true`)

### UX
- [ ] Onboarding: "Scan for gateway" button alongside manual URL entry
- [ ] Settings → Gateway: re-scan action for network changes
- [ ] Multiple gateways found: list with selection (not auto-connect to first)

## Done When
Gateway on same LAN is discoverable. Onboarding scan works. @qa_guy confirms no auto-connect without user confirmation.
