# WORKER FINDING — the resample guard counted the panel, not the evidence

**Severity:** BLOCKING · **Lane:** H_harness

**Atom:** `H_GAP_fabric_belief_truth_gap` (H_harness, L2→L3 draw, worker tick)
**Date:** 2026-08-12 · **TENTH EXPERT HOUR** on this machinery
**Outcome:** IT FOUND SOMETHING, SO THE LEVEL STAYS 2.
**Directed question, set verbatim by the ninth Hour:** `panel_mirror_weight_artefact`
is called a SHARE and is not bounded by 1 (the authored row reads 80% on [73%, 122%])
— named by the eighth Hour, untaken since, the oldest open item on this atom.

---

## 1. The directed question answers NO, and the answer is measured

**The unboundedness is REAL and it is NOT a defect in the statistic.** The eighth
Hour's own reading was right: the ratio exceeds one where the null moves the deciding
margin FURTHER than the mirror does — the sign flip opposing its own re-weighting
rather than adding to it — and those readings are informative.

Measured against the obvious replacement, a per-premise bounded decomposition
(`|null| / (|null| + |mirror − null|)`, the sixth Hour's own shape for
`panel_mirror_yardstick_share`, which had exactly this problem and was bounded by
dividing by the sum of the magnitudes):

| population | shipped ratio | bounded shape | delta |
|---|---|---|---|
| authored 15 | 0.8037 | 0.7670 | +0.0367 |
| drawn 200 | 0.7307 | 0.7307 | 0.0000 |

And across 800 real subpanels of the drawn population at n = 20/30/50/100, the two
shapes are **bit-identical on every one** (max |delta| = 0.0000), crossing the band on
none. The algebra says why: where the two channels share a sign and `|null| ≤ |mirror|`
the two shapes are the same number identically, and neither published population has a
single premise where they part. The bounded shape is also **always ≤ the shipped one**
(triangle inequality), so swapping it in could only ever GRANT certification — a repair
that hands out passes on evidence nobody asked for.

**So the statistic is left alone.** What was wrong is the word: the sentence said
`X% … is reproduced`, and "reproduced" does not admit 122%. That is now a sentence fix,
below.

## 2. Chasing where the authored row's 122% came from is what found the defect

The 122% is the upper end of a bootstrap. Over **FOUR HOMES**.

```
authored:  panel rows = 15   premises carrying the statistic =  4   MIN_HOMES_FOR_DIVERSITY = 5
drawn:     panel rows = 200  premises carrying the statistic = 18
```

`panel_mirror_weight_artefact_interval` withheld itself when
`len(self.margin_moves) < MIN_HOMES_FOR_DIVERSITY` — the panel's **ROW COUNT**. But the
share is `mean|null| / mean|mirror|`, and a premise neither channel moved contributes
exactly zero to both sums. It is a row in the panel; it is not evidence about this
instrument. So a 200-home panel in which the mirror moved ONE home was, to the guard
that exists to refuse an un-resamplable panel, a 200-home panel.

**The authored published row is below this file's own minimum and its guard passed.**

### The failure, measured on 1,200 real subpanels of this atom's own published population

The drawn population's own share is 0.7307, above the 0.50 band, so **every
certification granted on a subpanel of it is wrong by construction** — the eighth
Hour's own framing, re-used.

| movers | panels | CERTIFIED (all wrong) | unattributable | unresolved | median interval width |
|---:|---:|---:|---:|---:|---:|
| 1 | 147 | **59** | 0 | 88 | 0.792 |
| 2 | 204 | 24 | 0 | 180 | 1.000 |
| 3 | 161 | 7 | 0 | 154 | 1.000 |
| 4 | 149 | 2 | 23 | 124 | 1.000 |
| 5 | 102 | 1 | 7 | 94 | 0.908 |
| 6–15 | 373 | **0** | 29 | 344 | 0.57–0.84 |

**93 wrong certifications. 92 of the 93 (99%) came from panels with fewer than
`MIN_HOMES_FOR_DIVERSITY` movers; 83 (89%) from fewer than three; 59 (63%) from a
SINGLE moved home. The guard fired on none of the 1,200, because every panel had
20–100 rows.**

### The worst reachable point, and why the eighth Hour's repair could not stop it

Where one premise carries the whole statistic, every resample containing it reads the
same ratio and every resample missing it reads the 0/0 corner, so the percentile
interval **collapses to a width of zero**:

```
one mover of 20 rows, ratio 0.10   ->  95% interval [0.000, 0.100]   hi <= band  -> CERTIFIED
four identical movers of 20 rows   ->  95% interval [0.100, 0.100]   width 0.000 -> CERTIFIED
```

The eighth Hour made this gate read the interval *precisely so* an unresolvable panel
could not certify, and cited "the share was estimated from FOUR moved homes and its 95%
interval was [0.000, 1.000]" as the pathology it was closing. A degenerate interval is
the one shape that defeats an interval rule, and it arrives wearing **maximum
confidence**. Wide intervals get caught; narrow ones off four homes do not.

## 3. The class (R10)

> **A GUARD SIZED ON THE PANEL CANNOT PROTECT A STATISTIC CARRIED BY A SUBSET OF IT.**
> Failure signature: **the guard's subject grows with N while its evidence does not** —
> it gets more confident about its own sufficiency exactly as the panel gets larger and
> the moved fraction stays flat.

The fourth Hour found a rule FLAT IN N, the fifth one DECOUPLED FROM N, the ninth one
whose SENSITIVITY FALLS WITH N. This is the fourth sibling and it is about the
*guard* rather than the statistic: the population it counts and the population that
carries the number have simply never been the same set.

Sibling class, already this atom's: **a repair applied to the verdict and not to the
instrument that certifies it.** The fifth Hour built `largest_premise_share` because a
money verdict could be one house; the seventh built this instrument's interval an
Hour later with no equivalent, and the eighth gated on it.

## 4. Mechanised, not exhorted

* **`panel_mirror_artefact_evidence_premises`** — the count of premises where EITHER
  channel moved. Deliberately not `panel_mirror_moved_premises` (the mirror's movers
  only), which was the nearest thing to hand: a premise the NULL moved and the mirror
  did not carries numerator with no denominator, and it is exactly the premise that
  makes the ratio explode.
* **The guard reads it.** `panel_mirror_weight_artefact_interval` withholds itself when
  fewer than `MIN_HOMES_FOR_DIVERSITY` premises carry the statistic.
* **THE CONSTANT IS UNTOUCHED (R12, and the ninth Hour's rule — repair the statistic,
  not the band).** `MIN_HOMES_FOR_DIVERSITY` was already the right number for the right
  question ("how many homes stand behind this statistic") and it is the same subject
  the file's other seven uses give it, so this is **not** the sixth Hour's
  one-constant-two-subjects class. Only the counting was wrong. Calibrating a new
  constant off the table above would have been tuning a threshold to this population's
  outcomes (R13).
* **ONE-DIRECTIONAL BY CONSTRUCTION.** A withheld interval resolves to `unresolved`
  (fail-closed since the eighth Hour), never to a pass. No verdict this gate released
  before is newly released now.
* **The withheld-interval sentence names the population that was counted** — it said
  "too few premises to resample (under 5)" while counting rows. The eighth Hour's class
  (a disclosure inheriting the population its gate stopped using) applied before it
  could happen rather than an Hour after.
* **The over-100% clause**, closing the eighth Hour's named item as a sentence.
* **The diluted per-premise figures now say what they are.** The sentence printed
  "GBP 230 of 314 per premise … across the 18 of 200 premises the mirror moved" — but
  both means are over all 200, and per premise the mirror ACTUALLY moved the figure is
  GBP 3,494. **11.1x on the drawn row, 3.7x on the authored one**, with the sentence
  itself supplying the count a reader would multiply by. It now reads "per PANEL
  premise — both means are over all 200, not over the movers".
* **`panel_mirror_artefact_evidence_premises` rides in the ledger row**, because the
  guard that counted the wrong population was invisible for three Hours precisely
  because nothing printed the right one.

## 5. R15 — six source mutations, each firing its own named test

md5 byte-clean restore after every one (`a5973d0834791eec882188be2956e40f`), 8 green on
the same selection unmutated:

1. the guard counts panel rows again (**the exact defect reinstated**) → 4 tests fire
2. the evidence count counts the mirror's movers only → 1
3. the withheld-interval sentence keyed back to the panel → 1
4. the over-100% explanation dropped → 1
5. a withheld interval falls back to the point estimate (the fail-open shape) → 4
6. the diluted figures presented as the movers' own again → 1

**NOT ALWAYS-RED, and the proof was checked rather than assumed.** The eighth Hour's
own searched not-always-red population (`_flipping_population`, 60 homes) carries **29**
movers and still certifies — had it carried four, this repair would have deleted the
demonstration that the control it guards can pass.

## 6. No published figure moved, checked not asserted

Both rows re-taken on their own declared population (`--seed 17 --unit-rate 7.4
--population 200 --population-seed 17`, read back off the row per the `refresh_args`
mechanism) **after** the code landed, which is the only ordering under which the row
comes out `current`: gap **0.4269 / 0.4042**, forgone **GBP 548,919 / 451,832**,
misranked 10/11, declined 89/73, two-level still RED on `L2.4_scale_spread_p90_p10`
(the birth condition holding, not a regression). The drawn rows carry 18 movers, so
their interval ([36%, 90%]) and their resolution (`unresolved`) are unchanged.

The whole ledger diff is `measured_at`, `run_git_commit`, the one new field
(`panel_mirror_artefact_evidence_premises` = 18) and the one clause in the caveat that
now says which denominator it used. W2_11 re-stamped itself concurrently via its own
live writer and is not this tick's change.

**ONE CLAIM DID CHANGE, on the AUTHORED panel** (measured by the tool, not a ledger
row): it said "95% interval [73%, 122%]" and "above the 50% band"; it now says "too few
premises carry it to resample (4 moved either channel, under 5)" and "cannot resolve
which side". `panel_mirror_is_attributable` reads False before and after — what changed
is that the row no longer claims to have MEASURED something it estimated off four homes.

Suites: **252 passed 2 xfailed** in the atom's own file, **79** across its three
siblings; `epistemic_verifier` **PASS**, 555 files.

## 7. Opener for the eleventh Hour

**The register channel's own evidence count has never been asked for.** The ninth Hour
split that channel by branch and put the level branch on `panel_mirror_register_worst_breach`
— a worst-case over the premises, which needs no resample and so escaped this Hour's
finding. But its FALLBACK branch is still a panel mean against `MIRROR_FIDELITY_BAND`
with no interval and no statement of how many premises carry it, and the ninth Hour's
own measurement (unresolved on 3 of 22 subpanels at n=20) was taken on a branch neither
published population enters. A term measured only where it never runs is the third
Hour's "algebraically zero" note in a new place.

**ALSO NAMED, NOT TOUCHED:** this atom now publishes FOUR retained-but-superseded
fidelity statistics (`panel_mirror_relative_infidelity`, `panel_mirror_weight_artefact_aggregate`,
`panel_mirror_register_infidelity` on the level branch, `panel_mirror_register_mad`)
whose only defence against being misread is their docstrings — carried forward from the
ninth Hour, now one longer.
