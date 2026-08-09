# WORKER FINDING — a mutation fixture is pinned to a GENERATED value, so regenerating its own artefact turns the control red

**Found:** 2026-08-09, during the H32 note-rehome build (incidental — outside that atom's file_scope).
**Disposition:** QUEUED, not fixed on sight (SELF-INTERRUPT DISCIPLINE). Not fixed here because the
repair is a judgement about what the fixture should anchor to, not a one-line edit.
**Rank:** backlog — but see "why this is not merely cosmetic" below; it is live-red in the working
tree right now, and `tests/` is what the publish gate runs with `-x`.

## Observed, with evidence

```
$ python3 -m pytest tests/tools/test_knife_hotspot_measure.py -q
FAILED tests/tools/test_knife_hotspot_measure.py::test_mutation_undeclared_overlap_reds
FAILED tests/tools/test_knife_hotspot_measure.py::test_mutation_omitted_pair_reds_rather_than_defaulting_to_zero
```

Both fail at the same assertion (`tests/tools/test_knife_hotspot_measure.py:93`), and the assertion
is the *fixture-validity* guard, not the control itself:

```
AssertionError: mutation source line is no longer in the live plan:
'overlaps: reporting_monolith=0, wall_crossings=16, company_orphans=0'.
Re-point the fixture at a line that exists — do NOT relax the assertion; an un-mutated fixture
proves nothing.
```

**Observed**, not inferred — the line moved because the artefact was regenerated:

```
$ git show HEAD:docs/design/KNIFE_HOTSPOT_PASSES.md | grep -c 'wall_crossings=16, company_orphans=0'
1                                  # present on committed HEAD
$ grep -c 'wall_crossings=16, company_orphans=0' docs/design/KNIFE_HOTSPOT_PASSES.md
0                                  # absent in the working tree
$ grep -n 'overlaps:' docs/design/KNIFE_HOTSPOT_PASSES.md | head -3
388:overlaps: customer_straddle=0, wall_crossings=0, company_orphans=0
397:overlaps: reporting_monolith=0, wall_crossings=0, company_orphans=0
405:overlaps: reporting_monolith=0, customer_straddle=0, company_orphans=0
```

The measured overlap count genuinely changed, 16 → 0. `docs/design/KNIFE_HOTSPOT_PASSES.md` is
modified-but-uncommitted in the shared tree (` M` in `git status`), so this is **green on HEAD and
red in the working tree** — the opposite polarity to the H32 finding, and the known
"gate lints the WORKING TREE, so one writer's uncommitted work wedges everyone" class.

## The class, not the instance (R10)

This is `never_pin_generated_values_in_controls` with an extra turn of the screw: the pinned value
lives in a **generated artefact that the control's own subject regenerates**. So the healthier the
measurement (overlaps actually driven to zero — the outcome the ratchet exists to produce), the more
certainly the mutation fixture goes stale. Same shape as the ratchet H32 just repaid: *a control that
gets angrier the more the system succeeds will eventually be paid by weakening the control.*

Note the test anticipated exactly this and pre-refused the cheap fix ("do NOT relax the assertion").
That instruction is right and should be honoured — which is why this is queued rather than patched.

## Candidate repairs (for whoever draws it — recommendation first)

**Recommended: anchor the fixture STRUCTURALLY, not textually.** Have the test locate a line by
pattern (`^overlaps: .*=\d+`) and mutate whichever one it finds, rather than pinning one exact
rendered string. The mutation stays real (a declared overlap is still corrupted), and it survives
any regeneration of the plan. This keeps the "un-mutated fixture proves nothing" guarantee — the
test still asserts it actually changed something.

Alternatives considered: (a) re-point the fixture at today's literal — restores green in one line,
but re-arms the identical failure at the next regeneration, so it buys days, not a fix;
(b) generate the fixture into a tmp file from a committed sample rather than reading the live plan —
strongest isolation, largest change, and it decouples the mutation test from the artefact it is
supposed to be about.

## Not claimed

Whether the 16 → 0 overlap change is itself correct is **not** assessed here — this finding is about
the control's fragility only. Someone should confirm that drop is a real consolidation win and not a
measurement regression; if it is a regression, the stale fixture was the only thing that noticed,
which would make this urgent rather than backlog.
