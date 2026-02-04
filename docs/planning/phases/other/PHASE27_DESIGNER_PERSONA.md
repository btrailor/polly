# Phase 27: Designer Persona

**Status:** 📋 Planned  
**Priority:** HIGH (Major Differentiator)  
**Estimated Effort:** 4-6 weeks  
**Target Date:** June-July 2026  
**Depends On:** Phase 11c (Personas) ✅, Phase 24 (Orchestrator Mode), Phase 25 (Code Architecture)

---

## Overview

The Designer persona brings visual design capabilities to Polly, enabling UI/UX design, mockup creation, and design-to-code workflows. This transforms Polly from a development tool into a complete product design system.

**Core Concept:** Design and development shouldn't be separate workflows. Designer works in concert with Architect and Programmer to create cohesive, well-designed products from concept to code.

---

## Design Philosophy (From Your Brain Dump)

> "Things to think about for designer persona: **start simple with elegant design principles**. Avoid early implementation of icons and other bells and whistles. **Refine the basic UI organization early on** so needless overhauls that can break important features are avoidable."

**Key Principles:**
1. **Start Simple:** Focus on fundamentals before decoration
2. **Elegant Principles:** Clean, minimal, functional design
3. **No Premature Ornamentation:** Icons and embellishments come last
4. **Solid Foundation:** Get structure right first
5. **Architect → Designer Flow:** Always design architecture before UI

---

## User Problem

**Current State:**
- Design happens in external tools (Figma, Sketch)
- Designers and developers work in silos
- Mockups often don't match implementation
- Design decisions not documented
- No AI assistance for design reasoning

**Pain Points:**
```
Scenario 1: Building a new feature
- Developer: "I need a UI for this"
- Opens Figma, designs mockup
- Sends screenshot to developer
- Developer interprets (often incorrectly)
- Result: Design doesn't match code

Scenario 2: Design review
- "This button is too small"
- "Why did you choose this color?"
- Designer can't explain reasoning
- No design system documented

Scenario 3: Responsive design
- Mockup looks great on desktop
- Mobile is an afterthought
- Developer guesses at breakpoints
- Inconsistent experience across devices
```

**Desired State:**
- Architect defines structure first
- Designer creates mockup based on architecture
- User reviews and refines design
- Programmer receives design spec (not just PNG)
- Design and code stay in sync

---

## Designer Modes

### Mode 1: Vision (Strategic Design)

**Purpose:** High-level UX architecture and user flows

**Capabilities:**
- Information architecture
- User journey mapping
- Interaction patterns
- Accessibility planning
- Design system thinking

**Example:**
```
User: "Design a blog posting interface"

Designer (Vision mode):
"Let me think about the user experience...

🎨 Information Architecture:
┌─────────────────────────────────────────┐
│ Post Creation Flow                      │
├─────────────────────────────────────────┤
│                                         │
│ 1. New Post Screen                      │
│    ├─ Title input (prominent)          │
│    ├─ Content editor (markdown)         │
│    ├─ Tags/categories (sidebar)         │
│    └─ Preview toggle                    │
│                                         │
│ 2. Publishing Options                   │
│    ├─ Publish immediately               │
│    ├─ Schedule for later                │
│    └─ Save as draft                     │
│                                         │
│ 3. Post Management                      │
│    ├─ Draft posts list                  │
│    ├─ Published posts list              │
│    └─ Analytics (views, comments)       │
│                                         │
├─────────────────────────────────────────┤
│ Key Design Decisions:                   │
│ • Single-page editor (no modals)        │
│ • Autosave every 30 seconds             │
│ • Markdown preview side-by-side         │
│ • Mobile: Stack vertically              │
└─────────────────────────────────────────┘

User Flow Diagram:
[New Post] → [Edit] → [Preview] → [Publish]
              ↓
         [Save Draft] → [Drafts List]

Accessibility Considerations:
• Keyboard shortcuts for common actions
• ARIA labels for screen readers
• High contrast mode support
• Focus indicators on all interactive elements

Should I proceed to create detailed mockups?"
```

### Mode 2: Mockup (Visual Design)

**Purpose:** Create visual designs and layouts

**Capabilities:**
- Layout design
- Color palette selection
- Typography choices
- Component design
- Responsive breakpoints

**Example:**
```
User: "Create a mockup for the blog editor"

Designer (Mockup mode):
"Based on the Vision phase, here's the mockup:

╔════════════════════════════════════════════════╗
║  Blog Post Editor                    [Preview] ║
╠════════════════════════════════════════════════╣
║                                                ║
║  Title: [_________________________________]     ║
║                                                ║
║  ┌──────────────────────────────────────────┐ ║
║  │ # Write your post in markdown...         │ ║
║  │                                          │ ║
║  │                                          │ ║
║  │                                          │ ║
║  │                                          │ ║
║  └──────────────────────────────────────────┘ ║
║                                                ║
║  Tags: [javascript] [+]                        ║
║                                                ║
║  [Save Draft]        [Schedule] [Publish Now] ║
╚════════════════════════════════════════════════╝

Design Specifications:
───────────────────────────────────────────────
Colors:
• Background: #fafafa (light gray)
• Primary: #2563eb (blue)
• Text: #1a1a1a (near black)
• Border: #e5e5e5 (light gray)

Typography:
• Title: Inter 24px, Semi-bold
• Body: Inter 16px, Regular
• Buttons: Inter 14px, Medium

Spacing:
• Container padding: 24px
• Element spacing: 16px
• Button padding: 12px 24px

Responsive Breakpoints:
• Desktop: 1024px+
• Tablet: 768px - 1023px
• Mobile: < 768px

Components Used:
• Input (title)
• Textarea (markdown editor)
• Tag chip
• Button (primary, secondary)

[Generate Code] [Export to Figma] [Refine Design]"
```

### Mode 3: Critic (Design Review)

**Purpose:** Evaluate designs for quality, accessibility, UX

**Capabilities:**
- Design critique
- Accessibility audit
- Consistency checking
- Best practices enforcement
- Performance considerations

**Example:**
```
User: "Review this login page design"
[Shows screenshot]

Designer (Critic mode):
"Analyzing your login page design...

✅ Strengths:
• Clean, minimal layout
• Clear call-to-action
• Proper contrast ratios (WCAG AA compliant)
• Mobile-friendly form layout

⚠️  Areas for Improvement:

1. Password Input
   Issue: No "Show password" toggle
   Fix: Add visibility toggle icon
   Why: Improves UX, reduces login errors

2. Error States
   Issue: No indication of error styling
   Fix: Define error state (red border, error message)
   Why: Users need clear feedback

3. Loading State
   Issue: No loading indicator on submit
   Fix: Add spinner/disable button while processing
   Why: Prevents double-submission, shows progress

4. Accessibility
   Issue: Form labels missing "for" attributes
   Fix: Associate labels with inputs properly
   Why: Screen reader compatibility

5. Spacing
   Issue: Inputs too close together (8px)
   Suggestion: Increase to 16px minimum
   Why: Improves visual breathing room, easier to tap

📊 Scoring:
• Aesthetics: 8/10
• Usability: 7/10
• Accessibility: 6/10
• Consistency: 9/10

Overall: Strong foundation, needs refinement on accessibility and interaction states.

Should I create a revised mockup addressing these issues?"
```

### Mode 4: System (Design System Management)

**Purpose:** Define and maintain design systems

**Capabilities:**
- Component library creation
- Design tokens management
- Style guide generation
- Pattern documentation
- Theme management

**Example:**
```
User: "Create a design system for my app"

Designer (System mode):
"I'll create a comprehensive design system:

┌─ Design System: [App Name] ────────────────┐
│                                            │
│ 1. Design Tokens                           │
│    Colors:                                 │
│    • Primary: #2563eb                      │
│    • Secondary: #10b981                    │
│    • Accent: #f59e0b                       │
│    • Neutral: #6b7280                      │
│    • Error: #ef4444                        │
│                                            │
│    Typography Scale:                       │
│    • Display: 48px / 56px (line-height)    │
│    • Heading 1: 36px / 44px                │
│    • Heading 2: 30px / 38px                │
│    • Body: 16px / 24px                     │
│    • Caption: 14px / 20px                  │
│                                            │
│    Spacing Scale (4px base):               │
│    • xs: 4px                               │
│    • sm: 8px                               │
│    • md: 16px                              │
│    • lg: 24px                              │
│    • xl: 32px                              │
│                                            │
│ 2. Component Library                       │
│    ├─ Button (primary, secondary, ghost)   │
│    ├─ Input (text, password, email)        │
│    ├─ Card (default, elevated, outlined)   │
│    ├─ Modal (small, medium, large)         │
│    ├─ Toast (success, error, info)         │
│    └─ Navigation (sidebar, top bar)        │
│                                            │
│ 3. Patterns                                │
│    ├─ Form layouts                         │
│    ├─ Data tables                          │
│    ├─ List views                           │
│    └─ Empty states                         │
│                                            │
│ Saved to: vault/Design System/             │
│ Format: Markdown + Tailwind config         │
│                                            │
│ [Export as Figma Library]                  │
│ [Generate Tailwind Config]                 │
│ [Create Component Stubs]                   │
└────────────────────────────────────────────┘"
```

---

## Integration with Other Personas

### Architect → Designer Workflow

**Your Brain Dump:**
> "Architect should communicate with designer for instance. When planning a project that is based on a UI, **always start new features by solidifying the UI design in a basic sense**. Architect should send designer mockup and then user can enter the designer profile and tweak as they desire."

**Flow:**
```
1. Architect (Plan mode)
   "Designing authentication system..."
   Output: System architecture, data flow

2. Architect → Designer handoff
   "I need UI designs for:
    - Login page
    - Registration page
    - Password reset flow"

3. Designer (Vision mode)
   Analyzes architecture
   Proposes user flows
   Output: UX strategy

4. User reviews and approves

5. Designer (Mockup mode)
   Creates visual designs
   Output: Mockups with specs

6. User refines design (optional)
   Switch to Designer persona
   Iterate on mockups

7. Designer → Programmer handoff
   "Here are the design specs..."
   Output: Design tokens, component specs

8. Programmer (Implement mode)
   Builds UI based on specs
   Uses design tokens
   Output: Code
```

### Designer → Programmer Workflow

**Design Handoff Format:**
```json
{
  "component": "LoginForm",
  "design_spec": {
    "layout": {
      "type": "flex",
      "direction": "column",
      "gap": "16px",
      "padding": "24px"
    },
    "elements": [
      {
        "type": "input",
        "label": "Email",
        "placeholder": "you@example.com",
        "validation": "email",
        "styles": {
          "padding": "12px 16px",
          "border": "1px solid #e5e5e5",
          "borderRadius": "8px"
        }
      },
      {
        "type": "button",
        "text": "Sign In",
        "variant": "primary",
        "styles": {
          "backgroundColor": "#2563eb",
          "color": "#ffffff",
          "padding": "12px 24px"
        }
      }
    ]
  },
  "tokens": {
    "colors": {
      "primary": "#2563eb",
      "error": "#ef4444"
    },
    "spacing": {
      "md": "16px",
      "lg": "24px"
    }
  }
}
```

---

## Technical Architecture

### Designer Persona Class

```python
# core/personas/implementations/designer.py

class Designer(PersonaBase):
    """
    Designer persona for UI/UX design, mockup creation,
    and design system management.
    """
    
    modes = ["vision", "mockup", "critic", "system"]
    
    def vision(self, context: DesignContext) -> VisionOutput:
        """
        Strategic UX architecture and user flows
        """
        prompt = self._build_vision_prompt(context)
        response = self.llm.complete(prompt)
        return self._parse_vision_output(response)
    
    def mockup(self, context: DesignContext) -> MockupOutput:
        """
        Create visual designs and layouts
        """
        # Consider architecture from Architect
        if context.has_architecture:
            architecture = context.get_architecture()
            prompt = self._build_mockup_with_architecture(architecture)
        else:
            prompt = self._build_standalone_mockup(context)
        
        response = self.llm.complete(prompt)
        mockup = self._parse_mockup(response)
        
        # Generate ASCII art mockup
        ascii_mockup = self._generate_ascii_mockup(mockup)
        
        # Generate design specs
        specs = self._generate_design_specs(mockup)
        
        return MockupOutput(
            ascii_art=ascii_mockup,
            design_specs=specs,
            components=mockup.components,
            tokens=mockup.design_tokens
        )
    
    def critic(self, design_input: DesignInput) -> CritiqueOutput:
        """
        Evaluate design for quality, accessibility, UX
        """
        # Accessibility checks
        accessibility = self._check_accessibility(design_input)
        
        # Consistency checks
        consistency = self._check_consistency(design_input)
        
        # Best practices
        best_practices = self._check_best_practices(design_input)
        
        # Generate critique
        prompt = self._build_critique_prompt(
            design_input, 
            accessibility, 
            consistency, 
            best_practices
        )
        
        response = self.llm.complete(prompt)
        return self._parse_critique(response)
    
    def system(self, context: DesignContext) -> DesignSystemOutput:
        """
        Create and manage design system
        """
        # Define design tokens
        tokens = self._generate_design_tokens(context)
        
        # Component library
        components = self._generate_component_library(tokens)
        
        # Generate Tailwind config
        tailwind_config = self._generate_tailwind_config(tokens)
        
        # Export to files
        self._save_design_system(tokens, components, tailwind_config)
        
        return DesignSystemOutput(
            tokens=tokens,
            components=components,
            tailwind_config=tailwind_config,
            documentation=self._generate_docs(tokens, components)
        )
    
    def _check_accessibility(self, design: DesignInput) -> AccessibilityReport:
        """
        WCAG compliance checking
        """
        issues = []
        
        # Contrast ratios
        for color_pair in design.color_combinations:
            ratio = self._calculate_contrast_ratio(
                color_pair.foreground,
                color_pair.background
            )
            if ratio < 4.5:  # WCAG AA standard
                issues.append(f"Low contrast: {ratio:.2f}:1")
        
        # Interactive element sizing
        for element in design.interactive_elements:
            if element.size < 44:  # 44px minimum touch target
                issues.append(f"Touch target too small: {element.size}px")
        
        # Label associations
        for input_field in design.form_inputs:
            if not input_field.has_label:
                issues.append(f"Missing label for input: {input_field.name}")
        
        return AccessibilityReport(issues=issues)
```

### Mockup Generator

```python
# core/design/mockup_generator.py

class MockupGenerator:
    """
    Generate ASCII art mockups and design specs
    """
    
    def generate_ascii_mockup(self, design: DesignSpec) -> str:
        """
        Create visual representation in ASCII
        """
        width = design.width or 60
        
        mockup = []
        mockup.append("╔" + "═" * (width - 2) + "╗")
        
        for component in design.components:
            mockup.extend(self._render_component(component, width))
        
        mockup.append("╚" + "═" * (width - 2) + "╝")
        
        return "\n".join(mockup)
    
    def _render_component(self, component: Component, width: int) -> List[str]:
        """
        Render individual component as ASCII
        """
        if component.type == "input":
            return [
                f"║ {component.label}: [{'_' * 30}] ║"
            ]
        elif component.type == "button":
            text = component.text
            padding = (width - len(text) - 4) // 2
            return [
                f"║ {' ' * padding}[{text}]{' ' * padding} ║"
            ]
        # ... more component types
    
    def generate_design_specs(self, design: DesignSpec) -> DesignSpecs:
        """
        Extract detailed specifications for implementation
        """
        return DesignSpecs(
            colors=self._extract_colors(design),
            typography=self._extract_typography(design),
            spacing=self._extract_spacing(design),
            components=self._extract_component_specs(design),
            responsive=self._extract_responsive_rules(design)
        )
```

### Design System Storage

**Location:**
```
vault/.polly/design/
├── design_systems/
│   ├── my_app/
│   │   ├── tokens.json
│   │   ├── components.json
│   │   ├── tailwind.config.js
│   │   └── documentation.md
│   └── polly_ui/
│       └── ...
└── mockups/
    ├── login_page_v1.json
    └── dashboard_v2.json

vault/Design/  # User-visible notes
├── Design System.md
├── Component Library.md
└── Mockups/
    └── Login Page.md
```

---

## UI/UX Features

### 1. Design Canvas (Future Enhancement)

**Phase 27a: Visual Mockup Editor (Advanced)**
- Drag-and-drop component builder
- Real-time preview
- Export to code
- Similar to v0.dev or Builder.io

**For Phase 27 (Initial):**
- ASCII art mockups (works in chat)
- JSON design specs
- Text-based design descriptions
- Export to Figma (via API)

### 2. Design Review Interface

```javascript
// frontend: design-reviewer.js

class DesignReviewer {
    async reviewDesign(imageOrUrl) {
        // Upload screenshot
        const designInput = await this.uploadDesign(imageOrUrl);
        
        // Designer Critic mode
        const critique = await api.post('/persona/designer/critic', {
            design_input: designInput
        });
        
        // Render critique in chat
        this.renderCritique(critique);
        
        // Offer to create improved version
        if (critique.has_issues) {
            this.showImprovementOption();
        }
    }
}
```

### 3. Design Handoff to Programmer

```javascript
// When Designer completes mockup
async function handoffToProgrammer(mockup) {
    const designSpec = mockup.design_specs;
    
    // Create conversation with Programmer
    const conversation = await createConversation({
        persona: 'programmer',
        mode: 'implement',
        context: {
            design_spec: designSpec,
            from_persona: 'designer',
            implementation_task: 'Build UI components from design'
        }
    });
    
    // Switch user to Programmer conversation
    switchToConversation(conversation.id);
    
    // Programmer receives design context automatically
}
```

---

## Theme-as-Meta-Persona Concept

**Your Brain Dump:**
> "What if different themes in the UI could actually act like **meta personas with aesthetic values** that are distinct from the others. These aesthetics are represented in the actual UI styling."

**Concept Exploration:**

### Theme Personas

**1. Minimalist (Default)**
- Aesthetic: Clean, spacious, monochrome
- Typography: Sans-serif, plenty of whitespace
- Colors: Black, white, single accent
- Philosophy: "Less is more"

**2. Brutalist**
- Aesthetic: Raw, structural, bold
- Typography: Monospace, tight spacing
- Colors: High contrast, stark
- Philosophy: "Function over form"

**3. Playful**
- Aesthetic: Rounded, colorful, friendly
- Typography: Soft curves, readable
- Colors: Pastel palette, gradients
- Philosophy: "Joy in interaction"

**4. Professional**
- Aesthetic: Corporate, trustworthy, polished
- Typography: Traditional serif, formal
- Colors: Blues, grays, conservative
- Philosophy: "Serious work, serious tools"

**Implementation:**
```python
class ThemePersona:
    """
    Themes that influence design decisions
    """
    
    def suggest_colors(self, context: DesignContext) -> ColorPalette:
        if self.name == "minimalist":
            return ColorPalette(
                primary="#000000",
                secondary="#ffffff",
                accent="#808080"
            )
        elif self.name == "playful":
            return ColorPalette(
                primary="#ff6b6b",
                secondary="#4ecdc4",
                accent="#ffe66d"
            )
    
    def suggest_typography(self) -> TypographySystem:
        # Theme-specific font recommendations
        pass
    
    def filter_design_suggestions(self, suggestions: List[Design]) -> List[Design]:
        # Only suggest designs matching theme aesthetic
        pass
```

**Usage:**
```
User: "I want a playful design for my kids' app"

Designer (with Playful theme activated):
"Let's create something fun and engaging!

Colors:
• Primary: Coral #ff6b6b (warm, friendly)
• Secondary: Turquoise #4ecdc4 (playful)
• Accent: Sunny yellow #ffe66d (joyful)

Typography:
• Display: Fredoka One (rounded, fun)
• Body: Nunito (soft, readable)

Components:
• Rounded corners (16px border-radius)
• Bouncy animations
• Illustration-based empty states
• Large, tap-friendly buttons

This matches the playful, child-friendly aesthetic!"
```

---

## User Workflows

### Workflow 1: Architect → Designer → Programmer

```
Phase 1: Architecture
User: "Build a user dashboard"

Architect (Plan mode):
"Designing the dashboard architecture...
 
 Components needed:
 - Header (navigation)
 - Sidebar (user menu)
 - Main content area (widgets)
 - Widget system (modular)
 
 I'll hand this off to Designer for mockups."

Phase 2: Design
[Orchestrator switches to Designer]

Designer (Vision mode):
"Based on Architect's plan, here's the UX strategy...
 
 [Creates user flow diagram]
 
 Moving to mockup creation..."

Designer (Mockup mode):
[Creates ASCII mockup + design specs]

"Here's the visual design. Should I hand off to Programmer?"

Phase 3: Implementation
[Orchestrator switches to Programmer]

Programmer:
"I have the design specs from Designer.
 Building components:
 - Header component
 - Sidebar component
 - Widget container
 
 Using design tokens:
 • Primary color: #2563eb
 • Spacing: 16px grid
 ..."
```

### Workflow 2: Design Review

```
User: [Uploads screenshot of existing UI]
      "What do you think of this design?"

Designer (Critic mode):
"Analyzing your design...

✅ Strengths:
• Good color contrast
• Clear hierarchy

⚠️  Issues:
• Touch targets too small (32px, need 44px)
• No error states defined
• Accessibility: Missing ARIA labels

📊 Overall: 7/10

Should I create an improved version?"

User: "Yes please"

Designer (Mockup mode):
[Creates revised mockup addressing issues]

"Here's the improved design with:
• Larger touch targets
• Error state styling
• Proper ARIA labels
• Improved spacing

Compare:
[Before] → [After]"
```

---

## Success Criteria

### Phase 27 Complete When:

**Backend:**
- [x] Designer persona with 4 modes
- [x] ASCII mockup generation
- [x] Design spec generation
- [x] Accessibility checking
- [x] Design system creation
- [x] Architect → Designer handoff

**Frontend:**
- [x] Design review interface (upload screenshot)
- [x] Mockup rendering in chat
- [x] Design spec display
- [x] Export to Figma (basic)
- [x] Design system documentation

**Integration:**
- [x] Orchestrator coordinates Architect → Designer → Programmer
- [x] Design specs passed to Programmer
- [x] Theme personas influence suggestions

**Quality:**
- [x] Mockups are readable and useful
- [x] Design specs implementable by Programmer
- [x] Accessibility checks 90%+ accurate
- [x] Handoff workflow feels seamless

---

## Future Enhancements

### Phase 27a: Visual Designer (Advanced)
- Drag-and-drop mockup builder
- Real-time component preview
- Direct code generation
- Figma plugin (two-way sync)

### Phase 27b: Artist Mode
- Icon generation
- Illustration creation
- Image editing
- Asset management

### Phase 27c: Design Collaboration
- Shared design systems
- Design review workflows
- Comment on designs
- Version history

---

## Dependencies

**Required:**
- ✅ Phase 11c: Agent Personas
- Phase 24: Orchestrator (for Architect → Designer flow)

**Enhances:**
- Phase 25: Code Architecture (UI architecture visualization)
- Phase 26: Project Management (design milestones)
- Phase 17: Code Workspace (design-to-code)

---

## Risk Assessment

**High Risk:**
- Complexity: Design is subjective, hard to codify
- Quality: ASCII mockups may not be detailed enough
- Expectations: Users expect visual editor (Figma-level)

**Mitigations:**
- Start with text-based (ASCII art, specs)
- Clear about Phase 27 vs 27a (visual editor)
- Focus on design thinking, not pixel-perfect mockups
- Export to Figma for visual work

---

## Questions to Resolve

1. **Visual Editor Priority:** Build in Phase 27 or wait for 27a?
2. **Figma Integration:** How deep should integration be?
3. **Theme Personas:** Implement initially or later?
4. **Design File Format:** Custom format or use existing (e.g., Figma JSON)?

---

**Document Created:** February 3, 2026  
**Status:** Ready for implementation planning  
**Next Step:** Decide visual editor priority, then create implementation plan
