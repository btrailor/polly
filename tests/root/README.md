# Tests moved from repo root

These test files were moved from the project root during the Feb 2026 directory cleanup.

**Run from repo root:**

```bash
# Run all tests (including these)
pytest tests/

# Run only these (formerly root) tests
pytest tests/root/
```

If a test needs the project root on `PYTHONPATH`, run from repo root (e.g. `python -m pytest tests/root/` or `pytest tests/root/`).
