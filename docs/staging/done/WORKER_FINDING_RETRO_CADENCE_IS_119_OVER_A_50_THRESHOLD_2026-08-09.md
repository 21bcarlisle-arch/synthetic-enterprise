# [WORKER-FINDING] The retro cadence is 2.4x past its own threshold, and every phase-close has been stepping over the check that says so

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-09, at the `KNIFE2_customer_straddle` phase-close (checklist item 6 fired).
**Disposition:** QUEUED. Not absorbed into KNIFE2 — a 119-promotion backlog is not one atom's to pay.
**Rank:** propose top-of-backlog. It is cheap to close and it gates a checklist step every other close runs.

## Observed, with evidence

```
$ python3 -c "from background.shared_primitive_census import standing_review_due; print(standing_review_due())"
Retro cadence STALE: 119 maturity-map promotions since last retro
(2026-08-03-a-diagnostic-pinned-as-a-target-wedged-publishing-four-days.md), threshold 50
```

**The mechanism is not the problem.** `A1_learn_loop_chair` is L3/idle,
`background/retro_cadence_check.py` is R15-guarded against fail-open, and it is reporting the truth
loudly and correctly. What is missing is the *performance* of the duty: phase-close item 6 says
"run the `incident-retro` skill before closing", and 119 promotions have closed without one. The
check fires, the closer reads it, the close proceeds. That is the decay shape CLAUDE.md's
MAKE IT STICK rule names exactly — *a rule lives as CLAUDE.md prose AND as enforced code, or not at
all* — and here the code exists but only **reports**; nothing refuses.

The related item 6d row is worse and says so itself:

```
standing_review_never_recorded: no last_standing_review stamp -- the 5.3 standing structural
review has never been recorded through record_standing_review() (unrun is not evidence of no drift)
```

**Never**, not stale. So the shared-primitive standing review has run zero times since it was built.

## Why this close did not do it

Two reasons, both stated rather than implied:

1. **Scope.** The backlog is 119 promotions deep and was already ~2.4x over threshold when this tick
   started. Absorbing it into a wall-refactor atom would be the "consumed, not absorbed" move R17
   names, and would hide a 6-day-old debt inside an unrelated commit.
2. **A hard blocker on one half.** Checklist item 6d(ii) requires handing the census to the
   `phase-close-evaluator` agent, and this session is operating under an explicit instruction not to
   invoke subagents. That half cannot be done from here by anyone, so it is named rather than
   silently skipped. Item 6d(iv)'s ledger stamp is refused unless (ii)'s verdict exists, so the
   whole 6d chain is blocked on it — a tick that CAN spawn agents must run it.

## What closing it needs

- One `incident-retro` pass. There is no shortage of material: 2026-08-09 alone produced ~20
  `WORKER_FINDING_*` docs, and at least two of them are the same class twice
  (`..._A_LANDED_PASS_HAD_HALF_ITS_CODE_UNCOMMITTED_...` is the second instance in one day of work
  existing in a working tree only, after commit `83a55b750` fixed the first half of it).
- The 6d standing review, from a tick with subagent capability.
- **A mechanism question worth answering in that retro, not here:** should the cadence check be
  allowed to REFUSE, or is reporting the right power for it? Both answers are defensible — a
  refusing retro gate can wedge publishing, which this repo has already been bitten by — but 119
  is evidence that reporting alone does not hold, and "convert policy to mechanism, or accept it
  will evaporate" says pick one deliberately rather than by default.
