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
