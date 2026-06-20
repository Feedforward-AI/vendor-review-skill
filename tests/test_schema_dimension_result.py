import json
from pathlib import Path
import jsonschema
from so_schema_check import check_so_compliance

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "skills/feedforward-vendor-review/schemas/dimension-result.schema.json"
def load(): return json.loads(SCHEMA.read_text())

def test_so_compliant():
    assert check_so_compliance(load()) == []

def test_score_enum():
    assert load()["properties"]["score"]["enum"] == ["Pass", "Partial", "Fail", "Insufficient"]

def test_evidence_basis_is_superset():
    assert load()["properties"]["evidence_basis"]["enum"] == [
        "verified", "vendor_claim", "inferred", "informative_absence", "user_provided", "insufficient"]

def test_valid_instance():
    inst = {"dimension": "EXIT", "focus_area": "Portability & Migration",
            "score": "Fail", "assessment": "No documented export endpoint.",
            "trade_offs": {"gain": "—", "give_up": "Workflows are trapped."},
            "vendor_questions": ["Can workflows be exported as JSON?"],
            "confidence": "medium", "evidence_basis": "informative_absence",
            "evidence_citations": ["f1"]}
    jsonschema.validate(inst, load())
