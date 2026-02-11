/**
 * Template Gallery Component (Phase 16e)
 *
 * Visual template selection gallery that replaces the 3-question flow.
 * Shows cards with icons, descriptions, and preview panel.
 *
 * Usage:
 *   await TemplateGallery.init();
 *   TemplateGallery.show(suggestedTemplateFilename, onSelect);
 *
 * Flow:
 *   1. Load templates from API
 *   2. Display in 3-column grid with suggested template highlighted
 *   3. User selects template or clicks preview
 *   4. Call onSelect callback with selected template filename
 */

const TemplateGallery = {
  /**
   * All available templates (loaded from API)
   */
  templates: null,

  /**
   * Currently suggested template filename
   */
  suggestedTemplate: null,

  /**
   * Callback when template is selected
   */
  onSelectCallback: null,

  /**
   * Currently selected template for preview
   */
  selectedTemplate: null,

  /**
   * Initialize the template gallery (call once on page load)
   * Loads templates from API
   */
  async init() {
    console.log("[TemplateGallery] Initializing...");

    // Load templates from API with retry logic
    try {
      const data = await window.APIClient.fetchJSON(
        "/polly/templates",
        {},
        3,
        1000,
      );
      this.templates = data.templates || [];
      console.log(
        `[TemplateGallery] Loaded ${this.templates.length} templates`,
      );
    } catch (error) {
      const is503 = error && (error.message || "").includes("503");
      if (is503) {
        console.warn(
          "[TemplateGallery] Templates endpoint not ready yet (503); empty list for now.",
        );
      } else {
        console.error("[TemplateGallery] Failed to load templates:", error);
      }
      this.templates = [];
    }

    // Add container to DOM if not exists
    if (!document.getElementById("template-gallery-container")) {
      const container = document.createElement("div");
      container.id = "template-gallery-container";
      container.className = "template-gallery-container hidden";
      container.innerHTML = `
        <div class="template-gallery-overlay"></div>
        <div class="template-gallery-modal">
          <div class="template-gallery-header">
            <h3 class="template-gallery-title">Choose a Template</h3>
            <button class="template-gallery-close" aria-label="Close">×</button>
          </div>
          <div class="template-gallery-body">
            <div class="template-gallery-grid"></div>
            <div class="template-gallery-preview">
              <div class="template-preview-empty">
                Select a template to preview
              </div>
              <div class="template-preview-content hidden">
                <h4 class="template-preview-name"></h4>
                <p class="template-preview-description"></p>
                <div class="template-preview-meta">
                  <span class="template-preview-category"></span>
                  <span class="template-preview-tags"></span>
                </div>
                <div class="template-preview-structure">
                  <strong>Structure:</strong>
                  <ul class="template-preview-variables"></ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
      document.body.appendChild(container);

      // Attach event listeners
      this._attachListeners();
    }
  },

  /**
   * Attach event listeners
   */
  _attachListeners() {
    const container = document.getElementById("template-gallery-container");

    // Close button
    container
      .querySelector(".template-gallery-close")
      .addEventListener("click", () => {
        this.hide();
      });

    // Close on overlay click
    container
      .querySelector(".template-gallery-overlay")
      .addEventListener("click", () => {
        this.hide();
      });

    // Prevent modal close on modal content click
    container
      .querySelector(".template-gallery-modal")
      .addEventListener("click", (e) => {
        e.stopPropagation();
      });
  },

  /**
   * Show the template gallery
   * @param {string} suggestedFilename - Suggested template filename (optional)
   * @param {function} onSelect - Callback when template is selected
   */
  show(suggestedFilename = null, onSelect = null) {
    console.log(
      "[TemplateGallery] Showing gallery, suggested:",
      suggestedFilename,
    );

    this.suggestedTemplate = suggestedFilename;
    this.onSelectCallback = onSelect;
    this.selectedTemplate = null;

    // Render template cards
    this._renderTemplates();

    // Show container
    const container = document.getElementById("template-gallery-container");
    container.classList.remove("hidden");

    // Prevent body scroll
    document.body.style.overflow = "hidden";
  },

  /**
   * Hide the template gallery
   */
  hide() {
    console.log("[TemplateGallery] Hiding gallery");

    const container = document.getElementById("template-gallery-container");
    container.classList.add("hidden");

    // Restore body scroll
    document.body.style.overflow = "";

    this.suggestedTemplate = null;
    this.onSelectCallback = null;
    this.selectedTemplate = null;
  },

  /**
   * Render template cards in grid
   */
  _renderTemplates() {
    const grid = document.querySelector(".template-gallery-grid");
    grid.innerHTML = "";

    if (!this.templates || this.templates.length === 0) {
      grid.innerHTML =
        '<p class="template-gallery-empty">No templates available</p>';
      return;
    }

    // Render each template as a card
    this.templates.forEach((template) => {
      const card = this._createTemplateCard(template);
      grid.appendChild(card);
    });
  },

  /**
   * Create a template card element
   * @param {object} template - Template data
   * @returns {HTMLElement} Card element
   */
  _createTemplateCard(template) {
    const card = document.createElement("div");
    card.className = "template-card";
    card.dataset.filename = template.filename;

    // Add suggested badge if this is the suggested template
    const isSuggested = template.filename === this.suggestedTemplate;
    if (isSuggested) {
      card.classList.add("template-card-suggested");
    }

    // Get Lucide icon HTML
    const iconHtml = this._getLucideIcon(template.icon);

    card.innerHTML = `
      ${isSuggested ? '<span class="template-card-badge">(✓ AI)</span>' : ""}
      <div class="template-card-icon">${iconHtml}</div>
      <h4 class="template-card-name">${this._escapeHtml(template.name)}</h4>
      <p class="template-card-description">${this._escapeHtml(template.description)}</p>
    `;

    // Click handler - select template
    card.addEventListener("click", () => {
      this._selectTemplate(template);
    });

    // Hover handler - show preview
    card.addEventListener("mouseenter", () => {
      this._showPreview(template);
    });

    return card;
  },

  /**
   * Get Lucide icon HTML by name
   * @param {string} iconName - Lucide icon name
   * @returns {string} SVG HTML
   */
  _getLucideIcon(iconName) {
    // Map of icon names to Lucide icon data
    const icons = {
      calendar:
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>',
      lightbulb:
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="9" y1="18" x2="15" y2="18"></line><line x1="10" y1="22" x2="14" y2="22"></line><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1.36.46 2.56 1.38 3.5.76.76 1.23 1.52 1.41 2.5"></path></svg>',
      "book-open":
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>',
      microscope:
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 18h8"></path><path d="M3 22h18"></path><path d="M14 22a7 7 0 1 0 0-14h-1"></path><path d="M9 14h2"></path><path d="M9 12a2 2 0 0 1-2-2V6h6v4a2 2 0 0 1-2 2Z"></path><path d="M12 6V3a1 1 0 0 0-1-1H9a1 1 0 0 0-1 1v3"></path></svg>',
      package:
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="16.5" y1="9.4" x2="7.5" y2="4.21"></line><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>',
      "file-text":
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>',
    };

    return icons[iconName] || icons["file-text"];
  },

  /**
   * Show template preview
   * @param {object} template - Template data
   */
  _showPreview(template) {
    this.selectedTemplate = template;

    const emptyState = document.querySelector(".template-preview-empty");
    const content = document.querySelector(".template-preview-content");

    // Hide empty state, show content
    emptyState.classList.add("hidden");
    content.classList.remove("hidden");

    // Populate preview
    content.querySelector(".template-preview-name").textContent = template.name;
    content.querySelector(".template-preview-description").textContent =
      template.description;
    content.querySelector(".template-preview-category").textContent =
      template.category;

    // Render tags
    const tagsHtml = template.tags
      .map((tag) => `<span class="template-tag">#${tag}</span>`)
      .join(" ");
    content.querySelector(".template-preview-tags").innerHTML = tagsHtml;

    // Render variables (structure)
    const variablesHtml = template.variables
      .slice(0, 8)
      .map((v) => `<li><code>{{${v}}}</code></li>`)
      .join("");
    content.querySelector(".template-preview-variables").innerHTML =
      variablesHtml;
    if (template.variables.length > 8) {
      content.querySelector(".template-preview-variables").innerHTML +=
        `<li>...and ${template.variables.length - 8} more</li>`;
    }
  },

  /**
   * Select a template and call callback
   * @param {object} template - Template data
   */
  _selectTemplate(template) {
    console.log("[TemplateGallery] _selectTemplate called with:", template);
    console.log("[TemplateGallery] Template filename:", template.filename);
    console.log(
      "[TemplateGallery] onSelectCallback exists:",
      !!this.onSelectCallback,
    );

    // Save callback before hiding (hide() clears it!)
    const callback = this.onSelectCallback;

    // Hide gallery
    this.hide();

    // Call callback with filename
    if (callback) {
      console.log(
        "[TemplateGallery] Calling onSelectCallback with:",
        template.filename,
      );
      try {
        callback(template.filename);
        console.log("[TemplateGallery] onSelectCallback completed");
      } catch (error) {
        console.error("[TemplateGallery] Error in onSelectCallback:", error);
      }
    } else {
      console.warn("[TemplateGallery] No onSelectCallback set!");
    }
  },

  /**
   * Escape HTML for safe rendering
   * @param {string} text - Text to escape
   * @returns {string} Escaped text
   */
  _escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  },
};

// Export for use in other modules
if (typeof module !== "undefined" && module.exports) {
  module.exports = TemplateGallery;
}
