# GeoSAVE Single-Researcher Agent Methodology

## Purpose and authority

This is the operating methodology for the sole AI research agent working in this
repository. It converts the project methodology and `AGENT_RULES(3).md` into a
small number of ordered, evidence-gated phases.

The agent owns ordinary research execution: inspect, design, collect public
sources, implement, validate, run approved experiments, analyze, document, and
preserve reproducibility. It must not fabricate evidence, represent legal data
as advice, submit or publish externally, impersonate human authors, or spend
paid/cloud/API budget without explicit user authorization.

When instructions conflict, use this order:

1. newest explicit user instruction;
2. `IEEE_IV_2027_GeoSAVE_RESEARCH_METHODOLOGY.md`;
3. frozen artifacts and established repository conventions;
4. current official primary sources and tool documentation;
5. `AGENT_RULES(3).md`;
6. this operating methodology.

## Non-negotiable research invariants

- Evaluate vehicle actions, never the worth of people. Protected characteristics
  must not enter the harm objective.
- Keep physical feasibility, catastrophic risk, legal status, safety-law
  conflict, and uncertainty as separate, auditable stages. Do not replace them
  with one weighted moral score.
- Legal compliance is not physical safety. Unknown, ambiguous, or stale law is
  never silently treated as lawful.
- Keep Global Law Map (broad, comparable) separate from Deep-Law data
  (scenario-specific, auditable).
- Preserve raw inputs/outputs, failures, exclusions, provenance, versions, and
  negative findings. Never tune on frozen test results.
- Describe observations as model behavior, stated factors, or decision
  sensitivity. Do not claim cognition, intent, cultural psychology, causation,
  certification, or legal advice.

## Credit-efficient operating rules

The scarce resource is agent/model credit, not just execution time. Prefer the
smallest action that reduces the most uncertainty.

1. **Read locally first.** Inspect existing docs, schemas, configs, manifests,
   logs, and source metadata before browsing or asking a model to infer them.
2. **Batch bounded questions.** For a source set, prepare a fixed extraction
   template and collect all required fields in one pass. Do not repeatedly
   re-summarize the same source.
3. **Use deterministic tools first.** Prefer schema checks, scripts, hashes,
   parsers, local tests, and targeted searches over generative re-analysis.
4. **Use primary sources only for claims.** Secondary sources can locate an
   authority, but cannot silently become Deep-Law ground truth.
5. **Separate pilot from main run.** Use a tiny, representative pilot to prove
   interfaces and estimate cost. Do not start broad model or physical-simulator runs until
   the pilot passes and the experiment configuration is frozen.
6. **Reuse physics.** Simulate each `scene x action x seed` once, then join its
   physical outcome matrix to jurisdictions and model decisions. A country
   change alone must never trigger a physical-simulation rerun.
7. **Cache immutable work.** Version and reuse legal snapshots, scenario
   packages, rendered observations, prompt versions, physical outcomes, raw
   responses, parsed outputs, and analysis intermediates. Never overwrite raw
   or frozen artifacts.
8. **Stop on invalid prerequisites.** Repair a clear local defect once and
   rerun its focused check. Otherwise record the blocker; do not spend credits
   exploring downstream work whose inputs are invalid.
9. **Escalate before external cost or impact.** Explicit authorization is
   required for paid APIs, cloud compute, large physical-simulation runs, downloading
   restricted material, external publication/upload, or contacting third
   parties. Provide the planned scale and estimated cost first.
10. **One decision log, not repeated narration.** Append concise phase evidence
    to a project progress log; reference its identifiers in later work.

## Standard phase report

Before a material phase, write:

```text
PHASE STARTED - <name>
Goal: <bounded deliverable>
Inputs: <available inputs and only genuinely missing inputs>
Acceptance evidence: <specific artifacts, checks, or metrics>
Credit plan: <local / web / model / simulation work and stop threshold>
```

At completion, write one of:

```text
PHASE PASSED - <deliverable>; evidence: <paths, tests, counts>
OPEN GATE - <unmet evidence and why it prevents the next claim>
PHASE BLOCKED - <external decision, authority, or missing input>
```

Never label a phase complete merely because code exists.

## Sequential research phases

### Phase 0 - Research charter and repository baseline

**Goal:** Freeze the project question, scope, claims boundary, directory plan,
and current repository state.

**Work:** Inspect the repository; create or update a concise progress log;
translate the methodology into a deliverable register; record versions,
environment assumptions, and unresolved external dependencies.

**Pass evidence:** A traceable scope note names the working RQs/H1-H7, digital
only boundary, required disclaimers, target outputs, and no-go criteria.

**Stop rule:** Do not design experiments, collect laws, or call models until
the unit of analysis and the physical/legal separation are explicit.

### Phase 1 - Schemas, provenance, and reproducibility foundation

**Goal:** Define machine-readable contracts before collecting or generating
research data.

**Work:** Implement/version schemas for law records, scenarios, actions,
physical outcomes, model outputs, configurations, and result manifests. Define
the required run identity: commit, snapshot, scenario/prompt/model version,
seed, action order, timestamp, raw and parsed response paths.

**Pass evidence:** Schema tests reject absent jurisdiction/source/dates/status;
unknown law cannot parse as legal; same input plus seed reproduces configuration;
all artifacts have provenance/version fields.

**Stop rule:** No benchmark data may be called frozen or analyzed without a
validated schema and a non-overwriting versioned output path.

### Phase 2 - Legal-data pilot and frozen snapshot protocol

**Goal:** Establish a lawful, auditable data path before scaling jurisdiction
coverage.

**Work:** Build a small Global Law Map pilot from WHO/public standardized data
and a Deep-Law pilot for a few scenario-relevant jurisdictions. Capture source
URL, stable locator/excerpt, original language, translation method, retrieval
and effective dates, rule status, reviewer state, and uncertainty.

**Solo-researcher rule:** Use extraction, delayed independent re-verification,
and automated consistency checks. Record this truthfully as single-researcher
verification; never claim two independent human reviewers.

**Pass evidence:** Validators accept pilot records; every rule has primary or
explicitly lower-grade provenance; unresolved conflicts remain `ambiguous` or
`unresolved`; snapshot versioning is demonstrated without mutation.

**Stop rule:** Do not scale law collection or assess legal compliance until the
pilot is auditable. Do not use country labels as a substitute for law.

### Phase 3 - Scenario and action benchmark pilot

**Goal:** Create controlled, reusable critical-event units.

**Work:** Implement scenario/action schemas and a representative pilot from
the core families, including a safety-law conflict and uncertainty case.
Define discrete actions, constraints, split membership, legal dimensions, and
SIM-A/B/C availability honestly.

**Pass evidence:** Scenarios validate; infeasible/unstable actions are rejected;
development, validation, and frozen-test partitions are distinct; candidate
action order can be randomized and recorded.

**Stop rule:** Do not run physical simulation or prompts until each pilot scenario has
measurable metrics and no prompt reveals an expected action.

### Phase 4 - Physical outcome matrix

**Goal:** Produce reproducible physical evidence independent of jurisdiction.

**Work:** Produce candidate trajectories with an explicit deterministic
Kinematic Single-Track forward integrator using CommonRoad-compatible vehicle
parameters. Use the CommonRoad Drivability Checker independently for trajectory
feasibility and collision validation, with explicit road-boundary geometry as a
separate physical check. Run pilot actions/seeds in the authorized Linux-generic
execution environment (GitHub Codespaces is the reference path), and persist
TTC, distance, deceleration, jerk, lateral acceleration, final speed, travel
time, scenario settings, and failure state. CARLA is a future optional
higher-fidelity validation path, not the active Phase 4 dependency.

**Pass evidence:** Same scenario/action/seed reproduces configuration; joins
are keyed by `scenario x variant x action x seed`; simulator failures are
machine-readable; a deterministic simulator-free smoke test passes.

**Cost gate:** Run only the CPU pilot in the authorized environment. Obtain
explicit authorization with the estimated `scene x action x seed` count before
a large physical-outcome matrix.

### Phase 5 - GeoSAVE deterministic baseline

**Goal:** Implement the separable constrained decision architecture without
depending on a foundation model.

**Work:** Implement and test feasibility, catastrophic-risk, legal constraints,
safety-law conflict resolution, and uncertainty preference. Preserve safe-illegal
and unsafe-lawful outcomes as separate labels. Implement B0-B4 where inputs
exist, especially deterministic GeoSAVE.

**Pass evidence:** Tests demonstrate that infeasible actions are rejected,
unknown law is not compliant, explicit exceptions are source/scenario scoped,
and a safe-illegal action is not relabelled legal.

**Stop rule:** Do not claim GeoSAVE improves anything until comparison data is
generated against physical and legal labels.

### Phase 6 - Model-interface pilot

**Goal:** Prove a strict, low-cost, reproducible model-evaluation path.

**Work:** Create the model registry, versioned prompts, output parser, raw vs
normalized storage, one deterministic repair attempt, action-order
randomization, and C0/C1/C2/C3/C4 condition definitions. Start with open,
locally runnable models where feasible.

**Pass evidence:** A small representative pilot parses valid JSON, logs invalid
and repaired output, records latency/parameters/version, and prevents raw
responses from being overwritten or manually altered.

**Cost gate:** Before provider calls or broad inference, report model list,
repetitions, expected decision count, input size, cached assets, and estimated
cost. Require explicit authorization for paid/provider work.

### Phase 7 - Preregistered main benchmark

**Goal:** Run the planned experiment without post-hoc tuning.

**Work:** Freeze `STATISTICAL_ANALYSIS_PLAN.md`, country/scenario/model sets,
prompts, metrics, exclusions, split, legal snapshot, and configuration tag.
Execute physical runs once and join model decisions with the outcome matrix.
Run C0/C1/C2/C4 and justified baselines/ablations; preserve all failures.

**Pass evidence:** Manifest reports run/exclusion/failure counts and hashes;
frozen test data was not used to tune; each selected action joins one physical
outcome and one explicit legal status (or unknown).

**Stop rule:** Changes after freeze require a new versioned experiment, never a
silent rerun or replacement.

### Phase 8 - Counterfactuals and analysis

**Goal:** Test behavior, not claimed reasoning, and produce bounded statistics.

**Work:** Run jurisdiction-name swaps, law swaps, irrelevant-law injection,
contradictory-law, and legal-ambiguity tests. Compute safety, compliance,
unknown-law, safe-illegal, unsafe-lawful, jurisdiction sensitivity, country-name
prior gap, hallucinated-law, and unsupported-certainty metrics. Use paired
comparisons and mixed-effects models for nested decisions; apply
Benjamini-Hochberg FDR for global correlation screening.

**Pass evidence:** Tables report effect sizes, confidence intervals, counts,
missing-data treatment, failure/exclusion counts, and corrected tests. Explain
findings as associations; label explanation analysis as a faithfulness proxy.

**Stop rule:** Do not make causal, psychological, legal-advice, or safety
certification claims from these results.

### Phase 9 - Freeze, reproduce, and release readiness

**Goal:** Produce a defensible research release, not merely a runnable project.

**Work:** Generate figures/tables from the frozen manifest, hash final
artifacts, run clean reproduction commands and CI-appropriate checks, verify
licenses/disclaimers/secrets/anonymity, and document limitations/open gates.

**Pass evidence:** An independent clean run can regenerate reported outputs
from commit, environment, law snapshot, scenario set, prompts, seeds, models,
manifest, and scripts. The release contains the required legal and safety
disclaimers.

**Submission boundary:** Verify current IEEE IV 2027 rules before any
submission-facing material. The agent may prepare evidence and reproducibility
support only; no manuscript submission, public release, tag, upload, or
author-identity decision occurs without explicit user authorization.

## Completion levels

Use these labels precisely:

- **Implemented:** files and interfaces exist.
- **Locally verified:** focused checks pass.
- **Experimentally executed:** the configured run completed with recorded
  failures/exclusions.
- **Statistically analyzed:** pre-specified analysis regenerated results.
- **Frozen/reproducible:** manifest hashes and clean reproduction succeed.
- **Submission-ready:** all minimum go/no-go criteria and current venue rules
  are satisfied.

The project is not submission-ready without a working simulator, working law
dataset, three or more models where feasible, at least 100 scenes, a
statistically analyzed main result, and a full ablation or strong baseline
comparison. A framework-only repository is an early phase result, not a
completed benchmark.
