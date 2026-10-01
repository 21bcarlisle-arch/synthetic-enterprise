# Pre-registration — the look-ahead fix's +£7,331 split by writer and by book

Written 2026-10-01 ~21:10 BST, before either arm ran. Claim
`attribute-the-look-ahead-fixs-margin-rise-by-writer-and-book`. Arms: `old` = `65401d319` (parent of
`cd0c7c39c`; its `sim/`, `simulation/`, `company/` and `saas/` are byte-identical to `6f5bb8b68`, the
OLD arm of the original measurement). `new` = `cd0c7c39c`. One default world each
(`simulation.run_phase4c_on_phase2b.run_phase2b`). Script: `/var/tmp/se-attr/measure.py`. It logs
every `decide_renewal_rate` call (struck rate, final rate, components) and, for each term key
`customer|fuel|term_start`, net margin, revenue, standing charge, kWh, wholesale cost, record count
and first/last settled day.

## What is being split

ΔM = Σ `net_margin_gbp` (new) − Σ `net_margin_gbp` (old), over all records. The partition by term key:

- **(b1) composition, terms in one arm only.** Their whole net, + for new-only, − for old-only.
- **(b2) composition, matched terms whose extent changed.** The record count or first/last day
  differs, for example because a churn moved inside the term. Δnet on these terms.
- **(f) matched first terms, same extent.** Terms with no renewal-chain entry, or with term_index 0.
- **(a) matched renewals, same extent.** These are the writers. Each writer's £ is
  Δ(rate_after − rate_before) × kWh / 1000, summed per cause. The `struck` difference × kWh is a
  separate line. Whatever the writer £ does not explain of Δnet on (a) is reported as the residual.

(a) + (b1) + (b2) + (f) = ΔM exactly, by construction.

## Predictions

- **P0 (control).** The arms reproduce the earlier runs: 319,176 / 316,175 records, 3,250 / 3,236
  renewals, book net £122,754 / £130,085 (±£1). If not, nothing below is graded.
- **P1.** (f) = £0 ± £1. A first term reads no portfolio list.
- **P2.** (a) carries the majority: ≥ +£4,000 and below the +£7,331 total.
- **P3.** (b1 + b2) is positive, between +£1,000 and +£4,000. Revenue rose only £4,148 while net
  rose £7,331, so cost fell by about £3,200. The terms that left the book were loss-making crisis
  supply.
- **P4.** Within (a), `portfolio_premium` carries ≥ 70% of the writer £. The 12%/14% findings put
  it at 76–77%.
- **P5.** ≥ 60% of (a) is on renewals starting from 2021-07-01 to 2022-12-31.
- **P6.** On (a), the writer £ plus the struck line reconciles to Δnet within 10%.
