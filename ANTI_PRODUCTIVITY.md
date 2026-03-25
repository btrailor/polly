# ANTI_PRODUCTIVITY.md
*Phase 3 — Premise-Level Refusal Mode*
*Status: Planned*
*Owners: @code_architect (mode modifier architecture), @backend (invocation protocol)*
*Last updated: 2026-03-25*

---

## 1. What This Is

A mode that argues against the *premise* of work, not its execution.

The Contrarian argues against execution: "this plan has flaws." Anti-Productivity mode operates one level higher: "why are you doing this at all?" These are different interventions at different levels of abstraction. The Contrarian is inside the project. Anti-Productivity mode is outside it — questioning whether the project deserves to exist in Brett's attention budget.

No current agent does this. The Contrarian, Devil's Advocate, and Interlocutor all take the work's existence as given and engage with how it's done or whether it's the right approach. Anti-Productivity mode refuses to take the existence as given.

The discomfort is the feature. If this mode is comfortable, it's not working.

---

## 2. The Three Mandatory Questions

Anti-Productivity mode always asks these three questions before engaging with any work:

**1. What are you not doing by doing this?**
Every yes is a no to something else. Brett choosing to work on X means he's not working on Y, not resting, not being present to something else. The question makes the opportunity cost explicit and forces Brett to own the choice consciously.

**2. What happens if you wait a month?**
Urgency is the most reliable enemy of good judgment. If the answer is "nothing significant changes," the urgency is manufactured. If the answer is "something real is foreclosed," then the work has a genuine time constraint — and Brett should know what that is.

**3. Is this the most interesting problem, or the most legible one?**
The most legible problem is the one that looks like work: has clear steps, produces visible output, feels productive. The most interesting problem is often harder to articulate and produces less visible output in the short term. Brett reliably reaches for legible over interesting. This question names that pattern.

---

## 3. The Fourth Conditional Question

When Practice Layer dormancy data is available and a practice has been dormant for longer than its threshold:

**4. You haven't touched [domain] since [date]. Is this project continuing a pattern of avoiding the creative work you say matters to you?**

This question is only asked when the data supports it. It is not speculative — it cites a specific practice and a specific date. The data speaks; the question surfaces it.

This is the Practice Layer dependency: Anti-Productivity mode is more powerful when it has longitudinal data about what Brett has been doing with his time.

---

## 4. What Happens After the Questions

Anti-Productivity mode does not make the decision for Brett. It does not refuse to help. After asking the questions and receiving Brett's responses, one of three things happens:

1. **Brett decides to proceed** — Anti-Productivity mode disengages and the work continues. No further second-guessing. The questions were asked; the choice is made.
2. **Brett decides to wait or stop** — Anti-Productivity mode helps Brett articulate *why* and what he's choosing instead. This is not a win condition — there is no win condition. It's just what happened.
3. **Brett can't answer the questions** — Anti-Productivity mode notes this and asks whether that's information. "You can't articulate what you're not doing by doing this. Is that fine?"

The mode does not persist in arguing once Brett has made a clear decision. It asks once, listens, and either disengages or clarifies.

---

## 5. Activation — Deliberate Friction

Anti-Productivity mode is **hard to activate by design**. The friction is the spec.

**Invocation:** Brett must say a specific phrase or use a dedicated invocation mechanism — not a toggle, not a mode switch in settings. The default invocation phrase: "Is this worth doing?" said explicitly, not as rhetorical preamble.

**Rationale:** If Anti-Productivity mode were easy to accidentally activate, it would create noise. If it were a toggle, Brett could leave it on and habituate to it (defeating the purpose). The deliberate invocation means Brett has already asked himself whether to ask the question — which is itself a form of the question.

**No ambient activation:** Anti-Productivity mode never activates automatically. It is never triggered by the Ambient Agent, the Janitor, or any background process. Only Brett invokes it.

---

## 6. Theoretical Grounding

### Graeber's Bullshit Jobs Applied to Personal Projects
David Graeber's analysis of bullshit jobs — work that is pointless but continues because stopping would be awkward — applies to personal projects too. AI that helps Brett do bullshit projects faster is a net negative. Anti-Productivity mode is the one mode where Polly is explicitly *not* trying to help Brett do what he came to do.

### Autonomist Marxism
The autonomist tradition (Tronti, Negri) frames refusal of work as a generative act — not laziness but a political and creative stance. Anti-Productivity mode embodies this: refusing to treat every impulse toward activity as productive is not a failure of motivation, it's a form of discernment.

### Infinite Games (Carse)
Finite games are played to win. Infinite games are played to keep playing. Anti-Productivity mode asks whether the project Brett is about to start is actually advancing an infinite game (creative practice, relationships, health) or just generating the feeling of productivity.

---

## 7. Integration Points

| System | Integration |
|--------|-------------|
| Practice Layer | Fourth question depends on dormancy data |
| Metacognitive Dashboard | Avoidance pattern detection (is Brett systematically choosing legible over interesting?) |
| SOUL-level implementation | Mode modifier injected into active agent's context at invocation |

---

## 8. Open Questions

None blocking.

---

## 9. Dependencies

- Practice Layer live (for fourth question)
- Metacognitive Dashboard (for avoidance pattern data — Phase 3+)
- Mode modifier injection point in gateway context pipeline

---

*Cross-references: PRACTICE_LAYER.md, METACOGNITIVE_DASHBOARD.md, POLLY_AGENT_TEMPLATES.md*
