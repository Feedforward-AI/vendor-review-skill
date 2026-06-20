from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "feedforward-vendor-review"

def test_core_directories_exist():
    for rel in [
        ".claude-plugin", "agents",
        "skills/feedforward-vendor-review/reference/dimensions",
        "skills/feedforward-vendor-review/schemas",
        "skills/feedforward-vendor-review/scripts",
        "skills/feedforward-vendor-review/assets",
    ]:
        assert (ROOT / rel).is_dir(), f"missing dir: {rel}"
