import shutil, subprocess
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "skills/feedforward-vendor-review/workflow/evaluate-vendor.workflow.js"

def test_has_meta_and_stages():
    t = F.read_text()
    assert "export const meta" in t
    assert "phase(" in t and "agent(" in t

@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_node_syntax_ok():
    # --check parses but does not execute
    r = subprocess.run(["node", "--check", str(F)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
