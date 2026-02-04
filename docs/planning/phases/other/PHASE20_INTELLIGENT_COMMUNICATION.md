# Phase 20: Intelligent Communication

**Status:** Planned  
**Duration:** 2-3 weeks total (sub-phased: 20a, 20b, 20c)  
**Prerequisites:** Phase 11 (Multi-Model Routing), Phase 13 (Pattern Learning), Phase 18 (Onboarding)  
**Enables:** Email/calendar intelligence, communication pattern learning, progressive autonomy for coordination work  
**Tier:** 4 (Advanced Communication)

---

## Table of Contents

1. [Overview](#overview)
2. [Marketing Context](#marketing-context)
3. [Goals](#goals)
4. [Phase Structure](#phase-structure)
5. [Phase 20a: Email Intelligence](#phase-20a-email-intelligence)
6. [Phase 20b: Calendar & Action Items](#phase-20b-calendar--action-items)
7. [Phase 20c: Progressive Autonomy](#phase-20c-progressive-autonomy)
8. [Success Criteria](#success-criteria)
9. [Integration Points](#integration-points)
10. [Risk & Mitigation](#risk--mitigation)
11. [Storage & Data Model](#storage--data-model)
12. [UI/UX Specifications](#uiux-specifications)

---

## Overview

Phase 20 extends Polly's intelligence to communication and coordination work—email, calendar, and action items. Unlike Jace.ai which creates permanent dependency, Polly approaches communication intelligence through the lens of **progressive autonomy**: start with full AI assistance, progressively teach patterns to run locally.

This phase is **NOT** about building another email client or calendar app. It's about:

1. **Pattern learning** - Understanding YOUR communication patterns
2. **Progressive automation** - Teaching local rules based on AI observations
3. **Action extraction** - Converting email/calendar into actionable knowledge
4. **Cross-domain integration** - Connecting communication to your knowledge work

### Scope Philosophy

**What Phase 20 IS:**
- ✅ Intelligent layer on top of existing email/calendar (via permissions)
- ✅ Pattern learning that becomes local rules over time
- ✅ Action item extraction feeding into knowledge system
- ✅ Communication intelligence that reduces over-coordination

**What Phase 20 is NOT:**
- ❌ Full email client replacement
- ❌ Calendar app replacement
- ❌ Permanent AI dependency for email management
- ❌ Communication-first positioning (Polly is polymathic work, not email management)

### Sub-Phase Structure

**Phase 20a: Email Intelligence (1 week)**
- Email parsing and categorization
- Sender importance learning
- Thread summarization
- Spam/noise filtering

**Phase 20b: Calendar & Action Items (1 week)**
- Meeting analysis and prep suggestions
- Action item extraction from email/meetings
- Calendar optimization suggestions
- Deadline and commitment tracking

**Phase 20c: Progressive Autonomy (3-5 days)**
- Pattern → Local rule conversion
- Communication autonomy dashboard
- Offline communication intelligence
- Reduced cloud dependency for coordination

Total duration: **2-3 weeks**

### Key Principles

- **Privacy-first** - Email content processed locally or with explicit consent
- **Progressive autonomy** - AI teaches, local rules execute
- **Integration, not replacement** - Works with Apple Mail, Gmail, Calendar
- **Polymathic context** - Connects communication to knowledge work
- **Anti-busywork** - Reduces coordination overhead, doesn't add it

---

## Marketing Context

### Positioning Alignment

**"Progressive autonomy for coordination work"**

Phase 20 extends Polly's progressive autonomy model to communication intelligence. While Jace.ai keeps you dependent on their AI for email management forever, Polly teaches you (and your local system) the patterns—then runs them locally.

### Competitive Differentiation

**vs. Jace.ai:**
- **Jace.ai:** Permanent AI dependency for email/calendar management
- **Polly:** Start with AI assistance, progressively build local automation
- **Jace.ai:** Communication-first positioning (email is the product)
- **Polly:** Polymathic work-first (communication is one component)
- **Jace.ai:** Ongoing subscription cost for coordination
- **Polly:** Coordination intelligence compounds locally over time

**Head-to-head messaging:**
"Jace.ai rents you an executive assistant. Polly helps you build communication systems that run themselves. Both handle email and calendar—but only Polly is designed for progressive autonomy."

**vs. SaneBox / Hey / Superhuman:**
- They're email clients with smart features
- Polly is knowledge infrastructure that includes communication intelligence
- They force you into their app; Polly works with your existing tools
- They focus on inbox management; Polly connects communication to knowledge work

**vs. Reclaim.ai / Motion / Clockwise:**
- They're calendar optimization tools
- Polly learns YOUR patterns and teaches local rules
- They require ongoing AI dependency; Polly builds local capability
- They're single-purpose; Polly connects calendar to broader work context

### Target Audience Fit

**Polymaths/Cross-Domain Workers:**
- Communication often spans multiple projects and domains
- Need to connect email/meetings to relevant knowledge areas
- Value context-aware action extraction ("This email relates to Research + Coding domains")

**ADHD/Neurodivergent Users:**
- Email overwhelm is a major pain point
- Action item extraction reduces working memory burden
- Automatic categorization reduces decision fatigue
- Meeting prep suggestions reduce context-switching cost

**Privacy-Conscious Professionals:**
- Local email processing (no cloud leakage)
- Explicit consent for any cloud analysis
- Progressive shift to local rules (less data exposure over time)
- Self-hostable communication intelligence

### Key Marketing Messages

**"Stop managing email. Start extracting value."**
- Email is input to your knowledge system, not a separate app
- Action items flow into your work, not stuck in threads
- Meetings connect to projects, not isolated calendar blocks

**"Communication intelligence that compounds."**
- Week 1: AI categorizes your email
- Week 12: Local rules handle 70% of categorization
- Week 52: Sophisticated local patterns + selective AI queries

**"Jace.ai for people who want to own their systems."**
- Full Jace.ai-like scope (email, calendar, action items)
- But designed for progressive autonomy, not permanent dependency
- Build capability, don't rent it

---

## Goals

### Primary Objectives

1. **Email intelligence** - Parse, categorize, summarize email with privacy-first architecture
2. **Calendar intelligence** - Meeting prep, optimization, deadline tracking
3. **Action extraction** - Convert communication into actionable knowledge
4. **Pattern learning** - Understand user's communication patterns
5. **Progressive autonomy** - Teach local rules that replace AI over time
6. **Cross-domain integration** - Connect communication to knowledge work

### Success Metrics

**Email Intelligence:**
- Categorization accuracy: >85% after 2 weeks of learning
- User corrections: <5 per day after 1 month
- Thread summarization quality: >4/5 user rating
- Time saved on email triage: >30 minutes/week (self-reported)

**Calendar Intelligence:**
- Meeting prep suggestions used: >60% of meetings
- Calendar optimization suggestions accepted: >40%
- Deadline detection accuracy: >90%

**Action Extraction:**
- Action items detected: >80% of actual commitments (manual validation)
- False positive rate: <10%
- Action items integrated into work: >70% (user engagement metric)

**Progressive Autonomy:**
- Communication patterns → local rules: >50% of decisions local by Month 3
- Token usage for communication: Declining 30%+ over 6 months
- User satisfaction with autonomy: >4/5 rating

---

## Phase Structure

Phase 20 is split into three sub-phases for clearer milestones and progressive capability building:

| Sub-Phase | Duration | Focus | Key Deliverables |
|-----------|----------|-------|------------------|
| **20a** | 1 week | Email Intelligence | Parsing, categorization, summarization, filtering |
| **20b** | 1 week | Calendar & Actions | Meeting analysis, action extraction, deadline tracking |
| **20c** | 3-5 days | Progressive Autonomy | Pattern → rule conversion, autonomy dashboard, offline |

---

## Phase 20a: Email Intelligence

**Duration:** 1 week  
**Focus:** Email parsing, categorization, summarization, noise filtering

### Goals

1. Parse email from Apple Mail / Gmail with privacy-first architecture
2. Categorize email by importance, domain relevance, and urgency
3. Summarize long threads into actionable insights
4. Filter noise (newsletters, notifications, low-priority) automatically
5. Learn sender importance based on user behavior

### Technical Approach

#### Email Access Architecture

**Option A: macOS Mail Permissions (Phase 9)**
- Request Full Disk Access (already done in Phase 9)
- Read from `~/Library/Mail/` (mbox format)
- Parse email locally, no cloud transmission
- Real-time monitoring via FSEvents

**Option B: Gmail API (OAuth)**
- Use Gmail API with read-only scope
- Fetch email metadata + body
- Process locally or with explicit user consent for cloud
- Webhook for real-time updates

**Option C: IMAP (Universal)**
- Standard IMAP protocol for any email provider
- Local processing by default
- Most compatible, least feature-rich

**Recommendation:** Support all three, default to macOS Mail (local-first)

#### Email Parsing

```typescript
interface Email {
  id: string;
  threadId: string;
  
  // Basic metadata
  from: EmailAddress;
  to: EmailAddress[];
  cc: EmailAddress[];
  subject: string;
  body: string;
  bodyHTML: string;
  
  // Timestamps
  receivedAt: Date;
  sentAt: Date;
  
  // Classification (computed)
  category: 'important' | 'action-required' | 'informational' | 'noise';
  domains: string[]; // Which Polly domains this relates to
  urgency: 'high' | 'medium' | 'low';
  
  // Extracted data
  actionItems: ActionItem[];
  people: Person[];
  topics: string[];
  
  // Sender intelligence
  senderImportance: number; // 0-1 score
  responseNeeded: boolean;
  estimatedReadTime: number; // seconds
}

interface EmailAddress {
  email: string;
  name?: string;
}
```

#### Categorization Engine

**Categorization Logic:**

1. **Sender Importance**
   - Frequency of user replies to sender
   - How quickly user usually responds
   - Manual importance overrides
   - Org chart position (if available)

2. **Content Analysis**
   - Keywords: "urgent", "deadline", "ASAP", "action required"
   - Questions directed at user
   - Deadlines and dates mentioned
   - Thread length and participation

3. **Domain Relevance**
   - Match email topics to Polly domains
   - "This email relates to Coding + Research domains"
   - Cross-domain emails flagged for polymathic attention

4. **Historical Patterns**
   - Similar emails user engaged with previously
   - Time-of-day patterns (morning emails more urgent?)
   - Day-of-week patterns (Friday emails less urgent?)

**Categories:**

- **Important:** Requires attention, likely response needed
- **Action Required:** Contains explicit tasks or deadlines
- **Informational:** Useful context, no immediate action
- **Noise:** Newsletters, notifications, automated messages

```typescript
class EmailCategorizer {
  async categorize(email: Email, userContext: UserContext): Promise<EmailCategory> {
    // 1. Sender importance
    const senderScore = await this.calculateSenderImportance(email.from, userContext);
    
    // 2. Content analysis
    const contentFeatures = await this.analyzeContent(email.body);
    
    // 3. Domain relevance
    const domainRelevance = await this.matchDomains(email, userContext.domains);
    
    // 4. Historical patterns
    const historicalSignals = await this.getHistoricalPatterns(email, userContext);
    
    // 5. ML model or LLM classification
    const category = await this.classify({
      senderScore,
      contentFeatures,
      domainRelevance,
      historicalSignals,
    });
    
    return category;
  }
  
  private async calculateSenderImportance(sender: EmailAddress, context: UserContext): Promise<number> {
    const sent = await this.countEmailsFrom(sender);
    const replied = await this.countRepliesTo(sender);
    const avgResponseTime = await this.getAvgResponseTime(sender);
    
    // High reply rate + fast responses = important sender
    const replyRate = replied / sent;
    const quickResponder = avgResponseTime < 3600; // < 1 hour
    
    let score = replyRate * 0.6;
    if (quickResponder) score += 0.3;
    if (context.vips.includes(sender.email)) score += 0.1;
    
    return Math.min(score, 1.0);
  }
}
```

#### Thread Summarization

For long email threads (5+ messages), generate concise summaries:

```typescript
interface ThreadSummary {
  threadId: string;
  subject: string;
  participantCount: number;
  messageCount: number;
  
  // Generated summary
  summary: string; // 2-3 sentences
  keyPoints: string[]; // Bullet points
  decisions: string[]; // Explicit decisions made
  actionItems: ActionItem[]; // Extracted actions
  
  // Metadata
  lastActivity: Date;
  requiresResponse: boolean;
  estimatedReadTime: number;
}

// Example summary:
{
  threadId: "thread-123",
  subject: "Q4 Planning Discussion",
  summary: "Team discussing Q4 roadmap priorities. Sarah proposed focusing on performance improvements. Decision pending on resource allocation.",
  keyPoints: [
    "Performance improvements proposed as Q4 priority",
    "Resource allocation decision needed by Friday",
    "Marketing team needs technical estimate by Wednesday"
  ],
  decisions: [
    "Feature freeze begins Oct 1"
  ],
  actionItems: [
    { task: "Provide technical estimate to marketing", assignee: "you", due: "Wednesday" }
  ],
  requiresResponse: true
}
```

**Implementation:**
```typescript
class ThreadSummarizer {
  async summarize(thread: Email[]): Promise<ThreadSummary> {
    // Sort by date
    const sorted = thread.sort((a, b) => a.sentAt.getTime() - b.sentAt.getTime());
    
    // Extract key content (skip signatures, quotes)
    const keyContent = sorted.map(email => this.extractKeyContent(email.body));
    
    // Use LLM for summarization (local or cloud based on user preference)
    const summary = await this.llm.summarize({
      prompt: `Summarize this email thread in 2-3 sentences. Extract key points, decisions, and action items.`,
      content: keyContent.join('\n\n---\n\n'),
    });
    
    return {
      threadId: thread[0].threadId,
      subject: thread[0].subject,
      participantCount: this.countUniqueParticipants(thread),
      messageCount: thread.length,
      summary: summary.text,
      keyPoints: summary.keyPoints,
      decisions: summary.decisions,
      actionItems: summary.actionItems,
      lastActivity: sorted[sorted.length - 1].sentAt,
      requiresResponse: this.detectResponseNeeded(thread),
      estimatedReadTime: this.estimateReadTime(keyContent),
    };
  }
}
```

#### Noise Filtering

Automatically detect and filter low-priority email:

**Noise Patterns:**
- Newsletters (unsubscribe link + commercial sender)
- Automated notifications (no-reply@, noreply@)
- Social media notifications (twitter.com, linkedin.com)
- Marketing emails (bulk sender, promotional content)
- Receipts and confirmations (already acted upon)

**User Learning:**
- If user never opens emails from sender → noise
- If user archives without reading → likely noise
- If user unsubscribes → definitely noise
- Manual "mark as noise" overrides

```typescript
interface NoiseFilter {
  isNoise(email: Email, userHistory: UserHistory): boolean;
  
  learnFromBehavior(email: Email, action: UserAction): void;
}

class SmartNoiseFilter implements NoiseFilter {
  isNoise(email: Email, userHistory: UserHistory): boolean {
    // Hard rules
    if (this.isNewsletter(email)) return true;
    if (this.isAutomatedNotification(email)) return true;
    if (userHistory.markedAsNoise.includes(email.from.email)) return true;
    
    // Learned patterns
    const engagementRate = this.getSenderEngagementRate(email.from, userHistory);
    if (engagementRate < 0.05 && this.getSenderEmailCount(email.from) > 10) {
      return true; // User never engages with this sender
    }
    
    return false;
  }
  
  private isNewsletter(email: Email): boolean {
    return email.body.includes('unsubscribe') && 
           email.from.email.includes('newsletter' || 'marketing');
  }
  
  private isAutomatedNotification(email: Email): boolean {
    return email.from.email.startsWith('no-reply') || 
           email.from.email.startsWith('noreply');
  }
}
```

### Week Breakdown (Phase 20a)

**Day 1-2: Email Access & Parsing**
- Implement Apple Mail parsing (mbox format)
- Build Gmail API integration (OAuth)
- Create email data model
- Test parsing on real email data

**Day 3-4: Categorization Engine**
- Build sender importance calculation
- Implement content analysis (keywords, urgency detection)
- Create domain relevance matching
- Initial categorization logic (rule-based + ML)

**Day 5: Thread Summarization & Noise Filtering**
- Implement thread summarization with LLM
- Build noise detection patterns
- Create user behavior learning system
- Test on real threads

**Day 6-7: UI & Polish**
- Email inbox view with categories
- Thread summary cards
- Sender importance indicators
- Noise filter controls
- Testing and refinement

### Deliverables (Phase 20a)

- [ ] Email parsing from Apple Mail and Gmail
- [ ] Categorization engine (important / action / info / noise)
- [ ] Sender importance learning
- [ ] Thread summarization for long threads
- [ ] Noise filtering with user learning
- [ ] Email inbox UI with smart categories
- [ ] Privacy-first architecture (local processing default)

---

## Phase 20b: Calendar & Action Items

**Duration:** 1 week  
**Focus:** Meeting analysis, action extraction, deadline tracking, calendar optimization

### Goals

1. Parse calendar events from Apple Calendar / Google Calendar
2. Analyze meetings and suggest prep materials
3. Extract action items from email and meetings
4. Track deadlines and commitments
5. Suggest calendar optimizations
6. Connect calendar events to Polly domains

### Technical Approach

#### Calendar Access

**Option A: macOS Calendar (CalendarStore framework)**
- Request Calendar permissions (Phase 9)
- Read events via EventKit
- Real-time event monitoring
- Local processing

**Option B: Google Calendar API**
- OAuth with read/write scope
- Fetch events via Calendar API
- Webhook for real-time updates

**Recommendation:** Support both, default to macOS Calendar

#### Meeting Intelligence

```typescript
interface Meeting {
  id: string;
  
  // Basic metadata
  title: string;
  description: string;
  location: string;
  startTime: Date;
  endTime: Date;
  duration: number; // minutes
  
  // Participants
  organizer: Person;
  attendees: Person[];
  optional: Person[];
  
  // Classification
  type: 'sync' | 'decision' | 'brainstorm' | 'presentation' | 'one-on-one';
  domains: string[]; // Related Polly domains
  projects: string[]; // Related projects (if tracked)
  
  // Intelligence
  prepNeeded: boolean;
  prepSuggestions: PrepSuggestion[];
  relatedNotes: string[]; // Note IDs
  relatedEmails: string[]; // Email IDs
  
  // Follow-up
  actionItems: ActionItem[];
  decisions: string[];
  followUpNeeded: boolean;
}

interface PrepSuggestion {
  type: 'note' | 'email' | 'document' | 'reminder';
  title: string;
  content: string;
  relevance: number; // 0-1
}
```

#### Meeting Prep Suggestions

Before meetings, suggest relevant context:

```typescript
class MeetingPrepAnalyzer {
  async analyzeMeeting(meeting: Meeting, userContext: UserContext): Promise<PrepSuggestion[]> {
    const suggestions: PrepSuggestion[] = [];
    
    // 1. Find related notes based on meeting title/description
    const relatedNotes = await this.findRelatedNotes(meeting, userContext);
    for (const note of relatedNotes) {
      suggestions.push({
        type: 'note',
        title: note.title,
        content: `Review note about ${note.topic}`,
        relevance: note.relevanceScore,
      });
    }
    
    // 2. Find recent email threads with attendees
    const recentThreads = await this.findRecentThreads(meeting.attendees, userContext);
    for (const thread of recentThreads) {
      suggestions.push({
        type: 'email',
        title: thread.subject,
        content: `Recent discussion with ${thread.participants}`,
        relevance: thread.relevanceScore,
      });
    }
    
    // 3. Identify open action items with attendees
    const openActions = await this.findOpenActions(meeting.attendees, userContext);
    if (openActions.length > 0) {
      suggestions.push({
        type: 'reminder',
        title: 'Open action items',
        content: `${openActions.length} open items to discuss`,
        relevance: 0.8,
      });
    }
    
    // 4. Surface previous meeting notes
    const previousMeetings = await this.findPreviousMeetings(meeting, userContext);
    for (const prev of previousMeetings) {
      suggestions.push({
        type: 'note',
        title: `Previous meeting: ${prev.title}`,
        content: `Last met ${formatDate(prev.date)}`,
        relevance: 0.7,
      });
    }
    
    return suggestions.sort((a, b) => b.relevance - a.relevance).slice(0, 5);
  }
}
```

**Example Prep UI:**
```
┌────────────────────────────────────────────────────┐
│  Meeting in 30 minutes: Q4 Planning                │
├────────────────────────────────────────────────────┤
│                                                     │
│  Suggested Prep:                                   │
│                                                     │
│  📝 Review: "Q4 Roadmap Draft" (Research)          │
│  📧 Recent thread: "Budget discussion" with Sarah  │
│  ✅ 2 open action items to discuss                 │
│  📝 Previous meeting notes from Oct 15             │
│                                                     │
│  [Open All] [Dismiss]                              │
└────────────────────────────────────────────────────┘
```

#### Action Item Extraction

Extract commitments from email and meetings:

```typescript
interface ActionItem {
  id: string;
  
  // What
  task: string;
  description?: string;
  
  // Who
  assignee: 'me' | 'other';
  assigneeName?: string;
  
  // When
  dueDate?: Date;
  dueDateFuzzy?: string; // "next week", "Friday", "end of month"
  createdAt: Date;
  
  // Where (source)
  source: 'email' | 'meeting' | 'note';
  sourceId: string;
  
  // Context
  domains: string[];
  project?: string;
  relatedNotes: string[];
  
  // Status
  status: 'open' | 'in-progress' | 'completed' | 'cancelled';
  completedAt?: Date;
}

class ActionExtractor {
  async extractFromEmail(email: Email): Promise<ActionItem[]> {
    const actions: ActionItem[] = [];
    
    // Use LLM to extract action items
    const extracted = await this.llm.extract({
      prompt: `Extract action items from this email. For each action, identify:
        - The task description
        - Who is responsible (the recipient, sender, or someone else)
        - Any mentioned deadline or due date
        - Confidence score (0-1)`,
      content: email.body,
    });
    
    for (const item of extracted.actions) {
      if (item.confidence > 0.7) {
        actions.push({
          id: generateId(),
          task: item.task,
          assignee: item.assignee === 'recipient' ? 'me' : 'other',
          assigneeName: item.assigneeName,
          dueDate: item.dueDate,
          dueDateFuzzy: item.dueDateFuzzy,
          createdAt: email.receivedAt,
          source: 'email',
          sourceId: email.id,
          domains: email.domains,
          status: 'open',
        });
      }
    }
    
    return actions;
  }
  
  async extractFromMeeting(meeting: Meeting, meetingNotes?: string): Promise<ActionItem[]> {
    // Extract from meeting description + notes if available
    const content = [meeting.description, meetingNotes].filter(Boolean).join('\n\n');
    
    const extracted = await this.llm.extract({
      prompt: `Extract action items from this meeting. Identify tasks, owners, and deadlines.`,
      content,
    });
    
    return this.convertToActionItems(extracted, meeting);
  }
}
```

**Action Item UI:**
```
┌────────────────────────────────────────────────────┐
│  Action Items                                      │
├────────────────────────────────────────────────────┤
│                                                     │
│  ☐ Provide technical estimate to marketing        │
│     Due: Wednesday  |  From: Q4 Planning email    │
│     Domain: Coding                                 │
│                                                     │
│  ☐ Review Sarah's design mockups                   │
│     Due: End of week  |  From: Design sync meeting│
│     Domain: Creative                               │
│                                                     │
│  ☐ Update roadmap document                         │
│     Due: Next Monday  |  From: Roadmap thread     │
│     Domains: Research, Coding                      │
│                                                     │
│  [+ Add Action Item]                               │
└────────────────────────────────────────────────────┘
```

#### Deadline Tracking

Track all commitments with deadlines:

```typescript
interface Deadline {
  id: string;
  
  // What
  title: string;
  description?: string;
  
  // When
  dueDate: Date;
  reminder?: Date; // When to remind user
  
  // Source
  source: 'email' | 'meeting' | 'note' | 'manual';
  sourceId: string;
  
  // Context
  domains: string[];
  relatedActionItems: string[];
  
  // Status
  status: 'upcoming' | 'due-soon' | 'overdue' | 'completed';
  completedAt?: Date;
}

class DeadlineTracker {
  async detectDeadlines(content: string, context: any): Promise<Deadline[]> {
    // Extract date references
    const dates = this.extractDates(content); // "Friday", "next week", "Oct 30"
    
    // Use LLM to understand context
    const deadlines = await this.llm.extract({
      prompt: `Identify deadlines in this content. For each deadline, extract:
        - What needs to be done
        - When it's due
        - Who is responsible`,
      content,
    });
    
    return this.convertToDeadlines(deadlines, context);
  }
  
  private extractDates(text: string): Date[] {
    // Use chrono-node or similar for date parsing
    return chronoParse(text);
  }
}
```

#### Calendar Optimization

Suggest calendar improvements:

```typescript
interface CalendarOptimization {
  type: 'too-fragmented' | 'no-focus-time' | 'back-to-back' | 'meeting-overload';
  severity: 'low' | 'medium' | 'high';
  description: string;
  suggestion: string;
  affectedEvents: string[]; // Meeting IDs
}

class CalendarOptimizer {
  async analyzeWeek(events: Meeting[]): Promise<CalendarOptimization[]> {
    const optimizations: CalendarOptimization[] = [];
    
    // 1. Detect fragmented focus time
    const fragments = this.findTimeFragments(events);
    if (fragments.some(f => f.duration < 60)) {
      optimizations.push({
        type: 'too-fragmented',
        severity: 'high',
        description: 'Your calendar has many short gaps (<1h) that are hard to use productively.',
        suggestion: 'Consider clustering meetings to create larger focus blocks.',
        affectedEvents: fragments.map(f => f.adjacentMeetings).flat(),
      });
    }
    
    // 2. Detect lack of focus time
    const focusTime = this.calculateFocusTime(events);
    if (focusTime < 10) { // <10 hours per week
      optimizations.push({
        type: 'no-focus-time',
        severity: 'high',
        description: 'You have less than 10 hours of uninterrupted focus time this week.',
        suggestion: 'Block dedicated focus time or decline some meetings.',
        affectedEvents: [],
      });
    }
    
    // 3. Detect back-to-back meetings
    const backToBack = this.findBackToBackMeetings(events);
    if (backToBack.length > 3) {
      optimizations.push({
        type: 'back-to-back',
        severity: 'medium',
        description: `${backToBack.length} instances of back-to-back meetings with no break.`,
        suggestion: 'Add 5-10 minute buffers between meetings for breaks and context switching.',
        affectedEvents: backToBack.flat(),
      });
    }
    
    return optimizations;
  }
}
```

### Week Breakdown (Phase 20b)

**Day 1-2: Calendar Access & Meeting Intelligence**
- Implement calendar parsing (Apple Calendar + Google Calendar)
- Build meeting data model
- Create meeting type classification
- Implement meeting prep suggestions

**Day 3-4: Action Item Extraction**
- Build action item extraction from email
- Implement action item extraction from meetings
- Create action item tracking system
- Build action item UI

**Day 5: Deadline Tracking & Calendar Optimization**
- Implement deadline detection
- Build deadline reminder system
- Create calendar optimization analyzer
- Test on real calendar data

**Day 6-7: Integration & Polish**
- Connect action items to knowledge graph
- Link meetings to relevant domains
- Calendar optimization UI
- Testing and refinement

### Deliverables (Phase 20b)

- [ ] Calendar event parsing (Apple Calendar + Google Calendar)
- [ ] Meeting prep suggestions with related context
- [ ] Action item extraction from email and meetings
- [ ] Action item tracking and UI
- [ ] Deadline detection and tracking
- [ ] Calendar optimization suggestions
- [ ] Cross-domain integration (meetings → domains)

---

## Phase 20c: Progressive Autonomy

**Duration:** 3-5 days  
**Focus:** Pattern → local rule conversion, communication autonomy, reduced cloud dependency

### Goals

1. Convert learned communication patterns into local rules
2. Build communication-specific autonomy dashboard
3. Enable offline communication intelligence
4. Reduce cloud dependency for email/calendar over time
5. Export communication patterns (data ownership)

### Technical Approach

#### Pattern → Local Rule Conversion

After observing user behavior, convert AI decisions into local rules:

```typescript
interface CommunicationPattern {
  id: string;
  type: 'sender-importance' | 'categorization' | 'noise-filter' | 'meeting-decline';
  
  // Pattern description
  name: string;
  description: string;
  
  // Learned from observations
  observations: number;
  confidence: number; // 0-1
  
  // Rule logic
  conditions: RuleCondition[];
  action: RuleAction;
  
  // Metadata
  learnedAt: Date;
  lastApplied: Date;
  applicationCount: number;
  userCorrections: number;
}

interface RuleCondition {
  field: 'sender' | 'subject' | 'body' | 'time' | 'attendees';
  operator: 'equals' | 'contains' | 'matches' | 'before' | 'after';
  value: any;
}

interface RuleAction {
  type: 'categorize' | 'archive' | 'flag' | 'decline' | 'suggest-time';
  parameters: any;
}

// Example patterns:
const EXAMPLE_PATTERNS: CommunicationPattern[] = [
  {
    id: 'pattern-1',
    type: 'sender-importance',
    name: 'Sarah is important',
    description: 'You always respond quickly to emails from Sarah',
    observations: 47,
    confidence: 0.95,
    conditions: [
      { field: 'sender', operator: 'equals', value: 'sarah@example.com' }
    ],
    action: {
      type: 'categorize',
      parameters: { category: 'important' }
    },
    learnedAt: new Date('2026-01-10'),
    lastApplied: new Date('2026-01-24'),
    applicationCount: 23,
    userCorrections: 0,
  },
  {
    id: 'pattern-2',
    type: 'noise-filter',
    name: 'LinkedIn notifications are noise',
    description: 'You never open LinkedIn notification emails',
    observations: 34,
    confidence: 1.0,
    conditions: [
      { field: 'sender', operator: 'contains', value: 'linkedin.com' },
      { field: 'subject', operator: 'contains', value: 'notification' }
    ],
    action: {
      type: 'archive',
      parameters: { category: 'noise' }
    },
    learnedAt: new Date('2026-01-05'),
    lastApplied: new Date('2026-01-24'),
    applicationCount: 34,
    userCorrections: 0,
  },
  {
    id: 'pattern-3',
    type: 'meeting-decline',
    name: 'Decline large all-hands meetings on Fridays',
    description: 'You typically decline all-hands meetings scheduled on Fridays',
    observations: 8,
    confidence: 0.87,
    conditions: [
      { field: 'subject', operator: 'contains', value: 'all-hands' },
      { field: 'attendees', operator: 'greater-than', value: 20 },
      { field: 'time', operator: 'day-of-week', value: 'Friday' }
    ],
    action: {
      type: 'suggest-time',
      parameters: { suggestion: 'Decline and suggest watching recording' }
    },
    learnedAt: new Date('2026-01-18'),
    lastApplied: new Date('2026-01-22'),
    applicationCount: 3,
    userCorrections: 0,
  },
];
```

**Pattern Learning Process:**

1. **Observation Phase** (Weeks 1-4)
   - AI makes categorization decisions
   - User corrections tracked
   - Consistent behaviors identified

2. **Pattern Detection** (Week 4+)
   - Identify recurring decision patterns
   - Calculate confidence based on consistency
   - Generate rule candidates

3. **Rule Promotion** (Week 6+)
   - High-confidence patterns (>0.85) become local rules
   - User notified: "I've learned you always categorize emails from Sarah as important. Apply this rule automatically?"
   - User can approve, reject, or modify

4. **Local Execution** (Week 8+)
   - Rules run locally without AI
   - Significant token savings
   - User retains override capability

**Implementation:**
```typescript
class PatternLearner {
  async learnPatterns(userId: string): Promise<CommunicationPattern[]> {
    const decisions = await this.getUserDecisions(userId);
    const patterns: CommunicationPattern[] = [];
    
    // Group decisions by type
    const groupedByType = this.groupByType(decisions);
    
    for (const [type, decisions] of Object.entries(groupedByType)) {
      // Find consistent patterns
      const clusters = this.clusterSimilarDecisions(decisions);
      
      for (const cluster of clusters) {
        if (cluster.consistency > 0.85 && cluster.count > 5) {
          const pattern = this.generatePattern(cluster);
          patterns.push(pattern);
        }
      }
    }
    
    return patterns;
  }
  
  async promoteToRule(pattern: CommunicationPattern): Promise<void> {
    // Notify user
    await this.notifyUser({
      title: 'New Pattern Learned',
      message: `${pattern.description}. Apply this rule automatically?`,
      actions: ['Approve', 'Modify', 'Reject'],
    });
    
    // If approved, create local rule
    if (await this.userApproves(pattern.id)) {
      await this.createLocalRule(pattern);
    }
  }
}
```

#### Communication Autonomy Dashboard

Track progressive autonomy specifically for communication:

```
┌────────────────────────────────────────────────────┐
│  Communication Autonomy                            │
├────────────────────────────────────────────────────┤
│                                                     │
│  Local Patterns: 23 active rules                   │
│  Token Usage: 72% local ↑                          │
│  Email Categorization: 85% automated               │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │ Email Categorization                         │ │
│  │ ████████████████░░░░ 85% local               │ │
│  │                                               │ │
│  │ 23 patterns learned, 156 emails/week handled │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │ Active Patterns                              │ │
│  │                                               │ │
│  │ • Sarah emails → Important (47 applications) │ │
│  │ • LinkedIn notifications → Noise (34 apps)   │ │
│  │ • All-hands Fridays → Decline suggestion     │ │
│  │                                               │ │
│  │ [View All Patterns →]                        │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  Token Savings: $12/month vs. full AI processing  │
│                                                     │
└────────────────────────────────────────────────────┘
```

#### Offline Communication Intelligence

Enable core communication features to work offline:

**Offline Capable:**
- ✅ Apply learned patterns (local rules)
- ✅ Categorize email based on sender rules
- ✅ Filter noise automatically
- ✅ View action items and deadlines
- ✅ Parse new emails (local parsing)

**Requires Cloud (queued when offline):**
- ⚠️ Thread summarization (LLM-based)
- ⚠️ Action item extraction (LLM-based)
- ⚠️ Meeting prep suggestions (requires context search)

### Week Breakdown (Phase 20c)

**Day 1-2: Pattern Learning & Rule Conversion**
- Implement pattern detection algorithm
- Build pattern → rule conversion
- Create user approval flow for new rules
- Test pattern learning on real data

**Day 3: Communication Autonomy Dashboard**
- Build dashboard UI
- Display active patterns and stats
- Show token savings calculation
- Add pattern management (edit/disable rules)

**Day 4-5: Offline Mode & Testing**
- Implement offline rule execution
- Create offline communication UI indicators
- Build pattern export (data ownership)
- Comprehensive testing
- Bug fixes and polish

### Deliverables (Phase 20c)

- [ ] Pattern learning system (observations → patterns)
- [ ] Pattern → local rule conversion
- [ ] User approval flow for new patterns
- [ ] Communication autonomy dashboard
- [ ] Active pattern management UI
- [ ] Offline communication intelligence
- [ ] Pattern export capability
- [ ] Token savings calculation and display

---

## Success Criteria

### Functional Requirements (All Sub-Phases)

**Must Have:**
- [ ] Email parsing from Apple Mail and Gmail
- [ ] Email categorization (important / action / info / noise)
- [ ] Thread summarization for long threads
- [ ] Noise filtering with learning
- [ ] Calendar event parsing
- [ ] Meeting prep suggestions
- [ ] Action item extraction from email and meetings
- [ ] Deadline tracking
- [ ] Pattern learning from user behavior
- [ ] Pattern → local rule conversion
- [ ] Communication autonomy dashboard
- [ ] Offline communication intelligence (rules work offline)

**Should Have:**
- [ ] Calendar optimization suggestions
- [ ] Multi-domain email classification
- [ ] Action item completion tracking
- [ ] Deadline reminders
- [ ] Pattern approval workflow
- [ ] Token savings calculation
- [ ] Communication pattern export

**Nice to Have:**
- [ ] Email response suggestions
- [ ] Meeting recording transcription
- [ ] Automatic meeting notes generation
- [ ] Calendar conflicts resolution
- [ ] Smart meeting scheduling assistant

### Performance Requirements

- Email categorization: <500ms per email
- Thread summarization: <5 seconds for 20-message thread
- Action item extraction: <3 seconds per email
- Pattern detection: Runs daily in background, <30 seconds
- Offline rule application: <100ms per email

### Privacy Requirements

- Email content processed locally by default
- Explicit user consent for cloud processing
- Email data never stored on cloud without permission
- Pattern data exportable at any time
- Self-hostable communication intelligence

### User Experience Requirements

- Email categorization accuracy: >85% after 2 weeks
- User corrections: <5 per day after 1 month
- Pattern learning: 15+ patterns by Month 2
- Local rule coverage: >50% of decisions by Month 3
- User satisfaction: >4/5 rating for communication intelligence

---

## Integration Points

### Phase 9: macOS Permissions
- Request Mail and Calendar permissions
- Access mail database and calendar events
- Real-time monitoring via FSEvents

### Phase 11: Multi-Model Routing
- Email summarization routes to appropriate model
- Action extraction uses smart routing
- Pattern learning feeds confidence scores

### Phase 13: Pattern Learning
- Communication patterns stored alongside knowledge patterns
- Shared pattern learning infrastructure
- Cross-domain pattern recognition

### Phase 16: Native Notes
- Meeting notes created as Polly notes
- Action items link to relevant notes
- Email content captured in notes

### Phase 18: Onboarding
- Communication intelligence revealed progressively
- Autonomy dashboard includes communication metrics
- Tutorial for email/calendar integration

### Phase 19: Data Autonomy
- Communication patterns exportable
- Email categorization rules portable
- Self-hosting includes communication intelligence

---

## Risk & Mitigation

### Risk 1: Privacy Concerns with Email Processing
**Impact:** High  
**Probability:** Medium

**Mitigation:**
- Local processing by default (no cloud)
- Explicit consent for any cloud processing
- Clear privacy policy and data handling docs
- Self-hosting option for maximum privacy
- Open source email processing code

### Risk 2: Categorization Accuracy Insufficient
**Impact:** High  
**Probability:** Medium

**Mitigation:**
- Multi-signal categorization (sender + content + historical)
- User corrections feed back into model
- Conservative confidence thresholds (ask user if unsure)
- Gradual learning over weeks (don't rush)
- A/B testing different approaches

### Risk 3: Pattern Learning Creates False Rules
**Impact:** Medium  
**Probability:** Medium

**Mitigation:**
- High confidence threshold for rule promotion (>0.85)
- Minimum observation count before pattern consideration (>5)
- User approval required for all rules
- Easy disable/delete for bad rules
- Track user corrections and adjust

### Risk 4: Overwhelms Users with Action Items
**Impact:** Medium  
**Probability:** High

**Mitigation:**
- Conservative extraction (high confidence only)
- User can dismiss irrelevant items
- Learn from dismissals (reduce false positives)
- Smart prioritization (urgent first)
- Option to disable action extraction

### Risk 5: Integration Complexity (Multiple Email/Calendar Providers)
**Impact:** Medium  
**Probability:** High

**Mitigation:**
- Start with Apple Mail + Calendar (simplest)
- Add Gmail/Google Calendar as Phase 2
- Standardized internal format (adapt at edges)
- Comprehensive testing on each provider
- Clear documentation of supported systems

---

## Storage & Data Model

### Email Storage

```sql
CREATE TABLE emails (
  id TEXT PRIMARY KEY,
  thread_id TEXT,
  user_id TEXT NOT NULL,
  
  -- Metadata
  from_email TEXT NOT NULL,
  from_name TEXT,
  to_emails TEXT, -- JSON array
  cc_emails TEXT, -- JSON array
  subject TEXT NOT NULL,
  body TEXT NOT NULL,
  body_html TEXT,
  
  -- Timestamps
  received_at TIMESTAMP NOT NULL,
  sent_at TIMESTAMP NOT NULL,
  
  -- Classification
  category TEXT CHECK(category IN ('important', 'action-required', 'informational', 'noise')),
  domains TEXT, -- JSON array of domain IDs
  urgency TEXT CHECK(urgency IN ('high', 'medium', 'low')),
  
  -- Computed
  sender_importance REAL,
  response_needed BOOLEAN,
  estimated_read_time INTEGER,
  
  -- Processing
  processed BOOLEAN DEFAULT FALSE,
  processed_at TIMESTAMP,
  
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_emails_user ON emails(user_id);
CREATE INDEX idx_emails_thread ON emails(thread_id);
CREATE INDEX idx_emails_received ON emails(received_at);
CREATE INDEX idx_emails_category ON emails(category);
```

### Meetings Storage

```sql
CREATE TABLE meetings (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  
  -- Basic metadata
  title TEXT NOT NULL,
  description TEXT,
  location TEXT,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NOT NULL,
  duration INTEGER, -- minutes
  
  -- Participants (JSON)
  organizer TEXT, -- JSON object
  attendees TEXT, -- JSON array
  optional TEXT, -- JSON array
  
  -- Classification
  meeting_type TEXT CHECK(meeting_type IN ('sync', 'decision', 'brainstorm', 'presentation', 'one-on-one')),
  domains TEXT, -- JSON array
  projects TEXT, -- JSON array
  
  -- Intelligence
  prep_needed BOOLEAN DEFAULT FALSE,
  prep_suggestions TEXT, -- JSON array
  related_notes TEXT, -- JSON array of note IDs
  related_emails TEXT, -- JSON array of email IDs
  
  -- Follow-up
  action_items TEXT, -- JSON array
  decisions TEXT, -- JSON array
  follow_up_needed BOOLEAN DEFAULT FALSE,
  
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_meetings_user ON meetings(user_id);
CREATE INDEX idx_meetings_start ON meetings(start_time);
```

### Action Items Storage

```sql
CREATE TABLE action_items (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  
  -- What
  task TEXT NOT NULL,
  description TEXT,
  
  -- Who
  assignee TEXT CHECK(assignee IN ('me', 'other')),
  assignee_name TEXT,
  
  -- When
  due_date TIMESTAMP,
  due_date_fuzzy TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  -- Where (source)
  source TEXT CHECK(source IN ('email', 'meeting', 'note')),
  source_id TEXT NOT NULL,
  
  -- Context
  domains TEXT, -- JSON array
  project TEXT,
  related_notes TEXT, -- JSON array
  
  -- Status
  status TEXT CHECK(status IN ('open', 'in-progress', 'completed', 'cancelled')),
  completed_at TIMESTAMP,
  
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_actions_user ON action_items(user_id);
CREATE INDEX idx_actions_status ON action_items(status);
CREATE INDEX idx_actions_due ON action_items(due_date);
```

### Communication Patterns Storage

```sql
CREATE TABLE communication_patterns (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  
  -- Pattern metadata
  type TEXT CHECK(type IN ('sender-importance', 'categorization', 'noise-filter', 'meeting-decline')),
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  
  -- Learning
  observations INTEGER DEFAULT 0,
  confidence REAL DEFAULT 0.0,
  
  -- Rule logic (JSON)
  conditions TEXT NOT NULL, -- JSON array
  action TEXT NOT NULL, -- JSON object
  
  -- Status
  status TEXT CHECK(status IN ('learning', 'candidate', 'active', 'disabled')),
  
  -- Metadata
  learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_applied TIMESTAMP,
  application_count INTEGER DEFAULT 0,
  user_corrections INTEGER DEFAULT 0,
  
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_patterns_user ON communication_patterns(user_id);
CREATE INDEX idx_patterns_status ON communication_patterns(status);
```

---

## UI/UX Specifications

### Email Inbox View

```
┌────────────────────────────────────────────────────┐
│  📧 Email Intelligence                             │
├────────────────────────────────────────────────────┤
│                                                     │
│  [Important] [Action Required] [Info] [Noise (23)]│
│                                                     │
│  Important (5)                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                     │
│  ⭐ Sarah Chen <sarah@example.com>                │
│     Q4 Planning Discussion                         │
│     "I've updated the roadmap based on..."         │
│     2 hours ago  |  Research, Coding               │
│                                                     │
│  ⭐ Mark Johnson <mark@example.com>                │
│     Budget Approval Needed                         │
│     "Can you review and approve by Friday?"        │
│     5 hours ago  |  ✅ Action Required             │
│                                                     │
│  Action Required (3)                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                     │
│  📋 Technical estimate request                     │
│     From: marketing@company.com                    │
│     Due: Wednesday  |  1 day ago                   │
│                                                     │
│  [Show Info (12)] [Show Noise (23)]                │
│                                                     │
└────────────────────────────────────────────────────┘
```

### Thread Summary View

```
┌────────────────────────────────────────────────────┐
│  Thread: Q4 Planning Discussion (8 messages)       │
├────────────────────────────────────────────────────┤
│                                                     │
│  Summary:                                          │
│  Team discussing Q4 roadmap priorities. Sarah      │
│  proposed focusing on performance improvements.    │
│  Decision pending on resource allocation.          │
│                                                     │
│  Key Points:                                       │
│  • Performance improvements proposed as priority   │
│  • Resource allocation decision needed by Friday   │
│  • Marketing needs technical estimate by Wed       │
│                                                     │
│  Decisions:                                        │
│  • Feature freeze begins Oct 1                     │
│                                                     │
│  Action Items:                                     │
│  ☐ Provide technical estimate to marketing (you)  │
│     Due: Wednesday                                 │
│                                                     │
│  Participants: Sarah, Mark, You, +2 others         │
│  Estimated read time: 6 minutes                    │
│                                                     │
│  [Read Full Thread] [Archive] [Reply]             │
│                                                     │
└────────────────────────────────────────────────────┘
```

### Meeting Prep Card

```
┌────────────────────────────────────────────────────┐
│  🔔 Meeting in 30 minutes                          │
├────────────────────────────────────────────────────┤
│                                                     │
│  Q4 Planning Meeting                               │
│  Today at 2:00 PM - 3:00 PM                        │
│  With: Sarah, Mark, Lisa (+3 others)               │
│                                                     │
│  Suggested Prep:                                   │
│                                                     │
│  📝 Q4 Roadmap Draft (Research)                    │
│     Created 3 days ago                             │
│     [Open →]                                       │
│                                                     │
│  📧 Budget discussion thread                       │
│     Recent conversation with Sarah                 │
│     [Open →]                                       │
│                                                     │
│  ✅ 2 open action items to discuss                 │
│     [View Items →]                                 │
│                                                     │
│  📝 Previous meeting notes (Oct 15)                │
│     [Open →]                                       │
│                                                     │
│  [Open All] [Dismiss] [Snooze]                     │
│                                                     │
└────────────────────────────────────────────────────┘
```

### Action Items Dashboard

```
┌────────────────────────────────────────────────────┐
│  ✅ Action Items                                   │
├────────────────────────────────────────────────────┤
│                                                     │
│  Due Today (2)                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                     │
│  ☐ Provide technical estimate to marketing        │
│     From: Q4 Planning email                        │
│     Domain: Coding  |  Due: 6 PM today            │
│                                                     │
│  ☐ Review Sarah's design mockups                   │
│     From: Design sync meeting                      │
│     Domain: Creative  |  Due: End of day          │
│                                                     │
│  This Week (5)                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                     │
│  ☐ Update roadmap document                         │
│     From: Roadmap thread                           │
│     Domains: Research, Coding  |  Due: Monday      │
│                                                     │
│  [Show All (12)] [+ Add Action Item]               │
│                                                     │
└────────────────────────────────────────────────────┘
```

### Communication Autonomy Dashboard

```
┌────────────────────────────────────────────────────┐
│  Communication Autonomy                            │
├────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │ Email Categorization: 85% Local              │ │
│  │ ████████████████████░░░░                     │ │
│  │                                               │ │
│  │ 23 active patterns                           │ │
│  │ 156 emails/week handled automatically        │ │
│  │ Token savings: $12/month                     │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  Active Patterns:                                  │
│                                                     │
│  ✓ Sarah emails → Important (47 applications)     │
│    Confidence: 95%  |  [Edit] [Disable]           │
│                                                     │
│  ✓ LinkedIn notifications → Noise (34 apps)       │
│    Confidence: 100%  |  [Edit] [Disable]          │
│                                                     │
│  ✓ All-hands Fridays → Decline suggestion         │
│    Confidence: 87%  |  [Edit] [Disable]           │
│                                                     │
│  [View All 23 Patterns →]                          │
│                                                     │
│  Pattern Learning:                                 │
│  🔍 5 potential patterns detected                  │
│     [Review Candidates →]                          │
│                                                     │
└────────────────────────────────────────────────────┘
```

### Pattern Approval Dialog

```
┌────────────────────────────────────────────────────┐
│  New Pattern Learned                               │
├────────────────────────────────────────────────────┤
│                                                     │
│  Polly has detected a consistent pattern in your   │
│  communication behavior:                           │
│                                                     │
│  📧 "You always categorize emails from Sarah as    │
│      Important"                                    │
│                                                     │
│  Observations: 47 emails                           │
│  Confidence: 95%                                   │
│  Corrections: 0                                    │
│                                                     │
│  Suggested Rule:                                   │
│  When email is from sarah@example.com              │
│  → Categorize as "Important"                       │
│                                                     │
│  Apply this rule automatically?                    │
│                                                     │
│  [Approve & Apply]  [Modify Rule]  [Reject]       │
│                                                     │
│  Note: You can disable or edit this rule anytime   │
│  in Communication Autonomy settings.               │
│                                                     │
└────────────────────────────────────────────────────┘
```

---

## Marketing Integration

### Positioning in Phase 20

**Core Message:** "Progressive autonomy for coordination work"

**Key Differentiators:**
1. Jace.ai-like scope (email, calendar, action items) but with progressive autonomy
2. Pattern learning that becomes local rules (not permanent AI dependency)
3. Privacy-first architecture (local processing default)
4. Integration, not replacement (works with existing tools)
5. Connects communication to polymathic knowledge work

### Marketing Touchpoints

**In Onboarding (Phase 18):**
- Communication intelligence revealed after core features
- "Stop managing email. Start extracting value." messaging
- Autonomy dashboard includes communication metrics

**In Data Ownership (Phase 19):**
- Communication patterns exportable
- Self-hosting includes email/calendar intelligence
- Privacy guarantees for email processing

**In Documentation:**
- Direct Jace.ai comparison page
- "Build capability, don't rent it" positioning
- Progressive autonomy case studies

### Competitive Messaging

**Landing Page Section:**
```
Jace.ai vs. Polly

Jace.ai rents you an executive assistant for email and calendar.
Polly helps you build communication systems that run themselves.

Both handle:
• Email categorization and summarization
• Calendar optimization
• Action item extraction
• Meeting preparation

But only Polly:
✓ Teaches local patterns that replace AI over time
✓ Reduces token costs as your system learns
✓ Processes email locally by default (privacy-first)
✓ Connects communication to your broader knowledge work
✓ Self-hostable and offline-capable

Progressive autonomy vs. permanent dependency.
```

---

## Future Enhancements (Post-Phase 20)

### Email Response Suggestions
- Draft responses based on communication patterns
- Learn user's writing style and common replies
- Suggest responses for common email types

### Meeting Recording & Transcription
- Integrate with meeting recording tools
- Automatic transcription and summarization
- Action item extraction from transcripts
- Meeting notes auto-generation

### Smart Scheduling Assistant
- Suggest optimal meeting times based on patterns
- Automatic calendar coordination
- Buffer time management
- Focus time protection

### Cross-Team Coordination
- Detect coordination patterns with teams
- Suggest communication improvements
- Identify bottlenecks and delays
- Team-level communication intelligence

### Multi-Language Support
- Email categorization in multiple languages
- Action item extraction across languages
- Meeting prep for international teams

---

## Conclusion

Phase 20 extends Polly's intelligence to communication and coordination work, competing directly with Jace.ai while maintaining Polly's core philosophy: **progressive autonomy over permanent dependency**.

**Key Innovations:**
1. **Pattern → Rule Conversion:** AI observations become local automation
2. **Privacy-First:** Email processed locally, cloud only with consent
3. **Polymathic Integration:** Communication connects to knowledge work
4. **Token Cost Reduction:** Autonomy reduces ongoing cloud costs
5. **Data Sovereignty:** Communication patterns exportable and self-hostable

This phase positions Polly as "Jace.ai for people who want to own their systems"—full executive assistant capabilities with a path to independence.

**Key Success Metric:** 50% of communication decisions handled by local rules within 3 months (demonstrating successful progressive autonomy).

---

**Implementation Priority:** Medium-High (Tier 4 - Post-MVP, strong competitive positioning)

**Next Steps:** After Tier 4, evaluate user demand for additional coordination features vs. deepening existing intelligence capabilities.
