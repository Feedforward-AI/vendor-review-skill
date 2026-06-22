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
    # Gather all human-readable report text
    text_parts = []

    # Executive summary
    es = produced.get("executive_summary", {})
    text_parts.append(es.get("key_takeaway", ""))
    text_parts.append(es.get("suitability", ""))
    text_parts.extend(es.get("paragraphs", []))

    # Detailed entries (assessment, trade_offs, vendor_questions)
    for d in produced.get("detailed", []):
        text_parts.append(d.get("assessment", ""))
        trade_offs = d.get("trade_offs", {})
        text_parts.append(trade_offs.get("gain", ""))
        text_parts.append(trade_offs.get("give_up", ""))
        # Vendor questions are a list of strings
        text_parts.extend(d.get("vendor_questions", []))

    # Top-level key_questions
    text_parts.extend(produced.get("key_questions", []))

    # Top-level vendor_questions (extract question text from each entry)
    for vq in produced.get("vendor_questions", []):
        if isinstance(vq, dict):
            text_parts.append(vq.get("question", ""))
        else:
            text_parts.append(str(vq))

    hay = " ".join(str(p) for p in text_parts).lower()
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
