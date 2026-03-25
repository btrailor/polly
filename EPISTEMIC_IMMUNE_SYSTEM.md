# EPISTEMIC_IMMUNE_SYSTEM.md
*Phase 3 — Adaptive Constitutional Layer*
*Status: Planned*
*Owners: @code_architect (pattern library architecture), @backend (constitutional layer injection point)*
*Last updated: 2026-03-25*

---

## 1. What This Is

An adaptive constitutional layer — not what Polly believes (fixed principles), but *what it notices* (learned pattern recognition).

The standard constitutional layer injects fixed epistemic principles into every session: "consider cui bono," "check for second-order effects," etc. These are good principles but they're static. They don't know that Brett specifically tends to accept arguments from authority when the authority is adjacent to a domain he respects, or that urgency framing reliably bypasses his critical faculties in certain contexts.

The Epistemic Immune System learns Brett's specific rhetorical vulnerabilities and builds a pattern library from them. When a new argument matches a known pattern:

> "This has the same structure as the argument from February that you accepted without examining the funding source — the Contrarian later pointed out you'd missed a significant conflict of interest."

Biological metaphor is precise: not a firewall (blocks everything indiscriminately), not a whitelist (approves everything from trusted sources), but an immune response — targeted, pattern-specific, learned from prior exposure.

---

## 2. Why This Is Only Possible Here

Three prerequisites converge in Polly that exist nowhere else simultaneously:

1. **Longitudinal memory** — Polly remembers the argument from February. Most AI systems don't have cross-session memory.
2. **Epistemological framework** — Polly has the Contrarian, the constitutional layer, the CL4R1T4S pattern vocabulary. It can recognize rhetorical patterns, not just content.
3. **Self-hosted privacy guarantee** — A map of Brett's rhetorical vulnerabilities is among the most sensitive data the system holds. It must never leave his hardware. Privacy here is not just a protection — it is a prerequisite. This feature cannot exist on a cloud platform with production-grade ethics.

---

## 3. The Pattern Library

### 3.1 Structure

Each entry in the pattern library:

```json
{
  "id": "authority-adjacency-001",
  "pattern_name": "Appeal to Adjacent Authority",
  "description": "An authority in field A is cited to support a claim in adjacent field B, where their credentials don't transfer.",
  "rhetorical_structure": "X is an expert in [adjacent domain]. X believes Y. Therefore Y.",
  "emotional_register": "credibility_transfer",
  "domain_patterns": ["technology", "economics", "design"],
  "historical_instances": [
    {
      "date": "2026-02-14",
      "summary": "Accepted a claim about programming language design based on authority of a hardware engineer",
      "contrarian_correction": "The Contrarian noted the credentials didn't transfer — hardware and language design are distinct domains",
      "outcome": "position_revised"
    }
  ],
  "source": "CL4R1T4S",
  "confidence": 0.82
}
```

### 3.2 Starting Vocabulary

The CL4R1T4S research (`CL4R1T4S_RESEARCH.md`) provides the starting vocabulary. Initial pattern library seeded from:

- Appeal to authority
- Urgency injection ("you must decide now")
- Flattery ("you clearly understand this better than most")
- False dichotomy
- Overton window manipulation
- Manufactured consensus
- Emotional leverage (fear, pride, identity threat)
- Complexity weaponization (making the simple seem incomprehensible to discourage scrutiny)

These are not Brett-specific — they're the general rhetorical pattern vocabulary. The system learns which of these Brett is *specifically* susceptible to, in which *domains*, at which *emotional registers*.

### 3.3 Library Growth

The library grows from Contrarian session outcomes:

1. The Contrarian successfully challenges an argument Brett had accepted
2. A lightweight extraction pass identifies the rhetorical structure of the challenged argument
3. If the structure matches a known pattern → confidence score increases, historical instance added
4. If the structure is novel → candidate new pattern flagged for review (Brett approves addition)

Brett approves new pattern additions. The system doesn't silently expand its model of his vulnerabilities without his knowledge.

---

## 4. Runtime Behavior

### 4.1 Flags for Examination, Never Blocks

The Epistemic Immune System **flags for examination, never blocks**. It does not prevent Brett from accepting an argument. It does not argue against the argument. It surfaces a pattern recognition observation and lets Brett decide what to do with it.

> "This argument uses urgency framing — 'you need to decide this week.' That pattern has appeared in 3 previous arguments you later revised. Worth pausing on."

Brett may respond: "I know, but the urgency is real in this case." Fine. The flag is logged. The system does not persist in arguing.

### 4.2 Legibility Requirement

Every flag must show:
1. **Which pattern was recognized** — by name, not just "I noticed something"
2. **What in the current argument triggered it** — the specific phrase, structure, or register
3. **Historical grounding** — at least one prior instance where this pattern appeared and what happened

A flag that says "this seems manipulative" is not acceptable. A flag that says "this uses the appeal-to-adjacent-authority structure (pattern #003) — specifically, citing [X]'s work in [domain A] to support a claim in [domain B]. In February you accepted a similar argument; the Contrarian later noted the credentials didn't transfer" is acceptable.

Legibility is non-negotiable. Brett must be able to evaluate whether the pattern recognition is correct, not just whether to heed the warning.

### 4.3 Injection Point

The Epistemic Immune System runs as an extension of the constitutional layer injection point. It is not a separate agent — it is a layer in the existing gateway context injection pipeline.

**Trigger condition:** A pattern match above a confidence threshold (default: 0.7) during an active session where the constitutional layer is running.

**Injection format:**
```
[epistemic flag: Appeal to Adjacent Authority (confidence: 0.82) — "[quoted text]" cites [X]'s authority in [domain A] to support a claim in [domain B]. Prior instance: 2026-02-14, outcome: position revised after Contrarian review. Flag for examination.]
```

Injected ahead of the agent's next response, visible to the agent but not as a directive — the agent decides whether and how to surface it to Brett.

---

## 5. Privacy Architecture

The pattern library is among the most sensitive data in the system:

- Never leaves the gateway
- Not included in the standard export package by default (opt-in for COGNITIVE_ARTIFACT.md export)
- If included in export: encrypted layer, separate key
- Explicitly deletable, per-pattern and in bulk
- Brett can inspect the full library at any time

**Device seizure threat model:** A map of someone's rhetorical vulnerabilities is potentially usable for manipulation, not just by adversaries but by any party with access to the device. In Lockdown Mode, the pattern library is encrypted with the same key as session files. @security_audit to specify key management when writing LOCKDOWN_MODE.md.

---

## 6. Relationship to CL4R1T4S

`CL4R1T4S_RESEARCH.md` (complete, at `~/polly/CL4R1T4S_RESEARCH.md`) is the starting vocabulary for the pattern library. The research identified:

- Rhetorical patterns (appeal to authority, urgency injection, flattery, false dichotomy)
- The structural signatures that identify each pattern
- How patterns interact and compound

The Epistemic Immune System operationalizes this research: it takes the CL4R1T4S pattern vocabulary and makes it adaptive — tuned to Brett's specific history rather than applying uniformly to all users.

---

## 7. Open Questions

None blocking.

**Deferred:**
- **Q1:** Confidence threshold tuning — 0.7 is a starting point. Needs calibration against false positive rate in practice. Too sensitive = noise; too quiet = misses. User-tunable.
- **Q2:** Pattern decay — should old instances lose weight over time? An argument Brett was vulnerable to in 2026 may not be one he's vulnerable to in 2029. Time-weighted confidence scoring is Phase 3+.

---

## 8. Dependencies

- Constitutional layer live and injectable (@backend)
- Contrarian agent active (source of correction outcomes)
- Knowledge Skill corpus (for historical instance storage and retrieval)
- `CL4R1T4S_RESEARCH.md` complete ✅
- LOCKDOWN_MODE.md: must specify key management for pattern library encryption

---

*Cross-references: CL4R1T4S_RESEARCH.md, POLLY_AGENT_TEMPLATES.md (Contrarian), COGNITIVE_ARTIFACT.md, LOCKDOWN_MODE.md*
