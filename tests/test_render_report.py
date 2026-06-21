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

def test_html_does_not_crash_on_unexpected_score():
    # Structured outputs constrain the enum, but rendering must degrade gracefully
    # (CSS_CLASS.get fallback) rather than KeyError on an out-of-vocabulary score.
    r = load()
    r["detailed"][0]["score"] = "Conditional Pass"
    r["overview_table"][0]["result"] = "Conditional Pass"
    r["tradeoff_summary"][0]["result"] = "Conditional Pass"
    html = render_report.render_html(r, TEMPLATE)  # must not raise
    assert "Conditional Pass" in html


# --- FIX 1: HTML escaping tests ---

def test_html_escape_in_vendor_field():
    r = load()
    r["meta"]["vendor"] = '<script>x</script>'
    html = render_report.render_html(r, TEMPLATE)
    assert "&lt;script&gt;" in html
    assert "<script>x</script>" not in html

def test_html_escape_special_chars_in_dynamic_fields():
    """Inject XSS payloads and HTML-breaking chars into dynamic fields; assert they are escaped."""
    r = load()
    payload_script = '<script>x</script>'
    payload_amp = 'A & B'
    payload_quote = '"quoted"'
    # Inject into executive_summary fields
    r["executive_summary"]["key_takeaway"] = payload_script
    r["executive_summary"]["paragraphs"] = [payload_amp]
    r["executive_summary"]["suitability"] = payload_quote
    # Inject into a detailed dimension
    r["detailed"][0]["assessment"] = payload_script + " Two sentences here."
    r["detailed"][0]["trade_offs"]["gain"] = payload_amp
    r["detailed"][0]["trade_offs"]["give_up"] = payload_quote
    r["detailed"][0]["vendor_questions"][0] = payload_script
    # Inject into tradeoff_summary
    r["tradeoff_summary"][0]["gain"] = payload_script
    r["tradeoff_summary"][0]["give_up"] = payload_amp
    # Inject into overview focus_area
    r["overview_table"][0]["focus_area"] = payload_amp
    html = render_report.render_html(r, TEMPLATE)
    assert "&lt;script&gt;" in html
    assert "<script>x</script>" not in html
    assert "&amp;" in html
    assert "&quot;" in html

def test_html_escape_in_questions_html():
    """Vendor questions page also escapes injected content."""
    r = load()
    r["vendor_questions"][0]["question"] = '<script>x</script>'
    r["vendor_questions"][0]["why_we_ask"] = 'A & B'
    html = render_report.render_questions_html(r, TEMPLATE)
    assert "&lt;script&gt;" in html
    assert "<script>x</script>" not in html
    assert "&amp;" in html

def test_html_escape_in_changelog():
    """Changelog change/evidence fields are escaped."""
    r = load()
    r["changelog"] = [{"dimension": "SEE", "change": '<script>x</script>', "evidence": "A & B"}]
    html = render_report.render_html(r, TEMPLATE)
    assert "&lt;script&gt;" in html
    assert "<script>x</script>" not in html
    assert "&amp;" in html


# --- FIX 2: Table order tests ---

def test_html_overview_table_renders_in_dim_order():
    """overview_table renders in SEE→CHANGE→ADAPT→USE→LEARN→EXIT regardless of input order."""
    import copy
    r = load()
    # Shuffle overview_table to reverse order
    r["overview_table"] = list(reversed(r["overview_table"]))
    html = render_report.render_html(r, TEMPLATE)
    dims = ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]
    positions = [html.find(f"<td>{d}</td>") for d in dims]
    # All should appear and be in ascending position order
    assert all(p != -1 for p in positions), f"Not all dims found: {list(zip(dims, positions))}"
    assert positions == sorted(positions), f"Overview table not in DIM_ORDER: {list(zip(dims, positions))}"

def test_html_tradeoff_table_renders_in_dim_order():
    """tradeoff_summary renders in SEE→CHANGE→ADAPT→USE→LEARN→EXIT regardless of input order."""
    r = load()
    # Shuffle tradeoff_summary to reverse order
    r["tradeoff_summary"] = list(reversed(r["tradeoff_summary"]))
    html = render_report.render_html(r, TEMPLATE)
    dims = ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]
    # Find positions of each dimension in the tradeoff section
    tradeoff_start = html.find("Trade-off Summary")
    section = html[tradeoff_start:]
    positions = [section.find(f"<td>{d}</td>") for d in dims]
    assert all(p != -1 for p in positions), f"Not all dims found in tradeoff section: {list(zip(dims, positions))}"
    assert positions == sorted(positions), f"Tradeoff table not in DIM_ORDER: {list(zip(dims, positions))}"

def test_markdown_overview_table_renders_in_dim_order():
    """Markdown overview table renders in DIM_ORDER regardless of input order."""
    r = load()
    r["overview_table"] = list(reversed(r["overview_table"]))
    md = render_report.render_markdown(r)
    overview_start = md.find("## Evaluation Overview")
    detailed_start = md.find("## Detailed Evaluation")
    overview_section = md[overview_start:detailed_start]
    dims = ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]
    positions = [overview_section.find(f"| {d} |") for d in dims]
    assert all(p != -1 for p in positions), f"Not all dims in overview: {list(zip(dims, positions))}"
    assert positions == sorted(positions), f"Markdown overview not in DIM_ORDER"

def test_markdown_tradeoff_table_renders_in_dim_order():
    """Markdown tradeoff table renders in DIM_ORDER regardless of input order."""
    r = load()
    r["tradeoff_summary"] = list(reversed(r["tradeoff_summary"]))
    md = render_report.render_markdown(r)
    tradeoff_start = md.find("## Trade-off Summary")
    key_start = md.find("## Key Questions")
    tradeoff_section = md[tradeoff_start:key_start]
    dims = ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]
    positions = [tradeoff_section.find(f"| {d} |") for d in dims]
    assert all(p != -1 for p in positions), f"Not all dims in tradeoff: {list(zip(dims, positions))}"
    assert positions == sorted(positions), f"Markdown tradeoff not in DIM_ORDER"


# --- FIX A: Score/result display HTML escaping ---

def test_html_escape_score_in_detail_section():
    """Score with metacharacters in detailed evaluation must be HTML-escaped."""
    r = load()
    # Set a detailed entry's score to include metacharacters
    r["detailed"][0]["score"] = "Pa<b>ss"
    html = render_report.render_html(r, TEMPLATE)
    # Escaped version must appear, raw version must not
    assert "Pa&lt;b&gt;ss" in html
    assert "Pa<b>ss" not in html
    # Also check that the raw <b> tag did not get rendered
    assert "<b>ss</b>" not in html


def test_html_escape_result_in_overview_table():
    """Overview table result with metacharacters must be HTML-escaped."""
    r = load()
    # Set the overview_table result to include metacharacters
    r["overview_table"][0]["result"] = "Pa<b>ss"
    # Sync the detailed score too
    dim = r["overview_table"][0]["dimension"]
    for d in r["detailed"]:
        if d["dimension"] == dim:
            d["score"] = "Pa<b>ss"
    html = render_report.render_html(r, TEMPLATE)
    # Escaped version must appear in the table
    assert "Pa&lt;b&gt;ss" in html
    # Raw <b> must not appear as an HTML tag in result context
    assert "Pa<b>ss" not in html


def test_html_escape_result_in_tradeoff_table():
    """Tradeoff summary result with metacharacters must be HTML-escaped."""
    r = load()
    # Set the tradeoff_summary result to include metacharacters
    r["tradeoff_summary"][0]["result"] = "Pa<b>ss"
    # Sync the detailed and overview entries
    dim = r["tradeoff_summary"][0]["dimension"]
    for d in r["detailed"]:
        if d["dimension"] == dim:
            d["score"] = "Pa<b>ss"
    for o in r["overview_table"]:
        if o["dimension"] == dim:
            o["result"] = "Pa<b>ss"
    html = render_report.render_html(r, TEMPLATE)
    # Escaped version must appear
    assert "Pa&lt;b&gt;ss" in html
    # Raw version and stray <b> tag must not appear
    assert "Pa<b>ss" not in html


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


def test_html_emphasis_preserves_escaping_in_key_takeaway():
    r = load()
    r["executive_summary"]["key_takeaway"] = "*<b>bold</b>* and normal."
    html = render_report.render_html(r, TEMPLATE)
    assert "<b>bold</b>" not in html
    assert "<em>&lt;b&gt;bold&lt;/b&gt;</em>" in html

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
