# C32 Expert Hour re-take: held at 2 on one item, the needs-code crosswalk

**Fate (2026-11-14):** RESULT. C32 stays at level 2. The knowledge half of the one open item
lands with this file, in the commons, s.1b. The code half is the next build on C32.

**The pass.** A blind, same-model reviewer (`tools/blind_review.py`, ledger row
2026-11-14T17:30:00Z), as a veteran of PSR and debt-and-disconnection operations. It was given a
fresh plain-words statement of the current code. That statement disclosed the empty-category
registration rather than hiding it. Priors came first, and it returned 14 questions.

**What changed since the 7 Oct pass:**
- EH-1 is fixed: an undetermined flag blocks disconnection.
- EH-2 is closed: the company is consent-only, and the warrant register is archived.
- EH-3, the code side, is half-closed: mental health is evidenced, and bereavement is graded against code 32.
- EH-5 is closed: pensionable age is read from a birth date at the decision date.

## Grading against the code at de67bec582

| # | verdict | grade | evidence |
|---|---|---|---|
| 1 | DISQ | **passes** | No flags and no birth date gives NOT_ESTABLISHED in both January and July. With no reason to believe, the licence prohibits nothing, and the reason string names the voluntary Safety Net as not modelled. When a birth date is held but cannot be resolved, the result is "cannot determine", and only where that would change the answer. |
| 2 | DISQ | **passes, but counts are owed** | `test_every_outcome_is_reachable` covers all four outcomes. There are no book counts because no production path asks the decider (see 13). |
| 3 | DISQ | **partly passes** | An agent's flag is reason to believe: an `elderly` flag blocks. **A household's own PSR registration is not.** It lands with `categories=()`, and the decider would read that as NOT_ESTABLISHED. |
| 4 | DISQ | **FAILS: the one open item** | `receive_registration` refuses any needs code because no crosswalk is written. The world draws no codes while the code mix is a GAP, so this is latent, not live. But it is the atom's own claim, "protected in one system and ordinary in another", in its sharpest form: on the register, yet ordinary to the decider. |
| 5 | DISQ | **partly passes, folds into 4** | PSRCategory holds ten categories. S7 codes 19, 27, 28, 31, 33, 34, 36 and 37 match none of them, and s.1b now says so: the household is still registered, and the code carries no category term. |
| 6 | SUPP | **held, not a failure** | Mapping bereavement to code 32 is the practitioner's routine. Under K4 that is a starting point, not a source. The "cannot determine" grade confers nothing anyway, because code 32 is not a disconnection term. |
| 7 | DISQ | **open knowledge gap, fails closed** | The reviewer reads the all-reasonable-steps limb as winter-only (SLC 27.11). S4 gives it no season. The code applies it all year, which is the direction that keeps protection. Filed in commons s.4. |
| 8 | DISQ | **out of scope** | The debt endgame belongs to the collections atoms. It is not this atom's claim. |
| 9 | SUPP | passes, partly | Self-disconnection routes to `offer_emergency_credit`. No licence clause is cited. |
| 10 | DISQ | **out of scope, stated** | `network_shared_count` exists. No DNO data flow is modelled. The claim is one decider per outcome, not one register shared across the industry. |
| 11 | SUPP | passes, with a correction to the reviewer | `penetration_against_published` reads the sourced 24% (end-2018) against the 13% 2016 figure. The reviewer's prior of 25 to 35% is a newer figure that the commons has not sourced. |
| 12 | SUPP | open | The Schedule 4 tables are not transcribed. That is named in commons s.2a. |
| 13 | DISQ | **out of scope, and the real limit** | There is no production caller of any disconnection decision (grep, 2026-11-14), so the decider is pre-load-bearing. That matches the real record, where debt disconnection is near zero. It is also why items 3 and 4 are latent. |
| 14 | SUPP | passes | PSRService holds the core services, and `is_compliant` requires at least one. |

## The verdict

**FAIL on one item (4, with 3 and 5 folded in). Held at 2.** Independence is not the only open
question, so G16 does not apply.

**What would move the level.** Commons s.1b is the crosswalk, a reading graded by the same rule as
the flags. Next, `priority_services_register` should:
- read codes through s.1b;
- hold undetermined and no-category codes on the record;
- answer CANNOT_DETERMINE for a registered household that has no recorded need.

One control should cover the whole partition: a registered household never reads NOT_ESTABLISHED.
This is all within C32's file_scope.
