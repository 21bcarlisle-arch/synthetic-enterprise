**Severity:** RECORD · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`

# Pre-registration: the 18-seed re-run at HEAD, and the five things it can refute

**Filed 2026-09-25T03:31Z, BEFORE the first leg finished.** The run is in flight; nothing below is
known. Predictions filed after an answer are not predictions, so the bars are here and the result
will be written beside them whether it agrees or not.

## Why a re-run at all — the item's own instruction is half impossible

The drawn item says *"re-fold **or** re-run the SERVED noise-floor family so its seed rows carry
`scored_decisions`"*. **Re-folding cannot do it, and this is measured, not argued.** The served
family is `docs/observability/value_cycle_ab_s1_noise_floor_folded18_single_arm_20260917.json`; it
is a fold of two runs, and both of them carry **zero** rosters:

| member | rows | rows carrying `scored_decisions` |
|---|---|---|
| `value_cycle_ab_s1_noise_floor_20260910.json` | 9 | **0** |
| `value_cycle_ab_s1_noise_floor_20260910b.json` | 9 | **0** |

`scored_decisions` arrived on the seed row on 2026-09-19, nine days after those runs. A fold can
only pool what its members recorded, so no re-fold of any family now on disk can produce a roster
that was never written. Of the 23 noise-floor artefacts under `docs/observability/`, **exactly one**
carries rosters at all — `..._five_seed_head_20260924.json`, 5 seeds — and it is not the served
family and is not over the served seeds.

So the route is a re-run, and it is running: unit `longjob-floor18-head-rosters-20260925`, worktree
`/var/tmp/se-floor18-head-20260925` (locked, detached at `ba9bc6733`), six legs of three seeds
serially, then folded. Serial because `FLOOR_RUN_PEAK_MB` is 6,400 and that number is a **floor** on
the requirement taken from an OOM kill — two concurrent legs do not fit this guest, and the
2026-09-03 and 2026-09-23 kills are what established it.

## The seeds are the served family's own, and that is the whole design

`11111,22222,33333,44444,55555,66666,77777,88888,99999` and the same six-digit set. Re-running the
**same seeds** at HEAD is what makes the result checkable: every one of the 18 is shared with the
served artefact, and `run_value_cycle_ab --fold` refuses unless every shared seed returns the same
`selection_gbp` under both trees. **The tool is the oracle, not my reading of it** — the job's final
step folds the new family with the served one and records the exit code to
`shards/agreement_fold_rc.txt`.

## P1 — HEAD reproduces all 18 residuals

The fold of new-plus-served **succeeds** (rc 0). Reasoning: the world digest is `39a192ce04c1eda8`
on the served family, on both its members, and on the 2026-09-24 HEAD run — so the world has not
moved across the code that has. **Falsifier:** the fold refuses naming a seed. That refusal is not a
nuisance, it is a finding of its own class — it would mean the code between 2026-09-10 and HEAD
moved the published figure, and the served family could then not be replaced by this one without
changing what the page claims.

## P2 — the count becomes EXACT

18 of 18 rows carry `scored_decisions` and `priced_decision_fingerprint`, so
`draws_the_spread_is_entitled_to` is a number and not `None`. This is close to mechanical — the
producer writes both unconditionally at HEAD — and it is stated anyway because it is the entire
premise of the piece. **Falsifier:** any row without a roster.

## P3 — the exact count lands inside the published bound

`15 <= exact <= 18`. **Falsifier:** outside it. That would refute the residual floor itself, which
is published as a floor derived from the contrapositive of a measured coextension, not as a proof.

## P4 — the exact count is 15, not 16, 17 or 18

The served family returns **15 distinct residuals over 18 seeds**: `-3308.154399` twice and
`620.925008` three times. The coextension measured on the five-seed family (ten pairs, no exceptions
in either direction) says a pinned residual and an unchanged decision set go together, so I predict
the fingerprints group exactly as the residuals do: **exact == 15**.

**Falsifier, and it is the one I most expect to be wrong:** `exact > 15`, meaning two genuinely
distinct decision sets returned one residual to fifteen digits. That is possible — the residual is a
sum over ~20 priced renewals and two different sets can cancel to the same total — and it would mean
the residual floor is a floor and nothing more, exactly as it is labelled. `exact == 18` would say
the floor and the truth part company completely on this family.

## P5 — the regrade does NOT move the sign, and here are its numbers

Computed now, from the served residuals, conditional on P1 and P4 holding (collapse by fingerprint
then equals collapse by residual):

| leg | n | mean | stdev | sem | bar t(n−1) | margin needed | sems from zero | sign |
|---|---|---|---|---|---|---|---|---|
| over seeds | 18 | −£959.78 | 1631.80 | 384.62 | 2.1098 | **£811.48** | 2.4954 | NEGATIVE |
| over draws | 15 | −£1013.98 | 1574.60 | 406.56 | 2.1448 | **£871.98** | 2.4941 | NEGATIVE |

Margin ratio **×1.0746**. `the_verdict_changed` is **False**.

Note what this predicts and what it does not. The correction here is small where the same correction
on the five-seed family was **×2.74** (£140.34 → £384.05) — because 3 of 18 seeds collapse there and
2 of 5 collapse here. So P5 is not "the correction is negligible in general"; it is "this family has
enough draws that losing three does not reach its sign". **Falsifier:** `the_verdict_changed` True,
or a margin ratio outside ×1.00–×1.15. If the sign does not survive, the page's published NEGATIVE
selection direction has been resting on counting repeated draws as fresh ones, and withdrawing it
becomes the next piece.

## What was landed BEFORE the seeds, deliberately

The reader's half, so that the run's answer reaches a page without anybody editing a sentence when
it does: `_draws_this_family_is_entitled_to` now carries
`the_leg_regraded_over_those_draws`, and `site/capabilities/index.html` renders it in three states
(sign survives / sign does not survive / cannot be graded). **On every family now on disk it renders
the third**, with the reason on the surface, and no published figure moved. Five mutations proven to
bite. Landing it first is what makes P5 a prediction about the world rather than about whether I
remember to wire it up afterwards.

**Not** `sems_to_state_a_sign(draws)`, which is what the drawn item asked for: that moves one of the
three terms a repeated draw touches and would grade a sem taken over seeds at a bar earned by draws.
`regrade_over_distinct_draws` recomputes the whole leg and already says so at length; this reads
that block rather than substituting an `n`.

## How to grade this

The first draft of this section named `fold_noise_floor_family --check`. **There is no such
flag** — the tool takes `--out` and sources and nothing else. Kept here rather than quietly
corrected, because an offered verification string that names a command in no copy is the shape that
inverts a verdict, and this one was caught by typing it. What follows was run:

```
# P1 -- the tool's own refusal is the oracle, not a reading of the numbers
cat /var/tmp/se-floor18-head-20260925/shards/agreement_fold_rc.txt

# P2, P3, P4, P5 -- verified against `..._five_seed_head_20260924.json`, which reproduces the
# fold tool's own recorded x2.74, so the grader is known to work before the family it grades exists
cd /home/rich/synthetic-enterprise && python3 - \
    /var/tmp/se-floor18-head-20260925/shards/folded18_head_20260925.json <<'GRADE'
import json, pathlib, sys
from tools.fold_noise_floor_family import _priced_decision_draws, regrade_over_distinct_draws
rows = json.loads(pathlib.Path(sys.argv[1]).read_text())["seeds"]
c, r = _priced_decision_draws(rows), regrade_over_distinct_draws(rows)
print("P2/P3/P4  exact=%s at_least=%s at_most=%s floor_holds=%s" % (
    c["draws_the_spread_is_entitled_to"], c["at_least"], c["at_most"],
    c["the_residual_floor_holds"]))
print("P5        available=%s the_verdict_changed=%s" % (r["available"],
                                                        r.get("the_verdict_changed")))
if r["available"]:
    print("          margin draws=%.2f seeds=%.2f ratio=%.4f" % (
        r["margin_required_over_draws_gbp"], r["margin_required_over_seeds_gbp"],
        r["margin_required_over_draws_gbp"] / r["margin_required_over_seeds_gbp"]))
GRADE

# is it still alive -- and this one names the subject and carries its own verdict
python3 -m background.launch_liveness --check
```

At 2026-09-25T03:40Z that last command reads
`floor18-head-rosters-20260925: RUNNING -- ActiveState=active, which is a verdict from outside the
job's own cgroup and therefore survives the kill it would report`.

The family is a WATCHED artefact once promoted onto `NOISE_FLOOR_PATH`, so its promotion is owed in
the same commit as the move. That is the blocker the 2026-09-24 finding deliberately did not pay and
this piece does.
