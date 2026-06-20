from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "skills/feedforward-vendor-review/SKILL.md"

def test_frontmatter_and_pipeline():
    t = F.read_text()
    assert t.startswith("---")
    head = t.split("---", 2)[1].lower()
    assert "name: feedforward-vendor-review" in head
    assert "description:" in head
    body = t.lower()
    for stage in ["scope", "evidence", "dimension-analyst", "synthes", "drift", "render"]:
        assert stage in body, f"pipeline missing stage: {stage}"
    assert "review gate" in body and "10 min" in body.replace("minute", "min")
    assert "render_report.py" in body and "lint_report.py" in body
    assert "vendor response" in body or "rebuttal" in body
