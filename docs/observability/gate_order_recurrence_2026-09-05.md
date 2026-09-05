# Measurement — what the chain's early exit costs the cause split, and which copy of the log is the subject

*2026-09-05, delivery seat. Pre-registered before any classification:*
`docs/design/PREREGISTRATION_ARE_THE_GATES_QUEUEING_FLAPPING_OR_MASKED_2026-09-05.md`.

**Re-derive:**
`python3 -m tools.commit_refusal_attribution --log <shared tree>/docs/observability/sim-runner-log.md`

**Read that path twice, and see §2 before running it without `--log`.**

---

## 0. What this document is, after a concurrent lane landed the same question first

This turn and `SEAT_FINDING_THE_FIRING_ORDER_CONCEALS_RE_ARRIVALS_RATHER_THAN_FAKING_THEM…`
worked the predecessor's open question — queueing versus flapping versus an ordering artefact —
independently and simultaneously. **That finding landed first and its answer is the better one**,
on a point where my own framing was wrong: I labelled a forward step a `QUEUE STEP`, and a forward
step establishes nothing, because a genuine queue and a set of gates all red from the start produce
identical logs. Their `ORDER-CONSISTENT` bucket names that correctly.

Their `ordering_report` also tests a step against the **running peak rank** rather than against the
previous cause, which catches a re-arrival where a cause appears only once below a rank already
reached. My adjacent-pair test could not see those; there are 4 of them.

**So their implementation is the single definition and mine was deleted rather than merged
alongside it.** Two lanes centralising into one file merge cleanly into two definitions of one
concept, which is the defect this project pays for repeatedly. What follows is only what survived
as genuinely additive.

The headline that stands, from their measurement, is theirs: **ESTABLISHED re-arrival 11 of 16
mixed episodes, 147.4h, 82.4% of mixed outage.**

## 1. What the same early exit costs the cause split

`by_gate` is a distribution of **first failing** gate. Each count is a lower bound and the bias is
monotone in chain position: the last gate is only ever visible when every gate before it passes.
Per gate over the 174 refused cycles the episode view covers — **named**, proven to have **passed**
(a deeper gate was reached), or **unknown** (a shallower gate refused first, so it was never
reached):

| Gate (chain order) | named | proven passing | unknown |
|---|---:|---:|---:|
| finding-class consolidation | 31 | 122 | 21 |
| finding-severity gate | 0 | 122 | 52 |
| RED TEST | 70 | 52 | 52 |
| level-promotion gate | 12 | 40 | 122 |
| site-lane gate | 20 | 20 | 134 |
| moap-coherence gate | 0 | 20 | 154 |
| ruling-archive-question gate | 0 | 20 | 154 |
| consolidation-rhythm gate | 0 | 20 | 154 |
| size-ratchet gate | 0 | 20 | 154 |
| orphan-ratchet | 16 | 4 | 154 |
| company-network-isolation gate | 0 | 4 | 170 |
| file-scope-generated-paths gate | 1 | 3 | 170 |
| annual-report-import ratchet | 0 | 3 | 171 |
| half-hourly-dependency ratchet | 1 | 2 | 171 |
| running-total-order gate | 0 | 2 | 172 |
| scope-evidence ratchet | 2 | 0 | 172 |
| **write-time gate** | **0** | **0** | **174** |

**The write-time gate has no observation of any kind in this window.** Never named, never proven
passing: its state is unknown on all 174 refused cycles. "It never refused a publish" is not an
observation about that gate — it is unobservable, and reading `by_gate`'s silence as a fact about
the gate reads a fact about the chain's order as a fact about the world. Seven gates have zero
named refusals and 150+ unknown cycles each.

Read the other way: on **52 of 174 refused cycles (29.9%) the entire test suite is proven green**,
because a gate deeper than the pytest run was named. Those publishes were blocked purely by
governance state, and that is a positive observation rather than an inference.

**This is the magnitude behind P4**, which was proven a priori by the early exit. It says the
predecessor's `governance 48% / red 40%` split is a lower bound per gate whose internal ranking
(finding-class 31 > site-lane 20 > orphan 16) is confounded with chain position.

## 2. The instrument was answering zero from every clean tree

`docs/observability/sim-runner-log.md` is tracked, but the **committed copy was truncated to
2026-07-17 on 2026-08-31**, and every line this measurement reads has been written to the running
daemon's **working copy** since. Run from this isolated worktree against the default path, the
module printed:

```
commit_refused cycles: 0
attempts (lifetime):   1306  -> share 0.0%
total bounded outage: 0.0h over 0 episodes
```

A complete, confidently formatted report that the publisher has never once failed — the most
comfortable answer available, produced by an **absent** subject rather than a clean one. Three
findings now publish `python3 -m tools.commit_refusal_attribution` as their re-derivation
instruction, so anyone checking any of them from a clean checkout, CI, or a `git archive HEAD`
extract was handed that. It now refuses, with exit 2:

```
REFUSED: docs/observability/sim-runner-log.md contains no named commit outcome, so nothing here is measurable.
  read 1306 attempt line(s), 0 of them refused
  The named-outcome vocabulary began 2026-08-13. A file without it is either
  entirely older than that, or it is the COMMITTED copy -- truncated to
  2026-07-17 on 2026-08-31. The subject is the running daemon's working copy.
  Point --log at the shared tree's copy; do not read a zero here as a result.
```

The refusal **replaces** the report rather than preceding it: a zero printed underneath a warning
is still a zero a reader will quote.

## 3. Not done, and named rather than left implied

**`RED TEST` is a bucket, not a gate identity.** An established re-arrival of `RED TEST` may be one
test re-breaking or two different tests breaking in turn — a contended control versus ordinary
traffic, which are different findings with different remedies. The hook blocks retain `FAILED`/
`ERROR` node ids, so this is answerable from the log already retained. I built it against my own
recurrence machinery, which was deleted in favour of theirs, and did not rebuild it on top of
`ordering_report` this turn. It is the next question, not a gap in the data.
