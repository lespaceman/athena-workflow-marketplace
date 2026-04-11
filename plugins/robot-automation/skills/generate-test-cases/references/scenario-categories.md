# Scenario Categories — Detailed Checklists

These checklists support Step 4 of the generate-test-cases skill. Each category covers scenarios that may not be directly triggerable during browser exploration but must be included in comprehensive test specifications.

## Network & Performance

- Network failure during form submission (mock 500, abort request)
- Slow API response (loading states, skeleton screens, spinners)
- Large data sets (pagination, infinite scroll, 100+ items)
- Offline behavior (if PWA or service worker is present)

## Accessibility (WCAG 2.1 AA)

- Keyboard-only navigation through the entire flow (Tab, Enter, Escape)
- Screen reader announcements for dynamic content (ARIA live regions)
- Focus management after modal open/close, page transitions
- Color contrast for error states and disabled elements
- Form error association (`aria-describedby` linking errors to fields)

## Visual Consistency

- Layout stability (no unexpected content shifts after load)
- Responsive behavior at standard breakpoints (mobile 375px, tablet 768px, desktop 1280px)
- Dark mode rendering if supported

## Cross-browser Considerations

- Safari/WebKit-specific behavior (date inputs, smooth scrolling, storage quirks)
- Firefox form validation differences
- Mobile browser touch targets and gestures

## Concurrent & Session

- Session expiry mid-flow (cookie cleared during multi-step)
- Concurrent access (two tabs, same user)
- Race conditions (double-click submit, rapid navigation)
