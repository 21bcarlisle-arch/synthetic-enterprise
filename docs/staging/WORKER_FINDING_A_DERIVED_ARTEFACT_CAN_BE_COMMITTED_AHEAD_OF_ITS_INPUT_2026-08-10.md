# [WORKER-FINDING] A derived artefact can be committed ahead of the input it was derived from, and the whole site lane goes red for everyone (2026-08-10)

**Found:** landing `DIRECTOR_PRIORITY_BUILD_THE_BREATHING_2026-08-10` items 1+3. Four separate
attempts were refused by `surgical_land` before the cause resolved. Every refusal was correct.

**Severity:** this is the class that kept `site/proof` red **at HEAD** for every lane, indefinitely,
while every working tree that touched it was green — so it reads as "someone else's flaky test"
from inside any single lane and never gets owned.

## Observed, with evidence

`site/data/proof.json` is DERIVED from two inputs. All three are separately committable, and the
publisher commits the derived one on a different cadence from its sources.

```
HEAD 21fcd1ed8:
  site/state/live_portfolio.json        generated_at        = 2026-07-20T05:47:26Z   (3 weeks stale)
  site/data/proof.json                  outcome_source_stamp= 2026-08-10T13:33:42Z   (derived, current)
  site/state/track_record_scorecard.json wall_clock_today   = 2026-08-09             (stale)
```

Result on a clean checkout of HEAD — **not** a working tree:

```
$ git archive HEAD | tar -x -C /tmp/headchk && cd /tmp/headchk
$ python3 -m pytest site/proof/test_predictions_ledger_can_fail.py -q
2 failed, 33 passed
E  assert '-1 day(s) old' in '<div class="pred-head">…0 day(s) old…'
```

An age of **minus one day**: `outcome_source_age_days = _day_delta(today, stamp)` where `today`
comes from the scorecard (`generate_proof_data.py:1074`) and `stamp` from the portfolio snapshot.
A derived artefact dated *after* the clock its own consumer reads by.

## Why the obvious fixes do not work

1. **"Just regenerate proof.json."** The publisher rewrites `live_portfolio.json` every few minutes.
   Captured at `16:54:03Z`, the gate saw `16:59:32Z`. Regenerating fixes the stamp and leaves the
   age wrong, because the *third* file is the one carrying the clock.
2. **"Commit the source with it."** Two of three is still incoherent. The coherent set is
   `{live_portfolio.json, track_record_scorecard.json, proof.json}` and nothing declares that.
3. **"Drop the door that's red."** `test_every_live_data_door_opts_into_the_banner` refuses a
   partial rollout — correctly. That control is working and should not be weakened.

What actually worked: **regenerate the derived artefact immediately before `surgical_land` captures
the tree**, and name all three paths in one pathspec. `surgical_land` gates the tree it captured, so
coherence at capture is sufficient — but the coherence has to be manufactured by hand, every time,
by someone who already knows which three files are coupled.

## The class

`background/derived_artefact_register.py` exists and knows about derived-artefact staleness. It does
not know that a derived artefact can be committed **ahead** of its input, which is the opposite
direction from the staleness it was built for and produces a *negative* age rather than a large one.
Related: [[feedback_untracked_build_passes_local_green]],
[[feedback_the_record_can_outrun_the_code]], `WORKER_FINDING_DERIVED_ARTEFACT_STALENESS_IS_A_WEDGE_CLASS_2026-08-09.md`.

## Proposed atom (not built — queued per SELF_INTERRUPT_DISCIPLINE)

**`OPS_derived_coherence_set`** — declare the coupled `{sources → derived}` sets once, in code; have
the pre-commit gate refuse a commit that moves a derived artefact without the sources it was derived
from (and vice versa), and have the generator refuse to emit a negative age rather than publishing
one. R15 both ways: the guard must fire on the real 2026-08-10 tree state above, and must not fire
on a coherent triple.

**Recommendation:** queue at normal priority behind the drain. It is not blocking now — the three
files landed coherent in `1edad80a5` — but the next publisher cycle that commits one without the
others re-opens it, and the failure mode is a whole-lane red that no lane owns.
