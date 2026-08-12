# WORKER FINDING — the belief dimension's TRUTH side is a hand-copy of the company's own rule, and nothing measured it

**Severity:** BLOCKING · **Lane:** H_harness

**Date:** 2026-08-10 · **Found by:** worker tick running Expert Hour #4 on `H27_payment_belief_gap` (2→3)
**Advances:** `D20_belief_truth_rule_is_an_unmeasured_mirror` (minted here, built here)
**Verdict:** **HELD AT L2.** L3 means "no major flaws". A fourth was measured, in the claim that makes the
belief headline a measure of the wall at all.
**R12:** nothing was tuned. The belief gap is unchanged — `0.145933` (n=800, seed 7) before and after this tick.

## Why the Hour ran now

Hour #1 (2026-08-09) found the detection headline was an `as_of` artefact and counted one error direction
(`D11`). Hour #2 found one named quantity published as two numbers (`D16`). Hour #3 (2026-08-10) found the
belief headline blind to who holds which belief (`D19`). Each landed at L2 and emptied its block, and each
release said the same thing: a promoter must run the Hour on the CORRECTED instrument.

The D19 report handed over two named leads. This pass checked both, took neither, and found something under
them — recorded here because the lead that turns out not to be the defect is part of an honest register:

- **The two structurally-zero error directions** (detection's `missed_failure_rate`, belief's `overcall_rate`)
  are each honestly declared, each mutation-proven able to fire, and each is a property of *this book* rather
  than of the measure. Whether a balanced headline whose second direction reads 0 is acceptable at L3 is a
  real judgement, but it is a judgement about the population, and it is already visible in every place the
  number is published. It is not a flaw in the instrument.
- **The unattributed belief directions** in D8's `_ATTRIBUTED_MEASURES` are a D8 question, still open, still
  its owner's.

## The finding — "same threshold shape, different-coverage inputs" was never measured (observed, R9)

The belief dimension publishes its two sides like this, in the note the ledger and the Proof door carry:

> the company's own `arrears_risk_belief` (DD/rail-observed unresolved count) vs the TRUE severity
> (all-channel unresolved count) — **same threshold shape, different-coverage inputs**

That clause is not decoration. It is the entire reason the number counts as a measurement of the **wall**:
if the only difference between the two sides is *which failures the company got to see*, then the gap is
information loss at the seam. If the two sides also run *different rules*, the gap is a mixture — and the
mixture is published under the name of one of its terms.

`tools/couple_w2_11_d5.py::_severity_label` is a **hand-copy** of
`PaymentObservationConsumer._arrears_risk_belief`'s thresholds:

```
harness truth side                          company organ
  n == 0            -> normal                 n == 0  -> NORMAL
  n == 1            -> watch                  n == 1  -> WATCH
  n == 2, hard >= 2 -> high  else elevated    n == 2  -> HIGH if hardship_suggestive >= 2 else ELEVATED
  n >= 3            -> high                   n >= 3  -> HIGH
```

Its own docstring names the mirror ("the SAME thresholding shape ... Mirroring the rule, not re-deriving the
answer from the same inputs, is the R15 independence pattern"). **No test in the repository mentions
`_severity_label` at all.** The claim lived in prose on both surfaces and in code in neither.

### Measured, not argued

Three plausible drifts of the **company organ's own rule**, applied to the organ alone — world untouched,
truth-side rule untouched, seam untouched, so any movement is rule divergence by construction (n=1200, seed 7):

| organ drift (company rule only) | published belief headline | what fired |
|---|---|---|
| one observed failure no longer raises WATCH | 0.1424 → **0.4146** (2.9×) | a permutation probe's **vacuity guard** |
| hardship amplification 2 → 1 | over-call direction leaves 0 | *"this book's company now over-calls"* — a **population premise** |
| HIGH bar 3+ → 4+ | 0.1424 → **0.1551** | the **epistemic-wall-leak** R15 control |

Exactly **one** test fired each time. Not one named the divergence, and two gave an actively wrong diagnosis:
a reader would have gone looking for a weak permutation probe, or for a breach of the wall, while the headline
had quietly become a mixture of coverage loss and rule divergence and went on being published as coverage.

### Why the obvious control is the wrong one

The tempting fix is a test that asserts the two threshold tables match. That is the tautology R15 names: a
third copy of the rule, asserting two copies against each other, passing whenever all three drift together.

**Equalise the coverage instead, and the residual IS the divergence.** On a counterfactual population where
every customer pays by Direct Debit the company observes every failure, so the coverage term is zero by
construction and anything left is the two rules disagreeing on inputs they both fully saw. It needs no copy of
either rule to say so.

Measured at HEAD, n=600, seeds 7/11/23 — and with the vacuity witnesses non-empty each time:

| dimension | claims coverage-only | residual on the all-DD counterfactual | on the scored book |
|---|---|---|---|
| `belief` | **yes** | **0.000000** | 0.1338 / 0.1950 / 0.1325 |
| `belief_population_mix` | **yes** | **0.000000** | 0.0700 / 0.1033 / 0.0733 |
| `detection` | no | 0.000000 | 0.0121 / 0.0225 / 0.0120 |
| `detection_latency` | no | 0.9706 / 0.9319 / 1.0694 | 2.13 / 2.49 / 2.11 |
| `ageing` | no | 0.000000 | 0.1275 / 0.2880 / 0.1667 |

**The claim holds at HEAD.** That is the finding's whole point: it was *true* and *unmeasured*, which is the
state in which it silently stops being true.

## What was built (HARDEN)

- **`measure_coverage_only_residual`** — scores the all-DD counterfactual and reports the surviving residual
  per dimension. The counterfactual is reached by a declared `build_scenario(force_payment_method=...)`
  parameter, not a monkeypatch, so it is legible in the repo rather than living in a test's `setattr` (IaC).
  R13: it does not touch the baseline world; it builds a second, explicitly-labelled one to isolate one term.
- **`COVERAGE_ONLY_CLAIM_CONTRACT`** — which dimensions make the claim and, for the exempt ones, why. It is
  **differential on purpose**, the `DIMENSION_AS_OF_CONTRACT` lesson: a blanket "every residual must be zero"
  would fire on `detection_latency`, where non-zero is correct, and a control that false-positives teaches
  everyone to skip it.
- **The claim now travels with the number** — the belief note states what the claim is, that it was
  unmeasured until today, what three drifts did to the headline, and which control now measures it; the CLI
  prints the residual table and its witnesses under `--coverage-residual`.

**Vacuity is the hard part here**, because the control's healthy reading is a zero. Four witnesses, all
required, all asserted:

1. the scored book really carried the coverage loss being removed (non-DD true failures > 0),
2. the counterfactual really removed it (non-DD failures == 0 there),
3. both belief error populations are non-empty there,
4. **the differential** — at least one *exempt* dimension reads non-zero on the same population, so a run that
   collapsed every gap to zero (an empty book, a dead scorer, a broken build) cannot pass as agreement.

### The class control (R10 — the class, not the instance)

```
if a dimension's PUBLISHED TEXT tells a reader its two sides differ only in coverage,
it MUST be declared in the contract — which is what puts it under the measurement
```

Swept over the text a reader actually sees, per the D16/D19 phrase-sweep pattern, with the register **derived**
from the published dimensions rather than hand-maintained.

**The first draft of that sweep was itself vacuous** and its own vacuity guard caught it on first run: it swept
the CLI formatter output alone, where the phrase does not appear, so the control passed while never looking at
its own headline dimension. The swept text is now the summary **and** the note — the note being the surface the
ledger and the Proof door actually carry. Recorded rather than quietly fixed: it is the same fail-silent shape
this instrument has now produced four times, and it appeared inside the control written to close it.

### R15, mutating the SOURCE

- Each of the three organ drifts above, as a permanent in-suite mutation test: the company's own severity rule
  changes, the truth-side rule does not, and the coverage-only residual must leave zero. All three fire.
- Make `force_payment_method` silently ignored → **6 tests fire**, on the vacuity witnesses, not on the
  residual: the diagnostic says the counterfactual is dead, which is the true cause.
- Undeclare the claim `belief` publishes → the class sweep fires, naming the dimension.
- Both mutated files were restored and verified byte-identical by checksum (`md5sum -c`).

## What was NOT done, and why

`_severity_label` is left as a mirror. Making the harness call the organ's own thresholding function would
delete the independence the mirror exists to provide (a harness that asks the company to define truth cannot
measure the company against it), and rewriting the truth-side rule to something else moves a published number
for a reason no measurement supports — R12. The mirror is the right design; what was missing was the control.

## Why H27 is still at L2

The draw was H27 2→3, and this is the fourth consecutive Hour to find something in a published headline. Two
of those four defects were in claims *about* the instrument rather than in its arithmetic, which is the part of
L3 — "this harness measures what it says it measures" — that has been failing. It is also, again, the tick that
changed the instrument, and taking L3 on the reputation of a build one tick old is the exact move every prior
release refused.

No `depends_on` is added: `D20` is built, and pointing a block at a satisfied atom is the dead-mechanism class
this atom's note has already fallen into twice. **The next HARDEN draw of H27 is Expert Hour #5**, on the
corrected instrument. Where it should start:

1. Four Hours have now produced four defects, none of which the previous Hour predicted, and the arrival rate
   is not falling. That is itself evidence about the instrument, and an Hour that finds nothing is the first
   real evidence for L3 — the promotion criterion should probably be *two consecutive clean Hours*, stated in
   advance rather than decided by whichever tick happens to draw it.
2. The `ageing` dimension is the only one of the four that has never had an Hour of its own; every finding so
   far has landed on detection or belief. Its owner-atom `D6_payment_ageing_gap_validity` has sat at level 0
   since the original L0→L2 certification named it as blocker (2).

## Tests

**8 new** in `tests/tools/test_couple_w2_11_d5.py`; **195 green** across every coupled-pair suite
(`test_couple_w2_11_d5`, `test_live_payment_triad`, `test_couple_cohort`, `test_couple_w2_4_c6`,
`test_couple_w2_5_c7`, `test_couple_fabric`, `test_couple_supply_start`).
