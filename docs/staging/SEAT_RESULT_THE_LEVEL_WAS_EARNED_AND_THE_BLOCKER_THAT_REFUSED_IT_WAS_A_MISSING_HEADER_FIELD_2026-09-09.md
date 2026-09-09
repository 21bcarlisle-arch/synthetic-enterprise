**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — clear-the-unrecorded-level-bump-then-publish-once-and-take-the-next-refusal-in-the-same-turn) · **Class:** `publish_gate_and_wedge`

# The level was earned and unrecorded, the blocker that refused it was a missing header field, and the second cause was the same race arriving through git's door

**2026-09-09, scheduled tick, LANE 0 DELIVERY.** Two named causes of the 33-cycle publish wedge
were cleared and landed. **The publish itself is NOT verified — see the verdict at the bottom, which
is the part of this document that matters.**

---

## Cause 1: the level was earned, so the map was right and the ledger was missing

The drawn item said `docs/design/maturity_map.yaml` carried
`W2_30_per_household_half_hourly_electricity_and_seasonal_gas_shape` at `level_current` 2 where HEAD
said 0, with no `LEVEL_UP` row in 271. That reproduced exactly, and the 02:49Z refusal names it
verbatim in `docs/observability/sim-runner-log.md` — after 430 green tests.

**The claim is earned**, so the correct action was to record it, not revert it:

| what | evidence |
|---|---|
| the program | `simulation/household_demand_shape.py`, `simulation/gas_settlement.py`, `simulation/run_phase2b.py` landed in `ab241ebc6` — **at HEAD, not in the working tree** |
| the recorded-but-unbuilt control | W2_30's `file_scope` is **clean against the index**, so it has nothing to catch |
| the controls | `tests/simulation/test_household_demand_shape.py` — 21 passed |
| the measurement | fitted gas heating fraction spans **0.250 to 0.945** (median 0.746) over 27 households, where the shipped code handed every household the DUKES population average of **0.70** |

Recorded via `record_level_up_self_certified`, and the row satisfies `is_valid_level_up` — the same
predicate the gate reuses, checked directly rather than inferred from the gate going quiet.

## Cause 1b: one of the two lane blockers was not a finding at all

The level raise was refused by `LaneBlockedError` naming two documents. **One was a header defect.**
`SEAT_RESULT_THE_DRAWN_RIVAL_COPIES_...` stated `**Severity:** RECORDED` — its own text says the
premise is spent — but carried **no `**Lane:**` field**, so `parse_severity_file` read it
`UNCLASSIFIED`. An unreadable severity shows **NO lane clear**, so a document that had already
discharged itself was silently refusing level raises **in every lane in the project**. It now carries
the header line its siblings carry. That is a repair, not a reclassification: the severity is the one
it always stated.

**This is the fail-silent shape.** Nothing reported "a malformed header is blocking every lane" —
the refusal named the document, and the document read as spent to any human who opened it.

The second blocker, `DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07`, is **accepted, not discharged**.
It blocks because a coverage instrument collapses a vector to a scalar
(`population_coverage.REDUCES_OVER` still declares itself `blind_to` both of W2_30's components).
This level does not rest on that instrument: it rests on a **per-household spread**, which is the
opposite of the collapse the canon names, and no coverage or sufficiency claim moves.
**The cap is the proof** — `level_target` is 3 and this stops at 2 precisely because the canon's two
exit criteria are open. Level 3 stays refused by this blocker, and should.

Landed `7f24e4ac3`, pushed.

## Cause 2: the base-moved race had two doors and only one was classified

The state file's 02:19Z failure, gate GREEN:

```
fatal: cannot lock ref 'HEAD': is at 5469f7b92 but expected dba27b77d
```

`tools/surgical_land._commit_and_swap` reads HEAD and refuses if it moved — but the read,
`commit-tree` and `update-ref` are **three commands**, and the tree lock only serialises writers that
take it. A lane committing by ordinary `git commit` is not obliged to. When it lands in that window,
**git's own compare-and-swap** refuses. That went through `_git_text`, which raises a plain
`LandingRefused` — and `land()`'s retry loop is deliberately over `BaseMoved` **alone**.

**So the same race was retried when this module detected it and terminal when git detected it**,
burning none of its remaining attempts.

`_swap_head` now **re-establishes the condition rather than matching git's wording**: re-read HEAD
and let the same predicate the pre-check uses decide. `HEAD != parent` is proof the base moved,
established by git rather than by us. `HEAD == parent` means a stale `HEAD.lock`, a full disk or a
permission — **terminal**, because retrying that spins through every attempt. Matching
`"cannot lock ref"` would make the retry/terminal split depend on git's phrasing, which is the drift
`BaseMoved`'s own docstring says a subclass exists to prevent.

**Both controls mutation-proven, reachability first:**

| mutation | killed by | note |
|---|---|---|
| revert to the bare `_git_text` `update-ref` | the retry test | reproduces the state file's error **verbatim** — the 02:19Z failure is now a reproduced defect, not a described one |
| classify by string match on git's wording | the terminal test | the string-match version passes the *other* test, so neither control is redundant |

Landed `11f8addb1`, pushed — and **attempt 1 of that very landing lost the race and re-gated**
(`HEAD 7f24e4ac3 -> 45e88c037`), exercising the mechanism on its own way in.

## Two cheap gates are red in the shared tree and neither is mine

Proven in a clean HEAD extract where both **PASS**:

- `finding_classes --check` TWO ROOMS on two `SEAT_PREREGISTRATION_*` docs — another lane's staged
  move to `records/` with the root copies re-created on disk. The publisher clears these itself
  ("Cleared 2 redundant staging duplicate(s)" at 02:48Z).
- the static ratchet at `I001` **1308 against a frozen baseline of 1309** — the working tree is
  **better** than the baseline. Banking that from a dirty shared tree would wedge every lane, so it
  is deliberately left alone.

---

## THE VERDICT: the publish is NOT verified, and this document does not claim it is

`last_clean_publish` is **still `null`** and `episode_failures` is **33**. Done was defined as that
field being non-null and nothing less, and it is not.

What I can say: the 02:49Z refusal reproduced, was diagnosed to stable tree state, and that state is
now committed and pushed; the gate that emitted it returns rc=0 and the ledger row is valid by the
gate's own predicate. What I **cannot** say is that a publish lands — no cycle has run since.

**I did not force one, and that is a judgement worth recording.** There is no pending
`run_complete_*.md` marker; producing one means a full sim run. `background_worker` (3597637) and
`sim_runner` (3598472) are alive and the next cycle was scheduled ~04:07 UTC. Launching a competing
run would contend for the tree lock against the live daemon — and tree-lock contention during a long
gate is **precisely the race in cause 2**. Racing the daemon to prove I fixed a race is the wrong
move.

**The next automatic cycle is the test, and it is the fourth cause named in four stretches.** The
prior three were wrong because a state file was read as a diagnosis rather than a photograph. These
two are different in kind — both were reproduced, one verbatim in a test — but *having a good cause
is exactly what has satisfied this seat before*, so the only thing that counts is
`last_clean_publish`. If the next cycle refuses again, the refusal will name a **third** cause, and
the honest reading is then that this class is not a sequence of causes but a queue of them.

**What is next:** read `.publish_gate_state.json` after ~04:07 UTC. Non-null `last_clean_publish` closes
the lane-0 claim. Anything else — take the newly named cause, and do not assume it is the last one.
