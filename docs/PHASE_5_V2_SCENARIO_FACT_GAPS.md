# Phase 5 v2 scenario-fact gaps

The frozen geometry gives scenario identity, initial speed, road dimensions,
actor type, and coordinate-side semantics. It does not establish traffic side,
lane-marking type, whether a lateral maneuver crosses a marking/opposing lane
or shoulder, crossing designation, signal state, road class, locality, posted
limit, or legal necessity conditions.

Those gaps block unconditional action-level legal classifications. The v2 fact
table records each as `UNKNOWN`; it does not repair them by inference. The
left/right coordinate convention means only positive/negative lateral direction
in the frozen geometry, not a globally meaningful lane or traffic-side concept.
