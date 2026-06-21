# Vendor-Report Visual Redesign — Design

**Date:** 2026-06-21
**Status:** Approved (pending spec review)
**Scope:** Restyle the rendered `report.html` / `questions.html` to faithfully reproduce the example evaluation reports, and render inline Markdown emphasis as real formatting.

---

## 1. Problem

A live test produced an "extremely basic, text-only HTML" report that looks nothing like the example reports the user provided (`source_docs/*-evaluation-report.docx`). Investigation shows this is **not a bug** — it is exactly what the shipped template produces every run:

- `skills/feedforward-vendor-review/assets/report-template.html` uses a system-font stack and GitHub-grey palette with plain bordered tables.
- `skills/feedforward-vendor-review/scripts/render_report.py` emits flat markup (only the bracketed verdict tag is color-coded; the dimension name is not).

The skill wiring is correct: `SKILL.md` Stage 5 already mandates `render_report.py`, and `report.html` is the deliverable the exec prints to PDF. The output is plain because the **styling layer** diverges from the examples — that is what this redesign fixes.

A second, related defect: assessment prose in the source content uses Markdown emphasis (`*what*`). The renderer HTML-escapes prose but does not convert emphasis, so it renders **literal asterisks**. This is unacceptable in the deliverable.

## 2. Goals / Non-goals

**Goals**
- `report.html` and `questions.html` visually match the example reports' design system (typography, palette, color-coded results, tables, cover).
- Inline Markdown emphasis (`*italic*`, `**bold**`) renders as `<em>`/`<strong>` in the HTML, never as literal asterisks.

**Non-goals**
- No change to section order, the `report.json` schema/contract, lint rules, or `render_markdown` (the `.md` artifact keeps asterisks — correct for Markdown).
- No new dependencies. Output stays a single self-contained HTML file (inline CSS) that prints to PDF; scripts stay stdlib-only.
- No rebrand / logo / brand fonts (user chose "match examples faithfully").

## 3. Design system (extracted from the example DOCX)

Target environment for opening/printing: **Windows/Mac with Office** (Calibri installed), so a Calibri-compatible font stack renders true Calibri with no embedding.

**Font stack:** `Calibri, Carlito, "Segoe UI", system-ui, -apple-system, sans-serif`

**Tokens (CSS custom properties):**

| Token | Value | Use |
|---|---|---|
| `--ink` | `#2D3748` | Title, section headings, KEY TAKEAWAY statement |
| `--body` | `#4A5568` | Body paragraphs, kickers, list items |
| `--pass` | `#38A169` | Pass (green) |
| `--partial` | `#D69E2E` | Partial (amber) |
| `--fail` | `#E53E3E` | Fail (red) |
| `--insufficient` | `#718096` | Insufficient (slate) |
| `--rule` | `#E2E8F0` | Table borders, dividers, cover/footer rule |
| `--header-bg` | `#EDF2F7` | Table header shading |

**Type scale.** Sizes below are the **print baseline** (pt, faithful to the DOCX — `@media print`). On **screen**, everything scales up ~1.15× for reading comfort via a single larger root font-size; because the scale is expressed in `rem`, one root change rescales the whole document and proportions stay identical to print. Concretely: `:root { font-size: <print baseline>; } @media screen { :root { font-size: ~1.15× baseline; } }`.

| Element | Size / weight | Color |
|---|---|---|
| Vendor title | 28pt / 700 | `--ink` |
| Kicker ("VENDOR EVALUATION REPORT") | 10pt / uppercase / letter-spaced | `--body` |
| Category | 11pt | `--body` |
| Version · date | 9pt | `--body` |
| Section heading (Exec Summary, Evaluation Overview, …) | 18pt / 700, thin `--rule` underline | `--ink` |
| KEY TAKEAWAY label | 9pt / uppercase / letter-spaced | `--body` |
| KEY TAKEAWAY statement | 12pt / 600 | `--ink` |
| Body paragraph | 11pt / line-height 1.5 | `--body` |
| Dimension heading | 14pt / 700 | name + `[verdict]` colored by result; "— focus area" in `--ink` |
| "Trade-offs" / "Questions for Vendor" subhead | 11pt / 700 | `--ink` |
| `+ Gain:` label | 10pt / 700 | `--pass`; text `--body` |
| `− Give up:` label | 10pt / 700 | `--fail`; text `--body` |
| List / vendor-question items | 10pt | `--body` |
| Footer | 9pt, top `--rule` | `--body` |

**Cover:** vendor title + kicker stack separated from the body by a thin `--rule` line (replaces the current heavy 3px black bar).

**Tables:** shaded header row (`--header-bg`, `--ink` text), light `--rule` cell borders, comfortable padding; the **Result** cell is colored + bold by verdict. Dimension-name cells stay plain `<td>SEE</td>`.

## 4. Code changes

### 4.1 `assets/report-template.html`
- Replace the `<style>` block with the design system in §3.
- Express the type scale in `rem` against a root font-size; pin the faithful print baseline in `@media print` and a ~1.15× larger root in `@media screen` (dual sizing — larger on screen, faithful in PDF).
- **Keep** the class names `result-pass`, `result-partial`, `result-fail`, `result-insufficient` (only their color values change) — `test_html_template.py` asserts their presence.
- **Keep** the `.gain` / `.giveup` classes — restyle to `--pass` / `--fail`.
- **Keep** all `{{VENDOR}} {{CATEGORY}} {{VERSION}} {{DATE}} {{BODY}}` tokens and the inline `<style>` (self-contained guarantee).

### 4.2 `scripts/render_report.py`
- **`_detail_html`** — color the dimension heading by result. New shape:
  `<h3><span class='{cls}'>{dim}</span> — {focus} <span class='{cls}'>[{result}]</span></h3>`
  (focus area stays in default heading/ink color; name + verdict carry the result class).
- **Inline-emphasis helper `_rich(value)`** — HTML-escape first (via the existing escape), *then* convert emphasis on the escaped string:
  - `**bold**` → `<strong>…</strong>` (applied before italic)
  - `*italic*` → `<em>…</em>`
  - Match only emphasis hugging non-whitespace (e.g. `*word*`, not `3 * 4`), so prose with literal asterisks does not misfire.
  - Because conversion runs on already-escaped text and only wraps captured groups, injection safety is preserved (an injected `*<script>*` becomes `<em>&lt;script&gt;</em>` — inert).
- Apply `_rich` to every **prose** field in the HTML path: `assessment`, `key_takeaway`, exec-summary `paragraphs`, `suitability`, `trade_offs.gain`/`give_up`, `vendor_questions`, `key_questions`, changelog `change`. Do **not** apply it to `score`/`result`/`dimension`/`focus_area` (those keep plain `_e`).
- `render_markdown` is unchanged.

### 4.3 Tests
- `tests/test_html_template.py` — still passes (class names retained); optionally add assertions for the new tokens (`--ink`, `--pass`, etc.).
- `tests/test_render_report.py` — existing escaping/order tests must still pass (verified: payloads contain no `*`; dimension cells stay `<td>SEE</td>`; Result-cell coloring unaffected). Add:
  - `*x*` in a prose field → `<em>x</em>` in HTML, and no bare `*` survives in rendered prose.
  - `**x**` → `<strong>x</strong>`.
  - An injected `<script>` adjacent to emphasis stays escaped (regression guard for the escape-then-emphasize order).

## 5. Risks

- **Emphasis regex over-matching** — mitigated by the non-whitespace-hugging rule and bold-before-italic ordering; covered by a literal-asterisk test.
- **Escape/emphasis interaction** — mitigated by escaping first and operating only on escaped text; covered by an injection-adjacent-to-emphasis test.
- **Font fallback off-Office** — out of target scope (user opens on Office machines); the stack degrades to a metric-compatible face if ever needed, and embedding is a localized future change.

## 6. Out of scope / future
- Embedding a Calibri-metric web font for pixel-identical rendering on bare-Linux machines (one-line CSS `@font-face` addition if ever required).
- Block-level Markdown (lists/headings inside prose) — source prose only uses inline emphasis.
