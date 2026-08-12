# WORKER FINDING — the by-construction gate is silenced by an ordinary word, and fires inside a denial

**Severity:** BLOCKING · **Lane:** H_harness

**Filed** 2026-08-12, from the H27 Expert Hour #21 landing, which tripped it.
**Class** control-that-cannot-fail (R15) — FAIL-OPEN on the escape hatch, plus a false positive in
the other direction. Subject is `background/finding_severity.py::by_construction_violations`,
landed **today** as OPS9 deliverable 1 (`DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE_2026-08-12`).
**Rank requested** top of H_harness — the figure it produces is on the live record.

## Why this is BLOCKING and not LATENT

`docs/status/LATEST.md` cites this instrument's output as evidence: *"the by-construction rule is
checkable, not merely written: `--by-construction` names any non-BLOCKING doc whose own text says
an instrument, a control or a published figure is wrong; **0** after this pass."* That **0** is the
claim. Both defects below mean the 0 is not evidence for it. R15: an instrument whose passing
number is reachable without the property holding is not a control.

## Defect 1 — FAIL-OPEN: any of nine ordinary words silences a whole document

The gate skips a document entirely when `_REPAIRED_RE` matches its header block:

    \b(?:FIXED|CLOSED|REPAIRED|repaired|landed|relieved|CLEARED|cleared|DISCHARGED|discharged|accepted)\b

That is a bare word match, anywhere in the header block, with no requirement that the word refer to
*this* finding or to a repair at all. `landed`, `cleared`, `accepted` and `closed` are among the most
ordinary words in this project's finding prose — "the cut landed", "the queue cleared", "accepted as
debt" — and `header_block` is everything before the first `## `, which is exactly where a finding
states its provenance.

**Observed with evidence.** Two documents, identical but for one incidental clause in the header,
both saying in their own body that a published figure is wrong:

    doc A header: "**Filed** 2026-08-12. The published figure is wrong: ..."
    doc B header: "**Filed** 2026-08-12. Prior work landed separately. The published figure is ..."

    by_construction_violations() names: [('LATENT', 'published figure is overstated')]
    by_construction_evidence(doc B) finds:  ['published figure is overstated',
                                             'published figure is wrong: the door overstates']

Doc B's own text carries **two** matching phrases and the gate does not name it. One unrelated word
took it off the census. This is the fail-open pattern in its purest form: the checker passes because
it never looked.

## Defect 2 — the phrase is matched inside its own denial

The patterns are substring regexes with no negation handling, so a document stating that it does
**not** claim a figure is wrong is named as claiming it. That is how this finding was discovered:
`WORKER_FINDING_A_MUTATION_THAT_PATCHES_BOTH_SIDES_OF_ITS_SEAM_2026-08-12.md` contained

    "Not a claim that any published figure is wrong: no gap value ... depends on either control."

and was named `BY-CONSTRUCTION LATENT ... published figure is wrong`. Same class as the already-filed
`WORKER_FINDING_G6_FIRES_ON_THE_WORD_NOTHING_ANYWHERE_IN_A_WRAPPED_INDEX_NOTE_2026-08-11` — a
keyword gate reading a sentence it cannot parse — but on a new instrument, one day old.

The two defects compound in the worst direction. Defect 2 pressures every future finding author to
avoid the words, and the cheapest way to satisfy the gate is to drop a word from Defect 1's list
into the header. A gate that is noisy on honest docs and silent on evasive ones inverts its own
purpose, and its 0 measures authorship convention rather than the corpus.

## Recommendation — not asking, this is what the next draw here should do

1. **Make the escape name its subject.** A skip must require an explicit, structured header field
   —`**Repaired:** <commit/atom>` or the OPS9 severity header carrying `RECORDED` with a pointer —
   never a free-text word match. An escape hatch that any prose can open is not an escape hatch.
2. **Mutation-test both directions before trusting the census again** (R15): a doc that says a
   figure is wrong must be named *with* each of the nine words present in its header; a doc that
   denies it must not be named. Neither test exists today — the instrument's own suite asserts the
   census count, which is exactly the tautology shape (the checked value derived from the checker).
3. **Re-run the census after (1)** and treat the resulting number as the first real one. Do not
   restate today's 0; it was measured with the hole open, and the honest statement is that the
   population was never fully examined.
4. Do **not** hand-edit finding prose to satisfy the current patterns beyond the one false positive
   already corrected above — that is calibrating the corpus to the instrument, which is the
   inverted-fit defect this project has filed before.

## What this finding is NOT

Not a claim that any simulation output, gap value or financial figure is affected — this instrument
reads staged markdown and nothing else, and no company or world number passes through it. Not a
claim that the OPS9 severity *classifier* is wrong: the 127-document / 0-UNCLASSIFIED census is a
different code path, fail-closed, and is not in question here. The claim is scoped to the
by-construction sub-check and to the one sentence of LATEST.md that rests on it.
