# What bill shock is — a definition, before any more measuring

*Knowledge pass, delivery seat, 2026-09-01, on the director's instruction: "we have never defined
bill shock… go back to knowledge first and define it from published evidence before measuring it
again, including what share of households are on each payment method, since that decides which
definition applies to whom. Then the cause split follows from the definition rather than the
definition from the split."*

**This page supersedes the framing of Part 2 of
`satisfaction_drivers_and_the_three_bill_shocks.md`.** That page established three *causes* and was
right about each; it treated bill shock as one experience with three causes. It is the other way
round: there are **two experiences in different populations**, and the causes sit inside them.

---

## The failure this page exists to end

`bill_shock_pct` has always been *the percentage difference between two consecutive bill totals*.
That is not a definition of an experience — it is an arithmetic operation, applied uniformly to
households who would describe what happened to them in completely different words.

**For most GB households the bill is not the thing they pay.** They pay a fixed monthly amount. The
bill is a statement that arrives and is filed. Differencing two bills and calling the result a shock
measures something that household did not experience.

---

## The populations, and their published shares

| payment method | share of GB domestic | what the household actually pays |
|---|---:|---|
| **Direct debit** (fixed and variable together) | **~74%** | a monthly amount set by the supplier |
| **Standard credit** | **~13%** | the bill, in full, each period |
| **Prepayment** | **~13%** | credit at the meter, in advance |

*(Ofgem, 2026, already in this repository at `dd_attribution_confound_w2_10.md`; drives
`_TARGET_DD_SHARE = 0.74`.)*

Within direct debit, Ofgem's credit-balance publication counts **15 million households paying by
FIXED Direct Debit and in credit** (year ending June 2025), rising to ~17 million on the
12-months-ending-December-2025 window. Those are the households whose payment is a level amount
rather than the bill.

**The fixed-versus-variable direct-debit split is NOT published**, and it matters: a variable-DD
household pays the bill and therefore belongs, experientially, with standard credit. This is a real
gap and it is stated rather than filled — see "What is not settled" below.

---

## The definition, per population

### A. Households paying a level amount — fixed direct debit

**The bill shocks nobody. The payment change does.**

The shock is one of two things:

1. **A material change in the monthly payment.** The regulated trigger for a review is a variance
   beyond **±5%** (SLC 27B). Ofgem's own escalation cut in the 2022 Direct Debit Market Compliance
   Review was an increase **above 100%**, which put **over 900,000 direct debits** into a mandatory
   re-review; across Feb–Apr 2022 over 7 million SVT consumers saw an increase averaging **+62%**,
   with **8%** above 100%.
2. **A credit or debit balance they do not understand.** The published norm: **£200 average credit
   balance per household** (year ending June 2025, down from £244), **£3.09 billion** held in total
   across ~15 million households, **£178** average at the end of June 2025.

**A balance building and unwinding across the seasons is normal**, and a household not understanding
that is itself part of the experience rather than evidence of a supplier failure. The shock is not
the balance existing; it is the balance being *unexpected* — which is a communication property, not
an arithmetic one.

### B. Households paying the full amount — standard credit, and variable direct debit

**The shock is the bill**, and it has three published triggers:

1. **Cold weather** — a seasonal consumption rise the household did not anticipate.
2. **A usage change** — a new appliance, a new occupant, a change of circumstance.
3. **An actual read replacing a long-standing estimate**, arriving as a jump *plus* a catch-up.
   Ofgem's own words: *"suppliers estimating bills until they have an actual meter reading which may
   show that the customer's consumption is higher than expected. Suppliers then send a 'catch-up'
   bill to recover the difference."* Capped at **12 months** by SLC 21BA; **median domestic backbill
   £1,160** (2016/17); one of the largest single reasons domestic consumers contacted Citizens Advice
   (**>15%** of cases) and the Energy Ombudsman (**12%**) in 2016.

### C. Prepayment — neither definition applies

**~13% of households have no bill to be shocked by and no direct debit to be changed.** They top up
in advance. Their equivalent experience is self-disconnection or an unaffordable top-up, which is a
different measurement with a different remedy and is **out of scope of "bill shock" entirely.**
Including them in either definition would be the same error one level down.

---

## How the three causes map onto the two definitions

The director's three causes were right; they were not three cases of one thing.

| cause | population it lands in | responsibility |
|---|---|---|
| catch-up after estimates | **B** (the bill) | supplier — an inference failure |
| DD set wrong, then reset | **A** (the payment) | supplier — an operational failure |
| genuine renewal price rise | **both**, experienced differently | supplier — a commercial choice |

The renewal rise is the one that crosses: a full-payment household sees it in the next bill; a
fixed-DD household sees it only when the DD is next reviewed, possibly months later, and by then it
is entangled with any balance drift. **Same commercial decision, two different experiences, two
different lags.** That alone makes a single scalar untenable.

---

## What is not settled by the published record

1. **The fixed-versus-variable direct-debit split.** Ofgem publishes fixed-DD credit balances and the
   overall DD share; it does not publish how many DD households pay a level amount versus the actual
   bill. Without it, the boundary between definition A and definition B cannot be drawn from
   published data alone. **This is the single most load-bearing gap on this page.**
2. **Debit balances.** Ofgem publishes **credit** balances only — the money suppliers hold. The debit
   side, which is half of the director's definition A ("an unexpected credit *or debit* balance"), is
   not in the same series. An asymmetry worth naming: the regulator measures what suppliers hold, not
   what customers owe.
3. **Any seasonal breakdown of balances.** The publication is 12-month windows; it does not show the
   build-and-unwind cycle that the definition calls normal. So "normal seasonal swing" cannot
   currently be quantified from this source.
4. **What magnitude of DD change a household actually notices.** ±5% is a regulatory review trigger
   and >100% was a regulatory escalation cut. Neither is a measurement of noticing.

---

## What follows for measurement

**The cause split follows from the definition, not the reverse.** Concretely, before any further
measuring:

* A shock measure must know **which population a household is in**. Payment method is therefore an
  input to the measure, not a covariate of it.
* For population **A**, the quantity to measure is the **change in the amount collected**, and the
  balance alongside it. Not the bill.
* For population **B**, the quantity is the **bill**, and the existing cause split (catch-up /
  price / consumption) applies to it.
* For **C**, neither, and it should be excluded explicitly rather than by accident.

A single percentage difference between two bills is definition B's quantity applied to everybody,
including the ~74% for whom the bill is not what they pay.

*(What this project's own world currently does about that is a simulation reading and does not belong
on a commons page. It is measured in
`WORKER_FINDING_THE_WORLD_KNOWS_HOW_EACH_HOUSEHOLD_PAYS_AND_BILL_SHOCK_IS_THE_ONE_ORGAN_NOT_TOLD_2026-09-01`.)*

---

## Sources

- [Ofgem, Domestic Energy Customer Credit Balances, July 2024 – June 2025](https://www.ofgem.gov.uk/data/domestic-energy-customer-credit-balances-july-2024-june-2025) — £3.09bn total, £200 average per household, £178 at end-June, ~15m fixed-DD households in credit.
- [Ofgem, Domestic energy customer credit balances, January – December 2025](https://www.ofgem.gov.uk/data/domestic-energy-customer-credit-balances-january-2025-december-2025) — £3.17bn, ~17m households.
- [Ofgem, Direct Debit Market Compliance Review / press release, July 2022](https://www.ofgem.gov.uk/press-release/ofgem-requires-improvements-energy-suppliers-customer-direct-debits) — >7m SVT increases, +62% average, 8% above 100%, >900,000 re-reviewed.
- [Ofgem, back-billing ban beyond 12 months (SLC 21BA)](https://www.ofgem.gov.uk/press-release/ofgem-bans-suppliers-backbilling-customers-beyond-12-months); [Energy Ombudsman, What is back billing](https://www.energyombudsman.org/advice-for-consumers/what-is-back-billing).
- Payment-method mix (~74/13/13): Ofgem 2026, recorded in `docs/market_research/dd_attribution_confound_w2_10.md`.

*Fetched live 2026-09-01. No figure on this page is simulation output.*
