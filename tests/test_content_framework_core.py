from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "plugins/vendor-review/skills/feedforward-vendor-review/references/framework-core.md"

def test_anchors_present():
    t = F.read_text()
    # the one question
    assert "strengthen or weaken" in t.lower() or "build or erode" in t.lower()
    # all four score tokens
    for tok in ["Pass", "Partial", "Fail", "Insufficient"]:
        assert tok in t
    # critical rules
    assert "marketing claims are not evidence" in t.lower()
    assert "insufficient information" in t.lower()
    # explicit anti-generic + non-recommendation guardrails
    assert "not a generic" in t.lower()
    assert "not a decision-maker" in t.lower() or "buy/don" in t.lower()
    # informative-absence reconciliation
    assert "informative absence" in t.lower() or "conspicuous" in t.lower()
