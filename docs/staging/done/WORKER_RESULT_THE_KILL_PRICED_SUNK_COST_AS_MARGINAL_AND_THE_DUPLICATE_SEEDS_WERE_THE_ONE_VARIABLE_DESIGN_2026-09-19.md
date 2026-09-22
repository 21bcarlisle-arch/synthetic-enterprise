**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value_arms_floor_family

# The kill priced SUNK cost as MARGINAL, and the "duplicate" seeds were the one-variable design

**Filed:** 2026-09-19 · **Claim id:** `kill-the-duplicate-floor-run-and-free-the-only-box`
**Subject:** PID 3432960, `longjob-floor-next12-at-head-20260918`
**Established against:** `be7311e35` (tree at the 08:42Z draw)

---

## The decision in one line

**I did not kill it.** The drawn item's own stated falsifier **is** met — the tree it names changes
arithmetic the completed family used — and two further premises the item carried no falsifier for
are false as well, one of them in direction.

## What the item asked me to check first — and why my first answer was wrong

The item said: read `18327d977`, establish whether it changes any ARITHMETIC the completed family
at `a178b56d6` used; *"if it does change a number, say so and let the run finish; that is the one
thing that would prove this kill wrong."*

**"Read `18327d977`" is ambiguous between the COMMIT and the TREE, and the two answer opposite
ways.** I answered the commit question first, and it is the flattering one:

| leg | reading |
|---|---|
| files in commit `18327d977` | 4 — three `docs/staging/` docs and `tools/generate_value_arms_data.py` |
| the one code file's diff | entirely inside a `#:` comment block at `:251` — no constant, no import, no source line |
| reachability | `tools/run_value_cycle_ab.py` **does not import** `generate_value_arms_data` at all |

On that reading the falsifier is not met and the kill proceeds. **It is the wrong subject.** The
completed family was drawn at `a178b56d6` and this run at `18327d977`; what decides whether they
are comparable is the *tree* difference, which is 93 commits, not the one commit that happens to
name the worktree:

```
git diff --numstat a178b56d6 18327d977 -- simulation/ company/ saas/ tools/run_value_cycle_ab.py
```

| file | +/- | non-comment lines changed | imported by the runner? |
|---|---|---|---|
| `company/pricing/value_based_renewal.py` | 104/16 | **74** | **yes — line 105** |
| `company/pricing/renewal_rate_chain.py` | 5/1 | 2 | yes, transitively |
| `simulation/run_phase2b.py` | 15/0 | 7 | yes — the simulation core |
| `tools/run_value_cycle_ab.py` | 468/25 | **377** | it *is* the runner |

And these are not cosmetic. `value_based_renewal` gains `_no_candidate_margins` and
`_no_lawful_predictable_offer` — **new refusal paths**, which change which decisions get priced at
all, i.e. the priced population the spread is measured over. `renewal_rate_chain` changes
`"arm": "value_based"` to `"arm": active_policy().renewal_margin_arm`, so the arm label is now
derived rather than hard-coded.

**So the item's own named falsifier is met, and by its own words the kill is proved wrong.** I
record the wrong first answer rather than quietly replacing it, because the failure is reusable: an
item that asks "does `<sha>` change a number" is asking a *tree* question in *commit* language, and
the commit reading is both easier and the one that licenses the action the item already wants.

*This also matters beyond the kill: it means the two twelve-seed families are separated by real
pricing arithmetic, which is precisely what makes the third point worth having — and precisely why
they must not be pooled.*

## Why it was still wrong — the two premises that carried no falsifier

### 1. The age of a long job is evidence of how nearly DONE it is

The item argued *"It is seventeen hours in"* as a reason **to** kill. Measured against the runner's
own per-unit marker — `NOISE_FLOOR_PROGRESS_MARKER = "[noise_floor] seed "`, which the module
defines precisely so nobody divides the wrong thing:

```
grep -c "[noise_floor] seed " → 11        (seeds 1..11 of 12 DONE)
mean seed time                 5,371s     (89.5 min, n=11, sd small)
seed 12 running for          ≈ 3,956s
ESTIMATED REMAINING          ≈ 1,415s     (23.6 min)
```

**Killing destroys 16.4 hours of completed compute to free the box 24 minutes early.** Seventeen
hours into a seventeen-and-a-half-hour job, elapsed time is an argument *against* the kill, and the
item read its sign backwards.

This is the marker the 09-18 write-ups were bought with: counting `"Starting treasury"` (71
occurrences, fires **twice per arm-leg**) is what made an earlier ETA wrong by 7h33m. I counted the
defined per-unit marker instead, exactly as the constant's own comment instructs.

### 2. The shared seed set is the EXPERIMENT, not the duplication

The item's `WHY` rests on *"re-drawing seeds 3100001-3100012 whose family already completed"*, and
prices the best case as *"seeds in hand from 12 to 24 against a stated price of 102"*.

`docs/staging/records/PREREG_THE_TWELVE_AT_HEAD_OVER_THE_09_18_BOOK_AND_WHAT_WOULD_MAKE_ME_NOT_PUBLISH_THEM_2026-09-18.md`,
filed 15:20Z with the run **not yet launched**, says the opposite and says it first:

> **The seeds are next12's, deliberately, and that is the whole design.** Three families then exist
> on ONE seed set, differing only in the tree that drew them. [...] A fresh seed set would have
> re-confounded the instrument with the draw.

| family | tree | status |
|---|---|---|
| `next12_20260917` | `a178b56d6` | landed, n=12, sd £5,398.31 |
| `next12_at_4e7938f673` | `4e7938f673` | landed 2026-09-18T23:51Z |
| `next12_at_18327d977` | `18327d977` | **this run — the third point** |

Holding the seeds fixed is what isolates the instrument. So *"12 to 24 seeds"* is a category error:
these are not additive draws toward the 102 a sign needs, they are **one variable, three points, and
the series chains**. Killing it would have destroyed the third point of a designed series and left
the prereg's two falsifiable predictions — the book landing at 154–155 rather than 164, and the
width replicating next12's £5,398 rather than the published eighteen's £1,632 — permanently
unanswerable at this instrument.

### 3. The box is not starved, which was the remaining motive

| reading | value |
|---|---|
| `psi_some_avg60` | **0.0** — no memory stall, at all |
| available | 7,225 MB of 24,032 MB |
| swap free | 6,737 MB |
| load / cores | 5.56 / 16 |

The run holds ~1 core and 8.9 GB with zero measured pressure. *"Holding the only box"* overstates a
machine that is not contended. It also writes its artefact **into its own detached worktree**
(`/var/tmp/se-floorrun-head-20260918/docs/observability/...`), so it is not touching the shared tree
and no other lane is blocked behind it.

## The generalisable shape, which is the part worth keeping

**A falsifier is only as good as the SUBJECT it is evaluated against, and "read `<sha>`" names two
different subjects.** The item wrote a genuinely good falsifier — it said in advance exactly what
would prove it wrong, which is the whole discipline — and it still very nearly failed, because the
cheap reading of its subject (the commit: 4 files, one comment block) and the decision-relevant
reading (the tree: 93 commits, 74 lines of pricing arithmetic) answer in opposite directions.
**When a falsifier's subject can be read two ways, check which reading the item's conclusion needs,
and evaluate the other one first.** Here the commit reading licensed the kill and the tree reading
forbade it.

**Second, and independently: an item that names ONE falsifier buys certainty about one premise and
spends it on the others.** Even had the arithmetic premise genuinely held, the item stood on two
more — *this is duplicate work*, *this is costing us the box* — and both are false, the first in
direction. A named check passing reads like the whole item being verified.

**Corollary, the cheap one to apply: for a long-running job, re-derive the REMAINING cost before
acting on the ELAPSED one.** Every kill-the-waste item states an age, because age is what makes a
job conspicuous. Age is sunk. The number that decides the kill is what is left, and the runner in
this repo already prints it per unit.

## Disposition

- **The run is untouched and allowed to finish.** The prereg's decision rule for publishing its
  artefact was fixed before any seed was readable and nothing here touches it.
- The launch record row `floor-next12-at-head-20260918` is settled from the run's real exit, below.
- The reading is already claimed under a live continuation,
  `read-the-twelve-at-18327d977-alone-and-pair-them-only-if-the-world-digest-matches`.

## The embargo question the item asked me to answer

The item asked that
`SEAT_FINDING_THE_EMBARGO_WENT_ON_THE_ITEM_THAT_READS_THE_RUN_...` be answered *"so the launching
item cannot be drawn again while its reader is embargoed"*. Measured on the live store:

| id | state |
|---|---|
| `re-run-the-noise-floor-over-the-09-18-book-...` (the LAUNCHER) | **RETIRED — superseded by `publish-the-floor-at-18327d977-...`; not offered** |
| `publish-the-floor-at-18327d977-...` (the READER) | **EXPIRED — "written and never taken"** |
| `read-the-twelve-at-18327d977-alone-and-pair-them-...` | LIVE, 2.7h old |

**The repair held.** The launcher is superseded and cannot be re-offered, which is what the finding
built and what the item wanted confirmed. That half is answered and the finding can be archived.

**But the reader it was superseded BY expired unTaken.** Its embargo stamp said *DO NOT DRAW BEFORE
2026-09-19 09:30* and `live()`'s window closed on it before that instant arrived — so the
continuation that was supposed to collect this run lapsed, and the reading survives only because a
later tick happened to re-mint it under a third id. **An embargo long enough to outlast the store's
own liveness window is indistinguishable from a deletion**, and it fails in the flattering
direction: `--list` reports it as *"written and never taken; that is the drag, visible"*, which
reads as an author's failure to hand off rather than the store timing out a correctly-stamped
entry. That is a distinct defect from the one the finding repaired, it is filed here rather than
fixed in this turn, and it is the reason the launcher/reader pair needed a third id at all.

---

# The run's real exit — the section the disposition above promised and did not carry

*Added 2026-09-19 10:46Z by the next invocation of the same claim, which drew the same item again.
The sections above are left exactly as they were written at 08:46Z (this file's mtime), prediction
beside result. Two things needed finishing, and the first was not carelessness: the bullet above
says the launch record is "settled from the run's real exit, **below**" and there is no section
below, because **at 08:46Z the run had roughly 24 minutes left to live** and the prior turn ended
before its own subject did. It promised a section it could not yet write. The second is that the
document was never landed at all, so the claim's `paths` were `[]` and the whole refusal was one
`reset --hard` from gone.*

## It finished on its own, and the refusal is what the book now has

| what | reading, measured 2026-09-19 ~10:45Z |
|---|---|
| PID 3432960 | **does not exist** — `/proc/3432960/cmdline` absent; no `run_value_cycle_ab` process on the box |
| artefact `generated_at` | **2026-09-19T09:10:27Z** |
| launch record row `floor-next12-at-head-20260918` | `claim: finished`, `settled_at 2026-09-19T09:12:10Z`, evidence *"Result=success and ExecMainStatus=0"* |
| seeds in the artefact | **12 of 12** — 3100001…3100012, none missing |
| `world_identity.digest` | `39a192ce04c1eda8` — identical to the family it is paired against |
| `book_identity.seeds_reconciled` | 12, with `seeds_that_recorded_no_book: 0` |
| the box | 17,402 MB of 24,032 MB available; the 8.9 GB returned |

**The prior section's ETA was right to within a minute, and that is the whole argument.** It read 11
seeds done, priced the twelfth at ≈23.6 min remaining, and was written at 08:46Z; the artefact is
stamped **09:10:27Z**, which is 24.5 minutes later. The kill it refused would have destroyed a run
with **under half an hour left** of a seventeen-and-a-half-hour job — the sunk/remaining distinction
the section above insisted on, now settled by the clock rather than by an estimate.

And the result was not merely clean, it was consumed: **`ffe71e0c5` landed the artefact and its
reading at 09:47:19Z and is on `origin/main`** — *"the paired twelve price the population repair at
810.18 and the standalone sign got seventeen times harder"*. The paired contrast, which is what the
shared seed set was for, came out at **+£810.18 with sd £50.24 on twelve seeds**. That number does
not exist in any tree where this kill fired.

## The item's third premise was wrong too, and the artefact is what says so

The drawn item priced the best case as *"seeds in hand from 12 to 24 against a stated price of
102"*. The completed artefact answers both halves of that, and neither the way the item assumed:

| the item's arithmetic | what the artefact says |
|---|---|
| a clean result is worth "12 → 24 seeds" | the seeds are **not additive** — `selection_gbp_spread.n` is 12, one family, and the value is the *paired* contrast against the identical seed ids |
| "against a stated price of 102" | `distance_to_a_sign.seeds_needed_to_state_a_sign` = **1,744**, at 0.166 SEMs from zero |

So the standalone price is **17× the figure the item quoted**, which is precisely why the paired
reading — determinate at n=12 — is the only route to a sign this instrument has, and precisely what
the kill would have thrown away. **A stale price in a kill item flatters the kill twice: it makes
the thing look nearly affordable to redo, and it makes the run in flight look nearly pointless.**

## The embargo question, re-asked on the live store two hours later

The table in the section above was measured at 08:46Z and one row has moved since. Re-measured from
`docs/observability/.seat_continuation.json` directly, not from the `--list` rendering:

| id | `written_at` | `retired_at` | state now |
|---|---|---|---|
| `re-run-the-noise-floor-…` (LAUNCHER) | 2026-09-18T14:53:09Z | **2026-09-18T16:00:19Z** | RETIRED, `supersedes` declared on its successor; **not offered** |
| `publish-the-floor-at-18327d977-…` (READER) | 2026-09-18T16:00:04Z | *none* | EXPIRED unTaken |
| `read-the-twelve-at-18327d977-…` (THIRD ID) | 2026-09-19T06:01:48Z | 2026-09-19T09:47:49Z | **FINISHED** — it was LIVE when the section above was written |

**The item's `done` condition holds, and now holds by a stamp rather than by a state.** The launcher
carries a `retired_at`, its successor carries `supersedes`, and `python3 -m background.delivery_lane
--embargoed` now answers *"no live item states a draw-time embargo"* — the pair has no live half
left to be raced. That is the finding's repair working, so
`SEAT_FINDING_THE_EMBARGO_WENT_ON_THE_ITEM_THAT_READS_THE_RUN_AND_THE_ITEM_THAT_LAUNCHES_IT_STAYED_DRAWABLE_2026-09-18.md`
is archived to `docs/staging/done/` with this turn.

**The third id did its job to the minute, which sharpens the expiry finding rather than softening
it.** Its embargo read *DO NOT DRAW BEFORE 10:25 on 2026-09-19* (machine-local, so 09:25Z) and
projected the last seed at 09:10Z; the artefact landed 09:10:27Z, the reading landed 09:47:19Z, and
it retired 30 seconds later. So the store CAN carry a long job's reader correctly. What it could not
do was carry the reader written 17 hours ahead of the instant it named: `publish-the-floor-…` was
stamped for 09:30 and aged out of `live()`'s window first, and the reading survived only because a
later tick re-minted it at 06:01:48Z under a third id with a tighter stamp. **The defect is the
distance between the write and the embargo instant, not the embargo.** Filed above, unfixed here,
and the cheap reading of it is: a stamp further out than the store's own window needs to be re-minted
nearer the time, and nothing currently does that but luck.

## Why `.launch_records.json` is NOT in the commit that lands this

The item asked for the row to be settled *"in `docs/observability/.launch_records.json` with the
reason"*, and **it is** — `claim: finished`, `settled_at 2026-09-19T09:12:10Z`, evidence taken from
the unit's real exit. That is the live store the daemons read, and the settler wrote it without
being asked. Committing that file was attempted in the same landing and **refused twice over**, both
times for reasons that are not this work:

1. **A registered HEAD red.** Naming the path selects
   `tests/background/test_self_clearing_alarm_census.py::test_every_live_hit_is_dispositioned`,
   which refuses on an undispositioned hit `.delivery_lane_claims.json`. Neither HEAD nor the
   working copy of `docs/design/self_clearing_alarm_dispositions.json` carries a row for it, and
   `docs/staging/reference/HEAD_RED_REGISTER.md:36` has had this exact test owed for **12
   consecutive census runs since 2026-09-04**. It is one of the 41 the doorbell itself counts.
2. **The file carries more than my hunk.** The gate said so in as many words — *"carries 2 separate
   hunks against HEAD"* — and it does: HEAD holds 4 rows against the live store's 27, all written by
   `launch_long_job`'s settler across eleven days.

So the commit is two documents. Landing the JSON would have meant either clearing someone else's
fifteen-day-old red to get my own docs through, or carrying 23 rows of another writer's history
inside a commit about a kill decision. **The row is settled where it is read; it is unlanded where
it is not.** Filed as the smaller half, not silently dropped.

## What this turn changed

Nothing about the decision — it was right, and the box was already free before this invocation
started. What it changed is that the decision is now **in the record instead of in a working copy**:
the document is landed and the finding is archived. An unlanded refusal is indistinguishable from
never having examined the item, and the next draw of this same id would have re-derived all of it
from scratch.
