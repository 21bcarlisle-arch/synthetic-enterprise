**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS_stale_copy_refusal`

# A carried line is coincidence for a data artefact, and two of my four predictions were refuted

**Claim:** `is-partial-a-signal-for-a-data-artefact-and-which-callers-ask-the-blind-oracle`
**Pre-registered:** `docs/staging/records/SEAT_PREREGISTRATION_WHETHER_A_CARRIED_LINE_IS_EVIDENCE_OF_DERIVATION_FOR_A_DATA_ARTEFACT_2026-09-23.md`, written before any of this was measured.

## The question, and the answer

`BASE_WINS_RULES = (PREDATES, CLOCK)` excluded `PARTIAL` with this reason written at the constant:
*"`PARTIAL` says the copy carries SOME of the landing and therefore may be built on it."* That is an
argument about **derivation**, and it is only true where a shared line is unlikely to arise any
other way. For a `.py` a distinctive line is a STATEMENT. For a generated `.json` a line is a KEY
AND ITS VALUE, and two runs of one report share a line whenever the figure did not move.

**The answer is that for a data artefact the carry is coincidence, measured on the files
themselves.** So `PARTIAL` is not a vouch there, and `refresh_to_head.base_wins_rules(path)` now
admits it for `DATA_SUFFIXES` and for nothing else.

## The measurements

**Coincidence rate** = the share of one document's non-trivial, within-document-unique lines
(`_trivial()`, the rule's own filter) that also appear in a second document provably in NO
derivation relation with it — a sibling report from the same generator over different inputs.

| arm | pair | rate |
|---|---|---|
| data | `ladder_churn_factors` vs `…_continuous_satisfaction` | **20.6%** (210/1020) |
| data | `…_svt_segment_decisions` vs `…_continuous_satisfaction_svt_segment_decisions` | **24.9%** (1044/4199) |
| data | `ladder_churn_factors` vs `ladder_churn_ceiling_vs_belief` (different report shape) | 0.0% |
| `.py` | `refresh_to_head` vs `stale_copy_refusal` | 5.3% |
| `.py` | `isolate_hunks` vs `surgical_land` | 6.3% |
| `.py` | `stale_copy_refusal` vs `landing_pair` | 1.4% |
| `.py` | `generate_dashboard_data` vs `canon_drift_check` | 0.3% |

**On the two live copies directly**, rather than by borrowing a population statistic:

| copy | landing | distinctive | carried | of the carried, also in an unrelated sibling |
|---|---|---|---|---|
| `ladder_churn_factors.json` | `1939dd871` | 864 | 57 (6.6%) | **57 / 57 = 100%** |
| `…_svt_segment_decisions.json` | `1939dd871` | 4187 | 1060 (25.3%) | **1032 / 1060 = 97.4%** |

Carried lines look like `"sim_years_on_svt": 0.093,` and `"random_roll": 0.8636`. Each is a figure
that did not move between two runs. None is evidence that one document was built on the other.

## My predictions, kept beside the result

1. **Data arm >20%, `.py` control <5%.** Half right, and the bound I named is **REFUTED**: two `.py`
   pairs came in at 5.3% and 6.3%. Both are same-family modules (`refresh_to_head` *imports*
   `stale_copy_refusal`), which is the closest code analogue to "same generator" — so the honest
   reading is that the classes separate by about 4x, not that code never coincides. The <5% number
   was a guess dressed as a threshold and it had no business being one.
2. **Carried share above 30%.** **REFUTED for both** — 6.6% and 25.3%. It does not change the
   conclusion, and it is worth saying why the prediction was badly framed: a *low* carry makes the
   copy *more* clearly not the landing, so I predicted in the direction that would have made my own
   case weaker and still got the number wrong.
3. **A majority of each copy's carried lines also appear in an unrelated sibling.** **Held, and by a
   margin I did not expect** — 100% and 97.4%. This is the leg the decision rests on, because it is
   about these two files and not about a population.
4. **No control pins the `judge`-call ordering.** **Held.**

## What changed in the code

- `tools/refresh_to_head.base_wins_rules(path)` — new, carries the measurement in its docstring.
  `BASE_WINS_DATA_RULES = BASE_WINS_RULES + (PARTIAL,)`. Both `--base-wins` consultations and both
  refusal texts now ask it by PATH instead of reading the raw tuple.
- **The clock guard is untouched.** `clock_judge` reaches `PARTIAL` only through `taken_before`,
  which requires the result blob to BE the file on disk and that file's mtime to predate the landing
  commit. This admits no copy the clock has not already called older than the landing it would
  revert. The leaf-level question — what the copy supplies and drops — is still asked in the
  document's own terms by `_json_leaf_names` and is unchanged.
- **The ordering this exposes.** `PREDATES` (carries ZERO of the landing) was always admitted;
  `PARTIAL` (carries a handful by coincidence) was refused. The data copy sharing *nothing* with the
  landing was discardable and the one sharing 6.6% was protected. If the share is coincidence those
  are one copy in two states split by noise, and the door is now monotone in its own evidence.

## `judge`'s callers, censused against the suffixes they actually receive

| call site | receives | gated? |
|---|---|---|
| `stale_copy_refusal.violations` | every commit's paths | **yes** — `if suffix in READABLE else clock_judge` |
| `stale_copy_refusal.census` | every changed path | **yes** — same |
| `stale_copy_refusal.refused_to_run` | producer modules | **yes** — same |
| `refresh_to_head.judge_copy` ×2 | READABLE only | **by ORDERING, not by a guard** |

The two in `judge_copy` are safe today only because the `DATA_SUFFIXES` branch returns several
screens above them. That is a fact about one function's layout, not a control: move the branch, or
add a suffix to `DATA_SUFFIXES` without moving it, and `judge` — which returns `None` for every
suffix outside `READABLE` — silently agrees with every answer again, exactly as it did the first
time. `test_no_caller_in_this_module_asks_the_oracle_that_is_BLIND_to_the_suffix_it_holds` now pins
it with a spy over the live call path, and the spy is proven able to fire on a `.py` fixture in the
same test, because a spy that records nothing satisfies a zero-calls assertion perfectly.

## Mutation evidence

| mutation | red leg |
|---|---|
| `base_wins_rules` never admits PARTIAL (the pre-change behaviour) | `…_DATA_path_ADMITS_a_copy_that_carries_SOME…` |
| `base_wins_rules` admits PARTIAL for EVERY suffix | `…_refuses_a_copy_that_carries_SOME…` (the `.py` leg) **and** the data leg's explicit code-side assertion |
| the data branch asks `judge` again instead of `clock_judge` | the spy control **and** the data admission leg |
| the data branch keys on the SUFFIX and drops the clock condition | `…_DATA_path_still_refuses_a_copy_the_clock_has_NO_complaint_about` |
| `judge_copy` stops calling `judge` at all | the spy's reachability assertion (with 12 others) |

**One of these is weaker than it looks and I am not dressing it up.** The clock-guard mutation reds
the leg it was written for, but by `AttributeError` rather than by its assertion — the mutation
removes the binding the refusal string reads. The guard is proven load-bearing; the *message* is
not proven to be the thing that catches it. The `.py` mirror
(`test_base_wins_still_refuses_a_replacement_the_clock_has_no_complaint_about`) does assert on the
text, so the property has a clean leg one suffix class over.

## The two live copies: cleared at the door, NOT enacted

Both are `refreshable` under `--base-wins` against the shared tree's HEAD `1939dd871`, and still
`refused_supplies_names_head_lacks` by default — surveyed read-only, not written:

```
docs/reports/ladder_churn_factors.json                    default: refused → --base-wins: refreshable
docs/reports/ladder_churn_factors_svt_segment_decisions.json  default: refused → --base-wins: refreshable
```

**I did not write them, and that is a scope call rather than a result.** This turn runs in an
isolated worktree, and discarding two files in `/home/rich/synthetic-enterprise` is a write to
another writer's working tree — the one thing the isolation exists to prevent, and a genuine
collision risk against a lane mid-edit. The door is what was owed; the enactment belongs to a lane
on the shared tree, and the command is:

```
python3 -m tools.refresh_to_head --root /home/rich/synthetic-enterprise --write --base-wins \
    --slug ladder-churn-base-wins \
    docs/reports/ladder_churn_factors.json \
    docs/reports/ladder_churn_factors_svt_segment_decisions.json
```

It preserves the bytes on a `refs/preserved/refresh-to-head/` ref and runs the `git log --all -S`
recovery lookup before it writes one byte. Handed off.
