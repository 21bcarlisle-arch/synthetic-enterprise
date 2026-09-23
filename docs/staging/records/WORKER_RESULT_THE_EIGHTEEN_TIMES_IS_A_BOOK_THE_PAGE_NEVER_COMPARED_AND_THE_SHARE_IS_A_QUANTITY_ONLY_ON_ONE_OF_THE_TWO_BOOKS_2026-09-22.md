**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the eighteen times is a book the page never compared, and the share is a quantity on only one of the two books

**Filed:** 2026-09-22. Drawn as Lane 0 delivery,
`the-arms-page-cannot-say-whether-the-advantage-is-choosing-or-the-price-level`. Prediction filed
before any contrast was computed, in
`docs/staging/records/PREREG_WHY_THE_TWO_THREE_ARM_RUNS_DISAGREE_EIGHTEEN_TIMES_ABOUT_THE_COMPOSITION_2026-09-22.md`;
marked in §4 below, **beside each prediction and not over it.** Two of four are refuted.

## 0. The item asked for a run. The run was not needed, and the reason is the finding

The item asked me to re-run the three-arm contrast at one commit over one book, launched detached,
and warned about the 1.9 GB already on the box. **No run was launched.** Every artefact the
one-variable comparison needs is already on disk and has been for four days, and what was missing
was not a measurement — it was a *comparison the page is structurally unable to make*.

## 1. THE ANSWER — the two runs differ in THREE things, and the page said two

`site/data/value_arms.json` → `current_world.composition.differs_from_the_superseded_panel`
published, until this commit:

```
differ: ["the date it ran on", "the commit that produced it"]      how_many_differ: 2
same:   ["the world it ran in"]                                     unestablished: []
```

**Three differ.** The books are not the same book, and the artefacts say so plainly:

| control arm | `three_arm_20260908` (98.5% level) | `three_arm_20260918` (5.5% level) |
|---|---|---|
| billing accounts settled in window | **164** | **154** |
| with an electricity leg | 146 | 136 |
| with a gas leg | 105 | 90 |
| dual fuel | 87 | 72 |
| accounts at end of window | 73 | 55 |

`_same_book` — which compares exactly these five counts — **already existed in the same module**,
read by `_departure_term_rerun` and by nothing else. `_RUN_IDENTITY_FIELDS`, the tuple the
attribution count ranges over, held three entries and the book was not one of them. So the page's
own refusal understated itself **in the flattering direction**: "two things changed" invites a
reader to hold the third fixed, and the third is the one that moves the leg the share is a share OF.

## 2. WHY THE BOOK IS NOT A FOOTNOTE HERE — measured on the two same-book re-draw families

The share is `level_advantage_gbp / value_advantage_gbp`. Priced on the floor families that realise
each book — every seed row of each family carries `billing_accounts_settled_in_window`, and the
value is constant within each family:

| family | realises book | `level_advantage_gbp` mean | sd | CV | `level_share` sd |
|---|---|---|---|---|---|
| `folded18_single_arm_20260917` (**`NOISE_FLOOR_PATH`**) | **164** | £19,277 | £1,297 | **6.7%** | **0.1015** |
| `next12_20260917` @ `a178b56d6` | **154** | £8,465 | £5,593 | **66.1%** | **3.2838** |
| `next12_at_18327d977` @ `18327d977` | **154** | £7,655 | £5,610 | 73.3% | 2.9140 |
| `noise_floor_20260909b` (**`CURRENT_WORLD_NOISE_FLOOR_PATH`**) | **none — book_identity is `null`, 0 of 9 seed rows carry a count** | £19,400 | £1,177 | 6.1% | 0.1046 |

Two readings, and the second is the one that settles the item:

**The level leg's centre is 2.3× larger on the 164 book than on the 154 book** (£19,277 against
£8,465). That is a book effect, measured on two seed families rather than argued, and it is real.

**And the level leg's coefficient of variation goes from 6.7% to 66% — ten times noisier.** So
`level_share_of_advantage` is a determinable quantity over the 164 book (sd 0.10) and **is not a
quantity at all over the 154 book** (sd 2.91–3.28, one family's own re-draws running from −0.05 to
+12.07). The published 5.5% is one draw from a family whose range contains 98.5% as well.

**There is therefore no 18× disagreement to attribute.** One of the two answers has an error bar
that contains the other. The gap is one family's spread read as two findings.

## 3. THE CONTROL THAT COULD HAVE SAID SO WAS ASKING THE RIGHT QUESTION OF THE WRONG FAMILY

`_composition`'s first refusal is keyed to a property and not to today's answer, exactly as it
should be: *is the numerator determined in SIGN across the floor's re-draws?* It asks that of
`CURRENT_WORLD_NOISE_FLOOR_PATH` — the nine-seed family in the table above, the one whose
`book_identity` is `null` and whose nine seed rows carry no count at all. On that family the level
leg is 9-of-9 positive, so the sign test passes and the block reads `readable: True` on that leg.

Ask the same question of the family that realises the **same book as the run being compared
against** (`next12_at_18327d977`, 154): `level_advantage_gbp` is **1 of 12 negative** — the sign is
not determined, and the refusal would fire.

**A floor that cannot name its book agrees with every book**, and it happened to give the
flattering answer. This is not fixed in this commit — see §6 — because the fix is not the obvious
one, and the obvious one is shut.

## 4. MARKING THE PREDICTIONS

**P1 — REFUTED AS WRITTEN, and its substance survives on a family I did not name.** I predicted
the eighteen-seed single-arm family's `level_share_spread` would have min < 0.0551 and max > 0.9848.
It does not: its range is **[0.9646, 1.2451]** and 0.0551 is nowhere near it. I picked that family
because it is what `NOISE_FLOOR_PATH` names, without checking which book it realises — it realises
**164**, the book of the run I was trying to explain the *other* run with. The claim "the noise
alone spans both published answers" is true, and it is true of `next12_at_18327d977`, the family
drawn over the **154** book, whose range **[−0.0482, 10.6421]** contains both 0.0551 and 0.9848.
*Right mechanism, wrong family, and the reason I got the family wrong is the same reason the page
got the comparison wrong: I did not ask which book it was drawn over either.*

**P2 — CONFIRMED.** The one-book pairings state no sign, and by a wide margin:

| family (book 154) | n | mean | sd | sem | t | p | verdict | seeds needed at this mean and sd |
|---|---|---|---|---|---|---|---|---|
| `next12_20260917` | 12 | −£1,069.48 | 5,398.31 | 1,558.4 | −0.686 | 0.507 | **NO SIGN** | **101** |
| `next12_at_18327d977` | 12 | −£259.29 | 5,413.58 | 1,562.8 | −0.166 | 0.871 | **NO SIGN** | **1,677** |

Predicted t < 2.2 and p > 0.05. Both hold. For contrast, the family the page's error bar actually
uses (`folded18_single_arm`, book **164**) reads t = −2.495, p = 0.0232 — a sign IS stated there,
and it is stated over a different book from the run it is being compared against.

**P3 — REFUTED, and usefully.** I predicted no book-pairing check existed. One does, and it is
thorough: `_the_runs_declared_book`, `_floor_realised_book`, `_realised_book_pairing`,
`ADMITTED_ON_A_STAMP_PROXY`, all fail-closed per field, with a control that caught its own
`len(values) == len(seeds)` vacuity on first run. **What was missing was never the floor-to-run
pairing. It was run-to-run**, in `_RUN_IDENTITY_FIELDS` — and the module had the comparator for it
already. I looked for the gap in the sophisticated machinery and it was in a three-line tuple.

**P4 — CONFIRMED and it is not load-bearing.** `value_arm_pairing` records the code-tree step at
**£671.31, 20.4 sems from zero**, which is 2.5× the entire published £270.21 selection figure. Real,
and an order of magnitude below the £4,057 the selection leg moved between the two runs. As
predicted, the commit matters and cannot be the 18×. P1's mechanism carries it.

## 5. WHAT LANDED

`_RUN_IDENTITY_FIELDS` gains `("the book it was scored over", _the_book_a_run_was_scored_over)`,
reading the same five control-arm counts as `_same_book` from one hoisted `_BOOK_IDENTITY_FIELDS`
constant, so the rule has one implementation and not two edited on different days.

**Fails closed on a partial book.** The reader returns `None` unless all five counts are present. A
tuple built with plain `.get` would carry a `None` and compare **equal** to another equally-partial
run's tuple — manufacturing "same book" out of two silences. A leg asserts that directly.

**The prose stopped being a second copy of the list.** Three branches of
`_against_the_superseded_panel` hand-typed "the world, the date and the producing commit"; all
three would have gone false on this commit. They now derive the enumeration from the tuple. The
`" and ".join` that built those lists also published *"the date it ran on and the commit that
produced it and the book it was scored over"* on its first render — correct while every list held
two items — so `_listed` now owns the punctuation of a list whose length is data.

The page now reads: **"3 things differ between the two runs — the date it ran on, the commit that
produced it and the book it was scored over — so more than one thing changed."**

The control extends the existing whole-partition assert rather than adding a leg per branch. The
book must be reachable in all three of its states — differing alone, differing alongside the rest,
and unreadable — because *a field wired in but never able to differ would satisfy every assertion
that already existed.* Three mutations, each caught: dropping the tuple entry (the defect as it
stood), letting a partial book compare equal, and making the reader always return `None`.

## 6. WHAT IS NOW OWED, AND THE ONE REMEDY THAT IS SHUT

**The composition refusal asks its sign question of a book-silent floor (§3).** The obvious remedy —
move `CURRENT_WORLD_NOISE_FLOOR_PATH` onto the eighteen-seed single-arm family — is the one named
as remedy 1 in
`WORKER_RESULT_BOTH_LEGS_CLEARED_AND_THE_LARGER_FLOOR_WAS_ALREADY_ON_DISK_..._2026-09-22.md`, and
**it is refused by a door that already exists.** That constant's own block records it, tried and
measured on 2026-09-17: pointing both constants at one family puts that family's selection mean into
the `error_bar` region AND the `current_world` region, which `_the_legs_own_regions` refused in
words on 2026-09-09 — *"the selection leg's own figure renders 2 times in this headline"*. So the
move is not a judgement call that was skipped; it is shut, and a note proposing it again should say
so. **Neither of the two families is right: the nine-seed one cannot name its book, and the
eighteen-seed one names a book (164) that is not the disputed run's (154).**

The shape of the remedy is therefore a THIRD thing and not a swap: the composition block should ask
its sign question of a floor **selected by the book of the run being read**, and refuse — named, on
the surface — when no floor on disk realises that book. That refusal would fire today for the 154
book against the `current_world` panel, which is the honest state.

**The one-variable run this repo already names is still owed** — the twelve seeds at `4e7938f673`,
which separates the instrument from the seed set and settles the width disagreement
(sd 5,398 against 1,631, F = 10.94 on df (11,17), p = 2.3e-05) that the published sign rests
entirely on. Nothing in this turn touches that, and it is not a bounded tick's job.
