# The accuracy verdict had no error bar, and its band sat at the median of its own subject

**Atom:** `H_GAP_fabric_belief_truth_gap` · **Expert Hour #4** · 2026-08-11
**Outcome: the Hour found something NEW, so the level stays 2.**

The third Hour set this one's subject: *ask what population each `_favours` threshold is a
property of, and whether `VERDICT_MATERIALITY` — which decides "neither", and therefore
decides whether any of this machinery speaks at all — has ever been measured against
anything.*

**It never had.** Its docstring gives a motivating anecdote (a 0.3% difference flipping a
sign is not a finding) and no measurement. Measured now, it lands at the **median of the
distribution it discriminates**.

## What was measured

`accuracy_favours` compared the two arms' population-level normalised gaps against a fixed
5%-of-the-larger band. Over 120 random subpanels of the drawn population at each size:

| n | aggregate rule says "neither" | median relative difference | band |
|---|---|---|---|
| 25 | 54% | 0.0469 | 0.050 |
| 50 | 46% | 0.0404 | 0.050 |
| 100 | 46% | 0.0518 | 0.050 |
| 150 | 38% | 0.0534 | 0.050 |

**Flat in N.** A verdict rule whose decisiveness does not improve as homes are added is not
a resolution statement — it is a coin toss over which homes were drawn.

**The direction was never wrong**, which is exactly why it survived four Hours: of 249
decisive subpanels, **0 named the register**. The rule silenced a true and unanimous
direction on about half the panels drawable from the same population, and "neither" reads as
caution.

On the published drawn row the verdict cleared the band by **0.0032** (5.32% against 5.00%),
so a move to 0.055 — for a *money* reason, since this is the money band — would have erased a
published accuracy verdict.

## Three defects, and only the third is about the constant

1. **A per-premise claim audited by a difference of aggregates.** This is the sibling class
   the THIRD Hour named — and then fixed in one place only, the mirror's fidelity term
   (`_register_mad`). The headline verdict itself was left on the aggregate form. R10 says an
   instance fix does not close a class; this is the proof, one Hour later, in the same file.
2. **No uncertainty at all.** Two point estimates against a fixed band, with nothing anywhere
   saying whether the difference was *resolvable* on the panel that produced it. The fourth
   entry in this atom's record had already shown error bars decide the MONEY verdict. The
   accuracy verdict had none.
3. **One constant, two subjects.** `VERDICT_MATERIALITY`'s own comment asserted a firewall —
   *"one constant serving both would mean a change made for a money reason silently re-graded
   every mirror ever run"* — while describing the live wiring. It did.

## What was NOT the defect (refuted in the Hour, by measurement)

- **Sign instability**: refuted. 249/249 decisive subpanels agree. The direction is real.
- **Relative bands diluting on an extensive quantity**: refuted for money. `money_rel` *grows*
  with N (0.078 at n=10 → 0.177 at n=200) and "neither" falls from 47% to 0% — the money
  verdict does get more decisive with evidence, as it should.
- **A sign test as the replacement**: rejected. 166 of 200 drawn premises are exact ties, so a
  sign test runs on 34 rows and reads p=0.12 — it keeps the pairing and discards the
  magnitude, which is the mirror-image mistake.

## The mechanism

`_paired_accuracy_verdict`: the per-premise advantage `|register − truth| − |inference −
truth|`, with a percentile bootstrap CI (`ACCURACY_VERDICT_SEED`, C-S2 named substream — a
verdict movable by quietly reseeding is not a verdict). "neither" only when the interval
straddles zero. Decisiveness now behaves like evidence: "neither" on 55/60, 46/60, 35/60,
18/60 subpanels at n=25/50/100/150.

**Not a tuned threshold (R12/R13).** The *statistic* was repaired, not the band. Nothing was
chosen for the verdict it produces.

**The repair does not delete a disclosure.** On the authored panel the aggregate rule said
accuracy favoured the register while money favoured the inference, so `verdicts_agree` was
False and a HEADLINES DISAGREE caveat fired. Under the repaired verdict accuracy is
unresolvable there (15 premises, 7 exact ties, CI [−0.0162, +0.0075]) — which flips
`verdicts_agree` True and would have silently retired that sentence. `ACCURACY VERDICT
UNRESOLVED` now says so, carrying both figures.

## Evidence

- **R15: 7 source mutations, each firing its own named test**; md5 byte-clean restore
  (`87723c65…`). Includes re-routing the verdict back through `VERDICT_MATERIALITY` (fires),
  always-name-the-inference (fires), and always-unresolved (fires) — the control is proven
  not to be one-directional and not always-red.
- **One mutation was initially SILENT and that was the point.** The determinism test, written
  against a 12-premise fixture with two distinct advantage values, passed a mutation that
  unseeded the bootstrap: the percentiles land on the same discrete points whatever the seed.
  Rewritten against a continuous fixture; it now fires. Caught by the mutation run, not by
  review.
- 279 passed, 2 xfailed across `test_premise_two_level.py`, `test_couple_fabric.py`,
  `test_gap_ledger_reconciler.py`.
- **No published figure moved.** Ledger re-taken on the row's own declared `refresh_args`:
  gaps 0.4269 / 0.4042 unchanged to the bit; the drawn accuracy verdict stays "inferred" and
  is now earned (+0.0024 kW/K, CI [+0.0005, +0.0047], 166/200 ties).

## R10 CLASS

**A verdict band must be measured against the distribution of the quantity it bands.** A band
authored from an anecdote will sit wherever the anecdote put it, and if that happens to be the
median of its subject, the verdict is decided by sampling rather than by the beliefs — while
never once stating a wrong direction. Its failure signature is *decisiveness that is flat in
N*, and that is cheap to measure and nobody had.

**Companion, and this is the fourth Hour running to land in the same family:** the class named
by the third Hour — *a promise made per element cannot be audited by a difference of
aggregates* — was closed on one term and not swept. R10 requires the class to fail
automatically, not the instance.

## What this Hour did NOT do — stated, not implied

- **`panel_mirror_normaliser_drift` was named in the directed question and was not examined.**
  It is untouched and unmeasured by this Hour.
- **The MONEY half of `_favours` is still a relative band on two aggregate GBP sums** — the
  same shape, one subject over. It is *not* obviously the same defect (its decisiveness does
  improve with N, measured above), but it has no error bar either, and the confidence mirror
  already demonstrates that error bars flip it. That is the next Hour's subject, together with
  `panel_mirror_normaliser_drift`.

## Termination condition (unchanged in form)

An Hour on this machinery that finds nothing NEW moves the level; one that finds something
lands the finding and the level stays. **Four consecutive Hours have now found the same
family — a published number that is not the quantity it is named after.**
