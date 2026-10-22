**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `why-the-four-non-offer-switches-decide-without-acting` (Lane 0 delivery)
**Knowledge:** none -- a wiring fact about which world path reads a company decision; no domain claim

# The collections tone reaches no payment since the world went to one payment truth (2026-10-22)

## What was found

The company decides a dunning-letter tone per bill (`decision_policy.tone_for`; CURRENT_POLICY
`tone_mode="ab_test"`). The world reads it through
`company/interfaces/collections_communication.collections_tone_for`, from one place:
`simulation/arrears_engine._resolve_bills` → `payment_outcome(..., tone, ...)`, where
`nudge_physics.tone_effectiveness_multiplier` lifts on-time payment for a household whose hidden
susceptibility matches.

Since `ded298ecd2` (12 Oct, `simulation/world_payment_truth.UNIFIED = True`), `_resolve_bills` takes
the triad's outcome (`told = wpt.truth_outcome(...)`) for every bill the triad decided, and calls
`payment_outcome` only for the rest (`wpt.LAST_COUNTS["fallback_bills"]`). The triad's own draws do
not read the tone (no module outside `arrears_engine` and `conversation_response` imports
`tone_effectiveness_multiplier` or `collections_tone_for`).

**Evidence.** Prereg §16's `all_on_save_odds_lower_bound` (tone split) and `flat` (firm only), both
at `4eb192b604`, are byte-identical on `total_bad_debt_gbp`, `provisioned_bad_debt_gbp`,
`payment_health_series` and `dd_balance_book`. Recorded in
`docs/staging/records/SEAT_PREREG_THE_PER_CUSTOMER_SWITCHES_ON_TOGETHER_AGAINST_FLAT_2026-10-21.md`
§17.

## Why it matters

The flat arm is described as removing "the per-segment framing and the per-segment tone". On the
shipped world the tone half of that difference is inert, so no arm can credit or charge the tone
A/B. `company/analytics/nudge_discovery.py` would be learning a lift from a lever the world no
longer answers. The 12 Oct correction was right about bad debt. It dropped this channel as a side
effect, and nothing said so.

## Which way to fix, unchosen

The triad's monthly payment draw could take the tone, so the lever survives the single payment
truth. Or the record could say that tone is not a lever in this world until it does. The first is a
world change, decided blind to company results (the baseline/curriculum split). Its
anchor is the nudge-physics tone range (+3–10pp), already sourced. **I cannot yet say** how many
resi bills are fallback bills. One instrumented run reading `wpt.LAST_COUNTS` answers that, and it
should be the first step.
