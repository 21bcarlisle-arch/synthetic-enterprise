**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B13_a_dual_fuel_household_is_one_account_across_both_fuels`

# The dual-answer fix brings 26 of 41 split answers together, but the named residue is 13 of 34 households, over the third the prediction allowed

Graded by the delivery seat, 25 Nov, on `docs/reports/run_output_f2c6979d01_20261124T215935Z.json`.
That is the first book whose producing commit (f2c6979d01) descends from the fix (c41e70832) and its
neighbours (59cd5ebda, c09847b7c, 1624411d2, da34c45c1). The prediction was filed 20 Nov, before
any book, in `docs/market_research/how_households_respond_to_supplier_contact.md` §7.5c.

**The method, as pre-registered.** Read `riding_leg_answers`. Drop the rows whose `household_answer`
is None (51 rows, basis `no_household_answer`). Before the fix, a row is apart when
`simulation.customer_events.renewal_outcome(event_type='retained',
position_vs_default=row['own_position_vs_default'])` differs from `household_answer`. The row's own
`answer` is post-fix and is not used for this count. The residue is the rows with basis
`pair_above_default_after_the_decision_leg_contracted`.

| Quantity | Rows | Households | Prediction | Grade |
|---|---|---|---|---|
| Riding answers on the book | 312 | 183 | — | — |
| With a household answer | 261 | — | — | — |
| Apart before the fix | 41 | 34 | 20 to 120 households | **pass** |
| Named residue (still apart after) | 15 | 13 | under a third of 34 (11.3) | **fail**, 13 > 11.3 |

How the 41 split:
- 22 rows, `pair_within_default`: the gas alone sat over its own default, the pair did not, and the
  gas now takes the fix with the electricity.
- 4 rows, `household_declined`: the gas alone sat under its default, the electricity declined, and
  the gas now declines too (errs against the supplier, F11).
- 15 rows, `pair_above_default_after_the_decision_leg_contracted`: the electricity took its fix, the
  pair sits over its default, and the gas declines alone. These are the residue. The book's own
  post-fix count of rows whose `answer` differs from `household_answer` is also 15, which checks.

No row with a household answer has a null own position. There are no rows in 2022, a year with no
fixed renewals offered.

**What it means.** The fix works on the cases it was built for. The residue is the only route left
to two answers, and it is a bigger share than the prediction expected: 38% of the households, not
under 33%. Its cause is unchanged. The electricity answers before the gas offer is struck, so a
household that took the electricity fix cannot then decline both. Closing it needs a joint strike,
with the gas offer priced before the electricity answers (GAP in §7.5c). 13 households over nine
years is small beside the 183 who answer as one. The miss is recorded, and no threshold is moved
after the fact.

**Not decided here.** Whether the joint strike is worth building now is a ranking call for the
B13 lane. This finding does not gate S1 or B8: the verdict they were waiting for is now written.
