# Vendor-Report Visual Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle the rendered `report.html` / `questions.html` to faithfully match the example evaluation reports, and render inline Markdown emphasis as real `<em>`/`<strong>` instead of literal asterisks.

**Architecture:** Two contained changes. (1) `scripts/render_report.py` gains an escape-then-emphasize helper and emits faithful markup (result-colored dimension headings, section subheads, a structured KEY TAKEAWAY block). (2) `assets/report-template.html` gets a full CSS rewrite to the examples' design system with dual sizing (larger on screen, faithful pt baseline in print). The `report.json` contract, section order, lint rules, and `render_markdown` are untouched.

**Tech Stack:** Python 3 stdlib only (`html`, `re`, `json`); self-contained HTML + inline CSS; browser Print → PDF.

## Global Constraints

- Scripts stay **stdlib-only** — no new dependencies (no pandoc/poppler/jinja).
- `report.html` stays a **single self-contained file** with inline `<style>`.
- **Keep** CSS class names `result-pass`, `result-partial`, `result-fail`, `result-insufficient`, `.gain`, `.giveup` and template tokens `{{VENDOR}} {{CATEGORY}} {{VERSION}} {{DATE}} {{BODY}}` (tests pin them).
- **Escape-before-emphasize**: emphasis conversion runs only on already-HTML-escaped text; never apply emphasis to `score`/`result`/`dimension`/`focus_area`/`evidence`.
- Do **not** modify `render_markdown`, the JSON schema, or `lint_report.py`.
- Palette: `--ink #2D3748`, `--body #4A5568`, `--pass #38A169`, `--partial #D69E2E`, `--fail #E53E3E`, `--insufficient #718096`, `--rule #E2E8F0`, `--header-bg #EDF2F7`. Font stack: `Calibri, Carlito, "Segoe UI", system-ui, -apple-system, sans-serif`.
- Run all tests with `cd /home/exedev/Documents/vendor_review_skill && PYTHONPATH=skills/feedforward-vendor-review/scripts python -m pytest` (the suite imports `render_report` directly).

---

### Task 1: Render faithful markup + inline Markdown emphasis

**Files:**
- Modify: `skills/feedforward-vendor-review/scripts/render_report.py`
- Test: `tests/test_render_report.py`

**Interfaces:**
- Produces: `_rich(value) -> str` — HTML-escapes `value`, then converts `**bold**`→`<strong>…</strong>` and `*italic*`→`<em>…</em>` (emphasis must hug non-whitespace). Used for all prose fields in the HTML path.
- `_detail_html` emits `<h3><span class='{result-class}'>{DIM}</span> — {focus} <span class='{result-class}'>[{verdict}]</span></h3>`, `<p class='subhead'>Trade-offs</p>`, and `<p class='subhead'>Questions for Vendor</p>`.
- `render_html` emits `<p class='key-takeaway'><span class='kt-label'>KEY TAKEAWAY</span>{statement}</p>`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_render_report.py`:

```python
# --- Visual redesign: inline emphasis + faithful markup ---

def test_html_renders_markdown_italic_emphasis():
    r = load()
    r["detailed"][0]["assessment"] = "Harvey provides *meaningful* transparency. Second sentence."
    html = render_report.render_html(r, TEMPLATE)
    assert "<em>meaningful</em>" in html
    assert "*meaningful*" not in html

def test_html_renders_markdown_bold_emphasis():
    r = load()
    r["executive_summary"]["paragraphs"][0] = "This is **critical** context here."
    html = render_report.render_html(r, TEMPLATE)
    assert "<strong>critical</strong>" in html
    assert "**critical**" not in html

def test_html_emphasis_preserves_escaping():
    r = load()
    r["detailed"][0]["assessment"] = "*<script>x</script>* normal. Second sentence."
    html = render_report.render_html(r, TEMPLATE)
    assert "<script>x</script>" not in html
    assert "<em>&lt;script&gt;x&lt;/script&gt;</em>" in html

def test_html_emphasis_ignores_spaced_asterisks():
    r = load()
    r["detailed"][0]["assessment"] = "A times B is 3 * 4 here. Second sentence."
    html = render_report.render_html(r, TEMPLATE)
    assert "3 * 4" in html  # not turned into an <em>

def test_html_dimension_heading_colored_by_result():
    r = load()
    for d in r["detailed"]:
        if d["dimension"] == "SEE":
            d["score"] = "Fail"
    html = render_report.render_html(r, TEMPLATE)
    assert "<span class='result-fail'>SEE</span>" in html

def test_html_key_takeaway_label_markup():
    html = render_report.render_html(load(), TEMPLATE)
    assert "class='key-takeaway'" in html
    assert "class='kt-label'" in html
    assert "KEY TAKEAWAY" in html

def test_html_detail_has_subheads():
    html = render_report.render_html(load(), TEMPLATE)
    assert "class='subhead'>Trade-offs<" in html
    assert "class='subhead'>Questions for Vendor<" in html
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `cd /home/exedev/Documents/vendor_review_skill && PYTHONPATH=skills/feedforward-vendor-review/scripts python -m pytest tests/test_render_report.py -k "emphasis or dimension_heading or key_takeaway or subheads" -v`
Expected: FAIL (e.g. `<em>meaningful</em>` not found; `class='subhead'` not found).

- [ ] **Step 3: Add the `_rich` helper**

In `skills/feedforward-vendor-review/scripts/render_report.py`, add `import re` next to the existing imports, and add this helper directly below `_e`:

```python
_BOLD = re.compile(r"\*\*(\S(?:.*?\S)?)\*\*")
_ITALIC = re.compile(r"\*(\S(?:.*?\S)?)\*")


def _rich(value):
    """HTML-escape, then render inline Markdown emphasis as <strong>/<em>.

    Escaping runs first and emphasis only wraps captured (already-escaped)
    groups, so the result stays injection-safe. Emphasis markers must hug
    non-whitespace (``*word*``), so literal asterisks like ``3 * 4`` are left
    alone. Bold is converted before italic so ``**x**`` is not mis-split.
    """
    s = _html.escape(str(value))
    s = _BOLD.sub(r"<strong>\1</strong>", s)
    s = _ITALIC.sub(r"<em>\1</em>", s)
    return s
```

- [ ] **Step 4: Rewrite `_detail_html` with colored headings, subheads, and `_rich` prose**

Replace the entire `_detail_html` function with:

```python
def _detail_html(report):
    rows = []
    by_dim = {d["dimension"]: d for d in report["detailed"]}
    for dim in DIM_ORDER:
        d = by_dim[dim]
        cls = CSS_CLASS.get(d["score"], "")
        rows.append(f"<h3><span class='{cls}'>{_e(dim)}</span> — {_e(d['focus_area'])} "
                    f"<span class='{cls}'>[{_e(_result(d['score']))}]</span></h3>")
        rows.append(f"<p>{_rich(d['assessment'])}</p>")
        rows.append("<p class='subhead'>Trade-offs</p>")
        rows.append(f"<p><span class='gain'>+ Gain:</span> {_rich(d['trade_offs']['gain'])}<br>"
                    f"<span class='giveup'>− Give up:</span> {_rich(d['trade_offs']['give_up'])}</p>")
        rows.append("<p class='subhead'>Questions for Vendor</p><ul>"
                    + "".join(f"<li>{_rich(q)}</li>" for q in d["vendor_questions"]) + "</ul>")
    return "\n".join(rows)
```

- [ ] **Step 5: Apply `_rich` to prose in `_tradeoff_html`**

In `_tradeoff_html`, change the gain/give-up cells from `_e` to `_rich`:

```python
            rows.append(f"<tr><td>{_e(row['dimension'])}</td>"
                        f"<td class='{cls}'>{_e(_result(row['result']))}</td>"
                        f"<td>{_rich(row['gain'])}</td><td>{_rich(row['give_up'])}</td></tr>")
```

(Leave `_overview_html` unchanged — it has no free prose; its dimension cells must stay plain `<td>…</td>`.)

- [ ] **Step 6: Rewrite the body assembly in `render_html`**

In `render_html`, replace the executive-summary, key-questions, and changelog body lines so prose uses `_rich` and KEY TAKEAWAY uses the structured markup. The full body block becomes:

```python
    body.append("<h2>Executive Summary</h2>")
    body.append(f"<p class='key-takeaway'><span class='kt-label'>KEY TAKEAWAY</span>{_rich(es['key_takeaway'])}</p>")
    for p in es["paragraphs"]:
        body.append(f"<p>{_rich(p)}</p>")
    body.append(f"<p>{_rich(es['suitability'])}</p>")
    body.append(_overview_html(report))
    body.append("<h2>Detailed Evaluation</h2>")
    body.append(_detail_html(report))
    body.append(_tradeoff_html(report))
    body.append("<h2>Key Questions for Your Decision</h2><ol>"
                + "".join(f"<li>{_rich(q)}</li>" for q in report["key_questions"]) + "</ol>")
    if report.get("changelog"):
        body.append("<h2>What changed after vendor response</h2><ul>"
                    + "".join(f"<li><strong>{_e(c['dimension'])}</strong>: {_rich(c['change'])} ({_e(c['evidence'])})</li>"
                              for c in report["changelog"]) + "</ul>")
```

- [ ] **Step 7: Apply `_rich` to prose in `render_questions_html`**

In `render_questions_html`, change the question/why lines to use `_rich`:

```python
        why = f"<br><em>{_rich(q['why_we_ask'])}</em>" if q.get("why_we_ask") else ""
        items.append(f"<li><strong>[{_e(q['dimension'])}]</strong> {_rich(q['question'])}{why}</li>")
```

- [ ] **Step 8: Run the full render test file**

Run: `cd /home/exedev/Documents/vendor_review_skill && PYTHONPATH=skills/feedforward-vendor-review/scripts python -m pytest tests/test_render_report.py -v`
Expected: PASS — the new tests plus all pre-existing escaping/order/changelog tests (the escaping payloads contain no `*`, so `_rich` escapes them identically to `_e`).

- [ ] **Step 9: Commit**

```bash
git add skills/feedforward-vendor-review/scripts/render_report.py tests/test_render_report.py
git commit -m "feat: faithful report markup + inline Markdown emphasis in HTML"
```

---

### Task 2: Rewrite the HTML template CSS (design system + dual sizing)

**Files:**
- Modify: `skills/feedforward-vendor-review/assets/report-template.html`
- Test: `tests/test_html_template.py`

**Interfaces:**
- Consumes: the markup/classes produced in Task 1 (`.key-takeaway`, `.kt-label`, `.subhead`, `result-*`, `.gain`, `.giveup`, `<h2>`/`<h3>`/`table`).
- Produces: a self-contained template carrying the §3 design tokens, the Calibri stack, and dual sizing (`:root` screen baseline + `@media print` faithful pt baseline).

- [ ] **Step 1: Write the failing test**

Append to `tests/test_html_template.py`:

```python
def test_design_system_tokens_and_dual_sizing():
    t = F.read_text()
    for token in ["--ink", "--body", "--pass", "--partial", "--fail", "--insufficient", "--rule", "--header-bg"]:
        assert token in t, f"missing token {token}"
    assert "Calibri" in t
    assert "Carlito" in t
    assert "@media print" in t
    assert "@media screen" in t
    assert "11pt" in t  # faithful print baseline
    for cls in ["key-takeaway", "kt-label", "subhead"]:
        assert cls in t, f"missing style hook {cls}"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd /home/exedev/Documents/vendor_review_skill && PYTHONPATH=skills/feedforward-vendor-review/scripts python -m pytest tests/test_html_template.py::test_design_system_tokens_and_dual_sizing -v`
Expected: FAIL (`--ink` / `Calibri` / `@media screen` not present in the current template).

- [ ] **Step 3: Replace the template file**

Overwrite `skills/feedforward-vendor-review/assets/report-template.html` with:

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{{VENDOR}} — Vendor Evaluation Report</title>
<style>
  :root {
    --ink:#2D3748; --body:#4A5568;
    --pass:#38A169; --partial:#D69E2E; --fail:#E53E3E; --insufficient:#718096;
    --rule:#E2E8F0; --header-bg:#EDF2F7;
    font-size: 17px;                 /* screen: ~1.15x the print baseline, for reading comfort */
  }
  @media print { :root { font-size: 11pt; } }   /* faithful DOCX baseline */

  body { font-family: Calibri, Carlito, "Segoe UI", system-ui, -apple-system, Roboto, Helvetica, Arial, sans-serif;
         color: var(--body); max-width: 820px; margin: 0 auto; padding: 2.5rem 2rem;
         line-height: 1.5; font-size: 1rem; }

  .cover { border-bottom: 1px solid var(--rule); margin-bottom: 1.75rem; padding-bottom: 1rem; }
  .cover h1 { margin: 0 0 .25rem; font-size: 2.545rem; line-height: 1.1; font-weight: 700; color: var(--ink); }
  .kicker { letter-spacing: .12em; text-transform: uppercase; color: var(--body); font-size: .909rem; }
  .cover .meta { font-size: .818rem; color: var(--body); margin-top: .25rem; }

  h2 { color: var(--ink); font-size: 1.636rem; font-weight: 700; margin: 1.75rem 0 .5rem;
       padding-bottom: .25rem; border-bottom: 1px solid var(--rule); }
  h3 { color: var(--ink); font-size: 1.273rem; font-weight: 700; margin: 1.25rem 0 .4rem; }
  p { margin: .5rem 0; }

  .key-takeaway { font-size: 1.091rem; font-weight: 600; color: var(--ink); }
  .kt-label { display: block; font-size: .818rem; font-weight: 700; letter-spacing: .12em;
              text-transform: uppercase; color: var(--body); margin-bottom: .15rem; }
  .subhead { font-weight: 700; color: var(--ink); margin: .7rem 0 .2rem; }

  table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: .909rem; }
  th, td { border: 1px solid var(--rule); padding: .5rem .65rem; text-align: left; vertical-align: top; }
  th { background: var(--header-bg); color: var(--ink); font-weight: 700; }

  .result-pass { color: var(--pass); font-weight: 700; }
  .result-partial { color: var(--partial); font-weight: 700; }
  .result-fail { color: var(--fail); font-weight: 700; }
  .result-insufficient { color: var(--insufficient); font-weight: 700; }
  .gain { color: var(--pass); font-weight: 700; }
  .giveup { color: var(--fail); font-weight: 700; }

  ul, ol { margin: .4rem 0 .8rem; padding-left: 1.4rem; font-size: .909rem; }
  li { margin: .25rem 0; }

  .footer { margin-top: 2.5rem; border-top: 1px solid var(--rule); padding-top: .75rem;
            color: var(--body); font-size: .818rem; }

  @media print { body { padding: 0; max-width: none; } a { color: inherit; text-decoration: none; } }
</style>
</head>
<body>
  <div class="cover">
    <div class="kicker">Vendor Evaluation Report</div>
    <h1>{{VENDOR}}</h1>
    <div class="meta">{{CATEGORY}} &nbsp;•&nbsp; {{VERSION}} &nbsp;•&nbsp; {{DATE}}</div>
  </div>
  {{BODY}}
  <div class="footer">CONFIDENTIAL — FOR INTERNAL USE ONLY · This evaluation assesses vendors on immediate utility and long-term organizational AI capacity building · {{VERSION}}</div>
</body>
</html>
```

- [ ] **Step 4: Run the template tests**

Run: `cd /home/exedev/Documents/vendor_review_skill && PYTHONPATH=skills/feedforward-vendor-review/scripts python -m pytest tests/test_html_template.py -v`
Expected: PASS — both the pre-existing `test_tokens_and_color_classes` (tokens + `result-*` classes + `<style>` retained) and the new `test_design_system_tokens_and_dual_sizing`.

- [ ] **Step 5: Run the whole suite**

Run: `cd /home/exedev/Documents/vendor_review_skill && PYTHONPATH=skills/feedforward-vendor-review/scripts python -m pytest`
Expected: PASS (entire suite green — render, template, vocab-consistency, manifests, etc.).

- [ ] **Step 6: Visually verify the rendered artifact**

Render the sample fixture and open the HTML to confirm it matches the examples (slate text, color-coded verdicts, shaded tables, no literal asterisks):

```bash
cd /home/exedev/Documents/vendor_review_skill
PYTHONPATH=skills/feedforward-vendor-review/scripts python skills/feedforward-vendor-review/scripts/render_report.py tests/fixtures/sample_report.json /tmp/redesign_out
grep -c "<em>\|<strong>" /tmp/redesign_out/report.html   # emphasis rendered
grep -F "result-fail" /tmp/redesign_out/report.html | head -1   # verdict coloring present
```

Expected: emphasis tags present; `result-*` spans present; opening `/tmp/redesign_out/report.html` in a browser shows the redesigned look.

- [ ] **Step 7: Commit**

```bash
git add skills/feedforward-vendor-review/assets/report-template.html tests/test_html_template.py
git commit -m "feat: restyle report template to faithful design system with dual sizing"
```

---

## Self-Review

**Spec coverage:**
- §3 design tokens / type scale / font → Task 2 (template CSS) ✓
- §3 dual sizing (screen ~1.15×, print faithful) → Task 2 `:root` + `@media print` ✓
- §4.1 keep classes/tokens/`<style>` → Global Constraints + Task 2 test ✓
- §4.2 `_rich` helper + prose application → Task 1 Steps 3–7 ✓
- §4.2 result-colored dimension headings → Task 1 Step 4 ✓
- §4.2 `render_markdown` unchanged → not touched in any task ✓
- §4.3 emphasis tests, escaping regression, dimension-cell stability → Task 1 Step 1 + existing suite ✓
- KEY TAKEAWAY structured block + section subheads (faithful markup from §3) → Task 1 Steps 4, 6 ✓

**Placeholder scan:** No TBD/TODO/"handle edge cases"; every code step shows complete code. ✓

**Type/name consistency:** `_rich` defined in Task 1 Step 3, used consistently in Steps 4–7; classes `key-takeaway`/`kt-label`/`subhead`/`result-*`/`gain`/`giveup` emitted in Task 1 and styled under the same names in Task 2. ✓
