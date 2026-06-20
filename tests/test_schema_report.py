import json
from pathlib import Path
import jsonschema
from so_schema_check import check_so_compliance

ROOT = Path(__file__).resolve().parents[1]
SCH = ROOT / "skills/feedforward-vendor-review/schemas"
def load(n): return json.loads((SCH / n).read_text())

def test_both_so_compliant():
    assert check_so_compliance(load("vendor-question.schema.json")) == []
    assert check_so_compliance(load("report.schema.json")) == []

def test_why_we_ask_required():
    vq = load("vendor-question.schema.json")
    assert "why_we_ask" in vq["required"]

def test_flags_dimension_includes_overall():
    flags = load("report.schema.json")["properties"]["flags"]["items"]
    assert "OVERALL" in flags["properties"]["dimension"]["enum"]

def test_sentiment_enum():
    meta = load("report.schema.json")["properties"]["meta"]["properties"]
    assert meta["sentiment"]["enum"] == ["positive", "neutral", "negative"]

def test_valid_minimal_report():
    dim = {"dimension": "SEE", "focus_area": "Transparency & Visibility",
           "score": "Fail", "assessment": "Black box.",
           "trade_offs": {"gain": "Simple UI", "give_up": "No audit"},
           "vendor_questions": ["What model powers answers?"],
           "confidence": "high", "evidence_basis": "informative_absence",
           "evidence_citations": ["f1"]}
    report = {
      "meta": {"vendor": "X", "category": "AI Software", "version": "1.0",
               "date": "June 2026", "sentiment": "negative"},
      "executive_summary": {"key_takeaway": "k", "paragraphs": ["p"], "suitability": "s"},
      "overview_table": [{"dimension": "SEE", "focus_area": "Transparency & Visibility", "result": "Fail"}],
      "detailed": [dim],
      "tradeoff_summary": [{"dimension": "SEE", "result": "Fail", "gain": "Simple UI", "give_up": "No audit"}],
      "key_questions": ["Is AI fluency a priority?"],
      "vendor_questions": [{"id": "SEE-1", "dimension": "SEE", "question": "q",
                            "why_we_ask": "", "current_basis": "informative_absence",
                            "what_would_change": "doc moves Fail->Partial"}],
      "flags": [{"dimension": "OVERALL", "type": "org_context_dependent", "note": "n"}],
      "changelog": []
    }
    jsonschema.validate(report, load("report.schema.json"))
