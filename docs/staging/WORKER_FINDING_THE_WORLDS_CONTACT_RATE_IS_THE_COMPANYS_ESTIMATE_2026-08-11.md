# WORKER FINDING — the world's contact rate IS the company's estimate

**Severity:** BLOCKING · **Lane:** W4_the_wall

**Found:** 2026-08-11, during KNIFE pass 3 step 16 (`KNIFE3_wall_crossing_paydown`, register §3k)
**Class:** B2/B3 inversion — a company BELIEF constituting a world OUTCOME
**Disposition:** QUEUED, not fixed on sight (`SELF_INTERRUPT_DISCIPLINE`)

## The measurement

`saas/contact_model.py::contact_probability()` computes, from a bill's `clarity_score` and
`bill_shock_pct`, the probability that the customer contacts the supplier. It is the
SUPPLIER'S MODEL — three hand-set constants (`BASE_CONTACT_PROBABILITY = 0.05`,
`LOW_CLARITY_CONTACT_PENALTY = 0.3`, `BILL_SHOCK_CONTACT_PENALTY = 0.5`), documented in
that module as "seed estimates pending the `customer-archetype-data-enrichment` background
task".

`simulation/contact_centre.py::generate_contact_centre_log(bills, contact_model)` then draws
the world's ACTUAL contact events from it:

```python
event = simulate_contact(cid, entry["period_end"], entry["contact_probability"])
...
if rng.random() >= contact_probability_value:   # simulate_contact, line 70
```

So the number the company would be measured against is the number the company chose. If the
supplier revised `BASE_CONTACT_PROBABILITY` down tomorrow, its customers would contact it
less. There is no world-side contact physics for the belief to be wrong ABOUT.

Everything downstream inherits it: the contact-centre log, the SLA-breach rate the annual
report's SLC 25C check reads, and `service_quality_score`, which is derived from the same
estimate a second time.

## Why this is the named class and not a new one

Identical in shape to two the register has already cut:

* **§3g** (`B3_world_needs_its_own_cap_physics`, 2026-08-10) — `simulation/satisfaction_churn.py`
  was clamping the world's ground-truth churn probability at the COMPANY's
  `MAX_CHURN_PROBABILITY`. The world's ceiling now lives in `simulation/churn_ceiling.py`;
  the company keeps its estimate; both are 0.95, so no simulated outcome moved.
* **§3e** (`B7`, 2026-08-10) — `naked_fraction` was `1 - sim.hedging_strategy.MIN_HEDGE_FLOOR`,
  the world's mandate setting a company price input. Repaired in the same direction.

The repair shape is therefore already established, including its most important property:
**the two numbers may be equal, and a test must NOT pin them equal** — §3g and B7 both record
that refusal, because a test asserting the world's constant equals the company's restores the
coupling inside the suite. Independence is proven by mutation with a vacuity guard.

## Why it is queued rather than fixed in step 16

Step 16 cut the run module's IMPORT of `saas.contact_model` (into
`company/analytics/billing_experience_view.py` behind `company/interfaces/billing_experience.py`).
That is a different defect: the crossing was WHERE the composition happened. The world's USE
of the returned dict is untouched by it, and would be untouched by any composition lift.

Fixing it here would mean authoring world-side contact physics — what fraction of confused
customers actually pick up the phone, which is a behavioural-archetype question with its own
calibration, its own independence proof and its own R15 mutation set. That is a B3-shaped
atom, not a line in a paydown pass, and doing it inside a bounded tick is the accretion
`OPERATIONAL_LAYER_DESIGN.md` forbids.

The seam test built in step 16 deliberately carries NO control for this: a control here would
either pin the leak in place or fail on day one, and neither is that seam's job.

## Suggested shape (not built)

- `simulation/contact_propensity.py` — the world's own probability that a customer contacts
  its supplier, from the customer's archetype and the bill's OBSERVABLE properties, with no
  read of `saas.contact_model`.
- `generate_contact_centre_log` draws from that, and stops taking `contact_model` at all.
- `saas.contact_model` keeps its estimate untouched — that is the supplier's belief and it is
  allowed to be wrong.
- The COUPLED TRIAD measurement falls out for free and is the actual gain: belief
  (`contact_probability`) vs truth (world propensity) is a gap the harness can score, where
  today it is identically zero BY CONSTRUCTION — which is exactly the "gap of 0 is not always
  a leak, but a gap that CANNOT be non-zero is" shape.
- Mutation with a vacuity guard proving independence; **no test pinning the two constants
  equal** (§3g's and B7's recorded refusal).

## Evidence

- `saas/contact_model.py:41-70` (the estimate), `:26-36` (the three constants and their
  "seed estimates" caveat).
- `simulation/contact_centre.py:63-70` (`simulate_contact` drawing on it), `:98-108`
  (`generate_contact_centre_log` threading `by_customer`).
- `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §3k (recorded there as the leak step 16
  does not repair), §3g and §3e (the two prior cuts of the same class).
- `company/analytics/billing_experience_view.py` module docstring, "THE LEAK THIS CUT DOES NOT
  REPAIR".
