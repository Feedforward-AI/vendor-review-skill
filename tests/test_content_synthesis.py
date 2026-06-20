from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "skills/feedforward-vendor-review/reference"

def test_exec_summary_spec():
    t = (R / "synthesis/executive-summary.md").read_text().lower()
    assert "key takeaway" in t and "sentiment" in t and "suitab" in t

def test_key_questions_spec():
    t = (R / "synthesis/key-questions.md").read_text().lower()
    assert "5" in t and "question" in t

def test_output_template_sections_in_order():
    t = (R / "output-template.md").read_text()
    order = ["Title block", "Executive Summary", "Evaluation Overview",
             "Detailed Evaluation", "Trade-off Summary", "Key Questions", "Footer"]
    idxs = [t.find(s) for s in order]
    assert all(i != -1 for i in idxs), idxs
    assert idxs == sorted(idxs), "sections out of order"
