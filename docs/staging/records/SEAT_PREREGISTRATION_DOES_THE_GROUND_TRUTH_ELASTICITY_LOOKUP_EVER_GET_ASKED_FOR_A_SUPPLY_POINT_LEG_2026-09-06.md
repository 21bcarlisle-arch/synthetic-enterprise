**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: does the ground-truth elasticity lookup ever get asked for a supply-point leg?

*Delivery seat, 2026-09-06, claim `the-r1-ceiling-is-a-selected-maximum-published-as-a-bound`.
Written BEFORE the guard was added or any suite run against it. Nothing below is an observation.*

---

## What prompted it

`simulation.population_draw.price_elasticity_for_customer` is a hash of the id and **answers for
any string at all**. Measured, not argued: `price_elasticity_for_customer("NOT_A_REAL_ID", 20260724)`
returns `1.4223` — in range, right shape, drawn from nothing. So a caller that passes something
which is not a household gets a plausible elasticity and no signal that it asked the wrong
question.

That is not hypothetical. `tools/r1_inference_ceiling.py` keyed its target column on a run output's
`customer_id`, which is a **supply point**, and a household's gas leg is registered under its
electricity point's id plus a `g` suffix (`simulation/household.py:485`, `GAS_LEG_ID_SUFFIX`). On
`run_output_f53c90b85` I count **264 supply points belonging to 177 households — 87 legs**, and
`C1g` was graded against elasticity `0.5255` while the world gave household `C1` a `1.6043`.

The instance is being repaired in `tools/r1_inference_ceiling.py` by another lane, in flight, and I
am not touching that file. **This pre-registration is about the class**: a ground-truth draw that
cannot refuse a question it has no answer to will do this again to the next instrument.

## The measurement about to be made

Add one guard to `price_elasticity_for_customer`: refuse when `household_of(customer_id) !=
customer_id`, i.e. when the id passed is a supply-point leg rather than the property the world drew
a trait for. Then run the simulation's own suites and see **whether the guard ever fires in the
world**.

## The predictions, fixed now

**P1 — no world call site passes a leg, so the guard is inert in the simulation and every
simulation suite stays green.** The two call sites I have read both normalise first
(`simulation/customer_events.py:403` and `simulation/run_phase2b.py:1479` each do
`billing_account = household_of(cid)` before the elasticity is drawn). The guard would then be a
pure tripwire for future callers.

**P2 — and the one I am least sure of, which is why this is written down.**
`simulation/run_phase2b.py:947` passes `billing_account=quote["prospect_id"]` **raw**, with no
`household_of` normalisation, and prospect ids demonstrably do carry gas legs — `PROS-2016-0067g`
is in the census above. If that value reaches the elasticity draw, **the world itself has been
drawing a price elasticity for a leg**, which is a materially worse defect than the instrument's:
it would mean a gas leg behaved in the simulation as a household with a trait belonging to nobody.
I predict this **does NOT** reach the draw — that line 947 feeds a different constructor and the
elasticity call at `customer_events.py:543` reads the normalised local from line 403 — but I have
not traced it, and I am recording the alternative before I look so that finding it cannot be
rewritten as having been expected.

**P3 — the guard is reachable.** A control asserting it refuses `C1g` AND still answers for `C1`
covers both legs of the partition. If only the refusing leg were asserted, a guard that refused
*everything* would pass, which is this project's most-repeated control defect.

## The grading rule, fixed in advance

- P1 is refuted by any simulation suite that reds because of the guard, and the refutation is
  written beside the result, not folded into it.
- **P2 confirmed is the flattering answer** (nothing more to fix). P2 refuted is a BLOCKING finding
  against `simulation/`, it outranks the rest of this turn, and it gets filed as its own finding
  rather than as a paragraph inside this one.
- A guard that fires nowhere is reported as a tripwire, honestly labelled as such. "It found
  nothing" is a result; "it is therefore worth having" is a separate argument and is made on the
  class, not on a hit count.

## What this measurement CANNOT detect, stated before it runs

The guard keys on `household_of`, which is a **string transform** (strip a trailing `g`), not a
roster lookup. So it can only ever catch the leg class. `NOT_A_REAL_ID` is its own household by
that rule and will still be answered with `1.4223`. **The fail-open is narrowed here, not closed** —
closing it needs the population roster at the draw, which is a larger change with real blast radius
and is not what this turn buys. Anyone reading a green guard as "the lookup can no longer fabricate
a trait" would be over-reading it, so that limit is written into the code beside the guard.
