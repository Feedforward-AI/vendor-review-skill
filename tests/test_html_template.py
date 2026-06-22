import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "plugins/vendor-review/skills/feedforward-vendor-review/assets/report-template.html"

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
    for cls in ["key-takeaway", "kt-label", "subhead"]:
        assert cls in t, f"missing style hook {cls}"

    # Dual sizing: the screen baseline (17px) and the faithful print baseline (11pt)
    # must each live inside their own media query — no unconditional :root font-size
    # that would shadow one of them.
    screen = re.search(r"@media screen\s*\{[^}]*:root\s*\{\s*font-size:\s*17px", t)
    printq = re.search(r"@media print\s*\{[^}]*:root\s*\{\s*font-size:\s*11pt", t)
    assert screen, "screen baseline (17px) not set inside @media screen"
    assert printq, "print baseline (11pt) not set inside @media print"
    # 11pt must appear ONLY as the print override, never as an unconditional rule.
    assert t.count("11pt") == 1, "11pt should appear once, inside @media print"

def test_report_layout_style_hooks():
    t = F.read_text()
    for cls in ["report-shell", "score-grid", "score-card", "dimension-card", "evidence-meta", "evidence-list"]:
        assert cls in t, f"missing report layout hook {cls}"
