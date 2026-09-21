**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `does-minting-arrivals-widen-the-scored-decision-population`

# The world that mints arrivals cannot finish a value-arm pass, and the alarm that said so had no cause

*The drawn question was how many priced, scored decisions the arrival producer adds. The answer is
not yet a number, because the arrivals-ON leg **dies 880s in** on `KeyError: 'SYN-2016-008'` while
the arrivals-OFF leg finishes clean and reproduces the 2026-09-18 artefact to the last digit. The
crash is a registration/advance pairing that has been latent since long before C6 and that an
account opening on the default tariff walks straight into. A repeating alarm has been escalating
this exact KeyError, on this exact account, since 11:09Z — five hours before the producer landed —
and it was filed with `Atom: unminted` and no cause. This gives it one.*

**Delivery seat, Lane 0, 2026-09-19.** Premise re-measured: the item cites `ea2a8d93a`, an ancestor
of `origin/main`, cited as an established capability to use (`_auc_against_its_own_null` off a row's
own roster) rather than work to land. Intact.

---

## 1. What was run, and what it cost

Two value-arm passes at one commit, one seed, one roster, differing in exactly one rebound symbol —
`simulation.population_draw._draw_tariff_type` returning `None`, which is the field's own dataclass
default and therefore the pre-producer book. Instrument and pre-registration landed first at
`768895de2`; the pre-registration is
`docs/staging/records/PREREG_DOES_MINTING_DEFAULT_TARIFF_ARRIVALS_WIDEN_OR_NARROW_THE_SCORED_DECISION_POPULATION_2026-09-19.md`,
written at 16:45 BST with both leg artefacts absent from disk.

| | leg | outcome |
|---|---|---|
| **OFF** — `_draw_tariff_type` → `None` | 1,428s (23.8 min) | completed, artefact written |
| **ON** — HEAD as built | ~880s | **died: `KeyError: 'SYN-2016-008'`** |

Cost: one launch of `background.launch_long_job`, 39 min of the only box, 5.55 GB peak. **No seed
family was run** — the drawn item's hard constraint — and none is needed: the null width is a closed
form in `n1` and `n2`.

## 2. The OFF leg is a clean control, and that is worth saying first

| quantity | OFF leg, today | three-arm artefact, 2026-09-18 |
|---|---:|---:|
| roster records at `tariff_type` | **232 `None` of 232** | 232 of 232 |
| `renewals_the_world_offered` | 2,824 | 2,824 |
| `acquisition_term` / `product_not_upliftable` | 227 / 2,490 (all `'svt'`) | 227 / 2,490 |
| `priced` / `declined` / `no_observed_history` | 104 / 3 / 0 | 104 / 3 / 0 |
| `decisions_that_existed` | **107** | 107 |
| scored decisions | 104 — 60 retained, 44 left | 104 — 60 / 44 |
| `discrimination_auc` | 0.5566287878787879 | 0.5566287878787879 |

**Identical to the last digit.** Nothing landed between 2026-09-18 and this commit moves this
population, so the pre-producer half of the comparison is established and does not need re-running:
whatever the ON leg eventually reports, the difference is attributable to the producer and to
nothing else. That is the whole purpose of running the OFF leg at today's HEAD rather than reading
the 09-18 file, and it is the one part of the design that paid off immediately.

Its own null, off its own roster (`_auc_from_a_roster`, tie-corrected): **sd 0.05755173**, untied
0.05757077, 95% half-width **0.11280**, AUC 0.98 sd from 0.5 — it does not clear.

## 3. The ON leg's death, and it is not the producer's bug

```
File "simulation/run_phase2b.py", line 2496, in _main
    _journey_state = _churn_journey_register.advance(billing_account, ...)
File "simulation/churn_journey.py", line 218, in advance
    journey = self._journeys[customer_id]
KeyError: 'SYN-2016-008'
```

**The pairing, and where it comes apart.** Inside the decision-leg block
(`if term_index >= 1 and commodity == _decision_leg and not _indexed_tariff:`):

* the **registration** — `get_journey(...) is None` → `register_customer(...)` — sits inside
  `if old_decision_leg_rate is not None:`;
* the **advance** sits OUTSIDE that branch, at the end of the same block.

So the pairing holds only while every account's decision leg opens on a product that strikes a
rate. **An account that opens on the DEFAULT TARIFF never strikes one**, reaches its first in-window
term unregistered, and dies. The producer did not create this defect; it created the first account
that could walk into it. This is the shape CLAUDE.md names as a branch that exists to be taken
rarely — except here the rare branch was not merely untested, it was unreachable until a world
change made it reachable, and then it was fatal rather than wrong.

**The fix is in this commit and it is inert for every world that completes today.** The registration
guard is repeated immediately above the advance, and `tenure_for_est` is hoisted out of the
`old_decision_leg_rate is not None` branch so both sites use one expression rather than two copies.
An account reaching that line unregistered RAISED, so the new branch is reachable only in worlds
that currently cannot finish at all — it cannot move a published figure. That is the argument for
repairing it at the call site rather than in the producer, and it is checkable: every completed run
on disk is unaffected by construction.

**The repair is verified on the window that killed the run, not argued.** The full ON leg died at
`2017-03-29`, inside a 2016–2017 window, so that window reproduces the death for 255s of the box
instead of 880s. After the repair, `--leg arrivals_on --end-year 2017` **completes**: 35 `svt` on
the roster, 30 priced, 0 declined, `decisions_that_existed` 30, against the same truncated OFF leg's
29. **That +1 is NOT the answer to the drawn question** — a truncated window is a different
population, and the arrival exits this question turns on first appear at term index 4, mostly beyond
2017. It is quoted here as proof the branch now runs, and for no other purpose.

## 4. The alarm that has been firing all day, and what it was missing

`docs/staging/WORKER_FINDING_REPEATING_ALARM_RUN_FAILED_AFTER_S_KEYERROR_SYN_FULL_TAIL_IN_SIM_2026-09-19.md`
— *"[SIM] Run FAILED after 989s — KeyError: 'SYN-2016-008'"*, signature `auto:1c699a83ecb45075`,
first seen **2026-09-19T11:09:21Z**, escalated after 3 repeats, filed `Severity: LATENT · Atom:
unminted` with the note *"draw this, diagnose the condition, and either fix it or record why the
alarm is wrong"*.

**Same KeyError, same account, same site.** The alarm predates the producer's landing (`7bff15179`,
16:24 BST) by about five hours, which says the producer was live in a working tree and being run
before it was committed — the ordinary case in this tree, and the reason the alarm looked causeless
to everyone who read it. It is not causeless and it is not latent: it is the world refusing to
complete a pass. **It should be archived against this commit, and its severity was wrong.**

*What would refute the attribution:* a run at a tree with no arrival producer in it, before 11:09Z,
that raised the same signature. I have not found one, and the OFF leg — which IS that tree, at
today's HEAD — completes.

## 5. What is settled and what is NOT

**P3d (the patch fires) — CONFIRMED.** OFF leg: 232 of 232 `None`, zero `'svt'`. The counter that
would have raised on an inert rebind did not need to.

**P3b and P3c — the arithmetic stands on the OFF leg and is unchanged by the crash.** The null is
`sqrt((n1+n2+1)/(12 n1 n2))`. At 60/44 the half-width is 0.11280 and halving it needs **416** scored
decisions — four times today's 104. No repair touching 35 accounts of 226 can deliver that, whatever
sign its effect has.

**P2 and P3a — NOT SETTLED, and I will not guess the sign.** P2 (landed at `7bff15179`) predicts
`decisions_that_existed` above 107; my P3a predicts below it. The measurement that separates them is
the ON leg, and the ON leg cannot run until the repair in §3 is in the tree. It is relaunched here
and the answer is owed. **Nothing in this document may be read as evidence for either, and neither
prediction has been revised.**

**The explicit sentence the drawn item asks for, on the evidence I have:** *the rank leg did not get
cheaper today.* The only measured population is the OFF leg's 104, which is exactly what it was on
2026-09-18; the route that might widen it is still open and still unmeasured.

## 6. Owed

- The ON leg, and P2/P3a settled against it. Relaunched as `longjob-arrival-decision-population`
  after the repair; the fold lands at `docs/observability/arrival_decision_population.json`.
- The repeating-alarm document archived against this commit, and its `LATENT` severity corrected.
- **Not done here:** whether any OTHER route into that advance exists for an account with no struck
  rate. I fixed the pairing, not the class; a survey of every `advance`-like call whose registration
  sits inside a narrower branch is a separate pass and is not claimed.
