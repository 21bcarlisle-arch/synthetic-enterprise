**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the census had no control for a row whose hit disappeared, and at the commit before the repair, seventeen had

**Measured 2026-09-05, delivery seat, from an isolated worktree at `HEAD = 986499b1f`.
Pre-registration: `records/SEAT_PREREGISTRATION_WHAT_THE_INVERSE_OF_UNDISPOSITIONED_MUST_FIRE_ON_2026-09-05.md`,
filed before any census was derived at any commit other than HEAD.**

---

## The structural hole the parameter-seam repair left open

`18a01f889` restored the five carriers the loader sweep had erased. It did not close the hole that
let them go. `background/self_clearing_alarm_census.py` had exactly two teeth:

- `census_is_vacuous()` — refuses a **totally** empty census. Per-path erosion is not its subject.
- `undispositioned()` — refuses a **hit with no row**.

**Nothing refused a row whose hit had disappeared.** A path that stops being a hit needs no
disposition, so `--check` exits 0 and the class shrinks in silence.

## What the inverse would have caught, measured

Deriving with the **pre-repair** census module over the tree at `c30738d77`, against that commit's
own dispositions file, and applying the new `eroded_dispositions()`:

| | |
|---|---|
| hits | 29 |
| dispositioned rows | 46 |
| **`undispositioned()`** | **`[]` — green** |
| **`eroded_dispositions()`** | **17 rows** |

All five carriers named in the earlier finding fired, and none was missed:
`run_history.json`, `.harden_cooldown.json`, `.ntfy_digest_state.json`,
`.supervisor_map_exhausted_state.json`, `retired_paths_served.json` — plus eleven more that had
eroded in earlier eras, which is the "twelve" the earlier finding could only assert. Sixteen of the
seventeen fired on the **no-readers** leg, as pre-registered; one on the declassification leg.

At `HEAD`: 50 hits, 50 rows, **0 eroded** — as predicted, so the control's branches had to be
injected to be proved, not observed.

## The design, and the trap it is built to avoid

A row can stop being a hit four ways, and only one of them is a repair:

- path gone from `state_paths` — the derivation lost it → **RED**
- path present, **zero writers** → **RED**
- path present, **zero readers** → **RED** (this is exactly `run_history.json`)
- path present, still written **and** read, but no longer classified → **RED unless the row
  authors `declassified` with a reason**

Refusing every non-hit row outright would make the census go red **precisely when the code became
more honest** — a control keyed to today's answer, which is this project's named backwards shape.
So a genuine repair is admitted, in writing, never silently. A path the census can no longer see
written or read is not a repair, and no field excuses it.

**Why this is not the tautology the module's own header forbids.** The obvious implementation —
remember last run's hit count, refuse a drop — reads the census's own prior output to decide
whether the census is right. It is not needed: `undispositioned()` already forces every hit to
acquire an **authored** row, so the dispositions file *is* the high-water mark — human-attested,
in git, derived from nothing. Checking today's derivation against it is checking source against
judgement.

## A fail-open found by the new control's own partition leg, and repaired as a class

`str(row.get(field, "")).strip()` yields `"None"` — truthy — for a row carrying an explicit JSON
`null`. My first draft of the `declassified` check inherited it, and the partition test caught it
on its first run. **The identical slip was live one function up in `undispositioned()`:
`{"verdict": "benign", "why": null}` counted as a disposition.** Fixed in both places rather than
in mine only, and `test_a_benign_verdict_without_a_reason_does_not_count` now runs the `null` leg
it had never run — it only ever tested `"   "`. A blank string and a JSON null are different
values and only one was tested.

## The second question: which tree the executor control relativises against

`test_the_executor_writes_no_code_to_the_shared_tree` relativised all three
`SHARED_TREE_WRITES` entries against `seat_executor.PROJECT_DIR`. Two are anchored there; the
third, `seat_continuation.STORE`, is anchored to `shared_tree_dir()` **deliberately** — that
anchoring was the 2026-09-04 hand-off repair. From the shared tree the roots coincide; from any
linked worktree `relative_to` raises, so the control certifying *"the executor writes no code to
the shared tree"* was red in the only environment the executor ever runs in.

**Decision: neither root globally — each entry is relativised against the root it is anchored to,
discovered per entry.** A hand-listed per-entry mapping would decay at the next addition; pinning
the whole list to `shared_tree_dir()` would only move the breakage to the other two. This is
**strictly stronger** than what it replaces, which checked one root and would have admitted
anything at all under the other, and it passes from both trees.

## Corrections, beside the predictions rather than instead of them

1. **I predicted "at least five" rows at `c30738d77` and got seventeen.** The prediction was not
   wrong, but it was weak in a way worth recording: I sized it from the incident I knew about, and
   the eleven older ones were the reason the hole mattered more than the incident did.
2. **My first draft of the reason requirement was fail-open on `null`**, and it was the partition
   leg — the control over the whole partition rather than a leg per branch — that caught it, not
   any of the five per-leg tests, all of which passed.
3. **One mutation survived the first pass and it was a missing test, not an equivalence**: the
   `undispositioned()` null case had no coverage. Established and closed rather than assumed
   equivalent.

## Done means

`eroded_dispositions()` exists, is wired into `--check` (proved by driving `main()`, not by
asserting the function), every leg is mutation-killed, the partition is proved reachable in one
control, the register documents `declassified` as the only admissible exit from the class, and
the executor's own shared-tree control is green from a linked worktree.

## Left open and named

Nothing runs `self_clearing_alarm_census --check` on a schedule — the teeth are the test suite's
(`test_every_disposition_row_still_has_a_live_subject`), which is enough to block a commit and is
where `undispositioned()`'s teeth already were. Wiring the CLI into a daemon would be a second
mechanism for the same property and is not proposed.

## Class registration

Belongs to `controls_that_cannot_fail`.

*Declared 2026-09-05 by the delivery seat, on the director's instruction to fold findings into the class registers rather than leave them as individual documents. Classified on the MECHANISM THIS DOCUMENT DESCRIBES (its body), not on its title: the registered classifier greps titles, and the titles have outgrown its vocabulary — which is why 92 findings sat `unclassed` while the six classes held 138 instances. The body carries 3 matches for `controls_that_cannot_fail` against 1 for the runner-up, which is the threshold used; anything below it was left for a reader rather than graded from a sibling.*
