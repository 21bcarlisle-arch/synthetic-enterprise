<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- UNBLOCKS ON: nothing external — drawable now (L1 via twin standing authority; L3 batched to director) -->

# [PLANNER-MINTED / GOVERNANCE] — Cohort promotion disposition: take L1 at twin authority, batch L3 for the director with the reason (2026-07-28)

**Provenance:** MINT from `DIRECTOR_RULING_UNBLOCK_BATCH_2026-07-28.md` WORK-THIS-CREATES item 2 (rulings are a mint source, §2+§4 WORK_DEFINITION_AND_COHERENCE). Ruling §2: cohort assignment is **BUILT, blocked on level_up**. **Ruling:** if the promotion is L1/L2 → the director twin's standing authorization applies, **proceed, ledger-backed, no self-claims**; if L3 → **batch for the director's next ratification and say so**. The ruled activation (`e685eb76d`) stands: ratified values, no tuning, elicitation wall re-proven, company-side segmentation recorded **untestable at the current book**, not scored as working.

**Coverage note (no re-mint):** the cohort BUILD atoms `CA1_cohort_assignment_live`, `CA2_coverage_report_realised_cohort`, `CA3_segmentation_untestable_ledger_marking`, `CA4_cohort_activation_sequencing_verdict` all exist in `maturity_map.yaml`, code BUILT at L3-quality, `level_current: 0`, `blocked_on: director_level_up`. This deliverable is NOT the build — it is the **promotion-routing decision** across those atoms, which is not itself an atom. Minted here.

**Lane:** governance / W2_customer_generator (SIM_ACTORS front, OPEN). Doc + ledger action; drawable now.
**Target level:** the disposition itself (routes the CA atoms' level moves); no new build level.
**Deps:** reads the four CA atoms' `level_target`; uses the twin ratify path (`ratify_routine_level` / DIRECTOR_TWIN L1-L2 standing authority, `project_twin_ratifies_routine_levels`) for L1/L2 and the director-batch/NTFY channel for L3.

---

## THE DISPOSITION (stated, per the ruling's "proceed … or … say so")

Sorted by `level_target`:

| atom | level_target | route | reason |
|---|---|---|---|
| `CA4_cohort_activation_sequencing_verdict` | **L1** | **TWIN AUTHORITY — proceed, ledger-backed** | ruling §2: L1/L2 → twin standing authorization applies. CA4 is a written go/no-go verdict (PROCEED, all three counter-proposal triggers checked with disk/git evidence), the lightest of the four. |
| `CA1_cohort_assignment_live` | **L3** | **BATCH for director's next ratification** | ruling §2: L3 → director-reserved (R16). Code BUILT + R15 both-ways proven (seam re-proven post-activation, byte-identical regression green); level HELD at 0. |
| `CA2_coverage_report_realised_cohort` | **L3** | **BATCH for director** | L3, director-reserved. Joint-coverage report BUILT, 12-cell knee survives the real draw (N_scored=198), R11-verified, R15 both-ways green. |
| `CA3_segmentation_untestable_ledger_marking` | **L3** | **BATCH for director** | L3, director-reserved. Untestable-at-current-book class mechanism BUILT, 23 tests green; wiring-into-publish is a named follow-on (consumed ≠ absorbed). |

**Honest caveat carried into the batch (ruling §2):** the CA1 flip is presently **LATENT** behind the still-director-reserved `SE_DRAW_POPULATION` (default off, unwired) — it arms the release rung, changes nothing observable today. Company-side segmentation remains **untestable at the current 14-customer book** (CA3), NOT scored as working — activation is world variety, not a company book.

## Drawable work this atom creates

1. **CA4 → L1 via twin:** invoke the twin ratify path for `CA4` L0→L1 (standing L1/L2 authority, ledger-backed in `gate_authorizations.jsonl` — R16: the ledger is authority, no self-claim, no `--no-verify` on a `level_current` change). If the twin declines or the path is unavailable, fold CA4 into the L3 director batch instead and say so. On success, move `CA4.level_current` 0→1 with the ledger reference.
2. **CA1/CA2/CA3 → director L3 batch:** write the batch note (one dense item, per the ruling's "fewer advisor interventions — prefer one dense [ACT]") naming the three atoms, their built-and-proven state, the LATENT/untestable caveats, and requesting L3 ratification; NTFY it to the director. State plainly these are batched (not silently held).
3. **Register-publish:** record the disposition in the open-question register / daily note so none of the four "remains blocked-and-silent" (ruling acceptance).

## Walls untouched
- **L3 level moves** — director-reserved (R16); this atom BATCHES them, never self-bumps.
- **Curriculum values / ratified segmentation** — unchanged; no tuning (R12/R13); the ruled values (`e685eb76d`) stand.
- **`SE_DRAW_POPULATION`** — director-reserved; the LATENT flip is not armed here.
- **One-way doors** — none; a twin-ledgered L1 move and a git-reversible level bump behind the epistemic wall. Twin may NEVER answer a one-way door — CA4 L1 is neither.

— Planner mint, from DIRECTOR_RULING_UNBLOCK_BATCH_2026-07-28 item 2, 2026-07-28.
