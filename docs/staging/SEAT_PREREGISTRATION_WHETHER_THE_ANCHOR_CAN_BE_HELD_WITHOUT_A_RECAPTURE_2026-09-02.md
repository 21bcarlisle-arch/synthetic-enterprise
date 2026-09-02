**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# PRE-REGISTRATION — can `YEAR_LEVEL_ANCHOR` be held by anything at all without a re-capture?

**Filed 2026-09-02, delivery seat, from an isolated worktree at HEAD `4013b1de1`, BEFORE any
measurement in it was run and before any of its output was read.** Grading is appended below, beside
each prediction's filed text, misses kept.

## Why this run, given the drawn item is already landed

The drawn Lane 0 item's own "done means" is discharged, by two seats working concurrently, and none
of it is re-derived here: the collision is answered as a PARTITION at `d374b1977`
(`docs/design/THE_LEVEL_ANCHOR_COLLISION_ANSWERED_2026-09-02.md`), the block document is committed
at `9238075d9`, `tools/population_anchor.py`'s 2022 reads fail closed with named reasons, the
register is corrected rather than re-keyed, and the 2022 slot's inertness is established at
`6fc06b535`. Verified this tick, not assumed: `git status --porcelain
simulation/departure_level_anchor.py` is empty, `HEAD...origin/main` is `0 0`, and the three control
files are `81 passed, 2 xfailed` on a clean `git archive HEAD` stem.

**What is NOT discharged is the sentence the direction put underneath all of it:** *"whatever you
decide is unverifiable until the anchor has a control that can move against it."* `4871e53ee`
measured that halving every entry leaves the whole control file green. `d374b1977` added five legs
since. **Nobody has re-measured whether the hole is still open, and every document in this thread
asserts it from the 09-01 reading.** That is the subject.

The cause is documented and agreed: the band leg's subject is the STORED capture
`docs/reports/c2_departure_factors.json`, which carries the `sim_level_anchor` of the run that
produced it, so `simulation/departure_level_anchor.py` is **not in its read path at all**. The
anchor reaches its only accountability route through a re-capture.

**The question this run asks is whether that indirection is unavoidable.** A stored capture that
records the anchor it executed under is not opaque: it states, per row, which table produced it.
That makes one property checkable with no re-capture and no re-fit — *the capture the band verdict
is read from was produced by the table that is live*. If it holds, a control keyed to it moves
against every edit to `YEAR_LEVEL_ANCHOR` immediately, and a legitimate re-fit-plus-re-capture moves
both sides together and stays green. **That is keyed to the property, not to today's answer**, which
is the distinction the direction reserves and the reason this is not the forbidden re-keying.

## Predictions

**P1 — the null rung, replicating `4871e53ee` at today's HEAD.** Halving every value in
`YEAR_LEVEL_ANCHOR` (7 entries) on a clean HEAD stem leaves
`tests/architecture/test_switching_rate_commons.py`, `tests/simulation/test_departure_risks.py` and
`tests/tools/test_population_anchor.py` **entirely green** — same counts as unmutated, `81 passed,
2 xfailed`. **Predicted: the mutation SURVIVES; the hole `4871e53ee` found is still open after
`d374b1977`'s five new legs.** Refuted if any test fails or any xfail turns XPASS.

**P2 — the agreement holds today.** For each of the seven FITTED years, the `sim_level_anchor`
recorded in `docs/reports/c2_departure_factors.json` equals the live `YEAR_LEVEL_ANCHOR[year]` to
1e-6. **Predicted: all seven agree** — the correction to
`WORKER_FINDING_THE_LEVEL_ANCHOR_GUARD_IS_GREEN_AT_HEAD...` established the capture chain
seven-year block → `c2` capture by reading this same column, so the capture ran under the block that
is now HEAD. Refuted if any fitted year disagrees.

**P3 — the one I am least sure of, and the reason it is worth writing down.** The capture predates
the partition: it was produced by the PRE-`d374b1977` accessor, which fell back to the reference
year for every unfitted record year. So for the unfitted years the capture should carry `3.053619`,
and comparing that against today's `_unfitted_anchor` should **agree on 2016 and 2025** (still the
reference year's value) and **disagree on 2022** (today `NO_LEVEL_CORRECTION = 1.0`). **Predicted:
2022 disagrees, 2016 and 2025 agree.** Two ways this is refuted rather than confirmed: 2022 may be
absent from the capture entirely (the `c2`/`ladder`/native family carries zero 2022 renewal rows),
in which case the 2022 clause is **VACUOUS and I will report it as vacuous, not as passed**; or the
capture's unfitted rows may carry something other than `3.053619`.

*Consequence, registered in advance so it cannot be chosen after the fact:* if P3 holds, the new
control must be scoped to the FITTED years, and the 2022 disagreement is a separate reportable fact
— the stored capture the band verdict is read from ran 2022 at `3.053619`, not at the declared
`1.0`. It changes no number, because `6fc06b535` established the 2022 slot is inert, but a control
that swept 2022 in would go red at HEAD for a reason that is not drift.

**P4 — the new control can fail.** A leg asserting P2's agreement FIRES (red) under P1's halving
mutation, naming the disagreeing years and both values. **Predicted: fires on all seven fitted
years.** Refuted if it passes, or fires for a reason other than the anchor values (an import error,
a missing file, a scope assertion tripping before the verdict).

**P5 — and it is not a constant verdict, driven from BOTH sides.** The same leg is green at
unmutated HEAD, and also fires when the CAPTURE's `sim_level_anchor` column is mutated instead of
the table. **Predicted: green unmutated; fires on capture-side mutation.** Refuted if the pass
branch is unreachable, or if only one side drives it.

## Constraints — things that must NOT happen, discharged by reading the artefact

1. **No value in `YEAR_LEVEL_ANCHOR` is added, edited or deleted by this stretch**, and no entry in
   `UNFITTED_YEARS` is altered. All mutation is on a throwaway `/tmp` stem, never in the worktree.
2. **No band is widened, and no `xfail` marker is removed, narrowed or re-keyed to today's
   readings.** Both strict markers stand exactly as they are.
3. **No capture is regenerated or overwritten.** `docs/reports/` is read-only to this stretch.

Discharged at grading by pasting `git status --porcelain` and `git diff --stat` over
`simulation/`, `docs/reports/` and the two xfail markers — read from the artefact, not recalled.

---

# GRADING

*Appended after the run. Each prediction graded beside its filed text above; misses kept, not
revised.*

Run on a clean `git archive HEAD` stem of `4013b1de1` at `/tmp/mutchk`, mutations under `python3 -B`.

**P1 — CONFIRMED, and it is the finding.** Halving all seven entries on the clean stem:
`81 passed, 2 xfailed`, identical to unmutated. **A 2x error in every value of the table is still
invisible to all three control files, after `d374b1977` added five legs.** `4871e53ee`'s measurement
replicates at today's HEAD; the hole was not closed by any work in this thread, and every document
that has asserted it since 09-01 was asserting it from a stale reading that happened to be right.

**P2 — CONFIRMED, all seven.** `2017: 4.547299 · 2018: 2.882178 · 2019: 4.803900 · 2020: 6.412007 ·
2021: 4.488202 · 2023: 0.364038 · 2024: 3.053619`, each recorded in the capture exactly once and
equal to the live table to 1e-6. The capture chain the correction established by reading this column
is corroborated by re-reading it.

**P3 — SPLIT, and the clause I flagged as least sure is the one that went VACUOUS.**
- *2016 and 2025 agree:* **CONFIRMED.** Both record `3.053619`, the reference-year fallback, and
  `_unfitted_anchor` returns the same today.
- *2022 disagrees:* **VACUOUS, not passed.** 2022 is **absent from the capture entirely** — 9 of 10
  record years present (2016 n=1, 2017 n=20, 2018 n=20, 2019 n=16, 2020 n=18, 2021 n=23, 2023 n=17,
  2024 n=17, 2025 n=16). I registered this as one of two refutation routes and it is the one that
  fired. There is no stored 2022 row running at `3.053619`, so the "separate reportable fact" I
  registered in advance **does not exist and is withdrawn** rather than quietly dropped.

*The registered consequence is therefore also void, in the useful direction.* I pre-committed to
scoping the control to the fitted seven if P3 held. Because every year present agrees — unfitted as
well as fitted — the control covers all **nine**, and is written against `year_level_anchor` (the
accessor the world calls) rather than the table, so a change to the PARTITION is caught by the same
leg. That is a wider subject than the prereg planned for, arrived at by measurement rather than by
preference.

**P4 — CONFIRMED.** The new leg fires under the halving mutation, on the anchor values, with both
numbers in the message (`assert 1.5268... < 1e-06`). Not an import error, not a scope assertion
tripping first — the scope legs pass and the verdict leg is what fails.

**P5 — CONFIRMED, both sides.** Green unmutated (before and after all mutations, restored).
Fires on MUT-B (moving 2024 from `YEAR_LEVEL_ANCHOR` into `UNFITTED_YEARS`). Fires on MUT-C
(editing ONE capture row's `sim_level_anchor` to 9.999999), reporting *"the capture records 2
different anchors for 2020"* — so the verdict is driven from the artefact side as well as the module
side, and the pass branch is reachable. Not a constant verdict.

## Constraints, discharged by reading the artefact and not by recalling my own behaviour

```
$ git status --porcelain simulation/ docs/reports/
(empty)
$ git diff --stat tests/architecture/test_switching_rate_commons.py
 tests/architecture/test_switching_rate_commons.py | 102 ++++++++++++++++++++++
 1 file changed, 102 insertions(+)
```

All three hold. Constraint 2 is discharged more strongly than by inspection: the diff is **102
insertions and 0 deletions**, so no `xfail` marker, band or existing assertion can have been altered
by this stretch — there is no deleted line for an edit to hide in. All mutation was on `/tmp` stems,
restored and re-verified green.

## What remains open, and is not closed by this

The new leg holds the two artefacts to one generation. **It does not judge the anchor's value** —
the band leg still does, and it is still `xfail(strict)` with the world out of band in 7 of 7
readable years. The anchor is still band-held in NO year. What changed is that it is no longer
*unheld entirely*: an edit that is not followed by a re-capture can no longer pass silently.
2022 remains outside every control's reach for the mechanism reason `6fc06b535` established, and
this leg says so in its own docstring rather than letting a reader infer coverage it does not have.
