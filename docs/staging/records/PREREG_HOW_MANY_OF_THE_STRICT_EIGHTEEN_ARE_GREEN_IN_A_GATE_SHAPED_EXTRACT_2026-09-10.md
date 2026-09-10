**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `decide-what-selects-a-control-whose-subject-is-a-whole-package`) · **Class:** controls_that_cannot_fail

# PREREG — how many of the strict eighteen are green in a gate-shaped extract, and how many have drifted?

Written BEFORE the grading run. This turn takes items **0** and **1** of the "what is next" list in
`docs/staging/SEAT_RESULT_SELECTING_A_CONTROL_BY_WHAT_IT_SCANS_IS_THE_ALWAYS_RUN_LIST_SPELLED_DIFFERENTLY_2026-09-10.md`:

> 0. Advance this tree to origin, then cite the census from `pre_commit_test_gate.py` — the
>    backed-out wiring. Blocked only on the tree being three behind.
> 1. Grade each of the 18 strict members green in a **clean HEAD extract** (not this shared tree),
>    and add the green ones to `CONTROL_TESTS` with their measured cost stated.

Item 0's stated blocker is **discharged**, and that is read off git rather than predicted:
`git rev-list --count HEAD..origin/main` is **0** in this worktree, and the census now reports
`already on CONTROL_TESTS: 6` where the previous turn measured 5 — the sixth is origin's
`test_seat_guard_daemons.py`, landed atomically with its nine `refuse_if_foreign` guards. The pair
the previous turn refused to split has arrived whole.

## What is NOT the question

That door 3 collapses into door 1 is settled and I am not re-opening it. It was measured over 40
real commits — subject-selection at root granularity fires on **40 of 40**, adding a median of 50
files to a median-18 selection — and the arithmetic, not the opinion, is what refutes it. I agree
with the conclusion and with its reason: every commit in this repo touches one of these roots, so a
rule keyed to roots is an always-run list wearing a derivation. **The list is the instrument.** This
turn is the increment that makes the list actually cover the affordable unit.

Nor is the census membership a question: `--strict-dataflow` is deterministic over the tree and
returns the same 18 every time it is asked.

## The questions whose answers I do not know

**Q1. How many of the 18 pass in a clean HEAD extract shaped like the gate's own?**

Not the shared tree, and not this worktree either. Built with the gate's own helpers so the
environment is the one a candidate entry would actually face:
`git archive HEAD | tar -x` → `surgical_land._make_standalone_repo` (git init, read-only
alternates, HEAD at the parent, `read-tree`) → `surgical_land._overlay_untracked_data`. An
index-keyed control fails closed in an extract with no index, and a data-reading control fails on
an absent cache; both would read as a red that is really a wrong harness, so the harness is
borrowed rather than approximated.

**Prediction: 15 green (band 11–18).**

**Q2. How many of the reds are a GENUINE DRIFT — the control correctly reporting a population that
grew behind it — as opposed to machine state, isolation, or harness shape?**

This is the load-bearing one. The entire premise of this class is that a control nothing selects
drifts silently, and the class has exactly two demonstrated instances: `test_live_ledger_guard.py`
(74 → 86 writers over fourteen days) and `test_seat_guard_daemons.py` (nine entrypoints over nine
days). If eighteen more controls have never been selected and **none** of them has drifted, then the
cost of the selection defect is much lower than this class has been asserting, and the honest
consequence is that the 18 are worth less than the 43.8s they cost.

**Prediction: 1 genuine drift (band 0–3).**

**Q3. Wall-clock for the green subset as one pytest invocation, on this machine.**

The previous turn measured 390 tests / 43.8s for all 18 in the shared tree. The green subset is
smaller by however many Q1 removes.

**Prediction: 38s (band 15–70s).**

## What each answer commits me to, fixed now

- **Q1 ≥ 11 and Q3 within band** → add the green members to `CONTROL_TESTS`, each with its measured
  cost stated the way the existing nine entries state theirs, and cite the census beside them.
- **Any red at all** → it is **not** added, and it is filed with its cause named. Adding a red file
  to a list that runs on every code commit wedges every lane, which is strictly worse than the
  defect being fixed. This is not a judgement I get to re-make in the moment: it is the lesson
  `test_seat_guard_daemons.py` already paid for once, when its line was deliberately withheld.
- **Q3 above 70s** → I add a subset chosen by cost and say plainly which members I dropped and what
  the drop leaves uncovered. A silent top-N is the failure mode; `log what was dropped` is the rule.
- **Q2 = 0** → I say so, beside the class's own cost claim, and record that the two known drifts may
  be the whole of the damage rather than a sample of it. That would weaken the argument for this
  turn's own change, and it is written here before the answer so it cannot be quietly dropped after.

## Recorded before the answer

No part of the grading run has been executed at the time of writing. The only figures already in
hand are the census output (18 strict / 6 already listed), which is a derivation over the tree and
not a measurement, and the previous turn's 43.8s, which is quoted above as theirs.
