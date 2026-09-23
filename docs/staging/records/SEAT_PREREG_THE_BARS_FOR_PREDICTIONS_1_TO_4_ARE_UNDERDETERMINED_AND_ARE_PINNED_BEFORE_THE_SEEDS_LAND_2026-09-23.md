**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION AMENDMENT — the bars for predictions 1–4 are underdetermined, and are pinned here before the seeds land

*Lane 0 delivery, 2026-09-23T19:45Z. Drawn item:
`grade-the-paired-size-term-floor-predictions-1-to-4-when-the-family-closes`. Amends
`SEAT_PREREG_THE_PAIRED_SIZE_TERM_FLOOR_2026-09-23.md`.*

**What I read before writing this, and what I did not.** The reconciliation (base) pair only —
already graded and landed in `b1b3cb922`. **I have not read `leg_5101_blind.json` or
`leg_5101_seeing.json`**, the one seeded pair that exists, and no seeded difference appears
anywhere below. The rules registered here are therefore still predictions and not descriptions.
That is the whole reason this is being written now rather than in nine hours.

## The premise is NOT spent, and the duplicate claim is this same item

The draw flagged all three cited commits as ancestors of `origin/main` and one live rival claim.
Both check out as non-blocking:

- `b1b3cb922` graded **predictions 5 and 6 only**, and says so in its own message: *"Predictions 1–4
  need the ten remaining legs (~9h) and are NOT graded. The family is alive."* Predictions 1–4 are
  untouched anywhere in the tree.
- The "other" live claim is this very id in `.seat_work_in_hand.json` — the same piece of work under
  the same name, not a second one. No disposition is owed; this is the held claim working.

## The family has NOT closed, and it cannot close inside this turn

Measured at **2026-09-23T19:31Z**:

| | |
|---|---|
| unit | `longjob-size-term-paired-floor-legs-20260923`, `ActiveState=active` |
| seeds | **5101–5106 — six**, per the unit's own `ExecStart` |
| legs | 14 = reconciliation pair + 6 seeded pairs |
| shards on disk | **4** — `base_blind`, `base_seeing`, `5101_blind`, `5101_seeing` |
| in flight | leg 5102 blind, PID 482737, 42 min into ~53 |
| remaining | ~10 legs ≈ **8.8 h**, closing ≈ 2026-09-24T04:20Z |

One seeded pair is one reading, not a floor. The tool already refuses to summarise below two pairs,
in as many words. **Predictions 1–4 remain ungraded and nothing below grades them.**

The item's own clock was an hour fast: it read "20:35Z" from a **BST** wall clock, so the ~9 h it
quoted was already right but dated from 19:35Z, not 20:35Z. Noted so the next reader does not
conclude the run lost an hour.

## The three defects, all knowable now, all outcome-changing

The instrument is already built — `summarise()` carries the paired mean, sd, sem,
`distance_to_a_sign`, `seeds_positive` and `sign_is_unanimous`. What is missing is not code. It is
that **three of the four bars those numbers get compared against are not determined by the
pre-registration that declared them.** Left alone, each would be settled after the answer was
visible, which is exactly what a pre-registration exists to prevent.

### 1. Prediction 3's bar is a factor of 2.1 wide, and prediction 3 is the one worth being wrong about

The prereg declares a population and a formula, then quotes a range the formula does not produce
from that population:

> *"Read off the carried columns, that is £1,457–£3,453 of standard deviation across the `all`-mode
> families."* … *"`sd(d_net) < √2 × sd(VA)` on the marginal families, i.e. under about
> £3,000–£4,900."*

**There is no carried column.** No artefact in `docs/observability/` holds a `value_advantage_gbp`
standard deviation. The figure exists only as per-seed values under `seeds`, from which an sd must
be computed. Computing it over the 16 `all`-mode families (every `*noise_floor*.json` that is not
`except_` or `only_`):

- **max = £3,452.97** (`next12_20260917`, n=12) — reproduces the quoted 3,453 exactly.
- **min = £990.45** (`20260829`, n=3), with £991.46 (`20260903`) beside it.
- £1,457.33 (`20260908b`, `20260909`) **is a real family sd but is not the minimum.** Two `all`
  families sit below it.

So the quoted lower end depends on an exclusion rule the prereg never states. There is a defensible
one available — `20260829` is the floor the 08-31 rerun explicitly superseded for being measured
before the market could defend — but it is not written down, and it is not the only choice.

Carried through `√2 × sd`, prediction 3's bar is any of:

| lower end of bar | where it comes from |
|---|---|
| **£1,400.7** | √2 × £990.45 — the stated population, no exclusions |
| **£2,061.0** | √2 × £1,457.33 — the quoted floor, formula applied |
| **£3,000** | as written in the prereg — **the formula produces this from no candidate** |

The upper end is sound: √2 × £3,452.97 = **£4,883.2**, which the prereg rounded to £4,900.

**A factor of 2.14 between the loosest and tightest lower bar, and the loosest is the one written
down.** The marginal families' own sds land inside that gap repeatedly. If `sd(d_net)` comes in
anywhere in £1,401–£3,000 — entirely plausible — prediction 3 is **held** under the prose and
**refuted** under its own declared arithmetic. This is the project's named recurring shape: a bar
whose value is chosen, in effect, after the answer is known.

**REGISTERED RULE, prediction 3.** Grade against the whole stated population and report the verdict
at both ends. No single lower bar is selected, because selecting one now is indistinguishable from
selecting it later:

- `sd(d_net) < £1,400.7` → **held under every reading.**
- `sd(d_net) > £4,883.2` → **refuted under every reading**, and the paired ruler is decorative: the
  finding the prereg pre-committed to.
- between → **the verdict depends on which ruler, and that is published as the answer**, with all
  three candidate bars beside it. It is not resolved by picking one.

### 2. Prediction 4 names a denominator this family will never produce

> *"I predict at least 3 of any 10 seeds flip the sign of the net-margin move."*

**The family is six seeds.** There is no "any 10". Worse, at n=6 the claim is not merely awkward to
restate — it is untestable. The 95% Clopper–Pearson interval on the sign-flip rate:

| observed | rate | 95% CI |
|---|---|---|
| 1/6 | 0.167 | [0.004, 0.641] |
| 2/6 | 0.333 | [0.043, 0.777] |
| 3/6 | 0.500 | [0.118, 0.882] |

Every one of those intervals **contains 0.30**. No outcome this family can produce distinguishes
"at least 30% flip" from its negation. A pre-registered count predicts the instrument, not the
world, and this one predicted an instrument nobody built.

There is a second, independent hole: **"flip the sign" names no reference.** Relative to the
published −£634? To the family's own mean? To the base leg? The prereg implicitly meant the
published −£634 — and `b1b3cb922`'s frame correction moved exactly that: the base leg's `d_net` is
**+£3,121.6**, of opposite sign to the published −£634. The reference the prediction was written
against is one this family's own reconciliation leg does not reproduce.

**REGISTERED RULE, prediction 4.** Graded **NOT TESTABLE BY THIS FAMILY**, on the n=6 power
argument above, and that is the grade — not a softened restatement at a denominator that happens to
fit. Reported beside it, as a descriptive reading and explicitly not as the prediction's verdict:
the count of the six seeds whose `d_net` sign differs from the family's own majority sign, with its
Clopper–Pearson interval. `seeds_positive` / `sign_is_unanimous` already carry it.

### 3. Prediction 2 is graded against a figure this family's base leg refutes

> *"`mean(d_gross)` should land near the published +£21,450 and be several sems from zero."*

Two clauses, and only the second is testable here. The frame correction established that the
reconciliation leg reproduces the **seeing** figure but not the **blind** one. Carried into gross
margin, the base pair gives `d_gross = +£28,680.2` against the published **+£21,450** — a gap of
**£7,230** before a single seed is drawn, and 32 commits separate `fc390b918` from this run's base,
so that gap is not attributable from here.

"Near the published +£21,450" therefore measures the 32-commit drift, not the composition claim.
The substantive claim — *the arm stopped winning by avoiding bad customers and started winning on
gross margin* — is carried entirely by the second clause.

**REGISTERED RULE, prediction 2.** Graded on **"several sems from zero"** alone, which is what the
composition claim actually asserts: held iff `distance_to_a_sign` on `gross_margin_gbp` states a
sign and that sign is positive. The distance from +£21,450 is reported as a **reconciliation
quantity**, labelled as drift, and is not part of the grade. If the sign is not stated, the
composition claim is withdrawn in the words its headline got — the prereg's own instruction, which
stands unchanged.

### Prediction 1 needs no amendment, only its arithmetic stated

> *"`mean(d_net)` will sit inside `t(n−1) × sd(d_net)/√n`. I expect `|mean(d_net)|` under £2,000 and
> `sd(d_net)` over £2,000."*

Well-formed. At n=6, `t(5, 0.975) = 2.5706`, so the bar is **`|mean(d_net)| < 1.0494 × sd(d_net)`**.
Recorded here so the grader does not recompute it against a different n or a one-sided t. The two
side-conditions (£2,000 either way) are graded as stated and separately from the bar itself.

## What this changes about the published claim, and what it does not

Nothing here touches the frame correction, which stands and must travel with any publication: **the
family floors a cleanly-defined contrast that is not arithmetically the published move.** The base
move is +£3,122, not −£634, and of opposite sign. A reader must not be left to assume the family
closes the £634 — it does not, and no seed budget makes it.

What this adds is that **two of the four bars were loose enough to have decided their own verdicts**,
and one prediction was untestable from the moment it was written. Pinning them costs nothing now and
would have been unrecoverable in nine hours.

## DO NOT DRAW BEFORE 2026-09-24T04:20Z

The grading of predictions 1–4 cannot start until the 14th shard lands. Drawing this item again
before then buys another invocation re-deriving that the family is still running. When it does
close, the grader's job is mechanical and is fully specified above:

1. Confirm 14 shards, then re-run aggregation over them — `python3 -m tools.size_term_paired_floor
   --seeds 5101,5102,5103,5104,5105,5106` in `/var/tmp/se-floorrun-paired-20260923`. Completed
   shards are reused; nothing re-runs.
2. Grade 1, 2, 3, 4 by the rules registered above, **without reopening them.**
3. Publish with the frame correction attached.

**One thing the grader must check first.** That worktree is locked at `a35c798a2`, which predates
`b1b3cb922`. Its aggregation is the older code. Check the artefact's `producing_commit` before
trusting any field this amendment refers to, and re-run aggregation from a HEAD extract over the
same shard directory if they differ. The shards are leg outputs and are unaffected; only the
summary is.
