/**
 * KnowledgeSuggestionCard — Inline suggestion component for knowledge gap detection.
 *
 * Shown automatically after assistant responses when gap detection identifies
 * novel information worth saving to the knowledge base.
 *
 * Usage:
 *   showKnowledgeSuggestion(messageDiv, personaAction);
 */

(function () {
  'use strict';

  // Use the same API base URL as the rest of the app
  const API_BASE_URL = 'http://127.0.0.1:11436';

  /**
   * Display a knowledge gap suggestion card below a message element.
   *
   * @param {HTMLElement} messageDiv - The .message div to attach to
   * @param {Object} personaAction - PersonaAction from backend with type 'suggest_kb_write'
   */
  function showKnowledgeSuggestion(messageDiv, personaAction) {
    // Don't show if already exists
    if (messageDiv.querySelector('.knowledge-suggestion-card')) {
      return;
    }

    const data = personaAction.data || {};
    const gap = data.gap || {};
    const novelConcepts = data.novel_concepts || [];
    const suggestedTitle = data.suggested_title || 'Knowledge Note';
    const suggestedDomain = data.suggested_domain || '';
    const gapScore = data.gap_score || 0;
    const rawContent = gap.cloud_content || '';
    const query = gap.query || '';

    // Don't show if gap score is too low (shouldn't happen, but safe guard)
    if (gapScore < 0.4) return;

    const card = document.createElement('div');
    card.className = 'knowledge-suggestion-card';
    card.style.cssText = `
      background: linear-gradient(135deg, #1a2332 0%, #1e2738 100%);
      border: 1px solid #2d5a9e;
      border-radius: 8px;
      padding: 12px 16px;
      margin-top: 10px;
      font-size: 13px;
      color: #e0e0e0;
      box-shadow: 0 2px 8px rgba(45, 90, 158, 0.15);
      animation: slideIn 0.3s ease-out;
      overflow: hidden;
      box-sizing: border-box;
    `;

    // Build concept tags HTML
    const conceptsHTML = novelConcepts.length > 0
      ? novelConcepts.slice(0, 5).map(concept => 
          `<span style="display: inline-block; background: #2d4a6e; color: #a0c4ff; 
           padding: 2px 8px; border-radius: 12px; font-size: 11px; margin-right: 6px; margin-bottom: 4px;
           max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
           ${escapeHtml(concept)}
          </span>`
        ).join('')
      : '';

    card.innerHTML = `
      <div style="display: flex; align-items: start; gap: 12px;">
        <div style="flex-shrink: 0; width: 32px; height: 32px; background: #2d5a9e; 
                    border-radius: 6px; display: flex; align-items: center; justify-content: center;
                    font-size: 18px;">
          💡
        </div>
        
        <div style="flex: 1; min-width: 0; overflow: hidden;">
          <div style="font-weight: 600; font-size: 14px; margin-bottom: 4px; color: #a0c4ff;">
            This seems new. Save as a note?
          </div>
          
          <div style="font-size: 12px; color: #b0b0b0; margin-bottom: 8px;">
            Gap detected: <span style="color: #4caf50; font-weight: 600;">${Math.round(gapScore * 100)}%</span> novel
          </div>
          
          ${conceptsHTML ? `
            <div style="margin-bottom: 10px; display: flex; flex-wrap: wrap; gap: 4px;">
              ${conceptsHTML}
            </div>
          ` : ''}
          
          <div style="font-size: 12px; color: #808080; margin-bottom: 10px; overflow: hidden; text-overflow: ellipsis;">
            Suggested: <strong style="color: #e0e0e0;">${escapeHtml(suggestedTitle)}</strong>
            ${suggestedDomain ? ` → <em>${escapeHtml(suggestedDomain)}</em>` : ''}
          </div>
          
          <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
            <button class="ksg-quick-save"
              style="background: #2d5a27; color: #c8e6c9; border: none; padding: 6px 12px; 
                     border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 600;
                     transition: background 0.2s; white-space: nowrap;">
              Quick Save
            </button>
            
            <button class="ksg-enrich"
              style="background: #3a4a6e; color: #a0c4ff; border: none; padding: 6px 12px; 
                     border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 600;
                     transition: background 0.2s; white-space: nowrap;">
              Enrich with Scribe
            </button>
            
            <button class="ksg-dismiss"
              style="background: transparent; color: #606060; border: 1px solid #333; 
                     padding: 5px 12px; border-radius: 4px; cursor: pointer; font-size: 12px;
                     margin-left: auto; transition: all 0.2s; white-space: nowrap;">
              Dismiss
            </button>
          </div>
        </div>
      </div>
    `;

    // Add hover effects
    const quickSaveBtn = card.querySelector('.ksg-quick-save');
    const enrichBtn = card.querySelector('.ksg-enrich');
    const dismissBtn = card.querySelector('.ksg-dismiss');

    quickSaveBtn.addEventListener('mouseenter', () => {
      quickSaveBtn.style.background = '#3a6e31';
    });
    quickSaveBtn.addEventListener('mouseleave', () => {
      quickSaveBtn.style.background = '#2d5a27';
    });

    enrichBtn.addEventListener('mouseenter', () => {
      enrichBtn.style.background = '#4a5e8e';
    });
    enrichBtn.addEventListener('mouseleave', () => {
      enrichBtn.style.background = '#3a4a6e';
    });

    dismissBtn.addEventListener('mouseenter', () => {
      dismissBtn.style.color = '#e0e0e0';
      dismissBtn.style.borderColor = '#555';
    });
    dismissBtn.addEventListener('mouseleave', () => {
      dismissBtn.style.color = '#606060';
      dismissBtn.style.borderColor = '#333';
    });

    // Wire up button actions
    quickSaveBtn.addEventListener('click', async () => {
      quickSaveBtn.disabled = true;
      quickSaveBtn.textContent = 'Saving...';
      
      try {
        const payload = {
          content: rawContent,
          title: suggestedTitle,
          domain: suggestedDomain,
          tags: novelConcepts,
          source_type: 'cloud_response',
          conversation_id: window.currentConversationId || null
        };
        console.log('Quick save: Sending payload:', payload);
        
        const response = await fetch(`${API_BASE_URL}/api/settings/knowledge/save-quick`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        console.log('Quick save: Response status:', response.status);

        if (response.ok) {
          const result = await response.json();
          console.log('Quick save: Success result:', result);
          showToast('Note saved and indexed', 'success');
          card.style.animation = 'fadeOut 0.3s ease-out';
          setTimeout(() => card.remove(), 300);
          
          // Refresh autonomy metrics in background
          if (window.loadAutonomyData) {
            setTimeout(() => window.loadAutonomyData(), 1000);
          }
        } else {
          const errorText = await response.text();
          console.error('Quick save: Server error:', errorText);
          throw new Error(`Save failed: ${response.status} - ${errorText}`);
        }
      } catch (error) {
        console.error('Quick save error:', error);
        showToast(`Failed to save note: ${error.message}`, 'error');
        quickSaveBtn.disabled = false;
        quickSaveBtn.textContent = 'Quick Save';
      }
    });

    enrichBtn.addEventListener('click', () => {
      // Disable button to prevent double-clicks
      enrichBtn.disabled = true;
      const originalText = enrichBtn.textContent;
      enrichBtn.textContent = 'Opening...';
      
      // Open preview modal with Scribe enrichment flow
      if (window.PreviewModal) {
        // Get conversation history for Scribe context
        const conversationHistory = window.getCurrentConversationMessages
          ? window.getCurrentConversationMessages().map(m => ({ role: m.role, content: m.content }))
          : [];
        
        window.PreviewModal.show({
          content: rawContent,
          title: suggestedTitle,
          domain: suggestedDomain,
          tags: novelConcepts,
          conversation_history: conversationHistory
        }, async (noteData) => {
          // Callback: User clicked Save in the modal
          try {
            console.log('Scribe save: Sending note data:', noteData);
            
            const response = await fetch(`${API_BASE_URL}/api/settings/knowledge/save-scribe`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(noteData)
            });
            
            console.log('Scribe save: Response status:', response.status);
            
            if (response.ok) {
              const result = await response.json();
              console.log('Scribe save: Success result:', result);
              showToast('Note enriched and saved', 'success');
              
              // Remove card with animation
              card.style.animation = 'fadeOut 0.3s ease-out';
              setTimeout(() => card.remove(), 300);
              
              // Refresh autonomy metrics
              if (window.loadAutonomyData) {
                setTimeout(() => window.loadAutonomyData(), 1000);
              }
            } else {
              const errorText = await response.text();
              console.error('Scribe save: Server error:', errorText);
              throw new Error(`Scribe save failed: ${response.status} - ${errorText}`);
            }
          } catch (error) {
            console.error('Scribe save error:', error);
            showToast(`Failed to enrich note: ${error.message}`, 'error');
            
            // Re-enable button on error
            enrichBtn.disabled = false;
            enrichBtn.textContent = originalText;
          }
        });
        
        // Re-enable button after a short delay (modal is now open)
        setTimeout(() => {
          enrichBtn.disabled = false;
          enrichBtn.textContent = originalText;
        }, 500);
        
      } else {
        showToast('Preview modal not available', 'error');
        enrichBtn.disabled = false;
        enrichBtn.textContent = originalText;
      }
    });

    dismissBtn.addEventListener('click', () => {
      card.style.animation = 'fadeOut 0.3s ease-out';
      setTimeout(() => card.remove(), 300);
    });

    messageDiv.appendChild(card);
  }

  /**
   * Helper: Escape HTML to prevent XSS
   */
  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  /**
   * Helper: Show toast notification
   */
  function showToast(message, type = 'info') {
    if (window.showToast) {
      window.showToast(message, type);
    } else {
      // Fallback: console log
      console.log(`[${type.toUpperCase()}] ${message}`);
    }
  }

  // Export to global scope
  window.showKnowledgeSuggestion = showKnowledgeSuggestion;

})();
