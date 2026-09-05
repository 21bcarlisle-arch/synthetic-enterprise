# Pre-registration — are the gates queueing, flapping, or masking each other?

*Written 2026-09-05, BEFORE any recurrence was classified. Predictions below are not revised; where
the measurement refutes one, the refutation is recorded beside it and this file stays as written.*

Subject: `docs/observability/sim-runner-log.md`, observable window only (opens at the first named
commit outcome). Instrument: `tools/commit_refusal_attribution.py`.

Predecessors, both landed:
`docs/staging/SEAT_FINDING_THE_272_COMMIT_REFUSALS_ARE_175_CYCLES_AND_THE_RATE_IS_FOUR_TIMES_WHAT_THE_LIFETIME_COUNT_IMPLIES_2026-09-05.md`
established the share and the cause split;
`docs/staging/SEAT_FINDING_THE_PUBLISHER_COULD_NOT_LAND_45_PERCENT_OF_THE_WINDOW_AND_THE_COST_IS_IN_EPISODES_NO_SINGLE_CAUSE_OWNS_2026-09-05.md`
priced it and closed by naming this question, together with the alternative explanation it had not
ruled out.

---

## The question, and why the previous turn could not answer it

74.6% of all publisher outage sits in episodes carrying more than one cause. Of the 16 such
episodes, 9 have each cause in one contiguous block and **7 have a cause recur after another
intervened**. Queueing and flapping call for opposite responses — batch the gate reporting, versus
find what keeps re-breaking one gate — so the distinction has to be settled before either is built.

The previous turn recorded the alternative it could not rule out, verbatim: *"the gates fire in a
fixed order and serially, so the named cause is the FIRST gate to refuse, and an apparent
recurrence could be an artefact of that ordering rather than a gate genuinely re-breaking."*

## The mechanism, read before predicting (this is not a measurement)

`core.hooksPath = tools/git-hooks`, so `tools/git-hooks/pre-commit` is the live gate runner. Every
gate in it is invoked as `python3 … || exit 1`: **serial, fixed order, and it stops at the first
refusal.** `tools/git-hooks/commit-msg` runs afterwards and holds one further gate. Therefore:

> **A named cause proves every EARLIER gate passed on that cycle, and says nothing whatever about
> the later ones.** The by-gate distribution the predecessor published is a distribution of *first
> failing gate*, not of *failing gate*.

That single fact makes the question decidable by proof rather than by inference, in one direction
each way. For a cause `c` recurring at cycles `t1 < t3` with cause `m` named at some `t2` between:

- **`order(m) > order(c)` → PROVEN FLAP.** For `m` to be reached, every earlier gate passed at
  `t2`, and `c` is one of them. So `c` was genuinely cleared and re-broke.
- **`order(m) < order(c)` → MASKABLE.** `m` refusing first tells us nothing about `c`, which may
  have stood broken and invisible throughout. No evidence of a flap.
- **`order(m)` unknown → UNDECIDABLE**, and reported as its own bucket, never folded onto either
  side.

The same fact decides the queue direction, on consecutive distinct causes `c_j → c_{j+1}`:

- **`order(c_{j+1}) > order(c_j)` → QUEUE STEP.** Consistent with `c_j` being cleared and the next
  gate revealed.
- **`order(c_{j+1}) < order(c_j)` → PROVEN NEW BREAKAGE.** `c_{j+1}` was *passing* at cycle `j`
  (it is earlier, so it was reached and cleared) and failing at `j+1`. Something broke it during
  the episode.

## Rules fixed before counting

1. **Gate order is derived mechanically, never typed.** From the invocation order in
   `tools/git-hooks/pre-commit` then `commit-msg`, joined to the publisher's own
   `_REFUSING_GATE_BANNERS` table by the emitter path it already carries. Two causes sharing one
   emitter are sub-ordered by where their banner appears in that emitter's source. A hand-written
   order list would drift from the hook and the drift would be silent.
2. **Fail closed.** A banner whose emitter appears in neither hook file has UNKNOWN order. Every
   comparison involving an unknown is UNDECIDABLE. `UNATTRIBUTABLE` and `UNNAMED` are unknown by
   construction.
3. **`RED TEST` is a bucket, not a gate identity.** A proven flap of `RED TEST` may be one test
   re-breaking or two different tests breaking in turn. Where the hook block retains `FAILED`/
   `ERROR` node ids, the recurrence is additionally reported as SAME-TEST or DIFFERENT-TEST; where
   it does not, that refinement is reported as unavailable and not guessed.
4. **No mechanism, no alarm, no threshold this turn either.** Same reason as both predecessors: the
   answer decides *which* mechanism is worth building, and one written now would be keyed to
   today's answer.

## Predictions

**P1 — At least one PROVEN FLAP exists, i.e. flapping is real and not wholly an ordering artefact.**
Reasoning: the 68.8h episode's sequence is `FF?RRRRRRFRRRRRRFRR` with F = finding-class and
R = RED TEST. finding-class is *earlier* than the pytest run inside the same emitter, so every R
recurrence there is maskable — but F recurs around R, and R being reached proves F passed. F must
have re-broken.

**P2 — The majority of decidable recurrence pairs are PROVEN FLAPS rather than maskable.**
Reasoning, and I hold it weakly: `RED TEST` sits at position 1c, ahead of all thirteen governance
gates, so a red test recurring around *any* governance gate is proven cleared-and-re-broken. Only a
recurrence around finding-class or finding-severity is maskable. Given the predecessor's split
(finding-class 31, site-lane 20, orphan-ratchet 16, level-promotion 13 — three of the four later
than the test run), most intervening causes should be later ones. **This is the prediction most
likely to be wrong, and if it is refuted the masking explanation carries the 68.8h episode.**

**P3 — PROVEN NEW BREAKAGE occurs in at least a quarter of mixed episodes.** Reasoning: several
lanes commit into this tree continuously, and the median inter-attempt gap is 0.9h, which is long
enough for a lane to break an early gate that was passing. If this confirms, the mixed episodes are
not a queue the publisher must grind through — they are new breakage arriving faster than it clears
round trips, and batching the gate reporting would not have shortened them.

**P4 — The by-gate distribution is order-biased: gates late in the hook order are under-counted.**
Stated as a claim about the instrument, not the world, and it is *proven a priori* by the early
exit — what the measurement adds is the magnitude. Recorded here so the predecessor's 48%
governance share is read as the lower bound it is, and so I cannot later present the proof as a
discovery.

## The decision rule, declared in advance

- If **queueing** dominates (few proven flaps, few new breakages, mostly increasing order): the
  action is to tell the publisher about more than one refusal per round trip.
- If **flapping** dominates: the action is to find what re-breaks the specific gate, and batching
  would not have helped.
- If **new breakage** dominates: the episode is other lanes' traffic, not the publisher's
  ignorance, and *neither* of the above is worth building — the publisher's round-trip cost is
  incidental.
- If the classes are mixed with no majority: report that, build nothing, and say what would
  separate them.
