# Tier 2: Packaging & Permissions

**Status:** 📋 Not Started (0%)  
**Duration:** ~1 week  
**Prerequisites:** Tier 1 completion  
**Target Start:** March-April 2026

---

## Overview

Tier 2 focuses on packaging Polly for production deployment, ensuring proper permissions on macOS, and polishing the user interface for consistency. This tier prepares Polly for distribution to end users.

**Purpose:** Transform development build into production-ready, distributable application

---

## Phases in This Tier

### Phase 9: macOS Permissions 📋
**Status:** Not started  
**Priority:** HIGH  
**Estimated Effort:** 2-3 days  
**Depends On:** Tier 0 (Electron app)

**Scope:**

**Permission Types Needed:**
1. **File System Access:**
   - Full Disk Access (for reading notes across filesystem)
   - Documents folder access
   - Downloads folder access
   
2. **Notification Permissions:**
   - Desktop notifications for system events
   - Badge count for new messages

3. **Accessibility Permissions (Optional):**
   - Global hotkeys for quick note capture
   - Text selection from other apps

**Implementation Tasks:**

1. **Info.plist Configuration:**
   - Add permission usage descriptions
   - Declare required entitlements
   - Set app category and identifiers

2. **Permission Request UI:**
   - Onboarding flow explaining why permissions needed
   - Step-by-step permission setup wizard
   - Visual guides showing where to enable permissions
   - "Open System Preferences" helper buttons

3. **Permission Checking:**
   - Runtime permission status checks
   - Graceful degradation if permissions denied
   - User-friendly error messages
   - Re-request flow if permissions revoked

4. **Entitlements Configuration:**
   - Hardened runtime entitlements
   - Sandbox exceptions if needed
   - Network client entitlement
   - File access entitlements

**Files to Create/Modify:**
- `electron-app/Info.plist` (permission descriptions)
- `electron-app/entitlements.plist` (entitlements)
- `electron-app/src/renderer/onboarding.js` (permission wizard)
- `electron-app/main.js` (permission checking)

**Testing:**
- Test on clean macOS install
- Verify permission prompts appear correctly
- Test graceful degradation
- Test permission revocation and re-request

**Documentation Needed:**
- User guide for enabling permissions
- Troubleshooting guide for permission issues
- Developer notes on entitlements

**Success Criteria:**
- [ ] All required permissions declared in Info.plist
- [ ] Permission wizard guides user through setup
- [ ] App functions correctly with permissions granted
- [ ] App degrades gracefully without permissions
- [ ] No security warnings on first launch
- [ ] Permission status visible in settings

**Impact:** Required for macOS distribution, professional user experience

---

### App Signing & Notarization 📋
**Status:** Not started  
**Priority:** HIGH  
**Estimated Effort:** 2-3 days  
**Depends On:** Phase 9 (permissions)

**Scope:**

**Code Signing:**
1. **Developer Certificate:**
   - Apple Developer account required ($99/year)
   - Developer ID Application certificate
   - Keychain setup and certificate management

2. **Signing Configuration:**
   - Configure electron-builder for signing
   - Sign all binaries and frameworks
   - Sign helper processes
   - Embed provisioning profile

3. **Hardened Runtime:**
   - Enable hardened runtime
   - Configure entitlements
   - Exception handling for legitimate use cases

**Notarization:**
1. **Build for Notarization:**
   - Create signed build
   - Package as DMG or PKG
   - Include all required entitlements

2. **Submit to Apple:**
   - Upload to Apple's notarization service
   - Wait for processing (minutes to hours)
   - Retrieve notarization ticket

3. **Staple Ticket:**
   - Staple notarization ticket to app
   - Verify stapling successful
   - Test installation on clean machine

**Distribution:**
1. **DMG Creation:**
   - Create drag-to-Applications DMG
   - Custom background image
   - Window size and icon positioning
   - License agreement

2. **Auto-Updater Setup:**
   - Configure electron-updater
   - Setup update server or use GitHub releases
   - Implement update checking logic
   - Update UI notifications

**Files to Create/Modify:**
- `electron-builder.yml` (signing config)
- `electron-app/entitlements.mac.plist`
- `electron-app/entitlements.mac.inherit.plist`
- `scripts/notarize.js` (notarization script)
- `scripts/build-release.sh` (build script)
- DMG background assets

**Required Accounts/Services:**
- Apple Developer account ($99/year)
- App-specific password for notarization
- Code signing certificate in Keychain

**Testing:**
- Test signed build on developer machine
- Test on clean macOS without developer tools
- Verify Gatekeeper accepts app
- Test auto-updater flow
- Test installation from DMG

**Success Criteria:**
- [ ] App signed with Developer ID certificate
- [ ] Hardened runtime enabled
- [ ] Notarization successful
- [ ] Gatekeeper accepts app without warnings
- [ ] DMG installer works smoothly
- [ ] Auto-updater functional
- [ ] No security warnings on first launch

**Impact:** Required for macOS distribution, user trust, App Store readiness

---

### UI Polish Sprint 📋
**Status:** Not started  
**Priority:** MEDIUM  
**Estimated Effort:** 1 week  
**Depends On:** Tier 1 completion

**Scope:**

**Consistency Pass:**
1. **Design System Audit:**
   - Verify all components use design system
   - Consistent spacing, colors, typography
   - Icon consistency (size, style, stroke width)
   - Button styles and states (hover, active, disabled)

2. **Component Updates:**
   - Update any pre-Phase 0.5 components
   - Ensure all modals use consistent style
   - Forms and inputs standardized
   - Error and success states consistent

**Animations & Transitions:**
1. **Micro-interactions:**
   - Button hover effects
   - Click feedback
   - Loading states
   - Success/error animations

2. **Page Transitions:**
   - Smooth page navigation
   - Fade in/out for modals
   - Slide animations for sidebars
   - Skeleton loaders for async content

3. **Performance:**
   - 60fps animations
   - GPU acceleration where appropriate
   - Avoid layout thrashing
   - Optimize repaint areas

**Accessibility:**
1. **Keyboard Navigation:**
   - All interactive elements reachable via Tab
   - Visible focus indicators
   - Logical tab order
   - Keyboard shortcuts for common actions

2. **Screen Reader Support:**
   - ARIA labels on all interactive elements
   - Semantic HTML structure
   - Alt text for images and icons
   - Status announcements for async operations

3. **Color Contrast:**
   - WCAG AA compliance minimum
   - Check all text/background combinations
   - Ensure UI elements distinguishable

**Visual Polish:**
1. **Empty States:**
   - Friendly illustrations or icons
   - Clear call-to-action
   - Helpful guidance text

2. **Loading States:**
   - Skeleton screens for content loading
   - Progress indicators for long operations
   - Animated spinners with appropriate timing

3. **Error States:**
   - Clear error messages
   - Suggested actions to resolve
   - Visual distinction from success states

4. **Tooltips & Help:**
   - Contextual help tooltips
   - Consistent tooltip styling
   - Info icons with explanations

**Responsive Design:**
1. **Window Sizing:**
   - Test at various window sizes
   - Minimum window size enforced
   - Layout adapts gracefully
   - Sidebar collapse on small windows

2. **Text Overflow:**
   - Long text truncates with ellipsis
   - Tooltips show full text on hover
   - Scrollable areas clearly indicated

**Quality Checks:**
1. **Cross-browser Testing:**
   - Test in Electron (Chromium)
   - Verify all features work

2. **Performance Testing:**
   - Page load times
   - Animation smoothness
   - Memory usage
   - CPU usage during idle

3. **User Testing:**
   - Gather feedback from beta users
   - Identify confusing UI elements
   - Test common workflows
   - Iterate based on feedback

**Files to Update:**
- All UI component files
- `/electron-app/src/renderer/styles/main.css`
- `/electron-app/src/renderer/components/*`
- Animation definitions

**Success Criteria:**
- [ ] All components use design system
- [ ] Animations smooth (60fps)
- [ ] Keyboard navigation complete
- [ ] Screen reader accessible
- [ ] WCAG AA compliant
- [ ] Empty/loading/error states polished
- [ ] Responsive to window resizing
- [ ] User feedback positive
- [ ] No visual glitches or bugs

**Impact:** Professional, polished product ready for users

---

## Tier 2 Architecture

### Deployment Pipeline

```
┌─────────────────────────────────────────┐
│     Development Build                    │
│  - npm run dev                          │
│  - Hot reload enabled                   │
│  - Debug tools accessible               │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│     Production Build                     │
│  - npm run build                        │
│  - Minification enabled                 │
│  - Source maps generated                │
│  - Debug tools disabled                 │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│     Code Signing (macOS)                │
│  - Sign with Developer ID cert          │
│  - Hardened runtime enabled             │
│  - Entitlements embedded                │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│     Notarization (macOS)                │
│  - Upload to Apple                      │
│  - Wait for approval                    │
│  - Staple ticket to app                 │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│     Package Creation                     │
│  - DMG for macOS                        │
│  - NSIS installer for Windows           │
│  - AppImage/deb for Linux               │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│     Distribution                         │
│  - Upload to GitHub Releases            │
│  - Update auto-updater manifest         │
│  - Generate release notes               │
└─────────────────────────────────────────┘
```

---

## Dependencies

**External Dependencies:**
- Apple Developer account ($99/year)
- Code signing certificate (Developer ID Application)
- Notarization service access (Apple)

**Build Tools:**
- electron-builder (packaging)
- electron-notarize (macOS notarization)
- electron-updater (auto-updates)

**Prerequisites:**
- Tier 0 complete (Electron app exists) ✅
- Tier 1 complete (features ready for users) 🔄

---

## Integration Points

**Phase 9 → Signing:**
- Permissions must be declared before signing
- Entitlements configured together

**Signing → Notarization:**
- Must sign before notarizing
- Entitlements affect notarization success

**UI Polish → All Features:**
- Polish applies to all Tier 1 features
- Consistency across entire app

**Tier 2 → Tier 3:**
- Packaging enables distribution
- Onboarding built in Tier 3 uses polished UI

---

## Platform-Specific Considerations

### macOS
- **Permissions:** Most complex, requires user education
- **Signing:** Required for Gatekeeper
- **Notarization:** Required for Gatekeeper (macOS 10.15+)
- **Distribution:** DMG standard, can also do PKG
- **Updates:** Auto-updater via GitHub releases or custom server

### Windows
- **Permissions:** Generally less restrictive
- **Signing:** Optional but recommended (Authenticode)
- **Distribution:** NSIS installer standard
- **SmartScreen:** Reputation builds over time
- **Updates:** Auto-updater via GitHub releases or custom server

### Linux
- **Permissions:** Varies by distro
- **Signing:** Not typically required
- **Distribution:** AppImage (universal), deb (Debian/Ubuntu), rpm (Fedora/RedHat)
- **Updates:** Package manager or AppImage auto-update

---

## Testing Strategy

**macOS Testing:**
1. Clean macOS VM or fresh install
2. Install app from DMG
3. Verify no Gatekeeper warnings
4. Test permission requests
5. Test all features with permissions
6. Test auto-updater

**Windows Testing:**
1. Clean Windows VM
2. Install from NSIS installer
3. Verify SmartScreen behavior
4. Test all features
5. Test auto-updater

**Linux Testing:**
1. Test on Ubuntu, Fedora, Arch
2. Test AppImage on multiple distros
3. Test deb/rpm packages
4. Verify dependencies

**Regression Testing:**
- All Tier 0 and Tier 1 features still work
- No performance degradation
- Signing doesn't break functionality

---

## Success Criteria

### Tier 2 Complete When:
- [ ] macOS permissions properly configured (Phase 9)
- [ ] Permission wizard guides users
- [ ] App signed with valid certificate
- [ ] App notarized by Apple
- [ ] Gatekeeper accepts app without warnings
- [ ] DMG installer polished and functional
- [ ] Auto-updater working on all platforms
- [ ] UI polish complete (animations, consistency, accessibility)
- [ ] All Tier 1 features still functional
- [ ] Performance meets targets
- [ ] Ready for beta distribution

---

## Known Challenges

**Apple Notarization:**
- Can take minutes to hours
- Rejection requires debugging and resubmission
- Entitlements can be tricky to configure

**Windows SmartScreen:**
- New apps flagged as potentially unsafe
- Reputation builds over time with downloads
- Code signing helps but doesn't eliminate

**Permissions Education:**
- Users may not understand why permissions needed
- Clear communication essential
- Support documentation critical

---

## Documentation Needed

**User Documentation:**
- Installation guide per platform
- Permission setup guide (macOS)
- Troubleshooting guide
- FAQ for common issues

**Developer Documentation:**
- Build process documentation
- Signing and notarization process
- Release checklist
- Update deployment process

**Support Documentation:**
- Common permission issues and fixes
- Gatekeeper troubleshooting
- SmartScreen troubleshooting

---

## Cost Analysis

**One-Time Costs:**
- Apple Developer account: $99/year
- Code signing certificate (Windows, optional): $100-300/year

**Ongoing Costs:**
- Renewal of certificates annually
- Build server/CI if using (optional)

**Time Investment:**
- Initial setup: 1 week
- Each release: 2-4 hours (build, sign, notarize, upload)
- Support for permission issues: Ongoing

---

## Timeline

**Week 1:**
- Days 1-2: Phase 9 (macOS Permissions)
- Days 3-4: Signing & Notarization
- Day 5: Testing and fixes

**Week 2 (if needed):**
- Days 1-5: UI Polish Sprint
- Test, iterate, polish

**Total:** 1-2 weeks depending on UI polish needs

---

## Next Steps After Tier 2

**Immediate:**
- Beta testing with real users
- Gather feedback
- Fix critical bugs

**Tier 3: Polish & Autonomy**
- Onboarding experience
- Data export and autonomy features

**Tier 4: Advanced Communication (Optional)**
- Email and calendar integration
- Progressive autonomy features

---

**Status:** 📋 TIER 2 NOT STARTED - Waiting for Tier 1 completion

**Prerequisites:** Complete Tier 1 (3-4 phases remaining)  
**Target Start:** March-April 2026  
**Target Completion:** April-May 2026
