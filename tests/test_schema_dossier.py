import json
from pathlib import Path
import jsonschema
from so_schema_check import check_so_compliance

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "skills/feedforward-vendor-review/schemas/evidence-dossier.schema.json"

def load(): return json.loads(SCHEMA.read_text())

def test_so_compliant():
    assert check_so_compliance(load()) == []

def test_evidence_strength_enum():
    fact = load()["properties"]["facts"]["items"]["properties"]["evidence_strength"]["enum"]
    assert fact == ["verified", "vendor_claim", "inferred", "informative_absence", "user_provided"]

def test_valid_instance_passes():
    inst = {
      "vendor": {"name": "X", "url": "https://x.com", "category": "AI Software"},
      "scope_check": {"is_ai_b2b_saas": True, "rationale": "uses LLMs"},
      "facts": [{
        "id": "f1", "claim": "no prompt editing documented",
        "dimensions": ["SEE"], "source_type": "vendor_docs",
        "source_ref": "docs.x.com/api", "quote": "",
        "evidence_strength": "informative_absence",
        "expectation_set": "API ref, admin docs", "confidence": "medium"}],
      "gaps": [{"dimension": "SEE", "missing": "system prompt access",
                "suggested_vendor_question": "Can you edit the system prompt?"}]
    }
    jsonschema.validate(inst, load())

def test_extra_property_rejected():
    import pytest
    inst = {"vendor": {"name":"X","url":"u","category":"c"},
            "scope_check": {"is_ai_b2b_saas": True, "rationale": "r"},
            "facts": [], "gaps": [], "EXTRA": 1}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(inst, load())
