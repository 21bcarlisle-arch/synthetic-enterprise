**Severity:** LATENT · **Lane:** H_harness

# The level gate's two halves read two different trees, so an uncommitted ledger row authorises a committed level move

Found while landing `EP6_wall_protocol_typing` L1->L2 (worker tick, 2026-08-19). QUEUED, not fixed
on sight (SELF_INTERRUPT_DISCIPLINE) — the machine is not blocked, and this pass worked around it by
landing both halves in one commit. Everything below is `observed-with-evidence` unless labelled
`inferred` (R9).

## Observed

`tools/level_promotion_gate.py` decides "is this level increase RECORDED?" from two inputs that it
reads from two different trees:

| input | source | tree |
|---|---|---|
| the maturity map (the level move being judged) | `_git_show(f":{MAP_REL}")` in `main()` | the **INDEX** — the content actually being committed |
| the ledger (the record that authorises it) | `read_ledger()` → `background.gate_authorization.LEDGER_PATH` | the **WORKING TREE** — a plain filesystem path |

`LEDGER_PATH` is `PROJECT_DIR / "docs" / "observability" / "gate_authorizations.jsonl"`
(`background/gate_authorization.py:72`) — an ordinary `Path`, read with `open()`, never through git.

**Consequence:** a level move commits successfully when its authorising ledger row exists only as an
uncommitted working-tree edit. At HEAD the map then declares a level whose record is in no commit.
The gate reports the move as RECORDED; `git log` contains no record.

## The instance that surfaced it

`EP6_wall_protocol_typing` at HEAD `8233f3629`, before this pass:

- L2 ledger row present in the worktree, absent from HEAD —
  `git show HEAD:docs/observability/gate_authorizations.jsonl | grep -c EP6_wall_protocol_typing` = **1**;
  the same grep against the worktree file = **2**.
- The map still read `level_current: 1` (at HEAD *and* in the worktree), while the atom's code and its
  store record had both landed.

Committing the map move alone would have passed this gate. That is the same shape as the defect
commit `8233f3629` was written to repair — *"The counts were right and the records they count had
never been committed, so HEAD was red in a way no working tree could show."*

## Why this is the R15 FAIL-OPEN pattern, not a cosmetic mismatch

The gate's own docstring names its subject correctly: *"a control whose subject is the TREE publishing
a claim whose subject is the COMMIT"* — and it built the SECOND control (recorded-but-unbuilt) precisely
to close that seam for **source files**, using the porcelain worktree column. The seam was closed for
`file_scope` source and left open for the **ledger** the first control depends on. So the module already
contains the reasoning that condemns this; it was applied to one of its two inputs.

Note the asymmetry is not obviously wrong by construction — reading the ledger from the worktree is what
lets a tick *write* the row and commit in one step. The defect is that nothing then checks the row is
**in the commit**.

## Proposed repair (recorded, not asked — NEVER_ASK_WITHOUT_RECOMMENDING)

Extend the existing SECOND control rather than adding a third: for any atom whose `level_current`
increases in this commit, require that the ledger file be **clean in the porcelain worktree column** —
the identical predicate already used for `file_scope` source, applied to
`docs/observability/gate_authorizations.jsonl`. A row written but not staged then refuses the commit,
in the same direction and vocabulary as the control beside it.

**R15 mutation proof required both ways** (this is the whole point of the finding, so it must not ship
unproven): the MUST-FIRE case is a staged `level_current` increase whose authorising row is present in
the worktree and absent from the index — today that commits, and after the repair it must red. The
NULL CONTROL is the same commit with the row staged, which must stay green; without that half the
repair could be a gate that simply always refuses.

## Class check (R10)

The instance fix is "commit both halves together", which is what this pass did and which is exactly the
remembered discipline that MAKE_IT_STICK says will evaporate. The class is **a two-part control whose
halves read different trees**, and at least one sibling is already on file
(`feedback_a_two_part_control_can_have_each_half_read_a_different_tree`). Worth asking, when this draws,
whether other gates in the 10-gate pre-commit chain read one input from the index and another from disk —
that sweep is the class closure, not the single-line fix above.
