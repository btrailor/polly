# Research Queue

**Last Updated:** February 4, 2026  
**Purpose:** Track tools, services, and technologies to research for Polly development

---

## Active Research (High Priority)

### 1. SummonAI Kit
**Related Phase:** Phase 25 (Code Architecture System)  
**Purpose:** Code stack analysis and keeping AI on point when coding  
**Questions:**
- Does SummonAI offer better dependency analysis than custom AST parsing?
- Can it detect runtime dependencies (not just static imports)?
- What's the licensing model and cost?
- Integration complexity with Polly's architecture?
- Performance benchmarks vs. custom solution?

**Resources:**
- Website: [To be researched]
- Documentation: [To be found]
- Community reviews: [To be gathered]

**Next Steps:**
1. Visit SummonAI website, read documentation
2. Compare feature set with Phase 25 requirements
3. Assess integration effort
4. Make build vs buy decision

---

### 2. HyperTask.ai
**Related Phase:** Phase 26 (Project Management)  
**Purpose:** Learn from their project management implementation  
**Questions:**
- How do they handle project visualization?
- What's their approach to AI-assisted planning?
- Dependency management strategies?
- Can we learn from their UX decisions?
- Pricing model and target audience?

**Resources:**
- Website: [To be researched]
- Demo/trial: [Request access]
- User reviews: [Gather feedback]

**Next Steps:**
1. Sign up for trial account
2. Test project creation and management workflows
3. Document UI/UX patterns we like
4. Identify features to adopt or avoid

---

### 3. OpenCode Performance Issues
**Related Phase:** All infrastructure (avoid their mistakes)  
**Purpose:** Learn from OpenCode's performance problems to prevent similar issues in Polly  

**Known Issues (From Your Brain Dump):**
- Massive snapshot folder bloat (hundreds of GB in ~/.local/share/opencode/snapshots)
- High CPU usage (30-90% per process during LLM streaming)
- Excessive context/long session history causing slowdowns
- Subagent/session overload (500+ subagent sessions making TUI unresponsive)
- Intermittent hanging after instructions
- Hard limits on execution time (~80 minute limit)

**How to Avoid in Polly:**
- **Snapshot Management:** Implement Phase 26's smart snapshot system with automatic cleanup
- **CPU Usage:** Optimize LLM response streaming, use background threads
- **Context Management:** Aggressive compression (Phase 2b ✅), context windowing
- **Session Limits:** Cap subagent sessions, implement session pooling
- **Execution Monitoring:** Add timeouts and progress indicators
- **Regular Cleanup:** Automated maintenance tasks

**Research Actions:**
1. Monitor OpenCode GitHub issues for ongoing problems
2. Test Polly under similar loads to identify bottlenecks early
3. Implement monitoring/alerting for resource usage
4. User testing with large projects (1000+ files, 100+ conversations)

---

## Planned Research (Medium Priority)

### 4. Uare.ai
**Related Phase:** Phase 13b (User Profile System)  
**Purpose:** Competitive intelligence for personalized AI market  
**Status:** Market validation research

**Company Overview:**
- **Product:** Uare.ai - Cloud-based "Human Life Model" SaaS
- **Funding:** $10.3M raised (validates personalized AI market demand)
- **Approach:** Identity replication for monetization
- **Architecture:** Cloud-native, proprietary containers

**Strategic Insights:**
- Market validation: Investors believe in personalized AI (proved market exists)
- Uare.ai focuses on cloud SaaS model (monthly subscriptions)
- Polly's differentiator: Edge-native, user owns data, practice augmentation (not identity replication)
- Positioning: "Polly: Personal AI you own" vs "Uare.ai: Personal AI you rent"

**Competitive Advantages for Polly:**
1. **Data Ownership:** Local storage, markdown files, no cloud lock-in
2. **Privacy:** Data never leaves user's machine (unless explicitly sent to cloud providers)
3. **Control:** User can edit profile directly, inspect learned patterns
4. **Philosophy:** Practice augmentation vs identity monetization
5. **Cost:** One-time purchase vs ongoing subscription

**Questions to Research:**
- What profile categories does Uare.ai capture?
- How do they bootstrap user profiles (onboarding flow)?
- What personalization features do users value most?
- User reviews: What do users like/dislike?
- Pricing tiers and feature gating?

**Research Actions:**
1. Monitor Uare.ai blog/announcements for feature releases
2. Read user reviews (ProductHunt, Twitter, Reddit)
3. Identify gaps Polly can fill
4. Track their market messaging (what resonates with users?)

**Marketing Learnings:**
- Investors validated personalized AI market ($10.3M proves demand)
- Use this validation in Polly's positioning
- Emphasize ownership and autonomy (soft autonomist framing)
- Technical benefits: privacy, control, local-first architecture

**Reference:** Phase 13b specification, competitive analysis section

---

### 5. Reor.ai
**Related Phase:** Phase 16 (Notes), Phase 21 (Deduplication)  
**Purpose:** Self-organizing notes capabilities  
**Questions:**
- How do they implement self-organization?
- AI-powered note categorization strategies?
- Automatic tag/domain suggestions?
- Performance with large note collections?

**Next Steps:**
- Try Reor.ai with sample notes
- Document auto-organization features
- Assess applicability to Polly

---

### 6. Kilo Code (Free LLM Models)
**Related Phase:** Phase 11 (Multi-Model Routing)  
**Purpose:** Integrate free models (GLM 4.7, MiniMax 2.1) to reduce costs  
**Questions:**
- How does Kilo Code offer these models for free?
- API access and rate limits?
- Quality comparison with paid models?
- Integration complexity?
- Sustainability of free tier?

**Next Steps:**
1. Research Kilo Code's business model
2. Test GLM 4.7 and MiniMax 2.1 quality
3. Implement as Router v2 options
4. Set as fallback for budget-conscious users

---

## Technical Research

### 7. CodeMirror for Chat Enhancement
**Related Phase:** UI Polish  
**Purpose:** Use CodeMirror for more polished chat experience  
**Questions:**
- Can CodeMirror enhance chat input (syntax highlighting, autocomplete)?
- Performance with real-time streaming?
- Markdown rendering quality?
- Better than current text area?

**Next Steps:**
- Prototype chat input with CodeMirror
- Compare UX with current implementation
- Performance testing

---

### 8. Graph Databases (Neo4j vs JSON)
**Related Phase:** Phase 25 (Code Architecture), Phase 12 (Knowledge Graph)  
**Purpose:** Decide on graph storage format  
**Options:**
- **Neo4j:** Full graph database, powerful queries, overkill?
- **JSON Files:** Simple, portable, may not scale
- **SQLite + Graph Extension:** Middle ground

**Questions:**
- Performance at scale (10k+ nodes)?
- Query complexity needs?
- Portability requirements?
- Setup/dependency overhead?

**Next Steps:**
- Benchmark all three options
- Prototype with realistic data
- Make decision based on Phase 25/12 needs

---

## Design Research

### 9. Figma API Integration
**Related Phase:** Phase 27 (Designer Persona)  
**Purpose:** Two-way sync between Polly and Figma  
**Questions:**
- What's possible with Figma API?
- Can we import designs into Polly?
- Can we export Polly mockups to Figma?
- Authentication flow for users?
- Rate limits and pricing?

**Next Steps:**
1. Read Figma API documentation
2. Prototype basic import/export
3. Design handoff workflow (Designer → Figma → User → Polly)
4. Assess Phase 27a priority

---

### 10. Tailwind CSS Integration
**Related Phase:** Phase 27 (Designer Persona)  
**Purpose:** Design system to code pipeline  
**Questions:**
- Auto-generate Tailwind config from design tokens?
- Component generation with Tailwind classes?
- Customization and theming?

**Next Steps:**
- Research tools that do this well (v0.dev, Builder.io)
- Design token → Tailwind config mapping
- Implement in Designer.system() mode

---

## Monetization Research

### 11. One-Time Purchase Models
**Related Phase:** Business model  
**Purpose:** Study successful one-time purchase apps  
**Examples to Study:**
- **Things 3:** $49.99, thriving without subscriptions
- **Sublime Text:** $99, free trial, sustainable
- **Sketch:** Was one-time, moved to subscription (why?)
- **Panic apps:** Successful indie model

**Questions:**
- How do they fund ongoing development?
- Upgrade pricing strategies (v2, v3)?
- Expansion pack approach (Polly Tools)?
- Enterprise licensing?

**Next Steps:**
- Case studies of each app
- Revenue sustainability analysis
- Design Polly's pricing model

---

## Community Research

### 12. Monome Documentation Style
**Related Phase:** Phase 28 (Open Polly Tools)  
**Purpose:** Learn from their community documentation approach  
**Why Monome:**
- Clear, visual documentation
- Beginner-friendly yet comprehensive
- Community-focused
- Musical tools (creative parallel to Polly)

**Resources:**
- monome.org/docs
- Community norns documentation

**Next Steps:**
- Study documentation structure
- Adopt visual/example-heavy approach
- Apply to Polly Tools documentation

---

## Research Process

### When Adding New Research Item:

1. **Identify Need:** What phase or feature needs this research?
2. **Define Questions:** What do we need to learn?
3. **Set Priority:** High (blocking), Medium (helpful), Low (nice-to-have)
4. **Assign Owner:** Who will research this?
5. **Deadline:** When do we need answers?

### Research Output Format:

Create document in `/docs/planning/investigations/RESEARCH_[TOPIC].md`

```markdown
# Research: [Topic]

**Date:** [Date]  
**Researcher:** [Name]  
**Related Phase:** Phase X

## Summary
[1-2 paragraphs: What did you learn?]

## Key Findings
- Finding 1
- Finding 2
- Finding 3

## Recommendations
[Should we adopt this? How?]

## Resources
- Links
- Screenshots
- Notes
```

---

## Completed Research

### ✅ Pattern Learning Implementation
**Date Completed:** January 25, 2026  
**Phase:** Phase 13a ✅  
**Outcome:** Implemented successfully, 30-70% faster RAG retrieval

### ✅ Mental Models Framework
**Date Completed:** January 29, 2026  
**Phase:** Phase 14 ✅  
**Outcome:** PIL compression (2.3x ratio), three-tier activation

### ✅ Multi-Model Provider Research
**Date Completed:** January 30, 2026  
**Phase:** Phase 11 ✅  
**Outcome:** Integrated 7+ providers (Anthropic, OpenAI, GitHub, Grok, etc.)

---

## Research Archive

Completed research reports moved to: `/docs/planning/investigations/archive/`

---

**Document Maintained By:** Development Team  
**Update Frequency:** Add items as needed, review monthly  
**Status Reviews:** Quarterly assessment of active research
