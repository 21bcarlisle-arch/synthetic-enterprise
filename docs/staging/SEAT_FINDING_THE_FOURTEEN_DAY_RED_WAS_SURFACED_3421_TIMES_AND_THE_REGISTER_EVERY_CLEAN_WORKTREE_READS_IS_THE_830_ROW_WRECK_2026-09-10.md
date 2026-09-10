**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `find-the-ratchets-in-tests-background-that-are-red-at-head-and-select-nothing`) · **Class:** controls_that_cannot_fail

# FINDING — the fourteen-day red was surfaced 3,421 times, and the register every clean worktree reads is the 830-row wreck

Pre-registered before measurement:
`docs/staging/records/SEAT_PREREG_WHY_A_NIGHTLY_CENSUS_THAT_NAMES_A_RED_EVERY_NIGHT_SURFACES_NOTHING_2026-09-10.md`.
Three of its four predictions were wrong and the grading is in full at the bottom.

## The claim this refutes is my own seat's, twice

`SEAT_FINDING_THE_UNGUARDED_LEDGER_WRITER_RATCHET...2026-09-09`: *"nothing anywhere can currently
see it"*. Its sibling `SEAT_FINDING_A_SECOND_WHOLE_BACKGROUND_RATCHET...2026-09-10`: *"a red that
blocks nothing is never triaged into a baseline, because nothing ever surfaces it to be triaged."*
And `SEAT_RESULT_THE_STEM_SELECTOR_CANNOT_REACH_TWENTY_SEVEN...2026-09-10`, discharging item 3:
*"This is R15's FAIL-SILENT killer at the **selection** layer."*

**All three are false, and the same measurement kills all three.** Nothing was silent. Every layer
of the machinery ran, correctly, and said so — nightly, by test id, with age attached.

## What actually happened, layer by layer, all of it working

| layer | state | evidence |
|---|---|---|
| `head-green-census.timer` | fires nightly, enabled | last run 2026-09-10 03:30:33 BST |
| the unscoped suite vs a clean HEAD checkout | **runs, completes** | 7 completed runs in the journal retention window (Sep 4–10); 33,697 passed on the last |
| both ratchets detected | **named by test id, every night** | `NEW RED tests/background/test_live_ledger_guard.py::test_the_narrowing_...` on Sep 4,5,6,7,8,9,10 — 7 of 7 |
| age computed | **yes** | `runs_red: 9`, `first_seen: 2026-09-02T13:18:33` for both, in `head_red_observed.json` |
| `HEAD_RED_REGISTER.md` rendered | **yes, current** | "43 owed, longest-standing first", written 2026-09-10 04:46 |
| `head_red_register.drawable()` | **43, non-empty** | so the register IS work |
| spliced into `staging_rooms.work_queue` at rank 37 | **yes** | position **7 of 138** |
| supervisor doorbell names it | **yes** | **3,421 log lines** name `HEAD_RED_REGISTER.md` |

There is no broken link. **The red was surfaced roughly 3,421 times and drew nobody.**

## So what IS the defect: the doorbell has no differentiation

The supervisor's doorbell renders `_unprocessed_staging_files()` as **one line of 139
comma-separated filenames**, every ~2 minutes. `HEAD_RED_REGISTER.md` is the 7th name in that blob.
It carries no count, no age, no severity — nothing that separates "a register whose oldest red has
stood 10 consecutive nightly runs" from the 132 finding documents beside it.

And it is **structurally permanent**. Its own header says *"THIS IS A REGISTER, NOT A QUEUE ITEM.
Do not archive it."* So a never-removable item sits inside a list whose entire read is *a backlog to
be drained*. It has been in position ~7 of that list, unchanged, for fourteen days. An item that is
always there, in a list that means "these need clearing", is indistinguishable from furniture.

**That is the mechanism, and it is not a selection failure.** Selection was never the binding
constraint for these two tests: the nightly census is unscoped and selects *everything*.

### Which makes my own prior recommendation wrong at the layer it aims at

`SEAT_RESULT_THE_STEM_SELECTOR_CANNOT_REACH_TWENTY_SEVEN_WHOLE_TREE_RATCHETS...` recommended
option (3), *change the selector*, as the fix addressing the class. **That recommendation is aimed
one layer too low.** Widening the pre-commit stem selector would make these tests run *sooner*, at
commit time, when the nightly unscoped census already runs them and already names them. It buys
earlier notice of a fact that was published 3,421 times and read zero times. The binding constraint
is between the register and a reader, not between a staged path and a test.

I pre-registered this branch precisely because it was the one I would be slowest to see, and it is
the branch that fired.

## The second defect, and it is live in every worktree right now

`docs/observability/head_red_observed.json` was last **committed** in `bc57c8e30` on **2026-09-02**
— the run that recorded 830 red, 760 of them `OSError`, the tmpfs/ENOSPC wreck.
`docs/staging/reference/HEAD_RED_REGISTER.md` was last committed `108ff5a68`, 2026-09-05, at 21.

The census writes both into the **shared working tree** every night and nothing ever commits them.
Both show as ` M` in the shared tree and have for eight days. Consequence, measured in this
isolated worktree:

```
shared working tree:  {"owed": 43,  "runs": 10}   <- current, correct
THIS clean worktree:  {"owed": 830, "runs": 1}    <- the 2026-09-02 wreck
```

**Every isolated worktree, every clean HEAD extract, and every fresh checkout draws a register
that says 830 subjects are owed.** The register's own header text names exactly this as the thing
it was built to replace — *"one paragraph must not be able to retire 830 subjects, which is the
wallpaper this register exists to replace"* — and at HEAD the register **is** the 830.

### It also means both sibling findings' cited evidence was read from the wrong tree

Both wrote *"present in `head_red_observed.json` and absent from `head_red_baseline.json`"* as
proof of an observed-but-never-triaged red. Checked at **test-id** granularity: at HEAD that file's
only `live_ledger_guard` row is `test_write_gap_entry_still_writes_when_given_a_scratch_path`, and
its `seat_guard_daemons` rows are four `TestRefuseIfForeign`/`TestResidentDetection...` tests.
**Neither ratchet's own test id is in the file at HEAD.** The claim was true in the shared working
tree and false in the tree those findings graded their redness in. Instance wrong, mechanism right —
and the right mechanism turns out to say the opposite of what it was cited for: the store proves the
reds *were* observed, nine times each, with dates.

## The measurement the draw asked for: red at HEAD under `tests/background/`, with drift

From the store at HEAD `dceedff0f`, run `2026-09-10T03:46:53Z`. `runs_red` is consecutive nightly
census runs red — the drift figure.

| runs red | first seen | test |
|---:|---|---|
| **9** | 2026-09-02 | `test_seat_guard_daemons.py::TestStructuralLock::test_every_main_entrypoint_is_guarded` |
| **9** | 2026-09-02 | `test_live_ledger_guard.py::test_the_narrowing_to_measurement_ledgers_is_measured_not_assumed` |
| **6** | 2026-09-04 | `test_self_clearing_alarm_census.py::test_every_live_hit_is_dispositioned` |
| **4** | 2026-09-07 | `test_class_debt.py::test_an_accruing_undecided_class_is_work` |
| **4** | 2026-09-07 | `test_class_debt.py::test_an_accruing_class_outranks_a_finding_and_yields_to_a_persons_ask` |
| **4** | 2026-09-06 | `test_finding_severity.py::test_the_staging_root_has_no_false_discharges` |
| **2** | 2026-09-09 | `test_staging_root_resurrection_watch.py::test_the_landing_tool_actually_brackets_its_gate` |
| **1** | 2026-09-10 | `test_one_answer_standing_on_several_census_rows.py` — 8 tests, whole module |

**15 tests red in `tests/background/` at HEAD**, not the 2 the two sibling findings between them
account for. Six of the eight modules are ratchet-shaped in the load-bearing sense — a bound or a
disposition-completeness claim over a whole measured population (`test_self_clearing_alarm_census`
over every live hit, `test_finding_severity` over the staging root, `test_class_debt` over the class
corpus). The whole-module red in `test_one_answer_standing_on_several_census_rows.py` appeared
overnight and is one cause, not eight.

Repo-wide the same run owes **43**, and the trend across the seven journalled nights is
**25 → 21 → 29 → 28 → 25 → 35 → 43**. It is growing, and the growth is visible in a file nobody reads.

## Why BLOCKING

Not for the 15. For the second defect: every clean worktree's draw currently reports 830 owed
subjects from a wrecked run. Any lane that acts on that register from an isolated worktree — which
is how this seat runs — is working from an eight-day-old list dominated by 760 disk errors that no
longer exist. That is a live control reporting a false population to every reader that is not the
shared tree.

## What is next

1. **Commit the two artefacts, or decide deliberately that they are untracked machine state.**
   Right now they are the worst of both: tracked, so every worktree reads a stale copy as if it
   were current. This is a decision, not a cleanup, and it wants the second option examined first —
   a nightly-regenerated artefact that every lane must re-commit is a treadmill.
2. **Give the doorbell one differentiated line for the head-red register** — count and
   longest-standing `runs_red`, not a name in a 139-name blob. `render()` already computes `worst`;
   nothing carries it to a reader. This is the smallest mechanism that can fail here.
3. **Do not widen the stem selector for this class.** Recorded against my own prior
   recommendation, with the argument above.
4. The 13 newly-visible reds under `tests/background/` are work; the 8-test module red is one
   subject and should be drawn as one.

Deliberately **not** done here, per the draw's own instruction not to fix an instance before the
class is measured: none of the 15 is touched, and no bound is raised.

## Prereg grading — three of four wrong

| # | prediction | measured | verdict |
|---|---|---|---|
| Q1 | store is current in the shared tree, stale only at HEAD; never committed | exactly that — 10 runs shared, 1 run at HEAD, ` M` for 8 days | **HELD** |
| Q3 | age is not computable at all | age IS computed and stored (`runs_red: 9`); it is simply never shown to a reader | **REFUTED** |
| Q4 | the draw route fires but the register is outranked | it fires and ranks **7th of 138** — not outranked at all; the failure is undifferentiated presentation | **REFUTED** |
| Q5 | 6 ratchets in `tests/background/` (4–9); **2** red (band 2–4) | **15** tests red across 8 modules | **REFUTED, far outside the band** |

The direction of the error is the same one the last turn made and is worth naming twice: **I keep
predicting that the machinery failed to look, and the machinery keeps having looked.** Both turns
reached for an observation defect when the defect was downstream of a correct observation. Q4 is
the sharpest instance — I predicted a ranking failure and it was 7th.
