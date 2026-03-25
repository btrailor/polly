# TREE_OF_THOUGHTS.md
*Phase 3 — Activatable Reasoning Mode*
*Status: Planned*
*Owners: @backend (ToT orchestration, plan-space search), @code_architect (mode integration)*
*Last updated: 2026-03-25*

---

## 1. What This Is

Tree of Thoughts (ToT) as an activatable reasoning mode — a structured multi-path exploration of a problem space before converging on a response.

Standard chain-of-thought (CoT) reasoning is linear: one thought follows another. ToT branches: multiple reasoning paths are explored simultaneously, evaluated against each other, and the best path is selected. For certain problem types — those with a large solution space and no obvious path — ToT produces significantly better outcomes than linear reasoning.

**Reference:** Yao et al. (2023), "Tree of Thoughts: Deliberate Problem Solving with Large Language Models." Implementation reference: https://github.com/kyegomez/tree-of-thoughts

---

## 2. When ToT Is Appropriate

ToT is computationally expensive. It is not the default reasoning mode. It is activated explicitly or by agent judgment for problem types that benefit from it.

**Problem types where ToT adds value:**
- Goal decomposition (breaking a large goal into sub-goals requires exploring multiple decomposition strategies)
- Plan-space search (finding a path from current state to goal when multiple paths exist)
- Creative generation (exploring multiple framings before selecting one)
- Debugging/diagnosis (multiple hypotheses about root cause, each requiring exploration)

**Problem types where ToT adds no value:**
- Factual recall
- Simple Q&A
- Tasks with a clearly correct answer

**Activation:** Explicit via `[think carefully]` or `[explore this]` phrasing, or implicit via agent judgment when the agent identifies the problem type as a good ToT candidate.

---

## 3. Integration Points

### 3.1 §11 Mental Models

ToT is the implementation substrate for the §11 mental models library. When Brett invokes a mental model (e.g., "think about this using inversion"), ToT structures the exploration:

1. **Generate branches** — multiple applications of the mental model
2. **Evaluate branches** — which application is most illuminating?
3. **Select and develop** — deepen the best branch

This is composable: "think about this using inversion and second-order effects" generates branches for each model, then finds the intersection.

### 3.2 Plan-Space Search

For planning tasks, ToT generates multiple plan candidates, evaluates them against explicit criteria (time, resources, risk), and selects the Pareto-optimal candidate. This is the Estimator's natural territory — the Estimator can participate in plan evaluation branches.

### 3.3 Conversation Architecture Integration

ToT can be invoked as a single-agent reasoning mode inside a Conversation Architecture topology. The Diverge-Converge topology is a multi-agent approximation of ToT; ToT is the single-agent equivalent.

---

## 4. Implementation Architecture

### 4.1 Gateway-Side Orchestration

ToT runs at the gateway, not the client. The client sees the final selected response, not the branch exploration. The exploration is available in a "reasoning trace" view if Brett wants to inspect it.

### 4.2 Branch Depth and Width

Configurable per invocation, with defaults:
- **Width (b):** Number of branches per level — default 3
- **Depth (d):** Number of levels — default 2
- **Total calls:** b^d — default 9 (3 branches × 2 levels × 1 evaluation call)

9 LLM calls per ToT invocation at default settings. This is the computational cost Brett accepts when invoking ToT. For expensive problems, worth it. Not appropriate as a default.

### 4.3 Evaluation Heuristic

At each branch point, branches are evaluated by a lightweight evaluation prompt:

```
Given the problem: [problem]
And these candidate reasoning paths: [branches]
Which path is most promising and why? Score each 1-5.
```

The highest-scoring branch is selected for the next level.

---

## 5. Open Questions

None blocking.

**Deferred:**
- **Q1:** User-visible reasoning trace — should Brett be able to see the branch exploration? Opt-in, available on tap. Not surfaced by default (noisy).
- **Q2:** ToT + Knowledge Skill — can ToT branches query `knowledge_search` mid-exploration? Yes in principle; implementation complexity TBD.

---

## 6. Dependencies

- Gateway LLM capable of structured prompting
- §11 mental models library defined in POLLY_IOS_SPEC.md
- CONVERSATION_ARCHITECTURE.md (composable with Diverge-Converge topology)

**Reference:**
- Yao, S., et al. (2023). Tree of Thoughts: Deliberate Problem Solving with Large Language Models. *arXiv:2305.10601*.

---

*Cross-references: POLLY_IOS_SPEC.md §11, CONVERSATION_ARCHITECTURE.md, POLLY_AGENT_TEMPLATES.md (Estimator)*
