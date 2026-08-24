**Severity:** LATENT · **Lane:** W2_customer_generator

# The renewal profitability uplift can never fire: it groups settled records by a key no settlement record carries

**Found by:** enumerating every consumer of `run_phase2b.all_records` while making the run
incremental, 2026-08-24. Not the subject of that work, and not fixed there — the fold it landed
preserves this behaviour exactly, because a refactor that quietly turns a dead path live is a
behaviour change wearing a performance fix.

## The mechanism

`company/crm/customer_profitability.py::estimate_prior_term_net_margin` decides how much of a
renewal uplift a net-negative customer gets. It filters the supplier's settled records to one
customer before `term_start`, then:

```python
prior_term_starts = {r.get("term_start", "") for r in eligible if r.get("term_start")}
if not prior_term_starts:
    return None
```

**No settlement record carries `term_start`.** `simulation/hedged_settlement.py` documents the
17 keys it returns and `term_start` is not among them; `run_phase2b` then adds `bad_debt_gbp`,
`treasury_cash_balance_gbp`, `data_regime` and `commodity`, and nothing else. Every
`term_start` in `run_phase2b.py` is on a LOG dict — the demand-estimation log, the churn log,
the journey log — never on a settled period.

So `prior_term_starts` is always empty, the function always returns `None`, and
`renewal_unit_rate_uplift` returns `0.0` for every renewal it is asked about. The eligibility
rules above it (`UPLIFTABLE_TARIFF_TYPES`, `MIN_TERM_INDEX_FOR_UPLIFT`, the commodity check) are
all reachable and all irrelevant, because the branch under them cannot produce a number.

## What is NOT established, and why that matters here

**Inferred, not observed:** I have not run the campaign with an instrumented
`estimate_prior_term_net_margin` to confirm the return is `None` on every real call. The
reading above is from the code and from the record's key list. That is exactly the kind of
reasoning this project has been wrong with before, so before anyone repairs this, MEASURE it —
count the calls and the non-`None` returns over one real run.

Nor is it established which way the repair should go. There are two, and they are not the same
decision:

1. **Stamp `term_start` on settlement records.** Cheap, and it makes the existing policy live —
   which is a change to what the company charges renewing customers, on a book that is currently
   being grown toward 200. That is a pricing behaviour change, not a bug fix, and it should be
   landed deliberately with its effect on published margin measured, not slipped in.
2. **Delete the policy.** If nothing has depended on it since it was written, the honest reading
   may be that the supplier does not do this, and the code is a dead limb.

Nothing here says which. What it says is that the site currently publishes margin from a company
whose stated renewal policy has never once applied.

## Not fixed here (SELF_INTERRUPT_DISCIPLINE)

Queued. The machine is not blocked, no published figure is wrong as a result — the figures are
what the company actually did — and the repair is a pricing decision with a measurement in front
of it.
