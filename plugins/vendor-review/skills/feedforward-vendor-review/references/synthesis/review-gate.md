# Review-Gate Presentation

How to present the draft report to the exec at the Review Gate (after Stage 4, before Stage 5 render). The goal is a **direct, scannable ask** — not a status dump. Lead with "the report is ready," then ask plainly for the specific information that would sharpen it.

This presentation is built from the report's `flags` array plus any still-open vendor questions and org-context gaps. Do not invent asks: every item must trace to a flag, an open vendor question, or a missing piece of org context.

---

## The shape

**1. One-line headline — the report is ready.**
Open by telling the exec the work is done and the report stands on its own. Never open with apologies, caveats, or a wall of flags.

**2. A short, direct request for input — only if there are flags.**
Frame it as "here are a few areas that would benefit from more info — do you have any of the following?" Then an itemized, numbered list.

**3. A clear escape hatch.**
State that none of this is required and that any non-corrective reply finalizes the report as-is.

---

## Template (gated / interactive mode)

> **The report on _[Vendor — SKU]_ is ready to finalize.** It stands on its own as scored.
>
> A few areas would be sharper if you happen to have more information. **Do you have any of the following?**
>
> 1. **[EXIT] Contract data-export terms.** The docs don't confirm whether you can pull your data out in an open format. If your contract or a demo covered this, it could move EXIT off *Insufficient*.
> 2. **[SEE] Admin audit-log scope.** We found no mention of per-user action logs anywhere we'd expect them, so SEE is scored on that silence. If you know they exist, point us to where.
> 3. **[ADAPT] Vendor's fine-tuning claim.** The vendor says you can bring your own model weights, but we couldn't independently verify it. Anything from your sales conversations that confirms or contradicts this?
> 4. **[Org context] Your lock-in tolerance and AI-maturity stage.** The suitability line depends on these and you haven't told us yet — a sentence on each sharpens it.
>
> **None of this is required.** Share whatever you have and I'll fold it in and re-score only the affected dimensions. Otherwise just reply **"finalize"** (or "looks good") and I'll ship the report exactly as it stands.

Keep the list to the items that genuinely matter — typically **3–6**. If there are more flags than that, surface the highest-impact ones (those that could change a score) and note the rest are detailed inline in the report.

---

## How to phrase each item by flag type

Write each item as a plain-language request — what's missing, and what the exec's answer would change. Lead with the bracketed dimension tag.

| Flag `type` | How to phrase the ask |
|---|---|
| `insufficient` | "We couldn't confirm _[X]_. If you have _[doc / contract clause / demo note]_, it could move _[DIM]_ off *Insufficient*." |
| `informative_absence` | "We found no mention of _[X]_ anywhere we'd expect it, so _[DIM]_ is scored on that silence (medium confidence). If you know it exists, point us to it." |
| `unverified_claim` | "The vendor claims _[X]_ but we couldn't verify it independently. Anything that confirms or contradicts it?" |
| `low_confidence` | "Our read on _[X]_ is low-confidence. Any first-hand experience would firm it up." |
| `org_context_dependent` | "The suitability call depends on _[your AI-maturity stage / lock-in tolerance / whether this is a primary employee touchpoint]_ — tell us and I'll sharpen it." |

You may also list any still-open **vendor questions** the exec might be able to answer from internal knowledge — phrase those as "If you already know the vendor's answer to _[question]_, I'll treat it as evidence."

---

## Ordering

Order the list by impact, not by dimension order:

1. Items that could **change a score** (`insufficient`, `informative_absence`, `unverified_claim`) first.
2. `low_confidence` items next.
3. `org_context_dependent` items last (they sharpen framing, never move a score).

---

## When there is nothing to ask

If the drift check produced no material flags and no open vendor questions, do **not** manufacture asks. Say so directly:

> **The report on _[Vendor — SKU]_ is ready to finalize** — the evidence was complete enough that I have no open questions for you. Reply **"finalize"** to ship it, or tell me if you'd like to add evidence or org context first.

---

## Mode variations

- **`gated` (default):** present the template above and wait. Any non-corrective reply — "looks good," "finalize," or silence — ships it. The exec is never required to engage.
- **`one-shot` (`--no-questions`):** skip this presentation entirely; the finished report carries its flags inline.
- **`unattended`:** present the asks, then auto-finalize after the configured window (default ~10 minutes) if there is no reply.

In every mode the finished report carries its own soft-spot awareness — the gate is a courtesy, never a blocker.

---

## What the exec's reply may and may not do

Restate this only if the exec pushes to change a score by assertion:

- **May:** correct or add evidence; answer an open vendor question from internal knowledge (ingested as `user_provided`); add or refine org context.
- **May not:** change a score without new evidence, or soften/drop/override a framework criterion. Decline politely, explain the framework is fixed, note the disagreement in the executive-summary prose, and hold the score as scored.
