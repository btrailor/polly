/**
 * SkeletonLoader — view-specific skeleton placeholder templates.
 *
 * Usage:
 *   element.innerHTML = SkeletonLoader.forView('notes');
 *   element.innerHTML = SkeletonLoader.listItems(6);
 */
class SkeletonLoader {
  /**
   * Return an HTML string skeleton for the given view type.
   * @param {string} viewType - "dashboard"|"conversations"|"notes"|"patterns"|
   *                            "settings"|"knowledge"|"graph"|"curricula"|
   *                            "learning"|"garden-suggestions"
   * @returns {string} HTML string with role="status" for accessibility
   */
  static forView(viewType) {
    const templates = {
      dashboard: `
        <div class="skeleton-view" role="status" aria-label="Loading dashboard">
          <div class="skeleton skeleton-heading"></div>
          <div style="display:flex;gap:12px;margin-bottom:24px;">
            <div class="skeleton skeleton-stat"></div>
            <div class="skeleton skeleton-stat"></div>
            <div class="skeleton skeleton-stat"></div>
            <div class="skeleton skeleton-stat"></div>
          </div>
          <div class="skeleton skeleton-heading" style="width:30%;"></div>
          <div class="skeleton skeleton-card"></div>
          <div class="skeleton skeleton-card"></div>
        </div>
      `,

      conversations: `
        <div class="skeleton-view" role="status" aria-label="Loading conversations">
          ${SkeletonLoader._listItems(6)}
        </div>
      `,

      notes: `
        <div class="skeleton-view" role="status" aria-label="Loading notes">
          <div class="skeleton skeleton-heading"></div>
          ${SkeletonLoader._listItems(8, false)}
        </div>
      `,

      patterns: `
        <div class="skeleton-view" role="status" aria-label="Loading patterns">
          <div class="skeleton skeleton-heading"></div>
          <div class="skeleton skeleton-card" style="height:60px;"></div>
          <div class="skeleton skeleton-card" style="height:60px;"></div>
          <div class="skeleton skeleton-card" style="height:60px;"></div>
          <div class="skeleton skeleton-card" style="height:60px;"></div>
        </div>
      `,

      settings: `
        <div class="skeleton-view" role="status" aria-label="Loading settings">
          <div class="skeleton skeleton-heading"></div>
          <div class="skeleton skeleton-text skeleton-text--full" style="height:36px;margin-bottom:16px;"></div>
          <div class="skeleton skeleton-text skeleton-text--full" style="height:36px;margin-bottom:16px;"></div>
          <div class="skeleton skeleton-text skeleton-text--full" style="height:36px;margin-bottom:16px;"></div>
          <div class="skeleton skeleton-text skeleton-text--medium" style="height:32px;"></div>
        </div>
      `,

      knowledge: `
        <div class="skeleton-view" role="status" aria-label="Loading knowledge base">
          <div class="skeleton skeleton-heading"></div>
          <div style="display:flex;gap:12px;margin-bottom:16px;">
            <div class="skeleton skeleton-stat" style="height:60px;"></div>
            <div class="skeleton skeleton-stat" style="height:60px;"></div>
          </div>
          <div class="skeleton skeleton-card"></div>
          <div class="skeleton skeleton-card"></div>
        </div>
      `,

      graph: `
        <div class="skeleton-view" role="status" aria-label="Loading graph">
          <div class="skeleton skeleton-heading"></div>
          ${SkeletonLoader._listItems(5, false)}
        </div>
      `,

      curricula: `
        <div class="skeleton-view" role="status" aria-label="Loading curricula">
          <div class="skeleton skeleton-heading" style="width:60%;"></div>
          <div class="skeleton skeleton-card" style="height:70px;"></div>
          <div class="skeleton skeleton-card" style="height:70px;"></div>
          <div class="skeleton skeleton-card" style="height:70px;"></div>
        </div>
      `,

      learning: `
        <div class="skeleton-view" role="status" aria-label="Loading topics">
          <div class="skeleton skeleton-heading" style="width:50%;"></div>
          ${SkeletonLoader._listItems(6, false)}
        </div>
      `,

      'garden-suggestions': `
        <div class="skeleton-view" role="status" aria-label="Loading suggestions">
          <div class="skeleton skeleton-card" style="height:50px;"></div>
          <div class="skeleton skeleton-card" style="height:50px;"></div>
          <div class="skeleton skeleton-card" style="height:50px;"></div>
        </div>
      `,
    };

    return templates[viewType] ?? templates.settings;
  }

  /**
   * Shorthand: return N conversation-style list item skeletons (with avatar).
   * @param {number} count
   * @returns {string} HTML string
   */
  static listItems(count = 6) {
    return `<div class="skeleton-view" role="status" aria-label="Loading">
      ${SkeletonLoader._listItems(count)}
    </div>`;
  }

  // ── Private helpers ──────────────────────────────────────

  /** @private */
  static _listItems(count, withAvatar = true) {
    const item = withAvatar
      ? `<div class="skeleton-list-item">
           <div class="skeleton skeleton-avatar"></div>
           <div style="flex:1;">
             <div class="skeleton skeleton-text skeleton-text--medium"></div>
             <div class="skeleton skeleton-text skeleton-text--short" style="height:10px;"></div>
           </div>
         </div>`
      : `<div class="skeleton-list-item">
           <div style="flex:1;">
             <div class="skeleton skeleton-text skeleton-text--long"></div>
             <div class="skeleton skeleton-text skeleton-text--short" style="height:10px;"></div>
           </div>
         </div>`;

    return Array(count).fill(item).join('');
  }
}

window.SkeletonLoader = SkeletonLoader;
