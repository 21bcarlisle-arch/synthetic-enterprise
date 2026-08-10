# [WORKER-REPORT] The fourteenth wedge: a rest-ladder rung reading live disk (2026-08-10)

**Tick:** scheduled worker tick, 2026-08-10 ~11:46 UTC. **Rung:** the publish-gate red named in
`.last_gate_blocking_tests.json`, per `DIRECTOR_PRIORITY_PUBLISH_FIRST_2026-08-10` draw 1 ("if it
names a third test, that is the same species again, fix it at HEAD").
**Episode at draw:** 113 consecutive failures, `wedge_since` 2026-08-09 ~16:30 UTC, 70 markers queued.
**Fix:** this commit. **Publisher:** pid 2622357 was alive throughout; **no rival publisher started.**

## The named red, and why the tree disagreed with the gate

`.last_gate_blocking_tests.json` (13.6 min old at draw, `ts` 11:33:09) named:

```
FAILED tests/background/test_forward_discovery_draw.py::test_may_rest_with_genuinely_empty_authorized_set
```

`observed`: that test **passes in the working tree** and **fails at HEAD**.

```
$ python3 -m pytest <that test> -q                       # working tree
1 passed
$ git archive HEAD | tar -x -C /tmp/gatechk && cd /tmp/gatechk && python3 -m pytest <that test> -q
1 failed          # AssertionError: rest was refused ... assert False is True
```

Bisecting the rungs of `_is_drained_and_gated()` **in the HEAD checkout**, with the test's own
`_gate_core_and_idle_lanes` fixture applied, named the refuser on the first pass:

```
_publish_gate_wedge_active        -> None
_operational_red_persistent_draw  -> None
_declared_defect_backlog_draw     -> None
_stale_gap_row_draw               -> 'STALE-GAP-ROW self-refill (RUNG 4b): 13 published coupled-gap
                                      measurement(s) were taken by code that has since changed ...'
_propose_half_draw                -> None
_forward_discovery_draw           -> None
```

**RUNG 4b (`_stale_gap_row_draw`, landed 2026-08-10) reads live disk and nothing isolates it.** It
holds no path of its own: it imports `background.gap_ledger_reconciler` and reconciles the real
`docs/observability/coupled_gap_ledger.json` against real git history. At HEAD that ledger had 13
refreshable rows, so the rung fired, refused rest, and flipped every "authorized set is empty →
rest is permitted" assertion in the directory.

**Blast radius, measured at HEAD:** 11 failures across
`test_forward_discovery_draw.py` — forward-discovery, propose-half and three R15 mutation proofs,
none of which has anything to do with gap measurements.

**Why it was invisible locally, and this is the part worth keeping:** `coupled_gap_ledger.json` is
dirty-and-fresh in the shared working tree and stale at HEAD. The developer judges the tree; the
gate judges a clean `git archive HEAD` checkout
(`DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09`). A rung reading a *derived artefact* therefore
puts those two judges into systematic disagreement — the director's own named species ("derived
artefacts going stale at HEAD because work lands faster than hand-refreshing"), reaching the gate
through a **test fixture** rather than through the artefact's own consumer, which is why draw 2's
`_repair_derived_artefacts_in` did not catch it.

## FIFTH INSTANCE — closed at the class (R10), not the instance

| # | Rung | Date | Damage |
|---|---|---|---|
| 1 | RUNG 4 declared-defect backlog | 2026-07-24 | 16 tests red |
| 2 | RUNG 1 publish-gate wedge | 2026-07-24 | self-sustaining wedge, 12 tests red |
| 3 | RUNG 7 planner axes / blocked mints | 2026-07-27 | rest assertions flipped |
| 4 | RUNG 1b operational-layer red | 2026-08-08 | red-ed the gate through two files |
| 5 | RUNG 4b stale-gap-row | 2026-08-10 | 11 tests red, publish wedged |

Four instance fixes, each a pin added to `tests/background/conftest.py` on the day it bit. R10
forbids a sixth. **The class fix is `tests/background/test_rest_ladder_isolation.py`:**

* `refusal_rungs(source)` — **derives** the rung set by AST-parsing the shipped source of
  `_is_drained_and_gated` for the `if <rung>(): return False` shape. Not a hand-kept list (that is
  the thing that decayed four times). The terminal `return _rule0_harden_draw() is not None` is
  deliberately excluded: it carries the *opposite* obligation.
* `test_every_refusal_rung_is_silent_under_the_rest_proof_setup` — reproduces a rest proof's exact
  world (the same `_gate_core_and_idle_lanes` fixture, the same autouse conftest pins, the register
  empty) and asks **each rung individually** whether it is silent. A rung added tomorrow is
  enumerated automatically; if it leaks, **this test names it and quotes what it said**, instead of
  eleven unrelated tests failing with "rest was refused" and no clue which level refused.
* Instance pin, in the same commit: the conftest autouse fixture pins
  `gap_ledger_reconciler.LEDGER_PATH` at an absent tmp path (absent ⇒ empty ledger ⇒ no refreshable
  row ⇒ rung silent). Rung 4b's own tests inject `work=` directly, so the pin cannot weaken them.

**R15, both ways, on the real defect — not a synthetic stand-in:**

* *With* the pin, in a HEAD checkout: `42 passed` across
  `test_forward_discovery_draw.py` + `test_governance_refusal.py` + the new control (was 11 failed).
* *Remove the pin* from the conftest in that same checkout: **3 failed**, and the class control's
  message is the diagnosis — `REST-LADDER ISOLATION LEAK -- 1 rung(s) ... _stale_gap_row_draw ->
  'STALE-GAP-ROW self-refill (RUNG 4b): 13 published coupled-gap measurement(s) ...'`.
* Enumeration proven derived, not declared: rungs added to and removed from a synthetic source move
  the answer (`test_rung_enumeration_is_derived_not_declared`).
* Detector proven able to fire on the **shipped** ladder: stubbing the real `_stale_gap_row_draw` to
  return work makes the control report it *and* flips `_is_drained_and_gated()` to `False`
  (`test_the_control_fires_when_a_real_rung_leaks`).
* **Vacuity guard on the control itself:** `_real_refusal_rungs()` refuses a parse yielding fewer
  than 8 rungs, so a rewritten ladder cannot silently make the control pass unconditionally
  (`feedback_fail_silent_control_patterns`).
* The four earlier pins are asserted still in force, so this control cannot start failing for a
  reason its own message would misattribute.

## Standing note for whoever adds RUNG 4c

Do **not** stub the new rung inside one test file. Pin its live **input** to an absent tmp path in
`tests/background/conftest.py`'s autouse fixture, beside the five pins now there. The rung's own
tests set their state in the test *body*, which runs after the fixture and therefore still
exercises it for real. The class control will tell you if you forget — by name, in one test, before
the gate does it for you in eleven.

## What this does NOT close

The 13 stale gap rows at HEAD are **real drawable work** — the rung was doing its job, and it is
still saying so. This report fixes the *isolation*, not the *staleness*; RUNG 4b remains live in
`_self_refill_draw` and will draw the re-measurement on a later tick. Re-taking them here would
have moved published numbers on a publish-first draw, which is not this tick's mandate.

— Worker tick, 2026-08-10
