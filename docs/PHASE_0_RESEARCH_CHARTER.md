# Phase 0 - GeoSAVE Research Charter and Baseline

**Status:** passed locally on 2026-09-27  
**Repository commit baseline:** `7ff34e587405b67f17ed99ef36da73c4aeb44bf0` (`Initial commit`)  
**Operating methodology:** `AGENT_RESEARCH_METHODOLOGY.md`  
**Source methodology:** `IEEE_IV_2027_GeoSAVE_RESEARCH_METHODOLOGY.md`

## Research question and scope

GeoSAVE asks whether an autonomous-driving AI should change its selected action
when the physical safety-critical scene is held constant but the applicable
traffic-law context changes, and whether the resulting behavior can be made
explicit, measurable, physically safer, legally grounded, and reproducible.

This is a fully digital research program using public/legal data, simulation,
multimodal model evaluation, and statistical analysis. It includes no human
participant data collection and no physical vehicle testing.

The target research contribution is an intelligent-vehicle benchmark and
constrained decision-evaluation framework; it is not a trolley-problem,
human-psychology, legal-advice, or real-world vehicle-certification project.

## Frozen Phase 0 research questions and hypotheses

| Identifier | Bounded question or testable prediction |
|---|---|
| RQ1 / H5 | Measure action changes when relevant jurisdictional context changes while physics remains fixed. |
| RQ2 | Measure physical, legal, and contextual predictors of selected actions. |
| RQ3 | Characterize behavior when lower physical risk and literal legal compliance conflict. |
| RQ4 / H1 / H3 | Test whether structured law and GeoSAVE improve verified compliance without increasing physical risk. |
| RQ5 | Measure association, not causation, between broad country-law features and model behavior. |
| RQ6 / H4 | Compare model-family action distributions under identical evidence. |
| RQ7 / H7 | Test explanation-behavior consistency through controlled perturbations; this is a faithfulness proxy only. |
| H2 / H6 | Compare country-name effects with explicit-law effects and quantify residual jurisdiction differences. |

These are project hypotheses, not established results. Formal experiment
configuration, primary outcomes, exclusions, model set, and statistical methods
remain unfrozen until Phase 7.

## Unit of analysis and non-negotiable separation

| Unit | Identity | Purpose |
|---|---|---|
| Simulation unit | `scenario x variant x action x seed` | A jurisdiction-independent physical outcome. |
| Legal evaluation unit | `jurisdiction x scenario x action x law_snapshot` | Explicit legal status: legal, illegal, conditionally legal, not applicable, or unknown. |
| Model-decision unit | `scenario x jurisdiction x model x condition x repetition` | Selected candidate action and structured output. |
| Country unit | `jurisdiction` | Broad Global Law Map correlation/visualization unit. |

Physical simulation is generated once per simulation unit and joined to legal
and model-decision units. A jurisdiction label change alone must never cause a
physics rerun. Legal status and physical-risk outcomes remain separate fields;
the framework must preserve safe-illegal and unsafe-lawful cases.

## Required deliverable register

| Phase | Deliverable | Minimum evidence |
|---|---|---|
| 1 | Versioned schemas, validators, reproducibility contracts | Validation tests reject invalid/unknown-law misuse and reproduce configuration. |
| 2 | Global Law Map pilot and auditable Deep-Law pilot | Provenance, effective/retrieval dates, rule status, and frozen snapshot versioning. |
| 3 | Controlled scenario/action pilot | Validation, split membership, measurable metrics, and no prompt leakage. |
| 4 | Physical outcome-matrix pilot | Reproducible simulator configuration, metrics, failure logging, keyed joins. |
| 5 | Deterministic GeoSAVE and non-model baselines | Tested staged gates and separate safety-law conflict labels. |
| 6 | Strict model-interface pilot | Versioned prompts/registry, raw+parsed logs, parser failure/repair evidence. |
| 7 | Preregistered main benchmark | Frozen configuration, manifest, hashes, recorded exclusions and failures. |
| 8 | Counterfactual/statistical analysis | Paired/nested analysis, effect sizes/CIs, FDR where applicable, bounded claims. |
| 9 | Reproducible release package | Clean regeneration, figures/tables, disclaimer/license/secret/anonymity review. |

## Required public-facing boundaries

The repository and later release material must include these statements:

> The GeoSAVE legal dataset is a research representation of selected road-traffic
> rules and is not legal advice. Laws change and may contain jurisdiction-specific
> exceptions not represented in the benchmark. Verify current primary sources
> before use outside research.

> GeoSAVE is a research framework for simulation and analysis. It is not
> production autonomous-driving software and must not control a real vehicle
> without independent engineering verification, safety assurance, and regulatory
> review.

The harm objective must not vary with protected characteristics, nationality,
behavior, or legally relevant fault. A road-user's behavior may affect expected
motion, right-of-way, or legal status, but never intrinsic worth.

## Repository baseline

The Phase 0 inventory found only these repository artifacts:

| Path | Role |
|---|---|
| `README.md` | One-line project placeholder. |
| `IEEE_IV_2027_GeoSAVE_RESEARCH_METHODOLOGY.md` | Source research plan and target specification. |
| `AGENT_RULES(3).md` | Repository operating/research-integrity contract. |
| `AGENT_RESEARCH_METHODOLOGY.md` | Single-researcher phase methodology. |

At this baseline, the repository has no source-data directories, law records,
schemas, code package, configurations, simulator adapter, model registry,
prompts, test suite, experiment logs, results, figures, environment definition,
or CI configuration. No simulation, web data collection, model inference, or
statistical analysis has been run.

## Known external gates

- Current IEEE IV 2027 author, anonymity, deadline, and AI-use rules require
  official verification before any submission-facing work.
- Large CARLA, cloud, or paid API/model runs require explicit user approval
  after a pilot and a cost/scale estimate.
- Deep-Law records require current primary-source validation. This project has
  not yet collected such records.
- Human-authored manuscript and submission decisions remain outside agent
  authority unless the user explicitly authorizes a permitted action.

## Phase 0 acceptance evidence

- Scope, RQ1-RQ7, H1-H7, digital-only boundary, unit definitions, required
  disclaimers, deliverable register, and no-go criteria are recorded here.
- Repository inventory and Git baseline were inspected locally.
- No external, paid, destructive, or experimental action occurred.

## Next permitted phase

**Phase 1 - Schemas, provenance, and reproducibility foundation.** It may start
with a minimal directory and schema plan. It must not collect laws, run CARLA,
call models, or claim empirical results.
