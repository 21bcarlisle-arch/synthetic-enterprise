# WORKER FINDING — the H27 pair's published headline is measured on four events, and the door says `measured`

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-14 ~21:40 UTC, during the `H27_payment_belief_gap` 2→3 HARDEN draw (worker
tick), while regenerating `site/data/proof.json` to check that Expert Hour #30's fix had reached
the published artefact. The Hour #30 repair is unrelated to this; the regeneration is what made
the population visible.

**Class:** a fail-open on a thin population — the control publishes a confident chip on a
population small enough that one event dominates it.

**Disposition:** QUEUED, not fixed on sight (SELF-INTERRUPT DISCIPLINE). The repair touches the
`detection_measures` contract in `background/gap_metric.py`, which five metric families and every
coupled pair write through, and the right shape (a thinness caveat? an `n`-floor that refuses to
publish? a widened chip vocabulary?) is a design question, not a patch.

## Observed, with evidence

`site/data/proof.json` `coupled_gaps.pairs[5]` is this atom's own pair
(`W2_11_payment_behaviour_source` ↔ `D5_account_hierarchy_payments`), and it is a LIVE per-run
measurement — its note says so. Regenerating the door from the ledger on disk moved it, because
`proof.json` was four days stale relative to the ledger the live runs write.

**Three consecutive recorded values for one pair** (`observed-with-evidence`):

| source | value | `measured_at` |
|---|---|---|
| `site/data/proof.json` as published (pre-regeneration) | 0.083391 | 2026-08-10T09:27Z |
| `coupled_gap_ledger.json` at HEAD (`c8f4c00c5`) | 0.085938 | 2026-08-12T06:10Z |
| the ledger on disk / this regeneration | **0.031128** | 2026-08-14T21:34Z (`run_git_commit 5975a4e26`) |

**The population moved with it, and further:**

| component | 2026-08-10 publish | 2026-08-14 run | ratio |
|---|---|---|---|
| `universe_size` | 1600 | 276 | ÷5.8 |
| `truth_size` (TRUE DD failures) | 31 | **4** | ÷7.8 |
| `n_negatives` | 1451 | 257 | ÷5.6 |
| `n_false_flags` | 242 | 16 | ÷15 |
| `false_flag_rate` | 0.166782 | 0.062257 | ÷2.7 |
| headline `value` | 0.083391 | 0.031128 | ÷2.7 |

**The headline is exactly half the false-flag rate, in both runs.** `caught == truth_size` in both
(31/31 and 4/4), so `missed_failure_rate` is 0.0 both times and the D11 balanced headline is
`mean(0.0, false_flag_rate)`. Checked: 0.062257 / 2 = 0.031128 — the published value to all
sixteen figures.

**So the entire missed-failure direction rests on four events.** One missed failure in the smaller
population would make that direction 1/4 = 0.25 and the headline `mean(0.25, 0.0623)` = 0.156 —
**five times the value the door publishes today**. The same single event in the 2026-08-10
population would have moved the headline by 0.016, a fifth of its value. The instrument's
sensitivity to one event changed by 25× between two publishes, and nothing on the door says so.

**What the door renders for it:** `chip: "measured"`, `severity: "blue"`, `trend: "single"`,
`blocks_l3: false`. Per `_coupled_gaps`' own documented reading convention, blue/`measured` means
"the company has learned some, but not all, of the hidden structure (the honest steady state)".
That reading is not available from four events, and the panel has no chip that says so.

## Why this is a defect and not merely a small sample

The panel is explicitly "a CONTROL surface and must be able to FAIL (R15)", and its docstring
enumerates the ways it fails: `None` → untested/amber, `<= 0` → leak/red, `> 1` →
worse_than_blind/red, otherwise measured/blue. **Every one of those tests is on the VALUE. None is
on the POPULATION.** A gap computed over four events lands in the blue band by arithmetic, so the
one input that decides whether the value means anything cannot reach the verdict — the fail-open
shape from R15's own list, with `n` as the missing subject.

`detection_measures` does carry a vacuity guard, and it is the right idea: a population where
nothing was detected publishes `None`, not 0.0, and says why. The guard's threshold is zero. The
gap between "zero events, refuse to publish" and "four events, publish blue" is where this sits.

There is a second reading and it is worse, not better: if the population shrank because the run
got shorter, then the headline fell 63% for a reason that has nothing to do with the company's
skill — which is precisely the artefact class `tools/couple_w2_11_d5.py`'s own comment at line 842
names ("a number that moves while the thing it measures stands still is an artefact"). That
comment guards `as_of` movement. It does not guard population movement.

## What this finding does NOT claim

That 0.031128 is wrong — it is the correct arithmetic on the population it was given, and the
`missed_failure_rate: 0.0` direction is honestly disclosed in `raw_gap_is`. That the run which
produced 276 cases was misconfigured — that has not been checked and this finding does not assert
it. That the trend is real: with no measurement-history store the door reports `single` by design,
which is a documented absence, not this defect. Only that a headline whose sensitivity to one
event moved 25× between two publishes is rendered with the same confident chip as one measured on
1600, and that the panel's own R15 fail-list has no test that could catch it.

## Candidate repairs, none taken here

1. **A population term in the chip vocabulary.** `truth_size` below a stated floor → chip `thin`,
   severity amber, alongside the existing value-based chips. Cheapest, and it makes the reader's
   problem visible rather than solving it. Needs the floor to be *derived* (e.g. the `n` at which
   one event moves the headline by more than the headline) rather than picked, or it is a constant
   nobody can defend.
2. **Publish the one-event sensitivity beside the value.** It is computable from components
   already published (`1/truth_size` into the balanced mean) and needs no new measurement. This
   is the version that answers the reader's actual question.
3. **Refuse to publish below the floor**, the vacuity guard extended past zero. Strongest and the
   one to be most careful with: an instrument that goes silent when its population thins publishes
   nothing exactly when the world is most unusual, and `None` already means "untested" on this
   door, so it would collide with an existing reading.

Repair 2 is the recommendation: it weakens no control, invents no threshold, and is derived from
data the entry already carries.
