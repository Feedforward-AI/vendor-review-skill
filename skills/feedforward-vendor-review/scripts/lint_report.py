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
