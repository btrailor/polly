# Delta: iOS App — Phase 2 (Knowledge Skill UI)

## ADDED Requirements

### Requirement: Knowledge Skill Source Cards
The Settings screen MUST display source cards for connected knowledge sources (Obsidian, BookLore). Each card SHALL show: source name, icon, connection status, last-synced timestamp, note/book count.

#### Scenario: Vault connected
- GIVEN a user has configured an Obsidian vault path
- WHEN the user opens Settings → Knowledge
- THEN the vault source card shows status: "Connected", last synced timestamp, and note count
- AND the card shows an amber indicator if the index is stale (> 24h)
- AND the card shows a red indicator with "Rebuild Index" action if the index is corrupt

### Requirement: Add Source Picker
The Settings → Knowledge screen MUST include an "Add Source" button that presents: Obsidian (available), BookLore (available), and placeholder slots for future adapters (showing "Coming soon").

### Requirement: Knowledge Filter Chips in Chat
The chat UI MUST include a filter chip row for knowledge source filtering: All Sources, Vault, Books, Conversations. The selected filter SHALL be passed as the `sources` param to `knowledge_search`.

#### Scenario: Filter chip — Vault only
- GIVEN the user taps the "Vault" filter chip
- WHEN the agent calls knowledge_search
- THEN `sources: ["vault"]` is passed
- AND results from booklore and conversation are excluded

### Requirement: Domain Config Sync
The app MUST sync user-declared domains (MMKV `polly.domains`) to the gateway via config.patch as `polly.knowledge.domain_seeds` whenever the user modifies their domain configuration in Settings.

#### Scenario: Domain sync on settings change
- GIVEN a user adds a new domain in Settings → Domains
- WHEN the user saves
- THEN the app calls config.patch with the updated `polly.knowledge.domain_seeds` value
- AND the Knowledge Skill applies the updated domain seeds on its next ingest cycle
