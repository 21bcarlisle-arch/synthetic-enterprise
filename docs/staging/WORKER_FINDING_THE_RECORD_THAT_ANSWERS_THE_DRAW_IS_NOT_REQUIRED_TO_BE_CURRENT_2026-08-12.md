# WORKER FINDING — the record that answers the draw is not required to be current, and nothing asks

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-12, H27 Expert Hour #22 (worker tick, `H27_payment_belief_gap` 2→3 HARDEN draw)
**Class:** a hand-kept second copy of an answer the register already carries · **Disposition:** mechanism landed (atom D41)
**Answer to the draw:** still **L2**. Twenty-two Hours, twenty-two defects.
**Rank requested:** backlog. Nothing here is blocking.

## What the draw actually handed me

The self-refill drew this atom 2→3. The record whose whole job is to answer that question is
`level_hold_note`, and its closing sentence read:

> The next promoter runs Hour #19 on the corrected door; its leads are in
> `docs/staging/WORKER_FINDING_THE_DOORS_DEPTH_LIMIT_SWALLOWED_FIFTY_THREE_FIGURES_2026-08-11.md`

Hours #19, #20 and #21 had all already run, landed and recorded themselves
(`e72556e96`, `2b80066ac`, `a46e00cb9`). The promoter this tick was pointed at leads three Hours
discharged, by the one record built to prevent exactly that.

**This is the second recorded instance, not the first.** The same note carries Hour #16's write-up
of the same failure — one Hour behind, then — and describes it as *"the 2026-08-08 class inverted"*.
It was closed **by editing the note**: a prose fix for a prose defect. It recurred three times
larger. R3 applies: a second false record on the same component is a redesign, not a third patch.

## The measurement (observed-with-evidence)

Across the whole record store, not this atom alone — three atoms have run Expert Hours:

| atom | Hours recorded | latest Hour **answered** | lag |
|---|---|---|---|
| `W5_1_banking_payment_rails` | #2 | — (at target, no draw asks) | n/a |
| `H_GAP_fabric_belief_truth_gap` | #15 | #15 | **0** |
| `H27_payment_belief_gap` | #21 | #18 | **3** |

## The nearest working analogue is in this repo (R4)

`H_GAP` keeps **no separate hold note at all**. Each of its register entries carries its own
verdict — *"…AND IT FOUND SOMETHING, SO THE LEVEL STAYS 2"* — so the answer to the draw is written
by the one act an Hour cannot skip: recording itself. If the Hour exists, its verdict exists.

The diff is **where the verdict lives**. H27 keeps a second copy, by hand, and a second copy kept by
hand is the only shape that can fall behind.

So the invariant is not "keep the note fresh" (an exhortation, and this repo's own rule is that
exhortations evaporate) but: **the latest recorded Hour must be answered in a record the draw
reads.** Either shape satisfies it. Neither is mandated.

## What landed (atom D41)

`tools/map_assertion_provenance.py` — the module that already dates a cell's *level claim* against
its artefacts now carries a fourth clock, over the record that answers the *hold*:
`hour_ordinals` / `entry_hour` / `answered_hours` / `hold_record_findings` / `hold_record_atoms`,
plus `HOLD_STALE` and `HOLD_UNANSWERED`.

**The fail-open it is built against, pinned by name.** Every hold record here ends by naming the
*next* Hour, so the highest ordinal **mentioned** is current by construction, one step ahead of the
truth. At the one-Hour-behind instance — the real first occurrence — a mention check reads **green
on the defect it exists for**. Only ordinals in a sentence that *also states a hold verdict* count;
a forward pointer states none.

**The check's own first run committed the same defect on the other side.** It reported `H_GAP` as
one Hour behind, because that atom's fifteenth entry ends `OPENER FOR THE SIXTEENTH HOUR` — a
forward pointer on the *register* side, inflating the recorded count by one and reddening a
perfectly current atom. Fixed, not quietly corrected: an entry's Hour is now the **first** ordinal
it names (what the entry *is*, never what it refers to), and an entry that stops self-identifying
within 120 characters **raises** rather than guessing. Both directions are pinned by name.

**Population derived, not hand-typed** — every atom the store holds Hour entries for, which is the
construct lead `D40` is already open about.

## R15

Nine fixtures, written in the two conventions the two real registers actually use. Four mutations,
each firing a named finding: a note behind its register; a forward pointer accepted as an answer; a
register forward pointer inventing an Hour; Hours recorded with no verdict anywhere. Two refusals: a
drifted entry convention, and a register that parses to nothing — an unavailable check is a **failed**
check. One silence: an atom at its target is not asked why it is held. And the check is **wired into
the CLI**, with the stale finding proven to reach a non-zero exit and an unavailable check proven to
reach `COULD NOT RUN` — because D34's control was never wired into its own CLI and nobody noticed
for two Hours.

36 passed on the file (was 24). `ruff` clean on both files.

## R12

No published number moved. This Hour did not touch the instrument.

## Also fixed, and named because it was not mine

`SITE2_two_sided_wall_exhibit`'s `simplifications_count` said 1 against a store file of 2 — red at
`43a456cba`, before this Hour, from the SITE2 Expert Hour landing its register entry without its
count. One integer, corrected so HEAD is green; no judgement about that lane's work is implied.

## Queued, not fixed (SELF_INTERRUPT_DISCIPLINE)

**The same class is live on a second surface.** `D37`, `D38`, `D39` and `D40` exist **only** in this
register's prose and in no map cell, with `unfolded_inbox_ids()` empty — and Hour #21 describes `D37`
as *landed*. So the Hour's prose has outrun the map on four atoms. That is this Hour's own class
(a record outrunning the thing it records) on the mint surface rather than the hold surface, and
minting is a code change requiring per-atom scope judgement, so it is filed rather than swept in.

## Still L2

The honest reason is narrower than most Hours' and should be read as such: this Hour did not touch
the instrument, so nothing it did makes the five published figures better or worse. What it
establishes is that for three Hours the only record answering this draw was **wrong** — which is a
reason to distrust the promotion question, not the numbers. Hour #4's two-consecutive-clean-Hours
criterion is at zero.

## Leads for Hour #23 — the three Hour #21 left, untouched here

1. `D39_the_bar_is_a_scaled_render_no_sweep_can_express`
2. `D40_the_region_census_is_a_hand_typed_keyset`
3. Hour #20's `test_a_composer_that_stops_carrying_a_renderers_string_fires`, vacuous in isolation,
   proven pre-existing at `43a456cba`.

Plus the mint-surface gap above, if the next promoter would rather close this Hour's class than the
instrument's.
