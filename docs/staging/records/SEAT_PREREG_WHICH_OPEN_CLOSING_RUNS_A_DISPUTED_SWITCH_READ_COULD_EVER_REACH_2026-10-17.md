**Lane:** W2_customer_generator · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`

# Pre-registration: which open closing runs a disputed switch read could ever reach (2026-10-17, written before the split was run)

Direction item `what-trues-up-a-deemed-closing-read-after-the-customer-has-left`. Knowledge written
first (K8): `docs/market_research/unbilled_energy_and_revenue_assurance.md` §4a, "What trues up a
closing read after supply ends".

**The rule being applied** (sourced on that page): the only published route that replaces a closing
read after the account has closed is the disputed change-of-supplier read (BSCP504 §3.2.6.36–37 and
§4.4.1(b); the REC/SPAA Schedule 11 exceptions procedure for gas). It needs (a) a **gaining supplier**,
which exists only on a switch, (b) a dispute raised **within 12 months** of the supply start date, and
(c) a difference **over 250 kWh** (electricity) or **1,200 kWh** (gas), or a consumer who asks for a
new reading. A home mover's account closes on a change of tenancy with the same supplier. No
industry process applies, and the read is the supplier's own to correct.

**Population.** The 403 open closing runs (estimated last bill, run of at least one estimate) on the
graded run output `/var/tmp/closing-money-run-20261017.json` (cc23de757), the same one
`8cd8e9954` graded. Switcher = a household on `churned_billing_accounts`; mover = on
`home_move_outs`. A household on both is counted as a mover first and reported separately.

**Predictions.**
- **D1.** Switchers are the majority of the open runs: over 50% of accounts.
- **D2.** Few runs pass the kWh threshold. Under 20% of switcher open runs have |true − billed kWh|
  over 250 (electricity) or 1,200 (gas).
- **D3.** Under 25% of the £3,471 new demand sits on switcher runs that pass the threshold. Those
  runs are the only ones a dispute could start without the consumer asking.
- **D4.** Every switcher open run closed at least 12 months before the run's end, apart from those
  in the last year of the run. Fewer than 15% of switcher runs have a window still open at run end.

**What would refute the framing.** If most of the £3,471 sits on switchers above the threshold, the
seed is realisable and a dispute route is worth building. If most sits on movers, the seed has no
industry route and only the supplier's own correction could realise it.

---

## Graded (2026-10-17, same session, after the split ran)

Script: the per-account `what_closure_shows` loop from `departing_view`, with each row tagged by
`churned_billing_accounts` / `home_move_outs` and by |kWh| against the threshold. Run end is
2025-06-07. A household on both lists is counted as "both". **The basis of the £3,471 is corrected
here:** it is new demand summed over the **undercharge** runs, negatives included
(£3,470.63 reproduced exactly). It is not the sum of positive demands (£3,806.61, 150 people).

| Undercharge open runs | runs | new demand £ | window open at run end |
|---|---|---|---|
| switcher, over threshold | 17 (12 el, 5 gas) | **2,222.47** (C7 alone 1,431.26) | 0 |
| switcher, under threshold | 130 | 832.64 | 12 |
| home mover, over threshold | 5 | 68.51 | 2 |
| home mover, under threshold | 56 | 340.63 | 5 |
| on both lists | 2 | 6.38 | 0 |
| **total** | 210 | **3,470.63** | |

- **D1 held.** 265 of 403 open runs are switchers (66%), 132 movers, 6 on both lists.
- **D2 held.** 31 of 265 switcher runs (11.7%) pass the threshold. |kWh| medians are 35 (el) and
  212 (gas); p90s are 312 and 1,061.
- **D3 refuted.** 64% of the £3,471 sits on switcher runs over the threshold (under 25% was
  predicted). C7 is most of it. Without C7 it is £791 of £2,039 (39%), still refuted. The money
  is concentrated in a few large runs, which are the ones the threshold lets through.
- **D4 held.** 17 of 265 switcher runs (6.4%) closed within 12 months of the run's end, so their
  window is still open. None of the 17 undercharge runs over the threshold is among them.

**What it says.** A disputed switch read could ever realise **£2,222 of the £3,471, across 17
people**. The dispute would come from the gaining supplier, because an undercharging closing read
pushes the missed kWh onto its side. **£1,248 across 193 runs has no industry route:**
- £833 sits on switchers under the threshold. There the REC tells the supplier to offer an
  accommodation rather than dispute, unless the consumer asks for a new reading.
- £415 sits on movers. The supplier owns that read, and only its own correction could reach it.

The 14 switcher overcharge runs over the threshold (−£1,603 gross) are the reverse case. Only the
losing supplier has a reason to dispute them, and it holds no read after the loss.
