from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "skills/feedforward-vendor-review/assets/report-template.html"

def test_tokens_and_color_classes():
    t = F.read_text()
    for tok in ["{{VENDOR}}", "{{CATEGORY}}", "{{VERSION}}", "{{DATE}}", "{{BODY}}"]:
        assert tok in t
    for cls in ["result-pass", "result-partial", "result-fail", "result-insufficient"]:
        assert cls in t
    assert "<style" in t  # inlined CSS, self-contained

def test_design_system_tokens_and_dual_sizing():
    t = F.read_text()
    for token in ["--ink", "--body", "--pass", "--partial", "--fail", "--insufficient", "--rule", "--header-bg"]:
        assert token in t, f"missing token {token}"
    assert "Calibri" in t
    assert "Carlito" in t
    assert "@media print" in t
    assert "@media screen" in t
    assert "11pt" in t  # faithful print baseline
    for cls in ["key-takeaway", "kt-label", "subhead"]:
        assert cls in t, f"missing style hook {cls}"
