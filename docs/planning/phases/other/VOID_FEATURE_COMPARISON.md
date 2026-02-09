# Void vs. Polly - Feature Comparison Matrix

**Date:** February 5, 2025  
**Status:** Draft - Needs Verification

---

## Model Integration Comparison

| Feature | Void (Assumed) | Polly (Current) | Gap Analysis |
|---------|---------------|-----------------|--------------|
| **Provider Support** | ? | Ollama, Anthropic, OpenAI, GitHub Models | Need to verify Void's providers |
| **Routing Logic** | ? | Task-based routing (fast/balanced/thorough) | Need to verify Void's routing |
| **Model Selection** | ? | Manual + automatic | Need to verify UI |
| **Streaming** | ? | ✅ Supported | Need to verify |
| **Cost Tracking** | ? | ✅ Implemented | Need to verify |
| **Multi-Provider** | ? | ✅ 6+ providers | Need to verify |

**Key Questions:**
- Does Void support multiple providers?
- How does routing work?
- Is it extensible?

---

## Chat Sidebar Comparison

| Feature | Void (Assumed) | Polly (Needs) | Gap Analysis |
|---------|---------------|---------------|--------------|
| **Position** | ? | Right sidebar (collapsible) | Need to verify |
| **UI Framework** | ? | Custom HTML/CSS/JS | Need to verify |
| **Message Display** | ? | Streaming messages, history | Need to verify |
| **Code Context** | ? | Auto-include current file | Need to verify |
| **Model Selection UI** | ? | Dropdown with provider/model | Need to verify |
| **Save to Notes** | ? | ✅ Required | Likely missing |
| **Conversation History** | ? | ✅ Required | Need to verify |

**Key Questions:**
- How is the chat sidebar implemented?
- Does it include code context?
- How customizable is it?

---

## Time Savings Estimate

### Model Integration
- **Build from scratch:** 2-4 weeks
- **Customize Void:** ? (need to verify)
- **Potential savings:** 2-4 weeks if Void has it

### Chat Sidebar
- **Build from scratch:** 2-3 weeks
- **Customize Void:** ? (need to verify)
- **Potential savings:** 2-3 weeks if Void is close

### Total Potential Savings
- **If both exist:** 4-7 weeks
- **Migration effort:** ? (need to assess)
- **Net savings:** TBD

---

## Risk Assessment

### Maintenance Pause
- **Risk:** No upstream updates
- **Mitigation:** Can we maintain ourselves?
- **Impact:** Medium-High

### Build Complexity
- **Risk:** Same as VSCode (complex)
- **Mitigation:** We have experience now
- **Impact:** Medium

### Feature Gaps
- **Risk:** Missing Polly-specific features
- **Mitigation:** Can we add them?
- **Impact:** Low-Medium

---

## Next Steps

1. ✅ **Verify Void's features** (Phase 1)
2. ⏳ **Assess migration effort** (Phase 2)
3. ⏳ **Calculate time savings** (Phase 3)
4. ⏳ **Make recommendation** (Phase 3)

---

**Last Updated:** February 5, 2025
