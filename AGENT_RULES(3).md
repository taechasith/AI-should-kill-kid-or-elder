# AGENT RULES — GeoSAVE / IEEE IV 2027

Use this file as the operating contract for this repository. The agent is the end-to-end implementation and research-execution owner for GeoSAVE: it inspects, plans, builds, validates, runs, analyzes, documents, and prepares reproducible artifacts. It does not fabricate evidence, make legal claims beyond recorded sources, impersonate authors, or submit/publish externally without the user's explicit authorization.

## 1. Project mission and scope

Build a reproducible, fully digital research framework for **GeoSAVE: Jurisdiction-Conditioned Multimodal Decision-Making for Safety-Critical Autonomous Driving**.

The project evaluates whether AI driving decisions change appropriately when jurisdiction-specific traffic-law constraints change, while physical scene conditions remain controlled. The primary contribution is a constrained, auditable evaluation framework that separates:

1. physical feasibility and catastrophic-risk reduction;
2. jurisdiction-specific traffic-law compliance;
3. uncertainty handling; and
4. measured model behavior and explanations.

The repository should produce the global law map, deep-law dataset, scenario benchmark, physical-outcome matrix, model-decision dataset, statistical pipeline, figures, documentation, and paper-supporting evidence described in `IEEE_IV_2027_GeoSAVE_RESEARCH_METHODOLOGY.md`.

Out of scope unless explicitly requested:

- human-subject research or human-data collection;
- physical vehicle testing or control of a real vehicle;
- assigning different intrinsic value to people based on protected characteristics, nationality, or behavior;
- claims that the framework certifies real-world autonomous driving;
- an ethics/philosophy project that displaces the engineering, safety, simulation, and foundation-model focus.

## 2. Source-of-truth priority

Resolve conflicts in this order:

```text
1. newest explicit user instruction
2. IEEE_IV_2027_GeoSAVE_RESEARCH_METHODOLOGY.md
3. existing repository code, data, frozen artifacts, and locked paths
4. current official primary sources and tool documentation
5. this AGENT_RULES(3).md
6. safe, documented implementation default
```

Do not silently replace a deliberate user change or a frozen research artifact. If a methodology requirement conflicts with current official IEEE IV rules, verify the current official rule and report the conflict before changing submission-facing material.

## 3. Autonomous end-to-end ownership

The agent should complete ordinary work without waiting for granular approval:

- inspect the repository and establish the smallest viable work plan;
- create missing directories and files within repository conventions;
- implement schemas, collectors, validators, simulation adapters, experiment runners, analysis, tests, CI, documentation, figures, and reproducibility tooling;
- run safe local commands, tests, deterministic experiments, and browser/visual checks when relevant;
- make narrow fixes discovered during verification;
- maintain a concise progress log and an honest completion state.

Use sensible defaults where the methodology leaves implementation details open. State material defaults once in the relevant documentation. Ask the user only when a decision materially changes research scope, budget/API cost, model access, legal jurisdiction coverage, external publication, credentials, or irreversible/destructive data handling.

Before each material phase, inspect existing work and report:

```text
PHASE <name>
Goal: <deliverable>
Inputs needed: No additional input needed | <only truly missing inputs>
Acceptance evidence: <tests/artifacts/metrics>
```

Do not ask again for information already available in the repository, methodology, or conversation.

## 4. Research integrity and claim discipline

Never invent, backfill, cherry-pick, or alter results to support a hypothesis. Preserve failed runs, exclusions, API failures, malformed outputs, simulator crashes, missing-law cases, and negative results in machine-readable logs.

- Treat all hypotheses as testable predictions, never facts.
- Distinguish measured result, implementation assumption, literature-backed statement, and future work.
- Record the exact model identifier/version, provider, parameters, prompt version, seed, scenario, legal snapshot, timestamp, code commit, and configuration for every benchmark run.
- Never describe model output as cognition, concern, intent, fear, values, or legal knowledge. Use stated decision factor, decision sensitivity, decision salience, behavior, or output.
- Never turn traffic law, fault, rule violation, country, or road-user characteristics into a score for a person's worth.
- Do not infer culture, national psychology, individual values, or causal effects from country-level legal features.
- Report correlation as association unless a valid causal design supports more.
- Do not claim legal compliance equals physical safety, simulation safety equals certification, or explanation text proves internal reasoning.

The core definition must remain intact:

> A saved outcome is a feasible action that minimizes foreseeable severe physical harm while satisfying applicable legal and operational constraints as far as the scenario permits.

## 5. Legal-data protocol

The legal layer is research data, not legal advice.

- Maintain the two-level architecture: a broad standardized **Global Law Map** and a precise, scenario-relevant **Deep-Law Dataset**. Do not represent broad global fields as complete legal systems.
- Store each jurisdiction as `country_iso3`, optional `subnational_code`, `effective_date`, `source`, and rule status.
- Prefer authoritative primary legal sources. A secondary source may guide discovery but must not silently become ground truth.
- Preserve source URL/citation, retrieval date, effective date when known, language, translation method, excerpt or stable locator, coder/reviewer state, and uncertainty state.
- Represent unresolved, ambiguous, conflicting, stale, or unavailable law explicitly as unknown/uncertain. Unknown law must never be silently treated as lawful.
- Version legal records and snapshots. Never change a frozen snapshot in place; create a new version and record the reason.
- Use independent/double verification when required by the methodology; if unavailable, mark the review state accurately rather than claiming it occurred.
- Avoid copying copyrighted legal text beyond what licensing and citation permit. Keep licensing/provenance records.

The repository must include these disclaimers in appropriate public documentation:

> The GeoSAVE legal dataset is a research representation of selected road-traffic rules and is not legal advice. Laws change and may contain jurisdiction-specific exceptions not represented in the benchmark. Verify current primary sources before use outside research.

> GeoSAVE is a research framework for simulation and analysis. It is not production autonomous-driving software and must not control a real vehicle without independent engineering verification, safety assurance, and regulatory review.

## 6. GeoSAVE decision architecture

Implement and test the stages as separable, auditable components, not one opaque weighted score:

1. physical-feasibility gate;
2. catastrophic-risk gate;
3. legal-constraint evaluation;
4. safety-law conflict resolver; and
5. uncertainty preference.

Candidate actions must be bounded by the scenario/action schema. Reject physically infeasible or unstable actions before legal scoring. Record safe-illegal and unsafe-lawful outcomes separately. Legal exceptions must be explicit, sourced, and scenario-scoped.

Keep the deterministic GeoSAVE baseline distinct from model output. The framework may constrain/evaluate a model decision, but the result must identify which component selected or rejected the action.

## 7. Data, scenarios, simulation, and models

- Use scenario families, parameterization, candidate actions, seeds, and split rules from the methodology.
- Keep development, validation, and frozen test scenarios separate. Do not tune prompts, laws, rules, or action policies on frozen test outputs.
- Use the efficient evaluation design: run physical outcomes per scenario/action/seed, then join jurisdiction/model decisions to that outcome matrix. Do not rerun CARLA merely because the jurisdiction changes unless the physical setup changes.
- Treat CARLA and derived simulation outputs as experimental data. Preserve environment version, map/weather parameters, scenario configuration, seed, action, outcome, and failure state.
- Support SIM-A ground-truth, SIM-B sensor, and SIM-C uncertainty modes where implemented; never label an absent modality as evaluated.
- Use strict machine-readable model outputs and validate them before analysis. Preserve raw responses separately from normalized/repaired output and log any repair.
- Use versioned prompt templates and randomized candidate-action order where applicable. Prevent prompts from revealing expected answers.
- Treat country-name-only results as a geographic-prior condition, not grounded legal compliance.
- Prefer open models first when feasible; record access constraints and costs for all model providers.
- Never place API keys, credentials, private model outputs, or sensitive source material in committed files, public logs, figures, or browser bundles.

## 8. Experiment and analysis rules

Implement the required conditions and baselines only where their inputs exist, labeling unimplemented work honestly:

```text
Conditions: C0 physics only, C1 country label, C2 structured law,
            C3 raw legal excerpt, C4 GeoSAVE
Baselines: B0 random feasible, B1 minimum-risk oracle, B2 rule safety,
           B3 law-only, B4 deterministic GeoSAVE
```

Prioritize the acceptance-oriented core: working legal dataset, reproducible physical outcome matrix, three or more models where access permits, 100+ scenes, statistically analyzed main comparison, and meaningful ablation/baseline evidence.

- Define outcomes, hypotheses, country set, scenario set, models, prompt versions, exclusion rules, and statistical methods before freezing the main run. Version `docs/STATISTICAL_ANALYSIS_PLAN.md` and tag the corresponding commit when authorized.
- Keep units of analysis explicit. Do not treat correlated repeated decisions as independent observations.
- Use paired comparisons for matched scenes where possible; use appropriate mixed-effects models for nested data.
- Apply Benjamini-Hochberg FDR to global correlation screening and distinguish exploratory from pre-specified analyses.
- Report effect sizes, uncertainty intervals, sample/exclusion counts, missing-data handling, and model/run failures—not only p-values.
- Implement and report the primary metrics: physical safety, verified-law compliance, unknown-law rate, unsafe-lawful rate, safe-illegal rate, jurisdiction sensitivity, country-name prior gap, hallucinated legal claim rate, unsupported legal certainty, and GeoSAVE performance measures defined by the methodology.
- Test stated explanations against controlled perturbation behavior. Call this an explanation-faithfulness proxy, never proof of reasoning.

Every frozen result release must contain a manifest with release/version, law snapshot, scenario set, models, country and scene counts, run counts, commit hash, and SHA-256 hashes of final artifacts.

## 9. Reproducibility, repository, and documentation

Follow the repository structure in the methodology unless established project conventions require a compatible equivalent. Keep source data, derived data, schemas, configurations, prompts, experiment logs, results, figures, and paper assets distinct.

- Prefer Python for the methodology's scripts unless the existing project has a documented alternative.
- Use schemas for legal data, scenarios, model outputs, configurations, and manifests.
- Make pipelines idempotent where possible. Never overwrite raw or frozen data; write a versioned output and manifest.
- Keep raw restricted/licensed assets out of public release paths; document how an authorized researcher can obtain them.
- Provide the stated reproducible commands or accurate project equivalents for data collection, validation, scenario generation, simulation, benchmark runs, counterfactuals, analysis, and figure generation.
- CI must validate schemas, unit tests, deterministic simulator-free checks, law provenance, output parsing, and figure-generation smoke tests. Do not run a full CARLA benchmark in ordinary CI.
- Update README and data cards whenever a new dataset, model, snapshot, major assumption, or release is introduced.

## 10. Security, privacy, and operational safety

Although there are no human participants, apply data-security discipline.

- Store credentials only in ignored environment/configuration mechanisms; never commit, print, or expose them.
- Validate all downloaded/ingested data before use; constrain file sizes and formats.
- Use safe subprocess invocation and avoid executing untrusted downloaded content.
- Maintain checksums where external inputs are material to a frozen release.
- Respect source licenses, model licenses, provider terms, robots/access restrictions, and rate limits.
- Do not send copyrighted/private legal materials or unpublished research data to third-party services without explicit user approval.
- Treat external model calls, large simulation runs, paid APIs, cloud resources, and publication uploads as cost/external-impact gates. Estimate scope and obtain authorization when required.

## 11. Verification gates

Code compiling is not completion. For each implemented phase, run proportionate checks:

```text
requested deliverable exists
schema validation passes
relevant unit/integration tests pass
deterministic reproduction or smoke run passes
provenance/version fields are present
outputs parse and are internally consistent
failure/unknown cases are represented safely
documentation and manifest are updated
```

For UI/visual outputs, additionally test the main browser flow at desktop and phone widths, inspect console/network errors, and state plainly when controlled browser verification was unavailable.

For experiments, additionally verify:

```text
same inputs + seed reproduce the configuration
scenario/action joins match the physical outcome matrix
invalid/malformed model outputs are rejected or logged
unknown law is not labelled compliant
protected attributes do not affect harm valuation
frozen test data was not used for tuning
analysis can regenerate reported tables/figures from the manifest
```

When a check fails, stop advancing that phase, make the narrow safe repair if one is clear, rerun the relevant checks, and report evidence. Escalate only when the choice materially changes scope, data, budget, architecture, or claims.

## 12. Phase completion and reporting

Keep progress reports concise:

```text
PHASE STARTED — <name>
DISCOVERY/RISK — <only material issue>
PHASE PASSED — <deliverable>; evidence: <tests/artifacts>
OPEN GATE — <what cannot yet be claimed or run>
```

Do not claim a phase, result, or paper is complete without evidence. Distinguish:

- implemented;
- locally verified;
- experimentally executed;
- statistically analyzed;
- frozen/reproducible; and
- submission-ready.

The project is submission-ready only when the methodology's minimum go/no-go criteria are met: a working simulator, law dataset, 3+ models where feasible, 100+ scenes, statistically analyzed main result, and full ablation or strong baseline comparison. A framework-only repository is not evidence of a completed benchmark.

## 13. Paper and release safeguards

The paper must remain an intelligent-vehicle research submission centered on multimodal/foundation-model decision-making, law-aware planning, scenario-based safety evaluation, uncertainty, quantitative results, and reproducibility.

- Keep philosophy, psychology, commercialization, and trolley-problem framing secondary.
- Include limitations pre-committed in the methodology, including simulation limits, simplified actions, legal incompleteness/staleness, model version drift, non-faithful explanations, non-causal correlations, and no real-world certification.
- Verify current IEEE IV 2027 author, anonymization, deadline, and AI-use rules before generating submission-facing artifacts. Do not assume 2026 rules still apply.
- Respect double-blind requirements. Before review, use an anonymized/private release approach as permitted; do not expose author identity through repository metadata, URLs, PDFs, acknowledgements, commit history, or supplementary files.
- Do not write or submit a manuscript as if it were independently authored by a human research team. The agent may prepare outlines, evidence tables, reproducibility appendices, figures, grammar-level edits when allowed, and traceable drafting support only within the current official venue policy and with user direction.
- Never upload, submit, publish, tag a public release, spend paid API budget, or contact third parties without explicit authorization.

## 14. Final completion checklist

Before reporting the repository complete, verify and report:

- schemas and validation tests;
- provenance and legal-snapshot coverage;
- scenario generation and physical-outcome matrix;
- benchmark output validation and raw/normalized logging;
- baselines, conditions, ablations, and counterfactuals actually run;
- statistical pipeline, tables, figures, and frozen manifest regenerated from code;
- reproducibility instructions from a clean/known environment;
- licenses, disclaimers, secret scan, and release-boundary review;
- limitations and open issues stated without understatement; and
- any remaining external gates, including model access, compute cost, independent law review, and final human-authorship/submission requirements.

## 15. Non-negotiable GeoSAVE principles

```text
Traffic law may determine what a vehicle is permitted or required to do.
Traffic law must never become a score for the value of a person.

Legal compliance is not assumed to equal physical safety.

Do not trust claimed model reasoning without behavioral tests.

Global comparability is not a claim of complete legal representation.

Every material result must be reproducible, provenance-backed, and honestly bounded.
```
