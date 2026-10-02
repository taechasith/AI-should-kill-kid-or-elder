# KA-IRO KRISIS v2: Flagship Nature Target Amendment

**Status:** Prospective amendment, recorded before new experimental data generation

**Date:** 2026-10-02

**Applies to:** the prospective KA-IRO KRISIS v2 programme only

## Purpose and history

The first version of the v2 guide targeted *Nature Machine Intelligence* (NMI). Before K0/K1 execution in the revised programme and before any new simulation, provider call, scenario outcome, or result-generating work, the research team prospectively changed the aspirational first-choice target to the flagship journal *Nature*.

This amendment does not represent the original guide as having specified *Nature*. The original NMI-targeted guide remains preserved in Git history. No new experimental data were inspected before this target amendment.

## Scientific threshold

The prospective flagship question is:

> Does this research reveal a general phenomenon about machine decision-making or AI evaluation that is important beyond autonomous driving, multimodal AI, or HCI specialists?

A larger driving benchmark alone is not a Nature-level contribution. The experiment must be capable of falsifying the candidate proposition that interface compliance, semantic decision validity, downstream physical/task safety, representation stability, and semantic-counterfactual stability can systematically diverge.

All existing prospective hypotheses, exclusions, sampling rules, statistical methods, multiplicity policy, and stopping rules remain governed by the preregistration. Changing the publication target must not change results, exclusions, or analysis choices after outcomes are observed.

## Target hierarchy and end gate

1. **Aspirational first-choice:** *Nature*.
2. **Fallback Nature Portfolio target:** *Nature Machine Intelligence* when the contribution is strong and reproducible but principally specialized to AI, robotics, HCI, or safety-critical systems.

The programme must classify its final evidence without stretching claims:

- `NATURE_GO`: broad, robust, reproducible cross-layer finding; multiple model and scenario families; meaningful negative controls and a causal/interventional contrast; and a prospectively specified secondary-domain generalization test that supports a scientific implication beyond driving.
- `NATURE_BORDERLINE`: broad and robust within expanded driving evidence, but cross-domain/generalization evidence is incomplete or weaker.
- `NATURE_NO_GO_NMI_GO`: a strong, novel, reproducible result whose primary significance remains specialist machine-intelligence research.
- `NMI_NO_GO`: unstable, narrow, post-hoc-dependent, or conceptually insufficient evidence.

The secondary-domain protocol must be frozen before its model calls. A failure to generalize is a reportable result, not a reason to revise the target narrative.

## Project name and identifiers

The displayed project name is **KA-IRO KRISIS**. It is a newly coined research name inspired by the classical Greek concepts of *kairos*, the decisive moment for action, and *krisis*, judgment or decision at a turning point. It is not claimed to be an attested Ancient Greek term.

The normalized technical identifier is `ka-iro-krisis`; the v2 branch, documentation directory, data directory, and machine project ID use `ka-iro-krisis-v2` or the appropriate safe derivative. Historical `Kairokrisis` spelling remains visible only where needed to preserve historical records.

## Editorial reference

Accessed 2026-10-02. Nature's current official initial-submission guidance states that initial submission is format-flexible, titles should fit within 75 characters including spaces, and typical Article guidance is approximately 2,500 main-text words and four modest display items for six pages or approximately 4,300 words and five to six display items for eight pages; Methods are typically up to approximately 3,000 words. It requires appropriately documented LLM use, author contributions, competing-interests statements, data availability, and code availability where central custom code is used. These requirements will be reverified immediately before any submission.

- https://www.nature.com/nature/for-authors/
- https://www.nature.com/nature/for-authors/initial-submission
- https://www.nature.com/nature/for-referees/policies-and-processes

## Integrity boundary

This amendment does not alter frozen GeoSAVE Phase 4–9 artifacts or their tags. It authorizes only prospective preparation and does not authorize new model calls or physical simulation before an amended K1 preregistration, a repeated exact-name audit, and the remaining preparation gates are frozen.
