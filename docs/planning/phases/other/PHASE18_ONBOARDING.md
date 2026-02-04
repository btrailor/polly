# Phase 18: Onboarding & Progressive Teaching

**Status:** Planned  
**Duration:** 1-2 weeks  
**Prerequisites:** Phase 1.5 (Domain Configuration), Phase 11 (Multi-Model Routing), Phase 13 (Pattern Learning)  
**Enables:** User adoption, progressive feature revelation, autonomy awareness  
**Tier:** 3 (Polish & Autonomy)

---

## Table of Contents

1. [Overview](#overview)
2. [Marketing Context](#marketing-context)
3. [Goals](#goals)
4. [Technical Approach](#technical-approach)
5. [Week-by-Week Breakdown](#week-by-week-breakdown)
6. [Success Criteria](#success-criteria)
7. [Integration Points](#integration-points)
8. [Risk & Mitigation](#risk--mitigation)
9. [Storage & Data Model](#storage--data-model)
10. [UI/UX Specifications](#uiux-specifications)

---

## Overview

Phase 18 implements intelligent onboarding and progressive teaching systems that adapt to user behavior and reveal complexity over time. Instead of overwhelming new users with all features upfront, Polly starts simple and progressively reveals advanced capabilities as users build content and engagement.

This phase directly addresses the "Polly teaches you as you teach Polly" positioning theme, creating a user experience where Week 1 looks dramatically different from Week 52.

### Core Components

1. **First-Run Wizard** - Initial setup with dual-path choice (zero-config vs. custom domains)
2. **Progressive Feature Revelation** - Advanced features unlock based on readiness signals
3. **Adaptive Tutorial System** - Contextual guidance that fades as mastery increases
4. **Autonomy Dashboard** - Visual tracking of progressive local intelligence growth
5. **Usage Pattern Detection** - Identifies user goals and adapts experience accordingly

### Key Principles

- **No forced tutorials** - Users can skip and explore freely
- **Value before complexity** - Core features work immediately, advanced features reveal later
- **Contextual education** - Teach features when they become relevant, not upfront
- **Autonomy awareness** - Users understand they're building capability, not renting service
- **Adaptive pacing** - Fast for power users, patient for explorers

---

## Marketing Context

### Positioning Alignment

**"Polly teaches you as you teach Polly"**

This phase operationalizes the core marketing theme of mutual learning. As users teach Polly about their work (through notes, queries, and usage), Polly teaches users about:
- Their own thinking patterns (via knowledge graph)
- Advanced capabilities (progressive revelation)
- System autonomy (via dashboard metrics)
- Cross-domain connections (as content accumulates)

### Target Audience Considerations

**ADHD/Neurodivergent Users:**
- Zero-config path reduces setup paralysis
- Minimal onboarding friction (working in <60 seconds)
- Adaptive tutorials that don't demand immediate attention
- Progressive complexity avoids overwhelm

**Polymaths/Cross-Domain Workers:**
- Custom domain setup satisfies need for structure
- Progressive revelation matches deepening engagement
- Knowledge graph unlocks when meaningful (enough content to visualize)
- Advanced features appear as work complexity increases

**Privacy-Conscious Professionals:**
- Early visibility into autonomy progression
- Clear explanation of cloud vs. local processing
- Data ownership messaging from day one
- Self-hosting options surfaced when relevant

### Competitive Differentiation

**vs. Obsidian/Notion:**
- They dump you in an empty workspace. Polly guides you to immediate value.
- But unlike consumer apps, Polly doesn't force a tutorial - respects user agency.

**vs. ChatGPT/Claude:**
- They're the same experience on Day 1 and Day 100. Polly evolves with you.
- Progressive revelation shows you're building something persistent, not having ephemeral conversations.

**vs. Jace.ai:**
- They onboard you into dependency. Polly onboards you into progressive autonomy.
- Autonomy dashboard makes the difference explicit and measurable.

---

## Goals

### Primary Objectives

1. **Reduce time-to-first-value** to under 60 seconds (median)
2. **Increase feature discovery** - 70% of users discover advanced features within 30 days
3. **Build autonomy awareness** - 80% of users view autonomy dashboard at least once
4. **Minimize abandonment** - <10% of users abandon during onboarding
5. **Adapt to user type** - Correctly identify usage goals within first week

### Success Metrics

**Onboarding Speed:**
- Time to first note created: <60 seconds (median)
- Time to complete first-run setup: <3 minutes (median)
- % users who skip setup entirely (zero-config): Target 40%

**Feature Discovery:**
- % users who explore knowledge graph by Day 30: Target 70%
- % users who customize domains after zero-config start: Target 35%
- % users who engage with tutorial system: Target 60%

**Autonomy Awareness:**
- % users who view autonomy dashboard: Target 80% by Day 30
- % users who understand progressive autonomy concept: Target 65% (survey)
- Repeat dashboard visits: Target 3+ per month per active user

**Engagement Quality:**
- Notes created in first week: Target median 10+
- Queries asked in first week: Target median 20+
- Return rate Day 7: Target 70%
- Return rate Day 30: Target 50%

---

## Technical Approach

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Onboarding Orchestrator                  │
│  (Manages user journey state, feature revelation logic)    │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  First-Run   │ │  Progressive │ │   Adaptive   │
│   Wizard     │ │   Revelation │ │   Tutorial   │
│              │ │    Engine    │ │    System    │
└──────────────┘ └──────────────┘ └──────────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
                      ▼
        ┌──────────────────────────┐
        │  User Journey State DB   │
        │  (SQLite)                │
        └──────────────────────────┘
                      │
                      ▼
        ┌──────────────────────────┐
        │   Autonomy Dashboard     │
        │   (Metrics & Tracking)   │
        └──────────────────────────┘
```

### Component Breakdown

#### 1. Onboarding Orchestrator

**Responsibility:** Central state machine managing user journey

**Key Logic:**
- Tracks onboarding completion milestones
- Determines feature revelation timing
- Manages tutorial visibility and fading
- Coordinates between components

**State Tracking:**
```typescript
interface UserJourneyState {
  userId: string;
  onboardingCompleted: boolean;
  setupPath: 'zero-config' | 'custom' | 'skipped';
  
  // Milestone tracking
  milestones: {
    firstNoteCreated: Date | null;
    firstQueryAsked: Date | null;
    firstDomainCustomized: Date | null;
    knowledgeGraphExplored: Date | null;
    autonomyDashboardViewed: Date | null;
  };
  
  // Content accumulation
  noteCount: number;
  queryCount: number;
  domainCount: number;
  connectionCount: number;
  
  // Feature revelation state
  revealedFeatures: string[]; // Feature IDs that have been unlocked
  dismissedTutorials: string[]; // Tutorial IDs user has dismissed
  
  // Usage pattern detection
  detectedPatterns: {
    primaryUseCase: 'research' | 'creative' | 'coding' | 'multi-domain' | 'unknown';
    activityLevel: 'power' | 'regular' | 'casual';
    domainFocus: 'single' | 'multi';
  };
  
  // Autonomy metrics (cached for dashboard)
  autonomyMetrics: {
    tokenUsageLocal: number;
    tokenUsageCloud: number;
    ragHitRate: number;
    patternConfidence: number;
    daysSinceLastCloudQuery: { [topic: string]: number };
  };
}
```

#### 2. First-Run Wizard

**Responsibility:** Initial setup experience with dual-path option

**User Flow:**
```
1. Welcome Screen
   ├─> "Start Working" (Zero-Config) → Creates Work/Personal/Learning domains
   └─> "Customize Setup" (Custom) → Domain definition wizard

2. Quick Explanation (single screen, skippable)
   - What Polly does
   - Progressive autonomy concept
   - Data ownership guarantee

3. Optional: Connect Integrations
   - Obsidian vault (if detected)
   - Code workspace directory (if relevant)
   - Skip for now option

4. Done → Immediately usable interface
```

**Key Design Decisions:**
- Single "Start Working" button is primary CTA (not hidden)
- "Customize Setup" is secondary but equally visible
- No multi-step forms unless user chooses custom path
- All choices reversible later (reduce commitment anxiety)

#### 3. Progressive Revelation Engine

**Responsibility:** Unlock features based on readiness signals

**Revelation Logic:**

```typescript
interface FeatureRevealRule {
  featureId: string;
  featureName: string;
  
  // Conditions (all must be true to reveal)
  conditions: {
    minNotes?: number;
    minQueries?: number;
    minConnections?: number;
    minDomains?: number;
    daysSinceFirstUse?: number;
    requiredMilestones?: string[];
    usagePattern?: string[];
  };
  
  // How to reveal
  revealMethod: 'tooltip' | 'modal' | 'badge' | 'dashboard-card';
  revealMessage: string;
  
  // Optional tutorial
  tutorialId?: string;
}

// Example rules
const REVELATION_RULES: FeatureRevealRule[] = [
  {
    featureId: 'knowledge-graph',
    featureName: 'Knowledge Graph Visualization',
    conditions: {
      minNotes: 15,
      minConnections: 5,
    },
    revealMethod: 'modal',
    revealMessage: "You've created enough content to see your knowledge network. Ready to explore the graph?",
    tutorialId: 'knowledge-graph-intro',
  },
  {
    featureId: 'cross-domain-patterns',
    featureName: 'Cross-Domain Pattern Recognition',
    conditions: {
      minDomains: 2,
      minNotes: 30,
      daysSinceFirstUse: 7,
    },
    revealMethod: 'dashboard-card',
    revealMessage: "Polly is starting to recognize patterns across your domains. View insights.",
    tutorialId: 'cross-domain-intro',
  },
  {
    featureId: 'reasoning-transparency',
    featureName: 'Connection Reasoning',
    conditions: {
      requiredMilestones: ['knowledge-graph-explored'],
      minConnections: 10,
    },
    revealMethod: 'tooltip',
    revealMessage: "Click any connection to see WHY Polly made it.",
  },
  {
    featureId: 'mental-models',
    featureName: 'Mental Model Detection',
    conditions: {
      minNotes: 50,
      daysSinceFirstUse: 14,
      usagePattern: ['research', 'multi-domain'],
    },
    revealMethod: 'modal',
    revealMessage: "Polly has identified recurring mental models in your work. Explore them.",
    tutorialId: 'mental-models-intro',
  },
  {
    featureId: 'autonomy-dashboard',
    featureName: 'Autonomy Dashboard',
    conditions: {
      daysSinceFirstUse: 7,
      minQueries: 50,
    },
    revealMethod: 'badge',
    revealMessage: "See how your knowledge is compounding and token usage is shifting local.",
  },
  {
    featureId: 'self-hosting',
    featureName: 'Self-Hosting Options',
    conditions: {
      daysSinceFirstUse: 30,
      usagePattern: ['power'],
    },
    revealMethod: 'dashboard-card',
    revealMessage: "Ready to self-host Polly? View deployment options.",
  },
];
```

**Revelation Flow:**
1. Background service checks revelation rules every 24 hours
2. When conditions met, feature "unlocks" (visible in UI)
3. Revelation notification shown via appropriate method
4. User can explore feature or dismiss notification
5. Feature remains unlocked permanently

#### 4. Adaptive Tutorial System

**Responsibility:** Contextual guidance that fades with mastery

**Tutorial Types:**

**A. Contextual Tooltips**
- Appear on first interaction with UI element
- Dismissed automatically after 2-3 views
- Can be manually dismissed or disabled globally

**B. Interactive Walkthroughs**
- Optional step-by-step guides for complex features
- Can be paused, resumed, or skipped
- Progress tracked per user

**C. Discovery Prompts**
- "Did you know..." style tips based on usage patterns
- Appear in sidebar or as subtle notifications
- Frequency decreases over time (tutorial fade)

**Tutorial Fade Logic:**
```typescript
interface TutorialFadeState {
  tutorialId: string;
  viewCount: number;
  lastShown: Date;
  dismissed: boolean;
  
  // Fade parameters
  maxViews: number; // Auto-dismiss after N views
  cooldownDays: number; // Min days between showings
  fadeAfterDays: number; // Stop showing after N days
}

// Tutorial becomes less intrusive over time
function shouldShowTutorial(state: TutorialFadeState): boolean {
  if (state.dismissed) return false;
  if (state.viewCount >= state.maxViews) return false;
  
  const daysSinceLastShown = daysSince(state.lastShown);
  if (daysSinceLastShown < state.cooldownDays) return false;
  
  const daysSinceFirstUse = getUserDaysSinceFirstUse();
  if (daysSinceFirstUse > state.fadeAfterDays) return false;
  
  return true;
}
```

**Tutorial Content:**

1. **Knowledge Graph Tutorial**
   - "This is your knowledge network"
   - "Each node = a note, connection = related concepts"
   - "Click nodes to explore, click edges to see reasoning"
   - Shown: First time graph opened, max 2 views

2. **Domain Customization Tutorial**
   - "Domains organize your work areas"
   - "You can customize or create new domains anytime"
   - "Polly suggests new domains based on patterns"
   - Shown: First time domains page opened, max 2 views

3. **Progressive Autonomy Tutorial**
   - "Polly starts with cloud AI + your context"
   - "Over time, more queries answered locally"
   - "Your token costs decrease, intelligence increases"
   - Shown: First time autonomy dashboard opened, max 3 views

4. **Reasoning Transparency Tutorial**
   - "Click 'Why this connection?' to see Polly's reasoning"
   - "Learn how Polly identifies patterns"
   - "Understand your own thinking through AI explanations"
   - Shown: After first 10 connections made, max 2 views

#### 5. Autonomy Dashboard

**Responsibility:** Visual tracking of progressive local intelligence

**Metrics Displayed:**

**1. Token Usage Trend**
- **Metric:** Local vs. cloud token consumption over time
- **Visualization:** Stacked area chart showing split trending toward local
- **Insight:** "Your token usage is 67% local this month, up from 23% at start"

**2. RAG Hit Rate**
- **Metric:** % of queries answered from local context vs. cloud
- **Visualization:** Line chart with trend arrow
- **Insight:** "78% of your queries answered from your accumulated knowledge"

**3. Pattern Learning Progress**
- **Metric:** Number of recognized patterns + confidence scores
- **Visualization:** Progress bars per domain
- **Insight:** "Polly has learned 47 patterns across your domains with 82% confidence"

**4. Time Since Last Cloud Query (Per Topic)**
- **Metric:** Days since Polly needed cloud assistance for specific topics
- **Visualization:** List of topics with "going local" badges
- **Insight:** "'React optimization' hasn't required cloud queries in 23 days"

**5. Knowledge Compound Score**
- **Metric:** Synthetic score combining note count, connection density, pattern confidence
- **Visualization:** Single large number with historical graph
- **Insight:** "Your knowledge compound score: 847 (up 23% this month)"

**Dashboard Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  Autonomy Dashboard                                     │
│  "Watch your knowledge compound and costs decrease"     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Knowledge Compound Score: 847  ↗ +23%         │   │
│  │  [Historical graph: rising trend line]          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐   │
│  │ Token Usage          │  │ RAG Hit Rate         │   │
│  │ 67% Local ↑          │  │ 78% ↑                │   │
│  │ [Stacked area chart] │  │ [Line chart]         │   │
│  └──────────────────────┘  └──────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Pattern Learning Progress                       │   │
│  │                                                  │   │
│  │ Research: ████████░░ 82% (47 patterns)         │   │
│  │ Coding:   ██████░░░░ 65% (31 patterns)         │   │
│  │ Creative: ████░░░░░░ 43% (18 patterns)         │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Topics Going Local                              │   │
│  │                                                  │   │
│  │ • React optimization: 23 days without cloud     │   │
│  │ • Music theory: 45 days without cloud           │   │
│  │ • Project management: 12 days without cloud     │   │
│  │                                                  │   │
│  │ [View all topics →]                             │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  What This Means:                                       │
│  You're building a system that knows YOUR work          │
│  specifically. The more you use Polly, the less it      │
│  depends on cloud AI—and the more it knows about        │
│  your unique patterns.                                  │
│                                                          │
│  [Export Your Data] [Self-Hosting Options]             │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**
- Real-time metric calculation (with caching)
- Historical data stored in SQLite
- Charts rendered with lightweight library (Chart.js or similar)
- Accessible via sidebar badge + dedicated dashboard route

#### 6. Usage Pattern Detection

**Responsibility:** Identify user goals and adapt experience

**Detected Patterns:**

**Primary Use Case:**
- **Research:** Lots of notes, external links, query-heavy
- **Creative:** Multimedia content, less structured, visual focus
- **Coding:** Code snippets, technical queries, workspace integration
- **Multi-Domain:** Balanced activity across 3+ domains

**Activity Level:**
- **Power:** Daily usage, 50+ notes/month, deep feature engagement
- **Regular:** 3-5x/week usage, 20-50 notes/month, core features
- **Casual:** Sporadic usage, <20 notes/month, basic features

**Detection Logic:**
```typescript
function detectUsagePattern(state: UserJourneyState): UsagePattern {
  const { noteCount, queryCount, domainCount, milestones } = state;
  const daysSinceFirstUse = daysSince(milestones.firstNoteCreated);
  
  // Activity level
  const notesPerWeek = noteCount / (daysSinceFirstUse / 7);
  let activityLevel: ActivityLevel;
  if (notesPerWeek > 12) activityLevel = 'power';
  else if (notesPerWeek > 5) activityLevel = 'regular';
  else activityLevel = 'casual';
  
  // Primary use case (simplified heuristic)
  const queryToNoteRatio = queryCount / noteCount;
  let primaryUseCase: UseCase;
  
  if (hasCodeWorkspace(state) && queryToNoteRatio > 2) {
    primaryUseCase = 'coding';
  } else if (domainCount >= 3 && notesBalancedAcrossDomains(state)) {
    primaryUseCase = 'multi-domain';
  } else if (queryToNoteRatio > 3) {
    primaryUseCase = 'research';
  } else {
    primaryUseCase = 'creative';
  }
  
  return { primaryUseCase, activityLevel, domainFocus: domainCount > 1 ? 'multi' : 'single' };
}
```

**Adaptations Based on Patterns:**

- **Power users:** Reveal advanced features earlier, suggest self-hosting sooner
- **Research users:** Emphasize knowledge graph, cross-domain connections
- **Coding users:** Highlight code workspace features, technical patterns
- **Creative users:** Visual features, multimedia handling, less structured organization
- **Casual users:** Keep interface simple longer, gentle feature revelation

---

## Week-by-Week Breakdown

### Week 1: Core Onboarding Infrastructure (Days 1-5)

**Day 1-2: Onboarding Orchestrator + State Management**
- Build `UserJourneyState` schema and SQLite tables
- Implement onboarding orchestrator state machine
- Create milestone tracking system
- Build background service for metric updates

**Day 3-4: First-Run Wizard**
- Design and implement welcome screen UI
- Build dual-path choice (zero-config vs. custom)
- Implement zero-config domain creation (Work/Personal/Learning)
- Create custom domain setup wizard (if user chooses)
- Add integration connection step (Obsidian, code workspace)

**Day 5: Initial Tutorial System**
- Implement tooltip rendering system
- Create tutorial fade logic
- Build tutorial dismissal and tracking
- Design first 3 contextual tooltips (notes, domains, queries)

**Deliverable:** Working first-run wizard with both paths, basic tutorial system

---

### Week 2: Progressive Revelation + Autonomy Dashboard (Days 6-10)

**Day 6-7: Progressive Revelation Engine**
- Implement `FeatureRevealRule` system
- Create revelation rule checking service (runs every 24h)
- Build revelation notification UI (modal, tooltip, badge, card)
- Define initial 6 revelation rules (knowledge graph, cross-domain, reasoning, mental models, autonomy, self-hosting)

**Day 8-9: Autonomy Dashboard - Metrics**
- Implement metric calculation:
  - Token usage tracking (local vs. cloud)
  - RAG hit rate calculation
  - Pattern learning progress aggregation
  - Time since last cloud query per topic
  - Knowledge compound score formula
- Create metric historical storage
- Build metric caching system

**Day 10: Autonomy Dashboard - UI**
- Design dashboard layout
- Implement chart visualizations (Chart.js integration)
- Create "Topics Going Local" list
- Add dashboard navigation and badge
- Write explanatory messaging

**Deliverable:** Full progressive revelation system + working autonomy dashboard

---

### Optional Week 3: Polish & Advanced Tutorials (Days 11-14)

**Day 11: Usage Pattern Detection**
- Implement pattern detection algorithms
- Create activity level classification
- Build primary use case identification
- Add adaptive UI adjustments based on patterns

**Day 12-13: Advanced Tutorial Content**
- Create knowledge graph interactive walkthrough
- Build progressive autonomy explanation sequence
- Design reasoning transparency tutorial
- Implement domain customization guide
- Add discovery prompts system

**Day 14: Testing & Refinement**
- User testing of onboarding flows
- A/B test zero-config vs. custom path messaging
- Refine revelation timing based on test data
- Polish UI transitions and animations
- Bug fixes and edge cases

**Deliverable:** Polished, tested onboarding experience ready for users

---

## Success Criteria

### Functional Requirements

**Must Have:**
- [ ] First-run wizard with dual-path choice works
- [ ] Zero-config path creates Work/Personal/Learning domains automatically
- [ ] Custom path allows domain definition before first use
- [ ] All onboarding choices are reversible later
- [ ] Tutorial tooltips appear on first feature interaction
- [ ] Tutorial system respects dismissals and fades over time
- [ ] Progressive revelation unlocks features based on rules
- [ ] Autonomy dashboard displays all 5 core metrics
- [ ] Dashboard updates daily with fresh metric calculations
- [ ] Milestone tracking works accurately

**Should Have:**
- [ ] Usage pattern detection identifies user type within 1 week
- [ ] Adaptive UI adjustments based on detected patterns
- [ ] Interactive walkthroughs for complex features
- [ ] "Topics Going Local" list updates in real-time
- [ ] Historical metric graphs show at least 30 days
- [ ] Dashboard accessible via sidebar badge

**Nice to Have:**
- [ ] A/B testing framework for onboarding variants
- [ ] User survey integration for qualitative feedback
- [ ] Onboarding analytics dashboard (internal)
- [ ] Customizable autonomy metric goals
- [ ] Gamification elements (milestones, achievements)

### Performance Requirements

- First-run wizard loads in <500ms
- Metric calculations complete in <2 seconds
- Dashboard renders in <1 second with 90 days of history
- Revelation rule checking completes in <100ms (background)
- Tutorial fade logic executes in <50ms per check

### User Experience Requirements

- Time to first note created: <60 seconds (median)
- Onboarding abandonment rate: <10%
- Tutorial dismissal rate: <40% (shows tutorials are relevant)
- Autonomy dashboard engagement: 80% of users view by Day 30
- Feature discovery rate: 70% of users discover advanced features by Day 30

---

## Integration Points

### Phase 1.5: Domain Configuration
- First-run wizard creates domains (zero-config or custom)
- Tutorial content explains domain system
- Progressive revelation suggests new domains based on content clustering

### Phase 11: Multi-Model Routing
- Autonomy dashboard displays token usage metrics from routing layer
- RAG hit rate calculated from routing decisions
- "Topics Going Local" fed by routing confidence scores

### Phase 13: Pattern Learning
- Pattern learning progress metrics displayed in dashboard
- Pattern confidence scores contribute to knowledge compound score
- Revelation rules unlock mental model features when patterns mature

### Phase 12: Knowledge Graph
- Knowledge graph tutorial triggered when enough connections exist
- Graph exploration milestone tracked for revelation rules
- Connection count drives feature revelation timing

### Phase 16: Native Notes
- First note creation triggers milestone
- Note count drives revelation rules
- Auto-organization feature introduced via tutorial

### Phase 19: Data Autonomy
- Dashboard links to export and self-hosting features
- Data ownership messaging integrated into onboarding
- Self-hosting revelation appears for power users

---

## Risk & Mitigation

### Risk 1: Onboarding Friction Increases Abandonment
**Impact:** High  
**Probability:** Medium

**Mitigation:**
- A/B test onboarding flow length and complexity
- Make all steps skippable with smart defaults
- Measure time-to-first-value religiously
- Provide "Start Working" button prominently on every screen

### Risk 2: Feature Revelation Timing Feels Arbitrary
**Impact:** Medium  
**Probability:** Medium

**Mitigation:**
- Make revelation logic transparent ("You've created 15 notes, ready to see the graph?")
- Allow manual feature discovery (advanced settings)
- User testing to validate revelation timing feels natural
- Provide clear explanations with each revelation

### Risk 3: Tutorial Fatigue Annoys Power Users
**Impact:** Medium  
**Probability:** High

**Mitigation:**
- Aggressive tutorial fade for high-activity users
- Global "Disable all tutorials" setting
- Contextual tutorials only (never blocking)
- Skip buttons on every tutorial screen

### Risk 4: Autonomy Metrics Don't Resonate
**Impact:** Medium  
**Probability:** Low

**Mitigation:**
- User research on which metrics matter most
- Customizable dashboard (users choose which metrics to display)
- Clear explanatory text about what metrics mean
- Link metrics to cost savings (concrete benefit)

### Risk 5: Usage Pattern Detection Misclassifies Users
**Impact:** Low  
**Probability:** Medium

**Mitigation:**
- Conservative detection (default to generic experience if unclear)
- Allow manual override of detected pattern
- Use pattern detection for suggestions, not restrictions
- Continuous refinement of detection algorithms based on feedback

---

## Storage & Data Model

### SQLite Schema

```sql
-- User journey state
CREATE TABLE user_journey_state (
  user_id TEXT PRIMARY KEY,
  onboarding_completed BOOLEAN DEFAULT FALSE,
  setup_path TEXT CHECK(setup_path IN ('zero-config', 'custom', 'skipped')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Milestones
CREATE TABLE user_milestones (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  milestone_type TEXT NOT NULL,
  achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES user_journey_state(user_id)
);

CREATE INDEX idx_milestones_user ON user_milestones(user_id);
CREATE INDEX idx_milestones_type ON user_milestones(milestone_type);

-- Feature revelation state
CREATE TABLE revealed_features (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  feature_id TEXT NOT NULL,
  revealed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  viewed BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (user_id) REFERENCES user_journey_state(user_id),
  UNIQUE(user_id, feature_id)
);

CREATE INDEX idx_revealed_user ON revealed_features(user_id);

-- Tutorial state
CREATE TABLE tutorial_state (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  tutorial_id TEXT NOT NULL,
  view_count INTEGER DEFAULT 0,
  last_shown TIMESTAMP,
  dismissed BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (user_id) REFERENCES user_journey_state(user_id),
  UNIQUE(user_id, tutorial_id)
);

CREATE INDEX idx_tutorial_user ON tutorial_state(user_id);

-- Autonomy metrics (historical)
CREATE TABLE autonomy_metrics_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  -- Token usage
  tokens_local INTEGER DEFAULT 0,
  tokens_cloud INTEGER DEFAULT 0,
  
  -- RAG performance
  rag_hits INTEGER DEFAULT 0,
  rag_misses INTEGER DEFAULT 0,
  
  -- Pattern learning
  pattern_count INTEGER DEFAULT 0,
  pattern_confidence_avg REAL DEFAULT 0.0,
  
  -- Content accumulation
  note_count INTEGER DEFAULT 0,
  connection_count INTEGER DEFAULT 0,
  domain_count INTEGER DEFAULT 0,
  
  -- Synthetic score
  knowledge_compound_score INTEGER DEFAULT 0,
  
  FOREIGN KEY (user_id) REFERENCES user_journey_state(user_id)
);

CREATE INDEX idx_metrics_user_date ON autonomy_metrics_history(user_id, recorded_at);

-- Topics going local tracking
CREATE TABLE topic_local_status (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  topic_name TEXT NOT NULL,
  last_cloud_query TIMESTAMP,
  total_queries INTEGER DEFAULT 0,
  local_queries INTEGER DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES user_journey_state(user_id),
  UNIQUE(user_id, topic_name)
);

CREATE INDEX idx_topic_user ON topic_local_status(user_id);

-- Usage pattern detection
CREATE TABLE usage_patterns (
  user_id TEXT PRIMARY KEY,
  primary_use_case TEXT CHECK(primary_use_case IN ('research', 'creative', 'coding', 'multi-domain', 'unknown')),
  activity_level TEXT CHECK(activity_level IN ('power', 'regular', 'casual')),
  domain_focus TEXT CHECK(domain_focus IN ('single', 'multi')),
  last_calculated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES user_journey_state(user_id)
);
```

### Configuration Files

**`config/revelation_rules.json`**
```json
{
  "rules": [
    {
      "featureId": "knowledge-graph",
      "featureName": "Knowledge Graph Visualization",
      "conditions": {
        "minNotes": 15,
        "minConnections": 5
      },
      "revealMethod": "modal",
      "revealMessage": "You've created enough content to see your knowledge network. Ready to explore the graph?",
      "tutorialId": "knowledge-graph-intro"
    }
    // ... more rules
  ]
}
```

**`config/tutorial_content.json`**
```json
{
  "tutorials": [
    {
      "id": "knowledge-graph-intro",
      "type": "walkthrough",
      "steps": [
        {
          "title": "Your Knowledge Network",
          "content": "This is your knowledge graph. Each node represents a note, and connections show related concepts.",
          "targetElement": "#graph-canvas"
        }
        // ... more steps
      ],
      "fadeConfig": {
        "maxViews": 2,
        "cooldownDays": 7,
        "fadeAfterDays": 30
      }
    }
    // ... more tutorials
  ]
}
```

---

## UI/UX Specifications

### First-Run Wizard Screens

**Screen 1: Welcome**
```
┌───────────────────────────────────────────────────────┐
│                                                        │
│                    Welcome to Polly                    │
│                                                        │
│         Infrastructure for polymathic thinking         │
│                                                        │
│  ┌───────────────────────────────────────────────┐   │
│  │                                                │   │
│  │         [Large "Start Working" Button]         │   │
│  │                                                │   │
│  │  Zero-config setup. Working in 30 seconds.    │   │
│  │                                                │   │
│  └───────────────────────────────────────────────┘   │
│                                                        │
│                       or                               │
│                                                        │
│              [Customize Setup Link]                    │
│                                                        │
│         Define your domains and preferences            │
│                                                        │
└───────────────────────────────────────────────────────┘
```

**Screen 2a: Zero-Config Path**
```
┌───────────────────────────────────────────────────────┐
│                                                        │
│                  Setting things up...                  │
│                                                        │
│  Creating your workspace:                             │
│  ✓ Work domain                                        │
│  ✓ Personal domain                                    │
│  ✓ Learning domain                                    │
│                                                        │
│  You can customize these anytime.                     │
│                                                        │
│                  [Continue →]                          │
│                                                        │
└───────────────────────────────────────────────────────┘
```

**Screen 2b: Custom Path**
```
┌───────────────────────────────────────────────────────┐
│                                                        │
│              Define Your Work Domains                  │
│                                                        │
│  Domains organize your work areas. Examples:          │
│  • Research, Creative Projects, Client Work           │
│  • Code, Writing, Music                               │
│  • Whatever matches how YOU think                     │
│                                                        │
│  ┌─────────────────────────────────────────────┐     │
│  │ Domain 1: [________________]  [Icon ▼]      │     │
│  │ Domain 2: [________________]  [Icon ▼]      │     │
│  │ Domain 3: [________________]  [Icon ▼]      │     │
│  │                                              │     │
│  │ [+ Add Domain]                               │     │
│  └─────────────────────────────────────────────┘     │
│                                                        │
│              [← Back]  [Continue →]                    │
│                                                        │
└───────────────────────────────────────────────────────┘
```

**Screen 3: Optional Integrations**
```
┌───────────────────────────────────────────────────────┐
│                                                        │
│              Connect Your Existing Work                │
│                                                        │
│  ┌─────────────────────────────────────────────┐     │
│  │  📁 Obsidian Vault                          │     │
│  │                                              │     │
│  │  [Select Vault Directory]                   │     │
│  │                                              │     │
│  │  Polly will integrate with your vault       │     │
│  └─────────────────────────────────────────────┘     │
│                                                        │
│  ┌─────────────────────────────────────────────┐     │
│  │  💻 Code Workspace                          │     │
│  │                                              │     │
│  │  [Select Directory]                         │     │
│  │                                              │     │
│  │  Enable code intelligence features          │     │
│  └─────────────────────────────────────────────┘     │
│                                                        │
│           [Skip for Now]  [Continue →]                │
│                                                        │
└───────────────────────────────────────────────────────┘
```

**Screen 4: All Set**
```
┌───────────────────────────────────────────────────────┐
│                                                        │
│                    You're All Set!                     │
│                                                        │
│  Polly is ready. A few things to know:                │
│                                                        │
│  ✓ Your data stays local by default                  │
│  ✓ Progressive autonomy: less cloud, more local      │
│  ✓ Export your data anytime                          │
│  ✓ Advanced features unlock as you build content     │
│                                                        │
│  View autonomy dashboard anytime to track your        │
│  knowledge compounding.                               │
│                                                        │
│                [Start Creating →]                      │
│                                                        │
└───────────────────────────────────────────────────────┘
```

### Progressive Revelation UI Patterns

**Modal Revelation (for significant features):**
```
┌─────────────────────────────────────────────────┐
│                                                  │
│        🎉 New Feature Unlocked                  │
│                                                  │
│     Knowledge Graph Visualization               │
│                                                  │
│  You've created enough content to see your      │
│  knowledge network. Ready to explore the        │
│  graph?                                         │
│                                                  │
│  [Show Me]  [Maybe Later]  [Don't Show Again]  │
│                                                  │
└─────────────────────────────────────────────────┘
```

**Tooltip Revelation (for subtle features):**
```
    ┌────────────────────────────────┐
    │ Click any connection to see    │
    │ WHY Polly made it.             │
    │                                 │
    │ [Got It]                       │
    └───────┬────────────────────────┘
            │
            ▼
     [Connection Edge]
```

**Badge Revelation (for dashboard features):**
```
[🔔1] Autonomy Dashboard
```

**Dashboard Card Revelation (for long-form features):**
```
┌────────────────────────────────────────────────┐
│  Ready to Self-Host?                           │
│                                                 │
│  You've been using Polly for 30 days. Want    │
│  complete control? View self-hosting options.  │
│                                                 │
│  [Learn More →]  [Dismiss]                     │
└────────────────────────────────────────────────┘
```

### Tutorial Tooltip Example

**First note creation:**
```
     ┌──────────────────────────────────┐
     │ Create notes here. Polly will    │
     │ auto-file them based on content. │
     │                                   │
     │ [Got It] [Don't Show Tips]       │
     └─────────┬────────────────────────┘
               │
               ▼
        [+ New Note Button]
```

### Autonomy Dashboard Full Mockup

(See earlier section for detailed dashboard layout)

---

## Marketing Integration

### Onboarding → Marketing Messaging

**First-Run Wizard:**
- Welcome screen: "Infrastructure for polymathic thinking"
- Zero-config path: "Stop organizing. Start working."
- Custom path: "Your work doesn't fit in boxes."
- Completion screen: "Your data stays local by default" (data ownership)

**Progressive Revelation:**
- Knowledge graph unlock: "See how you think."
- Autonomy dashboard unlock: "Watch your knowledge compound."
- Self-hosting unlock: "Your data. Your freedom."

**Tutorial Content:**
- Weave in progressive autonomy messaging
- Emphasize data ownership throughout
- Reinforce "building capability, not renting service"

### User Journey Touchpoints

**Day 1:** Immediate value, zero friction
**Day 7:** Autonomy dashboard reveals, show compounding
**Day 14:** Knowledge graph unlocks, show connections
**Day 30:** Advanced features appear, showcase depth
**Day 90:** Self-hosting options surface, emphasize freedom

Each touchpoint reinforces core positioning themes.

---

## Testing Plan

### Unit Tests

- [ ] Revelation rule evaluation logic
- [ ] Tutorial fade calculations
- [ ] Usage pattern detection algorithms
- [ ] Metric calculation accuracy
- [ ] Milestone tracking correctness

### Integration Tests

- [ ] First-run wizard both paths (zero-config + custom)
- [ ] Tutorial tooltips appear on first interaction
- [ ] Progressive revelation triggers correctly
- [ ] Autonomy dashboard displays accurate data
- [ ] User journey state persists correctly

### User Testing

**Phase 1: Onboarding Flow (5-10 users)**
- Measure time-to-first-note
- Observe path choice (zero-config vs. custom)
- Track abandonment points
- Collect qualitative feedback on clarity

**Phase 2: Tutorial System (10-15 users)**
- Measure dismissal rates
- Observe engagement with walkthroughs
- Test tutorial fade timing
- Identify annoying vs. helpful tutorials

**Phase 3: Progressive Revelation (15-20 users over 30 days)**
- Track feature discovery rates
- Measure time-to-unlock for each feature
- Validate revelation timing feels natural
- Test autonomy dashboard resonance

### A/B Testing Candidates

1. **Zero-config vs. Custom path prominence**
   - A: "Start Working" primary, "Customize" secondary
   - B: Both options equally prominent

2. **Tutorial density**
   - A: Aggressive tooltips on all new features
   - B: Minimal tooltips, encourage exploration

3. **Autonomy dashboard timing**
   - A: Reveal at Day 7
   - B: Reveal at Day 14

4. **Revelation notification style**
   - A: Modal-heavy (interruptive)
   - B: Badge/card-heavy (non-interruptive)

---

## Future Enhancements (Post-Phase 18)

### Advanced Usage Pattern Detection
- Use ML to predict user churn risk
- Personalized feature recommendations based on detected goals
- Cohort analysis for better revelation timing

### Gamification Elements
- Milestone achievements with celebratory UI
- Knowledge compound score leaderboards (opt-in)
- Streak tracking for engagement

### Social Onboarding
- Invite system with referral tracking
- Shared knowledge graphs (opt-in, privacy-preserving)
- Community templates for domain setups

### Enhanced Autonomy Metrics
- Cost savings calculator ($ saved via local processing)
- Carbon footprint reduction (local vs. cloud)
- Comparative metrics (you vs. average Polly user)

---

## Conclusion

Phase 18 transforms Polly from a capable system into an approachable, teachable one. By implementing progressive revelation, adaptive tutorials, and autonomy awareness, we ensure users:

1. **Start immediately** - Zero friction to first value
2. **Learn progressively** - Complexity reveals when ready
3. **Understand autonomy** - See knowledge compounding visually
4. **Build capability** - Not just using a tool, building a system

This phase operationalizes the "Polly teaches you as you teach Polly" positioning theme and creates the foundation for long-term user engagement and retention.

**Key Success Metric:** Users who complete onboarding and view the autonomy dashboard within 30 days should have 3x higher retention at Day 90 compared to those who don't.

---

**Implementation Priority:** High (Tier 3 - Critical for user adoption and retention)

**Next Phase:** Phase 19 (Data Autonomy & Export) builds on autonomy awareness by providing concrete data ownership features.
