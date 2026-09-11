**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# A test evicted the director's own reserved item, because the isolation guard compared two values the test controls

Filed 2026-09-04 by the delivery seat, working the Lane 0 direction *"the figures stopped reaching
the reader and no direction ever named the path"*. Found by following a `promote_worktree_landing`
refusal rather than routing around it — the refusal named four files as unexpected churn, and one of
them was the director's.

**Fixed and landed in the same commit as this finding.** The mechanism is written up because the
*shape* generalises well beyond this file.

---

## What was on his surface

`site/data/director_reserved.json` is the off-nav Director window, surface 5 — the queue of items
**reserved for him**, which by `CLAUDE.md` means the four one-way doors and nothing else.

| tree | item on the surface |
|---|---|
| HEAD (`4a4ac598b`) | `executor-wall_escalated-f13e76f1` — *"Headless executor hit a one-way door (WALL)"*, awaiting his decision, **PIN 8883** |
| shared working tree | `publish_gate_wedged` — an alarm reading **"wedged since 1970-01-01T00:00 UTC"**, `git=dead` / `git=unknown` |
| this worktree, after one gate run | `publish_gate_wedged`, `git=dead`, *"Markers pending: 0"* (there were 12) |

`open_count` is **1** in each case, and the mirror rebuilds the whole list. So the fixture did not
sit *beside* his escalation — **it evicted it.** The publish daemon commits `site/`, so the next
clean publish serves it to him, and the one-way door he was asked to decide on simply stops being on
the page.

The epoch date is the tell. `1970-01-01T00:00` is a zero timestamp formatted as if it were a
measurement, and *"0h00m"* is that zero differenced against another zero. Two nulls, rendered as a
duration, on the surface reserved for the highest-stakes decisions in the project.

## The mechanism, and why the guard was worth nothing

`background/action_needed.py`, `save_register`:

```python
    # Only mirror to the site feed when writing the REAL register -- a test
    # passing a tmp_path must not touch site/data (test-isolation; ...).
    if path == REGISTER_PATH:
        _mirror_reserved_to_site(register)
```

The comment states the right intent. The code cannot deliver it, because **a test controls both
sides of that comparison.** Ten lines above, `_resolve_path`'s own docstring *instructs* tests in the
redirection idiom:

> `monkeypatch.setattr(action_needed, "REGISTER_PATH", tmp_path)`

After that monkeypatch, `_resolve_path(None)` returns the tmp path, and `REGISTER_PATH` **is** the
tmp path. `path == REGISTER_PATH` is `True`. The guard fires **open** and writes the fixture register
straight into the real site feed.

So the guard stopped exactly one of the two ways in:

* `save_register(reg, path=tmp)` — explicit argument. `tmp != REGISTER_PATH`. **Blocked.**
* `monkeypatch.setattr(..., "REGISTER_PATH", tmp)` — the documented idiom. **Waved through.**

It blocked the callers that were never the risk and admitted the one the module tells people to
write. And `_mirror_reserved_to_site` swallows every exception by design ("a mirror failure must
never wedge the register"), so it never announced itself.

## Reproduced on demand, not inferred

Reverting the one-line fix and re-running the new control leaves the real file on disk holding:

```
['would-have-evicted-the-director']
```

— a pytest fixture id, sitting where the director's escalation was. That is the whole defect in one
line, and it is why the control's last leg reads the **real** path rather than a redirected one.

## The class, and the part worth generalising

This is `controls_that_cannot_fail`, and the specific shape deserves a name because the repository
has the ingredients for it in many places:

> **An isolation guard keyed to a mutable module attribute is defeated by the very technique the
> module documents for redirecting that attribute.**

The related entry already on the record is *a deferral guard keyed to the condition that selects the
route makes that route unreachable*. This is its mirror image: **a guard keyed to the value its
adversary is expected to replace makes the guarded branch unavoidable.** Same root — the guard's
key is not independent of the thing it guards against.

The fix is therefore not "compare more carefully". It is to give the comparison a side the caller
cannot reach: `_REAL_REGISTER_PATH`, bound once at import. A module-level constant is right here
*precisely because* it is not injectable.

## The controls

`tests/background/test_the_director_surface_is_not_writable_by_a_test.py`, 5 tests.

**Mutation-proven, all three fire:**

| mutation | fires |
|---|---|
| guard back to `path == REGISTER_PATH` (the original defect) | 2 red, incl. the real-file leg |
| `_REAL_REGISTER_PATH` re-derived at call time (a cosmetic fix) | 2 red |
| mirror never fires (`if False`) | **reachability leg red** |

The third matters most. A guard that mirrored *nothing* would satisfy every negative assertion in
the file and silently freeze the director's window — the fail-silent this project keeps paying for.
`test_the_mirror_still_fires_for_the_real_register` is the null control over that partition, and it
is why the true branch had to be exercised by pointing **both** names at a tmp file rather than by
skipping it.

## Owed next — NOT done here

**1. The surface guard's scope is still argued from a stale measurement.**
`tests/production_surface_guard.py` protects `docs/observability` as a whole surface but keeps
`site/data/` file-scoped, and its own comment gives the reason: *"several generator tests
legitimately rewrite `site/data/*.json`"*, measured 2026-08-10. That reasoning is sound for
generator outputs and **wrong for this file** — `director_reserved.json` is not a generator output,
it is a mirror of a human decision queue. It belongs in `PROTECTED_FILES` beside
`site/data/publish_provenance.json`, which is there for the same reason. I have not added it in this
commit: that guard refuses at the *sink* and would newly refuse whatever legitimate writer the
daemons use, so it wants its own measurement of who writes that path in a full cycle. Named here so
it is not invisible.

**2. The epoch rendering is a separate defect and is untouched.** `_episode_phrase` guards with
`if not isinstance(wedge_since, (int, float))` — which correctly refuses `None` and **accepts `0`**,
because `0` is an `int`. A zero start time is not a start time, and it renders as `1970-01-01` with
a plausible-looking `0h00m` age beside it. The guard is one clause short of honest:
non-positive should degrade to the same explicit *"start time unrecorded (this alarm cannot bound
the episode)"* string that `None` already gets. Small, and it wants its own control and its own
mutation, so it is filed rather than smuggled into a commit about something else.

**3. Where did the zero come from?** Not established. It could be a fixture, or a real write path
that stamps `0` when it has no clock. Question, not a value to pick.
