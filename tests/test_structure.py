from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "vendor-review" / "skills" / "feedforward-vendor-review"

def test_core_directories_exist():
    for rel in [
        ".claude-plugin",
        "plugins/vendor-review/.claude-plugin",
        "plugins/vendor-review/.codex-plugin",
        "plugins/vendor-review/skills/feedforward-vendor-review/references/dimensions",
        "plugins/vendor-review/skills/feedforward-vendor-review/schemas",
        "plugins/vendor-review/skills/feedforward-vendor-review/scripts",
        "plugins/vendor-review/skills/feedforward-vendor-review/assets",
    ]:
        assert (ROOT / rel).is_dir(), f"missing dir: {rel}"
