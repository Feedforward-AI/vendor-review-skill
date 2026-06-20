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
