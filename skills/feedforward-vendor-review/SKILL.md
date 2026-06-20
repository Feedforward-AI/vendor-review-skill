---
name: feedforward-vendor-review
description: Evaluate an AI-powered software vendor (e.g. Glean, Harvey) against Feedforward's six-dimension framework — SEE, CHANGE, ADAPT, USE, LEARN, EXIT — to judge whether it strengthens or weakens the organization's independent, generalizable AI capacity. Use when asked to evaluate, review, or assess an AI vendor/tool for capacity, lock-in, or transparency. Produces a board-grade report. NOT a generic software review and NOT a buy/don't-buy recommendation.
---

# Feedforward Vendor Review — Orchestration Spine

This skill executes a structured, six-dimension evaluation of an AI-powered B2B SaaS vendor. It is **not** a generic software review and **never** produces a buy/don't-buy recommendation. The Feedforward framework is immutable: user input may correct evidence or add organizational context, but may not change scores without evidence or override framework criteria.

---

## Stage 0 — Intake & Scope Check

Before any analysis begins, confirm the evaluation target is appropriate for this framework.

1. **Target confirmation.** Ask (or infer from context) the specific vendor and product SKU being evaluated. If the product is ambiguous (e.g., multiple tiers or modules), clarify before proceeding.
2. **Framework eligibility.** Confirm the target is an AI-powered B2B SaaS product. If it is not AI-powered or not B2B SaaS, stop and explain that the Feedforward framework does not apply — do not force the evaluation.
3. **Optional user materials.** Accept any documents the exec wishes to supply (e.g., vendor pitch decks, demo transcripts, contract excerpts, internal use-case notes). Ingest them as `user_material` source evidence in Stage 1.
4. **Optional org context.** Accept any organizational context (e.g., current AI maturity, key strategic constraints, existing tooling). Org context is held separately and is only folded in at Stage 3 (suitability line + Key Questions) — it does not influence dimension scoring.

---

## Stage 1 — Evidence Pass

Build the evidence dossier conforming to `schemas/evidence-dossier.schema.json`.

**Research sources (in priority order):**
- Vendor documentation, API references, pricing pages, changelog/release notes
- Third-party coverage: analyst reports, customer reviews, security audits, press
- User-supplied materials (from Stage 0)

**Tagging requirements.** Every fact must be tagged with:
- `source_type` — one of: `vendor_docs` | `third_party` | `user_material` | `vendor_response`. The vendor's own product docs, API reference, pricing pages, and changelog are all `vendor_docs`; external analyst/practitioner/review coverage is `third_party`; materials supplied by the executive client are `user_material`; vendor answers ingested during a rebuttal pass are `vendor_response`.
- `evidence_strength` — one of: `verified` | `vendor_claim` | `inferred` | `informative_absence` | `user_provided`. A vendor's marketing assertion or unverifiable sales claim is `vendor_claim` (never promote it to `verified` without independent corroboration); a conspicuous, documented silence across all expected surfaces is `informative_absence`. Do NOT use strong / moderate / weak.
- `confidence` — one of: `high` | `medium` | `low`.

**Absence-as-evidence rule.** Per `reference/framework-core.md`: a vendor's failure to document a capability (e.g., no mention of export formats, no published API schema) is itself evidence that the capability does not exist or is intentionally obscured — record it as `evidence_strength: informative_absence`. Record absences explicitly; do not leave them blank.

---

## Stage 2 — Six Dimension Analysts

For each of the six dimensions — **SEE, CHANGE, ADAPT, USE, LEARN, EXIT** — spawn the `dimension-analyst` subagent (defined at `agents/dimension-analyst.md` at the plugin root).

**Per-dimension injection:**
- `reference/framework-core.md` — verbatim; provides universal scoring rules and the absence-as-evidence rule
- `reference/dimensions/<dim>.md` — verbatim; provides the dimension-specific criteria, indicators, and pass/fail thresholds (e.g., `reference/dimensions/see.md`, `reference/dimensions/change.md`, `reference/dimensions/adapt.md`, `reference/dimensions/use.md`, `reference/dimensions/learn.md`, `reference/dimensions/exit.md`)
- The evidence dossier from Stage 1

**Output requirement.** Each analyst must return a `dimension-result` conforming to `schemas/dimension-result.schema.json`. Required fields: `dimension`, `focus_area`, `score` (Pass / Partial / Fail / Insufficient), `assessment`, `trade_offs` (gain / give_up), `vendor_questions`, `confidence`, `evidence_basis`, `evidence_citations`.

**Concurrency.** Run all six analysts concurrently. Do not wait for one before starting the next.

---

## Stage 3 — Synthesis

Using `reference/synthesis/executive-summary.md`, `reference/synthesis/key-questions.md`, and `reference/output-template.md`, assemble the full report.

**Sections to produce:**

1. **Executive Summary** — per `reference/synthesis/executive-summary.md`:
   - KEY TAKEAWAY (one sentence; the single most important finding)
   - Overall sentiment (`positive` / `neutral` / `negative`)
   - Suitability line — the only place org context is folded in (e.g., "For an organization at early AI maturity with low lock-in tolerance, this vendor presents material risk on EXIT and SEE")

2. **Dimension Score Table** — SEE / CHANGE / ADAPT / USE / LEARN / EXIT with each dimension's focus area and score

3. **Trade-off Summary** — what the vendor does well vs. where it creates dependency or opacity

4. **Key Questions** — per `reference/synthesis/key-questions.md`: 5–6 STRATEGIC questions for the INTERNAL decision-maker/exec, NOT questions for the vendor. These help the reader determine whether this tool is right for their organization. Org context may sharpen them but does not manufacture questions not grounded in evidence gaps.

5. **Consolidated Vendor Questions** — the full list of `vendor_questions` from all six dimension results, deduplicated and prioritized. These are the vendor-facing questions (distinct from the internal Key Questions above).

**Output artifact.** Assemble `report.json` conforming to `schemas/report.schema.json`. This is the canonical artifact passed to subsequent stages.

---

## Stage 4 — Drift Check

Run the drift-check protocol defined in `reference/drift-check.md` (authoritative; this summary is subordinate to it).

The drift check is a **symmetric red-team** on two flanks:

- **Flank A — generic-review creep (too harsh / off-topic):** Flag and strip content that reads as a generic software review (security posture, pricing, market share, support SLAs, integration breadth, or "is it good software") unless tied to a dimension's capacity question. Flag any buy/don't-buy recommendation (the skill never makes one).
- **Flank B — false generosity (too soft on opacity):** Flag any dimension that buried a conspicuous, documented silence under "Insufficient Information" when the absence-as-evidence rule should instead drive a Fail/Partial (medium confidence) with a vendor question.
- **Immutability guard:** Confirm no user/vendor input overrode a criterion or a score-as-opinion. Scores may move ONLY because new evidence, run through the unchanged rubric, yields a different result.

If any dimension result fails either flank or the immutability guard, re-run the affected `dimension-analyst` subagent with the same inputs plus an explicit note of the drift flag. Emit all flags in the final `report.json` under `flags` (valid `type` values: `insufficient`, `informative_absence`, `unverified_claim`, `low_confidence`, `org_context_dependent`).

---

## Review Gate

**Non-blocking.** After Stage 4, present the draft report to the exec along with a concise "where your input would matter most" summary derived from the drift flags and open vendor questions.

**What the exec may do:**
- Correct **evidence** — supply a document, fact, or clarification that changes what is known about the vendor. Triggers a partial re-run of affected stages.
- **Answer open vendor questions** — if the exec has direct knowledge of a vendor answer, treat it as `user_material` evidence with `evidence_strength: user_provided`.
- Add or refine **org context** — updates the suitability line and Key Questions only; does not re-run dimension scoring.

**What the exec may NOT do:**
- Change a dimension score without supplying new evidence — decline this, note the client's disagreement in the Executive Summary prose, and hold the score on the evidence as scored. There is no structured `client_disagreement` field; the notation belongs in the executive summary paragraphs only.
- Override a framework criterion or dimension definition — the Feedforward framework is immutable. If the exec believes a criterion is wrong, note the disagreement but do not alter the analysis.

**Three operating modes:**

| Mode | Behavior |
|------|----------|
| `gated` (default) | Present draft; finalize on any non-corrective reply (e.g., "looks good", "proceed") |
| `one-shot` | Skip the review gate entirely; proceed directly to Stage 5 |
| `unattended` | Auto-finalize after approximately 10 minutes with no exec response (configurable via `review_gate_timeout_minutes`; default: 10). Useful for batch or overnight runs. |

On corrections, re-run only the affected stages. Do not re-run the full pipeline unless evidence changes touch more than three dimensions.

---

## Stage 5 — Render

Once `report.json` is finalized, render the deliverable artifacts.

**Step 1 — Render:**
```
scripts/render_report.py <report.json> <out_dir>
```
Produces:
- `report.md` — the board-grade narrative report in Markdown
- `report.html` — the standalone HTML version
- `questions.html` — the vendor questions page, suitable for sharing with the vendor

**Step 2 — Lint:**
```
scripts/lint_report.py <report.json>
```
The linter enforces tier-2 **semantic rules only** (schema conformance is guaranteed at generation time by structured outputs, not by the linter): dimension order (SEE→CHANGE→ADAPT→USE→LEARN→EXIT), 2–3 vendor questions per dimension, 2–4 sentence assessments, ≥1 evidence citation for any non-Insufficient score, `informative_absence` confidence capped at medium, and overview-table vs. detailed score alignment. **Fix all violations before delivering the report.** Do not deliver a report that fails linting.

---

## Vendor Rebuttal Loop

When the exec supplies vendor answers to the Key Questions or Consolidated Vendor Questions, re-enter the pipeline as a **vendor response pass**.

**Process:**
1. Ingest each vendor answer as evidence with `source_type: vendor_response`, then **adjudicate** it into one of five verdicts (this is an internal reasoning step — these verdict names are NOT schema field values): *substantive & verifiable*, *claim only*, *roadmap*, *non-responsive*, or *unanswered*. Record the resulting dossier fact with a valid `evidence_strength` enum value per the verdict: a verified substantive answer → `verified`; an unverifiable assertion (*claim only*) or a *roadmap*/future promise → `vendor_claim` (note roadmap items are not current capability); a *non-responsive* dodge → treat the documented silence as `informative_absence` where it confirms an undocumented affordance; an *unanswered* question → leave the gap open in `gaps`.
2. **Adjudication rule.** A dodge or non-responsive answer on a critical question can harden a Partial to Fail — silence is not neutral. A substantive, verifiable answer can upgrade a Fail or Partial if the evidence warrants it.
3. Re-run only the affected dimension analysts, then re-run synthesis and drift check.
4. Bump the minor version (e.g., v1.0 → v1.1) in `report.json`.
5. Populate the structured `report.changelog` array — each entry `{dimension, change, evidence}` — noting which scores changed, which remained unchanged despite vendor claims, and which questions remain open. `render_report.py` renders this as the "What changed after vendor response" section; do NOT add it as prose inside the executive summary.
6. Re-run `scripts/render_report.py` and `scripts/lint_report.py` to produce updated artifacts.
