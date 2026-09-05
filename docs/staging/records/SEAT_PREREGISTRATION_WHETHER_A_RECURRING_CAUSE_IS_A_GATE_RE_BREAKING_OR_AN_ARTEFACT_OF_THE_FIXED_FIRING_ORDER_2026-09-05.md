**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# PRE-REGISTRATION: is a recurring cause a gate genuinely re-breaking, or an artefact of the fixed firing order?

**Filed:** 2026-09-05, delivery seat, continuing the Lane 0 direction *"measure and attribute
commit_refused"*. **Written before any sequence was classified.** The predecessor finding
(`SEAT_FINDING_THE_PUBLISHER_COULD_NOT_LAND_45_PERCENT_OF_THE_WINDOW_AND_THE_COST_IS_IN_EPISODES_NO_SINGLE_CAUSE_OWNS_2026-09-05.md`)
closed by naming this and refusing to answer it:

> *"Of the 16 mixed episodes, 9 have each cause in a single contiguous block — gates queueing, each
> cleared once — and 7 have a cause recur after another intervened. […] **The alternative
> explanation, which I have not ruled out this turn:** the gates fire in a fixed order and serially,
> so the named cause is the FIRST gate to refuse, and an apparent recurrence could be an artefact of
> that ordering rather than a gate genuinely re-breaking. Settling it means reading the gate order in
> the hook runner against these sequences. Not done here."*

What is already established and is NOT re-litigated: 175 refused cycles of 442 (39.6%); 239.6h
bounded outage, 45.3% of the window; 16 of 26 multi-cycle episodes mixed, holding 74.6% of outage;
the 9-versus-7 split above, which is **post-hoc and carries no authority here.**

---

## The definitional work, done BEFORE the classification

### What the firing order actually is, read from the enforcement and not from a comment

`background/process_run_complete.py` carries a comment asserting its classifier table is "NOW
ACTUALLY THE CHAIN'S" order. That is a paraphrase, and CLAUDE.md says read the enforcement. The
order below is read from `tools/git-hooks/pre-commit` (each gate `|| exit 1`, serial) and, for the
gates that share one emitter, from the body of `tools/pre_commit_test_gate.py::main`:

| rank | gate | read from |
|---|---|---|
| 1 | status-honesty | pre-commit L12 |
| 2.1 | canon-size | test_gate main, 1st |
| 2.2 | **finding-class consolidation** | test_gate main, 2nd |
| 2.3 | landed-manifest | test_gate main, 3rd |
| 2.4 | **finding-severity** | test_gate main, 4th |
| 2.5–2.8 | record-landing-claim, wall-crossing, wall-channel-census, symbol-landing | test_gate main |
| 2.9 | **RED TEST** (pytest) | test_gate main, **LAST** (L1519) |
| 3 | level-promotion | pre-commit L33 |
| 4 | site-lane | L42 |
| 5 | moap-coherence | L53 |
| 6 | ruling-archive-question | L62 |
| 7 | consolidation-rhythm | L75 |
| 8 | size-ratchet | L94 |
| 9 | orphan-ratchet | L111 |
| 10 | company-network-isolation | L127 |
| 11 | file-scope-generated-paths | L150 |
| 12 | annual-report-import | L171 |
| 13 | half-hourly-dependency | L193 |
| 14 | running-total-order | L223 |
| 15 | scope-evidence | L251 |
| 16 | write-time | commit-msg, after all of pre-commit |

**The one fact that matters, and it is structural, not statistical:** the chain is serial and stops
at the first refusal. So a cycle that names gate *G* at rank *r* is a **positive observation that
every gate at rank < r PASSED in that cycle.** That is the only thing the log tells us about the
gates it did not name, and it is enough.

### The discriminator this licenses

For two refused cycles in one episode, earlier cycle naming rank `r_i`, later naming rank `r_j`:

- **`r_j > r_i` (forward step).** The gate at `r_i` cleared; the gate at `r_j` may have been red the
  whole time and merely unreachable. **UNINFORMATIVE** — this is exactly what a genuine queue AND a
  simultaneously-red set both produce.
- **`r_j = r_i` (same rank).** Persistence, or two refusal paths of one gate. **UNINFORMATIVE.**
- **`r_j < r_i` (backward step).** At cycle *i* the chain reached `r_i`, so the gate at `r_j`
  **passed** then; at cycle *j* it **refused**. That gate went passing → refusing. **ESTABLISHED
  re-arrival**, and immune to the ordering artefact by construction.

**This reframes the question rather than answering it as asked.** *Queue* is not falsifiable from
this log — a later gate's state is unobservable while an earlier one refuses, so "each cause cleared
once, in turn" and "all of them red from the start, revealed in rank order" have identical
signatures. Only the backward step is establishable. So the honest output is not a 9-versus-7 split
repaired; it is: **X episodes carry established re-arrival, the remainder are order-consistent and
cannot be told apart from simultaneous redness.** I am recording that this is what I expect to have
to report, before I know the numbers, so it cannot be read as a rationalisation of a null result.

### Rules fixed before looking

1. **Unattributable causes (`UNNAMED`, `UNATTRIBUTABLE`) have no rank and are SKIPPED**, never
   imputed. The step comparison is over the named subsequence only. An unattributable cycle between
   two named ones does not break the inference: the passed-below-rank observation is per-cycle.
2. **A backward step is detected against the RUNNING MAXIMUM rank**, not against the immediately
   preceding cause. Any cause whose rank is below the highest rank yet reached in that episode is a
   re-arrival, whether or not something else intervened adjacently.
3. **Ties are not backward steps.** Fail-closed: the ambiguous case is counted as uninformative, the
   direction that makes the result weaker.
4. **Outage is attributed to a class, never split within an episode.** Same discipline as the mixed
   bucket: an episode with one backward step is wholly "established re-arrival", not partly.
5. **Censored episodes are excluded from cost and reported separately**, as before.

---

## Predictions, filed before running

**P1 — of the 9 episodes the predecessor called contiguous/queueing, ≥2 contain a backward step.**
Tests whether the post-hoc split *understated* re-arrivals. A single cause pair in the wrong rank
order (B at rank 9 then A at rank 3) is a genuine re-arrival that the contiguous-block test scores
as a queue.

**P2 — ≥12 of the 16 mixed episodes contain at least one established backward step.** The strong
form. If this fails but P1 holds, the answer is "some flap, mostly unresolvable".

**P3 — order-consistent (monotone) episodes hold <50% of the multi-cause outage.** The cost version:
whether the establishable half is where the money is. This is the one that decides whether the gate
runner change the predecessor deferred is justified.

**P4 — the 68.8h episode (28.7% of all outage) contains a backward step.** Its published sequence is
`FF?RRRRRRFRRRRRRFRR…` — finding-class (2.2) and RED TEST (2.9) share an emitter, so a naive
same-gate reading would call this untestable; the internal order puts pytest LAST, which makes
`R → F` a backward step. **Flagged as WEAKLY INDEPENDENT**: I derived the expectation from a
sequence already printed in the predecessor, so P4 is a check on my rank assignment, not evidence.

## The control the analytic claim earns

Any recurrence (a cause at positions *i* and *k* with a different cause at *j* between them) must
imply at least one backward step — whichever way the ranks fall, one of `i→j` or `j→k` descends.
So **all 7 of the predecessor's recurrence episodes must show a backward step.** If any does not,
my rank table is wrong, not the data. This is a check on the instrument and is not a prediction.

## What I will NOT do

**No mechanism, again.** Two predecessors deferred the gate-runner change; this turn is the last
input it was waiting on, and building it in the same turn that establishes its justification is how
a control gets keyed to today's answer. If P3 confirms, the finding states what the change is and
the next turn builds it against a stated cost.
