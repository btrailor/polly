/**
 * EmptyState component — reusable empty state with optional call-to-action.
 *
 * Usage:
 *   const el = EmptyState.render({
 *     icon: 'message-square',
 *     title: 'No conversations yet',
 *     description: 'Start a conversation with Polly to see it appear here.',
 *     actionLabel: 'New Chat',
 *     onAction: () => createNewConversation(),
 *     size: 'small' // 'small' | 'medium' (default) | 'large'
 *   });
 *   container.appendChild(el);
 */
class EmptyState {
  /**
   * @param {object} options
   * @param {string} options.icon - Lucide icon name (e.g. "message-square", "search")
   * @param {string} options.title - Headline text
   * @param {string} options.description - Brief guidance text
   * @param {string} [options.actionLabel] - Primary button text
   * @param {function} [options.onAction] - Primary button click handler
   * @param {string} [options.secondaryLabel] - Optional secondary button text
   * @param {function} [options.onSecondary] - Secondary button click handler
   * @param {string} [options.size] - "small" | "medium" (default) | "large"
   * @returns {HTMLElement}
   */
  static render(options) {
    const {
      icon,
      title,
      description,
      actionLabel,
      onAction,
      secondaryLabel,
      onSecondary,
      size = 'medium',
    } = options;

    const container = document.createElement('div');
    container.className = `empty-state empty-state--${size}`;
    container.innerHTML = `
      <div class="empty-state__icon">
        <i data-lucide="${icon}" aria-hidden="true"></i>
      </div>
      <h3 class="empty-state__title">${title}</h3>
      <p class="empty-state__description">${description}</p>
      ${actionLabel ? `<button class="empty-state__action btn btn-primary">${actionLabel}</button>` : ''}
      ${secondaryLabel ? `<button class="empty-state__secondary btn btn-ghost">${secondaryLabel}</button>` : ''}
    `;

    if (actionLabel && onAction) {
      container.querySelector('.empty-state__action').addEventListener('click', onAction);
    }
    if (secondaryLabel && onSecondary) {
      container.querySelector('.empty-state__secondary').addEventListener('click', onSecondary);
    }

    // Trigger Lucide icon rendering after the element is in the DOM
    requestAnimationFrame(() => {
      if (typeof lucide !== 'undefined') {
        lucide.createIcons({ nodes: [container] });
      }
    });

    return container;
  }
}

window.EmptyState = EmptyState;
