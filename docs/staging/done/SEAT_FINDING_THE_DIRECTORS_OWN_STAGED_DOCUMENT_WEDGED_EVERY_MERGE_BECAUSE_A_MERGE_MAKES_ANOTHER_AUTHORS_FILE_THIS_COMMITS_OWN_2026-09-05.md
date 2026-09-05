**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the director staged a document and it refused every merge, because a merge makes another author's file "this commit's own"

**Measured 2026-09-05, delivery seat, from an isolated worktree. Hit live: `promote_worktree_landing`
refused my landing because origin had moved to `c0a731a50`, and
`surgical_land --merge origin/main` was then refused by the gate on a file that commit added and
mine did not touch.**

---

## What happened

`c0a731a50` is `DIRECTOR_CANON_PRODUCT_AND_MACHINERY_2026-09-05.md`, staged from the console. It
declares its severity twice in prose — `Severity: LATENT` in its **Type:** line, `Severity LATENT`
in its own commit subject — and carries no `**Severity:** … · **Lane:** …` header line, because the
director does not write in our header format and has never been asked to.

`_staging_severity_check` then refused every commit that merges it. Not a level raise: the commit
itself. And the reconciler's automatic close-the-fork merge is a commit, so the mechanism that
exists to stop a staged document blocking landings was itself blocked by a staged document.

## Why the gate's own scope argument does not hold across a merge

The check is deliberately narrow, and says so:

> SCOPE IS THIS COMMIT'S OWN DOCUMENTS, not the whole room, and that is deliberate. … A header is
> the AUTHOR's obligation at the moment of writing, and this fires exactly there.

That reasoning is sound for a document this machine writes. It fails for one it merges. **A merge
makes every incoming document "this commit's own"**, so the obligation lands on whoever next
integrates origin — a lane that did not write the file, cannot be told to have written it
differently, and has no standing to set another author's severity. The narrow scope was chosen to
avoid billing a committer for other authors' rot; a merge is the door through which it does exactly
that.

## And one corpus already has two registers that disagree about this

`background/finding_classes.py:116` defines `EXTERNALLY_AUTHORED_PREFIXES = ("ADVISOR_",
"DIRECTOR_")` and skips those documents at line 643. `background/finding_severity.py` has no such
exemption — its `classifiable_documents` filters `DOORBELL_PREFIXES` only. So the same document is
*out of scope by authorship* for one register over `docs/staging/` and *in scope and unclassified*
for the other, and nothing anywhere compares them.

## This is the second instance, and the first one was fixed as an instance

`_staging_severity_check`'s own docstring records it:

> MEASURED: two documents with no severity header
> (`DIRECTOR_DECISION_PENDING_RATE_REBASELINE_AND_SPLIT_APPROVAL_2026-08-14`, …) held
> level-recording in all 13 lanes. … Per R10 the instance fix (two header lines) does not close the
> class — this step is what makes the whole class fail automatically.

A `DIRECTOR_`-prefixed document was one of the two originals. The step built to close the class made
the *machine's* half of it fail automatically and left the externally-authored half exactly where it
was — the class recurring through the sibling the repair did not reach, three weeks later.

## What I did, and what I did not decide

I added the header line to the document, transcribing the severity it already declares, and said so
in an italic note directly beneath it. **The seat did not choose that value and is not entitled to.**
That is the instance fix, taken to unwedge the tree, and it is recorded here as an instance fix.

## The remedy, which is not this turn's work

**Exempt `EXTERNALLY_AUTHORED_PREFIXES` in `finding_severity` the way `finding_classes` already
does** — one register, one rule about authorship, both agreeing by construction rather than by
inspection. It is a strictly-scoped exemption and not a fail-open: the machine's own documents keep
the full fail-closed parse, which is where the control's evidence comes from.

It needs care, and that is why it is filed rather than done alongside a repair to a different
module. A document the director marks BLOCKING in prose would become invisible to
`gate_authorization` under a blanket exemption, so the exemption's null — *what still makes an
externally-authored blocker block* — has to be built with it. **CLAUDE.md's rule is that proposing a
gate on the director's path is itself a defect; an existing gate that fires on his path is the same
defect, and he has already ruled on this exact shape once**: *"a staged document arriving should
never block your landing"* (`origin_reconcile`'s opening docstring, 2026-09-02). That ruling was
implemented for the fork it named and not for the document's own contents.
