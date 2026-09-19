# EP19 — the prices held, and the clock they are on is not the one we recorded

**2026-09-19 DISCOVER** (worker tick, LANE 3 DISCOVER/FRAME only; **no BUILD code for this atom** —
`file_scope` stays `[]`, `loop_stage` stays `idle`, epoch-5 BUILD gating untouched).
Pre-registration, written before any measurement: `docs/design/EP19_PREREGISTRATION_2026-09-19.md`.
**Level held at 1.** Costs closed for 1 of 5 gated paths, lead times for 0 of 5 — unchanged.

## Why this pass existed

The atom's three prior passes (2026-08-13, 2026-08-15, 2026-08-18) each ended by naming what was still
owed. Every one of those is a claim about the world made a month ago and never re-asked. This pass
re-asked all four and recorded the predictions first so the answers could refute them.

**All four predictions held.** That is the least interesting possible outcome and it is reported as
such — but two of the four held for reasons different enough from the ones I gave that the register
changed anyway.

| | prediction | result |
|---|---|---|
| P1 | allowlist unchanged; `elexon.co.uk` still the only gated-counterparty host inside | **CONFIRMED** |
| P2 | the queued second fail-open is still live | **CONFIRMED — and it has been filed as `done`** |
| P3 | no new advisor research; costs 1/5, lead times 0/5 | **CONFIRMED** |
| P4 | the one reachable row's prices may have moved | **CONFIRMED unchanged — but on a clock we never recorded** |

## P1 — the wall is where it was, and the reachable surface is larger than "one page"

`check_allowed()` at HEAD, all ten register hosts: `elexon.co.uk` **True**; smartenergycodecompany,
smartdcc, recportal, xoserve, bacs, gocardless, ofgem, n3rgy, recco all **False**. Fifteen suffixes on
the allowlist. Unchanged, as expected — CLAUDE.md makes it director-console-only, so no tick could
have moved it.

**What the 2026-08-18 pass's phrasing obscured.** It concluded *"exactly one gated counterparty is
True: elexon.co.uk"*, which is correct and reads as *one website*. The allowlist matches by **suffix**,
so `bscdocs.elexon.co.uk` and `bmrs.elexon.co.uk` are both inside it too — and `bscdocs` is the
**authoritative BSC document store**, not a marketing page. The reachable surface behind the one open
row is a code library. That is recorded here so the next pass does not re-derive it, and it is what
made P4's finding visible at all.

## P4 — the figures held, and the finding is the clock, not the number

All three URLs the register cites return 200, and **every one of the ten published figures is
unchanged** after thirty-two days: accession fee £500, base monthly £250 + VAT, CVA Metering £50,
SVA Metering System £0.00757/MSID/month, CVA BM Unit £0 (was £50), Base BM Unit £0 (was £100),
Additional BM Unit £60, Notified Volume £0.0005/MWh, PTS £999 + VAT per half-day, SVA Qualification
£0. Credit Cover still unspecified by Elexon — *"it is up to the Party to decide"*.

**The structural finding.** `/bsc/market-entry/becoming-supplier/` is a **narrative restatement**. The
authoritative home is the **Schedule of Main and SVA Specified Charges**, an instrument under BSC
Annex D-3.3/D-3.4 that the **BSC Panel re-determines before the start of each BSC Year**. Observed
live on `bscdocs.elexon.co.uk`: **V24.0, Effective From Date 12/05/2026, status LIVE**, with a V23.0
behind it.

The register recorded ten figures with a **freshness** date — when we looked — and no **basis** date —
when the figure took effect. Those are different quantities and only one of them was on the page. The
consequence is not pedantic: a re-verification that reads only the restatement returns *unchanged*
both when the Panel did not move the price **and** when the narrative page has not caught up with the
schedule. So this pass's own confirmation is weaker than it looks, and it is now recorded at that
strength rather than as a clean tick. The next determination will move V24.0 with no signal whatever
on the page this register reads.

Basis date **12/05/2026** is now written into the register beside the figures.

**Not closed, and not inferred.** The schedule's body is served by a JavaScript document viewer; its
figures are absent from the static HTML this seat can fetch. Nothing was read across from the
restatement into the schedule's column to make the two clocks look reconciled — that would be exactly
the laundering the 2026-08-18 pass refused when it broke the Owner column's derivation rather than let
it write a wrong owner.

**One new figure, recorded because of what it collides with.** `/bsc/about/bsc-costs-charges/` gives a
**minimum monthly BSCCo invoice of £500** — a recurring billing floor, numerically identical to the
one-off accession fee and a completely different quantity. Two unlabelled £500s in one row is how the
next reader adds or divides the wrong pair. They are now two rows that each say what they count.

## P2 — the queued fail-open is not merely unfixed, it is filed as done

`background/one_way_door.py` has had **zero commits since 2026-08-18**, and at HEAD
`classify_action` still returns **PROCEED** for *"add a host to the egress allowlist"*, *"change the
sandbox security profile"*, *"widen ALLOWED_HOST_SUFFIXES to include xoserve.com"*, and for the two
Elexon acts (*"appoint an existing ECVNA…"*, *"complete CVA Qualification testing with Elexon…"*) that
make this register's Owner column a mixed instrument.

`WORKER_FINDING_THE_DOOR_RELEASES_THE_ONE_CONTROL_CLAUDE_MD_CALLS_A_WALL_2026-08-18.md` nonetheless
now sits in `docs/staging/done/`, moved by commit `2766c8ca2` — a **772-path bulk archive sweep**
clearing a 419-file backlog. Its own stated null control is false. **The sweep could not distinguish
"waiting on its named owner" from "finished"; age was the only input**, and this finding was waiting
for precisely the reason it wrote down.

That matters to EP19 directly, because this register's Owner-column caveat says it *"comes out when
this lands, and not before"* and cites the finding's old staging path. A reader following the citation
into `done/` would remove a caveat that is still true. The register now states the **null control** as
the condition for removing it, never the file's location. Raised as its own finding (with a one-leg
remedy — a sweep that refuses to archive a file whose stated null control is measurably false) at
`docs/staging/WORKER_FINDING_A_BULK_ARCHIVE_SWEEP_FILED_A_FINDING_AS_DONE_WHILE_ITS_OWN_NULL_CONTROL_IS_STILL_FALSE_2026-09-19.md`.

## P3 — no new source

No advisor research on these counterparties has arrived since the single dated source of 2026-08-05.
The 2026-08-18 recommendation — that the route to pricing the other four gated paths is the **advisor
staging bridge**, not an allowlist change — stands, unexercised, and is not re-asked here.

## My own near-miss, recorded rather than tidied away

I drafted a refutation of P4 — *"the site was restructured and every URL the prior pass used is
dead"* — off the back of two 404s. Both 404s were URLs **I had guessed** (`/about/our-fees-and-charges/`,
`/bsc-and-codes/…/joining-the-bsc/`), not URLs the register cites. When I checked the three it
actually cites, all three returned 200 and every figure was intact. Had I published the draft, this
register would carry a confident, sourced, false claim that its own evidence base had rotted — and the
next pass would have spent itself re-fetching pages that were never broken.

The ordering was the error, and it is the same ordering error this atom made on 2026-08-18 (testing
connectivity before reading the allowlist): **check what the document actually cites before concluding
the citation is dead.** It is written down because this atom has already been caught once publishing
"the boundary is HELD" when it was merely cited, and a near-miss that goes unrecorded is a defect
waiting for a tick with less budget to look twice.

## Level — held at 1, and why that is not a formality

The gain reads *"named qualifications with owners"*, and L2 needs owners, costs and lead times. Owners
were closed on 2026-08-15. Costs stand at **1 of 5** gated paths and lead times at **0 of 5**, exactly
where 2026-08-18 left them, and both remaining columns sit behind hosts this machine may never reach.
This pass improved the *quality* of the one priced row — a basis clock, a re-verification, a
disambiguated £500 — and closed none of the gap. Moving to L2 on that would be greening a criterion by
redefining it, which is the move 2026-08-15 refused on a third of the blocker and 2026-08-18 refused
on a fifth of a half. No map row is edited: the level does not move, and the map ratchet has 6,461
bytes of headroom that a cosmetic write should not spend.

## Reserved boundary

Held, and measured rather than asserted — see P2 for the measurement that says the *classifier*
guarding it is still fail-open on two shapes. No row gained an apply/start/contact/submit action or a
target date. £500, £250 and £999 are recorded as published prices, never as budget lines. Nothing here
proposes an allowlist widening, and nothing proposes unblocking the atom — pull-forward stays
proposal-only per `DIRECTOR_RULING_FUTURE_COMMITMENT_SETS_2026-08-08` §3, and was not exercised.

## Open items, unchanged by this pass

Register open items 3 (MRA/DCUSA subsumption), 4 and 5 are untouched — every one sits behind an
off-allowlist host, B3/Project Trident still the likeliest to have moved and still unreachable. The
2026-08-18 residue stands: the fail-open's real population is wider than this register, and only the
shapes with a demonstrated defect have been repaired.

**New open item (2026-09-19):** the Schedule of Main and SVA Specified Charges is reachable but
JS-rendered, so the *authoritative* figures behind B11 have never been read — only their restatement.
Whether V24.0 agrees with the narrative page is **unknown**, not assumed.
