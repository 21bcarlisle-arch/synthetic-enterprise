# WORKER FINDING — the world's contact rate IS the company's estimate

**Severity:** BLOCKING · **Lane:** W4_the_wall

**Found:** 2026-08-11, during KNIFE pass 3 step 16 (`KNIFE3_wall_crossing_paydown`, register §3k)
**Class:** B2/B3 inversion — a company BELIEF constituting a world OUTCOME
**Disposition:** QUEUED, not fixed on sight (`SELF_INTERRUPT_DISCIPLINE`) — REPAIRED 2026-08-13, see below
**Discharged:** `tests/simulation/test_contact_propensity.py::test_mutating_the_companys_constants_does_not_move_the_worlds_contacts`, `tests/simulation/test_contact_propensity.py::test_generate_contact_centre_log_no_longer_accepts_the_companys_model`, `simulation/contact_propensity.py`, `tools/couple_contact.py` — the world draws its contacts from its own response function and the log no longer accepts the supplier's model at all.

**The severity header above says what this Hour FOUND, and is left as found.** The repair is
recorded here rather than by rewriting the header, per the standing rule that a finding's
severity states what was discovered, not what was left behind; the machine-readable release is
the checked `**Discharged:**` field, which `background/finding_severity.py` reads down to
RECORDED — the same parse that raised the hold, so no second list can disagree with it. This is
the first REAL blocker OPS11's lane refusal has held and released; its own record notes it
landed quiescent and that the first live blocker is what would exercise it in anger.

**What was built, 2026-08-13** — the "Suggested shape" section below, as suggested:

- `simulation/contact_propensity.py` is the world's own response function. It is keyed on the
  household's engagement archetype (`simulation/household_segments.py`), which the company
  structurally cannot read — so the truth is STRUCTURALLY different from the belief, not merely
  numerically different, and the gap cannot return to zero by construction even if every
  constant were copied across.
- `generate_contact_centre_log(bills)` takes `bills` and nothing else. The `contact_model`
  parameter is GONE rather than defaulted: a parameter that still existed is a parameter
  something could pass again. `tests/tools/test_contact_centre_port.py`'s fixture, which built
  a synthetic `contact_model` with `contact_probability=1.0`, was the one caller that still
  reached through the wall to dial the world's contact rate; it now supplies bills.
- `saas/contact_model.py` is untouched. It is the supplier's estimate and is now free to be
  wrong about the world.
- `tools/couple_contact.py` scores belief vs truth — the COUPLED TRIAD gain that was the actual
  point, on a quantity where the gap was previously zero BY CONSTRUCTION.
- No test pins the world's constants equal to the company's (§3g's and B7's recorded refusal,
  held for the third time). Independence is proven by mutation with two vacuity guards, and the
  mutation was RUN, not merely written: restoring the leak (the world delegating to
  `saas.contact_model`) reds four cut tests while both vacuity guards stay green.

**The residual, named rather than left implied:** `clarity_score` is still computed by
`saas/bill_generator.py`, so the world reads the company's measure of its own document's
legibility. The defect repaired here was the RESPONSE FUNCTION being the company's, and it is
now the world's. The world measuring document complexity for itself is a further deepening,
queued not taken (`SELF_INTERRUPT_DISCIPLINE`).

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
