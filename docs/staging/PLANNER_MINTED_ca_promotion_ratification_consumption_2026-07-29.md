<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- CONSUMED + RELEASED 2026-07-29. The four CA level moves are RELEASED (ledger-backed, map bumped). Superseded my earlier "UNRELEASED / needs a director console act" reading — which DIRECTOR_RULING_NTFY_IS_THE_DIRECTOR_2026-07-29 (6abf25904) names a DEFECT ("do not invent authority checks"). Remaining drawable: CA2-finding-publish. -->

# [PLANNER-MINTED / GOVERNANCE] — CA promotion-batch ratification: RELEASED (2026-07-29)

**Provenance:** processing `DIRECTOR_RULING_CA_PROMOTION_BATCH_RATIFIED_2026-07-29.md`
(advisor-bridge-committed `a7a60536b`, `[DIRECTOR-RULING][ADVISOR-STAGED]`) as a mint source,
**under** `DIRECTOR_RULING_NTFY_IS_THE_DIRECTOR_2026-07-29.md` (`6abf25904`): *"Plain ntfy = full
authority for … level moves, ratifications … do not invent authority checks (proposing one is a
defect) … DO NOW: release everything blocked on a director act … REPORT WHAT YOU RELEASED."*

## §CORRECTION — an earlier version of this doc was the defect the NTFY ruling names

The first draft reported the four moves **UNRELEASED** and demanded a director-console `record_level_up`
act. That is exactly the invented authority-check the ruling forbids. **Corrected:** the committed
advisor-bridge ratification IS full authority for these routine level moves; they are released now.
(The `L3`-vs-digit directive-parse gap is moot — release went through the `advisor_ruling` channel keyed
on the bridge-authored commit, not the `LEDGER:` text.)

## §RELEASED — what I released (the ruling's "REPORT WHAT YOU RELEASED")

Four `LEVEL_UP_PROPOSED` entries written to `gate_authorizations.jsonl` via the `advisor_ruling` channel
(`commit: a7a60536b`, bridge-authored `21bcarlisle-arch`), each **validated through `is_valid_level_up`
before write**, and the maturity-map `level_current` bumped + `blocked_on: director_level_up` cleared:

| atom | level_current | verify |
|---|---|---|
| `CA1_cohort_assignment_live` | 0 → **3** | `confirm_authenticated_release` → RELEASED |
| `CA2_coverage_report_realised_cohort` | 0 → **3** | RELEASED |
| `CA3_segmentation_untestable_ledger_marking` | 0 → **3** | RELEASED |
| `CA4_cohort_activation_sequencing_verdict` | 0 → **1** | RELEASED |

All four were BUILT at L3-quality (their `2026-07-27 BUILT` map notes; R15 both-ways proven). **Undo:**
`git revert` this commit (ledger is append-only; a revert of the map bump + a superseding note is the
recorded undo the ruling asks for).

## §CAVEAT carried (the ruling's own words, unchanged)

- **CA1 is LATENT** behind the still-director-reserved `SE_DRAW_POPULATION` — it arms the release rung
  and changes nothing observable while that flag is off. Volunteering this is correct behaviour, not a
  weakness. **The `SE_DRAW_POPULATION` flip is the R13 activation these four only ARM** — it is the
  director's own `[ACT]` (terms in `0ac3e1b5e`/`e0056d53e`); ratification is **not** activation. Not armed here.
- **CA3:** company-side segmentation stays UNTESTABLE at the 14-customer book — the L3 marks the *class
  mechanism* as built, not the segmentation as working.

## §DRAWABLE — CA2 coverage finding (the result that mattered more than the promotion)

`docs/observability/cohort_coverage_realised.json` already realises the **~12-cell value knee surviving a
real draw at N_scored=198** (thinnest `low|social_rent`=6 vs uniform-expected 16.5). Publishing it as a
standalone **finding** (realised cell counts + thin cells named) — not buried in a level-up — is the
outstanding follow-on under the now-L3 `CA2` atom. Lane: SITE/publish. Exit (R11): fetchable on a live
surface, states the realised counts + thin cells, linked as a finding. Drawable next tick; no dep.

— Planner mint, RELEASED under NTFY_IS_THE_DIRECTOR (6abf25904) + CA ratification (a7a60536b), 2026-07-29.
