"""Validate a JSON Schema against the Anthropic structured-outputs supported subset."""

UNSUPPORTED_KEYWORDS = {
    "minLength", "maxLength", "minimum", "maximum", "exclusiveMinimum",
    "exclusiveMaximum", "multipleOf", "patternProperties", "minProperties",
    "maxProperties", "minContains", "maxContains", "uniqueItems",
}

def check_so_compliance(schema, path="$"):
    violations = []
    if not isinstance(schema, dict):
        return violations

    for kw in UNSUPPORTED_KEYWORDS:
        if kw in schema:
            violations.append(f"{path}: unsupported keyword '{kw}'")

    if schema.get("type") == "object":
        if schema.get("additionalProperties", None) is not False:
            violations.append(f"{path}: objects must set additionalProperties: false")
        props = schema.get("properties", {})
        required = set(schema.get("required", []))
        for name in props:
            if name not in required:
                violations.append(f"{path}: property '{name}' must be in 'required'")
        for name, sub in props.items():
            violations += check_so_compliance(sub, f"{path}.{name}")

    if schema.get("type") == "array":
        if "minItems" in schema and schema["minItems"] not in (0, 1):
            violations.append(f"{path}: array minItems must be 0 or 1, got {schema['minItems']}")
        if "items" in schema:
            violations += check_so_compliance(schema["items"], f"{path}[]")

    # union via type arrays is discouraged; flag null unions
    t = schema.get("type")
    if isinstance(t, list) and "null" in t:
        violations.append(f"{path}: nullable union types are disallowed; use a sentinel")

    return violations
