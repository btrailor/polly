"""
Tests for TemplateRegistry and built-in templates (Phase 24b).

Covers: all 5 built-ins validate, TemplateRegistry CRUD,
seed_builtins idempotency, domain filtering.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from core.nexus.storage import SwarmStorage
from core.nexus.templates import BUILTIN_TEMPLATES, TemplateRegistry
from core.nexus.workflow import MergeStrategy, WorkflowStep, WorkflowTemplate


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = Path(f.name)
    yield path
    path.unlink(missing_ok=True)


@pytest.fixture
def storage(temp_db):
    return SwarmStorage(temp_db)


@pytest.fixture
def registry(storage):
    return TemplateRegistry(storage)


@pytest.fixture
def seeded_registry(registry):
    registry.seed_builtins()
    return registry


# ---------------------------------------------------------------------------
# Tests: BUILTIN_TEMPLATES dict
# ---------------------------------------------------------------------------

class TestBuiltinTemplatesDict:
    def test_five_builtin_templates(self):
        assert len(BUILTIN_TEMPLATES) == 5

    def test_all_expected_ids_present(self):
        expected = {
            "research-to-write",
            "capture-and-summarize",
            "teach-and-assess",
            "plan-and-review",
            "multi-domain-analysis",
        }
        assert set(BUILTIN_TEMPLATES.keys()) == expected

    def test_all_builtins_are_marked_builtin(self):
        for tid, t in BUILTIN_TEMPLATES.items():
            assert t.is_builtin is True, f"{tid} not marked as builtin"

    def test_all_builtins_validate(self):
        for tid, t in BUILTIN_TEMPLATES.items():
            t.validate()  # Should not raise

    def test_all_builtins_have_at_least_one_step(self):
        for tid, t in BUILTIN_TEMPLATES.items():
            assert len(t.steps) >= 1, f"{tid} has no steps"

    def test_all_builtins_have_valid_output_step(self):
        for tid, t in BUILTIN_TEMPLATES.items():
            step_ids = {s.id for s in t.steps}
            assert t.output_step in step_ids, f"{tid} output_step not in steps"

    def test_all_builtins_have_description(self):
        for tid, t in BUILTIN_TEMPLATES.items():
            assert t.description, f"{tid} has no description"

    def test_all_builtins_have_domain_affinity(self):
        for tid, t in BUILTIN_TEMPLATES.items():
            assert len(t.domain_affinity) >= 1, f"{tid} has no domain_affinity"

    def test_research_to_write_has_intervention_points(self):
        t = BUILTIN_TEMPLATES["research-to-write"]
        assert len(t.intervention_points) >= 1

    def test_multi_domain_analysis_uses_ensemble_merge(self):
        t = BUILTIN_TEMPLATES["multi-domain-analysis"]
        assert t.merge_strategy == MergeStrategy.ENSEMBLE

    def test_multi_domain_analysis_has_parallel_steps(self):
        """capture and explain have no depends_on → run in parallel."""
        t = BUILTIN_TEMPLATES["multi-domain-analysis"]
        parallel_steps = [s for s in t.steps if not s.depends_on]
        assert len(parallel_steps) >= 2

    def test_all_builtins_serialise_roundtrip(self):
        for tid, t in BUILTIN_TEMPLATES.items():
            d = t.to_dict()
            t2 = WorkflowTemplate.from_dict(d)
            assert t2.id == t.id
            assert len(t2.steps) == len(t.steps)


# ---------------------------------------------------------------------------
# Tests: TemplateRegistry.seed_builtins
# ---------------------------------------------------------------------------

class TestSeedBuiltins:
    def test_seed_builtins_stores_all_five(self, seeded_registry, storage):
        templates = storage.list_templates()
        assert len(templates) == 5

    def test_seed_builtins_idempotent(self, registry, storage):
        registry.seed_builtins()
        registry.seed_builtins()
        registry.seed_builtins()
        templates = storage.list_templates()
        assert len(templates) == 5  # not 15

    def test_seeded_templates_are_retrievable(self, seeded_registry):
        for tid in BUILTIN_TEMPLATES:
            t = seeded_registry.get(tid)
            assert t is not None, f"Template '{tid}' not retrievable after seeding"

    def test_seeded_templates_validate(self, seeded_registry):
        for tid in BUILTIN_TEMPLATES:
            t = seeded_registry.get(tid)
            t.validate()  # Should not raise


# ---------------------------------------------------------------------------
# Tests: TemplateRegistry.get
# ---------------------------------------------------------------------------

class TestGet:
    def test_get_existing_returns_template(self, seeded_registry):
        t = seeded_registry.get("research-to-write")
        assert t is not None
        assert t.id == "research-to-write"

    def test_get_nonexistent_returns_none(self, seeded_registry):
        result = seeded_registry.get("nonexistent-template")
        assert result is None

    def test_get_returns_workflowtemplate_instance(self, seeded_registry):
        t = seeded_registry.get("teach-and-assess")
        assert isinstance(t, WorkflowTemplate)

    def test_get_preserves_steps(self, seeded_registry):
        t = seeded_registry.get("research-to-write")
        original = BUILTIN_TEMPLATES["research-to-write"]
        assert len(t.steps) == len(original.steps)

    def test_get_preserves_output_step(self, seeded_registry):
        t = seeded_registry.get("plan-and-review")
        original = BUILTIN_TEMPLATES["plan-and-review"]
        assert t.output_step == original.output_step


# ---------------------------------------------------------------------------
# Tests: TemplateRegistry.list_all
# ---------------------------------------------------------------------------

class TestListAll:
    def test_list_all_returns_all_seeded(self, seeded_registry):
        templates = seeded_registry.list_all()
        assert len(templates) == 5

    def test_list_all_returns_workflow_templates(self, seeded_registry):
        templates = seeded_registry.list_all()
        for t in templates:
            assert isinstance(t, WorkflowTemplate)

    def test_list_all_domain_filter_writing(self, seeded_registry):
        templates = seeded_registry.list_all(domain="writing")
        assert len(templates) >= 1
        ids = {t.id for t in templates}
        assert "research-to-write" in ids

    def test_list_all_domain_filter_education(self, seeded_registry):
        templates = seeded_registry.list_all(domain="education")
        assert len(templates) >= 1
        ids = {t.id for t in templates}
        assert "teach-and-assess" in ids

    def test_list_all_domain_filter_no_match(self, seeded_registry):
        templates = seeded_registry.list_all(domain="nonexistent_domain_xyz")
        assert templates == []

    def test_list_all_empty_when_no_templates(self, registry):
        templates = registry.list_all()
        assert templates == []


# ---------------------------------------------------------------------------
# Tests: TemplateRegistry.create
# ---------------------------------------------------------------------------

class TestCreate:
    def test_create_custom_template(self, registry):
        t = WorkflowTemplate(
            id="custom-1",
            name="Custom Template",
            description="A test",
            steps=[WorkflowStep(id="only", agent_capability="capture_note",
                                input_mapping={"query": "$user_input"})],
            output_step="only",
        )
        tid = registry.create(t)
        assert tid == "custom-1"

    def test_created_template_retrievable(self, registry):
        t = WorkflowTemplate(
            id="my-template",
            name="My Template",
            description="",
            steps=[WorkflowStep(id="s", agent_capability="c")],
            output_step="s",
        )
        registry.create(t)
        retrieved = registry.get("my-template")
        assert retrieved is not None
        assert retrieved.name == "My Template"

    def test_create_validates_before_storing(self, registry):
        t = WorkflowTemplate(
            id="invalid",
            name="Invalid",
            description="",
            steps=[
                WorkflowStep(id="a", agent_capability="c", depends_on=["b"]),
                WorkflowStep(id="b", agent_capability="c", depends_on=["a"]),
            ],
            output_step="a",
        )
        with pytest.raises(ValueError, match="cycle"):
            registry.create(t)

    def test_create_invalid_output_step_raises(self, registry):
        t = WorkflowTemplate(
            id="bad-output",
            name="Bad",
            description="",
            steps=[WorkflowStep(id="s", agent_capability="c")],
            output_step="ghost",
        )
        with pytest.raises(ValueError):
            registry.create(t)


# ---------------------------------------------------------------------------
# Tests: TemplateRegistry.update
# ---------------------------------------------------------------------------

class TestUpdate:
    def test_update_existing_template(self, seeded_registry):
        t = seeded_registry.get("capture-and-summarize")
        t.name = "Updated Name"
        seeded_registry.update("capture-and-summarize", t)
        retrieved = seeded_registry.get("capture-and-summarize")
        assert retrieved.name == "Updated Name"

    def test_update_nonexistent_raises(self, registry):
        t = WorkflowTemplate(
            id="ghost",
            name="Ghost",
            description="",
            steps=[WorkflowStep(id="s", agent_capability="c")],
            output_step="s",
        )
        with pytest.raises(ValueError, match="not found"):
            registry.update("ghost", t)

    def test_update_validates_new_definition(self, seeded_registry):
        t = seeded_registry.get("capture-and-summarize")
        t.output_step = "nonexistent-step"
        with pytest.raises(ValueError):
            seeded_registry.update("capture-and-summarize", t)


# ---------------------------------------------------------------------------
# Tests: TemplateRegistry.delete
# ---------------------------------------------------------------------------

class TestDelete:
    def test_delete_existing_returns_true(self, seeded_registry):
        result = seeded_registry.delete("capture-and-summarize")
        assert result is True

    def test_deleted_template_not_retrievable(self, seeded_registry):
        seeded_registry.delete("capture-and-summarize")
        assert seeded_registry.get("capture-and-summarize") is None

    def test_delete_nonexistent_returns_false(self, registry):
        result = registry.delete("nonexistent")
        assert result is False

    def test_deleted_template_not_in_list_all(self, seeded_registry):
        seeded_registry.delete("capture-and-summarize")
        templates = seeded_registry.list_all()
        ids = {t.id for t in templates}
        assert "capture-and-summarize" not in ids

    def test_delete_reduces_count(self, seeded_registry):
        before = len(seeded_registry.list_all())
        seeded_registry.delete("teach-and-assess")
        after = len(seeded_registry.list_all())
        assert after == before - 1


# ---------------------------------------------------------------------------
# Tests: TemplateRegistry repr
# ---------------------------------------------------------------------------

class TestRepr:
    def test_repr_contains_template_registry(self, registry):
        r = repr(registry)
        assert "TemplateRegistry" in r
