**Pre-registration, filed before either run.** Claim `restore-the-journey-decision-for-an-svt-conversion`.
**Graded in:** `docs/staging/WORKER_FINDING_AN_SVT_CONVERSION_NOW_RECORDS_A_STAYED_DECISION_AND_NOTHING_ELSE_MOVES_2026-10-02.md`

# An SVT conversion records a stayed decision on its journey

**2026-10-02, autonomous worker.**

## The change

`simulation/run_phase2b.py`, renewal block: a household converting off the SVT
(`departure_rolled_at_renewal` is False) now calls `_journey.record_decision(..., switched=False)`.
The departure roll stays off. A new SIM-side output, `renewal_decisions_log`, gets one row for each
decision the journey records, with `rolled` and `switched`.

## A correction to the item, made before the run

The item asks me to restore three side effects: the journey decision, the retention-log outcome and
the `nudge_physics_log` row. Only the first was lost. The `if event is not None:` block has an
`elif retention_modifier_val is not None and retention_log:` arm about 200 lines down. When
`event` is None, which is every conversion, that arm already labels the retention entry
`retained` and writes the nudge row. Moving those two writes into the conversion branch would
have written the nudge row twice. So this change restores the journey decision and nothing else.

## What reads the journey

Nothing in the run loop reads a journey's state. Its only reader is `churn_journey_log`, which is
written by `advance()` at each renewal, before the roll, and read only after the run, by
`annual_report` and the dashboard. `record_decision` draws no random number.

## Predictions (base = origin/main `ed7e89d0e`, change = the same commit plus this diff, one default world each, run serially)

- **P1. Whole-book departures: no change at all.** The count of `churned` customer events, in
  total and in each year, is identical. More strongly, the whole `customer_events` list is
  identical, row for row.
- **P2. Retention outcomes and nudge rows: no change.** `retention_log` outcomes and the
  `nudge_physics_log` row count are identical.
- **P3. Engaged decisions recorded on the journey go UP, by exactly the number of conversions.**
  The count of `renewal_decisions_log` rows in the change equals the base's count of rolled
  renewal events plus the number of `svt_conversion` rows, overall and in each year. The base
  has no such log, so the base count is the rolled events in `customer_events`.
- **P4. Later-year journey states move toward CONTENT and away from COMPARING.** The total count
  of `churn_journey_log` rows is identical. In years after the first conversion, rows in
  `comparing` FALL (or at least do not rise), and rows in `content` RISE (or at least do not
  fall). I predict a strict fall in `comparing`, with moderate confidence. It needs at least
  one converter, not resentment-burned, that had reached IN_MARKET or COMPARING when it
  converted. A burned journey is forced back to COMPARING on every advance, so a burned
  converter does not move.

If P1 or P2 fails, something in the loop reads the journey, and that path is the finding.

---

## Amendment, 2026-10-02 05:55Z, delivery seat. Filed BEFORE either default-world run.

**The base moves.** `ed7e89d0e` is no longer origin/main. Run base and change on whatever
origin/main is when the runs start. Write that commit into the finding. No `simulation/` or
`company/` path has moved since `f18e8b5dc` (`git diff --name-only f18e8b5dc 7e15fc9f9 --
simulation company` is empty). The exemption below is keyed to `f18e8b5dc` as the run commit.

**A second channel for P4, read from the code before any default-world run.** `record_decision(switched=False)`
sets `STAYED_SVT`. The next `advance()` resets `STAYED_SVT` to `CONTENT`. So a converter in
**IRRITATED** also moves, back to CONTENT, as well as a converter in IN_MARKET or COMPARING. P4
still reads "comparing does not rise, content does not fall". I add: **`irritated` does not rise in
years after the first conversion.** The STAYED_SVT label also names the wrong thing for a
household that just left the SVT. That is a naming defect in `churn_journey.py` and I am not changing it here.

**A fixture reading, not the graded run.** 2016–2018, `SIM_FAST_MODE=1`, base `7e15fc9f9` vs
change, one process each:
- P1 holds. `customer_events` is identical row for row (49 rows), and churned is 9 in 2017 and 4 in 2018 in both.
- P2 holds. `retention_log` is identical, and `nudge_physics_log` has 16 rows in both.
- P3 holds. 49 decisions = 33 rolled + 16 conversions, and it holds in every year (2016 1=1+0, 2017 26=22+4, 2018 22=10+12).
- P4 cannot be tested here. Journey rows are 49 in both, and the state counts per year are identical
  (2016 content 1; 2017 content 26; 2018 content 17, irritated 5). The window has no `comparing` row at all.

**The control.** `tests/simulation/test_run_phase2b.py::test_an_svt_conversion_records_a_stayed_decision_on_its_journey`.
It is green with the change. It is red when the condition is mutated back to `if event is not None:`
(`assert (True and False)` on the partition line).

**Not landed, deliberately.** Landing `simulation/run_phase2b.py` before P1 and P2 are graded on
the default world would withdraw the `f18e8b5dc` world-D retake as "not HEAD's code" on the page.
The retake (`longjob-arms-floor-d-head-1002b`) is on the box until about 10:45. The diff is
below, so the work survives this turn.

### The default-world recipe (run each in a SCRATCH worktree, serially, after the retake exits)

`main()` with no `report_end` and with `SIM_FAST_MODE` unset. It MUST be passed a scratch
`gap_ledger_path`. The default path is the live coupled-gap ledger. The run also writes
`docs/observability/book_growth_campaign.json` and `book_subset_verdict.json` into the tree it runs in.

```python
import json, os, sys, tempfile
from pathlib import Path
os.environ.pop("SIM_FAST_MODE", None)
sys.path.insert(0, os.getcwd())
from simulation.run_phase2b import main
r = main(gap_ledger_path=Path(tempfile.mkdtemp()) / "g.json")
keep = {k: r.get(k) for k in ("customer_events", "retention_log", "nudge_physics_log",
                               "churn_journey_log", "renewal_decisions_log")}
Path(sys.argv[1]).write_text(json.dumps(keep, default=str, sort_keys=True))
```

### The diff (apply to `simulation/run_phase2b.py` and `tests/simulation/test_run_phase2b.py`)

```diff
diff --git a/simulation/run_phase2b.py b/simulation/run_phase2b.py
index 901dd5680..a8526c17c 100644
--- a/simulation/run_phase2b.py
+++ b/simulation/run_phase2b.py
@@ -1789,6 +1789,8 @@ def _main(report_end: str | None = None, policy: DecisionPolicy | None = None,
     _cx_desk = CustomerExperienceDesk()
     _churn_journey_register = ChurnJourneyRegister()
     churn_journey_log: list[dict] = []
+    # One row per decision the churn journey records at a renewal, rolled or not.
+    renewal_decisions_log: list[dict] = []
     # Phase RU: solicited feedback survey engine (FEEDBACK_AND_REPUTATION.md Layer 1)
     feedback_survey_log: list[dict] = []
     reputation_events_log: list[dict] = []
@@ -2708,10 +2710,19 @@ def _main(report_end: str | None = None, policy: DecisionPolicy | None = None,
                     engagement_level=_engagement_level_str,
                     unit_rate_gbp_per_mwh=unit_rate,
                 ))
+            # A conversion off the SVT is still an engaged decision to stay -- the household chose
+            # a fixed deal -- so the journey records it as it does a rolled renewal. Skipping it
+            # with the roll (1cd4b03dc) changed what `advance()` reads at the next anniversary.
+            # `record_decision` draws no random number, and nothing in this loop reads the journey
+            # except `churn_journey_log` (graded in WORKER_FINDING_AN_SVT_CONVERSION_NOW_RECORDS_*).
+            if event is not None or not _rolled:
+                _switched = event is not None and event["event_type"] == "churned"
+                _journey.record_decision(date.fromisoformat(term_start_str), switched=_switched)
+                renewal_decisions_log.append({
+                    "customer_id": billing_account, "term_start": term_start_str,
+                    "commodity": commodity, "rolled": _rolled, "switched": _switched,
+                })
             if event is not None:
-                _journey.record_decision(
-                    date.fromisoformat(term_start_str), switched=(event["event_type"] == "churned"),
-                )
                 event["is_active_renewal"] = active_renewal
                 # Phase 2 Layer 1: SIM-internal ground truth, retained here for
                 # evidence-surface use only (same pattern as credit_bureau_true_
@@ -4044,6 +4055,7 @@ def _main(report_end: str | None = None, policy: DecisionPolicy | None = None,
         # Phase QL Part 2: hidden churn-journey state trajectory (SIM-side shadow
         # tracker -- does not gate the roll_lifecycle_event dice roll itself)
         "churn_journey_log": churn_journey_log,
+        "renewal_decisions_log": renewal_decisions_log,
         # Phase RU: solicited feedback survey engine (FEEDBACK_AND_REPUTATION.md Layer 1)
         "feedback_survey_log": feedback_survey_log,
         "reputation_events_log": reputation_events_log,
diff --git a/tests/simulation/test_run_phase2b.py b/tests/simulation/test_run_phase2b.py
index c77901c57..5a94e0a15 100644
--- a/tests/simulation/test_run_phase2b.py
+++ b/tests/simulation/test_run_phase2b.py
@@ -610,3 +610,22 @@ def test_a_household_converting_off_the_svt_leaves_a_renewed_row_in_the_run(_pha
     assert unrolled, "no SVT conversion was logged in 2016-2018"
     assert all(e["event_type"] == "renewed" and e["random_roll"] is None for e in unrolled)
     assert any(e.get("random_roll") is not None for e in events)
+
+
+def test_an_svt_conversion_records_a_stayed_decision_on_its_journey(_phase2b_result_2017):
+    """Defect: 1cd4b03dc skipped `record_decision` with the roll, so a conversion left no decision.
+
+    Asserts both arms of the partition -- rolled renewals AND conversions -- reach the log before
+    asserting what each writes, so a loop recording only one of them cannot pass.
+    """
+    events = _phase2b_result_2017["customer_events"]
+    decisions = _phase2b_result_2017["renewal_decisions_log"]
+    assert any(d["rolled"] for d in decisions) and any(not d["rolled"] for d in decisions)
+    conversions = {(e["customer_id"], e["event_date"]) for e in events
+                   if e.get("departure_rolled") is False}
+    unrolled = {(d["customer_id"], d["term_start"]) for d in decisions if not d["rolled"]}
+    assert unrolled == conversions
+    assert not any(d["switched"] for d in decisions if not d["rolled"])
+    rolled_events = [e for e in events if e.get("random_roll") is not None
+                     and e["event_type"] in ("renewed", "churned")]
+    assert len(decisions) == len(rolled_events) + len(conversions)
```
