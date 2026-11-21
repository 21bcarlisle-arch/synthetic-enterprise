**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The E-e trial draft made every minimal-arm landing unpromotable (fixed 21 Nov 2026)

**What happened.** On 21 Nov, the executor turn for
`a-dated-media-coverage-series-for-energy-price-rise-announcements-2016-2025` landed 80e1ba16a
by `surgical_land`. `promote_worktree_landing` then refused: "uncommitted tracked changes ... M
CLAUDE.md". The writer did not make that change. Trial E-e (`background/seat_executor.py`,
`CLAUDE_MD_TRIAL_WINDOW` 21–28 Nov) writes its draft over CLAUDE.md in the worktree before a
minimal-arm turn. `_refuse_if_dirty` excludes only `SHARED_BY_DESIGN`, so it counted the draft as
unfinished work.

**The consequence, had it not been caught.** Every Opus turn in the minimal arm (about half of
them, keyed on the work id) during the trial week could land but never promote. Each would be
logged `LANDED NOTHING` and its item re-offered. The trial would then also measure this failure
rather than the CLAUDE.md difference. The minimal arm's outcomes would be biased down for a cause
unrelated to the draft's content.

**The turn's way round it.** It wrote HEAD's CLAUDE.md bytes back into the worktree (the same
bytes `_restore_claude_md` writes after the turn), promoted, and put the draft back.

**Fix (same landing).** `tools/promote_worktree_landing._is_the_trial_draft`: a dirty CLAUDE.md
whose bytes are exactly `CLAUDE_MD_TRIAL_DRAFT`'s is the machine's write and is not refused. Any
other dirty CLAUDE.md, including an edit on top of the draft, is still refused. Mutation-proven
both ways by
`tests/tools/test_the_promotion_route_refuses.py::test_the_E_e_trial_draft_over_CLAUDE_md_is_the_machines_bytes_not_unfinished_work`.

**What stays open (why LATENT, not closed).** Any minimal-arm turn between the window opening
(21 Nov 00:00 UTC) and this landing may have been logged `LANDED NOTHING` for this cause. The E-e
read (prereg `docs/staging/records/SEAT_PREREG_TRIAL_E_E_MINIMAL_CLAUDE_MD_AGAINST_THE_FULL_ONE_2026-11-16.md`)
should exclude or flag minimal-arm turns that refused on `M CLAUDE.md` before this commit.
Archive this file once the E-e read has done so.
