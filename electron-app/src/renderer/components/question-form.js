/**
 * Question Form Component (Phase 16c Day 11)
 * 
 * Displays radio button questions from Scribe Organize mode.
 * OpenCode-style interface with "Type your own" option for each question.
 * 
 * Usage:
 *   QuestionForm.show(questionsData, onSubmit);
 *   
 * Example questionsData:
 * {
 *   "questions": [
 *     {
 *       "id": "q1_template",
 *       "question": "What type of note should this be?",
 *       "type": "radio",
 *       "options": [
 *         {"value": "meeting-notes", "label": "Meeting Notes", "description": "For discussions and decisions"},
 *         {"value": "concept-note", "label": "Concept Explanation", "description": "For understanding a concept"},
 *         {"value": "custom", "label": "Type your own", "input": true}
 *       ],
 *       "default": "meeting-notes"
 *     }
 *   ],
 *   "summary": "Please answer these questions to finalize your note"
 * }
 */

const QuestionForm = {
  /**
   * Current questions data
   */
  currentQuestions: null,
  
  /**
   * Callback when form is submitted
   */
  onSubmitCallback: null,
  
  /**
   * Initialize the question form (call once on page load)
   */
  init() {
    // Add container to DOM if not exists
    if (!document.getElementById('question-form-container')) {
      const container = document.createElement('div');
      container.id = 'question-form-container';
      container.className = 'question-form-container hidden';
      container.innerHTML = `
        <div class="question-form-overlay"></div>
        <div class="question-form-modal">
          <div class="question-form-header">
            <h3 class="question-form-title">Answer Questions</h3>
            <button class="question-form-close" aria-label="Close">×</button>
          </div>
          <div class="question-form-body">
            <p class="question-form-summary"></p>
            <form id="question-form-questions" class="question-form-questions"></form>
          </div>
          <div class="question-form-footer">
            <button class="btn btn-secondary question-form-cancel">Cancel</button>
            <button class="btn btn-primary question-form-submit">Continue</button>
          </div>
        </div>
      `;
      document.body.appendChild(container);
      
      // Attach event listeners
      this._attachListeners();
    }
  },
  
  /**
   * Attach event listeners to form elements
   */
  _attachListeners() {
    const container = document.getElementById('question-form-container');
    
    // Close button
    container.querySelector('.question-form-close').addEventListener('click', () => {
      this.hide();
    });
    
    // Cancel button
    container.querySelector('.question-form-cancel').addEventListener('click', () => {
      this.hide();
    });
    
    // Submit button
    container.querySelector('.question-form-submit').addEventListener('click', () => {
      this._handleSubmit();
    });
    
    // Close on overlay click
    container.querySelector('.question-form-overlay').addEventListener('click', () => {
      this.hide();
    });
    
    // Prevent modal close on modal content click
    container.querySelector('.question-form-modal').addEventListener('click', (e) => {
      e.stopPropagation();
    });
  },
  
  /**
   * Show the question form with given questions
   * 
   * @param {Object} questionsData - Questions data from Scribe Organize mode
   * @param {Function} onSubmit - Callback when form is submitted: (answers) => {}
   */
  show(questionsData, onSubmit) {
    this.currentQuestions = questionsData;
    this.onSubmitCallback = onSubmit;
    
    // Render questions
    this._renderQuestions(questionsData);
    
    // Show container
    const container = document.getElementById('question-form-container');
    container.classList.remove('hidden');
    
    // Focus first input/radio
    setTimeout(() => {
      const firstInput = container.querySelector('input[type="radio"], input[type="text"]');
      if (firstInput) {
        firstInput.focus();
      }
    }, 100);
  },
  
  /**
   * Hide the question form
   */
  hide() {
    const container = document.getElementById('question-form-container');
    container.classList.add('hidden');
    this.currentQuestions = null;
    this.onSubmitCallback = null;
  },
  
  /**
   * Render questions into the form
   */
  _renderQuestions(questionsData) {
    const summaryEl = document.querySelector('.question-form-summary');
    const formEl = document.getElementById('question-form-questions');
    
    // Set summary
    summaryEl.textContent = questionsData.summary || 'Please answer the following questions:';
    
    // Clear previous questions
    formEl.innerHTML = '';
    
    // Render each question
    questionsData.questions.forEach((q, index) => {
      const questionDiv = this._renderQuestion(q, index);
      formEl.appendChild(questionDiv);
    });
  },
  
  /**
   * Render a single question
   */
  _renderQuestion(question, index) {
    // Normalize question data (handle both simple and complex formats)
    const questionId = question.id || `q${index}`;
    const questionType = question.type || 'radio';
    const options = question.options || [];
    
    // Normalize options (convert strings to objects if needed)
    const normalizedOptions = options.map((opt, i) => {
      if (typeof opt === 'string') {
        return {
          value: opt,
          label: opt,
          description: null
        };
      }
      return opt;
    });
    
    const div = document.createElement('div');
    div.className = 'question-form-question';
    div.dataset.questionId = questionId;
    
    // Question text
    const questionLabel = document.createElement('label');
    questionLabel.className = 'question-form-question-label';
    questionLabel.textContent = `${index + 1}. ${question.question}`;
    div.appendChild(questionLabel);
    
    // Options container
    const optionsDiv = document.createElement('div');
    optionsDiv.className = 'question-form-options';
    
    if (questionType === 'radio') {
      normalizedOptions.forEach((option, optIndex) => {
        const normalizedQuestion = {
          ...question,
          id: questionId,
          type: questionType
        };
        const optionDiv = this._renderRadioOption(normalizedQuestion, option, optIndex);
        optionsDiv.appendChild(optionDiv);
      });
    }
    
    div.appendChild(optionsDiv);
    
    return div;
  },
  
  /**
   * Render a radio button option
   */
  _renderRadioOption(question, option, optIndex) {
    const optionDiv = document.createElement('div');
    optionDiv.className = 'question-form-option';
    
    // Radio input
    const radio = document.createElement('input');
    radio.type = 'radio';
    radio.name = question.id;
    radio.value = option.value;
    radio.id = `${question.id}_${optIndex}`;
    radio.className = 'question-form-radio';
    
    // Set default
    if (option.value === question.default) {
      radio.checked = true;
    }
    
    // Label for radio
    const label = document.createElement('label');
    label.htmlFor = radio.id;
    label.className = 'question-form-option-label';
    
    const labelText = document.createElement('span');
    labelText.className = 'question-form-option-text';
    labelText.textContent = option.label;
    label.appendChild(labelText);
    
    if (option.description) {
      const desc = document.createElement('span');
      desc.className = 'question-form-option-description';
      desc.textContent = option.description;
      label.appendChild(desc);
    }
    
    optionDiv.appendChild(radio);
    optionDiv.appendChild(label);
    
    // If this is a "Type your own" option, add text input
    if (option.input) {
      const customInput = document.createElement('input');
      customInput.type = 'text';
      customInput.className = 'question-form-custom-input hidden';
      customInput.dataset.questionId = question.id;
      customInput.placeholder = 'Type your answer...';
      
      // Show/hide custom input based on radio selection
      radio.addEventListener('change', () => {
        if (radio.checked) {
          customInput.classList.remove('hidden');
          customInput.focus();
        }
      });
      
      // Hide custom input when other options selected
      const allRadios = document.querySelectorAll(`input[name="${question.id}"]`);
      allRadios.forEach(r => {
        if (r !== radio) {
          r.addEventListener('change', () => {
            if (r.checked) {
              customInput.classList.add('hidden');
              customInput.value = '';
            }
          });
        }
      });
      
      optionDiv.appendChild(customInput);
    }
    
    return optionDiv;
  },
  
  /**
   * Handle form submission
   */
  _handleSubmit() {
    const answers = {};
    
    // Collect answers from all questions
    this.currentQuestions.questions.forEach((question, index) => {
      const questionId = question.id || `q${index}`;
      const selectedRadio = document.querySelector(`input[name="${questionId}"]:checked`);
      
      if (selectedRadio) {
        const value = selectedRadio.value;
        
        // Check if this is a custom input option
        if (value === 'custom') {
          const customInput = document.querySelector(`.question-form-custom-input[data-question-id="${questionId}"]`);
          if (customInput && customInput.value.trim()) {
            answers[question.question] = customInput.value.trim();
          } else {
            // Custom selected but no value - show error
            this._showError(questionId, 'Please enter a value or select a different option');
            return;
          }
        } else {
          // Use the actual question text as the key (for backend compatibility)
          answers[question.question] = value;
        }
      } else {
        // No answer selected - show error
        this._showError(questionId, 'Please select an option');
        return;
      }
    });
    
    // Validate we have all answers
    if (Object.keys(answers).length !== this.currentQuestions.questions.length) {
      return;
    }
    
    // Call callback with answers
    if (this.onSubmitCallback) {
      this.onSubmitCallback(answers);
    }
    
    // Hide form
    this.hide();
  },
  
  /**
   * Show error message for a question
   */
  _showError(questionId, message) {
    const questionDiv = document.querySelector(`[data-question-id="${questionId}"]`);
    if (!questionDiv) return;
    
    // Remove existing error
    const existingError = questionDiv.querySelector('.question-form-error');
    if (existingError) {
      existingError.remove();
    }
    
    // Add error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'question-form-error';
    errorDiv.textContent = message;
    questionDiv.appendChild(errorDiv);
    
    // Remove error after 3 seconds
    setTimeout(() => {
      errorDiv.remove();
    }, 3000);
  }
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => QuestionForm.init());
} else {
  QuestionForm.init();
}

// Export to global scope for browser use
window.QuestionForm = QuestionForm;

// Export for Node.js modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = QuestionForm;
}
