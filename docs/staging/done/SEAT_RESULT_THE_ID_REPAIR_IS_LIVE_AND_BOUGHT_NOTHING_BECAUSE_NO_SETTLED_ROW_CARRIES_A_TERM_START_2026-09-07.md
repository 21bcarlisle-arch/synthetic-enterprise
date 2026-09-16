**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the renewal arm prices no gas) · **Class:** no_caller_and_never_runs

# RESULT — the id repair is live and bought nothing, because no settled row carries a term_start

The one-variable pair asked for by the Lane 0 item, run and graded. **The pre-registered
prediction is REFUTED, and so is the fallback reading it offered.**

## The pair

Same command both legs, same fast-mode world, differing only in the one line landed in
`28ba48dd4`:

```
python3 -m tools.run_annual_report --fast --save-json <leg>.json --output <leg>.md
```

Counted off `rate_decomposition_log` (`cause == "profitability_uplift"`), because
`profitability_uplift_log` never reaches the saved payload — see
`SEAT_FINDING_WRITER_3S_OWN_LOG_IS_DROPPED_AT_THE_REPORTING_REDUCTION_...`.

| | decomposed renewals | writer 3 firings | every cause present |
|---|---|---|---|
| BEFORE (pre-fix) | 1,878 — 1,516 elec, 362 gas | **0** | margin_surcharge 127, portfolio_premium 1,847, price_cap 106 |
| AFTER (fixed) | 1,878 — 1,516 elec, 362 gas | **0** | margin_surcharge 127, portfolio_premium 1,847, price_cap 106 |

Byte-identical. **An identical number refutes the diagnosis, not the symptom**, so the writer
was asked directly rather than reasoned about.

## Grading the prediction, beside the claim

> *"the count of `profitability_uplift` entries rises from its electricity-only level"* —
> **REFUTED.** It did not rise. The count is 0 in both legs.

> *"If the entry count does NOT rise, no gas leg in this world had a net-negative prior term,
> and that is the finding instead."* — **ALSO WRONG, and wrong in a way worth keeping.** The
> fallback assumed a positive electricity-only baseline to rise from. There is none. Writer 3
> fires **0 times on electricity too**, so it was never unreachable on *half* the book — it is
> unreachable on all of it, and the id was not the binding constraint.

The item's own framing inherits that error: "DONE is the entry count measured against the
electricity-only level" presumes an electricity-only level above zero. Measured, it is zero.

## What is actually stopping it, measured

`/var/tmp/se-writer3/why_zero.py` patches `compute_profitability_uplift` in the module that
owns it — the chain holds a reference to `renewal_unit_rate_uplift`, which calls it as a module
global, so the patch is on the live path — and records what the writer read. Truncated to
2016–2019, because this is a cause split and not a level:

```
writer 3 asked 78 times  (53 electricity, 25 gas)
{"None: rows matched but none carries term_start": 78}
sample: {"cid": "C1", "commodity": "gas", "prior": null,
         "matched_rows": 365, "rows_with_net_margin": 365,
         "rows_with_term_start": 0, "distinct_term_starts": 0}
```

**78 of 78.** Every settled row the writer matched carries `net_margin_gbp` and not one carries
`term_start`, so `prior_term_starts` is empty and `estimate_prior_term_net_margin` returns
`None` before any margin is summed — for every account, both fuels. That is
`site/data/proof.json`'s FINDING 7 ("writer 3 of five is structurally dead in production,
fail-open through three layers, mutation-proved") still live, and the id mismatch sat
downstream of it the whole time.

`simulation/settlement_daily.CARRIED_FIELDS` already lists `"term_start"` among the fields a
day carries from its first record. The fold is ready for a field the writers never stamp.

## The repair IS live, and it was still worth landing

The same probe line proves it. Asked as `C1` for `commodity="gas"`, the filter matched **365
rows** — one year of daily gas settlement for a leg the world files as `C1g`
(`simulation/household.GAS_LEG_ID_SUFFIX`; the roster mints `C1`/`C1g` for one property). Under
`==` that count is 0. So the gas half of the book is now reachable by the writer that reprices
it, and stays unreachable-by-construction if the repair is reverted — which is what
`test_every_commodity_writer_3_reprices_can_reach_the_book_it_settled_itself` holds, poison-round
proved.

Reachable is not the same as firing. Both had to be true and only one of them now is.

## The eligibility funnel, so the next pass does not re-measure it

From `account_state_log` (2,098 rows, full window):

- `tariff_type`: svt 1,394 · fixed 528 · absent 176 — writer 3 admits `{fixed, pass_through}` only
- `term_index == 0`: 251 — the acquisition term, excluded by `MIN_TERM_INDEX_FOR_UPLIFT`
- **296 renewals clear every eligibility gate** (186 gas, 110 electricity) and reach the prior-term
  lookup. All 296 get `None`.

## What is next

1. **Stamp `term_start` on settled rows** in `simulation/hedged_settlement.py` and
   `simulation/gas_settlement.py`. Both already take it as an argument and neither writes it to
   the record. This is a world-side change to the shape of the book, so it needs its own
   one-variable pair and its own pre-registration — not folded into this one, or the two causes
   become unattributable again in exactly the way the deferral that produced this item avoided.
2. **Then re-run this pair.** The 296 eligible renewals are the population; the firing count and
   its commodity split are the measurement. Predict before running.
3. **Writer 2 fires 127 times on the same book** (80 electricity, 47 gas) reading a *different*
   source for the same question — `prior_term_margin_gbp` handed down by the world, not the
   settled book. Two writers four lines apart answering "was the prior term loss-making" from
   two sources, 127 against 0. Which one the supplier means is a definition question and belongs
   settled before either count is published.
