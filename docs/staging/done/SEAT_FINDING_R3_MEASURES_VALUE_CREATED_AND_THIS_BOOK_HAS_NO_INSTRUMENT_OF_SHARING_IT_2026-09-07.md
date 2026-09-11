**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# R3 measures value CREATED; this book holds no time-of-use tariff, so there is no instrument of SHARING it — and that is a missing product, not a missing measurement

**Found:** 2026-09-07, delivery seat, claim `a49-publishes-the-r3-and-r4-ceilings-on-harness`.
Neither instrument was looking for this. It fell out of putting the two readings side by side.

## The finding

R3 bounds what perfect timing advice could abate: **91.7 kgCO₂e per household-year**, worth
**£4.03** at the DESNZ traded carbon value, at a shiftable share of 1.0. That figure clears a
skill-free null by 4.82×. The carbon is real.

R4 then has to place that in a product column and cannot. Its `time_shifting` arm reports
`gbp_per_household_year: None`, and the instrument's own reason is the finding:

> R3's pounds are CARBON VALUED at the traded price, not a bill saving. A shifted kWh is cheaper
> only on a time-of-use tariff and this book holds none, so the BILL saving from shifting is zero
> here and the carbon value sits in its own column.

So: the lever with a carbon ceiling has **no bill-saving ceiling at all**, and the lever with a
bill-saving ceiling (`tariff_fit`, £2.19/household-year) abates **exactly zero** by the director's
standing rule that a saving counts only from reduced or time-shifted usage, never from discounting.

## Why this is the mission's own shape and not a modelling detail

The mission is *"creating enterprise value … **and sharing in that value**"*, and CLAUDE.md's first
consequence is that **value is created and THEN shared, so every decision has two sides.**

R3 is an instrument of the first side. There is currently no instrument of the second. A household
that moves load on this book abates carbon and pays exactly what it paid before; the company earns
nothing from the move; nobody's bill changes. The value is created and there is no mechanism through
which any of it is shared. **That is half a product.**

It is also the canon's own charge — *"the company can make a household cheaper and never greener"* —
arriving from the other direction. R4's bounded arms split cleanly: the one that abates cannot save
money, the one that saves money cannot abate. Both halves of that sentence are now on `/harness/` as
arithmetic rather than as a worry.

## Why it is a bigger item than the publishing it was found during

The publishing is done and landed. This is not.

A time-of-use tariff is not a measurement or a page — it is a **product in the book**: a tariff
structure the pricing chain can quote, that settlement can bill, that a household can be moved onto,
and that the company can earn a share of the created value through. That touches pricing, billing,
the renewal path and the customer's decision model. It is a programme, not an atom.

**And it is the precondition for R3 paying at all.** R3's ceiling is carbon-only *by construction*
while the book holds no ToU tariff. Building the timing advice first would produce a product that
demonstrably works and that nobody can be charged for.

## What I am NOT claiming

- **Not that the tariff should be built.** R3's ceiling is £4.03/household-year of *carbon value* at
  a shiftable share of 1.0, and no source establishes a domestic shiftable share — at a tenth of load
  moved it is 40p. Whether a ToU tariff pays is its own ceiling question and I have not measured it.
  This finding says the gap exists and is structural, not that the answer is yes.
- **Not that R3 is retired.** It clears its null. The instrument says so and says it does not retire
  time-shifting.
- **Not that the shiftable share is small.** Nothing in the knowledge layer, the commons or the
  market research establishes one. The curve is published; the number is a named gap.

## The recommendation, and I am not asking

**The next increment on this thread is a ceiling instrument for the SHARING side — what a
time-of-use tariff could be worth to the company and to a household on this book — before any ToU
product is built.** That is A49's own discipline applied to the gap A49's instruments exposed, and it
is the same argument EP13 paid twelve passes to learn. I am not starting it in this turn; the
publishing was the drawn work and it is landed.

## Where it is published

`/harness/`, in "The most the products beyond price could ever be worth", under *"And there is no way
to share the value time-shifting creates"*. Held by
`test_the_MISSING_TARIFF_that_makes_time_shifting_half_a_product_reaches_the_reader`, which fires if
the blank pounds column is ever rendered without its reason — because a blank with no explanation
reads as an arm that was measured and came out at nothing, which is the opposite of the truth.
