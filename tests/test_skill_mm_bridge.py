"""
Tests for SKILL↔Mental Model Bridge (Core Framework Wave 4, Task #25)

Tests cover:
- SkillMetadata.mental_models field (declaration in frontmatter)
- SkillManager parses mental_models from YAML frontmatter
- MentalModel.related_skills field
- get_models_for_context() skill_hints boost (+6 per hinted model)
- get_models_for_context_scored() skill_hints boost
- build_context_items() passes skill_hints through kwargs
- Skill hints can push model over MIN_SCORE_THRESHOLD
- Unknown skill hints don't affect unrelated models
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch


# ===================== SkillMetadata.mental_models =====================


class TestSkillMetadataField:
    """Tests for the new mental_models field on SkillMetadata."""

    def test_mental_models_defaults_to_empty_list(self):
        from core.skills.base import SkillMetadata

        meta = SkillMetadata(
            name="wiki-linking",
            category="note-taking",
            personas=["scribe"],
            version="1.0",
            path=Path("/fake/SKILL.md"),
        )
        assert meta.mental_models == []

    def test_mental_models_can_be_set(self):
        from core.skills.base import SkillMetadata

        meta = SkillMetadata(
            name="template-guide",
            category="note-taking",
            personas=["scribe", "librarian"],
            version="1.0",
            path=Path("/fake/SKILL.md"),
            mental_models=["instruments_over_tracks", "collaborative_maps"],
        )
        assert meta.mental_models == ["instruments_over_tracks", "collaborative_maps"]

    def test_to_dict_includes_mental_models(self):
        from core.skills.base import SkillMetadata

        meta = SkillMetadata(
            name="wiki-linking",
            category="note-taking",
            personas=["scribe"],
            version="1.0",
            path=Path("/fake/SKILL.md"),
            mental_models=["collaborative_maps"],
        )
        d = meta.to_dict()
        assert "mental_models" in d
        assert d["mental_models"] == ["collaborative_maps"]


# ===================== SkillManager parses mental_models =====================


class TestSkillManagerParsesField:
    """Tests for SkillManager._load_skill_metadata parsing mental_models."""

    def _make_skill_file(self, tmp_path: Path, frontmatter: str) -> Path:
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(f"---\n{frontmatter}\n---\n\n# Test Skill\n\nContent here.\n")
        return skill_file

    def test_parses_mental_models_list(self, tmp_path):
        from core.skills.manager import SkillManager

        skill_file = self._make_skill_file(
            tmp_path,
            "name: wiki-linking\ncategory: note-taking\npersonas: [scribe]\nversion: 1.0\n"
            "mental_models:\n  - instruments_over_tracks\n  - collaborative_maps\n"
        )
        mgr = SkillManager(skills_dir=str(tmp_path))
        meta = mgr._load_skill_metadata(skill_file)
        assert meta.mental_models == ["instruments_over_tracks", "collaborative_maps"]

    def test_parses_mental_models_string(self, tmp_path):
        """Single model as a string (not list) should be wrapped in list."""
        from core.skills.manager import SkillManager

        skill_file = self._make_skill_file(
            tmp_path,
            "name: wiki-linking\ncategory: note-taking\npersonas: [scribe]\nversion: 1.0\n"
            "mental_models: instruments_over_tracks\n"
        )
        mgr = SkillManager(skills_dir=str(tmp_path))
        meta = mgr._load_skill_metadata(skill_file)
        assert meta.mental_models == ["instruments_over_tracks"]

    def test_mental_models_defaults_empty_when_missing(self, tmp_path):
        from core.skills.manager import SkillManager

        skill_file = self._make_skill_file(
            tmp_path,
            "name: wiki-linking\ncategory: note-taking\npersonas: [scribe]\nversion: 1.0\n"
        )
        mgr = SkillManager(skills_dir=str(tmp_path))
        meta = mgr._load_skill_metadata(skill_file)
        assert meta.mental_models == []

    def test_discovered_skills_include_mental_models(self, tmp_path):
        from core.skills.manager import SkillManager

        self._make_skill_file(
            tmp_path,
            "name: template-guide\ncategory: note-taking\npersonas: [scribe]\nversion: 1.0\n"
            "mental_models: [progressive_autonomy]\n"
        )
        mgr = SkillManager(skills_dir=str(tmp_path))
        # get_skills_for_persona should return metadata with mental_models populated
        skills = mgr.get_skills_for_persona("scribe")
        assert len(skills) == 1
        assert skills[0].mental_models == ["progressive_autonomy"]


# ===================== MentalModel.related_skills field =====================


class TestMentalModelRelatedSkills:
    """Tests for the new related_skills field on MentalModel."""

    def test_related_skills_defaults_to_empty_list(self):
        from core.mental_models import MentalModel

        model = MentalModel(
            id="test_model",
            name="Test Model",
            description="A test model",
            principles=["principle 1"],
            prompt_injection="Use this model.",
        )
        assert model.related_skills == []

    def test_related_skills_can_be_set(self):
        from core.mental_models import MentalModel

        model = MentalModel(
            id="instruments_over_tracks",
            name="Instruments Over Tracks",
            description="Generative systems",
            principles=["Build instruments, not tracks"],
            prompt_injection="Think generatively.",
            related_skills=["template-guide", "wiki-linking"],
        )
        assert model.related_skills == ["template-guide", "wiki-linking"]


# ===================== Scoring with skill_hints =====================


def make_manager_with_model(model_id: str, extra_kwargs: dict = None):
    """Create a MentalModelManager with a single test model."""
    from core.mental_models import MentalModelManager, MentalModel

    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
        storage_path = f.name

    mgr = MentalModelManager(storage_path=storage_path)
    # Clear default models to isolate tests
    mgr.models.clear()

    kw = {"principles": ["p1"], "prompt_injection": "Use this.", **(extra_kwargs or {})}
    model = MentalModel(
        id=model_id,
        name=f"Test Model ({model_id})",
        description="A test model",
        **kw,
    )
    mgr.models[model_id] = model
    return mgr


class TestSkillHintsScoring:
    """Tests for skill_hints boost in get_models_for_context_scored."""

    def test_skill_hint_adds_6_points(self):
        mgr = make_manager_with_model("instruments_over_tracks")

        # Without hint: no score → excluded
        no_hint = mgr.get_models_for_context_scored(skill_hints=None)
        assert len(no_hint) == 0

        # With hint: score = 6 ≥ MIN_SCORE_THRESHOLD (5) → included
        with_hint = mgr.get_models_for_context_scored(skill_hints=["instruments_over_tracks"])
        assert len(with_hint) == 1
        model, score = with_hint[0]
        assert model.id == "instruments_over_tracks"
        assert score == 6

    def test_skill_hint_stacks_with_other_signals(self):
        """Skill hint +6 should stack with persona match +8."""
        mgr = make_manager_with_model(
            "progressive_autonomy",
            {"active_for_personas": ["scribe"]},
        )

        scored = mgr.get_models_for_context_scored(
            persona="scribe",
            skill_hints=["progressive_autonomy"],
        )
        assert len(scored) == 1
        model, score = scored[0]
        assert score == 14  # persona +8 + skill +6

    def test_unknown_hint_does_not_affect_other_models(self):
        """Hints for non-existent model IDs should be silently ignored."""
        mgr = make_manager_with_model("collaborative_maps", {"active_for_personas": ["librarian"]})

        scored = mgr.get_models_for_context_scored(
            persona="librarian",
            skill_hints=["non_existent_model_id"],
        )
        # collaborative_maps gets persona +8; non_existent is ignored
        assert len(scored) == 1
        model, score = scored[0]
        assert model.id == "collaborative_maps"
        assert score == 8

    def test_empty_skill_hints_no_effect(self):
        mgr = make_manager_with_model("instruments_over_tracks")
        result = mgr.get_models_for_context_scored(skill_hints=[])
        assert len(result) == 0

    def test_get_models_for_context_accepts_skill_hints(self):
        """get_models_for_context() (non-scored) should also accept skill_hints."""
        mgr = make_manager_with_model("instruments_over_tracks")
        result = mgr.get_models_for_context(skill_hints=["instruments_over_tracks"])
        assert len(result) == 1
        assert result[0].id == "instruments_over_tracks"

    def test_build_context_items_passes_skill_hints_through(self):
        """build_context_items(**kwargs) should forward skill_hints to scoring."""
        mgr = make_manager_with_model("instruments_over_tracks")

        # Patch get_models_for_context_scored to capture kwargs
        captured = {}
        original = mgr.get_models_for_context_scored

        def patched(*args, **kwargs):
            captured.update(kwargs)
            return original(*args, **kwargs)

        mgr.get_models_for_context_scored = patched

        mgr.build_context_items(
            "test query",
            ["scrolls"],
            persona="scribe",
            skill_hints=["instruments_over_tracks"],
        )

        assert "skill_hints" in captured
        assert captured["skill_hints"] == ["instruments_over_tracks"]

    def test_multiple_hints_can_activate_multiple_models(self):
        mgr = make_manager_with_model("instruments_over_tracks")
        mgr.models["collaborative_maps"] = __import__("core.mental_models", fromlist=["MentalModel"]).MentalModel(
            id="collaborative_maps",
            name="Collaborative Maps",
            description="Distributed knowledge",
            principles=["p1"],
            prompt_injection="Think collaboratively.",
        )

        result = mgr.get_models_for_context_scored(
            skill_hints=["instruments_over_tracks", "collaborative_maps"]
        )
        activated_ids = {m.id for m, _ in result}
        assert "instruments_over_tracks" in activated_ids
        assert "collaborative_maps" in activated_ids
