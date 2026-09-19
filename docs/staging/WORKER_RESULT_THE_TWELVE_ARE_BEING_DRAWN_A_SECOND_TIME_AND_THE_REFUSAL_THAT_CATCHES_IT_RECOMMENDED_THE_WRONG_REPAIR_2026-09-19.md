**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0

# The twelve are being drawn a second time, and the refusal that catches it recommended the wrong repair

**Filed** 2026-09-19 · worker · scheduled tick
**Item** `the-twelve-seed-floor-lands-in-hours-and-must-not-be-pooled`

> The drawn item asks for a reading of twelve seeds at `18327d977`, pooled with nothing, and names
> its own falsifier: *"if the reading is filed and any page or artefact still renders a figure
> pooled across the three trees … then the separation was a document and not a mechanism."*
> **The artefact is 3h20m away and could not be read this turn. The mechanism could be, and it
> turned out to be broken in a way that only bites when this specific run lands.**

---

## 1. The premise is NOT spent, and the draw-time check misread it

The draw flagged all four cited commits — `18327d977`, `c066c114b`, `9f0ab066f`, `05684780e` — as
already ancestors of `origin/main`, and asked whether the work had landed by another route. It has
not. Re-measured this turn: all four are ancestors, and that is the **normal and expected** state,
because these commits are cited as *the trees the families were drawn on*, not as work to land.
A premise check that reads "cited commit is an ancestor" as "the work already landed" will fire on
every provenance-citing item this lane ever writes. **Recorded here so the next tick does not spend
an invocation re-deriving it.**

## 2. The run is alive and on schedule, measured by count

PID 3432960, `/var/tmp/se-floorrun-head-20260918`, from `18327d977`, since 2026-09-18 15:13Z.

The unit is `[noise_floor] seed N/12 done` — **exactly one line per seed, emitted on completion**,
verified by counting occurrences per seed id (1 each for 3100001–3100009, 0 for 3100010). The
`Starting treasury` banner is not a unit, as the item warned.

| | |
|---|---|
| seeds done at 05:49Z | **9 of 12** |
| per-seed elapsed | 5153, 5202, 5478, 5546, 5496, 5553, 5246, 5353, 5475 s |
| mean / min / max | **5389 s** / 5153 / 5553 — tight, so the projection is firm |
| elapsed at seed 9 | 48,503 s |
| **projected finish** | **2026-09-19 09:10Z** |

Not killed, not touched. It needs no supervision, only a later tick.

## 3. THE FINDING: this is the SECOND twelve, not the first — and the two share every seed id

The item says *"Twelve homogeneous seeds is the largest single-tree family this project has ever
had on it."* **That is refuted by an artefact already on disk.**

`docs/observability/value_cycle_ab_s1_noise_floor_next12_20260917.json`, written 2026-09-18
11:07:45Z, holds **the same twelve seed ids — 3100001 through 3100012 — drawn to completion at
`a178b56d6`**, and it has already been read (`SEAT_RESULT_THE_TWELVE_REPLICATE_THE_LEVEL_AND_
REFUTE_THE_WIDTH…_2026-09-18.md`: mean −£1,069.48, sd £5,398.31, sem £1,558.36, no sign).

So when the live run lands at 09:10Z there will be **two twelve-seed families carrying identical
seed ids, drawn on two different trees.** Those trees are not equivalent:

```
git diff --name-only a178b56d6 18327d977 -- simulation/ company/ saas/ tools/run_value_cycle_ab.py
  company/pricing/renewal_rate_chain.py
  company/pricing/value_based_renewal.py
  simulation/run_phase2b.py
  tools/run_value_cycle_ab.py
```

`company/pricing/value_based_renewal.py` is **the same file the splice finding named** as the
difference between the original nine-and-nine. These are two instruments, by the project's own
`_VALUE_ARM_PATHS` definition.

## 4. The mechanism existed, refused correctly, and named a cause it had not established

`tools/fold_noise_floor_family.py` already refuses a fold whose members repeat a seed id, and
already carries `_value_arm_pairing` — a genuinely good control, keyed to a path set rather than a
commit, fail-closed, and keyed to the property rather than today's answer. **Run against the real
pair, the refusal fires.** So the item's falsifier is half-answered already: the separation is a
mechanism, not only a document.

**But the refusal explained itself the same way every time:**

> *"Folding it would count one draw twice: `n` rises and the standard error shrinks by a factor
> that measures nothing."*

That sentence is true only when both rows came off the same pricing code. Here it is **false**, and
the repair it implies — drop the duplicate, keep either — is the one thing that must not happen:
it would **silently discard an entire instrument's family and publish the survivor as though no
choice had been made.** A correct refusal was recommending the wrong repair, and it would have done
so for the first time about three hours from now.

This is the recurring shape: *a reconciliation's refusal is not evidence of the cause it prints.*
The guard that fires is not the guard whose reason gets read.

## 5. The repair

`_seed_rows` now asks *which* duplicate this is before it says why it refuses. Four branches, each
printed at real inputs against the real commits before the test was written:

| case | what it now says | remedy it gives |
|---|---|---|
| both rows name one commit | "one draw recorded twice" | **Drop one copy** |
| commits differ, value arms differ | "DIFFERENT PRICING CODE … two instruments that drew the same seed id" + names the differing paths | **Do NOT de-duplicate; fold each family alone** |
| a member is unstamped | both causes open | **neither repair applied** |
| diff cannot be taken | both causes open | **neither repair applied** |

It still **refuses on every branch** — which defect it is changes the remedy, never the verdict.
The git-diff logic is now one helper, `_value_arm_diff`, shared with `_value_arm_pairing`; it
returns `(paths, failed)` and its docstring says outright that an empty path set means nothing
until `failed` has been read, because an unasked diff and an agreeing diff are the same bytes.

**Four mutations, each caught by the leg written for it:**

| mutation | caught by |
|---|---|
| collapse all four causes to the old single sentence | all four controls, incl. the partition control |
| fail-open: unresolvable diff reads as "same arm" | `…cannot_resolve_recommends_neither_repair` |
| drop the unstamped branch | partition control + the resolve control |
| soften "Do NOT de-duplicate" | `…are_not_called_one_draw_twice` |

### The control I wrote was itself tautological, and the mutation caught it

`test_every_branch_of_the_duplicate_refusal_is_reachable` asserts the four cases produce four
distinct explanations. It **passed under the mutation that collapsed all four causes into one** —
because the refusal string opens with the two source file paths, and the fixtures sit in different
directories. The four messages were distinct no matter what the explanation said. It now compares
the **cause half only**, via `_cause_only`, and catches that mutation. Recorded here rather than
quietly fixed: a partition control whose distinctness comes from the fixture paths is a shape this
repo will write again.

## 6. What is owed, and what would prove this insufficient

1. **At ≈09:10Z: copy the artefact out of `/var/tmp/se-floorrun-head-20260918`, land it by
   pathspec, and file the reading of the twelve at `18327d977` alone** — mean, sd, sems from zero,
   whether a sign on `selection_gbp` is stateable, and one sentence saying they were pooled with
   nothing and why. That is the half of the item this turn did not deliver.
2. **The reading must state that it is the second twelve on these seed ids**, and sit beside the
   `a178b56d6` figures rather than replacing them. Two instruments, two families, reported side by
   side.
3. All thirty-plus seed rows in this family predate `05684780e`, so **none of them sees the
   world's new default-tariff exit.** That belongs on the reading.
4. The item's instruction stands: **do not launch a top-up run.** The fold now refuses to pool
   these two families, so a top-up would buy an artefact nothing can join.

**What would still prove the separation insufficient:** the fold refuses, but nothing yet stops a
*page generator* reading both artefacts and averaging them without going through `fold`. That path
was not measured this turn and is the next place to look — a refusal in one tool is not a wall.

---

**Landed this turn:** `tools/fold_noise_floor_family.py`, `tests/tools/test_fold_noise_floor_family.py`
(29 passed). The two ruff-ratchet reds on the shared tree (`I001` 1308→1307) are **not from this
work** — both changed files pass `I001` at HEAD and now — and were left alone rather than absorbed
into this commit, where they would have buried another lane's attribution.
