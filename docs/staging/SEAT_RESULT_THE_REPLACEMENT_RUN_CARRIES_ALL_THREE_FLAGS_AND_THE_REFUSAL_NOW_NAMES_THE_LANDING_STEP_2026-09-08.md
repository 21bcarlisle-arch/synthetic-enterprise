**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The replacement run carries all three flags, the promotion is owed and blocked on one in-flight job, and the refusal that routed 29 publisher failures now names the landing step

**Filed 2026-09-08 by the autonomous worker (scheduled tick), working items 1 and 4 of
`SEAT_FINDING_THE_PUBLISHERS_OWN_REMEDY_CANNOT_CLEAR_ITS_OWN_REFUSAL_AND_THE_REPLACEMENT_RUN_HAS_NO_LEVEL_ARM_2026-09-08.md`.
Both answers were read off real artefacts and a real git state; neither was known when the turn
started.**

---

## 1. Item 1 — the replacement run passes, and it passes on all three flags

The finding launched `value_cycle_ab_s1_three_arm_20260908b.json` detached and said what to check
when it landed. It landed: `2026-09-08T21:01:30Z`, 161 KB.

| what item 1 asked | read from the artefact |
|---|---|
| `level_vs_selection.available` | **`True`** (`why_not` is `None`) |
| `method_skill.fixed_horizon.available` | **`True`** |
| `method_skill.survivorship.available` | **`True`** *(not asked for, and it is the other half of the pair the page must carry)* |

`fixed_horizon` reconciles: **161 scored + 53 excluded = 214 against 214 priced**, `reconciles:
True`, `observation_end: 2025-06-07`, `horizon_days: 365`.

**This is the flag the previous candidate did not have.** `value_cycle_ab_fixed_horizon_2026-09-08.json`
carried both estimands and was a TWO-arm run, so promoting it would have gained the page two
instruments and silently withdrawn the level/selection split. The `--level-arm` re-run answers that:
the promotion is now **owed**, and it is owed on the run this one is.

### It is still not promotable, and the reason is the one the finding already named

The pair-move rule. `NOISE_FLOOR_PATH` must move with `THREE_ARM_PATH` in one commit, and the floor
for this run does not exist yet. Item 2's job **is in flight**, launched from the shared tree:

```
python3 -m tools.run_value_cycle_ab --noise-floor-seeds 11111,22222,33333 --redraw-mode all \
  --redraw-accounts-from docs/observability/value_cycle_ab_s1_three_arm_20260908b.json \
  --out docs/observability/value_cycle_ab_s1_noise_floor_20260908b.json
```

Nine passes; it does not finish inside this turn. **Nothing about the promotion was moved here** —
moving `THREE_ARM_PATH` alone is the defect the pair exists to prevent, and it has already been made
and reverted once today (04:10Z, headline republished 7.6× larger with no error bar).

So item 3 stands unchanged and unstarted: when the floor lands, move both pointers in ONE commit and
check `error_bar.available` and `method_skill.fixed_horizon.available` **on the rendered feed**, not
on the generator's return value.

---

## 2. Item 4 — landed. The refusal stops one step short no longer

`process_run_complete` writes into every `behind_origin` `cause_evidence`: *"Reconcile first:
`python3 -m background.origin_reconcile`"*. On a tree held by paths that are not byte-identical to
origin's, that command's only possible answer is a second refusal — and the publisher's failure
count went **24 → 25 → 29** across three directions that each named it.

`origin_reconcile`'s `NOT_ADVANCED` already enumerated the blocking paths and their kinds. What it
never said is the sentence that ends the loop, and it is a **property**, not a command:

> it clears a blocking path only when the path's bytes **ALREADY equal** what origin brings, so a
> second run on this tree returns this same refusal.

`_landing_clause` now states that, plus the door **per kind** — because the two kinds take different
doors and a reader with only untracked blockers sent to `isolate_hunks` has been given the same dead
end in a longer sentence. Both `NOT_ADVANCED` sites carry it (the nothing-of-ours leg and the
pushed-but-still-behind leg).

### At the live tree, right now

```
Refused by 2 path(s): docs/observability/value_cycle_ab_s1_three_arm_20260908b.json (untracked
here, and origin adds its own copy); docs/staging/SEAT_FINDING_THE_PUBLISHERS_OWN_REMEDY_CANNOT_
CLEAR_ITS_OWN_REFUSAL_AND_THE_REPLACEMENT_RUN_HAS_NO_LEVEL_ARM_2026-09-08.md (untracked here, and
origin adds its own copy). THE STEP IS TO LAND OR REVERT THOSE PATHS, NOT TO RE-RUN THIS MODULE:
it clears a blocking path only when the path's bytes ALREADY equal what origin brings, so a second
run on this tree returns this same refusal. Specifically, the 2 UNTRACKED path(s) clear by landing
them (`python3 -m tools.surgical_land <path>`) or by removing them, whichever the holding lane
wants. Then re-run `python3 -m background.origin_reconcile`.
```

### The controls, and the poison rounds that prove they can fail

Five added to `tests/background/test_a_refused_advance_names_the_paths_that_refused_it.py`. The
single assert *"does the detail mention landing"* would have passed against a constant paragraph
printed under every refusal — **including the two legs where no landing is the step** — so each kind
asserts its OWN door and the ABSENCE of the other's, and both no-path legs assert no step at all.

| poison | killed |
|---|---|
| ignore the `kind`, print both doors always | **3** of 5 (both mirror legs, and the unknown-kind leg) |
| revert `_blocking_clause` to its old body — *the exact defect being fixed* | **4** of 5 |

Restored: 14 passed. Reachability is against the real defect, not a synthetic one.

**A third kind added later inherits no door.** `_landing_clause` states the property and declines to
name a step rather than handing the reader whichever branch the code happened to reach.

---

## 3. What this turn did NOT do, and why

**The drawn LANE 1 BUILD atom `W2_29_the_coverage_is_re_measured_against_the_demand_vector` was not
dispatched, because its own exit criterion forbids it today.** The row reads, verbatim: *"EXIT: the
acceptance re-run over the FULL five-component vector **once W2_30 lands**"*, and
`depends_on: [W2_30_per_household_half_hourly_electricity_and_seasonal_gas_shape]`. W2_30 is at
`level_current: 2` against `level_target: 3`. A fork sent at W2_29 now cannot reach level 3 by the
map's own words; it can only produce a re-measurement over the same partial vector the row already
records as measured. **The draw is not wrong — the dependency is simply not discharged yet**, and
the honest move is to say so rather than to spend a fork proving it.

**The static quality ratchet is red in the shared tree and it is not this work's red, and not this
work's to bank.** `test_ruff_no_stale_baseline_entries` reports `I001: baseline 1309, now 1308` —
the working tree is BETTER than the frozen floor by one. The single differing file is
`tests/tools/test_generate_maturity_map_data.py`, fixed uncommitted by another lane and touched by
nothing here. It passes at clean HEAD, and it passes in **the tree this commit creates** (HEAD plus
these paths only, checked in a `/var/tmp` extract: 27 passed). Lowering the baseline from the dirty
shared tree would bank another lane's unlanded work into the floor and wedge every lane behind it.
It clears when they land.

---

## What is next

1. **When `value_cycle_ab_s1_noise_floor_20260908b.json` lands**, move `THREE_ARM_PATH` and
   `NOISE_FLOOR_PATH` in ONE commit and read `error_bar.available` and
   `method_skill.fixed_horizon.available` off the rendered feed. The run half is already verified
   above, so that check is the only thing between the reader and both populations named.
2. `W2_29` is drawable again the moment `W2_30` reaches level 3; until then a draw of it should be
   deferred to `W2_30` rather than dispatched.
3. The publisher's own static sentence in `process_run_complete._behind_origin` still says
   *"Reconcile first"* with no conditional. It is now true — the command it names finally hands the
   reader a next step — but it remains a claim that reconcile can clear the state, written by a
   module that has not asked. Worth re-reading once the fork is closed, not before.
