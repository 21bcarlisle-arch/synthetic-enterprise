# C32's fourth Expert Hour: from April to September the company would disconnect a household on home oxygen

**Fate (2026-11-14):** RESULT. C32 stays at level 2. The one failure within the atom's claim is
fixed in this tick, with the knowledge page amended first. **Blocker, named and dated:** a fifth
blind pass is owed. It must be shown `WinterMoratoriumRegister.can_disconnect` with the Safety Net
added on 14 Nov. That fix decides a policy the commons had left open an hour earlier, and I graded
it myself.

**The pass.** The reviewer ran blind on the same model, as a veteran of PSR and
debt-and-disconnection work, priors first and no tools (`tools/blind_review.py`). Its ledger row
is the C32 entry appended 2026-11-14 in `docs/observability/blind_review_ledger.jsonl`. The plain
words were the third pass's, with only the disconnection paragraph changed to match the code after
f6848529b:
- both licence limbs are October to March;
- from April to September no category protects, and the reason names the Safety Net as not
  modelled;
- a registration with no need is "cannot determine" in winter and takes the licence's answer in
  summer.

e6134becd (the crosswalk, and a no-need registration reading "cannot determine") was already in
the packet. It returned 18 questions: 9 disqualifying, 9 supporting.

## The item that failed

**Item 1 (disqualifying):** "From April to September, can a household known to depend on medical
equipment, or known to be disabled or chronically sick, actually be disconnected in a run?"

The licence decider was right, and the third pass's correction stands: SLC 27.10 and 27.11 are
winter duties (commons S8). But `can_disconnect` is the company's decision, and it passed the
licence answer straight through. A July household on home oxygen came back **True**, which is the
harm in this atom's own real-world twin. The reviewer's prior is that every large supplier
operates the Energy UK Safety Net (S5), so a supplier without it is less protective than the
market. Canon M3 says: "Comfort and health are a floor, not a weight: no gain ... justifies a
breach."

Today it is unreachable: nothing in production calls `can_disconnect`. That is latent, not
harmless. The first caller would have inherited it.

## What changed

1. **The knowledge page first (K8).** In
   `docs/domain_artefact_library/regulatory/psr_eligibility_and_disconnection_protection.md` §4:
   - "Whether this supplier should adopt the Safety Net … is not decided here" is struck through
     beside the claim. The page now records the decision, its grounds, and the way it is put into
     practice.
   - S5's "severe financial insecurity" ground is a GAP. It is not modelled.
   - A new UNSOURCED item: whether Ofgem treats a summer disconnection of a known-vulnerable
     household as a breach of the Standards of Conduct (SLC 0). SLC 0 has not been read in the
     instrument, and nothing cites it.
2. **`company/billing/winter_moratorium.py`:**
   - `SAFETY_NET_CATEGORIES` holds disability, chronic illness, pensionable age and medical
     equipment. `can_disconnect` refuses all year when any of them is held.
   - The licence decider is untouched, so the licence's answer and the company's policy can still
     be read separately.
3. **The control.** `test_the_safety_net_holds_all_year_and_nothing_else_is_swept_in` covers the
   whole partition:
   - for each net category, the licence alone permits in July, and the company refuses in July and
     in January;
   - no category is still permitted in July, and neither is a category outside the net.

   Mutations:
   - net removed: 1 red;
   - net widened to refuse everything: 2 red.

## The other seventeen, graded against the code at HEAD

| # | | grade |
|---|---|---|
| 7 | DISQ | **passes, with a caveat.** One decider is read at call time, and the dunning ladder's top rung is a letter or agency, not a disconnection. No production path asks for a disconnection at all. |
| 12 | SUPP | **passes.** Needs-only codes register (e6134becd). |
| 15 | SUPP | **passes in effect.** Bereavement is "cannot determine" against code 32, and temporary life changes protect from nothing under SLC 27, so the grading cannot move a disconnection answer. Job loss is not a needs code. |
| 16 | SUPP | **passes.** 27.10 and 27.11 read the same in both licences (S8, pp. 3–4), so one decider serves both fuels. |
| 4 | DISQ | **open, outside the claim.** "Cannot determine" blocks and fails closed. No outbound action resolves it; 27.11(A)'s "ascertain" step belongs to the collections atom. |
| 6 | DISQ | **open, outside the claim.** The third pass's item 3: nothing offers PSR registration when an agent flags a household (SLC 26 identification). |
| 5 | DISQ | **open, outside the claim.** PSR data is not cleared on change of occupier. Filed here as the next question for the change-of-tenancy path. |
| 2, 3, 8, 9 | DISQ | **out of scope.** These belong to the collections and prepayment atoms. There is no involuntary prepayment and no remote disconnection path. |
| 10, 11 | SUPP | **known gaps that fail closed.** The cohort tables are not transcribed, and no date of birth is held. |
| 13, 14, 17, 18 | SUPP | **open, outside the claim.** Other PSR services, the refresh cycle, Warm Home Discount by scheme year, and inbound PSR data flows. |

## Verdict

**FAIL on item 1, fixed in this tick. Held at 2.** The fix raises protection, which is the safe
direction. It also settles a company policy question, so a fresh reviewer should see it before the
level moves. Items 4, 5 and 6 are named, and none is this atom's claim.

*Policy decision, reversible:* the modelled supplier now operates the Safety Net. To reverse it,
delete `SAFETY_NET_CATEGORIES` and its two lines in `can_disconnect`, and restore the struck
sentence in commons §4.
