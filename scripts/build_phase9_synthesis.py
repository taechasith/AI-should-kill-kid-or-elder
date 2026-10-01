"""Generate Phase 9 evidence, tables, figures, and paper-ready Markdown offline."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/analysis/phase9"
TABLES, FIGURES = OUT / "tables", OUT / "figures"

def load(path): return json.loads(path.read_text(encoding="utf-8"))
def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
def csv_write(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
def pct(value): return "NOT_ESTIMABLE" if value is None else f"{100*value:.2f}%"

def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    inputs = load(OUT / "phase9_input_manifest.json")
    expected = "f02bd010286d6b3c965081b878419ccfde26e6106fc92709f983d7afcc7242a8"
    if inputs["phase8a"]["hash_manifest_sha256"] != expected: raise SystemExit("Phase 9 input manifest does not bind expected Phase 8A hash")
    results = load(ROOT / inputs["phase8a"]["results"]); rows = results["results"]; by_id = {row["result_id"]: row for row in rows}
    claims = load(OUT / "phase9_claim_registry.json")["claims"]
    unknown = [claim["claim_id"] for claim in claims if claim["source_result_id"] not in by_id]
    if unknown: raise SystemExit("claims lack source result IDs: " + ", ".join(unknown))
    accounting = results["accounting"]
    write(OUT / "phase9_final_results.json", {"schema_version":"phase9-final-results-v1","source_phase8a_results":inputs["phase8a"]["results"],"source_phase8a_results_sha256":inputs["phase8a"]["results_sha256"],"accounting":accounting,"claims":claims,"phase8a_results":rows})
    csv_write(OUT / "phase9_final_results.csv", [{"result_id":r["result_id"],"metric_name":r.get("metric_name",r.get("dimensions",{}).get("metric_name")),"estimate":r.get("weighted_estimate"),"interval":json.dumps(r.get("approximate_95_ci")),"estimability":r["estimability"],"estimator":r.get("estimator")} for r in rows], ["result_id","metric_name","estimate","interval","estimability","estimator"])
    table1 = [{"component":"Physical benchmark","frozen_artifact":"commonroad-pilot-v1","role":"deterministic KS/CommonRoad physical outcomes"},{"component":"Legal snapshot","frozen_artifact":"phase5-legal-snapshot-v1","role":"provenance and action-level NOT_DETERMINED boundary"},{"component":"Interface gate","frozen_artifact":"phase6-literature-v2-pilot-v1","role":"frozen decision-line interface"},{"component":"Provider sample","frozen_artifact":"phase7-psb-v1","role":"279 certainty plus 60 stratified SRSWOR units"},{"component":"Confirmatory analysis","frozen_artifact":"phase8a-confirmatory-analysis-v1","role":"design-weighted frozen evidence"}]
    table2 = [{"stage":"Design-accounted manifest","count":5454,"denominator":"design rows","status":"frozen"},{"stage":"Structurally not applicable C3","count":1350,"denominator":"design rows","status":"not applicable"},{"stage":"Provider-execution population","count":4104,"denominator":"design rows","status":"finite population"},{"stage":"Certainty observations","count":279,"denominator":"provider population","status":"pi=1"},{"stage":"Probability-sample observations","count":60,"denominator":"remaining stratum populations","status":"terminal"},{"stage":"Terminal analysis observations","count":339,"denominator":"selected units","status":"not a census"},{"stage":"Valid allowlisted actions / physical joins","count":323,"denominator":"terminal analysis observations","status":"no action inferred"}]
    rel = [by_id[x] for x in ("P8A-INTERFACE-001","P8A-INTERFACE-002","P8A-INTERFACE-003","P8A-INTERFACE-004","P8A-INTERFACE-005")]
    table3 = [{"result_id":r["result_id"],"metric":r["dimensions"]["metric_name"],"raw_numerator":r["raw_numerator"],"raw_denominator":r["raw_denominator"],"weighted_estimate":r["weighted_estimate"],"approximate_95_ci":json.dumps(r["approximate_95_ci"]),"source":"phase8a_results.json"} for r in rel]
    table4 = [{"result_id":r["result_id"],"action":r["dimensions"]["action_id"],"raw_selected":r["raw_numerator"],"selected_units":r["raw_denominator"],"weighted_joint_rate":r["weighted_estimate"],"approximate_95_ci":json.dumps(r["approximate_95_ci"])} for r in rows if r["result_id"].startswith("P8A-ACTION-")]
    table5 = [{"result_id":r["result_id"],"metric":r["metric_name"],"estimate":r["weighted_estimate"],"status":r["estimability"],"uncertainty":json.dumps(r["approximate_95_ci"]),"interpretation":"physical/map metric, not jurisdictional legality"} for r in rows if r["result_id"].startswith("P8A-PHYSICAL-")]
    table6 = [{"result_id":r["result_id"],"dimension":next(k for k in r["dimensions"] if k not in ("action_id","population_domain_size")),"group":next(v for k,v in r["dimensions"].items() if k not in ("action_id","population_domain_size")),"action":r["dimensions"]["action_id"],"population_domain_size":r["dimensions"]["population_domain_size"],"weighted_point_estimate":r["weighted_estimate"],"uncertainty_status":r["estimability"]} for r in rows if r["result_id"].startswith("P8A-DOMAIN-")]
    table7 = [{"dimension":"Physical collision","status":"ESTIMABLE"},{"dimension":"Physical feasibility","status":"ESTIMABLE"},{"dimension":"Map/road constraint compliance","status":"ESTIMABLE"},{"dimension":"Action behavior","status":"ESTIMABLE"},{"dimension":"Formatting reliability","status":"ESTIMABLE"},{"dimension":"Jurisdictional legal compliance","status":"NOT_ESTIMABLE"}]
    for index, table in enumerate((table1,table2,table3,table4,table5,table6,table7), 1): csv_write(TABLES / f"table{index}.csv", table, list(table[0]))
    # SVG figures use exact frozen values and include source/denominator in the rendered text.
    actions = table4; bars = "".join(f'<rect x="{50+i*105}" y="{250-180*r["weighted_joint_rate"]}" width="62" height="{180*r["weighted_joint_rate"]}" fill="#2f6f9f"/><text x="{50+i*105}" y="270">{r["action"]}</text><text x="{50+i*105}" y="{242-180*r["weighted_joint_rate"]}">{100*r["weighted_joint_rate"]:.1f}%</text>' for i,r in enumerate(actions))
    flow = "".join(f'<rect x="{30+i*105}" y="100" width="95" height="70" fill="#e7f0f6" stroke="#2f6f9f"/><text x="{35+i*105}" y="125" font-size="12">{r["stage"][:14]}</text><text x="{35+i*105}" y="150" font-size="18">{r["count"]}</text>' for i,r in enumerate(table2))
    figs = {"figure1_population_flow.svg":f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="230"><text x="20" y="28" font-size="18">Phase 9 study population flow</text><text x="20" y="50" font-size="11">Source: Phase 8A accounting; 339 observations are not a census.</text>{flow}</svg>', "figure2_interface_reliability.svg":f'<svg xmlns="http://www.w3.org/2000/svg" width="500" height="250"><text x="20" y="28" font-size="18">Interface reliability</text><text x="20" y="50" font-size="11">P8A-INTERFACE-003 and P8A-INTERFACE-004; weighted provider population n=4,104.</text><rect x="80" y="{220-160*by_id["P8A-INTERFACE-003"]["weighted_estimate"]}" width="90" height="{160*by_id["P8A-INTERFACE-003"]["weighted_estimate"]}" fill="#2f6f9f"/><text x="80" y="235" font-size="11">valid action</text><rect x="260" y="{220-160*by_id["P8A-INTERFACE-004"]["weighted_estimate"]}" width="90" height="{160*by_id["P8A-INTERFACE-004"]["weighted_estimate"]}" fill="#88b04b"/><text x="260" y="235" font-size="11">strict JSON</text></svg>', "figure3_action_distribution.svg":f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="300"><text x="20" y="28" font-size="18">Weighted selected-action joint rates</text><text x="20" y="50" font-size="11">Source: P8A-ACTION-A0 through P8A-ACTION-A6; denominator=4,104; valid action joint rates.</text>{bars}</svg>', "figure4_estimability.svg":'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="220"><text x="20" y="28" font-size="18">Evidence estimability boundary</text><text x="25" y="70" font-size="16" fill="#2f6f9f">ESTIMABLE: physical collision, feasibility, map/road constraints, actions, formatting</text><text x="25" y="120" font-size="16" fill="#a94442">NOT ESTIMABLE: jurisdictional legal compliance</text><text x="25" y="155" font-size="12">Source: P8A-LEGAL-001. Physical/map metrics are not legal determinations.</text></svg>'}
    for name, content in figs.items(): (FIGURES / name).write_text(content, encoding="utf-8", newline="\n")
    synthesis = f"""# Phase 9 Final Scientific Synthesis

This evidence package integrates frozen Phase 4–8A artifacts only. The sampled design accounted for 5,454 rows, of which 1,350 were structurally not applicable and 4,104 formed the provider-execution population. The analysis used 279 certainty observations plus 60 probability-sampled terminal observations; the 339 terminal observations are not a census. [C-P9-001]

The estimated valid allowlisted-action rate was 82.38% (approximate 95% CI 73.40%–91.36%). Strict JSON was separately estimated at 62.37%; formatting failure is not treated as absence of an explicit decision. [C-P9-001; C-P9-002]

Valid-action-linked physical metrics were a collision mean of 25.41%, feasibility mean of 81.87%, map/road-compliance mean of 82.07%, and descriptive conditional minimum distance of 3.106 m. These are frozen modeled physical/map outcomes and are not legal findings. [C-P9-003; C-P9-004; C-P9-005; C-P9-006]

Jurisdictional legal compliance remains **NOT_ESTIMABLE** because Phase 5 v1 contains no action-level determinations sufficient to estimate it. No breakthrough claim is warranted from the current evidence. [C-P9-007]
"""
    paper_results = """# Paper-ready Results Evidence

The frozen study design contained 5,454 rows; 1,350 C3 rows were structurally not applicable, leaving a finite provider-execution population of 4,104. The final analysis comprised 279 certainty observations and 60 stratified probability-sampled terminal observations (339 total), rather than a census. [C-P9-001]

Using the prespecified Horvitz–Thompson estimator with stratified SRSWOR variance and finite-population correction, the estimated valid allowlisted-action rate was 82.38% (approximate 95% CI 73.40%–91.36%). Strict JSON validity, measured separately as formatting reliability, was 62.37%. A model response could provide a valid explicit action without strict JSON; no unstated action was inferred. [C-P9-001; C-P9-002]

For valid selected actions, linked Phase 4 physical summaries yielded a collision mean of 25.41%, a physical-feasibility mean of 81.87%, and a map/road-compliance mean of 82.07%. The base-weighted conditional mean minimum distance was 3.106 m. These values describe the frozen modeled scenarios and map constraints, not jurisdiction-specific legal compliance. [C-P9-003; C-P9-004; C-P9-005; C-P9-006]

Jurisdictional legal-compliance rates were not estimable because frozen Phase 5 v1 lacks action-level legal determinations. [C-P9-007]
"""
    methods = """# Paper-ready Methods Evidence

Phase 4 fixed a deterministic Kinematic Single-Track/CommonRoad physical benchmark with three scenario families, two initial speeds, six candidate actions, and five seeds per scenario-speed-action cell. Its machine-readable outcomes were frozen before model benchmarking. Phase 5 froze legal provenance while retaining action-level determinations as NOT_DETERMINED; it therefore bounds, rather than supplies, legal-compliance estimation.

Phase 6 established a frozen multimodal decision-line interface. Phase 7 defined a finite provider-execution population of 4,104 rows within a 5,454-row manifest; 1,350 C3 rows were structurally not applicable. Pre-amendment terminal responses were retained as 279 certainty units. Sixty additional units were selected through stratified simple random sampling without replacement across model-by-condition strata, using recorded inclusion probabilities and base weights.

Phase 8A used the finite-population Horvitz–Thompson estimator with the frozen certainty contributions and sampled-unit inverse-probability weights. For binary rates, uncertainty used the frozen stratified SRSWOR finite-population-corrected variance estimator. Strict JSON formatting and explicit allowlisted action extraction were distinct metrics; the parser did not infer missing actions. A valid selected action joined to the existing Phase 4 scenario/speed/action cell, whose scalar physical value was the arithmetic mean over five frozen seeds. Map/road compliance was retained as a physical benchmark metric and was not reinterpreted as law.
"""
    limitations = """# Phase 9 Limitations

- Only 60 probability-sampled observations supplement 279 certainty observations; the 339 analysis units are not a provider-population census.
- Phase 7 encountered HTTP 429 and HTTP 503 attempts before all 60 sampled terminal observations were obtained; these operational outcomes are not model-intelligence measures.
- Historical Qwen execution used Groq `qwen/qwen3.8-27b`. Free-plan eligibility is supported by plan documentation and account attestation, while transaction-level billing evidence was not preserved.
- No validated jurisdiction-specific legal-compliance rate can be estimated from Phase 5 v1.
- CommonRoad results describe the frozen modeled scenarios and assumptions, not unrestricted real-world driving.
- Hosted models and provider endpoints are time-dependent.
- The broad local Windows suite remains environment-limited by missing `shapely` and `vehiclemodels` plus unrelated global package conflicts.
"""
    reproducibility = """# Phase 9 Reproducibility

Phase 9 requires no network, provider, API, simulation, or random sampling operation. From the repository root:

```text
python scripts/build_phase9_scaffold.py
python scripts/build_phase9_synthesis.py
python scripts/freeze_phase9_hashes.py
python scripts/validate_phase9_synthesis.py
```

Inputs are the frozen Phase 8A results and hash manifest, with the required Phase 8A hash-manifest digest recorded in `phase9_input_manifest.json`. The scripts use Python standard-library modules only. The Phase 7 sampling RNG seed remains a frozen input (`20260930`); Phase 9 does not resample.
"""
    for path, content in ((ROOT/"docs/PHASE9_SYNTHESIS.md",synthesis),(ROOT/"docs/PHASE9_PAPER_RESULTS.md",paper_results),(ROOT/"docs/PHASE9_PAPER_METHODS.md",methods),(ROOT/"docs/PHASE9_LIMITATIONS.md",limitations),(ROOT/"docs/PHASE9_REPRODUCIBILITY.md",reproducibility)): path.write_text(content,encoding="utf-8",newline="\n")
    integrity = {"schema_version":"phase9-integrity-report-v1","status":"READY_FOR_FINAL_HASH_VALIDATION","claim_count":len(claims),"claims_with_valid_phase8a_source":len(claims)-len(unknown),"frozen_phase8a_results_sha256":inputs["phase8a"]["results_sha256"],"legal_metrics":"NOT_ESTIMABLE","provider_or_network_calls":"not performed","simulation_execution":"not performed","sampling_execution":"not performed","frozen_artifact_mutations":"not performed"}
    write(OUT / "phase9_integrity_report.json", integrity)
    print(f"Phase 9 synthesis generated: {len(rows)} frozen result rows, {len(table6)} domain rows, {len(figs)} figures")

if __name__ == "__main__": main()
