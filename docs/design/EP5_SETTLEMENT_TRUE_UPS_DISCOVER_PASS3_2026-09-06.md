# EP5_settlement_true_ups — DISCOVER pass 3 (2026-09-06): the correction reached two of four

**Atom:** `EP5_settlement_true_ups` (lane `E_finance_treasury`, stream `wholesale_to_price`, epoch 2,
L0→L3, `loop_stage: idle`, `dial_inherited: 3`, `provenance: director_ruling`)
**Couples with:** `W3_2_settlement_timetable`
**Draw:** 2026-09-06 scheduled tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code written** —
`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1. **Level HELD at 0**, not moved and not requested.
**Measured at:** HEAD `fdfa0c94f`. Every file below read on disk this pass; `site/data/world.json`
parsed, not sampled.

**Builds on:** `EP5_SETTLEMENT_TRUE_UPS_DISCOVER_FRAME.md` (2026-08-17, landed `9eae51afa`) and
`EP5_SETTLEMENT_TRUE_UPS_DISCOVER_PASS2_2026-08-18.md` (landed `f1776d29d`), plus the primary-source
verification that followed them: `docs/market_research/elexon_settlement_run_timetable_verified.md`
(2026-08-29).

---

## 0. Why this pass exists at all

EP5's DISCOVER is saturated: two passes, and pass 2's central finding — that RF is the **last
scheduled run at 14 months** and the 28-month run is **DF, disputes only** — was verified against an
Elexon-authored primary document on 2026-08-29 and **acted on in code**. A third DISCOVER pass that
re-derived the same thing would be waste.

The question this pass asked instead is the interconnection one: **of what landed since pass 2, what
assumed it, and does that assumption still hold?** Pass 2 named *two* shipped implementations needing
correction. The answer is that there were **four**, the correction reached **two**, and one of the two
it did not reach is the copy that feeds the published site feed.

---

## 1. The census: one Elexon timetable, four implementations

Elexon's own timetable (Priestley, *Settlement Timetable*, 16 June 2014, hosted on ofgem.gov.uk;
transcribed in `docs/market_research/elexon_settlement_run_timetable_verified.md`):

| Run | II | SF | R1 | R2 | R3 | **RF** | DF |
|---|---|---|---|---|---|---|---|
| after settlement date | 1 wk | 1 mo | 2 mo | 4 mo | 7 mo | **14 mo (last scheduled)** | 28 mo (disputes only) |

What the tree carries, at HEAD `fdfa0c94f`:

| # | file | R1 | R2 | R3 | RF | state |
|---|---|---|---|---|---|---|
| 1 | `company/regulatory/settlement_reconciliation.py` (`_R*_MONTHS`, L59–62) | 2 | 4 | 7 | **14** | **CORRECTED**, with the correction narrated in its own comment (L35) |
| 2 | `simulation/settlement_timetable.py` (`R*_MONTHS`, L72–75) | 2 | 4 | 7 | **14** | **CONSTANTS CORRECTED — its own docstring was not** (§2) |
| 3 | `company/market/bsc_settlement_run_register.py` (`_SETTLEMENT_RUN_MONTHS`, L48–53) | 5 | 14 | 26 | **28** | **UNCORRECTED**, and disagrees on *every* run (§3) |
| 4 | `tools/generate_world_data.py` (`settlement_ladder`, L194–200) | 5 | 14 | 26 | **28** | **UNCORRECTED**, hardcoded, **reaches `site/data/world.json`** (§4) |

Pass 2 named #2 and #3. #1 was already right by then. **#4 did not exist in pass 2's frame at all** —
it is a fourth, hand-copied transcription of #3 living in the site data generator, and it is the one
with a reader outside this repository.

This is the shape CLAUDE.md names by hand: *one legal requirement, five implementations, a defect
fixed in one of them in July and still live in another in August, and nothing anywhere able to
notice.* Nineteen days elapsed between the correction landing and this pass finding the survivors.

---

## 2. #2 corrected its constants and left its prose asserting the refuted numbers

`simulation/settlement_timetable.py` lines 3–7, verbatim at HEAD:

> Real UK settlement is not a single, final-form figure produced at delivery time -- it is revised
> over a sequence of real Elexon settlement runs: R1 (~1 month post-delivery), R2 (~3 months),
> R3 (~5 months), and RF (Final Reconciliation, **~28 months**), each resolving a further share of the
> total adjustment volume (**60% / 25% / 12% / 3%** respectively).

Lines 21–22 repeat it (`R1 ~1mo post-delivery, R2 ~3mo, R3 ~5mo, RF ~28mo`). Lines 72–75, sixty lines
below, carry `R1_MONTHS = 2`, `R2_MONTHS = 4`, `R3_MONTHS = 7`, `RF_MONTHS = 14`, and the shares that
replaced 60/25/12/3.

**The module's own first paragraph — the thing a reader reads first — states the numbers the primary
source refuted, in the file where they were refuted.** No control catches this, because every control
reads the constants and none reads the prose. It is not a cosmetic point: pass 1's headline was that
this repo held *three timetables none of which cited a source*, and the remedy has left a fourth
uncited timetable inside the corrected file.

---

## 3. #3 disagrees on every run, cites nothing, and no production code imports it

`company/market/bsc_settlement_run_register.py` states its timetable as fact in its module docstring
(L6–10: `SF — T + 14 days`, `R1 — T + 5 months`, `R2 — T + 14 months`, `R3 — T + 26 months`,
`RF — T + 28 months`) and again in `SettlementRunType` comments (L36–39) and in
`_SETTLEMENT_RUN_MONTHS` (L48–53). Three copies inside one file, no citation on any of them.

Every figure is wrong against the sourced timetable, and wrong in a *structured* way: it looks like
the real ladder with each run pushed one rung late — the number Elexon gives R2 (4) is absent, the
number Elexon gives RF (14) is here attached to **R2**, and 28 (Elexon's DF, disputes only) is here
attached to **RF**. It is the same conflation pass 2 diagnosed, one rung deeper.

**Reach, measured** (`grep` over all `*.py`, non-test importers):

| importer | kind |
|---|---|
| `tools/generate_world_data.py` L25, L193, L222 | **prose reference and evidence citation only — no import** |
| `company/market/bsc_settlement_dispute_register.py` L15 | comment |
| `company/regulatory/network_code_modification_register.py` L29 | comment |
| `tests/company/market/test_bsc_settlement_run_register.py` | the only file that imports it |

**Zero non-test importers.** This is the unwired-and-wrong pair: a module nothing calls, carrying an
uncited timetable that contradicts the sourced one, *while being named as the evidence for a published
figure by a tool that does not import it* (§4). Being unwired is what has kept it wrong; being cited
is what makes that matter.

---

## 4. #4 is the copy with a reader, and it is in the published feed

`tools/generate_world_data.py` L194–200 hardcodes the ladder as five literal dicts — a hand copy of
#3's docstring, not a read of #3's constants. Its `mechanism` prose (L219) states the ladder
*"progressively swaps estimates for actuals over ~28 months"*, and its `evidence` field (L222) names
`company/market/bsc_settlement_run_register.py` — the module it does not import and which is itself
uncited.

**This reaches the published artefact.** `site/data/world.json`, `generated_at`
`2026-09-06T08:53:08Z`, `git_commit` `b01b1dbe3`, carries under `wall.crossings[id=meter_reads]`:

```
SF  Initial Settlement    T + 14 days     R1  First Reconciliation   T + 5 months
R2  Second Reconciliation T + 14 months   R3  Third Reconciliation   T + 26 months
RF  Final Reconciliation  T + 28 months   ("final, no further runs")
```

**Bound honestly:** `settlement_ladder` and `mechanism` are written into the feed but **no page
renders either** — `grep` for `settlement_ladder` across `site/**` hits `site/data/world.json` and
nothing else, and the wall crossings rendered by `site/harness/index.html` and
`site/capabilities/index.html` do not read `mechanism`. So this is *published into a served feed*, not
*rendered on a page*. That is the difference between a reader having to open the JSON and a reader
being shown it — and it is the whole of the mitigation. The figure is public and wrong either way.

Filed as its own finding this pass:
`docs/staging/SEAT_FINDING_ONE_ELEXON_TIMETABLE_HAS_FOUR_IMPLEMENTATIONS_THE_CORRECTION_REACHED_TWO_AND_THE_PUBLISHED_FEED_CARRIES_AN_UNCORRECTED_ONE_2026-09-06.md`.

---

## 5. What this changes in EP5's FRAME

Pass 1's FRAME assumed the timetable question was "which of the three is real". It is answered. The
question this pass leaves in its place is **why a correction to a domain constant reaches some of its
implementations and not others** — and that is not an EP5 question, it is the class question. EP5's
own frame gains one hard precondition:

> **EP5-P0 (new).** Before EP5 BUILD writes a single restating ledger entry, the four timetables must
> be **one** — a single sourced module the others import, or three deletions. A ledger that restates
> on the real timetable, built beside three copies that disagree about what the real timetable is,
> will be correct and unbelievable. Falsifier: a control that fails when any two of the four
> disagree — keyed to the *property* ("the tree holds one settlement timetable"), not to today's
> numbers, so it stays green when Elexon changes them and red when a fifth copy appears.

The L1/L2/L3 criteria in `EP5_SETTLEMENT_TRUE_UPS_DISCOVER_FRAME.md` §7 are otherwise unchanged by
this pass and are not restated here.

---

## What this pass did NOT do, so the next draw is not misled

**No code was changed** — not the docstring in #2, not the constants in #3, not the literals in #4.
All three are corrections to live modules, and this is a DISCOVER/FRAME draw on a BUILD-gated atom
(Rule 1). The correction is **queued in the finding, not applied here**, and the finding names the
exact lines.

`site/data/world.json` was **not** regenerated and the site was not republished. Whether `#3` should
be corrected or deleted was **not** decided — it has no importers, so deletion is live on the table
and that is a call for the lane that owns it, not for this pass. Whether the shares (60/25/12/3 vs
the corrected curve) have their own second home was **not** chased. `simulation/settlement_run_series.py`,
`simulation/settlement.py` and `simulation/hedged_settlement.py` were read for timing constants and
carry none — they are not a fifth and sixth copy, they consume `settlement_timetable`. EP5's level is
unchanged at 0 and no promotion is requested.
