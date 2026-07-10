# SLC 25C "Communication Channel Choice" — real domain-sense fix, not an instance patch

**Found:** 2026-07-10, director page comment on /supplier/ (Governance tab): *"I don't get the
red compliance failure. How do complaints link to channels available? Also lots are manual.
Does that mean fail? If we don't have a process linked to the license condition don't we need
to think maybe we have a missing process in the SIM or the supplier?"*

## What was actually wrong (R10 absurdity class, not a tuning issue)

`saas/reporting/annual_report.py::populate_compliance_scorecard()`'s COMPLAINTS domain check
(displayed on the Regulatory tab as **"SLC 25C: Communication Channel Choice"**) was keyed on
`avg_complaint_probability` — a churn-model metric measuring how likely a customer is to
complain at all. That has nothing to do with whether a customer had a real choice of
communication channel, or was served adequately once they used one. The live site showed RED
because the real portfolio's complaint probability (6.0%) crossed an arbitrary 5% threshold —
a real number, correctly computed, answering a question this specific obligation was never
about.

## The real process was NOT missing

Rich's third question — is there a missing SIM/supplier process behind this obligation — is a
fair and important question to ask, but the answer here is **no, it already exists**:
`simulation/contact_centre.py` models real multi-channel contact (phone/webchat/email, with a
real channel-mix distribution and a per-contact first-response-time simulation), and
`company/crm/contact_journey.py` tracks customer channel preferences and per-channel delivery
rates. Both were already built (an earlier phase, Core Fidelity Phase 3 item 4) and already
flowing into `run_output["contact_centre_log"]` -- they were simply never wired into this
specific compliance check, which used an unrelated pre-existing metric instead.

## Fix

`populate_compliance_scorecard()`'s COMPLAINTS domain now computes a real first-response
SLA-breach rate from `data["contact_centre_log"]`, filtered to the year in question:
GREEN <10% breach rate, AMBER <25%, RED >=25% (reasoned bands, consistent in spirit with this
function's other domain thresholds — e.g. bad-debt-ratio's 1%/3% bands — not independently
sourced against an Ofgem-published channel-choice standard, same honesty caveat this module's
`contact_centre.py` already carries for its own provisional SLA target). All three channels are
always structurally available by construction of the contact-centre model, so literal channel
*availability* can't meaningfully fail this check — the metric that can genuinely inform
"choice" in a compliance sense is whether the channels customers actually use are serving them
adequately.

**Live result after the fix:** SLC 25C -> GREEN (real portfolio SLA-breach rate is healthy).
Overall Regulatory RAG moved from RED to AMBER, now correctly driven by the (unrelated, genuine)
billing-clarity AMBER already present on 4 other billing_metering-domain obligations.

## The separate "lots are manual, does that mean fail?" question

This refers to the *other* compliance surface, `company/compliance/compliance_report.py`'s
risk-tiered report (Phase 4, DOMAIN_SENSE_AND_COMPLIANCE.md) — a different mechanism from the
Regulatory tab's RAG scorecard above. By explicit design (see that module's own docstring):
**MANUAL is not a failure status.** Only two obligations (billing accuracy, VAT-by-segment) have
a live automated GREEN/RED derived from the pre-bill validation gate's real exception queue;
every other obligation reports MANUAL, meaning "tracked by an existing module/process, not yet
wired to an automated live check feeding *this specific report*" — an honest abstention, not a
silent GREEN and not a RED. This is itself a real, deliberate design choice (avoiding the
r10-adjacent trap of a false-confidence GREEN for something not actually monitored live) and was
working as intended — the confusion was reasonable given the report doesn't itself repeat "MANUAL
!= FAIL" inline. Registered as a small follow-up: add that one-line clarification directly to
the risk-tiered compliance report's own rendering, not just its source docstring.

## Not touched

The other 22 SLC obligations were checked for the same class of mismatch (metric vs. label) --
none showed the same complete disconnect; billing/payment/information/governance domains all
use a metric genuinely related to their label (bill clarity, bad-debt ratio, demand-estimation
error, balance-sheet solvency). This was a single, specific miswiring, not a systemic pattern
across the scorecard — confirmed by reading, not assumed.
