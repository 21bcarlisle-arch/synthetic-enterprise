# [RESULT] The level reconciler now grades the one row it could never afford to run

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted

Answers `docs/staging/records/SEAT_PREREG_WHETHER_A_RED_AT_HEAD_SHORT_CIRCUIT_MOVES_THE_LEVEL_
RECONCILERS_GRADED_COUNT_2026-09-25.md`, written before the measurement. All four predictions
held; the one question I said I could not answer — how many rows other than KNIFE3 — came back
**one, and only one**, which is a smaller result than I expected and is stated as such below.

## What was wrong

`tools/level_zero_contradicted_by_its_own_controls.py` returned `population 28, graded 0`. The
age leg that discarded nine atom-own controls was fixed in `8a1269101` + `d214fc5e7` and the
number still did not move, because the instrument was bounded by **cost, not by evidence**:
production caps each atom at `_LEVEL_ZERO_TIMEOUT_S = 60` (`background/delivery_seat.py:1038`,
deliberately — the orientation's brief has to arrive) while `KNIFE3_wall_crossing_paydown`'s
twelve suites cost 1078s and 2.44 GB. The rows naming the most controls could never be weighed.

## The economy, and why it is not a loosening

CONTRADICTED requires the **whole** named set to pass. A set holding a test that is already red
at HEAD cannot reach it, whatever the run costs — so for those rows the expensive run buys a
verdict that is already known. `assess` now asks the HEAD-red observation store before the budget
check, and a row with a red in its named set resolves to SILENT with no run.

It is the predating-control leg's argument again: **this can only ever silence a row and can
never be the thing that refuses one.** `contradicted` is structurally unreachable from it.

## Measured, live, 2026-09-25

| | |
|---|---:|
| candidate population | 28 |
| rows silenced by a red at HEAD | **1** — `KNIFE3_wall_crossing_paydown` |
| controls not run for it | 12 |
| reds that silenced it | 2, both in `tests/simulation/test_home_move_undeliverable_win.py` |
| runtime saved per pass | ~1078s and 2.44 GB, against a 60s cap it could never meet |
| `contradicted` | 0, unmoved |

Both reds have been on the register **19 consecutive census runs since 2026-09-02**, which is the
longest-standing entry it holds. KNIFE3 was discharged by hand this way and came back SILENT; the
machine now reaches the same answer for free.

## The honest size of this

**One row of twenty-eight.** `graded` moves 0 → 1, and 27 rows are still ungradable — they return
earlier, on an absent named control, a predating set, or provenance. This did not fix the census;
it removed the one cause that no amount of budget could ever have fixed, and left the others
exactly where they were. Anyone reading `graded 1 of 28` should read it as that.

## The fail-closed half, which is the part that is not free

An unusable register falls through to the run exactly as before the leg existed. Three named
states, distinct because they send a reader to three different places: `REGISTER_UNOBSERVED` (no
run recorded), `REGISTER_UNDATED` (no readable stamp), `REGISTER_STALE` (older than seven nightly
census runs).

The staleness bound is **sourced, not chosen**: `background/head-green-census.timer` is
`OnCalendar=*-*-* 03:30:00`, `Persistent=true`, so a healthy store gains a run a day. It is
deliberately loose. A 24h bound would have made the whole mechanism inert on the day it landed —
measured, the last recorded run was `2026-09-23T04:31` — which is the fourth control-failure
class: a screen that is unsatisfiable exactly when its subject is worst.

**The stale arm is reachable in this very worktree, not only in a fixture.** The observation store
is untracked machine state, so in an isolated worktree or a `git archive` extract it is simply
absent, the probe reads UNOBSERVED, and every row fails closed to the run. Confirmed by running
the probe here: `reds: [] | unusable: no census run is recorded…`.

## Why it reads the store and not `HEAD_RED_REGISTER.md`

The work item named the register document. The register **is** that store rendered — one fact,
two surfaces — and a second parser of the rendering is the shape where one control comes to
disagree with the control it describes. It is not hypothetical: measured today, the committed
register says **41 red at `f705248ae`** and the live store says **37 at `8f315e53f`**. A markdown
parser would have silenced rows on four tests that are green now, and could not have said which
reading was current.

Redness is read as the **observation** (`currently_red`), never through `owed()`: acceptance in
`head_red_baseline.json` is a decision about whether we still owe work, and an accepted red is
still red. The question here is only whether the set can all pass.

## Controls, and what each one dies to

Four, in `tests/tools/test_level_zero_contradicted_by_its_own_controls.py`, mutation-proven:

* `test_all_four_states_of_the_red_at_head_probe_are_reachable` — one control over the whole
  partition, including that the three unusable reasons stay **distinct**. A probe that declined
  everything would satisfy three legs written singly and still red this one.
* `test_a_row_naming_a_control_red_at_HEAD_is_SILENT_and_its_suites_are_NEVER_RUN` — asserts on
  the list of paths the runner was handed, not on the verdict. A leg reaching the same silence
  *by running the suites* would pass a verdict-only test and buy nothing.
* `test_a_stale_or_unreadable_register_FAILS_CLOSED_and_the_suites_still_run` — both arms against
  one fixture, because a test pinning only the stale arm passes against a leg that was disabled.
* `test_a_red_a_person_has_ACCEPTED_still_silences_the_row` — and it asserts its own premise
  first (`owed` really does subtract that node), so it cannot go green on a rotted setup.

## The mutations, and the two that went green first

Seven mutations, each re-run until it fired on the leg written for it:

| mutation | caught by |
|---|---|
| the short circuit deleted entirely | the silence leg **and** the fail-closed leg |
| the leg made unconditional (silence on an unusable register) | 11 tests, incl. the partition control |
| the staleness bound removed | the partition control **and** the fail-closed leg |
| UNOBSERVED treated as usable | the partition control |
| acceptance subtracted from the reds | the acceptance leg |
| the three unusable reasons collapsed into one string | the partition control |
| the whole-path match loosened to a substring match | the partition control |

**Two of those went green on the first attempt and neither was an equivalence.**

* *Acceptance subtracted.* The first draft of that mutation called a function that does not
  exist, so it was a **no-op** — the third cause of a green mutation, and the flattering reading
  would have been "the control holds". The real mutation then exposed that the control could not
  have caught it anyway: it asserted `owed()` behaviour with the accepted list passed in **by
  hand**, and no baseline file existed in the fixture tree to subtract. The test now writes a
  real `head_red_baseline.json` at the path the loader resolves, and asserts its own premise
  before the claim. It fires.
* *Substring match.* `str(node).split("::", 1)[0] in wanted` loosened to `any(w in str(node) ...)`
  and all 45 tests stayed green. That is **a missing test, not an equivalence**: it silences a row
  on a red in `vendor/tests/x/test_a.py` when the row names `tests/x/test_a.py`. The partition
  control now carries that node and the mutation fires.

Both are recorded here rather than quietly fixed, because a control that was green for the wrong
reason and a control that was always right look identical once the gap is closed.
