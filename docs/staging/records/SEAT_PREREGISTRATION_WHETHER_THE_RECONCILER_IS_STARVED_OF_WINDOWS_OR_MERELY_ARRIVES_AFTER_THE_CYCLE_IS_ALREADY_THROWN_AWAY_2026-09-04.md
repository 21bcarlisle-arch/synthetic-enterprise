**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# PRE-REGISTRATION: is the reconciler STARVED of windows, or does it merely arrive after the publish cycle has already been thrown away?

**Filed:** 2026-09-04 ~21:50Z, delivery seat, working the Lane 0 direction *"the publisher meets a
real fork and no fast-forward bound can close it"*. **Written before the counts below were taken.**
The direction offers two candidates and the choice between them turns on a number nobody in this
repository has looked at.

---

## The two candidates and the premise that separates them

The direction names them:

* **(a)** let the publisher COMMIT but not push when `ahead > 0`, leaving `origin_reconcile` to
  merge and push it — *"which reverses a documented refusal and needs the 2026-09-01 fork-widening
  argument answered head-on, not ignored"*.
* **(b)** give `origin_reconcile` a window the publish cadence cannot close, so its gated merge can
  actually run.

**(b) rests on a premise that is stated nowhere and measured nowhere: that the reconciler is
STARVED.** The stand-down finding says *"the reconcile window is only whatever gap is left BETWEEN
publish cycles"* and reasons from a 672s cycle. If the publish loop ran back-to-back that would be
right and (b) would be the only move. If it does not, (b) builds a window for a mechanism that
already has more windows than it uses, and the real defect is somewhere else entirely.

`origin_reconcile.reconcile()` is called from exactly one place — `deadmans_switch._check_origin_fork`,
once per `POLL_INTERVAL_SECONDS = 300` pass — and every verdict is written to
`docs/observability/deadmans-switch-log.md` as `ORIGIN FORK (<STATUS>): <detail>`. The deadman's
cadence is a fixed 5-minute timer and is **uncorrelated with the publish cycle**, so the fraction of
its passes that read `GATE_RUNNING` is an unbiased estimator of the run lock's duty cycle. That
ledger has 659 entries. The number has been sitting there the whole time.

## What each number counts, before any of them is divided

* **P(GATE_RUNNING)** — of deadman `ORIGIN FORK` verdicts, the share that stood down for the run
  lock. This is the duty cycle of `process_run_complete`'s run lock as sampled every 300s. It is
  NOT "how often a fork was refused" and it is not scoped to real forks: `reconcile()` reads the
  gate before it reports `ahead`, so a `GATE_RUNNING` line cannot say which fork it declined.
* **Real-fork branch reached** — a count of verdicts that could ONLY have come from the
  `ahead > 0 and behind > 0` leg: `RECONCILED`, `REFUSED_CONFLICT`, `REFUSED_GATE`. Every one of
  these required an isolated worktree to be built and `surgical_land --merge` to be run, so each is
  positive evidence that the gated merge got its window and ran to a verdict.
* **`NOT_ADVANCED`** counts the `ahead == 0` leg only (nothing of ours to land, shared tree will not
  fast-forward). It is NOT evidence about the real-fork branch and must not be pooled with it.

## Predictions, and what would refute this seat

**P1 — the reconciler is not starved.** `P(GATE_RUNNING) < 0.50` over the whole log.
*Refuted if* `P(GATE_RUNNING) >= 0.80`.

**P2 — the gated merge does get to run.** The real-fork branch (`RECONCILED` +
`REFUSED_CONFLICT` + `REFUSED_GATE`) was reached **at least 5 times** across the log.
*Refuted if* it was reached **zero** times, which would mean the merge has never once completed on
this cadence and the stand-down really is total.

**P3 — the publisher's refusal is not what re-opens the fork.** On the `ahead > 0` branch the
publisher makes NO commit — it refuses before staging — so the `ahead` side of a real fork is
created by seats landing through `surgical_land` without pushing, not by the publish loop. I predict
**zero** local commits authored by the publish loop (`Auto-process run complete` / publish-surface
messages) sitting unpushed at the moment a real fork is observed.
*Refuted if* unpushed publish-loop commits are found on the ahead side.

## The decision rule, fixed now

* **P1 and P2 both hold** → the window is NOT the binding constraint, (b) is answering a false
  premise, and the work is **(a)**: let the publisher preserve its cycle as a local commit and let
  the reconciler drain it. The 2026-09-01 fork-widening argument is then answered by naming its
  unstated premise rather than by overriding it.
* **P1 or P2 fails** → the reconciler genuinely cannot run, (a) would pile commits onto a fork
  nothing is closing — which is precisely the 2026-09-01 loop — and the work is **(b)**.
* **P3 fails** → neither candidate is safe as stated and the publish loop is already widening the
  fork by a route the refusal was supposed to have closed. That would be a BLOCKING finding of its
  own and takes precedence over both.

## What is NOT being claimed

This pre-registration fixes no observation of mutable state as a fact — the live fork
(`ahead=1, behind=4` in `.last_publish_cause.json` at 21:46Z) is cited as the *occasion*, not as
evidence, and it will have moved by the time anything is measured. The counts above are taken from
an append-only ledger, which cannot move backwards.
