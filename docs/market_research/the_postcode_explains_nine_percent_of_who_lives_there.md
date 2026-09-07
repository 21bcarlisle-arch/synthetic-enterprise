**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
W2_19_who_lives_where_money_and_composition

**Knowledge:** none -- the people knowledge page is a later deliverable of the people ruling and is
not yet written. These are the rows it will publish; the declaration is replaced when the page lands.

# The postcode explains nine per cent of who lives there

**Measured 2026-09-07**, delivery seat, `W2_19` physical layer. Reproduce with
`python3 tools/people_physical_layer.py --split`.

The people ruling sets the structure: *"layer one is the household you would EXPECT given the
postcode and the house (published at small-area level, therefore guessable by the company from an
address); layer two is how this household DEVIATES from that... GEOGRAPHY IS THE COHERENCE KEY."*

The structure is right. **The premise underneath it is much weaker than it reads**, and this is the
number nobody in this project had looked at.

---

## The split, over every household in England and Wales

Census 2021 TS017, household size by output area — 24,783,116 households across all 188,880 output
areas, so this is the population and not a sample.

| | variance | share |
|---|---:|---:|
| **between** output areas — what an address tells you | 0.159 | **9.0%** |
| **within** an output area — what the company must discover | 1.603 | **91.0%** |
| total | 1.762 | 100% |

Mean household size 2.359. The decomposition is exact by the law of total variance, not a modelling
choice: between plus within equals total, and a control asserts it.

**An address gets you nine per cent of the way to knowing who lives there.** An output area averages
131 households, and inside it the spread of household sizes is almost the full national spread.

## Why this matters more than it looks

**It does not refute the two-layer structure — it prices it.** The ruling is right that the prior is
free and the residual is private. What it assumes is that the prior is *worth having*, and for
household size it is worth 9%.

**The consequence for the company is the useful part.** Occupancy drives consumption volume and the
daytime load shape, and both are things a supplier wants to know. If the address carried most of it,
a supplier could infer occupancy from the postcode and act on it at acquisition — before any meter
data exists. At 9% it cannot. **Occupancy is something this company must METER, not something it can
look up**, and any product design that assumed otherwise was assuming a number that had not been
measured.

**And it makes the residual the interesting object.** The ruling's "single pensioner in the four-bed,
five people in the two-bed flat" is not an edge case to be modelled on top of a strong prior. It is
where nine tenths of the variation lives.

## What this does not say

- **Household size is one physical quantity, not the layer.** Presence pattern, heating schedule,
  setpoint and appliance ownership are separate, and their between-area shares are not measured
  here. Tenure and dwelling type are known to be far more geographically clustered than size, so a
  prior built on those may be much stronger — that is the next measurement, not an assumption to
  carry forward.
- **It is 9% at OUTPUT AREA grain.** A coarser geography would explain less, not more. A finer one
  (postcode, ~15 addresses) could explain more and is not published at that grain for household
  size, so this is the best available and not a ceiling on what geography could ever give.
- **The top category is open.** "8 or more people" is used as 8, which understates that tail's mean.
  It holds about 0.1% of households, so the effect on any figure here is under a person-tenth.

## What was built

`tools/people_physical_layer.py` — the census pull, the prior per output area, the exact variance
split, and a draw that samples a household's size from **its own output area's published
distribution** rather than from a national mixture. An area absent from the census **refuses**: a
national fallback is precisely the independent draw this replaces, and it would be invisible in
every output.

**The commercial layer is deliberately absent** — no income, payment method, arrears or attitude —
per the canon's section 4. A control parses the module's syntax tree and refuses any of them. It
parses rather than greps because the first version searched the text, read the module's own prose
saying *"no income, no payment method, no attitude"*, and refused the module for stating what it
excludes. A text search cannot tell a mention from a use.

## What is not built yet

The three remaining physical quantities exist in the world already and are **not yet conditioned on
geography**: `fabric_physics.heating_schedule_for` draws setpoint and schedule per premise, and
`demand_model._daytime_occupancy_rate` is EFUS-anchored on household size with published pensioner
and employment cuts. Wiring `draw_size` into the population draw so those inherit a
geographically-conditioned occupancy is the next step, and it is what the half-hourly electricity
shape then rests on.
