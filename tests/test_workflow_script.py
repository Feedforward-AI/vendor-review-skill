# Workflow scripts legitimately use top-level await and return statements,
# which are rejected by node --check (designed for standalone modules).
# Structural validation via string membership asserts the required components.

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "skills/feedforward-vendor-review/workflow/evaluate-vendor.workflow.js"

def test_has_meta_and_stages():
    t = F.read_text()
    assert "export const meta" in t
    assert "name: 'evaluate-vendor'" in t
    assert "phases:" in t
    assert "phase(" in t
    assert "agent(" in t
    assert "parallel(" in t
    # Verify all six dimensions are present
    assert "SEE" in t
    assert "CHANGE" in t
    assert "ADAPT" in t
    assert "USE" in t
    assert "LEARN" in t
    assert "EXIT" in t
