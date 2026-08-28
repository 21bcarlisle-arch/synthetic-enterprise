**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `B10_competitor_switching_response`

# The defending market costs every arm the same, the headline reversal was not the chase, and my pre-registered reading was wrong

The chase-off counterfactual finished. It answers the question yesterday's instrument could not
resolve, and it refutes the inference I filed four hours earlier in
`WORKER_PREREGISTRATION_WHAT_THE_CHASE_OFF_RUN_MUST_SHOW_2026-08-28` — which is why that document
was committed (`ad8a730e2`) and pushed before this run finished.

## The clean comparison

Identical tree, identical book, identical seeds. Exactly one input differs: `chase_per_quarter`,
supplied through a scratch curriculum file so the committed
`docs/design/COMPETITOR_AGGRESSION.yaml` is untouched and the two arms differ by a declared
parameter rather than a working-tree state.

| arm | chase ON | chase OFF | **the chase costs** | churned ON | churned OFF |
|---|---|---|---|---|---|
| control (flat rules) | £159,423.50 | £162,447.87 | **−£3,024.38** | 35 | 29 |
| value arm (per-customer) | £154,699.49 | £157,913.20 | **−£3,213.71** | 46 | 39 |
| level arm (flat @ £44.50) | £164,326.41 | £167,543.06 | **−£3,216.65** | 38 | 31 |

**The world now presses, and it presses on everyone.** Three different pricing policies, three
tolls within £192 of each other, and six or seven accounts taken from each. That internal
agreement across three independent policies is the strongest thing in this result: it is not one
number that could be noise, it is the same number three times.

## What that makes the defending market: a LEVEL effect, not a SELECTION effect

| | chase ON | chase OFF | moved by |
|---|---|---|---|
| value advantage vs flat rules | −£4,724.01 | −£4,535.02 | +£188.99 |
| level advantage vs flat rules | £4,902.91 | £5,094.90 | +£191.99 |
| **selection** | **−£9,626.92** | **−£9,629.92** | **−£3.00** |

**Selection moved by three pounds out of nine thousand six hundred.** The rival that defends does
not differentially punish per-customer pricing on this book — it takes a roughly equal toll from
the flat rule, the per-customer arm and the flat-at-level arm alike.

The differential churn roster says the same thing at the account level: the accounts that leave
under the value arm and not under the control are **the same ten in both worlds**, with the chase
adding exactly one (`PROS-2022-0009`). Eleven differential accounts with the chase on, ten with it
off.

## My pre-registered prediction, scored honestly

| # | prediction | outcome |
|---|---|---|
| 1 | value-arm churn falls back toward 39 | **HOLDS** — 46 → 39, exactly |
| 2 | control stays near £159,423 | **FAILS** — £162,448, moved +£3,024 |
| 3 | value advantage returns positive | **does not hold** — −£4,724 → −£4,535 |
| 4 | level arm barely moves | **fails** — +£3,217 |

Predictions 2 and 4 failed **in the same direction and for the same reason**, and that reason is
the finding: I predicted the chase would hit the value arm specifically, because that is the arm
that prices high and the mechanism is one-sided. It hits everything.

**Where the reasoning went wrong, stated so the class is visible.** I inferred from the 07:36 →
10:47 churn deltas — control 36→35, level 38→38, value 39→46 — that only the value arm was
affected, and concluded the chase explained it. That inference compared two runs on **different
trees** with **two things changed at once**, and it was exactly the shape this project files
against itself: reading a difference-of-differences across an uncontrolled variable because the
interesting explanation was available. The controlled comparison was one run away and I should
have declined to infer until it existed. Filing the prediction first is what made the error
correctable instead of invisible.

## The headline reversal is NOT explained by the chase, and I cannot yet say what does explain it

With the chase **off**, on the current tree, the value arm still **loses £4,535** to flat rules.
This morning's published run had it winning by £4,668. Turning the defending market off does not
bring the old result back, so the reversal came from the other thing that changed.

The measurement, stated precisely for whoever owns that change:

| arm | 07:36 (other tree) | chase OFF (current tree) | difference |
|---|---|---|---|
| control | £153,244.79 | £162,447.87 | **+£9,203.08** |
| value arm | £157,913.200761 | £157,913.200761 | **exactly zero** |
| level arm | £158,484.58 | £167,543.06 | **+£9,058.48** |

**The value arm reproduces to twelve significant figures and the other two do not.** At that
precision this is not coincidence: whatever differs between the two trees leaves the value arm's
result bit-identical while moving the control and level arms by about £9.1k each.

The candidate is the uncommitted `simulation/settlement_clocks.py` +
`refresh_settlement_scalars`, which re-derives `total_net_gbp` after the bad-debt and
debt-recovery mutations — the exact field every figure here is read from, and whose own note puts
the discrepancy it repairs at £39,962.17. **This finding does not claim that.** An arm-selective
effect is not what a scalar re-derivation obviously produces, and the lane that owns the change
can test it in minutes where I would need another 35-minute run. What is handed over is the
number, the arm that is invariant, and the reproduction.

## B10 stays at level 2, and this says exactly what L3 still needs

This is a genuine coupled-triad *half*: the world can now press, the company was run against it,
and the effect is measurable and consistent — **which is the thing yesterday's 17-binary-decision
instrument could not deliver at all**
(`WORKER_FINDING_THE_DEFENDING_MARKET_IS_UNMEASURABLE_ON_SEVENTEEN_DECISIONS`). Money is
continuous and three arms agreed.

**What is missing for L3 is the gap, not the effect.** The COUPLED TRIAD requires the company's
BELIEF measured against the world's truth. This run measures what the world did to the P&L; it
does not measure what the company thought would happen. The company's churn model carries no
competitor term at all, so its belief about those six or seven accounts is knowably uninformed —
but "knowably uninformed" is an argument, and the atom needs a number.

**The cheapest path, and it needs no new instrument:** `tools/run_price_ladder.py` already
computes `world_curve_vs_belief` per decision. Run the ladder chase-on/chase-off and read the
BELIEF leg, which is unaffected by the chase by construction, against the world leg, which is
not. The difference between those two differences is the gap, and it is per-decision rather than
per-book.

## WORK THIS CREATES

1. **`B10` → L3**: the ladder pair for the belief-vs-truth gap, per the paragraph above.
2. **Hand the £9,203 / £9,058 / exactly-zero pattern to the settlement-clocks lane.** It is their
   change and their test; the reproduction is in this document.
3. **The noise floor is now two worlds stale**, not merely one clock
   (`WORKER_FINDING_THE_ERROR_BAR_ON_THE_LIVE_HEADLINE_IS_MEASURED_ON_THE_SUPERSEDED_CLOCK_2026-08-28`,
   update section). Re-running it costs ~105 minutes and should follow (2), not precede it.
4. **Seed replication on this comparison.** Three arms agreeing is internal replication across
   policies, not across draws. One seed pair would put an error bar on the −£3.0k.

## Reproducing it

The counterfactual curriculum is committed as `docs/observability/aggression_chase_off.yaml` and the
result as `docs/observability/value_cycle_ab_chase_off_2026-08-28.json`. The harness is reproduced
here **verbatim rather than committed as a module**: a one-off experiment wrapper checked into
`tools/` would be born an orphan needing a disposition ruling, and checked into `docs/` would be a
`.py` nothing imports. The text is the artefact.

```python
"""Run the three-arm A/B with the rival's chase switched OFF, without touching the tree.

WHY A WRAPPER AND NOT AN EDIT. `docs/design/COMPETITOR_AGGRESSION.yaml` is the director's
curriculum surface and it is COMMITTED. Editing it to run a counterfactual would make the
comparison's two arms differ by a working-tree state rather than by a declared parameter, and
would leave the repo briefly holding a curriculum nobody chose. `aggression()` reads
`AGGRESSION_PATH` at CALL time, so pointing the module constant at a scratch file before the run
changes exactly one input and nothing else.

The chase-ON arm is the run already written to
docs/observability/value_cycle_ab_s1_three_arm.json at 2026-08-28T10:47:24Z, on this same tree.
"""
import pathlib
import sys

sys.path.insert(0, "/home/rich/synthetic-enterprise")

from simulation import competitor_reference

OFF = pathlib.Path(
    "/tmp/claude-1000/-/29f540c9-c503-4cb4-8dc8-7e6d21848896/scratchpad/aggression_chase_off.yaml")
competitor_reference.AGGRESSION_PATH = OFF
assert competitor_reference.aggression()["chase_per_quarter"] == 0.0, (
    "the override did not take -- refusing to run a comparison whose only differing parameter "
    "did not actually change")
print("chase_per_quarter =", competitor_reference.aggression()["chase_per_quarter"])

from tools.run_value_cycle_ab import main  # noqa: E402

raise SystemExit(main([
    "--level-arm", "--out",
    "/tmp/claude-1000/-/29f540c9-c503-4cb4-8dc8-7e6d21848896/scratchpad/ab_chase_off_three_arm.json",
]))
```

The `assert` is the point: a comparison whose only differing parameter silently failed to change
would report the chase as costing nothing, which is the fail-silent shape that would have made this
whole run a confident null.

## CORRECTION 2026-08-28 — "the baseline arm now reproduces the published run" was circular

This document and the seat note say the 10:47 re-run resolved a divergence because its control arm
reproduced the published run to 6.75×10⁻⁹. **A concurrent lane showed the check is not independent,
and they are right: `docs/reports/run_output_latest.json` is written by
`simulation.run_phase4c_on_phase2b`, the same entry point the A/B calls once per arm.** The file my
run "reproduced" is the file my run had just written. I withdraw the inference; it appears here, in
a commit message and in two NTFY messages, and this is the correction of record.

**Their premise needed correcting in turn, and it changes the picture.** They report £1,529,289 as
"the figure the front door carries". Fetched live: `https://poesys.net/data/dashboard.json` publishes
**£153,244.79**. So the site never carried £1.53M, and what I called a "divergence resolved" this
morning was a gap between the A/B artefact and a *third* file that the site does not render.

**What survives untouched:** everything in the chase-on/chase-off comparison above. That comparison
is internal to two runs on one tree, differing in one declared parameter, and it never appealed to
the published run at all. The −£3.0k per arm, the 6–7 accounts, and the £3-out-of-£9,627 selection
move stand exactly as measured.

## Still live
