**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — found
while landing Lane 0 delivery "the gas tariff_type read becomes the C1b roll"

# The SVT population floor was red at HEAD, and it was a count over two generated quantities

**2026-09-16, scheduled tick, worker seat.** Found because it refused this lane's landing; proven
pre-existing; re-keyed in the same commit rather than lowered, and the reasoning is here because
the repair changes what the control claims.

## The red

```
tests/simulation/test_svt_product.py::test_an_account_on_the_svt_product_can_leave_it
E   AssertionError: only 136 electricity accounts; the check above has lost its subjects
E   assert 136 >= 140
```

**It is HEAD's.** Proven in a clean `git archive HEAD` extract with no edits applied at all: it
fails identically there. `origin/main` was `84bebe197` and local `HEAD` had been advanced onto it
before the extract was taken, so this is `origin/main`'s red and not a stale local tree's. A red
commit is structurally impossible here, so for as long as it stood it refused every lane whose
test selection reached that file.

## What the number is made of, measured rather than argued

| | 2026-08-30, per the control's own comment | 2026-09-16, measured |
|---|---|---|
| founder | 9 | **9** |
| drawn by the curriculum | 51 | **46** |
| won by the funnel | 90 | **81** |
| **total** | **150** | **136** |

**Nothing was deleted.** The founder roster is unchanged. The two that moved are the curriculum
DRAW and the acquisition funnel's WINS — both generated, both free to differ between runs and
between curriculum versions. A floor over their sum is a floor over today's answer.

That is the exact failure the control's own comment warns against, applied to itself:

> *"The floor sits below the measurement with headroom, never AT it: pinning it to today's count
> would red on any lane that lands one account."*

Below-with-headroom is not a different kind of pinning. 140 under 150 is 93%; one ordinary
variation in two generated quantities closed it.

## The second defect, which is the one worth more

The comment justified the floor as:

> *"An emptied roster would satisfy the assertion above by having no subjects."*

**That is not true of the assertion above it.** The assertion is

```python
segment = {"customer_id": "C1", "acquisition_date": "2020-01-01", ...}
assert inertia_hazard_for_term(segment, stint_start="2020-01-01") > 0.0
```

— a hand-built dict. It never reads `ELEC_CUSTOMERS`, so an emptied roster does not affect it at
all. The floor was guarding a claim it could not guard, and the sentence saying otherwise is what
made it read as coverage.

## The repair, and why it is not a lowering

**Do not lower a population floor when it fires.** A floor moved down each time it goes red is a
control that cannot fail, and this one has now earned its keep once by catching a 14-leg move
nobody had noticed.

It is re-keyed instead, to the property it was reaching for. What actually needs subjects is the
ROUTE onto the product: C1b assigns SVT mid-tenure from a resi household's own engagement roll, so
the population that matters is *resi electricity households whose active-renewal probability is
below certainty*. A roster with none of those has no account that can reach this product, every
control in `test_svt_assignment.py` would SKIP rather than fail, and this file's subject is gone.

```python
reachable = [c for c in ELEC_CUSTOMERS
             if c.get("segment", "resi") == "resi"
             and active_renewal_probability_for_customer(household_of(c["customer_id"])) < 1.0]
assert reachable, ...
```

Mutation-proven: forcing `active_renewal_probability_for_customer` to return 1.0 for every
household reds it with *"none of the 136 electricity accounts can reach the standard variable
product"*. It does not move when the draw returns 46 instead of 51.

## What is still owed, and it is not this control's job

**Why the draw fell 51 → 46 and the funnel's wins 90 → 81 is NOT established here**, and the
re-keyed control is deliberately blind to it — that is the point of keying to a property. Two
readings are open and one of them matters:

1. ordinary variation in two generated quantities, in which case there is nothing to do; or
2. a curriculum or funnel change that moved the book by 9% and was not recorded as moving it, in
   which case every measurement taken on this book since 2026-08-30 was taken on 136 accounts
   while the design note beside it said 150.

Settling it means diffing the curriculum draw's own output and the funnel's win log across the
window, which is a measurement and not an argument. Filed LATENT because nothing is now red and
nothing published depends on the count — but the 150 in
`DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md`'s addendum is stale either way, and whoever
settles this should correct it beside the claim rather than over it.
