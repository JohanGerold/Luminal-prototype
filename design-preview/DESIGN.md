---
name: AAP isolated design preview
description: Approved lavender and plum evaluation dashboard baseline; preview data remains illustrative.
colors:
  paper: "#fcfcfa"
  white: "#fff"
  canvas: "#e9e7ee"
  ink: "#2d293d"
  muted: "#6c677c"
  plum: "#302940"
  lavender: "#ece9f5"
  violet: "#766293"
  line: "#e9e6ee"
  pass: "#618071"
  pass-soft: "#e4ede7"
  fail: "#a9604e"
  fail-soft: "#f5e5de"
  uncertain: "#7b6a9a"
  uncertain-soft: "#eee8f5"
typography:
  display:
    fontFamily: "Manrope, Arial, sans-serif"
    fontSize: "49px"
    fontWeight: 500
    lineHeight: 1.12
    letterSpacing: "-.04em"
  headline:
    fontFamily: "Manrope, Arial, sans-serif"
    fontSize: "26px"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-.035em"
  title:
    fontFamily: "Manrope, Arial, sans-serif"
    fontSize: "19px"
    fontWeight: 550
    lineHeight: 1.4
    letterSpacing: "-.025em"
  body:
    fontFamily: "Manrope, Arial, sans-serif"
    fontSize: "14px"
    lineHeight: 1.5
    fontFeature: "ss01"
  label:
    fontFamily: "Manrope, Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 600
rounded:
  panel: "16px"
  field: "8px"
  pill: "30px"
  badge: "5px"
spacing:
  grid-gap: "20px"
  panel-padding: "27px 28px"
  page-inset: "46px"
components:
  button-primary:
    backgroundColor: "{colors.plum}"
    textColor: "{colors.white}"
    rounded: "{rounded.pill}"
    typography: "{typography.label}"
    padding: "10px 19px"
    height: "43px"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    typography: "{typography.label}"
    padding: "10px 19px"
  panel:
    backgroundColor: "{colors.white}"
    rounded: "{rounded.panel}"
    padding: "{spacing.panel-padding}"
  search:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.field}"
    height: "36px"
    padding: "0 11px"
  verdict-pass:
    backgroundColor: "{colors.pass-soft}"
    textColor: "#476650"
    rounded: "{rounded.badge}"
    padding: "4px 7px"
---

# Design System: AAP isolated design preview

## Overview

**Status: APPROVED AND LOCKED by the user on 3 October 2026. This implemented preview supplies the visual baseline for subsequent prototype screens; data remains illustrative. See ../docs/DESIGN_LOCK.md.**

The implemented direction translates the user's single BloomFi screenshot reference into lavender surfaces, warm white space and dark plum emphasis. Manrope, generous spacing and soft corners give the evaluation dashboard a calm, approachable character. This records the build, without assigning an unapproved creative North Star.

**Key Characteristics:**
- Tonal lavender layering with restrained plum emphasis.
- Soft panels and pill actions surrounding compact evidence data.
- Distinct verdict colors paired with visible labels.

Source: `assets/preview.css` and `../templates/design_preview.html`, with scope established by `PRODUCT.md` and `../docs/UI_DESIGN_PREVIEW.md`. Impeccable's detector engine was unavailable; no detector validation is claimed.

## Colors

### Primary

Plum anchors main actions and the dark explanatory panel; violet marks keyboard focus. Lavender supplies quiet secondary surfaces and interactions. The hero uses an authored lavender gradient, recorded in the sidecar rather than promoted to a general color token.

### Neutral

Canvas frames the warm paper application shell. White panels sit above paper; ink carries principal text, muted carries supporting text, and line separates panels and table rows.

Pass, fail and uncertain are semantic families, each with a soft background. Charts use lighter, context-specific tints. These indicate evaluation verdicts, while execution status remains separately labelled.

## Typography

The self-hosted Manrope variable font uses Arial and sans-serif fallbacks. Large headings have modest weight and tight tracking; dense evidence uses smaller text and tabular numerals where implemented.

Frontmatter describes the desktop hero, page title, panel title, body and button label roles. Evidence table text is (12px), navigation (13px), and supporting copy generally (11–13px), after the final readability overrides. The hero steps through (46px), (40px), and (34px), then (39px) when it stacks on phones. These are observed responsive values, not a uniform scale for future app screens.

## Layout

The shell caps at (1344px) with main content inset (46px). Main summary columns use a (1.7:1) split, lower panels (1.2:1), and a repeated grid gap (20px). Hero copy and its evidence map share two columns. White panels use the frontmatter padding; narrower views reduce it to (23px) or (20px).

At (820px) navigation wraps below the header and lower panels stack. At (590px) the hero and summary stack, controls wrap and page insets become (20px). The compact table hides tool attempts below (820px), then execution and duration below (590px); the evidence dialog retains those details. The shell uses outside margins instead of a full-bleed dashboard.

## Elevation & Depth

Most data panels use a thin line border and tonal separation. The hero's circular hub and orbit nodes have soft ambient shadows; primary actions gain a small hover shadow. Dialogs use a larger shadow over a translucent blurred backdrop. Exact shadows and the hero gradient are in the sidecar.

## Shapes

Broad panels and dialogs share the panel radius. Fields use the smaller field radius, action buttons use pills, and verdict badges have compact corners. Circular icon controls and the circular evidence hub are local component shapes. The orbit map is an authored preview illustration, not a mandatory layout for other surfaces.

## Components

- **Buttons:** plum primary, outlined secondary and warm-white hero action. Primary hover lightens plum and adds a soft shadow; secondary hover adds lavender. Text actions underline on hover. Phone new-evaluation becomes a circular icon control while retaining its accessible name.
- **Search and selects:** white, line border, compact field radius. Search gets a violet outline on focus within; buttons, links and native controls use a violet focus-visible outline with (4px) offset.
- **Navigation:** medium-weight text with muted inactive items; active plum text carries a short underline. Navigation wraps to its own row on smaller widths.
- **Verdict badges:** soft semantic fill, stronger semantic text and an inline SVG cue. PASS, FAIL and UNCERTAIN remain visible in words.
- **Panels:** white with a thin line border, soft corners and no resting shadow; the explanatory panel uses plum with lighter text.
- **Evidence interactions:** chart segments, orbit nodes, coverage cells and table inspection buttons open the same evidence dialog. Charts retain labelled groups; decorative SVG geometry stays separate from control names.
- **Dialogs:** warm paper, constrained viewport width, scrollable at (90vh); phone uses (90dvh). The backdrop blurs, and small circular close controls show keyboard focus.

## Do's and Don'ts

- **Do** retain visible sample labels on preview results and comparisons.
- **Do** pair verdict colors with text and keep execution status distinct from verdict.
- **Do** preserve keyboard focus and reduced-motion behavior when reusing preview components.
- **Don't** redesign the approved prototype visual baseline.
- **Don't** infer real reliability gains from the illustrative version comparison.
