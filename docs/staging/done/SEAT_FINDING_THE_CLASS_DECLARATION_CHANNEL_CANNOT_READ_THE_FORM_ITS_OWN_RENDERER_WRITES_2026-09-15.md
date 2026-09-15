**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS10_finding_class_consolidation`

# The class-declaration channel cannot read the form its own renderer writes, and 280 documents are declaring into it

**Filed 2026-09-15 by the delivery seat (isolated worktree), claim
`the-no-caller-pattern-cannot-reach-its-own-archived-instance`.** Not the subject of that claim —
turned up by the corpus scan it required, and larger than the defect that claim repaired.

LATENT and not BLOCKING: no published figure is wrong and no gate is red. What is established is
that the routing channel built to end a *silence* has a second mouth nobody is listening at, and
the measurement below is the size of it.

## What was measured

Every `.md` document under `docs/staging/` (7,879 of them), asked two questions: what does
`background.finding_classes.declared_class_of` read out of it, and does the document state a
real class id anywhere else in a fixed position?

| | count |
|---|---|
| declarations the parser reads (`## Class registration` + `` Belongs to `id` ``) | **76** |
| declarations it cannot read — a `**Class:** id` field on the header line | **280** |
| …of those 280, how many classify as `None`, i.e. reach no register at all | **241** |
| …how many are in the **live staging root**, where `check()` would act on them | **57** |
| …of those 57, how many classify as `None` | **53** |
| declarations it cannot read — `## Class registration` naming an id without `Belongs to` | **7** |

Reproduce: the scan is in the pre-registration's result section,
`docs/staging/records/PREREG_CAN_THE_NO_CALLER_PATTERN_SET_REACH_ITS_OWN_STRANDED_INSTANCE_WITHOUT_TAKING_ANYTHING_ELSE_2026-09-15.md`.

## Why this is the module's own shape, not a convention drift

`background/finding_classes.py` line 888 — the register renderer — emits:

> `**Instances:** N · **Class:** `publish_gate_and_wedge` · …`

**This module writes `**Class:** \`id\`` on every register it renders, and reads only
`## Class registration` / `` Belongs to `id` `` on everything else.** Authors copied the header
form off the registers, onto the same header line where `**Severity:**` and `**Lane:**` already
live and are already parsed. 280 documents did it. Nothing has ever read one.

The module's own comment block above `declared_class_of` states the case against itself exactly:

> *title-only is FAIL-OPEN in the other direction, and the failure is silent: a finding that
> genuinely belongs to a class but is titled for its MECHANISM rather than its FAMILY classifies
> as None, is not refused and not flagged, and the class document simply never learns it exists.*

That is this, at a different address. The declaration channel was the fix for it, and 241 of 280
attempted declarations land in the same silence the fix was built to end — the author DID the
act, in the form the artefact modelled for them, and the classifier did not hear it.

## How it was found, and what that says

It was found because the wide candidate for widening `no_caller_and_never_runs` would have
consolidated `SEAT_RESULT_THE_STEM_SELECTOR_CANNOT_REACH_TWENTY_SEVEN_WHOLE_TREE_RATCHETS` —
a document whose header says `**Class:** controls_that_cannot_fail`. **The document was already
telling the classifier its family, and the classifier was about to file it somewhere else.** The
temptation to widen a pattern on the verb in a title exists only because the channel that would
have settled it by declaration is deaf.

## What is owed, and why it is NOT done in this turn

The repair looks like four lines — read `**Class:**` off the header the way `**Lane:**` is
already read — and its consequence is not small: **53 live root findings would classify for the
first time**, and `derive_memberships` would then fold them into five registers and archive them
out of the live root in one step. That is a large, hard-to-unpick action to take as an
afterthought at the end of a turn about something else, and the staging root is the work queue.

Three things must be established first, and each is cheap:

1. **Do the 53 agree with their own declarations?** Measured: 0 of the 57 are contested (4 already
   classify into the class they name, 53 into nothing). So the declarations are not in conflict
   with the title regex — but they have not been read one by one, and a declaration made in a
   header field nobody read is a declaration nobody proof-read either.
2. **The lane guard must be shown to hold over them.** Several are `A_strategy_governance`. A
   declaration must NOT be able to route a document out of its own lane's blocker list — the
   guard exists in `derive_memberships`, but it has never been exercised on 53 documents at once.
3. **Should reading a declaration imply consolidation?** Today classification and consolidation
   are the same step. Declaring your family and consenting to be archived are different acts, and
   this is the first population large enough to make the difference cost something.

## Class registration

Belongs to `controls_that_cannot_fail` — a routing channel that cannot fail because nothing ever
reaches it, reporting PASS throughout. Declared here in the form the parser actually reads, which
is itself the point.
