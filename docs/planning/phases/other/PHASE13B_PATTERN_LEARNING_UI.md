# Phase 13b: Pattern Learning UI & Testing

**Status:** PLANNED  
**Priority:** Tier 1 (High Priority)  
**Estimated Effort:** 7 days  
**Complexity:** Medium  
**Dependencies:** Phase 13a (Core Pattern System must be complete)

---

## Part 2: Pattern Visualization UI (Days 3-4)

### Objectives
- Display all patterns with filtering/sorting
- Show pattern details and metrics
- RAG efficiency dashboard
- Pattern usefulness visualization

---

### 2.1: Pattern Browser Component

**File:** `electron-app/src/renderer/components/settings/PatternBrowser.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface Pattern {
    id: string;
    type: 'conceptual' | 'query_chunk' | 'domain_priority' | 'project_workflow';
    name: string;
    confidence: number;
    occurrences?: number;
    usefulness_score?: number;
    last_seen: string;
}

export function PatternBrowser() {
    const [patterns, setPatterns] = useState<Pattern[]>([]);
    const [filteredPatterns, setFilteredPatterns] = useState<Pattern[]>([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterType, setFilterType] = useState<string>('all');
    const [sortBy, setSortBy] = useState<'confidence' | 'usefulness' | 'occurrences'>('confidence');
    
    useEffect(() => {
        loadPatterns();
    }, []);
    
    useEffect(() => {
        applyFilters();
    }, [patterns, searchTerm, filterType, sortBy]);
    
    const loadPatterns = async () => {
        const data = await window.electron.getPatterns();
        setPatterns(data.patterns);
    };
    
    const applyFilters = () => {
        let filtered = patterns;
        
        // Search filter
        if (searchTerm) {
            filtered = filtered.filter(p => 
                p.name.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }
        
        // Type filter
        if (filterType !== 'all') {
            filtered = filtered.filter(p => p.type === filterType);
        }
        
        // Sort
        filtered.sort((a, b) => {
            if (sortBy === 'confidence') return b.confidence - a.confidence;
            if (sortBy === 'usefulness') return (b.usefulness_score || 0) - (a.usefulness_score || 0);
            if (sortBy === 'occurrences') return (b.occurrences || 0) - (a.occurrences || 0);
            return 0;
        });
        
        setFilteredPatterns(filtered);
    };
    
    const getConfidenceBadge = (confidence: number) => {
        if (confidence >= 0.8) return <Badge className="bg-green-500">High</Badge>;
        if (confidence >= 0.5) return <Badge className="bg-yellow-500">Medium</Badge>;
        return <Badge className="bg-red-500">Low</Badge>;
    };
    
    return (
        <Card>
            <CardHeader>
                <CardTitle>Pattern Browser</CardTitle>
                <p className="text-sm text-muted-foreground">
                    {filteredPatterns.length} of {patterns.length} patterns
                </p>
            </CardHeader>
            <CardContent>
                {/* Filters */}
                <div className="flex gap-4 mb-4">
                    <Input
                        placeholder="Search patterns..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="flex-1"
                    />
                    
                    <Select value={filterType} onValueChange={setFilterType}>
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Filter by type" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Types</SelectItem>
                            <SelectItem value="conceptual">Conceptual</SelectItem>
                            <SelectItem value="query_chunk">Query→Chunk</SelectItem>
                            <SelectItem value="domain_priority">Domain Priority</SelectItem>
                            <SelectItem value="project_workflow">Workflow</SelectItem>
                        </SelectContent>
                    </Select>
                    
                    <Select value={sortBy} onValueChange={(v) => setSortBy(v as any)}>
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Sort by" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="confidence">Confidence</SelectItem>
                            <SelectItem value="usefulness">Usefulness</SelectItem>
                            <SelectItem value="occurrences">Occurrences</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
                
                {/* Pattern Table */}
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Pattern</TableHead>
                            <TableHead>Type</TableHead>
                            <TableHead>Confidence</TableHead>
                            <TableHead>Usefulness</TableHead>
                            <TableHead>Last Seen</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {filteredPatterns.map(pattern => (
                            <TableRow key={pattern.id}>
                                <TableCell className="font-medium">{pattern.name}</TableCell>
                                <TableCell>
                                    <Badge variant="outline">{pattern.type}</Badge>
                                </TableCell>
                                <TableCell>
                                    {getConfidenceBadge(pattern.confidence)}
                                    <span className="ml-2 text-sm text-muted-foreground">
                                        {(pattern.confidence * 100).toFixed(0)}%
                                    </span>
                                </TableCell>
                                <TableCell>
                                    {pattern.usefulness_score !== undefined ? (
                                        <span>{(pattern.usefulness_score * 100).toFixed(0)}%</span>
                                    ) : (
                                        <span className="text-muted-foreground">N/A</span>
                                    )}
                                </TableCell>
                                <TableCell className="text-sm text-muted-foreground">
                                    {new Date(pattern.last_seen).toLocaleDateString()}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    );
}
```

---

### 2.2: RAG Efficiency Metrics Dashboard

**File:** `electron-app/src/renderer/components/settings/PatternMetricsDashboard.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

interface PatternMetrics {
    total_patterns: number;
    conceptual_patterns: number;
    query_chunk_patterns: number;
    domain_priority_patterns: number;
    workflow_patterns: number;
    avg_confidence: number;
    avg_usefulness: number;
    rag_speedup_estimate: number; // Percentage
    patterns_used_today: number;
    patterns_helped_today: number;
}

export function PatternMetricsDashboard() {
    const [metrics, setMetrics] = useState<PatternMetrics | null>(null);
    
    useEffect(() => {
        loadMetrics();
        const interval = setInterval(loadMetrics, 60000); // Refresh every minute
        return () => clearInterval(interval);
    }, []);
    
    const loadMetrics = async () => {
        const data = await window.electron.getPatternMetrics();
        setMetrics(data);
    };
    
    if (!metrics) return <div>Loading metrics...</div>;
    
    return (
        <Card>
            <CardHeader>
                <CardTitle>Pattern Learning Metrics</CardTitle>
                <p className="text-sm text-muted-foreground">
                    Real-time performance tracking
                </p>
            </CardHeader>
            <CardContent className="space-y-6">
                {/* Pattern Counts */}
                <div>
                    <h3 className="text-sm font-medium mb-3">Pattern Distribution</h3>
                    <div className="space-y-2">
                        <div className="flex justify-between items-center">
                            <span className="text-sm">Conceptual</span>
                            <Badge>{metrics.conceptual_patterns}</Badge>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm">Query→Chunk</span>
                            <Badge>{metrics.query_chunk_patterns}</Badge>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm">Domain Priorities</span>
                            <Badge>{metrics.domain_priority_patterns}</Badge>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm">Workflows</span>
                            <Badge>{metrics.workflow_patterns}</Badge>
                        </div>
                        <div className="flex justify-between items-center font-semibold pt-2 border-t">
                            <span>Total</span>
                            <Badge className="bg-primary">{metrics.total_patterns}</Badge>
                        </div>
                    </div>
                </div>
                
                {/* Quality Metrics */}
                <div>
                    <h3 className="text-sm font-medium mb-3">Pattern Quality</h3>
                    <div className="space-y-3">
                        <div>
                            <div className="flex justify-between text-sm mb-1">
                                <span>Average Confidence</span>
                                <span>{(metrics.avg_confidence * 100).toFixed(0)}%</span>
                            </div>
                            <Progress value={metrics.avg_confidence * 100} />
                        </div>
                        
                        <div>
                            <div className="flex justify-between text-sm mb-1">
                                <span>Average Usefulness</span>
                                <span>{(metrics.avg_usefulness * 100).toFixed(0)}%</span>
                            </div>
                            <Progress value={metrics.avg_usefulness * 100} />
                        </div>
                    </div>
                </div>
                
                {/* RAG Speedup */}
                <div>
                    <h3 className="text-sm font-medium mb-3">RAG Performance Impact</h3>
                    <div className="p-4 bg-secondary rounded-lg">
                        <div className="text-3xl font-bold text-primary">
                            +{metrics.rag_speedup_estimate}%
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                            Estimated RAG speedup from patterns
                        </p>
                    </div>
                </div>
                
                {/* Today's Activity */}
                <div>
                    <h3 className="text-sm font-medium mb-3">Today's Pattern Usage</h3>
                    <div className="space-y-2">
                        <div className="flex justify-between items-center">
                            <span className="text-sm">Patterns Used</span>
                            <Badge variant="outline">{metrics.patterns_used_today}</Badge>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm">Patterns Helped</span>
                            <Badge variant="outline">{metrics.patterns_helped_today}</Badge>
                        </div>
                        {metrics.patterns_used_today > 0 && (
                            <div className="flex justify-between items-center pt-2 border-t">
                                <span className="text-sm font-medium">Success Rate</span>
                                <span className="text-sm font-semibold">
                                    {((metrics.patterns_helped_today / metrics.patterns_used_today) * 100).toFixed(0)}%
                                </span>
                            </div>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
```

---

**Files Modified:**
- `electron-app/src/renderer/components/settings/PatternBrowser.tsx` (+150 lines, new file)
- `electron-app/src/renderer/components/settings/PatternMetricsDashboard.tsx` (+130 lines, new file)

**Completion Criteria:**
- ✅ Pattern browser displays all patterns
- ✅ Search/filter/sort working
- ✅ Metrics dashboard shows real-time stats
- ✅ RAG speedup estimate calculated and displayed
- ✅ Pattern usefulness scores visible
- ✅ UI loads in <500ms with 200+ patterns

---

## Part 3: Pattern Management Interface (Days 5-6)

### Objectives
- Delete/hide individual patterns
- Mark patterns as useful/noise
- Clear all patterns with backup
- Export patterns for analysis

---

### 3.1: Pattern Management Actions

**File:** `electron-app/src/renderer/components/settings/PatternManagement.tsx`

```typescript
import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';

export function PatternManagement() {
    const [isClearing, setIsClearing] = useState(false);
    const [isExporting, setIsExporting] = useState(false);
    
    const handleClearAllPatterns = async () => {
        setIsClearing(true);
        try {
            // Backend creates backup automatically
            await window.electron.clearAllPatterns();
            alert('All patterns cleared. Backup saved to ~/.polly/patterns.json.backup');
        } catch (error) {
            alert(`Failed to clear patterns: ${error.message}`);
        } finally {
            setIsClearing(false);
        }
    };
    
    const handleExportPatterns = async () => {
        setIsExporting(true);
        try {
            const filepath = await window.electron.exportPatterns();
            alert(`Patterns exported to: ${filepath}`);
        } catch (error) {
            alert(`Export failed: ${error.message}`);
        } finally {
            setIsExporting(false);
        }
    };
    
    return (
        <Card>
            <CardHeader>
                <CardTitle>Pattern Management</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Export */}
                <div>
                    <Button
                        onClick={handleExportPatterns}
                        disabled={isExporting}
                        variant="outline"
                        className="w-full"
                    >
                        {isExporting ? 'Exporting...' : 'Export Patterns (JSON)'}
                    </Button>
                    <p className="text-sm text-muted-foreground mt-2">
                        Export all patterns to JSON for analysis or backup
                    </p>
                </div>
                
                {/* Clear All */}
                <div>
                    <AlertDialog>
                        <AlertDialogTrigger asChild>
                            <Button
                                variant="destructive"
                                className="w-full"
                                disabled={isClearing}
                            >
                                Clear All Patterns
                            </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                            <AlertDialogHeader>
                                <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                                <AlertDialogDescription>
                                    This will delete all learned patterns. A backup will be created at ~/.polly/patterns.json.backup.
                                    You can restore patterns later if needed.
                                </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction onClick={handleClearAllPatterns}>
                                    Clear All Patterns
                                </AlertDialogAction>
                            </AlertDialogFooter>
                        </AlertDialogContent>
                    </AlertDialog>
                    <p className="text-sm text-muted-foreground mt-2">
                        Remove all patterns (backup created automatically)
                    </p>
                </div>
            </CardContent>
        </Card>
    );
}
```

---

**Files Modified:**
- `electron-app/src/renderer/components/settings/PatternManagement.tsx` (+80 lines, new file)

**Completion Criteria:**
- ✅ Clear all patterns creates backup
- ✅ Export generates JSON file
- ✅ Confirmation dialog for destructive actions
- ✅ Test: Clear patterns → backup exists → can restore

---

## Part 4: Testing & Validation (Day 7)

### Objectives
- RAG speed benchmarks
- Pattern quality verification
- End-to-end testing
- User acceptance testing

---

### 4.1: RAG Speed Benchmarks

**File:** `tests/test_pattern_rag_speedup.py`

```python
import pytest
import time
from core.polly import Polly

@pytest.mark.asyncio
async def test_rag_speedup_with_patterns():
    """Measure RAG speedup from patterns."""
    polly = Polly()
    
    # Test query
    test_query = "How do I use Docker with Python?"
    
    # Baseline (without patterns, first query)
    start = time.time()
    result1 = await polly.query(test_query)
    baseline_time = time.time() - start
    
    # Learn patterns (repeat query 5 times)
    for _ in range(5):
        await polly.query(test_query)
    
    # With patterns (6th query)
    start = time.time()
    result2 = await polly.query(test_query)
    pattern_time = time.time() - start
    
    # Calculate speedup
    speedup_percent = ((baseline_time - pattern_time) / baseline_time) * 100
    
    print(f"Baseline: {baseline_time:.3f}s")
    print(f"With patterns: {pattern_time:.3f}s")
    print(f"Speedup: {speedup_percent:.1f}%")
    
    # Assert at least 20% speedup (conservative target)
    assert speedup_percent >= 20, f"Expected >=20% speedup, got {speedup_percent:.1f}%"
```

---

### 4.2: Pattern Quality Verification

**File:** `tests/test_pattern_quality.py`

```python
import pytest
from learners.patterns import PatternLearner

def test_no_garbage_patterns():
    """Verify no garbage patterns like 'calm ↔ pick'."""
    learner = PatternLearner()
    learner.load_patterns()
    
    # Garbage concepts that should NOT appear
    garbage_concepts = {'calm', 'pick', 'spend', 'reach', 'for', 'think', 'social'}
    
    for pattern in learner.patterns.values():
        if pattern.pattern_type == 'conceptual':
            concept1 = pattern.metadata.get('concept1', '').lower()
            concept2 = pattern.metadata.get('concept2', '').lower()
            
            assert concept1 not in garbage_concepts, f"Found garbage concept: {concept1}"
            assert concept2 not in garbage_concepts, f"Found garbage concept: {concept2}"

def test_pattern_quality_thresholds():
    """Verify all patterns meet quality thresholds."""
    learner = PatternLearner()
    learner.load_patterns()
    
    # All conceptual patterns should have confidence >= 0.5
    for pattern in learner.patterns.values():
        if pattern.pattern_type == 'conceptual':
            assert pattern.confidence >= 0.5, f"Pattern {pattern.name} below confidence threshold"
            assert pattern.occurrences >= 7, f"Pattern {pattern.name} below occurrence threshold"
    
    # Should have <= 200 conceptual patterns
    conceptual_count = len([p for p in learner.patterns.values() if p.pattern_type == 'conceptual'])
    assert conceptual_count <= 200, f"Too many conceptual patterns: {conceptual_count}"
```

---

**Files Modified:**
- `tests/test_pattern_rag_speedup.py` (+40 lines, new file)
- `tests/test_pattern_quality.py` (+40 lines, new file)

**Completion Criteria:**
- ✅ RAG speedup test passes (>=20% faster)
- ✅ No garbage patterns in test
- ✅ All patterns meet quality thresholds
- ✅ Pattern count under limits

---

## Success Criteria - Phase 13b Complete

### UI & Controls
- ✅ Learning frequency controls working (5+ messages, domain-only, 3-day delay)
- ✅ Batch learning mode functional
- ✅ Pattern browser displays/filters/sorts patterns correctly
- ✅ Metrics dashboard shows real-time stats
- ✅ RAG speedup estimate displayed
- ✅ Pattern management (clear, export) working

### Performance
- ✅ UI loads in <500ms with 200+ patterns
- ✅ Pattern browser handles 400+ patterns smoothly
- ✅ Metrics update in real-time without lag

### Testing
- ✅ RAG speedup test passes (>=20% improvement measured)
- ✅ Pattern quality verification passes
- ✅ No garbage patterns exist
- ✅ End-to-end tests pass

---

## Files Modified/Created

### New Files (UI Components)
1. `electron-app/src/renderer/components/settings/PatternLearningSettings.tsx` (+120 lines)
2. `electron-app/src/renderer/components/settings/PatternBrowser.tsx` (+150 lines)
3. `electron-app/src/renderer/components/settings/PatternMetricsDashboard.tsx` (+130 lines)
4. `electron-app/src/renderer/components/settings/PatternManagement.tsx` (+80 lines)

### Modified Files
1. `electron-app/src/main/conversation-manager.js` (+50 lines)

### New Files (Testing)
1. `tests/test_pattern_rag_speedup.py` (+40 lines)
2. `tests/test_pattern_quality.py` (+40 lines)

**Total:** ~610 lines of new code

---

**End of PHASE13B_PATTERN_LEARNING_UI.md**


1. [Executive Summary](#executive-summary)
2. [Overview](#overview)
3. [Part 1: Learning Frequency Controls](#part-1-learning-frequency-controls)
4. [Part 2: Pattern Visualization UI](#part-2-pattern-visualization-ui)
5. [Part 3: Pattern Management Interface](#part-3-pattern-management-interface)
6. [Part 4: Testing & Validation](#part-4-testing--validation)
7. [Success Criteria](#success-criteria)
8. [Files Modified/Created](#files-modifiedcreated)

---

## Executive Summary

Phase 13b builds the user-facing components for the pattern learning system, providing visibility, control, and testing validation.

### What This Phase Delivers

1. **Learning Frequency Controls** (Days 1-2)
   - Smarter trigger conditions (5+ messages, domain-only, no re-learning < 3 days)
   - Batch learning mode
   - User controls for when learning happens

2. **Pattern Visualization UI** (Days 3-4)
   - View all patterns sorted by confidence/usefulness
   - See pattern details (occurrences, last seen, usefulness score)
   - RAG efficiency metrics dashboard
   - Pattern usefulness tracking visualization

3. **Pattern Management Interface** (Days 5-6)
   - Delete/hide patterns manually
   - Mark patterns as "useful" or "noise"
   - Clear all patterns (with backup)
   - Export patterns for analysis

4. **Testing & Validation** (Day 7)
   - RAG speed benchmarks (before/after patterns)
   - Pattern quality verification
   - End-to-end testing scenarios
   - User acceptance testing

### Why This Matters

Without UI/controls, users can't see or manage what the system learns. Phase 13b provides:
- **Transparency:** See what patterns exist
- **Control:** Delete bad patterns, mark good ones
- **Metrics:** Measure RAG speedup from patterns
- **Trust:** Validate that patterns actually help

---

## Overview

### Prerequisites

Phase 13a must be complete:
- ✅ Core pattern system implemented (Query→Chunk, Domain→Collection, Conceptual)
- ✅ Pattern storage working (`~/.polly/patterns.json` version 2.0)
- ✅ Pattern quality controls active (pruning, decay, usefulness tracking)
- ✅ Pattern APIs available (`get_pattern_stats()`, `export_patterns()`)

### Architecture

**UI Location:** Electron app settings panel (`electron-app/src/renderer/components/settings/`)

**UI Components:**
```
Settings
  └── Pattern Learning
        ├── Overview (stats, toggle on/off)
        ├── Learning Controls (frequency, triggers)
        ├── Pattern Browser (view/search/filter patterns)
        ├── Pattern Management (delete, mark useful, export)
        └── Metrics Dashboard (RAG speedup, usefulness scores)
```

---

## Part 1: Learning Frequency Controls (Days 1-2)

### Objectives
- Reduce unnecessary pattern learning overhead
- Give users control over when learning happens
- Implement smarter trigger conditions

---

### 1.1: Smarter Trigger Conditions

**File:** `electron-app/src/main/conversation-manager.js`

**Current Logic** (line 249):
```javascript
async triggerPatternLearning(conversationId) {
    const conversation = this.getConversation(conversationId);
    
    // Learn from every conversation with 3+ messages
    if (conversation && conversation.messages.length >= 3) {
        await this.learnPatterns(conversationId);
    }
}
```

**Enhanced Logic:**
```javascript
async triggerPatternLearning(conversationId) {
    try {
        const conversation = this.getConversation(conversationId);
        
        // More selective criteria
        if (!conversation || !conversation.messages) {
            return;
        }
        
        // 1. Must have 5+ messages (not 3)
        if (conversation.messages.length < 5) {
            console.log(`Skipping pattern learning: only ${conversation.messages.length} messages (need 5+)`);
            return;
        }
        
        // 2. Must be in a domain category (not uncategorized)
        if (conversation.category_id === 'uncategorized') {
            console.log('Skipping pattern learning: uncategorized conversation');
            return;
        }
        
        // 3. Must have at least one assistant message (not just user rambling)
        const hasAssistantMessage = conversation.messages.some(m => m.role === 'assistant');
        if (!hasAssistantMessage) {
            console.log('Skipping pattern learning: no assistant responses');
            return;
        }
        
        // 4. Don't re-learn same conversation too frequently
        const lastLearned = this._lastLearnedTimestamps.get(conversationId);
        if (lastLearned) {
            const daysSinceLastLearned = (Date.now() - lastLearned) / (1000 * 60 * 60 * 24);
            if (daysSinceLastLearned < 3) {
                console.log(`Skipping pattern learning: learned ${daysSinceLastLearned.toFixed(1)} days ago (wait 3 days)`);
                return;
            }
        }
        
        // All criteria met, proceed with learning
        console.log(`Pattern learning triggered for conversation ${conversationId}`);
        await this.learnPatterns(conversationId);
        
        // Record timestamp
        this._lastLearnedTimestamps.set(conversationId, Date.now());
        
    } catch (error) {
        console.warn('Pattern learning failed:', error.message);
    }
}
```

**Add to ConversationManager class:**
```javascript
class ConversationManager {
    constructor() {
        // ... existing code ...
        
        // Track when we last learned from each conversation
        this._lastLearnedTimestamps = new Map();
    }
}
```

---

### 1.2: Batch Learning Mode

**File:** `electron-app/src/main/conversation-manager.js`

**Add new method:**
```javascript
async batchLearnFromRecentConversations(days = 7) {
    """
    Batch learn patterns from recent conversations.
    
    Useful for:
    - First-time pattern learning (learn from all past conversations)
    - Periodic bulk learning (once per week)
    - Manual trigger by user
    """
    console.log(`Batch learning from conversations in past ${days} days...`);
    
    const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
    const recentConversations = this.conversations.filter(conv => {
        const lastMessage = conv.messages[conv.messages.length - 1];
        return new Date(lastMessage.timestamp) >= cutoffDate;
    });
    
    console.log(`Found ${recentConversations.length} conversations to learn from`);
    
    let learnedCount = 0;
    for (const conversation of recentConversations) {
        // Apply same filtering criteria
        if (conversation.messages.length >= 5 &&
            conversation.category_id !== 'uncategorized') {
            
            try {
                await this.learnPatterns(conversation.id);
                learnedCount++;
            } catch (error) {
                console.warn(`Failed to learn from conversation ${conversation.id}:`, error);
            }
        }
    }
    
    console.log(`Batch learning complete: learned from ${learnedCount} conversations`);
    
    return {
        total_conversations: recentConversations.length,
        learned_from: learnedCount
    };
}
```

---

### 1.3: User Controls UI

**File:** `electron-app/src/renderer/components/settings/PatternLearningSettings.tsx`

**Create new component:**
```typescript
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';

interface LearningSettings {
    enabled: boolean;
    minMessages: number;
    requireDomain: boolean;
    relearningDelay: number; // days
}

export function PatternLearningControls() {
    const [settings, setSettings] = useState<LearningSettings>({
        enabled: true,
        minMessages: 5,
        requireDomain: true,
        relearningDelay: 3
    });
    
    const [isBatchLearning, setIsBatchLearning] = useState(false);
    
    const handleBatchLearn = async () => {
        setIsBatchLearning(true);
        try {
            const result = await window.electron.batchLearnPatterns(7);
            alert(`Learned from ${result.learned_from} of ${result.total_conversations} recent conversations`);
        } catch (error) {
            alert(`Batch learning failed: ${error.message}`);
        } finally {
            setIsBatchLearning(false);
        }
    };
    
    return (
        <Card>
            <CardHeader>
                <CardTitle>Learning Frequency Controls</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Enable/Disable */}
                <div className="flex items-center justify-between">
                    <Label htmlFor="learning-enabled">Pattern Learning Enabled</Label>
                    <Switch
                        id="learning-enabled"
                        checked={settings.enabled}
                        onCheckedChange={(checked) => setSettings({...settings, enabled: checked})}
                    />
                </div>
                
                {/* Minimum Messages */}
                <div className="space-y-2">
                    <Label>Minimum Messages: {settings.minMessages}</Label>
                    <Slider
                        min={3}
                        max={10}
                        step={1}
                        value={[settings.minMessages]}
                        onValueChange={([value]) => setSettings({...settings, minMessages: value})}
                    />
                    <p className="text-sm text-muted-foreground">
                        Only learn from conversations with at least this many messages
                    </p>
                </div>
                
                {/* Require Domain */}
                <div className="flex items-center justify-between">
                    <Label htmlFor="require-domain">Require Domain Category</Label>
                    <Switch
                        id="require-domain"
                        checked={settings.requireDomain}
                        onCheckedChange={(checked) => setSettings({...settings, requireDomain: checked})}
                    />
                </div>
                
                {/* Re-learning Delay */}
                <div className="space-y-2">
                    <Label>Re-learning Delay: {settings.relearningDelay} days</Label>
                    <Slider
                        min={1}
                        max={7}
                        step={1}
                        value={[settings.relearningDelay]}
                        onValueChange={([value]) => setSettings({...settings, relearningDelay: value})}
                    />
                    <p className="text-sm text-muted-foreground">
                        Don't re-learn same conversation within this many days
                    </p>
                </div>
                
                {/* Batch Learning */}
                <div className="pt-4 border-t">
                    <Button
                        onClick={handleBatchLearn}
                        disabled={isBatchLearning || !settings.enabled}
                        className="w-full"
                    >
                        {isBatchLearning ? 'Learning...' : 'Learn from Recent Conversations (Past 7 Days)'}
                    </Button>
                    <p className="text-sm text-muted-foreground mt-2">
                        Manually trigger pattern learning from all recent conversations
                    </p>
                </div>
            </CardContent>
        </Card>
    );
}
```

---

**Files Modified:**
- `electron-app/src/main/conversation-manager.js` (+50 lines)
- `electron-app/src/renderer/components/settings/PatternLearningSettings.tsx` (+120 lines, new file)

**Completion Criteria:**
- ✅ Learning only triggers with 5+ messages
- ✅ Learning skips uncategorized conversations
- ✅ Learning doesn't repeat within 3 days
- ✅ Batch learning mode works
- ✅ User can configure learning settings
- ✅ Test: Change settings → verify behavior updates

---

