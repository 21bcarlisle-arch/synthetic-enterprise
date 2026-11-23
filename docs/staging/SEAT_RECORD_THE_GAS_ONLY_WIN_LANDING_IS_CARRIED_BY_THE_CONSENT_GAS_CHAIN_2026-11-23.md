**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Item:** `verify-gas-only-win-landing-from-the-6c-resume-chain` (released) → `close-gas-only-win-after-the-consent-gas-chain` (carries it)

# The gas-only win's landing is carried by the Consent-then-gas chain; the 6C resume chain's refusal was the live Consent red

Seat executor, 23 Nov 2026. Read, not built.

1. **The 6C resume chain ended refused.** `/var/tmp/se-reg6c-gas-chain-resumed-ended-20261123.txt`:
   `exit 1 2026-11-23T06:29:06Z`. `/tmp/seat_6c_v4/resume.log`: `GAS LAND EXIT 1`, the test gate
   red on two controls in `tests/company/billing/test_collections_journey.py`
   (`test_a_live_run_withholds_the_prepayment_offer_at_the_ninety_day_rung`,
   `test_the_world_counts_every_consent_offer_the_company_made`: "no live Consent offer"),
   2 failed / 2690 passed. Those are origin's own red since 7527a2e36 (finding 773e2d9ba0,
   root cause 813c99ccae), not the gas change's. `/var/tmp/se-gas-only-win-landed-20261123.txt`
   does not exist; the gas commit is not on origin/main.
2. **The remainder is the successor's.** `close-gas-only-win-after-the-consent-gas-chain` names
   every remaining step: land the re-keyed Consent controls, then the gas-only win from
   `/tmp/seat_exec_e/chain/files`, close direction row
   `supply-a-win-from-a-gas-only-household-as-gas`, remove `/var/tmp/se-reg6c-land` and
   `/var/tmp/se-consent-gas-land`. This item is released, not re-run.
3. **That chain is IN FLIGHT.** `launch_long_job --job consent-controls-then-gas-only-win`
   (pid 3117890, `/tmp/seat_exec_e/chain/chain.sh`) was running at draw time. Re-landing from
   `/tmp/seat_gas/files` as this item's refusal branch asked would have been a second landing
   over the same paths. Its end marker `/var/tmp/se-consent-gas-chain-ended-20261123.txt` did
   NOT exist at draw time, so the successor's hold is genuinely closed (unlike the stale marker
   recorded in the 6C chain-record of 05:46).
4. **Caveat for the successor.** The chain promotes with `--work-id
   verify-gas-only-win-landing-from-the-6c-resume-chain`, this released id. If the binding line in
   `/tmp/seat_exec_e/chain/chain.log` refuses on a released claim, bind the landed paths under the
   successor with `delivery_lane --landed-under`; the commits on origin are the evidence either way.
5. **Two duplicate holds retired (dropped, reversible).** After release, `--release` left
   `verify-gas-only-win-landing-from-the-6c-resume-chain` offered (its retiring artefact is the gas
   landing marker), with its DO NOT DRAW file already present, so it was dropped. So was
   `fix-the-live-consent-red-from-7527a2e36-then-land-the-gas-only-win`: its hold
   (`/var/tmp/se-consent-red-probe-20261123/compare.txt`, 08:13Z) was open, and its remainder
   (re-key the two controls, land the gas-only win) is exactly what the in-flight chain does, so a
   draw would have run a second landing over the same paths. Its full entry is saved at
   `/tmp/seat_rec_gas/dropped_fix_consent_red.json`; to reverse, re-hand it off from that file.
   Class: a successor written from a predecessor's reading must `--supersedes` it, or the
   predecessor's open hold offers the same landing twice.
