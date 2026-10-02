**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Claim:** `does-a-chosen-fixed-tariff-belong-under-the-cap` (Lane 0 delivery)

# Pre-registration: does writer 4 belong on a fixed tariff the customer chose?

Written 2026-10-02 at HEAD `db2184ec9`, before any run below has returned.

## The question

`company/pricing/renewal_rate_chain.CAPPED_TARIFF_TYPES` is `("fixed", "svt")`. The commons
(`docs/domain_artefact_library/regulatory/slc_28ad_multi_register_cap_test.md`, "What the text
settles" 4) says the cap binds default contracts only — Evergreen (SVT), Deemed and *default*
fixed-term contracts — and that a fixed tariff the customer chose is outside 28AD. In the world, a
renewal's `tariff_type` is set by the world's term builder; a passive term end goes to the SVT
(`SEAT_FINDING_THE_PASSIVE_TERM_END_NEEDS_NO_DEPARTURE_ROLL_..._2026-10-01.md`), so a `fixed`
renewal is an engaged choice. The fixed ceiling is also `min(cap, EPG)`, which drops the HMT
per-unit compensation suppliers received on fixed deals in the EPG window.

## The one variable

Same commit, same process code; `CAPPED_TARIFF_TYPES` is patched in-process to `("svt",)` in the
change arm and left alone in the base arm (`/var/tmp/se-fixed-cap/measure.py`). Each pair runs
twice: the live policy (`flat_rules`) and `VALUE_ARM_POLICY` (`value_based`), so the value arm's
`ceiling_bound` can be graded.

Removing `fixed` makes `net_of_epg` moot for fixed on writer 4, so the alternative variable
(`net_of_epg=False` for fixed) is not run separately unless P1 shows clamps that only the EPG
ceiling produces and the decision turns on them.

## Predictions

- **P1 (base, flat).** Writer 4 clamps at least 20 domestic fixed renewals (`price_cap`
  component), and at least half of them start between 2022-10-01 and 2023-06-30, because the
  `min(cap, EPG)` ceiling sits about a third below the cap there.
- **P2 (change, flat).** Domestic fixed renewals contracted above the flat cap ex-VAT go from 0
  to within ±25% of P1's clamp count. No fixed renewal moves down.
- **P3 (churn, flat).** Churned billing accounts in the change arm ≥ base. The rise is at most 5
  accounts, because the world's churn keys on the rate against the published SVT and the clamped
  renewals are a small part of the book.
- **P4 (SVT untouched, flat).** At most 5% of SVT chain calls change their contracted rate. Any
  that do move only through the portfolio premium reading a different margin history.
- **P5 (value arm).** In base, at least one fixed decision is `ceiling_bound`. In the change, 0
  fixed decisions are `ceiling_bound` (true by construction, since the arm is handed no ceiling).
  The graded part: at least half of base's ceiling-bound fixed decisions become
  `extrapolation_bound` in the change, i.e. the churn model's evidence frontier, not the law,
  becomes the binding constraint.
- **P6 (money).** `total_net` rises in the change arm on both policies. I make no prediction on
  size.

## What decides it

The decision is made on the law, not on the run. The commons says a chosen fixed is outside the
cap, so `fixed` comes out of the tuple unless the run shows something that makes the world unable
to press back (for example, uncapped fixed rates with churn that does not respond to them, P3).
If P3 shows no churn response at all to a material rise, that is a world-fidelity finding filed
alongside, not a reason to keep a cap the law does not impose.
