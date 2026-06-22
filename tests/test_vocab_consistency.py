"""Guards against prose drifting from the schemas.

Every recurring review bug in this repo was the same shape: an instruction file
(SKILL.md / a rubric / the output template / the analyst harness) named a field
or enum value that the JSON schemas do not actually define — e.g. `drift_flags`
(field is `flags`), `moderate` (not an `evidence_strength` value), `Cautious`
(not a `sentiment` value), `user_supplied` (it's `user_material`).

The schemas are enforced at runtime by structured outputs; the prose was not
checked against them. This test closes that gap: the schemas are the single
source of truth, and the instruction prose may only use schema vocabulary
(plus a small, explicit allow-list of deliberate non-schema operational terms).

Convention this enforces: reference a schema field or enum value in prose with
`backticks`. Backticked identifier-shaped tokens are checked here.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "vendor-review" / "skills" / "feedforward-vendor-review"

# Deliberate non-schema identifiers used in the instruction prose: operational
# modes, a config parameter, and one term referenced precisely BECAUSE it is not
# a schema field. Adding here is an explicit, reviewed decision.
ALLOWLIST = {
    "gated",                        # review-gate operating mode
    "unattended",                   # review-gate operating mode
    "review_gate_timeout_minutes",  # config param for unattended auto-finalize
    "client_disagreement",          # referenced only to state it is NOT a structured field
}

# Plain English words that may appear in backticks but are not identifiers.
STOPWORDS = {"and", "or", "the", "a", "an", "to", "of", "for", "in",
             "is", "as", "not", "no", "e", "g", "i"}

# A backticked token shaped like a schema identifier (snake_case / score word /
# ALLCAPS code) — no dots, slashes, hyphens, or spaces (those are filenames/paths).
IDENT = re.compile(r"^[A-Za-z][A-Za-z0-9_]+$")

# Historical drift bugs that must never reappear, including multi-word / phrase
# forms a single-token scan cannot see. Matched case-insensitively as substrings.
FORBIDDEN_SUBSTRINGS = [
    "Conditional Pass",          # invented score
    "drift_flags",               # field is `flags`
    "user_supplied",             # value is `user_material`
    "Cautious",                  # invalid `sentiment` value (use `neutral`)
    "evidence_strength: strong",
    "evidence_strength: moderate",
    "evidence_strength: weak",
]


def _schema_vocab():
    """All enum values + property names across every schema = the canonical vocabulary."""
    enums, fields = set(), set()

    def walk(node):
        if isinstance(node, dict):
            if isinstance(node.get("enum"), list):
                enums.update(v for v in node["enum"] if isinstance(v, str))
            if isinstance(node.get("properties"), dict):
                fields.update(node["properties"].keys())
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for f in sorted((SKILL / "schemas").glob("*.schema.json")):
        walk(json.loads(f.read_text()))
    return enums | fields


def _prose_files():
    """The instruction files whose vocabulary drives schema-constrained generation."""
    files = [SKILL / "SKILL.md"]
    files += sorted((SKILL / "references").rglob("*.md"))
    return [p for p in files if p.exists()]


def _unknown_identifiers(text, vocab):
    """Backticked identifier-shaped tokens that are neither schema vocab nor allow-listed."""
    out = set()
    for raw in re.findall(r"`([^`]+)`", text):
        tok = raw.strip()
        if IDENT.match(tok) and tok.lower() not in STOPWORDS:
            if tok not in vocab and tok not in ALLOWLIST:
                out.add(tok)
    return out


def test_prose_identifiers_match_schema_vocab():
    vocab = _schema_vocab()
    problems = {}
    for pf in _prose_files():
        unknown = _unknown_identifiers(pf.read_text(), vocab)
        if unknown:
            problems[pf.relative_to(ROOT).as_posix()] = sorted(unknown)
    assert not problems, (
        "Backticked identifier(s) in instruction prose are not valid schema "
        "field/enum values (and not allow-listed). Fix the prose to match the "
        "schema, or add a deliberate non-schema term to ALLOWLIST:\n"
        + json.dumps(problems, indent=2)
    )


def test_no_known_drift_strings():
    hits = {}
    for pf in _prose_files():
        low = pf.read_text().lower()
        found = [s for s in FORBIDDEN_SUBSTRINGS if s.lower() in low]
        if found:
            hits[pf.relative_to(ROOT).as_posix()] = found
    assert not hits, "Known schema-drift strings reappeared:\n" + json.dumps(hits, indent=2)


def test_checker_is_not_vacuous():
    # Proves this guard can actually fail: planted bad tokens are caught; real ones pass.
    vocab = _schema_vocab()
    assert {"flags", "score", "sentiment", "evidence_strength"} <= vocab
    assert {"drift_flags", "moderate", "user_supplied"}.isdisjoint(vocab)

    planted = "Set `drift_flags` and use `moderate` confidence."
    assert _unknown_identifiers(planted, vocab) == {"drift_flags", "moderate"}

    clean = "Emit `flags`; set `score` and `sentiment` to `positive`."
    assert _unknown_identifiers(clean, vocab) == set()
