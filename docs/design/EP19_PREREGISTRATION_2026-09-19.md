# EP19 — pre-registration, 2026-09-19, written BEFORE any measurement

Drawn: LANE 3 DISCOVER/FRAME only, EP19_counterparty_qualification_paths, level 1->2.
No BUILD code for this atom; file_scope stays [], loop_stage stays idle.

The atom's own record (three passes: 2026-08-13, 2026-08-15, 2026-08-18) names the L2 blocker as
**costs and lead times for the five gated paths**, and names the constraint as the **egress
allowlist**, not "no network" — 9 of 10 register hosts off-allowlist, exactly one (elexon.co.uk)
inside. Its recommended next step is the ADVISOR STAGING BRIDGE, never an allowlist change.

Every one of those is a claim about the tree made a month ago. This pass re-asks them. What I
expect, written down first so the answer can refute me:

**P1.** The allowlist is unchanged where it matters: `elexon.co.uk` is still the only gated-
counterparty host that `check_allowed()` returns True for; smartenergycodecompany.co.uk,
smartdcc.co.uk, recportal.co.uk, xoserve.com, bacs.co.uk, gocardless.com and ofgem.gov.uk are all
still False. *Confidence: high — CLAUDE.md makes this director-console-only, so no tick could have
moved it.*

**P2.** The second fail-open the 2026-08-18 pass QUEUED and did not fix is still live:
`one_way_door.classify_action` still returns PROCEED for "add a host to the egress allowlist" and
"change the sandbox security profile". *Confidence: medium-high — it was queued with a named owner
precisely because it is not a free widening, and those sit longest.*

**P3.** No new advisor research covering these counterparties has arrived since the single dated
source (`docs/design/refs/ADVISOR_RESEARCH_COUNTERPARTY_APIS_EPOCH3_2026-08-05.md`), so costs are
still closed for 1 of 5 gated paths and lead times for 0 of 5, and the level cannot move.
*Confidence: medium — the bridge is the director's to use and a month is long enough that it may
have been used.*

**P4.** The 2026-08-18 pass's own cost figures (BSC accession GBP 500, base monthly GBP 250 + VAT,
SVA Metering GBP 0.00757/MSID/month, etc.) are still what elexon.co.uk publishes — i.e. re-fetching
the one reachable host changes nothing. *Confidence: low-to-medium. This is the one host inside the
wall and therefore the only row that CAN rot under us without anyone noticing; a year-boundary price
schedule is exactly the thing that moves. If any prediction here is wrong I expect it to be this
one.*

What would make this pass worth its tokens even if all four hold: the register would then carry, for
the first time, a re-measured freshness date on every row rather than inheriting 2026-08-05, and the
L2 gap would be stated as a *bound* — how much of it is reachable at all from inside the wall —
rather than as a to-do that no tick can ever take.

Reserved boundary, unchanged and not merely cited: acting on any row means contacting a real
organisation and spending real money (one_way_door classes 1 and 2). No row gains an
apply/start/contact/submit action or a target date. Nothing here proposes an allowlist widening.
