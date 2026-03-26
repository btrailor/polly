# Phase 2: Today View CRUD

**Status:** 📋 Planned  
**Gate:** Phase 1 Today display (read-only rendering working)  
**Spec source:** `POLLY_IOS_SPEC.md` §4.2, §13  
**Owners:** @frontend

## Goal

Full CRUD for Today View items. Phase 1 Today View is display-only (renders items from gateway). Phase 2 adds creation, editing, completion, and deletion of triggers (reminders), items (tasks), and processes (background work).

## Tasks

### Item Creation
- [ ] Tap `+` in Today View → new item sheet
- [ ] Type picker: Trigger (reminder), Item (task), Process (background work)
- [ ] Trigger: title, `scheduledFor` (date/time picker), labels
- [ ] Item: title, description, labels, optional deadline
- [ ] Process: title, linked agent, status
- [ ] `aight_item` RPC on gateway to create (replaces Phase 1 inline creation path removed from phase-1-ios-foundation)

### Item Editing
- [ ] Tap item → detail view with edit mode
- [ ] Edit title, labels, deadline, notes
- [ ] `aight_item` update RPC

### Completion + Cancellation
- [ ] Swipe to complete (triggers: mark fired; items: mark done)
- [ ] Swipe to cancel
- [ ] Undo action (3-second window after swipe)
- [ ] `aight_item` status update RPC

### Deletion
- [ ] Long-press → delete confirmation
- [ ] Bulk delete (edit mode)

### Natural Language Creation from Chat
- [ ] Agent detects "remind me to..." / "create a task to..." → surfaces "Add to Today?" banner
- [ ] User taps → pre-filled creation sheet
- [ ] Confirm → create item; dismiss → ignore

### Agent-Created Items
- [ ] Agent can create items via `aight_item` tool (cron-scheduled Ops Coordinator, Scheduler)
- [ ] New agent-created items surface as "Polly added..." in Today View
- [ ] User can edit or delete agent-created items

## Done When
Full CRUD working. Natural language creation from chat working. Agent-created items rendering. @qa_guy sign-off.
