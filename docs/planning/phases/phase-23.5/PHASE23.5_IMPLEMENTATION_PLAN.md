# Phase 23.5: Security Hardening - Implementation Plan

**Status:** 📋 Ready for Implementation  
**Duration:** 2-3 weeks (15-21 days)  
**Last Updated:** February 3, 2026

---

## Overview

This document provides a detailed week-by-week implementation guide for Phase 23.5: Security Hardening. Each day includes specific tasks, file changes, and deliverables.

**Reference:** See `PHASE23.5_SECURITY_HARDENING.md` for complete specification and architecture.

---

## Week 1: Foundation + Pyodide Sandbox (Days 1-7)

### Days 1-2: Quick Security Wins

**Goal:** Fix critical security gaps immediately

#### Day 1: CORS Fix + Input Validation

**Tasks:**

1. **Fix CORS Policy** (`interfaces/server.py:111-118`)
   ```python
   # BEFORE:
   allow_origins=["*"]
   
   # AFTER:
   allow_origins=[
       "http://localhost:*",
       "http://127.0.0.1:*",
       "http://100.64.0.0/10"  # Tailscale CGNAT
   ]
   ```
   - Load allowed origins from `config/security_policy.yaml`
   - Add validation for origin format
   - Test with localhost and Tailscale IPs

2. **Add Input Validation Middleware** (`interfaces/server.py`)
   - Create validation decorator
   - Validate request payloads (JSON schema)
   - Sanitize user input (strip, escape)
   - Add rate limiting per IP
   - Log validation failures

3. **Create Security Policy Schema** (`config/security_policy.yaml`)
   - Define YAML structure
   - Document all security settings
   - Add validation on load

**Files to Modify:**
- `interfaces/server.py` (CORS fix, validation middleware)
- `config/security_policy.yaml` (NEW - create from template)

**Deliverables:**
- ✅ CORS restricted to localhost + Tailscale
- ✅ Input validation middleware active
- ✅ Security policy schema defined

#### Day 2: Electron Audit + Security Policy

**Tasks:**

1. **Audit Electron exec() Calls** (`electron-app/src/main/main.js:662`)
   - Find all `exec()` calls
   - Review each for necessity and safety
   - Document findings
   - Add security comments where needed

2. **Complete Security Policy Configuration**
   - Finish `config/security_policy.yaml`
   - Add all capability settings
   - Add sandbox settings
   - Add audit logging settings

3. **Create Security Policy Loader** (`core/security_policy.py` - NEW)
   - Load and validate YAML
   - Provide typed access to settings
   - Cache loaded policy

**Files to Create:**
- `core/security_policy.py` (NEW)

**Files to Modify:**
- `electron-app/src/main/main.js` (audit exec calls)
- `config/security_policy.yaml` (complete configuration)

**Deliverables:**
- ✅ Electron exec() calls audited
- ✅ Security policy loader implemented
- ✅ Configuration validated

---

### Days 3-5: Pyodide Code Sandbox

**Goal:** Replace subprocess with sandboxed execution

#### Day 3: Pyodide Integration Setup

**Tasks:**

1. **Add Pyodide to Electron App**
   - Add CDN reference to `package.json` or `index.html`
   - Use Pyodide v0.24.1 (or latest stable)
   - Load Pyodide in renderer process
   - Test basic Python execution

2. **Create Pyodide Loader** (`electron-app/src/renderer/pyodide-loader.js` - NEW)
   ```javascript
   // Load Pyodide and initialize
   async function loadPyodide() {
     const pyodide = await loadPyodide({
       indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/"
     });
     return pyodide;
   }
   ```

3. **Create Pyodide Worker** (`electron-app/src/renderer/pyodide-worker.js` - NEW)
   - Web Worker for isolation
   - Load Pyodide in worker
   - Execute code with timeout
   - Return results via postMessage

**Files to Create:**
- `electron-app/src/renderer/pyodide-loader.js` (NEW)
- `electron-app/src/renderer/pyodide-worker.js` (NEW)

**Files to Modify:**
- `electron-app/src/renderer/index.html` (add Pyodide script)
- `package.json` (document Pyodide dependency)

**Deliverables:**
- ✅ Pyodide loaded in Electron app
- ✅ Worker created for isolation
- ✅ Basic execution test passing

#### Day 4: PyodideSandbox Class

**Tasks:**

1. **Create PyodideSandbox Class** (`core/sandbox.py` - NEW)
   ```python
   class PyodideSandbox:
       async def execute(self, code: str, timeout: int = 10) -> ExecutionResult:
           # Send code to renderer via IPC
           # Renderer executes in Pyodide worker
           # Return output
   ```
   - Implement timeout handling
   - Implement memory limits
   - Handle errors gracefully
   - Return structured results

2. **Create ExecutionResult Dataclass**
   - `status`: success | error | timeout
   - `output`: stdout text
   - `error`: error message (if any)
   - `execution_time`: seconds

3. **Add IPC Endpoints** (`interfaces/server.py`)
   - `POST /polly/sandbox/execute` - Execute code in Pyodide
   - Return execution results

**Files to Create:**
- `core/sandbox.py` (NEW)

**Files to Modify:**
- `interfaces/server.py` (add sandbox endpoint)

**Deliverables:**
- ✅ PyodideSandbox class implemented
- ✅ IPC endpoint working
- ✅ Timeout and memory limits enforced

#### Day 5: Replace Subprocess

**Tasks:**

1. **Replace subprocess.run() in Exercise Endpoint** (`interfaces/server.py:4992-5074`)
   ```python
   # BEFORE:
   result = subprocess.run([...])
   
   # AFTER:
   sandbox = PyodideSandbox()
   result = await sandbox.execute(code, timeout=10)
   ```

2. **Update Curriculum System** (`learners/curriculum_manager.py`)
   - Use PyodideSandbox for exercise execution
   - Remove subprocess dependencies
   - Test exercise execution

3. **Test Sandbox Isolation**
   - Verify no network access
   - Verify no filesystem access
   - Test timeout handling
   - Test memory limits

**Files to Modify:**
- `interfaces/server.py` (replace subprocess)
- `learners/curriculum_manager.py` (use sandbox)

**Deliverables:**
- ✅ Subprocess replaced with Pyodide
- ✅ Curriculum exercises working
- ✅ Sandbox isolation verified

---

### Days 6-7: Package Detection System

**Goal:** Detect package installations in generated code

#### Day 6: Package Detector

**Tasks:**

1. **Create PackageDetector Class** (`core/package_detector.py` - NEW)
   ```python
   class PackageDetector:
       def scan_code(self, code: str) -> List[PackageReference]:
           # Detect imports
           # Detect pip install suggestions
           # Check against allowlist
   ```
   - Parse `import` statements
   - Parse `from X import Y` statements
   - Detect `pip install` in comments/docstrings
   - Return list of unapproved packages

2. **Create PackageReference Dataclass**
   - `name`: package name
   - `source`: import | pip_install | comment
   - `line_number`: where found
   - `requires_approval`: bool

3. **Integrate with Allowlist** (`config/approved_packages.yaml`)
   - Load allowlist on init
   - Check packages against stdlib
   - Check packages against approved list
   - Return unapproved packages

**Files to Create:**
- `core/package_detector.py` (NEW)

**Files to Modify:**
- `config/approved_packages.yaml` (create initial allowlist)

**Deliverables:**
- ✅ Package detection working
- ✅ Allowlist integration complete
- ✅ Test with sample code

#### Day 7: Integration with Personas

**Tasks:**

1. **Integrate with Professor Persona** (`core/personas/implementations/professor.py`)
   - Scan generated code before returning
   - Detect unapproved packages
   - Trigger approval flow if needed
   - Block execution if packages denied

2. **Integrate with Architect Persona** (`core/personas/implementations/architect.py`)
   - Same package detection logic
   - Same approval flow

3. **Integrate with Curriculum System** (`learners/curriculum_manager.py`)
   - Scan exercise code before execution
   - Block execution if unapproved packages
   - Show approval dialog

4. **Create Package Metadata Fetcher** (`core/package_metadata.py` - NEW)
   - Fetch PyPI package info
   - Integrate Context7 trust scores
   - Cache metadata locally

**Files to Create:**
- `core/package_metadata.py` (NEW)

**Files to Modify:**
- `core/personas/implementations/professor.py` (add package detection)
- `core/personas/implementations/architect.py` (add package detection)
- `learners/curriculum_manager.py` (add package detection)

**Deliverables:**
- ✅ Package detection in all code generation paths
- ✅ Approval flow triggered
- ✅ Metadata fetching working

---

## Week 2: Capability Broker Architecture (Days 8-14)

### Days 8-10: Core Broker

**Goal:** Implement capability request/grant system

#### Day 8: Capability Types + Broker Foundation

**Tasks:**

1. **Define Capability Types** (`core/capabilities/types.py` - NEW)
   ```python
   class CapabilityType(Enum):
       PACKAGE_INSTALL = "package_install"
       SHELL_EXEC = "shell_exec"
       API_CALL = "api_call"
   ```

2. **Create CapabilityRequest Dataclass**
   - `capability_type`: CapabilityType
   - `requestor`: str (e.g., "polly-core", "professor-persona")
   - `resource`: str (e.g., package name, command)
   - `metadata`: Dict (additional info)

3. **Create CapabilityBroker Class** (`core/capability_broker.py` - NEW)
   - Initialize with security policy
   - Request/grant system
   - Policy validation

**Files to Create:**
- `core/capabilities/types.py` (NEW)
- `core/capability_broker.py` (NEW)

**Deliverables:**
- ✅ Capability types defined
- ✅ Broker foundation implemented

#### Day 9: Grant Management

**Tasks:**

1. **Create Grant Management** (`core/capabilities/grants.py` - NEW)
   - Grant storage (in-memory + file)
   - Grant expiration
   - Grant revocation
   - Grant lookup

2. **Implement Grant System**
   - `request_capability()` - Request a capability
   - `grant_capability()` - Grant a capability
   - `revoke_capability()` - Revoke a grant
   - `check_grant()` - Check if granted

3. **Add Policy Validation**
   - Check if capability enabled
   - Check if resource allowed
   - Check if approval required

**Files to Create:**
- `core/capabilities/grants.py` (NEW)

**Files to Modify:**
- `core/capability_broker.py` (add grant management)

**Deliverables:**
- ✅ Grant management working
- ✅ Policy validation active

#### Day 10: Audit Logging

**Tasks:**

1. **Create Audit Logger** (`core/audit_logger.py` - NEW)
   - SQLite database at `~/.polly/audit.db`
   - Log capability requests
   - Log grants and denials
   - Retention policy (90 days default)

2. **Implement Audit Schema**
   ```sql
   CREATE TABLE audit_log (
       id INTEGER PRIMARY KEY,
       timestamp TEXT,
       event_type TEXT,
       capability_type TEXT,
       requestor TEXT,
       resource TEXT,
       status TEXT,
       metadata TEXT
   );
   ```

3. **Integrate with Broker**
   - Log all requests
   - Log all grants
   - Log all denials
   - Query audit logs

**Files to Create:**
- `core/audit_logger.py` (NEW)

**Files to Modify:**
- `core/capability_broker.py` (add audit logging)

**Deliverables:**
- ✅ Audit logging operational
- ✅ Database schema created
- ✅ All events logged

---

### Days 11-12: Package Management Integration

**Goal:** Connect package detection to capability broker

#### Day 11: Allowlist + Approval UI

**Tasks:**

1. **Create Approved Packages Allowlist** (`config/approved_packages.yaml` - NEW)
   - Python stdlib list (always safe)
   - ~100 pre-approved packages
   - Context7 trust score integration
   - Blocked packages list

2. **Create Package Approval Dialog** (`electron-app/src/renderer/components/package-approval-dialog.js` - NEW)
   - Show package metadata (PyPI info)
   - Show Context7 trust score
   - Show package description
   - Approve/Deny/Block buttons
   - Remember choice option

3. **Add Approval Endpoints** (`interfaces/server.py`)
   - `POST /polly/security/package/approve`
   - `POST /polly/security/package/deny`
   - `GET /polly/security/package/metadata`

**Files to Create:**
- `config/approved_packages.yaml` (NEW)
- `electron-app/src/renderer/components/package-approval-dialog.js` (NEW)

**Files to Modify:**
- `interfaces/server.py` (add approval endpoints)

**Deliverables:**
- ✅ Allowlist created
- ✅ Approval UI functional
- ✅ Endpoints working

#### Day 12: Broker Integration

**Tasks:**

1. **Connect Package Detector to Broker**
   - Route package requests through broker
   - Check allowlist first
   - Request approval if needed
   - Cache approved packages

2. **Update Package Metadata Fetcher**
   - Fetch PyPI info
   - Fetch Context7 trust score
   - Show in approval dialog

3. **Test Full Workflow**
   - Generate code with unapproved package
   - Detect package
   - Show approval dialog
   - Approve/deny
   - Execute or block

**Files to Modify:**
- `core/package_detector.py` (integrate with broker)
- `core/package_metadata.py` (add Context7 integration)
- `electron-app/src/renderer/app.js` (show approval dialog)

**Deliverables:**
- ✅ Full workflow working
- ✅ Context7 integration complete
- ✅ Approved packages cached

---

### Days 13-14: Content Sanitizer

**Goal:** Detect prompt injection patterns in documents

#### Day 13: Content Sanitizer

**Tasks:**

1. **Create ContentSanitizer Class** (`core/content_sanitizer.py` - NEW)
   - Detect suspicious patterns
   - Separate "data" from "instructions"
   - Warn user when patterns found
   - Configurable sensitivity

2. **Define Suspicious Patterns** (`core/security/patterns.py` - NEW)
   - "Ignore previous instructions"
   - Role-playing patterns ("You are now...")
   - Base64/Unicode obfuscation
   - System/User role markers

3. **Implement Pattern Detection**
   - Regex patterns for each type
   - Score-based detection (low/medium/high)
   - Return warnings (not blocking)

**Files to Create:**
- `core/content_sanitizer.py` (NEW)
- `core/security/patterns.py` (NEW)

**Deliverables:**
- ✅ Content sanitizer implemented
- ✅ Pattern detection working

#### Day 14: RAG Integration

**Tasks:**

1. **Integrate with RAG System** (`core/rag.py`)
   - Sanitize content before passing to LLM
   - Add warnings to chat UI
   - Log suspicious content

2. **Add Warning UI** (`electron-app/src/renderer/app.js`)
   - Show warnings in chat
   - Allow user to dismiss
   - Show pattern details

3. **Make Configurable** (`config/security_policy.yaml`)
   - Sensitivity levels
   - Warn-only vs block mode
   - User can disable

**Files to Modify:**
- `core/rag.py` (add sanitization)
- `electron-app/src/renderer/app.js` (add warning UI)
- `config/security_policy.yaml` (add settings)

**Deliverables:**
- ✅ RAG integration complete
- ✅ Warnings shown to user
- ✅ Configurable settings

---

## Week 3: API Security + Polish (Days 15-21)

### Days 15-17: API Key Hardening

**Goal:** Secure API key handling with context managers

#### Day 15: Context Manager Support

**Tasks:**

1. **Enhance Secrets Manager** (`core/secrets_manager.py`)
   - Add `get_secret_for_request()` context manager
   - Secure memory cleanup after use
   - Clear keys from memory explicitly

2. **Implement Context Manager Pattern**
   ```python
   async with secrets_manager.get_secret_for_request('anthropic') as api_key:
       response = await make_api_call(api_key)
   # Key cleared here
   ```

3. **Add Memory Cleanup**
   - Overwrite key in memory
   - Force garbage collection
   - Verify cleanup

**Files to Modify:**
- `core/secrets_manager.py` (add context manager)

**Deliverables:**
- ✅ Context manager implemented
- ✅ Memory cleanup verified

#### Day 16: Update Provider Adapters

**Tasks:**

1. **Update All Provider Adapters**
   - `core/providers/anthropic_provider.py`
   - `core/providers/openai_provider.py`
   - `core/providers/github_provider.py`
   - `core/providers/grok_provider.py`
   - `core/providers/perplexity_provider.py`
   - `core/providers/gemini_provider.py`
   - `core/providers/mistral_provider.py`

2. **Replace Direct Key Access**
   ```python
   # BEFORE:
   api_key = secrets_manager.get_secret('anthropic')
   
   # AFTER:
   async with secrets_manager.get_secret_for_request('anthropic') as api_key:
       # Use key
   ```

3. **Test All Providers**
   - Verify each provider works
   - Verify keys cleaned up
   - Test error handling

**Files to Modify:**
- All files in `core/providers/`

**Deliverables:**
- ✅ All providers using secure pattern
- ✅ Keys cleaned up after use

#### Day 17: Key Rotation Helpers

**Tasks:**

1. **Add Key Rotation Helpers** (`core/secrets_manager.py`)
   - `rotate_key()` - Helper for key rotation
   - `check_key_age()` - Check when key was created
   - `remind_rotation()` - Remind user to rotate

2. **Add Rotation Reminders**
   - Check key age on startup
   - Show reminder if > 90 days
   - User can dismiss

3. **Test Rotation Workflow**
   - Test key rotation
   - Test reminders
   - Test cleanup

**Files to Modify:**
- `core/secrets_manager.py` (add rotation helpers)

**Deliverables:**
- ✅ Rotation helpers implemented
- ✅ Reminders working

---

### Days 18-19: PII Detection

**Goal:** Detect PII in content before cloud API calls

#### Day 18: PII Filter

**Tasks:**

1. **Create PIIFilter Class** (`core/pii_filter.py` - NEW)
   - Detect email addresses
   - Detect phone numbers
   - Detect SSNs
   - Detect credit card numbers
   - Detect API keys in content

2. **Define PII Patterns** (`core/security/pii_patterns.py` - NEW)
   - Regex patterns for each type
   - Configurable sensitivity
   - False positive handling

3. **Implement Detection**
   - Scan content for patterns
   - Return list of detected PII
   - Don't block (warn-only)

**Files to Create:**
- `core/pii_filter.py` (NEW)
- `core/security/pii_patterns.py` (NEW)

**Deliverables:**
- ✅ PII detection working
- ✅ Patterns defined

#### Day 19: Router Integration

**Tasks:**

1. **Integrate with Router** (`core/router_v2.py`)
   - Scan content before cloud API calls
   - Detect PII
   - Show warnings

2. **Add Warning UI** (`electron-app/src/renderer/app.js`)
   - Show PII warnings in chat
   - List detected PII types
   - Allow user to send anyway

3. **Make Opt-In** (`config/security_policy.yaml`)
   - User can disable warnings
   - Warn-only mode (no blocking)
   - Configurable patterns

**Files to Modify:**
- `core/router_v2.py` (add PII detection)
- `electron-app/src/renderer/app.js` (add warning UI)
- `config/security_policy.yaml` (add settings)

**Deliverables:**
- ✅ Router integration complete
- ✅ Warnings shown to user
- ✅ Opt-in configuration

---

### Days 20-21: Testing + Documentation

**Goal:** Comprehensive testing and user documentation

#### Day 20: Security Test Suite

**Tasks:**

1. **Create Security Test Suite** (`tests/test_security.py` - NEW)
   - Test Pyodide sandbox isolation
   - Test package detection
   - Test capability broker
   - Test prompt injection detection
   - Test PII detection

2. **Create Package Detection Tests** (`tests/test_package_detector.py` - NEW)
   - Test import detection
   - Test pip install detection
   - Test allowlist matching
   - Test edge cases

3. **Create Content Sanitizer Tests** (`tests/test_content_sanitizer.py` - NEW)
   - Test pattern detection
   - Test warning generation
   - Test sensitivity levels

4. **Run All Tests**
   - Fix any failures
   - Achieve 100% test coverage for security features

**Files to Create:**
- `tests/test_security.py` (NEW)
- `tests/test_package_detector.py` (NEW)
- `tests/test_content_sanitizer.py` (NEW)

**Deliverables:**
- ✅ Comprehensive test suite passing
- ✅ All edge cases covered

#### Day 21: Documentation

**Tasks:**

1. **Create SECURITY.md User Guide** (`docs/SECURITY.md` - NEW)
   - How security features work
   - Configuration options
   - Approval workflows
   - Best practices
   - Troubleshooting

2. **Create Phase Completion Report** (`PHASE23.5_COMPLETE.md` - NEW)
   - Implementation summary
   - Success criteria verification
   - Files created/modified
   - Metrics and statistics

3. **Update Roadmap Documents**
   - Update `docs/status/CURRENT.md`
   - Update `docs/planning/README.md`
   - Update `MASTER_ROADMAP.md` (if exists)

**Files to Create:**
- `docs/SECURITY.md` (NEW)
- `PHASE23.5_COMPLETE.md` (NEW)

**Files to Modify:**
- `docs/status/CURRENT.md`
- `docs/planning/README.md`

**Deliverables:**
- ✅ User documentation complete
- ✅ Phase completion report
- ✅ Roadmap updated

---

## Implementation Checklist

### Week 1: Foundation + Pyodide Sandbox
- [ ] Day 1: Fix CORS policy
- [ ] Day 1: Add input validation middleware
- [ ] Day 2: Audit Electron exec() calls
- [ ] Day 2: Create security policy schema
- [ ] Day 3: Integrate Pyodide into Electron app
- [ ] Day 3: Create Pyodide worker
- [ ] Day 4: Create PyodideSandbox class
- [ ] Day 4: Add IPC endpoints
- [ ] Day 5: Replace subprocess in exercise endpoint
- [ ] Day 5: Update curriculum system
- [ ] Day 6: Create PackageDetector class
- [ ] Day 6: Create allowlist
- [ ] Day 7: Integrate with Professor persona
- [ ] Day 7: Integrate with Architect persona
- [ ] Day 7: Create package metadata fetcher

### Week 2: Capability Broker Architecture
- [ ] Day 8: Define capability types
- [ ] Day 8: Create CapabilityBroker class
- [ ] Day 9: Implement grant management
- [ ] Day 9: Add policy validation
- [ ] Day 10: Create audit logging system
- [ ] Day 10: Integrate with broker
- [ ] Day 11: Create approved packages allowlist
- [ ] Day 11: Create package approval dialog UI
- [ ] Day 11: Add approval endpoints
- [ ] Day 12: Connect package detector to broker
- [ ] Day 12: Update package metadata fetcher
- [ ] Day 13: Create ContentSanitizer class
- [ ] Day 13: Define suspicious patterns
- [ ] Day 14: Integrate with RAG system
- [ ] Day 14: Add warning UI

### Week 3: API Security + Polish
- [ ] Day 15: Enhance secrets manager with context manager
- [ ] Day 15: Add memory cleanup
- [ ] Day 16: Update all provider adapters
- [ ] Day 16: Test all providers
- [ ] Day 17: Add key rotation helpers
- [ ] Day 18: Create PIIFilter class
- [ ] Day 18: Define PII patterns
- [ ] Day 19: Integrate with router
- [ ] Day 19: Add PII warning UI
- [ ] Day 20: Create security test suite
- [ ] Day 20: Create package detection tests
- [ ] Day 20: Create content sanitizer tests
- [ ] Day 21: Create SECURITY.md user guide
- [ ] Day 21: Create phase completion report
- [ ] Day 21: Update roadmap documents

---

## Success Criteria Verification

Before marking Phase 23.5 complete, verify all success criteria:

### Code Execution Sandboxed
- [ ] Pyodide integrated and working
- [ ] No subprocess.run() for untrusted code
- [ ] Curriculum exercises running in sandbox
- [ ] Timeout and memory limits enforced
- [ ] No network or filesystem access from sandbox

### Package Management Secure
- [ ] Allowlist active with ~100 approved packages
- [ ] Package detection working in generated code
- [ ] Approval dialog functional
- [ ] User can approve/deny/block packages
- [ ] Context7 trust scores shown in approval dialog
- [ ] Approved packages cached to user config

### Capability Broker Operational
- [ ] All high-risk operations route through broker
- [ ] Audit logging captures all security events
- [ ] Policy enforcement working
- [ ] Grant management functional
- [ ] Audit database at `~/.polly/audit.db`

### Content Security Active
- [ ] Prompt injection detection working
- [ ] Suspicious content warnings shown
- [ ] PII detection active (warn-only mode)
- [ ] Configurable sensitivity levels
- [ ] Integration with RAG system

### API Keys Secure
- [ ] Context managers implemented
- [ ] All providers using secure pattern
- [ ] Memory cleanup verified
- [ ] Key rotation helpers added

### Testing Complete
- [ ] Security test suite passing
- [ ] Prompt injection scenarios tested
- [ ] Package detection edge cases covered
- [ ] Sandbox isolation verified
- [ ] Capability broker tested

### Documentation Complete
- [ ] SECURITY.md user guide written
- [ ] Phase completion report created
- [ ] Roadmap updated
- [ ] Configuration files documented

---

## Notes

- **Flexibility:** This plan is a guide. Adjust timeline as needed based on complexity.
- **Testing:** Write tests as you implement, don't wait until Day 20.
- **Documentation:** Document design decisions as you make them.
- **Integration:** Test integrations early and often.

---

**Last Updated:** February 3, 2026  
**Status:** Ready for Implementation
