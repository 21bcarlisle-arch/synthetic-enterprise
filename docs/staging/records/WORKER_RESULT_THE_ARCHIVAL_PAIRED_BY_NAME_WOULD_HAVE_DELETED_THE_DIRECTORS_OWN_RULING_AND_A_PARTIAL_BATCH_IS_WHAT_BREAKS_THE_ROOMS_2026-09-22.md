**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
claim `the-staging-archival-is-116-deletions-the-guard-itself-refuses`

# The archival paired by name would have deleted the director's own ruling, and a partial batch is what breaks the rooms

*The drawn item said to commit each deletion in the same commit as the `done/` copy that replaces
it. Both halves of that sentence hide a defect. Pairing by NAME passes it while losing the bytes —
three of 115 pairs have a destination that exists and does not carry the content, one of them 243
of 279 lines of the director's verbatim console record. And a batch that is not CLOSED under the
pairing manufactures the very TWO ROOMS state the rule exists to prevent: the full set has zero
collisions, my first partial batch had one.*

---

## 1. What was landed

111 removals with all 228 `done/` destinations that go with them. Before this, `docs/staging/`
carried 115 removals that had happened on disk and never in git, so every orientation — the seat's
and every worker tick's — ranked the next piece of work off a queue of notes dispositioned days
earlier.

Four are held back, each for a named reason, in §2 and §3.

## 2. A destination that EXISTS is not a destination that CARRIES THE CONTENT

The item's instruction is satisfied by name-matching. Name-matching is not the property wanted.
Measured over all 115 pairs by content, not by name:

| | count |
|---|---|
| byte-identical move | 102 |
| differs, benign | 5 |
| **differs, real content loss** | **3** |

The five benign differences are a re-captured `Source:` provenance line, dropped `/compact` turns,
and the severity-header rewrite that *is* the archival act. Those landed.

The three held back:

- **`console/DIRECTOR_CONSOLE_2026-08-30.md`** — 243 of 279 lines absent from the `done/` copy
  (32798B → 2505B). Among them, verbatim: *"Repair it — don't accept the limitation. My ruling on
  suspending I&C was that the SIM keeps creating those accounts and only the company's book
  changes. A dial that alters which households exist is the opposite of that, and it invalidates
  every comparison across it."* The `done/` copy is a thinner capture of the same day, not an
  archive of this file. Landing the deletion destroys a primary record of the director's words.
- **`SEAT_RESULT_THE_RE_RUN_WITHDRAWS_BOTH_BOUNDED_LEGS_...2026-09-18.md`** — the `done/` copy drops
  a CORRECTION filed beside the claim, which under this project's own rule is the only evidence the
  measurement was designed before its answer was known. **Both halves held**, so neither room is
  left contradicting the other.
- **`drafts/NEXT_PHASE.md`** — a pure name collision. `done/NEXT_PHASE.md` is an unrelated Phase 6b
  proposal sharing not one line with the Phase RY document at HEAD.

`.gitkeep` is held on the same reasoning: it name-matched `done/.gitkeep` and is not an archival.

**The class:** an archival is a MOVE, and a move is only a move if the content arrives. Every
instruction in this tree that says "pair the deletion with its destination" is checkable by name in
one line and by content in five, and the one-line version is the one that gets written.

## 3. The batch must be closed under the pairing, and `git status` is the wrong oracle for it

The first attempt was refused:

```
[test-gate] ❌ FINDING-CLASS CONSOLIDATION BROKEN -- COMMIT REFUSED.
  - TWO ROOMS WORKER_RESULT_W1_14S_NAMED_NEXT_ACTION_IS_THE_DESIGN_THE_DIRECTOR_REFUSED_...md:
    present in done AND root
```

**The tree did not hold that collision. My batch created it.** Measured both ways on one tree state:

| set | two-rooms collisions in the resulting tree |
|---|---|
| all 115 removals + all 229 additions | **0** |
| my first partial batch | **1** |

The cause is the oracle. I built the first batch from `git status --porcelain`'s `" D"` — a
deletion in the *working tree*. Another lane had already staged that one removal in the **shared
index**, where it reads `"D "`, so my filter did not see it. The `done/` copy therefore landed while
the root copy stayed at HEAD.

**The oracle without that blind spot is HEAD's tree against the disk** — `git ls-tree -r HEAD`
minus what is on disk. It sees a removal whatever the index says about it, and it is what this
landing is built from. In a tree where several lanes write at once, the index is *someone else's*
state; the disk and HEAD are the two that are actually shared.

## 3b. Archiving a note breaks every `LANDED` claim that cites it by its root path

A third refusal, from a different gate, on the next attempt:

```
[test-gate] done/WORKER_RESULT_THE_PAGE_STATED_A_SELECTION_SIGN_...md: claims
  `docs/staging/WORKER_RESULT_THE_LEVEL_LEGS_SIGN_NOW_REACHES_THE_READER_...md` LANDED,
  but it is ABSENT from the tree this commit creates.
```

Seven such claims across six archived notes. None of the seven documents is gone — every one has
simply **moved room**: four to `done/`, three to `records/`. The citing note names the path the
document had when the claim was written, and the archival is precisely the act that invalidates it.

This is structural, not incidental. A staging note that cites a sibling as LANDED is citing a
**mutable location**, and the disposition workflow's whole purpose is to change that location. The
citation is correct on the day it is written and false the day the cited note is dispositioned —
and because dispositions land in bulk, they all go false at once.

Repaired here by repointing all seven citations at the room each document now occupies. The claims
are the same claims; only the address changed. All six citing notes are `done/` copies landing in
this same commit, so this edits nothing another lane has committed.

**What this does not fix:** the next bulk archive will do it again. The durable repair is for the
LANDED check to resolve a staging citation by document identity — the filename is already unique
across rooms — rather than by exact path. Filed here rather than built, because it belongs to the
check's owner and not to this archival.

## 4. What I did NOT establish

Whether the `done/` copy of `DIRECTOR_CONSOLE_2026-08-30.md` was produced by a capture that ran
against a partial session set, or whether something truncated it after the fact. Both are
consistent with what I can see. The root copy is preserved, so the question stays answerable; I am
not guessing at it here.

The remaining four paths are a judgement about the director's own record, and the right next act is
to reconcile the two console captures into one that is a superset of both — not to pick a winner.

## 5. Predictions filed before the measurement

Written before running the content comparison, kept here whatever they turned out to be:

1. *"Most pairs will be identical moves; a handful will differ by an archival header."* — **held.**
   102 identical, 5 differing benignly, all five explained by the header/provenance shape.
2. *"Any difference large enough to matter will be in the notes, not the console captures."* —
   **refuted.** Both of the two worst losses are outside the notes: the largest by far is a console
   capture, and the total loss is a `drafts/` collision. The director's own record was the least
   protected part of the pile, because nothing in the archival path ever looked at it.
