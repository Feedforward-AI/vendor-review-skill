---
name: feedforward-vendor-review
description: Evaluate an AI-powered B2B SaaS vendor against Feedforward's six-dimension framework - SEE, CHANGE, ADAPT, USE, LEARN, EXIT - to judge whether it strengthens or weakens the organization's independent, generalizable AI capacity. Use when asked to evaluate, review, reassess, or run a vendor-response pass for an AI vendor/tool, especially for capacity-building, lock-in, transparency, portability, or board-grade vendor analysis. Not a generic software review and not a buy/don't-buy recommendation.
---

# Feedforward Vendor Review

Use this skill to produce a structured, evidence-backed vendor review for AI-powered B2B SaaS products. Keep the one question in view throughout: will adopting this vendor tool strengthen or weaken the organization's ability to build independent, generalizable AI capacity?

This is a platform-neutral Agent Skill. Treat all paths below as relative to this skill folder. Do not rely on host-specific plugin manifests, slash commands, or root-level agent files.

## Bundled Resources

- `references/framework-core.md`: authoritative scoring law, scoring vocabulary, and absence-as-evidence rule. Read before scoring.
- `references/dimensions/{see,change,adapt,use,learn,exit}.md`: dimension-specific rubrics. Read only the dimension file needed for each dimension pass.
- `references/dimension-analyst.md`: protocol for a single-dimension analyst pass. Use it directly, or pass it to a subagent if a multi-agent tool is available.
- `references/synthesis/*.md`, `references/output-template.md`, `references/drift-check.md`: synthesis, review gate, key questions, and drift-check rules.
- `schemas/*.schema.json`: structured output contracts for the evidence dossier, dimension results, vendor questions, and final report.
- `scripts/render_report.py`: render finalized `report.json` into Markdown and HTML deliverables.
- `scripts/lint_report.py`: semantic linter for finalized `report.json`.
- `scripts/eval_concordance.py` and `examples/*/expected-scores.json`: optional concordance checks against golden examples.
- `assets/report-template.html`: HTML template used by the renderer.

## Stage 0 - Intake And Scope

Confirm or infer the vendor and product SKU. Clarify if the target could mean multiple products, plans, or modules.

Proceed only for AI-powered B2B SaaS products. If the product is not AI-powered or not B2B SaaS, stop and explain that the Feedforward framework does not apply.

Accept optional user materials such as vendor decks, demo transcripts, contracts, security notes, or internal use-case notes. Treat these as `source_type: user_material`.

Accept optional org context such as AI maturity, strategic constraints, existing tooling, and lock-in tolerance. Hold org context separately. It may affect only the suitability line and internal Key Questions, not dimension scores.

Support three modes:

| Mode | Trigger | Behavior |
| --- | --- | --- |
| `gated` | default | Present draft after drift check and finalize on any non-corrective reply. |
| `one-shot` | `--no-questions`, "skip clarification", or equivalent | Skip the review gate and render final artifacts. |
| `unattended` | explicit unattended/batch request | Auto-finalize after approximately 10 minutes without user response. |

## Stage 1 - Evidence Pass

Build an evidence dossier conforming to `schemas/evidence-dossier.schema.json`.

Research in this priority order:

1. Vendor documentation, API references, admin docs, pricing pages, release notes, changelogs, security docs, and public product docs.
2. Third-party coverage such as analyst reports, customer reviews, practitioner writeups, audits, and credible press.
3. User-supplied materials.

For current vendor facts, browse or otherwise verify against current sources. Do not rely on stale model memory for product capabilities, pricing, API surface, model support, export functionality, or release status.

Tag every fact with:

- `source_type`: `vendor_docs`, `third_party`, `user_material`, or `vendor_response`.
- `evidence_strength`: `verified`, `vendor_claim`, `inferred`, `informative_absence`, or `user_provided`.
- `confidence`: `high`, `medium`, or `low`.

Apply the absence-as-evidence rule from `references/framework-core.md`. A conspicuous absence is evidence only when expected surfaces were checked and named. Cap `informative_absence` confidence at `medium` and raise a confirming vendor question. If expected surfaces were not checked, record a gap instead.

## Stage 2 - Dimension Passes

Produce one `dimension-result` for each dimension in this order: SEE, CHANGE, ADAPT, USE, LEARN, EXIT.

For each pass, use:

- `references/framework-core.md`
- `references/dimensions/<dimension>.md`
- `references/dimension-analyst.md`
- the evidence dossier from Stage 1
- `schemas/dimension-result.schema.json`

Keep dimension passes isolated. If a multi-agent or subagent tool is available, run the six dimension passes concurrently and provide each worker only the relevant dimension rubric plus the shared framework, evidence dossier, analyst protocol, and schema. If no such tool is available, run the six passes serially, but do not let later dimensions revise earlier scores without new evidence.

Each dimension result must include `dimension`, `focus_area`, `score`, `assessment`, `trade_offs`, `vendor_questions`, `confidence`, `evidence_basis`, and `evidence_citations`. Use only `Pass`, `Partial`, `Fail`, or `Insufficient` for scores.

## Stage 3 - Synthesis

Assemble `report.json` conforming to `schemas/report.schema.json`. Use `references/synthesis/executive-summary.md`, `references/synthesis/key-questions.md`, and `references/output-template.md`.

Include:

1. Executive Summary with a one-sentence key takeaway, overall sentiment, and a suitability line. Fold org context into the suitability line only.
2. Dimension Score Table for SEE, CHANGE, ADAPT, USE, LEARN, EXIT.
3. Trade-off Summary describing what the vendor gives and what the organization gives up.
4. Key Questions: 5-6 strategic internal questions for the executive decision-maker, not vendor-facing questions.
5. Consolidated Vendor Questions: deduplicated and prioritized vendor-facing questions from all dimension results.

Do not produce a buy/don't-buy recommendation. The skill illuminates trade-offs; the executive makes the decision.

## Stage 4 - Drift Check

Run `references/drift-check.md` before presenting or rendering the final report.

Check both flanks:

- Generic-review creep: remove unsupported discussion of security posture, pricing, market share, support SLAs, integration breadth, or "good software" unless tied to a dimension's capacity question.
- False generosity: flag cases where conspicuous documented silence was softened into `Insufficient` instead of treated as `informative_absence`.

Also enforce the immutability guard: user or vendor input may correct evidence, but may not override criteria or move a score without new evidence processed through the unchanged rubric.

If drift affects a dimension, re-run only the affected dimension pass with the same inputs plus the drift finding. Emit drift findings in `report.json` under valid `flags` entries.

## Review Gate

In `gated` mode, present the draft after Stage 4. Lead with: "the report is ready to finalize". If flags or open high-impact vendor questions remain, ask: "a few areas would be sharper with more info; do you have any of the following?" Then list 3-6 highest-impact asks with dimension labels.

The executive may correct evidence, answer open vendor questions from direct knowledge, or refine org context. Re-run only affected stages. The executive may not change a score by preference, override a criterion, or force a buy/don't-buy conclusion.

Any non-corrective reply finalizes the report as-is.

## Stage 5 - Render And Lint

After finalizing `report.json`, render deliverables:

```bash
python3 scripts/render_report.py <report.json> <out_dir>
```

This produces `report.md`, `report.html`, and `questions.html`.

Then run:

```bash
python3 scripts/lint_report.py <report.json>
```

Fix all lint violations before delivery. Do not deliver a report that fails linting.

## Vendor Response Pass

When the executive supplies vendor answers, treat the new material as a vendor-response pass.

Ingest each answer with `source_type: vendor_response`. Adjudicate it internally as substantive and verifiable, claim only, roadmap, non-responsive, or unanswered. Convert that adjudication into valid dossier fields: verified substantive evidence becomes `verified`; unverifiable claims and roadmap promises become `vendor_claim`; non-responsive answers may harden a documented silence into `informative_absence`; unanswered items remain gaps.

Re-run only affected dimension passes, then rerun synthesis and drift check. Bump the minor report version and populate the report changelog with dimension, change, and evidence entries. Render and lint again.
