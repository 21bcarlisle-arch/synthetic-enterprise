# EP5_settlement_true_ups — DISCOVER pass 2 (2026-08-18)

**Atom:** `EP5_settlement_true_ups` (lane `E_finance_treasury`, epoch 2, L0→L3, `loop_stage: idle`).
**Draw:** LANE 3, DISCOVER/FRAME only, no BUILD code — epoch gating
(`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1). Level HELD at 0 (unchanged by this pass).
**Builds on:** `EP5_SETTLEMENT_TRUE_UPS_DISCOVER_FRAME.md` (2026-08-17, landed 2026-08-18 in
`9eae51afa`), which left six open questions. This pass closes open questions 1 and 2 with a
primary source and gets a materially different answer than either shipped implementation encodes.

---

## 0. The headline

**Open question 1 ("which timetable is real?") is answered by a primary, dated Elexon/MHHS
document, fetched directly this pass. It does not split the difference between the world's and
company's numbers — it says both are wrong about which run is the expensive one, in the same
direction, for the same underlying reason: both call the 28-month run "RF" when the sourced
material calls the 28-month run "DF", and RF is a different, earlier run at 14 months.**

The director's framing and this atom's own `name:` field ("RF at 14 months") are the ones that
turn out correct. It is `simulation/settlement_timetable.py` and
`company/market/bsc_settlement_run_register.py` that need correcting — not the framing (partial
answer to open question 2: the correction is owed to the code, and does not touch the director's
document).

---

## 1. The source, and why it is trustworthy where prior passes could not get one

`www.elexon.co.uk` is Cloudflare-walled and returns HTTP 403 on every path — reproduced today
(three independent confirmations now: 2026-07-10 `settlement_rebilling_best_practice.md`,
2026-07-12 `ASSUMPTIONS.md` §on-page 393, and this pass). `bscdocs.elexon.co.uk` returns HTTP 200
but is a JS-rendered SPA shell with no document body in the fetched HTML — a dead end, not a wall.

The document that resolves this is a different artefact entirely, found via web search and fetched
directly (HTTP 200, no Cloudflare gate):

> **MHHS-DEL1590 v2.3, "Requirements for the Transition to the new MHHS Settlement Timetable",
> MHHS Programme (Elexon-facilitated, industry-led), status "Public", dated 14 March 2025.**
> `https://www.mhhsprogramme.co.uk/api/documentlibrary/Design%20Documents/MHHHS-DEL1590_MHHSP_Transition_to_new_Settlement_%20Timetable%20v2.3%20Approved.pdf`

This is a primary, named, dated, versioned official document (with its own change-control table:
draft 2023-08-10 through approved 2025-03-14), not a training-era recollection and not a search
snippet. `[H]` confidence per R9. Read in full (9 pages) via direct PDF extraction, not the lossy
web-fetch summariser, after the summariser reported the extracted text as "corrupted."

## 2. What it says, verbatim, quoted

Executive summary, first sentence:

> "This paper sets out the proposal to transition from **the legacy 14 month Settlement
> Timetable** to a new 4 month Settlement Timetable, known as the Settlement Timetable Transition
> (M16), which is the planned cutover date of **2 July 2027**."

§3.2's Operational Choreography table (`Transition Gate Closure` column — the pre-M16, i.e.
**current, still-live-today** timetable; document confirms M16 has not happened, is planned for
2027):

| Run | Timing (working days post-settlement) |
|---|---|
| II (Interim Information, info only) | WD +4 |
| **SF** (Initial Settlement — first charge/credit) | Settlement Run WD +15 |
| **R1** | Settlement Run WD +39 |
| **RF** (Final Reconciliation) | Settlement Run WD +292 |

§3.1 and §3.4, on the run beyond RF:

> "The DWG also recommended that the timing of the **Post Final Settlement** should be reduced
> from **28 Months to 20 Months**." / "...**DF is still at 28 Months**." (contrasted explicitly
> against RF, which the same proposal reduces earlier and separately)

**RF and DF are two different runs with two different owed timings — 14 months and 28 months
respectively — not one run with two names for the same number.** R2 and R3 are real and are named
repeatedly in the document's prose (e.g. "replace either the R3 Run or the R2 Run", "cut off...
at the current Second Reconciliation (R2) Run") but are not broken out in this table; their
day-offsets are corroborated only by web-search summaries of Elexon's own glossary and BSCP01
titles (R2 ≈ 5 months, R3 ≈ 7 months), not by a verbatim primary quote this pass obtained — `[M]`
confidence, flagged exactly as the prior two research passes flagged the same gap.

Converting WD+39 at ~21.75 working days/month gives R1 ≈ **1.8 months** — my own computed
conversion from the primary table, not a source-stated label, flagged as such.

## 3. Reconciled against what is shipped

| Run | World (`settlement_timetable.py`) | Company (`bsc_settlement_run_register.py`) | Sourced (this pass) |
|---|---|---|---|
| SF | *(none — run starts at "initial")* | 0 mo | ~0.7 mo (WD+15) `[H]` |
| R1 | 1 mo | 5 mo | ~1.8 mo (WD+39) `[H]` |
| R2 | 3 mo | 14 mo | ~5 mo `[M]` |
| R3 | 5 mo | 26 mo | ~7 mo `[M]` |
| **RF** | **28 mo** | **28 mo** | **~14 mo** `[H]` — matches the atom's own name and the
  director's framing exactly |
| DF (post-RF disputes) | *(not modelled as a separate run)* | *(not modelled as a separate run)* | 28 mo, reducing to 20 mo at M16 `[H]` |

Both shipped copies put their last, biggest run at 28 months and call it `RF`. The sourced
material's 28-month run is real — but it is `DF`, a further run **beyond** RF, and this repo
already has code for exactly that mechanism under a different name:
`company/market/bsc_settlement_dispute_register.py`, whose own docstring cites "BSC Section T
Settlement Disputes" and which is register-only today (per the 2026-08-17 pass's own caller
census, unchanged this pass — not re-verified live, carried from the prior pass). **The "third
timetable" the 2026-08-17 pass found is not three independent guesses; it is two implementations
making the same category error (folding DF's number into RF) against one correctly-named
director framing.**

R1 is wrong in both implementations, in opposite directions and by different margins: world's 1mo
undershoots ~1.8mo by less than half a month; company's 5mo overshoots it by more than 3 months.
SF is directionally right in the company register (0mo / "T+14 days" is close to the sourced
~0.7mo / WD+15) and absent entirely from the world module, which starts its run sequence at R1.

## 4. Open question 2, answered

> "Does the atom's own name need correcting? ... If the sourced answer is 28, the atom's `name:`
> and the framing doc both carry a wrong number, and R13 says the world moves to the citation —
> but the framing is the director's, so the correction is proposed to him, not applied."

**The sourced answer is 14, matching the name and the framing exactly. No correction is owed to
`THE_VALUE_CYCLE_FRAMING.md` or to this atom's `name:` field.** The correction is owed to the two
code modules, at the atom's eventual BUILD (R13: the world's timetable moves only with a
citation — this pass is that citation, not yet applied, because file_scope is `[]` under this
draw).

## 5. What remains open

Unchanged from the 2026-08-17 pass except questions 1 and 2, now closed:

* OQ3 (is `W3_2` really done at L2, or was L2 a target set before the coupling rule existed) —
  untouched.
* OQ4 (what the company's pre-run estimate is, EP2's overlap) — untouched.
* OQ5 (§3's clock-label fork, (a) relabel `settled`→`billed` now vs (b) let EP5 make it true) —
  untouched, still a build-time decision, still recommending (a).
* OQ6 (back-billing boundary ownership) — untouched.
* **New, narrower than OQ1 was:** R2/R3's exact day-offsets remain `[M]`-confidence
  (search-corroborated, not primary-quoted) — the reachable-Elexon-surface question this pass
  answers is "is `bscdocs.elexon.co.uk` or `data.elexon.co.uk`'s BMRS API a route to them,"
  and the answer is no: the BMRS balancing API (`data.elexon.co.uk/bmrs/api/v1`, confirmed live
  and on the egress allowlist, price/volume series only — probed this pass, `reference/datasets`
  and settlement-run-shaped paths 404) does not carry settlement-calendar/rules content at all,
  and `bscdocs.elexon.co.uk` (BSCP01, the section that would carry it) serves an empty JS shell
  to a non-browser fetch. Closing R2/R3 to `[H]` needs either a rendered-JS fetch of BSCP01 or
  another primary MHHS-programme-style document; not attempted further this pass (diminishing
  return against C-S1/R14, which bind regardless of R2/R3's exact offsets).

## 6. Disposition

**Level HELD at 0.** `loop_stage: idle`, BUILD-gated. No code under
`company/ sim/ simulation/ saas/ tools/ background/` touched by this pass — the reconciliation
in §3 is a table for the eventual BUILD to apply, not applied here.

**Nothing fixed on sight** (SELF_INTERRUPT_DISCIPLINE) — the RF/DF conflation is EP5's own build
subject matter, queued as this document.

Evidence line added to `docs/design/simplifications/EP5_settlement_true_ups.yaml`.
`docs/design/maturity_map.yaml` untouched (this atom carries no `simplifications_count` field —
verified against `tests/design/test_simplifications_store.py::test_count_check_permits_zero_or_absent_for_an_empty_register`,
the same pattern the 2026-08-17 pass used).
