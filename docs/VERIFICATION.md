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
