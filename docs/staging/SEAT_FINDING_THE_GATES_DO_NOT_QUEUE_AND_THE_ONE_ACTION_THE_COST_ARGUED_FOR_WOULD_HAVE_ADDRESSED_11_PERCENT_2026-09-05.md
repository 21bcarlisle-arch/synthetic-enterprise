**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the gates do not queue, so the one action the cost analysis argued for would have addressed 11% of the outage — and the instrument that proved it was answering zero from every clean tree

**Found:** 2026-09-05, delivery seat, third turn on the Lane 0 direction *"measure and attribute
commit_refused"*. Pre-registered before any classification:
`docs/design/PREREGISTRATION_ARE_THE_GATES_QUEUEING_FLAPPING_OR_MASKED_2026-09-05.md`.
Full measurement: `docs/observability/gate_order_recurrence_2026-09-05.md`.

Predecessors, both landed, both of whose conclusions survive:
`…THE_272_COMMIT_REFUSALS_ARE_175_CYCLES…` (share 39.6%, split red 40% / governance 48% /
unattributable 12%) and `…COULD_NOT_LAND_45_PERCENT_OF_THE_WINDOW…` (239.6h outage, 74.6% in
mixed-cause episodes). The second closed by naming this question and the alternative it had not
ruled out. Both are answered here.

---

## The answer, first

The previous turn wrote: *"the one action the cost distribution clearly argues for — telling the
publisher about more than one refusal per round trip"*. **That action addresses 11.1% of the
outage.** Pure-queue episodes — every step revealing a later gate, no cause ever recurring — are 4
of 26 and hold 25.4h of 228.7h. Episodes containing a *proven* flap or a *proven* new breakage hold
**58.0%**. The 68.8h episode, 28.7% of all outage by itself, contains both.

The publisher is not grinding through a queue of gates it was told about one at a time. **The tree
is being re-broken underneath it**, and batching the refusal reporting would have told it more
about a state that had already changed by the next attempt.

## Why this was decidable rather than arguable

`core.hooksPath` is `tools/git-hooks`; every gate there is `python3 … || exit 1`. Serial, fixed
order, first refusal wins. So **a named cause proves every earlier gate passed on that cycle and
says nothing about the later ones** — which turns the predecessor's open question into two proofs:

- A cause recurring with a **later** gate named in between was reached and cleared in between, so
  it re-broke. **PROVEN FLAP.** With only **earlier** gates in between it may never have been
  fixed: **MASKABLE**, and no evidence either way.
- A step to an **earlier** gate proves that gate was *passing* on the previous cycle. **PROVEN NEW
  BREAKAGE**, not a queue step.

The order is derived from the two hook files and joined to the publisher's own banner table by the
emitter path it already carries. Nothing is typed; a hand-written order would drift from the hook
silently, one level up from the private-vocabulary defect the banner reuse already fixed.

## Predictions, scored

**P1 — at least one PROVEN FLAP exists. CONFIRMED (8), and by the predicted mechanism.** I
predicted finding-class would be the provable flapper in the 68.8h episode because it is earlier
than the pytest run, so a red test being reached proves it passed. finding-class is the top flapper
at 4 proven, and it is the earliest gate in the hook.

**P2 — the majority of decidable recurrences are proven flaps. CONFIRMED, narrowly, and the
narrowness matters.** 8 of 13 decidable = 61.5%. But of all 16 recurrences it is **exactly 50.0%**,
which is not a majority — the prediction is carried only by excluding the 3 undecidable, and I did
declare "decidable" in advance. Recorded both ways rather than quoting the flattering one.

**P3 — proven new breakage in ≥25% of mixed episodes. CONFIRMED at 56.3%** (9 of 16), more than
twice the prediction. This is the result the finding turns on.

**P4 — the by-gate distribution is order-biased. CONFIRMED a priori; the magnitude is the new
part** — and it is larger than I expected. The **write-time gate's state is unknown on all 174
refused cycles**: never named, never proven passing. "It never refused a publish" is not an
observation about that gate, it is unobservable. Seven gates have zero named refusals and 150+
unknown cycles each. **So the predecessor's 48% governance share is a lower bound per gate with a
bias monotone in hook position**, and its internal ranking (finding-class 31 > site-lane 20 >
orphan 16) is confounded with the order. Read the other way: on **52 of 174 refused cycles (29.9%)
the whole test suite is proven green**, so those publishes were blocked purely by governance state.

## The decision, against the rule declared in advance

The pre-registered rule's fourth branch: **the classes are mixed with no majority — report it,
build nothing, and say what would separate them.** That is where this lands, but not symmetrically:
the *queueing* branch is affirmatively refuted on cost weight (11.1%), so the one mechanism that
was on the table is off it. What would separate flapping from new breakage further is naming the
gate's *subject* per refusal (which finding was unclassified, which module unwired) — the log
retains the banner but not the artefact it named, so that is a change to what the publisher logs,
not a further reading of what it already logged.

**`RED TEST` is a bucket, not a gate identity**, and the split matters: of the red-test recurrences
whose node ids survived, **3 were the same test re-breaking and 3 were different tests**. Half of
what reads as one flaky control is ordinary traffic.

## The defect found on the way, which is the more urgent half

**The instrument was answering zero from every clean tree, and both predecessor findings told
readers to run it.** `docs/observability/sim-runner-log.md` is tracked, but the committed copy was
truncated to 2026-07-17 on 2026-08-31; every line the measurement reads was written to the daemon's
**working copy** since. From this isolated worktree the module printed `commit_refused cycles: 0`,
`share 0.0%`, `total bounded outage: 0.0h over 0 episodes` — a complete, confidently formatted
report of the publisher never having failed, which is the most comfortable answer available and was
produced by an absent subject rather than a clean one. Both landed findings publish
`python3 -m tools.commit_refusal_attribution` as their re-derivation instruction. Anyone verifying
either of them from a clean checkout, CI, or a `git archive HEAD` extract was handed that.

It now **refuses** with exit 2, naming which copy it read, how many attempt lines it saw, and why
the file is empty of outcomes. A measurement whose subject is another process's uncommitted working
copy has to say so on its own surface; this one said `0.0h`.

## What landed

`tools/commit_refusal_attribution.py` gains `gate_order()`, `recurrence_pairs()`,
`classify_recurrence()`, `classify_transition()`, `recurrence_report()`, red-test node ids on each
cycle, and the fail-closed subject guard in `main`. Eight new controls in
`tests/tools/test_commit_refusal_attribution.py` (23 total, all green).

**All eight are mutation-proven, and the eighth exists because a mutation survived.** Relaxing
`gate_order`'s missing-hook refusal from `return {}` to `continue` still answers `{}` when *both*
hooks are absent, so the control I had written passed either way. With `pre-commit` gone and
`commit-msg` present it enumerates the survivor from index 0 — and that gate is `write-time`, which
really runs *last*. Every classification would have been computed against an order that is exactly
backwards, and would have read as confident. That was a missing test, not an equivalence, and the
partial-hook case is now its own control.

The controls are keyed to properties, not to today's counts: the two hook orders must give
**different** verdicts on one identical sequence; a step to an earlier gate must never come out as
a queue step; an unknown position must stay UNDECIDABLE and never fold onto either side; a cause
firing five times must be four recurrences and not ten; an absent subject must refuse *instead of*
printing a report, not above one.
