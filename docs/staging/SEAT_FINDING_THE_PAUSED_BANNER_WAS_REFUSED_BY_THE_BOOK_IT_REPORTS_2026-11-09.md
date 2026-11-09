**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The paused banner was refused by the book it reports, so poesys.net said "Verified 3 Nov" through every refusal on 8–9 Nov

Found by the seat executor on Mon 9 Nov, 05:20 GMT, reading the live status line after the 04:00
publish attempt (drawn item `read-the-monday-status-line-against-the-gate`; subject 58d90c457, the
change that makes a domain-invariant refusal print as `paused_gate` in the rule's words).

## What the live line said

`https://poesys.net/data/publish_provenance.json` at 05:20Z: `verification_state: verified`,
`written_at: 2026-11-03T02:24:29Z`, `paused_gate: null`. The director's 7 Nov item 3 — "'Not
updated' should never be silent" — was not just silent on the live site. The site said the
opposite: that it was verified.

The shared tree's own copy said the right thing: `paused` since 2026-11-08T20:48:26Z, with the gate
sentence. **58d90c457 works up to the file. The file never reached origin.**

## Why: two defects, both observed

**1. The banner commit was gated on the refused book (the cause of the silence).** In
`sim-runner-log.md`: `Provenance banner commit FAILED (rc=1)` at 8 Nov 20:59, 9 Nov 04:29 and
04:58. Each time it was the site lane:
`site/explore/test_the_tariff_label_is_the_term_in_force.py::test_every_printed_tariff_is_the_term_the_bills_record_at_that_moment`,
4 labels on PROS-2017-0183. That test reads `site/data/explore_cast.json` **from disk**. On a red
cycle the shared tree's `site/data/` holds the refused book: 1,337 modified files, written by the
publisher and then not committed. On origin's feed the same test passes (2 passed, run in this
worktree at 05:25Z). `_commit_and_push_paths` was a pathspec `git commit` in the shared tree, and
the hook chain grades the working copy. So the gate refused the banner because of the content the
banner exists to say was refused. That is the partial-commit defect `tools/surgical_land.py` was
written to close (its docstring, "THE SECOND DEFECT IT CLOSES"). The content publish moved to it on
2026-09-08; the banner never did.

**2. The gate sentence was cut mid-clause.** `plain_refusal` capped each statement at 200
characters but not the sentence. With three rules it ran past `PAUSED_GATE_CHARS` (900), and
`record_paused` sliced it: the stored line ends "(unit: book: its successful DD collections,". The
control asserted `len(plain) <= 900` on a two-rule fixture, so it was keyed to that answer rather
than to the property.

## What changed (this commit)

- `_commit_and_push_paths` lands through `surgical_land.land` (new `_land_liveness_surface`), which
  gates a clean extract of HEAD plus the named path. The shared index and working copy are no
  longer read. A lost race is retried inside `land`, so the old git ref-race re-land
  (`_lost_the_ref_race`, `_reland_after_lost_ref_race`) is gone along with the `git commit` it
  served.
- `surgical_land.NothingToLand` (a `LandingRefused` subclass) marks the byte-identical steady state
  by type, so the banner stays quiet when nothing changed.
- `plain_refusal(..., limit=)` fits the sentence to the line. Statements shorten first, then go;
  only then are trailing rules counted ("and N more"). Every rule's ID and count survives. The
  publisher passes `publish_provenance.PAUSED_GATE_CHARS`.
- Controls: `tests/background/test_the_banner_is_gated_on_its_commit_not_on_the_refused_working_copy.py`
  (this replaces the ref-race file), and the fitted-sentence leg in
  `test_the_status_line_names_the_gate_that_refuses_the_publish.py`, run against both live
  refusals. Three mutations were run and all three fired: ignore `limit`; drop the `NothingToLand`
  arm; restore a `git commit` call.
- Deleted: four `test_process_run_complete.py` tests whose subject was the removed `git commit` /
  `git add` call (the env on `git commit`, the liveness-vs-content deadline asymmetry, and two
  `git add` refusal legs). The asymmetry is now impossible by construction, because both routes run
  the same landing. `_commit_hook_env` and `_git_add_or_refuse` now have no production caller.
  They are left for a cleanup rather than widening this commit.

## Pre-registration (filed before the next cycle runs)

LATENT, not BLOCKING: the repair is in the commit that files this. What is still owed is the live grade below. Archive to `done/` once predictions 1–4 are graded.

Predictions for the first red publish cycle the shared tree's publisher runs on a checkout that
contains this commit:

1. `sim-runner-log.md` shows no `Provenance banner commit FAILED` that names a `site/**` test which
   passes on origin's feed.
2. A `chore(provenance): verification paused banner` commit reaches origin within that cycle.
3. `https://poesys.net/data/publish_provenance.json` reads `verification_state: paused` with
   `paused_since` = 2026-11-08T20:48:26Z (the stamp is preserved, not re-stamped).
4. Its `paused_gate` ends with "." and is at most 900 characters.

If 1 holds and 2 fails, the next suspect is a refusal the clean extract also gives: a red on HEAD
itself, or the behind-origin refusal. Name it from the log; don't re-derive it. If the publisher's
next cycle is GREEN, predictions 2–4 cannot be graded. Say so, and do not count it as a pass.

## Not done here

The 900-character line is long for a status banner. Whether the banner should carry the sentence
or link to `docs/reports/DOMAIN_INVARIANTS.md` is a presentation call I have not made.
