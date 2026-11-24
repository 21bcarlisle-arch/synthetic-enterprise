**Severity:** RECORDED · **Lane:** W3_industry_systems · **Epoch:** 4 · **Atom:** `W3_3_the_network_charge_splits_per_unit_and_per_day` · **Claim:** `seat-finding-the-world-settles-metered-kwh-and-no-losses-so-the-energy-line-is-9-to-12-pct-light`

# Pre-registration: the world settles a domestic supplier's electricity grossed up for losses

*Worker, 2026-11-24, in an `origin/main` worktree at ee7d60bbd5. This record lands before any book
carries the change. The switch is `SETTLEMENT_LOSSES_APPLIED` in `simulation/hedged_settlement.py`,
and it is False in the same commit. Its control is
`tests/simulation/test_the_world_settles_electricity_losses_by_one_switch.py`. Seven mutations each
turn it red, and each was restored byte-identically: the flag set True; every segment uplifted;
the switch unreadable; Economy 7 read on the single-rate row; gas uplifted in the deemed writer;
the reader falling back to 1.0 outside the workbook; the multi-register row ignored.*

## What is built

- **The law, in the commons.** `docs/domain_artefact_library/regulatory/ofgem_cap_loss_multipliers.json`
  holds Ofgem's demand-weighted transmission-and-distribution loss multiplier. It covers 14 regions
  × 32 cap periods (Apr 2015 – Dec 2026), single-rate and multi-register, plus the GB median of the
  regions. It was read from Annex 3 v1.25 `3b Losses`, section 2 (sha256 `36bced6c…f5ff3`, the hash
  the knowledge page recorded on 25 Oct). The builder is `/var/tmp/se-losses-probe/build_artefact.py`,
  outside the repo. The medians reproduce the knowledge page's §3b table: 1.095 in 2016/17,
  1.121 in Apr–Sep 2025.
- **The reader.** `simulation.policy_costs.get_electricity_loss_multiplier(date, multi_register=)`.
  Outside the workbook it returns None, and the settlement refuses that date rather than settling
  it loss-free.
- **The charge.** Domestic electricity, in the hedged and deemed writers, buys the loss energy at the
  same blended hedge/spot price as the metered energy: `loss_cost_gbp = wholesale × (m − 1)`. This
  is the shape the gas leg uses for Unidentified Gas. Revenue, levies, network and the meter's kWh do
  not move.
- **Not covered, named.** SME and I&C get no uplift, because Ofgem's table describes the domestic
  benchmark (GAP; an HV site's losses are lower). Flex terms are I&C pass-through, and a real flex
  contract passes losses through. The regional spread waits on an address-to-GSP-group mapping.
  The levies (RO, CfD, CM, FiT) are charged on metered volume here; whether each is charged on
  loss-adjusted volume is not examined (GAP).

## Why it is off

The first-term cap hold's deletion (`SEAT_PREREG_THE_FIRST_TERM_CAP_HOLD_DELETED_2026-11-24.md`)
waits on the post-s.12g book. If both landed on one book, neither change could be attributed. So
the order is:

1. Read the hold's book.
2. Take this switch, alone, against that book.

That makes this a one-variable run against a book already read.

## Predictions (filed before any book carries the change)

Flat-profile sizing at real inputs: the year's mean SSP × (m − 1) × 2.9 MWh, using the daily SSP
cache (`/var/tmp/se-losses-probe/size.py`).

| year | mean SSP £/MWh | mean m | £/yr per 2,900 kWh home |
|---|---|---|---|
| 2016 | 39.4 | 1.0949 | 10.8 |
| 2018 | 57.3 | 1.0913 | 15.2 |
| 2020 | 35.1 | 1.0947 | 9.6 |
| 2021 | 113.3 | 1.0950 | 31.2 |
| 2022 | 200.1 | 1.0987 | 57.3 |
| 2023 | 94.6 | 1.1020 | 27.9 |
| 2024 | 71.2 | 1.1070 | 22.1 |
| 2025 | 89.8 | 1.1144 | 29.5 |

- **P1.** The domestic electricity `wholesale_cost_gbp` rises by 9.0–11.5% in every year. By
  construction the ratio is the cost-weighted mean of m − 1, so a year outside the band means the
  switch did not reach the run's writers. That is narrower than the finding's
  9.5–12%: 2018–19 sit at 9.1–9.2%.
- **P2.** The largest increase in pounds falls in 2022, and 2022's share of the run's total loss
  cost is above 25%.
- **P3.** No count moves in the first year: the same customers, reads and bills, with revenue
  identical to the penny. Later years can move, because the company reprices on its own margin.
  A moved count after year one is a consequence to read, not a defect.
- **P4.** Domestic electricity net margin falls by the loss cost. Nothing in the company offsets
  it, because the company prices no losses: a grep of `company/` and `saas/` on 2026-11-24 finds no
  loss term in any strike. **That is a company follow-on, owed.** A real supplier prices losses into
  its unit rate from the published LLFs it is settled on, so the first-term strike
  (`cheapest_fix_against_the_default_tariff_gb_2016_2025.md` §9's wholesale line) should carry them
  through the seam as a published fact. It is not built here.

**Off-rule.** If P1 fails (a year outside 9.0–11.5%), the switch goes back off and the cause is
found before it is retried. If P3 fails in the first year, the charge has leaked onto the meter;
that is a defect, and the switch goes back off.

**Reversal.** Delete the switch, the reader, the artefact and the control. With the switch off, no
book moves.
