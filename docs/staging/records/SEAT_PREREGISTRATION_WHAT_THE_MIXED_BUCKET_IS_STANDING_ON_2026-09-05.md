**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# PRE-REGISTRATION: what is the MIXED bucket standing ON?

**Filed:** 2026-09-05, delivery seat, opening the sixth turn on the Lane 0 direction *"attack the
standing red, not the cadence"*. **Written before the interval decomposition below was computed
once.** The premise was re-measured first and holds: against the shared tree's live runner log,
`MIXED (more than one cause in one episode)` is **178.8h of 239.6h (74.6%)** of bounded outage over
16 episodes, and the single longest outage in the log (68.8h, 48 cycles, 28.7% of everything) wears
that label.

## The problem with the largest number we publish

`MIXED` is not a cause. It is `causes[0] if len(causes) == 1 else MIXED` — a refusal to attribute,
correctly chosen so that an episode with two causes is never assigned to whichever one makes the
split cleaner. That discipline is right and this document does not touch it.

But the consequence is that **74.6% of the cost carries a label that is by construction not an
answer**, and the decomposition that landed as 988270c2e — 82.9% of multi-cycle outage is redness
*standing* — therefore names no gate. We know the wide bracket is the redness. We do not know whose
redness. That is the same shape this direction has already paid for twice: a bucket nobody defined,
differenced, published, and treated as a driver.

## The question

> Inside a mixed episode, which named gate was holding the publish, and for how long?

## The unit, stated before the split rather than inferred from it

**The episode is the wrong unit and that is the whole reason `MIXED` exists.** An episode has one
`cause` field and several causes, so the field must either lie or abstain, and it correctly
abstains. The unit that does not have this problem is the **interval between two consecutive
attempts**, because each interval has exactly one observation at each end.

For a bounded episode with member cycles `m_0 … m_{n-1}` and recovery `r`:

    outage = (r − m_0) = Σ_{i<n-1} (m_{i+1} − m_i)  +  (r − m_{n-1})

This is an **exact partition of the episode's outage**, not an apportionment — every second of the
178.8h lands in exactly one interval, and the last term is the trailing gap already measured at
17.1%. Nothing is estimated, weighted, or shared out.

## The classes, and precisely what each one licenses

The chain is serial and stops at the first refusal, so a cycle naming a gate at rank `r` is a
positive observation that every gate *below* `r` passed in that cycle, and says **nothing** about
the gates above it. Every class below is derived from that one inference and no other. Let `A` be
the cause observed at the interval's start and `B` the cause at its end.

- **BRACKETED — `A == B`.** The same named gate refused at both ends, with no observation in
  between (the ends are adjacent cycles by construction). The log contains **no evidence the gate
  cleared**, so this is the strongest per-gate attribution available. It is *not* proof the gate
  stood throughout: it could have cleared and re-broken unobserved. It is named BRACKETED and not
  "held" for exactly that reason.
- **CLEARED-WITHIN — `rank(B) > rank(A)`.** At the far end the chain passed `A` and stopped higher,
  so **`A` demonstrably cleared at some instant inside this interval**. The interval is an UPPER
  bound on how much longer `A` held, and never an estimate of it.
- **MASKED — `rank(B) < rank(A)`.** The chain stopped below `A`, so `A`'s state at the far end is
  unobservable. What *is* established is the other direction: `B` passed at the start and refused
  at the end, so **`B` re-broke inside this interval**. Attributable to neither as duration.
- **UNRANKABLE.** Either end is a non-refusal cycle (a `behind_origin` attempt refuses nothing) or
  names an unranked cause (`UNATTRIBUTABLE`, `UNNAMED`). Ignorance, reported as ignorance.
- **TRAILING.** The final interval, `m_{n-1} → r`. Everything cleared somewhere inside it and the
  log cannot say when. Unattributable **by construction**, exactly as the single-cycle 100% is.

**BRACKETED and CLEARED-WITHIN are the only two classes that attribute time to a named gate**, and
they attribute it in opposite directions — one is a floor on a gate that stayed red, the other a
ceiling on a gate that went green. They must never be summed into one "attributed" figure without
saying so, and the headline table reports them in separate columns.

## The three predictions

Each is falsifiable against this log and stated so that both answers are possible.

1. **A named gate can be put on the majority of MIXED outage.** BRACKETED + CLEARED-WITHIN together
   exceed 50% of the 178.8h. **Refuted if the unattributable residue (MASKED + UNRANKABLE +
   TRAILING) is ≥ 50%.** *Basis:* 77.8% of same-gate pairs are the identical complaint, and mixed
   episodes are long and many-cycled (median 8.1h), so most intervals should have a refusal naming
   a ranked gate at both ends. *If this is refuted the direction is wrong and the honest finding is
   that the log cannot name the driver — which is a result, and it goes on the page as one.*

2. **The single largest named gate inside MIXED is RED TEST.** By BRACKETED hours. **Refuted if any
   other gate takes the top row.** *Basis:* RED TEST is named on 70 of 174 refused cycles and holds
   59 of 107 same-gate pairs, both the most of any gate. *This can easily be false:* the
   level-promotion gate carries an 18.2h median as a solo cause and appears inside the long mixed
   episodes, so a few of its intervals could outweigh many short RED TEST ones. Attribution by
   *hours* and attribution by *count* are different questions and this predicts the first.

3. **Inside MIXED, one gate standing beats gates queueing.** BRACKETED hours exceed CLEARED-WITHIN
   hours. **Refuted if CLEARED-WITHIN ≥ BRACKETED.** *This is the prediction that changes what gets
   built,* and it is the question `MIXED` currently conceals: a bucket of episodes where each gate
   clears in turn and the next fires is a **queue**, and the remedy is to run the chain further or
   in parallel so the whole set is visible at once. A bucket where one gate sits red across most of
   the interval time is a **standing red**, and the remedy is to work it. The label `MIXED` reads
   like the first and this measurement decides which it is.

**None of these licenses a change on its own.** Whatever the answer, the deliverable of this turn
is the attribution and the residue named honestly; a mechanism is the next turn's question.

## The controls, and what each one would catch

Written before the numbers exist, so a control cannot be tuned to make the answer come out.

- **C1 — the partition is exact.** For every bounded episode, `Σ interval durations = outage_s` to
  the second, re-derived from the episode's own member timestamps. Catches a decomposition that
  silently loses or double-counts time, which is the only way the percentages below could be wrong
  while every row looks reasonable.
- **C2 — the classes partition the intervals.** Every interval takes exactly one class; the class
  counts sum to the interval count. Catches an interval that falls through every branch and
  vanishes.
- **C3 — every class is REACHABLE.** One control over the whole partition asserting BRACKETED and
  CLEARED-WITHIN and MASKED and UNRANKABLE and TRAILING are each non-empty. A classifier that
  returned one label for everything would pass a per-class test and fail this one. Any class the
  live log does not reach is injected in a fixture rather than left unproven — a branch that
  cannot be taken is not a class.
- **C4 — MASKED must agree with `ordering_report`.** An episode containing a MASKED interval is an
  episode `ordering_report` marks `established` (a backward step), because both are computing the
  same backward rank move by different routes. **They are separate implementations and their
  disagreement is the finding, not an error to smooth over.** Asserted as equality of the two
  episode sets, in both directions.
- **C5 — a BRACKETED interval's ends are adjacent cycles.** With no cycle in between, "no evidence
  it cleared" is a property of the log and not an artefact of skipping an attempt. Catches the
  interval builder walking `refused` instead of `members` and quietly stepping over a
  `behind_origin` cycle that carries information.
- **C6 — no gate is attributed more than the episode's outage.** Catches sign and anchor errors of
  the class that C1 would miss if two errors cancelled.

## What I will not do

- No pooling of BRACKETED and CLEARED-WITHIN into a single "attributed" number.
- No re-labelling of the `MIXED` episode field. It is right and this analysis is beside it.
- No claim that a BRACKETED interval proves a gate stood. The log cannot say that and the class is
  named so no reader can infer it.
- No cadence change. Prediction 1 of the preceding pre-registration held at 17.1% and that remains
  pre-refused.
