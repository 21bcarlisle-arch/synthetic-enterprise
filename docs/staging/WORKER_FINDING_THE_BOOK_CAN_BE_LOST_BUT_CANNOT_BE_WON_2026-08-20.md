**Severity:** LATENT · **Lane:** W2_customer_generator · **Atom:** PB3_book_growth_as_earned_outcome

# The book can already be lost. It cannot be won. Growth is a coin flip no company decision can move

DISCOVER/FRAME output for PB3. **PB3 cannot BUILD** — it depends on PB2, which is level 0 and
parked, which depends on PB1, also level 0. What follows is the design work that is available
now, and it turns out PB3's premise needs restating before anything is built.

## The atom says the wrong thing, in an interesting way

PB3's stated gain is *"book size becomes an outcome the company can fail at, instead of a
number that goes up."* Half of that is already false, and the half that is true is worse than
the atom describes.

**Losses are real and priced.** `simulation/market_switching_propensity.py` (W2_3, L1) drives
churn from the *savings a customer could get by switching* — a properly researched piecewise
elasticity anchored on DESNZ 2015–2025, with the 2022 "nowhere cheaper to go" effect encoded.
It reaches customers through `simulation/customer_events.py`. Price badly and the book shrinks.

**Gains are a constant.** Measured, not read:

```
GAIN side — win rate across 2000 rolls
   resi: 0.218      sme: 0.218
   roll_acquisition(segment: str, rng_seed: str) -> bool
```

`saas.growth_mandate.roll_acquisition` takes a segment and a seed. That is all. The multi-stage
funnel that supersedes it (`simulation/acquisition_funnel.py`) is better in every other way —
real stages, real per-stage cost, real calendar spacing, a statutory 14-day cooling-off — but
every one of its stage rates is a function of **segment alone** (`_quote_to_application_rate`,
`_credit_check_to_onboarding_rate`), and `_cooling_off_survival_rate` adds only the date.

Neither module contains the string `competitor`. Confirmed by grep, then by running them.

## So the failure mode is not "a number that goes up"

It is an asymmetry, and it distorts the whole strategy space the company operates in:

> **The company's price is the only lever on book size, and it works in one direction.**

Price high and you lose customers to a competitor field that can see your price. Price low and
you stop losses — but you cannot *win* share, because acquisition cannot see your price either.
A company with a terrible offer acquires at 21.8%. A company with the best offer in the market
acquires at 21.8%.

Two consequences worth naming before anyone builds:

1. **The optimum the simulation currently rewards is defensive.** There is no modelled return
   on being competitive, only a penalty for being uncompetitive. Any strategy the company
   discovers under these mechanics is an artefact of that, and this is exactly the shape R12
   warns about — an output that looks like a finding but is a property of the machinery.
2. **The coupled-triad gap is unmeasurable here.** The company's own `company/crm/` layer has
   `churn_model`, `renewal_conversion`, `switching_cost_model`, `market_conditions` — a rich
   belief about winning and losing customers. Ground truth has elasticity on the loss side and
   a constant on the gain side, so the belief-vs-truth gap on acquisition is not currently a
   measurement of anything.

## What PB3 should actually be

Restated: **make the gain side see what the loss side already sees.** The competitor field
exists, is researched, and is on the wrong half of the loop.

Minimum shape, reusing what is built rather than adding:

- The funnel's `quote -> application` rate becomes a function of our offer against the
  competitor field, not of segment alone. That is the same savings-gap number
  `market_switching_multiplier` already computes, read from the other side.
- Wins and losses then share one driver, so the book is a net of two priced flows and can move
  in either direction for a reason.
- `should_attempt_acquisition`'s cap gate stays as it is — it is a solvency rule, not a
  competitiveness one, and conflating them would hide both.

**The exit test, and it must be able to fail:** sweep the company's price across its plausible
range and assert acquisition rate MOVES. Today that test fails by construction — 0.218 at every
price — which makes it a genuine R15 control rather than a formality. Its null is the current
build.

## What must happen first, and this is the real blocker

PB3 depends on PB2 (*"the company starts with a real book, and it had to win it"*, L0/idle),
which depends on PB1 (*"how big the world should be, with what it costs beside it"*, L0/idle,
depends on AO12 which IS at L2/2 and satisfied).

So the chain is unblocked at the bottom and unbuilt for its whole length. **PB1 is drawable
now.** Building PB3's coupling before PB2 would mean a growth curve operating on a 13-account
book that was assigned rather than won — a growth rate on a population whose existence has no
provenance.

Recommendation: PB1 next in this lane, not PB3. PB3's design is done and recorded here; its
build waits on the two atoms beneath it, and saying so is more useful than starting the piece
that was named.

## Provenance

Every claim above was measured or grepped in this tree at 2026-08-20T20:30Z, not recalled. The
one thing I got wrong on the way and corrected: I first reported the competitor field as
missing entirely, having searched for a file named after the atom rather than reading the
atom's own `file_scope`.
