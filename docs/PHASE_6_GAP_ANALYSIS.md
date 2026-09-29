# Phase 6 GeoSAVE gap analysis

Status: literature-scoping conclusion as of 2026-09-30. This is not a claim that no unpublished or unindexed work exists.

| Component | Assessment within reviewed literature | Closest work | GeoSAVE distinction |
| --- | --- | --- | --- |
| Multimodal driving scene representation | well studied | LMDrive; DriveLM; IDKB | GeoSAVE uses a bounded audit representation, not an end-to-end controller. |
| Candidate actions with known physical consequences | partially studied | closed-loop systems; TARGET | GeoSAVE joins a frozen action-scenario-seed physical matrix after model selection. |
| Jurisdiction-specific primary legal evidence | partially studied | Prakken; lawful-driving and formalization work | Existing work is typically single-jurisdiction or derives requirements; GeoSAVE preserves an auditable selected primary-law subset. |
| Multiple jurisdictions | partially studied | IDKB has multi-country driving knowledge material | No reviewed work tied a multi-jurisdiction legal snapshot to identical model decisions and physical outcomes. |
| Controlled legal-context conditions | rare | legal retrieval/formalization work | C0-C4 separates country label, structured evidence, raw evidence where permitted, and deterministic support. |
| Multimodal foundation-model driving decision | well studied | LMDrive; DriveLM; IDKB | GeoSAVE evaluates bounded external actions, not vehicle-control quality. |
| Explicit physical safety versus legal status | rare | Prakken | GeoSAVE records safe-illegal and unsafe-lawful outcomes separately. |
| Unknown/conflicting law | partially studied | Prakken; legal-reasoning error studies | GeoSAVE carries `NOT_DETERMINED`, rather than silently treating absent law as lawful. |
| Legal-hallucination evaluation in driving decisions | rare | legal error taxonomies; traffic-law formalization | GeoSAVE can audit unsupported legal claims against supplied evidence IDs. |
| Demographic semantic counterfactual audit | not found in reviewed literature | none identified | GeoSAVE proposes a non-normative wording audit with physics, law, and actions fixed. |

## Contribution discipline

The review found substantial prior work in multimodal driving, traffic-rule formalization, closed-loop evaluation, and legal LLM evaluation. GeoSAVE must not claim the first use of LLMs/VLMs in driving, legal traffic-rule reasoning, or structured outputs. The contribution is the auditable combination and controlled comparisons, contingent on completion of v2 and the main benchmark.

| Possible contribution | Closest prior work | Recommended wording |
| --- | --- | --- |
| Frozen physical outcomes joined to model actions | LMDrive, DriveLM, TARGET | “Within the reviewed literature, we did not identify an evaluation combining a frozen action-outcome matrix with controlled jurisdictional legal contexts for multimodal model decisions.” |
| Two-level legal evidence | IDKB, Prakken, traffic-law formalization | “GeoSAVE combines broad context with a limited, auditable primary-law subset; it does not claim complete global legal coverage.” |
| Safety, legality, and unknown separation | Prakken; legal LLM evaluations | “GeoSAVE operationalizes separation of safety, legality, conflict, and unknown law for benchmark reporting.” |
| Demographic wording audit | none located | “We include a bounded semantic counterfactual audit; this is an observed-output test, not evidence of model values or cognition.” |
