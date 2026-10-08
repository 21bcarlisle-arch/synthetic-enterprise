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
