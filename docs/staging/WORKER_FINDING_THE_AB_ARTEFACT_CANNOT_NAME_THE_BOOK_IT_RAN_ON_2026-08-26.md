**Severity:** LATENT · **Lane:** H_harness · **Rank:** after the current delivery-lane item · **Epoch:** 3 · **Atom:** `D9_worse_than_blind_chip_is_metric_blind`

# The value-cycle A/B artefact cannot name the book it ran on

**Filed by the worker seat, 2026-08-26, while writing the resi+SME reading into
`docs/design/THE_VALUE_CYCLE_REALISED_AB.md`. QUEUED, not fixed on sight (SELF-INTERRUPT
DISCIPLINE): a second concurrent code change plus its gate run would have contended with the
in-flight suspension landing.**

## The defect

`tools/run_value_cycle_ab.py` writes an artefact carrying `arm_identity`, `control_credibility`,
`decision_shape`, `belief_vs_outcome` and the basis string for every margin figure — and
**nowhere records which segments the run served.**

```
$ grep -n "served_segments\|SE_SERVED_SEGMENTS" tools/run_value_cycle_ab.py
$   # (no output)
```

The population is read through `simulation.live_population`, which applies
`docs/design/curriculum/served_segments.json` (and the `SE_SERVED_SEGMENTS` override) at import
time. So the book is a **free variable of the run that the record of the run does not capture.**

## Why this is the finding and not a tidy-up

This is the exact mechanism of the 48-hour confusion the suspension landing closes. Three
readings were produced from this tool on 2026-08-26:

| artefact | control accounts | book | EV delta |
|---|---|---|---|
| `value_cycle_ab.json` | 172 | resi + SME + I&C | +£2,293,743 |
| `value_cycle_ab_resi.json` | 131 | resi + SME | +£10,800 |
| `value_cycle_ab_resi_only.json` | 123 | resi | +£9,759 |

**The book column is inferred from account counts and from the filenames — neither is in the
artefact.** Two of those three readings were quoted as the company's answer to its own founding
question while being about a segment the director had already ordered suspended, and no control
could fire, because the artefact had nothing to check against.

It is the R14 shape one level up: *no financial figure without its clock* — and a realised A/B's
population is as much a part of its basis as its settlement clock is. It is also FAIL-OPEN in
R15's sense: a run on the wrong book produces a clean, complete, entirely plausible artefact.

The filename is not the control. `value_cycle_ab_resi.json` in fact served resi **and SME**, so
the one piece of provenance a reader does have is actively misleading.

## What closes it

1. `run_value_cycle_ab` records `served_segments` — the resolved list, read back from
   `simulation.live_population.served_segments()` after the run rather than from the file, so it
   reports what the run USED and not what the curriculum said (independence: a tautology here
   would re-read the same source the run read).
2. It records the `SE_SERVED_SEGMENTS` override separately when set, since an env-overridden run
   and a curriculum run are different claims.
3. R15 mutation: a run with the override set to `resi` must produce an artefact whose
   `served_segments` differs from one without it — a control that cannot distinguish two books
   is the defect being closed, not a fix for it.
4. Both arms are asserted to have served the SAME book. Two arms on two books is an
   uncontrolled variable of exactly the class `arm_identity` already exists to catch, and it is
   currently unguarded on the population axis.

Existing artefacts cannot be backfilled honestly and should not be — the three above are
annotated in `docs/design/THE_VALUE_CYCLE_REALISED_AB.md` instead, which is where a reader
looks.

Archive to `docs/staging/done/` when the artefact names its own book and the mutation test
proves it can tell two books apart.
