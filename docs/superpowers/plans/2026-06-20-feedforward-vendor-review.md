# Feedforward Vendor Review Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code plugin — distributed through a self-hosting marketplace repo — that evaluates an AI-powered software vendor against Feedforward's opinionated six-dimension capacity framework (SEE/CHANGE/ADAPT/USE/LEARN/EXIT) and produces a board-grade Markdown + print-to-PDF report.

**Architecture:** One skill owns the immutable framework as read-only reference files. `SKILL.md` orchestrates six "dimension-analyst" subagents over a shared, source-tagged evidence dossier, then synthesizes, runs a symmetric drift check, and renders. Structured-output JSON schemas hard-lock the scoring vocabulary and forbid generic-review fields. Two stdlib-only Python scripts render and lint the report. A deterministic Workflow script is an optional accelerator.

**Tech Stack:** Markdown instruction files; JSON Schema (structured-outputs subset); Python 3 standard library (runtime scripts); self-contained HTML/CSS; Claude Code plugin + marketplace manifests. Dev/test only: `pytest`, `jsonschema`.

**Spec:** `docs/superpowers/specs/2026-06-20-feedforward-vendor-review-design.md` (18 sections). Source framework docs and four golden sample reports (Glean, Harvey, Conveo, Legora) are in `./source_docs`.

## Global Constraints

Every task implicitly includes these (verbatim from the spec):

- **Runtime scripts are Python 3 standard library ONLY.** No `pandoc`, `poppler`, `jsonschema`, or markdown libraries at runtime. (`pytest` + `jsonschema` are dev-only test deps.)
- **All JSON schemas conform to the structured-outputs supported subset:** every object sets `"additionalProperties": false`; every property appears in `"required"`; controlled vocabularies are `"enum"`; NO `minLength`/`maxLength`/`minimum`/`maximum`/`multipleOf`; arrays use `minItems` only with value `0` or `1`; no nullable unions; empties expressed via sentinels (`"—"`, `""`, `[]`).
- **Scoring vocabulary (fixed):** enum tokens `Pass | Partial | Fail | Insufficient`; the renderer maps `Insufficient` → display label "Insufficient Information".
- **`evidence_strength` enum (dossier facts):** `verified | vendor_claim | inferred | informative_absence | user_provided`.
- **`evidence_basis` enum (dimension result) is a superset:** `verified | vendor_claim | inferred | informative_absence | user_provided | insufficient`.
- **`flags.dimension` enum:** `SEE | CHANGE | ADAPT | USE | LEARN | EXIT | OVERALL` (OVERALL = report-level flags).
- **Six dimensions, fixed report order:** SEE, CHANGE, ADAPT, USE, LEARN, EXIT.
- **Immutable "read-only law" files** (never paraphrased at runtime; injected verbatim): `reference/framework-core.md`, `reference/dimensions/*.md`, `reference/drift-check.md`.
- **Naming:** marketplace `feedforward` · plugin `vendor-review` · skill `feedforward-vendor-review` · repo `Feedforward-AI/vendor-review-skill`.
- **Model target:** `claude-opus-4-8`.
- **Color scheme:** Pass = green, Partial = amber, Fail = red, Insufficient = grey. HTML is self-contained (inlined CSS); board PDF via browser Print → PDF.
- **Auto-finalize default ≈ 10 minutes** (configurable; unattended mode only — interactive/one-shot do not wait).
- **The skill is an analyst, not a decision-maker.** It never makes buy/don't-buy recommendations and never produces a generic Gartner-style review.

## File Structure

```
vendor-review-skill/                              ← repo root = marketplace + plugin
├── .claude-plugin/marketplace.json               # marketplace "feedforward", lists plugin, source "./"
├── .claude-plugin/plugin.json                    # plugin "vendor-review"
├── agents/dimension-analyst.md                   # ★ analyst harness (custom subagent)
├── skills/feedforward-vendor-review/
│   ├── SKILL.md                                  # orchestration spine + trigger frontmatter
│   ├── reference/framework-core.md               # ★ IMMUTABLE
│   ├── reference/dimensions/{see,change,adapt,use,learn,exit}.md   # ★ IMMUTABLE
│   ├── reference/synthesis/{executive-summary,key-questions}.md
│   ├── reference/output-template.md
│   ├── reference/drift-check.md                  # ★ IMMUTABLE
│   ├── schemas/{evidence-dossier,dimension-result,vendor-question,report}.schema.json
│   ├── assets/report-template.html
│   ├── scripts/so_schema_check.py                # SO-subset compliance checker (shared by tests)
│   ├── scripts/render_report.py                  # report.json → report.md + report.html + questions.html
│   ├── scripts/lint_report.py                    # Tier-2 semantic validation
│   ├── scripts/eval_concordance.py               # golden score/theme concordance
│   ├── workflow/evaluate-vendor.workflow.js      # OPTIONAL deterministic accelerator
│   └── examples/{glean,harvey,conveo,legora}/expected-scores.json
├── tests/                                         # pytest (dev only)
│   ├── conftest.py
│   └── fixtures/
├── requirements-dev.txt
├── README.md
├── LICENSE
└── .gitignore
```

---

### Task 1: Repo scaffolding & dev tooling

**Files:**
- Create: `.gitignore`, `requirements-dev.txt`, `tests/conftest.py`, `LICENSE`, `README.md` (skeleton)
- Test: `tests/test_structure.py`

**Interfaces:**
- Produces: a `conftest.py` that puts `skills/feedforward-vendor-review/scripts` on `sys.path` so tests can `import so_schema_check, render_report, lint_report, eval_concordance`.

- [ ] **Step 1: Initialize repo and directory tree**

```bash
cd /home/exedev/Documents/vendor_review_skill   # or the chosen worktree
git init
mkdir -p .claude-plugin agents \
  skills/feedforward-vendor-review/{reference/dimensions,reference/synthesis,schemas,assets,scripts,workflow,examples} \
  tests/fixtures
```

- [ ] **Step 2: Write `.gitignore`, `requirements-dev.txt`, `conftest.py`**

`.gitignore`:
```
__pycache__/
*.pyc
.pytest_cache/
build/
*.egg-info/
```

`requirements-dev.txt`:
```
pytest>=8.0
jsonschema>=4.21
```

`tests/conftest.py`:
```python
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "feedforward-vendor-review" / "scripts"
sys.path.insert(0, str(SCRIPTS))
```

- [ ] **Step 3: Write the failing structure test**

`tests/test_structure.py`:
```python
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
```

- [ ] **Step 4: Install deps and run the test**

Run: `python -m pip install -r requirements-dev.txt && python -m pytest tests/test_structure.py -v`
Expected: PASS.

- [ ] **Step 5: Write a minimal `README.md` and a LICENSE**

`README.md` (skeleton — expanded in Task 18):
```markdown
# Feedforward Vendor Review

A Claude Code skill that evaluates AI-powered software vendors against Feedforward's six-dimension framework for independent AI capacity.
```
`LICENSE`: choose the license Feedforward wants (placeholder: copy an MIT or proprietary text the owner provides). If unknown at build time, create `LICENSE` containing `All rights reserved. © Feedforward.` and flag for the owner to finalize.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore: scaffold vendor-review-skill repo and dev tooling"
```

---

### Task 2: Plugin & marketplace manifests

**Files:**
- Create: `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`
- Test: `tests/test_manifests.py`

**Interfaces:**
- Produces: the marketplace name `feedforward` and plugin name `vendor-review` consumed by install commands and the README.

- [ ] **Step 1: Write the failing manifest test**

`tests/test_manifests.py`:
```python
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def _load(p):
    return json.loads((ROOT / p).read_text())

def test_marketplace_manifest():
    m = _load(".claude-plugin/marketplace.json")
    assert m["name"] == "feedforward"
    plugins = {p["name"]: p for p in m["plugins"]}
    assert "vendor-review" in plugins
    assert plugins["vendor-review"]["source"] == "./"

def test_plugin_manifest():
    p = _load(".claude-plugin/plugin.json")
    assert p["name"] == "vendor-review"
    assert "version" in p and "description" in p
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `python -m pytest tests/test_manifests.py -v`
Expected: FAIL (files missing).

- [ ] **Step 3: Write the manifests**

`.claude-plugin/marketplace.json`:
```json
{
  "name": "feedforward",
  "owner": { "name": "Feedforward", "url": "https://github.com/Feedforward-AI" },
  "metadata": { "description": "Feedforward's AI-vendor capacity-evaluation tools." },
  "plugins": [
    {
      "name": "vendor-review",
      "description": "Evaluate an AI-powered software vendor against Feedforward's six-dimension framework for independent AI capacity (SEE/CHANGE/ADAPT/USE/LEARN/EXIT).",
      "version": "0.1.0",
      "author": { "name": "Feedforward", "url": "https://github.com/Feedforward-AI" },
      "source": "./",
      "category": "productivity",
      "homepage": "https://github.com/Feedforward-AI/vendor-review-skill"
    }
  ]
}
```

`.claude-plugin/plugin.json`:
```json
{
  "name": "vendor-review",
  "version": "0.1.0",
  "description": "Evaluate an AI-powered software vendor against Feedforward's six-dimension framework for independent AI capacity (SEE/CHANGE/ADAPT/USE/LEARN/EXIT).",
  "author": { "name": "Feedforward", "url": "https://github.com/Feedforward-AI" },
  "homepage": "https://github.com/Feedforward-AI/vendor-review-skill",
  "repository": "https://github.com/Feedforward-AI/vendor-review-skill",
  "license": "UNLICENSED",
  "keywords": ["ai", "vendor-evaluation", "procurement", "feedforward", "capacity"]
}
```

- [ ] **Step 4: Run the test to confirm it passes**

Run: `python -m pytest tests/test_manifests.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .claude-plugin tests/test_manifests.py
git commit -m "feat: add plugin and marketplace manifests"
```

---

### Task 3: Structured-outputs subset compliance checker

**Files:**
- Create: `skills/feedforward-vendor-review/scripts/so_schema_check.py`
- Test: `tests/test_so_schema_check.py`

**Interfaces:**
- Produces: `check_so_compliance(schema: dict) -> list[str]` — returns a list of human-readable violation strings; empty list means compliant. Used by every schema test (Tasks 4–7).

- [ ] **Step 1: Write the failing test**

`tests/test_so_schema_check.py`:
```python
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
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `python -m pytest tests/test_so_schema_check.py -v`
Expected: FAIL (module missing).

- [ ] **Step 3: Implement `so_schema_check.py` (stdlib only)**

```python
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
```

- [ ] **Step 4: Run the test to confirm it passes**

Run: `python -m pytest tests/test_so_schema_check.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/feedforward-vendor-review/scripts/so_schema_check.py tests/test_so_schema_check.py
git commit -m "feat: add structured-outputs subset compliance checker"
```

---

### Task 4: Evidence-dossier schema

**Files:**
- Create: `skills/feedforward-vendor-review/schemas/evidence-dossier.schema.json`
- Test: `tests/test_schema_dossier.py`

**Interfaces:**
- Consumes: `check_so_compliance` (Task 3).
- Produces: the dossier schema with fact `evidence_strength` enum (5 values) and `source_type` enum.

- [ ] **Step 1: Write the failing test**

`tests/test_schema_dossier.py`:
```python
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
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `python -m pytest tests/test_schema_dossier.py -v`
Expected: FAIL (schema missing).

- [ ] **Step 3: Write `evidence-dossier.schema.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "additionalProperties": false,
  "required": ["vendor", "scope_check", "facts", "gaps"],
  "properties": {
    "vendor": {
      "type": "object", "additionalProperties": false,
      "required": ["name", "url", "category"],
      "properties": {
        "name": {"type": "string"},
        "url": {"type": "string"},
        "category": {"type": "string"}
      }
    },
    "scope_check": {
      "type": "object", "additionalProperties": false,
      "required": ["is_ai_b2b_saas", "rationale"],
      "properties": {
        "is_ai_b2b_saas": {"type": "boolean"},
        "rationale": {"type": "string"}
      }
    },
    "facts": {
      "type": "array",
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["id", "claim", "dimensions", "source_type", "source_ref",
                     "quote", "evidence_strength", "expectation_set", "confidence"],
        "properties": {
          "id": {"type": "string"},
          "claim": {"type": "string"},
          "dimensions": {"type": "array", "minItems": 1,
            "items": {"enum": ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]}},
          "source_type": {"enum": ["vendor_docs", "third_party", "user_material", "vendor_response"]},
          "source_ref": {"type": "string"},
          "quote": {"type": "string"},
          "evidence_strength": {"enum": ["verified", "vendor_claim", "inferred", "informative_absence", "user_provided"]},
          "expectation_set": {"type": "string"},
          "confidence": {"enum": ["high", "medium", "low"]}
        }
      }
    },
    "gaps": {
      "type": "array",
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["dimension", "missing", "suggested_vendor_question"],
        "properties": {
          "dimension": {"enum": ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]},
          "missing": {"type": "string"},
          "suggested_vendor_question": {"type": "string"}
        }
      }
    }
  }
}
```

- [ ] **Step 4: Run the test to confirm it passes**

Run: `python -m pytest tests/test_schema_dossier.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/feedforward-vendor-review/schemas/evidence-dossier.schema.json tests/test_schema_dossier.py
git commit -m "feat: add evidence-dossier schema"
```

---

### Task 5: Dimension-result schema

**Files:**
- Create: `skills/feedforward-vendor-review/schemas/dimension-result.schema.json`
- Test: `tests/test_schema_dimension_result.py`

**Interfaces:**
- Consumes: `check_so_compliance`.
- Produces: the per-analyst result schema (`score`, `evidence_basis` superset, `vendor_questions` minItems 1) — embedded by `report.schema.json` (Task 7).

- [ ] **Step 1: Write the failing test**

`tests/test_schema_dimension_result.py`:
```python
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
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `python -m pytest tests/test_schema_dimension_result.py -v` → FAIL.

- [ ] **Step 3: Write `dimension-result.schema.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "additionalProperties": false,
  "required": ["dimension", "focus_area", "score", "assessment", "trade_offs",
               "vendor_questions", "confidence", "evidence_basis", "evidence_citations"],
  "properties": {
    "dimension": {"enum": ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]},
    "focus_area": {"type": "string"},
    "score": {"enum": ["Pass", "Partial", "Fail", "Insufficient"]},
    "assessment": {"type": "string"},
    "trade_offs": {
      "type": "object", "additionalProperties": false,
      "required": ["gain", "give_up"],
      "properties": {"gain": {"type": "string"}, "give_up": {"type": "string"}}
    },
    "vendor_questions": {"type": "array", "minItems": 1, "items": {"type": "string"}},
    "confidence": {"enum": ["high", "medium", "low"]},
    "evidence_basis": {"enum": ["verified", "vendor_claim", "inferred", "informative_absence", "user_provided", "insufficient"]},
    "evidence_citations": {"type": "array", "items": {"type": "string"}}
  }
}
```

- [ ] **Step 4: Run the test to confirm it passes** → PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/feedforward-vendor-review/schemas/dimension-result.schema.json tests/test_schema_dimension_result.py
git commit -m "feat: add dimension-result schema"
```

---

### Task 6: Vendor-question & report schemas

**Files:**
- Create: `skills/feedforward-vendor-review/schemas/vendor-question.schema.json`, `skills/feedforward-vendor-review/schemas/report.schema.json`
- Test: `tests/test_schema_report.py`

**Interfaces:**
- Consumes: `check_so_compliance`; the dimension-result shape (Task 5) re-expressed inline in `report.schema.json` (`$ref` to external files is unsupported in the SO subset, so the detailed-result shape is inlined).
- Produces: `report.schema.json` — the single render source of truth consumed by `render_report.py` (Task 15) and `lint_report.py` (Task 16); `vendor-question.schema.json` with `why_we_ask` **required**.

- [ ] **Step 1: Write the failing test**

`tests/test_schema_report.py`:
```python
import json
from pathlib import Path
import jsonschema
from so_schema_check import check_so_compliance

ROOT = Path(__file__).resolve().parents[1]
SCH = ROOT / "skills/feedforward-vendor-review/schemas"
def load(n): return json.loads((SCH / n).read_text())

def test_both_so_compliant():
    assert check_so_compliance(load("vendor-question.schema.json")) == []
    assert check_so_compliance(load("report.schema.json")) == []

def test_why_we_ask_required():
    vq = load("vendor-question.schema.json")
    assert "why_we_ask" in vq["required"]

def test_flags_dimension_includes_overall():
    flags = load("report.schema.json")["properties"]["flags"]["items"]
    assert "OVERALL" in flags["properties"]["dimension"]["enum"]

def test_sentiment_enum():
    meta = load("report.schema.json")["properties"]["meta"]["properties"]
    assert meta["sentiment"]["enum"] == ["positive", "neutral", "negative"]

def test_valid_minimal_report():
    dim = {"dimension": "SEE", "focus_area": "Transparency & Visibility",
           "score": "Fail", "assessment": "Black box.",
           "trade_offs": {"gain": "Simple UI", "give_up": "No audit"},
           "vendor_questions": ["What model powers answers?"],
           "confidence": "high", "evidence_basis": "informative_absence",
           "evidence_citations": ["f1"]}
    report = {
      "meta": {"vendor": "X", "category": "AI Software", "version": "1.0",
               "date": "June 2026", "sentiment": "negative"},
      "executive_summary": {"key_takeaway": "k", "paragraphs": ["p"], "suitability": "s"},
      "overview_table": [{"dimension": "SEE", "focus_area": "Transparency & Visibility", "result": "Fail"}],
      "detailed": [dim],
      "tradeoff_summary": [{"dimension": "SEE", "result": "Fail", "gain": "Simple UI", "give_up": "No audit"}],
      "key_questions": ["Is AI fluency a priority?"],
      "vendor_questions": [{"id": "SEE-1", "dimension": "SEE", "question": "q",
                            "why_we_ask": "", "current_basis": "informative_absence",
                            "what_would_change": "doc moves Fail->Partial"}],
      "flags": [{"dimension": "OVERALL", "type": "org_context_dependent", "note": "n"}],
      "changelog": []
    }
    jsonschema.validate(report, load("report.schema.json"))
```

- [ ] **Step 2: Run it to confirm it fails** → FAIL.

- [ ] **Step 3: Write `vendor-question.schema.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "dimension", "question", "why_we_ask", "current_basis", "what_would_change"],
  "properties": {
    "id": {"type": "string"},
    "dimension": {"enum": ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]},
    "question": {"type": "string"},
    "why_we_ask": {"type": "string"},
    "current_basis": {"type": "string"},
    "what_would_change": {"type": "string"}
  }
}
```

- [ ] **Step 4: Write `report.schema.json`** (dimension-result inlined; vendor-question inlined)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "additionalProperties": false,
  "required": ["meta", "executive_summary", "overview_table", "detailed",
               "tradeoff_summary", "key_questions", "vendor_questions", "flags", "changelog"],
  "properties": {
    "meta": {
      "type": "object", "additionalProperties": false,
      "required": ["vendor", "category", "version", "date", "sentiment"],
      "properties": {
        "vendor": {"type": "string"}, "category": {"type": "string"},
        "version": {"type": "string"}, "date": {"type": "string"},
        "sentiment": {"enum": ["positive", "neutral", "negative"]}
      }
    },
    "executive_summary": {
      "type": "object", "additionalProperties": false,
      "required": ["key_takeaway", "paragraphs", "suitability"],
      "properties": {
        "key_takeaway": {"type": "string"},
        "paragraphs": {"type": "array", "items": {"type": "string"}},
        "suitability": {"type": "string"}
      }
    },
    "overview_table": {
      "type": "array",
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["dimension", "focus_area", "result"],
        "properties": {
          "dimension": {"enum": ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]},
          "focus_area": {"type": "string"},
          "result": {"enum": ["Pass", "Partial", "Fail", "Insufficient"]}
        }
      }
    },
    "detailed": {
      "type": "array",
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["dimension", "focus_area", "score", "assessment", "trade_offs",
                     "vendor_questions", "confidence", "evidence_basis", "evidence_citations"],
        "properties": {
          "dimension": {"enum": ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]},
          "focus_area": {"type": "string"},
          "score": {"enum": ["Pass", "Partial", "Fail", "Insufficient"]},
          "assessment": {"type": "string"},
          "trade_offs": {
            "type": "object", "additionalProperties": false,
            "required": ["gain", "give_up"],
            "properties": {"gain": {"type": "string"}, "give_up": {"type": "string"}}
          },
          "vendor_questions": {"type": "array", "minItems": 1, "items": {"type": "string"}},
          "confidence": {"enum": ["high", "medium", "low"]},
          "evidence_basis": {"enum": ["verified", "vendor_claim", "inferred", "informative_absence", "user_provided", "insufficient"]},
          "evidence_citations": {"type": "array", "items": {"type": "string"}}
        }
      }
    },
    "tradeoff_summary": {
      "type": "array",
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["dimension", "result", "gain", "give_up"],
        "properties": {
          "dimension": {"enum": ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]},
          "result": {"enum": ["Pass", "Partial", "Fail", "Insufficient"]},
          "gain": {"type": "string"}, "give_up": {"type": "string"}
        }
      }
    },
    "key_questions": {"type": "array", "items": {"type": "string"}},
    "vendor_questions": {
      "type": "array",
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["id", "dimension", "question", "why_we_ask", "current_basis", "what_would_change"],
        "properties": {
          "id": {"type": "string"},
          "dimension": {"enum": ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]},
          "question": {"type": "string"}, "why_we_ask": {"type": "string"},
          "current_basis": {"type": "string"}, "what_would_change": {"type": "string"}
        }
      }
    },
    "flags": {
      "type": "array",
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["dimension", "type", "note"],
        "properties": {
          "dimension": {"enum": ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT", "OVERALL"]},
          "type": {"enum": ["insufficient", "informative_absence", "unverified_claim", "low_confidence", "org_context_dependent"]},
          "note": {"type": "string"}
        }
      }
    },
    "changelog": {
      "type": "array",
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["dimension", "change", "evidence"],
        "properties": {
          "dimension": {"enum": ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT", "OVERALL"]},
          "change": {"type": "string"}, "evidence": {"type": "string"}
        }
      }
    }
  }
}
```

- [ ] **Step 5: Run the test to confirm it passes** → PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/feedforward-vendor-review/schemas/vendor-question.schema.json \
        skills/feedforward-vendor-review/schemas/report.schema.json tests/test_schema_report.py
git commit -m "feat: add vendor-question and report schemas"
```

---

### Task 7: Immutable `framework-core.md`

**Files:**
- Create: `skills/feedforward-vendor-review/reference/framework-core.md`
- Source: `source_docs/vendor_system_prompt.md`
- Test: `tests/test_content_framework_core.py`

**Interfaces:**
- Produces: the verbatim framework law injected into every analyst (Task 11) and the synthesis/drift stages.

- [ ] **Step 1: Write the failing content test**

`tests/test_content_framework_core.py`:
```python
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "skills/feedforward-vendor-review/reference/framework-core.md"

def test_anchors_present():
    t = F.read_text()
    # the one question
    assert "strengthen or weaken" in t.lower() or "build or erode" in t.lower()
    # all four score tokens
    for tok in ["Pass", "Partial", "Fail", "Insufficient"]:
        assert tok in t
    # critical rules
    assert "marketing claims are not evidence" in t.lower()
    assert "insufficient information" in t.lower()
    # explicit anti-generic + non-recommendation guardrails
    assert "not a generic" in t.lower()
    assert "not a decision-maker" in t.lower() or "buy/don" in t.lower()
    # informative-absence reconciliation
    assert "informative absence" in t.lower() or "conspicuous" in t.lower()
```

- [ ] **Step 2: Run it to confirm it fails** → FAIL.

- [ ] **Step 3: Author `framework-core.md`**

Copy the entire body of `source_docs/vendor_system_prompt.md` verbatim (Foundational Philosophy, What Excellent Vendors Look Like, Scoring Methodology, Critical Rules, Tone). Then **prepend** this north-star block and **append** the informative-absence rule:

Prepend at the very top:
```markdown
# Framework Core (Immutable)

## The One Question
This framework exists to answer exactly one question about an AI-powered software vendor:
**Will adopting this vendor tool strengthen or weaken the organization's ability to build real, independent, generalizable AI capacity?**

Every score, sentence, and section serves that question.

## What this is NOT
- NOT a generic "is this good software?" review (Gartner / G2 / Forrester style).
- NOT a scorecard of security posture, pricing, support SLAs, market share, or integration breadth — except where those bear directly on capacity-building.
- NOT a buy/don't-buy recommendation. You are an analyst, not a decision-maker.
```

Append at the end (after Tone):
```markdown
## Absence as Evidence (informative absence)
Default to "Insufficient Information" when you genuinely could not check. But a *conspicuous* absence — no affordance documented anywhere it would appear if it existed — is itself evidence of opacity/lock-in. When no positive evidence exists for a mechanic, ask: "Did I check the places it would be documented if it existed?"
- Yes, absent across all expected surfaces → record as informative absence; it may support a Fail/Partial, stated as an explicit inference, confidence capped at medium, plus a vendor question.
- No / it could plausibly exist undocumented → Insufficient Information + a vendor question.
This forbids inventing a positive fact to fill a gap; it permits a disciplined negative inference from documented silence.
```

- [ ] **Step 4: Run the test to confirm it passes** → PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/feedforward-vendor-review/reference/framework-core.md tests/test_content_framework_core.py
git commit -m "feat: add immutable framework-core"
```

---

### Task 8: Immutable dimension rubrics (six files)

**Files:**
- Create: `skills/feedforward-vendor-review/reference/dimensions/{see,change,adapt,use,learn,exit}.md`
- Sources: the matching `source_docs/*.md` dimension files
- Test: `tests/test_content_dimensions.py`

**Interfaces:**
- Produces: the six immutable rubrics injected one-per-analyst (Task 11).

- [ ] **Step 1: Write the failing test**

`tests/test_content_dimensions.py`:
```python
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
```

- [ ] **Step 2: Run it to confirm it fails** → FAIL.

- [ ] **Step 3: Author the six rubrics**

For each file, copy the matching `source_docs` dimension file verbatim as the body:
- `see.md` ← `source_docs/See - Transparency Prompt.md`
- `change.md` ← `source_docs/Change - customizability.md`
- `adapt.md` ← `source_docs/Adapt - Vendor Agility.md`
- `use.md` ← `source_docs/Use - Genuine Utility.md`
- `learn.md` ← `source_docs/Learn - Transferable Knowledge.md`
- `exit.md` ← `source_docs/Exit - Portability.md`

Then map the source score tokens to the fixed vocabulary: rewrite the scoring lines so each uses `Pass` / `Partial` / `Fail` / `Insufficient` (the source files say `yes`/`partially`/`no`/`insufficient` and `full`/`some`/`none` — normalize to the four tokens while keeping the descriptive guidance text).

Append this footer to **every** rubric:
```markdown
## Output contract
Assess ONLY this dimension, ONLY through the one question (build or erode independent AI capacity). This is NOT a generic software review — do not comment on security, pricing, market share, or support SLAs except where they bear on this dimension's capacity question. Marketing claims are not evidence. Cite every claim to a dossier fact id. Return exactly the `dimension-result` schema.
```

Append this additional block to `see.md`, `change.md`, and `exit.md` only:
```markdown
## Where you'd expect this documented (expectation set)
If none of these surfaces document the affordance, treat the silence as *informative absence*, not a mere gap: API reference, admin/console docs, security whitepaper, settings/configuration UI, developer/integration docs, pricing/tier pages. List the surfaces you checked in `expectation_set`.
```

- [ ] **Step 4: Run the test to confirm it passes** → PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/feedforward-vendor-review/reference/dimensions tests/test_content_dimensions.py
git commit -m "feat: add six immutable dimension rubrics"
```

---

### Task 9: Synthesis specs & output template

**Files:**
- Create: `skills/feedforward-vendor-review/reference/synthesis/executive-summary.md`, `.../synthesis/key-questions.md`, `.../output-template.md`
- Sources: `source_docs/Executive Summary.md`, `source_docs/Key Questions.md`, and the four sample reports (for layout)
- Test: `tests/test_content_synthesis.py`

**Interfaces:**
- Produces: the synthesis instructions (Stage 3) and the canonical report layout that `render_report.py` mirrors.

- [ ] **Step 1: Write the failing test**

`tests/test_content_synthesis.py`:
```python
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "skills/feedforward-vendor-review/reference"

def test_exec_summary_spec():
    t = (R / "synthesis/executive-summary.md").read_text().lower()
    assert "key takeaway" in t and "sentiment" in t and "suitab" in t

def test_key_questions_spec():
    t = (R / "synthesis/key-questions.md").read_text().lower()
    assert "5" in t and "question" in t

def test_output_template_sections_in_order():
    t = (R / "output-template.md").read_text()
    order = ["Title block", "Executive Summary", "Evaluation Overview",
             "Detailed Evaluation", "Trade-off Summary", "Key Questions", "Footer"]
    idxs = [t.find(s) for s in order]
    assert all(i != -1 for i in idxs), idxs
    assert idxs == sorted(idxs), "sections out of order"
```

- [ ] **Step 2: Run it to confirm it fails** → FAIL.

- [ ] **Step 3: Author the three files**

`synthesis/executive-summary.md`: copy `source_docs/Executive Summary.md` verbatim (it already specifies the KEY TAKEAWAY opener, 2–3 paragraphs, capacity-framework connection, suitability close, and the positive/neutral/negative sentiment). Add a one-line note: "Fold optional org context into the suitability line ONLY; never into the dimension assessments."

`synthesis/key-questions.md`: copy `source_docs/Key Questions.md` verbatim (5–6 strategic, org-context questions). Add: "Fold optional org context into these questions to sharpen them for the reader's situation."

`output-template.md`: write the canonical 7-section structure exactly as in spec §12, with these headers in order — `## 1. Title block`, `## 2. Executive Summary`, `## 3. Evaluation Overview`, `## 4. Detailed Evaluation`, `## 5. Trade-off Summary`, `## 6. Key Questions`, `## 7. Footer`. Under each, state the content rules (e.g., Title block = `Vendor · "VENDOR EVALUATION REPORT" · category · Version • Month Year`; Detailed Evaluation order = SEE, CHANGE, ADAPT, USE, LEARN, EXIT). Add the conditional-components note: Questions for the Vendor is always present (also a standalone export); "What changed after vendor response" appears on response-pass revisions (v1.1+); "Open items / where this is soft" is Markdown working-doc only. Footer text: `CONFIDENTIAL — FOR INTERNAL USE ONLY` + the one-line framework reminder + version.

- [ ] **Step 4: Run the test to confirm it passes** → PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/feedforward-vendor-review/reference/synthesis skills/feedforward-vendor-review/reference/output-template.md tests/test_content_synthesis.py
git commit -m "feat: add synthesis specs and output template"
```

---

### Task 10: Immutable `drift-check.md`

**Files:**
- Create: `skills/feedforward-vendor-review/reference/drift-check.md`
- Test: `tests/test_content_drift_check.py`

**Interfaces:**
- Produces: the symmetric red-team checklist run as Stage 4.

- [ ] **Step 1: Write the failing test**

`tests/test_content_drift_check.py`:
```python
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "skills/feedforward-vendor-review/reference/drift-check.md"

def test_symmetric_checks_and_immutability():
    t = F.read_text().lower()
    assert "generic" in t                 # anti-generic-creep flank
    assert "false generosity" in t or "too soft" in t   # anti-false-generosity flank
    assert "re-run" in t or "rerun" in t  # can re-run a slipped analyst
    assert "immutab" in t or "did not override" in t     # opinion-override guard
```

- [ ] **Step 2: Run it to confirm it fails** → FAIL.

- [ ] **Step 3: Author `drift-check.md`**

```markdown
# Drift / Red-Team Check (Immutable)

Re-read the assembled report against THE ONE QUESTION (build or erode independent, generalizable AI capacity). Catch drift on BOTH flanks and re-run any analyst that slipped before the report reaches the review gate.

## Flank A — generic-review creep (too harsh / off-topic)
Flag and strip any content that reads as a generic software review: security posture, pricing, market share, support SLAs, integration breadth, or "is it good software" — UNLESS it is tied to a dimension's capacity question. Flag any buy/don't-buy recommendation (the skill never makes one).

## Flank B — false generosity (too soft on opacity)
Flag any dimension that buried a conspicuous, documented silence under "Insufficient Information" and thereby let the vendor off the hook. Per framework-core's absence-as-evidence rule, that silence should drive a Fail/Partial (medium confidence) with a vendor question — not a neutral "Insufficient".

## Immutability guard
Confirm no user/vendor input overrode a criterion or a score-as-opinion. Scores may move ONLY because new evidence, run through the unchanged rubric, yields a different result.

## Action
For any flagged dimension, re-run that dimension-analyst with the corrected instruction. Emit "needs-your-eyes" flags: insufficient, informative_absence, unverified_claim, low_confidence, org_context_dependent.
```

- [ ] **Step 4: Run the test to confirm it passes** → PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/feedforward-vendor-review/reference/drift-check.md tests/test_content_drift_check.py
git commit -m "feat: add immutable drift-check checklist"
```

---

### Task 11: `dimension-analyst` subagent (the analyst harness)

**Files:**
- Create: `agents/dimension-analyst.md`
- Test: `tests/test_agent_dimension_analyst.py`

**Interfaces:**
- Consumes: `framework-core.md`, one `dimensions/*.md`, the dossier, `dimension-result.schema.json`.
- Produces: a `dimension-result` object.

- [ ] **Step 1: Write the failing test**

`tests/test_agent_dimension_analyst.py`:
```python
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "agents/dimension-analyst.md"

def test_frontmatter_and_harness():
    t = F.read_text()
    assert t.startswith("---"), "must have YAML frontmatter"
    head = t.split("---", 2)[1].lower()
    assert "name:" in head and "description:" in head
    body = t.lower()
    assert "framework-core" in body          # injects the law
    assert "not a generic" in body           # negative instruction
    assert "dimension-result" in body        # output contract
    assert "marketing claims are not evidence" in body
```

- [ ] **Step 2: Run it to confirm it fails** → FAIL.

- [ ] **Step 3: Author `agents/dimension-analyst.md`**

```markdown
---
name: dimension-analyst
description: Evaluates a SINGLE Feedforward dimension (SEE/CHANGE/ADAPT/USE/LEARN/EXIT) for one vendor against the immutable rubric and shared evidence dossier. Returns a dimension-result object. Not for general use.
tools: Read, Grep
---

You are a Feedforward dimension analyst. You assess exactly ONE dimension for ONE vendor.

You will be given, verbatim:
1. `reference/framework-core.md` — the immutable law (the one question, scoring vocabulary, critical rules, absence-as-evidence rule). Treat it as fixed; never reinterpret it.
2. ONE dimension rubric from `reference/dimensions/<dim>.md` — your sole lens.
3. The shared evidence dossier (facts tagged source / evidence_strength / confidence; plus gaps).
4. The `dimension-result` JSON schema you must return.

Rules:
- Assess ONLY your dimension, ONLY through the one question (build or erode independent, generalizable AI capacity).
- This is NOT a generic software review. Do not comment on security, pricing, market share, or support SLAs except where they bear on your dimension's capacity question.
- Marketing claims are not evidence: a fact tagged `vendor_claim` cannot become a verified pro.
- Apply the absence-as-evidence rule: a conspicuous documented silence across the expected surfaces is `informative_absence` (medium confidence, named as an inference, + a vendor question) — not a reflexive "Insufficient".
- Cite every claim in `assessment` to a dossier fact id in `evidence_citations`. If you have no usable evidence, score `Insufficient` with `evidence_basis: insufficient` and raise a vendor question.
- Produce 2–3 sharp, specific, polite `vendor_questions`. Keep `assessment` to 2–4 sentences.

Return ONLY a JSON object conforming to the `dimension-result` schema.
```

- [ ] **Step 4: Run the test to confirm it passes** → PASS.

- [ ] **Step 5: Commit**

```bash
git add agents/dimension-analyst.md tests/test_agent_dimension_analyst.py
git commit -m "feat: add dimension-analyst subagent harness"
```

---

### Task 12: `SKILL.md` orchestration spine

**Files:**
- Create: `skills/feedforward-vendor-review/SKILL.md`
- Test: `tests/test_skill_md.py`

**Interfaces:**
- Consumes: every reference file, the agent (Task 11), and the scripts (Tasks 15–17).
- Produces: the executable skill — the user-facing entry point.

- [ ] **Step 1: Write the failing test**

`tests/test_skill_md.py`:
```python
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "skills/feedforward-vendor-review/SKILL.md"

def test_frontmatter_and_pipeline():
    t = F.read_text()
    assert t.startswith("---")
    head = t.split("---", 2)[1].lower()
    assert "name: feedforward-vendor-review" in head
    assert "description:" in head
    body = t.lower()
    for stage in ["scope", "evidence", "dimension-analyst", "synthes", "drift", "render"]:
        assert stage in body, f"pipeline missing stage: {stage}"
    assert "review gate" in body and "10 min" in body.replace("minute", "min")
    assert "render_report.py" in body and "lint_report.py" in body
    assert "vendor response" in body or "rebuttal" in body
```

- [ ] **Step 2: Run it to confirm it fails** → FAIL.

- [ ] **Step 3: Author `SKILL.md`**

Frontmatter:
```markdown
---
name: feedforward-vendor-review
description: Evaluate an AI-powered software vendor (e.g. Glean, Harvey) against Feedforward's six-dimension framework — SEE, CHANGE, ADAPT, USE, LEARN, EXIT — to judge whether it strengthens or weakens the organization's independent, generalizable AI capacity. Use when asked to evaluate, review, or assess an AI vendor/tool for capacity, lock-in, or transparency. Produces a board-grade report. NOT a generic software review and NOT a buy/don't-buy recommendation.
---
```

Body — write the orchestration covering exactly these, referencing files by relative path:
1. **Stage 0 — Intake & scope check.** Confirm the target is AI-powered B2B SaaS; if not, stop and explain (don't force the framework). Confirm the specific product/SKU if ambiguous. Accept optional user materials and optional org context.
2. **Stage 1 — Evidence pass.** Build the evidence dossier (`schemas/evidence-dossier.schema.json`): research vendor docs/API/pricing/changelog + third-party coverage + ingest user materials. Tag every fact `source_type` / `evidence_strength` / `confidence`. Apply the absence-as-evidence rule from `reference/framework-core.md`.
3. **Stage 2 — Six dimension analysts.** For each of SEE, CHANGE, ADAPT, USE, LEARN, EXIT, spawn the `dimension-analyst` subagent, injecting `reference/framework-core.md` + the matching `reference/dimensions/<dim>.md` verbatim + the dossier; require a `dimension-result` (`schemas/dimension-result.schema.json`). Run them concurrently.
4. **Stage 3 — Synthesis.** Per `reference/synthesis/*.md` and `reference/output-template.md`, write the Executive Summary (KEY TAKEAWAY + sentiment + suitability), Trade-off Summary, Key Questions, and the consolidated vendor questions; fold optional org context into the suitability line + Key Questions ONLY. Assemble a `report.json` (`schemas/report.schema.json`).
5. **Stage 4 — Drift check.** Run `reference/drift-check.md`; re-run any slipped analyst; emit flags.
6. **Review gate.** Non-blocking. Present the draft + the "where your input would matter most" flags. The exec may correct EVIDENCE, answer open vendor questions, or add org context — but may NOT change a score without evidence or override a criterion/opinion (decline + log as client disagreement). Modes: gated (default — finalize on any non-corrective reply), one-shot (skip gate), unattended (auto-finalize after ~10 minutes, configurable). On corrections, re-run only affected stages.
7. **Stage 5 — Render.** Run `scripts/render_report.py <report.json> <out_dir>` → `report.md`, `report.html`, `questions.html`. Run `scripts/lint_report.py <report.json>` and fix any violations before delivering.
8. **Vendor rebuttal loop.** When the exec supplies vendor answers, re-enter as a response pass: ingest answers as `vendor_response` evidence, adjudicate each answer (substantive+verifiable / claim-only / roadmap / non-responsive / unanswered — a dodge can harden a Fail), partial re-run, bump the minor version (v1.0 → v1.1), and add a "What changed after vendor response" section.
9. **Optional accelerator:** note that power users may run `workflow/evaluate-vendor.workflow.js` via the Workflow tool for a deterministic run; the steps above are the dependable default.

- [ ] **Step 4: Run the test to confirm it passes** → PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/feedforward-vendor-review/SKILL.md tests/test_skill_md.py
git commit -m "feat: add SKILL.md orchestration spine"
```

---

### Task 13: Optional deterministic Workflow accelerator

**Files:**
- Create: `skills/feedforward-vendor-review/workflow/evaluate-vendor.workflow.js`
- Test: `tests/test_workflow_script.py`

**Interfaces:**
- Produces: a Workflow script mirroring Stages 1–5 (Phase 1 draft) with `schema` options; finishes by emitting `report.json` for the in-conversation gate.

- [ ] **Step 1: Write the failing test**

`tests/test_workflow_script.py`:
```python
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
```

- [ ] **Step 2: Run it to confirm it fails** → FAIL.

- [ ] **Step 3: Author the workflow script**

```javascript
export const meta = {
  name: 'evaluate-vendor',
  description: 'Deterministic Feedforward six-dimension vendor evaluation (Phase 1 draft).',
  phases: [
    { title: 'Evidence' },
    { title: 'Analyze' },
    { title: 'Synthesize' },
    { title: 'Drift' },
  ],
}

const DIMS = ['SEE', 'CHANGE', 'ADAPT', 'USE', 'LEARN', 'EXIT']

phase('Evidence')
const dossier = await agent(
  `Build the evidence dossier for vendor: ${JSON.stringify(args)}. Tag every fact with source_type, evidence_strength, confidence. Apply the absence-as-evidence rule.`,
  { label: 'evidence', schema: { type: 'object', additionalProperties: false,
      required: ['facts'], properties: { facts: { type: 'array', items: { type: 'object' } } } } }
)

phase('Analyze')
const results = await parallel(DIMS.map(d => () =>
  agent(`Analyze the ${d} dimension using its immutable rubric and this dossier: ${JSON.stringify(dossier)}.`,
    { label: `analyst:${d}`, phase: 'Analyze' })
))

phase('Synthesize')
const draft = await agent(
  `Synthesize the report (executive summary, sentiment, suitability, trade-off summary, key questions, consolidated vendor questions) from these dimension results: ${JSON.stringify(results.filter(Boolean))}.`,
  { label: 'synthesis' }
)

phase('Drift')
const checked = await agent(
  `Run the drift/red-team check on this draft, both flanks (generic creep + false generosity), confirm immutability, emit flags: ${JSON.stringify(draft)}.`,
  { label: 'drift-check' }
)

return checked
```

- [ ] **Step 4: Run the test to confirm it passes** → PASS (the node-syntax case is skipped if node is absent).

- [ ] **Step 5: Commit**

```bash
git add skills/feedforward-vendor-review/workflow/evaluate-vendor.workflow.js tests/test_workflow_script.py
git commit -m "feat: add optional deterministic workflow accelerator"
```

---

### Task 14: Self-contained HTML report template

**Files:**
- Create: `skills/feedforward-vendor-review/assets/report-template.html`
- Test: `tests/test_html_template.py`

**Interfaces:**
- Consumes: filled by `render_report.py` via `str.replace` on `{{TOKENS}}`.
- Produces: tokens `{{VENDOR}}`, `{{CATEGORY}}`, `{{VERSION}}`, `{{DATE}}`, `{{BODY}}`; CSS classes `.result-pass`, `.result-partial`, `.result-fail`, `.result-insufficient`.

- [ ] **Step 1: Write the failing test**

`tests/test_html_template.py`:
```python
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "skills/feedforward-vendor-review/assets/report-template.html"

def test_tokens_and_color_classes():
    t = F.read_text()
    for tok in ["{{VENDOR}}", "{{CATEGORY}}", "{{VERSION}}", "{{DATE}}", "{{BODY}}"]:
        assert tok in t
    for cls in ["result-pass", "result-partial", "result-fail", "result-insufficient"]:
        assert cls in t
    assert "<style" in t  # inlined CSS, self-contained
```

- [ ] **Step 2: Run it to confirm it fails** → FAIL.

- [ ] **Step 3: Author `report-template.html`**

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{{VENDOR}} — Vendor Evaluation Report</title>
<style>
  :root { --green:#1a7f37; --amber:#9a6700; --red:#cf222e; --grey:#57606a; }
  body { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
         color:#1f2328; max-width: 820px; margin: 0 auto; padding: 48px 32px; line-height: 1.5; }
  .cover { border-bottom: 3px solid #1f2328; margin-bottom: 32px; padding-bottom: 16px; }
  .cover h1 { margin: 0 0 4px; font-size: 32px; }
  .cover .kicker { letter-spacing: .12em; text-transform: uppercase; color: var(--grey); font-size: 13px; }
  table { border-collapse: collapse; width: 100%; margin: 16px 0; }
  th, td { border: 1px solid #d0d7de; padding: 8px 10px; text-align: left; vertical-align: top; }
  th { background: #f6f8fa; }
  .result-pass { color: var(--green); font-weight: 700; }
  .result-partial { color: var(--amber); font-weight: 700; }
  .result-fail { color: var(--red); font-weight: 700; }
  .result-insufficient { color: var(--grey); font-weight: 700; }
  .gain { color: var(--green); } .giveup { color: var(--red); }
  .footer { margin-top: 40px; border-top: 1px solid #d0d7de; padding-top: 12px;
            color: var(--grey); font-size: 12px; }
  @media print { body { padding: 0; } a { color: inherit; text-decoration: none; } }
</style>
</head>
<body>
  <div class="cover">
    <div class="kicker">Vendor Evaluation Report</div>
    <h1>{{VENDOR}}</h1>
    <div class="kicker">{{CATEGORY}} &nbsp;•&nbsp; {{VERSION}} &nbsp;•&nbsp; {{DATE}}</div>
  </div>
  {{BODY}}
  <div class="footer">CONFIDENTIAL — FOR INTERNAL USE ONLY · This evaluation assesses vendors on immediate utility and long-term organizational AI capacity building · {{VERSION}}</div>
</body>
</html>
```

- [ ] **Step 4: Run the test to confirm it passes** → PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/feedforward-vendor-review/assets/report-template.html tests/test_html_template.py
git commit -m "feat: add self-contained HTML report template"
```

---

### Task 15: `render_report.py` (report.json → md + html + questions)

**Files:**
- Create: `skills/feedforward-vendor-review/scripts/render_report.py`
- Test: `tests/test_render_report.py`, `tests/fixtures/sample_report.json`

**Interfaces:**
- Consumes: a `report.json` matching `report.schema.json`; `assets/report-template.html`.
- Produces: `render_markdown(report: dict) -> str`; `render_html(report: dict, template: str) -> str`; `render_questions_html(report: dict, template: str) -> str`; `main(report_path: str, out_dir: str)` writing `report.md`, `report.html`, `questions.html`. **Stdlib only.**

- [ ] **Step 1: Create the fixture `tests/fixtures/sample_report.json`**

A complete report with all six dimensions in order, mixed scores (use the Glean profile: SEE Fail, CHANGE Partial, ADAPT Partial, USE Pass, LEARN Fail, EXIT Fail), each `detailed` entry having trade_offs + ≥1 vendor_question + evidence_citations, plus `vendor_questions`, `flags` (include one `OVERALL`/`org_context_dependent`), and empty `changelog`. (Conform to `report.schema.json`.)

- [ ] **Step 2: Write the failing test**

`tests/test_render_report.py`:
```python
import json
from pathlib import Path
import render_report

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests/fixtures/sample_report.json"
TEMPLATE = (ROOT / "skills/feedforward-vendor-review/assets/report-template.html").read_text()

def load(): return json.loads(FIX.read_text())

def test_markdown_has_seven_sections_in_order():
    md = render_report.render_markdown(load())
    order = ["VENDOR EVALUATION REPORT", "Executive Summary", "Evaluation Overview",
             "Detailed Evaluation", "Trade-off Summary", "Key Questions",
             "CONFIDENTIAL"]
    idxs = [md.find(s) for s in order]
    assert all(i != -1 for i in idxs)
    assert idxs == sorted(idxs)

def test_markdown_dimension_order():
    md = render_report.render_markdown(load())
    pos = [md.find(f"### {d}") for d in ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]]
    assert all(p != -1 for p in pos) and pos == sorted(pos)

def test_insufficient_display_label():
    r = load()
    r["overview_table"][0]["result"] = "Insufficient"
    md = render_report.render_markdown(r)
    assert "Insufficient Information" in md

def test_html_applies_color_classes():
    html = render_report.render_html(load(), TEMPLATE)
    assert "result-fail" in html and "result-pass" in html
    assert "{{BODY}}" not in html and load()["meta"]["vendor"] in html

def test_questions_html_standalone():
    html = render_report.render_questions_html(load(), TEMPLATE)
    assert "Questions for the Vendor" in html
    assert load()["vendor_questions"][0]["question"] in html
```

- [ ] **Step 3: Run it to confirm it fails** → FAIL (module missing).

- [ ] **Step 4: Implement `render_report.py` (stdlib only)**

```python
"""Render a Feedforward vendor-review report.json into Markdown + self-contained HTML."""
import json
import sys
from pathlib import Path

DIM_ORDER = ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]
DISPLAY = {"Pass": "Pass", "Partial": "Partial", "Fail": "Fail", "Insufficient": "Insufficient Information"}
CSS_CLASS = {"Pass": "result-pass", "Partial": "result-partial",
             "Fail": "result-fail", "Insufficient": "result-insufficient"}


def _result(r):
    return DISPLAY.get(r, r)


def render_markdown(report):
    m = report["meta"]
    out = []
    out.append(f"# {m['vendor']}")
    out.append(f"**VENDOR EVALUATION REPORT** — {m['category']} — Version {m['version']} • {m['date']}\n")

    es = report["executive_summary"]
    out.append("## Executive Summary\n")
    out.append(f"**KEY TAKEAWAY** — {es['key_takeaway']}\n")
    for p in es["paragraphs"]:
        out.append(p + "\n")
    out.append(es["suitability"] + "\n")

    out.append("## Evaluation Overview\n")
    out.append("| Criterion | Focus Area | Result |")
    out.append("|---|---|---|")
    for row in report["overview_table"]:
        out.append(f"| {row['dimension']} | {row['focus_area']} | {_result(row['result'])} |")
    out.append("")

    out.append("## Detailed Evaluation\n")
    by_dim = {d["dimension"]: d for d in report["detailed"]}
    for dim in DIM_ORDER:
        d = by_dim[dim]
        out.append(f"### {dim} — {d['focus_area']}   [{_result(d['score'])}]\n")
        out.append(d["assessment"] + "\n")
        out.append("**Trade-offs**\n")
        out.append(f"+ Gain: {d['trade_offs']['gain']}")
        out.append(f"− Give up: {d['trade_offs']['give_up']}\n")
        out.append("**Questions for Vendor**\n")
        for q in d["vendor_questions"]:
            out.append(f"- {q}")
        out.append("")

    out.append("## Trade-off Summary\n")
    out.append("| Criterion | Result | You Gain | You Give Up |")
    out.append("|---|---|---|---|")
    for row in report["tradeoff_summary"]:
        out.append(f"| {row['dimension']} | {_result(row['result'])} | {row['gain']} | {row['give_up']} |")
    out.append("")

    out.append("## Key Questions for Your Decision\n")
    for i, q in enumerate(report["key_questions"], 1):
        out.append(f"{i}. {q}")
    out.append("")

    if report.get("changelog"):
        out.append("## What changed after vendor response\n")
        for c in report["changelog"]:
            out.append(f"- **{c['dimension']}**: {c['change']} ({c['evidence']})")
        out.append("")

    out.append("---")
    out.append(f"CONFIDENTIAL — FOR INTERNAL USE ONLY · Version {m['version']}")
    return "\n".join(out)


def _detail_html(report):
    rows = []
    by_dim = {d["dimension"]: d for d in report["detailed"]}
    for dim in DIM_ORDER:
        d = by_dim[dim]
        cls = CSS_CLASS[d["score"]]
        rows.append(f"<h3>{dim} — {d['focus_area']} "
                    f"<span class='{cls}'>[{_result(d['score'])}]</span></h3>")
        rows.append(f"<p>{d['assessment']}</p>")
        rows.append(f"<p><span class='gain'>+ Gain:</span> {d['trade_offs']['gain']}<br>"
                    f"<span class='giveup'>− Give up:</span> {d['trade_offs']['give_up']}</p>")
        rows.append("<p><strong>Questions for Vendor</strong></p><ul>"
                    + "".join(f"<li>{q}</li>" for q in d["vendor_questions"]) + "</ul>")
    return "\n".join(rows)


def _overview_html(report):
    body = ["<h2>Evaluation Overview</h2><table><tr><th>Criterion</th><th>Focus Area</th><th>Result</th></tr>"]
    for row in report["overview_table"]:
        body.append(f"<tr><td>{row['dimension']}</td><td>{row['focus_area']}</td>"
                    f"<td class='{CSS_CLASS[row['result']]}'>{_result(row['result'])}</td></tr>")
    body.append("</table>")
    return "".join(body)


def render_html(report, template):
    es = report["executive_summary"]
    body = []
    body.append("<h2>Executive Summary</h2>")
    body.append(f"<p><strong>KEY TAKEAWAY</strong> — {es['key_takeaway']}</p>")
    for p in es["paragraphs"]:
        body.append(f"<p>{p}</p>")
    body.append(f"<p>{es['suitability']}</p>")
    body.append(_overview_html(report))
    body.append("<h2>Detailed Evaluation</h2>")
    body.append(_detail_html(report))
    body.append("<h2>Key Questions for Your Decision</h2><ol>"
                + "".join(f"<li>{q}</li>" for q in report["key_questions"]) + "</ol>")
    m = report["meta"]
    html = template
    for tok, val in [("{{VENDOR}}", m["vendor"]), ("{{CATEGORY}}", m["category"]),
                     ("{{VERSION}}", m["version"]), ("{{DATE}}", m["date"]),
                     ("{{BODY}}", "\n".join(body))]:
        html = html.replace(tok, str(val))
    return html


def render_questions_html(report, template):
    items = []
    for q in report["vendor_questions"]:
        why = f"<br><em>{q['why_we_ask']}</em>" if q.get("why_we_ask") else ""
        items.append(f"<li><strong>[{q['dimension']}]</strong> {q['question']}{why}</li>")
    body = ("<h2>Questions for the Vendor</h2>"
            "<p>Sharp, specific questions the vendor can respond to. Substantive answers may move the diagnosis.</p>"
            "<ol>" + "".join(items) + "</ol>")
    m = report["meta"]
    html = template
    for tok, val in [("{{VENDOR}}", m["vendor"]), ("{{CATEGORY}}", m["category"]),
                     ("{{VERSION}}", m["version"]), ("{{DATE}}", m["date"]), ("{{BODY}}", body)]:
        html = html.replace(tok, str(val))
    return html


def main(report_path, out_dir):
    report = json.loads(Path(report_path).read_text())
    template_path = Path(__file__).resolve().parents[1] / "assets" / "report-template.html"
    template = template_path.read_text()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.md").write_text(render_markdown(report))
    (out / "report.html").write_text(render_html(report, template))
    (out / "questions.html").write_text(render_questions_html(report, template))
    print(f"Wrote report.md, report.html, questions.html to {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
```

- [ ] **Step 5: Run the test to confirm it passes** → PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/feedforward-vendor-review/scripts/render_report.py tests/test_render_report.py tests/fixtures/sample_report.json
git commit -m "feat: add report renderer (md + html + questions)"
```

---

### Task 16: `lint_report.py` (Tier-2 semantic validation)

**Files:**
- Create: `skills/feedforward-vendor-review/scripts/lint_report.py`
- Test: `tests/test_lint_report.py`

**Interfaces:**
- Consumes: a `report.json` dict.
- Produces: `lint(report: dict) -> list[str]` (empty = pass); `main(report_path)` prints violations and exits non-zero if any. **Stdlib only.**

Lint rules (semantics the schema cannot hold):
1. Exactly the six dimensions present in `detailed`, in order SEE, CHANGE, ADAPT, USE, LEARN, EXIT.
2. Each dimension has **2–3** `vendor_questions`.
3. Each `assessment` is **2–4** sentences (count terminal `.`/`?`/`!`).
4. Each non-`Insufficient` dimension has **≥1** `evidence_citations`; an `Insufficient` dimension has `evidence_basis == "insufficient"`.
5. Any dimension with `evidence_basis == "informative_absence"` must reference an `expectation_set` — enforced upstream in the dossier, but lint requires `confidence != "high"` for `informative_absence` (capped at medium).
6. `overview_table` results match `detailed` scores per dimension.

- [ ] **Step 1: Write the failing test**

`tests/test_lint_report.py`:
```python
import json, copy
from pathlib import Path
import lint_report

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests/fixtures/sample_report.json"
def base(): return json.loads(FIX.read_text())

def test_clean_report_passes():
    assert lint_report.lint(base()) == []

def test_detects_too_many_questions():
    r = base()
    r["detailed"][0]["vendor_questions"] = ["a?", "b?", "c?", "d?"]
    assert any("vendor_questions" in v for v in lint_report.lint(r))

def test_detects_missing_citation_on_scored_dimension():
    r = base()
    d = next(x for x in r["detailed"] if x["score"] != "Insufficient")
    d["evidence_citations"] = []
    assert any("citation" in v.lower() for v in lint_report.lint(r))

def test_detects_informative_absence_high_confidence():
    r = base()
    r["detailed"][0]["evidence_basis"] = "informative_absence"
    r["detailed"][0]["confidence"] = "high"
    assert any("informative_absence" in v for v in lint_report.lint(r))

def test_detects_overview_score_mismatch():
    r = base()
    # flip overview result away from detailed score
    dim = r["detailed"][0]["dimension"]
    for row in r["overview_table"]:
        if row["dimension"] == dim:
            row["result"] = "Pass" if r["detailed"][0]["score"] != "Pass" else "Fail"
    assert any("overview" in v.lower() for v in lint_report.lint(r))
```

- [ ] **Step 2: Run it to confirm it fails** → FAIL.

- [ ] **Step 3: Implement `lint_report.py` (stdlib only)**

```python
"""Tier-2 semantic validation for a Feedforward vendor-review report.json."""
import json
import re
import sys
from pathlib import Path

DIM_ORDER = ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]


def _sentence_count(text):
    return len([s for s in re.split(r"[.!?]+", text) if s.strip()])


def lint(report):
    v = []
    detailed = report.get("detailed", [])
    dims = [d["dimension"] for d in detailed]
    if dims != DIM_ORDER:
        v.append(f"detailed dimensions must be exactly {DIM_ORDER} in order, got {dims}")

    by_dim = {d["dimension"]: d for d in detailed}
    for dim, d in by_dim.items():
        nq = len(d.get("vendor_questions", []))
        if not (2 <= nq <= 3):
            v.append(f"{dim}: vendor_questions must be 2-3, got {nq}")
        sc = _sentence_count(d.get("assessment", ""))
        if not (2 <= sc <= 4):
            v.append(f"{dim}: assessment must be 2-4 sentences, got {sc}")
        if d["score"] != "Insufficient":
            if len(d.get("evidence_citations", [])) < 1:
                v.append(f"{dim}: scored dimension needs >=1 evidence citation")
        else:
            if d.get("evidence_basis") != "insufficient":
                v.append(f"{dim}: Insufficient score must have evidence_basis 'insufficient'")
        if d.get("evidence_basis") == "informative_absence" and d.get("confidence") == "high":
            v.append(f"{dim}: informative_absence confidence is capped at medium, got high")

    overview = {r["dimension"]: r["result"] for r in report.get("overview_table", [])}
    for dim, d in by_dim.items():
        if overview.get(dim) != d["score"]:
            v.append(f"{dim}: overview result '{overview.get(dim)}' != detailed score '{d['score']}'")

    return v


def main(report_path):
    report = json.loads(Path(report_path).read_text())
    violations = lint(report)
    if violations:
        print("LINT FAILED:")
        for x in violations:
            print(" -", x)
        sys.exit(1)
    print("LINT OK")


if __name__ == "__main__":
    main(sys.argv[1])
```

- [ ] **Step 4: Run the test to confirm it passes** → PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/feedforward-vendor-review/scripts/lint_report.py tests/test_lint_report.py
git commit -m "feat: add Tier-2 report linter"
```

---

### Task 17: Golden fixtures & concordance eval

**Files:**
- Create: `skills/feedforward-vendor-review/examples/{glean,harvey,conveo,legora}/expected-scores.json`
- Create: `skills/feedforward-vendor-review/scripts/eval_concordance.py`
- Test: `tests/test_eval_concordance.py`

**Interfaces:**
- Produces: `score_concordance(produced: dict, expected: dict) -> dict` with keys `matches`, `mismatches`, `pct`; `theme_presence(produced: dict, themes: list[str]) -> dict` with `found`, `missing`. **Stdlib only.**

Golden score profiles (from the four sample reports — copy exactly):
- **Glean:** SEE Fail, CHANGE Partial, ADAPT Partial, USE Pass, LEARN Fail, EXIT Fail.
- **Harvey:** SEE Partial, CHANGE Fail, ADAPT Partial, USE Partial, LEARN Partial, EXIT Partial.
- **Conveo:** SEE Fail, CHANGE Fail, ADAPT Partial, USE Partial, LEARN Fail, EXIT Partial.
- **Legora:** SEE Partial, CHANGE Partial, ADAPT Partial, USE Partial, LEARN Partial, EXIT Partial.

Core themes (substring checks) per vendor, e.g.:
- **Glean:** ["knowledge graph", "lock-in"]; **Harvey:** ["OpenAI", "single-vendor"]; **Conveo:** ["No expertise"]; **Legora:** ["Azure", "OpenAI"].

- [ ] **Step 1: Create the four `expected-scores.json` fixtures**

Example `examples/glean/expected-scores.json`:
```json
{
  "vendor": "Glean",
  "scores": {"SEE": "Fail", "CHANGE": "Partial", "ADAPT": "Partial",
             "USE": "Pass", "LEARN": "Fail", "EXIT": "Fail"},
  "themes": ["knowledge graph", "lock-in"]
}
```
(Repeat for harvey/conveo/legora using the profiles and themes above.)

- [ ] **Step 2: Write the failing test**

`tests/test_eval_concordance.py`:
```python
import eval_concordance as ec

def test_perfect_concordance():
    produced = {"detailed": [{"dimension": d, "score": s} for d, s in
                [("SEE","Fail"),("CHANGE","Partial"),("ADAPT","Partial"),
                 ("USE","Pass"),("LEARN","Fail"),("EXIT","Fail")]]}
    expected = {"scores": {"SEE":"Fail","CHANGE":"Partial","ADAPT":"Partial",
                           "USE":"Pass","LEARN":"Fail","EXIT":"Fail"}}
    r = ec.score_concordance(produced, expected)
    assert r["pct"] == 100.0 and r["mismatches"] == []

def test_partial_concordance():
    produced = {"detailed": [{"dimension":"SEE","score":"Pass"}]}
    expected = {"scores": {"SEE":"Fail"}}
    r = ec.score_concordance(produced, expected)
    assert r["pct"] == 0.0 and ("SEE", "Pass", "Fail") in [tuple(x) for x in r["mismatches"]]

def test_theme_presence():
    produced = {"executive_summary": {"key_takeaway": "proprietary knowledge graph lock-in",
                "paragraphs": [], "suitability": ""}, "detailed": []}
    r = ec.theme_presence(produced, ["knowledge graph", "missing-theme"])
    assert "knowledge graph" in r["found"] and "missing-theme" in r["missing"]
```

- [ ] **Step 3: Run it to confirm it fails** → FAIL.

- [ ] **Step 4: Implement `eval_concordance.py` (stdlib only)**

```python
"""Compare a produced report.json against a golden expected-scores.json."""
import json
import sys
from pathlib import Path


def score_concordance(produced, expected):
    prod = {d["dimension"]: d["score"] for d in produced.get("detailed", [])}
    exp = expected.get("scores", {})
    matches, mismatches = 0, []
    for dim, want in exp.items():
        got = prod.get(dim)
        if got == want:
            matches += 1
        else:
            mismatches.append([dim, got, want])
    pct = round(100.0 * matches / len(exp), 1) if exp else 0.0
    return {"matches": matches, "mismatches": mismatches, "pct": pct}


def theme_presence(produced, themes):
    es = produced.get("executive_summary", {})
    hay = " ".join([es.get("key_takeaway", ""), es.get("suitability", "")]
                   + es.get("paragraphs", [])
                   + [d.get("assessment", "") for d in produced.get("detailed", [])]).lower()
    found = [t for t in themes if t.lower() in hay]
    missing = [t for t in themes if t.lower() not in hay]
    return {"found": found, "missing": missing}


def main(produced_path, expected_path):
    produced = json.loads(Path(produced_path).read_text())
    expected = json.loads(Path(expected_path).read_text())
    sc = score_concordance(produced, expected)
    th = theme_presence(produced, expected.get("themes", []))
    print(json.dumps({"score_concordance": sc, "themes": th}, indent=2))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
```

- [ ] **Step 5: Run the test to confirm it passes** → PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/feedforward-vendor-review/examples skills/feedforward-vendor-review/scripts/eval_concordance.py tests/test_eval_concordance.py
git commit -m "feat: add golden fixtures and concordance eval"
```

---

### Task 18: README, full test sweep & end-to-end verification checklist

**Files:**
- Modify: `README.md`
- Create: `docs/VERIFICATION.md`
- Test: `tests/test_readme.py`

**Interfaces:**
- Produces: install/usage docs; a documented manual end-to-end check (the LLM-behavior parts that unit tests cannot cover).

- [ ] **Step 1: Write the failing README test**

`tests/test_readme.py`:
```python
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
R = (ROOT / "README.md").read_text()

def test_install_commands_present():
    assert "/plugin marketplace add Feedforward-AI/vendor-review-skill" in R
    assert "/plugin install vendor-review@feedforward" in R

def test_framework_explained():
    for d in ["SEE", "CHANGE", "ADAPT", "USE", "LEARN", "EXIT"]:
        assert d in R
```

- [ ] **Step 2: Run it to confirm it fails** → FAIL.

- [ ] **Step 3: Write `README.md`**

Include: a one-paragraph framing of the one question; the six dimensions; the install commands (`/plugin marketplace add Feedforward-AI/vendor-review-skill` then `/plugin install vendor-review@feedforward`); usage (`evaluate Glean`, optional materials, optional org context, one-shot mode, vendor-response pass); a note that `reference/framework-core.md`, `reference/dimensions/*.md`, and `reference/drift-check.md` are immutable law and must not be edited to soften the opinions; and that runtime scripts are stdlib-only.

- [ ] **Step 4: Write `docs/VERIFICATION.md`** (manual end-to-end checklist)

```markdown
# End-to-end verification

Unit tests cover schemas, rendering, linting, and concordance math. The LLM-behavior pipeline is verified manually:

1. Install locally: `claude` → `/plugin marketplace add ./` → `/plugin install vendor-review@feedforward`.
2. Run: `evaluate Glean`. Let it produce report.json.
3. Validate shape: `python skills/feedforward-vendor-review/scripts/lint_report.py <report.json>` → LINT OK.
4. Validate schema: load report.json against schemas/report.schema.json with jsonschema → valid.
5. Concordance: `python skills/feedforward-vendor-review/scripts/eval_concordance.py <report.json> skills/feedforward-vendor-review/examples/glean/expected-scores.json` → score pct ≥ 83% (5/6), themes found.
6. Render: `python skills/feedforward-vendor-review/scripts/render_report.py <report.json> out/` → open out/report.html, Print → PDF.
7. Adversarial spot-checks: confirm (a) no generic security/pricing/market-share prose survives; (b) a vendor marketing metric is tagged vendor_claim, not a verified pro; (c) a conspicuous silence produced informative_absence (not a reflexive Insufficient); (d) an opinion-override request was declined.
8. Repeat for harvey/conveo/legora against their expected-scores.json.
```

- [ ] **Step 5: Run the full suite**

Run: `python -m pytest -v`
Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add README.md docs/VERIFICATION.md tests/test_readme.py
git commit -m "docs: add README and end-to-end verification checklist"
```

---

## Self-Review

**Spec coverage:** §1 one-question/non-goals → Tasks 7, 11, 12 (anchors + guardrails). §2 framework/scoring/immutability → Tasks 7, 8. §3 architecture/file layout/orchestration → Tasks 1, 11, 12, 13. §4 pipeline/stages → Task 12 (+13). §5 data model/schemas → Tasks 4–6. §6 hybrid evidence → Task 12 Stage 1. §7 absence-as-evidence → Tasks 7, 8, 16 (lint cap). §8 review gate/flags → Task 12; flag enums → Task 6. §9 rebuttal loop/versioning → Task 12. §10 anti-drift stack → Tasks 7, 8, 10, 11, 12. §11 structured outputs → Tasks 3–6 (+ analyst schema use). §12 output/rendering → Tasks 9, 14, 15. §13 org tailoring → Tasks 9, 12. §14 error handling/scope → Task 12 Stage 0. §15 testing/golden → Tasks 16, 17, 18. §16 resolved decisions → Tasks 12 (10-min), 15 (questions export). §18 distribution/packaging → Tasks 1, 2, 18.

**Placeholder scan:** No "TBD/TODO/handle edge cases" in code steps; content tasks specify exact verbatim source copies plus exact added text; the only owner-deferred item is the LICENSE text (Task 1 Step 5), explicitly flagged.

**Type consistency:** Function names are consistent across tasks — `check_so_compliance` (Task 3 → used 4,5,6), `render_markdown`/`render_html`/`render_questions_html`/`main` (Task 15), `lint` (Task 16), `score_concordance`/`theme_presence` (Task 17). Score vocabulary (`Pass|Partial|Fail|Insufficient`), `evidence_basis` superset, and `flags.dimension` OVERALL are identical in schemas (Tasks 5,6), renderer (15), and linter (16).

**Known coverage limit (documented, not a gap):** LLM-behavior stages (evidence gathering, the six analyses, synthesis, drift judgment, the review gate, rebuttal adjudication) cannot be unit-tested deterministically; they are authored in Tasks 11–12 and verified via the golden-concordance eval (Task 17) and the manual checklist (`docs/VERIFICATION.md`, Task 18).
