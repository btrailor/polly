# PROJECT_STATUS.md

Living project status doc. @code_architect writes and maintains. All agents read-only.  
Last updated: 2026-03-25 (commit `ba28f6c` → agent templates updated post-commit)  
Branch: `development`

---

## Current State

### Phase 1 — iOS Foundation
**Status:** 🔨 Spec complete. Implementation not started.

The iOS app is a scaffold: ~450 lines TypeScript total. `chat.tsx` (216 lines) is the most substantive file. Gateway is not wired. `isConfigured` is hardcoded to `false`. Nothing functional ships until Phase 1 is implemented.

**10 missing npm packages** (must install before any Phase 1 feature work begins):
```
expo-secure-store
react-native-mmkv
zustand
@shopify/flash-list
react-native-markdown-display
lucide-react-native
expo-keep-awake
expo-audio
expo-document-picker
```
Plus the gateway client library (to be confirmed with @backend).

**Known violations in current scaffold:**
- `polly-ios/app/(main)/chat.tsx` line 269: `🎤` emoji must be replaced with Lucide `Mic` icon per §18.3 — **not yet fixed**
- `polly-ios/src/colors.ts`: duplicate file — superseded by theme system; **must be deleted** before sensibility work starts
- `isConfigured` hardcoded `false` in app bootstrap — gateway never wired

### Agent System
**Status:** 🔨 Spec complete. Not yet running.

- **43 agent templates:** all complete with full SOUL text + Prosodic Sensitivity
- **8 were stub-marked in summary (incorrect):** Mirror, Interlocutor, Experimentalist, Translator, Librarian, Scaffolder, Estimator, Janitor — all have complete SOULs; the "stub" label was stale
- **`autonomy_level` per-agent:** ✅ reference table added 2026-03-25 (this session)
- **`allowed_modes` per-agent:** ✅ reference table added 2026-03-25 (this session)
- **SOUL Baseline:** 6 blocks: Session Startup, Context Management, Blockers & Honesty, Memory Writes, Epistemological Commitments, Tool Use
- **Domain Boundary Protocol:** ✅ added to SOUL Baseline footer 2026-03-25 (this session)
- **Vault Write-Back protocol:** ✅ in SOUL Baseline (Phase 3 tool activation)
- **`behavioral_contract_version`:** target 1.0 at Phase 3 per `AGENT_BEHAVIOR_CONTRACT.md §10`

---

## Spec Status

| Spec | Status | Notes |
|------|--------|-------|
| `POLLY_IOS_SPEC.md` | ✅ Authoritative | Full iOS feature spec — canonical source |
| `POLLY_AGENT_TEMPLATES.md` | ✅ Authoritative | 43 agent templates; per-agent manifest table added 2026-03-25 |
| `KNOWLEDGE_SKILL.md` | ✅ Written | Tool signatures, graph layer, conversation adapter, index_hooks, degradation paths |
| `KNOWLEDGE_SERVICE_CONTRACTS.md` | ✅ Written | 5 tool contracts; §4 EIS freshness model pending @backend review |
| `KNOWLEDGE_WRITE_PATH.md` | ✅ Written | 7 write paths, dedup thresholds, vault write-back protocol |
| `ONBOARDING_SPEC.md` | ✅ Written | 11-phase OnboardingState machine, MMKV persisted, crash-resumable |
| `MODEL_ROUTING_SPEC.md` | ✅ Written | 5 evaluators, 3 insertion options, all @backend questions answered |
| `SWARM_COORDINATION_SPEC.md` | ✅ Written | All §8 gateway questions answered and locked |
| `SENSIBILITY_SYSTEM_SPEC.md` | ✅ Written | Two-axis architecture; Reas default; 7 theme files Phase 1 |
| `SECURITY_IMPLEMENTATION_SPEC.md` | ✅ Written | 50-item checklist, §7.10/§8.3 resolved, SECURE_STORE_KEYS (8 keys) |
| `TESTING_AND_QA_SPEC.md` | ✅ Written | 55 test cases, LLM grading framework, CI workflow |
| `AGENT_BEHAVIOR_CONTRACT.md` | ✅ Written | Tool surface by phase, autonomy levels, group chat behavioral contract, Ambient Agent spec |
| `PHASE_2_GAP_ANALYSIS.md` | ✅ Written | 4 boundary conflicts resolved, 10 missing changes identified |
| `PHASE_3_GAP_ANALYSIS.md` | ✅ Written | 3A/3B/3C/3D split, 7 missing changes identified, @backend Wave 4 tasks |
| `SOMATIC_INTERFACE.md` | 📋 Specced | Phase 2 — prosodic engagement signal layer |
| `GESTURE_LAYER.md` | 📋 Planned | Phase 2–3 — vocal gesture system (added 2026-03-30) |
| `AGENT_BUILDER.md` | 📋 Planned | Phase 2–3 — custom agent creation (added 2026-03-30) |
| `WARD.md` | 📋 Planned | Phase 2–4 — universal entry point + Liaison extension (added 2026-03-30) |
| `VOICE_INTERACTION.md` | 🔨 In progress | Phase 1 voice requirements |
| `COPY_VOICE.md` | 🔨 In progress | Voice design tokens + copy patterns |
| `VOICE_BEHAVIOR_TESTS.md` | 🔨 In progress | QA test suite for voice |
| `FIGMA_INTEGRATION.md` | 📋 Planned | Phase 2 |
| `LOCKDOWN_MODE.md` | 📋 Planned | Phase 2 |
| `DREAM_LOGIC.md` | 📋 Planned | Phase 3B |
| `KNOWLEDGE_SKILL.md` | 📋 Planned | Phase 2 |
| `COGNITIVE_ARTIFACT.md` | 📋 Planned | Phase 3D |
| `ORAL_HISTORY.md` | ✅ Written | Post-mortem format spec complete |
| `TEMPORAL_INTELLIGENCE.md` | 📋 Planned | Phase 3B |
| `METACOGNITIVE_DASHBOARD.md` | 📋 Planned | Phase 3B |
| `STRUCTURAL_ANALOGY.md` | 📋 Planned | Phase 3B |
| `CREATIVE_CONSTRAINT_ENGINE.md` | 📋 Planned | Phase 3C |
| `EPISTEMIC_IMMUNE_SYSTEM.md` | 📋 Planned | Phase 3B |
| `PRACTICE_LAYER.md` | 📋 Planned | Phase 3B |
| `CONVERSATION_ARCHITECTURE.md` | 📋 Planned | Phase 3C |
| `CHORUS_MODE.md` | 📋 Planned | Phase 4 |
| `ANTI_PRODUCTIVITY.md` | 📋 Planned | Phase 3 |
| `CREATIVE_CODE_SKILL.md` | 📋 Planned | Phase 3C — 6-task gate chain required |
| `SKILLS_MARKETPLACE.md` | 📋 Planned | Phase 2 |
| `MCP_ADAPTER.md` | 📋 Planned | Phase 2 |
| `DISTRIBUTED_NODES.md` | 📋 Planned | Phase 3 |
| `TREE_OF_THOUGHTS.md` | 📋 Planned | Phase 3B — @design_eng mobile UI review required first |

---

## OpenSpec Roadmap

35 changes total. See `openspec/ROADMAP.md` for the full table.

| Group | Changes | Status |
|-------|---------|--------|
| Phase 1 | #1 ios-foundation, #2 agent-system, #3 testing-infrastructure | 🔨 Spec complete, impl not started |
| Phase 2 | #4–#22 (19 changes, incl. gateway-changes) | 📋 Specced |
| Phase 3A | #23–#26 | 📋 Specced |
| Phase 3B | #27 cognitive-features | 📋 Specced |
| Phase 3C | #28–#29 | 📋 Specced |
| Phase 3D | #30–#34 | 📋 Specced |
| Phase 4 | #35 federation | 💡 Future |

**Critical path:** Phase 1 → `phase-2-push-security` (wave 0, pre-prod gate) → `phase-2-knowledge-skill` → Phase 3A → Phase 3B → Phase 3C/3D

---

## Git State

| Commit | Description |
|--------|-------------|
| `ba28f6c` | Creative Code Skill: lock sandbox audit write failure behavior and alert path |
| `9c76b71` | Creative Code Skill: full 6-task dependency chain with named deliverables |
| `b6e0bc8` | Creative Code Skill: sandbox audit failure table locked |
| `ccc8876` | Apply PHASE_3_GAP_ANALYSIS: 7 new Phase 3 change dirs, ROADMAP 28→35 |
| `f23084a` | Apply PHASE_2_GAP_ANALYSIS: 10 new Phase 2 change dirs, ROADMAP 18→28 |
| `46edc73` | Four housekeeping fixes (chat.tsx, setup.sh.md, agent-system spec, ToT tasks) |
| `e1e12b8` | Apply AGENT_BEHAVIOR_CONTRACT |
| `0989ac9` | Apply TESTING_AND_QA_SPEC |
| `0bc78c9` | Apply SECURITY_IMPLEMENTATION_SPEC |
| `3584ded` | Apply SENSIBILITY_SYSTEM_SPEC |

---

## Open Blockers

| Blocker | Owner | Blocks |
|---------|-------|--------|
| `KNOWLEDGE_SERVICE_CONTRACTS.md §4` — EIS flags freshness (session vs request scoped) | @backend | EIS implementation |
| `phase-2-gateway-changes` blocking relationships sanity-check | @backend | Phase 2 sequencing confidence |
| `knowledge_conversation_history` JSONL schema | @backend | @qa_guy fixture generator |
| Gateway conversation history — net-new or existing serialization? | @backend | Fixture generator design |
| `infra-observability-spec` — 4 signal schemas, metric counters, health surface | @infra | `qa-containment-validation-plan` |
| `security-design-doc` — Creative Code Skill sandbox (failure modes, capability scope, audit log spec, violation routing) | @security_audit | `infra-observability-spec` (failure mode enumeration) + entire Creative Code Skill gate chain |
| Creative Code Skill implementation | @backend | `security-design-doc` → `security-review-signoff` → `infra-observability-spec` → `qa-containment-validation-plan` — all must close first |
| Tree of Thoughts mobile UI design spec | @design_eng | Phase 3B ToT implementation |
| `test-eis-smoke-plan` | @qa_guy | Phase 3A EIS readiness gate |
| Gesture embedding model decision (`GESTURE_LAYER.md` §12 Q2) | @backend | Phase 2 gesture recognizer implementation |
| Ward context assembly design proposal | @backend | Phase 2 Ward routing implementation |

---

## Open Questions — Pending Brett's Decision

These questions must not be resolved unilaterally. Flag here, wait for Brett's input.

| Question | Spec | What's at stake |
|----------|------|-----------------|
| Ward conversation persistence — do Ward ambient interactions create conversation threads? | `WARD.md` §11 Q1 | @backend session model design. Spec recommends no — validate against gateway session model before implementing. |
| Gesture chaining — do gestures trigger sequences of behaviors? | `GESTURE_LAYER.md` §12 Q1 | Phase 3 gesture data model design. Do not implement assumptions. |
| Agent + gesture sharing between Polly users — should the data model support this now? | `AGENT_BUILDER.md` §9 Q1 | Data model design decision. Easier to add now than retrofit. |

---

## Pending (Code Architect)

- [ ] `SPEC_INDEX.md` update — 11 new specs not yet indexed (plus 3 new: GESTURE_LAYER, AGENT_BUILDER, WARD added 2026-03-30)
- [ ] Phase 1 iOS implementation — install 10 missing packages, wire gateway, onboarding, state mgmt, DrawerPanel, msg list, audio, vault capture, mental models, group chat, all screen stubs
- [ ] Lockdown Mode Phase 1 architectural hooks — @frontend + @backend agreement needed
- [ ] **@backend Phase 1 hook (IMMEDIATE):** Add gesture candidate log to gateway message processing pipeline — short utterances (≤ 8 words) with no gesture match logged to `gesture_candidate_log`. See `PHASE_2_GAP_ANALYSIS.md` §6 and `GESTURE_LAYER.md` §14. Flag here when complete.
