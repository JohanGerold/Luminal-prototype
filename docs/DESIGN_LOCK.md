# Approved frontend design lock

Approved by the user on 3 October 2026. Baseline: dashboard implemented at checkpoint `d91e067`, available at `/design-preview`. Preserve this visual direction when implementing real reports and missing screens; sample data remains illustrative until connected to saved evidence.

- Palette: warm paper (#fcfcfa), white, muted canvas (#e9e7ee), lavender (#ece9f5), dark plum (#302940), ink (#2d293d). Reuse semantic pass/fail/uncertain colors and visible labels from the existing CSS.
- Typography: self-hosted Manrope, modest heading weights, tight heading tracking; compact readable supporting text. Preserve the implemented responsive sizes.
- Spacing: generous outer whitespace and page insets, repeated 20px grid gaps, restrained dense evidence rows. Narrow screens stack existing groups.
- Surfaces: white/paper panels with thin subdued borders; lavender hero and plum explanatory panel. Preserve intentional evidence-map geometry and existing tonal treatment.
- Corners: 16px major panels, 8px fields, pill buttons, compact verdict badges. Reuse existing component styles rather than framework defaults.
- Layouts: horizontal header/navigation, two-column hero, asymmetric summary, scenario ledger, comparison and evidence coverage, shared evidence dialogs. Preserve the established hierarchy; new screens should reuse these patterns where relevant.
- Controls: plum primary actions, outlined secondary actions, white hero action; consistent icons, focus rings, search and native selects.
- Navigation: text links with a short active underline, wrapping below the header on narrow screens.
- Status: labelled semantic verdict colors; execution status stays separate. LIVE_MODEL and DEMO_FALLBACK must remain explicit. Never render illustrative comparisons as observed improvement.
- Motion: retain restrained hover/focus transitions and reduced-motion support. Execution motion may communicate real progress; it must not imply unobserved work.

Do not introduce a second theme, generic SaaS or bento layout, glassmorphism, glowing blobs, new purple/blue AI gradients, typography replacement, radical radius changes, or aesthetic page restructuring. Preserve functionality with the smallest necessary visual adjustment. Accessibility, responsive fixes and loading/error/empty states are permitted within this baseline.

Sources: `../design-preview/DESIGN.md`, `../design-preview/assets/preview.css`, `../templates/design_preview.html`. This records existing approved styling; it introduces no visual changes.
