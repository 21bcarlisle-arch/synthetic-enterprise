**Severity:** RECORDED · **Lane:** F_risk_compliance · **Epoch:** 3 · **Atom:** none — incidental, found while landing a Lane 0 item

# Archiving a finding falsified a commons artefact's pointer, and the control reports "not in the tree" for a file that IS in the tree

**Found incidentally** while gating
`the-republished-seed-price-carries-an-unbounded-count-in-every-artefacts-own-bytes`. **Not my
subject, not fixed here, and recorded so the next lane does not re-derive it.**

## The red

    tests/architecture/test_a_commons_artefact_can_tell_when_its_source_was_revised.py
      ::test_every_verdict_can_be_recorded[superseded]   FAILED
      ::test_every_verdict_can_be_recorded[cannot_tell]  FAILED

    Refusal(artefact='subject', leg='ACTIONED', detail="recorded `superseded` and its
      `open_finding` names docs/staging/SEAT_FINDING_TWO_COMMONS_ARTEFACTS_CITE_A_PUBLICATION_
      THAT_HAS_MOVED_AND_FOUR_OF_NINE_COULD_NOT_BE_ASKED_2026-09-07.md, which is not in the tree")

## It is pre-existing, and that is measured rather than assumed

The red reproduces at `origin/main` and is unreachable from the diff it was found beside. My commit
touches `tools/generate_value_arms_data.py`, its test, `site/data/value_arms.json` and two new
`docs/staging/` documents. This control reads the regulation commons and one staging directory; it
reads none of those five paths. Reproducible at collection positions 69–70 under `-p no:randomly`,
identically across three runs.

## The cause, and the control's own defect is the interesting half

The finding **is in the tree.** It was archived:

    docs/staging/done/SEAT_FINDING_TWO_COMMONS_ARTEFACTS_CITE_A_PUBLICATION_THAT_HAS_MOVED_AND_FOUR_OF_NINE_COULD_NOT_BE_ASKED_2026-09-07.md

— present at `origin/main`, tracked, not deleted. So there are **two defects, not one**, and they
want different remedies:

1. **The commons artefact's `open_finding` pointer went stale when the finding was archived.** The
   staging protocol moves a finding to `done/` and nothing updates the artefacts that cite it by
   path. That is the ordinary shape: a pointer with one home, invalidated by a move nobody told it
   about.
2. **The control's refusal names the wrong cause.** It says *"is not in the tree"*, which is false —
   the file is in the tree, one directory down. The check asks `docs/staging/<name>` and stops, so
   *archived* and *never existed* arrive at the reader as the same sentence. Those license opposite
   actions: one is a pointer to repair, the other is a citation to a document that does not exist.
   **A refusal whose reason is false is worse than no refusal, because the reason is the part a
   reader acts on** — and this one will send someone hunting for a deleted file that is sitting in
   `done/`.

Defect 2 is the one worth fixing as a class, because it will recur on every future archival and it
is what makes defect 1 expensive to diagnose. Defect 1 is one edit to one artefact.

## The cheapest honest remedy, not taken here

Have the check resolve the cited name **anywhere under `docs/staging/`** including `done/`, and split
the refusal into two: *"names a finding that has been ARCHIVED to `done/` — the pointer is stale"*
versus *"names a finding that is in no directory and no commit — the citation is unsupported"*. Then
repair the one artefact's `open_finding`. Keyed to the property: an archival stops being a red and
starts being a named, actionable pointer repair, without anybody editing a string per archival.

**Do not fix this by pointing the artefact at `done/`** — that pins the citation to today's location
and breaks again the moment the archive is reorganised. The resolution belongs in the reader.

## What is NOT claimed

I have not established how many commons artefacts carry `open_finding` pointers, nor how many of
those are already stale. Two legs of one parametrised test fired; that is two verdicts about **one**
artefact (`subject`), not a census. **The population is unmeasured and the first step is counting
it, not fixing this instance.**
