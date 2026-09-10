**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The supervisor re-parsed 439 files every cycle — caching a pure function took the module from unfinishable to 457s

Round 2 of the operational-layer TIMED-OUT self-refill (RUNG 1b, PRIORITY ZERO). Round 1
(`SEAT_RESULT_THE_OPERATIONAL_TIMEOUT_IS_SLOW_NOT_BLOCKED_...`) settled blocking-vs-slow on four
independent legs and left one thing open, in its own §5: **the ~4.3s per `run_cycle()` was not
attributed.** Its §7.3 made attribution the precondition for touching any test. This is that
attribution, and the repair it turned out to license.

---

## 1. The draw's first branch, re-checked — still not green

The draw said to re-run the signal first, because a fix may already have landed. It has not:

```
consecutive_red: 7, last_result: "red_timeout",
timed_out_at: "tests/background/test_supervisor.py::test_stuck_escalation_does_not_fire_when_grants_fail"
```

**Round 1's §3 prediction is confirmed in production.** It said: *"The next timeout will name a
different test for the same underlying reason."* The hourly daemon has since re-run and named a
different test in the same module — `..._does_not_fire_when_grants_fail`, where the previous
timeout named `..._survives_daemon_restart`. Both pass when run alone. The payload is a landmark,
not a defendant, and the record now shows that rather than asserting it.

*Process note, and a rule I nearly broke twice.* Round 1's own §1 warns that a forced re-run
launches a **second** copy of the suite alongside the daemon's. I did exactly that at the top of
this turn — under a 900s bash wrapper that would also have killed it before its own 1800s budget
could produce a subject, which is the same mistake round 1 recorded. I killed it within ten
minutes of noticing. Two copies starve the box, which is the 2026-08-21 publish-gate failure the
draw itself cites.

## 2. The attribution — one chain, 79% of the test

`python3 -m cProfile -m pytest tests/background/test_supervisor.py::test_stuck_escalation_survives_daemon_restart`
(31 real cycles, the test the 20:02 timeout named). Cumulative time, one link per line:

```
run_cycle                                  406.48s  (31 calls)
└─ find_work                               406.45s
   └─ _self_refill_draw                    406.44s
      └─ _self_refill_draw_ladder          375.23s
         └─ _stale_gap_row_draw            320.76s   <- 79% of the whole test
            └─ gap_ledger_reconciler.refresh_work
               └─ discover_writers         317.06s
                  └─ python_code_text.searchable -> code_text  (13,578 calls)
                     └─ ast.walk / iter_child_nodes / compile
```

`discover_writers()` asks every `.py` file in `tools/` and `background/` whether it **writes** the
gap ledger, and — correctly, since 2026-09-08 — asks that question *of code, not of bytes*, which
means an AST parse per file. **439 files, 13.1 MB, on every supervisor cycle.** 13,578 parses /
31 cycles = 438 per cycle. Measured directly, outside the profiler: **2.46s per walk, and 2.46s
again on the immediately following walk.** Nothing changed between them.

`_sync_origin_staging` cost 0.002s across all 31 cycles — round 1's prediction 3 (the `_FakeClock`
throttles it) holds a second time, on independent evidence.

## 3. My round-2 predictions: one right, one half-wrong, one right

Pre-registered in `docs/observability/operational_layer_timeout_prereg_2026-09-10.md` before the
profile was opened.

- **Prediction 4 (the cost is in `find_work`, not `_check_stuck_escalation`): CORRECT.** 406.45 of
  406.48.
- **Prediction 5 (a pure-Python parse, not a subprocess — "most likely the maturity map's YAML"):
  HALF WRONG, and the wrong half is the one I named specifically.** The class was right: no
  subprocess appears anywhere in the hot path, and the 100%-CPU/`wchan 0` reading round 1 took was
  read correctly. The artefact was wrong. It is **Python AST parsing** of the repository's own
  source (`ast.iter_child_nodes` 70.7s tottime, `ast.walk` 33.5s, `compile` 22.1s). YAML is
  present at roughly 20–30s — real, but a fifth of the AST cost and not the target. *I guessed the
  parser I had been reading about instead of the one the code reaches.*
- **Prediction 6 (the by-hand replication returned early and never paid the cost): CORRECT in
  effect** — the expensive step is one `find_work` reaches every time, and a 0.081s cycle cannot
  have executed it.

## 4. The repair — and why it is not the one round 1 proposed

Round 1 §7 proposed narrowing the *tests* (a shorter `STUCK_THRESHOLD_SECONDS` under test, or a
clock that jumps the boundary), and flagged the R15 hazard in its own proposal: a rare branch that
stops being **reachable** is how a control here goes quietly tautological.

The attribution makes that unnecessary. **The cost is a pure function recomputed on byte-identical
inputs.** `code_text(source)` is `ast.parse` plus three pure walks — no clock, no filesystem, no
globals. So it is cached on the source text, in `tools/python_code_text.py`:

```python
@functools.lru_cache(maxsize=1024)
def code_text(source: str) -> str | None:
```

**The source text is not a proxy for the key, it IS the key**, so a hit cannot be stale by
construction: a file that changed produces different bytes and therefore misses. That is the whole
reason to prefer it to an mtime or path scheme — both of those *can* go stale, and a stale answer
here is a wrong answer **inside a wall** (`epistemic_wall`, `company_network_isolation` and four
ratchets all read source through `searchable()`).

`maxsize=1024` is derived, not picked: the live daemon's repeated working set is the 439 files
above, and 1024 holds it with headroom. One-shot whole-repo tools (2,895 tracked `.py`, 44.7 MB)
get no hits at any size — a single pass has no repeats — so sizing for them would buy nothing and
only raise the resident cost of a process that polls forever.

**Not one test changed, not one cycle count changed, no branch became less reachable.** That is
the point: the R15 hazard round 1 flagged in its own proposal is not present in this one.

## 5. The numbers, before and after, at real inputs

| | round 1 (before) | now (after) |
|---|---|---|
| `discover_writers()`, second consecutive walk | 2.46s | **0.05s** (49×) |
| `test_stuck_escalation_survives_daemon_restart` | 128.54s | **30.23s** |
| `tests/background/test_supervisor.py`, 1700s cap | **132 of 201, KILLED at the cap** | **201 passed in 457.01s** |

The writer set is byte-identical across cached and uncached runs (20 writers, same paths).

*Honest caveat on the comparison, stated rather than buried:* round 1's 1700s run shared the box
with the publish gate's full non-operational suite **and** another lane's `tests/simulation` run;
mine shared it with one architecture-test run (load average 3.07 on 16 cores, against round 1's
5.76). The conditions are not identical. They do not need to be: the change is from *not
finishing 201 tests in 1700s* to *finishing all 201 in 457s*, which no plausible load difference
spans, and the per-walk 2.46s → 0.05s was measured back-to-back in one process.

## 6. The controls, and what each one catches

Three legs in `tests/tools/test_python_code_text.py`, each mutation-proven against a mutant built
in-process, and each red for its **own** defect and no other — the partition matters, because a
leg that catches everything is a leg that localises nothing:

| mutant | `keyed_to_the_BYTES` | `repeated_scan_does_not_re_parse` | `unparseable_fail_closed` |
|---|---|---|---|
| decorator deleted ("cleanup") | passes | **RED** | passes |
| cached, keyed on `len(source)` | **RED** | passes | passes |
| fallback returns `""` not the source | passes | passes | **RED** |

- **`..._keyed_to_the_BYTES_and_not_to_anything_that_merely_correlates`** — the killer. Uses two
  sources of **identical length** and differing code, so a cache keyed on a length, a path, an
  mtime or a hash prefix goes red. Content-keyed, it cannot.
- **`..._a_repeated_scan_of_the_same_source_does_not_re_parse_it`** — guards against the cache
  being *silently removed*. Keyed to the property (a second ask of identical bytes is served
  without re-parsing, read off `cache_info()`), not to a timing threshold, which would flake on a
  loaded box. Without this leg, deleting the decorator restores 2.46s per cycle and every other
  test still passes — the operational layer goes unmonitored again and nothing goes red.
- **`..._the_unparseable_fallback_is_still_fail_closed_through_the_cache`** — a cached `None` must
  still reach `searchable()` as the original text. A control that looked and saw nothing must
  never be reported as a clean file.

## 7. What this does NOT establish

- **Not that the operational signal is green.** The module was the dominant cost and no longer is,
  but the suite is larger than one module. **Prediction, filed before the answer:** the next
  hourly check completes inside 1800s and the signal goes GREEN, paging `[OPERATIONAL LAYER
  RECOVERED]`. If it times out again, this repair was necessary and not sufficient, and the next
  round profiles the suite rather than this module.
- **Not that round 1's §7 narrowing is wrong** — only that it is no longer needed for *this* cost.
  The escalation tests still drive 30–40 real cycles to assert one transition. That is now ~26s
  each rather than ~128s, which buys the time to do it carefully or not at all.
- **The 1800s budget is untouched**, per round 1 §7.1 and the director's 2026-08-21 ruling.
  Raising it is the move that produced this state.

## 8. A red I did not cause, recorded so it is not attributed to me

`tests/architecture/test_a_control_reads_python_as_code.py::test_the_floor_holds_and_no_row_is_stale`
is RED in the shared worktree, naming
`('tests/tools/test_fold_noise_floor_family.py', '_producer_made_floors')`. That file is another
lane's **uncommitted** edit; the symbol does not exist in HEAD's copy, and I never touched it. In
the tree this commit creates (HEAD plus my hunks) it is absent, which is why the landing goes
through `surgical_land` rather than a pathspec commit.

---

**Reversal:** revert the decorator and the `_CODE_TEXT_CACHE_MAXSIZE` block in
`tools/python_code_text.py`, and the three appended legs in `tests/tools/test_python_code_text.py`.
Evidence: `docs/observability/operational_layer_timeout_prereg_2026-09-10.md` (rounds 1 and 2,
predictions before answers).
