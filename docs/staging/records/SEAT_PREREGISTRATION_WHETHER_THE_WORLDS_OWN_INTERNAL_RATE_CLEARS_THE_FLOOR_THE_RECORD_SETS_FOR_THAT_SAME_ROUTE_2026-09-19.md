**Severity:** LATENT · **Lane:** W2_customer_generator · **Atom:** the world's product mix

# Pre-registration: does this world's internal re-contract rate clear the floor the record sets for *that same route*, and in which years?

**Filed 2026-09-19, delivery seat, claim
`the-svt-side-decision-has-no-home-because-simulation-cannot-read-the-published-floor`, BEFORE the
per-year measurement.** The drawn item asks a design question — does the SVT-side boundary decision
get a name in `simulation/`, and how does the published floor reach it. Answering it turned up a
comparison the tree can already make and does not, and this file records what I expect that
comparison to say before I run it.

---

## 1. What I already know, so it is not predicted here

Two committed artefacts each carry one half, and the arithmetic over their headline numbers is not a
measurement:

- `docs/reports/svt_internal_return_and_tenure.json` → `totals.internal_return_rate_per_svt_account_year
  = 0.185887`. Returns to a fixed term over SVT account-years of exposure, 125 stints, 49 returned.
- `tools.published_route_split.svt_internal_conversion_floor()` → `binding_floor = 0.0449`,
  conversions per SVT household per six months, binding at W4 (July 2023).

`0.185887 > 0.0449`, so **the world clears the binding floor in total by ~4.1x**. That is two
published numbers divided in my head and it is stated here so that it cannot later be presented as
a finding.

## 2. What each number counts, before either is compared

- **World `per_svt_account_year`** — stints whose fate is `returned_to_fixed`, over SVT
  account-DAYS/365.25 of exposure in the year the stint ENDS. Numerator: conversions. Denominator:
  time spent on the product. Population: this book's resi electricity accounts.
- **Floor `binding_floor`** — `(I - (1-s)*0.35) / s_max`, per SVT household per six months.
  Numerator: the part of CIM C4's internal-switching row that the fixed-renewal route provably
  cannot supply. Denominator: SVT households. Population: GB domestic survey respondents, both
  fuels.

**They are the same KIND of quantity — conversions per SVT household per unit exposure — which is
the whole reason this comparison is admissible and the one the reading currently makes is not.**
Two mismatches remain and neither is corrected, only named: a year against a half-year, and this
book's electricity accounts against GB households.

## 3. The direction, stated before the answer

**Using a six-month floor as an annual bar makes the bar LOWER than the true annual bar, so it
flatters the world.** "The world clears" is therefore the WEAK result and "the world is short" would
be the strong one. I will not annualise the floor to close that: `svt_internal_conversion_floor`
declines to annualise `I` for a named reason (no published repeat-switching assumption), and
inventing one here to strengthen my own verdict would be the worst version of this.

## 4. Predictions

1. **The total clears** — settled in §1, not a prediction.
2. **At least one year is BELOW 0.0449.** The artefact's `against_the_record` already shows W2 at a
   world rate of `0.0` for 2022, so at least one year has no returns at all. **Confidence: high.**
3. **2022 is one of the years below**, and the cause is `FTC_WITHDRAWAL_WINDOW` forcing every
   boundary passive — no fixed deal to convert onto. **Confidence: high.** If 2022 clears, my
   understanding of the withdrawal window's reach is wrong.
4. **The majority of years clear.** With a total of 0.186 against a bar of 0.045 and ten years, most
   years must sit well above. **Confidence: medium-high** — it is a claim about the spread, and the
   per-year counts are small (3 returns in 2024 over 34.5 account-years).
5. **2016 does not clear, and it is a burn-in artefact, not behaviour.** `svt_product.py` already
   records that every account opens on a fixed term and cannot reach SVT before its first
   anniversary; 2016 shows 3 accounts and 0.0055 account-years. **Confidence: medium.** If 2016
   shows a return I have misread the window's start.
6. **The verdict will NOT be uniform across years**, so a control keyed to "every year clears"
   would be red today and a control keyed to "no year clears" would be red today. The control I
   write must therefore be keyed to the PROPERTY (which denominator, which published quantity, and
   that both verdicts are reachable) and not to the count. **Confidence: high** — this follows from
   prediction 2 and 4 together.

## 5. What would refute the whole frame

If `per_svt_account_year` turns out NOT to be comparable to the floor — if the floor's `s` is a
point-in-time stock share rather than an exposure share, so that its denominator is households and
not household-time — then the two ratios are not the same quantity and this comparison publishes
the wrong cause. I have read `svt_internal_conversion_floor`'s derivation and believe `s` enters as
the share of the household stock over the recall window, which is exposure-like over that window.
**This is the assumption the reading rests on and it is stated at the reading, not only here.**

## 6. What this pre-registration does not cover

The design question itself — whether the decision gets a name in `simulation/`. That is a judgement,
not a measurement, and it is answered in the decision document beside this file. Nothing measured
here can settle it, and this file exists so that the measurement cannot be read as having settled it.
