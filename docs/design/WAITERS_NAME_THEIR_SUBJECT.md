# R18 — A WAITER NAMES ITS SUBJECT AND CARRIES A DEADLINE

**Status:** standing rule. Director NTFY, 2026-08-27, after the third incident of this class in
one week. CLAUDE.md carries the one-line pointer; this file is the full text, because the rule's
whole content is *why* the obvious shape is broken, and that does not compress.

> *"a waiter whose subject has gone looks exactly like work in progress, so the shell indicator
> now tells neither of us anything."* — the director, stating the failure better than the
> incident reports had.

## The rule

Never hand-roll a process waiter. Use:

```
python3 -m tools.wait_for --pid N       --subject "<what>" --deadline <seconds>   # preferred
python3 -m tools.wait_for --pattern ... --subject "<what>" --deadline <seconds>
```

`--subject` and `--deadline` are both **required**. There is no default deadline, because the
default that matters is the one nobody sets.

## Why the obvious shape cannot work

The shape that keeps getting written is:

```bash
until ! pgrep -f "the_thing"; do sleep 30; done   # BROKEN, ALWAYS
```

`pgrep -f` matches against the **full command line**, and a backgrounded shell's command line is
`bash -c '<the entire loop, including the pattern>'`. So the pattern is a substring of the
waiter's *own* cmdline. `pgrep -f` finds the waiter, the waiter concludes its subject is still
running, and the exit condition is unreachable **from the first second** — not after a race, not
under load, but always and immediately.

It fails in the most expensive possible direction. A waiter that exits early is noticed at once;
this one looks exactly like patience. The last instance burned **12 hours** on a subject that had
already finished, and left an empty output file, while the shell indicator showed work in
progress the whole time.

## What `tools/wait_for.py` does instead

- **`--pid` is preferred, and is the structural fix**: a PID cannot self-match. The pattern form
  remains for cases where no PID was captured.
- **Self *and ancestors* are excluded** from pattern matching. Excluding only `os.getpid()` is
  not enough — the waiter is typically a grandchild of the shell whose cmdline carries the
  pattern.
- **An absent subject REFUSES immediately** (`NEVER_STARTED`) rather than waiting. "Nothing
  matches" means the thing never started, which is a different fact from "it finished", and
  waiting on it is how a typo becomes an overnight stall.
- **An unreadable probe is not an absent subject.** A permission error while inspecting a process
  must not be scored as "gone".
- **Ceiling of 21,600s** (6h) on any deadline.

## The deadline is the defence that holds when the other one is wrong

This is the load-bearing half. The self-match exclusion is a fix for a *known* bug; the deadline
is the fix for the ones not yet found. The R15 mutation test in `tests/tools/test_wait_for.py`
reintroduces the original defect — excluding only `os.getpid()` and not the ancestors — and duly
reproduces the incident: the waiter matches itself. **It still terminates, in six seconds**,
because the deadline does not care why the exit condition was never reached.

A rule with one defence is a rule that fails silently the first time that defence is wrong.

## Family

Sibling of **R5** (alerting fires on state transitions, never repeats an unchanged status): a
control that looks healthy while doing nothing is worse than one that is visibly broken. Both are
about the same thing — an indicator whose steady state is indistinguishable from its failure
state carries no information at all.

Sibling also of the fixture-population lesson on `EP13_adapter_carbon_intensity`
(`tests/tools/test_ep13_embedded_generation_bound.py`): there, a fixture too small for the grid
made 92% of scored half hours answer from fallbacks, and the resulting null read as "the
instrument is blind". Same shape — the failure mode wears the costume of the working one, and
the flattering reading points at the wrong file.

## Proof

`tests/tools/test_wait_for.py`, R15-proven both ways: the control fires on its own named defect
(the `os.getpid()`-only mutation), and the deadline terminates the mutant.
