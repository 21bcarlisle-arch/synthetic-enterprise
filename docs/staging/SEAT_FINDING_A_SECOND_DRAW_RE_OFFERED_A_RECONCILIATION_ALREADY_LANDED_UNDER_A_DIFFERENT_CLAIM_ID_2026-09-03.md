**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# A second draw re-offered a reconciliation already landed, under a different claim id

**Class:** `uncommitted_and_orphaned_work`
**Filed:** 2026-09-03, delivery seat, Lane 0, claim
`the-shared-tree-holds-a-second-copy-of-a-landed-control-and-is-armed-to-revert-it`
**Subject:** the same six-file world-provenance divergence as
`docs/staging/done/SEAT_FINDING_THE_SIX_FILE_DIVERGENCE_MOVED_NO_ANCHOR_AND_ONE_CONTROL_WAS_BUILT_TWICE_2026-09-03.md`,
offered a second time under a new claim id after the first was already discharged.

**Discharged:** `site/test_the_baseline_comparison_reaches_the_reader.py::test_the_world_these_figures_were_measured_in_reaches_the_reader_before_the_number`, `site/test_the_baseline_comparison_reaches_the_reader.py::test_the_belief_reaches_the_reader_beside_its_ceiling_and_never_alone`, `site/test_the_baseline_comparison_reaches_the_reader.py::test_the_superseded_uncorrected_reading_never_reaches_the_reader` — the same three legs the parent finding cited, re-run green here rather than assumed. By the same evidence as the two findings closed in the commit that landed hours before this claim was even drawn — nothing new was built here. This claim's own draw ledger has no first_drawn_at entry predating this turn's 15:35:25 draw, so the delivery lane's record_landing correctly refuses to bind the commits that actually did the work (06ce91bc9 at 12:40 and ef9c801e3 at 12:56, both older than this claim's first draw) to *this* id; an older commit really is somebody else's work, and forcing the bind would be the exact mis-attribution that guard exists to prevent. Re-verified fresh in this tick rather than trusting the prior note: HEAD equals origin/main at 1df22e3bd8; all six subject paths — `simulation/departure_level_anchor.py`, `site/data/value_arms.json`, `site/test_the_baseline_comparison_reaches_the_reader.py`, `tests/architecture/test_switching_rate_commons.py`, `tests/tools/test_generate_value_arms_data.py`, `tools/generate_value_arms_data.py` — are clean against origin, with the svt drift belief publishing half still present and wired into the feed and the world provenance lineage still reaching it. Full re-runs, not spot checks: `site/test_the_baseline_comparison_reaches_the_reader.py` — 78 passed, 1 skipped; `tests/tools/test_generate_value_arms_data.py` — 96 passed; `tests/architecture/test_switching_rate_commons.py` — 36 passed, 2 xfailed.

---

## Why this is worth filing rather than silently releasing the claim

The underlying defect (`docs/staging/done/SEAT_FINDING_THE_SIX_FILE_DIVERGENCE_...`) was fixed at
`06ce91bc9`/`ef9c801e3`, and the loop that re-derives it from a stale "not done in this bounded
tick" clause was explicitly closed at `11e41e1c2` (13:10) — *for the claim id that work landed
under*, `the-baseline-was-beaten-in-a-world-that-no-longer-exists`. This turn was handed a
**different** claim id, `the-shared-tree-holds-a-second-copy-of-a-landed-control-and-is-armed-to-revert-it`,
naming the identical subject and identical disposition, drawn fresh at 15:35:25 — over two and a
half hours after the fix and after its own discharge note landed. The draw ledger
(`docs/observability/.delivery_lane_claims.draws.json`) has no entry for this id, so it is not the
RE-ISSUE-of-the-same-id shape the 2026-08-30 fix (`3f33d92fa`) covers — that fix reaches back to a
claim's *own* first draw, and this id's first draw genuinely is now. It is a second, independently-
minted claim id for a piece of work that a prior seat already found, fixed, and closed under a
sibling id. Two claim ids for one subject is the parked-atom failure `CLAUDE.md` names directly:
"the thing you are about to file is usually already on the map." Filing this note under *this* id
closes the loop a second time, for the id that would otherwise be swept in 100 minutes with `paths:
[]` and re-offered again with its full prose, at the cost of another whole invocation, exactly as
the parent note predicted for its own id.

## What was NOT done, and why not

No commits were reconciled, merged, or re-gated in this tick — there was nothing left to
reconcile; the six files have been identical to origin since 12:56. No attempt was made to bind
`06ce91bc9` or `ef9c801e3` to this claim via `--landed`: they predate this id's first draw, so
`record_landing`'s refusal is correct and was left standing rather than worked around.
