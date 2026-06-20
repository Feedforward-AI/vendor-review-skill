import json
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

# --- _sentence_count robustness tests ---

def test_sentence_count_not_inflated_by_url():
    # "Access docs.vendor.com/api requires admin." is 1 sentence containing a URL-like token
    # Combined with a second real sentence → 2 sentences → should NOT be flagged
    text = "Access docs.vendor.com/api requires admin. You must have the correct role assigned."
    count = lint_report._sentence_count(text)
    assert 2 <= count <= 4, f"Expected 2-4 but got {count}"

def test_sentence_count_not_inflated_by_version():
    # "They run v1.0 of the model." contains a decimal/version but is 1 sentence
    # Add a second real sentence to make it legitimately 2
    text = "They run v1.0 of the model. Performance is consistent across regions."
    count = lint_report._sentence_count(text)
    assert 2 <= count <= 4, f"Expected 2-4 but got {count}"

def test_sentence_count_not_inflated_by_abbreviation():
    # "Uses RAG, e.g. retrieval." — the "e.g." should not split into an extra sentence
    # Add more real sentences to reach a valid 2-4 range
    text = "Uses RAG, e.g. retrieval augmentation. This improves answer quality significantly. The model performance is measurable."
    count = lint_report._sentence_count(text)
    assert 2 <= count <= 4, f"Expected 2-4 but got {count}"

def test_sentence_count_too_few_still_detected():
    # A single short sentence should still count as 1 (below the 2 minimum)
    count = lint_report._sentence_count("This is one sentence.")
    assert count == 1

def test_sentence_count_too_many_still_detected():
    # Five genuinely distinct sentences should count as 5 (above the 4 maximum)
    text = ("First sentence here. "
            "Second sentence follows. "
            "Third sentence is present. "
            "Fourth sentence is included. "
            "Fifth sentence exceeds the limit.")
    count = lint_report._sentence_count(text)
    assert count == 5

def test_lint_flags_too_few_sentences():
    r = base()
    r["detailed"][0]["assessment"] = "One sentence only."
    violations = lint_report.lint(r)
    assert any("assessment" in v and "sentence" in v for v in violations)

def test_lint_flags_too_many_sentences():
    r = base()
    r["detailed"][0]["assessment"] = (
        "First sentence. Second sentence. Third sentence. Fifth sentence. Sixth sentence."
    )
    violations = lint_report.lint(r)
    assert any("assessment" in v and "sentence" in v for v in violations)
