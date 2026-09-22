**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** delivery-lane-disposition

# The sweep now reads the id in the header, and the binding the item ordered would have credited another lane's commit

**Filed:** 2026-09-19 · **Claim id:**
`reconcile-the-fork-and-take-the-repair-that-is-already-on-the-branch`

*(That is the id holding the claim and the deadline. The brief closed by ordering
`--landed the-sweep-cannot-see-a-finding-that-names-its-own-claim-id`, which has no row in the
claims store and none in the draw ledger, so it can bind nothing. Same shape as `838c07559`'s
subject, one stretch later. This document's own field carries the bindable one — and is, by
construction, the first artefact the leg below was built to read.)*

---

## The first instruction was refuted before it was run

The item opened: *"a binding is owed and costs one command. The lane recorded
`reconcile-the-fork-and-take-the-repair-that-is-already-on-the-branch` as `landed_unbound` against
`2f436602b`. Read that commit; if it is the work, run `--landed ... --commit 2f436602b`."*

**It is not the work, and the binding was not run.** Measured, not reasoned:

| | |
|---|---|
| claim's first draw | `1789716949.237` — 2026-09-18 08:35:49 |
| window + landing grace | closes 11:15:49 (`CLAIM_STALE_SECONDS` 6000 + grace 3600) |
| `2f436602b` committed | `1789724200` — 2026-09-18 **10:36:40**, inside that window |
| `2f436602b`'s subject | the product-gate census: `tools/decisions_by_account_class.py`, `tools/generate_value_arms_data.py`, the arms page |
| the claim's own subject | fast-forward this checkout onto `origin/main` and unwedge the publisher; *"done is `episode_clean_publishes` moving off zero"* |

Two different lanes, two different subjects. What joined them is a single path:
**`tools/run_value_cycle_ab.py`**, which `2f436602b` touches — and which the reconcile item's prose
names only to say it must **NOT** be landed:

> *(b) SUPERSEDED RIVAL work already on origin — `tools/run_value_cycle_ab.py` and
> `tests/tools/test_value_cycle_ab_noise_floor.py` carry a floor-progress marker whose twin
> `NOISE_FLOOR_PROGRESS_MARKER` is already on the branch, so these are `--drops`, NOT landings.*

So `_landed_unbound` credited the claim with a commit found on a path the claim named **in order to
drop it**. The join was right about the path and the window and wrong about everything that
matters. Running the bind would have written another lane's arms landing into this row, restarted
its deadline from that commit's instant, and made the reconcile work — which is still not done —
read as delivered.

**This is not a separate defect from the one the item then asked me to repair. It is that defect,
one rung up, caught in the act of ordering its own instance.**

## The repair: the discriminator was already in the artefacts

Every reading `tree_verdict` had of a closed window joined on a **path** or on a **clock**, and
both are inferences. `_claim_paths` returns paths the item's prose predicted *before the work was
done*; `_window_attributable_paths` returns whatever anybody wrote in the same hours — and says so,
in capitals, on every swept row: *ATTRIBUTED BY TIME AND NOT BY NAME*.

A filed finding's header carries `**Claim id:** <id>` — the turn saying, in the document, which
claim it was working. Exact, free, and read by nothing.

`background/delivery_lane.py` gains one leg, `_artefacts_naming_claim`, asked between the by-prose
strand and the by-clock candidate. It takes the **existing** `STRANDED` verdict, because "no
commit, and the bytes are sitting there" is already what it means and a sixth value for a second
route to an existing label is how a partition control stops covering its partition.

**Pre-check, as the item required.** `grep` of `background/` and `tools/` for a content-side
claim-id reader: none. `resolve_claim_id` / `near_claim_ids` are spelling-alias resolvers over the
claims store; `canon_drift_check._claim_ids_at_head` reads the canon YAML register. Neither reads
an artefact's body. The leg was written.

### The field form, not a substring, and the live tree says why

`docs/staging/WORKER_FINDING_REPEATING_ALARM_DELIVERY_LANE_STRANDED_2026-09-18.md` names
`reconcile-the-fork-and-take-the-repair-that-is-already-on-the-branch` **four times** — title,
quoted alarm body, signature line. It is an alarm filed by `background/alarm_repetition.py`
*because the claim delivered nothing*. Measured on that file at HEAD:

```
substring present: True | field match: False
```

A substring reader would publish it as evidence the work had moved, which would let the stranding
alarm extinguish its own condition on its second sweep.

### Measured at real inputs before the control was written

On the shared tree, 2026-09-19:

| | |
|---|---|
| dirty entries under `docs/staging/` + `tools/` | 215 |
| distinct ids carried in a `Claim id` **field** | 8 |
| scan finds, per id | 4, 2, 2, 1, 1, 1 … — exactly the field occurrences |
| hits for either live claim | 0 (neither has filed an artefact this window) |

The field **wraps** — `**Filed:** … · **Claim id:**` ending a line with the id alone on the next is
the commonest shape in `docs/staging/` today — so the text is flattened before matching. A
line-by-line reader is blind to every one of them.

## The control, and the four mutations that were RUN

`tests/background/test_a_swept_row_reads_the_claim_id_the_artefact_carries.py`, 8 legs.

| mutation | fires |
|---|---|
| delete the `by_name` block in `tree_verdict` | `…IS_read_as_the_work_having_moved` **+** `…NO_time_clause…` |
| `_names_claim_in_field` → `focus_id in flat` | `…only_MENTIONS_the_id…` **+** `…is_a_PREFIX…` |
| drop the `(?![\w-])` boundary | `…is_a_PREFIX_of_the_field_value…` |
| add `if mtime > window_closed: continue` | `…NO_time_clause_and_that_is_deliberate` |

Two of those caught **more** legs than the docstring first claimed. The prose was written before
the mutations were run and is corrected beside the claim in the file rather than tidied: a bare
`in` loses both discriminations because it has neither a left anchor nor a right boundary.

The sibling partition control
(`test_the_landing_ledger_reads_the_tree_in_both_directions.py::test_ALL_FOUR_VERDICTS_ARE_REACHABLE`)
stays green under every one of them — which is the point of taking an existing verdict, and the
reason this file cannot be substituted for by that one. 34 passed across both files at HEAD.

The direction named two legs explicitly and both are here:
`test_an_artefact_carrying_the_claim_id_IS_read_as_the_work_having_moved` (it CAN fire) and
`test_a_claim_with_NO_such_artefact_still_falls_through_and_still_sweeps` (which asserts the
silence **and** that `sweep_stale` still returns the claim to the pool — either alone is satisfied
by a broken reading).

## Known limit, stated rather than hidden

`tree_verdict` returns `None` above this leg when `_claim_paths` is empty — a row whose prose named
no tracked path. Those are the rows **most** likely to need a by-name answer and they still cannot
get one. Closing it is a change to the early returns, not a second leg, so it is filed here rather
than smuggled into a one-leg repair.

No mtime clause was added, deliberately: `_stranded_paths` needs its clock because "these paths are
dirty" is true of this tree almost always, and here the **name** does that work. A filter that
looks like consistency would re-lose exactly what the leg exists to find, and
`test_the_leg_has_NO_time_clause_and_that_is_deliberate` is what stops a later tidy-up doing it.

## What would prove this insufficient

The direction's own criterion, unchanged: **the next swept row whose evidence line still reads
*attributed by time and not by name* while an untracked artefact in the tree carries the swept id
in its header.** If that happens the remedy is in the wrong module and the next direction goes to
the artefact writer, not the sweeper.

A second, from this turn: **a swept row credited by name to an artefact that was not its work.**
That is the fail-open direction and it has no symptom, which is why the field form and the trailing
boundary are asserted separately rather than trusted.
