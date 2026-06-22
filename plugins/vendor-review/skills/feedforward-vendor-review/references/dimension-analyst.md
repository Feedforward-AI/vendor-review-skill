# Dimension Analyst Protocol

Use this protocol for exactly one Feedforward dimension for one vendor. It can be followed directly by Codex or supplied as a prompt to a subagent when a multi-agent tool is available.

Required inputs:

1. `references/framework-core.md` - immutable scoring law, one question, scoring vocabulary, and absence-as-evidence rule.
2. One dimension rubric from `references/dimensions/<dimension>.md`.
3. The shared evidence dossier with fact ids, source type, evidence strength, confidence, and gaps.
4. `schemas/dimension-result.schema.json`.

Rules:

- Assess only the assigned dimension and only through the independent, generalizable AI capacity question.
- This is not a generic software review. Discuss security, pricing, market share, support SLAs, or integration breadth only when they directly affect the assigned dimension's capacity question.
- Treat marketing claims as claims. A fact tagged `vendor_claim` cannot become a verified pro without corroboration.
- Apply the absence-as-evidence rule. A documented silence across expected surfaces is `informative_absence` with medium-or-lower confidence and a confirming vendor question. Do not use `informative_absence` when expected surfaces were not checked.
- Cite every assessment claim to a dossier fact id in `evidence_citations`.
- If there is no usable evidence, score `Insufficient`, set `evidence_basis` accordingly, and raise vendor questions.
- Produce 2-3 specific, polite `vendor_questions`.
- Keep `assessment` to 2-4 sentences.

Return only a JSON object conforming to `schemas/dimension-result.schema.json`.
