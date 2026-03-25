# Phase 2: Push Security Fix

**Status:** ⚠️ Required pre-production  
**Gate:** Must ship before Phase 2 goes to production users  
**Spec source:** `PUSH_SECURITY_FIX.md`  
**Pre-ship gate:** @security_audit sign-off required

## Goal

Close two pre-production security vulnerabilities in the push notification path before any real users are on the system.

## Vulnerabilities

**C1: Unauthenticated push registration**  
Any client can register a push token without authentication. Gateway accepts all registrations.

**C2: `sendKey` stored in cleartext in `devices.json`**  
The key used to authorize push sends is stored unencrypted on disk.

## Tasks

- [ ] C1: Require authenticated session to register push token — @backend
- [ ] C2: Move `sendKey` to macOS Keychain — @backend
- [ ] C2: Remove `devices.json` cleartext key storage — @backend
- [ ] @security_audit review + sign-off

## Done when
Both C1 and C2 resolved. @security_audit signed off. This change must be archived before Phase 2 ships to production.
