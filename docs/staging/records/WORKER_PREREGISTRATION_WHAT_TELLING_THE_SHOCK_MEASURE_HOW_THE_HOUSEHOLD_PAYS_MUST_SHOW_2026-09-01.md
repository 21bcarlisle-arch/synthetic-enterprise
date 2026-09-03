# [WORKER PREREGISTRATION] What telling the shock measure how the household pays must show

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`
**Filed:** 2026-09-01, **before the change and before the run.** Nothing below was written after a result.
**Knowledge:** `docs/market_research/what_bill_shock_is.md` (definition, already established and not
re-opened here). **Finding:** `WORKER_FINDING_THE_WORLD_KNOWS_HOW_EACH_HOUSEHOLD_PAYS_AND_BILL_SHOCK_
IS_THE_ONE_ORGAN_NOT_TOLD_2026-09-01`.

## The change, in one line

`saas/bill_generator.generate_bill()` learns **how the household pays**, and every bill carries which
of the two definitions applies to it. **The shock arithmetic does not change.**

    generate_bill(customer_id, records, contract_type, previous_bill_total_gbp,
    -              segment, commodity)
    +              segment, commodity, payment_channel=None)

    bill["payment_channel"]         # "direct_debit" | "standard_credit" | None
    bill["bill_shock_population"]   # "payment" | "bill" | "out_of_scope" | "unknown"

Threaded from `simulation/run_phase4c_on_phase2b.py` (world side, where the channel already lives)
through `company/billing/monthly_bill_assembly.build_monthly_bills` as an **injected mapping** — the
shape `saas/opex_ledger.py` already uses for this exact field, and for the same reason: the company
may know how its own customers pay it (it set the mandate up with them), but it may not reach into
`simulation.household_segments` to find out.

## Why this is deliberately the smallest possible step

The finding owes four things. This is only the first, on purpose: **(b) the wiring, (c) prepayment,
the definition split, and the population bound are four changes to one published figure, and three of
them landing together would be unattributable.** This one is chosen first because it is the only one
of the four that moves **no** published number — which makes it the one whose prediction can be
falsified cleanly.

## The predictions

**P1 — NOTHING MOVES. This is the whole point and it is the falsifier.**
`bill_shock_pct`, `bill_shock_baseline_gbp`, `clarity_score`, `avg_bill_shock_pct`, contact volume,
satisfaction, churn, net — **every one byte-identical to the `3df8f7400` run.** If any published
figure moves, the change did more than it claimed and must be reverted rather than explained.

**P2 — the split of the existing shock events by population.** Measured now, on the published
`3df8f7400` book, by resolving each event's account through `registered_point` and applying the
feed this commit adds:

| population | definition that applies | events | share |
|---|---|---:|---:|
| `payment` (direct debit) | **the change in the amount collected** — the bill is not what they pay | 2,238 | **70.8%** |
| `bill` (standard credit) | **the bill** | 912 | 28.9% |
| `unknown` (2 SME accounts) | neither: the definitions are domestic | 11 | 0.3% |

**So 70.8% of every "bill shock" this company has ever published is measured on households the
established definition says the bill does not shock.** That is the number this commit exists to make
visible, and the run must reproduce it exactly — 2,238 / 912 / 11 — unless the book itself changes,
because the mapping is deterministic in `(customer_id, commodity)`.

*A first draft of this table said 70.1% / 29.9%, and it is corrected here rather than silently.
That draft keyed every account on the electricity share, including gas accounts. It is the wrong
keying: `payment_channel_for_customer` is fuel-specific by construction (72% DD electricity, 75%
gas) and `arrears_engine` and `final_bill_outcome` both key on the account's own fuel. Using the
electricity default would have made the fourth organ disagree with the other three about how one
household pays — which is the defect this commit exists to end, one level down.*

**P3 — book-level channel mix unchanged at 178 DD / 71 standard credit / 2 non-resi over 251
accounts (70.9% / 28.3% / 0.8%)**, because nothing about the channel model is touched. Against a
published GB mix of ~74/13/13 that is close on DD and 2.2× on standard credit, **because our world
has no prepayment channel at all** — which is (c), and is NOT repaired here.

*(The finding's own 68.1%/31.9% is the same book under the electricity-default keying corrected
above; it does not disagree with this, it counts differently.)*

**P4 — `bill_shock_population` is `"unknown"`, never silently `"bill"`, when no channel is supplied.**
Every legacy and test caller passes no channel. The honest value for "we were not told" is its own
value; defaulting it to either definition would publish an unmeasured attribution as a measured one,
which is `a_default_zero_parameter_turns_an_unobservable_cause_into_a_published_measured_zero`
wearing a string's clothes.

**P5 — `"prepayment"` maps to `"out_of_scope"` and that branch is unreachable in this world today**,
because `PaymentChannel` has two members. It is written anyway, and its unreachability is stated on
the surface rather than left for a reader to discover, because the alternative — no branch at all —
is what let prepayment be folded into standard credit in the first place.

## What would refute this, stated before the run

- Any movement in `bill_shock_pct` or any downstream figure refutes **P1** and the change is wrong.
- A `payment`/`bill` split materially away from 70/30 refutes **P2** and means the mapping in the run
  is not the mapping three other organs already use.
- A default of `"bill"` or `"payment"` anywhere a channel was not supplied refutes **P4**.

## What this commit explicitly does NOT do

1. **It does not change what is measured for either population.** A DD household's `bill_shock_pct`
   is still the difference between two bills it does not pay. The field now says so; it does not yet
   stop doing it. That is the next commit, and it moves figures.
2. **It does not add prepayment**, or exclude it. (c), separately.
3. **It does not touch the DD amount.** Making the collected amount a modelled quantity from an
   estimated annual consumption is the director's own correction and a separate build with its own
   knowledge work behind it — explicitly out of scope by instruction.
4. **It does not publish a bound.** (d), separately.
