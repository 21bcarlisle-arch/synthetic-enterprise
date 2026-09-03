**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `B10_competitor_switching_response`

# The chase comparison was asking a between-arm question on the slope's population, and that is why it read "one rung in four" twice

Direction of 2026-08-29 (lane 0): re-run the chase-on/chase-off pair on the founder book and on a
window whose final year is not the only place the departure count can cross; report `max |ON − OFF|`
per rung against the world's own move, with the realised loss counts per arm per year beside it;
then either RECORD B10's level move with the measured gap or file the fourth refusal with numbers.

**B10 moves to L3 and the move is recorded** (`docs/observability/gate_authorizations.jsonl`,
self-certified, evidence below). It does not move for the reason the direction expected it to, and
the useful half of this is that the deeper book and the longer window were *not* what unblocked it.

## What was run

One tree, `e3cc43ce3` plus the shared worktree's uncommitted work, subject fingerprint
`23f45e73e252` **identical before and after both arms**. Founder book at 80 accounts seeded into
2016. Window `--end-year 2021`. Rungs `0, 0.5, 1, 2`. `chase_per_quarter` asserted to have taken
its value before each run (`0.5` ON, `0.0` OFF). Both arms report the null rung reproducing the
flat-rules control and `SVT recon agrees=True`.

**The arms ran SEQUENTIALLY, and that is a change forced by the machine, not a preference.**
`run_price_ladder` retains every rung's settlement records (`raw[k] = result`, and `household_side`
reads `phase2b.all_records`), so one arm peaks near 11 GB on this book and two at once exhaust the
guest. The first attempt ran four arms in parallel and the kernel was 1.2 GB from choosing a victim
itself. Sequential arms open a window of forty minutes for another lane to land work between them,
which nothing in the artefacts would have shown — both arms would still report their own null rung
reproducing their own control, because each arm is internally consistent with whatever tree it ran
on. `_ladder_chase_arm` now fingerprints the source before and after each arm and
`compare_chase_belief` **refuses a verdict** when the two disagree.

## The prediction I filed after the ON arm and before the OFF arm

`docs/observability/ladder_2021_prediction_before_the_off_arm.md`, written with the ON artefact on
disk and `OFF END` not yet in the driver log. It said the pair would move at the same number of
rungs as the 2026-08-28 pair — "most likely exactly one, and I do not expect more than two" —
because the ladder's paired population is 16 decisions with term starts in 2016–2018 only, whose
beliefs read evidence years 2016–2017 in either window.

**It was right, and being right is the finding.** On the cross-rung intersection the 2021-window
pair reproduces the 2026-08-28 pair *bit-identically*:

| rung | belief ON | belief OFF | move | world ON | world OFF | world move |
|---|---|---|---|---|---|---|
| 0.0 | 0.2153 | 0.2153 | +0.000000 | 0.0582 | 0.0498 | +0.0084 |
| 0.5 | 0.3728 | 0.3597 | **+0.013156** | 0.2346 | 0.2153 | +0.0193 |
| 1.0 | 0.5546 | 0.5546 | +0.000000 | 0.4344 | 0.3828 | +0.0516 |
| 2.0 | 0.8561 | 0.8561 | +0.000000 | 0.5417 | 0.5308 | +0.0109 |

Two more years of window, a book of 453 renewal decisions instead of a fraction of that, and **not
one digit changed.** A result that survives that much added evidence unchanged is not a
measurement of the world; it is a measurement of the join.

## The join

`slopes.common_population` is the set of decisions priced **and** rolled at **every** rung. It
exists for the *slope*, which has to run along one x-axis over one population. The chase question
is a between-arm comparison at a **fixed** rung, and it does not need that set — it needs only that
both arms priced and rolled the same decision at the rung being compared.

Using the slope's set costs the whole late window, and the artefact says so in one table. Decisions
priced, by term-start year:

| rung | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 |
|---|---|---|---|---|---|---|
| 0.0 | 3 | 9 | 8 | 6 | 6 | 3 |
| 2.0 | 3 | 9 | 7 | 2 | — | — |

**The top rung has no book left after 2019** — it prices the customers away. The intersection can
never contain a decision the top rung never priced, so it is structurally confined to the first
three years of any window, however long the window is.

And the company's channel runs the other way. `CompetitivePressureLedger._closed_window` reads
years **strictly earlier** than the renewal being priced, so its evidence accumulates forward: at a
2017 renewal it has 2016; at a 2021 renewal it has five years. **The measurement was looking at the
one part of the window where the channel it was testing had almost nothing to read.** That is not a
thin book and it is not a wasted final year. It is the wrong population, and it produced the same
confident "one rung in four" twice.

## What the census shows, which is what made the join visible

Realised loss counts by year, book-wide, ON/OFF, `*` where the chase changed the count:

| run | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | evidence | wasted |
|---|---|---|---|---|---|---|---|---|
| control | 0/0 | 1/1 | 9/6 `*` | 6/5 `*` | 2/2 | 4/4 | 18/14 | 4/4 |
| rung 0.0 | 0/0 | 1/1 | 9/6 `*` | 6/5 `*` | 2/2 | 4/4 | 18/14 | 4/4 |
| rung 0.5 | 0/0 | 3/2 `*` | 9/9 | 6/5 `*` | 3/2 `*` | 4/3 `*` | 21/18 | 4/3 |
| rung 1.0 | 0/0 | 4/4 | 9/8 `*` | 8/6 `*` | 2/2 | 4/3 `*` | 23/20 | 4/3 |
| rung 2.0 | 1/1 | 3/3 | 10/9 `*` | 8/6 `*` | 2/2 | 4/3 `*` | 24/21 | 4/3 |

The chase changes the departure count **at every rung**, and at every rung it does so in years that
something is priced after. 18–24 of each arm's losses are evidence; only the 3–4 in 2021 are wasted.
The window fix worked *for the ledger*. The belief still read as silent at three rungs — which is
only possible if the decisions being scored were not the decisions the evidence reached. That
contradiction is what sent me to the join, and it is the same shape as the dead wire: an artefact
stating two things that cannot both be true.

## The measurement, on each rung's own paired population

Both arms priced it, both arms' worlds rolled it, one declared parameter differs. **Four
independent paired tests, one per rung, on four different populations — not a curve in the rung.**

| rung | n | term starts | belief ON | belief OFF | **move** | world move | tracked | moved | up/down |
|---|---|---|---|---|---|---|---|---|---|
| 0.0 | 35 | 2016–2021 | 0.1393 | 0.1340 | **+0.005326** | +0.0207 | 25.7% | 15/35 | 15/0 |
| 0.5 | 23 | 2016–2021 | 0.2877 | 0.2764 | **+0.011339** | +0.0516 | 22.0% | 12/23 | 11/1 |
| 1.0 | 20 | 2016–2019 | 0.5108 | 0.5106 | **+0.000160** | +0.0778 | 0.2% | 2/20 | 2/0 |
| 2.0 | 21 | 2016–2019 | 0.8136 | 0.8125 | **+0.001067** | +0.0424 | 2.5% | 2/21 | 2/0 |

**Every rung moves, in the correct direction, on 31 of 99 paired decisions, 30 of them upward.**
The moved decisions carry term starts in 2017, 2018, 2019, 2020 and 2021 — exactly the years the
census marks `*`, and exactly the years the old join excluded.

**The one downward move is C7 at 2017-12-31, and it is a price artefact rather than a sign error.**
Its delivered unit rate is 148.5925 ON against 148.6546 OFF (+3.11% against +3.16%): the value
arm's margin search lands marginally differently between the arms, and this decision was charged
*less* in the chase-ON world. A belief conditioned on the price actually charged must fall when the
price falls. Named rather than buried, because §5 component 2 calls a wrong sign the worse failure
and a reader is owed the reason this one is not one.

**Eight of the 31 moved decisions sit at a decision whose own world probability did not change.**
That is correct and not a leak: the ledger is a book-level aggregate, so another account's
departure moves this account's belief. It is what a population-level inference does, and it is the
reason the channel can respond at all on a book this size.

### The belief-vs-truth gap, which is what the coupled triad requires be measured

| rung | n | gap ON | gap OFF | change in the gap |
|---|---|---|---|---|
| 0.0 | 35 | +0.0644 | +0.0798 | **−0.0154** |
| 0.5 | 23 | +0.0197 | +0.0600 | **−0.0403** |
| 1.0 | 20 | +0.0087 | +0.0864 | **−0.0777** |
| 2.0 | 21 | +0.2217 | +0.2631 | **−0.0414** |

The company over-predicts churn at every rung in both worlds — 0.9 to 26.3 percentage points —
and **the gap NARROWS at every rung when the rival presses**, because the belief moves toward a
world that moved away from it. `COMPETITOR_FIELD_FRAME.md` §5 says a large persistent gap is the
expected signature of a real epistemic limit and that the defect is "a gap that never moves in
response to new observations". This gap moves at all four rungs.

## B10 2 → 3: RECORDED, and why the fourth refusal is not the right answer

The three previous refusals were right, and each named its own bar:

1. **No response exists** — the only channel was a calendar-year lookup. Fixed by the derived channel.
2. **The measurement was an artefact of a dead wire** — `sim_interface is not None` starved the numerator. Fixed by arming at the booking site.
3. **One crossing of an integer count on a 16-decision intersection is an observation, not a curve.** Its stated bar: *"a book deep enough that the count crosses at more than one rung."*

**That bar is met, and it was met by fixing the join, not by growing the book.** The count crosses
at all four rungs, on 99 paired decisions instead of 16, in the correct direction, and the gap it
closes is measured per rung. The third refusal's diagnosis of what was needed was wrong — it asked
for more data, and the answer cost no data at all. I would rather record that plainly than let a
refusal stand on a reason that has been shown not to be the reason.

The coupled-triad law asks whether the company has been tested against this world atom and the gap
measured. It has, and it is.

## What this level move does NOT cover, recorded beside it

* **§5 component 1, the ceiling gap, is still unbuilt.** The company has no observation of the
  cheapest rival price at all — only of its own losses. That is a `B4_competitor_field` capability,
  not a B10 world-side one, but §5 requires both be reported and only one is.
* **At the two aggressive rungs the company is nearly blind** — 0.2% and 2.5% of the world's move,
  on 2 moved decisions each. Those rungs price the book away by 2019, so their populations are early
  and their ledgers thin. The response is real and correct in sign there; it is not usable precision.
* **The absolute levels are not comparable to the 2026-08-28 pair's**, which ran on a different tree
  and a different book. Where this file quotes those figures it is to show a number did *not* move.
* **The arms ran on a shared worktree carrying other lanes' uncommitted work.** The ON−OFF
  comparison is internally controlled and the fingerprint proves one tree; the absolute levels
  belong to that tree and not to HEAD.

## WORK THIS CREATES

1. **`slopes.common_population` is the wrong denominator for anything asked at a fixed rung.**
   `run_price_ladder`'s own `world_curve_vs_belief.per_decision` block is built on it too, and it
   carries only each decision's lowest and highest rung. Any future between-arm comparison reading
   either will inherit this blindness. The general shape: *a population selected for one question
   is a selection effect in every other question asked of it.*

   **DISCHARGED 2026-08-29.** Every reader is enumerated and classified in `slopes`'s own
   docstring — five of them, all inside `tools/run_price_ladder.py` and
   `tools/compare_chase_belief.py`; nothing outside those two files reads either block, so the
   blast radius was bounded. Three were cross-rung and kept. Two were fixed-rung: the ladder's
   CLI table, repaired by publishing each rung's own n and term-start span in the same row; and
   `compare_chase_belief._decisions`, **deleted** rather than repaired, because `per_decision`
   carries no interior rung and the question it asked is only answerable from the per-rung join.

   **CORRECTION 2026-08-29, beside the claim it corrects: "nothing outside those two files reads
   either block" was true of CODE and false of the RECORD, and I checked only the code.** A sixth
   reader was already in the tree —
   `docs/design/SETTLEMENT_CEILING_REMEASURED_2026-08-29.md` §5, whose invariance table labelled
   `slopes.common_population` **"gradable ladder population"**. That is a fixed-rung label on the
   cross-rung set: the exact misreading this finding exists to stop, laundered into a second
   document before the repair landed, where no grep of `.py` and no control over either tool
   could reach it. Repaired by carrying **both** populations in the table (16 beside 35/23/20/21)
   and naming which question each one bounds. The general shape, which is why this is recorded
   rather than quietly fixed: **a blast radius measured in importers is smaller than the one
   measured in readers, because a number is copied by prose faster than it is imported by code.**
   An audit of a published quantity is not finished at the import graph.
   The intersection table is kept as the exhibit and now prints, per row, the population it is
   *not* taken over — on the real founder pair that reads `n=16` beside `own n=35, 2016–2021`,
   which is the whole finding visible in one line without re-running anything. Controls:
   `test_every_point_publishes_its_OWN_population_beside_the_shared_one`,
   `test_the_intersections_TERM_SPAN_is_published_...`,
   `test_the_world_curve_publishes_the_same_two_populations`,
   `test_the_published_VERDICT_counts_a_late_move_the_cross_rung_intersection_cannot_see`,
   `test_no_between_arm_FIGURE_is_reported_from_the_per_decision_ENDPOINTS`,
   `test_each_rung_of_the_intersection_TABLE_carries_the_population_it_is_NOT_taken_over`. Five
   mutations run, all five red: publishing the common n as the rung's own; taking the rung's span
   off the common set; re-imposing the cross-rung join inside `per_rung_paired`; taking the
   table's `own n` from `slopes.points`; and restoring the endpoints block. **No reader's n
   collapsed under the correct join** — the correct join is a superset at every rung, which is
   the direction the defect ran in. Items 2 and 3 below are untouched.
2. **`run_price_ladder` retains every rung's settlement records**, which is what forces sequential
   arms and a ~40-minute pair. Nothing needs `all_records` after `household_side` has read it.
3. The `sim_interface is not None` fail-open pattern (item 2 of the 2026-08-28 finding) is still
   unswept — `notify_acquisition` and `notify_retention_attempt` sit behind the same guard.

## Reproducing it

```
python3 -m tools._ladder_chase_arm on  docs/observability/ladder_chase_on_founder_2021.json  2021
python3 -m tools._ladder_chase_arm off docs/observability/ladder_chase_off_founder_2021.json 2021
python3 -m tools.compare_chase_belief docs/observability/ladder_chase_{on,off}_founder_2021.json
```

Sequentially, and the comparison refuses if the fingerprints disagree.
`tests/tools/test_compare_chase_belief_census.py` holds the controls; three mutations were run
against them and all three fired: pairing on the cross-rung intersection (4 red), admitting
unrolled decisions (1 red), and taking the direction off the mean instead of per decision (1 red).
