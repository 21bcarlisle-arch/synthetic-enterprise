**Lane:** W2_customer_generator · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`

# Pre-registration: what the empty-period flag finds once an incoming account opens on the outgoing account's closing read (2026-10-17, written before the linked flag was run)

Direction item `the-company-holds-an-opening-read-at-a-change-of-tenancy`. Knowledge:
`docs/market_research/unbilled_energy_and_revenue_assurance.md` §4a, "The opening read at a change
of tenancy" (written first, K8).

**Premise re-measured at draw.** 9919e0346 is on origin/main. The flag's code still does not judge
a span that has no actual read before it (`seen_actual` starts False), and the run book's
incoming-account void stubs are still each account's first period. The premise is not spent.

**What changes.** `empty_period_flags` takes the status of the account's opening read. At a change
of tenancy with the same supplier, that read is the outgoing account's closing read on the same
meter (the boundary read is shared). If it is actual, the incoming account's first span is judged.
If it is estimated or absent, the first span is not judged, as before. `boundary_read_status`
reads the closing read off the outgoing account's own periods. The probe links each incoming
electricity account to its outgoing one: by `home_move_ins` where the run publishes it, otherwise
by move date and registry EAC. A pair that matches ambiguously is left unlinked and counted.

**Instrument facts read before predicting** (linkage only; no flag was run on them): 135 incoming
electricity accounts in the published run book (`run_output_latest.json`, 78f77c34e). 131 link
uniquely by move date and registry EAC, and 4 are ambiguous. The run predates the publication of
`home_move_ins`.

**Predictions** (run book, `--structural --occupied-run`):
- **O1.** Some void stubs become judged: **between 15 and 35** of the 54 first-period stubs. A stub
  is judged only when both the outgoing closing read and the stub's own read are actual. In the
  book, about a fifth of reads are smart (6,839 of 38,854), and smart reads are nearly all actual.
  Traditional reads are mostly estimated.
- **O2.** Every newly judged stub files as **`void`**, and **0** as `investigate`. The stub's bill
  carries the owner's void share of 1.
- **O3.** Occupied homes stay at **0** `investigate`.

*Refutation.* O2 fails if any stub files `investigate`: then the named-occupier leg mistakes a void
for a lead on a real book. O1 below 15 would mean the closing read is rarely actual, and the
opening read is then a smart-meter question rather than a CoT one. O1 at 0 would mean the linkage
or the boundary-date match is broken, not the world.

## Graded (same day)

`python3 -m tools.theft_void_screen_probe --structural --occupied-run docs/reports/run_output_latest.json`:
there are 131 incoming electricity accounts linked and 4 left unlinked. 125 open on an actual
closing read, and 6 have no read on the boundary. The book holds 16 zero-advance spans, every one
`void/void`, and no `investigate` of any cause.

- **O1 held, at its floor: 16 judged.** The prediction reasoned from the wrong bottleneck. The
  closing read was not the limit: 125 of 131 are actual. The limit was the stub's own read, which
  must also be actual to close a zero span. Most stubs end on an estimated traditional read, and
  their span runs into the occupier's use.
- **O2 held.** All 16 file as `void`. On a real book the named-occupier leg separates the owner's
  void from a lead.
- **O3 held.** Occupied homes: 0 `investigate`.

**What the 125 of 131 is.** The world makes every forced closing read actual (`final_read_for`).
91 of the boundary reads are forced, and 6 of the 16 judged stubs rest on one. Published practice
makes a final read actual only sometimes. Filed as
`../SEAT_FINDING_THE_WORLDS_CLOSING_READ_IS_ALWAYS_ACTUAL_2026-10-17.md`. The other 10 judged stubs
open on an ordinary actual read, so the result does not depend on the forced read.
