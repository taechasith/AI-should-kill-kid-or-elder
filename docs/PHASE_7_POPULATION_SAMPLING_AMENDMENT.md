# Phase 7 population-sampling amendment

Status: `FROZEN_FOR_DESIGN; EXECUTION_NOT_AUTHORIZED`

The original immutable Phase 7 manifest contains 5,454 rows: 4,104
provider-evaluable units and 1,350 protocol-defined C3 `not_applicable` rows.
The provider frame remains valid. Its exhaustive execution plan is superseded
for primary estimation because verified zero-cost provider quotas make a census
impractical. No original manifest, attempt, or raw response is modified.

`phase7-psb-v1` estimates rates over the finite provider population, not over
all real-world driving. Pre-amendment terminal HTTP-200 units are a certainty
component (`pi=1`); unresolved provider units are sampled with known
probabilities. The primary design is stratified simple random sampling without
replacement on `model_id × condition`. The default allocation is five remaining
units per nonempty stratum (60 new units across 12 strata); this is deliberately
disproportionate to guarantee domain coverage, and design weights correct it.

The sampling code reads only run IDs and terminal status from old attempts. It
does not read selected actions, legal correctness, physical consequences, or
other substantive outcomes. The frozen manifest records the RNG algorithm,
seed, stratum sizes, inclusion probabilities, base weights, certainty IDs, and
frame/selection hashes.

The primary estimator for a binary outcome is the finite-population
Horvitz--Thompson rate: exact certainty contribution plus sampled remaining
units weighted by `1/pi`, divided by 4,104. A stratified SRSWOR variance uses a
finite-population correction. A Hájek-style ratio estimate, calibration, and
model-assisted estimates are secondary only and may not replace the primary
design-based analysis.

No provider call, micro-batch, or sequential stopping is authorized by this
amendment. Micro-batching is disabled pending a separately frozen metadata-only
equivalence protocol; batch prompting changes model-visible context and can
produce cross-item interference. A small purposive contrast panel may be added
later, but it is excluded from population-rate estimation unless assigned valid
probability inclusion weights.

Methodological precedents: Horvitz and Thompson's unequal-probability
estimation; Deville and Tillé's balanced-sampling cube method; and NIST
covering-array methods motivate efficient, auditable designs. tinyBenchmarks
and adaptive LLM-evaluation work motivate efficiency but do not validate this
sample size for GeoSAVE. Small-sample LLM evaluation requires design-aware
uncertainty rather than a naive IID Wald interval. Batch Prompting and later
batch-interference research motivate the disabled-by-default batching rule.

Key references: Polo et al., *tinyBenchmarks* (ICML 2024),
https://arxiv.org/abs/2402.14992; Deville & Tillé, *Biometrika* 91(4), 2004,
doi:10.1093/biomet/91.4.893; Cheng, Kasai & Yu, *Batch Prompting* (EMNLP
Industry 2023); Yue & Yao, *Efficient but Vulnerable* (Findings ACL 2025);
Arviv et al., *Stop Guessing When to Stop Testing* (Findings ACL 2026); and
Bowyer, Aitchison & Ivanova, *Don't Use the CLT in LLM Evals With Fewer Than a
Few Hundred Datapoints* (ICML 2025).
