/**
 * Mental Models Editor Component (Phase 16f)
 *
 * Full-featured editor for managing mental models:
 * - List all models (33 total)
 * - Create new models from templates
 * - Edit existing models
 * - Toggle models on/off
 * - Delete custom models (protect defaults)
 * - View which models are currently active
 *
 * Usage:
 *   await MentalModelsEditor.init();
 *   MentalModelsEditor.show();
 */

const MentalModelsEditor = {
  /**
   * All mental models (loaded from API)
   */
  models: [],

  /**
   * Currently active models (based on context)
   */
  activeModels: [],

  /**
   * Currently editing model (null if viewing list)
   */
  editingModel: null,

  /**
   * Template for new models
   */
  newModelTemplate: {
    name: "",
    description: "",
    principles: ["", "", ""],
    prompt_injection: "",
    applies_to: [],
    active_on_pages: [],
    active_for_personas: [],
    active_for_modes: [],
    keywords: [],
    enabled: true,
  },

  /**
   * Available options for dropdowns
   */
  options: {
    domains: ["sigils", "signals", "scrolls", "glyphs", "grids"],
    pages: [
      "code",
      "projects",
      "learning",
      "notes",
      "patterns",
      "dashboard",
      "mail",
      "calendar",
    ],
    personas: ["programmer", "architect", "scribe", "teacher"],
    modes: ["plan", "build", "guide", "socratic", "capture", "enrich"],
  },

  /**
   * Initialize the mental models editor (call once on page load)
   */
  async init() {
    console.log("[MentalModelsEditor] Initializing...");

    // Add container to DOM if not exists
    if (!document.getElementById("mental-models-editor-container")) {
      const container = document.createElement("div");
      container.id = "mental-models-editor-container";
      container.className = "mental-models-editor-container hidden";
      container.innerHTML = this._getContainerHTML();
      document.body.appendChild(container);

      // Attach event listeners
      this._attachListeners();
    }

    // Load models from API
    await this.loadModels();

    console.log(
      "[MentalModelsEditor] Initialized with",
      this.models.length,
      "models",
    );
  },

  /**
   * Load all mental models from API
   */
  async loadModels(retries = 3, delay = 1000) {
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const response = await fetch(
          "http://127.0.0.1:11436/polly/mental-models/list",
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        this.models = data.models || [];
        console.log(`[MentalModelsEditor] Loaded ${this.models.length} models`);
        return; // Success, exit retry loop
      } catch (error) {
        console.warn(
          `[MentalModelsEditor] Load attempt ${attempt}/${retries} failed:`,
          error.message,
        );

        if (attempt < retries) {
          // Wait before retrying
          await new Promise((resolve) => setTimeout(resolve, delay));
        } else {
          // Final attempt failed (often 503 while Polly is still initializing)
          const is503 = (error.message || "").includes("503");
          if (is503) {
            console.warn(
              "[MentalModelsEditor] Models not ready yet (503); will show empty until retry.",
            );
          } else {
            console.error(
              "[MentalModelsEditor] Failed to load models after",
              retries,
              "attempts",
            );
          }
          this.models = [];
        }
      }
    }
  },

  /**
   * Load currently active models for context
   */
  async loadActiveModels(retries = 3, delay = 1000) {
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const response = await fetch(
          "http://127.0.0.1:11436/polly/mental-models/active",
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        this.activeModels = data.active_models || [];
        console.log(
          `[MentalModelsEditor] ${this.activeModels.length} models active for current context`,
        );
        return; // Success, exit retry loop
      } catch (error) {
        console.warn(
          `[MentalModelsEditor] Load active models attempt ${attempt}/${retries} failed:`,
          error.message,
        );

        if (attempt < retries) {
          // Wait before retrying
          await new Promise((resolve) => setTimeout(resolve, delay));
        } else {
          // Final attempt failed
          console.error(
            "[MentalModelsEditor] Failed to load active models after",
            retries,
            "attempts",
          );
          this.activeModels = [];
        }
      }
    }
  },

  /**
   * Show the mental models editor
   */
  async show() {
    console.log("[MentalModelsEditor] Opening editor...");

    // Load models and active context
    await this.loadModels();
    await this.loadActiveModels();

    // Render list view
    this.renderListView();

    // Show container
    const container = document.getElementById("mental-models-editor-container");
    container.classList.remove("hidden");
  },

  /**
   * Hide the mental models editor
   */
  hide() {
    console.log("[MentalModelsEditor] Closing editor...");
    const container = document.getElementById("mental-models-editor-container");
    container.classList.add("hidden");
    this.editingModel = null;
  },

  /**
   * Render the list view of all models
   */
  renderListView() {
    const body = document.querySelector(".mental-models-editor-body");

    // Group models by tier/category
    const tiers = {
      "Core Philosophy": [
        "infinite_games",
        "instruments_over_tracks",
        "constraint_as_meaning",
      ],
      "Learning & Thinking": [
        "pedagogy_of_liberation",
        "reverse_engineering",
        "socratic_method",
      ],
      "Systems & Technical": [
        "systems_thinking",
        "first_principles",
        "design_thinking",
      ],
      Communication: ["inbox_zero", "async_first", "time_blocking"],
      "Aesthetic & Craft": [
        "hyper_minimalism",
        "readability_ratchet",
        "local_variables",
        "instrument_standard",
        "sustainability_lens",
        "signal_to_noise",
        "generous_interface",
      ],
      "Decision-Making": [
        "constraint_based_filter",
        "compound_question",
        "delegation_test",
        "reverse_engineering_frame",
      ],
      "Workflow & Process": [
        "continuation_probe",
        "context_capture",
        "good_enough_threshold",
        "friction_audit",
        "two_week_test",
      ],
      "Architect-Specific": [
        "map_before_territory",
        "three_altitudes",
        "anchor_document",
      ],
      "Cross-Domain": ["domain_bridge", "problem_posing_pivot"],
    };

    let html = `
      <div class="mental-models-list-header">
        <h3>Mental Models (${this.models.length} total, ${this.activeModels.length} active)</h3>
        <button class="mm-btn mm-btn-primary" onclick="MentalModelsEditor.createNewModel()">
          + New Model
        </button>
      </div>
      <div class="mental-models-active-indicator">
        <strong>Currently Active:</strong>
        ${
          this.activeModels.length > 0
            ? this.activeModels
                .map(
                  (m) =>
                    `<span class="mm-badge mm-badge-active">${m.name}</span>`,
                )
                .join("")
            : '<span class="mm-text-muted">None (no context set)</span>'
        }
      </div>
    `;

    // Render each tier
    for (const [tierName, modelIds] of Object.entries(tiers)) {
      const tierModels = this.models.filter((m) => modelIds.includes(m.id));
      if (tierModels.length === 0) continue;

      html += `
        <div class="mental-models-tier">
          <h4 class="mental-models-tier-title">${tierName}</h4>
          <div class="mental-models-grid">
      `;

      for (const model of tierModels) {
        const isActive = this.activeModels.some((m) => m.id === model.id);
        html += this._getModelCardHTML(model, isActive);
      }

      html += `
          </div>
        </div>
      `;
    }

    // Custom models (not in default tiers)
    const customModels = this.models.filter(
      (m) => !Object.values(tiers).flat().includes(m.id),
    );

    if (customModels.length > 0) {
      html += `
        <div class="mental-models-tier">
          <h4 class="mental-models-tier-title">Custom Models</h4>
          <div class="mental-models-grid">
      `;

      for (const model of customModels) {
        const isActive = this.activeModels.some((m) => m.id === model.id);
        html += this._getModelCardHTML(model, isActive);
      }

      html += `
          </div>
        </div>
      `;
    }

    body.innerHTML = html;
  },

  /**
   * Get HTML for a single model card
   */
  _getModelCardHTML(model, isActive) {
    const statusClass = model.enabled ? "mm-card-enabled" : "mm-card-disabled";
    const activeClass = isActive ? "mm-card-active" : "";

    return `
      <div class="mental-models-card ${statusClass} ${activeClass}">
        <div class="mm-card-header">
          <h5 class="mm-card-title">${this._escapeHTML(model.name)}</h5>
          <div class="mm-card-actions">
            <button 
              class="mm-btn-icon mm-btn-toggle" 
              onclick="MentalModelsEditor.toggleModel('${model.id}')"
              title="${model.enabled ? "Disable" : "Enable"}">
              ${model.enabled ? "●" : "○"}
            </button>
          </div>
        </div>
        <p class="mm-card-description">${this._escapeHTML(model.description)}</p>
        <div class="mm-card-meta">
          ${
            model.active_for_personas.length > 0
              ? `<span class="mm-badge">Personas: ${model.active_for_personas.join(", ")}</span>`
              : ""
          }
          ${isActive ? `<span class="mm-badge mm-badge-active">Active Now</span>` : ""}
        </div>
        <div class="mm-card-footer">
          <button class="mm-btn mm-btn-sm" onclick="MentalModelsEditor.editModel('${model.id}')">
            Edit
          </button>
          <button class="mm-btn mm-btn-sm mm-btn-secondary" onclick="MentalModelsEditor.viewModelDetails('${model.id}')">
            View Details
          </button>
        </div>
      </div>
    `;
  },

  /**
   * Render the edit view for a specific model
   */
  renderEditView(modelId) {
    const model = this.models.find((m) => m.id === modelId) || {
      ...this.newModelTemplate,
      id: null,
    };
    this.editingModel = model;

    const body = document.querySelector(".mental-models-editor-body");

    body.innerHTML = `
      <div class="mental-models-edit-header">
        <button class="mm-btn mm-btn-secondary" onclick="MentalModelsEditor.renderListView()">
          ← Back to List
        </button>
        <h3>${model.id ? "Edit" : "Create"} Mental Model</h3>
      </div>
      
      <form class="mental-models-edit-form" onsubmit="MentalModelsEditor.saveModel(event)">
        <div class="mm-form-group">
          <label class="mm-label">Name</label>
          <input 
            type="text" 
            class="mm-input" 
            id="mm-edit-name" 
            value="${this._escapeHTML(model.name)}"
            required>
        </div>
        
        <div class="mm-form-group">
          <label class="mm-label">Description</label>
          <textarea 
            class="mm-textarea" 
            id="mm-edit-description" 
            rows="3"
            required>${this._escapeHTML(model.description)}</textarea>
        </div>
        
        <div class="mm-form-group">
          <label class="mm-label">Principles (one per line)</label>
          <textarea 
            class="mm-textarea" 
            id="mm-edit-principles" 
            rows="5"
            placeholder="Enter each principle on a new line"
            required>${(model.principles || []).join("\n")}</textarea>
          <small class="mm-help-text">Key ideas that guide this mental model</small>
        </div>
        
        <div class="mm-form-group">
          <label class="mm-label">Prompt Injection</label>
          <textarea 
            class="mm-textarea" 
            id="mm-edit-prompt" 
            rows="5"
            placeholder="Instructions for how Polly should use this model"
            required>${this._escapeHTML(model.prompt_injection)}</textarea>
          <small class="mm-help-text">Instructions injected into Polly's context when this model is active</small>
        </div>
        
        <div class="mm-form-row">
          <div class="mm-form-group">
            <label class="mm-label">Domains (applies_to)</label>
            <div class="mm-checkbox-group">
              ${this.options.domains
                .map(
                  (d) => `
                <label class="mm-checkbox-label">
                  <input 
                    type="checkbox" 
                    value="${d}" 
                    ${(model.applies_to || []).includes(d) ? "checked" : ""}>
                  ${d}
                </label>
              `,
                )
                .join("")}
            </div>
          </div>
          
          <div class="mm-form-group">
            <label class="mm-label">Pages (active_on_pages)</label>
            <div class="mm-checkbox-group">
              ${this.options.pages
                .map(
                  (p) => `
                <label class="mm-checkbox-label">
                  <input 
                    type="checkbox" 
                    value="${p}" 
                    ${(model.active_on_pages || []).includes(p) ? "checked" : ""}>
                  ${p}
                </label>
              `,
                )
                .join("")}
            </div>
          </div>
        </div>
        
        <div class="mm-form-row">
          <div class="mm-form-group">
            <label class="mm-label">Personas (active_for_personas)</label>
            <div class="mm-checkbox-group">
              ${this.options.personas
                .map(
                  (p) => `
                <label class="mm-checkbox-label">
                  <input 
                    type="checkbox" 
                    value="${p}" 
                    ${(model.active_for_personas || []).includes(p) ? "checked" : ""}>
                  ${p}
                </label>
              `,
                )
                .join("")}
            </div>
          </div>
          
          <div class="mm-form-group">
            <label class="mm-label">Modes (active_for_modes)</label>
            <div class="mm-checkbox-group">
              ${this.options.modes
                .map(
                  (m) => `
                <label class="mm-checkbox-label">
                  <input 
                    type="checkbox" 
                    value="${m}" 
                    ${(model.active_for_modes || []).includes(m) ? "checked" : ""}>
                  ${m}
                </label>
              `,
                )
                .join("")}
            </div>
          </div>
        </div>
        
        <div class="mm-form-group">
          <label class="mm-label">Keywords (comma-separated)</label>
          <input 
            type="text" 
            class="mm-input" 
            id="mm-edit-keywords" 
            value="${(model.keywords || []).join(", ")}"
            placeholder="keyword1, keyword2, keyword3">
          <small class="mm-help-text">Used for context-based activation</small>
        </div>
        
        <div class="mm-form-group">
          <label class="mm-checkbox-label mm-checkbox-large">
            <input 
              type="checkbox" 
              id="mm-edit-enabled" 
              ${model.enabled ? "checked" : ""}>
            <strong>Enabled</strong> (activate this model based on context)
          </label>
        </div>
        
        <div class="mm-form-actions">
          <button type="submit" class="mm-btn mm-btn-primary">
            ${model.id ? "Save Changes" : "Create Model"}
          </button>
          <button type="button" class="mm-btn mm-btn-secondary" onclick="MentalModelsEditor.renderListView()">
            Cancel
          </button>
          ${
            model.id
              ? `
            <button 
              type="button" 
              class="mm-btn mm-btn-danger mm-btn-right" 
              onclick="MentalModelsEditor.deleteModel('${model.id}')">
              Delete Model
            </button>
          `
              : ""
          }
        </div>
      </form>
    `;
  },

  /**
   * View detailed information about a model (read-only)
   */
  viewModelDetails(modelId) {
    const model = this.models.find((m) => m.id === modelId);
    if (!model) return;

    const body = document.querySelector(".mental-models-editor-body");

    body.innerHTML = `
      <div class="mental-models-detail-header">
        <button class="mm-btn mm-btn-secondary" onclick="MentalModelsEditor.renderListView()">
          ← Back to List
        </button>
        <h3>${this._escapeHTML(model.name)}</h3>
        <div class="mm-detail-actions">
          <button class="mm-btn mm-btn-primary" onclick="MentalModelsEditor.editModel('${model.id}')">
            Edit
          </button>
          <button 
            class="mm-btn ${model.enabled ? "mm-btn-warning" : "mm-btn-success"}" 
            onclick="MentalModelsEditor.toggleModel('${model.id}')">
            ${model.enabled ? "Disable" : "Enable"}
          </button>
        </div>
      </div>
      
      <div class="mental-models-detail-body">
        <div class="mm-detail-section">
          <h4>Description</h4>
          <p>${this._escapeHTML(model.description)}</p>
        </div>
        
        <div class="mm-detail-section">
          <h4>Principles</h4>
          <ul>
            ${(model.principles || []).map((p) => `<li>${this._escapeHTML(p)}</li>`).join("")}
          </ul>
        </div>
        
        <div class="mm-detail-section">
          <h4>Prompt Injection</h4>
          <pre class="mm-code-block">${this._escapeHTML(model.prompt_injection)}</pre>
        </div>
        
        <div class="mm-detail-section">
          <h4>Activation Rules</h4>
          <div class="mm-detail-grid">
            <div>
              <strong>Domains:</strong>
              ${
                model.applies_to.length > 0
                  ? model.applies_to
                      .map((d) => `<span class="mm-badge">${d}</span>`)
                      .join(" ")
                  : '<span class="mm-text-muted">None</span>'
              }
            </div>
            <div>
              <strong>Pages:</strong>
              ${
                model.active_on_pages.length > 0
                  ? model.active_on_pages
                      .map((p) => `<span class="mm-badge">${p}</span>`)
                      .join(" ")
                  : '<span class="mm-text-muted">None</span>'
              }
            </div>
            <div>
              <strong>Personas:</strong>
              ${
                model.active_for_personas.length > 0
                  ? model.active_for_personas
                      .map((p) => `<span class="mm-badge">${p}</span>`)
                      .join(" ")
                  : '<span class="mm-text-muted">None</span>'
              }
            </div>
            <div>
              <strong>Modes:</strong>
              ${
                model.active_for_modes.length > 0
                  ? model.active_for_modes
                      .map((m) => `<span class="mm-badge">${m}</span>`)
                      .join(" ")
                  : '<span class="mm-text-muted">None</span>'
              }
            </div>
          </div>
        </div>
        
        <div class="mm-detail-section">
          <h4>Keywords</h4>
          ${
            model.keywords.length > 0
              ? model.keywords
                  .map(
                    (k) =>
                      `<span class="mm-badge mm-badge-keyword">${k}</span>`,
                  )
                  .join(" ")
              : '<span class="mm-text-muted">None</span>'
          }
        </div>
        
        <div class="mm-detail-section">
          <h4>Status</h4>
          <p>
            <strong>Enabled:</strong> ${model.enabled ? "Yes" : "No"}
            ${
              this.activeModels.some((m) => m.id === model.id)
                ? '<span class="mm-badge mm-badge-active">Active in Current Context</span>'
                : ""
            }
          </p>
        </div>
      </div>
    `;
  },

  /**
   * Create a new model
   */
  createNewModel() {
    this.renderEditView(null);
  },

  /**
   * Edit an existing model
   */
  editModel(modelId) {
    this.renderEditView(modelId);
  },

  /**
   * Save model (create or update)
   */
  async saveModel(event) {
    event.preventDefault();

    // Collect form data
    const formData = {
      name: document.getElementById("mm-edit-name").value,
      description: document.getElementById("mm-edit-description").value,
      principles: document
        .getElementById("mm-edit-principles")
        .value.split("\n")
        .filter((p) => p.trim()),
      prompt_injection: document.getElementById("mm-edit-prompt").value,
      applies_to: Array.from(
        document.querySelectorAll(".mm-checkbox-group input[value]:checked"),
      )
        .filter((cb) => this.options.domains.includes(cb.value))
        .map((cb) => cb.value),
      active_on_pages: Array.from(
        document.querySelectorAll(".mm-checkbox-group input[value]:checked"),
      )
        .filter((cb) => this.options.pages.includes(cb.value))
        .map((cb) => cb.value),
      active_for_personas: Array.from(
        document.querySelectorAll(".mm-checkbox-group input[value]:checked"),
      )
        .filter((cb) => this.options.personas.includes(cb.value))
        .map((cb) => cb.value),
      active_for_modes: Array.from(
        document.querySelectorAll(".mm-checkbox-group input[value]:checked"),
      )
        .filter((cb) => this.options.modes.includes(cb.value))
        .map((cb) => cb.value),
      keywords: document
        .getElementById("mm-edit-keywords")
        .value.split(",")
        .map((k) => k.trim())
        .filter((k) => k),
      enabled: document.getElementById("mm-edit-enabled").checked,
    };

    // Generate ID for new models
    if (!this.editingModel.id) {
      formData.id = formData.name.toLowerCase().replace(/[^a-z0-9]+/g, "_");
    }

    try {
      const isNew = !this.editingModel.id;
      const url = isNew
        ? "http://127.0.0.1:11436/polly/mental-models/create"
        : `http://127.0.0.1:11436/polly/mental-models/${this.editingModel.id}`;

      const response = await fetch(url, {
        method: isNew ? "POST" : "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error("Failed to save model");

      console.log(
        `[MentalModelsEditor] ${isNew ? "Created" : "Updated"} model:`,
        formData.name,
      );

      // Reload and show list
      await this.loadModels();
      this.renderListView();

      // Show success message
      this._showToast(
        `Model ${isNew ? "created" : "updated"} successfully!`,
        "success",
      );
    } catch (error) {
      console.error("[MentalModelsEditor] Failed to save model:", error);
      this._showToast("Failed to save model. Please try again.", "error");
    }
  },

  /**
   * Toggle model enabled/disabled
   */
  async toggleModel(modelId) {
    try {
      const response = await fetch(
        `http://127.0.0.1:11436/polly/mental-models/${modelId}/toggle`,
        {
          method: "POST",
        },
      );

      if (!response.ok) throw new Error("Failed to toggle model");

      const data = await response.json();
      console.log(
        `[MentalModelsEditor] Toggled model ${modelId}:`,
        data.enabled,
      );

      // Reload and refresh view
      await this.loadModels();
      this.renderListView();

      this._showToast(
        `Model ${data.enabled ? "enabled" : "disabled"}`,
        "success",
      );
    } catch (error) {
      console.error("[MentalModelsEditor] Failed to toggle model:", error);
      this._showToast("Failed to toggle model. Please try again.", "error");
    }
  },

  /**
   * Delete a model
   */
  async deleteModel(modelId) {
    if (!(await ConfirmDialog.show({
      title: 'Delete mental model',
      message: 'Are you sure you want to delete this mental model? This cannot be undone.',
      confirmLabel: 'Delete',
      destructive: true,
    }))) {
      return;
    }

    try {
      const response = await fetch(
        `http://127.0.0.1:11436/polly/mental-models/${modelId}`,
        {
          method: "DELETE",
        },
      );

      if (!response.ok) throw new Error("Failed to delete model");

      console.log(`[MentalModelsEditor] Deleted model ${modelId}`);

      // Reload and show list
      await this.loadModels();
      this.renderListView();

      this._showToast("Model deleted successfully", "success");
    } catch (error) {
      console.error("[MentalModelsEditor] Failed to delete model:", error);
      this._showToast("Failed to delete model. Please try again.", "error");
    }
  },

  /**
   * Show toast notification
   */
  _showToast(message, type = "info") {
    // Simple toast implementation
    const toast = document.createElement("div");
    toast.className = `mm-toast mm-toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.classList.add("mm-toast-show");
    }, 10);

    setTimeout(() => {
      toast.classList.remove("mm-toast-show");
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  },

  /**
   * Escape HTML to prevent XSS
   */
  _escapeHTML(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  },

  /**
   * Get container HTML
   */
  _getContainerHTML() {
    return `
      <div class="mental-models-editor-overlay"></div>
      <div class="mental-models-editor-modal">
        <div class="mental-models-editor-header">
          <h2>Mental Models Manager</h2>
          <button class="mental-models-editor-close" aria-label="Close">×</button>
        </div>
        <div class="mental-models-editor-body">
          <!-- Content rendered dynamically -->
        </div>
      </div>
    `;
  },

  /**
   * Attach event listeners
   */
  _attachListeners() {
    // Close button
    const closeBtn = document.querySelector(".mental-models-editor-close");
    closeBtn.addEventListener("click", () => this.hide());

    // Close on overlay click
    const overlay = document.querySelector(".mental-models-editor-overlay");
    overlay.addEventListener("click", () => this.hide());

    // Escape key to close
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        const container = document.getElementById(
          "mental-models-editor-container",
        );
        if (!container.classList.contains("hidden")) {
          this.hide();
        }
      }
    });
  },
};

// Initialization is triggered from app.js after the backend server is ready
// so we avoid connection-refused errors on load.
