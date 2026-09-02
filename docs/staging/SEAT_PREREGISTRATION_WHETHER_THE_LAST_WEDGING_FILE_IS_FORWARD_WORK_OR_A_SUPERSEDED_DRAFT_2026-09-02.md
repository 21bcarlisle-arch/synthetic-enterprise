# [SEAT PREREGISTRATION] Whether the last file wedging publish is forward work or a superseded draft

**Severity:** RECORDED
**Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** D_opening_dd_seasonal_sizing
**Written:** 2026-09-02 19:4x UTC, BEFORE the measurement it names.

## Why this is written before the answer

`SEAT_FINDING_THE_RECONCILER_MANUFACTURED_THE_FORK_IT_EXISTED_TO_CLOSE_2026-09-02.md` §7 graded its
own prediction as REFUTED: closing the fork did not publish, and the next gate is
`tools/level_promotion_gate.py`. That gate's refusal at 18:47 named four files. **Three of them have
since stopped qualifying** — `company/billing/raw_account_export.py` is clean at HEAD,
`simulation/dd_balance_book.py` and `tests/simulation/test_dd_balance_book.py` are staged with a
clean Y column, and `dirty_source_paths` blocks only on the Y column.

**One file is left:** `company/billing/statement_export.py`, ` M` (modified-unstaged) in the shared
tree, inside the atom's `file_scope` (`company/billing`), and therefore the whole remaining wedge.

The repair depends entirely on which of two things that file is, and I do not know which:

* **(A) FORWARD WORK** — the orphaned DD lane's unlanded edit. Repair: land it with the level move
  in one commit, per the gate's own instruction.
* **(B) SUPERSEDED DRAFT** — an older copy of work already on origin, left behind because the shared
  tree could not advance. Repair: it must NOT be landed; landing it reverts `2dacf1d9d`. The tree
  copy is discarded in favour of HEAD.

These call for opposite acts, and doing (A)'s act on a (B) file is the armed-silent-revert shape
this very finding chain is about.

## The prediction, before running the diff

**I predict (B), a superseded draft.** The reasoning, so it can be wrong for a nameable reason:
commit `2dacf1d9d`'s own subject says it carried *"the raw-export repair and the statement export"*
onto this lane's fork correction. If the statement export landed there, the shared tree's copy
predates it, because the shared tree never advanced while the DD lane was editing — exactly the
mechanism §5a established for `30adb2b66`.

**Confidence: moderate, not high.** The competing reading is that `2dacf1d9d` carried only *part*
of the statement-export work and the tree holds a genuine increment on top.

**The falsifiable reading:** `git diff HEAD -- company/billing/statement_export.py` in the shared
tree.

* If the diff **removes** content HEAD has and adds nothing not already at HEAD → (B) confirmed.
* If the diff **adds** content absent from HEAD → (A), and this prediction is refuted.
* If it does both → neither, and the file is the "newer table, older function" shape: it must be
  composed, not chosen, and I will say so rather than forcing it into (A) or (B).

**Constraint on me, recorded so it can be checked afterwards:** whichever branch it is, I will not
`git checkout` the path and will not `git stash`. The preserved ref
`refs/preserved/dd-payload-2026-09-02-1938` (`6bfe07542`) already holds the shared tree's full
uncommitted state, taken before I read anything.

---

## GRADED 19:5x UTC. **REFUTED — it is (A), forward work.**

The diff is purely additive. It adds a `VAT_INCLUSIVE` constant carrying a sourced origin note, and
adds `"vat_basis": VAT_INCLUSIVE` to the catch-up line's fields. **It removes nothing HEAD has.**
Recorded beside the prediction rather than softening it: I reasoned from `2dacf1d9d`'s commit
subject naming "the statement export", and a commit subject naming a file is not evidence about
which *version* of that file it carried. That is the error, and it is the same class as reading a
doorbell instead of the artefact.

**What the refutation is worth, because a wrong prediction that changes nothing is not worth
filing:** branch (B) would have had me discard the tree's copy. Had I acted on the prediction
instead of measuring, I would have destroyed a sourced constant and the `vat_basis` disclosure it
puts on the catch-up line — and destroyed it silently, since nothing downstream reads that field
yet.

**The constraint held:** no `git checkout <path>`, no `git stash`. `git status --porcelain` for the
shared tree at the end of this turn is pasted in the finding this prereg feeds,
`SEAT_FINDING_THE_LAST_PUBLISH_WEDGE_WAS_ONE_UNSTAGED_FILE_2026-09-02.md`.

### A second thing was refuted that I had not pre-registered, and it is the larger one

I hand-picked the payload's file list and **missed `tests/company/billing/test_dd_review_runner.py`**,
which is `M ` (staged) in the shared tree. Running the partial copy produced **8 failures** that
looked exactly like "the orphaned work is incomplete and red". It was not. The complete payload is
**3061 passed**. Filing the first reading would have condemned a sound payload on evidence I had
manufactured by copying it badly. The systematic re-derivation — `git status --porcelain --` over
the whole subject rather than a list I typed — is what corrected it.
