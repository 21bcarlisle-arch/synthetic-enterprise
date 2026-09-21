**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
"the run ledger is tracked and never committed so HEAD's copy is 64 days stale"

# Pre-registration: is the site's published run-history series built from the stale `HEAD` ledger?

**Written BEFORE the measurement, delivery seat, 2026-09-19. Left uncorrected beside its results in
the result document. The question is §5 of
`SEAT_RESULT_ONE_QUANTITY_TWO_VINTAGES_AND_THE_RUN_LEDGER_HAS_BEEN_UNCOMMITTED_FOR_64_DAYS_2026-09-19.md`,
which filed it explicitly as "inferred, not yet measured".**

---

## What is known before measuring

- `docs/observability/run_history.json` is **tracked** and has been ` M` on the shared tree since
  2026-07-17. In this worktree (and every fresh checkout) it holds **100 entries, last
  `2026-07-17T09:57:51Z`, git `ac0869715`, £1,521,069.65**.
- `tools/generate_dashboard_data.py` reads it in two places — `extract_run_history()` (last 10, the
  published series) and `count_run_history_total()` (the Project tab's **"Sim runs"** KPI) — and
  writes both into `site/data/dashboard.json` as `run_history` / `run_history_total`.
- `background/process_run_complete.py` calls `generate_dashboard_json(...)` **on the shared tree**,
  immediately after `append_run_history(...)` has written the live ledger.
- The publish gate grades a throwaway `HEAD` checkout (memory: the gate never grades the worktree).

## The predictions

**P1 — the published figures are FRESH, not stale.** The committed `site/data/dashboard.json`
carries `run_history_total` > 100 and a `run_history[-1].generated_at` in September 2026, because
the only writer of that file is `process_run_complete` running on the shared tree, where the live
ledger is. Confidence: **medium-high**.

**P2 — nothing regenerates `dashboard.json` inside the publish gate's `HEAD` checkout.** The gate
*grades* the site; it does not rebuild its data. Confidence: **medium**.

**P3 — if P1 and P2 both hold, the exposure is LATENT, not live.** The site is not publishing a
64-day-old series today; what is true is that the published artefact and its committed source
disagree, so any rebuild from a clean checkout — a gate that gains a regeneration step, a machine
rebuild, a disaster recovery — would silently reset the "Sim runs" KPI to 100 and the series to
July. Confidence: **conditional, high**.

**P4 — the decision is very nearly determined regardless of the result.** The ledger is read by a
**published** surface, so "untracked machine-local state, delete `HEAD`'s copy" would leave a fresh
checkout publishing `run_history_total: 0` — the census-loader comment in `count_run_history_total`
already reasons that 0 is *honest*, but honest-and-wrong on the live site is not the trade we want.
So I expect to land **TRACKED, and committed by `process_run_complete` with the run's other
artefacts**. What the measurement changes is the **severity** of the finding and whether a control
is owed, not which shape wins. Saying so now is the point of writing this down: if the measurement
had been allowed to pick the shape, I would be claiming a prediction I never made.

**P5 — what would refute P4.** If `dashboard.json`'s run-history fields turn out to be built from
something else entirely (a different ledger, a derived artefact), or if nothing published reads the
file at all, then it *is* machine-local state and the untracked shape wins. I do not expect this.

## What will be measured

1. `git show HEAD:site/data/dashboard.json` → `run_history_total`, `len(run_history)`,
   `run_history[-1].generated_at`.
2. The same fields on the shared tree's working copy, and the shared tree's live ledger count.
3. Whether any publish/gate path calls `generate_dashboard_data` (grep the gate, not the theory).

## The control this will owe, keyed to the property and not to today's answer

**Property:** *the published run-history series and the ledger a fresh checkout would build it from
are the same vintage.* Not "the ledger has ≥ N entries" (goes green the day the file is deleted)
and not "`run_history_total` is 137" (goes red the day a run succeeds).
