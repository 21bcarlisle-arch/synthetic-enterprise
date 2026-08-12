# WORKER FINDING — the by-construction namer reads a clause boundary, and a quotation of its own rule, as a claim

**Severity:** LATENT · **Lane:** H_harness

**Filed** 2026-08-12, by the tick that closed
`WORKER_FINDING_THE_BY_CONSTRUCTION_GATE_IS_SILENCED_BY_AN_ORDINARY_WORD_2026-08-12` — found by
re-running the census with that finding's fail-open hole closed, which is the only reason these
two were visible at all.
**Class** control-that-cannot-fail (R15), noise half: a keyword gate reading a sentence it cannot
parse. Same family as `WORKER_FINDING_G6_FIRES_ON_THE_WORD_NOTHING_ANYWHERE_IN_A_WRAPPED_INDEX_NOTE_2026-08-11`.
**Subject** `background/finding_severity.py::_BY_CONSTRUCTION_PATTERNS`.
**Not fixed on sight** (SELF_INTERRUPT_DISCIPLINE): widening the patterns to fit four observed
documents is the inverted-fit defect, and the census is now honest with these two named.
**Routed to `measurements_that_mirror`** by `background/finding_classes.py`, on the phrase "own
rule" in the title — the wrong class (this is a namer's precision, not a measurement reading its
own subject back). Recorded rather than corrected by retitling: editing a document's words to move
it between classes is the same inverted fit as editing prose to satisfy the namer, and the routing
is derived, never hand-kept. That the router picks a class on one phrase is worth its own look.

## The measurement that produced it

First census taken with the escape hatch closed: **4 named documents, of which 2 are true**. That
precision is stated on the live record beside the 4 — a number whose error is unstated is the class
this project keeps filing.

## Shape 1 — the subject and the predicate meet across a clause boundary

    re.compile(r"\b(?:instrument|control|gate|check|oracle|measure|metric)\b[^.\n]{0,90}"
               r"\b(?:is|was|are|were)\s+(?:lying|untrustworthy|wrong|broken)", re.I)

The 90-character gap is bounded by the sentence, not by the clause, so any two clauses sharing a
sentence can supply the noun and the verb between them. Observed, in
`WORKER_REPORT_THE_WRONG_POPULATION_WAS_A_POPULATION_NOTHING_STILL_PRODUCED_2026-08-12.md`:

    "the control was right and my shortcut was wrong"

named as `control … was wrong`. The document says the exact opposite of what it is named for.

## Shape 2 — a document that quotes the rule is named by the rule

`WORKER_REPORT_OPS9_EVERY_FINDING_NOW_CARRIES_A_MACHINE_READABLE_SEVERITY_2026-08-12.md` contains
the instrument's own description — *"names any non-BLOCKING doc whose own text says an instrument,
a control or a published figure is wrong"* — and is named three times for it. Every future document
that explains this instrument inherits the same permanent name. Self-reference, not a defect claim.

## Why LATENT and not BLOCKING

These are FALSE POSITIVES, and a false positive costs one line to answer. The instrument's
published figure is not overstated in the direction that matters — nothing is being let through —
and the 4 is on the record with its 2-of-4 precision stated, so no reader is misled. The
fail-open half, which was BLOCKING, is closed.

## The fix, when drawn

1. **Shape 1** — require the subject and the predicate to sit in the same clause: forbid the gap
   from crossing ` and `, ` but `, `;` or `, ` unless the crossing is a parenthetical between
   commas. Prove it BOTH ways on the two live sentences before trusting it: the true positive
   ("the gate that certifies this lane is lying about its own subject") must survive the narrowing,
   which is what makes this worth a test rather than an edit.
2. **Shape 2** — a quotation guard is the wrong instinct (an instrument that ignores quoted text
   can be evaded by quoting). The narrower, honest move is to exclude the ONE sentence that is this
   instrument's own published description, keyed to the string in `finding_severity.py`'s docstring
   so the exclusion cannot outlive the sentence it excludes.
3. Re-run the census and restate the precision. Neither fix may be accepted on the four documents
   that motivated it alone — that is calibrating the instrument to its own sample.

## What this finding is NOT

Not a claim that any simulation output, gap value or financial figure is affected: this instrument
reads staged markdown and nothing else. Not a claim that the escape-hatch repair is wrong — it is
proven both ways by two mutations. The claim is scoped to the namer's precision on prose.
