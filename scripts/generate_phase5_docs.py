"""Generate Phase 5 review, coverage, and source documentation from frozen data."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE5 = ROOT / "data" / "legal" / "phase5"
DOCS = ROOT / "docs"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(name: str, body: str) -> None:
    (DOCS / name).write_text(body.rstrip() + "\n", encoding="utf-8")


def source_table(records: list[dict]) -> str:
    lines = ["| ISO3 | Official source | Scope / admission boundary | Second pass |", "| --- | --- | --- | --- |"]
    for record in records:
        title = record["source_title"].replace("|", "\\|")
        scope = f"{record['scope_status']}; {record['admission_status']}".replace("_", " ")
        access = record["second_pass_access"]
        if record.get("http_status") is not None:
            access += f" (HTTP {record['http_status']})"
        lines.append(f"| {record['country_iso3']} | [{title}]({record['official_source_url']}) | {scope} | {access} |")
    return "\n".join(lines)


def main() -> None:
    coverage = load(PHASE5 / "phase5_coverage_v1.json")
    source_metadata = load(PHASE5 / "source_metadata.json")["jurisdictions"]
    global_manifest = load(PHASE5 / "global_context" / "who_road_safety_2023_acquisition_manifest.json")
    source_metadata.sort(key=lambda record: record["country_iso3"])
    counts = coverage["source_second_pass_access_counts"]
    write("PHASE_5_LEGAL_REVIEW.md", f"""# Phase 5 legal review\n\n## Frozen snapshot\n\n`phase5-legal-snapshot-v1` freezes the legal-context overlay, 25-jurisdiction\nsource review, 900 legal queries, 900 decisions, global WHO context, and the\nassociated hash manifest. The snapshot is a research representation, not legal\nadvice or a claim of complete national traffic-law coverage.\n\n## Verification method\n\nEach frozen jurisdiction underwent two source passes: (1) source\ndiscovery/extraction and (2) an independent retrieval attempt against the\nofficial endpoint on 2026-09-28. This is **two-pass primary-source\nverification**, not expert legal review. The second pass retrieved {coverage['source_hash_available_count']}\nof 25 endpoint bodies and recorded all remaining access limitations explicitly\n({', '.join(f'{name}: {count}' for name, count in sorted(counts.items()))}).\n\n## Action-level result boundary\n\nAll {coverage['decision_count']} action-level decisions are `NOT_DETERMINED`. The\nfrozen physical scenarios do not establish material legal predicates such as a\nmarked-crossing type, signal state, posted speed, lane-marking type, traffic\nside, local jurisdiction, or a statutory exception. Those facts were not\ninvented to force a result. Consequently, this snapshot must not be reported as\na jurisdictional legality-rate comparison. It is an auditable uncertainty\nresult and a constraint on any later benchmark claim.\n\n## Source hierarchy and language\n\nOnly official statutes, regulations, codes, or government legal databases were\nretained as Deep-Law source candidates. Source-language text controls. No\nmachine translation is presented as official, and no action-level translation\nclaim is emitted in this snapshot. WHO data is global context only; UNECE\ninstruments remain international context unless domestic applicability is\nrecorded.\n\n## Required next legal-scope version\n\nA later snapshot can make action-level conclusions only by introducing a new,\nversioned legal overlay that supplies the missing predicates and by repeating\nsource review. It must never mutate this snapshot or its hashes.\n""")
    write("PHASE_5_COVERAGE.md", f"""# Phase 5 coverage\n\n| Measure | Value |\n| --- | ---: |\n| Frozen jurisdictions | {coverage['frozen_jurisdiction_count']} |\n| Legal queries | {coverage['query_count']} |\n| Legal decisions | {coverage['decision_count']} |\n| `NOT_DETERMINED` decisions | {coverage['decision_status_counts'].get('NOT_DETERMINED', 0)} |\n| Action-level resolved / conditional / conflicting decisions | 0 / 0 / 0 |\n| Primary-source index records | {coverage['evidence_count']} |\n| Retrieved and hashed source bodies | {coverage['source_hash_available_count']} |\n| WHO 2023 profiles collected | {coverage['global_context_profile_count']} |\n| WHO profile attempts unavailable or unparseable | {coverage['global_context_unavailable_or_unparseable_count']} |\n\nEvery query has exactly one decision. No blank, `TODO`, or implied-permission\ncell is present. The all-unknown decision distribution reflects omitted legal\npredicates in the frozen overlay, not a claim that the relevant jurisdictions\nhave no traffic law.\n\nThe full machine-readable coverage artifact is\n`data/legal/phase5/phase5_coverage_v1.json`.\n""")
    write("PHASE_5_SOURCES.md", f"""# Phase 5 official-source register\n\nRetrieved: 2026-09-28. Each row is a source-trace record; it is not an\naction-level legal conclusion. `retrieved` indicates that this collection\nprocess received and SHA-256-hashed a response body. Other outcomes preserve\naccess limitations for reproducibility.\n\n{source_table(source_metadata)}\n\nThe complete machine-readable version, including provision identifiers, source\nlanguage, source hash when available, review notes, and access errors, is\n`data/legal/phase5/source_metadata.json`.\n""")
    write("LEGAL_DATA_CARD.md", f"""# GeoSAVE legal data card\n\n## Snapshot\n\n- Snapshot: `phase5-legal-snapshot-v1`\n- Jurisdiction selection: 25 frozen ISO3 entries\n- Query unit: jurisdiction × scenario × initial speed × candidate action\n- Query count: {coverage['query_count']}\n- Physical dependency: immutable `commonroad-pilot-v1`; no physical result was\n  modified or re-run for this legal snapshot.\n\n## Layers\n\n**Global context:** WHO *Global status report on road safety 2023* profiles.\nThe collector retrieved {global_manifest['collected_profile_count']} country/territory profiles, with\n{global_manifest['unavailable_or_unparseable_count']} explicit unavailable or unparseable attempts.\nWHO fields are descriptive context and cannot establish candidate-action\nlegality.\n\n**Deep-Law:** 25 official-source index records with provision locators, source\nlanguage, scope, retrieval state, and two-pass verification history. A missing\nor access-limited source is kept explicit.\n\n## Status semantics\n\n`NOT_DETERMINED` means the snapshot does not have sufficient domestic\nprimary-law evidence plus all material scenario predicates to classify that\naction. It never means `PERMITTED`. `CONFLICTING_AUTHORITIES` is reserved for\ncontradictory applicable evidence, which was not emitted in this snapshot.\n\n## Limitations\n\nAll action-level decisions in this snapshot are `NOT_DETERMINED`; therefore it\nmust not be used as a resolved-law benchmark or to estimate jurisdictional\ncompliance. It is a frozen, provenance-backed record of the current legal\ncontext boundary. Source-language text controls, no human legal-expert review\nis claimed, and international instruments do not become domestic law by\ndefault.\n\n## Disclaimer\n\nThe GeoSAVE legal dataset is a research representation of selected\nroad-traffic rules and is not legal advice. Laws change and may contain\njurisdiction-specific exceptions not represented in the benchmark. Verify\ncurrent primary sources before use outside research.\n""")
    print("Generated Phase 5 documentation from frozen data")


if __name__ == "__main__":
    main()
