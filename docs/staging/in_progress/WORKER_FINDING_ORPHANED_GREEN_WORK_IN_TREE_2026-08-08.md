<!-- SUPERVISOR_DRAW: available -->
> **PARKED IN_PROGRESS 2026-08-08 (later tick). Sub-item 2 is CLOSED; 1 and 3 are the open half.**
>
> **Done — sub-item 2, the `premise_trace` orphan is disposed.** Owning atom identified by exact
> `file_scope` match: `W1_12_premise_trace_generator`. ADOPTED and committed as `46422b0d6`
> (pushed; `origin/main` verified at that SHA), attributed as an adoption, not as this tick's build.
> It did **not** verify clean: the orphan regressed `test_the_verdict_is_WORST_CELL_not_an_average`,
> which passes at HEAD (checked in a detached worktree). Diagnosed rather than patched — the verdict
> logic is correct; `_smooth` cannot out-run the natural spread of the more diverse population the
> atom now produces, and the fixture's own discrimination guard passed for the wrong reason. Repaired
> with a dominating mutation (`_flatten_within_day`) plus an explicit argmin assertion, R15
> mutation-tested both ways. Level HELD at L2 — the generator is still not wired into the demand
> path and the COUPLED_TRIAD gap vs `C14_thermal_parameter_inference` is unmeasured.
>
> **Blocking sub-item — 1, the tick-exit check.** This is the CLASS fix (R10) and the only thing that
> stops the next instance; sub-item 2 was the third instance found by accident. It is prose-only right
> now, which by MAKE_IT_STICK means it will evaporate. **What unblocks it:** a mechanism in
> `background/` that, before a bounded invocation exits, reports uncommitted tracked changes outside
> the tick's own `file_scope` — whose atom they match, whether their tests pass, whether a level move
> is recorded — and REPORTS only, never auto-commits. Sub-item 3 (the `maturity_map.yaml` contention
> note, relates to unbuilt `H9_map_write_serialisation`) rides with it.
>
> Left here deliberately so the draw re-surfaces the unbuilt half. Do not bulk-archive to silence it.

# [WORKER-FINDING] Green work is dying uncommitted in the shared tree (2026-08-08, AO2 tick)

**Class:** work-at-risk. **Found by:** the 21:04 tick, while committing `AO2_write_time_reuse_gate`.
**Status:** one instance ADOPTED and committed, one instance STILL AT RISK, class NOT closed.

## What was observed (observed-with-evidence, R9)

Committing AO2 required staging `docs/design/maturity_map.yaml`. The level-promotion gate refused the
commit — not for AO2, but for **a different atom's unrecorded level move sitting in the same file**:
`W2_16_payment_outcome_rng_substream_isolation`, moved 0→2 by an earlier tick that never committed.

Checked rather than assumed:

* the authoring tick's last write was **20:45**; this tick started **21:04**; `ps` showed **no other
  worker process alive**. So: died dirty, not in flight.
* its build was **complete and green** — `simulation/arrears_engine.py:117` defines `bill_substream`,
  all four consumers migrated, `test_arrears_engine.py` + `test_dd_collection_book.py` = **77 passed**.
* **Adopted, verified and committed** as `14e00c2ba`, with the level move recorded in
  `gate_authorizations.jsonl` explicitly as an **adoption** — honest attribution, so the ledger does
  not read as if this tick built it.

## The instance still at risk

`simulation/premise_trace.py` (+176 lines) and `tests/simulation/test_premise_trace.py` (+146 lines)
are **uncommitted in the working tree**, from a *third* tick — household routine-offset work
(the "population envelope is not any single household's clock" argument, an L2.3-class point-mass
defect). **51 tests pass.** This tick did **not** adopt it: it did not block AO2, its owning atom was
not identified, and adopting an unidentified atom's work is a worse defect than leaving it one more
tick. It is one broad `git checkout`/`git add` away from being lost or silently swept.

## Why this is a CLASS, not two incidents (R10)

Three ticks in one evening left green, uncommitted work in a shared tree. The bounded-invocation
contract says *"do the drawn work, commit it, then STOP"* — but a tick that is cut off, or that exits
believing it has finished, leaves the tree carrying value that **only a later tick's accident**
discovers. AO2's gate found this one by luck: it happened to need the same file. Nothing looks for it
on purpose.

The existing machinery is adjacent but does not cover this: `fork_reconciler` watches **fork
branches**, and the unmerged-work draw guard reads **git reality for branches** — both miss
**uncommitted working-tree state on `main` itself**, which is where all three instances lived.

## WORK THIS CREATES

1. **A tick-exit check** — before a bounded invocation exits, report uncommitted green work in the
   tree that is outside its own `file_scope`: whose it is (map cell / recent commits), whether its
   tests pass, and whether it is recorded. Report, never auto-commit — auto-committing another
   lane's half-finished build is the mirror defect.
2. **Dispose of the `premise_trace` orphan** — identify the owning atom, verify, then adopt-and-record
   or discard with a reason. Do not leave it a third night.
3. **A map-file contention note** — two ticks editing `maturity_map.yaml` cannot be separated by
   pathspec, so one tick's commit necessarily carries the other's cell. The ledger record is what
   keeps that honest; the alternative (reverting the other cell) destroys live work and is worse.
   Relates to `H9_map_write_serialisation`, still unbuilt.

*Queued, not fixed on sight, per SELF_INTERRUPT_DISCIPLINE — the machine was not blocked.*

---

## ADDENDUM (2026-08-08, the adopting tick) — a FOURTH instance, and it is worse

Having disposed of sub-item 2, this tick ran sub-item 1's check BY HAND, once, before exiting — which
is the whole argument for mechanising it. It found more (observed-with-evidence, R9):

* **`company/billing/credit_balance_control.py` is UNTRACKED**, with `tests/company/billing/
  test_credit_balance_control.py` likewise untracked. **14 passed.** Untracked is the *worse* shape of
  this class: it is invisible to `git diff`, so every review that looks at the diff sees a clean tree,
  and the local suite is green *because the file is there* — the "untracked build passes local-green"
  pattern that has now bitten this project a third time. Plausibly the build behind
  `ADVISOR_RESEARCH_CREDIT_BALANCES_2026-08-04.md`, still in staging.
* Modified and green alongside it: `tests/company/billing/test_direct_debit_characterization.py`,
  `test_invoice_characterization.py`, `tests/tools/test_generate_billing_ledger.py` (**182 passed**
  together), plus `tools/couple_supply_start.py`, `tests/tools/test_generate_billing_ledger_pw.py`,
  `tests/company/pricing/test_thermal_inference.py`, `site/customers/test_customers_door.py`.

**NOT adopted, deliberately.** This finding's own sub-item 1 says *report, never auto-commit* — and
adopting a company-layer build without identifying its owning atom, running the epistemic verifier on
it, and checking it against the money-core characterization work in staging would be the mirror
defect. It is reported here so the next tick draws it as work rather than discovering it by accident.

**This raises the count to four instances in two days, and moves sub-item 1 from "should" to the
class fix that is overdue** (R10: an absurdity-class defect may not be closed with an instance fix).
The check must cover UNTRACKED files, not just modified ones — the instance found today would have
been missed by a `git diff`-only implementation.

---

## FOURTH INSTANCE, 2026-08-09 — same file, and a WORSE variant this finding does not yet cover

Found by the W1_12 scheduled tick. `simulation/premise_trace.py` was orphaned **again** — the file
sub-item 2 above already adopted once (`46422b0d6`). Different work this time: the entire
cold-appliance/room coupling (`cold_appliance_kwh` field, `duty_at_room_temperature`, the
separability netting and its controls). Adopted and committed this tick as `6828f999f`, pushed,
`origin/main` verified at that SHA.

**The variant that is new, and that raises the severity of blocking sub-item 1:**

The three instances above were *work at risk* — green code that would be silently lost. This one
had already been **written into the committed record**. `docs/design/maturity_map.yaml` at HEAD
described the coupling in the past tense, in detail, with test counts — while `premise_trace.py`
at HEAD contained none of it. The map asserted a mechanism git did not contain.

That is strictly worse than losing the work, in two ways:

1. **Reconstruct-from-repo-alone silently fails.** The IaC test in CLAUDE.md's operational-layer
   rule is that the repo alone rebuilds the system. Here the repo alone rebuilds a system whose
   own records claim a defect is fixed when it is not. Nothing fails loudly; the L1.5 artefact
   just comes back.
2. **A downstream finding inherited the false premise.** `WORKER_FINDING_FABRIC_WORST_VALUE_PIN_DRIFTED`
   cleared HEAD on the reasoning *"no fabric source file is dirty in the working tree, so the
   failure reproduces at HEAD"* and guessed a commit. Both were wrong — the dirty file was the
   generator, one layer upstream of the statistic, in a subsystem the failing test never names.
   The dirty tree did not just risk work; it produced a **wrong published diagnosis**.

**What this does to sub-item 1.** The proposed exit check ("report uncommitted tracked changes
outside the tick's own file_scope") would have caught this — but the higher-value check is the
*converse*, and it is cheap: **a level/evidence row naming a mechanism that does not exist at
HEAD**. Sub-item 2's own adoption of this same file did not prevent a recurrence one day later,
which is the two-strike signal (R3) that the per-instance adoption is not the fix. Still prose;
still, by MAKE_IT_STICK, still evaporating.

**Also still orphaned in the tree right now, untouched by this tick** (a fifth instance, left
deliberately rather than swept into an unrelated commit): the C-S scale-constraint work —
untracked `tests/system/scale_constraints.py`, `tests/system/test_scale_constraints.py`,
`tests/system/test_scale_constraint_mutation.py`, `docs/design/SCALE_CONSTRAINT_CHECKS.md`,
`docs/design/TIME_SCALE_INVARIANCE_REGISTER.yaml`, plus modified `tests/conftest.py`,
`tests/background/test_operational_layer_signal.py`, `tests/background/test_publish_gate_scope.py`,
`tests/system/test_report_only_landing.py`. Not verified, not adopted — it is a different atom's
`file_scope` and adopting it blind is how in-flight work gets swept.
