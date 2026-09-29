# Phase 6 systematic scoping review

Execution date: 2026-09-30. Status: `COMPLETE_FOR_PHASE6_REDESIGN`.

## Scope and search method

This is a structured scoping review for redesigning the Phase 6 interface, not a systematic-review claim of exhaustive database coverage. Searches combined title/keyword queries for “autonomous driving LLM”, “VLM driving”, “vision-language-action driving”, “traffic law LLM”, “lawful autonomous driving”, “machine-readable traffic law”, “legal reasoning LLM”, “structured output JSON schema”, “explanation faithfulness”, and 2025–2026 recency queries. Sources screened included official proceedings/pages from CVF, AAAI, ACL Anthology, ACM/DOI pages, IEEE Xplore metadata, Springer, ScienceDirect, arXiv, and official project/provider documentation when the publication page required it. IEEE/ACM paywall or bot checks did not substitute non-primary claims: matrix entries retain official landing pages and label preprints.

Initial topic screening identified 37 candidate records. Twenty-two were included because they directly inform driving foundation models, traffic-law formalization, legal-reasoning error, structured outputs, or accountable explanation. Fifteen were excluded as duplicates, inaccessible summaries without verifiable primary metadata, or papers outside the Phase 6 construct. The included corpus is 16 peer-reviewed records and 6 preprints. Year distribution: 2016 (1), 2017 (1), 2019 (1), 2020 (1), 2022 (1), 2024 (4), 2025 (11), and 2026 (2).

The machine-readable record is [phase6_literature_matrix.csv](../data/literature/phase6_literature_matrix.csv). It contains title, author, venue, review status, DOI where verified, official URL, task/modalities, law/metric coverage, finding, limitation, and GeoSAVE relation for every included work.

## Taxonomy and synthesis

```text
Driving perception/reasoning ─┐
Driving planning/action ──────┼─> bounded candidate-action decision
Regulation-aware driving ────┤        │
Machine-readable law ────────┤        ├─> GeoSAVE audit
Legal LLM evaluation ────────┤        │      ├─ physical outcome (frozen)
Structured-output reliability ┤        │      ├─ legal status (separate)
Human-centered accountability ┘        │      └─ raw/parsed response audit
                                        └─> no inference of human worth or model cognition
```

| Taxonomy | Included examples | What it establishes | What it does not establish |
| --- | --- | --- | --- |
| Driving perception/reasoning | DriveLM, SimpleLLM4AD, ReasonDrive | VLMs can be evaluated through perception, prediction, planning, behavior, and VQA; richer context can help. | A language rationale is not proof of faithful reasoning, and such benchmarks do not evaluate jurisdictional law. |
| Driving planning/action | LMDrive, DriveGPT4-V2 | Language-conditioned systems can be assessed in closed loop. | Closed-loop control scores do not answer whether a model changes an action appropriately when applicable law changes. |
| Regulation-aware driving | Prakken; lawful-driving requirements | Legal rules involve exceptions, conflicts, vagueness, and context. | A general traffic-law framework is not a reviewed multi-jurisdiction dataset. |
| Machine-readable traffic law | TARGET; PROLOG formalization | Validation, restricted DSLs/predicates, and human review limit legal-formalization error. | LLM-generated rules alone are not legal ground truth. |
| Legal reasoning with LLMs | Hu et al.; Mishra et al.; Yao et al. | Outdated law, interpretation problems, hallucination, irrelevant premises, and factual errors recur. | General legal-task success does not establish lawful driving. |
| Structured-output reliability | SoEval, SchemaRL, StructEval, SOB | Syntax/schema reliability is a separable, imperfect capability; syntactic validity and semantic value correctness differ. | A JSON-only pass/fail is not a valid proxy for driving-decision competence. |
| Multimodal benchmark methodology | IDKB, DriveLM, LMDrive | Specialized driving knowledge and scene representations matter. | Training/control benchmarks do not automatically yield an auditable cross-jurisdiction action audit. |
| Human-centered explanation/accountability | Amershi et al.; Jacovi and Goldberg; FactSheets | Systems should disclose uncertainty, limitations, provenance, and failures; explanation plausibility differs from faithfulness. | This project is not a human-subject study and cannot infer trust or cognition from output text. |

## Closest prior work and gap

LMDrive and DriveGPT4-V2 are closest on multimodal action/control and closed-loop simulation. DriveLM is closest on structured visual reasoning across perception, prediction, planning, and behavior. IDKB is closest on driving-rule knowledge across countries and tests 15 LVLMs. Prakken, TARGET, and the PROLOG work are closest on lawful-driving requirements and machine-readable rules. None of these reviewed works was found to combine all of the following in one evaluated design: a frozen physical action-outcome matrix, reviewed jurisdiction-specific legal evidence, controlled legal-context conditions, multimodal model action selection, explicit safe-illegal/unsafe-lawful/unknown labels, and a demographic wording audit.

That is a meaningful but bounded research gap. It must be written as “within the reviewed literature,” and it does not support a “first” claim.

## Implications for GeoSAVE design

1. Keep Phase 4 physical data fixed and independent of jurisdiction/model decisions.
2. Keep the Phase 5 primary-law subset separate from broad contextual indicators.
3. Preserve unknown law, safety-law conflict, and legal-claim uncertainty as reportable states.
4. Treat the supplied legal evidence as a bounded context, not model legal knowledge; audit unsupported legal claims against evidence IDs.
5. Record explanation text as stated factors/rationale and test only behavioral consistency as a faithfulness proxy.
6. Report schema/format reliability independently from one unambiguous action decision.
7. Treat the bird's-eye plus telemetry package as a limited open-loop audit input, not sensor-equivalent production autonomy.

## Structured-output conclusion

The literature supports strict schema compliance as a secondary systems-reliability outcome, not a hard scientific exclusion criterion for the driving-decision construct. The Phase 6 v2 line protocol consequently separates `format_compliance`, `native_schema_success`, `normalization_success`, and `semantic_decision_success`. It never repairs substantive content: it cannot infer an action from a rationale, choose between actions, rename actions, or create factors/evidence/rationale that the response did not state.

## Literature limitations

Rapid model and provider change means the 2026 candidate-model review will become stale; model selection must therefore use current official provider documentation and a live non-generative preflight immediately before any pilot. Some recent law-aware driving publications are preprints and are marked as such. The review is English-language/source-access constrained and is not evidence that a contribution is globally unique.
