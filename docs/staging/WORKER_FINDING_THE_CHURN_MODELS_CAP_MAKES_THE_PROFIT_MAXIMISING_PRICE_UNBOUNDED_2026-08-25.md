**Severity:** LATENT · **Lane:** C_customer_ops

**Severity moved BLOCKING → LATENT on 2026-08-25, and the reason is at the foot of this
document, not here.** BLOCKING was right while the instrument was untrustworthy: the churn
belief could not carry the first decision made out of it. The two captive floors are gone, the
maximiser now has interior optima on 255 of 263 accounts, and the belief error against the world
has flipped from −7.8pp to +0.5pp. What remains is a real defect that invalidates nothing
published and no control's verdict — the value arm is still not wired to the renewal desk, by
decision — which is LATENT's definition.

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

---

# 2026-08-25, later the same day: the mechanism is fixed, the arm is still not fit, and the reason has changed

**Severity: BLOCKING → LATENT** (the header at the top of this document carries the machine-readable value). The arm still may not be wired to the renewal desk. What has gone
is the specific defect this document was filed about; what remains is a different question and
saying so is the point of this section, because the paragraph above ("What would discharge
this") would otherwise be read as still describing the obstacle.

## What the discharge condition asked for, and what was done

> *"A rate response that distinguishes a supplier-specific move from a market-wide one, and that
> does not leave a floor of unconditionally captive customers."*

Both, and a third the search turned up.

**1. The captive floor named here.** `MAX_CHURN_PROBABILITY` 0.95 → 1.0. The asymptote is 1.0
because nobody is unconditionally captive. `_saturate_churn_probability` is unchanged; only the
constant it reads moved, and every estimate below the 0.9 elbow -- which is every estimate any
real renewal in this book has ever produced -- is byte-for-byte identical.

**2. A SECOND captive floor, larger than the first, one layer up and not in this document.**
`enriched_churn_estimate` returned `p * market_conditions_multiplier(year)`. That bounds the
estimate at the MULTIPLIER: in 2022 (m = 0.44) no customer could be given more than a 44% chance
of leaving, so **56% of every account was modelled as staying whatever it was charged** -- an
order of magnitude more captive than the 5% this finding was filed about, reached by a different
route, and it would have kept the maximiser unbounded on its own after the cap was fixed. The
multiplier scales an annual switching RATE, and rates compose through the survivor function, so
it now applies as `1 - (1 - p) ** m`. That is what the multiplier IS, not a device to remove the
floor: it agrees with the old form to first order where every real renewal sits (p = 0.10,
m = 0.44: 0.0440 before, 0.0453 now) and cannot bound the estimate away from 1.0 for any finite
m. Same fix on the passive path, which had the same floor.

**3. The rate response now reads the supplier-specific move.** `estimate_churn_probability`
takes `market_move_pct` and the sensitivity multiplies `rate_increase_pct - market_move_pct`.
The market move is DERIVED from the published Default Tariff Cap through the company's own cap
module (2022: +66.7%; 2023: −13.1%), and an unknown year nets nothing rather than fabricating a
move. **No new sensitivity constant was added** -- deliberately. A fresh "supplier-specific
sensitivity" would have been a free parameter nothing outside this company could settle, sitting
in the exact place a maximiser is about to read; the correction moves an EXISTING calibrated
sensitivity onto the quantity it was always meant to describe. That leaves a named
simplification (a sensitivity fitted to market-wide savings transferring unchanged to
supplier-specific savings) which is conservative in the direction that matters: it understates,
never overstates, how hard a customer punishes a supplier-specific rise.

Nothing was retuned. All three moves cost the company money and none can save it any, which is
the R13 test that matters here.

## What is now observed

`P(stay) x contribution` **turns over**, which is the property this document was really about:

    margin GBP/MWh    2      10      30      60     100     130     200     400    2000
    P(leave)       0.142   0.203   0.355   0.590   0.895   0.950   0.991   1.000   1.000
    expected       33.6    51.0    81.2    89.9    36.0    21.8     5.7     0.1     0.0

An interior maximum at ~GBP 60/MWh. Before, this sequence was monotone increasing to whatever
the last candidate happened to be.

Over the live book (`python3 -m tools.couple_value_based_pricing`):

|                          | when filed | now |
|--------------------------|-----------:|----:|
| accounts at a grid edge  |         86 |   8 |
| median implied bill change | +63%     | +52% |
| median belief error vs the world | −8.6pp | **+3.6pp** |
| mean belief error        |     −7.8pp | **+0.5pp** |
| under-estimating departures | 156/263 | 123/263 |

The sign of the belief error is the whole story and it has flipped. The company was
UNDER-estimating departures at its own chosen price -- it would have over-priced and been
punished -- and now sits marginally on the conservative side.

## What still stands in the way, and it is NOT this document's defect

`fit_to_run` is still false, on the second of its two clauses: the median implied bill change is
+52%. 255 of 263 accounts now have interior optima, so the maximiser is being bounded by the
BELIEF and no longer by the candidate list. The open question is therefore a different one:

**is the control a credible average player?** The flat rule is `TARGET_MARGIN_GBP_PER_MWH =
2.00`, about GBP 6.20 a year on a 3.1 MWh household, against GBP 58–98 a year of expected cost.
If that is well below what an average supplier charges, then the value arm "beating" it measures
nothing about inference -- it measures that the control is under-priced -- and the director's
frame ("there has to be a baseline to beat ... average behaviour is the control") is not yet
satisfied. That is the next piece of work and it is a MEASUREMENT, not a retune: the Default
Tariff Cap carries a published EBIT allowance, which is an external answer to "what does an
average supplier earn" that this company does not currently read anywhere in its tree.

## What would discharge the REMAINING block

A flat control set to a defensible external figure for average supplier behaviour, and a
two-arm comparison against THAT. If the value arm still moves the median bill by tens of
percent against a credible average player, the belief is still wrong somewhere and the arm
stays unwired. If it converges, the honest earnings test -- same book, same world, one run per
arm, scored on outcomes -- is what settles it.

## Evidence for this section

- `tests/company/crm/test_captive_floor_and_market_netting.py` -- 17 tests, three mutations
  verified to fire by hand: restoring `MAX_CHURN_PROBABILITY = 0.95` reds 3, dropping the market
  netting reds 4, restoring `p * m` reds 3.
- `python3 -m tools.couple_value_based_pricing` and
  `docs/observability/value_based_pricing_arms.json` for both tables above.
- `company/crm/market_conditions.py::market_rate_move_pct` for the cap-derived market move.
