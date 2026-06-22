"""Tier-2 semantic validation for a Feedforward vendor-review report.json."""
import json
import re
import sys
from pathlib import Path

from _constants import DIM_ORDER


def _sentence_count(text):
    # Neutralize false terminators before splitting on sentence boundaries.
    t = text
    # 1. URLs (http/https)
    t = re.sub(r'https?://\S+', ' ', t)
    # 2. Common abbreviations (BEFORE domain/decimal, to prevent partial consumption)
    t = re.sub(r'\b(?:e\.g|i\.e|vs|etc|u\.s|inc|ltd|co|approx|dept|fig|no|vol)\.', ' ', t, flags=re.IGNORECASE)
    # 3. Decimals and version numbers (e.g. 1.0, v3.14)
    t = re.sub(r'\b\d+\.\d+\b', ' ', t)
    # 4. Domain/path tokens (word.word style tokens)
    t = re.sub(r'\b[\w-]+\.[\w./\-]+\b', ' ', t)
    # 5. Split on sentence boundaries and count non-empty parts
    parts = re.split(r'[.!?]+(?=\s|$)', t)
    return len([s for s in parts if s.strip()])


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

    # Check overview_table: results must match detailed scores
    overview = {r["dimension"]: r["result"] for r in report.get("overview_table", [])}
    for dim, d in by_dim.items():
        if overview.get(dim) != d["score"]:
            v.append(f"{dim}: overview result '{overview.get(dim)}' != detailed score '{d['score']}'")

    # Check overview_table dimension sequence equals DIM_ORDER
    overview_dims = [r["dimension"] for r in report.get("overview_table", [])]
    if overview_dims != DIM_ORDER:
        v.append(f"overview_table dimension order must be {DIM_ORDER}, got {overview_dims}")

    # Check tradeoff_summary: results must match detailed scores
    tradeoff = {r["dimension"]: r["result"] for r in report.get("tradeoff_summary", [])}
    for dim, d in by_dim.items():
        if tradeoff.get(dim) != d["score"]:
            v.append(f"{dim}: tradeoff_summary result '{tradeoff.get(dim)}' != detailed score '{d['score']}'")

    # Check tradeoff_summary dimension sequence equals DIM_ORDER
    tradeoff_dims = [r["dimension"] for r in report.get("tradeoff_summary", [])]
    if tradeoff_dims != DIM_ORDER:
        v.append(f"tradeoff_summary dimension order must be {DIM_ORDER}, got {tradeoff_dims}")

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
    # Ensure scripts dir is on path for _constants import when run directly
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main(sys.argv[1])
