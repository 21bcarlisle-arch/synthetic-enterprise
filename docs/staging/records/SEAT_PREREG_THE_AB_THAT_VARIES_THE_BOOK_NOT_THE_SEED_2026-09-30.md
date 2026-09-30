# Prereg: the A/B that varies the book, not the seed — ab6's n\* > 12 successor, written before P2 answers

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Item:** `prereg-the-book-varying-design-before-the-pilot-answers` · **Status:** written, pinned, **NOT launched, NOT built.** Written 2026-09-30 while ab6's bridge leg B (seed 33333 done at 5,368.9 s; 44444 running) was still ahead of P1 and P2. `/var/tmp/se-ab6-out/runP1.json` and `runP2.json` do not exist at the time of writing. So everything below is a prediction.

## Why this exists

ab6's prereg (`records/SEAT_PREREG_THE_NEXT_AB_ON_THE_SINGLE_ROLL_WORLD_WHAT_A_SEED_VARIES_2026-09-30.md`) says that if n\* > 12 the answer is *"stop, vary the book"*, and it puts ~70% on that branch (P2). It named two candidates: "a longer window, or a funnel that offers renewals more widely". The `REDRAW_KEYS` note in `tools/run_value_cycle_ab.py` names the same two. If the successor were designed after the pilot has answered, it would be fitted to that answer. This record chooses **one** variable now.

## The three candidates, and why two of them are refused

Measured on `/var/tmp/se-ab5-out/runB.json`, seed 33333 (the funnel is identical on every seed; only the elasticity moves):

- **Book:** 164 billing accounts settled, `report_end = null`, cohorts 2016 (74) → 2025 (5).
- **Renewal-decision distribution:** 94 accounts take **0** priced renewal decisions, 48 take 1, 16 take 2, 3 take 3 and 3 take 4. So 70 accounts carry 103 priced renewals.
- **The accounts that never renew are long stayers, not early leavers.** All 94 have `left_at = null` and 3–201 bills (median ≈ 50). 35 of the 74 accounts from the 2016 cohort sit through the whole window without a priced renewal. The 94 hold £106,116 of the value arm's £177,302 net.

**1. A longer window — refused: it does not exist.** The run already covers the full record (`report_end = null`; accounts from 2016-01). The 2016–2025 record is historical ground truth, and there is no later year to add. `--end-year` can only shorten the window.

**2. A wider renewal funnel — refused: it would make the book less like a real one.** A thin funnel is what a real GB book looks like. Knowledge map, row *Default/SVT share of the domestic book* (`tools/published_tariff_mix.DEFAULT_TARIFF_SHARE`): 58–74% of domestic households were on a default tariff in 2016–19, 80–90% in 2022–24 and 64–70% in 2025. Row *Active vs passive renewal*: ~35% actively renew and ~65% roll to SVT. A real supplier's book offers its pricing arm a renewal decision on a minority of accounts, and 70 of 164 (43%) is inside that band, not below it. There are two ways to widen the funnel, and neither is a measurement variable:
   - **World-side:** a lower SVT share. That is a baseline change for a non-fidelity reason, which is a wall.
   - **Company-side:** a conversion desk that approaches SVT households. That is a **new treatment**, not a larger sample of the old one. It is also still blocked on two declared gaps: the per-contact cost has no reachable citation, and the response rate to a supplier-initiated approach is unpublished (knowledge map, row *What a conversion decision at a cap boundary IS*). Widening the funnel to buy statistical power would change the thing being measured.

**3. More books — CHOSEN.** `simulation.live_population.live_population(base_seed)` draws the book from a seed. `_DEFAULT_BASE_SEED = 20260724` is documented at its definition as *"a MECHANISM default (determinism), NOT a curriculum knob — the curriculum decision is on/off; the seed only fixes which deterministic draw the 'on' state yields."* Varying it keeps everything the director set in `docs/design/FOUNDER_BOOK.yaml` (80 founders, the settlement customer-year budget, served segments) and redraws which households fill those slots. So it is the seat's to vary.

**Why "more books" is the faithful variable.** A real supplier exposes one book, but that book holds 10⁴–10⁶ accounts, not 164. D is a sum over accounts, and its renewal-roll noise shrinks roughly as 1/√N. K independent books of this size are the nearest thing this box can run to one book K times larger. That holds only while book-level couplings (the campaign budget, the opening capital) do not dominate, and K1 below tests that. It is also the estimand the mission names: **the enterprise value is the method, and the book is the evidence** (CLAUDE.md, mission point 3). ab6 on its best day answers *"on this one book, over its renewal noise"*. The book design answers *"on a book like this, does the method beat flat rules?"*

## A defect this design must close before it can run (measured 2026-09-30)

`founder_book(20260724)` and `founder_book(61001)` were compared (1.4 s, run in the shared tree). **77 of the 80 founder ids are shared, and only 18 of those records are identical.** For example, `SYN-2016-001` is a Yorkshire electricity-only home at one seed and a London gas home at the other. The ids are positional.

`churn_roll_for_renewal(billing_account, term_start_str)` hashes the id and the date with no seed (ab6 prereg, §What a seed varies). Founder acquisition dates cluster at 2016-01-01/02, so **a different household under a shared id would often take the same renewal roll in every book.** Rolls would correlate across books, the between-book spread would be too narrow, and it would be narrow in the flattering direction.

**The remedy already exists, so no new randomness is needed.** Run each book under `--redraw-key churn_roll` with the floor seed set **equal to the book seed**. `_churn_roll_redraw_patch` then composes the namespaced stream `floor{seed}_{account}_{term}`, so the book and the roll move together. Elasticity already follows the book, because `customer_events` passes `run_base_seed()` to `price_elasticity_for_customer`.

## What must be built first (not built here; one turn of code, no box time)

`run_value_cycle_ab --book-seeds S1,S2,…` (the name is illustrative). For each member it must:

- resolve the book at `base_seed = Sᵢ` **before** any entrypoint imports it (`live_population()` is called at module import, so this probably means one subprocess per book);
- patch the churn roll with floor seed `Sᵢ`;
- record `run_base_seed()` and `billing_accounts_settled_in_window` per member.

It must **refuse** in three cases:

- two members share a book seed;
- a member's recorded `run_base_seed()` is not the seed it was asked for (this is the silent-default failure `run_base_seed`'s docstring names);
- the churn-roll patch reports `redrawn = 0`.

The one-leg control is a two-book fold on a truncated window (`--end-year 2017`). It asserts that the two members' founder rosters differ **and** that their roll streams differ on a shared id. Controls that can only check that a book seed was used are refused.

## The statistic

**D_book = Σ over this book's decided-differently lineages of (value arm − level arm), divided by `billing_accounts_settled_in_window`.**

- The numerator counts pounds of selection on accounts where the two arms decided differently. It uses the lineage root, exactly as `grade_lineage.py` does.
- The denominator counts accounts the book held. So the ratio is selection value per account held over the window, which is a quantity. It is needed because book size varies with campaign wins.
- **There is no ex-0098 exclusion.** That exclusion was one book's named account, and under another seed `PROS-2016-0098` is a different household. A design that averages over books must not carry any single book's special cases. The total in £ is reported beside D_book, never instead of it.

## Cost, from measured seed times

Nine `--level-arm` seed passes are on disk (`/var/tmp/se-ab5-out/run{A1,A2c,B,L}.log`, `/var/tmp/se-ab6-out/run6.log`): 5,368.9–5,752.1 s, **mean 5,560 s = 1.54 box-hours per book**. A book pass is the same three-arm pass at the same book size, so it costs the same. Legs run 2 books each, strictly serial, at ab6's declared 11.2 GB peak (≈3.1 h per leg, inside a 5 h continuation).

| step | books | box-hours |
|---|---|---|
| book pilot | 4 (2 legs) | **6.2** |
| extend to n\*_b, capped at 12 | +8 at most | +12.4 (18.5 total) |
| for comparison: extending ab6 from 4 seeds to n\*_r = 13 (the smallest over-ceiling case) | +9 | +13.9 |
| for comparison: extending ab6 at P1's own point guess (s ≈ £4,000, \|m\| ≈ £1,000, so n\*_r ≈ 66) | +62 | +96 |

## The rule that decides between this design and extending ab6

1. **n\*_r ≤ 12 on ab6's pilot:** extend ab6, as its own rule says. This design is **not** launched. It stays filed as the generalisation question ("was that one book?"), to be drawn after ab6 is graded.
2. **n\*_r > 12:** **do not extend ab6.** Build `--book-seeds` and run the 4-book pilot (6.2 h). The pilot is cheaper than the smallest over-ceiling extension of ab6 (13.9 h). Its answer also decides whether any spend at this book size can sign D, and extending ab6 answers only the one-book question.
3. **After the book pilot, n\*_b ≤ 12:** extend to n\*_b books and grade with a t-CI on the mean D_book. Plain answer: *"on a book like this, over book and renewal noise, the per-customer arm does / does not beat flat rules."*
4. **n\*_b > 12:** **stop.** The answer is *"at 164 settled accounts, neither one book's renewal noise nor a family of books can sign D inside the compute ceiling"*. The remaining lever is book **size**, which is the director's curriculum (`FOUNDER_BOOK.yaml`), not the seat's. It goes to him as a priced menu (founders ↔ campaign width ↔ settlement budget, and the pass time a larger book costs), never as a run.

The ceiling of 12 is ab6's compute choice (~18.6 h, about three continuations), carried over unchanged. It is not a domain number.

## Predictions (fixed before runP2.json exists; nothing below has been run)

| id | line | prediction | refuted if |
|---|---|---|---|
| **K1** | between-book sd of D_book (4 books) against ab6's within-book roll sd, both per settled account | s_b ≥ s_r. A book seed re-draws the rolls **and** the composition, so it can only add variance | s_b < 0.8 · s_r. Book-level couplings are then pulling books together, and K books are **not** a stand-in for one bigger book. The rationale above fails |
| **K2** | n\*_b at the pilot's own mean | **> 12** (~65%), so rule 4 applies and the question goes to the director as book size | n\*_b ≤ 12 |
| **K3** | settled accounts per book | every book within 150–180 (the founders and the budget are fixed by curriculum; only the campaign's wins vary) | any book outside 150–180 |
| **K4** | accounts with ≥ 1 priced renewal, per book | every book within 55–85 (the thin funnel is world physics, not a draw of one book) | any book < 45 or > 100. The funnel is then a property of the 20260724 book, and refusal 2 above is weakened |
| **K5** | the share of D_book variance held by the single largest lineage in any book | < 50% (under book and roll redraw, no single household is present in every book) | ≥ 50% in any book |
| K6 (context) | the sign of D_book | 3 of 4 books positive | not graded |

**Confidence:** K1 ~75%, K2 ~65%, K3 ~80%, K4 ~80%, K5 ~70%.

**What would make this the wrong test.**
- If ab6's bridge refutes B1 badly (|Δ| > £1,000), HEAD is a different company. This design then runs at whatever pin ab6's successor is graded at, and not at `a322166cc`.
- If the one-leg control finds the roll streams equal on a shared id, the re-key did not reach the roll. The design is then void until it does, for the same reason ab6's `churn_rolls_redrawn = 0` voids ab6.

## Launch conditions (all must hold)

1. ab6 is graded, and its n\*_r > 12 (rule 2). Otherwise this record stays filed.
2. `--book-seeds` is landed with the refusals and the one-leg control above.
3. The same pin and weather-store checks as ab6's `legs6.sh`. No other `run_value_cycle_ab` is resident.
4. It is launched through `background.launch_long_job` as one unit of 2-book legs gated through `tools.wait_for`, declaring the 11.2 GB peak.

Grading: D_book per member, and n\*_b by ab6's formula (t₀.₉₇₅,ₙ₋₁ · s / √n ≤ |m|, also reported at |m| = ab5's £1,009.68 ÷ 164 per account). Then K1–K5 against this table.
