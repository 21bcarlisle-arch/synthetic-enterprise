**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** EP8_adapter_dcc_duis (found on its LANE 3 DISCOVER draw; filed out, not folded in) · **Class:** measurements_that_mirror

# FINDING — the world estimates a new customer's consumption at exactly the truth, for up to twelve periods

`simulation/meter_reads.py:simulate_read` computes the estimated-read figure the billing engine
bills from. Its normal path is a three-point trailing mean over the customer's own confirmed actual
reads. Its `else` path is not:

```python
if trailing_actuals_kwh:
    estimate = statistics.mean(trailing_actuals_kwh[-ESTIMATE_TRAILING_WINDOW:])
else:
    # No history yet: the opening read taken at switch/onboarding is a
    # real physical value a supplier does obtain, not a forecast --
    # bootstrap the very first period from it.
    estimate = true_consumption_kwh
```

**The comment's justification is true of the first period and the branch serves every period until
the customer's first actual read.** `trailing_actuals_kwh` is appended to only on an actual read
(`company/billing/monthly_bill_assembly.py:537`), so a customer whose reads keep failing to arrive
re-enters the bootstrap branch every month and is "estimated" at exactly their true consumption
every time.

This is the honest-gap-comment shape: the note names the limit of the case it was written for, and
the code applies it to a case the author was not looking at.

## Measured — `docs/reports/run_output_latest.json`, all 10,924 rows, HEAD `38e22f470`

```
estimated reads                                          6,852 of 10,924
estimate exactly equals round(true_consumption_kwh, 2)   1,095   (16.0% of estimated)
  before the customer's first actual read                1,072
  after an actual read (coincidence, not this branch)        23
consecutive_estimated_count on the exact rows            1..12, spread evenly (148 at 1 ... 66 at 12)
customers who never receive an actual read at all        9 of 251
```

Twelve consecutive estimated periods, each estimated perfectly. The estimated bill is then priced by
scaling settlement records by `est_kwh / true_kwh` (`monthly_bill_assembly.py:541`) — a ratio of
exactly 1.0 — so the estimated bill equals the true bill to the penny.

## It refutes a claim the billing module makes about itself

`company/billing/monthly_bill_assembly.py:44`, the module's own epistemic note:

> *"The one place a true figure drives a DECISION is `_resolve_catchup`, and it does so only once an
> ACTUAL read has arrived — at which point the real consumption is genuinely known to the supplier,
> which is what a catch-up bill IS."*

For 1,072 rows the billed amount is driven by `estimated_consumption_kwh`, which **is** the true
figure, **before** any actual read arrived. The sentence is correct about `_resolve_catchup` and
wrong about the module — the second true-driven decision is the estimated bill itself.

I am not filing this as an epistemic-wall breach. The `true_*` fields legitimately cross for
divergence analytics under the treatment `tools/meter_read_port.py` documents, and `simulate_read`
is world-side code entitled to read world state. **The defect is that a SUPPLIER-side conclusion is
computed in the world from a figure the supplier does not have** — a fidelity failure, and one the
wall was never going to catch, because nothing crosses that is not allowed to cross.

## What it costs

```
                              n       median rel err     mean rel err
all estimated reads         6,852          17.274%          45.906%
  before first actual read  1,072           0.001%           0.001%   <- exact by construction
  after  an actual read     5,780          21.901%          54.420%
```

The perfect-by-construction population is 15.6% of every estimated read and drags the headline
estimated-vs-actual divergence from 21.9% to 17.3%. Anything built on that divergence — bill-shock
incidence on estimated bills, catch-up rebilling magnitude, the D3 `billing_basis` analytics,
`company/compliance/population_sanity.check_estimated_read_rate`'s band — is biased toward the
supplier looking more accurate than it is, by a population that was not estimating at all.

It also lands hardest exactly where a real supplier is worst: a **new** customer, with no read
history, is the one this world estimates perfectly.

## What is next

1. **Decide what a supplier actually does with no history.** This is the knowledge-first question
   and it should not be answered by picking a rule. A real supplier estimates from the EAC/AQ on the
   registration flow, or from a TDCV band by property and fuel — both of which this company already
   has (`company/crm/property_model.estimated_annual_elec_kwh`, and the TDCV bands
   `population_sanity` already cites). Neither needs the truth.
2. **Do not simply delete the branch** — it would fall through to a mean of an empty list. The
   replacement has to name its source.
3. **The control this wants** is keyed to the property, not to today's count: *no estimated read
   equals the true consumption it is standing in for*, over the whole run, with the 23
   coincidental rows either explained or given a tolerance that cannot swallow the 1,072. A control
   pinned to "1,095" goes green the moment the bug gets worse in a different shape.
4. **EP8 makes it unwritable rather than fixed.** With estimation moved company-side per
   `docs/design/EP8_ESTIMATION_CUT_DISCOVER_2026-09-07.md` §5, this branch has no ground truth in
   scope to reach for. That is the better repair and it is gated behind EP6; item 1 should not wait
   for it.

## The control that would have caught it

Nothing asserts any relationship between `estimated_consumption_kwh` and `true_consumption_kwh` —
the pair is published on every row and read only by divergence analytics that treat whatever they
find as the answer. `check_estimated_read_rate` measures how MANY reads are estimated and never how
WELL, so a population estimating perfectly reads as healthy. **A measure of the rate of a thing is
blind to the quality of it**, and both were needed here.
