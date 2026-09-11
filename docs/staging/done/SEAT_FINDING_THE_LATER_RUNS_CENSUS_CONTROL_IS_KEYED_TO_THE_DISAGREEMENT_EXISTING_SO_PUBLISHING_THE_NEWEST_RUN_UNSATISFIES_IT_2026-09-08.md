**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

**Knowledge:** none — this is a control-design defect, not domain understanding.

# The later-runs census control is keyed to the disagreement existing, so publishing the newest run unsatisfies it

**Found 2026-09-08** while landing the lane-0 delivery item that moved
`CURRENT_WORLD_THREE_ARM_PATH` onto the 2026-09-08 three-arm re-take.

**Subject:** `tests/tools/test_generate_value_arms_data.py::test_a_later_run_in_this_world_that_disagrees_about_the_split_refuses_the_composition`,
WITNESS D — and the sibling door control
`site/test_the_baseline_comparison_reaches_the_reader.py::test_the_composition_the_page_states_is_the_one_the_feed_established`.
**Both are UNCOMMITTED work in the shared tree** — neither the tests nor the
`_later_runs_in_this_world` / `CANNOT_TELL_SELECTION_OR_LEVEL` machinery they exercise exists at
`02c859e5b`. This finding does not touch either file; it names the defect for the lane that holds
them.

## The defect

WITNESS D asserts the census reaches the real directory, and proves it by requiring the real
directory to return rows:

```python
live_rows = gva._later_runs_in_this_world(_read_current_world_run(), live, gva.OBSERVABILITY_DIR)
assert live_rows, ("the census finds nothing beside the run this page publishes, so nothing "
                   "here is wired to the directory the defect was found in")
```

`_later_runs_in_this_world` returns runs over the same world that are **strictly later** than the
one being published. The defect it was built for was a page publishing a 09-03 run while three
later runs disagreed with it. The remedy for that defect is to publish the newest run — and the
moment you do, the census is empty **by construction**, because nothing on disk is later than the
newest thing on disk.

**So the control is satisfied only while the defect it guards is present.** It reds when the page
becomes correct and goes green when the page falls behind again — which is exactly backwards, and
is the shape this project keeps paying for: *key a control to the property, not to today's answer.*

The door control fails the same way from the other end. Its refusal branch requires the director's
words (`CANNOT_TELL_SELECTION_OR_LEVEL`) on the page, and those words are produced **only** by
`_the_later_runs_disagree`. With no later runs there is no disagreement, so the feed carries a
refusal (`readable: false`, on the floor's sign-changing seeds) that the door's `readable is False`
branch does not accept. Two different refusals, one branch.

## Reproduce

```
$ python3 -m pytest tests/tools/test_generate_value_arms_data.py::test_a_later_run_in_this_world_that_disagrees_about_the_split_refuses_the_composition -q
E  AssertionError: the census finds nothing beside the run this page publishes …
E  assert []
```

## The repair, and it is one line of intent

WITNESS D's stated subject is *"the census reaches the real directory"* — that it can **read**
`OBSERVABILITY_DIR`, not that today's directory happens to contain a disagreement. Assert the
reachability instead: run the census against the real directory with a published run whose
`generated_at` is old enough that later rows must exist (the 09-03 artefact is still on disk and
still committed), and assert the rows come back. That is the same fail-open the witness was written
against, and it stays true whichever run the page publishes.

The door control needs its `readable is False` branch to accept **either** refusal — the
disagreement wording or the feed's own `why_not_readable` — since the second is now the live one and
the first is a strictly narrower case.

## What it blocks

Nothing at HEAD: both files are uncommitted, so `02c859e5b` is unaffected. It blocks **that lane's
own landing** — these two controls red the moment the tree they live in meets the current-world
artefact, and the flattering resolution (re-point `CURRENT_WORLD_THREE_ARM_PATH` back at 09-03 to
make the census non-empty) would restore the published defect to keep its control green.

## Repaired 2026-09-08, and both repairs were poisoned before they were believed

**Discharged:** `tests/tools/test_generate_value_arms_data.py::test_a_later_run_in_this_world_that_disagrees_about_the_split_refuses_the_composition`
and `site/test_the_baseline_comparison_reaches_the_reader.py::test_the_composition_the_page_states_is_the_one_the_feed_established`,
both landed in the same commit as this discharge and both red before it.

WITNESS D now takes the real census from a FIXED committed vantage —
`value_cycle_ab_s1_three_arm_20260903.json` — rather than from whatever
`CURRENT_WORLD_THREE_ARM_PATH` names, so the rows it asserts exist whichever run the page
publishes. It gained a leg the old shape could not have: the artefact the page publishes must
itself be ADMITTED by the census, which is the one file whose absence from the scan would leave
production blind in the flattering direction.

The door's `readable is False` branch now requires the feed's OWN reason to reach the reader on
every refusal, and the director's words only where the feed says a later run disagrees — which is
where he asked for them. The two refusals are different states with different remedies and the
producer has never folded them together; the door was the only place that did.

**Poison round, because "it passes now" is not evidence a control can fail.** Four legs, four
kills: census returns `[]` → *"the census finds nothing on the real directory"*;
`CURRENT_WORLD_THREE_ARM_PATH` repointed back at the 09-03 run (the flattering resolution this
finding names) → *"the page publishes a run at or before the census vantage … a constant that moved
BACKWARDS"*; the published artefact filtered out of the real scan only → *"the census cannot see
the artefact the page publishes"*; and on the door, a refusal whose reason is absent from the
render, a disagreement whose director's words are absent, and a refusal with no reason at all each
returned their own defect while the correct render returned none.

**One thing this repair carried that the finding did not name.**
`docs/observability/value_cycle_ab_s1_three_arm_20260908.json` — the artefact the constant was
moved onto — was UNTRACKED. The page's whole current-world panel reads from it, so at HEAD, and in
every clean extract, the constant pointed at a file that was not there. It lands here.
