# [DIRECTOR-DECISION] Three verified 2025/26 rates are ready and NOT landed; test-file split is APPROVED (2026-08-14)

**PARKED (2026-08-18, worker triage):** blocking sub-item is §2 — the director's explicit go on the
three verified rates — and §3 (Low Carbon reconciliation, source found, not transcribed). §1 (test-file
split) is approved and left to its owning lane. A reminder/recommendation NTFY was sent 2026-08-18
(id `ji855H4LbP4z`) restating §2 with a recommendation and flagging the two items found on the way
(CCL 2023/24 possible mis-transcription; Low Carbon reconciliation). Re-park here, not the root, so this
doesn't re-ring the doorbell every cycle while genuinely waiting on the director's own stated condition
("a published figure may not move without him being told first") — not silence-is-validation territory,
his word overrides the default. Unblocks on his explicit reply.

**Severity:** LATENT · **Lane:** W4_the_wall

Two separate things, filed together because they came from one director message.

**Why this header exists and why LATENT is the honest word.** This document reached the staging
root with no machine-readable severity, and `background/finding_severity.py` classifies an
unheadered document UNCLASSIFIED — which, by `background/gate_authorization.py`'s deliberate
design ("an unclassified document refuses EVERY lane"), held level-recording repo-wide rather
than in one lane. The header is the cheap release that design names. **LATENT, not BLOCKING**:
the accuracy defect below is real and queued, but the published surface already DISCLOSES the
clamp — `simulation/policy_costs.coverage_report` and the report's EXTRAPOLATED RATES note state
that 13 of 13 rate tables are read outside their window, from which date, at both edges. A reader
is not being told a rate is sourced when it is extrapolated, so no live instrument is lying; what
is owed is accuracy, not honesty. **Lane W4_the_wall** follows this subject's sibling findings
(`WORKER_FINDING_THE_COST_STACK_CLAMPS_SILENTLY_INSIDE_ITS_OWN_RUN_WINDOW_2026-08-14`,
`WORKER_FINDING_THE_NON_COMMODITY_STACK_IS_EXACTLY_SHAPE_INVARIANT_2026-08-14`, both LATENT ·
W4_the_wall), not a fresh judgement. §2's three rates remain PENDING THE DIRECTOR exactly as
written below — classifying this document does not land them, and must not be read as doing so.

---

## 1. APPROVED — split the H27 proof-door test module

The director's word, verbatim: **"Yes to splitting the test file."**

This answers the recommendation in the 2026-08-13 19:14Z page and
`WORKER_FINDING_THE_LANDING_GATE_CANNOT_WIN_THE_RACE_AGAINST_HEAD_2026-08-13.md`: the landing
gate is ~9m24s, ~99% of it one 457-test module (557s), HEAD moves every 3.5–10 min, and 3 of 5
landing attempts were refused for HEAD movement rather than for a red test.

**Left to the owning lane deliberately, not taken here.** That lane said it would take the split
next tick; racing it on a shared tree would risk two writers on the same module, which is the
class this repo has already paid for. This document is the approval it was waiting on.

Independent confirmation, same day: landing the cost-stack coverage work below hit the identical
wall — the gate outran a 10-minute shell cap and had to be re-run detached. The finding is not
theoretical and it is now costing every lane, not just H27.

---

## 2. PENDING THE DIRECTOR — three verified rates that would move a published figure

### Why this is not simply landed

The director's condition, restated 2026-08-14: **a published figure may not move without him
being told first.** These three rates move it. So they are fetched, verified, cited, and
deliberately **not committed** until he says go.

This is the lesson from the same morning: the 21.9h publish freeze ended with £1,526,252 →
£1,547,113 landing in one step, and nobody flagged the number before it published.

### The three, with primary sources

| table | key | current (clamped) | verified 2025/26 | source | vintage |
|---|---|---|---|---|---|
| `_RO_COST_BY_OY_START` | 2025 | 31.8 | **33.06** (0.493 × £67.06) | Ofgem *RO buy-out price and mutualisation threshold and ceilings 2025 to 2026*; DESNZ *Calculating the level of the Renewables Obligation for 2025 to 2026* | buy-out published 18 Feb 2025; obligation level published 30 Sep 2024 |
| `_CCL_ELECTRICITY_RATE_BY_YEAR` | 2025 | 7.35 | **7.75** (0.775 p/kWh) | HMRC, *Climate Change Levy rates* (gov.uk guidance) | rate effective 1 Apr 2025 |
| `_GAS_CCL_RATE_BY_YEAR` | 2025 | 7.75 | **7.75** (0.775 p/kWh) | HMRC, *Climate Change Levy rates* | rate effective 1 Apr 2025 |

Deltas at the rate level: RO **+£1.26/MWh (+4.0%)**, electricity CCL **+£0.40/MWh (+5.4%)**, gas
CCL unchanged. The P&L delta has not been measured — measuring it means running the sim with the
new rates, and that run's output is what the publisher picks up, so the measurement itself would
publish the move. **That is the decision being asked for.**

### A separate and larger thing found on the way, which is NOT a 2025 question

HMRC publishes the CCL electricity main rate as **0.775 p/kWh for 1 April 2023, 2024 and 2025**.
The table carries **7.26 for 2023 and 7.35 for 2024**. If the HMRC figure is right, the published
history is wrong for at least two years, not merely missing for 2025 — and correcting it revalues
years that have already been published many times.

**Not touched.** It is a bigger revaluation than the one asked for, it is a fidelity correction
under R13 (decided blind to P&L, and it moves cost UP, i.e. margin DOWN), and it deserves its own
measurement and its own heads-up rather than riding along with a 2025 extension. Filed here so it
is on the record rather than in one session's memory.

### What is already true without any of this

`simulation/policy_costs.coverage_report` and the report's EXTRAPOLATED RATES note landed
separately and revalue nothing: the page now states that 13 of 13 rate tables are being read
outside their window, from which date, and at both edges. **The clamp is disclosed whether or not
these three rates ever land.** That was the honesty gap; this is the accuracy one.

### The ten that remain extrapolated

`_NETWORK_COST_RESI_SME_BY_YEAR`, `_DUOS_IC_BY_YEAR`, `_CM_LEVY_BY_YEAR`, `_FIT_LEVY_BY_YEAR`,
`_GAS_NETWORK_COST_BY_YEAR`, `_GGL_RATE_GBP_PER_METER_YEAR`, `_CFD_LEVY_BY_YEAR`,
`_MUTUALIZATION_LEVY_BY_YEAR`, `_ELEC_SC_PENCE_PER_DAY_BY_YEAR`, `_GAS_SC_PENCE_PER_DAY_BY_YEAR`.

Not fetched. Each needs a different publisher (LCCC, NESO, Ofgem cap, DESNZ) and several are
modelled aggregates rather than a single published number, so transcribing one badly is worse
than leaving it declared-extrapolated. **One source was actively rejected on the way**: a
WebFetch of Ofgem's RO administration-costs PDF returned "0.088 ROCs/MWh, £44.97 buy-out" against
the £67.06 confirmed on Ofgem's own publication page. Two readings of the same scheme year
disagreeing is exactly the shape that puts a fabricated number into a published table, so the
obligation level was taken from the DESNZ statutory publication instead and the PDF discarded.

---

## 3. NOT DONE — the Low Carbon reconciliation. Source identified, series not transcribed.

The director asked for the same treatment on the Low Carbon disagreement
(`WORKER_FINDING_TWO_PUBLISHED_FUEL_MIX_TABLES_DISAGREE_ON_LOW_CARBON_2026-08-14`, discharged
2026-08-14 by clause 2 — the limitation stated in the report — for want of a network). Clause 1
is what he is asking for: reconcile to one sourced mix.

**What was established.** The authoritative source is named and reachable: DESNZ publishes a
**"Fuel mix disclosure data table"** on gov.uk, updated annually — which is the document the
report's own "UK Grid Fuel Mix Disclosure" section purports to render, so clause 1 has a real
owner rather than a judgement call between two in-tree tables. The wider series lives in DUKES
Chapter 5 / Energy Trends section 5.

**One anchor, transcribed and checked, for 2024:** DESNZ reports renewables **50.4%**, nuclear
**14.2%**, coal **0.7%**, and low carbon (nuclear + renewables) **64.7%**. Against the two
in-tree tables for 2024: the Carbon Emissions Reporting Observatory publishes **64%** and the UK
Grid Fuel Mix Disclosure publishes **65.5%**. So the eight-bucket table is nearer on the one year
that could be checked — which is the *opposite* of what the finding's own reasoning suggested
(it noted the five-bucket table's decimal places were "consistent with, but does not establish"
it being the transcribed series). One year is not a reconciliation and does not settle which
table owns the series.

**Why it is not finished here.** The remaining nine years need transcribing from the published
tables with a stated vintage, and doing that badly is worse than the disagreement — the finding
refused to name a true value for exactly this reason. It also revalues two published tables and
the grid-intensity column derived from one of them, so it needs the same heads-up as §2 whichever
way it lands. **This is the item the director asked for that I did not complete**; it is recorded
here rather than left in a session's memory, with the source named so the next pass starts from a
publisher instead of from a choice between two unattributed tables.

### Egress, stated rather than assumed

`background/egress_allowlist.py` does not list gov.uk or ofgem.gov.uk, and CLAUDE.md makes the
allowlist director-console-only — **it was not touched**. The distinction relied on: this is an
agent reading a public document and transcribing a verified figure into a static committed table.
The simulation's runtime egress is unchanged and no new host is reachable from any daemon. If the
director reads that distinction differently, the three rates above should be dropped, not the
allowlist widened.
