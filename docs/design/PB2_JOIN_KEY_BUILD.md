# PB2 BUILD step 1 — the join key is real, and the remainder exists

**Atom:** `PB2_opening_book_won_not_assigned` (lane `W2_customer_generator`, epoch 2).
**Level:** 0 → **1** (`been BUILT in any form`). **Not 2, not 3** — see §4, which says why in
terms of the atom's own exit criteria rather than in terms of effort spent.
**Predecessors:** `PB2_OPENING_BOOK_DISCOVER.md` (the size and its anchor),
`PB2_UNWON_REMAINDER_FRAME.md` (the design). This pass executes that frame's **step 1 of 4**.
**Source ruling:** `docs/staging/in_progress/DIRECTOR_RULING_POPULATION_AND_BOOK_GROWTH_2026-08-11.md`.

---

## 1. What the FRAME expected to find, and what was actually there

The FRAME pass (2026-08-14) recorded exit (d)'s blocker as an **absent** join key:

> `SyntheticCustomer` (fields listed at its dataclass) carries **no premise field at all**.
> Subset is a relation between sets of the same key. Today it is a relation between two id
> spaces that have never met.

Read at this pass's HEAD, that is **wrong in a way that matters**. `SyntheticCustomer` has carried
a `premise: Optional[DrawnPremise]` field since B12. The field is present. What was wrong is what
filled it:

```
_draw_one  ->  _draw_dwelling(customer_id, ...)  ->  draw_premise(customer_id, ...)
                                ^^^^^^^^^^^                       ^^^^^^^^^^^
```

`draw_premise`'s first positional parameter **is** `premise_id`. The customer id was being passed
as the premise id, so every account's premise was named after the account. Measured on the shipped
default path before the change:

```
customer_id = SYN-2023-001   premise_id = SYN-2023-001
customer_id = SYN-2024-001   premise_id = SYN-2024-001
customer_id = SYN-2025-001   premise_id = SYN-2025-001

stock ids          = P0000 ... P0199
book ∩ stock       = 0
premise_id == customer_id for every drawn account: True
```

**This is worse than the absent field the FRAME expected**, and the difference is not academic. An
absent field stops a build and makes it think. A field that is present, correctly typed, and
populated with the wrong thing invites a build to conclude step 1 is already done, wire a subset
control to it, and land a control that can only ever be trivially false (empty intersection) or —
after someone "fixes" it by mapping one grammar onto the other — tautologically true. That is R15's
first killer pattern arriving through the front door.

There is a second defect underneath it, and it is the structural one: a premise **minted from the
customer that caused it to exist** is not a premise the account was won at. The world had no stock
the book came out of, so there was no remainder, so exit (d) was unsatisfiable by construction —
which is exactly what the DISCOVER pass concluded, by a different route, about `live_population`.

## 2. What landed

**`simulation/population_draw.py`**

- `iter_acquisition_events(..., premise_stock=None)`. When a stock is supplied, each acquisition
  **claims** a premise out of it without replacement, and the account carries that stock premise —
  so its id is `P0054`, a genuine member. Default `None` keeps the per-customer mint and therefore a
  byte-identical stream.
- The claim order is shuffled from its **own salted substream** (`PREMISE_CLAIM_SALT`), never from
  the acquisition `rng` (C-S2). Proven: `test_the_claim_does_not_perturb_the_acquisition_stream`.
  Turning the stock on shifts no acquisition attribute, so every figure measured before this change
  was measured against the same world.
- A claim is made **only for a domestic point**. `_draw_dwelling` already returned `None` for
  SME/I&C and the stock is an England housing-stock draw, so claiming for a non-domestic account
  would burn a premise that no account holds — leaving the remainder quietly short by a premise that
  is neither won nor unwon.
- **Stock exhaustion raises** (`ValueError`) rather than truncating. A book silently shortened to fit
  its world has its size set by the wrong thing — and would still pass the subset control.
- `unwon_remainder(stock, book)` — the premises the world drew and the company never acquired.
- `subset_verdict(stock, book)` — the control, written as a function so any tool and the tests judge
  the same predicate (the convention `premise_population.observed_shares` already sets).

Measured after the change, same seed:

```
book:      SYN-2023-001 -> P0054,  SYN-2024-001 -> P0129,  SYN-2025-001 -> P0105
verdict:   ok=True  n_stock=200  n_book_domestic=3  n_remainder=197
same control, pre-repair path:  ok=False  failures=['outside_stock']
```

**`tests/simulation/test_opening_book_subset.py`** (new, 16 tests) — the positive claim plus the
R15 battery. **`tests/simulation/test_live_population_seam.py`** (+4) — the remainder added as a new
**subject** of the existing runtime wall instrument, not a third instrument, per FRAME §4(c).

## 3. The control's clauses, and the one my own mutation testing broke

`subset_verdict` fails closed on five named clauses. Four were designed from the FRAME; the fifth
was found by running the mutations.

| clause | shape it kills | its falsifier |
|---|---|---|
| `book_empty` | FAIL-OPEN — the empty set is a subset of anything. Not hypothetical: the 2016 window draws **zero** accounts today, so a bare check reports green on it | `test_the_control_reds_on_an_empty_book` |
| `remainder_empty` | FAIL-OPEN — if every drawn premise was won, "subset" carries no information. This is the `\|book\| == \|stock\|` tautology on today's `live_population` seam | `test_the_control_reds_when_nothing_was_left_unwon` |
| `outside_stock` | the real claim — a book premise the world never drew means the account was minted, not won | `test_the_control_reds_on_the_pre_repair_path` |
| `foreign_world` | **found by mutation, §3.1** | `test_the_control_reds_on_a_book_premise_from_another_world` |
| `double_won` | set subset cannot see it: `{P1} ⊆ {P1,P2}` stays true however many times P1 was sold | `test_the_control_reds_when_an_unwon_premise_is_registered_twice` |

The load-bearing falsifier is `test_the_control_reds_on_the_pre_repair_path`: it runs the control
against the **shipped default path**, not a mock, and requires it to RED. That is what stops the
control passing because the ids happen to line up.

### 3.1 `premise_id` is positional, not identity-bearing

Two mutants I expected to RED came back GREEN. `draw_premise_population` mints `P0000..P{n-1}` for
**every** `base_seed`, so a premise drawn from an entirely different world carries an id that *is*
in this stock:

```
ids from base_seed=42:    ['P0000', 'P0001', 'P0002']
ids from base_seed=7777:  ['P0000', 'P0001', 'P0002']
values equal?             False
```

An id-only subset check therefore cannot distinguish "won at P0054 of **this** world" from "won at
P0054 of **some** world" — the wrong-subject shape at one remove, and it would have shipped as a
green control. Membership is now decided by **value**; `unwon_remainder` matches by value for the
same reason. The two mutants are kept, and each now asserts its own precondition (that the ids
collide) so the test cannot quietly stop testing what it says it tests.

## 4. What is NOT done — the reason this is L1 and not L3

Against the atom's own exit criteria:

- **(a) a proposed opening size with an external plausibility case** — **met**, by the DISCOVER
  pass (3,217 anchored to Ofgem's £130 Capital Target and the company's own opening treasury; 465 as
  the fail-closed interim). Nothing here changes it.
- **(b) the book ARRIVES BY ACQUISITION — won, never assigned** — **NOT met, and this is the
  gap.** The claim is a seeded shuffle over the stock, not a funnel outcome. No quote is issued, no
  application is refused, nothing is lost, and no acquisition cost reaches the P&L. A shuffle-claim
  is a **better-shaped assignment**, not a win. It buys exit (d) a real subject and buys (b)
  nothing. FRAME steps 2 (the prospect seam) and 3 (the inversion — `lambda` re-homed to campaign
  volume, `register_acquired_point` reached only on a win) are what close it.
- **(c) the wall holds and is PROVEN to hold, R15 both ways** — **met for the remainder as a
  value**, via the existing instruments: the static ratchet (12 green, mutation-tested both
  directions) plus four new runtime assertions including their own falsifier
  (`test_the_remainder_leak_guard_can_fail`). Not yet exercised against a *live seam* that carries a
  remainder, because there isn't one — see the next bullet.
- **(d) the book is measured to be a genuine subset of the drawn population** — **met as a
  mechanism, not yet as a property of the running company.** `subset_verdict` is proven to fire on
  all five clauses, but nothing in the shipped run path calls it yet: `live_population()` still
  appends and registers the whole drawn cohort (FRAME §2 named that line as where a grant sneaks
  back in). Wiring it is step 3, not this step.

**And the book is still three accounts.** The director's requirement — materially larger than 13 —
is untouched by this pass, and the DISCOVER pass's affordability verdict still governs: 3,217 is
6.9× the `settlement_build` ceiling AO12 measured at 465 customer-years, so the target is not
affordable on current storage and the interim needs a bisection measurement that does not exist yet.

## 5. Honest simplification, dated

**2026-08-24 — book membership is not stable under stock growth.** The FRAME (§1.1) wanted the
remainder to grow without disturbing the book already won out of it. The stock draw itself has that
property (`P0007` is the same dwelling however large `n` gets). The **claim** does not: the shuffle
is seeded on the stock size, so growing the stock re-rolls which premises were won.

This is not laziness, it is a real tension: uniform selection from a set is incompatible with
membership stability under growth of that set — any scheme that picks uniformly from `n` premises
must change its pick when `n` changes. The resolution is not a cleverer shuffle, it is **step 3**:
once the funnel decides wins, the campaign fixes which premises were *approached* at the time it
ran, and stock added later is simply never quoted. Membership then becomes stable because it is
historical rather than recomputed. Recorded here so the build that lands step 3 knows this is a
property it is expected to deliver, not one it may assume it inherited.

## 6. Findings raised, not fixed (SELF_INTERRUPT_DISCIPLINE)

- The FRAME's §3 evidence is **stale**: it states `SyntheticCustomer` carries no premise field. It
  does, and has since B12. Corrected here (§1) rather than by editing the FRAME, which is the record
  of what that pass concluded. The correction matters because the FRAME's remedy ("add a premise
  reference") was already half-present and wrong, and a build following it literally would have
  added a second field beside a populated one.
- Preconditions from the DISCOVER pass remain owed and unaddressed by this step: the draw saturates
  silently above `lambda ≈ 745`; the `SYN` key set diverges from the static roster (seven consecutive
  failed runs on 2026-08-13); the curriculum-arms-from-disk / code-arms-at-HEAD asymmetry. All three
  bite at 465 accounts and none of them bite at three, which is precisely why they must be closed
  **before** the book grows rather than after.

---

— Worker tick, 2026-08-24. BUILD draw on `PB2_opening_book_won_not_assigned`, FRAME step 1 of 4.
