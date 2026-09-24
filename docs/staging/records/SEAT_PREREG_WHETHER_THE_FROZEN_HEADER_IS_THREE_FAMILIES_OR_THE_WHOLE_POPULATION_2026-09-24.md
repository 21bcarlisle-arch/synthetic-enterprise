**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# PRE-REGISTRATION — is the frozen repetition count three families, or all eleven?

Written BEFORE the measurement, while drawing
`escalate-derives-its-repetition-count-from-the-document-rather-than-trusting-a-callers-literal-1`.

## What prompted it

The landed finding
(`SEAT_FINDING_THREE_ALARM_FAMILIES_BYPASS_NOTIFY_AND_HARDCODE_REPEATS_1_...`, `612bd9ffe`) scopes
the defect to the three families that call `escalate()` directly and pass a literal `1`. While
reading `escalate()` to fix that, I noticed the header paragraph — *"This alarm has fired **N**
times without its state changing, over **Wh**"* — is written ONCE, at birth, into the document body
and is never rewritten. `_note_still_live` appends a new line each day; nothing touches the header.

If that is right, the literal `1` is the WORST case of a defect that has a milder form in every
family, including the ones that come through `notify()` with an honestly measured count. The
header is the first line a draw sees, and a header pinned to day one is a claim about a document
that has been accruing evidence for eight days.

**That changes the remedy's scope**: deriving the count only for the three direct callers would
leave the other eight frozen. Deriving it in `escalate()` for everyone, from the document itself,
fixes both — which is the R10 shape the finding already asked for, for a second reason it did not
know about.

## The claim under test

> For every live alarm document in `docs/staging/` (root and `in_progress/`) that carries at least
> one machine-written still-live line, the count stated in the **header** is LOWER than the highest
> count stated in that same document's own still-live lines.

## The prediction, registered before running it

**All of them.** The header is stamped at birth from the caller's argument at the moment of the
first firing, and every still-live line after it is stamped from a later firing, so the header can
only be the earliest and usually the smallest reading of the same quantity.

I expect the gap to be largest on `DEADMAN_WORKTREE_UNDECLARED` and `DEADMAN_LAUNCH_ARTEFACT`,
which fire on a fast cadence, and exactly `0` on any document whose highest still-live count equals
its birth count by coincidence.

## What would refute it

- Any document whose header count is GREATER THAN OR EQUAL to its own maximum still-live count
  refutes "the header can only be the earliest reading" for that family. A single one means the
  header is being rewritten somewhere I have not found, and the remedy must not assume it is not.
- If the population of documents carrying still-live lines is smaller than eight, the finding's
  "three of eleven" framing is the right scope after all and this is a narrower defect than I think.

## What this pre-registration does NOT claim

Not that the still-live counts are themselves comparable across days. They are plainly not: on
`DEADMAN_WORKTREE_UNDECLARED` they run 3, 22, 51, 70, 106, 298, 3 — a counter that resets, not a
total. **They must never be summed**, and the remedy below does not sum them. The claim here is
only about the header versus the maximum of the lines beneath it, which is a comparison of one
reading of a quantity against another reading of the same quantity.

## The remedy this is deciding the scope of

See `SEAT_FINDING_THE_HEADER_IS_STAMPED_ONCE_AND_NEVER_RE_DERIVED_2026-09-24.md` for the answer and
what was built.
