**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `an-svt-household-can-decline-the-fix-and-stay-on-default` (Lane 0 delivery)

# An SVT household can decline the fix: the premise holds, the rule is designed and pre-registered, and the code waits for the retake

Pre-registration: `docs/staging/records/WORKER_PREREG_A_HOUSEHOLD_THAT_STAYS_NEVER_CONTRACTS_A_FIX_ABOVE_ITS_DEFAULT_2026-10-02.md`.

## Where this stands

- **The premise holds at `0a410a961`.** No code reads the offered rate at an SVT conversion. A
  dual-fuel gas leg has no decision of its own at any boundary.
- **Baseline, from the 2f6a9ea05 harness.** 16 of 40 value-arm conversions sit above the
  household's default with renewals capped, and 36 of 38 with them uncapped. Every 2017–18
  conversion sits above it, by up to +59%. That excess is `portfolio_premium` plus `value_arm`
  over a base strike near the SVT. It is not the world's reference.
- **The rule needs no invented size.** A stayer never contracts a fix above its default. The
  destination is SLC 22/23. **The decline-versus-leave share is a declared gap (`None`):** no
  published series conditions on a rejected incumbent offer. The rule leaves every existing leave
  route as it is.

## Why no code landed this turn

1. **The world-D retake is running** (`longjob-arms-floor-d-head-1002b`, floor started 05:56 UTC,
   about 08:35 UTC to exit). Landing `simulation/` now would withdraw it on the page. This is the
   same reason item one's diff is held.
2. **Item one lands first and touches the same block.** `restore-the-journey-decision-for-an-svt-conversion`
   adds `_journey.record_decision` to the conversion branch. Its diff is embedded in
   `WORKER_PREREG_AN_SVT_CONVERSION_RECORDS_A_STAYED_DECISION_ON_ITS_JOURNEY_2026-10-02.md`.
3. **The decline needs a splice, not a flag.** The faced rate comes from `decide_renewal_rate` in
   the run loop, and `all_terms` is static. A declined term has to be replaced by
   `build_svt_schedule` segments in a 4,000-line loop, without moving the PB6 seed alignment. The
   pre-registration names the three hazards and the R13 byte-identity control.

## Owed, in order

1. After the retake exits and item one lands: build the splice and the decline event, plus the one
   partition control (accept / `declined_fix` / churned), mutation-proven.
2. Run the default world and the value arm serially at one commit. Grade P1–P6.
3. Write the `decline_versus_leave_share` gap into `docs/institutional/knowledge_map.md`'s
   retention row when the code lands, so the gap and the rule land together.
