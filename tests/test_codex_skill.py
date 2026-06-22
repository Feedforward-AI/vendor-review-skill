from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "vendor-review"
CODEX_SKILL = PLUGIN / "skills" / "feedforward-vendor-review"


def test_codex_skill_structure():
    assert (PLUGIN / ".codex-plugin" / "plugin.json").is_file()
    assert (CODEX_SKILL / "SKILL.md").is_file()
    assert (CODEX_SKILL / "agents" / "openai.yaml").is_file()
    for rel in [
        "references/framework-core.md",
        "references/dimension-analyst.md",
        "references/dimensions/see.md",
        "references/synthesis/executive-summary.md",
        "schemas/report.schema.json",
        "scripts/render_report.py",
        "scripts/lint_report.py",
        "assets/report-template.html",
        "examples/glean/expected-scores.json",
    ]:
        assert (CODEX_SKILL / rel).exists(), f"missing Codex resource: {rel}"


def test_codex_skill_metadata_and_instructions():
    text = (CODEX_SKILL / "SKILL.md").read_text()
    head = text.split("---", 2)[1]
    assert "name: feedforward-vendor-review" in head
    assert "description:" in head
    assert "[TODO" not in text
    assert "platform-neutral Agent Skill" in text
    assert "host-specific plugin manifests" in text
    assert "references/" in text
    assert "reference/framework-core.md" not in text
    assert "agents/dimension-analyst.md" not in text


def test_codex_openai_yaml():
    text = (CODEX_SKILL / "agents" / "openai.yaml").read_text()
    assert 'display_name: "Feedforward Vendor Review"' in text
    assert 'short_description: "Evaluate AI vendors for AI capacity"' in text
    assert "$feedforward-vendor-review" in text
