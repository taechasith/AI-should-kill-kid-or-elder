"""Render Phase 8A documentation from machine-readable results only."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/analysis/phase8a"

def main() -> None:
    data = json.loads((OUT / "phase8a_results.json").read_text(encoding="utf-8"))
    accounting = data["accounting"]
    rows = {row["result_id"]: row for row in data["results"]}
    validity = rows["P8A-INTERFACE-003"]
    strict = rows["P8A-INTERFACE-004"]
    action_rows = [rows[f"P8A-ACTION-{x}"] for x in ("A0", "A1", "A2", "A3", "A4", "A6")]
    physical_rows = [rows[x] for x in ("P8A-PHYSICAL-COLLISION", "P8A-PHYSICAL-FEASIBLE", "P8A-PHYSICAL-ROAD_COMPLIANT", "P8A-PHYSICAL-MIN-DISTANCE")]
    def pct(value): return "—" if value is None else f"{100 * value:.2f}%"
    result_md = f"""# Phase 8A Frozen Confirmatory Results

Generated only by `python scripts/run_phase8a_analysis.py` followed by `python scripts/generate_phase8a_docs.py`. All estimates are from frozen Phase 4–7 artifacts; no network, provider, or simulator operation is used.

## Accounting

| Quantity | Count |
| --- | ---: |
| Design-accounted Phase 7 rows | {accounting['design_accounted']} |
| Not applicable (C3) | {accounting['not_applicable']} |
| Provider-execution population | {accounting['provider_execution_population']} |
| Certainty observations | {accounting['certainty_observations']} |
| Probability-sample observations | {accounting['probability_sample_observations']} |
| Terminal analysis observations | {accounting['analysis_observations']} |
| Explicit actions | {accounting['explicit_actions']} |
| Valid allowlisted actions | {accounting['valid_allowlisted_actions']} |
| Phase 4-linked valid actions | {accounting['physical_outcome_linked_actions']} |

## Interface reliability

The primary valid-action estimate is {pct(validity['weighted_estimate'])} (approximate 95% CI {pct(validity['approximate_95_ci'][0])}–{pct(validity['approximate_95_ci'][1])}); it is a Horvitz–Thompson finite-population estimate with stratified SRSWOR variance and finite-population correction. Strict JSON is separately {pct(strict['weighted_estimate'])}. A valid explicit action is not treated as synonymous with strict JSON.

## Weighted selected-action joint rates

| Action | Weighted rate | Approximate 95% CI | Raw selected observations |
| --- | ---: | ---: | ---: |
""" + "\n".join(f"| {row['dimensions']['action_id']} | {pct(row['weighted_estimate'])} | {pct(row['approximate_95_ci'][0])}–{pct(row['approximate_95_ci'][1])} | {row['raw_numerator']} |" for row in action_rows) + """

Each action rate is joint with a valid allowlisted action and therefore preserves invalid/no-action observations rather than silently reassigning them.

## Physical linkage

Physical result identifiers `P8A-PHYSICAL-*` link a valid selected action to the existing Phase 4 scenario/speed/action cell and calculate an arithmetic mean across its five frozen seeds. `road_compliant` remains a Phase 4 map/road-boundary metric, not a jurisdictional legal conclusion. Conditional clearance is descriptive because no ratio-variance estimator was frozen.

| Metric | Estimate | Status |
| --- | ---: | --- |
""" + "\n".join(f"| {row['metric_name']} | {row['weighted_estimate']:.6f} | {row['estimability']} |" for row in physical_rows) + """

The domain-level action rows in `phase8a_results.json` cover the pre-specified model, scenario, speed, and condition dimensions. Their point estimates are design-weighted; intervals are intentionally omitted where a domain variance estimator was not pre-specified.

## Legal outcome status

All jurisdictional legal-compliance, legality-ranking, and legal-versus-safety metrics are **NOT_ESTIMABLE**. Frozen Phase 5 v1 does not provide action-level determinations; no inference or imputation was performed.
"""
    limitations = """# Phase 8A Limitations

- This is a design-weighted analysis of 279 certainty observations plus 60 stratified probability-sample observations, not a census and not a simple random sample.
- The exact Phase 7 aggregate valid-action result and its approximate interval were known before Phase 8A. This analysis is confirmatory relative to the pre-result Phase 8A specification, but is not strictly outcome-blind preregistration.
- The Phase 4 physical join has five deterministic seed records per scenario/speed/action cell; Phase 8A reports their arithmetic mean and does not create a new simulation.
- Phase 5 v1 lacks action-level legal determinations. Legal compliance is blocked rather than estimated.
- The historical Qwen route is Groq `qwen/qwen3.8-27b`; it is retained with its existing free-plan attestation limitation. It is not represented as OpenRouter.
- No model can be ranked as best, safest, most ethical, or most lawful from this snapshot.
"""
    reproducibility = """# Phase 8A Reproducibility

Run offline from the repository root:

```text
python scripts/build_phase8a_input_manifest.py
python scripts/run_phase8a_analysis.py
python scripts/generate_phase8a_docs.py
python scripts/validate_phase8a_analysis.py
```

These commands do not read environment secrets or make provider/network calls. The input builder fails closed when a frozen hash or selected raw-response reference disagrees with its provenance. The validator checks recovered Phase 7 accounting, duplicate IDs, the historical valid-action estimate, physical join cardinality, legal blocking, and output determinism.
"""
    (ROOT / "docs/PHASE8A_RESULTS.md").write_text(result_md, encoding="utf-8", newline="\n")
    (ROOT / "docs/PHASE8A_LIMITATIONS.md").write_text(limitations, encoding="utf-8", newline="\n")
    (ROOT / "docs/PHASE8A_REPRODUCIBILITY.md").write_text(reproducibility, encoding="utf-8", newline="\n")
    figures = OUT / "figures"; figures.mkdir(exist_ok=True)
    width, height = 720, 300
    bars = []
    for index, row in enumerate(action_rows):
        x = 55 + index * 105; bar = round(190 * row["weighted_estimate"], 2)
        bars.append(f'<rect x="{x}" y="{240-bar}" width="64" height="{bar}" fill="#2f6f9f"/><text x="{x}" y="264" font-size="13">{row["dimensions"]["action_id"]}</text><text x="{x}" y="{232-bar}" font-size="11">{100*row["weighted_estimate"]:.1f}%</text>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" role="img" aria-label="Phase 8A weighted selected action joint rates"><rect width="100%" height="100%" fill="white"/><text x="25" y="28" font-size="17">Phase 8A weighted selected-action joint rates</text><text x="25" y="48" font-size="11">Source: P8A-ACTION-A0 through P8A-ACTION-A6; denominator = 4,104 provider rows</text><line x1="45" y1="240" x2="690" y2="240" stroke="black"/>{"".join(bars)}</svg>'
    (figures / "phase8a_overall_action_distribution.svg").write_text(svg, encoding="utf-8", newline="\n")
    print("Phase 8A documentation rendered from phase8a_results.json")

if __name__ == "__main__": main()
