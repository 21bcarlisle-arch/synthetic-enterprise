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

## Grade of P1–P4, 2026-10-20 ~05:35 BST (r4, read after its end; predictions above unchanged)

**The run.** Unit `longjob-c34-renewal-on-arm-8b6fea024-r4` ran to the end ("OUTCOME: SURVIVED —
full window completed") and wrote `on_arm.json` at 02:14 BST (about 90 min, not the expected 200) (978 household rows, 1,503 per-leg
rows). It was graded with `grade.py` as stated above. The published file is not in a fresh worktree,
so it was read from the shared tree's `docs/reports/`. The grader's output is
`/var/tmp/se-c34-grade-out/grade.out`.

| | Predicted | Read | Verdict |
|---|---|---|---|
| P1 households | 182 ± 15 | **326** (314 with electricity, 12 gas only) | **REFUTED** |
| P1 two-leg | 77 ± 15 | **175** | **REFUTED, upward** (the design refutation, "near 0", does not fire) |
| P2 advised | 0–15 of ~546 (≤ 3%) | **109 / 978 = 11.1%** | **REFUTED, and above the 10% design line** |
| P3 floor-refused | ≥ 97% | 869 / 978 = 88.9% | **REFUTED** |
| P3 unscored | 0 | 0 | held |
| P4 household ≥ leg | per household advises at least as much | 109 rows vs 56 per leg; 0 leg-advised cases lost per household | **held** |

Advised rows by effect: (£2, 0.3 pt) 83, (£3, 0.3 pt) 23, (£2, 0.1 pt) 3. Household margin median is
£29.7/month, p90 £59.6, max £448. Hazard median is 0.032, p90 0.096, max 1.0.

**P1's denominator was the wrong instrument, and that is my error in writing it.** The 182 were
`tools.decision_probe` rows, written only where `decide_renewal` priced a term *and*
`roll_lifecycle_event` rolled it (178 electricity, 4 founder gas). The caller hooks every domestic
roll on the departure leg with a prior rate. Those two populations were never the same, and I set
the band as though they were. The two-leg count is high because the caller's riding-leg join is
working. It is not near 0.

**The book check: the on-arm book is not the published book.** 18 of the 47 list-valued keys
differ, all upward and all by about 1–3%. Examples: `account_state_log` 11,920 vs 11,743;
`demand_provider_by_customer` 539 vs 530; `home_move_outs` 196 vs 193. Acquisitions (11), churned
billing accounts (233) and churn journeys (383) are equal. **I cannot yet say why.** At least three
things differ from the 03:30Z weekly run:
- the switches (O1 showed that on equals off, but only on the short window);
- untracked data on disk in the scratch worktree compared with the shared tree;
- the runner entry point (`main()` directly vs `sim_runner`).

Before it is attributed, the one-variable run is an off arm in the same scratch worktree with the
same script. A ~1.5% larger book cannot move P2 from ≤3% to 11%, so the grades stand on this book.

**What drove P2, read post hoc from the same artefact. This is not a prediction.**
- Of the 495 rows at a household margin ≤ £30/month (the B11 range §6.1 measured), **0** are advised.
- Above £30, 109 of 483 are advised. Every advised row is above £30.
- The advised rows' median hazard is 0.023, inside B11's 0.5–3%/month.
- So the prereg's stated mechanism for a P2 refutation, "the company's belief would run far hotter
  than B11's", is **not** what happened. The margin input is.
- That margin is `(unit_rate − company_fwd) × EAC / 12`.
  - `unit_rate` is the all-in tariff rate: £252.6/MWh for PROS-2022-0400 on 2023-12-21, against a
    £273.5 default-tariff rate.
  - `company_fwd` is `estimate_forward_price`, the company's wholesale forward.
  - So the "margin" still contains network, policy costs and opex. No household in the log has a
    negative margin, including through 2021–22.
- Filed as `SEAT_FINDING_C34S_RENEWAL_MARGIN_IS_THE_ALL_IN_RATE_LESS_THE_WHOLESALE_FORWARD_SO_IT_IS_NOT_A_MARGIN_2026-10-20.md`.

**Also seen:** two households carry a renewal churn belief of 1.0, so h = 1.0 (SYN-2016-270
2024-06-10, SYN-2016-388 2024-09-01). There are no renewal decisions in 2022. Both are noted and
not chased here.

**What this means for the switch:** it stays off. The 11% does not show that C34 can be switched on
safely. It is the decision rule applied to a margin that is not a margin. Whether C34's floor binds
on the company's own belief cannot be graded until the margin is the supplier's contribution.
