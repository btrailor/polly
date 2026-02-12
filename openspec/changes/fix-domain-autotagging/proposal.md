# Fix Domain Auto-Tagging Misclassification

## What

Fix the auto domain tagging system so that learning paths, curricula, and learning notes are tagged with the correct domain instead of always defaulting to "glyphs."

## Why

Currently, all learning interactions through the Professor persona are hardcoded to `domain="glyphs"`. This means a Python learning path gets tagged as "glyphs" instead of "sigils," and a U.S. Labor movement curriculum gets tagged as "glyphs" instead of "scrolls" or "grids." Only content that genuinely belongs to the glyphs domain (e.g., Graphic Design curriculum) appears correct -- by coincidence.

This breaks the user-customizable domains structure: users configure domains with keywords and expect auto-tagging to respect those keywords, but the Professor persona bypasses the entire `DomainEngine` detection pipeline.

## Scope

- **Backend**: `core/personas/implementations/professor.py`, `core/domains.py`, `interfaces/server.py`
- **Frontend**: No changes required (frontend already renders whatever domain the backend provides)

## Roadmap Reference

Relates to Phase 16 (Native Notes) auto-tagging and the custom domains feature. Resolves Known Issue #4 (Domain Tagging Misclassification).
