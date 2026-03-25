# Push Registration Security Fix

**Status:** Required pre-production gate — Phase 2 blocked until this ships  
**Owner:** @backend  
**Reviewer:** @security_audit

---

## Issues

### C1 — Unauthenticated Push Registration

**Problem:** The push registration endpoint (`aight.push.register`) does not bind the registration to an authenticated WebSocket session. Any caller that knows the endpoint can register a device token without proving identity.

**Risk:** An attacker could register their own push token associated with a victim's gateway, receiving push notifications intended for the user.

**Fix:** Registration must be bound to an authenticated session. The gateway verifies that the `deviceId` in the registration request matches the authenticated session before accepting the registration. No authenticated session = registration rejected.

**Implementation:**
- Check active session auth before processing `aight.push.register`
- Bind `deviceId` to session identity at registration time
- Reject registration attempts with no valid session

---

### C2 — `sendKey` Stored in Cleartext

**Problem:** `~/.openclaw/aight/devices.json` stores `sendKey` in plaintext on disk. Confirmed in current state:

```json
{
  "sendKey": "ae692d6ab61098a8ededb618fc69ae8d..."
}
```

Anyone with filesystem access to the gateway machine can read push auth keys for all registered devices.

**Risk:** Compromised `sendKey` allows an attacker to send authenticated push payloads to the device, potentially triggering actions or delivering spoofed notifications.

**Fix (gateway side):** Encrypt `sendKey` at rest in `devices.json` using a gateway-held encryption key stored in the system keychain (macOS Keychain via `security` CLI or equivalent). The devices file stores the encrypted blob; the gateway decrypts on load.

**Fix (iOS side):** Already specced in `POLLY_IOS_SPEC.md` §8.2 — `sendKey` stored via `expo-secure-store`, never in `AsyncStorage` or on disk. No debug/Sentry logging of key material.

**Implementation:**
- Gateway: on first run after fix, generate a `devices.key` stored in system keychain
- Encrypt all `sendKey` values before writing to `devices.json`
- Decrypt on load; re-encrypt on any write
- Migration: on startup, detect plaintext `sendKey` entries, encrypt in-place, rewrite file

---

## Acceptance Criteria

- [ ] `aight.push.register` rejects requests with no authenticated session
- [ ] `devices.json` contains no plaintext `sendKey` values after migration
- [ ] Gateway load/save cycle round-trips correctly through encryption
- [ ] Existing registered devices survive migration (re-encrypted, not invalidated)
- [ ] @security_audit sign-off on both fixes before Phase 2 production deploy

---

## Out of Scope (Future)

- mTLS on gateway→relay channel (noted as future in §8.2 threat model)
- Relay domain pinning (future)
- 10-device cap enforcement (§8.6 M2 — separate item)
