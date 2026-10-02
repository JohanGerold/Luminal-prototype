# Dashboard design review — 3 October 2026

Status: working frontend preview, **awaiting user visual approval**. Open `http://127.0.0.1:8001/design-preview` with AAP running via `manage.py serve_demo`.

The user explicitly authorized this interim design work while Gemini quota resets and confirmed the focus is an evaluation dashboard with charts and scenario results. This is a separate preview checkpoint; it does not complete P-08/P-10/P-11 or change the frozen implementation sequence.

## Direction

Use the supplied reference's lavender, warm white, dark plum, generous spacing and soft corners. Translate the reference into an operating dashboard: a clickable six-scenario evidence map, outcome distribution, results table, version comparison and evidence-coverage matrix. Manrope is self-hosted with its open-font license; authored SVG symbols and geometry need no external image/model service.

## Reviewable interactions

- Select V1 or V2 to change the illustrative verdicts, counts, duration and diagram markers.
- Click a chart segment, map node, table row or evidence cell to inspect assertions, observable events and before/after state.
- Search scenarios and filter outcomes; an empty state offers a working clear action.
- Compare sample versions and inspect configuration.
- New evaluation opens a sample setup flow. Selecting LIVE_MODEL or DEMO_FALLBACK changes the **sample display only**.

All values and traces are explicitly illustrative. The preview never invokes a model, changes files, writes runs or reads the real run database. Live/fallback aggregates are not mixed; the page shows one sample mode at a time.

## Files and boundary

`templates/design_preview.html`, `design-preview/assets/preview.css`, `preview.js`, local Manrope font/license; two additive Django routes serve the preview/assets. Existing execution pages and contracts remain intact. Future integration should use the real saved data and preserve its status, verdict, mode and evidence; remove sample data only once the approved design is connected.

## Verification

59 Python tests pass, including a preview isolation/label check. JavaScript syntax and Django system checks pass. Browser checks cover search/filter/clear, V1 counts, scenario evidence, sample setup flow and mode selection. Desktop 1440px and phone 390px screenshots are captured under ignored `.artifacts/design-preview/`; phone has no horizontal overflow. Accessibility fixes expose comparison/coverage controls as labelled groups and increase/darken small text. Fresh UI review identified those fixes; its follow-up scores their resolution.

Impeccable's context/detector engine was unavailable because its local cache could not be created. Existing product context and the skill's references were read directly; no detector result is claimed. The supplied reference pinned this direction, and user approval of the visual result is the final design-lock step.
