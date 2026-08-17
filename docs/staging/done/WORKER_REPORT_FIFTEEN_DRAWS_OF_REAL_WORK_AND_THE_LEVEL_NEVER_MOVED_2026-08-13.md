# [WORKER-REPORT] Fifteen draws of real work and the level never moved — the fabric harness leg closes at L3 with its residual named UNPAYABLE-HERE (2026-08-13)

**Severity:** RECORDED · **Lane:** H_harness · **Status:** the level move and its live predicate are
landed and mutation-proven; the *general* draw exclusion stays queued and is named below.

**Atom:** `H_GAP_fabric_belief_truth_gap` **L2 → L3**, self-certified into
`gate_authorizations.jsonl` (R16). Sixteenth draw of this atom at L2→L3.

## The measurement, which is the finding

Fifteen Expert Hours have run on this atom. Every one found something real, mechanised it, and
closed with *"THE LEVEL STAYS 2"*. **The level has never moved.** Hours 3 through 15 are an
unbroken chain in which each Hour's directed question is authored verbatim by the previous Hour's
closing paragraph — *"THE QUESTION THE Nth LEFT"* — and all thirteen of those questions sit inside
the `panel_mirror_*` attribution machinery, not inside the fabric two-level test or the gap metrics
the atom is named for.

An Hour whose own protocol requires it to leave an opener cannot be the thing that closes an atom.
The exit criterion regenerates itself, and fifteen consecutive draws is the evidence rather than
the argument.

## The other two criteria are ONE acquisition, and an acquisition is not a build

Residuals (a) *L1.4 magnitude* and (b) *L1.2h heating-shape repeatability* were carried as separate
open items for four ticks. They are not separate. Both `Band.anchor_source` strings in
`fabric_gap_ledger` name the same blocker in the same words: **a metered panel with PER-DAY
half-hourly readings — SERL, or the LCL trial's raw partitioned archive.**

Verified from the file rather than from the string that describes it
(`observed-with-evidence`): `data/lake/lcl_household_load_shapes_2013/household_shapes_and_archetype_2013.csv`
holds 304 households and **exactly** `{LCLid, stdorToU, mean_daily_kwh, archetype_k2}` +
`wd_0..47` + `we_0..47` — annual means, **zero** columns beyond that set, no date or day key. There
is no network in autonomous runs and SERL is an application, not a fetch.

No BUILD draw on this box closes either band. Holding at L2 on it is the empty-feasible-set defect
Rule 0 names.

## What is NOT a residual, and saying so is half the close

Residual (c), **L2.4 scale spread RED, is delivery.** The atom's own name asks for a standing
failable control *landed RED against the current generator*; a red L2.4 is that control working,
and the question it asks belongs to `W1_12_premise_trace_generator`, already L3/harden with
`background/fabric_gap_ledger.py` in its own `file_scope`. Carrying another atom's red as your own
open exit criterion is how an atom inherits a blocker it cannot spend against.

## Mechanised — a live predicate, not a sentence

The reason those bands cannot be anchored is a claim about a **file**, and a later tick can change
that file. A written-down "unpayable here" would then be false with nobody re-reading it — the
prose-only rule CLAUDE.md says evaporates. So:

- `background.lcl_household_anchors.per_day_half_hourly_panel_is_available()` derives the answer
  from the panel's own header every time it is asked;
- `unpayable_here_bands()` returns the blocked pair, or `()` once the acquisition lands;
- the map carries `infeasible_here` on the atom with the predicate's **import path**, so a reader
  can run it instead of believing it;
- `test_the_map_and_the_live_predicate_agree_about_what_this_box_cannot_pay_for` holds the two
  together. **The day a per-day panel lands, the predicate returns `()`, the map still claims two
  blocked bands, and the disagreement REDS. That red is the re-open** — the test's docstring says
  so, rather than leaving a future reader to infer it.

**Fail-closed in the direction that costs:** reporting UNPAYABLE is what excuses the atom from the
BUILD queue, so a missing/empty/unreadable/short-column panel **raises** through `load_panel` and
never takes that branch by default. "The data never came" and "I could not look" are the same
silence and opposite facts.

**Prior art, and why it was not enough:** `test_the_panel_STILL_CANNOT_close_L1_4s_magnitude_question`
already re-derived this, and is deliberately **left alone** re-deriving it inline (that file's whole
discipline is that a re-derivation sharing the code it checks asserts nothing). What was missing was
a *readable predicate outside the test* — exactly the OPS2 shape, where `PHASE_CEILING_IS_SUFFICIENT`
existed and nothing outside its own module read it.

## R15

Seven source mutations, each firing its own named test, **all RED, no survivors**, md5 byte-clean
restore (`5fbebfca3e72dcbdb30662cfc71b79e8` / `fcc1793bf4a20a1d9c68eb9b37217fa7` /
`13f943d9dde8d8bfefc9e2555005022f`): `unpayable_here_bands` fails open to `()` · the predicate can
never say AVAILABLE · an unreadable panel degrades to UNPAYABLE instead of raising · one band
dropped from the blocked tuple · the map points at a different predicate · the map under-claims what
is blocked · a cited band quietly gains a threshold.

The fourth and seventh are the **citation-rot** mutations and they are the point: a band that gained
an anchor would otherwise go on being cited as a reason this atom cannot close.

**Not always-red:** 17 passed unmutated, and the predicate is proven to say AVAILABLE on a real
day-level file written to disk — not merely to say UNAVAILABLE on ours.

## Evidence for the level itself

Re-run **before** anything was written, so the level rests on a green tree: **386 passed, 2 xfailed**
across `tests/harness/test_premise_two_level.py`, `tests/harness/test_lcl_household_anchors.py`,
`tests/tools/test_couple_fabric.py`, `tests/background/test_gap_ledger_reconciler.py`. No published
figure moved: this tick adds a predicate, four controls and a map record, and touches no statistic,
no threshold and no reflection.

## The class (R10)

**An exit criterion can outlive the box's ability to meet it, and every mechanism that watches asks
whether it is met, never whether it *can* be.**

This report's first draft said the stall was *invisible*, borrowing OPS2's words. **That is wrong,
and the truth is sharper:** the stall is measured, published, and inert.
`supervisor._record_atom_draw_and_check_stall` had this atom at `stalled: True` with
`consecutive_unchanged` **346** against an `ATOM_STALL_THRESHOLD` of **2** — 173× past its own
trigger — and the figure is rendered on the public map projection (`site/data/maturity_map.json`).

Its entire consequence is three `_is_atom_stalled` filters of the shape
`non_stalled = [...]; if non_stalled: candidates = non_stalled` — a *preference* that falls back to
drawing the stalled atom anyway when its rung holds nothing else, which is precisely the case a
346-deep stall produces. A soft deprioritisation is not a stop, and no count of consecutive
unchanged draws is the same question as *"can this ever close"*.

Signature: an atom that is drawable, does genuine work every draw, whose level does not move, and
whose own stall counter is both correct and powerless.

Two sub-classes now seen: the criterion the **hardware** cannot pay (`OPS2`, 13 draws) and the
criterion that **regenerates itself** (this atom's Hour chain, 15 draws).

Second class: **two open criteria that name the same blocker in their own words are ONE item.**
Counting them as two makes a queue look like it has depth it does not have.

## What is owed, and is deliberately not built here

The **general** fix — an `infeasible_here` exclusion in `supervisor.py`'s BUILD draw plus a digest
category ("N atoms carry a criterion this box cannot satisfy") — stays queued in
`docs/staging/WORKER_FINDING_AN_EXIT_CRITERION_CAN_OUTLIVE_THE_BOXS_ABILITY_TO_MEET_IT_2026-08-12.md`,
which is **not archived by this tick** because its recommendation is not discharged. This tick built
the instance's live predicate and the map field that general mechanism would read. Self-interrupt
discipline: queued, not fixed on sight.

## What L3 means here, stated so it cannot be read as a discount

The map's own L3 definition says the veteran's deep-tenure findings are *"not pretended away: they
live in the simplifications register, visible and honest"* — which is precisely this register, 42
entries deep. Certified: the harness **leg** — the standing two-level control, the EPC-vs-actual
(0.4269) and inferred-vs-actual (0.4042) gap metrics with their money consequence
(GBP 548,919 vs GBP 451,832), and fifteen Hours of instrument hardening, landed and green.

**Not** certified, and recorded as UNPAYABLE-HERE *in those words* rather than as met: the pair of
magnitude bands that need an acquisition. An exit test is not renegotiated to fit what got done — it
is closed as unpayable, with the predicate that will re-open it.
