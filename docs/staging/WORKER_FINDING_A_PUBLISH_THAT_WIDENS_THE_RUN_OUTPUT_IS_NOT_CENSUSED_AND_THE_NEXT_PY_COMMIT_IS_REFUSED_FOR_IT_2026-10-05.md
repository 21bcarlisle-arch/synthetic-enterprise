**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` — publish-gate wedge draw

# A publish that widens the run output is not censused, and the next `.py` commit is refused for it

## What held the publish

The publish commit `a88fb2436` passed its gate and landed locally. Its push was refused because
origin had moved to `2b8644248`, D48 slice 1. The two sides share no paths. `origin_reconcile`
should have merged them on its next 5-minute pass. Instead, from 22:06 UTC every pass logged
`REFUSED_GATE` and a line that named no gate.

The full gate output, captured by wrapping `_classify_merge_failure`, shows the cause. The
wall-channel census found ten `F_published_artefact` keys newly read by
`saas/reporting/annual_report.py`, plus nested widening under twelve already-pinned keys. Run alone,
the census is green at `998814330` and at `2b8644248`, and red at `a88fb2436`.

## Why the publish passed and the merge did not

- **The publish commit was never censused.** `_wall_channel_census_check` in
  `tools/pre_commit_test_gate.py` returns early unless the commit stages a `.py` file or the
  baseline. Channel F's subject is `docs/reports/run_output_latest.json`. The one commit that
  widens it stages only JSON and Markdown, so it skips the step.
- **The bill went to the next `.py` commit.** That was the reconciler's merge, which carries D48's
  code. Neither D48 nor the merge wrote a crossing.
- **No crossing was written at all.** Every one of the ten reads predates the artefact. The earliest
  is `_cache_meta` (2026-06-15), the latest `opening_dd_by_customer` (2026-10-01). The artefact
  was last published on 2026-09-09, so it lacked the keys and the census could not see the reads.
  - *Correction, beside the claim:* this note first said all ten were already in the frozen flat
    list. They were not. A `--worktree` census over a trial merge read the flat channel differently
    from the gate's `--rev` and showed them as present. As a result, `d23344555` pinned only the
    nested schema. The merge `556b24b4e` passed its gate because it staged no `.py` (the same
    early return), so origin/main briefly refused every `.py` commit. The flat rows land in the
    commit that carries this note. **Verify a baseline with `--rev <the tree>`, never `--worktree`.**
- **The diagnosis was cut off as well.** `_classify_merge_failure` kept the first 400 characters
  after `GATE RED`, which are the `[live-hook]` preamble. The same defect was fixed for
  `MESSAGE GATE RED` on 2026-10-01; the test-gate branch never got the fix.

## What landed

1. The baseline gains the ten flat rows and the nested pins as a pure union, added by hand: nothing removed and no `--freeze`.
   The ruling is in `_meta.last_freeze`. Two `sim_` fields became visible under `customer_events`
   (`sim_experienced_bill_shock`, `sim_month_count_bill_shock_base`). They are read by no module
   in `company/` or `saas/`; the readers are `simulation/` and `tools/capture_departure_factors.py`.
2. `a88fb2436` is merged into origin.
3. The `GATE RED` branch now quotes from the refusing step's `❌` banner. There is a new test, and it
   reds when the fix is reverted.

4. **The merge also turned a live test red, fixed in the same commit.** At the merge, the
   artefact's last commit (`a88fb2436`) and its producer's last commit (D48's edit to
   `simulation/run_phase4c_on_phase2b.py`, `2b8644248`) are siblings. `_strictly_precedes`
   returns None for a fork, so `test_THE_LIVE_ARTEFACT_IS_DATED_AGAINST_ITS_PRODUCERS` read
   UNDETERMINED and was red on origin.
   - A fork is an answer: the artefact cannot carry a change outside its own history, so the
     producer is now counted as `predates` (stale). That is the unflattering direction.
   - git *failing* to answer is still undetermined.
   - This would have recurred at every reconciler merge of a publish with a moved origin.
   - There is a new fork test, and it reds when the fix is reverted.

## What is NOT fixed, and the recommendation

The early return still lets a publish widen channel F unseen and bill the next `.py` commit. That
will recur at every publish that refreshes the artefact after the readers have moved.

Adding `run_output_latest.json` to the trigger does not fix it by itself. The nested pin includes
customer-id-keyed dicts (`years`, `per_cid_comm_pnl`, `demand_provider_by_customer`,
`clv_snapshots`), whose "fields" are account ids. Those change with every book, so every publish
would refuse. `nested_freeze_note` already records this pin as frozen under protest.

**Recommendation, in order:**

1. Teach `nested_schema` to treat a dict whose keys are account ids or months as one wildcard
   field, so the pin stops moving with the book.
2. Then add `ARTEFACT_REL` to the census trigger, so the publish that widens the artefact is the
   commit that answers for it.

Doing step 2 alone would wedge the publisher on every run.
