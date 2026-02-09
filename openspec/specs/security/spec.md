# Security (OpenSpec)

Source of truth for security behavior. Current + planned (Phase 23.5): [docs/SECURITY.md](../../../docs/SECURITY.md). Phase 23.5 spec: [docs/planning/phases/phase-23.5/](../../../docs/planning/phases/phase-23.5/).

## Current

- **Secrets:** API keys in Keychain (Phase 5); env fallback. Multiple providers.
- **Code execution (Phase 23):** Curriculum exercises run via subprocess (Python). Timeout; stdout/stderr capture. **Not yet sandboxed** — Phase 23.5 will replace with Pyodide.

## Planned (Phase 23.5)

- **Capability Broker:** LLM requests capabilities; no direct access.
- **Pyodide sandbox:** Replace subprocess; WebAssembly Python; no network/filesystem; timeout and memory limits.
- **Package allowlist:** Pre-approved packages in `config/approved_packages.yaml`; approval workflow for unknown; Context7 trust scores.
- **Content sanitization:** Prompt-injection detection; PII detection (warn-only).
- **API key hardening:** Context managers; clear after use. Config: `config/security_policy.yaml`.

## Reference

- [docs/SECURITY.md](../../../docs/SECURITY.md) — User-facing security guide
- [PHASE23.5_SECURITY_HARDENING.md](../../../docs/planning/phases/phase-23.5/PHASE23.5_SECURITY_HARDENING.md) — Spec
- [PHASE23.5_IMPLEMENTATION_PLAN.md](../../../docs/planning/phases/phase-23.5/PHASE23.5_IMPLEMENTATION_PLAN.md)
