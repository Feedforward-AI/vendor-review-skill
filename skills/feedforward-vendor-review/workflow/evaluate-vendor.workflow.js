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
      required: ['vendor', 'scope_check', 'facts', 'gaps'],
      properties: {
        vendor: { type: 'string' },
        scope_check: { type: 'object' },
        facts: { type: 'array', items: { type: 'object' } },
        gaps: { type: 'array', items: { type: 'object' } }
      } } }
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
