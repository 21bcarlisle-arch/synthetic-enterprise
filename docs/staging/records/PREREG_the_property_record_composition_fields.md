**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_13`

# PRE-REGISTRATION — giving the property record its two composition fields

**This document is the RECORD: the predictions, and what happened to them. It owes nothing.**
The work it uncovered is owed by a separate finding in the root work queue —
`SEAT_FINDING_THE_DAYTIME_REFERENCE_WAS_ONE_NUMBER_FOR_THREE_INCOMPATIBLE_SCALES_2026-09-23.md`,
filed BLOCKING. Splitting them was not a filing preference: `background/staging_rooms` refused the
commit that filed this one document in the root, and it was right to — a pre-registration in the
work queue is a record wearing work's clothes, and the severity a record carries cannot be
discharged because `records/` has no exit. One document could not honestly be both.

**Written 2026-09-23, BEFORE any of the measurements below were run.**
Claim id: `the-property-record-has-no-pensioner-or-employment-so-the-daytime-shape-collapses-to-one-number`

## What I am about to do

`simulation.demand_model._daytime_occupancy_rate` is keyed on three EFUS cuts — household size,
pensioner presence, employment — and takes the equal-weight mean of *the cuts it was given*.
`simulation.dwelling_records.build_properties` supplies only the size cut, so every property
record in the book takes the size-only reading and the two composition cuts are silent. The
FABRIC path (`premise_trace.behaviour_profile_for`) draws both for itself. One home, two answers —
the same shape as the headcount defect that `people_count_for_area` closed on 2026-09-17.

## Predictions, in order, each falsifiable

**P1 (tree).** On the live book, `pensioner_present` and `someone_employed` are present on 0 of
the property records `build_properties` returns, and the record count is 144.
*(This is the draw's own claim about the tree, which is an un-re-asked prediction until I run it.)*

**P2 (knowledge).** There is NO published anchor in this repository for the population SHARE of
households containing a pensioner, or the share with someone employed. The rates (63/34, 60/35)
are anchored; the shares are not. `premise_trace` uses 0.22 and 0.25 with no cited origin.

**P3 (derivation).** EFUS publishes both the marginal rates AND the all-household headline (43%).
A marginal share is therefore DETERMINED by the published table rather than chosen:
`0.63·p + 0.34·(1−p) = 0.43` ⟹ **p = 0.3103** pensioner-present, and
`0.35·e + 0.60·(1−e) = 0.43` ⟹ **e = 0.68** someone-employed.
I predict both land inside [0, 1] and are therefore admissible. If either fell outside, the
inversion would be refuted and the honest answer would be an explicit gap, not a picked number.

**P4 (the interconnection — the part I expect to bite).** `_reference_daytime_rate()` is computed
at `(None, None)`: the size cut alone, 0.470. If the two fields are supplied to households but
the reference is left size-only, each household's rate becomes a 3-cut mean centred near
(0.470 + 0.43 + 0.43)/3 ≈ 0.443, and the population mean multiplier falls to roughly
(0.443/0.470)^elasticity < 1. I predict this **breaks `daytime_shape_is_mean_neutral`**
(tol 0.02) — i.e. wiring the fields alone, without recentring, silently cuts daytime demand.
**I predict the observed mean multiplier lands below 0.98.**

**P5.** Recomputing the reference over the JOINT distribution (TS017 size × P3's two shares)
restores the population mean multiplier to within 0.02 of 1.0.

**P6 (spread).** With the fields supplied, the daytime rate across the book stops being the single
number it is today. I predict at least three distinct daytime rates appear across the 144 records,
and the spread between the book's min and max rate is at least 1.2x.

## What "done" means for this item

No exit test was written for it, so: **done is that one home has one answer for these two fields,
the way `people_count_for_area` made one home have one headcount.** Concretely —

1. ONE function answers pensioner/employment for a given home, in `dwelling_records`, beside
   `people_count_for_area`, with the P3 derivation written down at the constant.
2. `build_properties` sets both fields from it.
3. `premise_trace.behaviour_profile_for` draws from the SAME function, so the fabric path and the
   property record cannot disagree about one house.
4. The reference rate is recentred so P4's silent re-levelling does not ship.
5. A control that can fail: the two paths agree per home, AND the book's daytime rate is not one
   number.

If 3 or 4 prove bigger than this turn, 1+2+5 land alone and this file records what was left.

## Results, against the predictions above

Run 2026-09-23, after the file above was written and before any code changed except where stated.

| | prediction | observed | verdict |
|---|---|---|---|
| **P1** | 144 records, 0 carrying either field | live book **144**, **0** and **0** | **HELD** |
| **P2** | no published share anywhere in the repo | none found; `premise_trace`'s 0.22 / 0.25 carry no origin | **HELD** |
| **P3** | p = 0.3103, e = 0.68, both admissible | **0.310345** and **0.680000**, both in [0,1], both re-checked to 0.43 | **HELD** |
| **P4** | wiring alone breaks neutrality, mean **< 0.98** | **0.95866** — a silent **4.1% cut** to daytime demand | **HELD** |
| **P5** | recentring restores it to within 0.02 of 1.0 | **0.99836**, control green | **HELD** |
| **P6** | ≥3 distinct rates, spread ≥1.2x | **18** distinct rates, spread **1.793x** | **HELD** |

**P1 was half wrong the first time I ran it, and the correction matters.** Against the STATIC
roster `build_properties` returns **7** records, not 144 — the 144 only exist once
`live_population()` draws the SYN cohort. The draw's figure was right about the live book and I
would have reported "7, refuted" had I stopped at the first run. A record count is a claim about
*which population you asked*, not about the builder.

**A correction to the draw's own framing, kept beside it.** "The daytime shape collapses to one
number" is right about the two cuts and wrong as stated about the book: the size cut alone already
gave **5** distinct rates across the 144 homes (0.37–0.67). What collapsed is the composition
response *within* a household size — every 3-person home took 0.5200 where the cuts span
0.4033–0.5833. The defect is real and its size is as described; the sentence overstated it.

**And one prediction I did not think to file, which is the actual finding.** I expected P4 to be a
nuisance — recompute the reference over the joint distribution and move on. It is not. It is a
defect in its own right, one layer under the one I was sent for:

> `_daytime_occupancy_rate` averages **the cuts it was given**. A size-only rate and a three-cut
> rate are therefore not the same quantity on the same scale — their population means are 0.470
> and 0.443. `_reference_daytime_rate` was a single constant. So the multiplier `rate/reference`
> was only aggregate-neutral for households carrying **exactly the cut-set the reference was
> computed on**, and nothing said so.

That was invisible and harmless while every caller in the world supplied the size cut alone. It
would have become a 4.1% silent re-levelling of the whole book's daytime demand the first time
*any* caller supplied more — mine, or the next one. The repair is that the reference is now a
function of the cut-set (`_reference_daytime_rate(pensioner_cut, employment_cut)`), each cut-set
centred on its own population mean, and the size-only answer is unchanged to the float.

## What is left

1. **`premise_trace.behaviour_profile_for` still draws its own 0.22 / 0.25-given-a-pensioner.**
   So one home still has two answers — but the two are no longer symmetric: the property record's
   is now EFUS-derived and testable, the fabric path's is uncited. Closing it means routing that
   draw through `dwelling_records.composition_cuts_for`, which moves the fabric book's demand
   (pensioner share 0.22 → 0.310, and the employment draw stops being conditional on it). That is
   a baseline fidelity change decided blind to P&L, of exactly the kind
   `fabric_demand_path` records for the headcount, and it is the next increment.
2. **The JOINT of the two cuts is a named gap, not an anchor.** EFUS's §4.1–4.2 tables are
   one-way. They are drawn independently, and `demand_model` says so at the shares rather than
   leaving the next reader to infer it. If a cross-tabulated source is located, the independence
   is the thing to replace — not the marginals, which are determined.
3. **This severity stays BLOCKING until (1) lands.** The arm is repaired; the two paths still
   disagree.
