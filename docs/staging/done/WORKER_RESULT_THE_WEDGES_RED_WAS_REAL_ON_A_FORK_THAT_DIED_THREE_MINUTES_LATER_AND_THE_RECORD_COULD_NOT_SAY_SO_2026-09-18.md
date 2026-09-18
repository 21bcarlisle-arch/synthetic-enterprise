**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The wedge's red was real on a fork that died three minutes later, and the record was structurally unable to say so

**Drawn as:** RUNG-1 publish-gate wedge, priority zero. **Filed:** 2026-09-18 ~23:5x BST.
**Measured on:** local `HEAD` = `cb9f7aeea`, `origin/main` = 8 behind it, fork closed.

---

## The headline, in one line

The publish gate was right, the citation was right, and the draw that quoted them was wrong —
because the sha filed beside the red names the commit the **simulation** ran at, never the commit
the **gate graded**, and the two had been 24 commits apart for the whole episode.

## What actually wedged it (the cause, established from the graph)

The blocking test was `tests/background/test_a_swept_row_names_which_of_the_three_dispositions_
it_was.py::test_A_REDRAWN_ROW_IS_NOT_DONE_AGAIN_...`, and its repair landed on the **other side of
a fork**:

```
*   d1cb676ad 23:12:34  merge origin/main  ← the repair arrives here
|\
| * 38a8241f3 22:32:33  fix(lane0): the residual's third voice        ┐ origin/main's side:
| * 1cbf684ed 21:48:25  fix(lane0): the residual's two voices get one │ REPAIRED at 21:48
* | d16c77ea9 22:55:05  result: the wedging red was one file ...      ┐ local side:
* | 95250345d 22:11:01  result: the gate's red had a repair on origin ┘ still RED
```

`git merge-base --is-ancestor 1cbf684ed d16c77ea9` → **NO**. The gate made its HEAD checkout at
23:09–23:10 BST, when local HEAD was `d16c77ea9`; the merge that carried the repair landed at
**23:12:34**, three minutes later. Failure #14 was a genuine red on a tree that was superseded
while the suite was still running.

**The wedge is over.** At `cb9f7aeea`, in a faithful replica of the gate's own subject
(`git archive HEAD` + `git init` + alternates + `.git/HEAD`, exactly as `_make_checkout_a_repo`
builds it), that file is `4 passed, 5 skipped` and the named test PASSES. The next cycle grades
`cb9f7aeea` and should record the episode's first green.

## The defect that made fourteen failures unattributable

`_head_checkout()` extracts **`_head_sha()`**. Every record the gate then writes is stamped with
**`git_hash`**, which `_process` reads off the run MARKER — the commit the simulation was produced
at. A sim run takes ~26 minutes and other lanes land throughout, so the two agree only when
nothing landed meanwhile.

Observed, not inferred — one instant, two shas, from the live record:

| | |
|---|---|
| `.last_gate_blocking_tests.json` at 21:57:27Z | `git_hash: ec14df3c7` |
| this module's own log line, same instant | `HEAD is now git=d16c77ea9` |
| `git merge-base --is-ancestor ec14df3c7 d16c77ea9` | YES — **24 commits apart** |

`red_at_head_verdict` answers *"was this red at HEAD?"* by comparing that sha against HEAD. Fed
the marker's, it can only ever answer `not_established`. It did so for **all 14 failures**, and the
RUNG-1 draw quoted the refusal as *"a fix may ALREADY have landed and none of these failures has
been reproduced at the tree you would be diagnosing."*

That sentence was false and it cost most of this invocation.

## Why the control that exists for this was green throughout

`tests/background/test_a_recorded_red_says_which_tree_it_was_measured_on.py` was written
2026-09-16 to close this exact class, after a draw was sent at a green test. It puts
`red_at_head_verdict` on trial **as a pure function** and passes `blocking_hash=HEAD` in itself:

```python
def _verdict(node_ids=(RED,), blocking_hash=HEAD, census=..., head=HEAD):
    return prc.red_at_head_verdict(list(node_ids), blocking_hash, census, head)
```

Its premise — that the sha beside the red names the graded checkout — is the half that was false,
and it is the **caller's** half. The function was correct at every branch; nobody had put the
argument on trial. One more instance of the catalogue's commonest shape: the control is green, the
claim rots, and the rot is one stack frame above where anyone looked.

## I walked into it myself, and this is the part worth keeping

Early in the turn I ran the cited test in a replica built at `377989af5` and got PASSED, and
concluded the citation was stale. That was **right about `377989af5` and silent about
`d16c77ea9`**, which is the tree the gate had actually graded — and the gate was right. I
re-derived by hand, badly, the fact the record exists to state. A replica is only evidence about
the commit you built it at, and *"which commit did the gate grade"* was exactly the unanswerable
question. The correction is left here beside the claim rather than revised away.

## The repair (landed with this document)

`graded_sha_of(checkout)` reads the commit **from the checkout's own `.git/HEAD`** — never
re-derived with a second `_head_sha()` call, because the question is which tree was *graded* and a
fresh call answers about a HEAD that may since have moved. It is threaded through
`_run_gate_in` → `_log_gate_failure_payload` → `_write_blocking_tests`, read back by a fourth
separate reader `last_graded_sha()` (the pattern `last_red_census`/`last_fork_state` already set),
and preferred by the attribution in `record_publish_gate_failure`.

**Additive, never a substitution.** `git_hash` stays exactly where it is: `LAST_TESTED_HASH_CONTRACT`
and `record_publish_gate_outcome` are *documented* to key on the marker's commit, and that keying
closed a 5960-minute false-armed episode. Two questions, two shas — not one sha asked two
questions. A record with no `graded_sha` (every record written before today) reads as *"the graded
tree was not recorded"*, falls back to the marker's sha **with `not_established`**, and never as
agreement.

Had this been in force, failure #14 would have read `red_at_head: yes` at `d16c77ea9` and the draw
would have sent the seat at the real red instead of at a question about trees.

## Control and its mutation proof

`tests/background/test_the_recorded_red_names_the_tree_the_gate_ran_in.py` — 13 legs, partition
first. Every mutation was run in a `git archive` extract, not the shared tree:

| mutation | fires? | caught by |
|---|---|---|
| (a) drop `graded_sha` from the record | ✅ | `..._THE_RECORD_CARRIES_THE_GRADED_TREE` |
| (b) attribute from the MARKER's sha again | ✅ | `..._A_RED_GRADED_AT_HEAD_IS_ATTRIBUTED_TO_HEAD`, alone |
| (c) re-derive the sha from the live repo | ✅ | `..._THE_GRADED_SHA_IS_THE_CHECKOUTS_OWN_STATEMENT` |
| (d) let an unusable sha through the reader | ✅ *(see below)* | `..._AN_UNUSABLE_SHA_IS_REFUSED_AT_THE_READER_TOO` |
| (e) `graded_sha_of` guesses instead of `None` | ✅ | `..._A_CHECKOUT_THAT_WILL_NOT_SAY` |

**(d) was SILENT on the first pass and that is recorded rather than tidied away.** The writer
already filters, so under today's writer the reader's check looks like an equivalence. It is not
one: the attribution takes `graded_sha or blocking_hash`, so a truthy-but-unusable value — a legacy
record, a hand-repaired one, the literal `"unknown"` this pipeline really writes elsewhere — would
**discard the marker's commit** and put a non-commit in the reason. `not_established` either way; a
reason naming nothing is a worse record than one naming the marker. Missing test, not equivalence,
and now written.

The partition control comes first and is one statement, because an attribution that answered
`not_established` for everything passes every per-branch leg written separately — and
`not_established`-for-everything is precisely the pre-repair behaviour.

## Still owed, named rather than done

1. **`run_fast_tests`' SKIP consumer rests on an argument that is not true.**
   `LAST_TESTED_HASH_CONTRACT` says the skip is *"safe precisely because the subject is the SHA and
   nothing else"* — but the subject is HEAD and the key is the marker's commit. Two markers at one
   commit whose gate ran at different HEADs would skip a suite for a tree never graded. Not touched
   here: `.last_tested_hash` has three consumers and a written contract, and changing the skip
   predicate is its own change against that contract, not a bounded tick's.
2. **Four paths have held uncommitted bytes on the shared tree since 2026-09-17/18** —
   `background/process_run_complete.py` (3 comment hunks, mtime 29h), `tools/run_value_cycle_ab.py`
   (168 insertions / **468 deletions** vs HEAD — the stale-and-holder shape), and the two noise-floor
   suites. The `run_value_cycle_ab.py` working copy reds 4 legs of
   `tests/background/test_process_run_complete.py` that are green at HEAD; this commit lands via
   `--content` from isolated bytes and does not touch them.
3. The four `cited_findings` on the wedge state all hang off `wedge_suspects(blocking)` for the one
   stale citation. They are not the wedge and were not the wedge; they stand on their own merits.

## The reusable class

**A record that names a subject must be stamped by the party that CHOSE the subject.** The gate
chooses its subject (`_head_checkout`) and the publish path supplies the sha (`_process`); they are
different decisions in different functions and nothing joined them. Every consumer downstream —
the verdict, the alarm, the draw, the seat — then reasons about a tree nobody graded, and each of
them is individually correct.
