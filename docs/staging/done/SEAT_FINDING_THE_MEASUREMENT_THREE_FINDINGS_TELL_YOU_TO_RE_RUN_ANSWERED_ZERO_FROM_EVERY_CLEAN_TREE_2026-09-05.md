**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the measurement three findings tell you to re-run answered "the publisher never failed" from every clean tree — and the deepest gate in the chain has never been observed at all

**Found:** 2026-09-05, delivery seat, third turn on the Lane 0 direction *"measure and attribute
commit_refused"*. Pre-registered before any classification:
`docs/design/PREREGISTRATION_ARE_THE_GATES_QUEUEING_FLAPPING_OR_MASKED_2026-09-05.md`.
Measurement: `docs/observability/gate_order_recurrence_2026-09-05.md`.

---

## First, what I got wrong and who was right

A concurrent lane worked the predecessor's open question — queueing, flapping, or an ordering
artefact — at the same time as me, and **landed first**:
`SEAT_FINDING_THE_FIRING_ORDER_CONCEALS_RE_ARRIVALS_RATHER_THAN_FAKING_THEM_AND_82_PERCENT_OF_THE_COST_IS_A_GATE_THAT_RE_BROKE_2026-09-05.md`.
We reached the same structural insight independently — the chain is serial and `|| exit 1`, so a
named cause proves every shallower gate passed — and **their answer is better than mine on the
point that decides it**:

- I labelled a forward step a `QUEUE STEP`. **A forward step establishes nothing.** A genuine queue
  and a set of gates all red from the start produce identical logs. Their `ORDER-CONSISTENT` bucket
  names what cannot be distinguished instead of asserting a queue, and mine asserted one.
- Their test compares each step against the **running peak rank**, not the previous cause, so it
  catches a re-arrival where a cause appears once below a rank already reached. My adjacent-pair
  test was structurally blind to those. **There are 4, and they are 4 that the predecessor's
  contiguous-block test also missed** — that test was under-counting, not over-counting.

The standing answer to the direction's question is theirs: **ESTABLISHED re-arrival in 11 of 16
mixed episodes, 147.4h, 82.4% of mixed outage.** My ordering machinery was **deleted, not merged
alongside it** — two lanes centralising into one file merge cleanly into two definitions of one
concept, and that is a defect this project has paid for before. What follows is what survived as
additive.

## The defect: an absent subject read as a clean result

**`docs/observability/sim-runner-log.md` is tracked, but its committed copy was truncated to
2026-07-17 on 2026-08-31.** Every line any of these three findings measures has been written to the
running daemon's **working copy** since. All three publish
`python3 -m tools.commit_refusal_attribution` as their re-derivation instruction.

Run from a clean checkout, an isolated worktree, CI, or a `git archive HEAD` extract — which is to
say from anywhere a reader would go to *verify* one of them — the module printed:

```
commit_refused cycles: 0
attempts (lifetime):   1306  -> share 0.0%
total bounded outage: 0.0h over 0 episodes
```

A complete, confidently formatted report that the publisher has never once failed. Not a crash, not
an empty output, not a warning: **the most comfortable answer available, produced by a file that
does not contain the subject.** This is the fail-open direction on a measurement whose entire
purpose is to price a failure, and I found it by running the tool I had come to extend.

It now refuses with exit 2, names which copy it read, how many attempt lines it saw, and why the
file is empty of outcomes. The refusal **replaces** the report rather than preceding it — a zero
printed under a warning is still a zero a reader will quote.

**The general shape, which is the part worth keeping:** a measurement whose subject is another
process's uncommitted working copy must say so on its own surface. This one said `0.0h`.

## The result: the deepest gate in the chain has never been observed

The same early exit that makes the ordering analysis work also bounds what `by_gate` can mean. It
is a distribution of **first failing** gate, so every count is a lower bound and the bias is
monotone in chain position. Per gate, over the 174 refused cycles — named, **proven** to have
passed (a deeper gate was reached), or unknown (never reached):

| Gate (chain order) | named | proven passing | unknown |
|---|---:|---:|---:|
| finding-class consolidation | 31 | 122 | 21 |
| RED TEST | 70 | 52 | 52 |
| level-promotion gate | 12 | 40 | 122 |
| site-lane gate | 20 | 20 | 134 |
| orphan-ratchet | 16 | 4 | 154 |
| scope-evidence ratchet | 2 | 0 | 172 |
| **write-time gate** | **0** | **0** | **174** |

*(full 17-row table in the measurement)*

**The write-time gate has no observation of any kind in this window.** Never named, never proven
passing. "It never refused a publish" is not an observation about that gate — it is unobservable,
and reading `by_gate`'s silence about it as a fact about the gate is reading a fact about the
chain's order as a fact about the world. Seven gates have zero named refusals and 150+ unknown
cycles each.

Inversely, and this one is a positive observation rather than an inference: on **52 of 174 refused
cycles (29.9%) the entire test suite is proven green.** Those publishes were blocked purely by
governance state.

**So the predecessor's `governance 48% / red 40% / unattributable 12%` split is a lower bound per
gate**, and its internal ranking — finding-class 31 > site-lane 20 > orphan 16 — is confounded with
chain position and should not be read as which gate causes most trouble.

## Predictions, scored

**P1 (a proven flap exists) CONFIRMED**, and by the predicted mechanism — finding-class, the
shallowest gate, is the one whose re-breaking is provable. **P3 (new breakage in ≥25% of mixed
episodes) CONFIRMED** and superseded by the rival lane's stronger 82.4% figure on the same
phenomenon. **P4 CONFIRMED a priori, magnitude above, and larger than I expected.**

**P2 is the one to keep. It said the majority of decidable recurrences would be proven flaps, and
it was computed on an instrument whose forward-step label was wrong.** 8 of 13 decidable, but
exactly 50.0% of all 16 — carried only by excluding the undecidable. I recorded that narrowness
before seeing the rival finding, and the rival finding then showed the whole framing was the weaker
one. **A prediction confirmed on a mis-specified instrument is not a confirmation**, and it is
recorded here as withdrawn rather than as a win.

**The decision rule declared in advance** sent me to "mixed with no majority — build nothing". The
rival's peak-rank test resolves it properly to "established re-arrival dominates". Either way the
action is the same and it is the pre-registered one: **no mechanism, no alarm, no threshold.**

## What landed

`tools/commit_refusal_attribution.py`: `masking_exposure()` and the fail-closed subject guard in
`main`, on top of the rival lane's `gate_ranks`/`ordering_report` which are now the single
definition. Three new controls in `tests/tools/test_commit_refusal_attribution.py` (28 total,
green), all mutation-proven: removing the subject guard, flipping the proven-passing direction,
counting every cause as proven passing, and folding unknown onto passing each fire a named test.

## Named, not done

**`RED TEST` is a bucket, not a gate identity.** An established re-arrival of it may be one test
re-breaking or two different tests breaking in turn — a contended control versus ordinary traffic,
different findings with different remedies. The node ids are already retained in the hook blocks. I
built this against my own recurrence machinery and it went when that did; it is the next question,
and it needs no new data.
