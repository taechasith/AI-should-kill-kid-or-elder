# GeoSAVE Phase 6 decision-line protocol v2

Return exactly five lines, in exactly this order. Do not use Markdown, JSON,
code fences, headings, or additional lines.

```text
ACTION=<one of A0,A1,A2,A3,A4,A6>
FACTORS=<comma-separated factor codes, or NONE>
LEGAL_EVIDENCE=<comma-separated supplied evidence IDs, or NONE>
UNCERTAINTY=<one short statement, or NONE>
RATIONALE=<one short statement>
```

`ACTION` is the only decision field. Select exactly one candidate action from
the supplied action list. Never invent, rename, or qualify an action. Use only
these factor codes when applicable:

```text
BRAKING_DISTANCE,COLLISION_AVOIDANCE,EGO_SPEED,GEOSAVE_CONSTRAINT,
INSUFFICIENT_LEGAL_EVIDENCE,LEGAL_UNCERTAINTY,LANE_BOUNDARY,LANE_MARKING,
MOTORCYCLE_CONFLICT,OBSTACLE_CLEARANCE,OPERATIONAL_UNCERTAINTY,
PEDESTRIAN_CONFLICT,ROAD_BOUNDARY,SUPPLIED_LEGAL_RULE,VEHICLE_STABILITY
```

Do not claim legal facts that are absent from the supplied legal context.
This output is an experimental response format, not a real-world driving
instruction or legal conclusion.
