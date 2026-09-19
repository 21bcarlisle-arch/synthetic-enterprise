# A bulk archive sweep filed a finding as `done` while its own null control is still false

**Severity:** BLOCKING for the archive path's honesty; the underlying door defect is unchanged and
still owned elsewhere.
**Class:** controls_that_cannot_fail
**Rule:** R15 — fail-silent. The archiver is a disposition step with no refusing branch: it infers
closure from a file's *location* rather than from its stated closure criterion, so it returns
"archived" for a finished finding and for one still waiting on its owner alike.
**Raised:** 2026-09-19, worker tick, while re-asking EP19_counterparty_qualification_paths' open items.
**Lane:** H_harness (the archive path). The door repair itself stays where 2026-08-18 put it.

## The instance

`WORKER_FINDING_THE_DOOR_RELEASES_THE_ONE_CONTROL_CLAUDE_MD_CALLS_A_WALL_2026-08-18.md` wrote its own
closure test, in those words:

> *"This finding is closed when the acts above gate **and** every simulation-internal safety-control
> phrasing still proceeds. If both move, the fix is wrong in the direction that matters most."*

It is now in `docs/staging/done/`. Measured at HEAD this pass:

| check | result |
|---|---|
| `classify_action("add a host to the egress allowlist")` | **PROCEED** — `is_one_way_door=False`, no category matched |
| `classify_action("change the sandbox security profile")` | **PROCEED** — matches `security profile`, but as the *released* `security_safety_control` category |
| `classify_action("widen ALLOWED_HOST_SUFFIXES to include xoserve.com")` | **PROCEED** — no category matched |
| commits to `background/one_way_door.py` since 2026-08-18 | **zero** (`git log --since=2026-08-18 -- background/one_way_door.py` is empty) |

The finding's first half is measurably unmet and no repair exists. It is in `done/` anyway.

## How it got there — not a judgement, a sweep

`git log` on the path returns one commit: **`2766c8ca2`**, *"a checker crashed on a scratch path two
documents honestly mention, so it refused every staging commit and a 419-file archive backlog could not
be cleared for six days"*. That commit moves **772** `docs/staging/done` path entries.

So the disposition was never taken. A backlog-clearing sweep moved everything that had been sitting in
`docs/staging/` for long enough, and this finding was sitting there for exactly the reason it said it
would be: it names a repair that is **not** a free safety-increasing widening, because it would
un-release a category the director explicitly released on 2026-07-29, so it has an owner and it waits.
**The sweep could not tell "waiting on its owner" from "finished".** Age was the only input.

### The distinction that makes this a defect and not just filing

This project has **two** routes into `done/` and they are not equivalent:

- **Consolidation** — `background/finding_classes.py --consolidate` moves a finding into `done/`
  *because a class document now carries it*. Severity survives the move: a class inherits the
  **maximum** severity of its members, explicitly so that "consolidation must never launder a blocker
  into a housekeeping note". The finding is superseded, not silenced, and `--check` refuses if the
  carrier's printed severity stops matching what its members derive.
- **The age sweep** — moves a finding into `done/` because it is old. Nothing carries it afterwards.

**Measured this pass:** `grep -rl` for the door finding's name across every `CLASS_*` document in
`docs/staging/reference/` returns **no class document**. The only file in the tree that names it is
this one. It took the second route, so its BLOCKING severity is carried by nothing, it appears in no
class count, and no `--check` leg can ever notice it again.

That is the whole defect in one line: **the two routes leave the file in the same directory and the
record in completely different states, and nothing downstream can tell which route a given file took.**

## Why this is worth a finding rather than a re-file

The door defect is already written up, with six checks and a null control; re-raising it buys nothing.
What is new is that **`done/` is now load-bearing and wrong**, and two readers depend on it:

1. `docs/design/EP19_COUNTERPARTY_QUALIFICATION_REGISTER.md` says its Owner column is a *mixed
   instrument* and that the caveat *"comes out when this lands, and not before"*, citing the finding at
   its **old `docs/staging/` path**. That citation now resolves into `done/`. A reader following it
   concludes the blocker cleared and removes a caveat that is still true. (Guarded in place this pass —
   the register now states the null control, not the location, as the condition.)
2. Any future census of "what is still owed" that reads staging-root membership will score this closed.

This is the third route this project has found to the same destination — treating a citation as a
discharge. The first was prose naming a mechanism that did not implement it (2026-08-15); the second
was a register asserting the boundary was *held* when it was merely *cited* (2026-08-13); this one is
an archive path inferring closure from a move.

## Recommended remedy — one leg, not a register

**Do not build a disposition register.** The findings already carry their own closure criteria in
prose; a second store of them would drift from the first.

The cheap leg: **a finding that states a null control may not be archived while that control is
measurably false.** Concretely — before a sweep moves `docs/staging/X.md` into `done/`, if X contains a
"closed when" / "null control" section, the sweep refuses that one path and names it, rather than
moving the batch minus nothing. That is one predicate on the archiver, it fails closed, and it would
have caught this exact file inside a 772-path batch.

Weaker fallback if extracting the criterion mechanically proves unreliable: the archiver records, per
moved file, **which** disposition it applied (actioned / superseded / swept-on-age), so "swept-on-age"
is visible rather than indistinguishable from "actioned". The first option is better because it
refuses; the second only annotates.

## What this finding does NOT claim

- **Not** that the 419-file backlog clearance was wrong. It was a real wedge and clearing it was right;
  the defect is that the sweep had no per-file refusal, not that it ran.
- **Not** that the door repair should now be done by the next tick. Its 2026-08-18 analysis stands,
  including that it un-releases a director-released category and therefore has an owner. This finding
  moves nothing on that question.
- **Not** that other files in the 772 are mis-filed. That is the obvious next question and this pass
  did **not** measure it — one instance is demonstrated, the population is unmeasured, and an empty
  instance list is never evidence a rule-class finding is safe to leave. Counting how many archived
  findings carry an unmet stated null control is the follow-up, and it is a `grep` over `done/`.
