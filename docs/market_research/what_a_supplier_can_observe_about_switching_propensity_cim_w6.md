# What a supplier can actually observe about a household's switching propensity — Ofgem CIM wave 6

**Research completed 2026-09-05, delivery seat, R1.** Live source fetched this pass: Ofgem's
*Consumer Impacts of Market Conditions* (CIM) survey wave 6 **data tables (XLSX, 27.4MB)**, parsed
locally. Sheet `Tables`, **Table 56** (question C4), which is the DEMOGRAPHIC-banner rendering of the
same question the switcher-split note read at Table 108/109.

**Opened by:** `SEAT_FINDING_R1S_INFERENCE_CEILING_IS_AT_THE_NULL_AND_R2_CANNOT_PAY_UNTIL_R1_LANDS_2026-09-05.md`,
whose closing item is *"an R1 build that gives elasticity observable antecedents"*. That measurement
established there is nothing in our own book to condition on. This one asks the prior question —
**what does the published record say a real supplier COULD condition on?**

**Why this was not already here.** `gb_domestic_switcher_split_cim_2022_2025.md` fetched the same
workbook on 2026-09-04 and read Table 108 (Total banner) and Table 109 (tariff type) only, because
its question was φ, the external/internal split. The demographic banner was never opened. One fetch,
two questions, and the second one had to be asked to find it.

---

## 1. The instrument and the base

**Question C4**, base all respondents (n=3458 unweighted, weighted base 3458):

> *"Which, if any, of these have you or your household done IN THE PAST 6 MONTHS?"*
> — with *"I/we have switched to a new supplier"* as its own code.

**Population base rate: 5.3%** switched supplier in the past six months (weighted 182.9 of 3458).

Everything below is that same 5.3% cut by a banner column. It is REPORTED BEHAVIOUR over six
months, not intention and not a switching rate per annum — see §4 for what it cannot be used for.

## 2. The tautology that presents as the strongest predictor, named first because it is the trap

The banner group **"Last time switched supplier"** offers one column, *"Switched supplier in last 2
years"*, and it reads **21.6%** against a 5.3% base — a 4.1× effect, the largest in the whole table,
and exactly the "prior switching predicts switching" result the literature would lead you to expect.

**It carries no information whatsoever.** Measured:

```
all past-6-month switchers (weighted)              182.9
of which inside "switched in last 2 years"         182.9   = 100.0%
```

Two years CONTAINS six months, so every household in the numerator is in the denominator's defining
set by construction. The 21.6% is `182.9 / 848` and is a statement about arithmetic, not about
households. **This is not a small subset-overlap to caveat; it is total.**

It is recorded rather than dropped because it was about to be published as this note's headline, and
because the general shape — *a "predictor" whose defining condition contains the outcome* — is one
this project has paid for repeatedly under other names.

**The same disqualification removes the banner group "Engagement with the energy market in the past
6 months"**, whose relevant column reads exactly 100.0%: that column IS the outcome.

## 3. What a supplier CAN observe, and what it is worth

Every row below is a field a GB supplier holds on its own book — the meter's payment method, the
tariff the customer is on, its own arrears ledger, its own size. Bases are unweighted.

```
                                              switched supplier      n      vs base
                                               in past 6 months            (5.3%)
TARIFF TYPE            fixed                        7.0%            2127     1.32x
                       variable                     2.5%            1316     0.47x
                                                            ratio fixed:variable  2.8x

PAYMENT METHOD         standard credit              5.7%             438     1.08x
                       direct debit                 5.6%            2483     1.06x
                       prepayment (all)             3.1%             491     0.58x
                         - smart PPM                3.2%             315     0.60x
                         - traditional PPM          1.7%             158     0.32x
                                                    ratio credit:traditional PPM  3.4x

SUPPLIER SIZE          small supplier               8.6%                     1.62x
                       large supplier               5.0%                     0.94x

ARREARS / DEBT         "getting harder"             6.8%                     1.28x
                       no debt                      4.2%                     0.79x

BILL DIFFICULTY        sometimes struggling         6.7%                     1.26x
                       no difficulties              3.9%                     0.74x
```

**The two that matter are tariff type (2.8×) and payment method (3.4×), and both are things we set
or meter rather than infer.**

## 4. The one that runs backwards, and it is the most useful line here

```
SUPPLIER SATISFACTION  satisfied                    5.4%
                       not satisfied                4.9%
                       DISSATISFIED                 3.0%
```

**Dissatisfied households switch at little more than half the rate of satisfied ones.** The naive
model — unhappy customers leave — is not merely weak in this data, it points the wrong way.

This is the engagement/elasticity separation the P4 brief asserted, arriving from the published
record rather than from reasoning: *whether a household enters a choice process at all* is a
different fact from *what it does once inside*. Dissatisfaction is not engagement. A household that
is dissatisfied, on a variable tariff and on traditional prepayment is the least likely to move of
anyone in this table — and it is precisely the household our current world would model as
high-elasticity, because we express "never switches" as "low elasticity" on one axis.

**A world built on the naive relationship would teach the company something that is not true**, and
the company would then act on it. That is `PB4_engagement_separated_from_elasticity`'s entire case,
now with a number attached.

## 5. What this establishes, and what it does not

**Established, and usable as an anchor:** switching propensity in GB varies by a factor of ~3
across characteristics a supplier already holds, and the direction of the satisfaction relationship
is inverted against the intuitive model.

**NOT established here, and each would need its own pass:**
- **These are marginals, not a model.** Fixed-tariff households and direct-debit households overlap
  heavily; nothing here says how much of the 2.8× and the 3.4× is the same variation counted twice.
  The banner cannot answer that — it would need the microdata.
- **Six months is not a year**, and this is one wave. The switcher-split note's §1 warning about
  reported behaviour applies unchanged.
- **Causation is not claimed anywhere above.** Traditional PPM households may switch less because
  of the meter, or because of who lives behind it. For our purposes the distinction is not load
  bearing — we need the OBSERVABLE association to build a world a supplier could learn from — but it
  would be load bearing the moment anyone proposed changing a household's meter to change its
  behaviour.

## 6. Sources

- Ofgem, *Consumer impacts of market conditions survey wave 6 data tables* (XLSX),
  https://www.ofgem.gov.uk/sites/default/files/2025-07/Consumer%20impacts%20of%20market%20conditions%20survey%20wave%206%20data%20tables.xlsx
  — fetched and parsed 2026-09-05; sheet `Tables`, Table 56, banner groups *Tariff type*,
  *Individual Payment Method*, *Supplier size*, *Levels of debt*, *Keeping up with energy bills*,
  *Supplier satisfaction*, *Last time switched supplier*.
- In-repo, followed rather than re-derived: `gb_domestic_switcher_split_cim_2022_2025.md` (the same
  workbook, the Total and tariff-type banners, and the C4 instrument description).
