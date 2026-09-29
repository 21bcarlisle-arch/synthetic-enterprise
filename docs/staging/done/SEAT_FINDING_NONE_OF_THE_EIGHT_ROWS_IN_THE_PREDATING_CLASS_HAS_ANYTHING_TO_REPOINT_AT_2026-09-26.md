**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# None of the eight rows in the predating class has anything to repoint at, and the two that looked like exceptions are the more interesting case

Closes the class opened by `e854d8c74`, which split `CONTROL_PREDATES_ROW`'s eight live members
into six owed "nothing to repoint at" and two — `D9_worse_than_blind_chip_is_metric_blind` and
`H41_the_map_ratchet_has_no_ongoing_drain` — owed a genuine repoint, because each names a subject
born AFTER its own row. That commit said plainly that the two repoints were still owed and that
it had not made them. **They have now been attempted, and the answer is that neither can be made.**

## What the two subject-landing commits actually wrote

The new cause's repair sends the reader at a path: *"ask `git log --all --oneline -- <the subject
born after the row>` for the commits that landed it and name the control they wrote. **If they
wrote none, that is the finding** — say so in the row rather than repointing it at an older
suite."* Asked, for both:

| row | subject younger than the row | landed by | controls that commit created |
|---|---|---|---|
| `H41` | `tools/migrate_gain_to_store.py` (2026-09-06, row 2026-08-10) | `992a037fc` | **none** — it is a one-off migration moving map prose into `docs/design/simplifications/*.yaml` |
| `D9` | `site/harness/index.html` (2026-08-19, row 2026-08-08) | `f0954c110` | **none** — it raises a page structure with two declared holes |

So the repair's second branch is the true one in both cases, on its first live application. The
escape hatch was written into that repair on the argument that a build can land code and write no
control; it did not have to wait long for an instance, and it would have been a defect to omit it.

## Why this is a finding and not a shrug

**The temptation here is precisely measurable and was refused.** Ten controls on disk mention
`generate_proof_data` or `site/harness` by name, and `D9` could have been repointed at any of
them — `test_generate_proof_data_expert_hour_findings.py` reads like a fit. None was written by
`D9`'s build. A name match is not authorship, and repointing on one would have produced a passing
control against a level-0 row: a **false CONTRADICTED**, published, about an atom nobody had
looked at. That is the same failure mode `e854d8c74` measured in the message-grep proxy, arriving
by a different door an hour later.

**`H41` is at zero for a reason already written in its own row**, and it is neither a map defect
nor unbuilt work. Its `block_reason` reads: *"Built, not ratified. OPS11 refuses a level move in
H_harness while the lane holds 13 live BLOCKING findings; the mechanism is landed and proven
either way."* The level grader cannot see that field, so it reports the row as ungradable and the
reader has to open the map to learn the row already explains itself. That is worth knowing about
the grader, and it is a THIRD state again — not "cannot grade", but "deliberately held".

## The two rows the drawn item called rotted pointers are not rotted

Measured while here, because the item asserted it: `C_supply_start_consumer_routing` and
`SITE3_wall_exhibit_url_rename` name **thirteen paths between them and every one is on disk.**
Neither is a rotted pointer. Both are `CONTROL_UNNAMED` — rows that name no control at all — which
is the largest remaining class (10 rows) and a different repair entirely. The item's instruction
to "repair or park the two rotted pointers" was addressed to a defect that does not exist.

## What is actually left in the level-zero population

| class | rows | what it needs |
|---|---|---|
| `CONTROL_UNNAMED` | 10 | name a control, having first asked whether one exists — real per-row work |
| `EXTENDS_WORK_OLDER_THAN_ITSELF` | 6 | build the atom; the row is correct |
| `HONESTLY_UNBUILT` | 4 | build the atom; the row is correct |
| `BUILD_LANDED_A_SUBJECT_AND_CITED_NO_CONTROL` | 2 | **resolved by this document**: neither build wrote one |
| `NAMES_ONLY_A_SCOPE` | 2 | refused in writing 2026-09-25 (`H40`, `H48`) — deliverable is a record |
| `CONTROL_NEVER_WRITTEN` | 2 | write the named control |
| `NOTHING_IN_THE_ROW` | 2 | `KNIFE3`, `OPS6` — the row is fine, the budget was spent |

**`graded` is still 0 of 28 and this turn did not move it.** That number is now unambiguous rather
than merely low: it is not a map that misreports where its evidence is. Twelve of the 28 rows are
correctly at zero with correct `file_scope` and owe a BUILD; ten owe a control they never named;
two are refused with a reason; two are instrument states. **The remaining question is a different
one and should be drawn as such — not "why can the grader grade none of its population" but "does
the pass reach a runner at all", which `d01283d58` already answered no and attributed to both
timeouts being dead dials.**
