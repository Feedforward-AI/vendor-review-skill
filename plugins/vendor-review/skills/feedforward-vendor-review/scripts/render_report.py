"""Render a Feedforward vendor-review report.json into Markdown + self-contained HTML."""
import html as _html
import json
import re
import sys
from pathlib import Path

from _constants import DIM_ORDER

DISPLAY = {"Pass": "Pass", "Partial": "Partial", "Fail": "Fail", "Insufficient": "Insufficient Information"}
CSS_CLASS = {"Pass": "result-pass", "Partial": "result-partial",
             "Fail": "result-fail", "Insufficient": "result-insufficient"}


def _e(value):
    """HTML-escape a dynamic value."""
    return _html.escape(str(value))


_BOLD = re.compile(r"\*\*([^*\s](?:[^*]*[^*\s])?)\*\*")
_ITALIC = re.compile(r"\*([^*\s](?:[^*]*[^*\s])?)\*")


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


def _result(r):
    return DISPLAY.get(r, r)


def _score_strip_html(report):
    cards = []
    by_overview = {r["dimension"]: r for r in report["overview_table"]}
    for dim in DIM_ORDER:
        if dim in by_overview:
            row = by_overview[dim]
            cls = CSS_CLASS.get(row["result"], "")
            cards.append(
                f"<div class='score-card {cls}'>"
                f"<div class='score-label'>{_e(row['dimension'])}</div>"
                f"<div class='score-focus'>{_e(row['focus_area'])}</div>"
                f"<div class='score-result'>{_e(_result(row['result']))}</div>"
                "</div>"
            )
    return "<div class='score-grid'>" + "".join(cards) + "</div>"


def render_markdown(report):
    m = report["meta"]
    out = []
    out.append(f"# {m['vendor']}")
    out.append(f"**VENDOR EVALUATION REPORT** — {m['category']} — Version {m['version']} • {m['date']}\n")

    es = report["executive_summary"]
    out.append("## Executive Summary\n")
    out.append(f"**KEY TAKEAWAY** — {es['key_takeaway']}\n")
    for p in es["paragraphs"]:
        out.append(p + "\n")
    out.append(es["suitability"] + "\n")

    out.append("## Evaluation Overview\n")
    out.append("| Criterion | Focus Area | Result |")
    out.append("|---|---|---|")
    by_overview = {r["dimension"]: r for r in report["overview_table"]}
    for dim in DIM_ORDER:
        if dim in by_overview:
            row = by_overview[dim]
            out.append(f"| {row['dimension']} | {row['focus_area']} | {_result(row['result'])} |")
    out.append("")

    out.append("## Detailed Evaluation\n")
    by_dim = {d["dimension"]: d for d in report["detailed"]}
    for dim in DIM_ORDER:
        d = by_dim[dim]
        out.append(f"### {dim} — {d['focus_area']}   [{_result(d['score'])}]\n")
        out.append(d["assessment"] + "\n")
        out.append("**Trade-offs**\n")
        out.append(f"+ Gain: {d['trade_offs']['gain']}")
        out.append(f"− Give up: {d['trade_offs']['give_up']}\n")
        out.append("**Questions for Vendor**\n")
        for q in d["vendor_questions"]:
            out.append(f"- {q}")
        out.append("")

    out.append("## Trade-off Summary\n")
    out.append("| Criterion | Result | You Gain | You Give Up |")
    out.append("|---|---|---|---|")
    by_tradeoff = {r["dimension"]: r for r in report["tradeoff_summary"]}
    for dim in DIM_ORDER:
        if dim in by_tradeoff:
            row = by_tradeoff[dim]
            out.append(f"| {row['dimension']} | {_result(row['result'])} | {row['gain']} | {row['give_up']} |")
    out.append("")

    out.append("## Key Questions for Your Decision\n")
    for i, q in enumerate(report["key_questions"], 1):
        out.append(f"{i}. {q}")
    out.append("")

    if report.get("changelog"):
        out.append("## What changed after vendor response\n")
        for c in report["changelog"]:
            out.append(f"- **{c['dimension']}**: {c['change']} ({c['evidence']})")
        out.append("")

    out.append("---")
    out.append(f"CONFIDENTIAL — FOR INTERNAL USE ONLY · Version {m['version']}")
    return "\n".join(out)


def _detail_html(report):
    rows = []
    by_dim = {d["dimension"]: d for d in report["detailed"]}
    for dim in DIM_ORDER:
        d = by_dim[dim]
        cls = CSS_CLASS.get(d["score"], "")
        card_cls = cls.replace("result-", "dimension-") if cls else ""
        rows.append(f"<section class='dimension-card {card_cls}'>")
        rows.append(f"<h3><span class='{cls}'>{_e(dim)}</span> — {_e(d['focus_area'])} "
                    f"<span class='{cls}'>[{_e(_result(d['score']))}]</span></h3>")
        meta = []
        if d.get("confidence"):
            meta.append(f"<span>Confidence: <strong>{_e(str(d['confidence']).title())}</strong></span>")
        if d.get("evidence_basis"):
            meta.append(f"<span>Evidence: <strong>{_e(str(d['evidence_basis']).replace('_', ' '))}</strong></span>")
        if meta:
            rows.append("<div class='evidence-meta'>" + "".join(meta) + "</div>")
        rows.append(f"<p>{_rich(d['assessment'])}</p>")
        rows.append("<p class='subhead'>Trade-offs</p>")
        rows.append(f"<p><span class='gain'>+ Gain:</span> {_rich(d['trade_offs']['gain'])}<br>"
                    f"<span class='giveup'>− Give up:</span> {_rich(d['trade_offs']['give_up'])}</p>")
        if d.get("evidence_citations"):
            rows.append("<p class='subhead'>Evidence Base</p><ul class='evidence-list'>"
                        + "".join(f"<li>{_rich(c)}</li>" for c in d["evidence_citations"])
                        + "</ul>")
        rows.append("<p class='subhead'>Questions for Vendor</p><ul>"
                    + "".join(f"<li>{_rich(q)}</li>" for q in d["vendor_questions"]) + "</ul>")
        rows.append("</section>")
    return "\n".join(rows)


def _overview_html(report):
    body = ["<h2>Evaluation Overview</h2><table class='overview-table'><tr><th>Criterion</th><th>Focus Area</th><th>Result</th></tr>"]
    by_overview = {r["dimension"]: r for r in report["overview_table"]}
    for dim in DIM_ORDER:
        if dim in by_overview:
            row = by_overview[dim]
            body.append(f"<tr><td>{_e(row['dimension'])}</td><td>{_e(row['focus_area'])}</td>"
                        f"<td class='{CSS_CLASS.get(row['result'], '')}'>{_e(_result(row['result']))}</td></tr>")
    body.append("</table>")
    return "".join(body)


def _tradeoff_html(report):
    rows = ["<h2>Trade-off Summary</h2>"
            "<table class='tradeoff-table'><tr><th>Criterion</th><th>Result</th><th>You Gain</th><th>You Give Up</th></tr>"]
    by_tradeoff = {r["dimension"]: r for r in report["tradeoff_summary"]}
    for dim in DIM_ORDER:
        if dim in by_tradeoff:
            row = by_tradeoff[dim]
            cls = CSS_CLASS.get(row["result"], "")
            rows.append(f"<tr><td>{_e(row['dimension'])}</td>"
                        f"<td class='{cls}'>{_e(_result(row['result']))}</td>"
                        f"<td>{_rich(row['gain'])}</td><td>{_rich(row['give_up'])}</td></tr>")
    rows.append("</table>")
    return "\n".join(rows)


def render_html(report, template):
    es = report["executive_summary"]
    body = []
    body.append("<h2>Executive Summary</h2>")
    body.append(f"<p class='key-takeaway'><span class='kt-label'>KEY TAKEAWAY</span>{_rich(es['key_takeaway'])}</p>")
    for p in es["paragraphs"]:
        body.append(f"<p>{_rich(p)}</p>")
    body.append(f"<p>{_rich(es['suitability'])}</p>")
    body.append(_score_strip_html(report))
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
    m = report["meta"]
    html = template
    for tok, val in [("{{VENDOR}}", _e(m["vendor"])), ("{{CATEGORY}}", _e(m["category"])),
                     ("{{VERSION}}", _e(m["version"])), ("{{DATE}}", _e(m["date"])),
                     ("{{BODY}}", "\n".join(body))]:
        html = html.replace(tok, str(val))
    return html


def render_questions_html(report, template):
    items = []
    for q in report["vendor_questions"]:
        why = f"<br><em>{_rich(q['why_we_ask'])}</em>" if q.get("why_we_ask") else ""
        items.append(f"<li><strong>[{_e(q['dimension'])}]</strong> {_rich(q['question'])}{why}</li>")
    body = ("<h2>Questions for the Vendor</h2>"
            "<p>Sharp, specific questions the vendor can respond to. Substantive answers may move the diagnosis.</p>"
            "<ol>" + "".join(items) + "</ol>")
    m = report["meta"]
    html = template
    for tok, val in [("{{VENDOR}}", _e(m["vendor"])), ("{{CATEGORY}}", _e(m["category"])),
                     ("{{VERSION}}", _e(m["version"])), ("{{DATE}}", _e(m["date"])), ("{{BODY}}", body)]:
        html = html.replace(tok, str(val))
    return html


def main(report_path, out_dir):
    report = json.loads(Path(report_path).read_text())
    template_path = Path(__file__).resolve().parents[1] / "assets" / "report-template.html"
    template = template_path.read_text()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.md").write_text(render_markdown(report))
    (out / "report.html").write_text(render_html(report, template))
    (out / "questions.html").write_text(render_questions_html(report, template))
    print(f"Wrote report.md, report.html, questions.html to {out}")


if __name__ == "__main__":
    # Ensure scripts dir is on path for _constants import when run directly
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main(sys.argv[1], sys.argv[2])
