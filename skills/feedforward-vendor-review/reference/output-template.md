# Output Template — Vendor Evaluation Report

Canonical 7-section structure for all feedforward vendor evaluation reports.
Scoring vocabulary: **Pass / Partial / Fail / Insufficient**

---

## 1. Title block

Format: `Vendor · "VENDOR EVALUATION REPORT" · category · Version • Month Year`

Example: `Acme Corp · VENDOR EVALUATION REPORT · Legal AI · v1.0 • June 2026`

Rules:
- Vendor name exactly as the vendor presents it.
- Category is the primary use-case category (e.g., Legal AI, Knowledge Management, Contract Analysis).
- Version increments on every published revision (v1.0, v1.1, v2.0 …).
- Month Year is the publication month in full (e.g., June 2026).

---

## 2. Executive Summary

Content: 3–5 sentences synthesizing the overall assessment.

Rules:
- Open with the key takeaway — a single quotable sentence.
- State the overall sentiment (positive / neutral / negative).
- Connect findings to the capacity-building framework.
- Close with a suitability statement naming the type of organization this tool suits (and optionally one it does not).
- Fold optional org context into the suitability line ONLY; never into the dimension assessments.

---

## 3. Evaluation Overview

Content: A summary table of dimension scores.

Rules:
- One row per dimension: SEE, CHANGE, ADAPT, USE, LEARN, EXIT.
- Columns: Dimension | Score | One-line rationale.
- Scores use canonical vocabulary: Pass / Partial / Fail / Insufficient.
- No narrative prose in this section — table only.

---

## 4. Detailed Evaluation

Content: Full write-up for each of the six dimensions in this exact order:

1. SEE — Transparency & Prompt Visibility
2. CHANGE — Customizability
3. ADAPT — Vendor Agility
4. USE — Genuine Utility
5. LEARN — Transferable Knowledge
6. EXIT — Portability

Rules:
- Each dimension: heading, score (Pass / Partial / Fail / Insufficient), evidence paragraphs, and a "Questions for the Vendor" sub-section (always present; also exported as a standalone document).
- Do not reorder the dimensions.
- Do not fold org context into dimension assessments; reserve it for the suitability line in section 2.

---

## 5. Trade-off Summary

Content: Concise enumeration of the primary trade-offs the reader must weigh.

Rules:
- 3–5 bullet points.
- Each bullet frames a genuine tension (e.g., immediate productivity vs. long-term capability building).
- Do not advocate; surface the trade-offs neutrally.

---

## 6. Key Questions

Content: 5–6 strategic questions for decision-makers.

Rules:
- Questions must be tailored to this vendor's specific findings, not generic.
- Fold optional org context into the questions to sharpen them for the reader's situation.
- Numbered list.

---

## 7. Footer

Text: `CONFIDENTIAL — FOR INTERNAL USE ONLY`

Rules:
- Include the one-line framework reminder: "Evaluated against the SEE / CHANGE / ADAPT / USE / LEARN / EXIT capacity-building framework."
- Include the report version and publication date (mirrors the Title block).
- No additional narrative.

---

## Conditional components

| Component | When present |
|---|---|
| Questions for the Vendor | Always present in section 4; also exported as a standalone document |
| What changed after vendor response | v1.1+ revisions following a vendor response pass |
| Open items / where this is soft | Markdown working-doc only; omit from PDF/DOCX exports |
