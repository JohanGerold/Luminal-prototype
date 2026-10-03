# Approved frontend design lock

Approved by the user on 3 October 2026: the monochrome Luminal dashboard at checkpoint `cfb90fe`, originally `/design-assets/monochrome.html`. The user explicitly asked to lock this design and integrate it. This document supersedes every earlier lavender/plum design instruction, including `design-preview/DESIGN.md`. Preserve the monochrome direction across the working product.

- Palette: white surfaces, near-white canvas `#fcfcfc`, ink `#242527`, muted text `#737579`, pale borders `#e9e9eb`, neutral wash `#f6f6f7`. No lavender hero, plum navigation, decorative gradients or glowing shapes.
- Typography: locally hosted Manrope, modest weights (500–650), compact headings with restrained tracking. Primary page titles about 25px, panel headings 14px, readable operational text 11–13px. Monospace is reserved for file paths, IDs and recorded data.
- Layout: fixed 222px left sidebar, narrow 77px header and 34px content insets on desktop. Overview uses four compact metrics, an activity chart beside recent activity, then a wide scenario table. Detail pages retain this shell and use restrained evidence panels and paired before/after views.
- Spacing: 15–23px panel gaps, 17–24px panel padding, compact controls with generous separation between sections. Related labels and values stay together.
- Surfaces: flat white panels with 1px pale borders, 9px main radii, 4–6px badges/controls. Avoid heavy shadows, oversized pill buttons and a second theme.
- Controls: charcoal primary buttons with white text; thin outlined secondary controls; consistent 1.5px outline SVG icons. Visible keyboard focus and hover states. Native selects remain keyboard accessible.
- Navigation: neutral sidebar rows, a pale active row with a narrow dark left indicator. Mobile uses a menu button and hidden closed navigation, without invisible keyboard targets.
- Status: PASS uses muted green, FAIL muted red, UNCERTAIN muted amber; always include the word. Execution status remains separate from verdict. LIVE_MODEL uses a neutral solid outline; DEMO_FALLBACK uses a warm dashed outline and an explicit scripted-execution explanation. Unknown evidence must not use success icons.
- Charts: monochrome line/area charts, fine grid lines, a dashed passed series, text descriptions and focusable points. Plot only observed saved counts in the product. Empty history shows zero counts and no invented pass rate or duration.
- Motion: restrained control transitions, reduced-motion support, execution feedback driven only by recorded events. No theatrical progress implying unobserved work.
- Responsive behavior: stack metric/chart/detail groups as needed; wide results use a labelled, keyboard-scrollable region without page overflow. Preserve accessible labels and report/trace links.

Canonical implementation: `design-preview/assets/monochrome.css`, `product.css`, `templates/base.html`, `templates/dashboard.html`. Product scripts are `product.js`, `dashboard.js`, existing `start.js` and `run.js`. The original monochrome demo remains clearly illustrative and isolated. Never load `monochrome.js` or demo fixtures into the working application.

Data convention: dashboard metrics and chart share a selected LIVE_MODEL or DEMO_FALLBACK mode and 7/28-day window. Pass rate uses all evaluated outcomes (including UNCERTAIN), excludes pending results, and displays its denominator. Recent activity and latest-per-scenario rows are explicitly all-time for that mode. Do not present aggregate results as certification or fabricate V2 improvement.
