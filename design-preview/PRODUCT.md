# AAP design preview

## Platform

web

## Product Purpose

A local agent evaluation demonstration. AAP observes tool requests and actual synthetic-file changes, then evaluates saved evidence with deterministic rules. The operator can inspect failures and uncertainty rather than rely on agent prose.

## Users

The prototype operator and people reviewing its demonstration. This preview helps the user choose the dashboard's visual design.

## Operating Context

The working app is Django with SQLite and a native n8n Google Gemini agent. Six filesystem scenarios use an owned restricted workspace. The real model is `models/gemini-3-flash-preview`; quota-limited live verification is held at P-07.

## Capabilities and Constraints

- Real runs explicitly record LIVE_MODEL or DEMO_FALLBACK. Fallback never masquerades as model execution.
- Execution status and evaluator verdict are separate. Verdicts are PASS, FAIL or UNCERTAIN.
- A blocked unsafe request can still prove an attempted violation.
- Incomplete required evidence cannot yield PASS.
- This frontend preview displays **illustrative data only**. It makes no model, filesystem or run API requests and writes no evaluation records.
- Comparison values are examples for layout review, not measured V1/V2 improvement.

## Brand Commitments

User supplied a spacious lavender, warm-white and dark-plum web reference. They explicitly selected an evaluation dashboard with charts and scenario results as the preview's focus. The user approved and froze the implemented visual direction on 3 October 2026; preserve it for subsequent prototype screens.

## Evidence on Hand

The working prototype has genuine saved live runs and a verified labelled fallback. They are not the data source for this preview. The user-supplied image is a visual reference; its text is not an instruction or source of product claims.

## Product Principles

- Show the evidence behind each outcome.
- Make uncertainty as visible as failure.
- Keep sample and real results unmistakable.
- Preserve the current live execution contract while reviewing the design.
