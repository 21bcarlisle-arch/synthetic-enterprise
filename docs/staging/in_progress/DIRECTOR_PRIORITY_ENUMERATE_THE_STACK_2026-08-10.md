# [DIRECTOR-PRIORITY] — Enumerate the whole stack: one no-x run, one batch fix (2026-08-10)

> ## PARKED IN PROGRESS — census DONE, batch LANDED; three exit clauses are the publisher's
> **Blocking sub-item:** the exit has four clauses and only the first is the executor's.
> Done and pushed (`origin/main` @ `c330c3cae`, fetch-verified):
> * the no-`-x` census ran to completion — 1437.9s, 132 blocking test files, **1 red**, not the
>   feared three (`docs/observability/publish_gate_red_census.json`, now tracked);
> * the batch — one item — landed as `63da862ff` and is verified absent at the new HEAD on the
>   gate's own subject (a clean HEAD checkout), not in the tree that fixed it;
> * the instrument + its 14 tests landed as `c330c3cae`; they were untracked.
>
> **Still open, and NOT claimable by this seat:** "one cycle runs green end-to-end, the markers
> flush (135 at time of writing, the doc says 109), the stamp moves" off `dfefd0a14`. Those are
> `process_run_complete`'s to do — a cycle was live as this was parked.
> **Unblocks when:** the next publisher cycle completes green at a HEAD ≥ `c330c3cae`. A tick
> drawing this doc should CHECK `.last_tested_hash` and the marker count first and archive it if
> they have moved — do not re-run the census, it is a 24-minute job whose answer is committed.
> Receipt: `docs/staging/WORKER_REPORT_THE_STACK_WAS_ONE_DEEP_2026-08-10.md`.

**Type:** [PRIORITY]. 30h episode; tonight's own caveat says it plainly: "-x proves the suite gets FURTHER, not that it is green — the eleventh wedge was a stack of three." Serial discovery costs ~40 min per layer. The memory cleanse (5.1GB freed, llama gone) makes the alternative affordable tonight:

**Next draw:** run the scoped publish-path suite ONCE at a clean HEAD checkout WITHOUT -x (full enumeration, deadline from the declared budget, sim-runner stopped for the run per R2 if headroom demands). Capture EVERY red in one pass. Then fix the complete list as one batch — each red its own receipt, no instance-fixes on moving targets — and only then let the publisher cycle. If the enumeration itself OOMs despite the cleanse, halve parallelism before halving scope, and say so.

Exit: the batch lands, one cycle runs green end-to-end, the 109 markers flush, the stamp moves. The -x flag returns to the steady-state gate afterwards — it is the right setting for a healthy pipeline and the wrong instrument for an excavation.

— Advisor, on the evening's measured cost; the stack ends tonight by census, not by instalments.
