"""Fail-closed K3 integrity validation for canonical KA-IRO KRISIS v2 output."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "ka-iro-krisis" / "v2" / "physical"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    manifest = json.loads((BASE / "ka_iro_krisis_physical_v2_manifest.json").read_text(encoding="utf-8"))
    outcomes = [json.loads(x) for x in (BASE / "ka_iro_krisis_physical_v2_outcomes.jsonl").read_text(encoding="utf-8").splitlines()]
    planned = {x["outcome_id"] for x in manifest["runs"]}; actual = [x["outcome_id"] for x in outcomes]
    assert len(manifest["runs"]) == 720 and len(planned) == 720
    assert len(actual) == len(set(actual)) == len(planned) and set(actual) == planned
    terminal = {"completed", "failed", "not_applicable"}
    assert all(x["run_status"] in terminal for x in outcomes)
    for outcome in outcomes:
        if outcome["run_status"] == "completed":
            path = ROOT / outcome["trajectory_path"]
            assert path.is_file() and sha(path) == outcome["trajectory_sha256"]
            assert outcome["simulation_completed"] is True
        else:
            assert outcome["simulation_completed"] is False and outcome["failure_reason"]
    report = {"status": "passed", "planned_outcomes": len(planned),
              "completed": sum(x["run_status"] == "completed" for x in outcomes),
              "failed": sum(x["run_status"] == "failed" for x in outcomes),
              "not_applicable": sum(x["run_status"] == "not_applicable" for x in outcomes)}
    (BASE / "validation_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))

if __name__ == "__main__": main()
