**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# PRE-REGISTRATION: the loader sweep's bulk annotation made 27 checkable claims and nothing opens them

**Written 2026-09-05, delivery seat, from an isolated worktree at `origin/main` = `5d0f57107`.
Filed BEFORE the measurement below was run.**

---

## The direction I was drawn against is already discharged

Lane 0 direction: *"26 benign rows still carry no `loader` field"*, naming
`.wedge_suspect_hit_rate.json`, `.product_interleave_state.json`, `.reconcile_watch_state.json`,
`.ntfy_digest_state.json` + `ntfy_digest_queue.jsonl`, `.remainder_annotation.json` and
`.origin_staging_sync.json` as the strongest unmeasured read-modify-write candidates.

**All seven now carry a `loader` field.** `c30738d77` ("sweep the 34 census rows that had never
been asked the loader question") landed the whole sweep: 46 of 46 disposition rows are annotated,
six carriers were repaired, and `tests/background/test_the_census_rows_that_had_never_been_asked_the_loader_question.py`
holds 36 tests over those six.

Per the standing rule that a deferral's stated precondition is a proxy that expires — **evaluate
the hazard, not the proxy.** The hazard the direction was pointing at is not "rows without a
`loader` field". It is "carriers whose absent-vs-unreadable behaviour nobody has measured". Those
are not the same set any more, and the difference is where the risk moved.

## Where the hazard actually is now

Of the 34 rows swept, **six were measured with a live-prior control leg and repaired, and they
are the six the test file covers.** The other **27 carry a bulk annotation** whose load-bearing
sentence is identical across them:

> ASKED AND CLEAN — measured across the whole partition
> (missing/empty/truncated/null/mapping/list-of-ints/bare-string) against a live prior, **no state
> raises and none is a read-modify-write.**

That is a checkable claim, asserted 27 times, and **nothing on disk opens it.** No test names any
of those 27 carriers. The claim's own words say what would falsify it, which is what makes this
worth an hour rather than an argument: *is a single function reading and writing the same state
path*, and *does the write's content derive from the read*.

This is the shape the record already names twice — *a refusal that cites an artefact has made a
checkable claim and nothing opens it*, and *a control derived from a register is blind to rows the
register never classified*. Here the register classified them; it just classified 27 of them in
one pass, by hand, in the same turn that found six defects in the other seven.

## The measurement, and what I predict before running it

**Instrument.** A read-modify-write detector over the census's own AST facts: for every
disposition row, the set of functions in `background/` and `tools/` that BOTH read and write that
state key. The census already derives reads and writes per function per key
(`_FunctionScan`), so the detector is a projection of an existing derivation, not a new lexicon.
A function-level read+write is a **candidate**, not a verdict — an overwrite whose content does
not derive from the prior read is not the harm. Each candidate gets the daemon read, not the row.

**Why this and not re-running the partition by hand on 27 carriers.** The partition harness is
per-carrier code; 27 of them is a turn spent on the flattering half. The RMW clause is the half
whose failure is SILENT — the six defects found so far split into "crashes a daemon" (loud, gets
found) and "destroys a record and reads afterwards as *not yet measured*" (silent, does not). The
detector goes at the silent half first.

**PREDICTION, recorded before the run:**

1. The detector finds **at least one** carrier among the 27 "ASKED AND CLEAN" rows where a single
   function both reads and writes the same key. Confidence **60%**. Reason: 34 rows read by hand
   in one turn, and the six that got the live-prior treatment are the ones the author ranked
   first — the tail is exactly where a hand pass thins out.
2. If one is found, I predict it is **more likely a pure-overwrite false positive than a real
   RMW** — roughly 2 in 3 — because "reads then writes" catches every load-then-save daemon.
3. I predict the detector **also flags at least one of the six already-repaired carriers**
   (`run_history.json`, `.wedge_suspect_hit_rate.json`, `.harden_cooldown.json`). If it does not,
   the instrument is broken and the run is void — **this is the vacuity leg, and it is asserted
   before the novel result, not after.**

**What would make me wrong and how I will say so.** If every one of the 27 comes back clean, the
finding is "the bulk annotation was true", the claim gets discharged in the disposition file with
the instrument named, and the 27 rows stop being unopened. That is a real outcome and it will be
written beside this prediction, not instead of it.

**Done means:** every candidate the detector raises has been read at its daemon and resolved
either as a repair or as a named non-defect, and the instrument that settles it is committed —
so the next session inherits an answer instead of 27 sentences of prose.

---

# RESULT, written beside the predictions and not instead of them

**Measured 2026-09-05, same turn. Full write-up:
`SEAT_FINDING_THE_CENSUS_LOST_FIVE_HITS_TO_THE_REPAIR_THAT_FIXED_THEM_2026-09-05.md`.**

| # | prediction | outcome |
|---|---|---|
| 1 | ≥1 of the 27 is a read-modify-write (60%) | **WRONG.** 2 candidates raised, both false positives on the daemon read. The bulk annotation held. |
| 2 | a found candidate is more likely a pure-overwrite false positive (2 in 3) | **RIGHT**, and at 2 of 2 rather than 2 of 3. |
| 3 | the detector also flags the already-repaired carriers, **or the run is void** | **The instrument was broken, and this leg is the only reason I found out.** It flagged **1 of 6**. |

**Prediction 3 is where the whole turn turned.** Had it been written after the answer — or not
written at all — the honest-looking output was "27 rows re-measured, all clean", published off an
instrument that could not see five of the six defects already known to exist. Instead the void
verdict forced the question *why does it under-report*, and the answer was the finding: the
census attributes state files by module-level symbol, so the sweep's own repair — routing every
read through `background/episode_prior`, whose loaders take the path as an argument — **deleted
five carriers from the census that found them**, 34 hits to 29, with `run_history.json` on zero
recorded readers.

So the answer to "are the 27 checkable claims true" is **yes**, and it was the wrong question.
The claim nobody had made was the one that failed: that the census could still see the carriers
it had already been used to repair.

**What this pre-registration got right structurally, and worth keeping:** the falsifier was named
before the run (*"is a single function reading and writing the same state path"*), and the
vacuity leg was asserted **before** the novel result rather than after it. Both are cheap. One of
them was load-bearing.
