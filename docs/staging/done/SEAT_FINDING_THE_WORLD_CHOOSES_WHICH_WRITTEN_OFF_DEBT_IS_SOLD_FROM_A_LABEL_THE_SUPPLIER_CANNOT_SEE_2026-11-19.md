**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `KNIFE3_wall_crossing_paydown`

# The world chooses which written-off debt is sold, from a label the supplier cannot see

Found while moving the DCA placement date company-side (KNIFE3, 19 Nov). That slice is done. This
part is not, and it is named here so that it is not read as covered.

`simulation/arrears_engine._post_writeoff_stages` and `post_write_off_recovery_gbp` decide whether a
written-off debt is **sold** to a debt purchaser or **worked** by an agency. They decide it from
`debt_archetype(...) == "AVOIDANT"`, which is read off the household's hidden
`income_stress_trajectory`. Selling or working a debt is the supplier's choice. Making that choice
from hidden household state is access, not inference.

**Why it is LATENT and not live:** the sale branch fires only when
`q3_debt_sale_price_share_of_face` has a value. The register holds `None` with a reason, so every
written-off debt is worked by an agency today. On the `run_output_8a300fa561` replay no `SOLD`
stage exists. Nothing published moves because of this today.

**When it goes live:** the day the register gets a sale price. From that day, the supplier would
sell exactly the debts that the world knows are persistently stressed. No real supplier has that
signal.

**What moving it takes (a design choice, not a mechanical move):** the company needs its own
sell-or-work rule, built from what it can observe. Examples are contact attempts with no answer,
failed arrangements, and the age and size of the balance. The world would keep the household's
response. This needs the knowledge page first (K8): what GB suppliers publish about debt sale
versus agency placement. `docs/market_research/debt_and_collections.md` is the place to start. It
should be done before any sale price is wired, and not at the same time.

## Done (2026-11-19, the commit that moves this file)

The choice is the company's now. The knowledge page came first: `docs/market_research/debt_and_collections.md`
s.7.7. It found no published GB rule for WHICH debts a supplier sells, and no energy sale price.
`company/billing/collections_journey.sells_written_off_debt` sells only when the offered price per GBP
is above the company's own expected post-close recovery (`cash_forecast_provision.PRIOR_POST_CLOSE_RECOVERY`,
0.122). Agency commission is a GAP and is not deducted, so the rule leans against selling (F11). The
world asks through `company/interfaces/collections_communication` with the register's price, and keeps
the proceeds. `_post_writeoff_stages`, `post_write_off_recovery_gbp`, `arrears_stages` and
`ic_arrears_stages` no longer take an archetype.

Pre-registered at /var/tmp/k3sell/PREDICTION.txt. All three held on `run_output_8a300fa561`.
- P1: at no price, the ledger and maps are cmp-equal.
- P2: at 0.07 (inside the published range) nothing is sold and the ledger is cmp-equal. The old rule
  would have sold 3 of 253 debts (GBP 57.21), chosen by hidden stress.
- P3: at 0.15, all 215 terminal stages are SOLD.

Still owed, and named here: a per-debt rule built from contact and arrangement history. The company
has no per-debt recovery estimate yet, so today's rule is the same for every debt.
`final_bill_outcome` still uses `debt_archetype is None` to mean "no trajectory was supplied"; it no
longer chooses anything with it.
