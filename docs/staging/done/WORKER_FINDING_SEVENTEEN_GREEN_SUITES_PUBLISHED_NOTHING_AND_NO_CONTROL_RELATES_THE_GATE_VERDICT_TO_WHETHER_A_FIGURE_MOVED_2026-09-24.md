**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# Seventeen green suites published nothing, and no control relates the gate's verdict to whether a figure moved

Filed from the Lane 0 item
`the-publisher-has-been-silent-53-hours-and-each-cleared-cause-named-another`, which asked for one
finding naming the sequence of distinct causes this single wedge presented. The sequence is real,
but it is not the finding. **The finding is that the wedge's two longest stretches were GREEN.**

## The window, from the gate's own log

`docs/observability/.publish_gate_state.json` at the time of reading: `last_clean_publish`
2026-09-21 18:15 UTC, `wedge_since` 2026-09-21 20:40 UTC, `episode_failures` 40,
**`episode_clean_publishes` 0**.

`docs/observability/publish_gate_duration.jsonl` holds exactly 40 runs in that window, and they fall
into three contiguous blocks with no interleaving at all:

| Block | Span | Runs | `outcome` |
|---|---|---|---|
| 1 | 2026-09-21 20:39 → 2026-09-22 05:21 | 5 | **all `pass`** |
| 2 | 2026-09-22 07:29 → 2026-09-23 00:44 | 23 | all `fail` |
| 3 | 2026-09-23 01:44 → 2026-09-24 01:11 | 12 | **all `pass`** |

**17 of the 40 runs passed. None of them published.** The wedge opened one minute after a `pass`
(20:39 run, `wedge_since` 20:40) and was still open after twelve consecutive `pass` runs.

## The sequence of causes, since it was asked for

Each block is a different cause, and clearing each one revealed the next:

1. **Block 1 — no test involved.** The suite was green for 8.7 hours and the wedge had already
   begun. This is the stretch the item's phrase *"a dead test citation"* points at: the state file
   still carries `citation_at_head_reason` = *"no red is named on this failure, so there is no
   citation to re-ask"*.
2. **Block 2 — genuine reds**, 17.3 hours, the site lane's failures. This is the only block a
   failing test explains.
3. **Block 3 — `behind_origin`**, 24.5 hours and counting, green throughout.
   `background/origin_reconcile` refused with `REFUSED_CONFLICT` on 74 paths.

A fourth cause is live and is in none of the three: `docs/observability/.publish_step_state.json`
reads `degraded: true` with `failing_steps` `["Customer data generation", "Customer sample
generation"]`, which no `cause` in `background/publish_cause.py` names.

**So a failing test accounts for 17.3 of the wedge's 54.5 hours — 32%.** Two thirds of the outage
happened while the instrument that looks like the publisher's health said `pass`.

## Why nothing noticed

`outcome` in `publish_gate_duration.jsonl` records **whether the publisher's scoped suite passed**.
`last_clean_publish` records **whether a figure reached origin**. They are different quantities, and
nothing in the repository compares them.

That is what let this run for 54 hours. Every automatic reader was looking at the first one:

- The duration log's own bands (`band: ok`, `headroom_ratio: 0.69`, `cadence_band:
  within_cadence`) grade the suite's *runtime*, and were `ok` on all 40 runs including the 23 reds.
- The heartbeat published "alive" three times in the last 3.1 hours of the wedge — it is keyed to
  the publisher *running*, not to the publisher *landing*.
- `blocking_tests` is `[]` and stays `[]` through both green blocks, which reads as health.

The three `not_established` fields in the state file (`citation_at_head`, `fork_state`,
`red_at_head`) are the one honest part of the surface: each carries a reason saying so explicitly
(*"This is not evidence that HEAD is green."*). They fail closed and say so. Nothing above them does.

## The control this earns, keyed to the property

Not "the suite is green" and not "the wedge is under N hours" — both are today's-answer keys that go
green the moment someone fixes an instance. The property is the **relation**:

> A run whose `outcome` is `pass` must advance `last_clean_publish`, or name a cause for why it did
> not.

A green suite that leaves `last_clean_publish` untouched and writes no `cause` is the defect, and it
is the state all 17 green runs were in. This is one leg over the existing pair of fields, not a new
register: it needs no new artefact, and it can fail — Block 1 and Block 3 are 17 recorded instances
that would have reddened it, so it is falsifiable against history rather than against a future.

**Deliberately not built here.** The wedge itself was the drawn work and is being cleared in the
same turn by resolving the 74-path fork; building the control in the same commit would make the
attribution impossible if anything downstream moved. One variable.

## A prediction, filed before its answer is known

If the control above is built and run against the 40 records in this window, it reds on exactly the
17 `pass` runs and is silent on the 23 `fail` runs. If it reds on fewer than 17, `last_clean_publish`
moved during the wedge without the state file recording a clean publish, and the two fields disagree
about their own subject — which would be a second, worse finding.

## A fourth cause, observed in the same turn, recorded beside the claim

The `behind_origin` cause above was cleared in this turn: the 74-path rename/delete fork closed
(`7511d33c8`), twelve gated landings reached origin, and the tree read 0 ahead / 0 behind. The
publisher did **not** publish. It named a new cause on its next invocation:

> `[stale-producer] REFUSED tools/generate_value_arms_data.py is a working copy that predates commit
> 6cad55bfc (predates_landing), so regenerating from it would republish over that landing.`

So the count in this document is a floor, not a total: **four distinct causes, not three**, and the
fourth was invisible until the third was cleared. That is the whole claim — the causes are serial,
each one masked by its predecessor, and no instrument reports the queue of them.

**The named door is refused here on evidence.** The refusal points at
`python3 -m tools.refresh_to_head tools/generate_value_arms_data.py`, and the clock agrees the copy
is older than the last commit to its path (disk 2026-09-23 07:42 and 11:43; last commit 23:36). But
the working copies supply **14 symbols that exist in no commit** — `_book_of`, `_its_block_rendered`,
`test_a_book_silent_floor_is_REFUSED_and_the_one_the_page_used_to_read_is_the_witness`,
`test_the_composition_floor_is_selected_by_the_runs_book_and_never_by_its_answer` and ten more, all
`ABSENT` from `git grep HEAD`. This is the concurrent-fork shape, not a stale revert, and
`refresh_to_head` would delete a lane's unlanded test suite to buy one publish. **Not done.** The
remedy is a three-way union merge of that pair, which is its own item with its own evidence, and it
is not this one.

**This also sharpens the control proposed above.** A cause-naming refusal is what let the fourth
cause be seen at all — the publisher said why, in words, on the surface. The gap is not that causes
go unnamed; it is that nothing keeps the *series*. A reader of the state file sees one `failures`
entry of length 1 and a 54-hour clock, and cannot recover that four different preconditions failed
in sequence. The control should append, never replace.

## A fifth cause, and it is a BLIND INSTRUMENT — the fixture, not the code

*Appended 2026-09-24 by the delivery seat, claim
`the-one-red-the-publish-gate-cites-collapses-both-legs-of-its-own-discrimination`. Pre-registration:
`docs/staging/records/SEAT_PREREG_IS_THE_COLLAPSED_WEDGE_DISCRIMINATION_A_BLIND_FIXTURE_OR_A_COLLAPSING_PRODUCTION_BRANCH_2026-09-24.md`,
written before the fixture was touched.*

The fourth cause was cleared. The publish gate then cited exactly one red, and it is a test:

> `tests/background/test_the_liveness_surfaces_refusals_left_only_an_orphaned_log_line.py::
> test_a_wedged_tree_and_a_hot_origin_are_told_apart_in_the_record`

**The question this document's series makes worth asking: is the publisher blocked by a broken
instrument, or by production code that genuinely collapses two states into one string?** The
flattering answer is the first, so it was pre-registered before it was measured.

### It is the first, and it is ONE command

`_refused_advance_cause` (`background/process_run_complete.py:6021`) calls
`origin_reconcile.commits_ahead` inside its own `try`. That shells `git rev-list --count
origin/main..HEAD`. The fixture's catch-all — correctly fail-closed since 2026-09-17 — raised
`AssertionError`, the function's broad `except` caught it, and it returned *"whether this is a
dirty-tree collision was NOT established"* **for every input**, discarding `blocking` (the one
argument that differs between a wedge and a hot origin) before `_blocking_clause` ever saw it. Both
legs therefore ended in the same sentence and the inequality red.

Production's discrimination was never reached. With the command modelled, it works:

* **wedged** — *"…a tracked file this tree has edited is holding the shared tree behind origin …
  Refused by 1 path(s): `background/process_run_complete.py` (modified here, and origin changes it
  too)"*, 900 chars, naming the holder and the KIND.
* **hot origin** — *"nothing local collides … NOTHING local collides with what origin brings"*,
  728 chars.

### One-variable attribution, both directions

| Variant | Result |
|---|---|
| HEAD | 1 red — the discrimination |
| all four commands modelled | 16 green |
| `rev-list` alone removed, other three modelled | the **same** red returns |
| `merge-tree`/`diff` removed, `rev-list` modelled | discrimination **green** |

So `git rev-list --count` is the collapsing command and the other two are not. The prediction filed
before the run said exactly this and is confirmed.

### …and the reachability leg found a SECOND blindness the refusal legs could not

The pre-registration's own warning — *"clearing the first is the flattering place to stop"* — earned
its place. `merge-tree`/`diff` changing no verdict is not a reason to model them and move on; it is
evidence they are unreachable. They were. `_drive` passed the publish path **relative**
(`"site/data/tick_heartbeat.json"`) where both production callers pass it **absolute**
(`str(PROJECT_DIR / rel)`, `str(_prov.PROVENANCE_FILE)`). `_our_publish_paths` does
`Path(p).resolve().relative_to(PROJECT_DIR)`, which takes its documented *"a path outside the repo
cannot be compared"* exit for a relative path — so `_publish_surface_collisions` answered `None` for
**every test in the file**, every `ahead > 0` leg refused on *"overlap with our own paths NOT
ESTABLISHED, so fail-closed"*, and the 2026-09-16 disjointness narrowing had no control on it here
at all.

**No refusal leg could ever have shown this**, because the fixture's blindness and the code's
judgement produce the identical verdict — this file's own most-repeated lesson, one layer down in a
fake. It took the leg that requires an **admission**:
`test_a_behind_origin_publish_origin_is_NOWHERE_NEAR_is_admitted_not_refused`. That leg is now what
makes `merge-tree`/`diff` load-bearing, and with it removed the suite goes red.

### What this cause is, in the series' own terms

Causes 1–4 were states of the tree. **This one is a state of the instrument**, and it is the first
in the series that could not have been cleared by any action on the tree. It also fits the series'
thesis exactly: it was invisible until cause 4 was cleared, and clearing it needed a pre-registered
question because the cheap reading — "the test is red, the code must be wrong" — points the wrong
way.

**What is NOT claimed.** `last_clean_publish` has not moved. This clears the one red the gate cites;
whether a publish cycle then completes is the next observation, not this one's result.
