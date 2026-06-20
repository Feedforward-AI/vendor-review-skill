from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "agents/dimension-analyst.md"

def test_frontmatter_and_harness():
    t = F.read_text()
    assert t.startswith("---"), "must have YAML frontmatter"
    head = t.split("---", 2)[1].lower()
    assert "name:" in head and "description:" in head
    body = t.lower()
    assert "framework-core" in body          # injects the law
    assert "not a generic" in body           # negative instruction
    assert "dimension-result" in body        # output contract
    assert "marketing claims are not evidence" in body
