**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] A standing track for usage efficiency, starting with quick-win trials after the 16 Nov reset (2026-11-15)

**Type:** STEER, through the advisor channel. The director's words, from chat on Sun 15 Nov, 06:45 GMT:

> "I think trialing and testing some potential quick wins and also investing in better understanding of the cost (usage of max limit) is worth the investment. But bear in mind we are at 91% this week. So maybe we do it next week when we can throttle other work. I am confident that the roi on this work will be worth it. In general I wonder if we don't want a continuous track of weekly allowance usage optimisation and efficiency measures, ideas and backlog? (I'm guessing we have this to some degree )"

## What the advisor found (check it)

**What we already have (to some degree, as he guessed):**
- The Friday review's burn section (`background/weekly_rhythm.py::_burn_section`, from `tools.tick_burn_rate`) gives cost per kind of turn and per model.
- The balance review sets `feature_share` and the `accelerate:` list before the Mon 03:00 GMT reset.
- The cost-of-work estimate comes from `tools.work_cost_estimate`.
- Since 14 Nov, `tick_burn_rate --reading` shows where reading tokens go.

**What we don't have:** one place that holds efficiency ideas, trials and their measured results week to week, or any measure of what the work costs against the allowance itself.

**The 14 Nov reading measurement** (`docs/staging/records/SEAT_RESULT_READING_TOKENS_GO_TO_THE_ALWAYS_LOADED_CONTEXT_AND_SHELL_OUTPUT_AND_NO_FEW_FILES_DOMINATE_2026-11-14.md`):
- Shell output is 39.1% of context tokens.
- The fixed first-call load is 37.0%; within it, CLAUDE.md is 9.8% and the opening prompt 4.9%.
- Search and census in Opus contexts is 12.5%, but a subagent pays about 36k tokens of its own fixed context.
- Output is 12.6m against 2,162m context tokens.
- A tool result is re-read by every later call until compaction, so its cost is its size times the calls that follow it.

**A stale line in the Friday burn section.** It still says "NTFY the director what changed". NTFY is mothballed (15 Oct). Correct it to the stretch log and `for_the_director`.

## Timing and budget

- **Nothing in this note starts before the Mon 16 Nov 03:00 GMT reset.** Usage is at 91% this week.
- **In the week of 16 Nov, this track gets first claim on harness slots and throttles other work** by his words. Say in the stretch log what was throttled to pay for it.
- **After the first week, it runs as a standing item** within the normal balance, reviewed every Friday.

## The outcome wanted

1. **One standing efficiency backlog.** Make it a single file or one Friday-review section, whichever is smaller. It holds ideas, trials, and results with measured before and after. Each row records:
   - the idea and its source;
   - its expected saving and on what class of tokens;
   - the trial and its result;
   - keep, revert or drop.

   Seed it with the items below. No new gate and no new daemon. The Friday review reads it and proposes the next week's trials.
2. **Quick-win trials in the week of 16 Nov,** one variable at a time, each with a pre-registered prediction and a before and after from `tick_burn_rate`:
   - **a. Split the 39% shell output by command family:** gate runs, pytest, git, python tools, and file reads. This aims everything below.
   - **b. Quiet-by-default output on the top family.** For example, gates and tests print failures and a one-line pass, and full logs go to a file. Measure the share it removes, and check nothing a session needed to see is hidden.
   - **c. Trim the opening prompt (4.9%).** The doorbell carries the whole staging list; carry the drawn item and a pointer instead.
   - **d. Refine the delegation rule.** Delegate only large, read-once censuses, given the ~36k-token fixed cost per subagent call. Amend CLAUDE.md's routing sentence to say so.
   - **e. Trim CLAUDE.md (9.8%; 77% fixed load for the delivery seat).** Propose cuts with their measured share. Keep what the measurement shows is read and needed.
3. **Understand the cost against the allowance.** This amends the earlier mothball by his words above. Measure usage against the Max allowance to understand it, never as a reason to slow down or stop ("better to hit the limit" still holds for pacing).
   - **Find out what can be read.** Can the plan's usage percentage be read by the machine, or only by him? Do not guess. If only he can read it, the test needs four readings from him and no more.
   - **A controlled test of the meter's weighting.** Run two short sessions of known token mix: one mostly cache reads, one mostly output. Record the usage percentage before and after each. From that, estimate how the meter weighs cache reads, fresh input and output. Report the estimate with its uncertainty, and say whether it changes the ranking in item 2.
   - **Then express each kept trial's saving as usage points per week,** alongside the token shares.
4. **Fix the stale NTFY line** in `_burn_section`.

## Rules

- **Measure before and after; key the result to the property** (usage and token share), not to effort spent.
- **Never trade correctness for tokens.** A trial that hides a failure a session needed is reverted, and that counts as its result.
- **The allowance is understood, not policed.** No throttle or automatic slow-down keyed to the percentage. Pacing stays the director's, set in the Friday balance.

## Risk

Touches: gate and test output formatting, the tick prompt, CLAUDE.md wording, the Friday review.
Blast radius: every session's context. A quieter gate that hides a failure is the main risk.
Probable failure modes:
- **Quiet output hides what a session needed.** Mitigated by keeping full logs to a file and a one-line pointer to them, plus the revert rule.
- **The meter test is confounded** by other sessions running at the same time. Run it in a quiet window and state what else ran.

Proportionality: harness, reversible. Implement directly, after the reset.

— Director steer, 15 Nov 2026, his words above; the reading and drafting are the advisor's.

## Done

Seat executor, Mon 16 Nov 2026, after the 03:00 GMT reset. Nothing started before it.
- **1. The backlog** is one file, `docs/operations/EFFICIENCY_BACKLOG.md`, seeded with trials a–e, the meter
  test (E-3) and Code Mode ("revisit when it supports -p or headless sessions; re-check each Friday").
  The Friday burn section points at it. No gate, no daemon. Landed in 8fa628acd.
- **2a. Trial (a)** ran against its pre-registration: shell output is file reads (16%) and search (12%);
  gates (0.3%) and pytest (0.1%). All four predictions held. Trial (b) as drafted is dropped (ceiling
  about 0.5%) pending E-b0. Trials c, d and e are queued in the backlog, one variable at a time.
- **3. The meter is machine-readable**: headless stream-json carries `rate_limit_event.seven_day.utilization`.
  No readings are needed from the director. Nothing throttles on it. The weighting test (E-3) is queued
  for a quiet window.
- **4. The stale NTFY line** in `_burn_section` now says the stretch log and `for_the_director`.
- **Throttled to pay for it** (stretch log): other H_harness draws this week.
- The track continues as the backlog's standing rows, reviewed each Friday. The second steer's load audit
  (E-f) is done: account plugins are off for headless seats (9554dcf49f), and trial E-e is wired from 21 Nov.
