**Severity:** BLOCKING · **Lane:** C_customer_ops

**Rank:** top. It is the thing standing between this company and its first real per-customer
decision, and it was invisible until something tried to make one.

# `MAX_CHURN_PROBABILITY = 0.95` is harmless in a belief that is reported and fatal in one that is acted on: it makes the profit-maximising price unbounded

All claims `observed-with-evidence`.

## How it surfaced

`company/pricing/value_based_renewal.py` (landed today) chooses a renewal margin per customer by
maximising expected discounted contribution against the company's OWN churn estimate. Run over
the real 263-account book it priced **every single account between £60 and £200/MWh** against a
flat control of £2.00 — thirty to a hundred times — a **+63% median bill change**, and reported
that not one account was value-negative.

The maximiser is not wrong. It found what the model actually says.

## What the model actually says

`company/crm/churn_model.py`, measured directly (`estimate_churn_probability`, resi, tenure 4y,
3,100 kWh):

    price change   P(leave)
          +10%       0.140
          +50%       0.460
         +100%       0.860
         +200%       0.946
         +400%       0.950   <- MAX_CHURN_PROBABILITY

`MAX_CHURN_PROBABILITY = 0.95` is a hard cap and the curve saturates toward it. **Five percent
of every account is modelled as staying whatever it is charged.** Against that, expected value
`P(stay) x margin x volume` is monotone increasing in price without limit, and any maximiser
run against it prices to infinity — or, in practice, to whatever ceiling you happen to give it.

## Why nothing noticed for months

Because the estimate was only ever REPORTED. It is computed per renewal, scored against the
world's truth (`churn_estimate_error_pct`), published — and consumed by no decision anywhere in
the tree. A belief that is only reported can be out of range at its tails forever and look
perfectly healthy in aggregate; the mean error stays small because real renewals sit at ±10%,
where the curve is fine.

That is the transferable lesson and it is worth more than the fix: **the moment you try to make
a decision out of a belief, you find out whether the belief was ever load-bearing.** This one
had been graded for months and could not carry its first decision.

## The likely root cause, and it has already been fixed once today on the other side

`estimate_churn_probability`'s rate sensitivity is calibrated on GB **market-wide** switching
behaviour. A single supplier raising its own price 83% while the market does not is a completely
different event from the market moving 83% together — in the first case a cheaper alternative
exists and is obvious; in the second there is nowhere to go, which is exactly the 2022 collapse
in switching the calibration contains.

`50274434a` (PB3 b1, this morning) found and fixed **this same defect on the WIN side**: the
shared elasticity returns a flat crisis floor for negative savings, "a statement about the WHOLE
MARKET holding no cheaper alternative ... for a single supplier priced above the average the
premise is false by construction", and reading it straight "collapsed every dearer position onto
one value". The loss side still has it.

`inferred`, not observed: that the sensitivity is the wrong shape rather than merely the cap
being wrong. The cap is observed; the cause is the natural reading and has not been isolated.

## What must NOT be done

Move the cap so the arm behaves. That is goal-seeking against a calibrated belief (R12: a metric
is a diagnostic, never a target; R13: the baseline changes for fidelity reasons only, decided
blind to company P&L). The number that would come out is one chosen to make a pricing rule look
sensible, which is the exact inversion this project exists to avoid.

## What was done instead

The DECISION was bounded by what its belief can support, not the other way round.
`value_based_renewal.max_supported_rate_increase_pct()` derives a ceiling from the largest
single-step rise the published domestic cap has ever made — **+83.1%, 1 Oct 2022**, read from
the company's own cap module. Customers have never been observed responding to a bigger
one-step rise than the market itself has ever made, so the company may not price on a prediction
beyond it.

It bounds 151 of 263 accounts and it is **not enough**: within +83% the model is still monotone,
so 86 accounts still sit at the edge of what they are allowed. The comparison says so itself
(`fit_to_run: false`) rather than being read as a result.

## What would discharge this

A rate response that distinguishes a supplier-specific move from a market-wide one, and that
does not leave a floor of unconditionally captive customers. Then re-run
`python3 -m tools.couple_value_based_pricing`: if the verdict turns `fit_to_run: true` with
interior optima, the decision can be wired to the renewal desk. Until then it must not be, and
this document is why.

## Evidence

- `python3 -m tools.couple_value_based_pricing` — 263 priced, 263 differ from the control, 86 at
  a grid edge, median implied bill change +63%, `fit_to_run: false`.
- `company/crm/churn_model.py:58` — `MAX_CHURN_PROBABILITY = 0.95`; `:105` — the saturation
  elbow that approaches it asymptotically.
- The response table above, from `estimate_churn_probability` directly.
- `git log -1 50274434a` — the same defect, found and fixed on the win side this morning.
