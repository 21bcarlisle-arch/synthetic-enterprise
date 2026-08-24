**Severity:** LATENT · **Lane:** W2_customer_generator

# The company now learns its win rate from years a settlement cap decided, not the market

**Found by:** me, immediately after landing the win-rate learning loop (`dcba2f2e2`) and PB3's ADD
path (`395c65ba4`), by running the real campaign rather than only its tests. Filing rather than
fixing: the obvious fix is a wall violation, and the real one is an engineering decision.

## The measurement

Real campaign, `live_population()` at HEAD, book of 81:

| year | mult | homes | quotes | wins | planning_on | realised |
|---|---|---|---|---|---|---|
| 2016 | 2.17 | 400 | 30 | 5 | belief | — |
| 2018 | 1.63 | 400 | 70 | 14 | realised | 0.129 |
| 2020 | 1.19 | 400 | 112 | 22 | realised | 0.169 |
| 2021 | 0.74 | 296 | 146 | **0** | realised | 0.178 |
| 2022 | 0.44 | 178 | 178 | **0** | realised | 0.124 |
| 2024 | 1.00 | 400 | 248 | **0** | realised | 0.064 |
| 2025 | 1.11 | 400 | 196 | **0** | realised | 0.051 |

From 2021 on the campaign wins essentially nothing — and **not because of the market or the
funnel**. Every one of those years carries `SETTLEMENT-BOUND`: `SETTLEMENT_CUSTOMER_YEAR_BUDGET`
(600.0) is exhausted, which the note itself calls "THIS MACHINE'S" limit. It is an engineering
ceiling, and it is honestly declared in `notes` — that part is working.

## Why it matters now, and did not before

Before `dcba2f2e2` the cap only truncated the BOOK. Now it also feeds a company BELIEF: the
company's realised win rate decays 0.169 → 0.051 across years whose outcome the harness decided,
and `expected_quotes_per_win` inverts that into ever-larger quote budgets — 112 quotes in 2020
against 248 in 2024 — chasing a conversion that no commercial mechanism suppressed. Published
acquisition spend inherits it.

The company's *inference* is not wrong. Its books really do say "quoted 196, won 0", and a real
supplier reading that would draw the same conclusion. What is wrong is that the world handed it an
outcome produced by a machine constraint.

## Why I did not "fix" it

The tempting repair — exclude settlement-bound years from the learning — **is a wall violation**.
`SETTLEMENT_CUSTOMER_YEAR_BUDGET` is harness internals; a company that could see which of its own
losses were artefacts would be reading the simulation. It must not, and no proxy for it is
acceptable either.

So the repair is on the WORLD side and is an engineering decision:

1. **Raise or remove the settlement customer-year budget** so wins are decided by funnel and market
   rather than by machine capacity. Related to the OOM finding of the same day
   (`WORKER_FINDING_THE_PRODUCER_IS_NOT_DEAD_IT_IS_OOM_KILLED_TWELVE_TIMES_TODAY_2026-08-24.md`) —
   both are the same 15GB box showing through into published figures, and raising this without
   headroom will simply move the failure to the OOM killer. **This is the only repair that removes
   the distortion rather than relocating it.**

2. **Stop quoting once the budget has closed** — DO NOT DO THIS WITHOUT OVERTURNING A DECISION
   ALREADY TAKEN. I proposed it first and withdrew it on reading the code: the branch is
   deliberate and carries its reasoning at `net_new_acquisition.py:572` — *"THE ENGINEERING CAP
   BITES ON THE WIN, not on the quote. A quote the company paid for is spent money whatever we can
   settle, and suppressing it would silently understate acquisition cost — the one number a reader
   would use to judge whether growth was worth it."* That is right, and it means the cap cannot be
   made harmless, only moved:

   | cap bites on | acquisition cost | learned win rate |
   |---|---|---|
   | the WIN (today) | honest | contaminated |
   | the QUOTE | understated | honest |

   Before the learning loop landed only the first column existed, so there was no trade-off to
   make. There is one now, and it belongs to whoever owns the number — not to a passing repair.

`inferred`, not observed: I have NOT established which the director wants, and (1) touches a
real-machine resource decision.

## What is safe to read today

`planning_on`, `believed_win_rate` and `realised_win_rate` per year are sound as a record of what
the company believed and when. Any reading of the form "the company's conversion collapsed after
2020" is an artefact of this entry, not a result.
