# Change - customizability
Evaluate the CHANGE (Customizability) criterion for this vendor.

Assess the degree to which you can modify the tool's AI operations:
- Can you adjust or replace system prompts?
- Can you select different models or model versions?
- Can you modify how context is retrieved, chunked, or prioritized?
- Can you adjust inference parameters?

Score as:
- Pass: Full customization of AI layer available
- Partial: Some customization exists but core AI layer cannot be modified
- Fail: No ability to customize AI behavior
- Insufficient: Cannot assess due to lack of information

Provide:
1\. A 2-4 sentence assessment with specific evidence
2\. Trade-off statement (what org gains vs gives up)
3\. 2-3 specific questions to ask the vendor if gaps exist

## Output contract
Assess ONLY this dimension, ONLY through the one question (build or erode independent AI capacity). This is NOT a generic software review — do not comment on security, pricing, market share, or support SLAs except where they bear on this dimension's capacity question. Marketing claims are not evidence. Cite every claim to a dossier fact id. Return exactly the `dimension-result` schema.

## Where you'd expect this documented (expectation set)
If none of these surfaces document the affordance, treat the silence as *informative absence*, not a mere gap: API reference, admin/console docs, security whitepaper, settings/configuration UI, developer/integration docs, pricing/tier pages. List the surfaces you checked in `expectation_set`.
