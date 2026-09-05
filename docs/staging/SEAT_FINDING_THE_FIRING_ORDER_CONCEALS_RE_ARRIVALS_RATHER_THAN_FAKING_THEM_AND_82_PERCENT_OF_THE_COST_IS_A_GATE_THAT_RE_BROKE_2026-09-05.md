**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# The fixed firing order CONCEALS re-arrivals rather than faking them, and 82% of the mixed-episode cost is a gate that passed and then refused

**Filed:** 2026-09-05, delivery seat. Third turn of the Lane 0 direction *"measure and attribute
commit_refused"*. Pre-registered in
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_A_RECURRING_CAUSE_IS_A_GATE_RE_BREAKING_OR_AN_ARTEFACT_OF_THE_FIXED_FIRING_ORDER_2026-09-05.md`,
**written before any sequence was classified.**

The predecessor closed by refusing to answer this, and naming exactly what would answer it:

> *"the gates fire in a fixed order and serially, so the named cause is the FIRST gate to refuse,
> and an apparent recurrence could be an artefact of that ordering rather than a gate genuinely
> re-breaking. Settling it means reading the gate order in the hook runner against these sequences.
> Not done here."*

Done here. **The worry was the right worry and it points the wrong way.**

## The answer

| | episodes | outage | share of mixed outage |
|---|---|---|---|
| **ESTABLISHED re-arrival** — a gate demonstrably passed, then refused | **11 of 16** | **147.4h** | **82.4%** |
| ORDER-CONSISTENT — cannot be told apart from simultaneous redness | 5 of 16 | 31.4h | 17.6% |

Of the 11 established, **4 are invisible to the predecessor's contiguous-block test** — its 9-vs-7
split was not an over-count inflated by the firing order, it was an **under-count**, and the
direction of that error is the finding.

## Why the ordering artefact cannot manufacture a re-arrival, only hide one

The hook is serial and every gate is `|| exit 1`, so it **stops at the first refusal**. That single
structural fact is the whole instrument:

> A cycle that names gate *G* at rank *r* is a **positive observation that every gate at rank < r
> PASSED in that cycle.**

So for two refused cycles in one episode:

- **Forward step** (later cause ranks higher). The gate below cleared; the gate above may have been
  red the whole time and merely unreachable. **Establishes nothing** — a genuine queue and a set of
  gates all red from the start produce identical logs.
- **Step back** (later cause ranks *lower*). When the deeper gate was named, the shallower one
  **passed**. Now it refuses. That gate went passing → refusing. **Established, and immune to the
  firing order by construction.**

The predecessor feared the order would invent recurrences. It cannot: a backward step requires the
chain to have reached *past* that gate first, which is a strictly harder thing to observe. The
order **suppresses** evidence of re-arrival. Everything hidden behind a refusing gate is hidden.

**So `queue` is not falsifiable from this log and is never reported as found.** The complement
bucket is named ORDER-CONSISTENT — a statement about what cannot be distinguished, not a finding
that the gates queued. This is a reframe of the question as asked, and it was pre-registered as the
expected shape of the answer before the numbers existed, precisely so it could not be read as a
rationalisation of a null result.

## The rank table is derived from the enforcement, not copied from it

`background/process_run_complete.py` carries a comment asserting its classifier table is "NOW
ACTUALLY THE CHAIN'S" order. A comment cannot be checked. `gate_ranks()` derives the order at call
time from `tools/git-hooks/pre-commit` itself, and — for the three causes that share one emitter —
from the position of each banner inside `tools/pre_commit_test_gate.py`. The comment turned out to
be **correct**; it is now also *checked*, and a reordered hook goes red here.

That sub-rank is not a detail. `finding-class`, `finding-severity` and `RED TEST` are all printed by
the test gate, which the hook invokes **once**. Ranking them equal would have made the largest
episode in the log — 68.8h, 28.7% of all outage, alternating finding-class and RED TEST — untestable.
`main()` runs the consolidation check 2nd and invokes pytest **last**, so a named red test is a
positive observation that finding-class passed. The 68.8h episode is established on exactly that.

## Two defects in the instrument, both caught by printing the table before trusting it

**A `.find()` that fails ranks the gate FIRST.** Gate banners are written in source as adjacent
string literals split across lines, so `finding-severity`'s runtime needle never occurs contiguously
in the file that prints it. `.find()` returned -1, and the obvious fallback — treat -1 as offset 0 —
put it at the strongest position in its emitter. Every later cause would then have looked like a
step back to it: **an established re-arrival manufactured out of a failed lookup**, in the one
direction this analysis cannot survive. Fallback is now `None` and the cause leaves the analysis.

**Then the fail-closed fix dropped three of the biggest gates.** A minimum-length floor applied to
the *needle* rather than to the *shrinking* silently discarded `[level-gate] ❌`, `[site-lane] ❌` and
`[scope-evidence] ❌` — short, entirely specific, and three of the commonest causes in the log. The
table printed clean because its biggest gates had left it. Both defects have a control named after
them; neither was found by thinking, both by printing the table at real inputs.

## Predictions, scored beside the predictions and not revised

**P1 — ≥2 of the 9 contiguous-block episodes contain a backward step. CONFIRMED: 4.** The post-hoc
split understated re-arrivals. A single pair in the wrong rank order (`site-lane` → `file-scope` →
`level-promotion`, 9.2h) is a genuine re-arrival that a recurrence test scores as a queue.

**P2 — ≥12 of 16 mixed episodes carry a backward step. REFUTED: 11.** Missed by one. The weaker
form of the claim survives (a clear majority, and 82.4% of the cost), but the strong form is refuted
and is recorded as refuted.

**P3 — order-consistent episodes hold <50% of mixed outage. CONFIRMED: 17.6%.** The establishable
half is where the cost is. This is the prediction that carries the action below.

**P4 — the 68.8h episode contains a backward step. CONFIRMED**, and flagged **WEAKLY INDEPENDENT**
in the pre-registration before it was run: the expectation was derived from a sequence already
printed in the predecessor, so it is a check on the rank assignment, not evidence.

**The instrument control HELD.** The pre-registration recorded an analytic claim — any recurrence
must imply a backward step, whichever way the ranks fall — and therefore that all 7 of the
predecessor's recurrence episodes must show one. All 7 do; the `recurrence ∧ ¬established` cell is
**empty**. Had it not been, the rank table would have been wrong, not the data.

## What this does to the change the last two turns deferred

The predecessor deferred one action: **tell the publisher about more than one refusal per round
trip**, justified by "it presents the whole tree and learns about ONE refusal per trip, at 0.9h a
trip". That justification assumed the causes were a **static set** being revealed one at a time.
They are not. In 11 of 16 mixed episodes, holding 82.4% of the cost, **a gate that had passed
refused again while the episode was open** — the subject is changing underneath the publisher.

So the change is still worth making and **it is no longer sufficient**, and the reason is now
priced rather than assumed. Batching every refusal into one round trip collapses the forward-step
portion — the 17.6% — and cannot touch the 82.4%, because a gate that was green when the batch was
taken can be red on the next attempt regardless of how much the batch told you.

**What re-breaks them is NOT established here and I am not going to guess it.** The obvious
candidate is the one CLAUDE.md already states as a standing condition — several sessions and daemons
writing this one tree concurrently, so the tree mutates mid-episode — and it is consistent with
every sequence above. It is not evidence. This instrument cannot distinguish "another lane landed
work that broke a gate" from "a fix that did not stick", because the log records which gate refused
and never what changed between attempts. **That is the next question, and it needs a different
instrument: the tree state between consecutive refused cycles, not the refusal.**

## What was NOT done, for the third turn running

**No mechanism, no alarm, no threshold.** Two predecessors deferred the gate-runner change pending
this answer; this turn establishes that the change was scoped against the wrong half of the cost, so
building it now would have shipped a fix for 17.6% of the problem with a justification that reads
like it addressed all of it. A control over "re-arrival rate" would also be keyed to today's 82.4%.
The next turn's subject is what changes between two refused cycles.

## What landed

`tools/commit_refusal_attribution.py` gains `gate_ranks()`, `_needle_pos()`, `_hook_order()` and
`ordering_report()`, plus the ordering section of the CLI. Six new controls in
`tests/tools/test_commit_refusal_attribution.py`, all mutation-proven: the fail-open lookup, the
shrink-floor over-correction, the derived order against the hook, pytest ranking last within its
emitter, the backward/forward partition asserted both ways in one log, and ties scored as
persistence.

**One mutation survived and was run down rather than left.** Replacing the running peak with
"compare to the previous cause" passed all 24 controls. It is a genuine **equivalence for the
`established` verdict** — if any rank sits below the running peak, some adjacent pair must descend,
or the sequence would be non-decreasing throughout — and **not** an equivalence for the step count,
which the docstring claims. The 25th control pins that claim: `orphan-ratchet(108) →
level-promotion(32) → site-lane(41)` is two gates that each passed and then refused, and the
previous-cause reading sees one.
