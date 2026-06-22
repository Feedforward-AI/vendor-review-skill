# See - Transparency Prompt
Evaluate the SEE (Transparency) criterion for this vendor.

Assess whether the vendor exposes the fundamental mechanics of how their AI operates:
- Can you see the prompts being used, including system prompts?
- Can you see which models are being selected and the logic behind model selection?
- Can you see how context is provided to the model—RAG systems, chunking strategies, retrieval approaches?
- Can you see inference parameters and other configuration choices?

Score as:
- Pass: Clear, verifiable evidence that transparency is provided
- Partial: Some visibility exists but with meaningful gaps
- Fail: No visibility into AI operations, operates as a black box
- Insufficient: Cannot assess due to lack of information

Provide:
1\. A 2-4 sentence assessment with specific evidence
2\. Trade-off statement (what org gains vs gives up)
3\. 2-3 specific questions to ask the vendor if gaps exist


## Output contract
Assess ONLY this dimension, ONLY through the one question (build or erode independent AI capacity). This is NOT a generic software review — do not comment on security, pricing, market share, or support SLAs except where they bear on this dimension's capacity question. Marketing claims are not evidence. Cite every claim to a dossier fact id. Return exactly the `dimension-result` schema.

## Where you'd expect this documented (expectation set)
If none of these surfaces document the affordance, treat the silence as *informative absence*, not a mere gap: API reference, admin/console docs, security whitepaper, settings/configuration UI, developer/integration docs, pricing/tier pages. List the surfaces you checked in `expectation_set`.
