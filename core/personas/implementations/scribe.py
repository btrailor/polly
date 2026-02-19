"""
Scribe Persona (Phase 16c Days 9-10)

The Scribe persona transforms conversations into structured notes with automatic
wiki-linking to existing knowledge base content.

Modes:
- Capture: Analyze conversation and extract key concepts
- Organize: Ask clarifying questions via radio buttons
- Enrich: Generate markdown with auto [[wiki-links]]
- Edit: Improve existing notes while preserving structure

Model Routing:
- Capture mode: Fast tier (Haiku 4 preferred)
- Organize mode: Fast tier (Haiku 4 preferred)
- Enrich mode: Balanced tier (Sonnet 4 preferred)
- Edit mode: Balanced tier (Sonnet 4 preferred)
"""

from typing import Dict, List, Optional, Any
import json
import re
import logging
from datetime import datetime

from ..base import AgentPersona, PersonaContext, PersonaResponse, PersonaAction
from core.router_v2 import TaskType, ConfidenceLevel

logger = logging.getLogger(__name__)


class ScribePersona(AgentPersona):
    """
    Scribe persona for transforming conversations into structured notes.
    
    Primary use case: Save conversation as note (Phase 16c)
    
    Workflow:
    1. User: "Save this conversation as a note"
    2. Scribe activates in Capture mode
    3. Scribe analyzes conversation, extracts concepts
    4. Scribe switches to Organize mode
    5. Scribe asks clarifying questions (radio buttons)
    6. User answers questions
    7. Scribe switches to Enrich mode
    8. Scribe generates markdown with [[wiki-links]]
    9. Preview modal shows note
    10. User reviews and saves
    """
    
    def __init__(self, name: str, router: Any, skill_manager: Any = None, rag: Any = None, pattern_engine: Any = None):
        """
        Initialize Scribe persona.
        
        Args:
            name: Persona name ("scribe")
            router: IntelligentRouterV2 instance for LLM calls
            skill_manager: SkillManager instance for loading skills
            rag: UnifiedRAG instance for related note search
            pattern_engine: PatternEngine instance for pattern-informed enrichment (Task #24)
        """
        super().__init__(name, router)
        self.skill_manager = skill_manager
        self.rag = rag
        self.pattern_engine = pattern_engine
        
        logger.info(f"Initialized Scribe persona (skills: {skill_manager is not None}, rag: {rag is not None}, patterns: {pattern_engine is not None})")
    
    @property
    def default_mode(self) -> str:
        return "capture"
    
    @property
    def available_modes(self) -> List[str]:
        return ["capture", "organize", "enrich", "edit"]
    
    async def process(self, context: PersonaContext) -> PersonaResponse:
        """
        Route to appropriate mode handler.
        
        Args:
            context: PersonaContext with user message and conversation
        
        Returns:
            PersonaResponse from mode-specific handler
        """
        mode = self.state.current_mode
        
        logger.info(f"Scribe processing in {mode} mode")
        
        if mode == "capture":
            return await self.capture(context)
        elif mode == "organize":
            return await self.organize(context)
        elif mode == "enrich":
            return await self.enrich(context)
        elif mode == "edit":
            return await self.edit(context)
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    def get_mode_prompts(self) -> Dict[str, str]:
        """
        Return mode-specific system prompts.
        
        These are loaded from scribe.yaml definition file by PersonaManager.
        This method is here for compatibility but the actual prompts come
        from the YAML file loaded by PersonaManager's lazy-loading system.
        """
        # Prompts are loaded from scribe.yaml by PersonaManager
        # This is just a fallback if YAML loading fails
        return {
            "capture": "You are Scribe in Capture mode. Analyze conversations and extract key concepts.",
            "organize": "You are Scribe in Organize mode. Ask clarifying questions using radio buttons.",
            "enrich": "You are Scribe in Enrich mode. Generate markdown with auto [[wiki-links]].",
            "edit": "You are Scribe in Edit mode. Improve existing notes while preserving structure."
        }
    
    # ========== Capture Mode ==========
    
    async def capture(self, context: PersonaContext) -> PersonaResponse:
        """
        Capture mode: Analyze conversation and extract key concepts.
        
        Process:
        1. Read conversation history (with compression if >8k tokens)
        2. Identify conversation type (meeting, concept, howto, etc.)
        3. Extract key concepts, insights, entities
        4. Identify relationships between concepts
        5. Suggest template and domain
        6. Return structured analysis
        
        Args:
            context: PersonaContext with conversation history
        
        Returns:
            PersonaResponse with concept extraction and metadata
        """
        logger.info("Scribe Capture mode: analyzing conversation")
        
        # Build messages for LLM
        messages = self._build_messages(context, include_history=True)
        
        # Add instruction to return JSON
        messages.append({
            "role": "system",
            "content": "Return your analysis as valid JSON matching the format specified in your prompt."
        })
        
        # Use fast tier for capture (Haiku 4 preferred)
        try:
            response = await self.router.complete_with_fallback(
                messages=messages,
                task_type=TaskType.DOCUMENTATION,
                confidence=ConfidenceLevel.FAST,
                max_tokens=2000,
                temperature=0.5
            )
        except Exception as e:
            logger.error(f"Router failed in capture mode: {e}")
            return PersonaResponse(
                content=f"Sorry, I encountered an error while analyzing the conversation: {str(e)}",
                mode="capture",
                actions=[],
                metadata={"error": str(e)}
            )
        
        # Parse JSON response
        try:
            analysis = self._parse_capture_response(response.content)
        except Exception as e:
            logger.error(f"Failed to parse capture response: {e}")
            # Fallback to simple analysis
            analysis = {
                "conversation_type": "quick",
                "primary_topic": "Conversation summary",
                "key_concepts": [],
                "entities": {},
                "action_items": [],
                "decisions": [],
                "questions": [],
                "suggested_template": "quick-note",
                "suggested_domain": "scrolls",
                "note_title_suggestions": ["Conversation Note"]
            }
        
        # Store analysis in state
        self.state.set_data("capture_analysis", analysis)
        self.state.set_data("captured_at", datetime.now().isoformat())
        
        # Show template gallery with suggested template (Phase 16e)
        suggested_template_filename = self._map_template_to_filename(analysis.get("suggested_template", "quick-note"))
        
        actions = [PersonaAction(
            type="show_template_gallery",
            data={
                "suggested_template": suggested_template_filename,
                "conversation_type": analysis.get("conversation_type", "quick"),
                "note_title_suggestions": analysis.get("note_title_suggestions", [])
            }
        )]
        
        # Format output for user
        output = self._format_capture_output(analysis)
        
        return PersonaResponse(
            content=output,
            mode="capture",
            actions=actions,
            metadata={
                "analysis": analysis,
                "model_used": response.model,
                "tokens_in": response.tokens_in,
                "tokens_out": response.tokens_out,
                "cost": response.cost
            }
        )
    
    # ========== Organize Mode ==========
    
    async def organize(self, context: PersonaContext) -> PersonaResponse:
        """
        Organize mode: Ask clarifying questions via radio buttons.
        
        Process:
        1. Load capture analysis from state
        2. Load template-guide and domain-structure skills
        3. Generate 3-5 radio button questions
        4. Return questions for UI to display
        
        Args:
            context: PersonaContext
        
        Returns:
            PersonaResponse with radio button questions
        """
        logger.info("Scribe Organize mode: generating questions")
        
        # Load capture analysis
        analysis = self.state.get_data("capture_analysis")
        if not analysis:
            return PersonaResponse(
                content="No analysis found. Please switch back to Capture mode first.",
                mode="organize",
                actions=[PersonaAction(
                    type="suggest_mode_switch",
                    data={"target_mode": "capture", "message": "Capture conversation first"}
                )],
                metadata={"error": "no_analysis"}
            )
        
        # Load skills
        template_skill = None
        domain_skill = None
        
        if self.skill_manager:
            template_skill = self.skill_manager.load_skill("template-guide")
            domain_skill = self.skill_manager.load_skill("domain-structure")
            
            logger.info(f"Loaded skills: template-guide={template_skill is not None}, domain-structure={domain_skill is not None}")
        
        # Build prompt with analysis and skills
        organize_prompt = self._build_organize_prompt(analysis, template_skill, domain_skill)
        
        messages = [
            {"role": "system", "content": self.get_system_prompt("organize")},
            {"role": "user", "content": organize_prompt}
        ]
        
        # Add instruction to return JSON
        messages.append({
            "role": "system",
            "content": "Return your questions as valid JSON matching the format specified in your prompt."
        })
        
        # Use fast tier for organize (Haiku 4 preferred)
        try:
            response = await self.router.complete_with_fallback(
                messages=messages,
                task_type=TaskType.SIMPLE_QUERY,
                confidence=ConfidenceLevel.FAST,
                max_tokens=1500,
                temperature=0.7
            )
        except Exception as e:
            logger.error(f"Router failed in organize mode: {e}")
            return PersonaResponse(
                content=f"Sorry, I encountered an error while generating questions: {str(e)}",
                mode="organize",
                actions=[],
                metadata={"error": str(e)}
            )
        
        # Parse questions response
        try:
            questions_data = self._parse_organize_response(response.content)
        except Exception as e:
            logger.error(f"Failed to parse organize response: {e}")
            # Fallback to basic questions
            questions_data = self._generate_fallback_questions(analysis)
        
        # Store questions in state
        self.state.set_data("questions", questions_data)
        self.state.set_data("organized_at", datetime.now().isoformat())
        
        # Generate UI action to show questions
        actions = [PersonaAction(
            type="show_questions",
            data={
                "questions": questions_data.get("questions", []),
                "summary": questions_data.get("summary", "Ready to create your note")
            }
        )]
        
        # Format output for user
        output = self._format_organize_output(questions_data)
        
        return PersonaResponse(
            content=output,
            mode="organize",
            actions=actions,
            metadata={
                "questions": questions_data,
                "model_used": response.model,
                "tokens_in": response.tokens_in,
                "tokens_out": response.tokens_out,
                "cost": response.cost
            }
        )
    
    # ========== Enrich Mode ==========
    
    async def enrich(self, context: PersonaContext) -> PersonaResponse:
        """
        Enrich mode: Generate markdown using selected template (Phase 16e).
        
        New Process:
        1. Load capture analysis and template_filename from metadata
        2. Load template from API
        3. Use template's AI hints (tone, focus, linking_priority)
        4. Generate content to fill template variables
        5. Query RAG to find related notes (similarity ≥0.85)
        6. Insert [[wiki-links]] following rules
        7. Apply smart defaults (domain, folder, tags)
        8. Return note with preview action
        
        Args:
            context: PersonaContext with template_filename in metadata
        
        Returns:
            PersonaResponse with generated note and preview action
        """
        logger.info("Scribe Enrich mode: generating note from template")
        
        # Load analysis
        analysis = self.state.get_data("capture_analysis")
        
        if not analysis:
            return PersonaResponse(
                content="No analysis found. Please run Capture mode first.",
                mode="enrich",
                actions=[PersonaAction(
                    type="suggest_mode_switch",
                    data={"target_mode": "capture", "message": "Start from Capture mode"}
                )],
                metadata={"error": "no_analysis"}
            )
        
        # Get template filename from metadata
        template_filename = context.metadata.get("template_filename")
        if not template_filename:
            logger.error("No template_filename in metadata")
            return PersonaResponse(
                content="No template selected. Please choose a template from the gallery.",
                mode="enrich",
                actions=[],
                metadata={"error": "no_template"}
            )
        
        # Load template from API
        try:
            template = await self._load_template(template_filename)
        except Exception as e:
            logger.error(f"Failed to load template {template_filename}: {e}")
            return PersonaResponse(
                content=f"Failed to load template: {str(e)}",
                mode="enrich",
                actions=[],
                metadata={"error": f"template_load_failed: {str(e)}"}
            )
        
        logger.info(f"Loaded template: {template['name']} with {len(template['variables'])} variables")
        
        # Load skills
        linking_skill = None
        domain_skill = None
        
        if self.skill_manager:
            linking_skill = self.skill_manager.load_skill("wiki-linking")
            domain_skill = self.skill_manager.load_skill("domain-structure")
            
            logger.info(f"Loaded skills for enrich: linking={linking_skill is not None}, domain={domain_skill is not None}")
        
        # Build generation prompt using template
        enrich_prompt = self._build_template_enrich_prompt(
            analysis, template, linking_skill, domain_skill, context
        )
        
        # Get Scribe-specific memory context (preferences, patterns) — Task #24
        # Use targeted multi-query retrieval for domain + template + edit feedback
        enrich_domain = template.get("smart_defaults", {}).get("domain", "scrolls")
        memory_context = self._get_enrichment_preferences(
            domain=enrich_domain,
            template_name=template['name'],
        )
        # Fall back to general memory context if no targeted preferences
        if not memory_context:
            memory_context = self._get_memory_context(
                f"enrichment style preferences for {template['name']} template"
            )
        
        # Build system prompt with memory context
        system_prompt = self.get_system_prompt("enrich")
        if memory_context:
            system_prompt = f"{system_prompt}\n\n{memory_context}"
        
        # Get pattern context for structure/concept boosting (Task #24)
        pattern_query = " ".join(
            analysis.get("note_title_suggestions", [])[:2]
            + analysis.get("key_concepts", [])[:3]
        )
        if pattern_query:
            pattern_context = self._get_pattern_context(
                query=pattern_query,
                domain=enrich_domain,
            )
            if pattern_context:
                system_prompt = f"{system_prompt}\n\n{pattern_context}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": enrich_prompt}
        ]
        
        # Use balanced tier for enrich (Sonnet 4 preferred)
        try:
            response = await self.router.complete_with_fallback(
                messages=messages,
                task_type=TaskType.CREATIVE,
                confidence=ConfidenceLevel.BALANCED,
                max_tokens=4000,
                temperature=0.8
            )
        except Exception as e:
            logger.error(f"Router failed in enrich mode: {e}")
            return PersonaResponse(
                content=f"Sorry, I encountered an error while generating the note: {str(e)}",
                mode="enrich",
                actions=[],
                metadata={"error": str(e)}
            )
        
        # Auto-link: Find and insert [[wiki-links]]
        enriched_content, inserted_links = await self._auto_link_content(
            response.content, linking_skill
        )
        
        # Parse generated note (should be JSON with variable values)
        try:
            generated_data = self._parse_template_enrich_response(enriched_content)
        except Exception as e:
            logger.error(f"Failed to parse enrich response as JSON: {e}")
            # Use raw content as fallback
            generated_data = {
                "title": analysis.get("note_title_suggestions", ["Untitled Note"])[0],
                "variables": {},
                "raw_content": enriched_content
            }
        
        # Render template with generated content
        try:
            if "raw_content" in generated_data:
                # Fallback: use raw content
                final_content = generated_data["raw_content"]
            else:
                # Normal path: render template with variables
                final_content = self._render_template(template, generated_data["variables"])
        except Exception as e:
            logger.error(f"Failed to render template: {e}")
            final_content = enriched_content  # Ultimate fallback
        
        # Apply smart defaults from template
        ai_hints = template.get("ai_hints", {})
        smart_defaults = template.get("smart_defaults", {})
        
        title = generated_data.get("title") or analysis.get("note_title_suggestions", ["Untitled Note"])[0]
        domain = smart_defaults.get("domain", "scrolls")
        folder = smart_defaults.get("folder", "")
        tags = smart_defaults.get("tags", [])
        
        # Build metadata
        metadata = {
            "title": title,
            "domain": domain,
            "folder": folder,
            "filename": f"{title.replace(' ', '-').lower()}.md",
            "template_used": template["filename"],
            "template_name": template["name"],
            "tags": tags,
            "ai_tone": ai_hints.get("tone", ""),
            "ai_focus": ai_hints.get("focus", ""),
            "inserted_links": inserted_links,
        }
        
        note_data = {
            "content": final_content,
            "metadata": metadata
        }
        
        # Store generated note in state
        self.state.set_data("generated_note", note_data)
        self.state.set_data("enriched_at", datetime.now().isoformat())
        
        # Record enrichment preferences in Mem0 (Task #24)
        self._record_enrichment_feedback(
            title=title,
            domain=domain,
            template_name=template["name"],
            content=final_content,
            inserted_links=inserted_links,
            tags=tags,
        )
        
        # Generate preview action
        actions = [PersonaAction(
            type="show_preview",
            data={
                "content": note_data["content"],
                "title": metadata["title"],
                "format": "markdown",
                "preview_type": "note",
                "save_path": folder + metadata["filename"],
                "metadata": metadata  # Include full metadata for save
            }
        )]
        
        # Format output
        output = f"""**Note Generated from Template: {template['name']}**

**Title:** {metadata['title']}
**Domain:** {metadata['domain']}
**Tags:** {', '.join(tags) if tags else 'None'}

Preview ready! Review and save your note."""
        
        return PersonaResponse(
            content=output,
            mode="enrich",
            actions=actions,
            metadata={
                "note": note_data,
                "model_used": response.model,
                "tokens_in": response.tokens_in,
                "tokens_out": response.tokens_out,
                "cost": response.cost
            }
        )
    
    # ========== Standalone Enrich (for KnowledgeWriter) ==========
    
    async def enrich_standalone(
        self,
        content: str,
        title: str,
        domain: str = "scrolls",
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Standalone enrich entry point for KnowledgeWriter.
        
        Skips Capture and Organize modes — takes raw content and produces
        an enriched note with wiki-links and proper formatting.
        
        Args:
            content: Raw text content to enrich
            title: Suggested note title
            domain: Target domain slug
            conversation_history: Optional conversation for additional context
        
        Returns:
            Dict with 'content', 'metadata' suitable for PreviewModal
        """
        logger.info(f"Scribe standalone enrich: title='{title}', domain='{domain}'")
        
        # Build a lightweight analysis from the raw content
        analysis = {
            "key_concepts": [],
            "note_title_suggestions": [title],
            "summary": content[:300],
            "domain": domain,
        }
        
        # Load linking skill for wiki-links
        linking_skill = None
        if self.skill_manager:
            linking_skill = self.skill_manager.load_skill("wiki-linking")
        
        # Build a simplified enrich prompt (no template required)
        enrich_prompt = f"""You are Polly's Scribe. Your task is to take the raw content below and transform it into a well-structured knowledge base note.

**Title:** {title}
**Domain:** {domain}

**Raw Content:**
{content}

**Instructions:**
1. Structure the content with clear headings (##, ###)
2. Add [[wiki-links]] to any concepts, tools, or topics that might exist in the user's knowledge base
3. Add a brief summary at the top
4. Use bullet points and code blocks where appropriate
5. Keep the original information intact — enrich, don't rewrite
6. Output ONLY the markdown content (no JSON wrapper)

Generate the enriched note:"""

        # Get enrichment preferences from Mem0 (Task #24)
        memory_context = self._get_enrichment_preferences(
            domain=domain,
            template_name="standalone",
        )
        if not memory_context:
            memory_context = self._get_memory_context(
                f"enrichment style preferences for {domain} domain"
            )
        
        system_prompt = self.get_system_prompt("enrich")
        if memory_context:
            system_prompt = f"{system_prompt}\n\n{memory_context}"
        
        # Get pattern context for structure/concept boosting (Task #24)
        pattern_context = self._get_pattern_context(
            query=f"{title} {domain}",
            domain=domain,
        )
        if pattern_context:
            system_prompt = f"{system_prompt}\n\n{pattern_context}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": enrich_prompt}
        ]
        
        try:
            response = await self.router.complete_with_fallback(
                messages=messages,
                task_type=TaskType.CREATIVE,
                confidence=ConfidenceLevel.BALANCED,
                max_tokens=4000,
                temperature=0.7
            )
        except Exception as e:
            logger.error(f"Standalone enrich failed: {e}")
            # Return the raw content as fallback
            return {
                "content": content,
                "metadata": {
                    "title": title,
                    "domain": domain,
                    "tags": [],
                    "error": str(e),
                }
            }
        
        # Auto-link the enriched content
        enriched_content, inserted_links = await self._auto_link_content(
            response.content, linking_skill
        )
        
        # Build frontmatter
        now = datetime.now()
        final_content = f"""---
title: "{title}"
date: {now.strftime('%Y-%m-%d')}
domain: {domain}
source: scribe_enrich
created_by: scribe_standalone
---

{enriched_content}
"""
        
        metadata = {
            "title": title,
            "domain": domain,
            "folder": "",
            "filename": f"{title.replace(' ', '-').lower()}.md",
            "tags": [],
            "template_used": "none (standalone enrich)",
            "inserted_links": inserted_links,
        }
        
        # Record enrichment preferences in Mem0 (Task #24)
        self._record_enrichment_feedback(
            title=title,
            domain=domain,
            template_name="standalone",
            content=final_content,
            inserted_links=inserted_links,
        )
        
        return {
            "content": final_content,
            "metadata": metadata,
        }
    
    # ========== Enrichment Feedback (Task #24) ==========
    
    def _get_enrichment_preferences(
        self,
        domain: str,
        template_name: str,
    ) -> str:
        """
        Query Mem0 for enrichment preferences across multiple dimensions.
        
        Makes targeted queries for:
        1. Domain-specific preferences (linking density, note length, structure)
        2. Template-specific preferences (which templates work for which domains)
        3. Edit feedback (what the user changed after enrichment)
        
        Returns a formatted instruction block for the system prompt.
        Empty string if Mem0 is disabled or no relevant memories found.
        
        Args:
            domain: Target domain (e.g. "scrolls", "workshop")
            template_name: Template being used (or "standalone")
        
        Returns:
            Formatted preferences string for system prompt injection
        """
        if not self.mem0:
            return ""
        
        try:
            user_id = f"persona:{self.name}"
            all_memories = []
            
            # Query 1: Domain-specific enrichment preferences
            domain_memories = self.mem0.search_memory(
                f"enrichment preferences for {domain} domain notes",
                user_id=user_id,
                limit=3,
            )
            all_memories.extend(domain_memories)
            
            # Query 2: Template-specific preferences
            if template_name and template_name != "standalone":
                template_memories = self.mem0.search_memory(
                    f"template preferences for {template_name}",
                    user_id=user_id,
                    limit=2,
                )
                all_memories.extend(template_memories)
            
            # Query 3: Edit feedback (what user changed after enrichment)
            edit_memories = self.mem0.search_memory(
                f"user edit feedback link removal content changes {domain}",
                user_id=user_id,
                limit=3,
            )
            all_memories.extend(edit_memories)
            
            if not all_memories:
                return ""
            
            # Deduplicate by memory text
            seen_texts = set()
            unique_memories = []
            for mem in all_memories:
                text = mem.get('memory', '')
                if text and text not in seen_texts:
                    seen_texts.add(text)
                    unique_memories.append(mem)
            
            if not unique_memories:
                return ""
            
            # Format as actionable preferences block
            pref_lines = []
            for mem in unique_memories[:6]:  # Cap at 6 to avoid prompt bloat
                text = mem.get('memory', '')
                score = mem.get('score', 0)
                if score >= 0.5:  # Only use reasonably relevant memories
                    pref_lines.append(f"- {text}")
            
            if not pref_lines:
                return ""
            
            preferences = (
                "## User Enrichment Preferences (from past interactions)\n"
                "Apply these preferences when generating the note. "
                "They reflect the user's actual editing patterns and choices:\n"
                + "\n".join(pref_lines)
            )
            
            logger.debug(
                f"Retrieved {len(pref_lines)} enrichment preferences "
                f"for domain={domain}, template={template_name}"
            )
            
            return preferences
            
        except Exception as e:
            logger.warning(f"Failed to get enrichment preferences: {e}")
            return ""
    
    def _get_pattern_context(
        self,
        query: str,
        domain: str,
    ) -> str:
        """
        Query PatternEngine for patterns relevant to the enrichment.
        
        Retrieves DOMAIN, CONCEPTUAL, and QUERY patterns that can inform:
        - Domain auto-suggestion (DOMAIN patterns)
        - Structure reuse from similar notes (QUERY patterns)
        - Relevant concepts to boost/link (CONCEPTUAL patterns)
        
        Args:
            query: Search query (typically the note title or key concepts)
            domain: Target domain slug
        
        Returns:
            Formatted pattern context string for system prompt injection.
            Empty string if PatternEngine is unavailable or no patterns found.
        """
        if not self.pattern_engine:
            return ""
        
        try:
            domains = [domain] if domain else []
            patterns = self.pattern_engine.get_patterns_for_prompt(
                query=query,
                domains=domains,
                limit=5,
            )
            
            if not patterns:
                return ""
            
            pattern_lines = []
            for p in patterns:
                # Include pattern type for the LLM to understand context
                ptype = p.pattern_type.value if hasattr(p.pattern_type, 'value') else str(p.pattern_type)
                confidence_pct = int(p.confidence * 100)
                
                if ptype == "domain" or ptype == "domain_priority":
                    pattern_lines.append(
                        f"- [Domain] {p.description} (confidence: {confidence_pct}%)"
                    )
                elif ptype == "conceptual":
                    pattern_lines.append(
                        f"- [Concept] {p.description} (confidence: {confidence_pct}%)"
                    )
                elif ptype == "query":
                    pattern_lines.append(
                        f"- [Prior Note] {p.description} (confidence: {confidence_pct}%)"
                    )
                else:
                    pattern_lines.append(
                        f"- [{ptype.title()}] {p.description} (confidence: {confidence_pct}%)"
                    )
            
            if not pattern_lines:
                return ""
            
            context = (
                "## Relevant Patterns from User's History\n"
                "These patterns were learned from the user's previous interactions. "
                "Use them to inform structure, concepts, and linking:\n"
                + "\n".join(pattern_lines)
            )
            
            logger.debug(
                f"Retrieved {len(pattern_lines)} patterns for enrichment "
                f"(query='{query[:50]}...', domain={domain})"
            )
            
            return context
            
        except Exception as e:
            logger.warning(f"Failed to get pattern context for enrichment: {e}")
            return ""
    
    def _record_enrichment_feedback(
        self,
        title: str,
        domain: str,
        template_name: str,
        content: str,
        inserted_links: Dict[str, Any],
        tags: List[str] = None,
    ) -> None:
        """
        Record enrichment preferences in Mem0 after each Scribe enrichment.
        
        Stores structured preference memories that future enrichments
        can query to provide user-aligned defaults (linking density,
        template affinity, note length, domain patterns).
        
        This is the write-back side of the persona memory loop.
        _get_memory_context() is the read side (already wired in enrich).
        
        Args:
            title: Note title
            domain: Target domain (e.g. "scrolls", "workshop")
            template_name: Template used (or "standalone")
            content: Final enriched content
            inserted_links: Dict with link stats from _auto_link_content()
            tags: Optional tags applied to the note
        """
        if not self.mem0:
            return
        
        try:
            # Compute enrichment metrics
            word_count = len(content.split())
            link_count = len(re.findall(r'\[\[.+?\]\]', content))
            heading_count = len(re.findall(r'^#{1,6}\s', content, re.MULTILINE))
            code_block_count = len(re.findall(r'```', content)) // 2
            
            # Determine note length category
            if word_count < 300:
                length_pref = "concise"
            elif word_count < 800:
                length_pref = "moderate"
            else:
                length_pref = "detailed"
            
            # Determine linking density category
            if link_count == 0:
                link_density = "none"
            elif link_count <= 3:
                link_density = "sparse"
            elif link_count <= 7:
                link_density = "moderate"
            else:
                link_density = "dense"
            
            # Build preference memory strings and store each one
            # 1. Template + domain preference
            template_memory = (
                f"User used '{template_name}' template for '{domain}' domain note. "
                f"Note was {word_count} words ({length_pref}), "
                f"{link_count} wiki-links ({link_density} linking), "
                f"{heading_count} headings."
            )
            self._add_memory(
                content=template_memory,
                metadata={
                    'type': 'enrichment_preference',
                    'subtype': 'template_domain',
                    'domain': domain,
                    'template': template_name,
                    'word_count': word_count,
                    'link_count': link_count,
                    'heading_count': heading_count,
                    'code_blocks': code_block_count,
                    'length_preference': length_pref,
                    'link_density': link_density,
                    'timestamp': datetime.now().isoformat(),
                }
            )
            
            # 2. Linking style preference (only if links were inserted)
            if link_count > 0:
                link_targets = re.findall(r'\[\[(.+?)(?:\|.+?)?\]\]', content)
                link_memory = (
                    f"User prefers {link_density} linking ({link_count} links) "
                    f"in {domain} domain notes. "
                    f"Link targets: {', '.join(link_targets[:5])}."
                )
                self._add_memory(
                    content=link_memory,
                    metadata={
                        'type': 'enrichment_preference',
                        'subtype': 'linking_style',
                        'domain': domain,
                        'link_density': link_density,
                        'link_count': link_count,
                        'timestamp': datetime.now().isoformat(),
                    }
                )
            
            # 3. Structure preference
            has_frontmatter = content.startswith('---')
            has_bullet_lists = bool(re.search(r'^\s*[-*]\s', content, re.MULTILINE))
            has_numbered_lists = bool(re.search(r'^\s*\d+\.\s', content, re.MULTILINE))
            
            structure_memory = (
                f"User's {domain} note structure: {heading_count} headings, "
                f"{'uses' if has_bullet_lists else 'no'} bullet lists, "
                f"{'uses' if has_numbered_lists else 'no'} numbered lists, "
                f"{code_block_count} code blocks, "
                f"{'has' if has_frontmatter else 'no'} frontmatter."
            )
            self._add_memory(
                content=structure_memory,
                metadata={
                    'type': 'enrichment_preference',
                    'subtype': 'structure_style',
                    'domain': domain,
                    'has_frontmatter': has_frontmatter,
                    'has_bullet_lists': has_bullet_lists,
                    'has_numbered_lists': has_numbered_lists,
                    'code_blocks': code_block_count,
                    'heading_count': heading_count,
                    'timestamp': datetime.now().isoformat(),
                }
            )
            
            logger.info(
                f"Recorded enrichment feedback: domain={domain}, "
                f"template={template_name}, words={word_count}, "
                f"links={link_count} ({link_density})"
            )
            
        except Exception as e:
            logger.warning(f"Failed to record enrichment feedback (non-critical): {e}")
    
    # ========== Edit Mode ==========
    
    async def edit(self, context: PersonaContext) -> PersonaResponse:
        """
        Edit mode: Improve existing notes while preserving structure.
        
        Process:
        1. Load existing note from context
        2. Parse edit request (clarify, expand, condense, reorganize, link)
        3. Load relevant skills
        4. Apply edits while preserving structure
        5. Update [[wiki-links]] as needed
        6. Return edited note with changes summary
        
        Args:
            context: PersonaContext with edit request and note content
        
        Returns:
            PersonaResponse with edited note and change summary
        """
        logger.info("Scribe Edit mode: improving existing note")
        
        # Get existing note from context metadata
        existing_note = context.metadata.get("note_content")
        if not existing_note:
            return PersonaResponse(
                content="No note provided for editing. Please provide the note content.",
                mode="edit",
                actions=[],
                metadata={"error": "no_note"}
            )
        
        # Load skills
        template_skill = None
        linking_skill = None
        
        if self.skill_manager:
            template_skill = self.skill_manager.load_skill("template-guide")
            linking_skill = self.skill_manager.load_skill("wiki-linking")
        
        # Build edit prompt
        edit_prompt = self._build_edit_prompt(
            existing_note, context.user_message, template_skill, linking_skill
        )
        
        messages = [
            {"role": "system", "content": self.get_system_prompt("edit")},
            {"role": "user", "content": edit_prompt}
        ]
        
        # Use balanced tier for edit (Sonnet 4 preferred)
        try:
            response = await self.router.complete_with_fallback(
                messages=messages,
                task_type=TaskType.CREATIVE,
                confidence=ConfidenceLevel.BALANCED,
                max_tokens=4000,
                temperature=0.7
            )
        except Exception as e:
            logger.error(f"Router failed in edit mode: {e}")
            return PersonaResponse(
                content=f"Sorry, I encountered an error while editing: {str(e)}",
                mode="edit",
                actions=[],
                metadata={"error": str(e)}
            )
        
        # Parse edited note
        try:
            edited_data = self._parse_edit_response(response.content)
        except Exception as e:
            logger.error(f"Failed to parse edit response: {e}")
            edited_data = {
                "content": response.content,
                "changes": {
                    "summary": "Edited note",
                    "change_type": "general"
                }
            }
        
        # Store edited note in state
        self.state.set_data("edited_note", edited_data)
        self.state.set_data("edited_at", datetime.now().isoformat())
        
        # Generate preview action
        actions = [PersonaAction(
            type="show_preview",
            data={
                "content": edited_data["content"],
                "title": "Edited Note",
                "format": "markdown",
                "preview_type": "diff",
                "original": existing_note
            }
        )]
        
        # Format output
        output = self._format_edit_output(edited_data)
        
        return PersonaResponse(
            content=output,
            mode="edit",
            actions=actions,
            metadata={
                "edited_note": edited_data,
                "model_used": response.model,
                "tokens_in": response.tokens_in,
                "tokens_out": response.tokens_out,
                "cost": response.cost
            }
        )
    
    # ========== Helper Methods: Parsing ==========
    
    def _parse_capture_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response from capture mode"""
        # Try to extract JSON from content
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        
        # Fallback: try to parse entire content
        return json.loads(content)
    
    def _parse_organize_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response from organize mode"""
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        
        return json.loads(content)
    
    def _parse_enrich_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response from enrich mode"""
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        
        # Fallback: treat entire content as markdown
        return {
            "content": content,
            "metadata": {
                "title": "Generated Note",
                "domain": "scrolls",
                "link_count": 0
            }
        }
    
    def _parse_edit_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response from edit mode"""
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        
        return {
            "content": content,
            "changes": {"summary": "Edited"}
        }
    
    def _parse_user_answers(
        self, context: PersonaContext, questions_data: Dict
    ) -> Dict[str, str]:
        """Parse user answers from context"""
        # In production, answers would be in context.metadata
        answers = context.metadata.get("user_answers", {})
        
        # Also check message for answers
        if context.user_message and not answers:
            # Simple parsing: treat message as answer to template question
            answers = {"template": "quick-note", "domain": "scrolls"}
        
        return answers
    
    # ========== Helper Methods: Prompt Construction ==========
    
    def _build_organize_prompt(
        self, analysis: Dict, template_skill, domain_skill
    ) -> str:
        """Build prompt for organize mode"""
        prompt = f"""Based on this conversation analysis, generate ONLY clarifying questions that help refine the note structure.

**Analysis:**
- Type: {analysis.get('conversation_type')}
- Topic: {analysis.get('primary_topic')}
- Concepts: {len(analysis.get('key_concepts', []))} key concepts identified
- Suggested template: {analysis.get('suggested_template')}
- Suggested domain: {analysis.get('suggested_domain')}

**IMPORTANT RULES:**
1. DO NOT ask for note title - you will generate it automatically
2. DO NOT ask "what is the main topic" - you already analyzed it
3. DO NOT ask "how many concepts to identify" - decide automatically based on content
4. DO NOT ask "what domain" - infer from content (e.g., Max4Live = Signals + Sigils)
5. DO NOT ask "what format" - always use markdown

**ONLY ASK questions that genuinely need user input:**
- Is this a project idea, tutorial, reference doc, or conceptual note?
- Should this include code examples/technical details?
- Are there specific existing notes this should link to?
- Is this work-in-progress or complete/polished?

**If the analysis is clear enough (you have topic, type, domain), return ZERO questions and proceed directly to note generation.**

Generate 0-3 radio button questions ONLY if truly necessary for clarity.
"""
        
        if template_skill:
            prompt += f"\n**Available Templates:**\n{template_skill.get_section('Available Templates')[:500]}\n"
        
        if domain_skill:
            prompt += f"\n**Available Domains:**\n{domain_skill.get_section('Core Domains Overview')[:500]}\n"
        
        return prompt
    
    def _build_enrich_prompt(
        self, analysis: Dict, user_answers: Dict,
        template_skill, linking_skill, domain_skill
    ) -> str:
        """Build prompt for enrich mode"""
        prompt = f"""Generate a complete, comprehensive note based on this information.

**Conversation Analysis:**
{json.dumps(analysis, indent=2)}

**User Answers:**
{json.dumps(user_answers, indent=2)}

**IMPORTANT INSTRUCTIONS:**

1. **Be COMPREHENSIVE and DETAILED**: This should be a substantial note (500-1000+ words)
2. **Expand ALL concepts**: Take every feature, step, or idea from the analysis and write 2-3 paragraphs explaining it in detail
3. **Include context and reasoning**: Don't just list features - explain WHY they matter, HOW they work, WHAT problems they solve
4. **Add examples and use cases**: For technical concepts, include code examples, workflow descriptions, or usage scenarios
5. **Write complete prose**: Use full paragraphs, not just bullet points or short summaries
6. **Structure with multiple sections**: Overview, Features (detailed), Implementation (step-by-step with explanations), Technical Considerations, Next Steps, etc.
7. **Include frontmatter**: Add YAML frontmatter with title, date, tags, domain, type

**Template to follow:**

```markdown
---
title: [Note Title]
date: {datetime.now().strftime('%Y-%m-%d')}
tags: [relevant, tags]
domain: [domain from user_answers]
type: [type from user_answers]
---

# [Note Title]

## Overview
[2-3 paragraphs providing context, background, and purpose]

## Core Features/Concepts
[For each major feature or concept:]
### [Feature Name]
[2-3 paragraphs explaining this feature in detail, including:]
- What it does
- Why it's important
- How it works
- Examples or use cases
- Technical considerations

## Implementation
[Detailed step-by-step breakdown:]
### Step 1: [Step Name]
[2-3 paragraphs explaining:]
- What this step involves
- How to approach it
- Tools and techniques needed
- Potential challenges

### Step 2: [Next Step]
[Continue for all steps...]

## Technical Considerations
[Discuss:]
- Architecture decisions
- Performance implications
- Compatibility issues
- Best practices

## Next Steps / Future Work
[Detailed roadmap:]
- Immediate next actions
- Medium-term goals
- Long-term vision

## Related Concepts
[Links to related notes with context about how they relate]

## References
[Any external resources, tools, or documentation mentioned]
```

"""
        
        if template_skill and user_answers.get("template"):
            template_name = user_answers["template"]
            template_section = template_skill.get_section(template_name)
            if template_section:
                prompt += f"\n**Template Structure ({template_name}):**\n{template_section[:1000]}\n"
        
        if linking_skill:
            prompt += f"\n**Wiki-Linking Rules:**\n{linking_skill.get_section('When to Create Links')[:500]}\n"
        
        prompt += "\n\n**Remember**: Generate a COMPREHENSIVE, DETAILED note with full explanations, not just a brief summary. Aim for depth and clarity."
        
        return prompt
    
    def _build_edit_prompt(
        self, existing_note: str, edit_request: str,
        template_skill, linking_skill
    ) -> str:
        """Build prompt for edit mode"""
        prompt = f"""Edit this existing note based on the user's request.

**Existing Note:**
```markdown
{existing_note}
```

**Edit Request:**
{edit_request}

"""
        
        if linking_skill:
            prompt += f"\n**Wiki-Linking Rules (for adding links):**\n{linking_skill.get_section('When to Create Links')[:300]}\n"
        
        prompt += "\nProvide the edited note and a summary of changes made."
        
        return prompt
    
    # ========== Helper Methods: Auto-Linking ==========
    
    async def _auto_link_content(
        self, content: str, linking_skill
    ) -> tuple:
        """
        Automatically insert [[wiki-links]] based on RAG search.
        
        Process:
        1. Extract significant terms from content
        2. Query RAG for each term
        3. If similarity >=0.85, insert [[link]]
        4. Follow rules from linking_skill
        
        Returns:
            Tuple of (linked_content: str, inserted_links: dict)
            where inserted_links maps {term: target_title}
        """
        if not self.rag or not linking_skill:
            logger.warning("RAG or linking skill not available, skipping auto-linking")
            return content, {}
        
        logger.info("Auto-linking content...")
        
        # Load stopwords from linking skill
        stopwords_section = linking_skill.get_section("When NOT to Create Links")
        stopwords = self._extract_stopwords(stopwords_section)
        
        # Extract significant terms (capitalize words, repeated phrases)
        terms = self._extract_linkable_terms(content, stopwords)
        
        logger.info(f"Found {len(terms)} potential linkable terms")
        
        # Query RAG for each term
        links_to_insert = {}
        
        for term in terms[:20]:  # Limit to 20 terms to avoid excessive queries
            try:
                results = self.rag.search(query=term, n_results=1)
                
                if results and len(results) > 0:
                    top_result = results[0]
                    similarity = top_result.get('similarity', 0.0)
                    
                    if similarity >= 0.85:
                        target_title = top_result.get('title', term)
                        links_to_insert[term] = target_title
                        logger.info(f"Auto-link: '{term}' → [[{target_title}]] (similarity: {similarity:.2f})")
                
            except Exception as e:
                logger.warning(f"Failed to query RAG for term '{term}': {e}")
                continue
        
        # Insert links into content (first occurrence per section only)
        linked_content = self._insert_links(content, links_to_insert)
        
        logger.info(f"Inserted {len(links_to_insert)} wiki-links")
        
        return linked_content, links_to_insert
    
    def _extract_stopwords(self, stopwords_section: Optional[str]) -> set:
        """Extract stopwords from linking skill"""
        if not stopwords_section:
            return {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "a", "an"}
        
        # Extract words from stopwords section
        stopwords = set()
        lines = stopwords_section.split('\n')
        for line in lines:
            words = re.findall(r'\b\w+\b', line.lower())
            stopwords.update(words)
        
        return stopwords
    
    def _extract_linkable_terms(self, content: str, stopwords: set) -> List[str]:
        """Extract terms that might be linkable"""
        terms = []
        
        # Extract capitalized phrases (potential proper nouns)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        terms.extend(capitalized)
        
        # Extract technical terms (words with specific patterns)
        technical = re.findall(r'\b[a-z]+[A-Z][a-z]*\b', content)  # camelCase
        terms.extend(technical)
        
        # Filter out stopwords
        terms = [t for t in terms if t.lower() not in stopwords and len(t) > 3]
        
        # Deduplicate while preserving order
        seen = set()
        unique_terms = []
        for term in terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)
        
        return unique_terms
    
    def _insert_links(self, content: str, links: Dict[str, str]) -> str:
        """Insert [[wiki-links]] into content (first occurrence per section only)"""
        if not links:
            return content
        
        # Split content by sections (## headings)
        sections = re.split(r'(^##\s+.+$)', content, flags=re.MULTILINE)
        
        linked_sections = []
        
        for section in sections:
            section_links_used = set()
            
            for term, target in links.items():
                # Skip if already used in this section
                if term in section_links_used:
                    continue
                
                # Find first occurrence (not in code blocks or existing links)
                # Simple approach: replace first occurrence outside of ``` blocks and [[ ]]
                if term in section and '[[' + term not in section:
                    # Insert link at first occurrence
                    section = section.replace(term, f'[[{target}]]', 1)
                    section_links_used.add(term)
            
            linked_sections.append(section)
        
        return ''.join(linked_sections)
    
    # ========== Helper Methods: Formatting ==========
    
    def _format_capture_output(self, analysis: Dict) -> str:
        """Format capture analysis for display"""
        output = f"""**Conversation Analysis**

**Type:** {analysis.get('conversation_type', 'unknown')}
**Topic:** {analysis.get('primary_topic', 'N/A')}

**Key Concepts Identified:**
"""
        
        concepts = analysis.get('key_concepts', [])
        for concept in concepts[:5]:  # Show first 5
            concept_name = concept.get('concept', 'Unknown')
            output += f"- {concept_name}\n"
        
        if len(concepts) > 5:
            output += f"  ... and {len(concepts) - 5} more\n"
        
        output += f"\n**Suggested Template:** {analysis.get('suggested_template', 'quick-note')}"
        output += f"\n**Suggested Domain:** {analysis.get('suggested_domain', 'scrolls')}"
        
        output += "\n\n✓ Analysis complete! Preparing questions..."
        
        return output
    
    def _format_organize_output(self, questions_data: Dict) -> str:
        """Format organize questions for display"""
        output = "**Clarifying Questions**\n\n"
        output += questions_data.get('summary', 'Please answer the following questions:')
        output += "\n\n"
        
        questions = questions_data.get('questions', [])
        for i, q in enumerate(questions):
            question_text = q.get('question', f'Question {i+1}')
            output += f"{i+1}. {question_text}\n"
        
        output += "\nPlease select your answers, then I'll generate the note."
        
        return output
    
    def _format_enrich_output(self, note_data: Dict) -> str:
        """Format generated note for display"""
        metadata = note_data.get('metadata', {})
        link_count = metadata.get('link_count', 0)
        
        output = f"""**Note Generated**

**Title:** {metadata.get('title', 'Untitled')}
**Domain:** {metadata.get('domain', 'scrolls')}
**Template:** {metadata.get('template_used', 'N/A')}
**Wiki-links:** {link_count} automatic links inserted

Note is ready for preview. Review and save when ready.
"""
        
        return output
    
    def _format_edit_output(self, edited_data: Dict) -> str:
        """Format edited note for display"""
        changes = edited_data.get('changes', {})
        
        output = f"""**Note Edited**

**Changes Made:** {changes.get('summary', 'Note updated')}
**Type:** {changes.get('change_type', 'general')}

Edited note is ready for preview.
"""
        
        return output
    
    # ========== Helper Methods: Fallbacks ==========
    
    def _generate_fallback_questions(self, analysis: Dict) -> Dict:
        """Generate basic fallback questions if LLM parsing fails"""
        return {
            "questions": [
                {
                    "id": "q1_template",
                    "question": "What type of note should this be?",
                    "type": "radio",
                    "options": [
                        {"value": "meeting-notes", "label": "Meeting Notes", "description": "For discussions and decisions"},
                        {"value": "concept-note", "label": "Concept Explanation", "description": "For understanding a concept"},
                        {"value": "quick-note", "label": "Quick Note", "description": "Brief capture"},
                        {"value": "custom", "label": "Type your own", "input": True}
                    ],
                    "default": analysis.get('suggested_template', 'quick-note')
                },
                {
                    "id": "q2_domain",
                    "question": "Which domain should this go in?",
                    "type": "radio",
                    "options": [
                        {"value": "scrolls", "label": "Scrolls 📜", "description": "Writing and documentation"},
                        {"value": "sigils", "label": "Sigils 🔐", "description": "Code and infrastructure"},
                        {"value": "custom", "label": "Type your own", "input": True}
                    ],
                    "default": analysis.get('suggested_domain', 'scrolls')
                }
            ],
            "summary": "Please answer these questions to finalize your note"
        }
    
    def _map_template_to_filename(self, template_name: str) -> str:
        """
        Map template name to filename (Phase 16e).
        
        Args:
            template_name: Template name from analysis (e.g., "meeting", "concept")
        
        Returns:
            Template filename (e.g., "meeting-notes.md")
        """
        # Mapping from analysis template names to actual filenames
        template_map = {
            "meeting": "meeting-notes.md",
            "meeting-notes": "meeting-notes.md",
            "concept": "concept-note.md",
            "concept-note": "concept-note.md",
            "howto": "howto-guide.md",
            "how-to": "howto-guide.md",
            "guide": "howto-guide.md",
            "research": "research-summary.md",
            "research-summary": "research-summary.md",
            "project": "project-note.md",
            "project-note": "project-note.md",
            "quick": "quick-note.md",
            "quick-note": "quick-note.md",
        }
        
        # Normalize template name (lowercase, strip)
        normalized = template_name.lower().strip()
        
        # Return mapped filename or default to quick-note
        return template_map.get(normalized, "quick-note.md")
    
    async def _load_template(self, template_filename: str) -> Dict:
        """
        Load template from API (Phase 16e).
        
        Args:
            template_filename: Template filename (e.g., "meeting-notes.md")
        
        Returns:
            Template dict with name, icon, description, variables, markdown_content, etc.
        """
        import aiohttp
        
        url = f"http://127.0.0.1:11436/polly/templates/{template_filename}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        template = await response.json()
                        logger.info(f"Loaded template: {template.get('name')}")
                        return template
                    else:
                        error_text = await response.text()
                        raise Exception(f"API returned {response.status}: {error_text}")
        except Exception as e:
            logger.error(f"Failed to load template {template_filename}: {e}")
            raise
    
    def _build_template_enrich_prompt(
        self,
        analysis: Dict,
        template: Dict,
        linking_skill: Optional[Any],
        domain_skill: Optional[Any],
        context: PersonaContext
    ) -> str:
        """
        Build enrich prompt using template structure and AI hints (Phase 16e).
        
        Args:
            analysis: Capture analysis from state
            template: Template loaded from API
            linking_skill: Wiki-linking skill
            domain_skill: Domain-structure skill
            context: PersonaContext with conversation history
        
        Returns:
            Formatted prompt for LLM
        """
        ai_hints = template.get("ai_hints", {})
        tone = ai_hints.get("tone", "natural, clear")
        focus = ai_hints.get("focus", "key information")
        linking_priority = ai_hints.get("linking_priority", [])
        
        conversation_history = context.metadata.get("conversation_history", [])
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in conversation_history[-10:]  # Last 10 messages
        ])
        
        prompt = f"""# Task: Generate Note from Template

## Template: {template['name']}
{template.get('description', '')}

**Tone:** {tone}
**Focus:** {focus}
**Linking Priority:** {', '.join(linking_priority)}

## Conversation to Capture
```
{conversation_text}
```

## Analysis
**Type:** {analysis.get('conversation_type', 'general')}
**Primary Topic:** {analysis.get('primary_topic', 'Unknown')}
**Key Concepts:** {', '.join(analysis.get('key_concepts', [])[:10])}

## Template Structure
The template has the following variables: {', '.join(template['variables'])}

## Instructions
1. Read the conversation and analysis carefully
2. Extract relevant information for each template variable
3. Write content in the specified tone: {tone}
4. Focus on: {focus}
5. Generate well-structured, clear prose (not bullet points unless appropriate)
6. Use the template's markdown structure
7. Include [[wiki-links]] when referring to concepts, people, projects, or tools
8. Prioritize linking to: {', '.join(linking_priority)}

## Output Format
Return a JSON object with:
{{
  "title": "Suggested note title",
  "variables": {{
    "variable_name": "Generated content for this variable",
    ...
  }}
}}

**IMPORTANT:** 
- Fill in ALL template variables
- Use markdown formatting within variable content
- Insert [[wiki-links]] for key concepts
- Keep content concise but informative
"""
        
        # Add wiki-linking skill if available
        if linking_skill:
            prompt += f"\n\n## Wiki-Linking Rules\n{linking_skill.content[:500]}"
        
        # Add domain structure if available
        if domain_skill:
            prompt += f"\n\n## Domain Structure\n{domain_skill.content[:300]}"
        
        return prompt
    
    def _parse_template_enrich_response(self, content: str) -> Dict:
        """
        Parse LLM response for template-based generation (Phase 16e).
        
        Args:
            content: LLM response content (should be JSON)
        
        Returns:
            Dict with title and variables
        """
        # Try to extract JSON from response
        import json
        import re
        
        # Find JSON block
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                return data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
        
        # Fallback: couldn't parse
        raise ValueError("Could not parse LLM response as JSON")
    
    def _render_template(self, template: Dict, variables: Dict[str, str]) -> str:
        """
        Render template with variable values (Phase 16e).
        
        Args:
            template: Template dict with markdown_content
            variables: Dict mapping variable names to values
        
        Returns:
            Rendered markdown content
        """
        content = template["markdown_content"]
        
        # Replace each {{variable}} with its value
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            content = content.replace(placeholder, var_value)
        
        # Replace any remaining placeholders with empty string
        content = re.sub(r'\{\{[^}]+\}\}', '', content)
        
        return content
