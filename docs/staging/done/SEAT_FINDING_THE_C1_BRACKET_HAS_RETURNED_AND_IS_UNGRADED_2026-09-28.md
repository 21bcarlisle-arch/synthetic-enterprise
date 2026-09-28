**Severity:** BLOCKING · **Lane:** D_billing_metering · **Atom:** `unminted` · **Class:** `measurements_that_mirror`

# The C1 bracket's three runs have returned and are ungraded

Written 2026-09-28T15:18:59Z by a queued unit, not by a session. The waits' rc was 0. Nothing
here is graded.

- (a): artefact present; account-diff rc=0 -> `/var/tmp/se-c1-bracket-a/account_diff.json`
- (b): artefact present; account-diff rc=0 -> `/var/tmp/se-c1-bracket-b/account_diff.json`
- (c): artefact present; account-diff rc=0 -> `/var/tmp/se-c1-bracket-c/account_diff.json`

**Work.** Grade C1–C6 and the decision rule in
`docs/staging/records/SEAT_PREREG_THE_C1_BRACKET_THREE_RUNS_AT_ONE_COMMIT_2026-09-28.md`, in a
`SEAT_RESULT_` record beside it. Each artefact's `producing_commit` must be `fcba478b7`,
or the run is void. (c) was relaunched at 12:39Z at  after its first attempt bound
at  (voided). (b) is stamped , a docs-only fork_salvage of 
(ref ): record that as a DEVIATION with
docs/context-handshake-latest.md
docs/observability/book_growth_campaign.json
docs/observability/book_subset_verdict.json
docs/observability/coupled_gap_ledger.json
docs/observability/fidelity_evidence_ledger.json
docs/observability/token-log.md as evidence -- do not count it silently. The `[leg 4b]` totals for C2/C3 are in the three logs. Then write in the
selection finding which outcome holds, and remove the `/var/tmp/se-c1-bracket-src` worktree.
If the director has answered NTFY `N8U7crm2DRQP` ("bounce" or retry), fold that in. Then move
this file to done.

## Closed 2026-09-28 ~16:50Z

All three artefacts graded. (a) and (c) are at `fcba478b7`; (b)'s fork_salvage deviation was
recorded, with evidence, in the (a)/(b) record. Grades and the decision rule's outcome ("C1 does
not matter to the sign") are in
`records/SEAT_RESULT_THE_C1_BRACKET_RUN_C_GRADED_AND_C1_DOES_NOT_MATTER_TO_THE_SIGN_2026-09-28.md`
and folded into the selection finding. No director answer to `N8U7crm2DRQP` was on record. The
`/var/tmp/se-c1-bracket-src` worktree was already gone.
