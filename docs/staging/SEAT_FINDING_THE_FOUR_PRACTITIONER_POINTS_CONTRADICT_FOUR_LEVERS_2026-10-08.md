**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_9_segment_debt_tnc` · **Claim:** `the-four-practitioner-points-reach-the-knowledge-pages` (Lane 0)

# The four practitioner points contradict four levers in the build

## Premise, re-measured at draw

The research for the director's item 2 (2026-10-07) was already on origin: `fe150ffd1` wrote all four
points into the three pages, with sources and named GAPs. The drawn item's own DONE clause was still
open, though: a table mapping each point to the levers it bears on, and a finding for each
contradiction. That table is now `back_billing_and_liability.md` §10. This finding covers the rows
in it that contradict the build.

## The contradictions

1. **World post-write-off recovery is above the evidence, and it does not read the register.**
   `simulation/arrears_engine.py` recovers 25.5p (OVERWHELMED), 17.0p (NEUTRAL) and 12.0p (AVOIDANT,
   sold) per GBP written off. Those figures were printed from `dca_recovered_amount` and
   `debt_sale_proceeds`, and phase 4c reaches them through `compute_debt_recovery`. The world writes
   off at the final bill's due date. For a write-off that early, the published comparison is the
   10-25p implied by Centrica's final-bill coverage over 90 days. The DCA figures sit at or above the
   top of that range. The 12p sale is above both published purchase prices (Lowell 5.4p, Arrow 9.3p)
   on debt only about 120 days past due. The register's `q3_post_write_off_recovery_share` (0.05) is
   read by no code. Direction: the world's realised loss is understated, and the supplier's bad debt
   with it.
2. **The unread-meter class is keyed to the customer, not the premises.**
   `simulation/meter_reads.is_hard_to_read(customer_id)`. Every published cause of persistent
   no-access is a trait of the premises (Ofgem 2018 p.8). **Today this does nothing**, because with
   moves off each premises has one customer for life. **It goes live the moment the director switches
   `home_moves_activation` on**: an incoming occupier redraws the class. The share (0.01) stands. This
   is already W2_36's work (read-access page §5, §9.3), so this is a pointer and not a new atom.
3. **Smart-meter exposure is not tilted by tenure.** `simulation/premise_population.smart_read_share`
   is one national curve. EHS 2022-23 measures 57.0% of private renters without an electricity smart
   meter, against 43.9% of owner occupiers. This moves who is read by hand, not how many.
4. **The company names the void leg as the occupier's.**
   `company/crm/change_of_tenancy_register.DeemedLeg.VOID_OCCUPIER`. For an unoccupied premises the
   deemed contract is with the owner (Electricity Act 1989 Sch 6 para 3(1)). Only `deemed_legs()`
   counts it today and no collection route reads it, so the cost is a wrong frame for the first
   landlord-collection code that does.

Also stale, and corrected nowhere yet: the director's open row `home-moves-can-now-be-switched-on`
still says "the incoming account pays for the whole change-of-tenancy window". B7 slice 4
(`dfa787a37`) books that window as occupier debt, so the bias it names in our favour has been
removed. Nothing in point (a) argues against the row's proposal.

## Proposed, in order

1. Read `q3_post_write_off_recovery_share` (and `q3_debt_sale_price_share_of_face` when it has a
   value) in `arrears_engine`, in place of the typed rates. Pre-register the change in the run's
   bad-debt total before running it. World code: `sim-engineer`.
2. Key W2_36's hard-to-read class to the premises **before** moves are switched on, or in the same
   landing.
3. Tilt `smart_read_share` by tenure from the EHS table, keeping the national curve as the mean.
4. Rename the void leg to the owner's when a collection route first reads it. Until then, record
   rather than change it.

## Not established

How any of these moves a published figure. No run was made this turn. Row 1's direction (losses
understated) is derived from the rates, not measured.

## Contradiction 1: pre-registration (written 2026-10-08 00:32Z, before any run)

**What the recovery share IS, before choosing a row.** The register's
`q3_post_write_off_recovery_share` (0.05) is defined for a LATE write-off, six to twelve months after
the final bill, and its own `meaning` says a write-off at the final bill's due date "is a different
event and is compared with 1 - prov_coverage_final_bill_over_90d instead". The world writes off at
the due date (`WRITE_OFF_DATE_CONVENTION`), so everything a real supplier collects between the due
date and its late write-off sits inside the world's post-write-off leg. Reading 0.05 there would
drop that collection and make the world too harsh, inverting the defect rather than fixing it. So
`arrears_engine` reads the row the convention names: `1 - prov_coverage_final_bill_over_90d` =
0.122 (Centrica ARA 2025 Note 17). `q3_post_write_off_recovery_share` is the row for a late
convention, and the engine refuses any convention it has no row for. The register calls the
coverage complement "expected recovery", with no commission deducted, so the typed 15% commission
goes too. `q3_debt_sale_price_share_of_face` is null, so no debt is sold: the SOLD stage is reached
only when the register gives that row a value, and AVOIDANT debt is worked at the same share.

**Instrument.** One `run_phase4c_on_phase2b.main()` founders run from origin/main. The inputs
`compute_debt_recovery` receives are captured once, and the old and new rates are applied to the
SAME write-offs in ONE process. Only the recovery leg differs.

**Predictions:**
1. Gross write-offs (close + statute-barred): **unchanged**, to the penny. Recovery is booked after
   write-off and feeds nothing upstream.
2. Recovery falls. The old blended rate is between 0.12 and 0.255 by archetype. I predict NEUTRAL
   dominates, so the blend is about 0.17 and recovery falls by about **28%** (0.17 to 0.122).
3. Net bad debt (write-offs less recovery) rises by about **6%** ((0.17 - 0.122) / (1 - 0.17)).
   Anything above 12% means OVERWHELMED (0.255) carries more of the book than I think.

## Contradiction 1: result (2026-10-08 01:20Z), beside the prediction above

One `run_phase4c_on_phase2b.main()` from origin/main `1caaec35a`, default window, 2,783 s. The
captured `compute_debt_recovery` inputs were scored by the origin engine and the new engine in one
process (`/tmp/recovery_measure.py`; not kept).

| | origin (typed rates) | register | change | predicted |
|---|---:|---:|---:|---:|
| Gross write-offs, all at close | GBP 14,411.11 | GBP 14,411.11 | 0 | unchanged |
| Recovery | GBP 2,439.85 (0.169 of write-offs) | GBP 1,758.14 (0.122) | -27.9% | about -28% (blend about 0.17) |
| Net bad debt | GBP 11,971.26 | GBP 12,652.97 | +5.7% | about +6% |

Close write-offs by archetype: NEUTRAL 195 cases (GBP 13,626.72), AVOIDANT 13 (GBP 568.27),
OVERWHELMED 6 (GBP 216.12). All three predictions held. No statute-barred write-off occurred in
this window.

**Bounds.** 214 write-offs and GBP 14k on one seed: this is a statement about the mechanism, not a
bad-debt level to publish. The recovery is gross of collection cost. Ofgem's 3p per GBP (DRS IA,
fn 6) is not deducted, so net loss is still understated by up to about 3p per GBP written off.
Pricing that cost is a separate item.

**What landed.** `arrears_engine.post_write_off_recovery_share` reads
`prov_coverage_final_bill_over_90d`, the row the register names for the world's write-off date. A
late write-off convention would read `q3_post_write_off_recovery_share`, and until one exists any
other convention is refused. `debt_sale_price_share` reads `q3_debt_sale_price_share_of_face`.
That row is null, so the reason travels with it and nothing is sold. `final_bill_outcome` folds
the same function. The control is
`tests/simulation/test_post_write_off_recovery_reads_the_register.py`: it moves the register and
asks the world to move with it, and it reds when the typed 25.5p/17.0p rates return (mutation run
2026-10-08: two legs red). Archetype no longer changes the recovery, because nothing published
separates it.
