**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The publisher's four reds were one refactor, and every property they guard was intact

**Claim:** `publish-the-withdrawal-the-belief-leg-did-not-survive`
**Pre-registration:** `SEAT_PREREGISTRATION_ARE_THE_PUBLISH_GATES_FOUR_REDS_RED_AT_HEAD_2026-09-23.md`
(same room) — including its own refuted reasoning.

## The measurement the state file had never taken

`docs/observability/.publish_gate_state.json` carried `red_at_head: "not_established"`, with the
reason: *"the red was measured at git=d533d9a93 and HEAD is now git=c50ea7f0b — that record
describes a different commit's tree, so it says nothing about HEAD."* It had said a version of that
for as long as the wedge has been open: `episode_clean_publishes: 0`, `episode_failures: 26`.

Graded in a `git clone --local` of the common git dir forced to `c50ea7f0b`, no uncommitted state,
`GIT_*` scrubbed — **all four RED, in 0.14 seconds.**

| the red | subject |
|---|---|
| `test_publish_step_ledger.py::TestWiredIntoThePublishPath::test_the_publish_path_actually_uses_the_ledger` | the step ledger is constructed |
| `test_publish_step_ledger.py::TestWiredIntoThePublishPath::test_the_five_evidenced_failures_are_all_covered` | four named generator steps are wrapped |
| `test_the_site_publish_pipeline_is_contained.py::test_the_publish_pipeline_actually_calls_the_guard_first` | the test-process guard is the FIRST statement |
| `test_website_integrity_fix.py::test_the_gate_verdict_is_what_generate_dashboard_json_returns` | the accumulated verdict reaches the caller |

**0.14 seconds is the finding's first sentence.** These are not behavioural tests. Four pure
source-shape controls had held the publisher shut across 26 failures.

## One cause, not four, and the code was never wrong

All four did `inspect.getsource(process_run_complete.generate_dashboard_json)`. `cc5cc0032` wrapped
that entry point:

```python
def generate_dashboard_json(json_path, git_hash="unknown"):
    with refuse_stale_producers():
        return _generate_dashboard_json(json_path, git_hash=git_hash)
```

The body moved to `_generate_dashboard_json`, and four controls began reading four lines of
delegation that contain none of what they check. **Every property they guard is intact in the
body** — verified field by field: the `PublishStepLedger` construction, all five named
`_ledger.step(...)` wrappers, `guard_site_publish_pipeline(...)` as the first statement, and the
trailing `return ok`. The wrap had a real reason: `refuse_stale_producers` replaces entries in
`sys.modules` and every `return` below it — including the coverage gate's early one — would
otherwise leave the stand-ins in place for the rest of the daemon's life.

So this is the project's named failure — *a control pinned to the current state goes red when the
code becomes more honest* — with one twist worth keeping. **Three of the four were explicitly keyed
to a property and said so in their own docstrings.** `test_the_gate_verdict_...` says "Keyed to the
PROPERTY, not to today's answer"; it asserts the last statement is a `Return` of the accumulated
verdict rather than pinning the value. That keying was correct and it did not save it. **A control
keyed to a property of the WRONG FUNCTION is pinned after all** — the subject is as pinnable as the
assertion, and nothing in this project's rules said so.

## The repair: resolve the subject, never name it

Re-pointing the four at `_generate_dashboard_json` fixes today and re-arms the identical trap for
the next seat with a good reason to wrap the entry point — and the last one had a good reason.

`tests/conftest.py` gains `resolve_through_delegation(fn, module)` and a `publish_path_body`
fixture: *whatever `generate_dashboard_json` ultimately runs*. A conftest fixture and not a new
module because `tests/conftest.py` already reaches both `tests/background/` and `tests/tools/`,
which is where the four live.

A delegation is recognised narrowly: the whole body, docstring aside, must be ONE statement
containing exactly one `return <same-module function>(...)`. Anything else stops the walk.
**Under-walking is fail-closed** — the caller reads the wrapper, finds the property absent, and
reds, which is precisely the wedge being repaired. **Over-walking is fail-open** and would move all
three source-shape controls onto the wrong function where they would pass while measuring nothing.
The narrowness is aimed at that direction, and so is the resolver's own control.

## Mutation-proven, not asserted

Each repaired leg was made to fail by breaking the property it names, against the resolved subject:

| mutation in `_generate_dashboard_json` | leg | result |
|---|---|---|
| `PublishStepLedger(` → `_NOT_THE_LEDGER(` | ledger is constructed | **RED** |
| rename one of the four evidenced steps | evidenced steps covered | **RED** |
| move the guard below the coverage gate | guard is FIRST | **RED** |
| trailing `return ok` → `return True` | verdict reaches the caller | **RED** |

And the resolver itself, in the dangerous direction: deleting its single-statement requirement so
it over-walks reds `test_the_delegation_resolver_follows_a_wrapper_and_STOPS_at_real_work`. That
test also carries a null control — a function that is already the body resolves to itself — so the
live leg is about following a wrapper and not about the resolver simply always moving.
`background/process_run_complete.py` was restored from backup and `git status --porcelain` confirmed
clean after the sweep.

## What this does NOT establish

It does not establish that the publisher now publishes. These four were the reds the gate NAMED;
the gate runs 258 blocking test files and a red it never reached is still a red. `last_clean_publish`
moving is the only evidence that would settle it, and that is the publisher's to produce, not mine.

It also does not establish that the three armed-revert feed inputs named in the drawn item are
harmless. It establishes only that they are **not** the cause of these four: none of the four reads
`site/data/value_arms.json` at all. That was the mechanism my pre-registration predicted and it is
dead — see the amendment there, written before the run.

## Carried forward

**A control's SUBJECT is as pinnable as its assertion, and keying the assertion to a property does
not protect the subject.** Three of these four said "keyed to the property" in their own docstrings
and were blinded by a wrapper anyway. Where a control reads the source or shape of a named function,
ask whether that name still resolves to the code that holds the property — and prefer resolving the
subject to naming it. `resolve_through_delegation` is the first instance; it is not obviously the
last, because `inspect.getsource(<named function>)` is a common shape in this tree's controls.
