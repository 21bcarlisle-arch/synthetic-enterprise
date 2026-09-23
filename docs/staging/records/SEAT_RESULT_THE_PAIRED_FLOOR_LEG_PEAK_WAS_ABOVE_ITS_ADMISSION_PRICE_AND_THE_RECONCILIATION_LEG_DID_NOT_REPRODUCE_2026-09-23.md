**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — predictions 5 and 6 graded, both REFUTED, and one of them inverts the remedy the item asked for

*Lane 0 delivery, 2026-09-23 ~20:00Z. Against
`docs/staging/records/SEAT_PREREG_THE_PAIRED_SIZE_TERM_FLOOR_2026-09-23.md` (predictions 1–5) and
`docs/staging/records/SEAT_RESULT_THE_PAIRED_FLOOR_NOW_SPAWNS_ONE_LEG_PER_PROCESS_..._2026-09-23.md`
(prediction 6). Drawn item:
`grade-the-paired-size-term-floor-against-its-five-pre-registered-predictions`.*

## State of the run, measured not assumed

The family is **alive**: unit `longjob-size-term-paired-floor-legs-20260923`, active 3h 36m,
orchestrator PID 3794281 holding 124 MB (which is the split working), child PID 482737 on
`--leg-only 5102 --configuration blind`. Four legs of fourteen are on disk:

| shard | peak_rss_mb | elapsed_s |
|---|---|---|
| `leg_base_blind` | 7,989.7 | 3,138.1 |
| `leg_base_seeing` | 8,094.1 | 3,092.4 |
| `leg_5101_blind` | 8,291.8 | 3,208.1 |
| `leg_5101_seeing` | 8,280.6 | 3,290.3 |

~53 min per leg, so the remaining ten legs are ~9h. **Predictions 1–4 are not gradeable and are not
graded here** — they need the seed family and one seed pair exists. This record grades only what the
completed legs can answer, which is 5 and 6.

## Prediction 6 — REFUTED, and refuted in the direction that kills

> *"A single leg's `VmHWM` will come in materially below 7,878 MB — I predict 6,000–7,000 MB."*

Observed range **7,989.7–8,291.8 MB** over four legs. Not one is in the predicted band, and not one
is below 7,878. Every leg exceeded `PAIRED_FLOOR_LEG_PEAK_MB` (7,800) — **the admission price it was
let through on** — by up to 491.8 MB.

**The item's instruction inverts.** It said: *"If the observed leg peak is materially below 7,800,
LOWER `PAIRED_FLOOR_LEG_PEAK_MB` to the measurement."* The measurement went the other way, so the
constant has been **raised to 8,400**, not lowered.

**Why the bound was wrong, which is the reusable part.** `PAIRED_FLOOR_LEG_PEAK_MB` was set to the
pair's peak on the argument *a leg is contained in the pair that ran it, so the pair's peak bounds a
leg's from above*. **The containment step is valid. Its input was not.** The 7,878 MB it bounded
from was the `MemoryPeak` of a pair the OOM killer took at 1h 26m — so that pair never reached its
own peak, and the constant's own comment said in as many words that 7,878 was a **floor** on the
pair's requirement. A floor cannot bound anything from above. The tree therefore carried a refusal
threshold *below* the cost it existed to refuse, for the whole life of the split, and the error
read as caution the entire time.

**8,400 and not 8,292**, because what OOM-kills is the cgroup, not the process: the same unit's
`MemoryPeak` is 8,767,266,816 B = **8,361.1 MB**, 69.3 MB above the largest leg inside it, since the
orchestrator shares that cgroup. The census deliberately does not count the orchestrator as a leg,
so folding its footprint into the leg's price is the only place this arithmetic can count it at all.
8,400 is the first round hundred above the figure that does the killing.

**The rounding goes UP here where its siblings round DOWN, and that is a difference in evidence, not
a change of convention.** 6,400 and 7,800 were rounded down from OOM-killed runs — already
underestimates, where the stated worry was refusing runs that would have finished. This is the first
figure taken from processes that ran to completion, so it is a true peak; the residual uncertainty
runs the other way (max over 4 legs of a 14-leg family). The first three rose monotonically and the
fourth did not, so this is spread around ~8,100–8,300 and **not** a leak climbing with leg index.

### The control that should have caught it, and why it could not

`leg_peak_rss_mb.how_to_read_this` had exactly one remedy in it: *if the observation is materially
BELOW the price, the bound is loose and should be lowered.* That is the flattering half. The
instrument built to replace the bound with a measurement was **structurally unable to state the one
outcome that occurred**, and a field that cannot express an answer agrees with every other one.
Repaired: the reading now carries `exceeds_admission_price` and a `verdict` stated over all three
states (UNDER-PRICED / LOOSE / PRICED), with a control asserting all three over one population and
their distinctness. Mutation-proven both ways — inverting the comparison and wedging the verdict on
the flattering state each turn it red.

### A pre-existing RED on the trunk, found on the way

`tests/tools/test_value_cycle_ab_noise_floor.py::test_the_leg_census_sees_a_paired_floor_leg_and_prices_it_at_its_own_peak`
was **failing at `origin/main`** before this work. `a35c798a2` moved the paired row of
`FLOOR_LEG_SHAPES` from `--seeds` to `--leg-only` and made the orchestrator deliberately invisible;
this fixture kept spawning a `--seeds` argv and asserting it was seen — i.e. it asserted the exact
behaviour its sibling `test_the_census_sees_a_leg_and_does_not_see_its_orchestrator` asserts must
**not** happen. Two controls over one census, disagreeing, is how long a red can sit unread. Fixed,
and its `pytest.approx(7800.0)` literal replaced by the constant: a control keyed to today's answer
goes red when the number becomes *more* honest.

## Prediction 5 — REFUTED on one leg of two, and the prereg's own inference from that is WRONG

> *"The blind leg at the base (unpatched) roll will reproduce £14,074 and the seeing leg £13,440,
> within rounding. If it does not, my rebind is not the switch the commit made."*

| | published `fc390b918` | reconciliation leg | gap |
|---|---|---|---|
| blind net margin advantage | £14,074 | **£10,387.84** | −£3,686 (26%) |
| seeing net margin advantage | £13,440 | **£13,509.40** | +£69 (0.5%) |
| the move | **−£634** | **+£3,121.56** | sign flipped |

The **seeing** leg reproduces. The **blind** leg does not.

**The prereg's stated consequence does not follow, and I am correcting it beside the claim rather
than over it.** `fc390b918`'s only functional change to `company/crm/churn_model.py` is the size
term itself — the diff, stripped of comments, deletes one line and adds the guarded block:

```
-    p = base_rate + effective_rate_sensitivity * own_move_pct - tenure_discount + ...
+    if segment == "resi" and annual_consumption_kwh > 0 and size_reference_kwh > 0:
+        size_scale = min(annual_consumption_kwh / size_reference_kwh, MAX_SIZE_SCALE)
+    else:
+        size_scale = 1.0
+    p = (base_rate + effective_rate_sensitivity * size_scale * own_move_pct - tenure_discount + ...
```

At `size_scale = 1.0` the new expression is **algebraically identical to the deleted one**. So
zeroing `SIZE_REFERENCE_KWH_ELEC/GAS` is an exact behavioural revert of the commit within that
module, and the rebind **is** the switch. The instrument stands; the failure to reproduce is not a
defect in it. This correction runs in the flattering direction, which is why the diff is quoted
rather than asserted.

The witnesses confirm the rebind bit, per leg, as designed: blind `size_term_reached_calls` 5,322
with `size_term_distinct_scales` **0**; seeing 5,718 calls with **124** distinct scales over
[0.116, 11.289] (the raw pre-cap ratios; `MAX_SIZE_SCALE = 4.0` clips downstream).

**What I cannot yet say, and will not say.** There are **32 commits** between `fc390b918` and
`a35c798a2`, the run's base. More than one thing changed, so the £3,686 is **not attributable** from
here. What is odd and worth stating plainly: a common tree drift should move both legs, and this
moved the blind reading 26% while moving the seeing reading 0.5%. That is an *interaction* — something
that landed in those 32 commits matters much more when the size term is off — or the published blind
figure was never comparable to this tree. I cannot distinguish them with what is on disk.

**The one-variable control, pre-registered and deliberately NOT run:** re-run the blind leg at
`fc390b918` itself and compare to £14,074. If it reproduces there, the cause is tree drift in the 32
commits and the published table's blind column is stale; if it does not, the cause is in the rebind
or the base roll. **I predict it reproduces £14,074 at `fc390b918` (confidence: moderate).** Not run
because it costs ~53 min of an 8.4 GB leg beside a family already holding one, and the family
finishing is worth more than this attribution. Filed as the next control, not as a conclusion.

### What this does to the £634 the item is about

It does **not** close it, and it changes what the family can claim. The running instrument measures
the contrast *"`SIZE_REFERENCE_*` zeroed vs not"* — a genuinely cleaner one-variable switch than the
published comparison, which moved a whole commit. But the reconciliation leg says that contrast's
base reading is **+£3,122**, not −£634, and of **opposite sign**. So the family will floor a
cleanly-defined quantity that is not arithmetically the published move. That strengthens rather than
weakens `fc390b918`'s original refusal to call −£634 a change: two defensible readings of the same
contrast disagree in sign before any noise floor is applied.

Gross margin, for the record and at n=1: published +£21,450, reconciliation **+£28,680** — same
sign, 34% larger. Prediction 2 is *not* graded on that; it needs the family.

## A named residual, measured and not fixed

The census prices the leg and deliberately not its orchestrator. Measured, the orchestrator is
124 MB resident and the cgroup peak exceeds the largest leg by 69.3 MB. Folding that into the leg's
price (as 8,400 does) covers it for a single family; it would under-price two families sharing a
guest by one orchestrator. Left as a named gap rather than a second constant — it is 0.3% of a
24 GB guest, and a constant minted to carry it would be a number picked because a number was
available.

## What is outstanding

Predictions 1–4, which need the ten remaining legs (~9h). The artefact rebuilds after every pair, so
a killed run leaves usable seeds. Prediction 3 is still the one worth being wrong about.
