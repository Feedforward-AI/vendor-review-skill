from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "plugins/vendor-review/skills/feedforward-vendor-review/references/drift-check.md"

def test_symmetric_checks_and_immutability():
    t = F.read_text().lower()
    assert "generic" in t                 # anti-generic-creep flank
    assert "false generosity" in t or "too soft" in t   # anti-false-generosity flank
    assert "re-run" in t or "rerun" in t  # can re-run a slipped analyst
    assert "immutab" in t or "did not override" in t     # opinion-override guard
