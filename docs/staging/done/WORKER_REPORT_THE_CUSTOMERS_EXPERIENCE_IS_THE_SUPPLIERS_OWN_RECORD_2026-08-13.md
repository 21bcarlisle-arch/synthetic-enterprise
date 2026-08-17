# WORKER REPORT — the customer's experience is the supplier's own record

**Severity:** RECORDED
**Lane:** `H_harness`
**Date:** 2026-08-13
**Atom:** `KNIFE3_wall_crossing_paydown` (H_harness), design `A_composition_lift`, **step 21**
**Disposition:** CLOSED — landed and recorded in the same change set
**Register section:** `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §3p

## What moved

**4 edges cut, 28 → 24 live** (26 → 22 direct; the 2 indirect untouched for the **eighth**
consecutive step, which is again the proof that a bridge route was not silently taken instead).
91 ruled: **cut 67, owed 24** (20 to `A_composition_lift`, 4 to `B2_company_brain_decides_the_world`),
grandfathered 0 — measured by `python3 -m tools.wall_crossing_dispositions` (rc 0) against the
working tree, not asserted.

`simulation/run_phase2b.py::main()` opened four of the supplier's CRM books at setup
(`CustomerSatisfactionAccumulator`, `NPSTracker`, `ComplaintBook`, `PaymentBehaviourAnalytics`),
threaded them through the renewal loop, read them at the end — and made every one of the
supplier's bookkeeping decisions on the way past, at nine call sites. That a bill shock costs
trust. That a raised complaint costs more and resolving one on time gives some back. That a CSAT
answer and an NPS answer land in different books. That satisfaction decays twelve months per
renewal term. That a complaint about a bill is filed under `BILLING`.

Now `company/crm/customer_experience_desk.py` takes four observations behind
`company/interfaces/customer_experience.py` — `RenewalReached`, `SurveyResponse`,
`CustomerContact`, `PaymentOutcome` — and hands back the company's own beliefs. What the world
owns is that a bill went up, that a survey was answered with a number, that a customer got in
touch and the contact was or was not closed on time, and that a payment landed on time, late or
not at all.

## Step 20 predicted a cut in the OTHER direction here. There is none — checked, reported either way

§3o found that world physics keeps ending up in `company/crm/` because that is where the CRM
vocabulary lives (`PASSIVE_CHURN_CAP` sat in a company module labelled `# SIM ground-truth cap` in
its own source), and warned the next group under this design might need the same treatment.

Checked, symbol by symbol, across all four books. Every input they take is an outcome the supplier
observes on its own systems; every constant is a supplier's own model parameter (trust deltas,
decay rate, CSS thresholds, score bands — plus `OMBUDSMAN_ESCALATION_DAYS`, which is published law
and therefore the commons); none of them rolls a die or caps anything the world does. Whether a
customer answers a survey, whether they get in touch and whether a payment actually lands are all
decided in `simulation/` and stay there. **This one is a pure composition lift.** The warning was
a check to run, not a claim about the next group.

## The defect this cut invites — two call sites became one field

Before the cut, a CSAT answer and an NPS answer were two DIFFERENT call sites against two
DIFFERENT objects. You could not route one into the other without writing a visibly different
line. They are now one `observe_survey_response` distinguished by an `instrument` **field** — so a
caller can silently post CSAT answers into the **published NPS** and every test driving the desk
stays green, because the desk did what it was told.

This is §3o's "the branch became a field" for the **second** time, and the recurrence is the
finding worth carrying forward: **a composition lift converts control flow the caller could not
fake into data the caller supplies, every time.** The next step under this design should expect it
rather than rediscover it.

## Evidence

- `tests/company/interfaces/test_customer_experience_seam.py` — **17 tests, 17 passed**, of which
  **5 are mutations that PERFORM the named defect**: the lazy world import (on a COPY of the
  source, never a repo file edited mid-pytest), the swapped instrument, the hardcoded instrument,
  the collapsed survey arms, and the swapped decay/shock order.
- `test_the_event_stream_is_not_degenerate` asserts the fixture can fail every control that reads
  it (satisfaction off baseline, payment score non-default, both survey books non-empty), so no
  control here passes on a degenerate fixture.
- **No number moves, measured not asserted:** control 2 drives the four RAW books through the exact
  pre-cut sequence and the desk through the door over the same event stream, then compares the
  satisfaction scalar, its per-year trajectory, both annual summaries across both years, the
  payment score, the three published metrics, the miss buckets, and the KEY ORDER of the
  `behavioural_record` dict spliced into `per_customer_behavioral` for the Sim tab.
- `tests/architecture/` — 94 passed (the ratchet allowlist lowered by exactly the four cut edges,
  and `test_sim_reads_company_allowlist_has_no_stale_entries` is what forces that).
- `tests/company/crm/`, `tests/company/interfaces/`, plus the direct consumers — 2572 passed.
- `python3 -m tools.epistemic_verifier` — PASS, 561 files, no barrier violations.

## An R15 note worth keeping

The mutated desk copies must be registered in `sys.modules` **before** execution: `@dataclass`
resolves its field annotations through the module entry, so loading an unregistered copy fails
inside `dataclasses` rather than in the assertion. That failure mode makes the mutation
**unavailable** — and an unavailable check is a FAILED check, not a skip. Both mutations were red
this way on first run and were fixed rather than dropped.

## Still open, repeated rather than dropped

- **Step 17's residual:** `FITBook.levelisation_charge_gbp(year, total_mwh_supplied)` is handed kWh
  and divides by 1000 internally — arithmetic right, naming wrong. Naming debt on
  `company/regulatory/fit_book.py`, not a wall crossing.
- **Step 20's masking finding:** on the ACTIVE churn arm, `bill_shock_count` / `behaviour_score` /
  `satisfaction_score` move the estimate by exactly nothing at a +33% rate rise, because the two
  estimators combine as `max(rate, payment)` and the rate arm dominates. A fidelity question the
  company's model owns; untouched here, because a wall pass never moves a number in the same commit
  as an import (B7).

## Level

`level_current` stays **0**, deliberately. 24 of 91 crossings remain live; booking the target at
three-quarters-paid is the false-completion class this project names explicitly. No level move,
so nothing to record in `gate_authorizations.jsonl`.
