# Phase 23.5: Security Hardening

**Status:** 📋 PLANNING COMPLETE - Ready for Implementation  
**Priority:** 🔐 CRITICAL - Must complete before Phase 24  
**Estimated Duration:** 2-3 weeks (15-21 days)  
**Complexity:** High

**Planning Date:** February 3, 2026  
**Strategic Insertion Point:** After Phase 23, before Phase 24

---

## Executive Summary

Phase 23.5 implements comprehensive security hardening for Polly using the **Capability Broker Pattern**. This phase addresses critical security gaps introduced in Phase 23 (code execution) and establishes a secure foundation before building Phase 24 (Orchestrator Mode), which will enable complex multi-persona workflows.

**Key Architectural Decision:** Capability Broker Pattern
- LLM has no inherent power, must request capabilities explicitly
- All high-risk operations route through centralized broker
- Explicit delegation model with audit logging
- Request/grant system for package installations, shell execution, API calls

**Why Now:**
- Phase 23 introduced unsandboxed code execution (CRITICAL RISK)
- Phase 24 (Orchestrator) will compound security complexity (multi-persona workflows)
- Phase 27 (Designer) will generate code with package imports (exactly the attack vector we're securing)
- Phase 28 (Plugins) will introduce external untrusted code (highest risk)
- Retrofitting security after these features = 10x harder

**Success Criteria:**
- ✅ Code execution fully sandboxed (Pyodide, no subprocess)
- ✅ Package management secure (allowlist + approval workflow)
- ✅ Capability broker operational (all high-risk ops routed)
- ✅ Content security active (prompt injection detection, PII warnings)
- ✅ API keys secure (context managers, memory cleanup)
- ✅ Comprehensive testing complete
- ✅ User documentation complete

---

## Problem Statement

### Current Security Gaps

#### 1. Unsandboxed Code Execution (CRITICAL)
**Location:** `interfaces/server.py:4992-5074`
- Uses `subprocess.run()` to execute Python code
- No isolation from host system
- No network restrictions
- No filesystem restrictions
- Can execute arbitrary system commands
- **Risk:** Malicious code can access user files, network, system resources

#### 2. Permissive CORS Policy (HIGH)
**Location:** `interfaces/server.py:111-118`
- Allows all origins (`allow_origins=["*"]`)
- Allows all methods and headers
- **Risk:** Any website can make requests to Polly server
- **Impact:** CSRF attacks, unauthorized API access

#### 3. No Package Installation Controls (HIGH)
**Location:** Code generation in Professor/Architect personas
- LLM can suggest arbitrary package installations in generated code
- No detection or approval workflow
- **Risk:** Malicious packages installed via code suggestions
- **Attack Vector:** LLM generates `import malicious_package` in curriculum exercises

#### 4. No Input Validation (MEDIUM)
**Location:** All API endpoints
- No validation on request payloads
- No sanitization of user input
- **Risk:** Injection attacks, malformed requests

#### 5. API Key Exposure Risk (MEDIUM)
**Location:** `core/secrets_manager.py`
- Keys may linger in memory after use
- No secure cleanup pattern
- **Risk:** Keys exposed in memory dumps, logs

#### 6. No Prompt Injection Protection (MEDIUM)
**Location:** RAG content passed to LLM
- Documents may contain instructions that hijack LLM behavior
- No separation of "data" from "instructions"
- **Risk:** Malicious documents can manipulate LLM responses

#### 7. No PII Detection (LOW)
**Location:** Content sent to cloud APIs
- Email addresses, phone numbers, SSNs sent to cloud providers
- No user awareness or filtering
- **Risk:** Privacy violations, compliance issues

### User Pain Points

**Current Workflow (Unsafe):**
1. User: "Create a Python exercise for data analysis"
2. Professor: Generates code with `import pandas`
3. System: Executes code directly via subprocess
4. **Problem:** No verification that `pandas` is safe to import
5. **Problem:** Code runs with full system access

**Desired Workflow (Secure):**
1. User: "Create a Python exercise for data analysis"
2. Professor: Generates code with `import pandas`
3. Package Detector: Scans code, finds `pandas`
4. Capability Broker: Checks allowlist, `pandas` is approved ✅
5. Pyodide Sandbox: Executes code in isolated environment
6. **Result:** Safe execution with no system access

---

## Solution Architecture

### Design Decisions (Confirmed)

#### 1. Code Execution: Pyodide Instead of Docker
**Decision:** Use Pyodide (Python compiled to WebAssembly) instead of Docker

**Rationale:**
- Docker in app bundle too complex for distribution
- Pyodide = ~6MB bundle size (acceptable)
- Runs in browser/Electron renderer process
- Inherently sandboxed by browser security model
- No network access by default
- No filesystem access by default
- Limited to pure Python + scientific libs (numpy, pandas work!)

**Tradeoff:**
- Can't install arbitrary packages (they must be pre-compiled to WASM)
- This is actually a **security feature** for our use case
- Curriculum exercises use pure Python + supported scientific libs

**Implementation:**
- `core/sandbox.py` - PyodideSandbox class
- `electron-app/src/renderer/pyodide-worker.js` - Web Worker for isolation
- Replace `subprocess.run()` in `/polly/exercises/execute` endpoint

#### 2. Package Management: Allowlist + Approval
**Decision:** Pre-approved allowlist with user approval for unknown packages

**Rationale:**
- Python stdlib always safe (no approval needed)
- ~100 vetted packages pre-approved (numpy, pandas, requests, etc.)
- Unknown packages require user approval
- Context7 integration provides trust scores for informed decisions

**Approval Flow:**
1. Package Detector scans generated code
2. Finds unapproved packages
3. **Blocks execution immediately**
4. Shows approval dialog with:
   - Package name and description (from PyPI)
   - Context7 trust score (if available)
   - Usage statistics
   - Known vulnerabilities (future: OSV integration)
5. User can: Approve, Deny, or Permanently Block

**Context7 Integration:**
- Leverage existing `integrations/context7.py`
- Use `trust_score` field from library search results
- Show trust score in approval dialog
- Auto-approve if trust score >= 7 (configurable)

**Implementation:**
- `core/package_detector.py` - Scans code for imports
- `core/package_metadata.py` - Fetches PyPI + Context7 info
- `config/approved_packages.yaml` - Allowlist configuration
- `electron-app/src/renderer/components/package-approval-dialog.js` - Approval UI

#### 3. Capability Broker Pattern
**Decision:** Centralized broker for all high-risk operations

**Architecture:**
```
User/LLM Request
      ↓
Capability Broker (NEW)
  - Validates request
  - Checks policy
  - Logs to audit.db
  - Requires approval if needed
      ↓
Approved Operation
  - Pyodide Sandbox (code execution)
  - Package Manager (with allowlist)
  - API Gateway (secure key handling)
  - Shell Executor (if enabled)
```

**Capability Types:**
- `PACKAGE_INSTALL` - HIGH RISK (always require approval)
- `SHELL_EXEC` - HIGH RISK (disabled by default for personal use)
- `API_CALL` - MEDIUM RISK (for rate limiting, not blocking)
- **NOT** `FILE_WRITE` - Permissive (trusted operation for vault/notes)
- **NOT** `CODE_EXEC` - Handled by Pyodide sandbox (inherently safe)

**Implementation:**
- `core/capability_broker.py` - Core broker logic
- `core/capabilities/types.py` - Capability type definitions
- `core/capabilities/grants.py` - Grant management
- `core/audit_logger.py` - Audit logging to SQLite
- `~/.polly/audit.db` - Audit log database

#### 4. Content Security: Prompt Injection Detection
**Decision:** Detect and warn on suspicious content patterns

**Rationale:**
- Documents in RAG may contain instructions that hijack LLM
- Separate "data" from "instructions" in content
- Warn user when suspicious patterns detected
- Don't block (warn-only for personal use)

**Patterns to Detect:**
- "Ignore previous instructions"
- "You are now a..."
- "System: ..." / "User: ..." role-playing
- Base64-encoded instructions
- Unicode obfuscation

**Implementation:**
- `core/content_sanitizer.py` - Content sanitization
- `core/security/patterns.py` - Suspicious pattern definitions
- Integrate into RAG pipeline before LLM calls

#### 5. PII Detection: Warn-Only Mode
**Decision:** Detect PII but only warn, don't block

**Rationale:**
- Personal use case (less restrictive)
- User decides what to send to cloud providers
- Preserves context (no automatic redaction)

**PII Patterns:**
- Email addresses
- Phone numbers
- SSNs
- Credit card numbers
- API keys (in content)

**Implementation:**
- `core/pii_filter.py` - PII detection
- `core/security/pii_patterns.py` - Regex patterns
- Integrate into `router_v2.py` before cloud API calls
- Show warnings in chat UI

#### 6. API Key Security: Context Managers
**Decision:** Use context managers for secure key access

**Pattern:**
```python
async with secrets_manager.get_secret_for_request('anthropic') as api_key:
    # Key available here
    response = await make_api_call(api_key)
# Key securely cleared from memory here
```

**Implementation:**
- Enhance `core/secrets_manager.py` with context manager support
- Update all provider adapters to use secure pattern
- Add memory cleanup after API calls

#### 7. CORS Policy: Restrict to Localhost + Tailscale
**Decision:** Restrict CORS to localhost and Tailscale CGNAT range

**Rationale:**
- Current `allow_origins=["*"]` is too permissive
- Personal use case: Only need localhost access
- Tailscale CGNAT range (100.64.0.0/10) for remote access

**Implementation:**
- Update `interfaces/server.py:111-118`
- Configure allowed origins in `config/security_policy.yaml`

---

## Implementation Plan

### Week 1: Foundation + Pyodide Sandbox (Days 1-7)

#### Days 1-2: Quick Security Wins
**Goal:** Fix critical security gaps immediately

**Tasks:**
1. Fix CORS policy (`interfaces/server.py:111-118`)
   - Restrict to localhost + Tailscale CGNAT range
   - Update from `allow_origins=["*"]` to specific origins
2. Add input validation middleware (`interfaces/server.py`)
   - Validate request payloads
   - Sanitize user input
   - Add rate limiting
3. Audit Electron exec() calls (`electron-app/src/main/main.js:662`)
   - Review all `exec()` calls
   - Ensure they're necessary and safe
4. Create security policy schema (`config/security_policy.yaml`)
   - Define configuration structure
   - Document all security settings

**Deliverables:**
- ✅ CORS restricted to localhost + Tailscale
- ✅ Input validation middleware active
- ✅ Security policy schema defined

#### Days 3-5: Pyodide Code Sandbox
**Goal:** Replace subprocess with sandboxed execution

**Tasks:**
1. Integrate Pyodide into Electron app
   - Add Pyodide CDN reference (no npm package needed)
   - ~6MB bundle size (acceptable)
2. Create PyodideSandbox class (`core/sandbox.py`)
   - Execute Python code in Pyodide
   - Enforce timeout and memory limits
   - Return execution results
3. Create Pyodide worker (`electron-app/src/renderer/pyodide-worker.js`)
   - Web Worker for isolation
   - Load Pyodide runtime
   - Execute code with timeout
4. Replace subprocess in `/polly/exercises/execute` endpoint
   - Remove `subprocess.run()` call
   - Use PyodideSandbox instead
5. Update curriculum system to use Pyodide
   - Test exercise execution
   - Verify timeout and memory limits

**Deliverables:**
- ✅ Pyodide integrated (~6MB via CDN)
- ✅ Code execution fully sandboxed
- ✅ Curriculum exercises running in Pyodide
- ✅ Timeout and memory limits enforced

#### Days 6-7: Package Detection System
**Goal:** Detect package installations in generated code

**Tasks:**
1. Create PackageDetector class (`core/package_detector.py`)
   - Scan code for `import` statements
   - Detect `pip install` suggestions in comments/docstrings
   - Cross-reference against allowlist
2. Create PackageMetadata fetcher (`core/package_metadata.py`)
   - Fetch PyPI package info
   - Integrate Context7 trust scores
   - Cache metadata locally
3. Integrate with Professor persona (`core/personas/implementations/professor.py`)
   - Scan generated code before execution
   - Trigger approval flow for unapproved packages
4. Integrate with Architect persona (`core/personas/implementations/architect.py`)
   - Same package detection logic
5. Integrate with curriculum system (`learners/curriculum_manager.py`)
   - Scan exercise code before execution
   - Block execution if unapproved packages found

**Deliverables:**
- ✅ Package detection working
- ✅ Integration with code generation personas
- ✅ Block execution and show approval dialog

### Week 2: Capability Broker Architecture (Days 8-14)

#### Days 8-10: Core Broker
**Goal:** Implement capability request/grant system

**Tasks:**
1. Create CapabilityBroker class (`core/capability_broker.py`)
   - Request/grant system
   - Policy validation
   - Integration with audit logger
2. Define capability types (`core/capabilities/types.py`)
   - PACKAGE_INSTALL
   - SHELL_EXEC
   - API_CALL
3. Implement grant management (`core/capabilities/grants.py`)
   - Grant storage
   - Grant expiration
   - Grant revocation
4. Create audit logging system (`core/audit_logger.py`)
   - SQLite database at `~/.polly/audit.db`
   - Log all capability requests
   - Log grants and denials
   - Retention policy (90 days default)

**Deliverables:**
- ✅ Capability broker operational
- ✅ Three capability types defined
- ✅ Audit logging active
- ✅ Policy validation working

#### Days 11-12: Package Management Integration
**Goal:** Connect package detection to capability broker

**Tasks:**
1. Create approved packages allowlist (`config/approved_packages.yaml`)
   - Python stdlib (always safe)
   - ~100 pre-approved packages (numpy, pandas, requests, etc.)
   - Context7 trust score integration
2. Create package approval dialog UI (`electron-app/src/renderer/components/package-approval-dialog.js`)
   - Show package metadata (PyPI info)
   - Show Context7 trust score
   - Approve/Deny/Block buttons
3. Add package approval endpoints (`interfaces/server.py`)
   - `POST /polly/security/package/approve`
   - `POST /polly/security/package/deny`
   - `GET /polly/security/package/metadata`
4. Integrate package detector with capability broker
   - Route package requests through broker
   - Show approval dialog when needed
   - Cache approved packages to user config

**Deliverables:**
- ✅ Allowlist with ~100 pre-approved packages
- ✅ Approval UI functional
- ✅ User can approve/deny/block packages
- ✅ Approved packages cached

#### Days 13-14: Content Sanitizer
**Goal:** Detect prompt injection patterns in documents

**Tasks:**
1. Create ContentSanitizer class (`core/content_sanitizer.py`)
   - Detect suspicious patterns
   - Separate "data" from "instructions"
   - Warn user when patterns found
2. Define suspicious patterns (`core/security/patterns.py`)
   - "Ignore previous instructions"
   - Role-playing patterns
   - Base64/Unicode obfuscation
3. Integrate with RAG system (`core/rag.py`)
   - Sanitize content before passing to LLM
   - Add warnings to chat UI
4. Make it configurable (`config/security_policy.yaml`)
   - Sensitivity levels (low/medium/high)
   - Warn-only vs block mode

**Deliverables:**
- ✅ Prompt injection detection working
- ✅ Warnings shown to user
- ✅ Configurable sensitivity

### Week 3: API Security + Polish (Days 15-21)

#### Days 15-17: API Key Hardening
**Goal:** Secure API key handling with context managers

**Tasks:**
1. Enhance secrets_manager.py with context manager support
   - `get_secret_for_request()` context manager
   - Secure memory cleanup after use
   - Key rotation helpers
2. Update all provider adapters
   - `core/providers/anthropic_provider.py`
   - `core/providers/openai_provider.py`
   - `core/providers/github_provider.py`
   - `core/providers/grok_provider.py`
   - `core/providers/perplexity_provider.py`
   - `core/providers/gemini_provider.py`
   - `core/providers/mistral_provider.py`
3. Test secure key cleanup
   - Verify keys cleared from memory
   - Test key rotation workflow

**Deliverables:**
- ✅ Context managers implemented
- ✅ All providers using secure pattern
- ✅ Memory cleanup verified

#### Days 18-19: PII Detection (Warn-Only)
**Goal:** Detect PII in content before cloud API calls

**Tasks:**
1. Create PIIFilter class (`core/pii_filter.py`)
   - Detect email, phone, SSN, credit card patterns
   - Detect API keys in content
2. Define PII patterns (`core/security/pii_patterns.py`)
   - Regex patterns for each PII type
   - Configurable sensitivity
3. Integrate with router_v2.py
   - Scan content before cloud API calls
   - Show warnings in chat UI
   - User can choose to send anyway
4. Make it opt-in (`config/security_policy.yaml`)
   - User can disable warnings
   - Warn-only mode (no blocking)

**Deliverables:**
- ✅ PII detection active
- ✅ Warnings shown to user
- ✅ Opt-in configuration

#### Days 20-21: Testing + Documentation
**Goal:** Comprehensive testing and user documentation

**Tasks:**
1. Write security test suite (`tests/test_security.py`)
   - Test Pyodide sandbox isolation
   - Test package detection
   - Test capability broker
   - Test prompt injection detection
   - Test PII detection
2. Write package detection tests (`tests/test_package_detector.py`)
   - Test import detection
   - Test pip install detection
   - Test allowlist matching
3. Write content sanitizer tests (`tests/test_content_sanitizer.py`)
   - Test pattern detection
   - Test warning generation
4. Create SECURITY.md user guide (`docs/SECURITY.md`)
   - How security features work
   - Configuration options
   - Approval workflows
   - Best practices
5. Create Phase 23.5 completion report (`PHASE23.5_COMPLETE.md`)
   - Implementation summary
   - Success criteria verification
   - Files created/modified

**Deliverables:**
- ✅ Comprehensive test suite passing
- ✅ User documentation complete
- ✅ Phase completion report

---

## Configuration Files

### config/security_policy.yaml

```yaml
# Polly Security Policy Configuration
# Phase 23.5: Security Hardening

security_mode: personal  # personal | team | public

# Capability Broker Configuration
capabilities:
  # Package Installation
  package_install:
    enabled: true
    allowlist_path: config/approved_packages.yaml
    require_approval: true  # Always require approval
    show_pypi_metadata: true
    show_context7_info: true  # Use Context7 trust scores
    min_context7_trust: 7  # Auto-approve if trust score >= 7
    block_on_deny: false  # Don't permanently block, just deny this time
  
  # Shell Command Execution
  shell_exec:
    enabled: false  # Disabled by default for personal use
    allowed_commands: []
    require_approval: true
  
  # API Calls (for rate limiting)
  api_call:
    enabled: true
    rate_limit_per_minute: 60
    log_all_requests: true

# Code Execution Sandbox
sandbox:
  type: pyodide  # pyodide | docker (docker not used)
  timeout_seconds: 10
  memory_limit_mb: 512
  network_access: false
  filesystem_access: false

# Content Security
content_security:
  scan_for_prompt_injection: true
  prompt_injection_sensitivity: medium  # low | medium | high
  warn_on_suspicious_content: true
  block_suspicious_content: false  # Warning only for personal use
  
  pii_detection:
    enabled: true
    warn_only: true  # Your choice: warn but don't block
    patterns:
      - email
      - phone
      - ssn
      - credit_card
      - api_key
    # Opt-in: user can disable warnings
    user_can_disable: true

# API Key Security
api_keys:
  use_secure_context_manager: true
  auto_cleanup_memory: true
  rotation_reminder_days: 90  # Remind user to rotate keys
  
# Audit Logging
audit:
  enabled: true
  database_path: ~/.polly/audit.db
  retention_days: 90
  log_events:
    - capability_request
    - capability_grant
    - capability_deny
    - package_install_request
    - package_install_approved
    - package_install_denied
    - code_execution
    - api_call
    - pii_detected
    - suspicious_content_detected

# CORS Policy (Fixed in Week 1)
cors:
  allowed_origins:
    - http://localhost:*
    - http://127.0.0.1:*
    - http://100.64.0.0/10  # Tailscale CGNAT range
  allow_credentials: true
```

### config/approved_packages.yaml

```yaml
# Polly Package Allowlist
# Phase 23.5: Security Hardening
# Starting allowlist inspired by Context7's curated library approach

# Python Standard Library (always allowed, no approval needed)
stdlib_modules:
  - os
  - sys
  - json
  - re
  - datetime
  - pathlib
  - typing
  - collections
  - itertools
  - functools
  - asyncio
  - logging
  - math
  - random
  - string
  - urllib
  - http
  # ... (full stdlib list)

# Pre-approved packages (common, safe, well-vetted)
# Inspired by Context7's curated library approach
approved_packages:
  # Data Science & ML (Context7 top libraries)
  - numpy
  - pandas
  - matplotlib
  - scikit-learn
  - scipy
  - jupyter
  
  # Web & API
  - requests
  - httpx
  - aiohttp
  - flask
  - fastapi
  
  # Testing
  - pytest
  - unittest
  - coverage
  
  # Code Quality
  - black
  - ruff
  - mypy
  - pylint
  
  # Utilities
  - python-dotenv
  - pyyaml
  - click
  - rich
  
  # ... (~100 total packages)

# Explicitly blocked (known malicious)
blocked_packages:
  - malicious-example  # Placeholder

# Approval required for anything not in approved list
require_approval_for_unlisted: true

# Integration with Context7
context7:
  use_trust_score: true  # Leverage Context7 library trust scores
  min_trust_score: 7     # Minimum trust score (0-10) to auto-approve
  
  # When LLM suggests a package not in allowlist:
  # 1. Check Context7 for library info
  # 2. Show trust score, description, usage stats
  # 3. User decides to approve/deny/block
```

---

## Success Criteria

Phase 23.5 is complete when all of the following are verified:

### ✅ Code Execution Sandboxed
- [ ] Pyodide integrated and working
- [ ] No `subprocess.run()` for untrusted code
- [ ] Curriculum exercises running in sandbox
- [ ] Timeout and memory limits enforced
- [ ] No network or filesystem access from sandbox

### ✅ Package Management Secure
- [ ] Allowlist active with ~100 approved packages
- [ ] Package detection working in generated code
- [ ] Approval dialog functional
- [ ] User can approve/deny/block packages
- [ ] Context7 trust scores shown in approval dialog
- [ ] Approved packages cached to user config

### ✅ Capability Broker Operational
- [ ] All high-risk operations route through broker
- [ ] Audit logging captures all security events
- [ ] Policy enforcement working
- [ ] Grant management functional
- [ ] Audit database at `~/.polly/audit.db`

### ✅ Content Security Active
- [ ] Prompt injection detection working
- [ ] Suspicious content warnings shown
- [ ] PII detection active (warn-only mode)
- [ ] Configurable sensitivity levels
- [ ] Integration with RAG system

### ✅ API Keys Secure
- [ ] Context managers implemented
- [ ] All providers using secure pattern
- [ ] Memory cleanup verified
- [ ] Key rotation helpers added

### ✅ Testing Complete
- [ ] Security test suite passing
- [ ] Prompt injection scenarios tested
- [ ] Package detection edge cases covered
- [ ] Sandbox isolation verified
- [ ] Capability broker tested

### ✅ Documentation Complete
- [ ] SECURITY.md user guide written
- [ ] Phase completion report created
- [ ] Roadmap updated
- [ ] Configuration files documented

---

## Risk Mitigation

### Risk: Pyodide doesn't support all Python packages
**Mitigation:** 
- Curriculum exercises use pure Python + supported scientific libs
- numpy, pandas work in Pyodide
- Document limitations in user guide

### Risk: Performance degradation from security checks
**Mitigation:** 
- Checks only run when code is executed or packages detected
- Not on every query
- Cache package metadata locally

### Risk: User friction from approval dialogs
**Mitigation:** 
- Pre-approve ~100 common packages
- Only prompt for unknown packages
- Show Context7 trust scores for informed decisions

### Risk: Context7 API rate limits
**Mitigation:** 
- Cache trust scores locally
- Fallback to PyPI if Context7 unavailable
- Rate limit handling in integration

### Risk: False positives in prompt injection detection
**Mitigation:** 
- Configurable sensitivity levels
- Warn-only mode (don't block)
- User can disable warnings

---

## OpenClaw Compatibility

**Decision:** Build Polly-first with clean abstraction layers

**Rationale:**
- OpenClaw decision point is Phase 20 (Communication features)
- Security architecture is request-source agnostic by design
- Capability Broker has `requestor` field (could be "polly-core" or "openclaw-gateway")
- Audit logs track request origin
- Same security policies apply regardless of entry point

**Zero Compatibility Cost:**
- Architecture designed to be request-source agnostic
- If OpenClaw integrated later, it would work like:
  ```
  OpenClaw Message → Polly Capability Broker → Approved Operations
  ```

**Timeline:** Defer OpenClaw decision until Phase 20 planning

---

## Post-Phase 23.5: Unlocked Phases

Once Phase 23.5 completes, these phases can proceed safely:

✅ **Phase 22 Frontend** (Teaching Mode UI) - 1-2 days  
✅ **Phase 24** (Orchestrator Mode) - 2-3 weeks ← CRITICAL UNBLOCK  
✅ **Phase 13b** (User Profile System) - 3 weeks  
✅ **Phase 27** (Designer Persona) - 8-12 weeks  
✅ **Phase 28** (Plugin Ecosystem) - 4-6 weeks ← EXTERNAL CODE SAFE

---

## Files to Create/Modify

### New Files (Week 1)
- `core/sandbox.py` - PyodideSandbox class
- `electron-app/src/renderer/pyodide-worker.js` - Web Worker
- `electron-app/src/renderer/pyodide-loader.js` - Pyodide initialization
- `core/package_detector.py` - Package detection
- `core/package_metadata.py` - PyPI + Context7 metadata
- `config/security_policy.yaml` - Security configuration

### New Files (Week 2)
- `core/capability_broker.py` - Capability broker
- `core/capabilities/types.py` - Capability type definitions
- `core/capabilities/grants.py` - Grant management
- `core/audit_logger.py` - Audit logging
- `config/approved_packages.yaml` - Package allowlist
- `electron-app/src/renderer/components/package-approval-dialog.js` - Approval UI
- `core/content_sanitizer.py` - Content sanitization
- `core/security/patterns.py` - Suspicious patterns

### New Files (Week 3)
- `core/pii_filter.py` - PII detection
- `core/security/pii_patterns.py` - PII regex patterns
- `tests/test_security.py` - Security test suite
- `tests/test_package_detector.py` - Package detection tests
- `tests/test_content_sanitizer.py` - Content sanitizer tests
- `docs/SECURITY.md` - User-facing security guide

### Modified Files
- `interfaces/server.py` - CORS fix, input validation, Pyodide integration, package approval endpoints
- `electron-app/src/renderer/app.js` - Pyodide worker integration, approval dialog
- `core/personas/implementations/professor.py` - Package detection integration
- `core/personas/implementations/architect.py` - Package detection integration
- `learners/curriculum_manager.py` - Package detection before execution
- `core/secrets_manager.py` - Context manager support
- `core/providers/*.py` - Secure key pattern
- `core/rag.py` - Content sanitization integration
- `core/router_v2.py` - PII detection integration
- `electron-app/src/main/main.js` - Audit exec() calls
- `package.json` - Pyodide CDN reference

---

## Dependencies

**Prerequisites:**
- Phase 23 ✅ (Curriculum System - introduces code execution risk)
- Phase 11 ✅ (Multi-Model Routing - provider adapters)
- Phase 14 ✅ (Mental Models - for context)

**Blocks:**
- Phase 24 (Orchestrator Mode) - CRITICAL DEPENDENCY
- Phase 27 (Designer Persona) - Generates code with packages
- Phase 28 (Plugin Ecosystem) - External untrusted code

---

## Timeline

**Estimated Duration:** 2-3 weeks (15-21 days)

**Week 1:** Foundation + Pyodide Sandbox (7 days)  
**Week 2:** Capability Broker Architecture (7 days)  
**Week 3:** API Security + Polish (7 days)

**Start Date:** [TBD]  
**Target Completion:** [TBD + 2-3 weeks]

---

## References

- **Context7 Integration:** `integrations/context7.py`
- **Current Code Execution:** `interfaces/server.py:4992-5074`
- **Current CORS Policy:** `interfaces/server.py:111-118`
- **Secrets Manager:** `core/secrets_manager.py`
- **Phase 23 Completion:** `docs/planning/phases/phase-23/PHASE23_COMPLETE.md`
- **Master Roadmap:** `MASTER_ROADMAP.md`

---

**Maintained By:** Development team  
**Last Updated:** February 3, 2026  
**Status:** Planning Complete, Ready for Implementation
