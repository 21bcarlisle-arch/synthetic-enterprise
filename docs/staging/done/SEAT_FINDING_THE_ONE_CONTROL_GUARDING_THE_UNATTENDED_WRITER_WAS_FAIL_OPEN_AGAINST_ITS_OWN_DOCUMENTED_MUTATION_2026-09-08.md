**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING — the one control guarding the unattended writer was fail-open against its own documented mutation, and red at HEAD for the opposite reason

BLOCKING, and both directions were broken at once: it **refused an accurate comment** (red at HEAD,
wedging every lane that touches `background/`) and it **admitted a real second scheduler** (fail-open,
silent). The subject is `tests/background/test_the_seat_executor_stands_down.py::test_the_only_thing_that_invokes_it_is_the_declared_schedule`
— the single control standing between this repository and a second unattended writer on the shared
tree, which is the configuration that caused August's damage.

**Filed:** 2026-09-08, delivery seat (isolated worktree). Found while landing the teardown check;
neither defect was introduced by that work.

---

## 1. It was RED AT HEAD, and not because of my change

Proven in a clean extract, not in the shared tree — a green or red in a dirty worktree measures
several lanes:

```
$ git archive HEAD | tar -x -C /var/tmp/headx && cd /var/tmp/headx
$ python3 -m pytest tests/background/test_the_seat_executor_stands_down.py::test_the_only_thing_that_invokes_it_is_the_declared_schedule
E   AssertionError: the seat executor is INVOKED from something outside its declared
E   schedule: ['background/launch_long_job.py']
1 failed
```

`background/launch_long_job.py` does not invoke anything. Its docstring cites
`0::/user.slice/…/app.slice/seat-executor.service` as the worked example of why `setsid` does not
survive a `KillMode=control-group` teardown. **Naming the cgroup you die in is the opposite of
arming a turn**, and the control's own docstring says its subject is *"INVOCATION, NOT MENTION"* —
then matched the bare substring `"seat-executor.service"`.

This is the **fourth** time this same control has been widened by an accurate comment: `fork_salvage`
and `fork_reconciler` reading `worktree_is_live`; `delivery_lane.hand_off_focus` explaining the
stand-down; now `launch_long_job` naming the cgroup. Each previous fix corrected the *instance*
(add a `(`, refine a spelling) and left the class — a control that reads prose as code — intact.

## 2. It was FAIL-OPEN against the exact mutation its docstring offers as proof

Worse, and silent. The control's docstring says, verbatim:

> MUTATION: add `subprocess.run(["python3", "-m", "background.seat_executor", "--once"])` anywhere
> under `background/`, `tools/`, `systemd/` or `.claude/` and this fires with the path named.

It does not fire. Measured:

```
documented mutation text: subprocess.run(["python3", "-m", "background.seat_executor", "--once"])
matches any pattern?  False
```

The argv-**list** form — how every subprocess call in this repository is written, *including the
executor's own spawn of `claude -p`* — contains none of the six patterns as a substring. `"-m
background.seat_executor"` is never contiguous in `["python3", "-m", "background.seat_executor"]`.

**A mutation named in prose and never executed is a claim, not evidence.** The control has carried
a mutation-proven claim since 2026-08-31 that was false on the day it was written, and nothing
could notice because the prose was the only place the mutation existed. This is the same shape as
`tools/launch_shape_census.py`'s own recorded near-miss — *"a census whose docstring says it detects
the shape and not the word was detecting the word"* — one file over, shipped rather than caught.

## 3. One cause, one fix

Both defects are the same class: **substring matching cannot tell code from prose, in either
direction.** The fix reads Python as Python:

* `.py` files → AST. A call is an `ast.Call` node; a docstring is a bare `Expr(Constant(str))` and
  is dropped; comments never reach the AST at all. String **lists are rejoined with spaces** before
  matching, which is what closes the argv-list hole.
* everything else (`.service`, `.timer`, `.yaml`, `.json`, `.sh`) → substring, because there is no
  prose/code distinction worth drawing: naming the unit in a unit file IS the wiring.
* the unit name in a `.py`/`.sh` now requires a **start verb** (`systemctl … start|restart`,
  `systemd-run`), because that is the property that separates starting a unit from naming one.

The allow-list did not grow. It shrank by one bare pattern and gained a rule.

**Reachability proven over the whole partition**, not a leg apiece: `test_the_documented_mutation_actually_fires`
(six real second-scheduler spellings, including the one the old docstring promised),
`test_prose_about_the_executor_is_not_an_invocation_of_it` (four real prose forms that were red),
and `test_naming_the_unit_and_starting_the_unit_are_told_apart`. 5 mutations written against the
repaired control; the two that matter — `_python_invokes` pinned to `False` (the original fail-open)
and pinned to `True` (the original red) — are each killed by a different one of those legs.

## What is next

* The `_ARMED_BY` population floor is unchanged and still passes, so this narrowing did not make
  the control vacuous — that was checked, because a filter that now refuses everything would pass
  the caller just as happily as a correct one.
* **Other controls in this repo that scan source with substrings should be re-asked the same
  question.** This one had a live fail-open for eight days behind a docstring asserting the
  opposite. `tools/launch_shape_census.py` already made this exact correction *before* shipping;
  the two of them are now the evidence that the class is worth a sweep, and that sweep is the
  natural next Lane 0 item rather than anything in this turn.
