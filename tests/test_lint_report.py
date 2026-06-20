import json, copy
from pathlib import Path
import lint_report

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests/fixtures/sample_report.json"
def base(): return json.loads(FIX.read_text())

def test_clean_report_passes():
    assert lint_report.lint(base()) == []

def test_detects_too_many_questions():
    r = base()
    r["detailed"][0]["vendor_questions"] = ["a?", "b?", "c?", "d?"]
    assert any("vendor_questions" in v for v in lint_report.lint(r))

def test_detects_missing_citation_on_scored_dimension():
    r = base()
    d = next(x for x in r["detailed"] if x["score"] != "Insufficient")
    d["evidence_citations"] = []
    assert any("citation" in v.lower() for v in lint_report.lint(r))

def test_detects_informative_absence_high_confidence():
    r = base()
    r["detailed"][0]["evidence_basis"] = "informative_absence"
    r["detailed"][0]["confidence"] = "high"
    assert any("informative_absence" in v for v in lint_report.lint(r))

def test_detects_overview_score_mismatch():
    r = base()
    # flip overview result away from detailed score
    dim = r["detailed"][0]["dimension"]
    for row in r["overview_table"]:
        if row["dimension"] == dim:
            row["result"] = "Pass" if r["detailed"][0]["score"] != "Pass" else "Fail"
    assert any("overview" in v.lower() for v in lint_report.lint(r))
