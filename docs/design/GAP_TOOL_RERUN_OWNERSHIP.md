# Which surface owns re-running a gap tool (2026-08-10)

**Status:** decided and mechanised (RUNG 4b, `background/supervisor.py::_stale_gap_row_draw`).
**Answers:** the design pass registered as residual (d) of `H_GAP_fabric_belief_truth_gap` on five
consecutive ticks, and explicitly deferred by
`WORKER_FINDING_DERIVED_ARTEFACT_STALENESS_IS_A_WEDGE_CLASS_2026-08-09` ("both are defensible and
the choice wants a design pass, not a guess").

## The question

`docs/observability/coupled_gap_ledger.json` holds one row per coupled pair: a belief-vs-truth gap
number, the commit it was measured at, and the money consequence. `site/data/proof.json` renders
them, so these are numbers on a public door. `background/gap_ledger_reconciler.py` (built
2026-08-09) answers one mechanical question per row — *has the code that produced this number
changed since?* — and is REPORT-ONLY by construction.

That left half a control. Five consecutive worker ticks read the drift set and cleared it **by
hand**; nothing in the machine re-runs a gap tool. A drift set no lane can act on is the exact
shape of the overnight operational-red incident: an alarm that pages for thirteen hours because no
draw rung ever surfaces "go clear it".

## Why the answer is not "the same place the derived-artefact class went"

The wedge-class tick (2026-08-10) put projection repair in the **publish path**
(`process_run_complete._repair_derived_artefacts_in`). That is right for a projection and wrong
here, for reasons that are about the artefact, not about taste:

| | derived artefact (`BLOCKED_ATOM_VISIBILITY.md`) | gap ledger row |
|---|---|---|
| what it is | a **rendering** of committed sources | a **measurement** taken over a drawn population |
| repair cost | milliseconds, deterministic | seconds to minutes each, eleven tools |
| does staleness wedge the gate? | **yes** — a blocking `--check` test reds | no — no test blocks on a stale row |
| is the output evidence? | no, it restates its sources | **yes** — the number can MOVE |
| who needs to read the result? | nobody; a diff of zero lines is the success case | a human, because a moved gap is a finding |

The last row decides it. Re-rendering a projection has no reading; re-taking a measurement
does — this atom's own record spent a paragraph on a 4th-decimal move in `inferred-vs-actual` and
declined to attribute it. Automating that into a silent path would destroy the only part of the
act that was worth anything, and would republish a changed public figure with no one in the loop.

## Candidates considered

1. **The publish path**, as for projections. Rejected: adds minutes of measurement to a
   latency-critical, repeatedly-wedged surface to fix something that does not wedge it, and
   silently republishes evidence. Accretion of the kind `OPERATIONAL_COHERENCE_DESIGN_PASS`
   forbids.
2. **The reconcile-watch timer** (`background/reconcile_watch.py`). Rejected: its stated guarantee
   is REPORT-ONLY (G-R3) — "it reconciles and notifies; it starts/stops/enables/reaps NOTHING".
   Giving the watcher hands to fix what it watches also removes the independence that makes its
   verdict worth anything.
3. **Each tool re-runs itself** on some trigger. Rejected: eleven patches where one reconciliation
   already exists; the residual this closes named that trap by name.
4. **The draw ladder.** Chosen.

## The decision

**A stale published gap measurement is DRAWN WORK.** The reconcile detects it; the ladder offers
it; a tick takes the measurement and reports what moved. This is the answer this codebase has
already given twice for a report-only drift control that needed hands — the publish-gate wedge
(RUNG 1) and the persistent operational red (RUNG 1b) — and it is the answer that keeps a human
reading a changed number.

`background/gap_ledger_reconciler.refresh_work()` is the drain: the rows a re-measurement would
clear, each with the command that takes it. `supervisor._stale_gap_row_draw()` is RUNG 4b, below
the declared-defect backlog (an open product defect outranks a stale number) and above
propose-half / forward-discovery / the HARDEN treadmill (refreshing a public number beats
re-verifying a finished atom). `_is_drained_and_gated` mirrors it, so rest cannot be declared
while a stale published number is refreshable.

## Guarantees

* **Still report-only below the ladder.** The reconciler prints commands; it has never run one.
  Nothing acquired hands except the tick, which already had them.
* **It drains.** Only `stale`/`unattributable` rows — the ones re-measurement actually clears —
  are drawn. `never_landed` (a tool whose output lands nowhere) and `never_measured` (a declared
  pair with no row) are design defects no re-run touches, and are deliberately excluded: a rung
  that can never drain is a rung everyone learns to ignore.
* **Fail-closed on the worse defect.** A refreshable row whose producers are all un-invocable
  stays in the list with `command: None`, drawn as *a published number nobody can re-take* — a
  worse defect than staleness, and the one an exclusion-shaped filter would have hidden.
* **Fail-open on its own error.** A reconciler that cannot import or cannot read git yields no
  work and the ladder falls through. The rung can never invent a hold.
* **The acceptance test is the verdict, not the command.** "The command ran" is not evidence: the
  draw asks for `python3 -m background.gap_ledger_reconciler` to show the row reading CURRENT,
  which the reconcile decides independently of the string the draw printed.

## Evidence (2026-08-10)

* The command form was found by RUNNING one, not reading it: `python3 tools/couple_w2_4_c6.py
  --write-ledger` dies in 0.2s on `ModuleNotFoundError: simulation`; `python3 -m
  tools.couple_w2_4_c6 --write-ledger` wrote the row in 0.5s. The work list emits the module form
  and a test pins it.
* The drain is real, not asserted: that re-run moved the live drift set 11 → 10 and its row read
  CURRENT on the next reconcile.
* R15 both ways, eight source mutations with byte-clean restore (md5-verified), each firing its
  own named test: treating `never_landed` as refreshable; dropping a no-runner row instead of
  listing it; the path-form command; dropping either half of the runner test (invocable / writes);
  removing the rung from `_self_refill_draw`; removing it from `_is_drained_and_gated`; and
  removing the fail-open error path so the rung invents a hold.

## What this does NOT close

The `never_landed` entry (`tools/couple_cohort.py` carries `--write-ledger` for a pair with no
ledger row) is untouched by this rung by design. It is an orphan-transition defect and wants a
finding, not a re-run.
