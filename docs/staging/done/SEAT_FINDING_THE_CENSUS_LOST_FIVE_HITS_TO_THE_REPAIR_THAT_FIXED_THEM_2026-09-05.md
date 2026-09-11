**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the census lost five hits to the repair that fixed them, and the fail-open got stronger the more correctly a carrier was repaired

**Measured 2026-09-05, delivery seat, from an isolated worktree at `origin/main` = `5d0f57107`.
Pre-registration: `SEAT_PREREG_THE_BULK_LOADER_ANNOTATION_MADE_27_CHECKABLE_CLAIMS_AND_NOTHING_OPENS_THEM_2026-09-05.md`,
filed before any of this was run.**

---

## The direction was already discharged, so the hazard had moved

Lane 0 drew me against *"26 benign rows still carry no `loader` field"*. All 46 rows already
carried one: `c30738d77` landed the whole sweep earlier today. Evaluating the hazard rather than
the expired proxy, the question became whether the sweep's own bulk annotation — *"ASKED AND
CLEAN … no state raises and **none is a read-modify-write**"*, asserted across 27 rows with
nothing on disk opening it — was true.

**It was true. What was not true was the census underneath it.**

## What I measured

A read-modify-write detector over the census's own AST facts, run first as a vacuity leg against
the six carriers the sweep had already repaired. **It flagged one of six.** Under the
pre-registration that voided the run as an exoneration — and the reason it under-reported turned
out to be the finding.

Deriving the census over the tree either side of `c30738d77`, one variable, same module:

| | hits |
|---|---|
| before the sweep | **34** |
| after the sweep | **29** |

```
LOST: run_history.json  .harden_cooldown.json  .ntfy_digest_state.json
      .supervisor_map_exhausted_state.json  retired_paths_served.json
```

`run_history.json` went to **zero recorded readers** while `count_run_history_total` — the Project
tab's "Sim runs" KPI — reads it on every dashboard build.

## The mechanism

The census attributes a state file by **module-level symbol**: it sees
`RUN_HISTORY_PATH.read_text()`. The sweep repaired six carriers by routing every read through
`background/episode_prior`, whose loaders take the path as an **argument** — and inside
`episode_prior` no module symbol names it. The key dies at the parameter seam.

**So the fail-open was getting stronger with adoption.** The more correctly a carrier was
repaired — through the shared helper rather than a hand-rolled loop, which is exactly what this
project asks for, and what the sweep's own commit message states it did — the more certainly it
left the class the census enumerates. Twelve further paths dispositioned in earlier eras had been
eroded the same way and were already silently absent.

Nothing anywhere could notice this:

- `census_is_vacuous()` refuses a **totally** empty census. Per-path erosion is not its subject.
- `undispositioned()` checks a hit with no row. **The inverse — a row whose hit disappeared — is
  checked by nothing.** A path that stops being a hit needs no disposition and `--check` exits 0.

That is the census's own stated fail-open shape arriving through the one door it had not guarded,
and it is the second-order form of the class the census exists to enumerate: the repair silenced
the instrument that found the defect.

## The repair

`_attribute_through_parameters` in `background/self_clearing_alarm_census.py` walks a caller's
**keyed argument** into the callee's **parameter**, to a fixpoint. It is a generalisation, not a
lexicon of known helpers: any path-taking helper, present or future, is now attributed. Result —
**134 attributions, all five carriers restored, and sixteen paths visible that were not**.

| | hits |
|---|---|
| before the sweep, old census | 34 |
| after the sweep, old census | 29 |
| after the sweep, **fixed** census | **50** |

Four of the sixteen had never been dispositioned at all. Each was read at its daemon, not at its
row:

- **`.seat_work_in_hand.json` — `real`, and a live defect.** `claimed_at` is an episode start:
  `last_progress` returns `max(claimed_at, last commit touching the claimed paths)` and
  `stale_claims` publishes `idle_seconds` from it as the severity of the `[SEAT]` escalation.
  `claim`/`release`/`sweep` read-modify-write the whole store, and `_load` answered `{}` for a
  corrupt file exactly as for a missing one. **Measured at HEAD against a live prior of two other
  lanes' claims: empty / truncated / `null` / `[1,2,3]` / `"abc"` all left 1 claim, 0 survivors,
  no crash and no copy kept.** Repaired via `load_episode_prior` + `preserve_unreadable` in the
  writers only — the readers stay pure. The loss is made **recoverable, not prevented**: refusing
  to claim on a corrupt byte would wedge the seat, which is the worse failure.
- **`.last_publish_cause.json` — benign, and the best loader in the census.** `read_cause` splits
  absent from unreadable from malformed from unstamped, each with its own named sentence.
- **`naive_organ_log.jsonl` — benign.** Append-only, parsed per line; a corrupt line costs one
  entry, never the file.
- **`run_insights.json` — benign.** Regenerated wholesale; the writer never consults the prior.

## Corrections, recorded beside the predictions rather than instead of them

1. **I predicted a missed read-modify-write among the 27 and was wrong about where the defect
   was.** The bulk annotation held up; the instrument beneath it did not. The prediction that
   earned its keep was the **vacuity leg** — "if the detector does not flag the known
   read-modify-writes, the run is void" — which is the only reason I looked at the census instead
   of publishing "the 27 are clean."
2. **My first cut of the parameter walk restored one carrier of five.** Aliases (`p = Path(path)`)
   were recorded under the local name, which means nothing to a caller binding by position.
3. **I checked the pre-existing red below in a `git archive` extract and reported it as passing at
   HEAD. That check was invalid** — an extract is not a linked worktree, so it cannot reach the
   branch that fails. Re-run in a real linked worktree at HEAD, it fails there too.
4. **A mutation survived and it was a missing test, not an equivalence.** Reducing the fixpoint to
   a single pass passed the whole file, because my two-hop case happened to be declared
   inner-first — a lucky order. Declared caller-first, one pass cannot reach it. All five named
   mutations now fire.

## Left open and named rather than quietly fixed

`tests/background/test_the_seat_executor_stands_down.py::test_the_executor_writes_no_code_to_the_shared_tree`
**cannot pass from a worktree.** `SHARED_TREE_WRITES` includes
`delivery_lane.seat_continuation.STORE`, which resolves to the **shared** tree by design — that
fix was the point of the hand-off repair — while the test relativises all three entries against
`seat_executor.PROJECT_DIR`, which is *this* tree. From the shared tree they coincide and it
passes; from any linked worktree `relative_to` raises. So the control certifying "the executor
writes no code to the shared tree" is red in the only environment the executor actually runs in.

Confirmed pre-existing at `5d0f57107` in a clean linked worktree, and **not touched here**:
deciding which tree that assertion should be relative to is a judgement about another lane's
control, and making it silently inside this commit is how a control acquires a second definition.

## Done means

The census attributes reads and writes across a parameter seam; the five carriers the sweep
removed are back in the class; the sixteen it had never seen are dispositioned or repaired; and
the erosion is recorded in the artefact (`parameter_attributions`) so a walk that stops matching
is loud rather than flattering.
