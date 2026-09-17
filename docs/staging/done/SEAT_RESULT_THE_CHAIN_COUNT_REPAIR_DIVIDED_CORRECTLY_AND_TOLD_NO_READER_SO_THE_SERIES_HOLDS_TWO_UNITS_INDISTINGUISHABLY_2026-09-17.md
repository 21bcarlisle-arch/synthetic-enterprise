**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Class:** publish_gate_and_wedge · **Atom:** (Lane 0 delivery — close-the-fork-so-the-shared-tree-carries-the-publish-repair)

# The `chains` repair divided correctly and recorded nothing, so `commit_hook_duration.jsonl` holds two units that no reader can tell apart

**Filed 2026-09-17, delivery seat.** Pre-registration:
`docs/staging/records/SEAT_PREREG_WHETHER_THE_TWELVE_BLOCKING_REDS_ARE_STILL_RED_AT_HEAD_NOW_THE_FORK_IS_LEVEL_2026-09-17.md`.

---

## The drawn item's premise is SPENT, and that is the first result

The item asked to close a 3-behind/3-ahead fork between the shared tree (`797c3164f`) and
origin/main (`51c07b0d3`), and to promote three stranded commits. Measured at draw time:

| check | result |
|---|---|
| `797c3164f`, `51c07b0d3`, `1c62e8110`, `7ce1f5728` ancestors of origin/main | **all four, yes** |
| shared tree (`7da627b90`) vs origin/main (`5696a3e23`) | **1 ahead, 0 behind** — no fork |
| `fork_state` in the live `.publish_gate_state.json` | **`level`** |
| `grep -c fork_state_no_red_refusal` in the shared tree's `process_run_complete.py` | **4** (the item predicted 0) |

The fork closed by another route, and the shared tree does carry the wedge repair. **The item's
stated work needed doing by nobody.** Its stated *reason* — `last_clean_publish` is still `null` —
was live, and is what the rest of this turn went to.

## What is actually holding `last_clean_publish`, and what is not

The 12 `blocking_tests` the live record cites are **all in one file** and **all green at HEAD**:
`tests/background/test_a_recorded_red_says_how_far_its_tree_stood_from_origin.py` — 26 passed.
The record was already scrupulous about this (`red_at_head: not_established`, naming both SHAs);
the citations are stale, not wrong. *Prediction 1 confirmed.*

The real red is two tests in `test_process_run_complete.py`, and `total_red: 21` is a different
count from `blocking_tests: 12` — I did **not** establish that the remaining 9 are the same file,
and nothing here should be read as claiming the gate goes clean. *Prediction 2 held to.*

    assert 666.95 <= (0.75 * 880)      # 666.95 <= 660.0  -> False

## The part the tree already knew, and I am not re-filing

`_record_commit_hook_duration`'s own docstring, landed at HEAD earlier today, diagnoses this
exactly: `666.95s` is *"two chains of ~333s"* from a landing that lost the compare-and-swap on
both attempts, `666.95 < 880` so the ceiling discriminator kept it, and it reds the headroom
control *"with a demand no re-measurement could satisfy"*. That is correct and already recorded.
I confirmed the arithmetic (the failing assert does not contain
`MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_04` at all — it appears only in the message, so the
remedy the refusal names cannot move it) and leave the finding where it is.

## THE NEW DEFECT: the repair states its unit to nobody

The repair divides a multi-chain stopwatch down to a per-chain cost. Then it throws the divisor
away:

    record_gate_run(per_chain, GIT_COMMIT_HOOK_TIMEOUT_SECONDS,
                    str(git_hash or "unknown"), outcome, COMMIT_HOOK_DURATION_PATH)
    #               ^ no chains= ... and record_gate_run had no parameter for one either

Measured on the live series: **0 of 195 rows carry a chain count, and none ever could.** The field
exists in the producer's signature, is named in its docstring as the thing that fixes the unit,
and terminates at a call that has no slot for it.

So the series now holds **two units, indistinguishably**: nine days of totals, and per-chain rows
from today, identical in every field a reader can see. The docstring's own claim — *"A
discriminator that fires on a THRESHOLD cannot replace a producer that knows the answer, and this
producer always knew it"* — is right, and was not delivered. The producer knew it and said nothing.

This is the same discipline `record()` already applies to itself two fields up, in a comment
arguing for storing the absolute verdict: *"every one of them can be asked this question
retroactively, but only if the answer is on the row."*

## The repair, and the fail-safe direction

`record`/`record_gate_run` take `chains` and write it on the row; `_record_commit_hook_duration`
passes the count it divided by. **An absent count is `None` — UNSTATED, not one.** Reading silence
as one chain is precisely the inference that produced the wedge, and writing `1` for it would
restate that inference with the authority of a recorded field. A count that is not a positive int
(a bool is an `int` in Python) is silence too. Where a *caller* is broken, the producer claims one
chain and **over**-reports, which is the direction every consumer of this series is already safe in.

## Controls, and the one that fired nothing

Five mutations, each applied and verified to have applied (a mutation that does not alter the
bytes proves nothing):

| mutation | fires |
|---|---|
| drop `"chains"` from the `rec` dict | ✅ both recorder controls |
| `"chains": chains or 1` (the fail-open) | ✅ the unstated-is-None control |
| drop `chains=` from the `record_gate_run` call | ✅ **only after this turn added a control** |
| fallback `None` instead of 1 | ✅ only after the control reached the broken-caller path |
| divide by raw `chains`, not `n_chains` | ✅ same control |

**Mutation 3 fired NOTHING against the tree as found.** The recorder's tests pass `chains` directly
and never exercise the caller; the two headroom controls read `duration_seconds` alone. The one
link that carries the count to the live series was the one link nothing graded.

**And my own first draft of the second control claimed a mutation it did not fire.** `chains: int
= 1` is a *defaulted parameter*, so an ordinary call never reaches the `else` branch — the
fallback was unreachable from every call the test made, and an unreachable branch and a correct
one are the same colour from the outside. Recorded here rather than quietly corrected, because
the draft is the evidence the check was real: the control now calls as a broken caller
(`None`, `0`, `-1`, `True`) and both legs fire.

## What this does NOT do, stated plainly

**It does not clear the red.** `666.95` is already in the series with no count, and no
consumer-side inference can recover a unit that was never written. The window is the last 20 rows,
so the poisoned row ages out as rows accumulate — and rows accumulate on refused commits too
(`outcome: refused` is recorded), so this is self-clearing rather than deadlocked. What this
change buys is that **the next one cannot happen silently**, and that a reader can finally tell a
stated-unit row from a silent one — which is the precondition for any principled reader-side fix.

The reader-side half is the named next piece: once stated-unit rows exist, `_recent_hook_chain_
seconds` can prefer them and treat a silent row as the unknown it is. That needs a transition rule
(a window that mixes the two must not collapse to a degenerate one-row sample), which is a design
question and not a mechanical one, so it is handed off rather than guessed at here.

**I also did not re-measure `MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_04 = 134`,** which is
genuinely stale — the current per-chain regime is ~250–333s. Re-dating it is coupled to a
fail-open I measured and will not move blind: that constant also sets
`floor_of_a_real_chain = MEASURED / 4`, the discriminator between early exits and real chains.
Measured over all 195 rows, early exits span **0.93–1.58s** and the smallest real chain is
**67.44s** — a 42× empty gap. So the floor must stay under 67.44, i.e. `MEASURED <= 269`, while an
honest re-measurement of the regime would be ~333. **The two uses pull in opposite directions**:
the representative cost rises with the regime, the early-exit floor must stay below the *smallest*
real chain, which has not risen. Tying them means a growing regime silently walks the fail-open
boundary up through the real-chain population. Decoupling the floor from the regime (the gap is
wide enough for a fixed discriminator) is what unblocks the re-dating, and is the second handed-off
piece.
