# [DIRECTOR-RULING] — Page-comment authority path: RETIRE (2026-07-24)

**Type:** [DIRECTOR-RULING] via advisor bridge, answering the [ACT] "retire vs redesign the page-comment authority path". Director's word: **"Retire."**

## The ruling

The page-comment channel is **retired as a director-authority path, permanently.** It is not merely locked pending redesign: the intake, its daemon, and its staging path are decommissioned. Rationale on the record: the advisor bridge and the (pending) signed-NTFY path supersede it; a PIN-authenticated web form that stages content as the director's voice is the weakest link in the authority model, and it ran unnoticed for a week.

## What decommissioning means

1. **Daemon and intake removed**, not just stopped — the `_write_comment_to_staging` authority path deleted, the poll disabled, and any form/widget removed from every served page (the folded /supplier already greps clean; confirm site-wide).
2. **Manifest updated** so the reconciler no longer reports `director-comments: MISSING` as drift — retirement is the expected state. This closes the standing drift alarm; a self-healing reconciler must never be able to resurrect a retired authority path.
3. **History preserved:** the 35 existing `from_rich_comment_*` artifacts in `docs/staging/done/` stay as record. Retirement removes the channel, not the archive.
4. **If page comments ever return as a convenience**, they return in a clearly non-authority namespace as *unauthenticated suggestions*, visible to the director, actionable only after confirmation through the bridge or a signed director channel. They may never again be staged as director voice.
5. **Synthetic-marker class stands** (from the incident doc): test/synthetic inputs carry an unmistakable marker and cannot occupy an authority namespace.

## R15

Post-retirement, a comment submitted by any means must be **inert**: nothing staged, nothing attributed to the director, no daemon revived by the reconciler. Prove it, including the reconciler path.

**Sequencing note:** this queues behind the publish/push pipeline emergency; the channel remains locked meanwhile, so exposure is nil until it is consumed.

**Risk & proportionality:** removes an input and an authority path; archive preserved; reversible only by explicit director ruling. Tag: **proceed after the pipeline fix.**

— Advisor bridge, carrying the director's ruling, 2026-07-24.
