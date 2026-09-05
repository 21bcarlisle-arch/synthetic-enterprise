# What the `commit_refused` publish cycles actually died of

*Measured 2026-09-05. Re-derive with `python3 -m tools.commit_refusal_attribution`. Pre-registered
before counting in `docs/design/PREREGISTRATION_COMMIT_REFUSED_ATTRIBUTION_2026-09-05.md`.*

Subject: `docs/observability/sim-runner-log.md`, retained span 2026-06-19 → 2026-09-05.

---

## The number the direction carried does not exist

The Lane 0 direction opened with *"commit_refused 272, behind_origin 30, commit_timeout 19,
push_did_not_reach_origin 13"*. None of those four is a count of cycles. Each is the sum of two
different line shapes about the same cycle:

| outcome | `Commit/push failed (X)` | `DID NOT LAND (outcome: X)` | sum | cycles |
|---|---|---|---|---|
| commit_refused | 175 | 97 | **272** | **175** |
| behind_origin | 17 | 17 | 34 | 17 |
| commit_timeout | 14 | 5 | 19 | 14 |
| push_did_not_reach_origin | 7 | 6 | 13 | 7 |

The second shape was added on **2026-08-19**, so it exists for some cycles and not others. Summing
the two double-counts every cycle after that date and single-counts every cycle before it. `272`
is 175 cycles plus the 97 of them that happened late enough to get a second line.

The ratios survive better than the absolute figures: refusals really are ~10x the fork branch two
directions were spent on. The *conclusion* of the direction stands; its arithmetic does not.

## The rate, and why the lifetime figure is not one

175 refusals over 1,903 lifetime publish attempts is **9.2%**, and that is the wrong division.

Named outcomes did not exist before **2026-08-13 22:23**. Every earlier failure — refused and
empty-index alike — logged the same line, `Commit/push failed (possibly nothing changed)`, 177
times. So 1,461 of those 1,903 attempts (77%) are in a span where a refusal was **unnameable**,
not absent. Every one of the 175 refusals falls after 2026-08-13, which reads as "the problem
started then" and is really "the instrument was installed then".

Over the window where the question is answerable at all:

> **175 of 442 publish cycles were refused: 39.6%.**

Four in ten. That is **4.3× the lifetime figure**, and the lifetime figure is the one the direction
implied.

## What refused them

| refusing gate | cycles | share |
|---|---|---|
| a red test | 70 | 40.0% |
| finding-class consolidation | 31 | 17.7% |
| site-lane gate | 20 | 11.4% |
| orphan-ratchet | 16 | 9.1% |
| level-promotion gate | 13 | 7.4% |
| scope-evidence ratchet | 2 | 1.1% |
| file-scope-generated-paths gate | 1 | 0.6% |
| half-hourly-dependency ratchet | 1 | 0.6% |
| *unattributable — hook block not retained* | 14 | 8.0% |
| *unattributable — no banner, no red named* | 7 | 4.0% |

**Named red 40% · non-test gate 48% · unattributable 12%.** The 12% is reported as its own bucket
and never folded onto either side.

The shape worth acting on: **a red test is a minority cause.** The largest single class is the
whole-tree governance gates — finding-class, site-lane, orphan-ratchet, level-promotion — which
together refuse 46% of cycles, more than every red test combined. These gates judge tree state that
the publisher did not create and cannot fix: the publish daemon commits regenerated site data, and
is refused because some *other* lane left a finding unclassified or a module unwired.

## The rate is not a per-cycle hazard

Refusals arrive in **46 contiguous runs**, not as independent events. The longest is **41
consecutive refused cycles** — 23.4% of every refusal in the span, one unfixed cause. Runs of five
or more hold **61%** of all refusals. The longest same-cause streak is 26 consecutive red-test
refusals.

So "39.6% of cycles are refused" is a true share and a misleading hazard. The publisher is not
failing four times in ten; it is failing totally for hours at a time and then working. The unit
that matters is the **episode**, not the cycle, and the cost of one is however long a human-scale
fix takes — the 41-run is a single cause that nothing cleared for the length of 41 publish cycles.

## Predictions, scored

- **P1 — "more than half named zero red tests": REFUTED as stated.** Non-test gates are the
  plurality at 48%, not a majority. Only if the 12% unattributable is discarded does it reach
  55% — and discarding it to reach a prediction's threshold is the move that makes a
  pre-registration worthless, so it is not made. Called at >50%; measured 48%.
- **P2 — "the largest contiguous run is ≥15% of refusals": CONFIRMED.** 41 of 175 = 23.4%.
- **P3 — "the recent rate exceeds the lifetime share": CONFIRMED**, and for a reason the
  prediction had wrong. I reasoned the gates were added over the span so early cycles could not
  be refused by them. The actual reason is that early cycles could not be *recorded* as refused
  by anything. The prediction was right about the direction and wrong about the mechanism, which
  makes its confirmation worth much less than it looks.

## What this does not establish

- **Whether the refusals are correct.** Every one may be a gate doing its job. This measures what
  refused, not whether it should have. A 48% non-test share is a finding about *where the cost
  falls*, not evidence any gate is wrong.
- **The cost of a refusal.** The episode is the unit, and episode duration is not measured here.
- **The 12%.** Fourteen refusals lost their hook block to log retention and seven named nothing
  the publisher's own banner table knows. The second seven are the more interesting: they are
  either a gate with no banner or a banner that drifted from the table.

## What follows

Nothing is built on this yet, on purpose — a control written before the distribution was known
would be keyed to today's answer. The next question is **episode duration by cause**, because it
converts this share into a cost and decides whether the 46% governance-gate share is a problem or
just the gates working. That question needs the episode boundaries, which are in the same log.
