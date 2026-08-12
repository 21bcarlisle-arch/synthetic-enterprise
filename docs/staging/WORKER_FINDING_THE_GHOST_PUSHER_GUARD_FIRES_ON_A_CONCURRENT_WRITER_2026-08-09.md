# [WORKER-FINDING] The GHOST PUSHER guard cannot tell a test's commit from a concurrent writer's, so the publish gate wedges itself whenever a worker commits mid-run (2026-08-09)

**Severity:** LATENT · **Lane:** H_harness

**Found during:** the ~10h publish-wedge unwedge, while running the gate's own argv without `-x`.
**Disposition:** QUEUED, not fixed on sight. The fixture's own message says *"Isolate it; do not
silence this fixture"* — and it is right, which is exactly why the fix is not mine to improvise
during an incident. **Not blocking today** (the gate is green without it), but it is a live,
recurring wedge source.

## Observed, with evidence

The full publish-gate suite (22,525 passed, 612s) ended with:

```
ERROR at teardown of test_trading_hedge_annual_has_hf_key
E   Failed: GHOST PUSHER: this test session moved the REAL repo's HEAD.
E     83c2bce93 -> 7f6b7f3ba
E     commit(s) manufactured:
E       7f6b7f3ba D14: the world could not produce an innocent drop, so the false-alarm rate was 0.0000 by construction
```

The guard (`tests/background/conftest.py:165-171`) is:

```python
@pytest.fixture(autouse=True, scope="session")
def _no_test_may_commit_to_the_real_repo():
    before = _real_repo_head()
    yield
    _assert_head_unmoved(before, "this test session")
```

It snapshots HEAD once and compares once, **at session teardown** — so its window is the whole run.
Anything that moves HEAD inside that window is attributed to the test session.

**`7f6b7f3ba` was not manufactured by a test.** It is a substantive D14 build commit — a full
multi-paragraph message describing `simulation.self_rationing.DropConfounder`, four anchored
incidence rates, a false-flag rate moving 0.0000 → 0.0560, and a denominator fix. Its timestamp is
`2026-08-09 13:04:09 +0100`, inside the 12:55–13:05 run window. A `claude -p` scheduled-tick worker
whose standing instruction is *"do the drawn work on REAL disk/git state, **commit it via
tree_lock**, then STOP"* is demonstrably running that loop on this box (PID 1296997 observed at
13:06 running the next invocation).

So: **observed** — the guard fired, and the commit it named is real build work, not test output.
**Inferred** — that the scheduled-tick worker made it. I did not catch the committing process in the
act; the attribution rests on the message content, the author/timestamp, and the loop being live.

## Why this is a wedge source, not a curiosity

The publish gate runs this suite on every cycle and takes ~10 minutes. The autonomous worker commits
several times an hour. Every overlap turns a **green** suite into gate `rc=1`, and
`record_publish_gate_failure` books it as a `test_regression` — indistinguishable in the alarm from a
real red. Today's episode was caused by genuine reds; this one would produce the same alarm with
nothing wrong.

It also inverts the control's own purpose. The named defect is *"a test reached a
credential-holding publish path on the real tree"* — a property of **one test**. The check is scoped
to **the session**, so it reports a true statement ("HEAD moved") as a false one ("a test moved it"),
and the remedy it prints (`monkeypatch.setattr(<module>, "PROJECT_DIR", tmp_path)`) points at a test
that is innocent. R9, applied to a control: it asserts an actor it has no evidence for.

Note the per-test sibling fixture immediately below it (`_this_test_may_not_commit_to_the_real_repo`)
does not have this problem — its window is one test, so a concurrent commit is far less likely to
land inside it, and when it does the blast radius is one test rather than the whole gate.

## What closing it looks like

1. **Attribute, don't infer.** The session guard should distinguish "HEAD moved" from "a test moved
   HEAD". The cheapest discriminator already exists in-repo: commits made by the test path go
   through a known code path, and real lane commits hold `tree_lock`. Recording the committing PID
   (or asserting the commit is absent from the reflog entries the session itself produced) turns the
   verdict from an inference into an observation.
2. **Keep it fail-loud, narrow the claim.** If the session guard cannot attribute, it should say
   "HEAD moved during this session, by an unidentified writer" and **not** fail the publish gate —
   or fail it under its own distinct `kind` so the wedge alarm does not mislabel a concurrency
   collision as `test_regression`.
3. **R15:** the mutation it must still fire on is a test that really does commit to the real tree.
   Any narrowing has to keep that test red, or the guard has been silenced rather than fixed —
   which is what its own message warns against.

## Related

* `WORKER_FINDING_THE_STALENESS_DETECTOR_CANNOT_SEE_THE_DAEMONS_THAT_GO_STALE_2026-08-09.md` — same
  incident; a control whose population is a declaration rather than an observation. This is the
  mirror: a control whose *verdict* is an inference rather than an observation.
* `process_run_complete.py:1600` — the original ghost-pusher incident this fixture was built for
  ("every unexplained `main` push this week was a test run manufacturing a real `chore(liveness)`
  commit"). That defect was real; this finding is only about the guard's scope.

— Worker finding, 2026-08-09, during the second publish-wedge episode.
