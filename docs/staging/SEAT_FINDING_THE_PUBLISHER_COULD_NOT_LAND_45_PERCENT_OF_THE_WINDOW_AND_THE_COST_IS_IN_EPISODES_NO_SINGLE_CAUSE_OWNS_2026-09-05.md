**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the publisher could not land for 45% of the window, and three quarters of that cost sits in episodes no single cause owns

**Found:** 2026-09-05, delivery seat, continuing the Lane 0 direction *"measure and attribute
commit_refused"*. Pre-registered before any duration was computed:
`SEAT_PREREGISTRATION_WHAT_AN_EPISODE_OF_REFUSAL_COSTS_AND_WHETHER_THE_GOVERNANCE_GATE_SHARE_IS_A_PROBLEM_2026-09-05.md`.
Predecessor: `SEAT_FINDING_THE_272_COMMIT_REFUSALS_ARE_175_CYCLES_AND_THE_RATE_IS_FOUR_TIMES_WHAT_THE_LIFETIME_COUNT_IMPLIES_2026-09-05.md`,
which established the share (175 of 442 cycles, 39.6%) and the cause split (red 40%, governance
gates 48%, unattributable 12%) and closed by naming this as the next question.

Re-derive everything below: `python3 -m tools.commit_refusal_attribution`.

---

## The answer, first

**The cause split does not predict the cost, so the episode — not the cause — is the unit worth
acting on.** That is the third branch of the decision rule, declared in advance and reached
without needing to be argued into.

Over the observable window (2026-08-13 23:21 → 2026-09-05 00:18, **529.0h**, 442 cycles):

| | |
|---|---:|
| Total bounded outage | **239.6h** |
| …as a share of the window | **45.3%** |
| Episodes (run broken by a LANDING) | 38 |
| Censored (open at the log's end) | **0** |
| Longest single outage | **68.8h** (48 cycles) — **28.7%** of all outage |
| Held by MIXED-cause episodes | **178.8h — 74.6%** |
| Median gap between attempts | 3240s (0.9h) |

**Say what 45.3% counts.** It is the share of wall clock during which the publisher's most recent
commit attempt had failed and no subsequent attempt had yet landed. It is **not** a claim that the
site was 45% stale: `origin_reconcile` and the delivery lanes land work by other routes, and this
measurement is blind to all of them. It is a statement about one daemon's ability to complete its
own cycle, and nothing wider.

## Pure-cause episodes are short. The gates individually work.

The direction's live question was whether the 48% governance-gate share is a problem or the gates
working correctly. For episodes with **one** cause, the answer is clear and it is the comfortable one:

| Cause | Episodes | Median outage | Total |
|---|---:|---:|---:|
| finding-class consolidation | 6 | 1.1h | 6.7h |
| site-lane gate | 2 | 2.3h | 4.6h |
| orphan-ratchet | 1 | 2.0h | 2.0h |
| half-hourly-dependency ratchet | 1 | 0.7h | 0.7h |
| RED TEST | 3 | 3.8h | 9.6h |
| level-promotion gate | 1 | 18.2h | 18.2h |

The median inter-attempt gap is 0.9h, so a pure governance-gate episode is **one to two attempts**:
the gate refuses, the owning lane clears the artefact it named, the next cycle lands. Against a
declared 7-day cadence that is a rounding error, and per the pre-registered rule the correct action
on it is **nothing**.

**But those episodes are 25.4% of the cost.** All the single-cause rows together are 42h of 239.6h.

## Where the cost actually is: episodes with several causes in succession

**16 of 26 multi-cycle episodes (61.5%) carry more than one cause, and they hold 74.6% of all
outage.** Every one of the 16 contains at least one governance gate; 8 of 16 also contain a red
test. The worst are not one gate refusing for a long time — they are a queue:

```
  68.8h  48cyc  RED TEST + UNATTRIBUTABLE + finding-class
  18.2h   6cyc  level-promotion gate                                   <- the one long pure episode
  14.0h  15cyc  UNNAMED + finding-class + level-promotion + orphan-ratchet + scope-evidence + site-lane
  12.5h  15cyc  RED TEST + UNATTRIBUTABLE + orphan-ratchet
  12.2h   8cyc  RED TEST + level-promotion + orphan-ratchet
```

Fifteen cycles and **five distinct gates** in one 14-hour episode. Each gate is doing exactly what
it was built to do, each refusal is correct, and the publisher still cannot get through, because it
presents the whole tree to the gates once per attempt and learns about **one** refusal per round
trip — at a median 0.9h a trip. This is why the cause split cannot price the cost: asking "which
gate refused" of a 15-cycle episode has five true answers and no useful one.

**A mixed episode is attributed to no cause here, ever.** Assigning it to its first or its
commonest would give 74.6% of the cost a label it did not earn, and would make the by-cause medians
above describe episodes that were never purely that cause.

## Predictions, scored

**P1 — the longest outage holds ≥20% of all outage. CONFIRMED, 28.7%.** The cycle-share version was
23.4%; wall clock did concentrate harder, as predicted and for the predicted reason.

**P2 — red-test episodes' median outage ≥2× governance gates'. UNANSWERABLE at this resolution, and
recorded as unanswerable rather than scored.** The nominal comparison (RED TEST 3.8h vs
finding-class 1.1h) is 3.5× and would read as confirmed, but it rests on n=3 against n=6, the
single level-promotion episode at 18.2h reverses the sign on its own, and the pure episodes it is
computed over are a quarter of the cost. A ratio of two medians at n=1..6 is not a finding. **The
prediction was answerable only if pure-cause episodes carried the cost, and P4 is exactly the
result that they do not — so P2 was malformed at the moment P4 confirmed.** Left standing beside
its result rather than revised, because a prediction that dissolves on contact with a companion
result is evidence the design preceded the answer.

**P3 — a landing-based run-breaker merges episodes, ≥10% fewer. CONFIRMED, 46 → 38, a 17.4%
reduction.** The predecessor's run definition ends a run at any cycle that was not
`commit_refused`, so a `behind_origin` or `commit_timeout` cycle mid-wedge read as a recovery. It
was not one — the publisher did not land. Both definitions are kept and reported side by side;
neither replaces the other, because the share question and the cost question want different ones.

**P4 — ≥25% of multi-cycle episodes are mixed. CONFIRMED, and by a distance: 61.5%.** This is the
result the rest of the finding turns on, and its margin over the prediction is the interesting part.

## Post-hoc, and labelled so: the causes may be flapping, not only queueing

Not pre-registered, examined after the numbers were in, and therefore a **hypothesis for the next
turn and not a result of this one.** Within a mixed episode the cause order is retained
(`cause_sequence`). Of the 16 mixed episodes, 9 have each cause in a single contiguous block —
gates queueing, each cleared once — and **7 have a cause recur after another intervened**,
including the 68.8h one (`FF?RRRRRRFRRRRRRFRR…`: a red test standing for days with finding-class
breaking repeatedly around it). Queueing and flapping call for opposite responses — reorder or
batch the gates, versus find what keeps re-breaking one — so the distinction is worth resolving.

**The alternative explanation, which I have not ruled out this turn:** the gates fire in a fixed
order and serially, so the named cause is the FIRST gate to refuse, and an apparent recurrence
could be an artefact of that ordering rather than a gate genuinely re-breaking. Settling it means
reading the gate order in the hook runner against these sequences. Not done here.

## What was NOT done, again deliberately

**No mechanism, no alarm, no threshold.** The pre-registration committed to this before the numbers
existed, and the numbers do not overturn it: the one action the cost distribution clearly argues
for — telling the publisher about more than one refusal per round trip — is a change to the gate
runner, not a control over the measurement, and it wants the queue-versus-flap question answered
first. A control written now would be keyed to today's 45.3%.

**The comparison that puts this in proportion.** The two Lane 0 directions before this one were
spent on the publisher meeting a real fork: 3 events, p90 latency 92 minutes, **0.9% of one
declared 7-day cadence**. The longest single refusal episode is **68.8h — 41% of one cadence** —
and there were 38 of them. The predecessor's conclusion that refusals are where publish cycles
actually die survives being priced, which is not something the figures it arrived with did.

## What landed

`tools/commit_refusal_attribution.py` gains `cycles()`, `episodes()` and `episode_report()`
(+ 6 controls in `tests/tools/test_commit_refusal_attribution.py`, all six mutation-proven — each
was made to fail by mutating the property it names, and restored). The controls are keyed to
properties the measurement must hold — censoring excluded and reported separately; the two run
definitions required to give *different* answers on a log built to separate them; outage strictly
greater than span for a 1-cycle episode; a mixed episode attributed to neither cause; cause order
surviving into the record; the blind span not read as a wall of landings — so they stay green as
the numbers move and go red when the measurement starts lying.
