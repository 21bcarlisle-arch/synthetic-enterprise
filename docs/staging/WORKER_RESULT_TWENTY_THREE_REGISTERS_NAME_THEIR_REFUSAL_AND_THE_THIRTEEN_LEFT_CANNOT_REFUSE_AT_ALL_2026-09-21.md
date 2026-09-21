**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0

# 23 registers name their refusal, and the 13 the survey still calls BARE cannot refuse at all

**Filed** 2026-09-21 · autonomous worker · scheduled tick
**Claim** `name-the-35-remaining-bare-keyerror-refusals-on-raise-on-missing-registers`
**Mutation-proven in a clean `git archive HEAD` extract. Two mutations run; each caught by the leg written for it.**

*Worker, 2026-09-21. Lane 0 delivery item
`name-the-35-remaining-bare-keyerror-refusals-on-raise-on-missing-registers`.*

## Premise, re-measured before starting

The item cites `0bc30b578` and the draw's own check said it is already an ancestor of `origin/main`.
It is — but that commit is the **enabling** one (it landed the survey and the one named refusal on
`ChurnJourneyRegister.advance`), not the enabled work. Re-measured on the live tree at draw time:
`docs/observability/conditional_registration_survey.json` held **36 BARE of 38** accessors. The
premise was live, not spent.

## What the brief asked for, and where it was wrong

> Give each one a message naming the key, the book that refused, and what should have registered it.

**It is not 35 accessors. It is 23.** The other 13 cannot be reached with an absent key at all, so a
named refusal there would be unreachable code — the flattering reading of a silent mutation, which
CLAUDE.md names explicitly. Establishing which was the first half of the work.

The 13 split into two causes:

**(a) The key is drawn from the book being subscripted — a true equivalence (6).**

| Accessor | The line |
|---|---|
| `CarbonLedger.events` | `tuple(self._events[k] for k in sorted(self._events))` |
| `ConsumerDutyBoardRegister.outcome_trend` | `for year in sorted(self._reports): self._reports[year]` |
| `AcquisitionJourney.current_stage` | `max(self.stage_dates, key=lambda s: self.stage_dates[s])` |
| `CompetitivePressureLedger._closed_window` | `years = [y for y in self.decisions_by_year ...]` |
| `LedgerBook.verify_against_invoicing` | `for aid in self.accounts()`, and `accounts()` is `sorted(self._ledgers)` |
| `_DoorRowWalker.handle_data` | the path key is written by `handle_starttag` for the same stack |

**(b) The read sits behind an early-return or early-raise guard the survey cannot see (7).**

`tools/conditional_registration_survey._membership_guarded` recognises exactly two shapes: a
comprehension `if` and an *enclosing* `if`. It does not recognise the idiom this repo actually uses:

```python
if customer_id not in self._records:
    return None
return score_payment_history(self._records[customer_id])   # <- reported BARE
```

Seven accessors are in that shape: `COTBook.void_days`, `CustomerCommPreferenceRegister.can_contact`,
`PaymentBehaviourAnalytics.get_score`, `PaymentBehaviourAnalytics.get_metrics`,
`PSRBook.update_needs`, and — with an early *raise* rather than an early return —
`TriadNotificationBook.issue_alert` and `HedgingSchedule.add_contract`. **The last two already raise
a KeyError naming the key**, which is what the brief asked for; the survey counted them as the
defect because they name it one statement earlier than the detector looks.

So the instrument reads narrow in a way that inflates its own headline by ~54% (13 of 24 reported).
This is the same class as the catalogued `widening a detector's vocabulary` failure and it is
**filed here rather than fixed**: widening `_membership_guarded` changes `raw_loads`, which feeds
`pairs()` and therefore every NARROWER/PAIRED/UNSETTLED verdict. That is a second, separable change
and it should not ride in on a repair commit.

## What landed

23 accessors across 11 files in `company/` now refuse by name. Every message carries three things —
**the key, the book that refused (`Class._attr`), and the registrar that should have written it**:

```
KeyError: no DSR participant SYN-2016-008 in DSRBook._participants:
          dispatch() was reached before enroll() registered them
```

Two refusals say something different because the failure *is* different, and saying "register it
first" there would send the reader the wrong way:

- `CreditFacilityBook.total_interest_accrued_gbp` keys on a **drawdown's** `facility_id`, so its
  refusal names the orphaned drawdown: the drawdown outlived its facility.
- `TenancyChangeCoupler._changes_for` keys on an id held by `_by_key`, so its refusal names **both**
  stores: the index and the store disagree, and `_open_change()` is the only writer of both.

Three accessors (`CampaignTracker.close_campaign`/`record_contact`, `CustomerLifecycleTracker.transition`,
`TenancyChangeCoupler.record_exit_outcome`/`record_acquisition_outcome`) were routed through their
class's own `get()` rather than given a duplicate message.

## The control

`tests/company/test_a_register_that_can_refuse_names_the_key_the_book_and_the_registrar.py` — 23
cases, each of which **serves a registered key and refuses an absent one in one test**, because a
guard that refuses everything passes every assertion about what it refuses.

Mutation-proven in a clean `git archive HEAD` extract, and **each mutation was caught by the leg
written for it**, not by a neighbour:

| Mutation | Which leg reds |
|---|---|
| revert `PaymentDeferralBook.cancel` to the raw subscript | the *book-name* assertion: `'PaymentDeferralBook._deferrals' in "'NEVER-REGISTERED-001'"` |
| make `CampaignTracker.get` refuse **every** key | the *serve* leg — which is the whole reason it is there |

## The numbers, including the one that moved the wrong way

| | before | after |
|---|---|---|
| accessors raising a BARE KeyError | 36 of 38 | **13 of 33** |
| NARROWER (the survey's defect class) | 0 | 0 |
| PAIRED | 2 | 2 |
| UNSETTLED | 14 | **19** |

**The denominator moved and that is not free.** 38 → 33 because five raw reads were routed through a
sibling `get()` and stopped being catalogued accessors in their own right. Read the 13 as *13 of the
original 38*, not as a share of 33.

**UNSETTLED rose by 5**, and every one of the five is a new `self.get(...)` call site I created. The
survey has no registration guard to pair a self-call against, so "cannot tell" is the honest verdict
rather than a regression. NARROWER — the class that actually indicts something — stayed at 0, and
`instrument proven` stayed True.

## Two reds this commit does not own

`tests/company/billing/test_the_statement_shows_how_each_bill_reached_its_number.py` fails two legs
(`only 725 catch-up bills: an emptied ledger would pass`). Reproduced in a clean `git archive HEAD`
extract before any of this work: pre-existing, and among the 48 in `HEAD_RED_REGISTER.md`.

## What is left

1. **Widen `_membership_guarded` to see the early-return/early-raise guard**, then the survey's BARE
   count means what its name says and a control can key to `BARE == 0`. Until then the count has a
   floor of 13 that no repair can move, and anyone reading it will think 13 accessors are defective.
2. Decide whether `TriadNotificationBook.issue_alert` and `HedgingSchedule.add_contract` should carry
   the full three-part message rather than key-only. They are correct today; they are just terser
   than the rest.
