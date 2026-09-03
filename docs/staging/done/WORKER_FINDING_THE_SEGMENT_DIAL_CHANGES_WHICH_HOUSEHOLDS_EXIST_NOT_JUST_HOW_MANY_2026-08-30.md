**Severity:** BLOCKING · **Status:** DISCHARGED 2026-08-30 (see the discharge at the foot of this
file) · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`PB4_engagement_separated_from_elasticity`

# Suspending a business segment changes WHICH households exist, not just how many — so no A/B across that dial is attributable

**Found:** 2026-08-30, dispositioning the HEAD red census. Filed BLOCKING rather than LATENT
because it is a confound in a curriculum dial: any measurement taken across `SE_SERVED_SEGMENTS`
compares two different populations and cannot be attributed to the dial.

**No published figure is known to be wrong.** The live book runs with all segments served, so the
confound has not been exercised by a published run. It is the measurement that is unsafe, not the
current number.

> **WRONG, corrected at discharge (2026-08-30) and left standing beside the claim.** The live book
> does **not** serve all segments: `docs/design/curriculum/served_segments.json` has served
> `["resi", "SME"]` since 2026-08-26. The confound *has* been exercised by every published run
> since. No published figure was wrong for the book it was measured on, but the composition of that
> book was a function of the dial, and repairing it moves the live book by 4 accounts and 150 of
> its 238 households. Numbers in the discharge at the foot of this file.

## Reproduced directly, same function, same seed

```
SE_SERVED_SEGMENTS="resi,SME,I&C"  ->  {resi: 238, SME: 9, I&C: 11}   n = 258
SE_SERVED_SEGMENTS="resi"          ->  {resi: 257}                     n = 257
```

The residential count moves from **238 to 257** when the business segments are suspended. If the
dial were a filter, suspending a segment could not add nineteen households.

And the sets are not nested in either direction:

```
resi accounts present ONLY when I&C is served:
  SYN-2016-003, -006, -010, -029, -035, -036, -049
resi accounts present ONLY when I&C is suspended:
  SYN-2016-004, -017, -021, -024, -025, -026, -050, -060, -061, -064, ...
```

**Households appear and disappear in both directions.** The dial is not selecting from a fixed
population; it is generating a different one.

## The mechanism

`simulation/live_population.py` applies the filter in three places, and two of them are fine.
`static` is filtered after the roster is read (line ~434) and `drawn` is filtered after the trickle
is drawn (line 204) — both pure subsets, both correct.

The third is the growth campaign:

```python
won = [c for c in _won_customer_dicts(_campaign(_pre_growth_book(seed), seed))
       if _serves(c, served)]
```

The WINNERS are filtered, which is what the 2026-08-26 repair was about and is correct as far as
it goes. But the campaign's **input** is `_pre_growth_book(seed)`, and that function is itself
segment-filtered:

```python
book = [sc for sc in _drawn_trickle(seed) if _serves(sc.to_customer_dict(), served)]
...
static = [c for c in _STATIC_ROSTER if _serves(c, served)]
```

So suspending a segment changes the book the campaign plans against, which changes the campaign's
stochastic funnel, which changes **which residential prospects it wins**. The filter is applied
correctly at the output and leaks in through the input.

That is exactly what the red control says in its own words — *"the filter is not independent of
the segment it is filtering on"* — and the control is right.

## Why this is BLOCKING rather than a note

`served_segments` is a **curriculum dial**: it decides which world the company lives through, and
it is the director's instrument. The entire point of a dial is that it can be moved and the
consequence attributed. This one cannot be:

- Two arms differing only in the dial have different residential books, so any difference in P&L,
  churn or arms performance is confounded by population composition.
- The confound is invisible in the aggregate — 238 vs 257 looks like "we suspended some accounts"
  until you diff the identities.
- It sits on the same class as the standing rule that a comparison must not change two things at
  once. Here one deliberate change silently makes a second.

**Nothing has been measured across this dial yet as far as I can find, which is the only reason
this is not also a correction to a published figure.** Anyone who does so before it is repaired
will get a number and no way to know what it means.

## Is the campaign SUPPOSED to depend on the dial?

There is a real argument that it should: a supplier that serves fewer segments genuinely runs a
different acquisition campaign, and modelling that is more faithful than not. **That argument is
about the SIZE of the campaign, not about the IDENTITY of the households it wins.** A supplier
withdrawing from I&C does not thereby win a different set of houses; it wins the same houses with
a different budget.

So the repair is not "stop the campaign seeing the dial". It is to make the campaign's household
draw independent of the dial — the same C-S2 constraint the drawn cohort already honours, keyed on
the customer rather than on draw order — while leaving the campaign's scale free to respond.

## What is owed

1. Make the campaign's residential prospect draw a function of `(prospect_id, base_seed)` rather
   than of the book's contents, so the dial cannot reorder it.
2. A control keyed to the property: **the residential SET, not the residential COUNT, is identical
   across dial positions.** The existing test asserts the count, which is why it took a
   nineteen-account swing to fire — a dial that swapped ten households for ten others would have
   passed it silently. That is the sharper half of this finding and the reason it is filed
   separately from the labelling one it was found beside.

Not repaired here: it changes the composition of the live book and therefore moves published
figures. It needs its own pre-registration and a one-variable run.

## The consequence of the severity, chosen against my own convenience

BLOCKING means *"new level-raises in the affected LANE are refused until it is repaired, or until
the limitation is explicitly recorded and accepted."* The affected lane is
`W2_customer_generator`, which is the lane the entire choice-and-channel programme sits in — C1b
and C2 both live there.

I considered filing this LATENT for exactly that reason, and `background/finding_severity.py`
names that move in its own docstring as the anti-pattern: *"deciding one's own finding is not
BLOCKING in order to keep a lane open."* It is BLOCKING on the definition — the dial is an
instrument and the instrument is untrustworthy — so it is filed BLOCKING.

**What this does and does not stop.** It refuses new LEVEL-RAISES in `W2_customer_generator`. It
does not stop the work: C2 (competing-risks departures) and C1b (SVT assignment) touch nothing in
this path and proceed. What they cannot do until this is repaired is claim a level move on the
strength of a measurement taken across the segment dial — which is precisely the claim that would
be wrong.

**The accept-the-limitation route is the director's, not mine.** `served_segments` is a curriculum
instrument and R13 puts curriculum with him. The limitation is recorded above; accepting it is a
decision about his own dial. Recommendation if he wants the lane open before the repair: accept
it explicitly and narrowly — *no result may be attributed to the served-segments dial until the
residential SET is proven stable across dial positions* — which costs nothing today, because
nothing is measured across it.

## Its relationship to the companion finding, stated so they are not merged

`WORKER_FINDING_ELEVEN_DRAWN_HOUSEHOLDS_ARE_WEARING_A_BUSINESS_LABEL_2026-08-30.md` is a different
defect that presents in the same place. That one is a labelling error with no behavioural
consequence beyond three red controls. This one is a draw-order dependency in a curriculum
instrument. Fixing the labels would change the numbers above and would NOT fix this — the
nineteen-household swing would become a smaller swing, and the confound would remain, quieter.
**Merging them would have hidden this one behind the easier repair**, which is the reason for two
documents.

---

# DISCHARGE — 2026-08-30

**Repaired.** The world is now a function of the seed alone and the segment dial is applied once,
at the company's book, in `live_population()`. Four places read the dial *while drawing* and all
four stopped: `founder_book` filtered the roster before sizing its top-up, `_founder_roster_size`
and `founder_accounts` sized that top-up against the filtered length, `_drawn_founder_pairs`
skipped non-served accounts **inside** the draw loop (so the dial changed how far down the stream
it walked to reach `wanted`), and `_pre_growth_book` handed the campaign a filtered planning book.
The finding named the last of those; the first three were found while repairing it and are the
larger half of the effect.

## The prediction this run was given, and its refutation

The instruction that drew this work predicted the repair would be **inert on the live world**,
*"because the published book serves all segments and the filter is then the identity."*

**That premise is false and the prediction is refuted.** The live dial is not all segments:
`docs/design/curriculum/served_segments.json` has served `["resi", "SME"]` since 2026-08-26 — the
director's own I&C suspension. The filter has therefore never been the identity on the live book,
and the repair moves it.

## The two censuses, printed at real inputs

One variable. Both arms in the same worktree, on the same data, differing only in
`simulation/live_population.py`. `resi-set` is a digest of the residential customer-id **set**, so
the identity question is answerable from the output rather than from a count.

**At the committed draw weights (`DEFAULT_SEGMENT_WEIGHTS` as at `d7d1b07b6`) — the state this
commit lands into:**

```
                        BEFORE                                          AFTER
resi,SME,I&C   n=258  {resi 238, SME  9, I&C 11}  e62bc9f1f645 | n=258  {resi 238, SME 9, I&C 11}  e62bc9f1f645
resi,SME       n=251  {resi 238, SME 13}          3633d87337f8 | n=247  {resi 238, SME 9}          e62bc9f1f645
resi           n=255  {resi 255}                  3b5365e098b2 | n=238  {resi 238}                 e62bc9f1f645

BEFORE: resi-only vs all-three — 172 households present only when the business segments are
        served, 189 only when they are suspended; the book is a subset of the all-served book in
        NEITHER direction (183 removed, 180 ADDED).
AFTER:  every dial position has the identical residential set, and every book is a strict subset
        of the all-served book (11 removed, 0 added; 20 removed, 0 added).
```

Note the SME row in the BEFORE column: suspending **I&C** changed the number of **SME** accounts,
13 to 9. The dial was not even confined to the segment it names.

**At the working tree's draw weights** (the sibling lane's uncommitted `{"resi": 1.00}`, from
`WORKER_FINDING_ELEVEN_DRAWN_HOUSEHOLDS_ARE_WEARING_A_BUSINESS_LABEL_2026-08-30.md`), the same
comparison, so the result is not an artefact of one weight setting: before, the live dial swapped
**142 of 251** residential households against the all-served book; after, 0, with the book a strict
subset at every position. Reported separately because the two changes are in flight together and
neither is attributable through the other.

## What this costs, stated because it is a move in a published composition

At the committed weights the live book goes **251 → 247 accounts, and 150 of its 238 residential
households are different ones.** No published figure was *wrong* — each run was correct for the
book it had — but the next regeneration will not reproduce the current per-account record, and
anything reconciling account-by-account against a pre-repair artefact will find it does not match.
That is the price of the dial becoming an instrument, and it is paid once. The alternative was
keeping a book whose composition is a function of a curriculum switch.

This is **not** a curriculum change. `served_segments` still holds exactly what the director set
and still suspends exactly what he suspended; what changed is that suspension now removes accounts
instead of generating a different world. Director notified rather than asked, per the standing
rule, with the number above.

## The control, keyed to the property and not to today's answer

Three tests in `tests/simulation/test_served_segments_curriculum.py`, and none of them names a
count:

1. `test_the_residential_SET_is_identical_across_dial_positions` — the load-bearing one. The
   pre-existing control asserted the residential **count**, which is why it took a nineteen-account
   swing to fire at all; a dial that swapped ten households for ten others passed it silently.
2. `test_suspending_a_segment_is_a_strict_subset_and_removes_only_that_segment` — a filter may
   only ever remove, and only the thing it filters on. Carries its own null (`removed` must be
   non-empty, or the dial is not reaching the book at all).
3. `test_the_world_itself_is_untouched_by_the_dial` — asserted upstream, on `founder_book` and
   `_pre_growth_book` directly, so a future change that re-filters the draw and then re-filters the
   book back into agreement still reds.

**R15 — mutation-proven, at both weight settings.** All three run RED against `HEAD`'s
`live_population.py` in an isolated worktree and GREEN against the repaired one, with everything
else held identical: `3 failed, 29 deselected` → `3 passed, 29 deselected`.

## What was owed and what was done instead

The finding asked for the campaign's prospect draw to be keyed on `(prospect_id, base_seed)`. It is
not; its **input** was made dial-independent instead, which delivers the same property — the world
is a function of the seed — without re-keying the funnel. The funnel remains order-dependent on its
planning book, so a deliberate curriculum change to that book (the founder count, say) still moves
which prospects it wins. That is a real remaining sharp edge, it is *not* this defect, and it is
recorded here rather than left implied.

---

## DISCHARGED 2026-08-30 — the director ruled repair, not acceptance

**Discharged:** `tests/simulation/test_served_segments_curriculum.py::test_the_residential_SET_is_identical_across_dial_positions`

Director, 2026-08-30, on the acceptance route this document offered him:

> "Repair it — don't accept the limitation. My ruling on suspending I&C was that the SIM keeps
> creating those accounts and only the company's book changes. A dial that alters which households
> exist is the opposite of that, and it invalidates every comparison across it. The segment choice
> belongs at the company's acquisition decision, not in the world's draw."

## The mechanism section above was RIGHT AND INCOMPLETE — there were four leaks, not one

It named the campaign's input and stated that `static` and `drawn` were "both pure subsets, both
correct". Repairing only the campaign's input left the confound in place and made it **worse in
one direction** — 26 residential accounts existed only under suspension, up from 10. The other
three were found by re-measuring after the first repair rather than by reasoning about it:

| site | how it reached the draw |
|---|---|
| `_pre_growth_book` | the campaign plans against it, so a filtered input reorders the stochastic funnel (the one this document found) |
| `founder_book` | filtered `_STATIC_ROSTER`, **then sized its top-up against the filtered length** — so the dial changed how many founders were drawn |
| `_founder_roster_size` / `founder_accounts` | same filtered count, feeding `wanted` |
| `_drawn_founder_pairs` | **skipped non-served accounts INSIDE the draw loop**, so the dial changed how far down the same stream it walked to reach `wanted` |

The last one is the subtlest and the one a reader would defend: skipping an account you do not
serve looks obviously correct, and it is — after the draw, never during it. A `continue` inside a
generator loop is a change to the sequence.

**Recorded because the first repair looked complete and made the number worse.** Re-measuring
after each step, rather than reasoning that the fix was sufficient, is the only reason the other
three were found.

## The repair

The world is now a function of `seed` alone: `founder_book`, `_founder_roster_size`,
`founder_accounts`, `_drawn_founder_pairs` and `_pre_growth_book` no longer read
`served_segments()`, and every drawn point is registered whether or not this company serves it —
*a suspended segment is an account this company does not serve, not an account that does not
exist.* The segment choice applies **once**, in `live_population`, at the point the company's book
is assembled. Quote-level spend is untouched: a supplier that quoted a prospect it will not serve
has still spent the money.

## Measured, after

```
SE_SERVED_SEGMENTS="resi,SME,I&C"  ->  {resi: 238, SME: 9, I&C: 11}   n = 258
SE_SERVED_SEGMENTS="resi"          ->  {resi: 238}                     n = 238

residential SET identical across dial positions:  True   (238 vs 238)
resi_only is a strict subset of everything:       True
removed by the dial: 20 accounts, all non-resi:   {SME, I&C}
```

Before: the dial ADDED nineteen households and the sets were non-nested in both directions.
After: it removes twenty non-residential accounts and touches nothing else.

## The controls, keyed to the SET rather than the count

Three new, in `tests/simulation/test_served_segments_curriculum.py`, plus the pre-existing count
test which stays:

* `test_the_residential_SET_is_identical_across_dial_positions` — the load-bearing one. The count
  test took a nineteen-account swing to fire; a dial that swapped ten households for ten others
  would have passed it silently.
* `test_suspending_a_segment_is_a_strict_subset_and_removes_only_that_segment` — a filter may only
  remove, and only the thing it filters on.
* `test_the_world_itself_is_untouched_by_the_dial` — asserts the property directly on
  `founder_book` and `_pre_growth_book`, so a future change that re-filters the draw and then
  re-filters the book back into agreement still reds.

**R15, applied in place and reverted:** restoring the `_serves` skip inside `_drawn_founder_pairs`'
draw loop — the subtlest of the four leaks — reds all four (the three new ones and the original
count test). Nothing else moves.

## Five tests updated, each with its reason beside it

`tests/simulation/test_founder_book.py` computed its expectations from the SERVED roster, which is
the contract being repaired. Four moved to the world's roster. The fifth,
`test_every_founder_is_dated_at_the_windows_START`, is the interesting one: it asserted the
acquisition year over the whole founder book and **passed only because the dial happened to hide
its counterexamples** — the hand-authored roster carries five I&C accounts dated 2017–2020
(C_IC1..C_IC4, C_IC3g), all suspended by default. When `founder_book` stopped reading the dial they
reappeared and it went red on hand-authored history, which is not a defect. It is now keyed to the
DRAWN founders, which are its actual subject, and is the stronger control for it: it can no longer
be satisfied by a filter hiding its counterexamples.

`test_every_founder_REACHES_THE_SERVED_BOOK` gained its other half — the world's *unserved*
founders must NOT reach the served book, which only became assertable once the dial stopped
reaching into the draw.

## Blast radius

`tests/simulation` + `tests/saas` + `tests/sim`: 5,731 passed, 6 xfailed.
`tests/company`: 14,868 passed, 3 xfailed, 4 subtests.
