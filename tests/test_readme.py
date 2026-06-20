from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
R = (ROOT / "README.md").read_text()

def test_install_commands_present():
    assert "/plugin marketplace add Feedforward-AI/vendor-review-skill" in R
    assert "/plugin install vendor-review@feedforward" in R

def test_framework_explained():
    for d in ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]:
        assert d in R
