"""
Built-in workflow templates and TemplateRegistry (Phase 24b).

Built-in templates use capability names from PERSONA_CAPABILITY_MAP:
  scribe:    capture_note, organize_notes, summarize
  architect: plan_task, design_system, review_code
  professor: explain_concept, teach_topic, answer_question

Usage:
    storage = SwarmStorage(db_path)
    registry = TemplateRegistry(storage)
    registry.seed_builtins()          # idempotent; safe to call on every startup
    template = registry.get("research-to-write")
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from core.nexus.storage import SwarmStorage
from core.nexus.workflow import MergeStrategy, WorkflowStep, WorkflowTemplate

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Built-in templates
# ---------------------------------------------------------------------------

BUILTIN_TEMPLATES: Dict[str, WorkflowTemplate] = {
    # ------------------------------------------------------------------
    # research-to-write
    # Scribe pipeline: capture raw content → organize → produce summary
    # ------------------------------------------------------------------
    "research-to-write": WorkflowTemplate(
        id="research-to-write",
        name="Research → Write",
        description=(
            "Capture a research topic, organize the key ideas, "
            "then produce a polished written summary."
        ),
        steps=[
            WorkflowStep(
                id="capture",
                agent_capability="capture_note",
                input_mapping={"query": "$user_input"},
            ),
            WorkflowStep(
                id="organize",
                agent_capability="organize_notes",
                input_mapping={"query": "$capture.output"},
                depends_on=["capture"],
            ),
            WorkflowStep(
                id="write",
                agent_capability="summarize",
                input_mapping={"query": "$organize.output"},
                depends_on=["organize"],
            ),
        ],
        output_step="write",
        intervention_points=["capture"],
        domain_affinity=["writing", "notes", "knowledge"],
        merge_strategy=MergeStrategy.FIRST,
        is_builtin=True,
    ),

    # ------------------------------------------------------------------
    # capture-and-summarize
    # Minimal scribe workflow: capture → summarize
    # ------------------------------------------------------------------
    "capture-and-summarize": WorkflowTemplate(
        id="capture-and-summarize",
        name="Capture & Summarize",
        description=(
            "Capture a note and produce a concise summary. "
            "Ideal for quick knowledge capture workflows."
        ),
        steps=[
            WorkflowStep(
                id="capture",
                agent_capability="capture_note",
                input_mapping={"query": "$user_input"},
            ),
            WorkflowStep(
                id="summarize",
                agent_capability="summarize",
                input_mapping={"query": "$capture.output"},
                depends_on=["capture"],
            ),
        ],
        output_step="summarize",
        intervention_points=[],
        domain_affinity=["writing", "notes"],
        merge_strategy=MergeStrategy.FIRST,
        is_builtin=True,
    ),

    # ------------------------------------------------------------------
    # teach-and-assess
    # Professor pipeline: explain → structured lesson
    # ------------------------------------------------------------------
    "teach-and-assess": WorkflowTemplate(
        id="teach-and-assess",
        name="Teach & Assess",
        description=(
            "Explain a concept clearly, then produce a structured lesson "
            "suitable for learning or teaching others."
        ),
        steps=[
            WorkflowStep(
                id="explain",
                agent_capability="explain_concept",
                input_mapping={"query": "$user_input"},
            ),
            WorkflowStep(
                id="lesson",
                agent_capability="teach_topic",
                input_mapping={"query": "$explain.output"},
                depends_on=["explain"],
            ),
        ],
        output_step="lesson",
        intervention_points=["explain"],
        domain_affinity=["education", "learning", "teaching"],
        merge_strategy=MergeStrategy.FIRST,
        is_builtin=True,
    ),

    # ------------------------------------------------------------------
    # plan-and-review
    # Architect pipeline: plan → design system
    # ------------------------------------------------------------------
    "plan-and-review": WorkflowTemplate(
        id="plan-and-review",
        name="Plan & Review",
        description=(
            "Break down a complex goal into structured steps, "
            "then produce a system design based on the plan."
        ),
        steps=[
            WorkflowStep(
                id="plan",
                agent_capability="plan_task",
                input_mapping={"query": "$user_input"},
            ),
            WorkflowStep(
                id="design",
                agent_capability="design_system",
                input_mapping={"query": "$plan.output"},
                depends_on=["plan"],
            ),
        ],
        output_step="design",
        intervention_points=["plan"],
        domain_affinity=["code", "software", "architecture", "planning"],
        merge_strategy=MergeStrategy.FIRST,
        is_builtin=True,
    ),

    # ------------------------------------------------------------------
    # multi-domain-analysis
    # Parallel: scribe (capture) + professor (explain) → ensemble merge
    # Demonstrates true parallel execution across different agent types.
    # ------------------------------------------------------------------
    "multi-domain-analysis": WorkflowTemplate(
        id="multi-domain-analysis",
        name="Multi-Domain Analysis",
        description=(
            "Simultaneously capture a note and explain the concept, "
            "then combine both perspectives into a unified view."
        ),
        steps=[
            WorkflowStep(
                id="capture",
                agent_capability="capture_note",
                input_mapping={"query": "$user_input"},
                depends_on=[],
            ),
            WorkflowStep(
                id="explain",
                agent_capability="explain_concept",
                input_mapping={"query": "$user_input"},
                depends_on=[],
            ),
            # Merge step: depends on both parallel branches
            WorkflowStep(
                id="synthesize",
                agent_capability="summarize",
                input_mapping={"query": "$user_input"},
                depends_on=["capture", "explain"],
            ),
        ],
        output_step="synthesize",
        intervention_points=[],
        domain_affinity=["knowledge", "research", "education"],
        merge_strategy=MergeStrategy.ENSEMBLE,
        is_builtin=True,
    ),
}


# ---------------------------------------------------------------------------
# TemplateRegistry
# ---------------------------------------------------------------------------

class TemplateRegistry:
    """
    CRUD interface for workflow templates backed by SwarmStorage.

    Usage:
        registry = TemplateRegistry(storage)
        registry.seed_builtins()       # call on startup (idempotent)
        t = registry.get("research-to-write")
        all_t = registry.list_all(domain="writing")
    """

    def __init__(self, storage: SwarmStorage) -> None:
        self.storage = storage

    # ---- Built-in seeding ----

    def seed_builtins(self) -> None:
        """
        Upsert all BUILTIN_TEMPLATES into storage.

        Safe to call on every startup — uses INSERT OR REPLACE semantics.
        """
        for template in BUILTIN_TEMPLATES.values():
            try:
                self.storage.create_template(
                    template_id=template.id,
                    name=template.name,
                    definition=template.to_dict(),
                )
                logger.debug(f"TemplateRegistry: seeded built-in '{template.id}'")
            except Exception as e:
                logger.warning(
                    f"TemplateRegistry: failed to seed '{template.id}': {e}"
                )

    # ---- Read ----

    def get(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Return a WorkflowTemplate by ID, or None if not found."""
        d = self.storage.get_template(template_id)
        if d is None:
            return None
        d.pop("_usage_count", None)
        return WorkflowTemplate.from_dict(d)

    def list_all(self, domain: Optional[str] = None) -> List[WorkflowTemplate]:
        """
        Return all active templates, optionally filtered by domain affinity.

        Ordered by usage_count descending (most-used first).
        """
        dicts = self.storage.list_templates(domain=domain)
        templates = []
        for d in dicts:
            d.pop("_usage_count", None)
            try:
                templates.append(WorkflowTemplate.from_dict(d))
            except Exception as e:
                logger.warning(f"TemplateRegistry: skipping malformed template: {e}")
        return templates

    # ---- Write ----

    def create(self, template: WorkflowTemplate) -> str:
        """
        Validate and store a new (user-defined) workflow template.

        Returns the template ID.

        Raises:
            ValueError: If the template fails structural validation.
        """
        template.validate()
        self.storage.create_template(
            template_id=template.id,
            name=template.name,
            definition=template.to_dict(),
        )
        logger.info(f"TemplateRegistry: created template '{template.id}'")
        return template.id

    def update(self, template_id: str, template: WorkflowTemplate) -> None:
        """
        Replace the definition of an existing template.

        Raises:
            ValueError: If the template fails structural validation or does not exist.
        """
        existing = self.storage.get_template(template_id)
        if existing is None:
            raise ValueError(f"TemplateRegistry: template '{template_id}' not found")
        template.validate()
        self.storage.update_template(template_id, template.to_dict())
        logger.info(f"TemplateRegistry: updated template '{template_id}'")

    def delete(self, template_id: str) -> bool:
        """
        Soft-delete a template. Returns True if found and deleted.
        """
        result = self.storage.delete_template(template_id)
        if result:
            logger.info(f"TemplateRegistry: deleted template '{template_id}'")
        return result

    def __repr__(self) -> str:
        return f"<TemplateRegistry storage={self.storage}>"
