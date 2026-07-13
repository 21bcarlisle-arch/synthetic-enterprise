# Judge gold set — the director's Expert Hours, frozen

Each `*.json` here is a real case the director (or an equivalent human
adjudication) **caught** — an artefact that looked plausible and was in fact
defective. Because every case is a director catch, every case's
`director_verdict` is `"defect"`. A judge that returns `"pass"` on one of these
**missed what the director saw** — and now we can say so with a number
(`background/judge_validation.py::score_judge_against_gold`).

This is approach 4 of JUDGING_THE_JUDGES.md Part 1 (director P1, 2026-07-13):
the LLM-judge verdict QUALITY is un-mutation-testable, so it is OUTCOME-tested,
and the gold set is the human-adjudicated ground truth against which any judge —
mechanical control, cold-eyes persona, phase-close-evaluator — is scored.

## Case schema
- `case_id` — stable id.
- `director_verdict` — always `"defect"` (a director catch).
- `defect_class` — the class of the error (drives R10 class-fix reasoning).
- `artefact` — the plausible-looking thing put in front of a judge (the claim,
  the figure, the chart, the bill), in the terms a judge would see it.
- `the_catch` — what the director actually saw / why it is wrong.
- `source` — a checkable doc reference (real, never fabricated).
- `detectable_by` — the mechanical control(s) that SHOULD fire on this class,
  where one exists (links the gold set to the CONTROLS_THAT_CANNOT_FAIL / R15
  mutation apparatus). `null` where the catch is a judgment no mechanical
  control encodes — exactly the cases only an LLM judge or the director can hold.

## Adding a case
Seed only from a REAL human adjudication with a checkable `source`. A fabricated
gold case poisons every judge score derived from it — worse than no gold set.
