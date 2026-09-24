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

## A sixth cause: the citation is DEAD, the tree is green, and the refusal names no cause at all

*Appended 2026-09-24 by the delivery seat, same claim as the fifth cause above. This is the
measured outcome of that repair, recorded whether or not it flatters it.*

**The fifth cause is cleared, and the gate's own instrument says so** — not this seat. From
`docs/observability/.publish_gate_state.json` on the shared tree, the two publish failures either
side of the landing (`697625722`, on `origin/main` at 06:36Z):

| | 06:02:19Z — before | 06:55:10Z — after |
|---|---|---|
| `citation_at_head` | `reproduces` | **`dead`** |
| reason | "all 1 cited red(s) are still red, so the citation is live and repairing it is the unblock" | "all 1 cited red(s) PASS … so this citation is DEAD" |

`blocking_tests: []`. `total_red: 0`. `liveness_surface_refusal: null`, and the liveness heartbeat
published at `cd6fad764` — the surface the fifth cause's controls guard.

**And the publisher still failed.** `episode_failures` went 43 → 45, `last_clean_publish` is
unmoved at 2026-09-21T18:15Z, and the cause recorded for that 06:55 failure is:

> `cause: "unattributed"` — *"recorded with no observation attached (rc=1, kind=test_regression) —
> this exit path names no cause, so which one it was is NOT established here"*

So the sixth cause is **an exit that refuses without naming why**, and it is a different kind of
thing from the five before it. Causes 1–4 were states of the tree; cause 5 was a state of the
instrument; **cause 6 is the absence of an instrument.** The refusal says `kind=test_regression`
while `total_red` is 0 and every cited red passes at HEAD — three statements that cannot all be
about the same tree.

**This is the document's own thesis arriving on schedule**, and it should be read as evidence for
it rather than as a disappointment: *"the causes are serial, each one masked by its predecessor, and
no instrument reports the queue of them."* Five of six were only visible once their predecessor was
cleared. The difference now is that the sixth cannot be cleared by looking at what the publisher
said, because the publisher did not say.

**What the next lane should NOT do:** re-run the cited test and conclude the publisher is fixed.
It is green, it is dead as a citation, and the publisher is still refusing. The next item is the
unattributed exit itself — `background/process_run_complete.py`, the rc=1 path that reaches
`"this exit path names no cause"` — and the question is which observation it is dropping between
the rc it saw and the record it wrote.

**What is NOT claimed:** that the fifth cause was the last one, that clearing it was sufficient, or
that `last_clean_publish` will move. It has not. The claim is bounded to what the gate measured:
the cited red is dead at HEAD, and it was this landing that killed it.

## The sixth cause, found and repaired: the gate's return code was thrown away one frame below the refusal

*Appended 2026-09-24 by the delivery seat, same claim as the fifth and sixth causes above. The
question the previous section left open — "which observation is it dropping between the rc it saw
and the record it wrote" — is answered here, with the line of code that drops it.*

**The observation existed. It was written down. Then it was left behind at a door that could not
carry it.** One cycle, four minutes, from the shared tree's own records:

| when | record | what it says |
|---|---|---|
| 06:51:17Z | `.last_gate_blocking_tests.json` | `node_ids: [FAILED …test_a_wedged_tree_and_a_hot_origin_are_told_apart_in_the_record]`, `total_red: 1`, `graded_sha: 35f9e3462` |
| 06:55:10Z | `.publish_gate_state.json` | `cause: "unattributed"`, `cause_evidence: "recorded with no observation attached (rc=1, kind=test_regression) — this exit path names no cause"` |

And in `sim-runner-log.md` between them, verbatim: `1 failed, 1805 passed, 9 skipped, 282
deselected` then `Scoped publish-path gate FAILED - not committing content`.

**Where it is dropped.** `_run_gate_in` ends `return result.returncode == 0, False`. The suite's
return code — the one thing that separates a judged red from a killed child — is collapsed to a
**boolean** on that line. `_gate_refusal` therefore had one non-timeout answer, a bare `return 1`,
and `record_publish_gate_outcome` had only its generic fall-through, which passes no cause and lets
`_classify_gate_failure` call every non-zero `test_regression`.

**Three separable things were arriving as one**, and the log shows all three live:

* rc>0 with a named node — a real red at a sha we recorded. (06:51Z above.)
* rc>0 with nothing named, or rc<0 — nothing judged. `Publish gate RED (rc=-15) — no FAILED/ERROR
  summary line found` appears on 2026-08-14, 08-18 (twice) and 08-19; `rc=1` with the same line,
  sixteen consecutive times on 2026-08-11.
* no subject at all — the checkout could not be materialised, so the gate never ran.

**Why this is the fifth time, not the first.** rc=77, rc=78, rc=79 and the two outer deadline kills
were each carved out of this same bare `return 1`, each with a comment in `process_run_complete.py`
saying "same class, own name". The 2026-08-21 carve-out took the publisher's inner *clock* out and
left everything else in. What was left was never one thing.

**The repair.** `EXIT_SCOPED_GATE_REFUSED = 81`, two causes in `publish_cause`
(`scoped_suite_red` / `scoped_gate_unjudged`), and `_run_gate_in` recording which it saw at the
instant it sees it — the same cross-process carrier rc=77 has used since 2026-08-30, keyed to the
same git hash the router reads back. The judged/unjudged split rides on the **cause**, not on a
sixth and seventh exit code: a code licenses the router to read the attribution, it is not the
attribution. `scoped_gate_unjudged` is in `UNJUDGED_GATE_KINDS` and in the supervisor's
`WEDGE_KINDS_NO_TEST_JUDGED`, so the RUNG-1 draw stops being sent after a red that does not exist.

**Control:** `tests/background/test_the_scoped_gates_refusal_names_which_refusal_it_was.py`, nine
legs, written over the whole partition rather than one leg per branch. Four observable shapes,
three states, **and the collapse is asserted rather than left to the reader** — the two unjudged
shapes share a state deliberately (the reader's instruction is the same: implicate nobody) and are
held to *differing* evidence lines, because they send a diagnostician to different places. Eight
mutations run, each biting the leg its docstring names, including the chain leg: delete the
recording call from `_run_gate_in` and only the leg that drives the real `run_fast_tests` reds.

### Pre-registered, before the next cycle can answer it

Written now so it cannot be filed after the result. **Prediction:** the next publish-gate failure
recorded after this lands carries `cause` ∈ {`scoped_suite_red`, `scoped_gate_unjudged`} with a
`cause_evidence` naming a return code, and `kind` is `test_regression` **only** on the first of
those. **What would refute it:** another `"recorded with no observation attached"` at rc=81, or an
rc=1 record from the publish path at all — rc=1 is now reachable from `_process` only by the three
non-gate paths (marker missing, JSON missing, report regeneration failed), and a gate refusal
arriving as rc=1 means the router is reading a stale exit code from a daemon that has not restarted
onto this commit.

**What is NOT claimed.** Not that `last_clean_publish` will move: this names the sixth cause and
repairs the instrument that failed to name it. Whether a seventh is behind it is the next
observation, and on this document's own thesis — *the causes are serial, each masked by its
predecessor* — one should be expected rather than hoped against. What *is* claimed is narrower and
falsifiable: the publisher will no longer refuse without saying which refusal it was.
