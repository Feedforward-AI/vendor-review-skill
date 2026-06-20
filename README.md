# Feedforward Vendor Review

A Claude Code skill that evaluates AI-powered B2B SaaS vendors against Feedforward's six-dimension framework for independent AI capacity.

---

## The One Question

This skill exists to answer exactly one question about an AI-powered software vendor:

**Will adopting this vendor tool strengthen or weaken the organization's ability to build real, independent, generalizable AI capacity?**

Every score, sentence, and section serves that question. This is **NOT** a generic "is this good software?" review (Gartner / G2 / Forrester style). It is **NOT** a scorecard of security posture, pricing, support SLAs, or market share — except where those bear directly on capacity-building. It is **NEVER** a buy/don't-buy recommendation. The skill produces analysis that illuminates trade-offs; the executive makes the decision.

---

## The Six Dimensions

The Feedforward framework evaluates vendors across six dimensions of independent AI capacity:

| Code | Dimension | Core Question |
|------|-----------|---------------|
| **SEE** | Transparency | Can you see the AI's mechanics — system prompts, model choice, retrieval, parameters? |
| **CHANGE** | Customizability | Can you modify the AI layer — swap prompts and models, tune retrieval and parameters? |
| **ADAPT** | Vendor Agility | Does the vendor keep pace with the AI frontier, or lock you to one provider's orbit? |
| **USE** | Genuine Utility | Is the value real and differentiated, or commodity-model capability with a markup? |
| **LEARN** | Transferable Knowledge | Does daily use build portable, generalizable AI fluency, or only skill at this one tool? |
| **EXIT** | Portability | When you leave, does your institutional intelligence come with you, or is it trapped? |

---

## Install

**Step 1 — Add from the marketplace:**
```
/plugin marketplace add Feedforward-AI/vendor-review-skill
```

**Step 2 — Activate in your session:**
```
/plugin install vendor-review@feedforward
```

---

## Usage

### Basic evaluation

```
evaluate Glean
```

The skill runs a structured, six-stage pipeline: intake → evidence gathering → six dimension analyses → synthesis → drift check → structured report.

### Supply optional materials

Attach vendor pitch decks, demo transcripts, contract excerpts, or internal use-case notes when invoking. They are ingested as `user_supplied` evidence in the evidence pass.

```
evaluate Harvey  [attach: harvey-pitch-deck.pdf, contract-redline.docx]
```

### Supply optional org context

Provide your organization's current AI maturity, strategic constraints, or existing tooling. Org context is held separately from dimension scoring and is only folded in at the suitability line and Key Questions stage.

```
evaluate Glean  [org context: mid-market law firm, 200 lawyers, no in-house ML team]
```

### One-shot mode

If you want a full report without interactive clarification prompts, invoke with `--no-questions`:

```
evaluate Conveo --no-questions
```

### Vendor-response pass

After receiving the vendor's written response to the report's questions, feed it back for re-analysis:

```
vendor response for Glean  [attach: glean-response.pdf]
```

The skill re-runs the affected dimension analysts against the new evidence, produces a versioned updated report, and notes which scores changed and why.

---

## Framework Integrity

`reference/framework-core.md`, `reference/dimensions/*.md`, and `reference/drift-check.md` are **immutable law**. They must not be edited to soften opinions, lower thresholds, or accommodate vendor pushback. User input may correct evidence or supply organizational context, but may not change scores without evidence or override framework criteria. If you believe a criterion is wrong, raise it with Feedforward — do not silently alter the reference files.

---

## Technical Notes

- **Runtime scripts are stdlib-only.** `scripts/lint_report.py`, `scripts/eval_concordance.py`, and `scripts/render_report.py` use only Python standard library modules. No third-party dependencies are required to run the pipeline tooling.
- **Structured outputs.** All intermediate and final outputs conform to JSON schemas in `schemas/`. The report schema is `schemas/report.schema.json`.
- **Golden examples.** `examples/glean/`, `examples/harvey/`, `examples/conveo/`, and `examples/legora/` contain reference reports and expected scores for concordance evaluation.

---

## Testing

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

All unit tests cover schemas, rendering, linting, and concordance math. LLM-behavior stages are verified manually; see `docs/VERIFICATION.md`.
