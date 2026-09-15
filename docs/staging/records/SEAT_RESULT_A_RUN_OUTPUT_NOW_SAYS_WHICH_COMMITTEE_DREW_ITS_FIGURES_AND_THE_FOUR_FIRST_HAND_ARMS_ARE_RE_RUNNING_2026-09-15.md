**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

# RESULT — a run output now says which committee drew its figures, and the four first-hand arms are re-running in this world

**Filed 2026-09-15, worker tick (LANE 0 delivery, claim
`the-five-blind-arms-are-re-run-and-stamped-in-this-world`).** Step 1 of the drawn item is landed
as **`331c4958f`**; steps 3 and 4 are launched and outstanding respectively.

---

## What the grep said before the change

The drawn item's premise held. On `c9769d426`:

```
$ grep -c "fast_mode\|SIM_FAST_MODE\|mock\|risk_committee_mode" /var/tmp/p6_arm_cull.json
0
```

`docs/design/blind_envelope_arms_2026-09-11.json` carries the sentence
`"pounds_are_not_publishable": "All five arms ran SIM_FAST_MODE=1, identically."` — and that
sentence was **unfalsifiable from the artefacts it is a claim about**. It is the same shape the
world digest was in before `dda5a27b2`, one layer along.

## What landed — `331c4958f`

The run identity header answered WHICH CODE (`producing_commit`) and WHICH WORLD
(`world_identity.digest`, plus `world_identity.homes.digest` since `c9cd58dae`) and could not
answer WHICH MACHINE. `SIM_FAST_MODE=1` swaps the local-LLM risk committee for
`sim.risk_committee_agent._call_mock`, a deterministic always-increase policy, so every hedge
decision in the run comes out of a different process.

* `sim/risk_committee_agent`: `FAST_MODE_ENV` and `fast_mode_enabled()`. `invoke()` now branches on
  the **function**, not a second copy of the comparison — two copies of a predicate are two facts,
  and the one in the header would be a claim about a branch it never watched being taken.
* `tools/run_annual_report`: `_execution_mode()` beside `_world_level_or_reason()`, published at
  `execution_mode` in the header and declared as `execution_mode.risk_committee` in
  `run_identity_fields`.

**Read from the ENVIRONMENT, not from `args.fast`.** The launch shape this has to survive is
`SIM_FAST_MODE=1 python3 -m tools.run_annual_report` with **no flag**, which is how the arm runs,
`tools/tournament_runner` and `tools/measure_publish_gate_subject_cost` all start their children. A
stamp keyed to `args.fast` reads False for every one of them.

**Why `execution_mode.risk_committee` is the declared field and the other two are not**, and the
choice is forced by the census rather than by taste: `_resolve_declared_field` returns `None` for a
bool, so declaring `execution_mode.fast` would contribute nothing to grading and say nothing about
contributing nothing; declaring the raw `sim_fast_mode` string would put an arbitrary environment
value through `_RUN_IDENTITY`, so `SIM_FAST_MODE=2026-09-15` could inject a run-identity token the
run does not have.

**Named and not covered:** `--end-year` truncates the simulation window and is equally fatal to
comparability. It does not reach `reconcile_and_stamp` and is **not stamped**. Said in the
docstring so the block is not read as covering it.

### The control, and each mutation that kills it

Four legs added to `tests/tools/test_the_published_run_output_names_its_world_and_adds_up.py` — no
new module, because that file already owns what a published run output says about itself.

| leg | mutation | result |
|---|---|---|
| `names_which_committee_ran` | pin `execution_mode` to a constant | **RED** |
| `names_which_committee_ran` | delete the `execution_mode` block | **RED** |
| `stamp_and_committee_obey_one_predicate` | re-inline the env read inside `invoke` | **RED** |
| `a_fast_mode_variable_set_to_something_other_than_one` | `bool(os.environ.get(...))` | **RED** |
| `declared_execution_mode_field_still_resolves` | declare the bool instead | **RED** |

The first leg is **one control over the whole partition** and that is the point: a stamp pinned to
`"mock"` passes every assertion a fast-mode-only leg can make, and the mock is what nearly every
run on this box uses — the constant would have looked right for months.

11 passed. Two reds in `tests/tools/` (`run_value_cycle_ab`'s declaration, and an artefact on disk
disagreeing with its own filename) are **pre-existing at HEAD**, proven in a clean extract of
`c9769d426`. The `static_quality_ratchet` I001 stale-baseline red is **another lane's uncommitted
edit**: per-file I001 counts for all three landed files are identical at HEAD and in the working
tree (0, 1, 0).

## The launch — step 3, recorded

Four arms. **ARM C′ is not re-run and must not be**: it has no first-hand run output on this box,
and an honest absence with its reason is the right answer for it.

* **Extract, not the shared tree.** `git archive 331c4958f` into
  `~/.cache/arm_rerun_331c4958f`, with `sim/cache` symlinked to the shared tree's 704M cache.
  Running from the shared tree would have stamped `331c4958f` onto a run that imported several
  other lanes' uncommitted edits — the launch-label-as-sha defect in a new costume.
* **The real sha.** `/var/tmp/p6_arm3.py` passes `code_commit="p6-arm-" + ARM`, which is what
  `SEAT_FINDING_A_LAUNCH_LABEL_PASSES_THE_PRODUCING_COMMIT_GUARD_AND_IS_PUBLISHED_AS_A_SHA` names.
  The copy at `~/.cache/arm_rerun_331c4958f/arm_rerun.py` reads `ARM_PRODUCING_COMMIT` instead,
  set to `331c4958f`. **Nothing else in the harness changed**, so these four stay comparable with
  each other exactly as the 09-11 four were.
* **Launched** `2026-09-15T17:52:06Z`, `setsid`, sequential (~13 min each, ~52 min total), by
  `~/.cache/seat_lane0/launch_arms.sh` → `~/.cache/seat_lane0/arms.log`. Order: `cull` (ARM A),
  `cull83` (ARM C), `tenure` (ARM D), `chosen` (ARM B). Outputs land at
  `~/.cache/seat_lane0/arm_<key>.json`.

  > **CORRECTED 2026-09-15T18:05Z, beside the claim. THIS LAUNCH DIED AND THIS BULLET WAS WRONG
  > WHEN IT WAS WRITTEN.** `setsid` cannot detach anything on this box: the tick runs inside
  > `worker-tick.service`, which is `Type=oneshot` / `KillMode=control-group`, and `setsid` changes
  > the session and the process group — a cgroup is neither. All four arms were killed **8m41s**
  > in, at 18:00:47Z, with only `cull` ever started and **no output written at all**. The signature
  > is the catalogued one: truncated final line, zero tracebacks in 9.9 MB, and no `END arm=` line
  > (so bash died too, not just python). Neither OOM nor the extract's missing `.git` is the cause;
  > both were checked and excluded.
  >
  > **This bullet is the exact shape the paragraph below warns about.** The harness was
  > smoke-tested and the record says so; the **launcher** was not, and the launcher is what failed.
  > A process state was published here as an established fact, became the next tick's premise, and
  > carried a `DO NOT RELAUNCH` instruction that discouraged the one check that would have caught
  > it. Liveness must be keyed to the property — `cat /proc/<pid>/cgroup` naming the job's own unit
  > — never to the log's size or to this sentence.
  >
  > **Relaunched 18:07:24Z** under `systemd-run --user --unit=blind-arms-rerun` (no `--collect`, so
  > `Result` survives a death), verified into its own cgroup, everything else unchanged. Full
  > account, and what the next tick should check before filing:
  > `docs/staging/SEAT_FINDING_THE_DRAWN_PREMISE_CHECKED_A_COMMIT_AND_THE_THING_THAT_MATTERED_WAS_FOUR_DEAD_PROCESSES_2026-09-15.md`.
* **Smoke-tested before the 52 minutes were spent**, which is the only reason this is a record and
  not a prediction. `reconcile_and_stamp` in the extract returns
  `producing_commit.commit = "331c4958f"`, `execution_mode.fast = true`,
  `execution_mode.sim_fast_mode = "1"`, and `world_identity.homes.digest = 35f8efe8ff02f245` —
  which is the live stock, and therefore exactly what `_blind_envelope_homes_refusal` is waiting
  for.

## Where the page stands, from origin's own bytes

```
$ git show origin/main:site/data/value_arms.json | python3 -c "...print(d['blind_envelope'])"
available: false
why_not: 5 of these 5 books carry no record of which HOUSES they ran on ... The live stock is 35f8efe8ff02f245.
```

Unchanged by this tick and correctly so — the refusal is honest until the arms are **filed**, not
until they are run.

## What is outstanding

**Step 4 only.** Each arm, as its run lands, into `docs/design/blind_envelope_arms_2026-09-11.json`
with `home_digest` and the execution mode **from its own run output**, and `producing_commit.commit`
set to the real `331c4958f` (the `launch_label` field stays, and stays separate). ARM C′ keeps
`home_digest: null` with its reason — which means
`_blind_envelope_homes_refusal` will still refuse, on a **new and narrower** reason naming one arm
instead of five. That is the drawn item's own stated finish condition ("or when the refusal on the
page names a NEW reason rather than the one it carries today") and it is worth saying out loud that
the four-arm envelope is publishable on the first-hand arms alone — `_blind_envelope` already
computes that split.
