from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "skills/feedforward-vendor-review/reference/dimensions"

NAMES = ["see", "change", "adapt", "use", "learn", "exit"]

def test_all_six_exist_with_scoring():
    for n in NAMES:
        t = (D / f"{n}.md").read_text()
        for tok in ["Pass", "Partial", "Fail", "Insufficient"]:
            assert tok in t, f"{n}.md missing score token {tok}"

def test_expectation_set_checklist_on_see_change_exit():
    for n in ["see", "change", "exit"]:
        t = (D / f"{n}.md").read_text().lower()
        assert "where you'd expect this documented" in t, f"{n}.md missing expectation-set checklist"
