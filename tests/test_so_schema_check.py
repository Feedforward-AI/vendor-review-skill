from so_schema_check import check_so_compliance

def test_compliant_schema_has_no_violations():
    schema = {
        "type": "object", "additionalProperties": False,
        "required": ["score"],
        "properties": {"score": {"enum": ["Pass", "Fail"]}},
    }
    assert check_so_compliance(schema) == []

def test_flags_unsupported_keyword():
    schema = {
        "type": "object", "additionalProperties": False,
        "required": ["name"],
        "properties": {"name": {"type": "string", "minLength": 2}},
    }
    v = check_so_compliance(schema)
    assert any("minLength" in s for s in v)

def test_flags_missing_additional_properties_false():
    schema = {"type": "object", "required": [], "properties": {}}
    assert any("additionalProperties" in s for s in check_so_compliance(schema))

def test_flags_property_not_required():
    schema = {
        "type": "object", "additionalProperties": False,
        "required": [], "properties": {"a": {"type": "string"}},
    }
    assert any("required" in s for s in check_so_compliance(schema))

def test_flags_bad_min_items():
    schema = {
        "type": "object", "additionalProperties": False, "required": ["xs"],
        "properties": {"xs": {"type": "array", "minItems": 3, "items": {"type": "string"}}},
    }
    assert any("minItems" in s for s in check_so_compliance(schema))
