# Disposition: the per-renewal decision fields landed in 5f05e0068, and the stranded copies are cleared


**Severity:** RECORDED · **Lane:** D_billing_metering
*Tick worker, 2026-09-29. Item `add-the-per-renewal-decision-fields-once-the-arrears-lines-land`,
disposed premise-spent and released.*

**The premise is spent.** The arrears lines landed in `f997f8bf7`. Then `5f05e0068` added both of
b6a21c885's fields to the artefact and to each noise-floor row: `renewal_decisions_by_arm` and
`decided_differently_by_account`. It joins on (customer_id, commodity, term_start), counts roster
differences apart, and has 10 join mutations plus 1 wiring mutation, all red. Both commits are
ancestors of origin/main. Nothing was built twice.

**The three stranded shared-tree copies (written 19:53–19:54Z on 2026-09-28), read against origin/main:**

| Path | Verdict | Action |
|---|---|---|
| `simulation/arrears_engine.py` | byte-identical to origin/main | none; the fast-forward clears it |
| `tools/run_value_cycle_ab.py` | `predates_landing`, and origin/main strictly supersedes it | `refresh_to_head --base origin/main --write`; preserved as ref `stranded-run-value-cycle-ab-2026-09-28` |
| `tests/tools/test_the_arrears_lines_reconcile_each_accounts_net_to_the_penny.py` | older draft of origin's file: it lacks the sub-penny test and the churned-event fixture | `refused_no_base` (HEAD lacks the path); the fast-forward overwrites it |

The one line the refresh discarded was the per-line `round(v, 2)` in
`_arrears_lines_by_billing_account`. That is the 1.2p reconciliation red that origin's sub-penny
test exists to catch. The stranded copy was the defective draft, not lost work.

**Retention: the log exists but is not carried.** The item asked for a grep before anything was
added for retention. A per-customer `retention_log` exists: it is built at
`simulation/run_phase2b.py:1828`, appended at :2393 with outcomes at :2598/:2787, and emitted in the
phase-2b output at :3837. `tools/run_value_cycle_ab.py` never reads it. The +880 split therefore
covers pricing decisions only. A retention-side "decided differently" join is possible from data
that already exists, but it is not built. Anyone taking it up should start by folding that log per
arm on (customer_id, event date). It needs no new logging.
