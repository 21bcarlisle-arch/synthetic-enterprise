**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: the premise was spent, and the re-run refuted the spec's own claim that M11 survives

**Measured 2026-09-06 03:18–03:30 BST, delivery seat, worktree `/var/tmp/se-seat-executor` at
`e20d5a2dc`. Claim id `fuel-mix-return-annotation-and-battery-anchor`. Results read from
`/var/tmp/grid_intensity_fuel_mix_battery_95c9da4db380.json`. Spec:
`tools/grid_intensity_feed_contract_battery.py`. Engine: `tools/contract_battery.py`.
Pre-registration beside this file:
`SEAT_PREREG_WHAT_THE_FUEL_MIX_RERUN_AT_THE_NEW_FINGERPRINT_WILL_SHOW_2026-09-06.md`, written
before rows M10 and M11 were readable and landed in this same commit.**

---

## The premise was spent before the turn began

The drawn item asked for three things in one commit: the return annotation, the battery anchor,
and a re-run. **The first two had already landed at `177de48c1`**, which is an ancestor of
`origin/main`. `fuel_mix` now annotates and documents seven members, and the anchor is held once
as `SUBJECT_DEF` with the three anchor strings built from it. Nothing was left to repair there,
and re-doing it would have moved the fingerprint a second time for no gain.

| the item's three deliverables | state at draw time |
|---|---|
| return annotation + docstring say SEVEN | **landed** `177de48c1` |
| `POISON_OLD`/`POISON_NEW` anchor follows it | **landed** `177de48c1`, as `SUBJECT_DEF` |
| re-run so the results file matches the new fingerprint | **in flight, not mine** |

The re-run was PID 1448564, launched 03:06:22 BST from the **shared tree**
(`/home/rich/synthetic-enterprise`), and it completed at 03:22 with all eleven rows written. I did
not start it, and deliberately did not start a second one — see the finding filed beside this,
which is about what would have happened if I had.

Verified after it finished: the shared tree's copy of the subject is clean, so the engine's
`atexit` restore did its job and no mutated source was left behind.

## The predictions, scored

Four of five confirmed. **The refutation is the useful one.**

| # | prediction | outcome |
|---|---|---|
| 1 | M1, M2 killed; every other contract killed by nobody; **M10 and M11 both survive** | **REFUTED** — M10 survives, **M11 DIES** |
| 2 | `survived_all` is `false` on all eleven rows, and that is not a survivor count of zero | CONFIRMED |
| 3 | the tenth suite has no cell anywhere | CONFIRMED — absent from baseline, poison, null and every `per_suite` |
| 4 | reachability stays at three of nine; the six `ep13_*` suites do not reach | CONFIRMED |
| 5 | both control suites stay green under the poison | CONFIRMED — the floor still discriminates |

## The refutation: M11 dies, and the spec's own prose said it survives

The spec's module docstring said, in the present tense and until this commit:

> It is M2 with `series = {}` in place of `series = []`, and it **SURVIVES** where M2 dies

and then, in the very same paragraph, described the repair that ends that survival — the control
`test_the_feed_REFUSES_to_publish_without_the_fuel_mix_rather_than_reverting_to_the_old_shape`
now asserting that the refusal **NAMES** the missing cache. **A paragraph that asserts a survival
and describes the landed repair which reverses it, and the assertion is the half a reader
believes.** M11 exists precisely because a type-correct fallback shipped past the old control; once
the control began naming the cache, the wrong namer is caught.

Measured at fingerprint `95c9da4db380`: M11 is killed by that same control, `died_but_grades_text`
false, and the **null round is green on every suite** — so the kill is behaviour, not a suite
reading this module's bytes. **The repair works, and this run is the evidence.**

Corrected in this commit, beside the claim rather than over it: the survival is kept as the reason
M11 exists, and the kill recorded as the evidence the repair landed. The fingerprint is
**unchanged at `95c9da4db380`** — verified — because `fingerprint()` hashes `(id, old, new)` and
not the contract prose or the module docstring, so this correction cannot orphan the results file.

## Where the subject actually stands

| | |
|---|---|
| contracts mutated | **11** |
| suites graded | **9** of 10 |
| contracts killed by any suite | **3** — M1, M2, M11 |
| of those, kills that grade the contract | **2** — M1 and M11 |
| contracts killed by nobody | **8** |
| suites that ever killed anything | **1** — `tests/tools/test_grid_intensity_feed_and_explore_carbon.py` |
| suites that reach the subject | **3** of 9 |
| suites that reach it and prove nothing | **2** — `test_process_run_complete`, `test_elexon_fuel_outturn` |
| rows carrying a `survived_all` verdict | **0** |

M2's kill is still the known false kill: it reddens on an `AttributeError` from a list, the wrong
class, so it never sees the contract. M11 is the honest version of the same contract and it is the
row that now proves it.

## What is NOT established, said plainly

**No row has a verdict.** `contract_battery.py:374` scores `survived_all` as
`len(callers) == len(spec.suites)`, over all **ten** declared suites; the run graded nine. So
`survived_all: false` appears on all eleven rows for a reason that has nothing to do with any
contract. The engine prints this honestly — `NOT YET GRADED ON EVERY SUITE (no verdict)` — but at
the JSON layer eleven `false`s read as "nothing survived", which is the flattering misreading and
the opposite of the truth.

The ungraded tenth suite is `tests/tools/test_ep13_embedded_generation_bound.py`, excluded on
measured cost (655.1s per round against ~90s for the other nine together; ~2h over eleven rounds).
That exclusion is a stated bound and was already documented — it is not a new defect.

**The cheap thing worth buying next is not the two hours.** All six other `ep13_*` suites are
non-reaching, because they read the subject as text and walk it as an AST rather than executing it.
If the tenth is the same, the full run buys eleven green cells that prove nothing. **One poison
round on that suite alone (~11 min) settles it**, and only if it reaches is the remaining ~2.5
hours worth spending. That is the hand-off.
