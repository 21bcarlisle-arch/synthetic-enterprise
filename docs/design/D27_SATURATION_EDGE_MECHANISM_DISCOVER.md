# D27 — the saturation edge is not the book's alone: `edge = span + AS_OF_BUFFER_DAYS`

**DISCOVER pass 5, 2026-08-18** (worker tick, DISCOVER/FRAME lane; **NO BUILD code** — the atom is
epoch-parked). Atom: `D27_belief_window_saturates_on_this_book`, lane `D_billing_metering`, L0.

Takes the fourth pass's own §8 fourth open lead, quoted verbatim:

> **The 30-day offset in `edge = span + 30` was measured, not derived.** It is exact on six books
> and its mechanism (the fixed due-date-to-value-date lag) is inferred, not proven.

The lead was right to flag itself. The inferred mechanism is **false**, the real one belongs to a
*different atom*, and once it is named the fourth pass's central structural claim — that the
published side cannot be given an event beside the line without changing the constructor — is
**refuted by measurement**.

---

## 1. The inferred mechanism is false (null control, both directions)

Pass 4 attributed the +30 to "the fixed due-date-to-value-date lag", i.e. `PAYMENT_TERMS_DAYS = 14`
and the ARUDD lag. Moving that constant does nothing to the edge.

Measured 2026-08-18, shipped `LivePaymentTriad.measure_and_write` with only the book spec, the
consumer window and one candidate constant substituted; edge found by bisecting the published
carrier against the `W=60000` baseline, read exactly as `measure_component_render_sites` reads it.
Book: `n_customers=20, months=6`, span 152d (`2020-01-28` → `2020-06-28`).

| move | edge | prediction | verdict |
|---|---|---|---|
| baseline, `belief` | **182** | `span+30 = 182` | reproduces pass 4 |
| baseline, `belief_population_mix` | **182** | `span+30 = 182` | reproduces pass 4 |
| `AS_OF_BUFFER_DAYS` 30 → **10** | **162** | `span+10 = 162` | **tracks exactly** |
| `AS_OF_BUFFER_DAYS` 30 → **50** | **202** | `span+50 = 202` | **tracks exactly** |
| `PAYMENT_TERMS_DAYS` 14 → **7** | 182 | — | **does not move** |
| `PAYMENT_TERMS_DAYS` 14 → **28** | 182 | — | **does not move** |

The last two rows are the **null control** this finding needed: a 4× move of the constant pass 4
named leaves the edge bit-identical, while a ±20d move of the buffer relocates it to the day. The
offset is `AS_OF_BUFFER_DAYS`, and the law is

```
edge = book span + AS_OF_BUFFER_DAYS
```

which is derivable, not merely fitted: `measure()` sets
`as_of = max(due_date) + AS_OF_BUFFER_DAYS` (`live_payment_triad.py:811`) and
`_arrears_risk_belief` keeps an event while `(as_of - value_date).days <= window`
(`payment_observation_consumer.py:629/633`). The oldest event's `value_date` sits at the first due
date, so the reach the window must cover is exactly `(last_due + buffer) - first_due`. Payment
terms never enter: `issue = due - PAYMENT_TERMS_DAYS` puts them *behind* the due date by
construction, which the first DISCOVER pass had already recorded about this same constant and
which nobody carried across to the edge.

**The offset was never the book's.** It is the harness's reading position.

## 2. So the edge has a second lever, and it is not capped

Pass 4 §6 concluded, of the published side:

> …and unlike the scored side it *cannot be given one* without changing the constructor, because
> the ceiling is 335 days and the line is at 6000.

That is now false. The 335-day ceiling binds `months`; it does not bind the buffer. **Predicted in
advance and confirmed to the day**: set `AS_OF_BUFFER_DAYS = 5848` on the *shipped* six-month book
so that `span + buffer = 6000`, exactly the live composer's `_RUN_SPANNING_WINDOW_DAYS`.

| window | `belief` | `belief_population_mix` |
|---|---|---|
| 5998 | 0.25 | 0.3 |
| 5999 | 0.25 | 0.3 |
| **6000** | **0.15625** | **0.24999999999999997** |
| 6001 | 0.15625 | 0.24999999999999997 |
| 60000 | 0.15625 | 0.24999999999999997 |

The edge lands on 6000 to the day. Null: the identical window grid at the shipped `buffer=30`
reads 0.15625 / 0.2499… at every one of 5998 / 6000 / 60000 — saturated, as pass 4 reported.

So the "5,635 days unreachable **by construction**" figure is wrong in its modality. Those days are
unreachable **by choice of a constant**, and the constant is a plain module int with no ceiling in
it. The constructor is not the wall pass 4 took it for.

## 3. But one knob for the EDGE is two knobs for the FIGURES

The obvious inference from §2 — buy the missing resolution with the buffer and leave the book alone
— does not survive measurement. Two books whose edges are *identical* publish *different companies*.

Edge-matched pair, both reaching `edge = 365`, all five published dimensions:

| dimension | A: `months=12, buffer=30` | B: `months=6, buffer=213` | same? |
|---|---|---|---|
| `detection` | 0.11538461538461539 | 0.08333333333333333 | no |
| `detection_latency` | 2.546667 | 2.461538 | no |
| `belief` | 0.15 | 0.15625 | no |
| `belief_population_mix` | 0.30000000000000004 | 0.24999999999999997 | no |
| `ageing` | 0.3946153846153846 | 0.3173076923076923 | no |

Span and buffer are one degree of freedom for *where the edge falls* and two for *what gets
published*, because lengthening the book adds events and moving the buffer only moves the vantage.
A reshape that treats them as interchangeable — the shortest reading of §2 — silently changes every
figure on the pair while appearing to change only an instrument setting.

## 4. What buffer-bought resolution actually costs, measured

On a fixed book (`n=20, months=6`) at the shipped saturated window, sweeping the buffer:

| buffer | `detection` | `detection_latency` | `belief` | `belief_population_mix` | `ageing` |
|---|---|---|---|---|---|
| 30 | 0.08333333333333333 | 2.461538 | 0.15625 | 0.24999999999999997 | **0.27884615384615385** |
| 45 | ″ | ″ | ″ | ″ | **0.27884615384615385** |
| 60 | ″ | ″ | ″ | ″ | **0.3173076923076923** |
| 100 / 400 / 1000 | ″ | ″ | ″ | ″ | 0.3173076923076923 |

The price is exactly **one dimension**: `ageing` steps once between 45 and 60 (+13.8% of the
shipped figure) and is then saturated itself; the other four are bit-identical across a 33× buffer
move. This is consistent with the first DISCOVER pass's scored-side reading (buffer 30→6 moved
`ageing` by 12–33% and nothing else) and extends it to the published side — and it is `ageing`
saturating in the *same shape* this atom exists to name, one constant over.

## 5. Ownership, and a dependency that points the wrong way

`AS_OF_BUFFER_DAYS` is **D29's** (`D29_the_as_of_buffer_floors_the_memory_grid`), handed over in
writing by the first DISCOVER pass. The map records `D29.depends_on: [D27]`. This pass measures the
arrow in the other direction as well: **D27's own edge cannot be stated without D29's constant**,
because the buffer is half the law in §1 and the only uncapped half. That is a genuine
co-dependency, not a mis-filed edge — and it is a sequencing fact a BUILD needs before either atom
is drawn, because whichever lands first fixes the other's baseline.

Recorded, not resolved: this pass does not re-file either atom, and does not propose changing
`depends_on`. Naming it is D27's; deciding it is the planner's.

**R12 / R13.** No value change is proposed or implied. 30 is not criticised as a number, 5848 is a
*probe* and not a recommendation, `months=6` is not defended by its output, and no buffer is
proposed for either side. The buffer values were fixed to test a stated law before any published
figure was read; the figures moved as a consequence and are reported, not selected for. Every run
substitutes only the book spec, the consumer window and one named constant — a different vantage
on the same world, never a different world.

## 6. What a BUILD would land, and the mutation that proves each control can fail (R15)

These **replace pass 4's criterion 2**, which asked the published side for a window-resolution
reading derived from "the book's own event dates and the composer's declared window" — §1 shows
that subject is incomplete and such a control would compute the wrong edge on any non-default
buffer.

1. **The saturation edge is DERIVED from both of its terms.** The published-side reading computes
   `span + AS_OF_BUFFER_DAYS` from the book's event dates *and* the harness's declared buffer,
   never from the span alone and never from any severity threshold (the D20/D21 tautology).
   *Mutation:* move the buffer to 10 and to 50 with the book fixed — the reported edge must move to
   162 and 202. A reading that stays at 182 is computing pass 4's law and is wrong on both.
   *Fail-open leg:* move `PAYMENT_TERMS_DAYS` — the edge must NOT move, or the control has picked
   up a term that does no work and will drift with an unrelated constant.
2. **A saturated belief dimension is a VISIBLE state on the artefact, and it names WHICH lever is
   short.** The stamp distinguishes "the book is too short for this window" from "the vantage is
   too close", because §3 proves the two are not the same repair.
   *Mutation:* build at `buffer=5848` on the shipped book — the stamp must clear at `W=6000` and
   must be present at `W=5999`. A stamp that is always present is the fail-open this instrument has
   produced before; one that clears whenever *either* lever moves cannot tell the two repairs apart.
3. **A buffer change declares its cost on every published dimension, not just the one it targets.**
   Any move of `AS_OF_BUFFER_DAYS` records the before/after of all five carriers.
   *Mutation:* move the buffer 45 → 60 — the control must report `ageing` moving and the other four
   fixed. A control reporting "no material change" has averaged across dimensions and lost the only
   figure that moved. *Independence:* the cost is read off the carriers the door receives, never
   re-derived from the buffer.
4. **An edge-matched pair is not treated as an equivalent population.** Any code path offering
   "reach edge E" must state which lever it used and refuse to present the two as interchangeable.
   *Mutation:* request `edge=365` via `months=12` and via `buffer=213` — the two must produce
   different declared populations and the control must say so; a path returning one answer for both
   has reproduced §3's defect in code.

## 7. What this pass does not settle

- **The `ageing` step's own edge is bracketed, not located.** It falls between buffer 45 and 60;
  the bisect was not run. Its mechanism is unmeasured and is D29's subject, not this atom's.
- **The edge law was verified at four buffer values (10, 30, 50, 5848) on one book shape.** It is
  exact at all four and derivable from two shipped lines, but the joint
  `span × buffer` surface is unswept — as is `n_customers × months`, still open from pass 4.
- **Carried forward unchanged from pass 4**: a third book unmeasured, and the four measurement
  functions defaulting to `RESOLUTION_SEEDS` still unswept.
- **Owners:** D28 keeps the register declarations, D31 the undefined-reading witness, **D29 the
  buffer — now with D27's edge law resting on it**. D27 keeps the census shape and the published
  book's span.

## 8. Reproducing the measurement

```python
# All shipped except the book spec, the consumer window, and one named constant.
import background.live_payment_triad as lpt
from background.live_payment_triad import LivePaymentTriad

def belief(n, months, window, buf):
    lpt.AS_OF_BUFFER_DAYS = buf
    t = LivePaymentTriad(dd_failure_window_days=window)
    for i in range(n):
        for m in range(1, months + 1):
            t.record_period(customer_id=f"RESI{i:05d}", due_date=date(2020, m, 28),
                            amount_gbp=120.0, income_stress_value="high", segment="resi")
    return t.measure_and_write(ledger_path=tmp)["belief"]      # carrier, as the render sweep reads it

# §1  bisect the edge against the W=60000 baseline at buf in {10, 30, 50};
#     null-control by moving PAYMENT_TERMS_DAYS instead.        -> edge == span + buf, exactly
# §2  buf = 6000 - span; belief(20, 6, W, buf) for W in 5999, 6000.   -> straddles the live window
# §3  (months=12, buf=30) vs (months=6, buf=213), both edge 365.      -> all five dimensions differ
# §4  buf in 30, 45, 60, 100, 400, 1000 at W=60000.                   -> only `ageing` moves, once
```

Runtime: each bisect is ~11 composer runs (~0.4s each at n=20); the whole pass is ~4 minutes.

## 9. Level

**LEVEL STAYS L0, and that is correct rather than a hold.** L1 is "has been BUILT in any form"
(`MATURITY_MAP.md` §3) and this atom's deliverable is a reshape of `tools/couple_w2_11_d5.py`,
which is epoch-gated. The doc is not this atom's deliverable, so DISCOVER cannot move it.
