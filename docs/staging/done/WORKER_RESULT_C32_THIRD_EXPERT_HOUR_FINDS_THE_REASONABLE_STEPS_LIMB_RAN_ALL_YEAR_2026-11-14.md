# C32's third Expert Hour: the reasonable-steps limb ran all year, and the licence says winter

**Fate (2026-11-14):** RESULT. C32 stays at level 2. The one failure within the atom's claim is
fixed in this tick, knowledge page first. A fourth pass on the corrected code is owed, because the
fix lowers protection and I graded my own fix.

**The pass.** A blind, same-model reviewer (`tools/blind_review.py`, ledger row
2026-11-14T19:30:00Z), as a veteran of PSR and debt-and-disconnection operations. It worked with
no tools. The plain words were the re-take's, with the needs-code crosswalk landed in e6134becdd
now described. Before it was shown, I checked the packet's examples of no-category codes against
commons s.1a and corrected them. Priors came first, and it returned 15 questions.

## The item that failed, and what settled it

Item 1 asked whether SLC 27.11's "all reasonable steps" duty is winter-only. The 14 Nov re-take's
reviewer had asked the same thing (its item 7). The commons recorded it as a GAP, and the code
applied the limb all year, "the direction that keeps protection".

**This time the instrument was read.** Ofgem's modification direction of 15 Sep 2010, effective
1 Oct 2010, prints the conditions as modified, for gas (p. 3) and electricity (p. 4):

> 27.11 The licensee must take all reasonable steps to avoid Disconnecting, **in Winter**, a
> Domestic Premises at which the Domestic Customer has not paid Charges for the Supply of
> Electricity if the occupants of the premises include a person who is of Pensionable Age,
> disabled or chronically sick and to whom paragraph 27.10 does not apply.

27.11(A), added by that direction, requires all reasonable steps to ascertain whether 27.10 or
27.11 applies before disconnecting. That is the licence ground for "cannot determine blocks".

**So the decider's claim to be "the published rule" was false from April to September.**
"Keeps protection" was a policy choice, the voluntary Safety Net, presented as the licence.

**Wording not read.** Whether the 2010 text was amended between 2016 and 2025. The 2022
parliamentary answer still cites 27.10, which is consistent with no change.

## What changed

1. **Commons first (K8).** The page is
   `psr_eligibility_and_disconnection_protection.md`. Three edits:
   - S8 (the instrument) is added to the sources.
   - §2 is corrected beside the claim, and now records 27.11(A).
   - In §4, the season gap is closed and the instrument gap is narrowed to the conditions not yet
     read. The design choice is stated there: the decider returns the licence's answer, and
     whether the supplier adopts the Safety Net is a company policy question, not decided.
2. **`_disconnection_protection`.** The reasonable-steps limb is gated to winter, and so is
   medical-equipment-alone's "cannot determine". That one asked whether the person is also
   disabled or chronically sick, which outside winter changes nothing. Outside winter, a
   protecting category reads NOT_ESTABLISHED, and the reason names both licence limbs as winter
   duties and the Safety Net as voluntary and not modelled.
3. **`PSRRecord.disconnection_protection`.** A registration with no need recorded now asks the
   counterfactual over every category. It reads CANNOT_DETERMINE in winter, as before. In summer it
   reads the licence's NOT_ESTABLISHED, because no need could change that answer.

**At real inputs, every category × 15 Jan / 15 Jul / 30 Sep / 1 Oct / 31 Mar / 1 Apr ×
composition:**
- Protection from pensionable age, disability, chronic illness and medical equipment holds on
  1 Oct and 31 Mar, and is absent on 30 Sep, 1 Apr and 15 Jul.
- The other six categories are NOT_ESTABLISHED on every date.

**Tests.**
- Four legs asserted the all-year reading and were re-keyed to winter. They are in
  `test_priority_services_register.py` (reachability, the October boundary, medical equipment),
  `test_psr_registration_from_disclosure.py` (code 22, and the empty registration, renamed
  `..._in_winter`, with a summer leg added) and `test_vulnerability_register.py`.
- One new control covers the whole partition: `test_both_licence_limbs_are_winter_duties`. No
  category protects in any household from April to September. Each such answer names the
  voluntary commitment. Pensionable age, disability, chronic illness and medical equipment each
  still block somewhere in winter, so a guard that permits everything also reds.

**Mutations, three, all killed:**
- the winter gate removed from reasonable steps: 3 red;
- the winter gate removed from medical equipment: 3 red;
- the empty-registration counterfactual removed: 1 red.

## The other fourteen items, graded against the code at HEAD

| # | | grade |
|---|---|---|
| 2 | DISQ | **passes.** A flag or code graded "cannot determine" that would change the answer blocks. Reason to believe is never read as unprotected. |
| 3 | DISQ | **open, outside this atom's claim.** Nothing offers PSR registration when an agent flags an unregistered household. SLC 26's identification duty is a separate obligation. The flag still reaches the decider (item 2), so the household is not "ordinary" for disconnection. Filed here as the next SLC 26 question. |
| 4 | DISQ | **partly passes.** Needs-only registrations (the no-category codes) register. The date-dependent switch from the categorical regime to the needs-based one is not modelled. This is latent, because the world draws no codes. |
| 5 | DISQ | **out of scope, stated.** It is the re-take's item 10: no industry PSR data flow, inbound on a switch or outbound to the network, is modelled. |
| 6, 8, 12 | | **out of scope.** These belong to the collections and prepayment atoms. |
| 7 | DISQ | **passes, with the stated reason.** No production path asks for a disconnection decision, so the rate is zero. The real record is near zero. |
| 9 | SUPP | **passes.** The 60–66 band is "cannot determine", which is conservative, and the cohort tables are a named gap. The reviewer's point about men at 65 before 2018 is the cost of that gap. |
| 10 | SUPP | **open.** No company path observes household composition, so 27.10's PROHIBITED is unreachable in production: winter pensionable age reads "cannot determine". That fails closed. |
| 11 | SUPP | **open.** The review date is the registration date. The commons has no published review interval, and the reviewer's "two-yearly" is a prior, not a source. |
| 13 | SUPP | **open, latent.** The needs-code list is not versioned by date, so code 37 (water) is accepted in 2016. No codes are drawn. |
| 14 | SUPP | **passes.** The sourced 13% (2016) and 24% (end-2018) are read by `penetration_against_published`. |
| 15 | DISQ | **passes for prepayment by construction.** There is no involuntary prepayment. A referral to a collection agency is not a licence outcome, and so is not this decider's. |

## Verdict

**FAIL on item 1, fixed in this tick. Held at 2.** The fix moves the answer in the direction
that removes protection, and I wrote it and graded it. The level should move only on a fourth
blind pass, shown the corrected decider, that finds nothing within the claim. Items 3, 10 and 13
are named here, and none is this atom's claim.
