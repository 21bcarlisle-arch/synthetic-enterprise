**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-commons-artefact-cannot-tell-when-its-source-was-revised

# The cap composition now covers all 33 published periods, and the divisor rule the opening finding stated was wrong for two of them

**Measured:** 2026-09-07, delivery seat. Predictions fixed before measurement in
`SEAT_PREREGISTRATION_WHAT_DIVISOR_DOES_EACH_2026_CAP_PERIOD_CARRY_2026-09-07.md`.
Discharges item 1 of `SEAT_FINDING_THE_CAP_COMPOSITION_CITES_A_MODEL_TWELVE_EDITIONS_STALE_...`.

## What landed

`ofgem_cap_unit_rate_composition` was derived from v1.19 and published 21 cap periods, ending
October–December 2023. It is now derived from **v1.31, fetched from the publisher this pass** (HTTP
200, 5,319,726 bytes) and publishes **all 33 columns the model carries**, to October–December 2026,
in all three payment methods. Its verdict moves `superseded` → `current`.

Three changes to `tools/ofgem_cap_unit_rate_composition.py`, and a fourth the model forced:

1. The benchmark sheet is resolved **by pattern** (`ElecSingle_<method>_(Benchmark|<n>kWh)`). v1.31
   renamed `ElecSingle_Other_3100kWh` to `ElecSingle_Other_Benchmark`, which is why the reader failed
   closed on it. A sheet named for a consumption is explicitly **not** read as evidence of the
   divisor — in v1.31 the two disagree for four periods.
2. The divisor is **per period**, carried on every published row as `benchmark_kwh`.
3. The basis change is stated **in the artefact's `basis`, beside the figures**, with each base's
   provenance and its standing separately recorded.
4. **VAT is per period too.** Not in the brief, and the model made it necessary — see below.

## The correction: THREE bases, not two, and the finding's rule would have been 8% wrong

The opening finding read the note in row 7 of the benchmark sheet and stated the rule as two bases:
3,100 kWh up to P15b, 2,500 kWh from P15b (January 2026). **That is not what v1.31 does.** Row 8 of
the same sheet carries a *second* note, from a decision published 27 May 2026, and the model's `1c`
consumption table states the mapping as figures against named date ranges:

| applies from | kWh | where it comes from | standing |
|---|---|---|---|
| the start of the series | 3,100 | the basis of the whole pre-2026 series | **corroborated** — the eight periods Jan 2024 – Oct 2025 land within 0.5% against published cap levels, and 24% high at 2,500 |
| January 2026 (P15b) | **2,700** | Ofgem's benchmark-consumption decision of 21 Nov 2025 | publisher's own table only |
| July 2026 (P16b) | 2,500 | the 'review of typical domestic consumption values' decision of 27 May 2026 | publisher's own table only |

So the header cell's "2,500 kWh" is the **latest** basis, not the basis from P15b. Applying the
finding's two-base rule verbatim would have divided January–June 2026 by 2,500 instead of 2,700 and
published those two periods **8% high** — smaller than the 24% the finding caught, in the same
direction, and invisible for exactly the same reason: **every share stays right, because a share is
a ratio and the divisor cancels.** The finding's mechanism was right and its instance was wrong.

The note the finding read was not misquoted. It was **complete when written and superseded by the
time it was read**, in the same file, three rows above the note that superseded it. That is the
shape worth keeping: *a prose note inside a source is itself an edition, and it rots at a different
rate from the figures beside it.*

## What was predicted and what happened

| # | prediction | outcome |
|---|---|---|
| P1 | `1c` restates every period at one consumption, so its ratio to the main sheet reveals each period's divisor (0.8065 / 0.9259 / 1.0000) | **REFUTED — and uninformative, which is the honest reading.** Observed ratios run 1.41–2.10 with no step at either boundary (Oct 2025 → Jan 2026 steps by 1.092 where the divisor change alone predicts 1.148; Apr → Jul 2026 steps by 1.185 where it predicts 1.080). `1c` is a *re-derivation* of historical periods on current methodology, not a restatement, so it says nothing either way about the divisor. **It does not support the 2026 divisors and it does not challenge them.** |
| P2 | electricity VAT is 0%, not 5%, for Oct 2026 – Mar 2027 | **CONFIRMED.** The model's `1a` note says so with a gov.uk citation, and the workbook shows it: for Oct–Dec 2026 the GB-average *including-VAT* electricity row equals the ex-VAT row (854.72 both), while gas on the same row carries 5% (819.39 → 860.36). |
| P3 | the eight new checkable periods land within 0.5% at 3,100 kWh | **CONFIRMED** — worst 0.50% (Jan–Mar 2024), five of eight under 0.25%. |
| P4 | no already-published figure moves | **CONFIRMED** — 0 of 21 periods × 3 payment methods × 6 fields moved at any published decimal place. |

**P1 was the prediction that mattered and it failed.** Its named failure mode was "ratio ≈ 1.0
everywhere, test says nothing"; the actual outcome was neither the supporting result nor the named
null, so it is reported as uninformative rather than as either. The consequence is that **the 2026
divisors rest on the publisher's own consumption table alone** — a table, not prose, but not
independently corroborated. The artefact says that on its face rather than leaving it to be found:
`which_periods_the_cross_check_reaches` counts, per basis, how many published periods the
cross-check actually reaches, and names 2,700 and 2,500 as reaching none.

## The control, and the poison round before it

`tests/tools/test_the_cap_benchmark_divisor_is_per_period.py`. A dated schedule hardcoded in a
module is a claim about a publisher, and a claim about a publisher that nothing re-asks is what put
this artefact twelve editions behind in the first place. So `_verify_benchmark_schedule` re-reads
`1c` on every run and **refuses to publish** on disagreement — a fourth revision must stop the
press, not be averaged in.

Every mutation was killed, and the two that matter are the ones that catch a control that cannot
fail:

| mutation | killed by |
|---|---|
| `benchmark_kwh` returns 3,100 always (the "one constant" defect) | 2 legs |
| `benchmark_kwh` returns 2,500 always (**the header-cell defect itself**) | 3 legs |
| the witness never refuses (fail-open) | 4 legs |
| VAT is a flat 1.05 | 1 leg |
| **the witness ALWAYS refuses** (a guard that refuses everything and passes every refusal test) | 2 legs |

That last row is the reason the acceptance leg exists. Without it, "the witness refuses" would mean
"the witness is broken" and "the model moved" equally well, and only one of those is a finding.

## A downstream figure MOVED, and the reason is the point

`tools/tou_price_shape_episode.py` joins each day to the commodity share in force over it, via
`share_for`, which carries the last known period forward. With the artefact ending at
October–December 2023, **every day from 2024-01-01 to 2025-12-31 was being assigned the
October–December 2023 share** — 24 months of carry-forward. The 2024–2025 episode's
`commodity_share_median` was therefore 0.5595, which is Oct–Dec 2023's number, not a 2024–25 one.

It is now **0.5079**, measured from the periods those days actually fell in. The episode verdict
("DOES NOT REACH THE EVIDENCE RANGE") does not change; the faced ratios and modelled responses move
slightly, all in the direction of the lower share.

**The carry-forward is silent, and that is the latent defect here.** `share_for` returns
`(share, in_force)` with no signal that it ran off the end of the schedule, so a share carried 24
months past the last period Ofgem published is indistinguishable, to every caller, from one read
off the period it belongs to. The pre-2019 case is handled honestly — falling *before* the earliest
column returns `in_force=False` and says so. Falling *after* the last column returns the last
value with full confidence. **The two ends of the same schedule are treated differently and only
one of them is honest.** Not fixed here for the same attribution reason as the item below; it is
worth a control of its own, because it will recur every quarter until the artefact is refreshed.

## Found on the way, NOT fixed here, and deliberately so

**`GB average` is being counted as a distribution region.** The model's benchmark and nil sheets
carry a `GB average` row alongside the 14 real distribution regions, and this module takes its
median and min/max over all 15. The artefact says "median across distribution regions" and publishes
`regions: 15`. One of those 15 is not a region, it is an average of the other 14, and it is
definitionally inside the spread it is being used to describe.

It is left alone in this landing on purpose. Removing it moves 21 already-published medians for a
reason that has nothing to do with the divisor, and a result that moves for two reasons at once
cannot be attributed to either. **It is the next item on this artefact**, and it should land alone.

## What is still open

1. **`GB average` as a 15th region**, above. One-line change, published figures move, land alone.
1. **`share_for` should say when it is extrapolating past the last published cap period**, the way
   it already says when it is before the first. Same shape as the divisor: right for most inputs,
   silently wrong at one edge, and invisible in the output.
2. **Extend `ofgem_default_tariff_cap_windows.json` past 2025-12-31.** Without it the cross-check
   covers less of the series every quarter — it now reaches 21 of 33 periods and **none** of the
   four on the new divisors. **Re-siting its unit rates onto the cap level model, which its own
   `how_to_recheck` proposes as the fix, would make this cross-check a tautology**: the composition
   would be checked against a series derived from the same workbook by the same subtraction. The
   independence of that third-party series is what makes the check evidence. Whatever extends it
   must come from Ofgem's published headline levels, not from the model.
3. **`ofgem_default_tariff_cap_windows` and `gb_domestic_switching_rate` remain `cannot_tell`**, for
   the reasons their own blocks state — a third-party compilation with no edition marker, and a
   citation that names an in-repo derivation rather than an edition.
