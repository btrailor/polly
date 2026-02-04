/**
 * Package Approval Dialog
 * Phase 23.5: Security Hardening
 * 
 * Shows package approval dialog when unapproved packages are detected.
 * Displays package metadata from PyPI and Context7 trust scores.
 */

/**
 * Show package approval dialog
 * @param {Array} packages - Array of package objects with approval_id and package_name
 * @param {Function} onApprove - Callback when user approves (approval_id, permanent)
 * @param {Function} onDeny - Callback when user denies (approval_id, reason)
 */
async function showPackageApprovalDialog(packages, onApprove, onDeny) {
  if (!packages || packages.length === 0) {
    console.warn('No packages to approve');
    return;
  }

  // Fetch metadata for all packages
  const packagesWithMetadata = await Promise.all(
    packages.map(async (pkg) => {
      try {
        const response = await fetch(`http://127.0.0.1:11436/polly/packages/metadata/${pkg.package_name}`);
        if (response.ok) {
          const metadata = await response.json();
          return { ...pkg, metadata };
        }
      } catch (error) {
        console.error(`Error fetching metadata for ${pkg.package_name}:`, error);
      }
      return { ...pkg, metadata: null };
    })
  );

  // Create dialog HTML
  const dialogHTML = `
    <div id="package-approval-dialog" class="modal">
      <div class="modal-content" style="max-width: 600px;">
        <div class="modal-header">
          <h3>🔐 Package Approval Required</h3>
          <button class="modal-close" id="close-package-approval">&times;</button>
        </div>
        <div class="modal-body">
          <p style="margin-bottom: 16px; color: var(--text-secondary);">
            The following packages were detected in generated code and require your approval:
          </p>
          
          <div id="package-approval-list" style="max-height: 400px; overflow-y: auto;">
            ${packagesWithMetadata.map((pkg, index) => `
              <div class="package-approval-item" data-approval-id="${pkg.approval_id}" style="
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 12px;
                background: var(--bg-secondary);
              ">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                  <div>
                    <h4 style="margin: 0 0 4px 0; font-size: 18px; color: var(--text-primary);">
                      ${pkg.package_name}
                    </h4>
                    ${pkg.metadata?.description ? `
                      <p style="margin: 0; color: var(--text-secondary); font-size: 14px;">
                        ${pkg.metadata.description}
                      </p>
                    ` : ''}
                  </div>
                  ${pkg.metadata?.context7_trust_score ? `
                    <div style="
                      background: ${pkg.metadata.context7_trust_score >= 7 ? 'rgba(34, 197, 94, 0.1)' : 'rgba(234, 179, 8, 0.1)'};
                      color: ${pkg.metadata.context7_trust_score >= 7 ? '#22c55e' : '#eab308'};
                      padding: 4px 12px;
                      border-radius: 12px;
                      font-size: 12px;
                      font-weight: 600;
                    ">
                      Trust: ${(pkg.metadata.context7_trust_score * 10).toFixed(0)}/10
                    </div>
                  ` : ''}
                </div>
                
                ${pkg.metadata ? `
                  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px; font-size: 12px; color: var(--text-secondary);">
                    ${pkg.metadata.version ? `
                      <div>
                        <strong>Version:</strong> ${pkg.metadata.version}
                      </div>
                    ` : ''}
                    ${pkg.metadata.author ? `
                      <div>
                        <strong>Author:</strong> ${pkg.metadata.author}
                      </div>
                    ` : ''}
                    ${pkg.metadata.homepage ? `
                      <div style="grid-column: 1 / -1;">
                        <strong>Homepage:</strong> 
                        <a href="${pkg.metadata.homepage}" target="_blank" style="color: var(--link-color);">
                          ${pkg.metadata.homepage}
                        </a>
                      </div>
                    ` : ''}
                  </div>
                ` : `
                  <div style="margin-top: 12px; padding: 8px; background: rgba(234, 179, 8, 0.1); border-radius: 4px; font-size: 12px; color: var(--text-secondary);">
                    ⚠️ Metadata not available
                  </div>
                `}
                
                <div style="margin-top: 12px; display: flex; gap: 8px;">
                  <label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 14px;">
                    <input type="checkbox" class="package-permanent-checkbox" data-approval-id="${pkg.approval_id}" style="cursor: pointer;">
                    <span>Add to allowlist (permanent approval)</span>
                  </label>
                </div>
              </div>
            `).join('')}
          </div>
          
          <div id="package-approval-error" class="error-message hidden" style="
            margin-top: 12px;
            padding: 8px;
            background: rgba(239, 68, 68, 0.1);
            border-left: 3px solid #ef4444;
            color: #ef4444;
            border-radius: 4px;
          "></div>
        </div>
        <div class="modal-footer" style="display: flex; justify-content: space-between; align-items: center;">
          <button class="btn btn-secondary" id="deny-all-packages">
            Deny All
          </button>
          <div style="display: flex; gap: 8px;">
            <button class="btn btn-secondary" id="cancel-package-approval">
              Cancel
            </button>
            <button class="btn btn-primary" id="approve-all-packages">
              Approve All
            </button>
          </div>
        </div>
      </div>
    </div>
  `;

  // Remove existing dialog if present
  const existing = document.getElementById('package-approval-dialog');
  if (existing) {
    existing.remove();
  }

  // Add to DOM
  document.body.insertAdjacentHTML('beforeend', dialogHTML);

  const dialog = document.getElementById('package-approval-dialog');
  const closeBtn = document.getElementById('close-package-approval');
  const cancelBtn = document.getElementById('cancel-package-approval');
  const approveAllBtn = document.getElementById('approve-all-packages');
  const denyAllBtn = document.getElementById('deny-all-packages');
  const errorDiv = document.getElementById('package-approval-error');

  // Show dialog
  dialog.classList.remove('hidden');

  // Close handlers
  const closeDialog = () => {
    dialog.classList.add('hidden');
    setTimeout(() => dialog.remove(), 300);
  };

  closeBtn.addEventListener('click', closeDialog);
  cancelBtn.addEventListener('click', closeDialog);

  // Approve all handler
  approveAllBtn.addEventListener('click', async () => {
    try {
      errorDiv.classList.add('hidden');
      approveAllBtn.disabled = true;
      approveAllBtn.textContent = 'Approving...';

      // Get permanent checkboxes
      const permanentCheckboxes = dialog.querySelectorAll('.package-permanent-checkbox');
      
      for (const pkg of packagesWithMetadata) {
        const checkbox = Array.from(permanentCheckboxes).find(
          cb => cb.dataset.approvalId === pkg.approval_id
        );
        const permanent = checkbox?.checked || false;

        // Call approve callback
        if (onApprove) {
          await onApprove(pkg.approval_id, permanent);
        } else {
          // Default: call API
          const response = await fetch(
            `http://127.0.0.1:11436/polly/capabilities/approve/${pkg.approval_id}`,
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ permanent })
            }
          );

          if (!response.ok) {
            throw new Error(`Failed to approve ${pkg.package_name}`);
          }

          // If permanent, also add to package allowlist
          if (permanent) {
            await fetch('http://127.0.0.1:11436/polly/packages/approve', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ packages: [pkg.package_name], permanent: true })
            });
          }
        }
      }

      closeDialog();
      
      // Show success message
      if (window.showNotification) {
        showNotification(`Approved ${packagesWithMetadata.length} package(s)`, 'success');
      }
    } catch (error) {
      console.error('Error approving packages:', error);
      errorDiv.textContent = `Error: ${error.message}`;
      errorDiv.classList.remove('hidden');
      approveAllBtn.disabled = false;
      approveAllBtn.textContent = 'Approve All';
    }
  });

  // Deny all handler
  denyAllBtn.addEventListener('click', async () => {
    try {
      errorDiv.classList.add('hidden');
      denyAllBtn.disabled = true;
      denyAllBtn.textContent = 'Denying...';

      for (const pkg of packagesWithMetadata) {
        // Call deny callback
        if (onDeny) {
          await onDeny(pkg.approval_id, 'User denied all packages');
        } else {
          // Default: call API
          const response = await fetch(
            `http://127.0.0.1:11436/polly/capabilities/deny/${pkg.approval_id}`,
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ reason: 'User denied all packages' })
            }
          );

          if (!response.ok) {
            throw new Error(`Failed to deny ${pkg.package_name}`);
          }
        }
      }

      closeDialog();
      
      // Show message
      if (window.showNotification) {
        showNotification(`Denied ${packagesWithMetadata.length} package(s)`, 'info');
      }
    } catch (error) {
      console.error('Error denying packages:', error);
      errorDiv.textContent = `Error: ${error.message}`;
      errorDiv.classList.remove('hidden');
      denyAllBtn.disabled = false;
      denyAllBtn.textContent = 'Deny All';
    }
  });

  // Click outside to close
  dialog.addEventListener('click', (e) => {
    if (e.target === dialog) {
      closeDialog();
    }
  });
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { showPackageApprovalDialog };
}

// Make available globally
window.showPackageApprovalDialog = showPackageApprovalDialog;
