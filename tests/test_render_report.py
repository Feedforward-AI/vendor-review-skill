import json
from pathlib import Path
import render_report

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests/fixtures/sample_report.json"
TEMPLATE = (ROOT / "skills/feedforward-vendor-review/assets/report-template.html").read_text()

def load(): return json.loads(FIX.read_text())

def test_markdown_has_seven_sections_in_order():
    md = render_report.render_markdown(load())
    order = ["VENDOR EVALUATION REPORT", "Executive Summary", "Evaluation Overview",
             "Detailed Evaluation", "Trade-off Summary", "Key Questions",
             "CONFIDENTIAL"]
    idxs = [md.find(s) for s in order]
    assert all(i != -1 for i in idxs)
    assert idxs == sorted(idxs)

def test_markdown_dimension_order():
    md = render_report.render_markdown(load())
    pos = [md.find(f"### {d}") for d in ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]]
    assert all(p != -1 for p in pos) and pos == sorted(pos)

def test_insufficient_display_label():
    r = load()
    r["overview_table"][0]["result"] = "Insufficient"
    md = render_report.render_markdown(r)
    assert "Insufficient Information" in md

def test_html_applies_color_classes():
    r = load()
    html = render_report.render_html(r, TEMPLATE)
    assert "result-fail" in html and "result-pass" in html
    assert "result-partial" in html
    assert "{{BODY}}" not in html and r["meta"]["vendor"] in html

def test_html_applies_insufficient_class():
    r = load()
    # Set one detailed entry to Insufficient and sync its overview_table row
    r["detailed"][0]["score"] = "Insufficient"
    r["detailed"][0]["evidence_basis"] = "insufficient"
    r["detailed"][0]["evidence_citations"] = []
    dim = r["detailed"][0]["dimension"]
    for row in r["overview_table"]:
        if row["dimension"] == dim:
            row["result"] = "Insufficient"
    html = render_report.render_html(r, TEMPLATE)
    assert "result-insufficient" in html

def test_questions_html_standalone():
    html = render_report.render_questions_html(load(), TEMPLATE)
    assert "Questions for the Vendor" in html
    assert load()["vendor_questions"][0]["question"] in html

def test_html_has_tradeoff_summary_table():
    r = load()
    html = render_report.render_html(r, TEMPLATE)
    assert "Trade-off Summary" in html
    # At least one give_up value from the fixture must appear
    assert r["tradeoff_summary"][0]["give_up"] in html
    # All six dimension rows should be present
    for row in r["tradeoff_summary"]:
        assert row["dimension"] in html

def test_html_tradeoff_table_appears_after_detailed_before_key_questions():
    r = load()
    html = render_report.render_html(r, TEMPLATE)
    pos_detail = html.find("Detailed Evaluation")
    pos_tradeoff = html.find("Trade-off Summary")
    pos_key = html.find("Key Questions for Your Decision")
    assert pos_detail != -1 and pos_tradeoff != -1 and pos_key != -1
    assert pos_detail < pos_tradeoff < pos_key

def test_html_changelog_section_rendered():
    r = load()
    r["changelog"] = [
        {"dimension": "SEE", "change": "Score upgraded from Fail to Partial.", "evidence": "VQ-SEE-01 response"}
    ]
    html = render_report.render_html(r, TEMPLATE)
    assert "What changed after vendor response" in html
    assert "Score upgraded from Fail to Partial." in html
    assert "VQ-SEE-01 response" in html

def test_html_no_changelog_section_when_empty():
    r = load()
    r["changelog"] = []
    html = render_report.render_html(r, TEMPLATE)
    assert "What changed after vendor response" not in html
