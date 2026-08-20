# WORKER FINDING — the map merge deletes the hand-authored comment on the one field it rewrites

**Severity:** LATENT · **Lane:** H_harness

LATENT and not BLOCKING, decided rather than defaulted: no published figure and no control's
verdict depends on the deleted comment — the note's content lives in full in the per-atom
simplifications store, which is where FM-1 put notes. What is wrong is a tool's stated contract,
which owes work but invalidates nothing already claimed.

**Rank:** backlog (P-1: every staged directive declares its rank).
**Found:** 2026-08-20, worker tick, atom `EP6_wall_protocol_typing` pass 20, while folding a
routine `append_simplification` inbox.
**Class:** a control/tool whose stated contract is the opposite of its behaviour.
**Disposition:** QUEUED, not fixed on sight (SELF_INTERRUPT_DISCIPLINE — the machine is not
blocked; the supply of harness findings is infinite and fixing on sight is the treadmill).

## Observed, with evidence

`tools/merge_atom_status.py`'s module docstring states its CRITICAL CONTRACT in as many words:

> this is a NARROW FIELD MERGE, never a wholesale regeneration. `maturity_map.yaml` carries rich
> hand-authored content (`provenance`, `expert_hour`, `depends_on`, and the
> `simplifications_count` scalar) that must survive untouched.

`_set_or_create_scalar` (tools/merge_atom_status.py:340) rewrites the whole LINE for the field it
sets. When that line carries a trailing `# ...` comment, the comment is deleted with it.

Reproduced, not inferred: folding one `append_simplification` for `EP6_wall_protocol_typing`
produced a one-line diff on `docs/design/maturity_map.yaml` that replaced

    simplifications_count: 18   # 2026-08-20 pass 19 GIVES CHANNEL C ITS CONFORMANCE QUESTION -- <~2,900 chars of hand-authored summary>

with

    simplifications_count: 19

The summary was written by hand by the previous pass and is in no other file in that form. It was
not preserved, not moved, and nothing warned.

## Why it is small today and why it is still worth a row

Small: `grep "simplifications_count:.*#"` over the live map returns **1 of 213** atoms, so exactly
one atom had ever carried such a comment and it is now gone. The CONTENT was not lost — the full
pass-19 note lives in `docs/design/simplifications/EP6_wall_protocol_typing.yaml`, which is where
notes belong since retro FM-1 moved them out of the map.

Still worth a row, for two reasons that outlive the instance:

1. **The docstring is the promise a reader relies on.** Anyone who reads that contract will believe
   a hand-authored annotation on a merged field is safe. It is not, and the failure is silent —
   no warning, no refusal, no record. A tool that quietly does the opposite of its stated contract
   is worse than one with no contract, for the same reason a control that cannot fail is worse
   than none.
2. **The blast radius is a property of the map's current shape, not of the tool.** One annotated
   line today; the tool would erase fifty the same way. Nothing stops the annotation convention
   growing, because nothing tells anyone it is unsafe.

## The two honest repairs, and a recommendation

* **(a) PRESERVE.** Split the trailing comment off in `_set_or_create_scalar`, rewrite only the
  `key: value` half, re-attach the comment. Cheap; keeps the docstring's promise true.
* **(b) REFUSE.** Raise `MergeError` when the target line carries a comment, forcing the author to
  move the prose to the store where notes live. Also keeps the promise true, and pushes in the
  direction FM-1 already chose.

**Recommendation: (a), plus one line in the docstring saying trailing comments ARE preserved** —
because (b) refuses a commit for a reason its author cannot have predicted, and the whole class of
defect here is "the tool did something the reader had no way to expect".

An R15 mutation for whichever is built: set a field on a line carrying a comment and assert the
comment survives (a); or assert the merge refuses (b). Null control: the same field with no
comment merges unchanged either way, so the test moves on the comment and not on the merge.
