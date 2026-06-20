# Feedforward Vendor Review Skill — Design Spec

**Date:** 2026-06-20
**Status:** Design approved; pending spec review → implementation planning
**Owner:** Adam Davidson (Feedforward)
**Skill name (working):** `feedforward-vendor-review`

---

## 1. The one question

This skill exists to answer a single question about an AI-powered software vendor:

> **Will adopting this vendor tool strengthen or weaken the organization's ability to build real, independent, *generalizable* AI capacity?**

Every score, sentence, and section serves that question. The governing assumption (from `vendor_system_prompt.md`): foundation models are now commodity, so a vendor's durable incentive is to manufacture lock-in — proprietary formats, opaque mechanics, tool-specific skill — and a quick productivity win can quietly buy that lock-in at the cost of the organizational AI fluency that matters far more over a 3–10 year horizon.

The skill is an **analyst, not a decision-maker**. It illuminates trade-offs; the executive decides.

### Non-goals (what this is deliberately NOT)

- Not a generic "is this good software?" review (Gartner / G2 / Forrester style).
- Not a scorecard of security posture, pricing tiers, support SLAs, market share, or integration breadth — *except* where those bear directly on capacity-building.
- Not a buy / don't-buy recommendation.

The single largest design risk is **drift**: an LLM that sees "evaluate a vendor" reaches for the standard rubric. Defeating that drift is the organizing principle of the entire design (see §10).

---

## 2. The framework (immutable)

Six dimensions, each a probe of the same capacity question. Report order tells a story: visibility and control of the AI layer → the vendor's pace → the honest utility floor → your people's fluency → the lock-in tax.

| Code | Dimension | The capacity question it probes |
|---|---|---|
| **SEE** | Transparency | Can you see the AI mechanics — prompts, models, RAG, params — or is it a black box? |
| **CHANGE** | Customizability | Can you control those mechanics, or are you locked to the vendor's one-size config? |
| **ADAPT** | Vendor Agility | Does the vendor keep pace with the frontier, or are you bet on one provider's orbit? |
| **USE** | Genuine Utility | Is the value real and differentiated, or commodity-model capability with a markup? |
| **LEARN** | Transferable Knowledge | Does daily use build portable AI fluency, or only skill at operating this one UI? |
| **EXIT** | Portability | When you leave, does your institutional intelligence come with you, or is it trapped? |

**Scoring vocabulary (fixed):** `Pass` · `Partial` · `Fail` · `Insufficient Information`. Default to `Insufficient Information` when uncertain (but see the informative-absence rule in §7). In schemas the enum value is the short token `Insufficient`; the renderer maps it to the display label "Insufficient Information."

**Critical rules (load-bearing, from `vendor_system_prompt.md`):**
1. Default to `Insufficient Information` when uncertain — never infer or speculate to fill a gap.
2. Marketing claims are not evidence — vendor-asserted metrics are flagged unverified, never logged as a "pro."
3. Frame every gap as a question for the vendor.
4. Trade-offs, not verdicts.
5. Tone: direct, declarative, conclusions-first, no corporate hedging. If something is a problem, call it a problem.

**Immutability principle (the product itself):** The framework's criteria, scoring methodology, and value judgments are fixed. User and vendor input may supply or correct *evidence* and add *org context for tailoring* — never override the criteria or the opinions. A score moves only when new evidence, run through the unchanged rubric, yields a different result.

---

## 3. Architecture

**One skill** that owns the immutable framework as data. `SKILL.md` orchestrates **six over-briefed dimension-analyst subagents** (optionally via a bundled deterministic Workflow) over a **shared evidence dossier**, followed by synthesis, a symmetric drift check, and rendering.

### Why one skill + subagents (not six skills)

"Skill" and "subagent" are orthogonal: a skill is reusable knowledge/procedure; a subagent is an isolated execution context. The separation we want (focus, parallelism) comes from **subagents**, not from skill-ifying each dimension. Six skills would fragment the opinions across six independently-drifting units and buy no isolation. So: one skill is the single source of truth for the framework; the six analyses are six subagent runs of one **analyst harness** (see §10, L2), each handed a different immutable rubric.

### Orchestration: SKILL.md-driven subagents (primary), deterministic Workflow (optional)

Because the skill ships through the Claude Code marketplace to executives who will not have the (gated) Workflow tool enabled, the **dependable primary path is `SKILL.md` orchestrating bundled `dimension-analyst` subagents** via the always-available Agent tool: evidence pass → spawn six analysts (parallel) → synthesis → drift check → render. The deterministic **Workflow script** is bundled as an **optional accelerator** (run-to-run consistency, a guaranteed drift gate) for power users and Feedforward-internal runs, invoked by `scriptPath` against the bundled file. Both paths use the same immutable rubrics, the same six-analyst structure, and the same schemas — only the driver differs. The analyst harness (§10, L2) is packaged as a bundled custom subagent type (`agents/dimension-analyst.md`).

### File layout

The skill is wrapped as a Claude Code plugin in a single self-hosting marketplace repo (see §18):

```
vendor-review-skill/                       ← GitHub repo = marketplace + plugin
├── .claude-plugin/
│   ├── marketplace.json          # marketplace name "feedforward", lists this plugin, source "./"
│   └── plugin.json               # plugin manifest (name, version, description, author, license)
├── agents/
│   └── dimension-analyst.md      # ★ the analyst harness as a bundled custom subagent type
├── skills/
│   └── feedforward-vendor-review/
│       ├── SKILL.md              # Spine: frontmatter name+description (trigger) + staged orchestration (Stage 0–5)
│       ├── reference/
│       │   ├── framework-core.md         # ★ IMMUTABLE — one question, philosophy, scoring, rules, tone
│       │   ├── dimensions/
│       │   │   ├── see.md  change.md  adapt.md
│       │   │   └── use.md  learn.md   exit.md   # ★ IMMUTABLE — one rubric per dimension
│       │   ├── synthesis/
│       │   │   ├── executive-summary.md  # KEY TAKEAWAY + sentiment + suitability spec
│       │   │   └── key-questions.md      # 5–6 strategic questions spec
│       │   ├── output-template.md        # canonical 7-section structure + scoring vocab
│       │   └── drift-check.md            # ★ the symmetric red-team checklist
│       ├── schemas/
│       │   ├── evidence-dossier.schema.json   dimension-result.schema.json
│       │   ├── report.schema.json             vendor-question.schema.json
│       ├── assets/
│       │   └── report-template.html      # styled cover + color-coded tables → print-to-PDF
│       ├── scripts/
│       │   ├── render_report.py          # report.json → report.md + report.html (stdlib only)
│       │   └── lint_report.py            # Tier-2 semantic validation (§11)
│       ├── workflow/
│       │   └── evaluate-vendor.workflow.js   # OPTIONAL deterministic fan-out accelerator
│       └── examples/                     # Glean / Harvey / Conveo / Legora golden references
├── README.md
└── LICENSE
```

The starred files (`framework-core.md`, the six rubrics, `drift-check.md`) are **read-only law**: injected verbatim into every analyst, never paraphrased. User input has exactly two doors in: (1) evidence → the dossier, (2) org context → synthesis tailoring. There is no third door to the criteria or the scores-as-opinion.

---

## 4. Pipeline & data flow

The **review gate is always an in-conversation step** (§8); the autonomous research-and-draft work runs around it. The pipeline therefore stages as Phase 1 (draft) → review gate → Phase 2 (partial re-run). The primary `SKILL.md` path runs these stages directly with subagents; the optional Workflow accelerator follows the identical staging but, because a workflow cannot be interactive mid-run, splits into two separate workflow invocations around the in-conversation gate.

```
EXECUTIVE: "evaluate <vendor>"  (+ optional materials, + optional org context)
   │
   ▼  PHASE 1 — DRAFT (autonomous)
   ├─ Stage 0 · Intake & scope check — is this AI-powered B2B SaaS? If not → stop & explain.
   ├─ Stage 1 · Evidence pass → EVIDENCE DOSSIER
   │     multi-modal sweep (parallel), dedup/merge into one dossier; every fact tagged
   │     source · evidence_strength (one of §5's five values) · confidence
   ├─ Stage 2 · Fan-out · SIX DIMENSION ANALYSTS (parallel) → 6× DIMENSION RESULT
   │     each = analyst harness (framework-core + its rubric, verbatim) + dossier + schema
   ├─ Stage 3 · Synthesis (barrier) → DRAFT REPORT
   │     Executive Summary (KEY TAKEAWAY + sentiment + suitability) · Trade-off Summary ·
   │     Key Questions — folds optional org context into suitability line + questions ONLY
   └─ Stage 4 · Drift / red-team check → CLEANED DRAFT + FLAGS
         strips generic creep AND false generosity; re-runs any slipped analyst; emits flags
   │
   ▼  REVIEW GATE (in conversation · non-blocking · auto-finalizes) — §8
   │    shows draft + "where your input would matter most"; exec may correct EVIDENCE,
   │    answer open vendor questions, or add org context. No engagement → finalize as-is.
   │
   ├─ (corrections) ─▶ PHASE 2 — partial re-run (only affected stages)
   │                     new evidence → affected analyst(s) → re-synthesize → re-drift-check
   │                     org context only → re-synthesize
   └─ (no engagement / "looks good")
   │
   ▼  Stage 5 · RENDER → report.md (canonical) + report.html (styled, print-to-PDF)
```

---

## 5. Data model

All schemas are authored to the structured-outputs supported subset and complexity limits (see §11). Every field `required`; `additionalProperties: false`; controlled vocabularies as `enum`; empties expressed with sentinels (`"—"`, `""`, `[]`) rather than optional/nullable fields.

### Evidence dossier (shared ground truth)

```jsonc
{
  "vendor":      { "name", "url", "category" },
  "scope_check": { "is_ai_b2b_saas": true, "rationale" },
  "facts": [{
     "id", "claim",
     "dimensions": ["SEE","EXIT"],                       // enum array, which probes it bears on
     "source_type": "vendor_docs|third_party|user_material|vendor_response",
     "source_ref", "quote",                              // "" if none
     "evidence_strength": "verified|vendor_claim|inferred|informative_absence|user_provided",
     "expectation_set": "",                              // surfaces checked; "" unless informative_absence
     "confidence": "high|medium|low"
  }],
  "gaps": [{ "dimension", "missing", "suggested_vendor_question" }]
}
```

`evidence_strength` enforces *claims ≠ evidence*: a vendor's marketing metric stays tagged `vendor_claim` and cannot be promoted to `verified`. `informative_absence` carries an `expectation_set` so the silence is auditable (§7).

### Dimension result (one per analyst)

```jsonc
{
  "dimension": "EXIT", "focus_area": "Portability & Migration",
  "score": "Pass|Partial|Fail|Insufficient",            // enum, grammar-locked
  "assessment": "2–4 sentences, evidence-cited",         // length enforced by lint
  "trade_offs": { "gain": "…", "give_up": "…" },         // "—" sentinel allowed
  "vendor_questions": ["…","…"],                          // minItems 1; "2–3" enforced by lint
  "confidence": "high|medium|low",                        // drives needs-your-eyes flag
  "evidence_basis": "verified|vendor_claim|inferred|informative_absence|user_provided|insufficient",
  "evidence_citations": ["fact_id", …]                   // every claim traces to the dossier
}
```

**Enum relationship:** `evidence_basis` is a superset of the dossier's `evidence_strength` — it carries all five fact-level values (`verified`, `vendor_claim`, `inferred`, `informative_absence`, `user_provided`) plus `insufficient`, used only when the score is `Insufficient` and rests on no usable evidence. `evidence_strength` itself never needs `insufficient`: a fact that exists has some strength, and true absence lives in the dossier's `gaps[]`.

### Report (synthesis output → single render source of truth)

```jsonc
{
  "meta": { "vendor", "category", "version", "date", "sentiment": "positive|neutral|negative" },
  "executive_summary": { "key_takeaway", "paragraphs": ["…"], "suitability" },
  "overview_table": [ { "dimension", "focus_area", "result" } ],      // ×6
  "detailed": [ <dimension_result> ],                                // ×6
  "tradeoff_summary": [ { "dimension","result","gain","give_up" } ], // ×6
  "key_questions": [ "…" ],                                          // 5–6
  "vendor_questions": [ <vendor_question> ],                          // consolidated, §9
  "flags": [ { "dimension","type","note" } ],                        // working-doc only (§8); dimension enum adds "OVERALL" for report-level flags
  "changelog": [ … ]                                                 // response-pass revisions (v1.1+) only (§9)
}
```

**Citations note:** `evidence_citations` are our own dossier fact-IDs, *not* the API's native Citations feature (which is incompatible with `output_config.format`). No conflict.

---

## 6. Evidence sourcing (hybrid)

The evidence pass blends:
- **Live web research** — vendor docs, API reference, pricing, changelog; third-party coverage, practitioner reports, independent benchmarks.
- **User-supplied materials** — decks, security questionnaires, call transcripts, vendor answers.

Where neither surfaces a fact, fall back to `Insufficient Information` + a vendor question — unless the absence is *conspicuous* (§7).

---

## 7. Evidentiary logic: absence as evidence

Naively, "no info about system prompts" → `Insufficient`. But a **conspicuous absence** — no affordance documented anywhere it would appear if it existed — is itself evidence of opacity/lock-in. This is already latent in the framework (`framework-core.md`: "obscuring prompts, models, and architecture often signals thin differentiation") and practiced in the samples (Harvey EXIT = Fail partly because "the platform lacks a documented content download endpoint").

**Two kinds of "we found nothing":**

| | True gap | Informative absence |
|---|---|---|
| What | We didn't/couldn't look in the right places | We checked every surface the affordance would appear on; it's absent across all |
| Handling | → `Insufficient` + vendor question | → negative evidence supporting `Fail`/`Partial`, stated as explicit inference + vendor question |

**Decision rule (each analyst):** When no positive evidence exists for a mechanic, ask *"Did I check the places it would be documented if it existed?"*
- Yes, absent across all → **informative absence** → may support `Fail`/`Partial`, inference *named as an inference*, **confidence capped at medium**, plus a confirming vendor question.
- No / could plausibly exist undocumented → `Insufficient` + vendor question.

**Four guardrails keeping it disciplined (not speculation):**
1. Name the inference as an inference.
2. Enumerate where you looked (`expectation_set`) — absence is informative only relative to an expectation set.
3. Always rebuttable — generates a vendor question.
4. Confidence caps at medium on absence alone; rises only with corroboration.

Reconciles with critical rule #1: that rule forbids inventing a *positive* fact to fill a gap; it does not forbid a *disciplined negative inference* from documented silence. The rubrics for **SEE, CHANGE, EXIT** each carry an explicit "where you'd expect this documented" checklist.

---

## 8. The review gate

Fires once, after the Phase-1 draft + drift-check. Presents the draft plus a focused "where your input would matter most" list. **Non-blocking — it never holds the report hostage.**

**Correctable vs locked:**

| ✓ The exec CAN | ✗ The exec CANNOT |
|---|---|
| Correct or add evidence | Change a score without evidence |
| Answer open vendor questions (internal knowledge) | Soften, drop, or reweight a criterion |
| Add org context (industry, building-capacity?, primary touchpoint?, lock-in tolerance) | Override the framework's opinion / value judgment |

If the exec pushes to override an opinion, the skill declines, explains the framework is fixed, and may log it as a noted *client disagreement* — score stands.

**Three operating modes (the "auto-finalize" intent):**
- **Gated (default, interactive):** present draft + flags, invite correction, state "I'll finalize as-is unless you give corrections." Any non-corrective reply — "looks good," "finalize," or silence — ships it. The exec is never required to engage.
- **One-shot:** "just give me the report" skips the gate; final report carries flags inline.
- **Unattended/scheduled:** a configurable window (default **~10 minutes**) auto-finalizes for genuinely headless runs.

In all three, the finished report carries its own soft-spot awareness.

**Flag taxonomy** (populates "where your input would matter most"):
- `insufficient` — a true gap + its vendor question
- `informative_absence` — score driven by conspicuous silence (medium confidence)
- `unverified_claim` — a `vendor_claim` fact that materially affects a score
- `low_confidence` — any dimension below high confidence
- `org_context_dependent` — a suitability call hinging on context not supplied (report-level; carries flag dimension `OVERALL`, not one of the six)

**Flag rendering (deliberately different by surface):**
- Canonical Markdown + the review gate: explicit, itemized (the working document).
- Styled board deliverable: dissolved into the framework's native hedging prose ("self-reported, not independently verified," "undisclosed," "the absence of any documented export endpoint indicates…") plus the Questions-for-Vendor section. No "⚠ confidence" chrome. Flags do double duty: drive the gate AND tune the carefulness of the final prose.

---

## 9. Vendor rebuttal loop

The vendor gets a genuine chance to move the diagnosis; the skill also judges whether their answer actually answers the question.

**1. Questions are a first-class deliverable.** All per-dimension and gap-driven questions consolidate into one send-ready **"Questions for the Vendor"** document (house style: sharp, specific, falsifiable, professional — per the samples). Each question carries internal metadata:

```jsonc
{
  "id":"SEE-2", "dimension":"SEE",
  "question":"Can enterprise customers view or edit the system prompt … and through which interface?",
  "why_we_ask":"Determines whether your team can audit and shape AI behavior.",   // vendor-facing; required, "" sentinel if not surfaced (per §5)
  "current_basis":"informative_absence — not in API ref, admin docs, or security whitepaper",  // internal
  "what_would_change":"A documented admin/API setting to edit the system prompt moves SEE Fail → Partial"  // internal
}
```

`what_would_change` pre-commits, before the vendor responds, to what a genuinely responsive answer would shift — so neither side moves the goalposts.

**2. Vendor Response Mode.** The exec pastes/attaches the vendor's replies; the skill detects a response pass and re-enters the pipeline as a re-evaluation, ingesting answers as evidence with `source_type: vendor_response`.

**3. Adjudication — each answer graded for responsiveness *before* it can touch a score:**

| Verdict | Meaning | Effect |
|---|---|---|
| Substantive + verifiable | Specific, checkable | Skill verifies where it can → new evidence → re-runs that analyst; score may move |
| Claim only | Asserted, no evidence | Logged `vendor_claim`; score generally holds; noted |
| Roadmap | "Coming in Q3" | Recorded as roadmap, not current capability; score unchanged |
| Non-responsive / evasive | Dodges/deflects/refuses | **Itself evidence** — can reinforce a `Fail`; stated plainly ("did not answer X; responded with Y, which does not address it") |
| Unanswered | Skipped | Stays an open gap / `Insufficient` |

A refusal to answer *is* an answer (cf. Glean: "competitive advantages that cannot be disclosed").

**4. Output: a versioned revision with a visible diff.** Each response pass bumps the **minor** version (v1.0 → v1.1 → v1.2 …) and adds a "What changed after vendor response" section: per question — verdict + any score delta with triggering evidence. (There is no "v2" jump; response-pass revisions are v1.1+.)

**5. Immutability holds.** A score moves only because a responsive, substantive answer added real evidence that, through the unchanged rubric, yields a different result. The drift check's false-generosity guard (§10, L5) prevents a smooth non-answer from quietly softening a score.

---

## 10. Anti-drift guardrail stack (defense in depth)

Each layer independently defends the one question; generic-review drift must defeat all six to reach the page.

```
THE ONE QUESTION: does this build or erode independent, generalizable AI capacity?
├─ L1 · Immutable framework files ...... framework-core + 6 rubrics, injected VERBATIM
├─ L2 · Analyst harness ................ each clean subagent over-briefed + explicit "this is NOT a generic review"
├─ L3 · Structured-output cage (HARD) .. schema forbids generic fields at decode time; scoring vocab grammar-locked (§11)
├─ L4 · Evidence discipline ............ claims≠evidence · citations required · informative-absence handled
├─ L5 · Drift-check stage (symmetric) .. strips generic creep (too harsh) AND false generosity (too soft on opacity)
└─ L6 · Review gate .................... human corrects EVIDENCE, never the OPINION
```

**L2 — the analyst harness.** A fresh subagent under-briefed will default to Gartner. So we over-brief: each clean subagent's entire worldview is the injected payload — `framework-core.md` + its rubric (verbatim) + the dossier + an explicit "this is NOT a generic review; assess ONLY this dimension, ONLY through the one question; marketing claims are not evidence; no evidence → Insufficient + a vendor question" + the output schema. The clean context flips from liability to asset: once filled completely, nothing competes with the framework. Specialization lives in the rubric files; the harness is the shared wrapper that *forces* the opinionated framing onto every run.

**L5 — symmetric drift check.** A dedicated red-team pass re-reads the assembled report against the one question and catches drift on both flanks: a section that wandered into generic territory, *and* a section that went quietly easy on a vendor's silence. It can re-run any analyst that slipped before the report reaches the gate.

---

## 11. Structured outputs

Generally available on Opus 4.8 (our model). Constrained decoding turns L3 from a soft cage into a hard guarantee: always-valid JSON, no parse failures, no schema-violation retries.

**Two consequences on the anti-drift goal:**
- `additionalProperties: false` is enforced at decode time — the model cannot emit a stray `market_position` / `support_sla` key.
- Controlled vocabularies are `enum` (`score`, `confidence`, `evidence_strength`, `sentiment`, rebuttal `verdict`) — the model cannot invent a fifth score or a softer label.

**Schema-authoring rules (to stay within the supported subset + complexity limits):**

| Limit | Our rule |
|---|---|
| 24 optional params total; optionals also reorder output | Mark every field `required`; use sentinels (`"—"`, `""`, `[]`) instead of optional/nullable — as the samples already do |
| Union types capped at 16, "especially expensive" | No nullable unions — sentinels again |
| Grammar-complexity ceiling / 180s compile / "too complex" | Small, shallow schema per agent; never emit the whole report in one call. The six-way fan-out is justified twice: research depth *and* staying under the complexity ceiling |
| `minItems` 0 or 1 only; no `minLength`/`maxLength`/numeric ranges/array counts > 1 | Rules schemas can't express ("2–3 questions," "2–4 sentences," "≥1 citation unless Insufficient") move to prompt + post-lint |

**Two residual failure modes still owned (constrained decoding guarantees shape, not completion):**
- **Refusal** (`stop_reason: "refusal"`) — handle gracefully, surface to the exec.
- **Truncation** (`stop_reason: "max_tokens"`) — generous per-call `max_tokens` + detect-and-retry.

**Two-tier validation:**
- **Tier 1 — schema (hard, free):** structure, required fields, vocabulary; enforced at decode.
- **Tier 2 — lint (`lint_report.py`):** semantics the schema can't hold — 2–3 questions, 2–4 sentence assessments, ≥1 citation unless Insufficient, informative-absence carries an `expectation_set`.

**Mechanism in practice:** each analyst subagent receives its schema via structured outputs (the optional Workflow path uses the harness's `agent({schema})` option for the same effect); any direct-API utility (e.g., the eval harness) uses Pydantic + `messages.parse()`, whose SDK auto-transforms unsupported constraints and post-validates. Stable, versioned schemas hit the 24-hour grammar cache; the fan-out and the 4-vendor eval suite can run on the Batch API (50% off).

---

## 12. Output structure & rendering

### Canonical 7-section report (locked to the samples)

1. **Title block** — Vendor · "VENDOR EVALUATION REPORT" · category subtitle · `Version • Month Year`
2. **Executive Summary** — **KEY TAKEAWAY** (one declarative sentence) → 2–3 paragraphs → "best suited / poor fit for…" suitability line · overall sentiment
3. **Evaluation Overview** table — 6 × {Criterion, Focus Area, Result}
4. **Detailed Evaluation** — per dimension, report order **SEE · CHANGE · ADAPT · USE · LEARN · EXIT**: `[Result]` heading → assessment (2–4 sentences, cited) → Trade-offs (`+ Gain` / `− Give up`) → Questions for Vendor
5. **Trade-off Summary** table — 6 × {Criterion, Result, You Gain, You Give Up}
6. **Key Questions for Your Decision** — 5–6 strategic, org-tailored questions
7. **Footer** — `CONFIDENTIAL — FOR INTERNAL USE ONLY` + framework reminder + version

**Questions for the Vendor** (consolidated, send-ready) is **always present** — every dimension emits ≥1 vendor question, so it is a core deliverable, not conditional; it also renders as its own **standalone styled export** (the artifact the exec forwards to the vendor), not just an in-report section. Two components are conditional, rendered only when applicable: **What changed after vendor response** (response-pass revisions, v1.1+) and **Open items / where this is soft** (Markdown working-doc only).

### Rendering — one source of truth, no fragile dependencies

```
report.json ──┬──► report.md    (canonical; stdlib string templating)
              └──► report.html  (render_report.py → assets/report-template.html)
```

HTML is self-contained — inlined CSS, color-coded results (Pass = green · Partial = amber · Fail = red · Insufficient = grey), cover block, both tables, trade-off grid. The browser's **Print → PDF** produces the board deliverable. **Zero server-side PDF/Markdown dependencies** (the target environment had no pandoc/poppler; the skill must not inherit that fragility).

---

## 13. Org tailoring

The six-dimension analysis stays objective and org-agnostic (a vendor either exposes its prompts or it doesn't). If the exec supplies org context, the skill sharpens **only** the Executive Summary's suitability line and the Key Questions — never the dimension assessments. This honors "will it help YOUR company" without diluting the objective capacity analysis, and never overrides the opinions.

---

## 14. Error handling & edge cases

- **Out-of-scope vendor** (not AI-powered B2B SaaS): Stage 0 stops and explains; does not force the framework onto an ill-fitting target.
- **Thin evidence overall:** more `Insufficient` / informative-absence; the report says so plainly and leans on Questions for the Vendor.
- **Structured-output refusal / truncation:** §11 — surface refusals; retry truncations with higher `max_tokens`.
- **Subagent failure:** Workflow fallback — the affected dimension re-runs; if the workflow itself can't run, `SKILL.md` drives the same pipeline inline.
- **Vendor name ambiguity / multiple products:** confirm the specific product/SKU at intake before researching.
- **Opinion-override attempt** (exec or vendor): declined; logged as noted disagreement; score stands.

---

## 15. Testing & validation

The four existing reports (Glean, Harvey, Conveo, Legora) are golden references.

| Class | Checks | How |
|---|---|---|
| **Structural / lint** | All 7 sections; exactly 6 dimensions in order; valid scoring vocab; each assessment cites ≥1 fact or is Insufficient; each dimension has trade-offs + 2–3 questions | Deterministic schema + `lint_report.py` |
| **Golden concordance** | Same Pass/Partial/Fail per dimension as the human report? Same core trade-offs (Glean's knowledge-graph lock-in, Harvey's OpenAI single-vendor bet, Conveo's "No expertise needed" tell)? | LLM-judge vs. golden |
| **Adversarial anti-drift** | Strong security/pricing but poor capacity → stays on capacity · glowing marketing → tagged `vendor_claim` · conspicuous silence → informative-absence fires (not over-Insufficient) · vendor non-answer → graded non-responsive, can harden · opinion-override → declined | Curated red-team fixtures |
| **Immutability** | Same vendor + same evidence → same scores · override refused | Repeat runs + assertions |

The golden-concordance and adversarial suites form a multi-agent eval harness, runnable as a workflow during implementation. `examples/` doubles as style exemplars (tone/format only — opinions always come from the rubrics, never from imitating an example's verdict).

---

## 16. Resolved design decisions / future

- **Auto-finalize window:** unattended mode defaults to **~10 minutes**, configurable (§8). Interactive and one-shot modes do not wait.
- **Single-dimension spot-check:** not building it for v1. The architecture supports it later (it is one analyst subagent) if ever wanted.
- **Questions-for-the-Vendor standalone export:** **yes** — the consolidated vendor-questions doc renders as its own styled HTML / print-to-PDF artifact (the file the exec forwards to the vendor), in addition to its in-report section (§12).
- **Legora:** read in full; confirmed identical 7-section structure and house voice (the canonical "uniform Partial / competent-but-stops-short" exemplar). Used as both a validation target and a style exemplar alongside Glean/Harvey/Conveo.

---

## 17. Net architecture (one paragraph)

One skill guarding an immutable framework; `SKILL.md` orchestrating six over-briefed dimension-analyst subagents (with an optional deterministic Workflow accelerator) over a shared, source-tagged evidence dossier; a symmetric drift gate; a non-blocking review gate with auto-finalize; a vendor rebuttal loop that grades responsiveness; structured-output schemas that hard-lock the scoring vocabulary and forbid generic fields at decode time; Markdown + print-to-PDF output validated against four golden reports; shipped as a Claude Code plugin through a self-hosting marketplace repo.

---

## 18. Distribution & packaging (Claude Code marketplace)

The skill ships as a Claude Code **plugin** distributed through a **single self-hosting marketplace repo** (the same pattern the `last30days` skill uses: repo root holds `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json`, with `source: "./"`).

**Repo:** `github.com/Feedforward-AI/vendor-review-skill` (a fresh repo). The existing `Feedforward-AI/vendor-review` repo and its archive are **not** used (the archive is a known-broken version).

**Install flow for an executive:**
```
/plugin marketplace add Feedforward-AI/vendor-review-skill
/plugin install vendor-review@feedforward
```

**`.claude-plugin/marketplace.json`** (shape, from real manifests):
```jsonc
{
  "name": "feedforward",
  "owner":   { "name": "Feedforward", "url": "https://github.com/Feedforward-AI" },
  "metadata":{ "description": "Feedforward's AI-vendor capacity-evaluation tools." },
  "plugins": [{
    "name": "vendor-review",
    "description": "Evaluate an AI-powered software vendor against Feedforward's six-dimension framework for independent AI capacity (SEE/CHANGE/ADAPT/USE/LEARN/EXIT).",
    "version": "0.1.0",
    "author":   { "name": "Feedforward", "url": "https://github.com/Feedforward-AI" },
    "source":   "./",
    "category": "productivity",
    "homepage": "https://github.com/Feedforward-AI/vendor-review-skill"
  }]
}
```

**`.claude-plugin/plugin.json`** carries `name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`.

**Naming (proposed; Feedforward to confirm):** marketplace `feedforward` · plugin `vendor-review` · skill `feedforward-vendor-review`. The skill's invocation trigger lives in `SKILL.md` frontmatter (`name`, `description`) and must be written to fire on "evaluate/review an AI vendor" intent **without** colliding with generic "review vendor" phrasings that belong to other tools.

**Versioning:** plugin `version` in `plugin.json` + `marketplace.json` move together; the report's own `Version` (§12) is independent of the plugin version.

**Setup actions (deferred — outward-facing, require explicit go-ahead + `gh` auth):** create the new GitHub repo, scaffold the plugin/marketplace files, push. None done yet.

**Cross-platform note:** `scripts/*.py` must remain stdlib-only and OS-agnostic (no pandoc/poppler) so the plugin works on every installer's machine; the styled deliverable is produced via the browser's Print → PDF, not a local PDF engine.
