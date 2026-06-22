# End-to-end verification

Unit tests cover schemas, rendering, linting, and concordance math. The LLM-behavior pipeline is verified manually:

1. Install locally in Claude Code: `claude` → `/plugin marketplace add ./` → `/plugin install vendor-review@feedforward`.
2. Install locally in Codex: `codex plugin marketplace add ./` → `codex plugin add vendor-review@feedforward`.
3. Run: `evaluate Glean`. Let it produce report.json.
4. Validate shape: `python plugins/vendor-review/skills/feedforward-vendor-review/scripts/lint_report.py <report.json>` → LINT OK.
5. Validate schema: load report.json against `plugins/vendor-review/skills/feedforward-vendor-review/schemas/report.schema.json` with jsonschema → valid.
6. Concordance: `python plugins/vendor-review/skills/feedforward-vendor-review/scripts/eval_concordance.py <report.json> plugins/vendor-review/skills/feedforward-vendor-review/examples/glean/expected-scores.json` → score pct ≥ 83% (5/6), themes found.
7. Render: `python plugins/vendor-review/skills/feedforward-vendor-review/scripts/render_report.py <report.json> out/` → open out/report.html, Print → PDF.
8. Adversarial spot-checks: confirm (a) no generic security/pricing/market-share prose survives; (b) a vendor marketing metric is tagged vendor_claim, not a verified pro; (c) a conspicuous silence produced informative_absence (not a reflexive Insufficient); (d) an opinion-override request was declined.
9. Repeat for harvey/conveo/legora against their expected-scores.json.
