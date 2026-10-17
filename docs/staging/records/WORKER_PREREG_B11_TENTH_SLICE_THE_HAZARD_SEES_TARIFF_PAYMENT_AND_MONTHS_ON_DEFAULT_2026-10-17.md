**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` (parked; row untouched) · **Claim:** `b11-slice-10-the-hazard-sees-what-a-supplier-holds` (Lane 0 delivery)

# Pre-registration: B11 slice 10, a departure hazard that sees what a supplier holds

Written 2026-10-17 at origin `9b8209daf`. No observable-keyed hazard exists yet, and no departure
has been read against any of the three observables. The only things looked at so far are the cell
SIZES at each cut (how many legs are fixed or on default, how many bills go by each channel), never
an outcome. This file is not edited after the run. Results go in a separate finding, each one
graded beside its prediction here.

## The book: a stated substitution

The direction names "the slice-5 book". That file (`/var/tmp/b11s5_run/run_output_b11s5.json`,
run at `3f1ebfac3`) **no longer exists**: `/var/tmp/b11s5_run/` is gone, and a whole-disk `find`
returns nothing. It was never committed.

This slice therefore grades on `docs/reports/run_output_latest.json`: producing commit `78f77c34e`,
generated 2026-10-16T15:53Z, 772 billing accounts, home moves on, with 212 rows in the move-out
register. It has the same shape as the slice-5 book (the full 2016-2025 annual report, with the
register), but it is a different run at a later commit. **So no number here can be differenced
against slices 5-9.** To keep the comparison within one book, the contract-year rule (the default
since slice 1) is re-graded on this book beside the new key.

## The three observables, and where each is read

All three come from the company's own records in the run report. None is read from world state:
`per_customer_behavioral[...].world_payment_truth` is in the same report and is NOT read.

| observable | read from | at month m |
|---|---|---|
| tariff type | `account_state_log` (the company's own term record, one row per term per leg) | `fixed` if any of the account's legs is in a fixed term covering m, else `default` |
| payment method | `bills[].payment_channel` (the company's own bills) | the channel on the account's latest bill starting on or before m: `direct_debit`, `standard_credit` (on receipt of bill), or `prepayment` |
| months on default | `account_state_log` | consecutive months on default up to and including m, counted from the later of the account's first month and its last fixed month |

`book_from_run_output` keys today on commodity and segment only, so step one is to carry these on
`AccountHistory`. Over the forecast horizon the observables are FROZEN at the cut, except that
months on default advances for an account on default. A supplier would know the scheduled term
end of a fixed account, but not whether it will fix again, so freezing it is a stated
simplification.

## The rule

Per-customer departure hazard = segment flat hazard × M(observables) × c_segment.

- **M** is the product of three multipliers, one per observable, each relative to a reference
  level (default tariff, direct debit, under 36 months on default).
- **Each multiplier** is a prior with its range, shrunk toward what the book itself says:
  `M_l = w·r_l + (1−w)·prior_l`, with `w = n/(n+k)`. Here `r_l` is the book's own fit-window ratio
  (exits observed over exits expected at the calendar year's rate, relative to the reference
  level), `n` is the level's expected exits, and `k = 1/(prior·se²)`. That is the gamma-Poisson
  credibility weight, with `k` READ from the prior's range, not chosen. It is the same `n/(n+k)`
  form as the margin's shrinkage. With little evidence the prior holds; with much, the book does.
- **c_segment** rescales so that, over the fit window, the per-customer rule expects exactly the
  flat rule's exits in each segment. The new key may move WHERE an exit is expected, never HOW
  MANY. Any ranking gain is therefore knowledge, not level.

### The priors (docs/market_research/observable_correlates_of_price_responsiveness.md §A, §C)

95% ranges are the sampling interval on the log ratio, from the published cell bases (CIM w6
Table 56 bases, from `what_a_supplier_can_observe_about_switching_propensity_cim_w6.md` §3).

| level vs reference | prior | 95% range | source |
|---|---|---|---|
| fixed vs default | 2.80 | 1.93–4.06 | CIM w6 C4: 7.0% (n=2,127) vs 2.5% (n=1,316) |
| standard credit vs direct debit | 1.02 | 0.67–1.54 | CIM w6: 5.7% (n=438) vs 5.6% (n=2,483) |
| prepayment vs direct debit | 0.55 | 0.33–0.93 | CIM w6: prepayment (all) 3.1% (n=491) vs 5.6% |
| 36+ months on default vs under 36 | 0.54 | 0.44–0.66 | CMOL control arm: 0.7% vs 1.3% |

**The CMOL range is the weakest.** The band bases are not on file. The range assumes the control
arm is a third of N=137,876, split evenly between the two bands. It is labelled as that assumption.

**Every prior measures switching (E), and the hazard here is all-cause, moves included.** A prior
applied to a move is wrong in kind. The shrinkage lets the book correct the level, but not the
kind. This is stated, not fixed, in this slice.

## Grading

On the one book, at cuts 2020, 2022 and 2023, with everything else at its default:

- the per-customer rule (observables) is paired against flat, using the existing DeLong 95%
  interval on the AUC difference;
- by held-back outcome, stayers, switchers and movers are each ranked against the stayers;
- the margin error is paired per outcome.

The contract-year rule is run beside it on the same book. **Every result is DEVELOPMENT**: one
book, one seed, a world whose engagement axis was itself fitted to some of these same sources (see
P3).

## Predictions

- **P1 (reachability, the partition).** At every cut, every graded account carries all three
  observables, and each observable has at least two levels populated among graded accounts. The
  control asserts that a fixed account, a non-DD account and a 36+-month account are each reachable
  in one fixture, before it asserts what any of them does.
- **P2 (level held).** Mean per-customer departure p equals the flat rule's to within 0.01 at every
  cut. This holds by construction of `c_segment` over the fit window. It can drift over the horizon
  because months on default advance. If it misses, the renormalisation is wrong.
- **P3 (direction of the book's own ratios, fit window, cut 2020).** The direction of each fitted
  ratio is predicted, not its size:
  - fixed vs default **> 1**;
  - prepayment vs DD **< 1**;
  - 36+ months on default vs under 36 **< 1**;
  - standard credit vs DD: no direction predicted.

  Basis: the world's engagement axis carries payment channel (CIM w6 factors) and the CMOL tenure
  gradient, and an active renewal takes a fix. **Caveat, stated now:** the world was fitted to
  some of these same sources, so agreement here is partly circular and is not evidence about real
  customers.
- **P4 (switchers rank better).** For switchers against stayers, the per-customer AUC exceeds the
  flat AUC, with the 95% interval on the difference above zero, at **at least one** of the three
  cuts. Cut 2020 is the likeliest: 136 fixed legs are on supply at the end of 2020, against 17 at
  the end of 2022.
- **P5 (movers: cannot tell).** For movers against stayers, "cannot tell" at all three cuts. A move
  is a life event, not engagement, and nothing here keys on it.
- **P6 (whole book).** For departed against stayed over the whole graded book, the per-customer
  AUC is at least the flat AUC at every cut. A bound-clearing "per-customer ranks better" is
  predicted at cut 2020 only.
- **P7 (margin error: cannot tell).** Paired absolute margin error, per-customer minus flat:
  "cannot tell" for stayers at all three cuts. Only survival moves, and a stayer's survival is
  forecast below one by both rules.
- **P8 (against the old key).** The observables key's whole-book AUC exceeds the contract-year
  rule's at cut 2020. This is a point estimate only, with no bound: the two are not paired by the
  existing machinery.

**F11, erring against the thesis.** If P4 holds at only one cut and nowhere else, the finding reads
"cannot tell, leaning per-customer". It does not read "ranks better".

## What decides whether the key goes into EP17's arm

The key is recommended for EP17's per-customer arm only if both of these hold:

- switchers rank better beyond the bound at **two or more** of the three cuts;
- **no** outcome ranks worse beyond the bound at any cut.

Otherwise the recommendation is "not yet". EP17's fresh-seed verdict stays the director's open
row: this slice recommends, and does not rule.
