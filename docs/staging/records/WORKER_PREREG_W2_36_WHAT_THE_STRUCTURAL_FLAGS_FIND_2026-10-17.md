**Lane:** W2_customer_generator · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`

# Pre-registration: what the two structural flags find among thefts, voids and occupied homes (2026-10-17, written before either flag was run)

Direction item `the-company-theft-screen-reads-a-window-not-a-ratio`. Knowledge:
`docs/market_research/unbilled_energy_and_revenue_assurance.md` §4a (written first, K8).

**The two flags** (`company/billing/theft_indicator.py`), both on company observables only:
- **Empty period.** Electricity. The advance between two consecutive actual reads is zero, and a
  named occupier was liable for some of the span (the bill is neither wholly the owner's void
  charge nor wholly "the occupier"'s). No cut: zero is zero.
- **Annual window.** Registered over the company's own expectation, summed over a window of at
  least 360 days. Its cut is None, because no published source gives one, so at default it returns
  `unscreened`. The probe passes the earlier table's cuts as an instrument only.

**Populations.** As in the two 2026-10-16 pre-registrations: 20,000 synthetic premises per tenure,
2016–2025, monthly actual reads (a smart read), the world's own moves, voids and thefts; and the
published run's book (`run_output_latest.json`) for occupied homes and the void stubs on incoming
accounts.

**Predictions**, per 10,000 premise-years:
- **S1.** Empty period, synthetic premises: thefts about 1,100 (the same as the month-under-0.05
  cut, because a theft hides all use); voids **0** in every tenure, because a wholly void month has
  no named occupier. A theft month that also holds a void day can still flag, as "both"; under 20.
- **S2.** Empty period, run book: **0** occupied homes (the earlier grade found none empties a
  period) and **0** void stubs, because the stub's bill carries the owner's void share. If the stub
  flags, the named-occupier test is reading the wrong field.
- **S3.** Annual window at default: every window `unscreened`, no flag of any cause.
- **S4.** Annual window at the instrument's 0.65: the earlier table's 84–107 thefts, 0 voids,
  0 occupied.

*Refutation.* S1 voids above 0 means the named-occupier leg does not separate a void at all. S2
occupied above 0 means the world empties a named home's period and the flag is not structural.

## Graded (same day)

`python3 -m tools.theft_void_screen_probe --structural --premises 20000`, and
`--structural --occupied-run docs/reports/run_output_latest.json` (633 accounts, 2,099 premise-years).

| Per 10,000 premise-years | theft | theft and void in one month | void alone | occupied (run book) |
|---|---|---|---|---|
| Empty period, owner | 1,149 | 0 | 0 | |
| Empty period, private | 1,074 | 26 | 0 | |
| Empty period, social | 1,156 | 9 | 0 | |
| Empty period, run book | | | 0 | **0** |
| Annual window at default | unscreened | unscreened | unscreened | unscreened |
| Annual window at 0.65 (instrument) | 84–107 | 6–19 | 0 | 0 |

- **S1: the void leg held; the "both" bound was refuted in private lets.** No void alone ever flags.
  "Both" is under 20 in social lets but **26 in private lets, above the predicted 20.** A theft month that also holds a short private void registers zero
  and still has a named occupier for the rest of it, and private voids are the most frequent.
- **S2 held, for a different reason than predicted.** No zero-advance span on the run book was judged
  at all. All 56 zero periods are incoming-account void stubs. Every one carries the owner's void share
  of 1, so the named-occupier leg would file each as a void. But 54 are the account's first period,
  and the company's book has no opening read before them, so the flag never reaches them. The
  named-occupier leg is proven by the unit control and the synthetic table, not by this run.
- **S3 held.** The annual window classified nothing on its own.
- **S4 held**, matching the earlier annual table.
