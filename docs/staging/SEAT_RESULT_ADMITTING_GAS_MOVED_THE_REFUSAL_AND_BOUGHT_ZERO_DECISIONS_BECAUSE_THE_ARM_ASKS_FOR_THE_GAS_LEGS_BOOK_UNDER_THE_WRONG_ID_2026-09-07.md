**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the renewal arm prices no gas)

# RESULT — admitting gas moved the refusal and bought zero decisions, because the arm asks for the gas leg's book under the wrong id

The gate is widened and the exclusion is closed: `not_the_arms_commodity` is **0**. Not one
additional renewal is priced, not one additional account is reached, and the reason is a defect
the gate was hiding.

The prediction written before the run is
`SEAT_PREDICTION_WHAT_ADMITTING_GAS_TO_THE_ARM_WILL_AND_WILL_NOT_BUY_2026-09-07.md`. **Prediction 1
was wrong in the direction that matters** — I predicted the renewal count would move by most of the
346 and the account count by less. The account count moved by zero, and so did the decision count.
Kept beside the result rather than revised.

## The one-variable comparison

Two full three-arm runs, **same world** (`world_identity.digest = 39a192ce04c1eda8`), same seed,
same tree, same 2,039 offered renewals. The only difference is `UPLIFTABLE_COMMODITIES`, reverted
in-process for the before-run (`/tmp/ab_gate_reverted.py`, patching the three modules that bound it
by value) so no file was edited and the shared tree could not be caught mid-revert.

| value-arm funnel stage | BEFORE (electricity only) | AFTER (electricity + gas) | Δ |
|---|---|---|---|
| `acquisition_term` | 252 | 252 | 0 |
| **`not_the_arms_commodity`** | **337** | **0** | **−337** |
| `product_not_upliftable` | 1,350 | 1,508 | **+158** |
| `no_observed_history` | **0** | **179** | **+179** |
| `declined` | 6 | 6 | 0 |
| **`priced`** | **94** | **94** | **0** |
| accounts priced | 66 | 66 | **0** |

`158 + 179 = 337`. Every gas renewal is refused one gate further down. New accounts the arm reaches
only because of gas: **none**.

And so nothing downstream moves either — identically, not approximately:

| | BEFORE | AFTER |
|---|---|---|
| `decisions_scored` | 54 | 54 |
| `accounts` | 38 | 38 |
| `detectable_excess` | 0.090496 | 0.090496 |
| `observed_excess` | 0.052760 | 0.052760 |
| `observed_share_of_what_was_detectable` | 0.5830 | 0.5830 |
| `decisions_needed_for_the_observed_effect` | 159 | 159 |

**A fix that returns the identical number refutes the diagnosis, not the symptom.** The diagnosis on
the doorbell was "the arm is fitted to electricity and has never been fitted to gas". It is fitted
to gas now — the gate, the churn `fuel`, the cost-to-serve cadence, the standing-charge table and
the cap ceiling all take the renewal's own commodity, each proved by reverting it (`3088f8c71`).
That was necessary and it was not sufficient, and nothing in the renewal count could have told the
difference.

## The 179, and it is not "this account has no gas history"

`simulation/run_phase2b.py:1539` calls the chain with `billing_account = household_of(cid)`.
`simulation/household.household_of` strips the gas-leg suffix, so a gas renewal on supply point
`PROS-2019-0302g` reaches the arm as `account_id="PROS-2019-0302"`. The world's settlement rows
carry the **leg** id (`simulation/hedged_settlement.py` stamps `customer_id` unchanged), so the gas
rows are filed under `PROS-2019-0302g`.

`observed_account_state` filters `r.get("customer_id") == account_id`. For a gas renewal that
matches only the ELECTRICITY leg's rows — which the commodity filter then correctly rejects. Run
against the world's own two id shapes:

```
gas leg id      : PROS-2019-0302g
billing_account : PROS-2019-0302     <- what run_phase2b passes as account_id

observed_account_state(account_id='PROS-2019-0302',  commodity='gas')         -> None   <-- no_observed_history
observed_account_state(account_id='PROS-2019-0302g', commodity='gas')         -> eac_kwh=10800
observed_account_state(account_id='PROS-2019-0302',  commodity='electricity') -> eac_kwh=3000
```

So **not one of the 337 gas renewals can find its own book**, and the 179 is that, exactly. It is
an id-space mismatch between the household/billing key and the supply-point key, and the commodity
gate was standing in front of it: while the arm refused gas at the commodity, the lookup was never
reached and the mismatch could not show. It is a latent defect that the repair made visible, which
is the repair working.

**This was invisible to the renewal count and would have been published as a win.** 346 renewals
moved out of an exclusion the doorbell called "a gap in our code". They moved into two other
refusals. The drawn work said it in advance — *"MEASURE the gain in independent decisions, never
infer it from the renewal count"* — and that is the only reason it was caught.

## The 158 are not a defect

They are gas legs on `svt`/unlabelled products — the same ceiling the electricity book has, and a
fact about the market rather than about our code. Only a household on a fixed deal has a struck
renewal rate any arm can move. No repair reaches them; winning them onto a fixed deal is an
acquisition decision and not this arm's.

## What is owed next, and it is one filter

`observed_account_state` should match a record to the account the way the supplier bills it, not by
string equality: `_billing_account_id(r["customer_id"]) == account_id`. That helper already exists
company-side in `saas/customer_reaction.py` and encodes exactly this ("`C1g` and `C1` both bill
under `C1`"), so no new mechanism is needed and no wall is crossed — a supplier knows which of its
own supply points bill under which account.

**Not landed here, deliberately.** It changes what the pricing chain charges, and the only honest
measurement of it is another one-variable pair of full runs (~50 minutes each). Landing a pricing
change on the strength of a unit test, with the funnel unmeasured, is the shape this project keeps
paying for. The next invocation has the fix named, the before-artefact on disk to compare against
(`value_cycle_ab_gas_admitted_2026-09-07.json` is now the BEFORE for that change), and the
prediction to make first.

Expected on that run, filed now: `no_observed_history` falls from 179 toward 0, `priced` rises from
94, and `decisions_scored` rises from 54 — the first real increase in the arm's decision count that
this thread has produced. If `priced` does not move, the gas legs are on products the arm cannot
price and the 158 is the whole story.

## A note on the published feed, which is not a valid before

`site/data/value_arms.json` records 1,953 offered renewals, 120 priced, 346 at
`not_the_arms_commodity`, 86 `decisions_scored` and `detectable_excess` 0.0715. **This world offers
2,039, prices 94, had 337 at that stage, scores 54 and detects 0.0905.** The published figures come
from a different and older world; the doorbell's own premise numbers (346, 120, 86, 0.0715) are
that superseded run's. Comparing this run against the page would have shown `priced` falling
120 → 94 and read as the gas change making things worse, when the gas change moved neither number
at all. The before/after published above is the one-variable pair and nothing else.

## Artefacts

- `docs/observability/value_cycle_ab_gate_reverted_2026-09-07.json` — BEFORE, gate reverted in-process, commit `3088f8c71`
- `docs/observability/value_cycle_ab_gas_admitted_2026-09-07.json` — AFTER, gate widened, commit `d1aebbd79`

Both stamp `world_identity.digest = 39a192ce04c1eda8` and both clock audits PASS.
