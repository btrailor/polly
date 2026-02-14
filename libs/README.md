# Polly Libraries (Monorepo)

Internal libraries extracted from `core/` for clearer boundaries and optional standalone use. Polly remains the orchestrator; these packages are installed in editable mode during development.

## Layout

| Library           | Package             | Description                              |
| ----------------- | ------------------- | ---------------------------------------- |
| polly-routing     | `polly_routing`     | Router v2, providers, budget manager     |
| polly-patterns    | `polly_patterns`    | Unified pattern engine, storage backends |
| polly-compression | `polly_compression` | Conversation/context compression         |
| polly-entities    | `polly_entities`    | Entity store, extractor, context builder |
| polly-personas    | `polly_personas`    | Persona base, manager, implementations   |

## Setup

From the project root (use a virtual environment if your Python is externally managed):

```bash
# Recommended: install app deps and libs in one step (from project root)
pip install -r requirements.txt
```

That installs app dependencies and the **polly-routing** library (editable). To install or update only the libs:

```bash
./scripts/install_libs.sh
# or manually:
pip install -e libs/polly-routing
# pip install -e libs/polly-patterns   # when extracted
# pip install -e libs/polly-compression
# pip install -e libs/polly-entities
# pip install -e libs/polly-personas
```

The app requires `polly_routing` for router v2 and budget tracking. If it’s missing, you’ll see: _"polly_routing is not installed. From the project root run: pip install -r requirements.txt"_.

**Signed / packaged app (e.g. Electron build):** The bundle includes `libs/` and sets `PYTHONPATH` so the packaged Python environment can import `polly_routing` from `resources/python/libs/polly-routing`. No extra install step for the lib inside the bundle.

## Dependency order

- **polly-routing** — no internal lib deps
- **polly-compression** — no internal lib deps
- **polly-patterns** — no internal lib deps
- **polly-entities** — no internal lib deps
- **polly-personas** — may depend on polly_routing (Protocol), others via injection

## Development

Libraries are not published to PyPI. They are versioned with the main Polly repo. See [openspec/changes/library-extraction/](../openspec/changes/library-extraction/) for the extraction plan.
