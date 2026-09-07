**Severity:** RECORDED · **Lane:** W2_customer_generator · **Class:** MEASUREMENTS_THAT_MIRROR

# The 158 unlabelled refusals are the drawn gas book, and the census that exists to explain them was misreading 137 electricity legs

**Found and repaired:** 2026-09-07, delivery seat, claim
`the-arm-prices-a-quarter-of-its-book-and-the-refused-three-quarters-are-svt`.
**Landed in** `simulation/run_phase2b.py` (`resolved_tariff_type`, three call sites) and
`tools/run_value_cycle_ab.py` (`product_label_by_account_class`).
**Held by** five mutation-proven controls in
`tests/simulation/test_the_tariff_type_read_has_one_home.py`; the two AST controls were poisoned by
restoring each historical spelling and both fired.

---

## What was asked, and the answer

`docs/observability/value_cycle_ab_leg_id_fixed_2026-09-07.json` reads

```
renewal_funnel.value_arm.product_not_upliftable_by_tariff_type = {"'svt'": 1350, "None": 158}
```

**The 158 are the renewal terms of 18 curriculum-drawn GAS legs.** Not legacy records, not a
pre-2026-08-30 residue: they are produced by every run of the current tree, and they appeared the
day gas was admitted to the arm.

## How that is established, and it is three independent readings agreeing

**1. By construction.** `population_draw.to_customer_dict` renders `"tariff_type"`
unconditionally, so a drawn or won record carries the key PRESENT and `None`. `run_phase2b` built
electricity schedules with `c.get("tariff_type") or "fixed"` — repaired 2026-08-30 — and gas
schedules with `c.get("tariff_type", "fixed")`, whose default a present key never reaches. The gas
builder stamps that `None` on every term it emits; the term loop reads it back with the same
defeated spelling; `UPLIFTABLE_TARIFF_TYPES` refuses it; the funnel logs `repr(None)`.

**2. By census.** 18 gas records carry the key present and unset (105 gas legs, 87 omit it). Their
unclipped term count over 2016–2025 is 176, of which the term loop's own `continue` for churned
billing accounts drops 18 — leaving 158.

**3. By difference.** The `None` bucket is absent from
`value_cycle_ab_gate_reverted_2026-09-07.json`, which reverted the gas gate, and present at
exactly 158 in both artefacts that admit gas. One variable, one change.

## The second half, which was not asked for and is worse

`product_label_by_account_class` exists *specifically* to explain this bucket — it censuses the
guard's own input off the roster. To do that it had restated the world's read as
`record.get("tariff_type", "fixed")`, "spelled exactly as `run_phase2b` spells it at its two
schedule-building call sites". That sentence was true when written and stopped being true on
2026-08-30, when one of the two call sites was repaired and this one was not.

For eight days the same artefact published both of these:

| block | what it said about the found electricity book |
|---|---|
| `product_not_upliftable_by_tariff_type` | 158 unlabelled refusals, all gas |
| `product_label_by_account_class` | 137 electricity legs at `resolved_tariff_type: null`, `the_guard_admits_it: false` |

The builder labels those 137 legs `fixed` and the guard admits them. `found_accounts_the_guard_would_admit`
published **83**; the corrected read returns **137**. The derived verdict
`a_found_account_can_reach_the_product_gate` did not flip — it was already True on the strength of
the 83 gas legs that omit the key — so nothing went red, and the block that exists to tell a reader
whether the found book can ever be priced was understating the answer by 54 accounts while looking
exactly like a working diagnostic.

**Two blocks of one file, each internally consistent, disagreeing about one read.** This is the
same shape `tools/product_gate_refusal.py` was built on 2026-09-04 to stop — a sentence about the
world copied to a second place and going stale there — and it survived that repair because the copy
was a line of code rather than a paragraph of prose, and nobody looks for prose in an expression.

## The repair

`simulation.run_phase2b.resolved_tariff_type(record, *, successor=False)` is now the only place
either spelling exists. It returns what that record's own schedule builder stamps on every term:
`or "fixed"` for electricity, `.get(..., "fixed")` for gas, and `"fixed"` for a successor leg whose
call site passes no `tariff_type` at all and therefore never consults the record. All three call
sites and the census call it.

**The gas defect is preserved, deliberately.** Whether the drawn gas book should carry a decided
product is a curriculum question owed a fidelity determination, and this lane has already measured
what closing it would do to the arm's denominator (+158 renewals). Deciding it here would be a
world change made by someone who has seen the company result, which R13 forbids. It is filed as
`SEAT_DECISION_AN_SVT_HOUSEHOLD_IS_NOT_A_DECISION_THIS_ARM_DECLINES_2026-09-07.md` §4 instead.

## What is next

1. **The gas fidelity determination** (§4 of the decision above). `DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md`
   settled the electricity half on 2026-08-28 and did not reach gas; its §(a) reasoning — an
   account the company won or drew arrived by taking a deal, so its *opening* term is fixed —
   applies unchanged to a gas leg. Closing it deletes
   `test_the_two_commodities_are_read_differently_and_that_is_the_finding`, which is why that
   control asserts the difference rather than the value.
2. **`billing_accounts_whose_legs_disagree_about_labelling` is now live, not latent** — 83
   accounts whose gas leg omits the key while their electricity leg carries it unset. Since
   2026-09-07 both legs reach the product gate, so one account is priced on one fuel and refused
   on the other for a reason that is a record shape rather than a product.
3. **Re-run the A/B** so the published artefact carries the corrected census. The funnel counts do
   not move — the world is unchanged — but `found_accounts_the_guard_would_admit` goes 83 → 137.
