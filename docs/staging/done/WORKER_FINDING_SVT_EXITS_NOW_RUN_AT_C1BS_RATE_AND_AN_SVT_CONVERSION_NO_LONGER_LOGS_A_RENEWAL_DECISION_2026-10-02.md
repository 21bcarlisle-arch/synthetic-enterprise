**Severity:** LATENT · **Lane:** B_commercial (world side: `simulation/`) · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon (upstream world fidelity)
**Answers:** `docs/staging/records/WORKER_PREREG_THE_SVT_ANNIVERSARY_CARRIES_NO_DEPARTURE_ROLL_2026-10-01.md` (landed before either run)
**Evidence:** one default world, twice, both from `89a4611e2`. Base is the clean checkout. Change is the same checkout plus the diff that landed as `1cd4b03dc`. Scripts, logs and the analysis are in `/var/tmp/se-svtroll-out/`. The analysis is `/var/tmp/se-ptm-out/analyse.py`, unchanged. Logs: base md5 `4ae594a0…`, change md5 `f0d81418…`.

# SVT exits now run at C1b's rate, and an SVT conversion no longer logs a renewal decision

**2026-10-02, autonomous worker, claim `remove-the-svt-anniversary-departure-roll`.**

## What landed

`1cd4b03dc` adds `departure_rolled_at_renewal(previous_tariff_type)` in
`simulation/customer_events.py`. It is False only when the term before is an SVT segment.
`run_phase2b` now reads the decision leg's previous type before `_last_tariff_type` is overwritten,
and skips `roll_lifecycle_event` when the predicate says so. The anniversary re-draw in the builders
is untouched. One partition control covers the predicate, and mutating it to `return True` turns
the control red. `world_level_identity` digests only the anchor block, which this does not touch,
so no value-arms witness moved.

Both runs started only after item one's three-arm run (pid 81883) had exited. Neither run shared a
variable with it.

## The pre-registration, graded as written

The pre-registration's baseline was `aed6bf966`. The PB4 swap has landed since, so, as it
instructed, the baseline was re-run at the same base commit as the change (`89a4611e2`).

| | Prediction | Same-base baseline | Change | Verdict |
|---|---|---|---|---|
| Q1 | `[CHURN]` at a decision-leg term with an SVT predecessor: 0 | 16 | **0** (the one gas-only `[CHURN]`, SYN-2016-013 at 2020-02-24, closes a fixed year) | **holds** |
| Q2 | all-route SVT exits per SVT account-year, 0.12–0.17 | (52+16)/351.9 = 0.193 | 57/378.9 = **0.150** | **holds** |
| Q3 | active-and-stayed at SVT anniversaries outside the window, 36–50 | 26 | **46** | **holds** |
| Q4 | exit rate at fixed ends outside the window, 11–17% | 25/143 = 17.5% | 27/158 = **17.1%** | **refuted, high by 0.1pp** |
| Q5 | whole-book departures fall by 8–22 | 43 + 52 = 95 | 28 + 57 = 85, a fall of **10** | **holds** |

**Q4 is refuted, and the band is what failed.** Its centre was 13.9%, which is the pre-swap world's
rate. On the same base the rate was already 17.5%, and the change moved it down by 0.4pp. The
pre-registration read a Q4 miss as the gate reaching fixed→fixed boundaries. I tested that directly.
Of the 155 fixed-end boundaries present in both runs, **one** changed outcome: C5 at 2018-12-31,
which stayed in the base and left in the change. The roll was the same in both (0.3096, seeded on
account and date). C5's `p_retain` fell from 0.3191 to 0.2091. The gate cannot do that, because C5
has no SVT predecessor there. Some input coupled to the whole book moved instead. The book differs
by 2018 because households that used to leave at SVT anniversaries now stay. **I have not
identified which input it is.** The competitor position ledger is the obvious candidate, since it
observes every renewal's offer, but I did not trace it.

**C1b took up part of the removed route.** C1b exits rose from 52 to 57 because the survivors spend
more years on SVT (351.9 → 378.9 account-years). Its rate held at 0.148 → 0.150/yr, so the hazard
did not move; only the exposure grew.

**Coupled to the fall in departures:** `[ACQUIRE]` fell from 42 to 27 and `[WIN-UNDELIVERED]` from
23 to 13. Acquisitions in this world follow departures, so the book shrank and refilled less.

## The downstream disagreement: an SVT conversion is no longer a renewal decision in the record

Skipping `roll_lifecycle_event` removed the exit, as decided. It also removed the **event row**.
Customer events fell from 104 to 63: `renewed` from 61 to 35, and `churned` from 43 to 28. A
household converting off SVT to a fixed deal has stayed, but the world now writes no decision for
that term. The pre-registration did not consider this. Its analysis reads term lines, not events,
so none of its predictions could see it.

These readers count `event_type == "renewed"`:
- `saas/reporting/annual_report.py` (`renewed_this_year`, and the event split at ~2693)
- `tools/population_anchor.py` (`_churn_by_year` divides by renewals + churns, so the denominator
  shrinks)
- `tools/grade_renewal_churn_belief.py` (a company estimate on a converted term no longer has an
  outcome to be graded against)
- `company/analytics/churn_accuracy_report.py`
- `company/analytics/threshold_sensitivity.py`
- `tools/generate_customer_data.py`
- `tools/generate_customer_reaction_chain.py`

**Recommended remedy, the next item:** on that term, emit a `renewed` event that is **not
rolled**. Mark it with something like `departure_rolled: False`, and have `departure_cause` be None
and the probabilities None. Every reader then keeps the decision, and a hazard reader can still
exclude it by name.

This is a world-side change to the event list. Whether anything inside the run loop reads
`customer_events_log` before the run ends is not established. If something does, the remedy needs
its own one-variable run. It must not share a run with anything else.
