# FINDING — a register's "LANDED" is checked against another record, never against the tree

**Severity:** RECORDED · **Lane:** H_harness · **Disposition:** BUILT (H27 Expert Hour #25,
2026-08-13) — but **the recommendation below was measured and falsified before it was built**, and
is left standing verbatim as the record of that. A HEAD-only check reads CLEAN at both moments this
was queued from: at `1f1b09893` and `dfc233094` the committed tree is internally consistent, so no
reading of it can find the defect. The witness is the DIFFERENCE between the two trees, and plain
`file_scope` dirtiness is noise on a tree that normally carries 200+ dirty paths. What landed
instead is atom **D42** — a self-labelled Hour present in the working tree and absent from HEAD.
**Discharged:** `tests/tools/test_map_assertion_provenance.py::test_the_end_to_end_check_fires_on_a_real_repo_with_real_uncommitted_work`, `tests/tools/test_map_assertion_provenance.py::test_an_hour_entry_written_but_not_committed_FIRES`, `tests/tools/test_map_assertion_provenance.py::test_MUTATION_reading_the_working_tree_on_BOTH_sides_goes_blind`

**Atom:** `H27_payment_belief_gap` (Expert Hour #23, 2026-08-13)
**Class:** the freshness control compares record to record; nothing compares either to what is committed

## Observed, with evidence

`H27`'s Expert Hour #22 (commit `758c385b8`) closed with its own brief for the next Hour, in its
own words: *"Hour #21's three open leads (D39, D40, and the vacuous-in-isolation sibling control)
are untouched by this Hour."*

The repair for the third of those leads — atom **D38** — was already complete and **uncommitted in
the working tree** when Hour #23 drew:

- at `HEAD 1f1b09893`, `tests/tools/test_couple_w2_11_d5.py` contains the string
  `renderer_provenance` **zero** times;
- the working tree contains it **five** times, across **+162/−15** lines in
  `tools/couple_w2_11_d5.py` and `tests/tools/test_couple_w2_11_d5.py`;
- every added docstring self-labels **"atom D38, H27 Expert Hour #22"**;
- the committed register names `D38` once, in prose.

So Hour #22 authored D38, wrote about it, listed the lead D38 repairs as still open, and landed
neither the code nor a correction.

## Why the existing control cannot see it

Hour #22's own landing, D41 (`tools/map_assertion_provenance.py`), exists for exactly this family:
*for every atom held below its target with Hours recorded, the LATEST recorded Hour must be
ANSWERED in a record the draw reads.* That is **record against record**.

Here both records were perfectly current **with each other** — the register's newest entry was
Hour #22's and it carried its own verdict — and both were wrong about the tree. D41 is satisfied
by construction and the defect is invisible to it.

The generalisation: **a register entry is a claim about what LANDED, and no control compares that
claim to what is committed.** The neighbours already filed are the inverse or the adjacent case —
`feedback_the_record_can_outrun_the_code` (the record ahead of the code) and
`feedback_a_draw_may_already_be_built_and_unlanded_in_the_working_tree` (the *draw* rebuilding
existing work). Neither is a control; both are recall. Nothing fires.

## What it costs

Two ways, and the second is the expensive one:

1. The next draw rebuilds work that already exists — Hour #23 was one grep away from doing so.
2. A concurrent lane's pathspec commit sweeps the half-verified change in under an unrelated
   message. This tree currently has 191 dirty paths and three lanes' hunks staged in
   `docs/design/maturity_map.yaml` alone; the window is not hypothetical.

## Recommendation — and this is what I would take

Extend `tools/map_assertion_provenance.py` with a second question asked of the **same derived
population** it already builds: for each atom whose latest register entry claims an artefact
LANDED, resolve the atom's `file_scope` and refuse when that scope is **dirty at the paths the
entry names**. Keyed to `git status --porcelain` at check time, so it is a live predicate rather
than a stored boolean — the same R15 shape D41 itself was built to.

Fail-closed in the direction that costs: an unreadable git state must **raise**, never report
clean. "The tree is fine" and "I could not look at the tree" are the same silence and opposite
facts.

**Not taken this tick, deliberately (SELF_INTERRUPT_DISCIPLINE):** it is a change to a control
outside `H27_payment_belief_gap`'s `file_scope`, and nothing is blocked by queueing it — D38 is
now landed and verified. Registered here rather than fixed on sight.

## What was done instead

D38 was **verified and landed, in that order**, rather than rebuilt: both named controls proven to
pass run **alone** (the exact condition Hour #21 filed them as failing), 442 passed on the atom's
file, four source mutations each firing a named test with no survivors and an md5 byte-clean
restore, and R12 measured rather than asserted (all four walkable dimensions report
`the_composers` on the shipped walk, so no D38 refusal fires and no published figure moved).
Full record: `docs/design/simplifications/H27_payment_belief_gap.yaml`, twenty-third entry.
