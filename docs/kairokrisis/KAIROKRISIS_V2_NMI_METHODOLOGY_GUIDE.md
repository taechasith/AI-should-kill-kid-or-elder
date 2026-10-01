# KAIROKRISIS v2 — Nature Machine Intelligence Research Expansion Guide

**Status:** Prospective research plan  
**Date:** 2026-10-02  
**Supersedes:** None. The frozen Phase 4–9 pilot remains immutable.  
**Target venue:** *Nature Machine Intelligence* (aspirational, not guaranteed)  
**Target content type:** Article, unless later editorial assessment supports Analysis  
**Operational horizon:** ~72 hours of agent-assisted research using the existing repository, compute, simulator, and zero-cost/provider resources unless the research team explicitly authorizes otherwise.

---

## 0. New project identity

### Working name: **KAIROKRISIS**

**ASCII/repository form:** `Kairokrisis`

KAIROKRISIS is a coined compound from two Ancient Greek ideas:

- **kairos**: the critical, fitting, or opportune moment for action;
- **krisis**: judgment, decision, distinguishing, or choosing at a decisive point.

The intended research meaning is:

> **judgment at the critical moment**

This fits the scientific problem better than a driving-specific name because the research is no longer intended to ask only whether an AI chooses a particular driving maneuver. It asks how machine decisions behave when a decision must be made at a critical moment and when different notions of “success” can diverge.

A web search performed on 2026-10-02 found **no obvious indexed exact-match use of “Kairokrisis”** as an AI benchmark, company, software product, robotics project, driving benchmark, or GitHub project. This is not a trademark or legal clearance. Before public branding, repeat the collision search and, if necessary, conduct formal trademark/domain checks.

Useful etymological background:
- Ancient Greek *krisis* derives from *krinein/krino*, associated with distinguishing, choosing, deciding, and judging.
- *Kairos* is commonly used for the fitting or critical moment for action.

The historical pilot name and all frozen tags/commits must remain unchanged for provenance. KAIROKRISIS begins as a **new versioned research programme**, informed by the pilot rather than rewriting it.

---

# 1. Why the project is changing

The Phase 4–9 pilot successfully established a reproducible pipeline separating:

1. semantic decision validity;
2. strict output-format validity;
3. physical feasibility and consequences;
4. map/road-constraint compliance;
5. jurisdictional legal evidence.

The pilot also established an important evidence boundary: jurisdictional legal compliance is **NOT_ESTIMABLE** from the current legal snapshot.

The next project should not simply add more rows to the pilot.

The new goal is to test a broader scientific proposition:

> **Safety-critical AI evaluation may be structurally misleading when it collapses distinct layers of decision quality into one score.**

The key scientific question is whether the layers that are often treated as proxies for one another actually agree:

- Does better structured-output compliance predict safer physical action?
- Does an explicit valid action imply a physically acceptable action?
- Do model comparisons remain stable when the evaluation layer changes?
- Do physically identical scenes produce stable decisions when only human semantic labels change?
- Do interface constraints alter formatting without equivalently altering downstream physical risk?
- Which conclusions are empirically supported, and which remain outside the evidence?

The v2 research must **test** these possibilities. It must not assume them.

---

# 2. Editorial target and scientific threshold

The aspirational target is *Nature Machine Intelligence* (NMI).

Current NMI guidance states that Articles are substantial novel studies with a complex story, often combining multiple techniques or approaches. NMI covers AI, robotics, human–robot interaction, transport, and ethical/social/legal implications of machine intelligence.

Nature Portfolio peer-review guidance states that a publishable paper should represent an advance in understanding likely to influence thinking in the field, with strong evidence, and should have a discernible reason for Nature Portfolio visibility rather than only a specialist venue.

Therefore, **scale alone is not the target**.

A successful 72-hour expansion must aim to establish a general and falsifiable phenomenon, not merely produce a larger driving dataset.

### Nature-facing scientific thesis to test

A possible high-level thesis is:

> **Decision-layer divergence:** interface compliance, semantic decision validity, and downstream physical safety are empirically distinct properties of multimodal AI systems, and interventions that improve one layer do not necessarily improve the others.

This is a hypothesis/programme-level framing. Do not write it as an established conclusion until the new experiment supports it.

---

# 3. Frozen pilot foundation

The original Phase 4–9 pilot remains immutable.

Authoritative checkpoints include:

- Phase 8A commit: `852df37`
- Phase 8A tag: `phase8a-confirmatory-analysis-v1`
- Phase 9 commit: `3eac34c`
- Phase 9 tag: `phase9-final-synthesis-v1`
- recovered Phase 7 base: `99551fa`
- clean Linux/CommonRoad reproduction: `CLEAN_REPRODUCTION_PASSED`
- full compatible Linux test suite: 108 tests passed

Frozen pilot headline evidence:

- design rows: 5,454
- not applicable: 1,350
- provider population: 4,104
- certainty observations: 279
- probability sample: 60
- terminal analysis observations: 339
- valid allowlisted actions / physical joins: 323
- valid allowlisted-action estimate: 82.38%
- approximate 95% CI: 73.40%–91.36%
- strict JSON estimate: 62.37%
- approximate 95% CI: 56.51%–68.22%
- valid-action-linked collision mean: 25.41%
- physical-feasibility mean: 81.87%
- map/road-compliance mean: 82.07%
- conditional weighted minimum distance: 3.106 m
- jurisdictional legal compliance: `NOT_ESTIMABLE`

These values are **pilot evidence**, not targets that the v2 experiment should reproduce.

The new benchmark must not modify, overwrite, or silently extend frozen pilot artifacts.

---

# 4. Research principles for KAIROKRISIS v2

## 4.1 Preserve layer separation

Never collapse these into one score:

- response availability;
- semantic action validity;
- strict serialization/JSON validity;
- physical feasibility;
- collision outcome;
- clearance;
- map/road constraint compliance;
- jurisdictional legal compliance.

Legal compliance remains blocked unless a separately validated legal dataset is completed.

## 4.2 No demographic value weighting

KAIROKRISIS must never encode numerical “value” for a child, older adult, pedestrian, passenger, cyclist, or other person.

No demographic group receives a moral score or utility weight.

Counterfactual demographic analyses, if run, measure **decision sensitivity/invariance**, not the moral worth of a group.

## 4.3 No parser inference

A parser may recognize a clearly stated allowlisted action.

It may not invent, repair, or infer an unstated action.

## 4.4 New experiments require prospective specifications

Before new model calls or simulation expansion, freeze:

- scenario grammar;
- factors and levels;
- hypotheses;
- primary outcomes;
- exclusions;
- missingness rules;
- sampling/full-factorial design;
- statistical estimators;
- multiplicity policy;
- stopping rules;
- provider/model identity rules.

## 4.5 Preserve all failed and deferred execution states

HTTP errors, quota delays, parse failures, refusals, invalid actions, and unavailable outputs remain part of the evidence.

Do not silently retry until success without preserving attempt history.

## 4.6 Zero-cost constraint unless explicitly changed

Do not incur API charges without explicit research-team authorization.

Provider eligibility and account state must be documented before execution.

A model endpoint must be recorded exactly, including provider and model ID.

---

# 5. The 72-hour research strategy

The next three days should optimize **scientific information gain**, not row count.

The work is divided into gates K0–K8.

No later gate may silently repair a failure in an earlier gate.

---

# K0 — Repository reset, naming audit, and clean scientific branch

## Goal

Create a clean v2 lineage containing the frozen scientific foundation and no obsolete manuscript-preparation clutter.

## Actions

1. Inspect the complete Git graph and current working tree.
2. Do not delete historical branches or tags.
3. Create a new branch from the authoritative frozen scientific lineage, preferably:
   - `phase9-final-synthesis-v1`
   - plus the clean Linux reproduction report if it exists in a later scientific-only commit.
4. Branch name:
   - `kairokrisis-v2`
5. Do **not** branch from an IJHCI manuscript-preparation commit unless unavoidable.
6. If the clean Linux validation exists only in a later manuscript branch, cherry-pick only the scientific validation commit/file.
7. Exclude/delete from the **new branch only** obsolete IJHCI drafting artifacts, export ZIPs, render-QA directories, and temporary conversion files that are unrelated to the new Nature-facing research goal.
8. Never delete the old branches/tags that preserve those files historically.
9. Keep `.env.example` untouched unless it is tracked scientific infrastructure and a change is explicitly required.
10. Run an exact-name collision audit for:
    - `Kairokrisis`
    - `KAIROKRISIS`
    - `"Kairokrisis benchmark"`
    - `"Kairokrisis AI"`
    - GitHub repository/project names
    - scholarly title/index searches
    - major company/product web searches.
11. Record results in `docs/kairokrisis/NAME_AUDIT.md`.
12. Update only the new v2 README/project-facing metadata to explain:
    - historical project/pilot names remain part of provenance;
    - KAIROKRISIS is the new research programme.

## Gate

Do not rename the remote repository automatically.

Do not rewrite frozen tags.

Proceed only when the v2 branch is scientifically clean and the naming audit shows no obvious collision.

---

# K1 — Freeze the new scientific question before generating new evidence

Create:

`docs/kairokrisis/KAIROKRISIS_V2_PREREGISTRATION.md`

and a machine-readable equivalent:

`data/kairokrisis/v2/preregistration.json`

The preregistration must define the hypotheses below before new experimental result inspection.

## Primary research question

> To what extent do interface reliability, semantic decision validity, and downstream physical safety agree or diverge in multimodal AI decision-making under critical driving conditions?

## Primary hypotheses

### H1 — Interface-to-safety association

Test whether strict structured-output compliance predicts downstream physical safety among observations with interpretable actions.

Primary effect should be reported as a design-consistent effect size with uncertainty, not merely a p-value.

Do not prespecify that the association must be weak or strong.

### H2 — Interface intervention effect

Randomized/paired prompt-interface manipulation:

- natural explicit-action interface;
- strict structured-output interface.

Test separately whether the intervention changes:

1. strict format validity;
2. semantic action validity;
3. collision risk;
4. physical feasibility;
5. clearance;
6. map/road compliance.

The important scientific question is whether improving the interface layer transfers to downstream physical outcomes.

### H3 — Cross-layer ordering stability

Assess whether relative model performance is stable across evaluation layers.

Do not collapse metrics.

Report cross-metric rank concordance/correlation only where statistically meaningful.

If ordering changes, report the pattern rather than declaring a universal “best” model.

### H4 — Counterfactual semantic invariance

For matched physically invariant scenes, change only the semantic identity label of an involved human agent.

Primary measure:

`counterfactual action flip rate`

Secondary measures:

- action-distribution distance;
- safety-outcome change rate;
- model × semantic-condition interaction.

This is a **sensitivity/invariance** analysis.

It is NOT evidence that a model morally values one demographic group more than another.

### H5 — Multimodal representation stability

Where technically feasible, compare:

- image + structured text/context;
- semantically equivalent text-only representation.

Measure whether the chosen action and its downstream physical consequences are stable across representations.

This tests representation dependence rather than claiming one modality is universally superior.

## Exploratory analyses

Any analysis not frozen in K1 must be labeled exploratory.

Do not silently promote an exploratory discovery into a confirmatory result.

---

# K2 — Expand the scenario grammar

## Goal

Move beyond three pilot scenario families while retaining deterministic physical linkage.

### Minimum target

Aim for:

- **12 scenario families**
- **at least 120 unique base physical scenes**
- approximately 10+ systematically varied scenes per family

If the simulator pipeline can support more without compromising QA, scale further.

Do not sacrifice validity for volume.

## Candidate family classes

Use the existing pilot scenario architecture where applicable, then add physically distinct families such as:

1. pedestrian crossing conflict;
2. occluded pedestrian emergence;
3. cyclist conflict;
4. motorcycle cut-in;
5. vehicle cut-in;
6. stopped obstacle / blocked lane;
7. intersection crossing conflict;
8. turning-path conflict;
9. multi-agent conflict;
10. emergency braking / lead-vehicle event;
11. constrained-lane evasive choice;
12. limited-visibility / occlusion condition.

These are candidate categories, not mandatory labels. The agent must adapt them to the actual CommonRoad-compatible scenario generator and validate that they are meaningfully distinct.

## Controlled factors

Where physically valid, vary prospectively defined factors such as:

- ego speed;
- time-to-conflict;
- stopping distance;
- obstacle/pedestrian position;
- occlusion;
- available lane/escape geometry;
- road curvature;
- friction or equivalent physical condition if supported;
- number of interacting agents.

## Scenario validity checks

Every generated scene must pass:

- schema validation;
- deterministic regeneration;
- physically interpretable initial state;
- unique scenario ID;
- provenance/hash;
- no impossible geometry;
- no accidental leakage of answer/action labels into model input.

---

# K3 — Build the expanded physical counterfactual benchmark

## Goal

Precompute physical outcomes for every allowlisted action so model decisions can be linked to a deterministic physical consequence.

### Recommended target

For at least 120 base scenes and the full allowlisted action set, target **600+ canonical action-level physical outcomes**.

If the expanded scenario grammar supports a larger matrix safely, aim for approximately 1,000+ canonical outcomes.

Volume is secondary to deterministic validity.

## Required physical metrics

Retain existing definitions where possible:

- collision;
- physical feasibility;
- minimum distance/clearance;
- map/road constraint compliance;
- trajectory completion/failure;
- any existing deterministic risk variables.

Add new metrics only prospectively with definitions and tests.

## Validation

- repeat deterministic subset;
- verify hashes;
- run CommonRoad regression tests;
- validate join uniqueness:
  `scenario × condition × action → exactly one physical outcome`
- preserve failure states rather than dropping them.

Freeze this expanded physical snapshot before new model calls.

Suggested tag after completion:

`kairokrisis-physical-v2`

---

# K4 — Freeze model and interface panel

## Goal

Use model diversity strategically without introducing uncontrolled provider substitutions.

### Minimum panel

Retain at least the distinct model families already validated in the pilot if still available under the authorized cost constraint.

Historical identities must remain historical; do not rewrite providers.

For all new calls, record:

- provider;
- exact model endpoint;
- model family;
- model version/date if exposed;
- modality support;
- structured-output support;
- free/paid eligibility;
- account-plan evidence;
- request parameters.

### Preferred expansion

If additional genuinely distinct multimodal model families are available at zero additional cost and can be validated prospectively, add them.

Do not add near-duplicate endpoints merely to inflate model count.

### No silent substitution

If a frozen endpoint becomes unavailable:

- record unavailable;
- stop that stratum or activate a prospectively defined replacement rule;
- never silently swap models after seeing outcomes.

---

# K5 — Core model experiment

## Preferred factorial design

For the core scenario set, aim for a paired design crossing:

- scenario;
- model;
- interface condition;
- representation condition.

Suggested interface conditions:

1. explicit allowlisted action, natural response format;
2. strict structured-output / JSON format.

Suggested representation conditions:

1. multimodal scene input;
2. semantically matched text-only representation, if the conversion can be frozen and validated before calls.

### Resource-aware target

A scientifically useful core could be approximately:

`120 scenes × 3 models × 2 interface conditions × 2 representations = 1,440 terminal target decisions`

Additional counterfactual semantic pairs may be run on a prespecified subset.

This is a target, not permission to violate provider limits or incur costs.

If full factorial execution cannot be completed with the authorized resources:

1. do not opportunistically shrink based on observed results;
2. use a prospectively specified stratified probability sample;
3. preserve inclusion probabilities;
4. use design-consistent estimators;
5. report that the evidence is sampled rather than a census.

## Execution controls

- deterministic manifest before calls;
- exact request ID;
- attempt log;
- rate-limit handling;
- bounded retry rules;
- no result-dependent retries;
- raw response hash;
- parser version;
- action validity;
- strict-format validity as separate field;
- latency/token/cost metadata when available.

---

# K6 — Counterfactual semantic audit

## Goal

Test whether model decisions change when semantic human labels change but the physical scene remains invariant.

This is central to the provocative child/older-adult framing, but it must be methodologically careful.

### Design

Create matched pairs where:

- geometry is identical;
- trajectories are identical;
- physical constraints are identical;
- image embodiment is either controlled/neutralized or deliberately manipulated in a documented factorial design;
- only the intended semantic identity label changes.

Example conceptual pair:

- condition A: person described as a child;
- condition B: physically identical person described as an older adult.

Do not alter body size, speed, location, collision probability, or stopping-distance requirement unless those changes are a separate factor.

### Primary metric

`action_flip = action_A != action_B`

Report:

- overall counterfactual flip rate;
- model-specific flip rate;
- scenario-family variation;
- physical-consequence change rate.

### Negative controls

Add at least one non-moral label perturbation that should not alter the decision, for example:

- neutral identifier A/B;
- irrelevant color/name token;
- reordered non-causal metadata.

This helps distinguish general prompt instability from demographic semantic sensitivity.

### Interpretation rule

Never write:

> “the model values children more/less”

from a flip-rate result alone.

Permitted framing:

> “the model’s action selection was sensitive to the demographic semantic label under physically matched conditions.”

Any moral interpretation requires additional theory and evidence.

---

# K7 — Cross-layer divergence analysis

## Goal

This is the principal scientific synthesis.

Create a pre-registered cross-layer matrix covering, where estimable:

- semantic action validity;
- strict format validity;
- collision;
- physical feasibility;
- clearance;
- map/road compliance;
- counterfactual action stability.

Jurisdictional legal compliance remains blocked unless a separately completed legal dataset exists.

## Core analyses

### 7.1 Layer concordance

Quantify pairwise association/concordance among the measurable layers.

Use appropriate statistics for metric type and sampling design.

### 7.2 Conditional safety

Estimate physical outcomes conditional on:

- strict-format success/failure;
- semantic valid-action success;
- interface condition;
- representation condition;
- model;
- scenario family.

### 7.3 Prompt-interface causal contrast

Because interface condition is paired/randomized prospectively, estimate the effect of structured-output constraints on:

- format reliability;
- semantic validity;
- physical outcomes.

Do not assume gains transfer across layers.

### 7.4 Cross-model stability

Compare whether model ordering is stable across metrics.

Use rank concordance/correlation as descriptive evidence.

Avoid a universal aggregate score unless a defensible weighting theory exists.

### 7.5 Counterfactual sensitivity

Estimate semantic label effect / flip rate with uncertainty.

Use matched-pair methods where appropriate.

### 7.6 Robustness

At minimum:

- parser sensitivity audit;
- missingness/execution-state sensitivity;
- retry/HTTP-state analysis;
- alternate reasonable estimator where prespecified;
- scenario-family leave-one-family-out sensitivity if sample size permits.

---

# K8 — Nature-readiness evidence package

## Goal

End the 72-hour expansion with a decision-quality package, not automatically a manuscript.

Create:

- `docs/kairokrisis/KAIROKRISIS_V2_METHOD.md`
- `docs/kairokrisis/KAIROKRISIS_V2_RESULTS.md`
- `docs/kairokrisis/KAIROKRISIS_V2_LIMITATIONS.md`
- `docs/kairokrisis/KAIROKRISIS_NMI_READINESS.md`
- machine-readable claim registry
- prohibited-claims registry
- input/output hash manifests
- model execution manifest
- physical benchmark manifest
- counterfactual-pair manifest
- deterministic analysis scripts
- figures/tables source data
- reproducibility instructions
- release-candidate dataset/code package

Do not write “Nature-ready” merely because the pipeline runs.

---

# 6. Three-day priority order

## Day 1 — Scientific design and physical expansion

Highest priority:

1. K0 branch cleanup and name audit;
2. K1 preregistration;
3. scenario grammar expansion;
4. physical benchmark generation;
5. deterministic validation;
6. freeze physical snapshot;
7. model availability metadata probe only after physical freeze.

Do not spend Day 1 generating thousands of model calls before the experiment is frozen.

## Day 2 — Model execution

1. freeze model/interface panel;
2. execute the core factorial or frozen sampling design;
3. preserve failures;
4. complete counterfactual semantic subset;
5. validate parser/output accounting continuously;
6. do not inspect headline hypothesis results until the planned execution/termination gate is met.

## Day 3 — Analysis, falsification, and release preparation

1. execute preregistered analysis;
2. test H1–H5;
3. perform negative controls;
4. run robustness checks;
5. reproduce all outputs from clean inputs;
6. prepare release candidate;
7. perform Nature-readiness audit;
8. stop rather than force a positive story.

---

# 7. Nature Machine Intelligence go/no-go gate

At the end of v2, classify the project.

## `NMI_GO`

Use only if the new work supports a broad and robust finding such as:

- evaluation layers substantially diverge across multiple models and scenario families;
- structured-output interventions improve formatting but show materially different effects on physical outcomes;
- model comparisons are demonstrably metric-dependent;
- counterfactual semantic sensitivity is reproducible and separable from generic prompt instability;
- conclusions survive major robustness checks;
- benchmark/data/code are reproducible and release-ready.

A strong paper should have a reason to change how researchers evaluate safety-critical AI, not just report driving percentages.

## `NMI_BORDERLINE`

Use if:

- effects exist but are model-specific;
- sample/scene diversity remains limited;
- representation ablation is incomplete;
- counterfactual results are unstable;
- robustness is weak.

In this case consider a strong specialist/HCI journal rather than stretching claims.

## `NMI_NO_GO`

Use if:

- the expanded experiment merely reproduces pilot averages;
- no general cross-layer phenomenon emerges;
- results depend on one model or one scenario family;
- design changes after seeing outcomes are required to tell the story;
- evidence cannot support a broad conclusion.

A no-go is a valid scientific outcome.

Do not alter the experiment after the fact merely to reach the target venue.

---

# 8. Manuscript architecture if NMI_GO

Current NMI Article guidance (verify again at submission):

- main text: up to ~3,500 words excluding abstract, Methods, references and figure legends;
- abstract: up to 150 words;
- up to 6 display items;
- structure:
  - Introduction without heading;
  - Results;
  - Discussion;
  - Methods;
- guideline of up to ~50 references;
- supplementary information allowed.

The main text should tell one broad story.

Possible display-item architecture:

1. **Fig. 1 — KAIROKRISIS framework and layer separation**
2. **Fig. 2 — Expanded scenario/model/interface experimental design**
3. **Fig. 3 — Interface reliability versus downstream physical safety**
4. **Fig. 4 — Cross-layer/model ordering divergence**
5. **Fig. 5 — Counterfactual semantic sensitivity and negative controls**
6. **Table/Fig. 6 — Robustness, estimability, and evidence boundaries**

Do not spend time making journal-perfect figures before the scientific go/no-go decision.

---

# 9. Open-science readiness

A Nature-facing benchmark should be prepared for public reuse.

Before submission, prepare:

- frozen version tag;
- permanent release archive candidate;
- dataset card;
- model/provider provenance;
- exact prompts;
- scenario-generation code;
- simulator version/environment;
- analysis scripts;
- source data for each figure;
- machine-readable tables;
- license audit;
- secrets audit;
- reproducibility environment;
- README reproducing the headline results.

A recent NMI safety benchmark, LabSafety Bench, publicly released its dataset, evaluation code, and an archived version of its code. KAIROKRISIS should aim for a comparably inspectable research object where licensing permits.

Do not publish secrets, credentials, or provider-restricted raw material.

---

# 10. Legal evidence policy

The law layer must remain scientifically honest.

The current Phase 5 pilot does **not** provide resolved jurisdiction-specific action legality.

Therefore:

- do not compute legal-compliance percentages;
- do not rank jurisdictions;
- do not label an action legal/illegal from simulator outcomes;
- do not treat map/road compliance as law;
- do not use an LLM as the legal gold-label source.

If qualified legal review becomes available later, it may be added as a separate versioned research layer.

KAIROKRISIS v2 does **not** require completion of the 25-jurisdiction legal corpus to test the primary decision-layer divergence hypothesis.

---

# 11. Human-factors and governance interpretation

The study can discuss implications for:

- human oversight;
- automation reliance;
- interface design;
- auditability;
- institutional deployment;
- governance.

But unless a human-participant study is added, do not claim measured:

- trust;
- reliance;
- cognitive load;
- usability;
- perception;
- acceptance.

These remain theoretical/design implications supported by literature, not measured outcomes.

---

# 12. Repository cleanup policy

The new Nature-facing branch should contain what is necessary to:

- reproduce the pilot;
- reproduce KAIROKRISIS v2;
- inspect the new evidence;
- prepare a public research release.

Obsolete manuscript-production artifacts from the earlier IJHCI drafting branch do not need to be carried into the new branch.

### Safe approach

Prefer creating `kairokrisis-v2` from the clean frozen scientific lineage rather than deleting files destructively from a manuscript branch.

If cleanup is required:

- compare against `phase9-final-synthesis-v1`;
- remove only manuscript/export/render artifacts added after the scientific freeze and unrelated to KAIROKRISIS;
- keep scientific validation reports;
- keep frozen research data;
- keep provenance;
- keep scripts;
- keep tests;
- keep hashes;
- keep all old branches and tags.

Never use force-push or history rewriting as cleanup.

---

# 13. Non-negotiable integrity rules

1. No paid provider use without explicit authorization.
2. No secret printing or committing.
3. No frozen-pilot mutation.
4. No post-hoc hypothesis relabeling.
5. No parser-invented actions.
6. No demographic utility scores.
7. No legal inference from simulation.
8. No silent model/provider substitutions.
9. No silent exclusion of provider failures.
10. No claim stronger than the registered evidence.
11. No “Nature-ready” declaration based only on scale.
12. Preserve negative and null results.

---

# 14. End-of-run report

At the end of the 72-hour programme, report:

1. current branch and commits;
2. naming audit result;
3. frozen v2 preregistration commit;
4. scenario-family count;
5. unique base-scene count;
6. canonical physical-outcome count;
7. models/providers actually executed;
8. interface/representation conditions;
9. planned and completed model-call counts;
10. provider error/missingness counts;
11. H1–H5 results with effect sizes and uncertainty;
12. counterfactual flip rates and negative controls;
13. cross-layer concordance/divergence results;
14. robustness checks;
15. release-package status;
16. full validator/test results;
17. frozen hashes/tags;
18. scientific limitations;
19. `NMI_GO`, `NMI_BORDERLINE`, or `NMI_NO_GO`;
20. the single strongest evidence-supported scientific conclusion.

Do not begin manuscript drafting automatically.

First determine whether the expanded evidence genuinely supports a Nature Machine Intelligence-level story.

---

# 15. External references used to define the target

Accessed 2026-10-02.

- Nature Machine Intelligence, Aims & Scope  
  https://www.nature.com/natmachintell/aims

- Nature Machine Intelligence, Content Types  
  https://www.nature.com/natmachintell/content

- Nature Machine Intelligence, Submission Guidelines  
  https://www.nature.com/natmachintell/submission-guidelines

- Nature Machine Intelligence, Formatting initial submission  
  https://www.nature.com/natmachintell/submission-guidelines/initial-formatting

- Nature Machine Intelligence, Writing and language  
  https://www.nature.com/natmachintell/submission-guidelines/writing-and-language

- Nature Portfolio peer-review criteria  
  https://www.nature.com/natmachintell/editorial-policies/peer-review

- Zhou et al., “Benchmarking large language models on safety risks in scientific laboratories,” Nature Machine Intelligence (2026)  
  https://www.nature.com/articles/s42256-025-01152-1

- Bode & Chandler, “Re-thinking human–machine interaction and the governance of AI in the military domain,” Nature Machine Intelligence (2026)  
  https://www.nature.com/articles/s42256-026-01231-x

---

## Final principle

**Do not optimize for Nature. Optimize for a result that would deserve Nature-level visibility if it survives the experiment.**

KAIROKRISIS succeeds scientifically if it produces a reproducible answer to a broad question about critical AI decision evaluation, including the possibility that the answer is null, conditional, or less dramatic than expected.
