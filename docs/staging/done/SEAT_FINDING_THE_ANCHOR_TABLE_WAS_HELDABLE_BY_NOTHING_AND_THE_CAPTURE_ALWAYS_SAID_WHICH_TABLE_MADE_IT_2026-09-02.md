**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# A 2x error in every anchor value was still invisible after five new legs — and the capture had been naming its own producer the whole time

**Class:** `controls_that_cannot_fail` (existing; this instance is born archived). Second class named
in the body: `figures_on_a_superseded_clock`.

**Found and closed 2026-09-02, delivery seat, isolated worktree at HEAD `4013b1de1`.**
Pre-registration, filed before any measurement and graded beside its own text:
`docs/staging/SEAT_PREREGISTRATION_WHETHER_THE_ANCHOR_CAN_BE_HELD_WITHOUT_A_RECAPTURE_2026-09-02.md`.

## The drawn item was already discharged, so this is what the stretch found instead

Verified this tick, not assumed, and none of it re-derived here: the level-anchor collision is
answered as a PARTITION at `d374b1977`, the unlanded block document is committed at `9238075d9`,
`tools/population_anchor.py`'s 2022 reads fail closed with named causes, the register is corrected,
and `6fc06b535` established the 2022 slot is inert. `git status --porcelain
simulation/departure_level_anchor.py` is empty and `HEAD...origin/main` is `0 0`. **The direction's
description of the tree — a ` M` on the anchor module, a live `.get("sim_churn_rate", 0.0)` — is
stale in both particulars.**

What was NOT discharged is the sentence underneath all of it: *whatever you decide is unverifiable
until the anchor has a control that can move against it.*

## The finding

`4871e53ee` measured on 2026-09-01 that halving every `YEAR_LEVEL_ANCHOR` entry leaves the whole
control file green. Every document in this thread has cited that since. **Nobody re-measured it after
`d374b1977` added five legs.** Re-measured here on a clean `git archive HEAD` stem:

```
unmutated            81 passed, 2 xfailed
all 7 entries / 2    81 passed, 2 xfailed     ← byte-identical
```

**A 2x error in every value of the table — larger than the 1.98x fallback that started this entire
thread — was invisible to all three control files.** Five legs were added on top of a table nothing
could hold, and the fact that the hole was still open was true by luck rather than by check: it had
been asserted from a reading taken before those legs existed.

## The thing that had been sitting in the artefact all along

The documented cause is right and is not disputed: the band leg's subject is the STORED capture
`docs/reports/c2_departure_factors.json`, so `simulation/departure_level_anchor.py` is not in its
read path, and the anchor reaches its only accountability route through a re-capture. Three
documents state this correctly.

**What none of them noticed is that a capture recording the anchor it ran under is not opaque about
it.** Every row carries `sim_level_anchor` — the value the accessor returned during the run that
produced the row. The capture has been stating which table made it since it was written. That makes
one property checkable with no re-capture and no re-fit:

> The band verdict cannot be attributed to the live table unless the live table is the one that
> produced the capture it is read from.

Measured across all nine years the capture carries, they agree exactly (1e-6) — fitted and
declared-unfitted alike. So the property holds today, and a control keyed to it is green now and red
on the first un-recaptured edit.

`test_the_capture_the_band_verdict_is_read_from_was_produced_by_the_live_anchor` is that control.
It compares against `year_level_anchor` — the accessor the world calls on its hot path — not against
the table, so it covers the fitted seven, the declared-unfitted years, and any future change to the
PARTITION itself in one statement.

**Mutation-proven under `python3 -B`, from both sides:** halving fires (the case the file was blind
to); moving 2024 from `YEAR_LEVEL_ANCHOR` into `UNFITTED_YEARS` fires; editing ONE capture row's
`sim_level_anchor` fires, reporting *"the capture records 2 different anchors for 2020"*; unmutated
is green before and after, so the pass branch is reachable and this is not a constant verdict.

## Why this is not the re-keying the anchor's markers forbid

Both xfail markers say, in their own words, *never re-key this to today's readings*. This control
pins no anchor to a number and is not a reading of the band at all. A re-fit that lands a new block
**and** the re-capture it was fitted on moves both sides together and passes. An edit to the table
alone fails — and that failing state is precisely the one in which the band leg's verdict is being
read off a run some other table produced. That is `figures_on_a_superseded_clock`, the class this
same file has already produced twice: the retired ten-year block's citation resolved, at HEAD, to a
capture its own successor produced, under a stable path over a moving run.

The diff is **102 insertions and 0 deletions**. No marker, band or existing assertion was altered.

## What this does NOT do, stated so no reader infers coverage it lacks

It does not judge the anchor's value. The band leg still does and is still `xfail(strict)`, with the
world out of band in 7 of 7 readable years. **The anchor is still band-held in no year.** What
changed is that it is no longer unheld *entirely*: an edit that is not followed by a re-capture can
no longer pass silently. The `_HELD_INDIRECTLY` register is corrected to say exactly this — that
defeat (ii) has a partial remedy and defeat (i) does not — rather than being allowed to read as
though the anchor is now held.

**2022 is absent from the capture entirely** (9 of 10 record years present), so this leg does not
hold it and cannot. That is the mechanism reason `6fc06b535` established, not a gap to close: the
year is 100% crisis-forced-passive, C1b routes every roll to the SVT table, and the slot is inert.
The control's docstring names its own 2022 blindness for the same reason this section exists.

## The transferable shape

**A control that cannot reach its subject may still be able to reach the subject's fingerprint.**
The correct and repeatedly-stated conclusion here was *"the module is not in the read path, so the
anchor is only checkable through a re-capture"* — and it stopped one step short, because the stored
artefact records the identity of the code that produced it. When a control is blocked by an
indirection, ask what the far side of the indirection already writes down about the near side before
concluding the near side is unholdable.

**And: a measurement that a hole is open goes stale exactly like a measurement that it is closed.**
This one was re-cited for a day across three documents while five legs landed that could have closed
it. Re-running it cost five seconds.
