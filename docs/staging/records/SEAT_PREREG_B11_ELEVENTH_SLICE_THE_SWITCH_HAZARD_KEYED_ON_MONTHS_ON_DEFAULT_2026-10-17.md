**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` (parked; row untouched) · **Claim:** `b11-slice-11-the-switch-hazard-keyed-on-months-on-default` (Lane 0 delivery)

# Pre-registration: B11 slice 11, the level fix alone, then the switch hazard keyed on months on default

Written 2026-10-17 at origin `f10a51da2`, before either change exists. Not edited after the run;
results go in a separate finding, each graded beside its prediction here.

**What is already known and therefore NOT predicted.** Slice 10's finding
(`docs/staging/WORKER_FINDING_B11_THE_HAZARD_THAT_SEES_WHAT_A_SUPPLIER_HOLDS_CANNOT_YET_TELL_SWITCHERS_APART_2026-10-17.md`)
reports on this book: the level drift with months advancing (−0.081, −0.055, −0.041); the
months-on-default-alone all-cause grade (switchers +0.079, +0.067, +0.127, clearing at 2023); and,
in its addendum, the switch-only fit-window ratio for 36+ months (0.68 at 2020, 0.50 at 2023). Every
prediction below is about a rule nobody has run.

## The book

`docs/reports/run_output_latest.json` read through `tools/run_output_store` — slice 10's book
(run at `78f77c34e`, 772 accounts, 212 move-out rows). Cuts 2020, 2022, 2023. One book, one seed:
**every result is DEVELOPMENT.**

## Step one: freeze the months-on-default band at the cut (one variable)

Slice 10's rule advances an on-default account's months over the horizon, so accounts cross into
the 0.57 band after `c_segment` was renormalised. The change: over the horizon each account's
view is the one it held at the cut, months on default included. Nothing else moves. Graded on
slice 10's rule (all three observables, all-cause) by mean per-customer p minus flat p.

- **S1a.** |mean p_pc − p_flat| is strictly smaller than slice 10's at all three cuts.
- **S1b.** It is NOT within 0.01 at cut 2020, and stays negative at all three cuts. Reason, stated
  now: `c_segment` is renormalised over the whole fit window, whose band mix is not the cut's. Every
  account opens on a fixed term, so a 36+ month is reachable only late in the window and is far
  commoner at the cut than across the window. Freezing removes the horizon drift, not this one.
  If S1b is right, freezing is necessary but not sufficient, and the finding says so; it does not
  then reach for a second fix inside this grade.

## Step two: the switch hazard keyed on months on default alone

Per-customer monthly departure hazard = `h_move,seg + c_seg · M(band at the cut) · h_switch,seg`.

- `h_switch,seg` and `h_move,seg` are the existing `_fit_hazards` with moves censored and switches
  censored respectively; they sum to the flat segment hazard, so the flat rule is untouched.
- `M` is one multiplier: 36+ months on default against under 36, the CMOL 0.54 prior with its
  0.44–0.66 range, shrunk to the book's own SWITCH ratio (moves censored) by the existing
  `n/(n+k)` weight, `k` read from the range. Tariff and payment are not keyed.
- `c_seg` makes the fit window expect the flat rule's SWITCH exits in each segment. The band is
  frozen at the cut (step one).

Graded on switchers against stayers at each cut, paired with the existing DeLong 95% interval
(a) against flat and (b) against the contract-year rule on the same accounts. Movers and the whole
book are graded the same way, as the guard on "ranks worse".

- **S2a (reachability).** At every cut both bands carry graded accounts, and the multiplier is
  strictly between the book's switch ratio and 0.54 wherever the book ratio is defined and
  differs from the prior.
- **S2b (switchers vs flat).** Point estimate positive at all three cuts; beyond the bound at 2023
  only. Cannot tell at 2020 and 2022.
- **S2c (switchers vs contract-year).** Cannot tell at all three cuts. Point estimate positive at
  2020 (contract-year ranked at 0.531 whole-book there, near chance).
- **S2d (movers vs flat).** Cannot tell at all three cuts, with a NEGATIVE point estimate at 2020:
  on moves the 36+ band leaves at 1.68× under 36, and this rule ranks it lower.
- **S2e (level).** Mean p_pc − p_flat is negative at every cut, by less than step one's (only the
  switch part is scaled).

**F11.** If switchers clear the bound at one cut only, the finding reads "cannot tell, leaning
the key", never "ranks better".

## What decides whether the key goes into EP17's arm

Recommended for EP17's per-customer arm only if all three hold:

1. switchers rank better than flat beyond the bound at **two or more** cuts;
2. **no** outcome (switchers, movers, whole book) ranks worse than flat beyond the bound at any cut;
3. switchers do **not** rank worse than the contract-year rule beyond the bound at any cut.

Otherwise "not yet". By S2b this prereg expects "not yet". EP17's fresh-seed verdict stays the
director's open row: this slice recommends, it does not rule.

## Controls, named before they are written

- Freeze: an on-default account under 36 months at the cut keeps its per-customer hazard over a
  long horizon. Mutation: restore `months_on_default + step + 1` → red.
- Switch key: two accounts alike but for their band at the cut get different p; the move part is
  untouched by the band; refused without a move register. Mutations: key the all-cause hazard
  instead (drop the censoring) → red; `M` = prior only (w = 0) → red; key reaches nothing → red.
- Paired ranking: the DeLong pairing of two rules on one book equals the existing
  per-customer-vs-flat pairing when the second rule IS flat. Mutation: drop the covariance → red.
