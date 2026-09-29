**Severity:** LATENT · **Lane:** A_strategy_governance · **Atom:** `value-arms-error-bar`

# The served selection sign does not reproduce at HEAD, and the decision fingerprint does not determine the residual

**2026-09-26.** Result of the 18-seed re-run at HEAD, graded in
`docs/staging/records/SEAT_PREREG_THE_EIGHTEEN_SEED_RE_RUN_AT_HEAD_REPRODUCES_THE_SERVED_RESIDUALS_2026-09-25.md`.

1. **HEAD does not reproduce the served family on any of its 18 seeds** (`agreement_fold_rc=2`).
   The published NEGATIVE selection direction (−£959.78, 2.50 sems) comes from runs of
   2026-09-10. On the same seeds at HEAD: mean **+£169.60, 0.31 sems** from zero. No sign.
2. **Same priced decisions, different residuals.** Three of HEAD's four fingerprints each span
   residuals from about −£4,300 to +£1,550. The coextension the exact-count design rested on does
   not hold at HEAD, so fingerprint-counted "draws" are not an established unit.

**Consequence on the public page.** `site/capabilities` states a selection direction that the code
now running does not reproduce. That is not a defect in the served numbers, which are what those
runs returned. But the claim is no longer a property of the model that exists.

**Recommendation, not acted on (director's slowdown until the reset):** withdraw the published
selection sign to "not established at the current code" on Monday, and keep the served family
as the record of what 2026-09-10 returned. The second item needs its own question first: what
besides the priced decisions moves the selection residual. Answering it comes before any exact
count is published.

---

## The recommendation above is COUNTERMANDED, and it is kept beside the correction rather than edited

**Director, 2026-09-26T09:29Z, verbatim:** *"Don't withdraw the selection figure — I was wrong to
push that. Report what you found."* He named both numbers.

So the withdrawal recommended above is not the remedy and was never enacted. The remedy is that the
page carries **both** readings side by side, each labelled with the code it was measured on, with no
direction stated off either. The recommendation stays on the page above because a recommendation
filed and then reversed is the only evidence the reversal happened.

*Merged at archival 2026-09-29: this paragraph was written into the root copy (`401cd5784`) after the
archive copy forked from it, and is carried here so neither side is lost.*

**CORRECTED 2026-09-26 by the director: do NOT withdraw the figure.** Reporting that the
2026-09-10 runs returned −£960 and today's code returns +£170, indistinguishable from zero, *is* the
observability working. What is owed is the ROOT CAUSE. The director's hypothesis, to be tested
rather than assumed, is **book depth**. Identical decisions producing outcomes about £6,000 apart
means luck dominates, which is what you'd expect when few accounts have enough renewals for a
choice to compound. Measure how much of the residual variance renewal count explains, and whether
a deeper book would let selection be measured at all. Queued for after the reset as
`is-the-selection-residual-book-depth-luck`. No page figure changes.

## Actioned 2026-09-27 — what landed

1. **The HEAD fold is promoted off `/var/tmp`.** It was the only copy of the 18-seed HEAD family and
   a reboot would have ended it:
   `docs/observability/value_cycle_ab_s1_noise_floor_folded18_head_20260925.json`.
2. **`selection_across_code` on the served feed** — `tools/generate_value_arms_data.
   _selection_across_code`, above the `available` gate, reading both floor families and publishing
   each one's figure, standard error, distance from zero, own bar, commits and run dates. Neither
   family replaces the other: `NOISE_FLOOR_PATH` is unmoved, because the agreement fold REFUSED
   (`agreement_fold_rc=2`) and the rule here is that a family may only replace the served one when
   that fold succeeds.
3. **`#arms-selection-across-code` on `site/capabilities`**, rendered BEFORE the door's
   `if (!d.available) return` — unlike `#arms-blind-envelope`, which is assigned after it and so
   does not render on that branch despite its own comment. The publish whose run artefact cannot be
   read is exactly the publish on which an unreproduced direction would go unnoticed.
4. **Five door controls**, every one mutation-proven, in
   `site/test_the_baseline_comparison_reaches_the_reader.py`. Two mutations SURVIVED their first
   drafts and both survivals are recorded in that file's own R15 block — a whole-block amber grep
   satisfied by amber elsewhere, and a per-row figure check satisfied by the composed sentence that
   already names both figures.

**What the anti-tautology rung found, which is the part worth carrying forward.** The first draft of
`this_page_states` was the literal string *"NO DIRECTION for the choosing"* — printed on every
input. A block that refuses to pick a side whatever the evidence says has not made a finding, and it
would have gone on refusing on the day a re-run reproduced the served sign. It is composed from the
rows now (`_cross_code_statement`), and the identical defect was then found a second time in the
amber styling.

**Still owed, and item 2 of this finding is untouched by any of the above:** what besides the priced
decisions moves the selection residual. Until that is answered no exact draw count off either family
is established, and `regrade_over_distinct_draws` returns unavailable on the HEAD family for exactly
that reason. The page says so in `what_would_settle_this`.
