# DD attribution confound (W2_10) — anchoring & provenance

World-side hidden truth for the first "selection-bias trap the company must
discover it is falling into". Provenance for the anchors and honest
simplifications encoded in `simulation/dd_attribution.py`. Dated 2026-07-13.

## What the module models
Customers who are on direct debit (DD) differ *systematically* from those who are
not: they are more financially **organised** and (partly for that same reason,
not because of DD) carry a lower **true** arrears risk. A naive channel-attribution
analytics that credits the DD cohort's better outcomes **to the DD channel**
over-credits DD — most of the observed gap is **selection**, not treatment.

The module holds two quantities apart:
- `delta_true` — the genuine causal DD effect (do-operator), the honest ceiling on
  what a DD-discount business case could legitimately claim.
- `delta_naive` ingredients — the per-customer observables (channel + arrears) a
  real supplier holds; the C12 twin aggregates these into `delta_naive`, and the
  harness scores the gap `|delta_naive − delta_true| / |delta_naive|` = the
  fraction of the DD business case that is confound artefact.

## Anchors [L] (real, sourced — never fabricated)
- **Payment-method mix**: ~74% direct debit / 13% standard credit / 13% prepayment
  (Ofgem, 2026). Recorded in the W2_10 DISCOVER pass (`docs/design/maturity_map.yaml`).
  → `_TARGET_DD_SHARE = 0.74`. Modelled as a **binary** DD-vs-non-DD world; non-DD
  folds standard credit + prepayment together (26%).
- **Direction of the risk difference**: Ofgem sets a **higher** price cap for the
  standard-credit cohort because it "reflects the additional costs and risks in
  servicing" that payment method — i.e. the regulator's own methodology already
  treats payment-method cohorts as structurally different-risk populations. This
  fixes the *direction* only (non-DD ⇒ higher arrears risk).
- **The surface correlation the trap warns against**: Ofgem has publicly noted "a
  generalised shift ... to direct debit has reduced the numbers of customers who
  fell into arrears" — exactly the correlation a naive reading mistakes for pure
  causation.
- **Arrears-scale plausibility**: ~5.3 million people (~19% of GB households) live
  in a household in debt to their energy supplier (Citizens Advice). Used as a
  R12 sanity band for the realised population arrears rate, never a target.

## Honest simplifications (R10 / R13)
- **The selection-vs-treatment split is deliberately un-anchorable (R13).** There
  is *no* published decomposition of the DD arrears gap into selection vs
  treatment — that missing decomposition **is** the trap, and real suppliers
  cannot see it either. So `_SELECTION_STRENGTH`, `_ORG_ARREARS_PROTECTION_K` and
  `_DD_TREATMENT_MULT` are director-curriculum diagnostics: overridable, never
  claimed as measured, never tuned toward a P&L, an arrears rate, or a gap number.
- **Prepayment folded into non-DD (R10).** Prepayment has its own distinct physics
  (pay-as-you-go, self-disconnection — W2_8's scope) and is not separated here;
  this atom's confound is DD-vs-everything-else.
- **Static selection (R10).** Channel is a static per-customer selection (organised
  customers select *into* DD). The dynamic variant the FRAME pass named — failing
  payers pushed *off* DD over time, landing bad debt in the credit cohort — is the
  same confound by a time-varying mechanism (would make `payment_channel`
  event-responsive) and is an acknowledged extension, not silently assumed away.

## Coupling to W2_4 (why the confound is consistent)
The hidden `organisation` latent blends an idiosyncratic conscientiousness draw
(60%, own substream — a low-income customer *can* be highly organised) with the
affordability signal (income decile) read from `simulation.household_budget`
(W2_4, 40%). Organisation lowers arrears **and** raises DD adoption, so it is a
genuine common cause (back-door path) of channel and outcome — the textbook shape
of a confound, and consistent with the same customer's affordability in the budget
twin.

## Honest level: held at L2
Target L3 is **gated** on the C12 twin existing and a non-degenerate gap being
measured (COUPLED_TRIAD binding rule: no world atom reaches L3 until the company
has been tested against it). This build is the complete world side — hidden truth,
`delta_true`, the naive-analytics ingredients, deterministic substreams — but C12
does not yet exist, so it holds at **L2** with a precise note in the map. The
coupling harness (`tools/couple_w2_10_c12.py`, mirroring `couple_w2_6_c8.py`) and
the gap panel are the L3 increment.
