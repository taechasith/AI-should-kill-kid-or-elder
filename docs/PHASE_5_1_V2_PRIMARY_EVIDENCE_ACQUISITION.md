# Phase 5.1 v2 — Primary Legal Evidence Acquisition

This stage follows a one-way evidence chain:

```text
official source → extracted proposition → reviewer interpretation →
applicability → formal rule → action-level result
```

It never starts with a desired action label and searches backward for support.
The collection workflow is machine-readable in
`configs/legal/phase5_v2_collection_workflow.json`.

`NOT_DETERMINED` is reserved for a record that has not completed review. A
completed review must use a more informative final outcome where supported:
`PROHIBITED`, `REQUIRED`, `EXPLICITLY_PERMITTED`,
`CONDITIONALLY_PERMITTED`, `NOT_APPLICABLE`,
`INSUFFICIENT_SCENARIO_FACTS`, `LEGAL_AMBIGUITY`,
`CONFLICTING_AUTHORITIES`, or `NO_CONTROLLING_PRIMARY_RULE_FOUND`.

Before a record can leave `NOT_DETERMINED`, the reviewer must document the
official source search, either cite controlling primary authority or document
that none was found, assess jurisdictional and factual applicability, and link
the formal rule to evidence. International instruments are supplementary
context, never a substitute for domestic applicability analysis.
