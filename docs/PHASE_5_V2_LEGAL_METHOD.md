# Phase 5 v2 legal method

Status: `PREPARATION_ONLY — HUMAN_REVIEW_REQUIRED`.

Phase 5 v2 is a new primary-law action-level research dataset. It does not
modify `phase5-legal-snapshot-v1`, Phase 4, Phase 7, or Phase 8A.

## Methodological basis

Traffic-law evaluation must be grounded in the facts that make a provision
applicable. Prakken's traffic-law case study highlights that legal compliance
cannot be reduced to a generic driving label and can involve exceptions and
contextual applicability. [Prakken (2017)](https://link.springer.com/article/10.1007/s10506-017-9210-0)
LawBreaker similarly treats traffic-law testing as specification against a
scenario, rather than collision checking alone. [Sun et al. (2022)](https://arxiv.org/abs/2208.14656)
Structured formalisation work shows why source rules, conditions, and
exceptions need traceable representations. [McLachlan et al. (2021)](https://academic.oup.com/ijlit/article/29/4/255/6534108)

These works guide the data method only; they are not authority for any current
jurisdiction's law. Final status requires an official domestic primary source,
an applicable effective-date state, adequate scenario facts, and human review.

## Rules

- Scenario facts are derived only from frozen Phase 4/Phase 6 artifacts.
- A missing material fact is `UNKNOWN`, never an assumed default.
- Official legislation, regulations, gazettes, official legal databases, or
  necessary binding decisions are required for a determined status.
- Exceptions, open-textured standards, translations, and subnational scope are
  explicit fields, not hidden adjudications.
- `NOT_DETERMINED` is valid and required whenever those conditions are unmet.
- Legal classification and physical safety are separate outputs.

The v2 preparation records are `AI_PREPARED` and are not legal advice or legal
ground truth. They must not be labelled `HUMAN_REVIEWED` or `EXPERT_REVIEWED`
without an actual reviewer of the stated role.
