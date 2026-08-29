**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `W3_2_settlement_timetable`

# The repo holds two different answers for when a settlement day is final, and the one in code was never the one that was researched

Found while establishing a NON-CIRCULAR basis for the publish interval that
`SETTLEMENT_CUSTOMER_YEAR_BUDGET` needs (`docs/design/SETTLEMENT_CEILING_ALLOCATION_2026-08-29.md`
§7). I did not get to an answer, and this is why — **stated as a blocker rather than resolved in the
flattering direction**, which was available and tempting.

## The two answers

| | says | confidence stated | where |
|---|---|---|---|
| **Code, enforced** | Final Reconciliation at **28 months** | source given as *"Elexon Settlement Performance Reports; Ofgem supplier review data"* — a general attribution, not a citation for this number | `company/regulatory/settlement_reconciliation.py:31` (`_RF_MONTHS = 28`) |
| **Research commons** | RF *"roughly **12–14 months** later under the old Standard Settlement Timetable"* | **[M]**, and explicitly: *"I do not have high confidence in the exact day-offsets … these should be verified directly against Elexon's BSC Section T / published Settlement Calendar once the site is reachable, rather than hard-coded from this recall"* | `docs/market_research/settlement_rebilling_best_practice.md:32` |

The research note asked that its own numbers **not** be hard-coded before verification. Code had
already hard-coded a different one. Neither has been checked against Elexon's timetable — the note
records that live verification was blocked by a Cloudflare 403 on elexon.co.uk.

`docs/market_research/f4_international_expansion_probe.md:332` reads the 28-month figure back out of
the code as though it were the sourced fact (`_RF_MONTHS=28`, shares `0.60/0.25/0.12/0.03`) and
builds a GB-vs-SEMO structural comparison on it — *"GB's RF tail runs to 28 months; SEMO's final
[run at] 13 months"*, called out as a **"terminal lag is less than half"** difference. If 28 is
wrong, that comparison inverts to near-parity. **A constant read back out of code becomes evidence
for the next document**, which is how an unverified number acquires a provenance it never had.

## Why it is load-bearing right now

`simulation/run_phase2b.py::REPORT_END` is **2025-06-07**, which is ~14.8 months before today.

- **If RF is at 14 months**, the whole reported window has reached Final Reconciliation. Nothing in
  any published figure can move on new data, and the publish interval is a pure choice about how
  fast our own code changes become visible — the director's to name, with no external constraint.
- **If RF is at 28 months**, roughly the last **13 months** of the reported window are still
  reconciling, and there *is* an external reason data could revise under a published figure.

**Those are different worlds and I cannot pick between them from what this repo holds.** I nearly
published the first as the ceiling's new basis on the strength of the research note alone, which
would have been choosing the number that made my argument work.

## WHAT THIS CREATES

1. **One verified number, from Elexon's own timetable** — BSC Section T / the published Settlement
   Calendar. The note names the exact route and records the 403 that blocked it; an alternate
   channel is the task, not more recall.
2. **Whichever way it lands, the loser gets corrected in place.** If 28 is wrong it is enforced in
   company code and cited in an international-expansion comparison; if 12–14 is wrong the research
   commons is handing the next reader a figure it already told them not to trust.
3. **A question for the knowledge map, and it is the general one:** how many other constants were
   hard-coded from recall a research note explicitly asked not to be hard-coded? This one was found
   by needing it. `docs/institutional/knowledge_map.md` is where the answer belongs.
4. **Not blocking the ceiling work.** The allocation fix of 2026-08-29 stands on its own and did not
   need this; only the ceiling's *time* leg does, and that leg is already recorded as having no
   valid basis rather than a wrong one.
