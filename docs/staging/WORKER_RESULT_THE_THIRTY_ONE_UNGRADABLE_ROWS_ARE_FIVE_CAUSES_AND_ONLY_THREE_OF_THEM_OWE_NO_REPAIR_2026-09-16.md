**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the-thirty-ungradable-rows-are-at-least-three-causes-and-each-has-its-own-repair)

# The thirty-one ungradable rows are five causes, and only three of them owe no repair at all

**2026-09-16, scheduled tick, delivery seat.** The Lane 0 direction was that the ungradable census
has not moved in twelve briefs while being asserted to be one problem, and that the split into
*unbuilt / control-never-written / pointer-rot* is what makes it tractable. That split is now
computed rather than asserted, it is mutation-proven, and it has been run against the live map.

## What was built

`tools/level_zero_contradicted_by_its_own_controls.ungradable_causes` answers a question the census
could not: **why** a row cannot be graded, as against what SHAPE its `file_scope` has. The four
existing reasons — names no control, names an absent control, control predates the row, budget
spent — describe the row's syntax. None of them says what to do, and rows sharing one reason had
opposite repairs. Every ungradable record now carries `causes`, a LIST, and the CLI prints each
cause with the repair it instructs.

Five causes, each mechanically decided, none of them a hand-kept field:

| cause | decided by | repair |
|---|---|---|
| pointer rot | path absent here, `git log --all` knows it | repoint `file_scope` |
| control never written | path absent AND unknown to git, subject on disk | write the control |
| honestly unbuilt | no named subject file on disk, nothing mislaid | **none — the row is right to read zero** |
| names only a scope | every entry is a directory | name the files, not the directory |
| undecidable | git could not be asked | classify in a tree with history |

**It is COMPUTED and deliberately not a field in the row.** A hand-written `cause:` in
`maturity_map.yaml` is pinned to today's answer: it stays `unbuilt` through the build that fixes it
and stays `pointer_rot` after the repoint. The rot this function detects *is* a map field that
stopped matching the tree, so recording the cause as another map field would have reproduced the
defect one level down. Deriving it every pass is the only version that cannot go stale — and it
keys the instrument to the property, not to today's answer.

## The prediction, and the measurement that corrects it

The reading going in — the direction's and this seat's — was that a large part of the census was
never a defect. **It is not.** Of 31 ungradable rows:

| cause | rows |
|---|---|
| the subject is on disk and nobody wrote the control | **14** |
| a rotted pointer (3 of the 4 ALSO owe a control) | 4 |
| every named entry is a directory | 4 |
| **honestly unbuilt — owes no repair** | **3** |
| instrument state, no cause at all (5 predate-row, 1 budget) | 6 |

So the census was not mostly noise. It is mostly a **real backlog of fourteen unwritten controls**
wearing one undifferentiated label, and the reason the number did not move is that nobody could see
which three of the thirty-one were finished. The wrong prediction stays written here beside the
result: that is the only evidence the split was designed before its answer was known.

The three rows the direction named as its worked examples each landed in exactly the cause it
predicted, which is the one prediction that did hold:

- `A51_the_plain_english_report...` — **pointer rot AND control never written**, both printed on
  the first pass. A single-primary-cause classifier would have sent the reader to repoint and call
  the row repaired while it stayed ungradable.
- `PB5_pounds_or_percent_resolved` — **control never written**; the subject is on disk.
- `W1_28_the_weather_partition...` — **honestly unbuilt**; both the tool and its test are absent
  from history, and the row's zero is the true answer.

## What was repaired

`A50` and `A51` both named `docs/staging/DIRECTOR_RULING_SUPPLIER_USE_CASE_REGISTER_AND_SIM_FIDELITY_2026-09-06.md`,
which archived into `docs/staging/done/`. Repointed. `A50`'s rot is gone and it now reads as the
instrument state it always was; `A51` now reads control-never-written alone, which is the honest
remaining claim against it.

Two rotted rows are **not** repointed, and the reason is that they are not repoints:
`C_supply_start_consumer_routing` and `SITE3_wall_exhibit_url_rename` name five site pages deleted
on `03dd8c49e` — "eleven pages deleted, their content moved". There is no single path either row
moved *to*; each needs a judgement about what its subject is now, which is a decision and not a
mechanical fix. They are named here so the next reader does not spend a turn rediscovering that.

## How it can fail

`test_all_five_causes_are_reachable_in_one_pass` is one assertion over the whole cause partition,
written as one assertion for the reason this file's other legs are all positive claims: a
classifier returning the same cause for everything would pass each of them read alone. Four more
legs pin the parts most likely to be simplified away — both-causes-on-one-row, the rot gate, the
cause/repair pairing, and the cause reaching `assess`'s own output rather than merely existing
beside it.

Five mutations, five distinct reds, each on the leg that owns it:

| mutation | red |
|---|---|
| drop the rot gate | `..._is_never_read_as_HONESTLY_UNBUILT` |
| return one primary cause | `..._names_BOTH` |
| fold scope-only into unbuilt | `..._all_five_causes_are_reachable...` |
| `assess` stops attaching causes | `..._attaches_causes_to_every_ungradable_row` |
| fold undecidable into never-written | the partition leg AND the rot-gate leg |

**The rot gate is the leg worth reading.** `honestly unbuilt` is the only cause that says a row
owes NO repair. Reached over a path the row names wrongly it is exactly backwards — the subject may
be on disk under the name the row stopped using — so the unbuilt question is refused whenever any
named path is rotted or undecidable. The control question is deliberately *not* gated the same way:
it asks about a different path, and a mislaid subject says nothing about whether the test was ever
written. That asymmetry is what lets `A51` print both repairs at once.

## What is next, and what this does NOT claim

This moves no level and publishes nothing. It makes fourteen rows say "write this control" instead
of saying "31".

1. **The fourteen.** Each now names its own repair. They are ordinary build work, not census work.
2. **`PB5`'s control** — `tests/simulation/test_the_decision_scale_is_pounds_on_both_sides.py` — is
   named by the direction and is **not** written by this turn. The row still reads
   control-never-written and is right to.
3. **The brief.** `background/delivery_seat._by_reason` still groups by REASON, so the three-hourly
   brief publishes the old undifferentiated count. The cause reaches the CLI and the JSON record,
   not yet the brief. It was left alone deliberately: `background/delivery_seat.py` is edited in
   this working tree by another lane, and a pathspec stages the working-tree copy.
4. **The two site rows** above need a subject decision, not a repoint.
