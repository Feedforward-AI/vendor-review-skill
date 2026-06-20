# Exit - Portability
Evaluate the EXIT (Portability) criterion for this vendor.

Assess the difficulty of transitioning away from this vendor:
- Does the tool use proprietary data formats that would require conversion or be lost?
- Does it create artifacts in proprietary formats or languages?
- Can data and workflows be exported in standard, usable formats?
- How much institutional knowledge would be trapped if you left?

Score as:
- Pass: Easy migration with standard export formats
- Partial: Some data portable but with significant limitations
- Fail: Data and configurations locked in proprietary formats
- Insufficient: Cannot assess due to lack of information

Provide:
1\. A 2-4 sentence assessment with specific evidence
2\. Trade-off statement (what org gains vs gives up)
3\. 2-3 specific questions to ask the vendor if gaps exist

## Output contract
Assess ONLY this dimension, ONLY through the one question (build or erode independent AI capacity). This is NOT a generic software review — do not comment on security, pricing, market share, or support SLAs except where they bear on this dimension's capacity question. Marketing claims are not evidence. Cite every claim to a dossier fact id. Return exactly the `dimension-result` schema.

## Where you'd expect this documented (expectation set)
If none of these surfaces document the affordance, treat the silence as *informative absence*, not a mere gap: API reference, admin/console docs, security whitepaper, settings/configuration UI, developer/integration docs, pricing/tier pages. List the surfaces you checked in `expectation_set`.
