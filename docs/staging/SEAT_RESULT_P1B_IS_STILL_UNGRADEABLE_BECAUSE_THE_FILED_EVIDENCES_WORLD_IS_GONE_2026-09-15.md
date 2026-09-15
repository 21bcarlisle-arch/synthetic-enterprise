**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

# RESULT — §A's P1b is still ungradeable, and the reason is now much stronger: the world its evidence came from is not the world we ship

**Filed 2026-09-15, delivery seat.** Pre-registered before the run, with the grading rule, the
kill lines and the self-check all fixed in advance:
`docs/staging/records/SEAT_PREREG_WHERE_THE_CHOOSERS_GAIN_SITS_PER_AXIS_AND_WHETHER_SECTION_AS_P1B_HOLDS_2026-09-15.md`.

Harness: `tools/settlement_per_axis_gain.py`. Artefact:
`docs/observability/settlement_per_axis_gain.json`.

---

## The headline

I went to grade one clause — §A's P1b, *"the gain is concentrated on the fabric axes rather than on
cost"* — which
`SEAT_RESULT_SECTION_A_OF_THE_MERGED_PREREGISTRATION_REGRADED_AGAINST_ITS_OWN_NUMBERING_2026-09-15.md`
had recorded as UNGRADEABLE because the filed evidence reports worst-axis KS and P1b is a claim
about per-axis KS.

**The per-axis numbers are now measured. P1b is still ungradeable against its own evidence, and the
new reason is worse than the old one.** The filed scalars do not reproduce, and the cause is not
the harness:

```
seed 42                    FILED (09-11)        MEASURED (this tree, 09-15)
candidates                     502                    502     same
cull settled / cy           90 / 1195.4          90 / 1195.4   same
chosen settled / cy         84 / 1197.0          83 / 1199.2   DIFFERENT
distinct fabric vectors        109                    105      DIFFERENT
worst-axis KS  cull / chosen  0.12798 / 0.08241   0.09765 / 0.05878
worst-axis ratio              1.553x               1.661x
```

**The funnel is identical and the homes are not.** The cull is a deterministic systematic rule over
the candidate list, and it settles *the same 90 accounts at the same 1195.3895 customer-years* —
so the candidate list, its order and its costs are byte-for-byte the list the filed run used. What
moved is what those candidates *live in*.

## The attribution, established rather than suspected

`0d86d6dfe` — *"the world's homes are drawn from the fitted joint now, and the insulation ceiling
the company sells against was understated by a third"* — **is not an ancestor of `3957ba848`**, the
commit the 09-11 measurement was filed from. It reached this tree later, through the fork-closing
merge `2212d0eed`.

```
$ git merge-base --is-ancestor 0d86d6dfe 3957ba848 ; echo $?
1
```

A KS over the fabric axes is a statistic **about the homes**. So the filed 0.12798 / 0.08241 / 1.553×
are not stale readings of this world; they are correct readings of a different one.

**This is not a tolerance to be widened, and the harness does not widen it.**
`tools/settlement_per_axis_gain.py --check` refuses, names the five disagreements, and prints the
attributed cause so the next session does not re-derive it.

## What the 09-11 pre-registration asked for in advance, and the answer

§A's own §5 said, verbatim:

> *"If P1 fails on this base and the same measurement passes on the shared tree's main, the honest
> reading is that the chooser needs the richer home — which would make promoting those 21 commits
> the higher-value work, and I will say so rather than fit the design to the base I happen to be on."*

That question is now answerable, and it resolves in the *undramatic* direction: **the chooser does
not need the richer home, and it does slightly better on it.** 1.661× against 1.553×. P1a's band
[1.2×, 2.0×] holds on the current base, and §B's ≥1.25× holds on it too.

**The obvious reading of that is wrong and is worth stating.** The chooser did not get better in
absolute terms — *both* arms sit closer to the population on the fitted-joint stock (cull 0.12798 →
0.09765, chosen 0.08241 → 0.05878). The richer home stock made the whole problem easier. Only the
*relative* advantage grew, and it grew by less than the base change moved either arm.

**A second filed figure moved with it.** §A's P2 was graded against "109 distinct fabric vectors in
the population". On this base there are **105**. P2's verdict (FAILS, 59 of a ceiling of 109) is not
overturned by that, but its denominator is no longer the one on the page.

## P1b's verdict, and the two things that are not the same claim

**Against §A's filed evidence: UNGRADEABLE.** Not waved through, and not graded on a substitute.
The pre-registration committed to this outcome before the numbers were seen, and it is honoured
literally. Getting a verdict against the filed evidence means re-running at `3957ba848` — which
would grade a prediction against a world the company no longer lives in, and is why it was not done
here rather than being left as an oversight.

**On the shipped base, as a separate and clearly-named claim, the profile is decisive:**

| axis | KS cull | KS chosen | gain `g = cull/chosen` |
|---|---|---|---|
| `raw_infiltration_ach` | 0.09765 | 0.02151 | **4.540×** |
| `floor_area_m2` | 0.04626 | 0.01753 | **2.639×** |
| `fabric_w_per_k` | 0.08061 | 0.05878 | **1.371×** |
| `customer_years` (cost) | 0.01080 | 0.04930 | **0.219×** |

Every fabric axis gains; the cost axis **loses by 4.6×**. On the pre-committed rule that is HOLDS,
on the three-physical-axis fabric set and on §A's named-and-existing pair alike. The profile is not
flat (spread 20.7×), so "concentrated" has a referent and the clause was falsifiable after all.

**The two rows above are in the artefact under two different keys on purpose**
(`grading_against_the_FILED_evidence`, which stays `null`, and
`profile_on_THIS_base_which_is_NOT_the_filed_one`). One key holding both is how "graded on a
substitute base" becomes "graded".

## My own predictions, graded on this base, including the one that failed

* **N1 — the fabric axes gain more than cost. HOLDS**, decisively (min fabric 1.371 vs cost 0.219).
* **N2 — `g_cost` in [0.85, 1.20], "roughly neutral, possibly slightly worse". FAILS.** Measured
  **0.219**. My reasoning was right in direction and badly wrong in magnitude: I said the systematic
  cull over a year-ordered list "should be hard to beat" on `customer_years` and predicted a
  near-draw. It is not a near-draw — the cull is *nearly perfect* there (KS 0.0108) because
  systematic-over-year-ordered is very close to a stratified draw on that axis, and the chooser
  gives up most of that to buy the fabric axes. **My kill line was on the wrong side.** I bounded
  the case where cost gains too much and left the case where cost is sacrificed unbounded, so the
  band could only fail silently in the direction it actually failed in.
* **N3 — arm B's worst axis is a fabric axis. HOLDS** — `fabric_w_per_k` (0.05878), which is the
  column the 0.08241 that graded P1a belonged to on the old base.
* **N4 — spread ≥ 1.5×. HOLDS**, 20.7×.
* **N5 — the year-group repair costs the cost axis and pays a fabric axis. HOLDS, narrowly and
  less interestingly than I expected.** Pre-repair (`groups=None`) `g_cost` is 0.2249 against the
  shipped 0.2191, and `floor_area_m2` gains 2.571 pre-repair against 2.639 shipped. Both moves are
  in the predicted direction and both are small — the repair that fixed a **+84.9%** year
  reconstruction error costs about **2.6%** of the cost axis's KS gain. That is the repair being
  nearly free, which is a better result for it than a large effect would have been.

## What this does NOT claim

* It does not claim the filed 09-11 result was wrong. It was right about its own base, and the
  conclusion it drew — the chooser beats the cull — holds on this base too, by more.
* It does not re-grade P1a, P2 or any other §A or §B prediction. P2's denominator is flagged, not
  re-graded; doing that properly is the same re-run question and it is named below rather than
  half-done here.
* It does not claim per-axis KS is the right instrument for "concentration" in general. It is the
  instrument P1b's own wording implies.
* It changes no selection rule, no axis list and no constant. Every arm here is a patch applied
  inside the harness and reverted in a `finally`; the shipped path is what was measured.

## What is next, in order

1. **Every filed figure from `3957ba848` that is a statistic about the homes is now suspect, and
   nothing in the tree says so.** This found two (worst-axis KS, distinct fabric vectors) by going
   after a third. The 09-11 result file is still on the page presenting 1.553× and 109 as current.
   The cheap, correct move is a note *beside those numbers* naming their base — not a re-run.
2. **The band-on-one-side habit that N2 failed by.** I wrote a two-sided band and a one-sided kill
   line, so the prediction could only be refuted in the direction I already doubted. Worth checking
   whether the other live pre-registrations do the same thing; it is the cheapest possible audit
   and it is about the shape of the prediction, not its subject.
