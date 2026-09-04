**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING — an unattributed publish failure named no reason, on three of its four branches

LATENT, and deliberately not higher: no published figure is wrong because of this. It is a
diagnostic that misroutes readers — and it misrouted this turn's own direction, which is how
it was found.

**Filed:** 2026-09-04, delivery seat (isolated worktree). **Repaired in the same commit.**

**Discharged:** `tests/background/test_a_publish_failure_names_which_of_the_three_it_was.py::test_no_failure_branch_records_an_unattributed_verdict_with_no_reason`

---

## The record, as a reader found it

`docs/observability/.publish_gate_state.json`, shared tree, 2026-09-04 11:18:50Z:

```json
{"cause": "unattributed", "cause_evidence": "", "git_hash": "3d369242c",
 "kind": "test_regression", "rc": 1,
 "reason": "process_run_complete rc=1 on run_complete_20260904T104410Z.md"}
```

`"we cannot tell"` — which this project treats as a result — **with nothing at all saying why.**
That is the one shape `CLAUDE.md`'s rule on refusals forbids: *write refusals that name their
reason*, because naming the reason is how you discover the refusal itself was wrong.

## Why it was empty

`record_publish_gate_failure` stored `str(cause_evidence or "")`. Exactly one of its four
failure-producing branches passes a cause at all — the `rc=77` (`EXIT_PUBLISH_DID_NOT_LAND`) one,
which consults `publish_cause.read_cause`, and that function's contract is that it **always**
returns a sentence, on the attribution and on the refusal alike. The other three — `rc=78`
(`gate_timeout`), `rc=79` (`tree_lock_unavailable`), and the generic fall-through that catches
`rc=1` — passed neither field, so the record read `unattributed` / `""`.

The prose was never the problem: `_fire_publish_gate_alert` already falls back to
*"no cause record was available"*. The **record** did not — and the module's own comment beside
the green-test suppression says why that is backwards:

> *Suppressed at the RECORD, not only in the alarm prose, because the record is the thing that
> gets quoted.*

Same reasoning, one field to the left, not applied.

## The class, and it is one this repo has already catalogued

The property *"an unattributed failure says why"* was **already under a control** —
`test_an_unattributed_failure_says_so_rather_than_guessing`, whose docstring calls itself THE NULL
CONTROL. It is a good control. It just holds the property for `rc=77` only, which is the single
branch where the property was never at risk, because that branch gets its sentence from
`read_cause` for free.

So the property was **true where it was tested and false everywhere else** — this repo's own
*"a fix that removes one cause of a silent absence leaves the absence itself"*, and the reason the
repair is one control over the whole partition rather than a fifth parametrised row.

## What it cost, concretely

This is not hypothetical misdirection; it is measured, and the victim was this turn.

The `unattributed` cause is also what gates the green-test suppression:
`publish_cause.no_test_was_judged(UNATTRIBUTED)` returns `False` **deliberately** (fail-safe
toward *showing* the blocking list — a documented, and I think correct, trade-off). So an
unattributed cause carries a blocking list forward, and the seat brief that produced this turn's
direction quoted `blocking_tests` and sent me at
`site/test_the_site_lane_runs_no_untracked_control.py` — a wedge already resolved: `site/harness/`
is tracked at HEAD, `git status --porcelain site/` is clean, and a publish landed `rc=0` at
10:53Z. Roughly the first third of this turn went on establishing that the direction's premise was
stale. A record that said *why* it could not attribute would have cost one line to read.

## What is NOT claimed

- **Not** that the census was wrong. I pre-registered that it was, and **the prediction was
  refuted**: `test_the_worker_log_does_not_pass_off_library_noise_as_a_diagnosis` was genuinely
  red at `3d369242c`, and red at HEAD at the failure instant. See
  `SEAT_PREREG_WAS_THE_NAMED_BLOCKING_TEST_ACTUALLY_RED_AT_THE_COMMIT_STAMPED_BESIDE_IT_2026-09-04.md`.
  The census did its job.
- **Not** that `no_test_was_judged(UNATTRIBUTED) == False` should change. It is argued for in the
  module and the argument holds; this repair makes the *unattributed* verdict legible, which is
  the half that was missing.
- **Not** that the cause should be inferred on these branches. See below — that is the trap.

## The repair, and the trap it deliberately does not step in

`background/process_run_complete.py`: when no observation is supplied, the record now carries a
named reason instead of `""`, distinguishing "this exit path names no cause" from "a cause was
named without the observation that decided it".

**The cause itself is still not invented.** The obvious-looking fix — have these branches read
`PUBLISH_CAUSE_FILE` too — is wrong, and `publish_cause`'s own doctrine says so: *the evidence is
OBSERVED, never inferred from the exit status*. The publisher reaches `rc=1`/`78`/`79` precisely
when it did **not** observe one of the five named causes, so any record sitting at that hash is a
different cycle's, and attributing it is the carried-forward defect wearing a new field name. The
honest `unattributed` stands; it now says why. Live-case check: the cause record on disk was for
`git=16a646e81`, not `3d369242c` — so reading it would have attributed one cycle's failure to
another's evidence.

## The control

One control over the whole partition, per `CLAUDE.md` (*"write one control over the whole
partition rather than a leg per branch"*), and it asserts **reachability first**: four rcs must
still yield four *distinct* `kind`s, so a mutation that routed everything through the `rc=77`
branch — which would make the evidence non-empty everywhere and pass every other assertion —
reds instead of silently deleting three diagnoses.

**Mutation-proven, not asserted.** Disabling the backstop reds it, and it reds on `rc=78` /`79`
/`1` while the `rc=77` row still passes — which is the evidence that the property was partial
rather than absent:

```
E  AssertionError: rc=78 (gate_timeout) recorded `cause` = 'unattributed' with an EMPTY reason
1 failed, 16 passed
```

---

## Recording the substitution, as the direction asked

The direction said: *"If the wedge has moved to a different test, fix that one and record the
substitution."* It moved twice, and **neither surviving wedge was mine to fix**:

| | wedge | state at this turn |
|---|---|---|
| as briefed | `site/test_the_site_lane_runs_no_untracked_control.py` (untracked site controls) | **already resolved** — `site/harness/{test_the_deployment_reading_reaches_the_reader.py,_render_harness.mjs}` are tracked at HEAD; `site/` clean |
| as recorded | `test_the_worker_log_does_not_pass_off_library_noise_as_a_diagnosis` @ `3d369242c` | **real, and already fixed by another lane** in `e78e17581`, 4 min after the failure was stamped; green at HEAD `4d1d6298c` (24 passed), green in the shared tree |

And the publisher **is moving**: `rc=0` publish at 10:53Z closed the zero-progress episode and
drain-superseded 10 markers; `process_run_complete.py` was running on the newest marker throughout
this turn. The four-hour outage the direction describes had ended before the turn began.

The one thing left that was nobody's and still live is the empty `cause_evidence` — the field that
sent the brief to the wrong wedge in the first place. That is what this commit repairs.
