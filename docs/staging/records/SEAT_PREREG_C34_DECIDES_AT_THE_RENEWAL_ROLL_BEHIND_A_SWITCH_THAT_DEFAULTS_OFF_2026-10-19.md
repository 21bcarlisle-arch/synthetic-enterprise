# Pre-registration: C34 gets an engine caller at the renewal roll, behind a switch that defaults off

**Written 2026-10-19 ~19:45 BST, before the build.** Claim
`c34-gets-an-engine-caller-at-the-renewal-roll-off-by-default` (Lane 0, seat direction). No code for the
caller exists yet, and no run or probe was read to write this. The build is a later commit than this
one.

## What is being built, said first

- **The switch.** A new `DecisionPolicy.next_best_action_decides_at_renewal`, default False on every
  standing policy and declared `run_argument` in `FIELD_CONSUMPTION`.
- **The trigger.** On, each domestic renewal roll on the departure leg (`_decision_leg`, with a prior
  rate) hands the company's own observables to a new door, `company/interfaces/renewal_advice.py`.
  That is the same roll where `estimate_renewal_churn` runs.
- **What the door is handed:**
  - the account;
  - the term start;
  - the fuel;
  - the monthly margin, (offered rate − company forward) × company EAC / 12;
  - the company's churn belief `company_est_pre`.
- **The riding leg.** A dual household's other leg joins when it is priced on the same start.
- **The decision.** At the end of the run the door groups the legs by (account, start) and merges them
  through `states_for_decision`. Each of the page's three stated advice effects runs through
  `next_best_action.decide`, so there is one row per household per effect, written to
  `next_best_action_renewal_log`.
- **Its limits.** The hazard is the company's belief and never the world's draw. Nothing is sent and
  nothing moves the world. `next_best_action_shares_by_retention_rise` is not touched, so the decision
  is C34 alone (no rise).
- **Knowledge:** `docs/market_research/next_best_action_and_cross_sell.md` §6.1, "Where a real
  supplier makes this decision", landed with this pre-registration.

## Predictions

**O1, off arm.** A run at the build's sha with the switch off equals a run at its parent, byte for
byte, at a fixed seed over a short window. The run-output JSON is compared after removing only the
provenance stamps (git sha and wall-clock times). Nothing on the off path draws a number, so any
difference refutes the build.

**D1, the on branch decides.**
- With the switch on, the log is not empty.
- Every row carries a `Decision` with a reason.
- The control asserts this before it asserts any refusal (CLAUDE.md, "assert it CAN be taken").

**On arm, on the 19 Oct published dual-fuel book.** The figures to beat come from `ad8afadc5` (run
`8b6fea024`) and the `dfa2f9b22` grade: 182 renewal decisions, 3/546 advised with no rise needed, and
543/546 refused by C34's floor. The caller's inputs are not the probe's:
- the hazard is the company's renewal churn belief, not B11's per-account p;
- the margin is offered rate − company forward, not flat − base.

So the predictions are bands, not digits:
- **P1. Decisions (households) are 182 ± 15.** About 77 ± 15 of them carry two legs: the dual
  households that stayed at the roll (the probe's 77 of 129).
- **P2. Advised rows are 0 to 15 of about 546 (≤ 3%).** At B11-scale inputs our side is negative in
  all 18 grid cells. Advice pays our side only above roughly £30–40 a month of household margin
  (worked from the forward-value derivative at h = 1–3%/month, 48 months). Few households reach that,
  even with both legs summed. The (£2, 0.3 point) effect carries most of what is advised.
- **P3. Floor-refused rows are at least 97% of all rows.** The reason is "no scored action leaves
  both the customer and us no worse off". Unscored rows are 0, because every stated effect is
  known.
- **P4. Per household advises at least as many as per leg.** Summing the margins can only lift our
  side.

**How it will be graded.** O1 and D1 are graded in the build commit. P1–P4 need a full on-arm run
of the published book, which is not part of DONE for this claim. They are graded when that run is
read. If the run is not read, they stay ungraded here, and this file says so.

## What would refute the design, not just a number

- **P2 above 10%.** The company's belief would then run far hotter than B11's, and C34's floor would
  not be binding where the canon says it binds. That is a finding about the churn belief, not a
  licence to switch it on.
- **P1 two-leg count near 0.** The riding-leg join would not be reaching the gas leg, which is the
  same instrument defect `608c0d0fa` fixed in the probe.

## Grade, 2026-10-19 (build commit; short window to 2017-06-30, CURRENT_POLICY, fixed seed)

- **O1 held.** The off arm at the build's code and a run at its parent (`c52f83113`, the same code as
  `ab169e127`) give run-output JSON that is identical byte for byte (`cmp`), stamps included.
- **On moves no world quantity.** The on arm equals the off arm in every one of the 96 top-level
  keys, apart from the new `next_best_action_renewal_log`.
- **D1 held.** The log holds 96 rows: 32 households × 3 effects. 1 row is advised: `PROS-2016-0170`,
  a two-leg household at £38.19/month and h = 0.034, under (£2, 0.3 pt). 95 rows are refused by the
  floor, with the stated reason, and 0 are unscored.
- **13 of the 32 households carry two legs.** That equals the 13 riding gas legs the probe wrote in
  the same window (`608c0d0fa`).
- **A defect found on the first on-arm run, and fixed before landing.** When a household declined
  the fix, the engine withdrew that term and spliced default-tariff segments on the same start. The
  splice passed the hook again, so 8 gas legs joined twice (`legs: 3`) and their margin counted
  twice. Now the first observation of each leg stands, because the notice carries the fix as first
  offered. A control covers this, and both of its guards were mutated red.
- **P1–P4 are not graded.** They need the full on-arm run of the 19 Oct book.

## The on arm for P1–P4, as launched (2026-10-19 ~21:35 BST, before any of it is read)

- **Base: `8b6fea024` itself, with 18503313a's code applied on top**, in the scratch worktree
  `/var/tmp/se-c34-grade`. It is not run at HEAD. Between the published run and HEAD the world code
  moved: the SLC 27.8D offset went on (`3d518bdef`), B7 deaths landed (`e0b301545`), split homes are
  won at P(dual | gas) 0.90 (`30246d6f0`), plus HH-EAC and budget payment. A HEAD run would read a
  different book, and the 182 and 77 would no longer be its denominators. The cherry-pick conflicted
  only on this staging file. The code applied cleanly.
- **Policy:** `CURRENT_POLICY` at `8b6fea024`, with `next_best_action_decides_at_renewal=True` and
  `next_best_action_decides_per_household=True`. The second switch was off at `8b6fea024`. It went
  on in `f6e23a535`, and the caller's design assumes it ("one row per household"). With it off, 2
  of the caller's 16 control tests fail at this base. With it on, all 16 pass. Only
  `states_for_decision` reads it, so it records and moves nothing.
- **P4 reading:** the same desk's legs are decided a second time with per-household off, on the
  same run (`per_leg_log`). P4 compares the two.
- **Book check:** every list-valued key of the phase-2b result is length-compared with the
  published `run_output_ad8afadc5_20261019T132751Z.json`. A difference is reported, not explained
  away.
- Full window, default seed, phase 2b only. The renewal log is written there, and phase 4c does not
  touch it. Unit `longjob-c34-renewal-on-arm-8b6fea024`. The script and grader are in
  `/var/tmp/se-c34-grade-out/`. The predictions above are unchanged.
- **Correction, ~22:20 BST.** That unit died at import: the script did not put the worktree on
  `sys.path`. Its log is `run.first-importerror.log`, and nothing was read from it. The fixed script
  is queued as `longjob-c34-renewal-on-arm-8b6fea024-r3` (`launch3q.out`, retrying every 60 s for
  up to 10 h). The box is full: the weekly `sim_runner` run holds 7 GB and the executor's
  `world_constant_reach` holds 4 GB. **To grade:** once `/var/tmp/se-c34-grade-out/on_arm.json`
  exists, run `python3 /var/tmp/se-c34-grade-out/grade.py /var/tmp/se-c34-grade-out/on_arm.json
  docs/reports/run_output_ad8afadc5_20261019T132751Z.json` from the repo root, then read P1–P4 and
  the book check against its lines.
- **Correction, 2026-10-20 ~00:45 BST: r3 died, and r4 is running.**
  - **Cause.** r3 was admitted at 22:16 BST and exited 1 after 18 s
    (`run.r3-policyscope.log`). `run_phase2b._main` refused it: "given policy='current' but the
    active policy scope is 'current'". The guard tests identity (`policy is not active_policy()`).
    The arm is a `dataclasses.replace` of `CURRENT_POLICY`, so it keeps the name and is still a
    different object. The fault is the script's, not the production caller's: the guard passes any
    caller that also swaps the scope. So nothing is filed against the caller. Nothing was read
    from r3.
  - **The scratch worktree had also been reaped.** By 00:40 BST, `/var/tmp/se-c34-grade` was gone
    from disk and from `git worktree list`. It was rebuilt the same way: `8b6fea024`, then
    `git diff 18503313a^ 18503313a -- . ':!docs/staging' | git apply --3way`, applied clean, with
    the six code and test paths of 18503313a. This time it is `git worktree lock`ed, a leg that
    `worktree_is_live` honours.
  - **Fix.** `run_on_arm.py` now runs `main(policy=arm)` inside `policy_scope(arm)`. Nothing else
    changed: the policy, the P4 re-decision, the artefact path and the grader are all as before.
  - **Dry run.** The same script with `report_end="2016-02-29"` exited 0 in the rebuilt worktree.
    The log was empty, as it should be, because no renewal rolls in the first month.
  - **Relaunch.** Launched as `longjob-c34-renewal-on-arm-8b6fea024-r4` at 23:43:39Z through
    `background.launch_long_job` (`launch4q.out`). It was admitted at once, expected to take about
    200 min, and writes the same `/var/tmp/se-c34-grade-out/on_arm.json`.
  - **Grading.** The queued grading continuation was replaced by
    `read-the-c34-on-arm-r4-and-grade-p1-p4`, not before 05:00 BST. The old one's 03:30 was local
    time (02:30Z), roughly 35 min before r4 can end, and it named r3. The grading route above is
    unchanged. The predictions are unchanged, and they are still ungraded.
